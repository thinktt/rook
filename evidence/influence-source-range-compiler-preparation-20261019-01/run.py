#!/usr/bin/env python3
"""Run the frozen45 generic build or its backend-admitted focused controls."""
from pathlib import Path
import datetime, hashlib, json, os, re, shutil, subprocess, sys

R = Path('/home/legolas/rook2')
E = R / 'evidence'
P = Path(__file__).resolve().parent
W = Path('/home/legolas/rook2-work/imp2-influence-source-range-20261019-01')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())


def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def field(value, dotted):
    for part in dotted.split('.'):
        value = value[part]
    return value


def checked_record(row):
    assert row is not None and row['proof'] is not None and row['terminal'] is not None
    for key in ['proof', 'terminal']:
        assert sha(row[key]['path']) == row[key]['sha256']
    terminal = load(row['terminal']['path'])
    assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code'] == 0
    assert terminal['terminal_chunk_id']
    proof = load(row['proof']['path'])
    for key, expected in row.get('proof_checks', {}).items():
        assert field(proof, key) == expected, key
    for key in row.get('nonempty_fields', []):
        assert field(proof, key), key
    return proof, terminal


def admission(mode):
    plan = load(P/'plan.json'); clearance = load(P/'execution-clearance.json')
    assert plan['launch'] is True and plan['parent_review_accepted'] is True
    assert clearance['launch'] is True and clearance['parent_review_accepted'] is True
    assert clearance['plan_sha256'] == sha(P/'plan.json') and clearance['helper_sha256'] == sha(__file__)
    assert mode in clearance['authorized_modes']
    for path, identity in plan['input_sha256'].items():
        assert sha(path) == identity
    assert set(plan['prerequisites']) == {'current43_whole12_collector', 'current43_whole12_independent'}
    collector, terminal = checked_record(plan['prerequisites']['current43_whole12_collector'])
    assert collector['games12']['actual_terminal_chunk'] == terminal['terminal_chunk_id']
    checked_record(plan['prerequisites']['current43_whole12_independent'])
    if mode == 'focused':
        acceptance, _ = checked_record(plan['focused_backend_acceptance'])
        assert acceptance['allow_focused_validation'] is True
    assert sha(plan['source_freeze']['path']) == plan['source_freeze']['sha256']
    return plan


def main():
    mode = sys.argv[1]
    assert mode in ('build', 'focused')
    assert set(os.sched_getaffinity(0)) == H
    assert os.environ['PATH'] == '/usr/bin:/bin'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE'])
    plan = admission(mode)  # Closed current43 whole12 + independent proof before any runtime/output.
    freeze = load(plan['source_freeze']['path'])
    assert freeze['source_preparation_accepted'] and freeze['source_graph_sha256'] == plan['source_graph_sha256']
    before = {n: sha(W/n) for n in freeze['files_sha256']}
    assert before == freeze['files_sha256']
    assert {n: sha(R/n) for n in before if n.startswith('tools/')} == {n: h for n, h in before.items() if n.startswith('tools/')}
    out = E / ('influence-source-range-' + ('generic-build-execution' if mode == 'build' else 'focused-native-check') + '-20261019-01')
    out.mkdir(exist_ok=False)
    build = E / 'influence-source-range-generic-build-20261019-01'
    commands = []

    def run(argv, stem, env=None):
        with (out/(stem+'.stdout')).open('xb') as o, (out/(stem+'.stderr')).open('xb') as e:
            child = subprocess.Popen(argv, cwd=W, env=env, stdout=o, stderr=e)
            code = child.wait()
        row = dict(argv=argv, pid=child.pid, exit_code=code, actual_child_return_observed=True,
                   stdout_sha256=sha(out/(stem+'.stdout')), stderr_sha256=sha(out/(stem+'.stderr')))
        commands.append(row)
        assert code == 0, row
        return row

    result = dict(complete=False, mode=mode, commands=commands, failure=None,
                  helper_sha256=sha(__file__), source_freeze_sha256=sha(plan['source_freeze']['path']),
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        if mode == 'build':
            run(['/usr/bin/python3', str(R/'tools/build.py'), '--crate', str(W), '--mode', 'generic',
                 '--bin', 'rook2', '--jobs', '4', '--output', str(build)], 'build')
            b = load(build/'receipt.json')
            assert b['outcome'] == 'build-succeeded-with-stable-input-snapshot'
            assert {k: b[k] for k in plan['expected_build']} == plan['expected_build']
            assert b['source_sha256_before'] | b['tool_sha256_before'] == before
            assert b['source_sha256_before'] == b['source_sha256_after']
            assert b['tool_sha256_before'] == b['tool_sha256_after']
            image = build/'rook2-exact'
            shutil.copy2(b['binary_output']['path'], image)
            image.chmod(0o555)
            assert sha(image) == b['binary_output']['sha256']
            save(build/'frozen-image.json', dict(path=str(image), sha256=sha(image), bytes=image.stat().st_size,
                 mode='0555', source_graph=freeze['source_graph_sha256']))
            run(['/usr/bin/python3', str(R/'tools/archive_build.py'), str(build)], 'archive')
            result['artifact_sha256'] = sha(image)
        else:
            acceptance, _ = checked_record(plan['focused_backend_acceptance'])
            assert acceptance['allow_focused_validation'] is True
            b = load(build/'receipt.json')
            assert acceptance['candidate_sha256'] == sha(build/'rook2-exact') == b['binary_output']['sha256']
            env = os.environ.copy()
            env.update(b['environment_overrides'])
            for index, name in enumerate(plan['focused_tests']):
                stem = 'focused-' + str(index)
                run(['/usr/bin/cargo', 'test', '--offline', '--locked', '--release', '--target', b['target_triple'],
                     '--jobs', '4', '--target-dir', b['target_directory'], '--manifest-path', str(W/'Cargo.toml'),
                     '--lib', name, '--', '--exact', '--test-threads=1'], stem, env)
                text = (out/(stem+'.stdout')).read_text()
                assert ('test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; ' + str(plan['library_declarations'] - 1) + ' filtered out;') in text
                assert name in text
            result.update(focused_passed=len(plan['focused_tests']), library_declarations=plan['library_declarations'], development_tests_unselected=2,
                          full_native_suite_executed=False)
        assert {n: sha(W/n) for n in before} == before
        result.update(complete=True, source_unchanged=True)
    except BaseException as error:
        result['failure'] = repr(error)
    finally:
        save(out/'result.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'commands'}))
    return 0 if result['complete'] else 1


if __name__ == '__main__':
    sys.exit(main())
