#!/usr/bin/env python3
"""Finite CLI and inherited one/two-CPU original08 correctness controls."""
import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import HELPERS, SPEC, audit, read, sha, stop_owned, write


def clean_environment():
    return {key: value for key, value in os.environ.items()
            if not key.startswith('ROOK2_') and key != 'LLVM_PROFILE_FILE'}


def affinity_replay(image, out, mask, configured):
    workload = next(c for c in read(SPEC/'workloads.json')['cases'] if c['id'] == 'profile-08')
    oracle_file = read(SPEC/'replay-oracle.json')
    oracle = next(c for c in oracle_file['cases'] if c['id'] == 'profile-08')
    options = ['--threads=3', '--owner-local-inventory', '--q-owner-local-inventory', *oracle_file['mode']]
    command = [str(image), *options]
    setup = ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
    prefix = b'cm_parm\n'
    sent, output = bytearray(), bytearray()
    started = time.monotonic_ns()
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=clean_environment(), start_new_session=True,
        preexec_fn=lambda: os.sched_setaffinity(0, set(mask)))
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ)
    deadline = time.monotonic()+180
    masks, errors = None, b''

    def send(data):
        child.stdin.write(data); child.stdin.flush(); sent.extend(data)

    def receive_until(predicate):
        while not predicate(bytes(output)):
            remaining = deadline-time.monotonic()
            assert remaining > 0, 'affinity control deadline'
            if not selector.select(min(remaining, 1)):
                continue
            chunk = os.read(child.stdout.fileno(), 65536)
            assert chunk, 'native exited before expected affinity-control reply'
            output.extend(chunk)
            assert len(output) <= 8*1024*1024

    try:
        send(prefix)
        receive_until(lambda data: data == prefix)
        tids = sorted(Path(f'/proc/{child.pid}/task').iterdir())
        masks = {p.name: sorted(os.sched_getaffinity(int(p.name))) for p in tids}
        assert len(masks) == configured and all(value == mask for value in masks.values())
        send(setup)
        receive_until(lambda data: data.endswith(b'cm_parm rnd=0\n'))
        send(b'go\n')
        receive_until(lambda data: any(line.startswith(b'move ') for line in data.splitlines()))
        sent.extend(b'quit\n')
        tail, errors = child.communicate(b'quit\n', timeout=max(.01, min(20, deadline-time.monotonic())))
        output.extend(tail)
        assert child.returncode == 0 and errors == b''
    except BaseException as error:
        stop_owned(child)
        write(out/'failure.json', dict(error=repr(error), nativePid=child.pid,
            masks=masks, exit=child.returncode))
        raise
    finally:
        selector.close()
        for stream in [child.stdin, child.stdout, child.stderr]:
            if stream is not None and not stream.closed:
                stream.close()
        (out/'stdin.raw').write_bytes(sent)
        (out/'stdout.raw').write_bytes(output)
        (out/'stderr.raw').write_bytes(errors)
    # Project the extra startup handshake and end(data) quit away explicitly.
    raw = dict(stdin=setup+b'go\n', stdout=bytes(output)[len(prefix):], stderr=errors)
    actual = dict(stdout=raw['stdout'].decode(), stderr=errors.decode(),
                  exit=dict(code=child.returncode, signal=None))
    posts = audit.original_streams(actual, workload, oracle, raw)
    assert not Path(f'/proc/{child.pid}').exists()
    return dict(argv=command, nativePid=child.pid, requestedThreads=3,
        configuredThreads=configured, inheritedMask=mask, taskAffinities=masks,
        orderedPosts=posts, elapsedNs=time.monotonic_ns()-started,
        sha256={name: sha(out/name) for name in ['stdin.raw', 'stdout.raw', 'stderr.raw']},
        scope='original08 with extra startup cm_parm; inherited CPU permission and exact output/liveness, not timing')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image, out = args.engine.resolve(), args.output.resolve()
    out.mkdir()
    assert set(os.sched_getaffinity(0)) == HELPERS
    digest = sha(image)
    rows = []
    positive = [([], 1, 1, sorted(HELPERS)), (['--threads=1'], 1, 1, sorted(HELPERS)),
        (['--threads=2'], 2, 2, sorted(HELPERS)), (['--threads=3'], 3, 3, sorted(HELPERS)),
        (['--threads=8'], 8, 3, sorted(HELPERS)),
        (['--threads=3'], 3, 1, [14]), (['--threads=3'], 3, 2, [6, 14]),
        (['--threads=8'], 8, 2, [6, 14]),
        (['--threads=3','--owner-local-inventory','--q-owner-local-inventory'],3,3,sorted(HELPERS))]
    for options, requested, configured, mask in positive:
        command = [str(image), *options, '--inspect-threads']
        reply = subprocess.run(command, input=b'', capture_output=True, timeout=20,
            env=clean_environment(), preexec_fn=lambda mask=mask: os.sched_setaffinity(0, set(mask)))
        row = dict(argv=command, inheritedMask=mask, exit=reply.returncode,
            stdout=reply.stdout.decode(), stderr=reply.stderr.decode())
        rows.append(row); write(out/'cli-progress.json', rows)
        assert reply.returncode == 0 and reply.stderr == b''
        assert json.loads(reply.stdout) == dict(requested_threads=requested, configured_threads=configured)
    for value in ['0', '-1', '', 'oops', '184467440737095516160']:
        command = [str(image), '--threads='+value, '--inspect-threads']
        reply = subprocess.run(command, input=b'', capture_output=True, timeout=20, env=clean_environment())
        rows.append(dict(argv=command, inheritedMask=sorted(HELPERS), exit=reply.returncode,
                         stdout=reply.stdout.decode(), stderr=reply.stderr.decode()))
        write(out/'cli-progress.json', rows)
        assert reply.returncode != 0 and reply.stdout == b'' and reply.stderr
    probes = []
    for name, mask, configured in [('one-cpu', [14], 1), ('two-cpu', [6, 14], 2)]:
        directory = out/name; directory.mkdir()
        probes.append(affinity_replay(image, directory, mask, configured))
    assert sha(image) == digest
    result = dict(schema='rook2-completion-fence-focused-cli-v1', complete=True,
        engine=str(image), engineSha256=digest, cli=rows, affinityReplays=probes)
    write(out/'result.json', result)
    print(json.dumps(dict(complete=True, cliControls=len(rows), affinityReplayLives=len(probes))))


if __name__ == '__main__':
    main()
