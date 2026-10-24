#!/usr/bin/env python3
"""Fixed 48-lifetime original replay pilot: old control and preparation budgets1/2/4.

Each case/configuration gets one excluded warmup and three retained rotations.
No retries, replacement samples, PGO, workload changes, or broad qualification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
HELPERS = {0, 1, 8, 9, 10, 11, 12, 13}
CASES = ['profile-35', 'profile-08', 'profile-04']
sys.path.insert(0, str(ROOT/'tools'))
from compare_ordinary import stop_owned


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def numbers(value, prefix=''):
    if not isinstance(value, dict):
        return {}
    result = {}
    for key, item in value.items():
        name = prefix + str(key)
        if isinstance(item, dict):
            result.update(numbers(item, name + '.'))
        elif isinstance(item, (int, float)) and not isinstance(item, bool):
            result[name] = item
    return result


def distribution(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    original_affinity = os.sched_getaffinity(0)
    helper_affinity = original_affinity & HELPERS
    if not helper_affinity:
        parser.error('no declared helper CPU available')
    out = args.output.resolve()
    out.mkdir()
    variants = {'control': (args.control.resolve(), 1, []),
                'budget1': (args.candidate.resolve(), 1, ['--child-preparation=1']),
                'budget2': (args.candidate.resolve(), 2, ['--child-preparation=2']),
                'budget4': (args.candidate.resolve(), 4, ['--child-preparation=4'])}
    modes = json.loads((SPEC/'replay-oracle.json').read_text())['mode']
    schedule = []
    for case in CASES:
        schedule += [dict(case=case, variant=name, warmup=True, repeat=0) for name in variants]
        for repeat in range(3):
            order = list(variants)
            order = order[repeat:] + order[:repeat]
            schedule += [dict(case=case, variant=name, warmup=False, repeat=repeat+1) for name in order]
    assert len(schedule) == 48
    paths = [Path(__file__), HERE/'account.py', ROOT/'tools/tap_wire.mjs',
             ROOT/'tools/compare_ordinary.py', SPEC/'replay-check.mjs', SPEC/'benchmark.mjs',
             SPEC/'workloads.json', SPEC/'replay-oracle.json', args.control.resolve(), args.candidate.resolve()]
    manifest = dict(schema='rook2-child-preparation-pilot-v1',
                    variants={name: dict(path=str(value[0]), sha256=sha(value[0]),
                                        threads=value[1], args=value[2]) for name, value in variants.items()},
                    schedule=schedule, inputSha256={str(path): sha(path) for path in paths},
                    coordinatorCpu=14, workerCpus={1: [], 2: [6], 4: [6, 4, 2]},
                    inheritedHelperAffinity=sorted(original_affinity), helperAffinity=sorted(helper_affinity),
                    excludedSiblings=[3, 5, 7, 15],
                    limits=dict(perLifetimeSeconds=180, aggregateSeconds=1800,
                                ownedCleanupSeconds=10,
                                comparatorStdoutBytes=8*1024*1024, comparatorStderrBytes=1024*1024,
                                nativeRawBytes=8*1024*1024, preparationReportBytes=1024*1024),
                    boundaries=dict(search='tap before original go write through move data callback',
                                    cpu='native wait4 whole lifetime, all native threads, plus pre-exec prefix',
                                    lifetime='startup/setup/search/joined shutdown included',
                                    rss='whole native process peak RSS',
                                    counters='dedicated fresh ROOK2_CHILD_PREPARATION_REPORT; native standard streams unchanged'),
                    limitsOfEvidence='point affinity observations; no continuous VM/host isolation proof; finite original-case pilot')
    write(out/'plan.json', manifest)
    rows = []
    result = dict(complete=False, failure=None, runs=rows)
    deadline = time.monotonic() + 1800
    os.sched_setaffinity(0, helper_affinity)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())

    def supervisor(name, directory):
        image, threads, options = variants[name]
        command = [sys.executable, str(HERE/'account.py'), '--engine', str(image),
                   '--record', str(directory/'native.json'), '--known-single-process',
                   '--thread-budget', str(threads)]
        if name != 'control':
            command += ['--preparation-report', str(directory/'stats.json')]
        return command + options

    try:
        for index, step in enumerate(schedule):
            if time.monotonic() >= deadline:
                raise RuntimeError('aggregate deadline before next lifetime')
            directory = out/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
            directory.mkdir()
            native = supervisor(step['variant'], directory)
            config = dict(version=1, expectedArgv=native+modes, directory=str(directory/'wire'),
                          nativeExecutable=str(variants[step['variant']][0]),
                          maxRawBytes=8*1024*1024, tickHz=os.sysconf('SC_CLK_TCK'))
            write(directory/'tap-config.json', config)
            env = dict(os.environ, ROOK2_WIRE_TAP_CONFIG=str(directory/'tap-config.json'))
            command = ['/usr/bin/node', '--import', str(ROOT/'tools/tap_wire.mjs'),
                       str(SPEC/'replay-check.mjs'), '--case', step['case'], '--', *native]
            write(directory/'launch.json', dict(argv=command, step=step))
            run_deadline = min(deadline, time.monotonic()+180)
            with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
                child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
                try:
                    while child.poll() is None:
                        if time.monotonic() >= run_deadline:
                            raise RuntimeError('per-lifetime or aggregate deadline')
                        if ((directory/'stdout').stat().st_size > 8*1024*1024
                                or (directory/'stderr').stat().st_size > 1024*1024):
                            raise RuntimeError('comparator stream byte cap')
                        stats_path = directory/'stats.json'
                        if stats_path.exists() and stats_path.stat().st_size > 1024*1024:
                            raise RuntimeError('preparation report byte cap')
                        if (directory/'wire/failure.json').exists():
                            raise RuntimeError('wire capture failed')
                        time.sleep(.05)
                except BaseException:
                    stop_owned(child)
                    write(directory/'failure.json', dict(exit=child.poll(), step=step))
                    raise
            assert child.returncode == 0, 'comparator exit: ' + str(directory)
            assert (directory/'stdout').stat().st_size <= 8*1024*1024, 'comparator stdout cap'
            assert (directory/'stderr').stat().st_size <= 1024*1024, 'comparator stderr cap'
            assert (directory/'stderr').stat().st_size == 0, 'comparator stderr'
            replay = json.loads((directory/'stdout').read_text())
            receipt = json.loads((directory/'native.json').read_text())
            tap = json.loads((directory/'wire/receipt.json').read_text())
            variant = manifest['variants'][step['variant']]
            assert replay['status'] == 'pass' and replay['selectedCases'] == [step['case']]
            assert len(replay['results']) == 1
            actual = replay['results'][0]
            assert actual['status'] == 'pass' and actual['complete'] and not actual['truncated']
            assert actual['discardedObservedBytes'] == 0 and actual['exit'] == dict(code=0, signal=None)
            assert receipt['failure'] is None and receipt['native_exit_code'] == 0
            assert receipt['supervisor_signals'] == []
            assert receipt['engine_sha256_before'] == receipt['engine_sha256_after'] == variant['sha256']
            assert receipt['launcher_sha256'] == manifest['inputSha256'][str(HERE/'account.py')]
            assert receipt['argv'] == [variant['path'], *variant['args'], *modes]
            assert receipt['expected_threads'] == variant['threads']
            affinities = receipt['native_post_exec']['task_affinities']
            assert len(affinities) == variant['threads'] and affinities[str(receipt['native_pid'])] == [14]
            workers = [cpus for tid, cpus in affinities.items() if tid != str(receipt['native_pid'])]
            assert sorted(workers) == sorted([[cpu] for cpu in manifest['workerCpus'][variant['threads']]])
            prep = receipt['preparation_report']
            if step['variant'] == 'control':
                assert prep is None and not (directory/'stats.json').exists()
            else:
                assert isinstance(prep, dict) and receipt['preparation_report_path'] == str(directory/'stats.json')
                assert sha(directory/'stats.json') == receipt['preparation_report_sha256']
                assert json.loads((directory/'stats.json').read_text()) == prep
            assert tap['failure'] is None and tap['pending'] is None and len(tap['searches']) == 1
            search = tap['searches'][0]
            for boundary in ['beforeWrite', 'afterData']:
                assert search[boundary]['available'] and search[boundary]['pid'] == receipt['native_pid']
                assert search[boundary]['lastProcessor'] == 14
            for stream, item in tap['raw'].items():
                path = directory/'wire'/f'{stream}.raw'
                assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'] == item['observedBytes']
                assert item['discardedObservedBytes'] == 0
            assert (directory/'wire/stdout.raw').read_bytes() == actual['stdout'].encode()
            assert (directory/'wire/stderr.raw').read_bytes() == actual['stderr'].encode()
            assert (directory/'wire/stdin.raw').read_bytes().splitlines().count(b'go') == 1
            assert not Path(f'/proc/{receipt["native_pid"]}').exists()
            assert not Path(f'/proc/{receipt["supervisor_pid"]}').exists()
            artifact_names = ['native.json', 'stdout', 'stderr', 'wire/receipt.json']
            if prep is not None:
                artifact_names.append('stats.json')
            row = dict(**step, directory=str(directory), searchWallNs=search['wallNs'],
                       wholeCpuSeconds=receipt['total_cpu_s'], wholeWallNs=receipt['wall_ns'],
                       nonSearchWallNs=receipt['wall_ns']-search['wallNs'], rssKiB=receipt['maxrss_linux_kib'],
                       nativePid=receipt['native_pid'], taskAffinities=affinities, preparation=prep,
                       sha256={name: sha(directory/name) for name in artifact_names})
            rows.append(row)
            write(out/'progress.json', result)
        assert all(sha(Path(path)) == digest for path, digest in manifest['inputSha256'].items())
        summaries = []
        for case in CASES:
            for name in variants:
                selected = [row for row in rows if row['case'] == case and row['variant'] == name and not row['warmup']]
                assert len(selected) == 3
                entry = dict(case=case, variant=name)
                for metric in ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']:
                    entry[metric] = distribution([row[metric] for row in selected])
                counter_rows = [numbers(row['preparation']) for row in selected]
                assert all(set(row) == set(counter_rows[0]) for row in counter_rows)
                entry['preparation'] = {key: distribution([row[key] for row in counter_rows])
                                        for key in counter_rows[0]}
                summaries.append(entry)
        result.update(complete=True, summaries=summaries,
                      qualification='three original cases, 48 lifetimes including12 excluded warmups; no PGO or broad qualification')
    except BaseException as error:
        result['failure'] = repr(error)
        write(out/'result.json', result)
        raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
        os.sched_setaffinity(0, original_affinity)
    write(out/'result.json', result)
    print(json.dumps(dict(complete=True, lifetimes=len(rows), summaries=result['summaries']), indent=2))


if __name__ == '__main__':
    main()
