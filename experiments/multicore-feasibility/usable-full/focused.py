#!/usr/bin/env python3
"""Finite CLI and one-permitted-CPU controls, separate from performance samples."""
import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import time

from common import SPEC, audit, read, sha, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image, out = args.engine.resolve(), args.output.resolve()
    out.mkdir()
    digest = sha(image)
    rows = []
    for options, requested, configured in [([], 1, 1), (['--threads=1'], 1, 1),
            (['--threads=2'], 2, 2), (['--threads=8'], 8, 2)]:
        command = [str(image), *options, '--inspect-threads']
        result = subprocess.run(command, input=b'', capture_output=True, timeout=20)
        row = dict(argv=command, exit=result.returncode,
                   stdout=result.stdout.decode(), stderr=result.stderr.decode())
        rows.append(row)
        write(out/'cli-progress.json', rows)
        assert result.returncode == 0 and result.stderr == b''
        assert json.loads(result.stdout) == dict(requested_threads=requested,
                                                 configured_threads=configured)
    for value in ['0', '-1', '', 'oops', '184467440737095516160']:
        command = [str(image), '--threads='+value, '--inspect-threads']
        result = subprocess.run(command, input=b'', capture_output=True, timeout=20)
        rows.append(dict(argv=command, exit=result.returncode,
                         stdout=result.stdout.decode(), stderr=result.stderr.decode()))
        write(out/'cli-progress.json', rows)
        assert result.returncode != 0 and result.stdout == b'' and result.stderr

    workload = next(c for c in read(SPEC/'workloads.json')['cases'] if c['id'] == 'profile-08')
    oracle = next(c for c in read(SPEC/'replay-oracle.json')['cases'] if c['id'] == 'profile-08')
    options = ['--threads=2', *read(SPEC/'replay-oracle.json')['mode']]
    command = [str(image), *options]
    started = time.monotonic_ns()
    output = bytearray()
    # The child inherits one CPU; neither engine nor supervisor widens its mask.
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True,
                             preexec_fn=lambda: os.sched_setaffinity(0, {14}))
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ)
    deadline = time.monotonic()+180

    def receive_until(predicate):
        while not predicate(bytes(output)):
            remaining = deadline-time.monotonic()
            assert remaining > 0, 'one-CPU external deadline'
            if not selector.select(min(remaining, 1)):
                continue
            chunk = os.read(child.stdout.fileno(), 65536)
            assert chunk, 'one-CPU native exited before reply'
            output.extend(chunk)
            assert len(output) <= 8*1024*1024

    masks = None
    try:
        child.stdin.write(b'cm_parm\n'); child.stdin.flush()
        receive_until(lambda b: b == b'cm_parm\n')
        tids = sorted(Path(f'/proc/{child.pid}/task').iterdir())
        masks = {p.name: sorted(os.sched_getaffinity(int(p.name))) for p in tids}
        assert len(masks) == 2 and all(mask == [14] for mask in masks.values())
        setup = ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
        child.stdin.write(setup); child.stdin.flush()
        receive_until(lambda b: b.endswith(b'cm_parm rnd=0\n'))
        child.stdin.write(b'go\n'); child.stdin.flush()
        receive_until(lambda b: any(line.startswith(b'move ') for line in b.splitlines()))
        tail, errors = child.communicate(b'quit\n', timeout=max(.01, min(20, deadline-time.monotonic())))
        output.extend(tail)
        assert child.returncode == 0 and errors == b''
    except BaseException as error:
        # No engine recovery/retry: discharge this owned process only.
        try: os.killpg(child.pid, 9)
        except ProcessLookupError: pass
        child.wait()
        write(out/'failure.json', dict(error=repr(error), nativePid=child.pid,
                                       masks=masks, exit=child.returncode))
        raise
    finally:
        selector.close()
        for stream in [child.stdin, child.stdout, child.stderr]:
            if stream is not None and not stream.closed: stream.close()
        (out/'one-cpu-stdout.raw').write_bytes(output)
    raw = dict(stdin=setup+b'go\n', stdout=bytes(output)[len(b'cm_parm\n'):], stderr=errors)
    actual = dict(stdout=raw['stdout'].decode(), stderr=errors.decode(),
                  exit=dict(code=child.returncode, signal=None))
    posts = audit.original_streams(actual, workload, oracle, raw)
    assert sha(image) == digest and not Path(f'/proc/{child.pid}').exists()
    result = dict(complete=True, engine=str(image), engineSha256=digest,
                  cli=rows, oneCpu=dict(argv=command, nativePid=child.pid,
                    allowedTaskMasks=masks, exit=child.returncode, orderedPosts=posts,
                    elapsedNs=time.monotonic_ns()-started,
                    stdoutSha256=sha(out/'one-cpu-stdout.raw'),
                    scope='Extra startup cm_parm handshake, original08 projected replay, inherited CPU14 for both threads; liveness/correctness, not timing.'))
    write(out/'result.json', result)
    print(json.dumps(dict(complete=True, cliControls=len(rows), oneCpuPosts=posts)))


if __name__ == '__main__':
    main()
