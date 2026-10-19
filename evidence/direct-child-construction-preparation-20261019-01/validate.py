#!/usr/bin/env python3
"""Separate reviewed experiment28 build/native/strict stages; no timing."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/legolas/rook2')
E = ROOT / 'evidence'
TRIAL = Path('/home/legolas/rook2-work/imp2-direct-child-construction-20261019-01')
BUILD = E / 'direct-child-construction-generic-build-20261019-01'
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]


def load(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    with p.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert len(sys.argv) == 2 and sys.argv[1] in ['build', 'native', 'regression']
    stage = sys.argv[1]
    binding = load(HERE / 'execution-binding.json')
    assert binding['parent_source_review_complete']
    assert binding['driver_sha256'] == sha(Path(__file__))
    assert sorted(os.sched_getaffinity(0)) == HELPERS
    assert os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE', 'NODE_OPTIONS'])
    pins = {TRIAL / name: digest for name, digest in binding['source69'].items()}
    pins.update({Path(name): digest for name, digest in binding['helpers_and_inputs'].items()})
    assert all(sha(p) == digest for p, digest in pins.items())
    output = E / f'direct-child-construction-{stage}-validation-20261019-01'
    output.mkdir()
    records = []

    def run(command, label, env=None):
        with (output / (label + '.stdout')).open('xb') as stdout, (output / (label + '.stderr')).open('xb') as stderr:
            child = subprocess.Popen(command, cwd=TRIAL, env=env, stdout=stdout, stderr=stderr)
            save(output / (label + '-launch.json'), dict(command=command, pid=child.pid, affinity=HELPERS))
            code = child.wait()
        row = dict(command=command, pid=child.pid, exit_code=code,
                   stdout_sha256=sha(output / (label + '.stdout')), stderr_sha256=sha(output / (label + '.stderr')))
        save(output / (label + '-terminal.json'), row)
        records.append(row)
        assert code == 0, (stage, label, code)

    try:
        if stage == 'build':
            run(['/usr/bin/python3', str(ROOT / 'tools/build.py'), '--crate', str(TRIAL),
                 '--mode', 'generic', '--jobs', '4', '--bin', 'rook2', '--output', str(BUILD)], 'build')
            receipt = load(BUILD / 'receipt.json')
            assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot'
            assert receipt['source_sha256_before'] == receipt['source_sha256_after'] == {k: v for k, v in binding['source69'].items() if not k.startswith('tools/')}
            assert receipt['tool_sha256_before'] == receipt['tool_sha256_after'] == {k: v for k, v in binding['source69'].items() if k.startswith('tools/')}
            baseline = load(E / 'ordinary-projected-bits-generic-build-20261018-01/receipt.json')
            for key in ['mode', 'target_triple', 'target_cpu', 'rust_flags', 'toolchain']:
                assert receipt[key] == baseline[key], key
            image = BUILD / 'rook2-exact'
            shutil.copyfile(receipt['binary_output']['path'], image)
            image.chmod(0o555)
            assert sha(image) == receipt['binary_output']['sha256']
            run(['/usr/bin/python3', str(ROOT / 'tools/archive_build.py'), str(BUILD)], 'archive')
        elif stage == 'native':
            env = dict(os.environ, RUSTC='/usr/bin/rustc', RUSTC_WRAPPER='', RUSTC_WORKSPACE_WRAPPER='',
                       RUSTFLAGS='-C target-cpu=x86-64',
                       CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64', CARGO_NET_OFFLINE='true')
            run(['/usr/bin/cargo', 'test', '--offline', '--locked', '--release', '--target',
                 'x86_64-unknown-linux-gnu', '--manifest-path', str(TRIAL / 'Cargo.toml'),
                 '--target-dir', str(TRIAL / 'target/native-tests-generic-01'), '--jobs', '4',
                 '--lib', '--bin', 'rook2-dev', '--no-run', '--message-format=json'], 'native-build', env)
            artifacts = [json.loads(line) for line in (output / 'native-build.stdout').read_text().splitlines()]
            artifacts = [a for a in artifacts if a.get('reason') == 'compiler-artifact'
                         and a.get('executable') and a.get('profile', {}).get('test')]
            assert len(artifacts) == 2
            identities = {}
            for artifact in artifacts:
                kind = artifact['target']['kind']
                name, count = ('lib', 176) if kind == ['lib'] else ('dev', 2)
                assert kind in [['lib'], ['bin']] and name not in identities
                source = Path(artifact['executable'])
                frozen = output / ('rook2-' + name + '-tests-exact')
                shutil.copyfile(source, frozen)
                frozen.chmod(0o555)
                identities[name] = dict(path=str(frozen), sha256=sha(frozen),
                                        cargo_artifact=artifact, expected_passed=count)
                save(output / (name + '-identity-before.json'), identities[name])
                run([str(frozen), '--test-threads=1'], name + '-tests', env)
                assert sha(frozen) == identities[name]['sha256']
                text = (output / (name + '-tests.stdout')).read_text()
                assert f'test result: ok. {count} passed; 0 failed;' in text
            assert set(identities) == {'lib', 'dev'}
            save(output / 'native-identities.json', dict(total_tests=178, tests=identities,
                 frozen_before_first_test_execution=True, repeated_cargo_test_execution=False))
        else:
            image = BUILD / 'rook2-exact'
            assert sha(image) == load(BUILD / 'receipt.json')['binary_output']['sha256']
            run(['/usr/bin/node', '/home/legolas/king-spec/conformance/profiling/replay-check.mjs',
                 '--', '/usr/bin/taskset', '-c', '14', str(image)], 'strict54')
            strict = load(output / 'strict54.stdout')
            assert strict['status'] == 'pass' and len(strict['results']) == 54
            assert not (output / 'strict54.stderr').stat().st_size
            run(['/usr/bin/python3', str(ROOT / 'tools/check_live.py'), '--engine', str(image),
                 '--output', str(output / 'wire')], 'wire')
            wire = load(output / 'wire/receipt.json')
            assert wire['pass'] and len(wire['results']) == 8
            assert sum(len(row['searches']) for row in wire['results']) == 24
            assert wire['engine_sha256_before'] == wire['engine_sha256_after'] == sha(image)
        assert all(sha(p) == digest for p, digest in pins.items())
        save(output / 'result.json', dict(complete=True, stage=stage, records=records,
                                         stable_source_and_inputs=True, native_timing=False))
        print(json.dumps(dict(complete=True, stage=stage)), flush=True)
    except BaseException as error:
        save(output / 'failure.json', dict(stage=stage, error=repr(error), records=records))
        raise


if __name__ == '__main__':
    main()
