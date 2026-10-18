#!/usr/bin/env python3
"""Frozen six-case generic typed-list influence pilot; strict oracle and direct native accounting."""
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
    'baseline': 'relation-baseline-bitplanes-build-20261018',
    'groups': 'influence-groups-build-20261018',
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
    baseline_check = ROOT/'evidence/relation-kernel-bitplanes-check-20261018/verification.json'
    candidate_check = ROOT/'evidence/influence-groups-check-20261018/identity.json'
    units = ROOT/'evidence/influence-groups-preparation-20261018/native-verification.json'
    baseline = json.loads(baseline_check.read_text())
    candidate = json.loads(candidate_check.read_text())
    native_units = json.loads(units.read_text())
    assert baseline['complete'] and baseline['variants']['baseline']['cases'] == 54
    assert native_units['complete'] and native_units['units']['rook2']['passed'] == 132
    replay_path = candidate_check.parent/'profile-all.stdout'
    replay = json.loads(replay_path.read_text())
    assert replay['status'] == 'pass' and len(replay['results']) == 54
    assert sha(replay_path) == candidate['replay_sha256']
    wire = ROOT/'evidence/influence-groups-interruption-wire-20261018/receipt.json'
    wire_report = json.loads(wire.read_text())
    assert wire_report['pass'] and len(wire_report['results']) == 8
    assert wire_report['engine_sha256_before'] == wire_report['engine_sha256_after'] == candidate['native_artifact_sha256']
    assert sha(wire) == candidate['wire_receipt_sha256']
    paths = {k:ROOT/'evidence'/v/'rook2-exact' for k,v in VARIANTS.items()}
    assert sha(paths['baseline']) == baseline['variants']['baseline']['artifact_sha256']
    assert sha(paths['groups']) == candidate['native_artifact_sha256']
    validation = {}
    for name,directory,check in [('baseline',VARIANTS['baseline'],baseline_check),('groups',VARIANTS['groups'],candidate_check)]:
        build = ROOT/'evidence'/directory/'receipt.json'
        expected = baseline['variants']['baseline']['build_receipt_sha256'] if name == 'baseline' else candidate['build_receipt_sha256']
        assert sha(build) == expected
        validation[name] = {str(p):sha(p) for p in [build,check,units,wire]}
    write('validation-before.json', validation)

    write('suite.json', dict(cases=CASES, variants={k: dict(path=str(v), sha256=sha(v)) for k, v in paths.items()},
                            order='Cases in declared order; each compare_ordinary.py uses one warmup/variant then four alternating forward/reverse rounds',
                            driver_sha256=sha(Path(__file__)), performance='Reported-only matched generic typed-list influence pilot; no PGO or reference qualification'))
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
