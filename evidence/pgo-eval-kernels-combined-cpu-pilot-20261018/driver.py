#!/usr/bin/env python3
"""Frozen six-case baseline/table/combined own-PGO pilot; strict oracle and direct native accounting."""
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
    'baseline': 'production-bitplanes-use-build-20261018',
    'states': 'pgo-relation-states-use-build-20261018',
    'combined': 'pgo-eval-kernels-combined-use-build-20261018',
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
    paths = {k:ROOT/'evidence'/v/'rook2-exact' for k,v in VARIANTS.items()}
    validation = {}
    for name,build_directory,check_directory,replay_name,wire_directory in [
        ('baseline','production-bitplanes-use-build-20261018','production-bitplanes-use-check-20261018','profile-all.json','production-bitplanes-interruption-wire-20261018'),
        ('states','pgo-relation-states-use-build-20261018','pgo-relation-states-use-check-20261018','profile-all.stdout','pgo-relation-states-interruption-wire-20261018'),
        ('combined','pgo-eval-kernels-combined-use-build-20261018','pgo-eval-kernels-combined-use-check-20261018','profile-all.stdout','pgo-eval-kernels-combined-interruption-wire-20261018'),
    ]:
        build = ROOT/'evidence'/build_directory/'receipt.json'
        identity_path = ROOT/'evidence'/check_directory/'identity.json'
        replay_path = identity_path.parent/replay_name
        wire_path = ROOT/'evidence'/wire_directory/'receipt.json'
        identity = json.loads(identity_path.read_text())
        report = json.loads(replay_path.read_text())
        wire = json.loads(wire_path.read_text())
        assert sha(paths[name]) == identity['native_artifact_sha256']
        assert sha(build) == identity['build_receipt_sha256']
        assert sha(replay_path) == identity['replay_sha256']
        assert identity['missing_function_warnings'] == 0
        assert report['status'] == 'pass' and len(report['results']) == 54
        assert wire['pass'] and len(wire['results']) == 8
        assert wire['engine_sha256_before'] == wire['engine_sha256_after'] == sha(paths[name])
        validation[name] = {str(p):sha(p) for p in [build,identity_path,replay_path,wire_path]}
    write('validation-before.json', validation)

    write('suite.json', dict(cases=CASES, variants={k: dict(path=str(v), sha256=sha(v)) for k, v in paths.items()},
                            order='Cases in declared order; each compare_ordinary.py uses one warmup/variant then four alternating forward/reverse rounds',
                            driver_sha256=sha(Path(__file__)), performance='Reported-only local pilot; no reference qualification'))
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
