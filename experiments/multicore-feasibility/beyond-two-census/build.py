#!/usr/bin/env python3
"""One archived generic opt-in census build in isolated trial source; no PGO."""
import argparse
import hashlib
import importlib.util
import json
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
DEFAULT_CRATE = Path('/home/legolas/rook2-experiments/workspaces/beyond-two-census-20261025-01')
FEATURE = 'branch-work-census'
BASE = Path('/home/legolas/rook2-experiments/configured-full-20261024-01/production')
BASE_RECEIPT = BASE/'use-build/receipt.json'
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    def bad(value):
        raise ValueError('nonfinite JSON '+value)
    return json.loads(Path(path).read_text(), parse_constant=bad)


def write(path, value):
    path = Path(path); temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temporary.replace(path)


def snapshot(crate):
    paths = [crate/'Cargo.toml', crate/'Cargo.lock']
    paths += sorted(p for p in (crate/'src').rglob('*') if p.is_file())
    paths += [crate/n for n in ['build.rs', 'rust-toolchain', 'rust-toolchain.toml'] if (crate/n).is_file()]
    return {str(p.relative_to(crate)): sha(p) for p in paths}


def load_usable():
    path = HERE.parent/'usable-full/common.py'
    spec = importlib.util.spec_from_file_location('beyond_two_frozen_usable_common', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def baseline():
    receipt = read(BASE_RECEIPT)
    assert receipt['source_sha256_before'] == receipt['source_sha256_after'] == snapshot(ROOT)
    assert receipt['binary_output']['sha256'] == '8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b'
    images = {
        str(BASE/'rook2-pgo'): receipt['binary_output']['sha256'],
        str(Path(receipt['pgo']['profile'])): 'b7bd8ca21e8b9f64426af124be95bfc14feadd9b01bb94fb14bbefc7c550c6be',
        '/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build/rook2-exact':
            '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a',
        '/home/legolas/rook2-experiments/full-split-production-20261024-01/rook2-pgo':
            'a977bb0031b1beeb6fb50f8c391968f6e2d959ae86d648727442bdf027c88763',
        '/home/legolas/rook2-experiments/full-split-production-20261024-01/training/merged.profdata':
            'f9eefbd025c74a3247449c10fa0074fc5f178bcc49f1d623bed36cd9dcbdcadc'}
    for path, digest in images.items():
        assert sha(path) == digest
    return dict(rootSource=receipt['source_sha256_before'], protectedArtifacts=images,
                receipt=dict(path=str(BASE_RECEIPT), sha256=sha(BASE_RECEIPT)))


def effective_options(directory):
    commands = [shlex.split(line.split('Running `', 1)[1].rsplit('`', 1)[0])
                for line in (directory/'stderr').read_text().splitlines()
                if 'Running `' in line and '--crate-name rook2 ' in line]
    result = {}
    for source in ['src/lib.rs', 'src/bin/rook2.rs']:
        matches = [cmd for cmd in commands if source in cmd]
        assert len(matches) == 1, (source, len(matches))
        command, options = matches[0], {}
        assert 'feature="'+FEATURE+'"' in command
        assert not any('feature="'+name+'"' in command for name in ['branch-transactions', 'child-preparation'])
        for i, item in enumerate(command):
            if item == '-C':
                value = command[i+1]
            elif item.startswith('-C') and len(item) > 2:
                value = item[2:]
            else:
                continue
            key, sep, value = value.partition('='); assert key not in options
            options[key] = value if sep else True
        for key, value in [('opt-level', '3'), ('panic', 'abort'), ('codegen-units', '1'),
                           ('debuginfo', '1'), ('target-cpu', 'x86-64')]:
            assert options.get(key) == value, (source, key, options)
        assert not any(k.startswith('profile-') or k == 'llvm-args' for k in options)
        if source.endswith('rook2.rs'):
            assert options.get('lto') == 'thin' and 'linker-plugin-lto' not in options
        else:
            assert options.get('linker-plugin-lto') is True and 'lto' not in options
        result[source] = options
    return result


def admit(directory):
    receipt = read(directory/'receipt.json'); crate = Path(receipt['crate'])
    assert receipt['schema'] == 'rook2-branch-work-census-build-v1' and receipt['complete']
    assert receipt['exit'] == 0 and receipt['features'] == [FEATURE] and receipt['pgo'] == 'none'
    assert receipt['sourceBefore'] == receipt['sourceAfter'] == snapshot(crate)
    for name, digest in receipt['sourceBefore'].items():
        assert sha(directory/'source-before'/name) == digest
    assert receipt['baselineBefore'] == receipt['baselineAfter'] == baseline()
    assert receipt['flags'] == ['-C', 'target-cpu=x86-64']
    assert receipt['effectiveOptions'] == effective_options(directory)
    assert receipt['toolsBefore'] == receipt['toolsAfter']
    for path, digest in receipt['toolsBefore'].items():
        assert sha(path) == digest
    for path, digest in receipt['cargoConfig'].items():
        assert sha(path) == digest
    assert sha(receipt['binary']) == receipt['binarySha256']
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crate', type=Path, default=DEFAULT_CRATE)
    parser.add_argument('--features', choices=[FEATURE], default=FEATURE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); crate, out = args.crate.resolve(), args.output.resolve()
    assert crate != ROOT and sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    assert not out.exists(); out.mkdir()
    before, original = snapshot(crate), baseline()
    archive = out/'source-before'; archive.mkdir()
    for name, digest in before.items():
        destination = archive/name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(crate/name, destination); assert sha(destination) == digest
    tools = {str(p): sha(p) for p in [Path(__file__), Path('/usr/bin/rustc'), Path('/usr/bin/cargo')]}
    config_paths = set()
    for parent in [crate, *crate.parents]:
        config_paths.update(p for p in [parent/'.cargo/config', parent/'.cargo/config.toml'] if p.is_file())
    cargo_home = Path(os.environ.get('CARGO_HOME', str(Path.home()/'.cargo')))
    config_paths.update(p for p in [cargo_home/'config', cargo_home/'config.toml'] if p.is_file())
    configs = {str(p): sha(p) for p in sorted(config_paths)}
    env = dict(os.environ, PATH='/usr/bin:/bin', RUSTC='/usr/bin/rustc', RUSTFLAGS='-C target-cpu=x86-64', CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS', 'CARGO_BUILD_RUSTFLAGS', 'RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER', 'LLVM_PROFILE_FILE', 'ROOK2_BRANCH_WORK_CENSUS_REPORT'] or key.startswith('CARGO_PROFILE_'):
            env.pop(key, None)
    command = ['/usr/bin/cargo', 'build', '--offline', '--locked', '--verbose', '--release',
               '--jobs', '4', '--features', FEATURE, '--target', 'x86_64-unknown-linux-gnu',
               '--bin', 'rook2', '--target-dir', str(out/'target')]
    receipt = dict(schema='rook2-branch-work-census-build-v1', crate=str(crate), argv=command,
                   complete=False, features=[FEATURE], pgo='none', flags=['-C', 'target-cpu=x86-64'],
                   sourceBefore=before, baselineBefore=original, toolsBefore=tools, cargoConfig=configs)
    write(out/'receipt.json', receipt); started = time.monotonic()
    try:
        with (out/'stdout').open('xb') as stdout, (out/'stderr').open('xb') as stderr:
            child = subprocess.Popen(command, cwd=crate, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=300)
            except BaseException:
                os.killpg(child.pid, signal.SIGKILL); child.wait(); raise
        receipt.update(exit=code, wallSeconds=time.monotonic()-started,
                       sourceAfter=snapshot(crate), baselineAfter=baseline(),
                       toolsAfter={path: sha(path) for path in tools},
                       toolchain={})
        assert code == 0
        for tool in ['rustc', 'cargo']:
            command_version = ['/usr/bin/'+tool, '-Vv' if tool == 'rustc' else '--version']
            result = subprocess.run(command_version, capture_output=True, text=True, timeout=10, check=True)
            receipt['toolchain'][tool] = dict(argv=command_version, stdout=result.stdout, stderr=result.stderr, exit=result.returncode)
        assert receipt['sourceBefore'] == receipt['sourceAfter'] and receipt['toolsBefore'] == receipt['toolsAfter']
        receipt['effectiveOptions'] = effective_options(out)
        binary = out/'target/x86_64-unknown-linux-gnu/release/rook2'
        frozen = out/'rook2-census'; shutil.copy2(binary, frozen)
        receipt.update(binary=str(frozen), binarySha256=sha(frozen), complete=True)
        write(out/'receipt.json', receipt); admit(out)
        print('built '+receipt['binarySha256'], flush=True)
    except BaseException as error:
        receipt.update(failure=repr(error), complete=False)
        write(out/'receipt.json', receipt); raise


if __name__ == '__main__':
    main()
