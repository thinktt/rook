#!/usr/bin/env python3
"""Recompute all54 CPU evidence from original native/comparator records, no runs."""
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
PREP = Path(__file__).resolve().parent
OUT = ROOT / 'evidence/production54-cpu-eval-kernels-20261018'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
REFERENCE = Path('/home/legolas/king-spec/performance/reference54.json')
EXPECTED = '8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953'
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def write(p, value):
    with p.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    hashes = {}

    def load(p):
        hashes[str(p)] = sha(p)
        return read(p)

    terminal = load(PREP / 'driver-terminal.json')
    summary, manifest = load(OUT / 'summary.json'), load(OUT / 'manifest.json')
    assert terminal['collector_returncode'] == 0 and terminal['stable_dependencies'] is True
    assert terminal['summary_sha256'] == sha(OUT / 'summary.json')
    assert terminal['engine_sha256_after'] == manifest['engine_sha256'] == EXPECTED
    assert sha(Path(manifest['engine'])) == EXPECTED
    assert summary['complete'] is True and summary['failure'] is None
    assert summary['artifact_sha256_after'] == EXPECTED
    assert all(sha(Path(p)) == digest for p, digest in manifest['input_sha256'].items())
    assert summary['input_sha256_after'] == manifest['input_sha256']
    workloads = load(SPEC / 'workloads.json')
    case_ids = [c['id'] for c in workloads['cases']]
    assert len(case_ids) == len(set(case_ids)) == 54
    schedule = [dict(case=c, repeat=i, warmup=i == 0) for c in case_ids for i in range(4)]
    assert schedule == manifest['schedule'] and len(summary['runs']) == len(schedule) == 216
    for suffix in ['before', 'after']:
        assert load(OUT / f'context-{suffix}.json')['helper_affinity'] == HELPERS

    samples = {c: [] for c in case_ids}
    retained_bytes = 0
    for index, (step, row) in enumerate(zip(schedule, summary['runs'])):
        assert all(row[k] == v for k, v in step.items())
        assert row['comparator_exit'] == 0 and row['failure'] is None
        directory = OUT / f"{index:03d}-{step['case']}-r{step['repeat']}"
        native_path, comparator_path = directory / 'native.json', directory / 'comparator.stdout'
        native, comparator = load(native_path), load(comparator_path)
        stderr = directory / 'comparator.stderr'
        assert stderr.stat().st_size == 0
        hashes[str(stderr)] = sha(stderr)
        retained_bytes += comparator_path.stat().st_size
        assert sha(native_path) == row['native_receipt_sha256']
        assert sha(comparator_path) == row['comparator_sha256']
        assert comparator['status'] == 'pass' and comparator['selectedCases'] == [step['case']]
        assert len(comparator['results']) == 1
        assert native['schema'] == 'rook2-native-wait4-v1'
        assert native['native_exit_code'] == native['native_wait_status'] == 0
        assert native['failure'] is None and native['exec_error'] is None
        assert native['supervisor_signals'] == [] and native['known_single_process'] is True
        assert native['engine_sha256_before'] == native['engine_sha256_after'] == EXPECTED
        assert native['engine'] == manifest['engine']
        assert native['launcher_sha256'] == manifest['input_sha256'][str(ROOT / 'tools/account_native.py')]
        assert sha(Path(native['python_executable'])) == native['python_executable_sha256']
        assert native['argv'] == [native['engine'], '--work-clock=kingwcr', '--work-clock-post=work']
        assert native['supervisor_affinity'] == native['inherited_supervisor_affinity'] == HELPERS
        assert native['native_pre_exec']['affinity'] == native['native_post_exec']['affinity'] == [14]
        assert native['native_post_exec']['tasks'] == [str(native['native_pid'])]
        assert native['native_pre_exec']['pid'] == native['native_pid']
        assert native['native_post_exec']['path'] == manifest['engine']
        assert native['user_cpu_s'] >= 0 and native['system_cpu_s'] >= 0
        assert native['user_cpu_s'] + native['system_cpu_s'] == native['total_cpu_s'] == row['cpu_s']
        assert native['user_cpu_s'] == row['user_s'] and native['system_cpu_s'] == row['system_s']
        assert native['wall_ns'] == row['wall_ns'] == native['reaped_monotonic_ns'] - native['start_monotonic_ns']
        assert comparator_path.stat().st_size <= manifest['limits']['bytes_per_comparator_stream']
        assert native_path.stat().st_size <= manifest['limits']['bytes_per_native_receipt']
        assert row['command'] == ['/usr/bin/node', str(SPEC / 'replay-check.mjs'), '--case', step['case'], '--',
                                  native['python_executable'], str(ROOT / 'tools/account_native.py'),
                                  '--engine', manifest['engine'], '--record', str(native_path), '--known-single-process']
        if not step['warmup']:
            samples[step['case']].append(native['total_cpu_s'])

    assert retained_bytes == summary['retained_comparator_stream_bytes'] <= manifest['limits']['aggregate_stream_bytes']
    reference = load(REFERENCE)
    assert sha(REFERENCE) == '9d83793221fdc8b9f1a165138888bc8011e443af783d3dd1b16d825726d1a87c'
    assert [c['caseId'] for c in reference['casesData']] == case_ids
    old = load(ROOT / 'evidence/production54-cpu-20261018-pgo/summary.json')
    assert old['complete']
    rows, total, reference_total = [], 0.0, 0.0
    for case, published, published_summary in zip(case_ids, reference['casesData'], reference['summary']):
        values = samples[case]
        assert len(values) == 3
        local = dict(samples=values, median=statistics.median(values), minimum=min(values), maximum=max(values))
        local['range_over_median'] = (local['maximum'] - local['minimum']) / local['median']
        assert local == summary['case_summaries'][case]
        assert published_summary['caseId'] == case
        reference_values = [s['e2e']['totalCpuMs'] / 1000 for s in published['samples']]
        reference_median = statistics.median(reference_values)
        assert abs(reference_median - published_summary['e2eCpuMedianMs'] / 1000) < 1e-12
        old_median = old['case_summaries'][case]['median']
        rows.append(dict(case=case, local=local, reference_samples_s=reference_values,
                         reference_median_s=reference_median, raw_uncalibrated_ratio=local['median'] / reference_median,
                         raw_uncalibrated_gap_s=local['median'] - reference_median,
                         historical_3660_median_s=old_median, historical_3660_ratio=local['median'] / old_median))
        total += local['median']
        reference_total += reference_median
    assert abs(total - summary['sum_case_medians_s']) < 1e-12, 'floating aggregate differs beyond metadata rounding'
    # wait4 values have integer-microsecond resolution. Sum their medians in
    # integer units, independent of interpreter float summation strategy.
    median_us = []
    for values in samples.values():
        exact = []
        for value in values:
            micros = round(value * 1000000)
            assert abs(value * 1000000 - micros) < 0.000001
            exact.append(micros)
        median_us.append(statistics.median(exact))
    exact_total_us = sum(median_us)
    total = exact_total_us / 1000000
    assert abs(total - summary['sum_case_medians_s']) < 1e-12
    result = dict(complete=True, lifetimes_independently_reconciled=216, excluded_warmups=54, measured_lifetimes=162,
                  artifact_sha256=EXPECTED, sum_case_medians_cpu_s=total, exact_sum_case_medians_cpu_us=exact_total_us,
                  floating_metadata_comparison_tolerance_s=1e-12, metadata_tolerance_scope='Floating summation identity only; not a measurement uncertainty or acceptance allowance',
                  reference_sum_case_medians_cpu_s=reference_total, raw_uncalibrated_ratio=total / reference_total,
                  max_observed_range_over_median=max(c['local']['range_over_median'] for c in rows),
                  historical_3660_sum_case_medians_cpu_s=old['sum_case_medians_s'],
                  historical_3660_aggregate_ratio=total / old['sum_case_medians_s'],
                  historical_comparison='Sequential historical observation after multiple changes; not a matched attribution experiment',
                  cases=rows, input_receipts_sha256=hashes, reconciler_sha256=sha(Path(__file__)),
                  scope='Reported-only local whole-native CPU evidence; no reference pass/fail or calibrated conversion. PMU/resource/observer/uncertainty/calibration and gameplay remain separate.')
    write(OUT / 'verification.json', result)
    print(json.dumps({k: result[k] for k in ['complete', 'lifetimes_independently_reconciled', 'sum_case_medians_cpu_s', 'reference_sum_case_medians_cpu_s', 'raw_uncalibrated_ratio', 'max_observed_range_over_median', 'historical_3660_aggregate_ratio']}))


if __name__ == '__main__':
    main()
