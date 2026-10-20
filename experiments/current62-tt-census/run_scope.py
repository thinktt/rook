#!/usr/bin/env python3
"""Finite build/tests only for the selected TT count-only diagnostic preparation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

W = Path('/home/legolas/rook2-experiments/tt-probe-store-census-20261020-01/worktree')
B = Path('/home/legolas/rook2-experiments/tt-probe-store-census-20261020-01')
R = Path('/home/legolas/rook2')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def source_check():
    before = json.loads((B / 'source-before.json').read_text())
    for name, expected in (before['source_sha256'] | before['tool_sha256']).items():
        if sha(W / name) != expected:
            raise ValueError('frozen source changed: ' + name)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['tests', 'build'])
    a = ap.parse_args()
    assert os.sched_getaffinity(0) == H
    assert os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp'
    source_check()
    out = B / (a.stage + '-execution')
    out.mkdir()
    if a.stage == 'tests':
        command = ['/usr/bin/cargo', 'test', '--offline', '--locked', '--lib',
                   '--target-dir', str(B / 'test-target'), '--', '--test-threads=4']
    else:
        command = ['/usr/bin/python3', str(R / 'tools/build.py'), '--crate', str(W),
                   '--mode', 'generic', '--bin', 'rook2', '--jobs', '4',
                   '--output', str(B / 'build')]
    save(out / 'command.json', {'argv': command, 'cwd': str(W), 'affinity': sorted(H),
                               'timeout_s': 240, 'cleanup_s': 5,
                               'scope': 'Known Cargo/build process group; no engine benchmarks'})
    started = time.monotonic()
    failure = None
    with (out / 'stdout').open('xb') as stdout, (out / 'stderr').open('xb') as stderr:
        p = subprocess.Popen(command, cwd=W, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = p.wait(timeout=240)
        except BaseException as error:
            failure = repr(error)
            os.killpg(p.pid, signal.SIGKILL)
            code = p.wait(timeout=5)
    source_check()
    save(out / 'child-terminal.json', {'actual_child_exit_observed': True, 'exit_code': code,
                                     'failure': failure, 'elapsed_s': time.monotonic() - started,
                                     'log_bytes': {n: (out / n).stat().st_size for n in ('stdout', 'stderr')},
                                     'source_unchanged': True,
                                     'actual_outer_tool_terminal_observed': False})
    print(json.dumps({'stage': a.stage, 'exit_code': code, 'failure': failure,
                      'stdout_tail': (out / 'stdout').read_text()[-2000:],
                      'stderr_tail': (out / 'stderr').read_text()[-1500:]}))
    if code or failure:
        raise SystemExit(1)
    if a.stage == 'build':
        receipt = json.loads((B / 'build/receipt.json').read_text())
        assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot'
        assert receipt['pgo']['mode'] == 'none' and receipt['rust_flags'] == ['-C', 'target-cpu=x86-64']
        binary = Path(receipt['binary_output']['path'])
        exact = B / 'build/rook2-exact'
        exact.write_bytes(binary.read_bytes())
        exact.chmod(0o555)
        assert sha(exact) == receipt['binary_output']['sha256']
        save(B / 'build/frozen-image.json', {'path': str(exact), 'sha256': sha(exact),
                                          'bytes': exact.stat().st_size, 'mode': '0555'})


if __name__ == '__main__':
    main()
