#!/usr/bin/env python3
"""Production control versus one own-PGO candidate in inline/worker modes.

Default:36 original replay lives plus three separate startup/idle/exit probes.
--full54:162 original replay lives, one observation/configuration/case, no probes.
The caller evaluates the small-study gate; this script never extends a study.
"""
import argparse
import json
import os
from pathlib import Path
import selectors
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from train import (ROOT, HERE, SPEC, ACCOUNT, HELPERS, CONTROL_SHA, admit_build,
                   read, write, sha, supervisor, run_lifetime, stop_owned)

CONTROL_BUILD = Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build')
SMALL_CASES = ['profile-35', 'profile-08', 'profile-04']
VARIANTS = ['control', 'budget1', 'budget2']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def distribution(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def extension_gate(summaries):
    by = {(row['case'], row['variant']): row for row in summaries}
    lower, separated = [], []
    for case in SMALL_CASES:
        worker = by[case, 'budget2']['searchWallNs']
        controls = [by[case, name]['searchWallNs'] for name in ['control', 'budget1']]
        lower.append(all(worker['median'] < value['median'] for value in controls))
        separated.append(all(worker['max'] < value['min'] for value in controls))
    sums = {name: sum(by[case, name]['searchWallNs']['median'] for case in SMALL_CASES) for name in VARIANTS}
    ratios = {name: sums['budget2']/sums[name] for name in ['control', 'budget1']}
    passed = all(lower) and all(sums['budget2']*100 <= sums[name]*98 for name in ['control', 'budget1']) and sum(separated) >= 2
    return dict(passed=passed, workerMedianLowerBothByCase=dict(zip(SMALL_CASES, lower)),
                workerRangeBelowBothByCase=dict(zip(SMALL_CASES, separated)),
                workerSelectedSumRatios=ratios,
                rule='budget2 medians lower than control and budget1 in all3; selected summed medians gain>=2% versus both; >=2 cases max budget2<min both controls',
                automaticExtension=False)


def proc_ticks(pid):
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    return int(fields[11])+int(fields[12])


def idle_probe(directory, name, image, budget, options):
    directory.mkdir()
    command = supervisor(image, budget, directory, options)
    write(directory/'launch.json', dict(argv=command, variant=name, kind='startup-idle-shutdown'))
    started = time.monotonic_ns()
    with (directory/'stderr').open('xb') as stderr:
        child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=stderr, start_new_session=True)
        selector = selectors.DefaultSelector()
        try:
            child.stdin.write(b'cm_parm\n'); child.stdin.flush()
            selector.register(child.stdout, selectors.EVENT_READ)
            assert selector.select(10), 'idle startup acknowledgment deadline'
            reply = child.stdout.readline()
            assert reply == b'cm_parm\n'
            startup = time.monotonic_ns()-started
            children = Path(f'/proc/{child.pid}/task/{child.pid}/children').read_text().split()
            assert len(children) == 1
            pid = int(children[0])
            before = proc_ticks(pid)
            begin = time.monotonic_ns()
            time.sleep(.25)
            after = proc_ticks(pid)
            end = time.monotonic_ns()
            child.stdin.write(b'quit\n'); child.stdin.close()
            shutdown = time.monotonic_ns()
            assert child.wait(timeout=10) == 0
            shutdown = time.monotonic_ns()-shutdown
            assert child.stdout.read() == b''
        except BaseException:
            stop_owned(child)
            raise
        finally:
            selector.close()
            child.stdout.close()
    (directory/'stdin.raw').write_bytes(b'cm_parm\nquit\n')
    (directory/'stdout.raw').write_bytes(reply)
    native = read(directory/'native.json')
    assert native['failure'] is None and native['native_exit_code'] == 0
    assert native['expected_threads'] == budget and native['native_pid'] == pid
    assert native['argv'] == [str(image), *options]
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
    assert (directory/'stderr').stat().st_size == 0
    assert not Path(f'/proc/{pid}').exists() and not Path(f'/proc/{child.pid}').exists()
    hz = os.sysconf('SC_CLK_TCK')
    row = dict(variant=name, nativePid=pid, supervisorPid=child.pid,
               idleNs=end-begin, idleCpuTicks=after-before, tickHz=hz,
               idleCpuSeconds=(after-before)/hz, startupReplyNs=startup,
               startupCpuTicks=before, shutdownStartCpuTicks=after,
               shutdownSupervisorNs=shutdown, wholeCpuSeconds=native['total_cpu_s'],
               wholeWallNs=native['wall_ns'], rssKiB=native['maxrss_linux_kib'],
               boundaries='startup through cm_parm reply; idle process ticks for250ms; quit through direct supervisor exit; CPU boundary samples have tick resolution',
               sha256={name: sha(directory/name) for name in ['launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr']})
    write(directory/'probe.json', row)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--full54', action='store_true')
    args = parser.parse_args()
    build_directory = args.build.resolve()
    build, built_image, effective = admit_build(build_directory, 'profile-use')
    control, candidate = args.control.resolve(), args.candidate.resolve()
    assert sha(control) == CONTROL_SHA, 'exact accepted dynamic production control required'
    assert sha(candidate) == sha(built_image) == build['binary_output']['sha256']
    old = read(CONTROL_BUILD/'receipt.json')
    for tool in ['rustc', 'cargo']:
        assert old['toolchain'][tool]['stdout'] == build['toolchain'][tool]['stdout']
        assert old['toolchain'][tool+'_executable_sha256'] == build['toolchain'][tool+'_executable_sha256']
    assert old['target_triple'] == build['target_triple'] and old['target_cpu'] == build['target_cpu']
    assert old['binary_output']['sha256'] == CONTROL_SHA
    variants = {'control': (control, 1, []),
                'budget1': (candidate, 1, ['--research-threads=1']),
                'budget2': (candidate, 2, ['--research-threads=2'])}
    cases = [case['id'] for case in read(SPEC/'workloads.json')['cases']] if args.full54 else SMALL_CASES
    schedule = []
    for index, case in enumerate(cases):
        if args.full54:
            order = VARIANTS[index % 3:] + VARIANTS[:index % 3]
            schedule += [dict(case=case, variant=name, warmup=False, repeat=1) for name in order]
        else:
            schedule += [dict(case=case, variant=name, warmup=True, repeat=0) for name in VARIANTS]
            for repeat in range(3):
                order = VARIANTS[repeat:] + VARIANTS[:repeat]
                schedule += [dict(case=case, variant=name, warmup=False, repeat=repeat+1) for name in order]
    assert len(schedule) == (162 if args.full54 else 36)
    out = args.output.resolve(); out.mkdir()
    inputs = [Path(__file__), HERE/'train.py', HERE/'reconcile.py', ACCOUNT, ROOT/'tools/tap_wire.mjs',
              ROOT/'tools/compare_ordinary.py', SPEC/'replay-check.mjs', SPEC/'benchmark.mjs',
              SPEC/'workloads.json', SPEC/'replay-oracle.json', control, candidate,
              CONTROL_BUILD/'receipt.json', ROOT/'release/qualification.json',
              build_directory/'receipt.json', build_directory/'build.stderr',
              Path(build['pgo']['profile']), Path(build['pgo']['training_record'])]
    manifest = dict(schema='rook2-full-split-production-plan-v1', study='original54' if args.full54 else 'three-case',
                    variants={name: dict(path=str(value[0]), sha256=sha(value[0]), threads=value[1], args=value[2])
                              for name, value in variants.items()},
                    cases=cases, schedule=schedule, inputs={str(path): sha(path) for path in inputs},
                    candidateBuildDirectory=str(build_directory), effectiveRustcOptions=effective,
                    controlCompatibility=dict(acceptedArtifactSha256=CONTROL_SHA,
                        receipt=str(CONTROL_BUILD/'receipt.json'), recipe='Rust1.85.1/LLVM19.1.7 x86-64 O3 ThinLTO oneCGU panicabort debug1 ownPGO profiledExtTSP',
                        compilerVersionsEqual=True, sourceProfileChangedForCandidate=True),
                    coordinatorCpu=14, workerCpu=6, helperAffinity=sorted(HELPERS), idleOwnedSiblings=[7, 15],
                    limits=dict(perLifetimeSeconds=180, aggregateSeconds=1800,
                                nativeRawBytesPerLifetime=8*1024*1024, ownedCleanupSeconds=10),
                    idleVariants=[] if args.full54 else VARIANTS,
                    boundaries=dict(search='tap before original go write through move data callback',
                                    cpu='native wait4 user+system for all threads, complete lifetime plus pre-exec prefix',
                                    rss='whole native peak RSS', lifecycle='three separate startup/250ms-idle/quit probes in small study'),
                    limitations='finite original replay; no host-isolation proof, current KingWCR comparison or performance qualification')
    write(out/'plan.json', manifest)
    original_affinity = os.sched_getaffinity(0)
    assert HELPERS <= original_affinity
    os.sched_setaffinity(0, HELPERS)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    result = dict(complete=False, failure=None, runs=[], idle=[])
    deadline = time.monotonic()+1800
    try:
        for index, step in enumerate(schedule):
            assert time.monotonic() < deadline, 'aggregate study deadline'
            image, budget, options = variants[step['variant']]
            row = run_lifetime(out/f'{index:03d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}',
                               step, image, budget, options, deadline)
            result['runs'].append(row)
            write(out/'progress.json', result)
        if not args.full54:
            for name, (image, budget, options) in variants.items():
                assert time.monotonic()+21 < deadline, 'idle probe exceeds aggregate budget'
                result['idle'].append(idle_probe(out/('idle-'+name), name, image, budget, options))
        assert all(sha(Path(path)) == digest for path, digest in manifest['inputs'].items())
        summaries = []
        for case in cases:
            for name in VARIANTS:
                selected = [row for row in result['runs'] if (row['case'], row['variant'], row['warmup']) == (case, name, False)]
                assert len(selected) == (1 if args.full54 else 3)
                summary = dict(case=case, variant=name)
                for metric in METRICS:
                    summary[metric] = distribution([row[metric] for row in selected])
                summaries.append(summary)
        result.update(complete=True, summaries=summaries,
                      extensionGate=None if args.full54 else extension_gate(summaries),
                      qualification='descriptive original54 single observations' if args.full54 else 'three original cases;27 retained replay observations and9 excluded warmups, plus3 separate idle probes')
    except BaseException as error:
        result['failure'] = repr(error)
        write(out/'result.json', result)
        raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
        os.sched_setaffinity(0, original_affinity)
    write(out/'result.json', result)
    print(json.dumps(dict(complete=True, replayLifetimes=len(result['runs']), idleProcesses=len(result['idle']),
                         summaries=result['summaries'], extensionGate=result['extensionGate']), indent=2))


if __name__ == '__main__':
    main()
