#!/usr/bin/env python3
"""Two fresh strict replays for an instrumented branch census, never speed."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path('/home/legolas/rook2')
HERE = Path(__file__).resolve().parent
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
H = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
sys.path.insert(0, str(ROOT / 'tools'))
from compare_ordinary import stop_owned


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    plan = read(HERE / 'execution-binding.json')
    assert plan['parent_source_review_complete'] and plan['all_native_jobs_closed']
    assert plan['cases'] == ['profile-35', 'profile-08']
    assert plan['collector_sha256'] == sha(__file__)
    assert sorted(os.sched_getaffinity(0)) == H
    assert os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE', 'NODE_OPTIONS'])
    for name, digest in plan['immutable_inputs'].items():
        assert sha(name) == digest, name
    engine = plan['engine']
    assert sha(engine['path']) == engine['sha256']
    output = Path(plan['output'])
    output.mkdir()
    save(output / 'plan.json', plan)
    result = dict(complete=False, failure=None, engine_runs=0, cases=[],
                  scope='Instrumented whole-process branch counts; no CPU, traffic or qualification claim')
    try:
        for case in plan['cases']:
            directory = output / case
            directory.mkdir()
            census_path = directory / 'census.json'
            native_path = directory / 'native.json'
            command = ['/usr/bin/node', str(SPEC / 'replay-check.mjs'), '--case', case, '--',
                       '/usr/bin/python3', str(ROOT / 'tools/account_native.py'),
                       '--engine', engine['path'], '--record', str(native_path), '--known-single-process']
            stdout_path = directory / 'comparator.stdout'
            stderr_path = directory / 'comparator.stderr'
            environment = dict(os.environ, ROOK2_INFLUENCE_CENSUS_PATH=str(census_path))
            with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
                child = subprocess.Popen(command, cwd=ROOT, env=environment,
                                         stdout=stdout, stderr=stderr, start_new_session=True)
                save(directory / 'launch.json', dict(command=command, pid=child.pid,
                     census_path=str(census_path), helper_affinity=H, engine_cpu=14))
                try:
                    deadline = time.monotonic() + 960
                    while child.poll() is None:
                        assert time.monotonic() < deadline, 'census replay deadline'
                        assert stdout_path.stat().st_size <= 8388608 and stderr_path.stat().st_size <= 8388608
                        time.sleep(.05)
                except BaseException:
                    stop_owned(child)
                    raise
            save(directory / 'terminal.json', dict(pid=child.pid, exit_code=child.returncode))
            assert child.returncode == 0 and stderr_path.stat().st_size == 0
            replay, native, census = read(stdout_path), read(native_path), read(census_path)
            assert replay['status'] == 'pass' and replay['selectedCases'] == [case] and len(replay['results']) == 1
            assert native['failure'] is None and native['native_exit_code'] == 0
            assert native['engine_sha256_before'] == native['engine_sha256_after'] == engine['sha256']
            assert native['native_pre_exec']['affinity'] == native['native_post_exec']['affinity'] == [14]
            assert native['native_post_exec']['tasks'] == [str(native['native_pid'])]
            assert native['supervisor_affinity'] == H
            rows = census['ordinary_first_fill_by_origin']
            assert census['schema'] == 'influence-delta-demand-census-v1'
            assert census['scope'] == 'whole-native-process'
            assert len(rows) == 5 and [row['origin'] for row in rows] == list(range(5))
            values = [census['fresh_build_entries'], census['update_entries'], census['ready_hits']]
            values += [row[key] for row in rows for key in ['eligible', 'unlinked']]
            assert all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in values)
            eligible = sum(row['eligible'] for row in rows)
            unlinked = sum(row['unlinked'] for row in rows)
            assert census['ordinary_first_fill_total'] == eligible + unlinked
            assert census['ordinary_eligible_first_fill_total'] == eligible
            assert census['ordinary_unlinked_first_fill_total'] == unlinked
            assert eligible == census['update_entries']
            assert sum(row['eligible'] for row in rows[:4]) == 0
            assert unlinked <= census['fresh_build_entries']
            result['engine_runs'] += 1
            result['cases'].append(dict(case=case, native_pid=native['native_pid'], counts=census,
                 ordinary_first_fills=eligible + unlinked,
                 eligible_fraction=eligible / (eligible + unlinked) if eligible + unlinked else None,
                 other_fresh_entries=census['fresh_build_entries'] - unlinked,
                 census_sha256=sha(census_path), native_sha256=sha(native_path), replay_sha256=sha(stdout_path)))
            print(json.dumps(result['cases'][-1]), flush=True)
        assert result['engine_runs'] == 2
        assert len({row['native_pid'] for row in result['cases']}) == 2
        offline = subprocess.run(['/usr/bin/node', str(HERE / 'check_census.mjs'), str(output)],
                                 capture_output=True, text=True, check=True)
        save(output / 'offline-replay.json', json.loads(offline.stdout))
        assert not offline.stderr and json.loads(offline.stdout) == dict(originalCheckReplayCount=2, engineRuns=0)
        for name, digest in plan['immutable_inputs'].items():
            assert sha(name) == digest, name
        assert sha(engine['path']) == engine['sha256']
        result['complete'] = True
    except BaseException as error:
        result['failure'] = repr(error)
        raise
    finally:
        save(output / 'result.json', result)
    print(json.dumps(dict(complete=True, engine_runs=2, cpu_benchmark=False)), flush=True)


if __name__ == '__main__':
    main()
