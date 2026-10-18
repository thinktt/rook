#!/usr/bin/env python3
"""Isolated shared-kernel diagnostic verification; requires prior native timing terminal."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('/tmp/imp2-eval-pawn-context-20261018')
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def run(argv, stdout, stderr, env):
    with stdout.open('xb') as out, stderr.open('xb') as err:
        result = subprocess.run(argv, cwd=ROOT, env=env, stdout=out, stderr=err)
    return dict(command=argv, exit_code=result.returncode,
                stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', default='20261018', help='Fresh attempt label; preserve failed attempts')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.label):
        parser.error('invalid attempt label')
    plan = json.loads((HERE/'plan.json').read_text())
    live = Path(plan['live_collection'])
    terminal = Path(plan['collection_terminal'])
    if not terminal.exists():
        parser.error('no terminal collection receipt; poll its existing tool handle before starting native verification')
    actual_terminal = json.loads(terminal.read_text())
    if actual_terminal['collector_returncode'] != 0 or not actual_terminal['stable_dependencies']:
        parser.error('collection did not terminate successfully with stable dependencies')
    live_manifest = json.loads((live/'manifest.json').read_text())
    live_summary = json.loads((live/'summary.json').read_text())
    if not live_summary['complete'] or len(live_summary['runs']) != 216 or sha(live/'summary.json') != actual_terminal['summary_sha256']:
        parser.error('terminal receipt and complete216-lifetime collection differ')
    required_receipts = [Path(path) for path in plan.get('required_terminal_receipts', [])]
    if any(not path.exists() for path in required_receipts):
        parser.error('required pilot terminal receipt missing; poll its original tool handle first')
    for receipt_path in required_receipts:
        if json.loads(receipt_path.read_text())['exit_code'] != 0:
            parser.error('required pilot did not terminate successfully; preserve and resolve its evidence first')
    driver_paths = {*plan.get('additional_drivers', [])}
    native_images = {live_manifest['engine'], *plan.get('additional_native_images', [])}
    active = []
    for process in Path('/proc').iterdir():
        if not process.name.isdigit(): continue
        try:
            argv = (process/'cmdline').read_bytes().decode().split('\0')
            image = os.readlink(process/'exe')
            cwd = Path(os.readlink(process/'cwd'))
            resolved = {str((Path(arg) if Path(arg).is_absolute() else cwd/arg).resolve()) for arg in argv if arg and not arg.startswith('-')}
            if (driver_paths & resolved or image in native_images
                    or (str(ROOT/'tools/collect_ordinary.py') in resolved and str(live) in resolved)):
                active.append(int(process.name))
        except (OSError, UnicodeDecodeError):
            pass
    if active:
        parser.error(f'collection or named native image is still live: {active}')
    if any(sha(Path(p)) != digest for p,digest in plan['fixtures'].items()):
        parser.error('declared fixture changed')
    reference = json.loads(Path(plan['native_build_reference']).read_text())
    native_before = source_snapshot(SOURCE)
    if native_before != reference['source_sha256_before']:
        parser.error('native library differs from the declared source closure; retain a new explicit plan')
    preparation = HERE/plan['adapter_preparation']
    prepared = json.loads(preparation.read_text())
    if source_snapshot(SOURCE/'diagnostic') != prepared['adapter_source_sha256']:
        parser.error('adapter source differs from the reviewed preparation')
    if sha(HERE/prepared['archive']) != prepared['archive_sha256'] or sha(Path(__file__)) != prepared['planned_verifier_sha256']:
        parser.error('prepared archive or verifier differs from the declared identity')
    output = ROOT/'evidence'/('diagnostic-eval-pawn-context-'+args.label)
    build = ROOT/'evidence'/('diagnostic-eval-pawn-context-build-'+args.label)
    if output.exists() or build.exists(): parser.error('attempt output/build must be absent')
    output.mkdir()
    env = dict(os.environ, RUSTFLAGS='-C target-cpu=x86-64',
               CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64', CARGO_NET_OFFLINE='true', CARGO_BUILD_JOBS='4')
    helpers = {0,1,2,3,4,5,8,9,10,11,12,13}
    os.sched_setaffinity(0, os.sched_getaffinity(0) & helpers)
    adapter_before = source_snapshot(SOURCE/'diagnostic')
    dependencies = [Path(__file__), HERE/'plan.json', preparation, HERE/prepared['archive'],
                    ROOT/'tools/build.py', ROOT/'tools/archive_build.py', Path(plan['native_build_reference']),
                    Path('/home/legolas/king-spec/conformance/run.mjs'), terminal, *required_receipts,
                    *map(Path,plan['fixtures'])]
    before = {str(p):sha(p) for p in dependencies}
    write(output/'inputs-before.json', dict(native=native_before, adapter=adapter_before,
        dependencies=before, environment={k:env[k] for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']},
        helper_affinity=sorted(os.sched_getaffinity(0)), collection_matching_processes=active,
        scope='External adapter verification only; ordinary production binary is unchanged'))
    receipt = dict(complete=False, failure=None, stages=[])
    try:
        command = ['cargo','test','--offline','--locked','--release','--no-run','--message-format=json',
                   '--manifest-path',str(SOURCE/'diagnostic/Cargo.toml')]
        stage = run(command, output/'unit-build.stdout', output/'unit-build.stderr', env)
        receipt['stages'].append(stage); assert stage['exit_code'] == 0, 'unit compilation failed'
        artifacts = []
        for line in (output/'unit-build.stdout').read_text().splitlines():
            item = json.loads(line)
            if item.get('reason') == 'compiler-artifact' and item['profile']['test'] and item.get('executable'):
                artifacts.append(Path(item['executable']))
        assert len(artifacts) == 1, 'unit test executable inventory'
        (output/'unit-bin').mkdir()
        tests = output/'unit-bin/rook2-diag-exact'
        shutil.copy2(artifacts[0], tests)
        test_sha = sha(tests)
        stage = run([str(tests)], output/'unit-tests.stdout', output/'unit-tests.stderr', env)
        receipt['stages'].append(stage); assert stage['exit_code'] == 0, 'unit tests failed'
        assert test_sha == sha(tests), 'unit image changed'
        match = re.search(r'test result: ok\. (\d+) passed; 0 failed;', (output/'unit-tests.stdout').read_text())
        assert match and int(match[1]) == plan['expected_unit_tests'], 'unit test count'
        receipt['unit_binary_sha256'] = test_sha
        assert source_snapshot(SOURCE/'diagnostic') == adapter_before and source_snapshot(SOURCE) == native_before, 'source changed during unit verification'
        command = [sys.executable,str(ROOT/'tools/build.py'),'--crate',str(SOURCE/'diagnostic'),
                   '--bin','rook2-diag','--mode','generic','--output',str(build)]
        stage = run(command, output/'build-driver.stdout', output/'build-driver.stderr', env)
        receipt['stages'].append(stage); assert stage['exit_code'] == 0, 'production adapter build failed'
        build_receipt = json.loads((build/'receipt.json').read_text())
        frozen = build/'rook2-diag-exact'
        shutil.copy2(build_receipt['binary_output']['path'], frozen)
        adapter_sha = sha(frozen)
        assert adapter_sha == build_receipt['binary_output']['sha256'], 'frozen adapter mismatch'
        command = [sys.executable,str(ROOT/'tools/archive_build.py'),str(build)]
        stage = run(command, output/'archive.stdout', output/'archive.stderr', env)
        receipt['stages'].append(stage); assert stage['exit_code'] == 0, 'adapter source archive failed'
        command = ['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
        for path in plan['fixtures']: command += ['--fixtures',path]
        command += ['--',str(frozen)]
        stage = run(command, output/'conformance.json', output/'conformance.stderr', env)
        receipt['stages'].append(stage); assert stage['exit_code'] == 0, 'external conformance failed'
        report = json.loads((output/'conformance.json').read_text())
        assert report['pass'] and len(report['results']) == plan['expected_case_count'], 'external result count'
        assert not (output/'conformance.stderr').stat().st_size, 'unexpected conformance stderr'
        assert adapter_sha == sha(frozen), 'adapter changed during conformance'
        receipt.update(complete=True, adapter_sha256=adapter_sha, cases=len(report['results']))
    except BaseException as error:
        receipt['failure'] = f'{type(error).__name__}: {error}'
    finally:
        native_after, adapter_after = source_snapshot(SOURCE), source_snapshot(SOURCE/'diagnostic')
        after = {str(p):sha(p) for p in dependencies}
        stable = native_after == native_before and adapter_after == adapter_before and after == before
        receipt['inputs_stable'] = stable
        if not stable: receipt.update(complete=False, failure='source/dependency changed')
        write(output/'inputs-after.json', dict(native=native_after, adapter=adapter_after, dependencies=after))
        write(output/'verification.json', receipt)
    print(json.dumps(dict(output=str(output), complete=receipt['complete'], failure=receipt['failure'])))
    return 0 if receipt['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
