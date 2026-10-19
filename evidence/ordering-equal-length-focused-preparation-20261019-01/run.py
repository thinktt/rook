#!/usr/bin/env python3
"""Run six existing controls after the parent-admitted49 compiler gate."""
from pathlib import Path
import hashlib, json, os, subprocess

ROOT = Path('/home/legolas/rook2')
E = ROOT / 'evidence'
HERE = Path(__file__).resolve().parent
WORK = Path('/home/legolas/rook2-work/imp2-ordering-equal-length-20261019-01')
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
load = lambda path: json.loads(Path(path).read_text())

def main():
    assert os.sched_getaffinity(0) == {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
    assert os.environ['PATH'] == '/usr/bin:/bin'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE'])
    decision = load(E/'ordering-equal-length-parent-backend-review-20261019-01/decision.json')
    assert decision['allow_focused_validation'] and decision['bounds_checks_reduced']
    assert decision['sort_semantics_and_public_helper_preserved'] and decision['workspace_capacity_unchanged']
    freeze = load(E/'ordering-equal-length-parent-review-20261019-01/source-freeze.json')
    assert freeze['source_preparation_accepted'] and freeze['changed_files'] == ['src/tactical.rs']
    assert {p: sha(WORK/p) for p in freeze['files_sha256']} == freeze['files_sha256']
    build = E/'ordering-equal-length-generic-build-20261019-01'
    receipt = load(build/'receipt.json')
    assert sha(build/'rook2-exact') == decision['candidate_sha256'] == receipt['binary_output']['sha256']
    assert receipt['source_sha256_before'] | receipt['tool_sha256_before'] == freeze['files_sha256']
    tests = decision['focused_tests']
    assert len(tests) == 6 and decision['library_declarations'] == 187
    out = E/'ordering-equal-length-focused-native-check-20261019-01'
    out.mkdir(exist_ok=False)
    result = dict(complete=False, commands=[], focused_passed=0, failure=None,
                  helper_sha256=sha(__file__), library_declarations=187,
                  development_tests_unselected=2, full_native_suite_executed=False)
    env = dict(os.environ)
    env.update(receipt['environment_overrides'])
    try:
        for index, name in enumerate(tests):
            argv = ['/usr/bin/cargo', 'test', '--offline', '--locked', '--release',
                    '--target', receipt['target_triple'], '--jobs', '4',
                    '--target-dir', receipt['target_directory'],
                    '--manifest-path', str(WORK/'Cargo.toml'), '--lib', name,
                    '--', '--exact', '--test-threads=1']
            stdout = out/f'focused-{index}.stdout'
            stderr = out/f'focused-{index}.stderr'
            with stdout.open('xb') as a, stderr.open('xb') as b:
                child = subprocess.Popen(argv, cwd=WORK, env=env, stdout=a, stderr=b)
                code = child.wait()
            result['commands'].append(dict(argv=argv, pid=child.pid, exit_code=code,
                actual_child_return_observed=True, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
            assert code == 0, (name, code)
            text = stdout.read_text()
            assert name in text and '1 passed; 0 failed; 0 ignored; 0 measured; 186 filtered out' in text
            result['focused_passed'] += 1
        assert {p: sha(WORK/p) for p in freeze['files_sha256']} == freeze['files_sha256']
        result.update(complete=True, source_unchanged=True)
    except BaseException as error:
        result['failure'] = repr(error)
    finally:
        with (out/'result.json').open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'commands'}))
    return 0 if result['complete'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
