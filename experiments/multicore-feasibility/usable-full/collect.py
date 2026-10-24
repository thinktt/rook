#!/usr/bin/env python3
"""Selected generic48 replay lives plus3 idle probes. No retries or extension."""
import argparse
import hashlib
import os
from pathlib import Path
import selectors
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, ROOT, ORIGINAL, ACCOUNT, SPEC, HELPERS, CASES, NAMES, METRICS,
                    admission, audit_placement, native_receipt, read, write, sha,
                    ready_record, run_lifetime, schedule, train, variants)


def distribution(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def proc_ticks(pid):
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    return int(fields[11])+int(fields[12])


def idle_probe(directory, name, image, budget, options, deadline, hashes):
    directory.mkdir()
    command = train.supervisor(image, budget, directory, options)
    write(directory/'launch.json', dict(argv=command, variant=name, kind='startup-idle-shutdown'))
    started = time.monotonic_ns()
    with (directory/'stderr').open('xb') as stderr:
        child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=stderr, start_new_session=True)
        selector = selectors.DefaultSelector()
        try:
            ready = ready_record(directory, child.pid, image, budget, min(deadline, time.monotonic()+12))
            release = time.monotonic_ns()
            write(directory/'native.json.input-gate.json', dict(
                schema='rook2-placement-input-gate-v1', implementation='python-idle',
                gate_sha256=sha(Path(__file__)), ready_path=str(directory/'native.json.ready'),
                ready_sha256=sha(directory/'native.json.ready'), native_pid=ready['native_pid'],
                supervisor_pid=child.pid, release_monotonic_ns=str(release),
                first_write_bytes=8, first_write_sha256=hashlib.sha256(b'cm_parm\n').hexdigest()))
            child.stdin.write(b'cm_parm\n'); child.stdin.flush()
            selector.register(child.stdout, selectors.EVENT_READ)
            assert selector.select(max(.001, min(10, deadline-time.monotonic()))), 'idle startup deadline'
            reply = child.stdout.readline()
            assert reply == b'cm_parm\n'
            startup = time.monotonic_ns()-started
            children = Path(f'/proc/{child.pid}/task/{child.pid}/children').read_text().split()
            assert children == [str(ready['native_pid'])]
            pid = ready['native_pid']
            before = proc_ticks(pid)
            begin = time.monotonic_ns()
            assert time.monotonic()+.25 < deadline
            time.sleep(.25)
            after, end = proc_ticks(pid), time.monotonic_ns()
            child.stdin.write(b'quit\n'); child.stdin.close()
            shutdown = time.monotonic_ns()
            assert child.wait(timeout=max(.001, min(10, deadline-time.monotonic()))) == 0
            shutdown = time.monotonic_ns()-shutdown
            assert child.stdout.read() == b''
        except BaseException:
            train.stop_owned(child)
            raise
        finally:
            selector.close()
            child.stdout.close()
    (directory/'stdin.raw').write_bytes(b'cm_parm\nquit\n')
    (directory/'stdout.raw').write_bytes(reply)
    native = native_receipt(directory/'native.json', image, budget, options, hashes)
    assert native['native_pid'] == pid and native['supervisor_pid'] == child.pid
    assert (directory/'stderr').stat().st_size == 0
    hz = os.sysconf('SC_CLK_TCK')
    row = dict(variant=name, nativePid=pid, supervisorPid=child.pid,
               idleNs=end-begin, idleCpuTicks=after-before, tickHz=hz,
               idleCpuSeconds=(after-before)/hz, startupReplyNs=startup,
               startupCpuTicks=before, shutdownStartCpuTicks=after,
               idleStartMonotonicNs=begin, idleEndMonotonicNs=end,
               shutdownSupervisorNs=shutdown, wholeCpuSeconds=native['total_cpu_s'],
               wholeWallNs=native['wall_ns'], rssKiB=native['maxrss_linux_kib'],
               placement=audit_placement(directory, native, hashes),
               boundaries='startup through cm_parm reply; whole-process ticks for250ms; quit through supervisor exit; CPU samples have tick resolution',
               sha256={n: sha(directory/n) for n in ['launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr']})
    write(directory/'probe.json', row)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['control', 'candidate', 'build', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    control, candidate, build = args.control.resolve(), args.candidate.resolve(), args.build.resolve()
    receipt = admission(build, control, candidate)
    out = args.output.resolve(); out.mkdir()
    modes = variants(control, candidate)
    inputs = sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    inputs += [ORIGINAL/n for n in ['train.py', 'collect.py', 'reconcile.py']]
    inputs += [HERE.parent/'reversed-full/collect.py', ROOT/'tools/tap_wire.mjs',
               ROOT/'tools/compare_ordinary.py', SPEC/'replay-check.mjs', SPEC/'benchmark.mjs',
               SPEC/'workloads.json', SPEC/'replay-oracle.json', control, candidate,
               build/'receipt.json', build/'build.stderr',
               Path('/home/legolas/rook2-experiments/full-split-production-20261024-01/idle-build/receipt.json')]
    inputs += [build/'source-before'/name for name in receipt['source_sha256_before']]
    plan = dict(schema='rook2-usable-full-generic-v1', variants=modes, schedule=schedule(),
                build=str(build), coordinatorCpu=14, workerCpu=6,
                nativePreExecAffinity=[6, 14], idleOwnedSiblings=[7, 15],
                helperAffinity=sorted(os.sched_getaffinity(0)),
                inputSha256={str(path): sha(path) for path in inputs},
                limits=dict(perLifeSeconds=180, totalSeconds=1800,
                            supervisorPlacementSeconds=10, inputGateSeconds=12),
                boundaries=dict(search='unchanged tap: go write through move data callback',
                    cpu='native direct wait4 all threads and pre-exec prefix', rss='whole lifetime peak RSS',
                    placement='external supervisor pins main14/helper6 before first setup input; original pipes',
                    lifecycle='separate startup/250ms process-tick idle/quit probes'),
                notes='preserved winning generic current2 control vs cleaned1/2; excluded warmups; no PGO or retune; no accepted-serial speed claim')
    assert plan['helperAffinity'] == sorted(HELPERS)
    write(out/'plan.json', plan)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    state = dict(complete=False, failure=None, runs=[], idle=[], streamStartMonotonicNs=time.monotonic_ns())
    deadline = time.monotonic()+1800
    try:
        for i, step in enumerate(plan['schedule']):
            assert time.monotonic() < deadline, 'aggregate study deadline'
            v = modes[step['variant']]
            directory = out/f'{i:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
            state['runs'].append(run_lifetime(directory, step, Path(v['path']),
                                              v['budget'], v['options'], deadline, plan['inputSha256']))
            write(out/'progress.json', state)
        for name, v in modes.items():
            assert time.monotonic()+35 < deadline, 'insufficient aggregate idle allowance'
            state['idle'].append(idle_probe(out/('idle-'+name), name, Path(v['path']),
                                             v['budget'], v['options'], deadline, plan['inputSha256']))
        summaries = []
        for case in CASES:
            for name in NAMES:
                rows = [r for r in state['runs'] if r['case'] == case and r['variant'] == name and not r['warmup']]
                assert len(rows) == 3
                summaries.append(dict(case=case, variant=name,
                    **{k: distribution([r[k] for r in rows]) for k in METRICS}))
        assert all(sha(Path(path)) == digest for path, digest in plan['inputSha256'].items())
        admission(build, control, candidate)
        assert time.monotonic() < deadline
        state.update(complete=True, summaries=summaries, streamEndMonotonicNs=time.monotonic_ns(),
                     qualification='four-case generic research;36 retained replay lives,12 excluded warmups,3 separate idle probes; no PGO/full qualification/adoption')
        write(out/'result.json', state)
    except BaseException as error:
        state['failure'] = repr(error)
        write(out/'result.json', state)
        write(out/'failure.json', dict(error=repr(error), completed=len(state['runs'])))
        raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
    print('complete48 replay lives +3 idle processes', flush=True)


if __name__ == '__main__':
    main()
