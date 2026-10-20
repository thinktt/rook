#!/usr/bin/env python3
"""Balanced whole-lifetime CPU pilot over one unchanged public profiling case.

The released comparator owns all behavioral assertions. account_native.py
collects direct native wait4 CPU without relaying protocol bytes. This pilot
is not the full54 reference schedule or a performance acceptance decision.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SPEC = Path('/home/legolas/king-spec/conformance/profiling')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
    temporary.replace(path)


def children(pid):
    try:
        return [int(x) for x in Path(f'/proc/{pid}/task/{pid}/children').read_text().split()]
    except FileNotFoundError:
        return []


def stop_owned(comparator):
    # The known direct children are our accounting supervisors. Their SIGTERM
    # handler forwards to/reaps the native child before mirroring its signal.
    supervisors = children(comparator.pid)
    for pid in supervisors:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        comparator.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    for pid in supervisors:
        try:
            if os.getpgid(pid) == pid and pid in children(comparator.pid):
                os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        os.killpg(comparator.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    comparator.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', action='append', required=True, metavar='NAME=ENGINE')
    parser.add_argument('--case', default='profile-01')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    variants = {}
    for value in args.variant:
        name, path = value.split('=', 1)
        if not name or not all(c.isascii() and (c.isalnum() or c in '-_') for c in name) or name in variants:
            parser.error('variant names must be unique ASCII letters/digits/hyphen/underscore')
        variants[name] = Path(path).resolve()
    workloads = json.loads((SPEC / 'workloads.json').read_text())
    if not any(c['id'] == args.case for c in workloads['cases']):
        parser.error('unknown released workload case')
    args.output.mkdir()
    original_affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, original_affinity & {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13})
    names = list(variants)
    schedule = [dict(variant=n, warmup=True, repeat=0) for n in names]
    for repeat in range(1, 5):
        schedule += [dict(variant=n, warmup=False, repeat=repeat)
                     for n in (names if repeat % 2 else names[::-1])]
    manifest = dict(schema='rook2-balanced-ordinary-pilot-v1', case=args.case,
                    variants={n: dict(path=str(p), sha256=sha(p)) for n, p in variants.items()},
                    schedule=schedule, helper_affinity=sorted(os.sched_getaffinity(0)), engine_cpu=14,
                    files={str(p): sha(p) for p in [Path(__file__), ROOT/'tools/account_native.py',
                           SPEC/'replay-check.mjs', SPEC/'workloads.json', SPEC/'replay-oracle.json']},
                    limits=dict(seconds_per_run=960, aggregate_seconds=1800,
                                bytes_per_comparator_stream=8388608, cleanup_seconds=5),
                    performance='reported-only pilot, not a full-corpus performance decision')
    write(args.output / 'manifest.json', manifest)
    report = dict(complete=False, failure=None, runs=[])
    deadline = time.monotonic() + 1800
    try:
        for index, step in enumerate(schedule):
            directory = args.output / f"{index:02d}-{step['variant']}"
            directory.mkdir()
            native_receipt = directory / 'native.json'
            command = ['/usr/bin/node', str(SPEC/'replay-check.mjs'), '--case', args.case, '--',
                       sys.executable, str(ROOT/'tools/account_native.py'),
                       '--engine', str(variants[step['variant']]), '--record', str(native_receipt),
                       '--known-single-process']
            stdout_path, stderr_path = directory/'comparator.stdout', directory/'comparator.stderr'
            failure = None
            with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
                run_deadline = min(deadline, time.monotonic()+960)
                try:
                    while process.poll() is None:
                        if time.monotonic() >= run_deadline:
                            failure = 'host-deadline'
                        if stdout_path.stat().st_size > 8388608 or stderr_path.stat().st_size > 8388608:
                            failure = 'comparator-stream-cap'
                        if failure:
                            stop_owned(process)
                            break
                        time.sleep(0.02)
                except BaseException:
                    stop_owned(process)
                    raise
            row = dict(**step, command=command, comparator_exit=process.returncode, failure=failure)
            try:
                native = json.loads(native_receipt.read_text())
                comparator = json.loads(stdout_path.read_text())
                assert process.returncode == 0, 'comparator nonzero/signal'
                assert stderr_path.stat().st_size == 0, 'comparator stderr'
                assert comparator['status'] == 'pass' and len(comparator['results']) == 1, 'strict oracle failed'
                assert native['failure'] is None and native['native_exit_code'] == 0, 'native accounting invalid'
                assert native['engine_sha256_before'] == native['engine_sha256_after'] == manifest['variants'][step['variant']]['sha256'], 'native artifact changed'
                assert native['launcher_sha256'] == manifest['files'][str(ROOT/'tools/account_native.py')], 'recorder changed'
                row.update(native_cpu_s=native['total_cpu_s'], native_wall_ns=native['wall_ns'],
                           native_receipt_sha256=sha(native_receipt), comparator_sha256=sha(stdout_path))
            except (AssertionError, OSError, ValueError, KeyError) as error:
                row['failure'] = row['failure'] or str(error)
            report['runs'].append(row)
            write(args.output/'summary.json', report)
            if row['failure']:
                report['failure'] = row['failure']
                break
        report['complete'] = (len(report['runs']) == len(schedule) and report['failure'] is None)
        report['summaries'] = {}
        if report['complete']:
            for name in names:
                values = [r['native_cpu_s'] for r in report['runs'] if r['variant'] == name and not r['warmup']]
                report['summaries'][name] = dict(samples=values, median=statistics.median(values),
                                                minimum=min(values), maximum=max(values))
        report['artifact_hashes_after'] = {n: sha(p) for n, p in variants.items()}
        if any(report['artifact_hashes_after'][n] != manifest['variants'][n]['sha256'] for n in names):
            report.update(complete=False, failure='artifact changed')
        report['input_hashes_after'] = {p: sha(Path(p)) for p in manifest['files']}
        if report['input_hashes_after'] != manifest['files']:
            report.update(complete=False, failure='recorder/comparator/input changed')
        write(args.output/'summary.json', report)
    finally:
        os.sched_setaffinity(0, original_affinity)
    print(json.dumps(dict(output=str(args.output), complete=report['complete'], failure=report['failure'], summaries=report.get('summaries'))))
    return 0 if report['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
