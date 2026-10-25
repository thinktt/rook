#!/usr/bin/env python3
"""One focused-test/build/three-case count lane. Stop on failure; never retry."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from build import HERE, ROOT, DEFAULT_CRATE, FEATURE, HELPERS, baseline, snapshot, sha, read, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crate', type=Path, default=DEFAULT_CRATE)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--test-selector', action='append', required=True,
                        help='instrumentation owner focused counter test selector; repeat only for disjoint selections')
    parser.add_argument('--expected-focused-tests', type=int, default=4)
    args = parser.parse_args(); crate, out = args.crate.resolve(), args.output.resolve()
    assert crate != ROOT and sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    assert len(set(args.test_selector)) == len(args.test_selector)
    assert args.expected_focused_tests > 0
    assert 'ROOK2_BRANCH_WORK_CENSUS_REPORT' not in os.environ
    original, source = baseline(), snapshot(crate)
    tools = {str(p): sha(p) for p in [*(HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']),
                                    Path('/usr/bin/cargo'), Path('/usr/bin/rustc'), Path('/usr/bin/node')]}
    out.mkdir()
    state = dict(schema='rook2-beyond-two-count-pipeline-v1', complete=False, failure=None,
                 crate=str(crate), sourceBefore=source, baselineBefore=original, driverInputs=tools,
                 focusedSelectors=args.test_selector, expectedFocusedTests=args.expected_focused_tests, stages=[], active=None,
                 scope='one focused counter control lane and one generic count image; exactly3 original lives; no PGO, speed claim, retune or retry')
    started, deadline = time.monotonic_ns(), time.monotonic()+1800
    state['startMonotonicNs'] = started; write(out/'pipeline.json', state)
    env = dict(os.environ, PATH='/usr/bin:/bin', RUSTC='/usr/bin/rustc', RUSTFLAGS='-C target-cpu=x86-64', CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS', 'CARGO_BUILD_RUSTFLAGS', 'RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER', 'LLVM_PROFILE_FILE'] or key.startswith('CARGO_PROFILE_'):
            env.pop(key, None)

    def inputs():
        assert baseline() == original and snapshot(crate) == source
        assert all(sha(path) == digest for path, digest in tools.items())

    def stage(name, command, seconds):
        inputs(); state['active'] = name; write(out/'pipeline.json', state)
        start = time.monotonic_ns()
        remaining = min(seconds, deadline-time.monotonic()); assert remaining > 0
        with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen(command, cwd=crate, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=remaining)
            except BaseException:
                try:
                    os.killpg(child.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); child.wait()
                state['stages'].append(dict(stage=name, argv=command, pid=child.pid,
                    exit=child.returncode, failure='external stage deadline/interruption', elapsedNs=time.monotonic_ns()-start))
                write(out/'pipeline.json', state); raise
        row = dict(stage=name, argv=command, pid=child.pid, exit=code,
                   elapsedNs=time.monotonic_ns()-start, stdoutSha256=sha(out/(name+'.stdout')),
                   stderrSha256=sha(out/(name+'.stderr')))
        if name.startswith('counter-tests-') and code == 0:
            text = (out/(name+'.stdout')).read_text()
            names = re.findall(r'^test (\S+) \.\.\. ok$', text, re.M)
            summaries = re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;', text, re.M)
            assert len(summaries) == 1 and int(summaries[0][0]) == len(names) > 0
            assert summaries[0][1:] == ('0', '0')
            row['passedTests'] = names
        state['stages'].append(row); write(out/'pipeline.json', state)
        print(f'{name} exit {code}', flush=True)
        assert code == 0, (name, code)
        inputs(); assert time.monotonic() < deadline

    try:
        for i, selector in enumerate(args.test_selector):
            stage(f'counter-tests-{i:02d}', ['/usr/bin/cargo', 'test', '--offline', '--locked',
                '--lib', '--features', FEATURE, '--target', 'x86_64-unknown-linux-gnu', '--jobs', '4',
                '--target-dir', str(out/'test-target'), selector, '--', '--test-threads=1'], 240)
        names = [name for row in state['stages'] for name in row.get('passedTests', [])]
        assert len(names) == len(set(names)), 'focused selectors overlap; do not repeat successful controls'
        assert len(names) == args.expected_focused_tests, 'focused counter coverage differs from selected count'
        stage('build', ['/usr/bin/python3', str(HERE/'build.py'), '--crate', str(crate),
                        '--features', FEATURE, '--output', str(out/'build')], 330)
        stage('collect', ['/usr/bin/python3', str(HERE/'collect.py'), '--build', str(out/'build'),
                          '--output', str(out/'observations')], 930)
        stage('reconcile', ['/usr/bin/python3', str(HERE/'reconcile.py'), str(out/'observations')], 120)
        assert read(out/'observations/reconciled.json')['complete']
        inputs()
        state.update(complete=True, active=None, sourceAfter=snapshot(crate), baselineAfter=baseline(),
                     endMonotonicNs=time.monotonic_ns(), focusedTests=len(names))
        write(out/'pipeline.json', state)
    except BaseException as error:
        state.update(failure=repr(error), endMonotonicNs=time.monotonic_ns())
        write(out/'pipeline.json', state); raise


if __name__ == '__main__':
    main()
