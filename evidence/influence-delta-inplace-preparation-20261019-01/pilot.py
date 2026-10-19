#!/usr/bin/env python3
"""One declared experiment30 matched CPU pilot using the unchanged comparator."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path('/home/legolas/rook2')
sys.path.insert(0, str(ROOT / 'tools'))
from measure import cgroup_snapshot

HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
CASES = ['profile-01', 'profile-02', 'profile-04', 'profile-05', 'profile-29', 'profile-35', 'profile-08']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def jobs():
    found = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            exe = os.readlink(entry / 'exe')
            if Path(exe).name.startswith(('rook2', 'cargo', 'rustc', 'callgrind', 'valgrind', 'git', 'objdump', 'readelf', 'llvm-profdata', 'nm', 'tar')):
                found.append(dict(pid=int(entry.name), executable=exe))
        except OSError:
            pass
    return found


def context():
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                helper_affinity=sorted(os.sched_getaffinity(0)), uname=list(os.uname()),
                proc_stat=Path('/proc/stat').read_text(), loadavg=Path('/proc/loadavg').read_text(),
                cgroups=cgroup_snapshot(), native_jobs=jobs(),
                scope='Point guest observations only, no exclusive host or continuous sibling-ownership claim.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True, type=Path)
    args = parser.parse_args()
    plan = read(args.plan)
    assert plan['parent_review_complete'] and plan['all_owned_jobs_closed']
    assert plan['cases'] == CASES and list(plan['variants']) == ['baseline', 'candidate']
    assert sorted(os.sched_getaffinity(0)) == HELPERS
    assert os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE', 'NODE_OPTIONS'])
    assert sha(__file__) == plan['driver_sha256']
    for path, digest in plan['immutable_inputs'].items():
        assert sha(path) == digest, path
    for variant in plan['variants'].values():
        assert sha(variant['path']) == variant['sha256']
    assert not jobs(), 'Unclosed native/build/codegen/profile/archive job'
    output = Path(plan['output'])
    output.mkdir()
    save(output / 'plan.json', plan)
    save(output / 'context-before.json', context())
    result = dict(complete=False, failure=None, cases=[], lifetimes=0)
    try:
        for case in CASES:
            command = ['/usr/bin/python3', str(ROOT / 'tools/compare_ordinary.py'),
                       '--case', case, '--output', str(output / case)]
            for name, variant in plan['variants'].items():
                command += ['--variant', name + '=' + variant['path']]
            with (output / (case + '.stdout')).open('xb') as stdout, (output / (case + '.stderr')).open('xb') as stderr:
                child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
                code = child.wait()
            save(output / (case + '-terminal.json'), dict(command=command, pid=child.pid, exit_code=code))
            report = read(output / case / 'summary.json')
            assert code == 0 and report['complete'] and report['failure'] is None
            assert not (output / (case + '.stderr')).stat().st_size
            assert len(report['runs']) == 10
            result['cases'].append(dict(case=case, summaries=report['summaries']))
            result['lifetimes'] += 10
            print(json.dumps(result['cases'][-1]), flush=True)
        assert result['lifetimes'] == 70
        assert not jobs()
        for path, digest in plan['immutable_inputs'].items():
            assert sha(path) == digest, path
        for variant in plan['variants'].values():
            assert sha(variant['path']) == variant['sha256']
        save(output / 'context-after.json', context())
        result['complete'] = True
    except BaseException as error:
        result['failure'] = repr(error)
        raise
    finally:
        save(output / 'result.json', result)
    print(json.dumps(dict(complete=True, lifetimes=70)), flush=True)


if __name__ == '__main__':
    main()
