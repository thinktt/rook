#!/usr/bin/env python3
"""Frozen six-case generic destination-table generation pilot; strict oracle and direct native accounting."""
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
    'baseline': 'activity-specialization-build-20261018',
    'rays': 'generation-rays-build-20261018',
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
    check_path = ROOT / 'evidence/generation-rays-check-20261018/verification.json'
    units = ROOT / 'evidence/generation-rays-preparation-20261018/native-verification.json'
    focused_terminal = ROOT / 'evidence/focused-eval-kernels-20261018/tool-terminal.json'
    check_terminal = check_path.parent / 'tool-terminal.json'
    focused_check = focused_terminal.parent / 'verification.json'
    assert json.loads(focused_terminal.read_text())['exit_code'] == 0
    assert json.loads(check_terminal.read_text())['exit_code'] == 0
    assert json.loads(focused_check.read_text())['complete']
    assert json.loads((focused_terminal.parent/'seed-controls-verification.json').read_text())['complete']
    diagnostic = ROOT/'evidence/diagnostic-threats-20261018'
    assert json.loads((diagnostic/'tool-terminal.json').read_text())['exit_code'] == 0
    assert json.loads((diagnostic/'identity.json').read_text())['cases'] == 3236
    check = json.loads(check_path.read_text())
    native_units = json.loads(units.read_text())
    assert check['complete'] and native_units['complete'] and native_units['inputs_stable']
    assert native_units['units']['rook2']['passed'] == 132
    assert sha(units) == check['units_verification_sha256']
    paths = {k:ROOT/'evidence'/v/'rook2-exact' for k,v in VARIANTS.items()}
    validation = {}
    for name,directory in VARIANTS.items():
        variant = check['baseline' if name == 'baseline' else 'candidate']
        build = ROOT/'evidence'/directory/'receipt.json'
        replay = Path(check['baseline']['replay_path']) if name == 'baseline' else check_path.parent/'candidate-replay.stdout'
        r = json.loads(replay.read_text())
        assert variant['cases'] == 54 and r['status'] == 'pass' and len(r['results']) == 54
        assert sha(build) == variant['build_receipt_sha256']
        assert sha(replay) == variant['replay']['stdout_sha256']
        assert sha(paths[name]) == variant['artifact_sha256']
        validation[name] = {str(p):sha(p) for p in [build,check_path,units,replay,focused_terminal,check_terminal,focused_check]}
    write('validation-before.json', validation)

    write('suite.json', dict(cases=CASES, variants={k: dict(path=str(v), sha256=sha(v)) for k, v in paths.items()},
                            order='Cases in declared order; each compare_ordinary.py uses one warmup/variant then four alternating forward/reverse rounds',
                            driver_sha256=sha(Path(__file__)), performance='Reported-only matched generic destination-table generation pilot; no PGO or reference qualification'))
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
