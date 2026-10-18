#!/usr/bin/env python3
"""Independently reconcile all original-byte generic production95 versus combined103 six-case pilot receipts.

No engine is executed. Recompute the schedule, sample selection and aggregate
from direct native wait4 records, checking the separate strict comparator.
"""
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/ordered-q-seeded103-combined-cpu-pilot-20261018'
CASES = ['profile-01', 'profile-02', 'profile-04', 'profile-05', 'profile-35', 'profile-29']
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
NAMES = ['baseline', 'combined']
HASHES = {'baseline': '6e7b29358eb3774f578308f79a2e83b20587e7bd5cdacae1ff762764e7b11ec5', 'combined': '1befaa6d9c439d3d806e6e189a27756ab86f4c5b5ce3b74f59ed302d98ee5c0d'}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    inputs = {}

    def load(p):
        inputs[str(p.relative_to(ROOT))] = sha(p)
        return read(p)

    suite = load(OUT / 'suite.json')
    final = load(OUT / 'suite-summary.json')
    validation = load(OUT / 'validation-before.json')
    assert suite['cases'] == CASES and list(suite['variants']) == NAMES
    assert suite['driver_sha256'] == sha(OUT / 'driver.py')
    assert final['complete'] is True and final['artifact_hashes_after'] == HASHES
    for name in NAMES:
        assert suite['variants'][name]['sha256'] == HASHES[name]
        assert sha(Path(suite['variants'][name]['path'])) == HASHES[name]
        assert all(sha(Path(p)) == digest for p, digest in validation[name].items())
    for suffix in ['before', 'after']:
        assert load(OUT / f'context-{suffix}.json')['helper_affinity'] == HELPERS

    schedule = [dict(variant=n, warmup=True, repeat=0) for n in NAMES]
    for repeat in range(1, 5):
        order = NAMES if repeat % 2 else NAMES[::-1]
        schedule.extend(dict(variant=n, warmup=False, repeat=repeat) for n in order)

    cases, lifetimes = [], 0
    for case in CASES:
        directory = OUT / case
        manifest = load(directory / 'manifest.json')
        report = load(directory / 'summary.json')
        assert manifest['case'] == case and manifest['schedule'] == schedule
        assert manifest['variants'] == suite['variants']
        assert manifest['helper_affinity'] == HELPERS and manifest['engine_cpu'] == 14
        assert all(sha(Path(p)) == digest for p, digest in manifest['files'].items())
        assert report['input_hashes_after'] == manifest['files']
        assert report['artifact_hashes_after'] == HASHES
        assert report['complete'] is True and report['failure'] is None
        assert len(report['runs']) == len(schedule) == 10
        samples = {n: [] for n in NAMES}
        for i, (step, row) in enumerate(zip(schedule, report['runs'])):
            assert all(row[k] == v for k, v in step.items())
            assert row['failure'] is None and row['comparator_exit'] == 0
            run = directory / f"{i:02d}-{step['variant']}"
            native_path = run / 'native.json'
            comparator_path = run / 'comparator.stdout'
            native, comparator = load(native_path), load(comparator_path)
            stderr = run / 'comparator.stderr'
            assert stderr.stat().st_size == 0
            inputs[str(stderr.relative_to(ROOT))] = sha(stderr)
            assert sha(native_path) == row['native_receipt_sha256']
            assert sha(comparator_path) == row['comparator_sha256']
            assert comparator['status'] == 'pass' and comparator['selectedCases'] == [case]
            assert len(comparator['results']) == 1
            assert native['schema'] == 'rook2-native-wait4-v1'
            assert native['failure'] is None and native['exec_error'] is None
            assert native['native_exit_code'] == native['native_wait_status'] == 0
            assert native['supervisor_signals'] == [] and native['known_single_process'] is True
            assert native['engine_sha256_before'] == native['engine_sha256_after'] == HASHES[step['variant']]
            assert native['engine'] == suite['variants'][step['variant']]['path']
            assert native['launcher_sha256'] == manifest['files'][str(ROOT / 'tools/account_native.py')]
            assert sha(Path(native['python_executable'])) == native['python_executable_sha256']
            assert native['argv'] == [native['engine'], '--work-clock=kingwcr', '--work-clock-post=work']
            assert native['supervisor_affinity'] == native['inherited_supervisor_affinity'] == HELPERS
            assert native['native_pre_exec']['affinity'] == native['native_post_exec']['affinity'] == [14]
            assert native['native_post_exec']['path'] == native['engine']
            assert native['native_post_exec']['tasks'] == [str(native['native_pid'])]
            assert native['native_pre_exec']['pid'] == native['native_pid']
            assert native['user_cpu_s'] >= 0 and native['system_cpu_s'] >= 0
            cpu = native['user_cpu_s'] + native['system_cpu_s']
            assert cpu == native['total_cpu_s'] == row['native_cpu_s']
            assert native['wall_ns'] == row['native_wall_ns']
            assert native['wall_ns'] == native['reaped_monotonic_ns'] - native['start_monotonic_ns']
            assert row['command'] == [
                '/usr/bin/node', '/home/legolas/king-spec/conformance/profiling/replay-check.mjs',
                '--case', case, '--', native['python_executable'], str(ROOT / 'tools/account_native.py'),
                '--engine', native['engine'], '--record', str(native_path), '--known-single-process',
            ]
            if not step['warmup']:
                samples[step['variant']].append(cpu)
            lifetimes += 1
        summaries = {}
        for name, values in samples.items():
            assert len(values) == 4
            summaries[name] = dict(samples=values, median=statistics.median(values), minimum=min(values), maximum=max(values))
        assert summaries == report['summaries'] == final['summaries'][case]
        cases.append(dict(case=case, summaries=summaries,
                          ratio=summaries['combined']['median'] / summaries['baseline']['median'],
                          observed_ranges_disjoint_in_favor_of_combined=
                          summaries['combined']['maximum'] < summaries['baseline']['minimum']))
        for suffix in ['stdout', 'stderr']:
            p = OUT / f'{case}.{suffix}'
            inputs[str(p.relative_to(ROOT))] = sha(p)
            assert p.stat().st_size == (0 if suffix == 'stderr' else p.stat().st_size)
    sums = {n: sum(c['summaries'][n]['median'] for c in cases) for n in NAMES}
    assert lifetimes == 60
    ratio = sums['combined'] / sums['baseline']
    result = dict(complete=True, lifetimes_independently_reconciled=lifetimes,
                  excluded_warmups=12, measured_lifetimes=48,
                  sum_case_medians_cpu_s=sums, combined_to_baseline=ratio,
                  percent_lower=100 * (1 - ratio),
                  all_six_observed_ranges_disjoint=all(c['observed_ranges_disjoint_in_favor_of_combined'] for c in cases),
                  cases=cases, input_receipts_sha256=inputs, reconciler_sha256=sha(Path(__file__)),
                  scope='Reported-only matched generic production95 versus combined103 pilot; no confidence band, universal improvement, reference qualification or full54/12 cost result.')
    with (OUT / 'analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ['complete', 'lifetimes_independently_reconciled', 'sum_case_medians_cpu_s', 'combined_to_baseline', 'percent_lower', 'all_six_observed_ranges_disjoint']}))


if __name__ == '__main__':
    main()
