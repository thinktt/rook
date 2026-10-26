#!/usr/bin/env python3
"""Prepare one generic candidate against the preserved old colors3 image.

Default prepare stops after focused controls, candidate build and CLI checks. A later collect
invocation reuses the successful preparation without rebuilding or repeating it.
The parent announces the native timing window before invoking collect/all.
"""
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
from common import (HERE, ROOT, HELPERS, DEFAULT_CRATE, CONTROL_CRATE, admission,
    CONTROL_IMAGE, CONTROL_BUILD, BUILD_ADAPTER, FOCUSED,
    admit_build, baseline, image_layout, old_evidence, preparation, prepared_run, read, sha, write)


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=['prepare', 'collect', 'all'], default='prepare')
    parser.add_argument('--skip-collection', action='store_true', help='alias for --stage=prepare')
    args = parser.parse_args()
    if args.skip_collection:
        assert args.stage == 'prepare', '--skip-collection only accompanies default prepare'
    prepared_path, out = args.preparation.resolve(), args.output.resolve()
    prepared = preparation(prepared_path)
    assert set(os.sched_getaffinity(0)) == HELPERS
    if args.stage == 'collect':
        state = read(out/'pipeline.json')
        assert state['schema'] == 'rook2-epoch-colors-pipeline-v1'
        assert state['prepared'] and not state['collected'] and state['failure'] is None
        assert state['preparation'] == str(prepared_path) and state['preparationSha256'] == sha(prepared_path)
        assert state['sourcePreparation'] == prepared
        assert state['protectedArtifacts'] == baseline()
        assert state['stages'][-1]['stage'] == 'cli-affinity'
        state['complete'] = False
    else:
        out.mkdir()
        state = dict(schema='rook2-epoch-colors-pipeline-v1', complete=False,
            prepared=False, collected=False, failure=None, stages=[],
            pipelineStartMonotonicNs=time.monotonic_ns(), pipelineSeconds=3600,
            preparation=str(prepared_path), preparationSha256=sha(prepared_path),
            sourcePreparation=prepared, protectedArtifacts=baseline(),
            buildOrder=['verify-preserved-oldcolors3', 'candidate-only'],
            control=dict(path=str(CONTROL_IMAGE), sha256=sha(CONTROL_IMAGE), bytes=CONTROL_IMAGE.stat().st_size),
            controlBuild=str(CONTROL_BUILD),
            reusedFocusedEvidence=prepared['reusedFocusedEvidence'],
            buildAffinityAdaptation='unchanged tools/build.py imported by pinned adapter; only HELPERS overridden',
            parentTimingAnnouncementRequired=True)
    write(out/'pipeline.json', state)
    env = dict(os.environ, PATH='/usr/bin:/bin', RUSTC='/usr/bin/rustc',
        RUSTFLAGS='-C target-cpu=x86-64', CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS', 'CARGO_BUILD_RUSTFLAGS', 'RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER', 'LLVM_PROFILE_FILE'] or key.startswith(('CARGO_PROFILE_', 'ROOK2_')):
            env.pop(key, None)
    assert state['pipelineSeconds'] == 3600
    assert 0 < state['pipelineStartMonotonicNs'] <= time.monotonic_ns()
    deadline = state['pipelineStartMonotonicNs']/1_000_000_000+state['pipelineSeconds']
    assert Path(state['control']['path']) == CONTROL_IMAGE
    assert state['control']['sha256'] == sha(CONTROL_IMAGE)
    assert state['controlBuild'] == str(CONTROL_BUILD)

    def check():
        assert preparation(prepared_path) == prepared
        assert sha(prepared_path) == state['preparationSha256']
        assert baseline() == state['protectedArtifacts']

    def stage(name, command, cap, cwd=ROOT, tests=None):
        check()
        state['active'] = name; write(out/'pipeline.json', state)
        started = time.monotonic_ns()
        limit = min(cap, deadline-time.monotonic()); assert limit > 0
        with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen(command, cwd=cwd, env=env, stdout=stdout,
                stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=limit)
            except BaseException:
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    child.wait()
                raise
        row = dict(stage=name, argv=[str(x) for x in command], cwd=str(cwd), pid=child.pid,
            exit=code, elapsedNs=time.monotonic_ns()-started,
            stdoutSha256=sha(out/(name+'.stdout')), stderrSha256=sha(out/(name+'.stderr')))
        state['stages'].append(row); write(out/'pipeline.json', state)
        assert code == 0, (name, code)
        if tests is not None:
            text = (out/(name+'.stdout')).read_text()
            passed = re.findall(r'^test (\S+) \.\.\. ok$', text, re.M)
            summaries = re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;', text, re.M)
            assert len(summaries) == 1 and summaries[0][1:] == ('0', '0')
            assert int(summaries[0][0]) == len(passed) > 0
            if 'expectedPassed' in tests:
                assert len(passed) == tests['expectedPassed'], (name, passed)
            row['passedTests'] = passed; write(out/'pipeline.json', state)
        print(name+' exit '+str(code), flush=True)
        check()

    def freeze_image(directory, path, crate, source):
        receipt = read(directory/'receipt.json')
        shutil.copy2(Path(receipt['binary_output']['path']), path)
        admit_build(directory, path, crate, source)
        return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)

    try:
        if args.stage != 'collect':
            # The old generic colors3 is immutable evidence: verify source,
            # build and38 saved controls before starting any candidate work.
            old_evidence(prepared)
            admit_build(CONTROL_BUILD, CONTROL_IMAGE, CONTROL_CRATE, prepared['controlSource'])
            for index, tests in enumerate(prepared['focused']):
                command = ['/usr/bin/cargo', 'test', '--offline', '--locked', *tests['target'],
                    '--target', 'x86_64-unknown-linux-gnu', '--jobs', '4',
                    '--target-dir', str(out/'test-target'), tests['selector'], '--', '--test-threads=1']
                if tests.get('exact', False):
                    command.append('--exact')
                if tests.get('ignored', False):
                    command.append('--ignored')
                stage(f'tests-{index:02d}-{tests["name"]}', command,
                      tests.get('limitSeconds', 300), DEFAULT_CRATE, tests)
            stage('candidate-build', ['/usr/bin/python3', str(BUILD_ADAPTER),
                '--crate', str(DEFAULT_CRATE), '--mode', 'generic', '--bin', 'rook2',
                '--jobs', '4', '--output', str(out/'candidate-build')], 360)
            state['candidate'] = freeze_image(out/'candidate-build', out/'rook2-candidate',
                                             DEFAULT_CRATE, prepared['candidateSource'])
            admission(CONTROL_BUILD, out/'candidate-build', Path(state['control']['path']),
                      Path(state['candidate']['path']), prepared)
            stage('cli-affinity', ['/usr/bin/python3', str(FOCUSED),
                '--engine', state['candidate']['path'], '--output', str(out/'focused')], 420)
            files = [out/(row['stage']+'.'+suffix) for row in state['stages'] for suffix in ['stdout', 'stderr']]
            files += [path for path in (out/'focused').rglob('*') if path.is_file()]
            record = dict(schema='rook2-epoch-colors-prepared-run-v1',
                sourcePreparation=str(prepared_path), sourcePreparationSha256=sha(prepared_path),
                source=prepared['candidateSource'], stages=state['stages'],
                candidate=image_layout(Path(state['candidate']['path'])), control=image_layout(CONTROL_IMAGE),
                reusedFocusedEvidence=prepared['reusedFocusedEvidence'],
                inputSha256={str(path): sha(path) for path in sorted(files)},
                pipelineStartMonotonicNs=state['pipelineStartMonotonicNs'], pipelineSeconds=3600,
                preparedMonotonicNs=time.monotonic_ns())
            write(out/'prepared-run.json', record)
            prepared_run(out/'prepared-run.json', prepared_path, prepared, Path(state['candidate']['path']))
            state.update(prepared=True, complete=args.stage == 'prepare', active=None)
            write(out/'pipeline.json', state)
        if args.stage in ['collect', 'all']:
            prepared_run(out/'prepared-run.json', prepared_path, prepared, Path(state['candidate']['path']))
            admission(CONTROL_BUILD, out/'candidate-build', Path(state['control']['path']),
                      Path(state['candidate']['path']), prepared)
            assert read(out/'focused/result.json')['complete']
            stage('collection', ['/usr/bin/python3', str(HERE/'collect.py'),
                '--control', state['control']['path'], '--candidate', state['candidate']['path'],
                '--control-build', str(CONTROL_BUILD), '--candidate-build', str(out/'candidate-build'),
                '--preparation', str(prepared_path), '--output', str(out/'pilot')], 1850)
            stage('reconcile', ['/usr/bin/python3', str(HERE/'reconcile.py'), str(out/'pilot')], 120)
            assert read(out/'pilot/reconciled.json')['complete']
            state.update(collected=True, complete=True, active=None)
        check()
        assert time.monotonic() < deadline, 'persisted aggregate pipeline deadline'
        write(out/'pipeline.json', state)
        print('prepared candidate with preserved oldcolors3'+(' and completed48+4 pilot' if state['collected'] else '; stopped before timing'), flush=True)
    except BaseException as error:
        state.update(complete=False, failure=repr(error))
        write(out/'pipeline.json', state)
        raise


if __name__ == '__main__':
    main()
