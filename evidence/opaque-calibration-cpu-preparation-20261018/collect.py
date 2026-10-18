#!/usr/bin/env python3
"""All54 opaque fixed-calibrator CPU collection with the released strict oracle.

One excluded warmup followed by three measured fresh-process repetitions per
case, in stored corpus order. No reference qualification or PMU claim.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

sys.path.insert(0, "/home/legolas/rook2/tools")
from compare_ordinary import sha, stop_owned, write
from measure import cgroup_snapshot

ROOT = Path('/home/legolas/rook2')
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def context():
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                uname=list(os.uname()), helper_affinity=sorted(os.sched_getaffinity(0)),
                cgroups=cgroup_snapshot(), proc_stat=Path('/proc/stat').read_text(),
                loadavg=Path('/proc/loadavg').read_text(),
                scope='Local snapshots only, no assertion of exclusive host ownership',
                pmu='Unavailable through disabled self-scoped opens; no I/C/IPC data')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--identity-record', required=True, type=Path)
    parser.add_argument('--launch-authority', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    engine, identity_path = args.engine.resolve(strict=True), args.identity_record.resolve(strict=True)
    identity = json.loads(identity_path.read_text())
    engine_sha = sha(engine)
    if identity != json.loads((Path(__file__).resolve().parent/'artifact-identity.json').read_text()) or identity['kind'] != 'approved-opaque-calibrator' or engine_sha != identity['sha256'] or str(engine) != identity['path']:
        parser.error('opaque artifact must match the approved exact identity; no synthetic build record')
    authority = json.loads(args.launch_authority.read_text())
    if authority.get('authorized') is not True or authority.get('scope') != 'opaque-fixed-calibrator-cpu-only' or authority.get('collector_sha256') != sha(Path(__file__)) or authority.get('all_conflicting_owned_jobs_closed') is not True:
        parser.error('exact collector authority and a closed measurement window are required')
    if os.geteuid() != 1000 or int(next(s.split(':',1)[1] for s in Path('/proc/self/status').read_text().splitlines() if s.startswith('CapEff:')),16) != 0 or engine.stat().st_mode & 0o6000:
        parser.error('engine/controller must remain UID1000 with no effective capabilities or set-ID executable')
    workloads = json.loads((SPEC/'workloads.json').read_text())
    case_ids = [c['id'] for c in workloads['cases']]
    if len(case_ids) != 54 or len(set(case_ids)) != 54:
        parser.error('expected the released54-case corpus')
    args.output.mkdir()
    initial_affinity = os.sched_getaffinity(0)
    if not HELPERS & initial_affinity:
        parser.error('no housekeeping CPU available')
    os.sched_setaffinity(0, HELPERS & initial_affinity)
    dependencies = [Path(__file__).resolve(), ROOT/'tools/account_native.py',
                    ROOT/'tools/compare_ordinary.py', ROOT/'tools/measure.py',
                    SPEC/'replay-check.mjs', SPEC/'workloads.json', SPEC/'replay-oracle.json',
                    identity_path, args.launch_authority.resolve(), Path(__file__).resolve().parent/'profile.json',
                    Path('/home/legolas/spec-issues/v2.5.0/2026-10-16-performance-handoff/calibration/calibration-data.json'),
                    Path('/usr/bin/node').resolve(), Path(sys.executable).resolve()]
    schedule = [dict(case=c, repeat=i, warmup=i == 0) for c in case_ids for i in range(4)]
    manifest = dict(schema='rook2-opaque-calibration54-cpu-v1', engine=str(engine), engine_sha256=engine_sha,
                    opaque_identity_record=str(identity_path), schedule=schedule,
                    input_sha256={str(p):sha(p) for p in dependencies},
                    limits=dict(seconds_per_run=960, aggregate_seconds=3600,
                                bytes_per_comparator_stream=8388608,
                                bytes_per_native_receipt=262144,
                                aggregate_stream_bytes=268435456,
                                outer_cleanup_seconds=10, released_cleanup_seconds=5),
                    behavior='Unchanged released strict comparator asserts every case/run',
                    accounting='Direct native wait4 user+system lifetime plus small Python child pre-exec prefix; no byte relay',
                    ownership='Known single-process native engine; one post-exec task/placement observation, not continuous descendant monitoring',
                    measurement='CPU-only per-case planning calibration; no PMU, cross-hardware qualification or universal conversion; lifetime wall boundaries differ from attached reference',
                    environment={k:os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE']})
    write(args.output/'manifest.json', manifest)
    write(args.output/'context-before.json', context())
    report = dict(complete=False, failure=None, runs=[], case_summaries={})
    aggregate_deadline = time.monotonic()+3600
    retained_stream_bytes = 0
    try:
        for index, step in enumerate(schedule):
            directory = args.output/f"{index:03d}-{step['case']}-r{step['repeat']}"
            directory.mkdir()
            receipt = directory/'native.json'
            command = ['/usr/bin/node', str(SPEC/'replay-check.mjs'), '--case', step['case'], '--',
                       sys.executable, str(ROOT/'tools/account_native.py'), '--engine', str(engine),
                       '--record', str(receipt), '--known-single-process']
            stdout_path, stderr_path = directory/'comparator.stdout', directory/'comparator.stderr'
            failure = None
            with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
                run_deadline = min(aggregate_deadline, time.monotonic()+960)
                try:
                    while process.poll() is None:
                        stdout_size, stderr_size = stdout_path.stat().st_size, stderr_path.stat().st_size
                        if time.monotonic() >= run_deadline:
                            failure = 'host-deadline'
                        elif max(stdout_size, stderr_size) > 8388608:
                            failure = 'comparator-stream-cap'
                        elif retained_stream_bytes+stdout_size+stderr_size > 268435456:
                            failure = 'aggregate-stream-cap'
                        if failure:
                            stop_owned(process)
                            break
                        time.sleep(0.02)
                except BaseException:
                    stop_owned(process)
                    raise
            retained_stream_bytes += stdout_path.stat().st_size+stderr_path.stat().st_size
            row = dict(**step, command=command, comparator_exit=process.returncode, failure=failure)
            try:
                assert max(stdout_path.stat().st_size, stderr_path.stat().st_size) <= 8388608, 'stream cap exceeded at exit'
                assert retained_stream_bytes <= 268435456, 'aggregate stream cap at exit'
                assert receipt.stat().st_size <= 262144, 'native receipt cap'
                native = json.loads(receipt.read_text())
                comparator = json.loads(stdout_path.read_text())
                assert process.returncode == 0 and not stderr_path.stat().st_size, 'comparator exit/stderr'
                assert comparator['status'] == 'pass' and comparator['selectedCases'] == [step['case']], 'strict oracle case failed'
                assert len(comparator['results']) == 1, 'unexpected result count'
                assert native['failure'] is None and native['native_exit_code'] == 0, 'native accounting invalid'
                assert native['engine_sha256_before'] == native['engine_sha256_after'] == engine_sha, 'native changed'
                assert native['launcher_sha256'] == manifest['input_sha256'][str(ROOT/'tools/account_native.py')], 'recorder changed'
                row.update(cpu_s=native['total_cpu_s'], user_s=native['user_cpu_s'], system_s=native['system_cpu_s'],
                           wall_ns=native['wall_ns'], native_receipt_sha256=sha(receipt), comparator_sha256=sha(stdout_path))
            except (AssertionError, OSError, ValueError, KeyError) as error:
                row['failure'] = row['failure'] or str(error)
            report['runs'].append(row)
            if row['failure']:
                report['failure'] = row['failure']
                write(args.output/'summary.json', report)
                break
            if step['repeat'] == 3:
                samples = [r['cpu_s'] for r in report['runs'] if r['case'] == step['case'] and not r['warmup']]
                v = dict(samples=samples, median=statistics.median(samples), minimum=min(samples), maximum=max(samples))
                v['range_over_median'] = (v['maximum']-v['minimum'])/v['median']
                report['case_summaries'][step['case']] = v
                print(json.dumps(dict(case=step['case'], **v)), flush=True)
            write(args.output/'summary.json', report)
        report['complete'] = len(report['runs']) == len(schedule) and report['failure'] is None
        report['artifact_sha256_after'] = sha(engine)
        report['input_sha256_after'] = {str(p):sha(p) for p in dependencies}
        if report['artifact_sha256_after'] != engine_sha or report['input_sha256_after'] != manifest['input_sha256']:
            report.update(complete=False, failure='artifact/input changed')
        report['retained_comparator_stream_bytes'] = retained_stream_bytes
        if report['complete']:
            report['sum_case_medians_s'] = sum(report['case_summaries'][c]['median'] for c in case_ids)
        write(args.output/'summary.json', report)
        write(args.output/'context-after.json', context())
    finally:
        os.sched_setaffinity(0, initial_affinity)
    print(json.dumps(dict(complete=report['complete'], failure=report['failure'],
                          sum_case_medians_s=report.get('sum_case_medians_s'))))
    return 0 if report['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
