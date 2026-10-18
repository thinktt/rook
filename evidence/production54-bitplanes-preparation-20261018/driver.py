#!/usr/bin/env python3
"""Freeze validated canonical inputs, run the unchanged all54 CPU collector once."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PREP = Path(__file__).resolve().parent
OUT = ROOT / 'evidence/production54-cpu-bitplanes-20261018'
EXPECTED = '915f83e4c93bbb1b378c9a7d4250f93981347a4a75760db1510330ee395277fd'
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    assert not OUT.exists(), 'Never overwrite/retry an executed collection'
    assert set(os.sched_getaffinity(0)) <= HELPERS
    build = ROOT / 'evidence/production-bitplanes-use-build-20261018/receipt.json'
    engine = build.parent / 'rook2-exact'
    identity = ROOT / 'evidence/production-bitplanes-use-check-20261018/identity.json'
    replay = identity.parent / 'profile-all.json'
    wire = ROOT / 'evidence/production-bitplanes-interruption-wire-20261018/receipt.json'
    pilot = ROOT / 'evidence/production-bitplanes-cpu-pilot-20261018/analysis.json'
    pilot_terminal = pilot.parent / 'driver-terminal.json'
    assert sha(engine) == EXPECTED
    b, i, r, w, p, t = [json.loads(x.read_text()) for x in [build, identity, replay, wire, pilot, pilot_terminal]]
    assert b['outcome'] == 'build-succeeded-with-stable-input-snapshot' and b['binary_output']['sha256'] == EXPECTED
    assert i['native_artifact_sha256'] == EXPECTED and i['build_receipt_sha256'] == sha(build)
    assert i['replay_sha256'] == sha(replay) and i['missing_function_warnings'] == 0
    assert r['status'] == 'pass' and len(r['results']) == 54
    assert w['pass'] and len(w['results']) == 8
    assert w['engine_sha256_before'] == w['engine_sha256_after'] == EXPECTED
    assert p['complete'] and p['lifetimes_independently_reconciled'] == 60
    assert t['exit_code'] == 0 and t['suite_summary_sha256'] == sha(pilot.parent / 'suite-summary.json')
    command = [sys.executable, str(ROOT / 'tools/collect_ordinary.py'), '--engine', str(engine),
               '--build-record', str(build), '--output', str(OUT)]
    deps = [Path(__file__), build, identity, replay, wire, pilot, pilot_terminal,
            ROOT / 'tools/collect_ordinary.py', ROOT / 'tools/account_native.py',
            ROOT / 'tools/compare_ordinary.py', ROOT / 'tools/measure.py']
    hashes = {str(x): sha(x) for x in deps}
    write(PREP / 'preflight.json', dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          command=command, engine_sha256=EXPECTED, input_sha256=hashes,
          helper_affinity=sorted(os.sched_getaffinity(0)),
          ownership='Only this owned native collection; no concurrent owned builds/tests/engines/profilers',
          scope='Complete reported-only local CPU collection; final PMU/resource/observer/uncertainty/calibration qualification remains open'))
    result = subprocess.run(command, cwd=ROOT)
    summary = OUT / 'summary.json'
    after = {str(x): sha(x) for x in deps}
    terminal = dict(collector_returncode=result.returncode, completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    command=command, driver_sha256=sha(Path(__file__)), engine_sha256_after=sha(engine),
                    stable_dependencies=after == hashes, input_sha256_after=after,
                    summary_sha256=sha(summary) if summary.exists() else None,
                    origin='Actual subprocess.run return; does not infer terminal status from a summary-complete field')
    write(PREP / 'driver-terminal.json', terminal)
    assert after == hashes and sha(engine) == EXPECTED
    print(json.dumps(dict(collector_returncode=result.returncode, stable_dependencies=True)), flush=True)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
