#!/usr/bin/env python3
"""Direct native wait4 with external TID placement before first protocol input."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time

HELPERS = {0, 1, 2, 3, 8, 9, 10, 11, 12, 13}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def record(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--known-single-process', action='store_true', required=True)
    parser.add_argument('--thread-budget', type=int, choices=[1, 2, 3], required=True)
    args, engine_args = parser.parse_known_args()
    engine, receipt = args.engine.resolve(), args.record.resolve()
    ready_path = Path(str(receipt)+'.ready')
    pending = Path(str(ready_path)+'.pending')
    report_path = os.environ.get('ROOK2_COLORS_REPORT')
    if report_path is not None:
        report_path = Path(report_path)
        if not report_path.is_absolute() or report_path != receipt.parent/'colors.json':
            parser.error('colors report must be the declared absolute per-life colors.json')
    fresh = [receipt, ready_path, pending] + ([report_path] if report_path else [])
    if any(p.exists() or p.is_symlink() for p in fresh) or not receipt.parent.is_dir():
        parser.error('receipt and placement/report artifacts must be fresh')
    inherited = sorted(os.sched_getaffinity(0))
    if inherited != sorted(HELPERS):
        parser.error('supervisor must inherit the frozen housekeeping mask')
    engine_hash, launcher_hash = sha(engine), sha(Path(__file__))
    native_mask = {4, 6, 14} if args.thread_budget == 3 else {6, 14}
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    pid, signals = None, []

    def forward(signum, _frame):
        signals.append(signum)
        if pid:
            try:
                os.kill(pid, signum)
            except ProcessLookupError:
                pass

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, forward)
    started_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    start = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                signal.signal(signum, signal.SIG_DFL)
            os.sched_setaffinity(0, native_mask)
            placement = dict(pid=os.getpid(), pgid=os.getpgrp(), affinity=sorted(os.sched_getaffinity(0)))
            os.write(write_fd, (json.dumps(placement)+'\n').encode('ascii'))
            os.execv(str(engine), [str(engine), *engine_args])
        except BaseException as error:
            os.write(write_fd, (json.dumps(dict(exec_error=repr(error)))+'\n').encode('ascii'))
            os._exit(127)
    os.close(write_fd)
    private = bytearray()
    while True:
        chunk = os.read(read_fd, 4096)
        if not chunk:
            break
        private.extend(chunk)
        if len(private) > 8192:
            os.kill(pid, signal.SIGKILL)
            break
    os.close(read_fd)
    placement, exec_error, observed, placement_error = None, None, None, None
    for line in private.splitlines():
        value = json.loads(line)
        if 'exec_error' in value:
            exec_error = value['exec_error']
        else:
            placement = value
    deadline = time.monotonic()+10
    before_pinning = None
    try:
        while not exec_error and time.monotonic() < deadline:
            if os.readlink(f'/proc/{pid}/exe') != str(engine):
                time.sleep(.001)
                continue
            tasks = sorted((p.name for p in Path(f'/proc/{pid}/task').iterdir()), key=int)
            if len(tasks) != args.thread_budget:
                time.sleep(.001)
                continue
            before_pinning = {tid: sorted(os.sched_getaffinity(int(tid))) for tid in tasks}
            assert all(mask and set(mask) <= native_mask for mask in before_pinning.values())
            os.sched_setaffinity(pid, {14})
            helper_tasks = [tid for tid in tasks if tid != str(pid)]
            for tid, cpu in zip(helper_tasks, [6, 4]):
                os.sched_setaffinity(int(tid), {cpu})
            affinities = {tid: sorted(os.sched_getaffinity(int(tid))) for tid in tasks}
            assert tasks == sorted((p.name for p in Path(f'/proc/{pid}/task').iterdir()), key=int)
            assert affinities[str(pid)] == [14]
            assert [affinities[tid] for tid in helper_tasks] == [[cpu] for cpu in [6, 4][:len(helper_tasks)]]
            observed = dict(path=os.readlink(f'/proc/{pid}/exe'),
                affinity=sorted(os.sched_getaffinity(pid)), pgid=os.getpgid(pid),
                tasks=tasks, task_affinities=affinities,
                task_names={tid: Path(f'/proc/{pid}/task/{tid}/comm').read_text().strip() for tid in tasks})
            if args.thread_budget == 3:
                assert [observed['task_names'][tid] for tid in helper_tasks] == ['rook2-eval-whit', 'rook2-eval-blac']
            assert observed['path'] == str(engine) and observed['pgid'] == os.getpgrp()
            break
        if not observed:
            raise RuntimeError('external startup placement deadline or native exec failure')
        assert placement == dict(pid=pid, pgid=os.getpgrp(), affinity=sorted(native_mask))
        ready = dict(schema='rook2-external-placement-ready-v1', native_pid=pid,
            supervisor_pid=os.getpid(), engine=str(engine), engine_sha256=engine_hash,
            launcher_sha256=launcher_hash, expected_threads=args.thread_budget,
            native_pre_exec=placement, native_post_exec=observed,
            task_affinities_before_pinning=before_pinning,
            helper_assignment='numeric TID order: first6, second4',
            ready_monotonic_ns=str(time.monotonic_ns()))
        record(pending, ready)
        pending.rename(ready_path)
    except BaseException as error:
        placement_error = repr(error)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    _, status, usage = os.wait4(pid, 0)
    end, after_hash = time.monotonic_ns(), sha(engine)
    code = os.waitstatus_to_exitcode(status)
    report_error, report_hash = None, None
    if report_path is not None:
        if report_path.is_file() and 0 < report_path.stat().st_size <= 1024*1024:
            report_hash = sha(report_path)
        else:
            report_error = 'missing-empty-or-oversized-colors-report'
    failure = ('native-exec-error' if exec_error else
        'external-placement-unverified' if placement_error else
        'engine-artifact-changed' if after_hash != engine_hash else
        report_error if report_error else
        'abnormal-native-or-supervisor-termination' if code or signals else None)
    result = dict(schema='rook2-native-wait4-v1', engine=str(engine),
        engine_sha256_before=engine_hash, engine_sha256_after=after_hash,
        launcher_sha256=launcher_hash, python_executable=sys.executable,
        python_executable_sha256=sha(Path(sys.executable)), argv=[str(engine), *engine_args],
        supervisor_pid=os.getpid(), native_pid=pid, supervisor_affinity=sorted(os.sched_getaffinity(0)),
        inherited_supervisor_affinity=inherited, native_pre_exec=placement, native_post_exec=observed,
        started_utc=started_utc, start_monotonic_ns=start, reaped_monotonic_ns=end, wall_ns=end-start,
        user_cpu_s=usage.ru_utime, system_cpu_s=usage.ru_stime,
        total_cpu_s=usage.ru_utime+usage.ru_stime, maxrss_linux_kib=usage.ru_maxrss,
        minor_faults=usage.ru_minflt, major_faults=usage.ru_majflt,
        voluntary_context_switches=usage.ru_nvcsw, involuntary_context_switches=usage.ru_nivcsw,
        native_wait_status=status, native_exit_code=code, exec_error=exec_error,
        supervisor_signals=signals, failure=failure, known_single_process=True,
        expected_threads=args.thread_budget, placement_error=placement_error,
        ready_path=str(ready_path), ready_sha256=sha(ready_path) if ready_path.exists() else None,
        colors_report_path=str(report_path) if report_path else None, colors_report_sha256=report_hash,
        scope='direct native wait4 includes all joined threads and Python pre-exec prefix; original pipes',
        ownership_limit='point TID placement before first input; no continuous host-exclusivity claim')
    record(receipt, result)
    if code < 0:
        signum = -code
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
        return 128+signum
    return code if code else (125 if failure else 0)


if __name__ == '__main__':
    raise SystemExit(run())
