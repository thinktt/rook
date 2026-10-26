#!/usr/bin/env python3
"""Selected focused controls, one build, two serial simulations, one offline audit."""
import argparse
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, FEATURE, DEFAULT_CRATE, BASE_HELPER, FROZEN_TOOLS, baseline, snapshot, read, write, sha
from collect import policy

EXTRA_SELECTORS = ['branch_journal::prefix_tests::', 'hierarchical_recovery::tests::', 'remembered::sparse_tests::', 'branch_journal::range_tests::',
                   'remembered::tests::', 'branch_transactions::focused_tests::']
EXPECTED_TESTS = dict(zip(['hierarchical_recovery::prefix_tests::', *EXTRA_SELECTORS], [6, 5, 4, 3, 5, 10, 1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crate', type=Path, default=DEFAULT_CRATE)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--critical-selector', default='hierarchical_recovery::prefix_tests::')
    parser.add_argument('--expected-critical-tests', type=int, default=6)
    parser.add_argument('--test-selector', action='append', help='explicit selected disjoint old/sparse control selectors; defaults to the six selected existing/journal modules')
    args = parser.parse_args(); crate, out, chosen_path = args.crate.resolve(), args.output.resolve(), args.policy.resolve()
    chosen, source, original = policy(chosen_path), snapshot(crate), baseline()
    assert crate != ROOT and sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    assert args.critical_selector == 'hierarchical_recovery::prefix_tests::'
    assert args.expected_critical_tests == 6
    extras = args.test_selector if args.test_selector is not None else EXTRA_SELECTORS
    assert extras == EXTRA_SELECTORS, 'selected old/sparse control modules differ'
    selectors = [args.critical_selector, *extras]
    assert len(selectors) == len(set(selectors)) and all(selectors)
    pins = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']]
    pins += [BASE_HELPER, *FROZEN_TOOLS, ROOT/'tools/account_native.py', chosen_path, Path('/usr/bin/rustc'), Path('/usr/bin/cargo')]
    identities = {str(path): sha(path) for path in pins}
    out.mkdir(); shutil.copy2(chosen_path, out/'policy.json')
    state = dict(schema='rook2-consumed-prefix-pipeline-v1', complete=False, failure=None, active=None,
        crate=str(crate), trialBase='d3c4a7186ab58ab7fb08e5214b3ea703132bdf43', sourceBefore=source, baselineBefore=original,
        policy=chosen, policyPath=str(chosen_path), policySha256=sha(chosen_path), driverInputs=identities,
        selectors=selectors, expectedTests=EXPECTED_TESTS, criticalSelector=args.critical_selector, expectedCriticalTests=6, stages=[],
        startMonotonicNs=time.monotonic_ns(),
        scope='one serial consumed-prefix discriminator; no policy sweep, parallel workers, standard wire replay, PGO or qualification')
    write(out/'pipeline.json', state); deadline = time.monotonic()+1800
    env = dict(os.environ, PATH='/usr/bin:/bin', RUSTC='/usr/bin/rustc', RUSTFLAGS='-C target-cpu=x86-64', CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS', 'CARGO_BUILD_RUSTFLAGS', 'RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER', 'LLVM_PROFILE_FILE'] or key.startswith('CARGO_PROFILE_') or key.startswith('ROOK2_'):
            env.pop(key, None)

    def verify():
        assert snapshot(crate) == source and baseline() == original
        assert policy(chosen_path) == chosen and sha(out/'policy.json') == sha(chosen_path)
        assert all(sha(path) == digest for path, digest in identities.items())

    def stage(name, command, cap, critical=False):
        verify(); state['active'] = name; write(out/'pipeline.json', state)
        started = time.monotonic_ns(); maximum = min(cap, deadline-time.monotonic()); assert maximum > 0
        with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen(command, cwd=crate, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=maximum)
            except BaseException:
                try:
                    os.killpg(child.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); child.wait()
                state['stages'].append(dict(stage=name, argv=command, exit=child.returncode,
                    elapsedNs=time.monotonic_ns()-started, failure='external stage timeout/interruption'))
                write(out/'pipeline.json', state); raise
        row = dict(stage=name, argv=command, pid=child.pid, exit=code, elapsedNs=time.monotonic_ns()-started,
                   stdoutSha256=sha(out/(name+'.stdout')), stderrSha256=sha(out/(name+'.stderr')))
        state['stages'].append(row); write(out/'pipeline.json', state)
        if name.startswith('tests-'):
            text = (out/(name+'.stdout')).read_text()
            names = re.findall(r'^test (\S+) \.\.\. ok$', text, re.M)
            summaries = re.findall(r'^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;', text, re.M)
            row.update(passedTests=names, critical=critical, testSummaries=summaries)
            write(out/'pipeline.json', state)
            assert code == 0, (name, code)
            assert len(summaries) == 1 and summaries[0][0] == 'ok' and int(summaries[0][1]) == len(names) > 0
            assert summaries[0][2:] == ('0', '0')
            selected = command[command.index('--')-1]
            assert all(name.startswith(selected) for name in names)
            assert len(names) == EXPECTED_TESTS[selected], (selected, len(names))
            if critical:
                assert len(names) == 6
        write(out/'pipeline.json', state)
        print(f'{name} exit {code}', flush=True); assert code == 0, (name, code)
        verify(); assert time.monotonic() < deadline

    try:
        for index, selector in enumerate(selectors):
            stage(f'tests-{index:02d}', ['/usr/bin/cargo', 'test', '--offline', '--locked', '--lib',
                '--features', FEATURE, '--target', 'x86_64-unknown-linux-gnu', '--jobs', '4',
                '--target-dir', str(out/'test-target'), selector, '--', '--test-threads=1'], 240, index == 0)
        passed = [name for row in state['stages'] for name in row.get('passedTests', [])]
        assert len(passed) == len(set(passed)), 'test selectors overlap'
        stage('build', ['/usr/bin/python3', str(HERE/'build.py'), '--crate', str(crate), '--output', str(out/'build')], 330)
        stage('collect', ['/usr/bin/python3', str(HERE/'collect.py'), '--build', str(out/'build'),
                          '--policy', str(chosen_path), '--output', str(out/'pilot')], 930)
        stage('reconcile', ['/usr/bin/python3', str(HERE/'reconcile.py'), str(out/'pilot')], 120)
        assert read(out/'pilot/reconciled.json')['complete']; verify()
        state.update(complete=True, active=None, sourceAfter=snapshot(crate), baselineAfter=baseline(),
                     endMonotonicNs=time.monotonic_ns(), focusedTests=len(passed))
        write(out/'pipeline.json', state)
    except BaseException as error:
        state.update(failure=repr(error), endMonotonicNs=time.monotonic_ns()); write(out/'pipeline.json', state); raise


if __name__ == '__main__':
    main()
