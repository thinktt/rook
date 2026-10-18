#!/usr/bin/env python3
"""Supervise one known-single-process native engine with direct wait4 accounting.

stdin/stdout/stderr are inherited directly by the child, with no byte relay.
Use with the released correctness replay, never its main-PID CPU benchmark:
the latter would sample this waiting supervisor instead of the engine.
External bounded supervision remains required (the released runners supply it).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_file(path, value):
    # No existing receipt is replaced, including a prior failed run.
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--known-single-process', action='store_true', required=True)
    args, engine_args = parser.parse_known_args()
    engine, receipt = args.engine.resolve(), args.record.resolve()
    if receipt.exists() or not receipt.parent.is_dir():
        parser.error('receipt must be fresh, in an existing directory')
    engine_hash = sha(engine)
    parent_affinity = sorted(os.sched_getaffinity(0))
    helpers = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
    if not (helpers & set(parent_affinity)):
        parser.error('no housekeeping CPU is available to the supervisor')
    os.sched_setaffinity(0, helpers & set(parent_affinity))
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
            # On successful exec this private pipe closes. Public descriptors
            # remain the comparator's original pipe descriptions throughout.
            os.execv(str(engine), [str(engine), *engine_args])
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
    # exec success normally precedes the first read. Short processes may have
    # already exited; such a missing observation is explicit and invalid here.
    for _ in range(50):
        try:
            native_path = os.readlink(f'/proc/{pid}/exe')
            if native_path == str(engine):
                observed = dict(path=native_path, affinity=sorted(os.sched_getaffinity(pid)),
                                pgid=os.getpgid(pid),
                                tasks=sorted(p.name for p in Path(f'/proc/{pid}/task').iterdir()))
                break
        except (FileNotFoundError, ProcessLookupError):
            break
        time.sleep(0.001)
    _, status, usage = os.wait4(pid, 0)
    end = time.monotonic_ns()
    exit_code = os.waitstatus_to_exitcode(status)
    after_hash = sha(engine)
    failure = None
    if exec_error:
        failure = 'native-exec-error'
    elif placement != dict(pid=pid, pgid=os.getpgrp(), affinity=[14]):
        failure = 'pre-exec-placement-unverified'
    elif observed is None or observed['affinity'] != [14] or observed['pgid'] != os.getpgrp():
        failure = 'native-post-exec-placement-unverified'
    elif observed['tasks'] != [str(pid)]:
        failure = 'native-threads-need-separate-review'
    elif after_hash != engine_hash:
        failure = 'engine-artifact-changed'
    elif exit_code != 0 or signals:
        failure = 'abnormal-native-or-supervisor-termination'
    record = dict(schema='rook2-native-wait4-v1', engine=str(engine),
                  engine_sha256_before=engine_hash, engine_sha256_after=after_hash,
                  launcher_sha256=sha(Path(__file__)), python_executable=sys.executable,
                  python_executable_sha256=sha(Path(sys.executable)),
                  argv=[str(engine), *engine_args], supervisor_pid=os.getpid(), native_pid=pid,
                  supervisor_affinity=sorted(os.sched_getaffinity(0)),
                  inherited_supervisor_affinity=parent_affinity,
                  native_pre_exec=placement, native_post_exec=observed,
                  started_utc=started_utc, start_monotonic_ns=start, reaped_monotonic_ns=end,
                  wall_ns=end-start, user_cpu_s=usage.ru_utime, system_cpu_s=usage.ru_stime,
                  total_cpu_s=usage.ru_utime+usage.ru_stime, maxrss_linux_kib=usage.ru_maxrss,
                  minor_faults=usage.ru_minflt, major_faults=usage.ru_majflt,
                  voluntary_context_switches=usage.ru_nvcsw,
                  involuntary_context_switches=usage.ru_nivcsw,
                  native_wait_status=status, native_exit_code=exit_code,
                  exec_error=exec_error, supervisor_signals=signals,
                  failure=failure, known_single_process=True,
                  scope='direct native child plus small Python child pre-exec prefix; no protocol relay',
                  ownership_limit='one post-exec task/affinity observation; no continuous descendant monitor',
                  behavior='separate strict comparator required', performance='reported-only')
    record_file(receipt, record)
    if exit_code < 0:
        signum = -exit_code
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
        return 128 + signum
    return exit_code if exit_code != 0 else (0 if failure is None else 125)


if __name__ == '__main__':
    raise SystemExit(run())
