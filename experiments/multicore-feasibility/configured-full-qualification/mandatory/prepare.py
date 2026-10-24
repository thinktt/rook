#!/usr/bin/env python3
"""Source-only setup: isolate frozen engine+adapter and derive current inventory."""
import argparse
import os
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
from common import (HERE, ROOT, SPEC, OLD, HELPERS, PRODUCTION, VERIFICATION,
                    SOURCE_COMMIT, ORDINARY_SHA, OPTIONAL, sha, read, put,
                    inventory, passed_tests, executable, verify)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-receipt', type=Path, default=PRODUCTION/'use-build/receipt.json')
    parser.add_argument('--ordinary', type=Path, default=PRODUCTION/'rook2-pgo')
    parser.add_argument('--verification', type=Path, default=VERIFICATION)
    args = parser.parse_args()
    build_path, ordinary, old = args.build_receipt.resolve(), args.ordinary.resolve(), args.verification.resolve()
    receipt = read(build_path)
    proof_path = ROOT/'experiments/multicore-feasibility/configured-full/proof.json'
    proof = read(proof_path)
    assert proof['complete'] and proof['sourceCommit'] == SOURCE_COMMIT
    assert proof['profileUseReceiptSha256'] == sha(build_path)
    assert receipt['source_sha256_before'] == receipt['source_sha256_after']
    assert receipt['source_identity_unchanged'] and receipt['pgo']['mode'] == 'profile-use'
    assert sha(ordinary) == receipt['binary_output']['sha256'] == ORDINARY_SHA
    archive = build_path.parent/'source-before'
    source = receipt['source_sha256_before']
    for name, digest in source.items():
        assert sha(archive/name) == sha(ROOT/name) == digest
    verification = read(old/'pipeline.json')
    assert verification['complete']
    assert verification['source'] == {str(ROOT/name): digest for name, digest in source.items()}
    verification_proof_path = ROOT/'experiments/multicore-feasibility/configured-full/verification-proof.json'
    verification_proof = read(verification_proof_path)
    assert verification_proof['complete']
    for path, digest in verification_proof['bindings'].items():
        assert sha(path) == digest
    lib = executable(old/'budgets.stderr')
    assert lib == executable(old/'lifecycle.stderr')
    parser_elf = executable(old/'parser.stderr')
    reused = []
    for stage, kind in [('budgets', 'library'), ('lifecycle', 'library'), ('parser', 'ordinary-parser')]:
        names = passed_tests(old/(stage+'.stdout'))
        record = next(row for row in verification['stages'] if row['stage'] == stage)
        assert record['exit'] == 0 and record['passedTests'] == len(names) > 0
        assert record['stdoutSha256'] == sha(old/(stage+'.stdout'))
        assert record['stderrSha256'] == sha(old/(stage+'.stderr'))
        reused.append(dict(stage=stage, kind=kind, tests=names,
                           stdout=str(old/(stage+'.stdout')), stderr=str(old/(stage+'.stderr')),
                           executable=str(parser_elf if kind == 'ordinary-parser' else lib)))
    skip = [name for row in reused if row['kind'] == 'library' for name in row['tests']]
    assert len(skip) == len(set(skip))
    out = args.output.resolve(); out.mkdir()
    worktree = out/'source'; worktree.mkdir()
    for name in source:
        destination = worktree/name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(archive/name, destination)
    diagnostic = [ROOT/'diagnostic/Cargo.toml', ROOT/'diagnostic/Cargo.lock']
    diagnostic += sorted(path for path in (ROOT/'diagnostic/src').rglob('*') if path.is_file())
    adapter_map = {str(path.relative_to(ROOT)): sha(path) for path in diagnostic}
    # This check documents the actual adapter mode; it does not alter defaults.
    assert all('set_threads(' not in path.read_text() and 'set_threads_with_affinity(' not in path.read_text()
               for path in diagnostic if path.suffix == '.rs')
    for path in diagnostic:
        target = worktree/path.relative_to(ROOT); target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    selected = inventory(); put(out/'selection.json', selected)
    image = out/'diagnostic-target/x86_64-unknown-linux-gnu/release/rook2-diag'
    launcher = ['/usr/bin/python3', str(OLD/'native_launch.py'), str(image), '--']
    target = ['--target', 'x86_64-unknown-linux-gnu', '--jobs', '4', '--message-format=json']
    test_tail = ['--', '--test-threads=4']
    cargo = ['/usr/bin/cargo']
    fixture_argv = ['/usr/bin/node', '--import', str(OLD/'capture.mjs'), str(SPEC/'run.mjs')]
    for row in selected['files']:
        fixture_argv += ['--fixtures', row['path']]
    fixture_argv += ['--', *launcher]
    stages = dict(
        library_list=dict(argv=[str(lib), '--list', '--format', 'terse'], maximumSeconds=30),
        library_complement=dict(argv=[str(lib), '--test-threads=4', *sum((['--skip', name] for name in skip), [])], maximumSeconds=300),
        diagnostic_build=dict(argv=cargo+['build', '--offline', '--locked', '--release', *target,
            '--manifest-path', str(worktree/'diagnostic/Cargo.toml'), '--target-dir', str(out/'diagnostic-target'), '--bin', 'rook2-diag'], maximumSeconds=300),
        diagnostic_tests=dict(argv=cargo+['test', '--offline', '--locked', *target,
            '--manifest-path', str(worktree/'diagnostic/Cargo.toml'), '--target-dir', str(out/'diagnostic-target'), '--bin', 'rook2-diag', *test_tail], maximumSeconds=300),
        development_tests=dict(argv=cargo+['test', '--offline', '--locked', *target,
            '--manifest-path', str(worktree/'Cargo.toml'), '--target-dir', str(out/'development-target'), '--bin', 'rook2-dev', *test_tail], maximumSeconds=300),
        fixtures=dict(argv=fixture_argv, maximumSeconds=1200),
        independent=dict(argv=['/usr/bin/node', str(HERE/'reconcile.mjs'), str(out)], maximumSeconds=120))
    for stage in stages.values():
        stage.update(cwd=str(worktree), expectedExit=0)
    env = dict(PATH='/usr/bin:/bin', PYTHONDONTWRITEBYTECODE='1', RUSTC='/usr/bin/rustc',
               RUSTC_WRAPPER='', RUSTC_WORKSPACE_WRAPPER='', RUSTFLAGS='-C target-cpu=x86-64',
               CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64', CARGO_NET_OFFLINE='true',
               CARGO_BUILD_JOBS='4', CARGO_INCREMENTAL='0')
    pins = [HERE/n for n in ['common.py', 'prepare.py', 'run_lane.py', 'reconcile.mjs']]
    pins += [build_path, proof_path, verification_proof_path, old/'pipeline.json', lib, parser_elf,
             ordinary, OLD/'capture.mjs', OLD/'native_launch.py', SPEC/'run.mjs', SPEC/'README.md',
             out/'selection.json', Path('/usr/bin/cargo'), Path('/usr/bin/rustc')]
    for row in reused:
        pins += [Path(row['stdout']), Path(row['stderr'])]
    old_diag_plan = read(OLD/'mandatory-completion/plan.json')
    old_diag = Path(old_diag_plan['diagnosticImage'])
    assert sha(old_diag) == old_diag_plan['diagnosticSha256']; pins.append(old_diag)
    pins += [Path(row['path']) for row in selected['files']+selected['excludedOptionalFiles']]
    plan = dict(schema='rook2-configured-full-mandatory-v1', sourceCommit=SOURCE_COMMIT,
                repo=str(ROOT), worktree=str(worktree), engineArchive=str(archive), engineSource=source,
                diagnosticSource=adapter_map, ordinaryImage=str(ordinary), ordinarySha256=ORDINARY_SHA,
                diagnosticImage=str(image), diagnosticMode='default requested1/configured1; no adapter helper configuration',
                launcherCommand=launcher, helperCpus=HELPERS, diagnosticCpu=14, quietSiblings=[7, 15],
                environment=env, pins={str(path): sha(path) for path in pins}, stages=stages,
                reusedFocused=reused, skippedLibraryTests=skip,
                libraryExecutable=dict(path=str(lib), sha256=sha(lib),
                    provenance='same retained test ELF path recorded in both exact-source original Cargo test logs; newly pinned at qualification setup'),
                allowedIgnoredLibraryTests=['evaluator_worker::lifecycle_tests::helper_delay_beyond_ten_seconds_preserves_result_and_lifecycle'],
                selection=str(out/'selection.json'), aggregateSeconds=1800,
                limits=dict(stageOutputBytes=512*1024**2, addressSpaceBytes=8*1024**3),
                scope='one current mandatory default1 pass and normal test complement; reused worker-aware checks separately; same engine source, distinct diagnostic artifact; no ordinary rebuild/retraining or mode2 mandatory claim')
    verify(plan); put(out/'plan.json', plan)
    for name in stages:
        (out/name).mkdir()
    (out/'fixtures/native').mkdir(); (out/'fixtures/wire').mkdir()
    put(out/'fixtures/tap-config.json', dict(image=str(image), rawRoot=str(out/'fixtures/wire'),
        expectedCalls=[launcher for _ in range(selected['mandatoryCases'])], maxBytes=1024*1024))
    print(f'Source-only setup complete: {len(selected["files"])} mandatory files, {selected["mandatoryCases"]} cases, {len(selected["mandatoryOperations"])} operations; no native launch')


if __name__ == '__main__':
    main()
