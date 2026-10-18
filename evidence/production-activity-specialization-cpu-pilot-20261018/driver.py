#!/usr/bin/env python3
"""Frozen six-case canonical own-PGO static piece-kind activity traversal pilot; strict oracle and direct native accounting."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from measure import cgroup_snapshot

CASES = ['profile-01', 'profile-02', 'profile-04', 'profile-05', 'profile-35', 'profile-29']
VARIANTS = {
    'baseline': 'production-eval-kernels-use-build-20261018',
    'specialized': 'production-activity-specialization-use-build-20261018',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def context():
    return dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                uname=list(os.uname()), helper_affinity=sorted(os.sched_getaffinity(0)),
                cgroups=cgroup_snapshot(), proc_stat=Path('/proc/stat').read_text(),
                loadavg=Path('/proc/loadavg').read_text(),
                owned_background_work='No owned build, other engine collection, or profiling run active',
                scope='Point-in-time local observation, no assertion of exclusive host ownership',
                pmu='Last retained disabled self-scoped open EACCES; no fresh probe or PMU data in this pilot')


def main():
    controls = {
        'baseline': ROOT/'evidence/production-eval-kernels-use-check-20261018/identity.json',
        'specialized': ROOT/'evidence/production-activity-specialization-use-check-20261018/identity.json',
    }
    training = ROOT/'evidence/production-activity-specialization-training-20261018/verification.json'
    pilot = ROOT/'evidence/activity-specialization-cpu-pilot-20261018'
    assert json.loads((pilot/'tool-terminal.json').read_text())['exit_code'] == 0
    assert json.loads((pilot/'analysis.json').read_text())['complete']
    assert json.loads(training.read_text())['complete']
    assert json.loads((controls['specialized'].parent/'tool-terminal.json').read_text())['exit_code'] == 0
    paths = {k:ROOT/'evidence'/v/'rook2-exact' for k,v in VARIANTS.items()}
    validation = {}
    for name,directory in VARIANTS.items():
        check = controls[name]
        identity = json.loads(check.read_text())
        assert identity['status'] == 'all54-strict-replays-and-eight-interruption-fixtures-pass'
        build = ROOT/'evidence'/directory/'receipt.json'
        replay = check.parent/'profile-all.stdout'
        r = json.loads(replay.read_text())
        assert r['status'] == 'pass' and len(r['results']) == 54
        assert sha(build) == identity['build_receipt_sha256']
        assert sha(replay) == identity['replay_sha256']
        assert sha(paths[name]) == identity['native_artifact_sha256']
        wire = ROOT/'evidence'/('production-eval-kernels-interruption-wire-20261018' if name == 'baseline' else 'production-activity-specialization-interruption-wire-20261018')/'receipt.json'
        w = json.loads(wire.read_text())
        assert w['pass'] and len(w['results']) == 8
        assert w['engine_sha256_before'] == w['engine_sha256_after'] == sha(paths[name])
        assert sha(wire) == identity['wire_receipt_sha256']
        validation[name] = {str(p):sha(p) for p in [check,build,replay,wire,training,pilot/'analysis.json',pilot/'tool-terminal.json']}
    write('validation-before.json', validation)

    write('suite.json', dict(cases=CASES, variants={k: dict(path=str(v), sha256=sha(v)) for k, v in paths.items()},
                            order='Cases in declared order; each compare_ordinary.py uses one warmup/variant then four alternating forward/reverse rounds',
                            driver_sha256=sha(Path(__file__)), performance='Reported-only matched canonical independently trained PGO static piece-kind activity traversal pilot; no PGO or reference qualification'))
    write('context-before.json', context())
    summaries = {}
    for case in CASES:
        command = [sys.executable, str(ROOT / 'tools/compare_ordinary.py'), '--case', case, '--output', str(OUT / case)]
        for name, path in paths.items():
            command += ['--variant', name + '=' + str(path)]
        with (OUT / (case + '.stdout')).open('x') as stdout, (OUT / (case + '.stderr')).open('x') as stderr:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        r = json.loads((OUT / case / 'summary.json').read_text())
        assert result.returncode == 0 and r['complete'], (case, result.returncode, r['failure'])
        summaries[case] = r['summaries']
        print(json.dumps(dict(case=case, summaries=r['summaries'])), flush=True)
    write('context-after.json', context())
    assert all(sha(Path(path)) == digest for files in validation.values() for path,digest in files.items()), 'validation changed'
    write('suite-summary.json', dict(complete=True, summaries=summaries,
                                    artifact_hashes_after={k:sha(v) for k,v in paths.items()}))


if __name__ == '__main__':
    main()
