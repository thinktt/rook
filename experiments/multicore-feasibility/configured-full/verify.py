#!/usr/bin/env python3
"""Finite configuration checks and two exact one-CPU original08 replays.

This separate record preserves the earlier usable-full verification unchanged.
Elapsed values describe these single observations; no timing threshold applies.
"""
import argparse
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
USABLE = HERE.parent/'usable-full'
sys.path.insert(0, str(USABLE))
from common import SPEC, audit, read, sha, write

RAW_CAP = 8*1024*1024
LIFETIME_SECONDS = 180
TOTAL_SECONDS = 420


def replay(directory, image, digest, requested, workload, oracle, total_deadline):
    directory.mkdir()
    command = [str(image), f'--threads={requested}', *read(SPEC/'replay-oracle.json')['mode']]
    setup = ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
    search_record = (workload['protocol']['searchRecord']+'\n').encode()
    handshake = b'cm_parm\n'
    inputs, outputs, errors = bytearray(), bytearray(), bytearray()
    started = time.monotonic_ns()
    deadline = min(total_deadline, time.monotonic()+LIFETIME_SECONDS)
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True,
                             preexec_fn=lambda: os.sched_setaffinity(0, {14}))
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ, outputs)
    selector.register(child.stderr, selectors.EVENT_READ, errors)
    observations = dict(count=0, minimumTasks=None, maximumTasks=0,
                        first=None, last=None, taskIds=[])
    first_reply_ns = search_start_ns = move_ns = reaped_ns = None
    communicated = False

    def observe():
        paths = sorted(Path(f'/proc/{child.pid}/task').iterdir())
        masks = {path.name: sorted(os.sched_getaffinity(int(path.name))) for path in paths}
        snapshot = dict(monotonicNs=time.monotonic_ns(), taskAffinities=masks)
        observations['count'] += 1
        observations['minimumTasks'] = min(observations['minimumTasks'] or len(masks), len(masks))
        observations['maximumTasks'] = max(observations['maximumTasks'], len(masks))
        if observations['first'] is None:
            observations['first'] = snapshot
        observations['last'] = snapshot
        observations['taskIds'] = sorted(set(observations['taskIds']) | set(masks))
        assert masks == {str(child.pid): [14]}, 'one-CPU request created another native task or changed affinity'
        assert os.readlink(f'/proc/{child.pid}/exe') == str(image)

    def send(data):
        inputs.extend(data)
        child.stdin.write(data)
        child.stdin.flush()

    def receive_until(predicate, check_tasks):
        while not predicate(bytes(outputs)):
            remaining = deadline-time.monotonic()
            assert remaining > 0, 'one-CPU external deadline'
            if check_tasks:
                observe()
            for key, _ in selector.select(min(remaining, .01)):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    if key.fileobj is child.stdout:
                        raise RuntimeError('native exited before the expected complete reply')
                    continue
                key.data.extend(chunk)
                assert len(outputs)+len(errors) <= RAW_CAP

    write(directory/'launch.json', dict(argv=command, requestedThreads=requested,
        configuredThreads=1, inheritedAllowedCpus=[14], perLifetimeSeconds=LIFETIME_SECONDS,
        engine=str(image), engineSha256=digest, nativePid=child.pid))
    failure = None
    try:
        send(handshake)
        receive_until(lambda value: value == handshake, False)
        first_reply_ns = time.monotonic_ns()
        observe()
        send(setup)
        receive_until(lambda value: value.endswith(b'cm_parm rnd=0\n'), True)
        observe()
        search_start_ns = time.monotonic_ns()
        send(search_record)
        receive_until(lambda value: any(line.startswith(b'move ') for line in value.split(b'\n')[:-1]), True)
        move_ns = time.monotonic_ns()
        observe()
        inputs.extend(b'quit\n')
        tail, final_errors = child.communicate(b'quit\n', timeout=max(.01, min(20, deadline-time.monotonic())))
        communicated = True
        reaped_ns = time.monotonic_ns()
        outputs.extend(tail)
        errors.extend(final_errors)
        assert len(outputs)+len(errors) <= RAW_CAP
        assert child.returncode == 0 and errors == b''
    except BaseException as error:
        failure = repr(error)
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if not communicated:
            tail, final_errors = child.communicate()
            outputs.extend(tail)
            errors.extend(final_errors)
        write(directory/'failure.json', dict(error=failure, nativePid=child.pid,
            exit=child.returncode, taskObservations=observations))
        raise
    finally:
        selector.close()
        for stream in [child.stdin, child.stdout, child.stderr]:
            if stream is not None and not stream.closed:
                stream.close()
        (directory/'stdin.full.raw').write_bytes(inputs)
        (directory/'stdout.full.raw').write_bytes(outputs)
        (directory/'stderr.raw').write_bytes(errors)
    assert failure is None and bytes(outputs).startswith(handshake)
    raw = dict(stdin=setup+search_record, stdout=bytes(outputs)[len(handshake):], stderr=bytes(errors))
    (directory/'stdin.raw').write_bytes(raw['stdin'])
    (directory/'stdout.raw').write_bytes(raw['stdout'])
    actual = dict(stdout=raw['stdout'].decode(), stderr=raw['stderr'].decode(),
                  exit=dict(code=child.returncode, signal=None))
    posts = audit.original_streams(actual, workload, oracle, raw)
    assert sha(image) == digest and not Path(f'/proc/{child.pid}').exists()
    result = dict(requestedThreads=requested, configuredThreads=1,
        nativePid=child.pid, exit=child.returncode, orderedPosts=posts,
        taskObservations=observations, lifetimeElapsedNs=reaped_ns-started,
        searchElapsedNs=move_ns-search_start_ns, startupReplyNs=first_reply_ns-started,
        sha256={name: sha(directory/name) for name in ['launch.json', 'stdin.full.raw',
            'stdout.full.raw', 'stdin.raw', 'stdout.raw', 'stderr.raw']},
        scope='One original08 observation; extra startup cm_parm handshake and quit are retained in full streams. Exact projected original replay; CPU14 inherited without widening. Task polling every at most 10ms is not continuous tracing. Elapsed values are descriptive, not performance qualification.')
    write(directory/'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image, out = args.engine.resolve(), args.output.resolve()
    out.mkdir()
    digest = sha(image)
    deadline = time.monotonic()+TOTAL_SECONDS
    dependencies = [Path(__file__).resolve(), USABLE/'common.py',
        HERE.parent/'full-split-production/reconcile.py', SPEC/'workloads.json', SPEC/'replay-oracle.json']
    hashes = {str(path): sha(path) for path in dependencies}
    rows = []
    for cpus in [[14], [6, 14]]:
        for value in [None, 1, 2, 8]:
            requested = 1 if value is None else value
            configured = 1 if len(cpus) == 1 else min(requested, 2)
            command = [str(image), *([] if value is None else [f'--threads={value}']), '--inspect-threads']
            result = subprocess.run(command, input=b'', capture_output=True,
                timeout=max(.01, min(20, deadline-time.monotonic())),
                preexec_fn=lambda allowed=set(cpus): os.sched_setaffinity(0, allowed))
            row = dict(argv=command, permittedCpus=cpus, requestedThreads=requested,
                       configuredThreads=configured, exit=result.returncode,
                       stdout=result.stdout.decode(), stderr=result.stderr.decode())
            rows.append(row)
            write(out/'cli-progress.json', rows)
            assert result.returncode == 0 and result.stderr == b''
            assert json.loads(result.stdout) == dict(requested_threads=requested, configured_threads=configured)
    for value in ['0', '-1', '', 'oops', '184467440737095516160']:
        command = [str(image), '--threads='+value, '--inspect-threads']
        result = subprocess.run(command, input=b'', capture_output=True,
            timeout=max(.01, min(20, deadline-time.monotonic())),
            preexec_fn=lambda: os.sched_setaffinity(0, {14}))
        rows.append(dict(argv=command, permittedCpus=[14], exit=result.returncode,
                         stdout=result.stdout.decode(), stderr=result.stderr.decode()))
        write(out/'cli-progress.json', rows)
        assert result.returncode != 0 and result.stdout == b'' and result.stderr
    workload = next(case for case in read(SPEC/'workloads.json')['cases'] if case['id'] == 'profile-08')
    oracle = next(case for case in read(SPEC/'replay-oracle.json')['cases'] if case['id'] == 'profile-08')
    lives = [replay(out/f'request{requested}', image, digest, requested, workload, oracle, deadline)
             for requested in [1, 2]]
    assert sha(image) == digest and all(sha(Path(path)) == value for path, value in hashes.items())
    result = dict(schema='rook2-configured-full-verification-v1', complete=True,
        engine=str(image), engineSha256=digest, inputSha256=hashes,
        totalLimitSeconds=TOTAL_SECONDS, perLifetimeLimitSeconds=LIFETIME_SECONDS,
        cli=rows, oneCpu=lives,
        scope='Configuration-time affinity policy and exactly two one-CPU original08 lives; no repeated timing, bad-mode rerun, or modification of earlier evidence.')
    write(out/'result.json', result)
    print(json.dumps(dict(complete=True, cliControls=len(rows), originalLives=len(lives))))


if __name__ == '__main__':
    main()
