#!/usr/bin/env python3
"""Observe one native process without relaying protocol data or changing its exit."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import time


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine', required=True, type=Path)
    p.add_argument('--record', required=True, type=Path)
    p.add_argument('--known-single-process', required=True, action='store_true')
    a, options = p.parse_known_args()
    assert os.sched_getaffinity(0) == {14} and not a.record.exists()
    before = sha(a.engine)
    rfd, wfd = os.pipe2(os.O_CLOEXEC)
    start = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        os.close(rfd)
        try:
            os.sched_setaffinity(0, {14})
            os.write(wfd, (json.dumps(dict(pid=os.getpid(), pgid=os.getpgrp(), affinity=[14]))+'\n').encode())
            os.execv(str(a.engine), [str(a.engine), *options])
        except BaseException as error:
            os.write(wfd, (json.dumps(dict(execError=str(error)))+'\n').encode())
            os._exit(127)
    os.close(wfd)
    signals = []
    def forward(sig, _):
        signals.append(sig)
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]:
        signal.signal(sig, forward)
    with os.fdopen(rfd, 'rb') as stream:
        startup = [json.loads(line) for line in stream.read().splitlines()]
    pre = next((x for x in startup if 'affinity' in x), None)
    error = next((x['execError'] for x in startup if 'execError' in x), None)
    observed = None
    try:
        observed = dict(path=os.readlink(f'/proc/{pid}/exe'), affinity=sorted(os.sched_getaffinity(pid)),
                        tasks=[x.name for x in Path(f'/proc/{pid}/task').iterdir()])
    except (ProcessLookupError, FileNotFoundError, PermissionError):
        pass
    waited, status, usage = os.wait4(pid, 0)
    after = sha(a.engine)
    failure = None
    if error or pre is None or before != after or signals:
        failure = 'exec, placement, artifact or supervisor failure'
    elif pre['affinity'] != [14] or (observed and observed['affinity'] != [14]):
        failure = 'unexpected placement'
    code = os.waitstatus_to_exitcode(status)
    record = dict(engine_sha256_before=before, engine_sha256_after=after,
        supervisor_pid=os.getpid(), native_pid=pid, supervisor_affinity=[14],
        native_pre_exec=pre, native_post_exec=observed, exec_error=error,
        native_exit_code=code, wait_status=status, waited_pid=waited, failure=failure,
        argv=[str(a.engine), *options], supervisor_signals=signals,
        total_cpu_s=usage.ru_utime+usage.ru_stime, wall_ns=time.monotonic_ns()-start,
        recorderSha256=sha(Path(__file__)),
        observationLimit='Short children may finish before the post-exec point observation; direct exec/wait remains recorded.')
    with a.record.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    if code < 0:
        sig = -code
        signal.signal(sig, signal.SIG_DFL)
        os.kill(os.getpid(), sig)
    return code if code else (125 if failure else 0)


if __name__ == '__main__':
    raise SystemExit(main())
