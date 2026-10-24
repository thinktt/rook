#!/usr/bin/env python3
"""PGO-only pipeline after focused/configuration closure; stop after small64.

The separate full54 stage requires a later explicit parent invocation. There is
no numerical extension gate, retry, repeated training, profile reuse or retune.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, ROOT, HELPERS, SERIAL_BUILD, PREVIOUS_BUILD, SERIAL_SHA,
                    PREVIOUS_SHA, admission, train, read, write, sha)


def check_inputs(state):
    assert train.source_snapshot(ROOT) == state['sourceInputs'], 'frozen engine source changed'
    assert sha(Path(state['serial'])) == SERIAL_SHA and sha(Path(state['previous'])) == PREVIOUS_SHA
    for field in ['toolInputs', 'driverInputs', 'closureInputs']:
        assert all(sha(Path(path)) == digest for path, digest in state[field].items()), field+' changed'


def admit_closure(build, verification):
    receipt, proof = read(build/'receipt.json'), read(verification)
    assert receipt['schema'] == 'rook2-development-build-v1'
    assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot' and receipt['cargo_exit_code'] == 0
    assert receipt['mode'] == 'generic' and receipt['binary_name'] == 'rook2'
    assert receipt['target_triple'] == 'x86_64-unknown-linux-gnu' and receipt['target_cpu'] == 'x86-64'
    assert receipt['pgo']['mode'] == 'none'
    for before, after in [('source_sha256_before', 'source_sha256_after'),
                          ('tool_sha256_before', 'tool_sha256_after'),
                          ('cargo_config_sha256_before', 'cargo_config_sha256_after')]:
        assert receipt[before] == receipt[after]
    assert train.source_snapshot(ROOT) == receipt['source_sha256_before']
    assert sha(Path(receipt['binary_output']['path'])) == receipt['binary_output']['sha256']
    assert proof['schema'] == 'rook2-configured-full-verification-v1' and proof['complete']
    assert proof['engineSha256'] == receipt['binary_output']['sha256'] == sha(Path(proof['engine']))
    assert proof['totalLimitSeconds'] == 420 and proof['perLifetimeLimitSeconds'] == 180
    assert len(proof['cli']) == 13 and len(proof['oneCpu']) == 2
    assert [row['requestedThreads'] for row in proof['oneCpu']] == [1, 2]
    paths = [build/'receipt.json', build/'build.stderr', verification, Path(proof['engine'])]
    for path, digest in proof['inputSha256'].items():
        assert sha(Path(path)) == digest
        paths.append(Path(path))
    for row in proof['oneCpu']:
        assert row['configuredThreads'] == 1 and row['exit'] == 0
        observed = row['taskObservations']
        assert observed['count'] >= 1 and observed['minimumTasks'] == observed['maximumTasks'] == 1
        assert observed['taskIds'] == [str(row['nativePid'])]
        for bound in ['first', 'last']:
            assert observed[bound]['taskAffinities'] == {str(row['nativePid']): [14]}
        directory = verification.parent/f'request{row["requestedThreads"]}'
        assert read(directory/'result.json') == row
        paths.append(directory/'result.json')
        for name, digest in row['sha256'].items():
            path = directory/name
            assert sha(path) == digest
            paths.append(path)
    return receipt, paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=['pgo-small', 'full54'], default='pgo-small')
    parser.add_argument('--source-build', type=Path, help='completed generic validation build (pgo-small)')
    parser.add_argument('--verification', type=Path, help='completed configured-full/verify.py result.json (pgo-small)')
    parser.add_argument('--source-revision', help='expected checkpoint HEAD (optional, verified when supplied)')
    parser.add_argument('--serial', type=Path, default=SERIAL_BUILD/'rook2-exact')
    parser.add_argument('--previous', type=Path, default=PREVIOUS_BUILD.parent/'rook2-pgo',
                        help='preserved a977 image copy')
    args = parser.parse_args()
    # Use the preserved image copy, never its old mutable Cargo target path.
    previous = args.previous.resolve()
    serial, out = args.serial.resolve(), args.output.resolve()
    assert sha(serial) == SERIAL_SHA and sha(previous) == PREVIOUS_SHA
    assert HELPERS <= os.sched_getaffinity(0)
    env = dict(os.environ, PATH='/usr/bin:/bin')
    env.pop('LLVM_PROFILE_FILE', None)
    original_affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, HELPERS)
    state = None
    try:
        if args.stage == 'pgo-small':
            assert args.source_build and args.verification, '--source-build and --verification are required'
            build = args.source_build.resolve()
            proof = args.verification.resolve()
            generic, closure_paths = admit_closure(build, proof)
            closure_paths += [serial, previous, SERIAL_BUILD/'receipt.json', PREVIOUS_BUILD/'receipt.json']
            assert not out.exists() and out.parent.is_dir(), 'pipeline output must be fresh'
            out.mkdir()
            revision = subprocess.run(['/usr/bin/git', 'rev-parse', '--verify', 'HEAD'],
                cwd=ROOT, env=env, check=True, capture_output=True, text=True, timeout=10).stdout.strip()
            assert len(revision) == 40
            if args.source_revision: assert revision == args.source_revision
            tools = {str((ROOT/name).resolve()): digest for name, digest in generic['tool_sha256_before'].items()}
            tools.update(generic['cargo_config_sha256_before'])
            state = dict(schema='rook2-configured-full-pipeline-v1', complete=False,
                active=None, failure=None, stages=[], sourceRevision=revision,
                sourceInputs=generic['source_sha256_before'], toolInputs=tools,
                toolSourceInputs=generic['tool_sha256_before'],
                cargoConfigInputs=generic['cargo_config_sha256_before'],
                driverInputs={str(path.resolve()): sha(path) for path in HERE.glob('*.py')},
                closureInputs={str(path.resolve()): sha(path) for path in closure_paths},
                genericBuild=str(build), verification=str(proof), serial=str(serial), previous=str(previous),
                preservedSha256=dict(serial=SERIAL_SHA, previous=PREVIOUS_SHA),
                entryCondition='Parent completed selected focused checks, generic build/configuration+two one-CPU original08 closure, then source checkpoint before invoking this PGO-only pipeline; focused tests are not repeated here',
                stageCapsSeconds=dict(instrumentedBuild=300, training=2500, trainingAudit=120,
                                      useBuild=300, small=1900, smallAudit=120, full54=1900, full54Audit=120),
                automaticExtension=False, stopAfter='small64-and-independent-audit',
                nativeLimits=dict(trainingLives=108, smallLives=64, manualFull54Lives=216,
                                  perLifeSeconds=180, trainingSeconds=2400, comparisonSeconds=1800))
            write(out/'pipeline.json', state)
        else:
            assert not args.source_build and not args.verification, 'full54 uses the already frozen pipeline'
            state = read(out/'pipeline.json')
            assert state['schema'] == 'rook2-configured-full-pipeline-v1'
            assert state['complete'] and state['failure'] is None and state['stopAfter'] == 'small64-and-independent-audit'
            assert not (out/'full54').exists() and 'full54Extension' not in state
            assert str(serial) == state['serial'] and str(previous) == state['previous']
            assert read(out/'small/reconciled.json')['complete']
            state['full54Extension'] = dict(selectedBy='explicit separate --stage full54 invocation',
                                            complete=False, failure=None)
            write(out/'pipeline.json', state)

        check_inputs(state)

        def stage(name, command, limit):
            check_inputs(state)
            state['active'] = name
            write(out/'pipeline.json', state)
            started = time.monotonic_ns()
            with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
                child = subprocess.Popen([str(item) for item in command], cwd=ROOT, env=env,
                    stdout=stdout, stderr=stderr, start_new_session=True)
                try:
                    code = child.wait(timeout=limit)
                except BaseException:
                    # Let each selected driver drain its own native child first.
                    try: os.killpg(child.pid, signal.SIGINT)
                    except ProcessLookupError: pass
                    try: child.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        try: os.killpg(child.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                        child.wait()
                    raise
            state['stages'].append(dict(stage=name, argv=[str(item) for item in command], exit=code,
                elapsedNs=time.monotonic_ns()-started, stdoutSha256=sha(out/(name+'.stdout')),
                stderrSha256=sha(out/(name+'.stderr'))))
            write(out/'pipeline.json', state)
            print(name, code, flush=True)
            assert code == 0, (name, code)
            check_inputs(state)

        def freeze(build, name):
            receipt = read(build/'receipt.json')
            assert receipt['source_sha256_before'] == receipt['source_sha256_after'] == state['sourceInputs']
            assert receipt['tool_sha256_before'] == receipt['tool_sha256_after'] == state['toolSourceInputs']
            assert receipt['cargo_config_sha256_before'] == receipt['cargo_config_sha256_after'] == state['cargoConfigInputs']
            source = Path(receipt['binary_output']['path'])
            assert sha(source) == receipt['binary_output']['sha256']
            target = out/name
            assert not target.exists()
            shutil.copy2(source, target)
            assert sha(target) == sha(source)
            return target

        if args.stage == 'pgo-small':
            stage('instrumented-build', ['/usr/bin/python3', ROOT/'tools/build.py', '--mode', 'generic',
                '--bin', 'rook2', '--jobs', '4', '--pgo-generate', out/'profile-raw',
                '--output', out/'instrumented-build'], 300)
            freeze(out/'instrumented-build', 'rook2-instrumented')
            stage('training', ['/usr/bin/python3', HERE/'train.py', '--build', out/'instrumented-build',
                '--output', out/'training'], 2500)
            stage('training-audit', ['/usr/bin/python3', HERE/'training_reconcile.py', out/'training'], 120)
            assert read(out/'training/reconciled.json')['complete']
            stage('use-build', ['/usr/bin/python3', ROOT/'tools/build.py', '--mode', 'generic', '--bin', 'rook2',
                '--jobs', '4', '--pgo-use', out/'training/merged.profdata', '--training-record', out/'training/training.json',
                '--ext-tsp-profiled', '--output', out/'use-build'], 300)
            candidate = freeze(out/'use-build', 'rook2-pgo')
            _, effective, compatibility = admission(out/'use-build', serial, previous, candidate)
            state['candidate'] = str(candidate)
            state['candidateSha256'] = sha(candidate)
            state['profileSha256'] = sha(out/'training/merged.profdata')
            state['effectiveRustcOptions'] = effective
            state['controlCompatibility'] = compatibility
            write(out/'pipeline.json', state)
            command = ['/usr/bin/python3', HERE/'collect.py', '--serial', serial, '--previous', previous,
                       '--candidate', candidate, '--build', out/'use-build', '--output', out/'small']
            stage('small', command, 1900)
            stage('small-audit', ['/usr/bin/python3', HERE/'reconcile.py', out/'small'], 120)
            assert read(out/'small/reconciled.json')['complete']
            state['complete'] = True
            state['active'] = None
            write(out/'pipeline.json', state)
            print('PGO and small64 complete; stopped for parent evidence decision, no automatic full54', flush=True)
        else:
            candidate = Path(state['candidate'])
            assert sha(candidate) == state['candidateSha256']
            assert sha(out/'training/merged.profdata') == state['profileSha256']
            admission(out/'use-build', serial, previous, candidate)
            command = ['/usr/bin/python3', HERE/'collect.py', '--serial', serial, '--previous', previous,
                       '--candidate', candidate, '--build', out/'use-build', '--output', out/'full54', '--full54']
            stage('full54', command, 1900)
            stage('full54-audit', ['/usr/bin/python3', HERE/'reconcile.py', out/'full54'], 120)
            assert read(out/'full54/reconciled.json')['complete']
            state['full54Extension']['complete'] = True
            state['active'] = None
            write(out/'pipeline.json', state)
            print('Separately selected descriptive216 complete', flush=True)
    except BaseException as error:
        if state is not None:
            if args.stage == 'full54' and 'full54Extension' in state:
                state['full54Extension']['failure'] = repr(error)
            else: state['failure'] = repr(error)
            write(out/'pipeline.json', state)
        raise
    finally:
        os.sched_setaffinity(0, original_affinity)


if __name__ == '__main__':
    main()
