#!/usr/bin/env python3
"""One supervised focused/build/48-life lane; stop on failure, no automatic retry."""
import argparse
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

from common import HERE, ROOT, HELPERS, read, sha, write

CONTROL = Path('/home/legolas/rook2-experiments/reversed-full-20261024-01/control/rook2')
PGO = Path('/home/legolas/rook2-experiments/full-split-production-20261024-01/rook2-pgo')
PROFILE = PGO.parent/'training/merged.profdata'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir()
    assert set(os.sched_getaffinity(0)) == HELPERS
    env = dict(os.environ, PATH='/usr/bin:/bin', CARGO_TARGET_DIR=str(out/'test-target'))
    env.pop('LLVM_PROFILE_FILE', None)
    pins = {str(p): sha(p) for p in [CONTROL, PGO, PROFILE]}
    assert pins[str(CONTROL)] == '64e01d986242f43f2063887b164e06e8201460fd5aefca5d6494a2f4b3634323'
    assert pins[str(PGO)] == 'a977bb0031b1beeb6fb50f8c391968f6e2d959ae86d648727442bdf027c88763'
    assert pins[str(PROFILE)] == 'f9eefbd025c74a3247449c10fa0074fc5f178bcc49f1d623bed36cd9dcbdcadc'
    source = [ROOT/'Cargo.toml', ROOT/'Cargo.lock', *sorted((ROOT/'src').rglob('*.rs'))]
    pins.update({str(p): sha(p) for p in source})
    pins.update({str(p): sha(p) for p in HERE.rglob('*') if p.is_file() and p.suffix in ['.py','.mjs','.md']})
    state = dict(complete=False, stages=[], inputs=pins)
    write(out/'pipeline.json', state)

    def stage(name, command, limit, tests=None):
        state['active'] = name
        write(out/'pipeline.json', state)
        started = time.monotonic_ns()
        with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                     start_new_session=True)
            try:
                code = child.wait(timeout=limit)
            except BaseException:
                os.killpg(child.pid, signal.SIGINT)
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); child.wait()
                raise
        row = dict(stage=name, argv=[str(x) for x in command], pid=child.pid, exit=code,
                   elapsedNs=time.monotonic_ns()-started,
                   stdoutSha256=sha(out/(name+'.stdout')), stderrSha256=sha(out/(name+'.stderr')))
        state['stages'].append(row)
        write(out/'pipeline.json', state)
        print(name, code, flush=True)
        assert code == 0, (name, code)
        if tests is not None:
            found = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',
                               (out/(name+'.stdout')).read_text())
            assert found == [(str(tests), '0')], (name, found, tests)
            row['passedTests'] = tests
            write(out/'pipeline.json', state)

    try:
        for name, selector, count in [
            ('worker', 'evaluator_worker::lifecycle_tests', 8),
            ('numerical', 'evaluator::parallel_tests', 7),
            ('scope', 'evaluator::lifecycle_tests', 3),
        ]:
            stage(name, ['/usr/bin/cargo','test','--lib',selector,'--','--test-threads=1'], 300, count)
        stage('delayed', ['/usr/bin/cargo','test','--lib',
              'evaluator_worker::lifecycle_tests::helper_delay_beyond_ten_seconds_preserves_result_and_lifecycle',
              '--','--ignored','--exact','--test-threads=1'], 60, 1)
        stage('cli-parser', ['/usr/bin/cargo','test','--bin','rook2',
              'tests::thread_argument_requires_a_positive_representable_integer',
              '--','--exact','--test-threads=1'], 300, 1)
        stage('generic-build', ['/usr/bin/python3',str(ROOT/'tools/build.py'),
              '--mode','generic','--bin','rook2','--jobs','4','--output',str(out/'build')], 300)
        receipt = read(out/'build/receipt.json')
        built = Path(receipt['binary_output']['path'])
        assert sha(built) == receipt['binary_output']['sha256']
        candidate = out/'rook2-generic'
        shutil.copy2(built,candidate)
        assert sha(candidate) == sha(built)
        state['binary'] = dict(path=str(candidate), sha256=sha(candidate), bytes=candidate.stat().st_size)
        stage('cli-affinity', ['/usr/bin/python3',str(HERE/'focused.py'),
              '--engine',str(candidate),'--output',str(out/'focused')], 240)
        stage('collection', ['/usr/bin/python3',str(HERE/'collect.py'),
              '--control',str(CONTROL),'--candidate',str(candidate),'--build',str(out/'build'),
              '--output',str(out/'pilot')], 1850)
        stage('reconcile', ['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'pilot')], 120)
        assert all(sha(Path(p)) == h for p,h in pins.items())
        state.update(complete=True, active=None)
        write(out/'pipeline.json',state)
        print('complete: focused checks, generic build,48 replay lives+3 idle; no PGO/adoption',flush=True)
    except BaseException as error:
        state['failure'] = repr(error)
        write(out/'pipeline.json',state)
        raise


if __name__ == '__main__':
    main()
