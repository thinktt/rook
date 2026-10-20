#!/usr/bin/env python3
"""Focused experiment50 controls only; inert until exact parent source/build/backend admission."""
from pathlib import Path
import hashlib, json, os, re, subprocess

HERE = Path(__file__).resolve().parent
WORK = Path('/home/legolas/rook2-work/imp2-influence-mask-cancel-delta-20261019-01')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
load = lambda path: json.loads(Path(path).read_text())

def pinned(row):
    assert row is not None and row['path'] and row['sha256']
    assert sha(row['path']) == row['sha256']
    return load(row['path'])

def executed_tests(text, expected, library_total):
    # Successful actual named rows, not Cargo's exit status alone. The set and
    # multiplicity reject zero-match, duplicate, ignored and unexpected tests.
    rows = re.findall(r'^test (\S+) \.\.\. ok$', text, re.MULTILINE)
    assert len(rows) == len(set(rows)) == len(expected)
    assert set(rows) == set(expected), (rows, expected)
    assert re.findall(r'^running (\d+) tests?$', text, re.MULTILINE) == [str(len(expected))]
    summary = (f'test result: ok. {len(expected)} passed; 0 failed; 0 ignored; '
               f'0 measured; {library_total - len(expected)} filtered out;')
    assert summary in text
    return rows

def main():
    assert os.sched_getaffinity(0) == H
    assert os.environ['PATH'] == '/usr/bin:/bin'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE'])
    plan = load(HERE/'plan.json')
    clearance = load(HERE/'execution-clearance.json')  # Deliberately absent during inert preparation.
    assert plan['launch'] is True and plan['parent_review_accepted'] is True
    assert plan['backend_accepted'] is True and plan['all_other_jobs_closed'] is True
    assert clearance['launch'] is True and clearance['parent_review_accepted'] is True
    assert clearance['plan_sha256'] == sha(HERE/'plan.json')
    assert clearance['helper_sha256'] == sha(__file__)
    for path, identity in plan['input_sha256'].items():
        assert sha(path) == identity
    freeze = pinned(plan['source_freeze'])
    assert freeze['source_preparation_accepted'] is True
    assert freeze['source_graph_sha256'] == plan['source_graph_sha256']
    before = {name: sha(WORK/name) for name in freeze['files_sha256']}
    assert before == freeze['files_sha256']
    assert len(before) == plan['source_counts']['total']
    assert sum(name.startswith('tools/') for name in before) == 23
    assert plan['source_counts']['native'] + 23 == len(before)
    pinned(plan['declarations_record'])
    backend = pinned(plan['backend_acceptance'])
    assert backend['allow_focused_validation'] is True
    pinned(plan['backend_terminal'])
    terminal = load(plan['backend_terminal']['path'])
    assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code'] == 0
    assert terminal['terminal_chunk_id']
    receipt = pinned(plan['build_receipt'])
    assert receipt['mode'] == 'generic' and receipt['target_cpu'] == 'x86-64'
    assert receipt['rust_flags'] == ['-C', 'target-cpu=x86-64'] and receipt['jobs'] == 4
    assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot'
    assert receipt['source_sha256_before'] == receipt['source_sha256_after']
    assert receipt['tool_sha256_before'] == receipt['tool_sha256_after']
    assert receipt['source_sha256_before'] | receipt['tool_sha256_before'] == before
    assert sha(plan['candidate_image']['path']) == plan['candidate_image']['sha256'] == receipt['binary_output']['sha256']
    assert backend['candidate_sha256'] == plan['candidate_image']['sha256']
    build_terminal = pinned(plan['build_terminal'])
    assert build_terminal['actual_tool_terminal_observed'] is True and build_terminal['exit_code'] == 0
    assert build_terminal['terminal_chunk_id']
    library_total = plan['declarations']['library']
    assert plan['declarations']['native'] == library_total + plan['declarations']['development']
    assert plan['declarations']['development'] == 2
    new_tests = plan['experiment50_tests']
    controls = plan['existing_controls']
    assert len(new_tests) == plan['declarations']['new_experiment50']
    assert all('::experiment50_' in name for name in new_tests)
    assert len(new_tests + controls) == len(set(new_tests + controls))
    out = Path(plan['output'])
    out.mkdir(exist_ok=False)
    result = dict(complete=False, commands=[], focused_passed=0, failure=None,
                  helper_sha256=sha(__file__), plan_sha256=sha(HERE/'plan.json'),
                  actual_clearance_sha256=sha(HERE/'execution-clearance.json'),
                  source_graph_sha256=plan['source_graph_sha256'],
                  artifact_sha256=plan['candidate_image']['sha256'], library_declarations=library_total,
                  development_tests_unselected=2, full_native_suite_executed=False)
    env = dict(os.environ)
    env.update(receipt['environment_overrides'])
    try:
        groups = [('experiment50_', new_tests, False)] + [(name, [name], True) for name in controls]
        for index, (filter_name, expected, exact) in enumerate(groups):
            argv = ['/usr/bin/cargo', 'test', '--offline', '--locked', '--release',
                    '--target', receipt['target_triple'], '--jobs', '4',
                    '--target-dir', receipt['target_directory'],
                    '--manifest-path', str(WORK/'Cargo.toml'), '--lib', filter_name, '--']
            if exact:
                argv.append('--exact')
            argv.append('--test-threads=1')
            stdout = out/f'focused-{index}.stdout'
            stderr = out/f'focused-{index}.stderr'
            with stdout.open('xb') as a, stderr.open('xb') as b:
                child = subprocess.Popen(argv, cwd=WORK, env=env, stdout=a, stderr=b)
                code = child.wait()
            row = dict(argv=argv, cwd=str(WORK), pid=child.pid, exit_code=code,
                actual_child_return_observed=True, process_role='cargo test supervisor',
                stdout=str(stdout), stderr=str(stderr), stdout_sha256=sha(stdout), stderr_sha256=sha(stderr),
                expected_tests=expected)
            result['commands'].append(row)
            assert code == 0, (filter_name, code)
            row['observed_tests'] = executed_tests(stdout.read_text(), expected, library_total)
            result['focused_passed'] += len(expected)
        assert {name: sha(WORK/name) for name in before} == before
        assert sha(plan['candidate_image']['path']) == plan['candidate_image']['sha256']
        result.update(complete=True, source_and_tools_unchanged=True, artifact_unchanged=True,
                      source_sha256_before=before, source_sha256_after=before)
    except BaseException as error:
        result['failure'] = repr(error)
    finally:
        with (out/'result.json').open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ['commands', 'source_sha256_before', 'source_sha256_after']}))
    return 0 if result['complete'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
