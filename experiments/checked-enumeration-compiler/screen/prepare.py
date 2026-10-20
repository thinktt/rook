#!/usr/bin/env python3
"""Freeze an inert fixed70 plan using the unchanged admitted helpers/images."""
import hashlib
import json
from pathlib import Path

R = Path('/home/legolas/rook2')
B = Path('/home/legolas/rook2-experiments/checked-enumeration-compiler-20261020-01')
S = R / 'experiments/checked-enumeration-compiler/screen'
C = Path('/home/legolas/rook2-experiments/original-worktree/evidence/bitplane-pin-summary-generic-build-20261020-01')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def main():
    prep = B / 'screen-preparation'
    prep.mkdir()
    pins = {}
    for build in (C, B / 'build'):
        receipt = json.loads((build / 'receipt.json').read_text())
        assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot'
        assert receipt['pgo']['mode'] == 'none'
        assert receipt['rust_flags'] == ['-C', 'target-cpu=x86-64']
        for name, expected in (receipt['source_sha256_before'] | receipt['tool_sha256_before']).items():
            p = build / 'source-before' / name
            assert sha(p) == expected
            pins[str(p)] = expected
        for n in ('receipt.json', 'frozen-image.json', 'archive-receipt.json', 'verified-source-before.tar.gz'):
            pins[str(build / n)] = sha(build / n)
    closure = json.loads((S.parent / 'closed-summary.json').read_text())
    assert closure['scope_complete'] and closure['repaired_tests_passed'] == 196
    for name, expected in closure['named_supports_sha256'].items():
        assert sha(B / name) == expected
        pins[str(B / name)] = expected
    for n in ('report.md', 'closed-summary.json', 'prototype.patch', 'fixture-repair.patch', 'fixture-repair.json', 'plan.json'):
        pins[str(S.parent / n)] = sha(S.parent / n)
    for n in ('pilot.py', 'reconcile_pilot.py', 'check_pilot.mjs'):
        p = S / n
        old = R / 'experiments/pressure-presence-compiler/screen' / n
        assert p.read_bytes() == old.read_bytes()
        pins[str(p)] = sha(p)
    for p in [R / 'tools' / n for n in ('compare_ordinary.py', 'account_native.py', 'measure.py')]:
        pins[str(p)] = sha(p)
    spec = Path('/home/legolas/king-spec/conformance/profiling')
    for n in ('replay-check.mjs', 'benchmark.mjs', 'workloads.json', 'replay-oracle.json'):
        pins[str(spec / n)] = sha(spec / n)
    for n in ('python3', 'node', 'taskset'):
        p = Path('/usr/bin') / n
        pins[str(p)] = sha(p)
    cases = ['profile-01', 'profile-02', 'profile-04', 'profile-05', 'profile-29', 'profile-35', 'profile-08']
    schedule = []
    for case in cases:
        rows = [dict(variant=n, warmup=True, repeat=0) for n in ('baseline', 'candidate')]
        for repeat in range(1, 5):
            rows += [dict(variant=n, warmup=False, repeat=repeat)
                     for n in (('baseline', 'candidate') if repeat % 2 else ('candidate', 'baseline'))]
        schedule += [dict(case=case, index=i, **row) for i, row in enumerate(rows)]
    assert len(schedule) == 70
    save(prep / 'frozen-schedule.json', schedule)
    pins[str(prep / 'frozen-schedule.json')] = sha(prep / 'frozen-schedule.json')
    variants = {
        'baseline': dict(path=str(C / 'rook2-exact'), sha256='5d10b2fa6b75b1eead79a444c5eaccd13f5e8b959e1d0469075be1ebabba27e6'),
        'candidate': dict(path=str(B / 'build/rook2-exact'), sha256='0cde6b78b95a3b99840560c52ae315b5813815810f44099948c14a9bb36b7ead'),
    }
    for v in variants.values():
        assert sha(Path(v['path'])) == v['sha256']
    plan = dict(experiment='checked-enumeration-compiler', phase='ONE unchanged fixed70 generic engineering screen',
                authority='/home/legolas/agent-memos/rook2-lead-checked-screen-and-tt-census-20261020T181017Z.md',
                status='INERT_ROOT_ACTIVATION_REQUIRED', cases=cases,
                frozen_rule=dict(aggregate_candidate_div_baseline_max=.995, minimum_lower_cases=5,
                                 worst_case_ratio_max=1.02, otherwise='PARK without retune, repeat or PGO rescue'),
                schedule=dict(excluded_warmups=14, measured=56, lifetimes=70),
                parent_review_complete=False, backend_review_complete=False, all_owned_jobs_closed=False,
                launch_authorized=False, quiet_point_verified=False, variants=variants,
                output=str(B / 'generic-screen'), driver_sha256=sha(S / 'pilot.py'), immutable_inputs=pins,
                no_retry=True, no_PGO_authority=True, production_adoption=False,
                runtime_scope='Known native wait4 lifetimes, original live/offline70 checks; point guest context only. No PMU, qualification or host exclusivity.')
    save(S / 'plan.json', plan)
    save(prep / 'preparation.json', dict(plan_sha256=sha(S / 'plan.json'), schedule_sha256=sha(prep / 'frozen-schedule.json'),
                                       immutable_pins=len(pins), helpers_byte_identical=True, engine_runs=0))
    print(json.dumps(dict(immutable_pins=len(pins), plan_sha256=sha(S / 'plan.json'), preparation_complete=True)))


if __name__ == '__main__':
    main()
