#!/usr/bin/env python3
"""Integrate exact reviewed kernels only after complete pilot and adapter returns.

This is an explicit engineering action, not a performance acceptance decision.
The caller first reviews the complete matched data and chooses to execute it.
"""
import hashlib
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('/tmp/imp2-eval-kernels-combined-20261018')
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def main():
    pilot = ROOT/'evidence/pgo-eval-kernels-combined-cpu-pilot-20261018'
    adapter = ROOT/'evidence/diagnostic-endings-20261018'
    analysis = load(pilot/'analysis.json')
    assert analysis['complete'] and analysis['lifetimes_independently_reconciled'] == 90
    assert analysis['combined_to_baseline'] < 1 and analysis['combined_to_states'] < 1
    assert load(pilot/'driver-terminal.json')['exit_code'] == 0
    verification = load(adapter/'verification.json')
    assert verification['complete'] and verification['inputs_stable'] and verification['cases'] == 2215
    assert load(adapter/'terminal.json')['exit_code'] == 0
    assert load(adapter/'identity.json')['cases'] == 2215
    before, candidate = source_snapshot(ROOT), source_snapshot(SOURCE)
    previous = ROOT/'evidence/production-bitplanes-use-build-20261018/receipt.json'
    build = ROOT/'evidence/pgo-eval-kernels-combined-use-build-20261018/receipt.json'
    assert before == load(previous)['source_sha256_before']
    assert candidate == load(build)['source_sha256_before'] == load(build)['source_sha256_after']
    assert load(ROOT/'evidence/eval-kernels-combined-preparation-20261018/native-verification.json')['complete']
    check = ROOT/'evidence/pgo-eval-kernels-combined-use-check-20261018/identity.json'
    assert load(check)['native_artifact_sha256'] == load(build)['binary_output']['sha256']
    names = ['src/influence.rs', 'src/lib.rs', 'src/relation_table.rs']
    assert set(candidate) - set(before) == {'src/relation_table.rs'}
    assert {n for n in before if before[n] != candidate[n]} == {'src/influence.rs', 'src/lib.rs'}
    for name in names:
        (ROOT/name).write_bytes((SOURCE/name).read_bytes())
    after = source_snapshot(ROOT)
    assert after == candidate
    inputs = [pilot/'analysis.json', pilot/'driver-terminal.json', adapter/'verification.json',
              adapter/'identity.json', adapter/'terminal.json', previous, build, check]
    result = dict(status='Canonical source integrates exact formatted combined kernels; canonical tests/profile/build/timing still required',
                  copied_from=str(SOURCE), copied_files=names, source_before=before, source_after=after,
                  candidate_source=candidate, input_sha256={str(p):sha(p) for p in inputs},
                  driver_sha256=sha(Path(__file__)),
                  scope='Immutable relation tables and typed-list influence enumeration only; no Position/Node, ownership, ordering, semantic work or lifecycle change')
    with (OUT/'source-integration.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(integrated_files=names, exact_candidate_match=True)))


if __name__ == '__main__':
    main()
