#!/usr/bin/env python3
"""One isolated generic internal-split driver build; no ordinary/PGO build."""
import argparse
import importlib.util
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_CRATE = Path('/home/legolas/rook2-experiments/workspaces/coarse-pure-salvage-20261026-01')
FEATURE, BINARY = 'coarse-pure-salvage', 'rook2-coarse-pure-census'
BASE_HELPER = HERE.parent/'beyond-two-census/build.py'
spec = importlib.util.spec_from_file_location('hierarchical_preserved_baseline_helper', BASE_HELPER)
preserved = importlib.util.module_from_spec(spec); spec.loader.exec_module(preserved)
sha, read, write, snapshot = preserved.sha, preserved.read, preserved.write, preserved.snapshot
HELPERS = preserved.HELPERS

def baseline():
    return preserved.baseline()


def effective_options(directory):
    commands = [shlex.split(line.split('Running `', 1)[1].rsplit('`', 1)[0])
                for line in (directory/'stderr').read_text().splitlines() if 'Running `' in line]
    result = {}
    for source in ['src/lib.rs', 'src/bin/rook2-coarse-pure-census.rs']:
        matches = [cmd for cmd in commands if source in cmd]; assert len(matches) == 1, (source, len(matches))
        command, options = matches[0], {}
        assert all('feature="'+feature+'"' in command for feature in ['coarse-pure-salvage', 'internal-split', 'hierarchical-recovery', 'branch-transactions'])
        assert not any('feature="'+f+'"' in command for f in ['branch-work-census', 'child-preparation'])
        for i, token in enumerate(command):
            if token == '-C':
                value = command[i+1]
            elif token.startswith('-C') and len(token) > 2:
                value = token[2:]
            else:
                continue
            key, sep, value = value.partition('='); assert key not in options
            options[key] = value if sep else True
        for key, value in [('opt-level', '3'), ('panic', 'abort'), ('codegen-units', '1'),
                           ('debuginfo', '1'), ('target-cpu', 'x86-64')]:
            assert options.get(key) == value, (source, key, options)
        assert not any(k.startswith('profile-') or k == 'llvm-args' for k in options)
        if source == 'src/lib.rs':
            assert options.get('linker-plugin-lto') is True and 'lto' not in options
        else:
            assert options.get('lto') == 'thin' and 'linker-plugin-lto' not in options
        result[source] = options
    return result


def admit(directory):
    receipt = read(directory/'receipt.json')
    assert receipt['schema'] == 'rook2-coarse-pure-build-v1' and receipt['complete'] and receipt['exit'] == 0
    assert receipt['features'] == [FEATURE] and receipt['binaryName'] == BINARY and receipt['pgo'] == 'none'
    assert receipt['sourceBefore'] == receipt['sourceAfter'] == snapshot(Path(receipt['crate']))
    for name, digest in receipt['sourceBefore'].items():
        assert sha(directory/'source-before'/name) == digest
    assert receipt['baselineBefore'] == receipt['baselineAfter'] == baseline()
    assert receipt['toolsBefore'] == receipt['toolsAfter']
    for path, digest in receipt['toolsBefore'].items():
        assert sha(path) == digest
    assert receipt['flags'] == ['-C', 'target-cpu=x86-64']
    assert receipt['effectiveOptions'] == effective_options(directory)
    assert sha(receipt['binary']) == receipt['binarySha256']
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crate', type=Path, default=DEFAULT_CRATE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); crate, out = args.crate.resolve(), args.output.resolve()
    assert crate != ROOT and sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    before, original = snapshot(crate), baseline(); out.mkdir()
    for name, digest in before.items():
        destination = out/'source-before'/name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(crate/name, destination); assert sha(destination) == digest
    tools = {str(p): sha(p) for p in [Path(__file__), BASE_HELPER, Path('/usr/bin/cargo'), Path('/usr/bin/rustc')]}
    env = dict(os.environ, PATH='/usr/bin:/bin', RUSTC='/usr/bin/rustc', RUSTFLAGS='-C target-cpu=x86-64', CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS', 'CARGO_BUILD_RUSTFLAGS', 'RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER', 'LLVM_PROFILE_FILE'] or key.startswith('CARGO_PROFILE_') or key.startswith('ROOK2_'):
            env.pop(key, None)
    command = ['/usr/bin/cargo', 'build', '--offline', '--locked', '--verbose', '--release',
               '--jobs', '4', '--features', FEATURE, '--target', 'x86_64-unknown-linux-gnu',
               '--bin', BINARY, '--target-dir', str(out/'target')]
    receipt = dict(schema='rook2-coarse-pure-build-v1', crate=str(crate), argv=command,
                   complete=False, features=[FEATURE], binaryName=BINARY, pgo='none',
                   sourceBefore=before, baselineBefore=original, toolsBefore=tools, flags=['-C', 'target-cpu=x86-64'])
    write(out/'receipt.json', receipt); started = time.monotonic_ns()
    try:
        with (out/'stdout').open('xb') as stdout, (out/'stderr').open('xb') as stderr:
            child = subprocess.Popen(command, cwd=crate, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=300)
            except BaseException:
                os.killpg(child.pid, signal.SIGKILL); child.wait(); raise
        receipt.update(exit=code, wallNs=time.monotonic_ns()-started, sourceAfter=snapshot(crate),
                       baselineAfter=baseline(), toolsAfter={p: sha(p) for p in tools}, toolchain={})
        assert code == 0
        for name in ['rustc', 'cargo']:
            argv = ['/usr/bin/'+name, '-Vv' if name == 'rustc' else '--version']
            version = subprocess.run(argv, capture_output=True, text=True, timeout=10, check=True)
            receipt['toolchain'][name] = dict(argv=argv, exit=version.returncode, stdout=version.stdout, stderr=version.stderr)
        receipt['effectiveOptions'] = effective_options(out)
        binary = out/'target/x86_64-unknown-linux-gnu/release'/BINARY
        frozen = out/BINARY; shutil.copy2(binary, frozen)
        receipt.update(binary=str(frozen), binarySha256=sha(frozen), complete=True)
        write(out/'receipt.json', receipt); admit(out); print('built '+receipt['binarySha256'], flush=True)
    except BaseException as error:
        receipt.update(complete=False, failure=repr(error)); write(out/'receipt.json', receipt); raise


if __name__ == '__main__':
    main()
