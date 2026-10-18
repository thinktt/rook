#!/usr/bin/env python3
"""All54 opaque fixed-calibrator CPU collection with the released strict oracle.

One excluded warmup followed by three measured fresh-process repetitions per
case, in stored corpus order. No reference qualification or PMU claim.
"""
import argparse
import hashlib
import datetime
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import signal

sys.dont_write_bytecode = True
from guard import authority_preflight

ROOT = Path('/home/legolas/rook2')
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


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

def read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except OSError:
        return None


def cgroup_snapshot() -> dict:
    """Read the unified local cgroup and ancestors, without changing them."""
    membership = read_text(Path("/proc/self/cgroup"))
    result = {"membership": membership, "visible_ancestors": {}}
    for line in (membership or "").splitlines():
        if not line.startswith("0::/"):
            continue
        relative = line[3:].lstrip("/")
        if ".." in Path(relative).parts:
            continue
        root = Path("/sys/fs/cgroup")
        leaf = root / relative
        for parent in [leaf, *leaf.parents]:
            if parent != root and root not in parent.parents:
                continue
            result["visible_ancestors"][str(parent)] = {
                name: read_text(parent / name)
                for name in ("cpu.max", "cpuset.cpus.effective", "memory.max",
                             "memory.swap.max")
            }
    return result


def context():
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                uname=list(os.uname()), helper_affinity=sorted(os.sched_getaffinity(0)),
                cgroups=cgroup_snapshot(), proc_stat=Path('/proc/stat').read_text(),
                loadavg=Path('/proc/loadavg').read_text(),
                scope='Local snapshots only, no assertion of exclusive host ownership',
                pmu='Not collected; no PMU probe, instructions/cycles or IPC data')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--identity-record', required=True, type=Path)
    parser.add_argument('--launch-authority', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--launch-authority-sha256', required=True)
    args = parser.parse_args()
    authority, profile, identity, engine_file = authority_preflight(
        args.launch_authority, args.launch_authority_sha256, args.output)
    engine, identity_path = args.engine.resolve(strict=True), args.identity_record.resolve(strict=True)
    if str(engine) != identity['path'] or identity_path != Path(__file__).resolve().parent/'artifact-identity.json':
        parser.error('CLI identity/engine differs from frozen launch authority')
    engine_sha = identity['sha256']
    workloads = json.loads((SPEC/'workloads.json').read_text())
    case_ids = profile['cases']
    initial_affinity = os.sched_getaffinity(0)
    dependencies = dict(authority['pins'])
    dependencies[str(args.launch_authority.resolve())] = args.launch_authority_sha256
    # First output mutation occurs only AFTER every exact dependency/profile/
    # identity/reference/privilege/order/launch pin has been verified.
    args.output.mkdir()
    closure = args.output/'input-closure';closure.mkdir()
    snapshots = {}
    for index, (name, digest) in enumerate(dependencies.items()):
        path=Path(name);data=path.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest or sha(path) != digest:raise ValueError('dependency changed before snapshot: '+name)
        target=closure/f'{index:03d}-{path.name}'
        with target.open('xb') as stream:stream.write(data)
        snapshots[name]={'snapshot':str(target.relative_to(args.output)),'sha256':digest}
    schedule = [dict(case=c, repeat=i, warmup=i == 0) for c in case_ids for i in range(4)]
    manifest = dict(schema='rook2-opaque-calibration54-cpu-revision02', engine=str(engine), engine_sha256=engine_sha,
                    opaque_identity_record=str(identity_path), schedule=schedule,
                    input_sha256=dependencies, input_snapshots=snapshots, profile=profile,
                    launch_authority=str(args.launch_authority.resolve()), launch_authority_sha256=args.launch_authority_sha256,
                    engine_file_identity=engine_file,
                    limits=dict(seconds_per_run=960, aggregate_seconds=3600,
                                bytes_per_comparator_stream=8388608,
                                bytes_per_native_receipt=262144,
                                aggregate_stream_bytes=268435456,
                                outer_cleanup_seconds=10, released_cleanup_seconds=5),
                    behavior='Unchanged released strict comparator asserts every case/run',
                    accounting='Direct native wait4 user+system lifetime plus small Python child pre-exec prefix; no byte relay',
                    ownership='Known single-process native engine; one post-exec task/placement observation, not continuous descendant monitoring',
                    measurement='CPU-only per-case planning calibration; no PMU, cross-hardware qualification or universal conversion; lifetime wall boundaries differ from attached reference',
                    environment=authority['environment'])
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
                       sys.executable, str(Path(__file__).resolve().parent/'account_native.py'), '--engine', str(engine),
                       '--record', str(receipt), '--known-single-process',
                       '--expected-engine-sha256', engine_sha,
                       '--expected-file-identity', json.dumps(engine_file,sort_keys=True)]
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
            process.wait(timeout=10)
            retained_stream_bytes += stdout_path.stat().st_size+stderr_path.stat().st_size
            row = dict(**step, command=command, comparator_exit=process.returncode, actual_comparator_return_observed=True, failure=failure)
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
                assert native['launcher_sha256'] == manifest['input_sha256'][str(Path(__file__).resolve().parent/'account_native.py')], 'recorder changed'
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
        report['input_sha256_after'] = {name:sha(Path(name)) for name in dependencies}
        authority_preflight(args.launch_authority,args.launch_authority_sha256,args.output,fresh=False)
        if report['artifact_sha256_after'] != engine_sha or report['input_sha256_after'] != manifest['input_sha256']:
            report.update(complete=False, failure='artifact/input changed')
        report['captured_search_cpu_wall_pmu_fields'] = 'unavailable; lifetimewait4 only; posts remain strictbehavior raw, no terminalN/R invention'
        report['qualification'] = 'reported-only opaque calibration, not qualifiedKingREpass'
        report['retained_comparator_stream_bytes'] = retained_stream_bytes
        if report['complete']:
            report['sum_case_medians_s'] = sum(report['case_summaries'][c]['median'] for c in case_ids)
        write(args.output/'summary.json', report)
        write(args.output/'context-after.json', context())
    except BaseException as error:
        report.update(complete=False,failure=repr(error))
        write(args.output/'summary.json',report)
        raise
    finally:
        os.sched_setaffinity(0, initial_affinity)
    print(json.dumps(dict(complete=report['complete'], failure=report['failure'],
                          sum_case_medians_s=report.get('sum_case_medians_s'))))
    return 0 if report['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
