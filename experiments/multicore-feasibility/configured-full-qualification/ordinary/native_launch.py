#!/usr/bin/python3
"""Exec the frozen placement supervisor, or observe one unchanged no-search control.

The released synchronous seed controls can terminate before a task observation.
Those controls keep their original eager input and have no placement guarantee.
Actual searches use the frozen wait4 supervisor plus an external first-input gate.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
ACCOUNT = HERE.parents[1]/'usable-full/account_threads.py'
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    image, threads, separator, *options = sys.argv[1:]
    assert separator == '--' and threads in ['--threads=1', '--threads=2']
    assert options in [[], ['--diagnostic-seed-command']]
    image = Path(image).resolve()
    directory = Path(os.environ['ROOK2_FOCUSED_NATIVE_DIR'])
    record = directory/f'{os.getpid()}.json'
    assert directory.is_dir() and not record.exists()
    assert sorted(os.sched_getaffinity(0)) == HELPERS
    budget = int(threads[-1])
    if os.environ.get('ROOK2_QUALIFICATION_FAST_CONTROL') != '1':
        os.execv('/usr/bin/python3', ['/usr/bin/python3', str(ACCOUNT), '--engine', str(image),
            '--record', str(record), '--known-single-process', '--thread-budget', str(budget), threads, *options])
    row = dict(schema='rook2-qualification-fast-control-wait4-v1', supervisor_pid=os.getpid(),
        supervisor_affinity=HELPERS, image=str(image), image_sha256_before=sha(image),
        argv=[str(image), threads, *options], requested_threads=budget,
        signals=[], exec_error=None, failure=None, post_exec=None,
        post_exec_unavailable=None, placement_guaranteed=False,
        scope='Original synchronous no-search seed input; actual/null point observation only, without a placement or threaded-search claim.')
    started = time.monotonic_ns()
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            os.sched_setaffinity(0, {6, 14})
            os.write(write_fd, (json.dumps(dict(pre_exec=dict(pid=os.getpid(), pgid=os.getpgrp(),
                affinity=sorted(os.sched_getaffinity(0)))))+'\n').encode())
            os.execv(str(image), row['argv'])
        except BaseException as error:
            os.write(write_fd, (json.dumps(dict(exec_error=repr(error)))+'\n').encode())
            os._exit(127)
    os.close(write_fd)
    row['native_pid'] = pid

    def forward(number, _frame):
        row['signals'].append(number)
        try:
            os.kill(pid, number)
        except ProcessLookupError:
            pass

    for number in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]:
        signal.signal(number, forward)
    with os.fdopen(read_fd, 'rb') as stream:
        startup = stream.read(8193)
    assert len(startup) <= 8192
    for line in startup.splitlines():
        row.update(json.loads(line))
    try:
        tasks = sorted(int(path.name) for path in Path(f'/proc/{pid}/task').iterdir())
        observation = dict(exe=os.readlink(f'/proc/{pid}/exe'),
            argv=Path(f'/proc/{pid}/cmdline').read_bytes().rstrip(b'\0').decode().split('\0'),
            tasks=tasks, task_affinities={str(tid): sorted(os.sched_getaffinity(tid)) for tid in tasks})
        if observation['exe'] == str(image) and observation['argv'] == row['argv'] and tasks:
            row['post_exec'] = observation
        else:
            row['post_exec_partial'] = observation
            row['post_exec_unavailable'] = 'IncompletePostExecSnapshot'
    except (FileNotFoundError, ProcessLookupError, PermissionError) as error:
        row['post_exec_unavailable'] = type(error).__name__
    waited, status, usage = os.wait4(pid, 0)
    row.update(waited_pid=waited, wait_status=status,
        native_exit_code=os.WEXITSTATUS(status) if os.WIFEXITED(status) else None,
        native_signal=os.WTERMSIG(status) if os.WIFSIGNALED(status) else None,
        image_sha256_after=sha(image), wall_ns=time.monotonic_ns()-started,
        user_cpu_s=usage.ru_utime, system_cpu_s=usage.ru_stime, maxrss_linux_kib=usage.ru_maxrss)
    if row['exec_error'] or row['image_sha256_before'] != row['image_sha256_after']:
        row['failure'] = 'native exec or image identity failure'
    put(record, row)
    return row['native_exit_code'] if row['native_exit_code'] is not None else 128+row['native_signal']


if __name__ == '__main__':
    raise SystemExit(main())
