#!/usr/bin/env python3
"""Direct wait4 accounting for the declared 1/2/4-thread preparation pilot.

Native stdin/stdout/stderr are inherited without a relay. The optional research
report uses a dedicated fresh path in the native child's environment, preserving
the unchanged released replay's complete stdout/stderr/exit assertions.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time


HELPERS = {0, 1, 8, 9, 10, 11, 12, 13}
WORKERS = {1: [], 2: [6], 4: [6, 4, 2]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_json(path):
    def invalid(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(path.read_text(), parse_constant=invalid)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--known-single-process', action='store_true', required=True)
    parser.add_argument('--thread-budget', type=int, choices=[1, 2, 4], required=True)
    parser.add_argument('--preparation-report', type=Path)
    args, engine_args = parser.parse_known_args()
    engine, receipt = args.engine.resolve(), args.record.resolve()
    report = args.preparation_report.resolve() if args.preparation_report else None
    if receipt.exists() or not receipt.parent.is_dir():
        parser.error('receipt must be fresh, in an existing directory')
    if report and (report.exists() or not report.parent.is_dir()):
        parser.error('preparation report must be fresh, in an existing directory')
    engine_hash = sha(engine)
    parent_affinity = sorted(os.sched_getaffinity(0))
    helpers = HELPERS & set(parent_affinity)
    if not helpers:
        parser.error('no declared helper CPU available to the supervisor')
    os.sched_setaffinity(0, helpers)
    native_env = dict(os.environ)
    native_env.pop('ROOK2_CHILD_PREPARATION_REPORT', None)
    if report:
        native_env['ROOK2_CHILD_PREPARATION_REPORT'] = str(report)
    started_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    pid = None
    signals = []

    def forward(signum, _frame):
        signals.append(signum)
        if pid:
            try:
                os.kill(pid, signum)
            except ProcessLookupError:
                pass

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, forward)
    start = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                signal.signal(signum, signal.SIG_DFL)
            os.sched_setaffinity(0, {14})
            placement = dict(pid=os.getpid(), pgid=os.getpgrp(),
                             affinity=sorted(os.sched_getaffinity(0)))
            os.write(write_fd, (json.dumps(placement) + '\n').encode('ascii'))
            os.execve(str(engine), [str(engine), *engine_args], native_env)
        except BaseException as error:
            os.write(write_fd, (json.dumps(dict(exec_error=repr(error))) + '\n').encode('ascii'))
            os._exit(127)
    os.close(write_fd)
    private = bytearray()
    while True:
        data = os.read(read_fd, 4096)
        if not data:
            break
        private.extend(data)
        if len(private) > 8192:
            os.kill(pid, signal.SIGKILL)
            break
    os.close(read_fd)
    placement = None
    exec_error = None
    for line in private.splitlines():
        value = json.loads(line)
        if 'exec_error' in value:
            exec_error = value['exec_error']
        else:
            placement = value
    observed = None
    # Pool creation is part of CLI setup before the first protocol read. This
    # is a point observation, not a claim of continuous affinity monitoring.
    for _ in range(100):
        try:
            native_path = os.readlink(f'/proc/{pid}/exe')
            if native_path == str(engine):
                tasks = sorted(p.name for p in Path(f'/proc/{pid}/task').iterdir())
                affinities = {tid: sorted(os.sched_getaffinity(int(tid))) for tid in tasks}
                worker_cpus = sorted(cpus[0] for tid, cpus in affinities.items()
                                     if tid != str(pid) and len(cpus) == 1)
                if (len(tasks) == args.thread_budget and affinities.get(str(pid)) == [14]
                        and worker_cpus == sorted(WORKERS[args.thread_budget])):
                    observed = dict(path=native_path, affinity=sorted(os.sched_getaffinity(pid)),
                                    pgid=os.getpgid(pid), tasks=tasks, task_affinities=affinities)
                    break
        except (FileNotFoundError, ProcessLookupError):
            break
        time.sleep(.001)
    _, status, usage = os.wait4(pid, 0)
    end = time.monotonic_ns()
    exit_code = os.waitstatus_to_exitcode(status)
    after_hash = sha(engine)
    prep = prep_hash = prep_error = None
    if report:
        try:
            if report.stat().st_size > 1_048_576:
                raise ValueError('preparation report byte cap')
            prep = strict_json(report)
            if not isinstance(prep, dict):
                raise ValueError('preparation report is not an object')
            prep_hash = sha(report)
        except (OSError, ValueError) as error:
            prep_error = str(error)
    failure = None
    if exec_error:
        failure = 'native-exec-error'
    elif placement != dict(pid=pid, pgid=os.getpgrp(), affinity=[14]):
        failure = 'pre-exec-placement-unverified'
    elif observed is None or observed['affinity'] != [14] or observed['pgid'] != os.getpgrp():
        failure = 'native-post-exec-placement-unverified'
    elif after_hash != engine_hash:
        failure = 'engine-artifact-changed'
    elif exit_code != 0 or signals:
        failure = 'abnormal-native-or-supervisor-termination'
    elif prep_error:
        failure = 'preparation-report-invalid'
    record = dict(schema='rook2-child-preparation-wait4-v1', engine=str(engine),
                  engine_sha256_before=engine_hash, engine_sha256_after=after_hash,
                  launcher_sha256=sha(Path(__file__)), python_executable=sys.executable,
                  python_executable_sha256=sha(Path(sys.executable)),
                  argv=[str(engine), *engine_args], supervisor_pid=os.getpid(), native_pid=pid,
                  supervisor_affinity=sorted(os.sched_getaffinity(0)),
                  inherited_supervisor_affinity=parent_affinity,
                  native_pre_exec=placement, native_post_exec=observed,
                  expected_threads=args.thread_budget, expected_worker_cpus=WORKERS[args.thread_budget],
                  preparation_report_path=str(report) if report else None,
                  preparation_report_sha256=prep_hash, preparation_report=prep,
                  preparation_report_error=prep_error,
                  started_utc=started_utc, start_monotonic_ns=start, reaped_monotonic_ns=end,
                  wall_ns=end-start, user_cpu_s=usage.ru_utime, system_cpu_s=usage.ru_stime,
                  total_cpu_s=usage.ru_utime+usage.ru_stime, maxrss_linux_kib=usage.ru_maxrss,
                  minor_faults=usage.ru_minflt, major_faults=usage.ru_majflt,
                  voluntary_context_switches=usage.ru_nvcsw,
                  involuntary_context_switches=usage.ru_nivcsw,
                  native_wait_status=status, native_exit_code=exit_code,
                  exec_error=exec_error, supervisor_signals=signals, failure=failure,
                  known_single_process=True,
                  scope='direct native child and all threads plus small Python child pre-exec prefix; no protocol relay',
                  ownership_limit='one post-exec task-affinity observation; not continuous isolation verification',
                  behavior='unchanged released strict comparator required', performance='reported-only')
    with receipt.open('x') as stream:
        json.dump(record, stream, indent=2, allow_nan=False)
        stream.write('\n')
    if exit_code < 0:
        signum = -exit_code
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
        return 128 + signum
    return exit_code if exit_code != 0 else (0 if failure is None else 125)


if __name__ == '__main__':
    raise SystemExit(run())
