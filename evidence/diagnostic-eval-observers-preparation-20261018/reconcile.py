#!/usr/bin/env python3
"""Independently reconcile declared cases, raw exits, units and source identities."""
import hashlib
import json
from pathlib import Path
import re

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]
OUT = ROOT/'evidence/diagnostic-eval-observers-20261018'
BUILD = ROOT/'evidence/diagnostic-eval-observers-build-20261018'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def main():
    plan = load(PREP/'plan.json')
    verification = load(OUT/'verification.json')
    report = load(OUT/'conformance.json')
    before, after = load(OUT/'inputs-before.json'), load(OUT/'inputs-after.json')
    build = load(BUILD/'receipt.json')
    assert verification['complete'] and verification['inputs_stable'] and verification['failure'] is None
    assert report['pass'] and report['completeEngineQualification'] is False
    assert len(report['results']) == verification['cases'] == plan['expected_case_count'] == 3470
    ids, operations = [], set()
    for name, digest in plan['fixtures'].items():
        assert sha(Path(name)) == digest
        for case in load(Path(name))['cases']:
            ids.append(case['id'])
            operations.add(case['request']['operation'])
    assert len(ids) == len(set(ids)) == 3470 and len(operations) == 64
    assert set(ids) == {r['id'] for r in report['results']}
    assert all(r['pass'] and r['exit'] == dict(code=0, signal=None) for r in report['results'])
    assert all(s['exit_code'] == 0 for s in verification['stages'])
    assert not (OUT/'conformance.stderr').stat().st_size
    assert before['native'] == after['native'] == load(Path(plan['native_build_reference']))['source_sha256_before']
    assert before['adapter'] == after['adapter'] == build['source_sha256_before'] == build['source_sha256_after']
    assert before['dependencies'] == after['dependencies']
    assert all(sha(Path(p)) == h for p, h in before['dependencies'].items())
    assert sha(BUILD/'rook2-diag-exact') == build['binary_output']['sha256'] == verification['adapter_sha256']
    assert sha(OUT/'unit-bin/rook2-diag-exact') == verification['unit_binary_sha256']
    assert re.search(r'test result: ok\. 58 passed; 0 failed;', (OUT/'unit-tests.stdout').read_text())
    identity = dict(status='64-native-backed-diagnostic-operations-pass', adapter_sha256=verification['adapter_sha256'],
                    cases=3470, units=58, operations=sorted(operations), full_fixture_files=52,
                    unchanged_selected_cases_from_one_partial_file=3,
                    build_receipt_sha256=sha(BUILD/'receipt.json'), verification_sha256=sha(OUT/'verification.json'),
                    external_report_sha256=sha(OUT/'conformance.json'),
                    native_build_reference=plan['native_build_reference'],
                    native_build_reference_sha256=sha(Path(plan['native_build_reference'])),
                    reconciler_sha256=sha(Path(__file__)),
                    complete_mandatory_qualification=False)
    with (OUT/'identity.json').open('x') as stream:
        json.dump(identity, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k:identity[k] for k in ['cases', 'units', 'adapter_sha256']}))


if __name__ == '__main__':
    main()
