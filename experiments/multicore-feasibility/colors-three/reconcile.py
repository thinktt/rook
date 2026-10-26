#!/usr/bin/env python3
"""Independent raw replay/placement/counter audit; no native or helper execution."""
import argparse
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
from common import (HERE, ACCOUNT, SPEC, HELPERS, LIMITS, admission, audit,
    audit_placement, baseline, code_paths, native_receipt, preparation, read, sha, variants)

CASES = ['profile-35', 'profile-08', 'profile-43']
NAMES = ['preserved2', 'inline1', 'current2', 'colors3']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def dist(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def readiness(directory, row, budget, enabled, idle=False):
    """Reparse native JSON and recompute all partitions and histogram bounds."""
    path = directory/'colors.json'
    if not enabled:
        assert row is None and not path.exists()
        return None
    assert row['path'] == str(path) and row['sha256'] == sha(path)
    value = read(path)
    assert value == row['report'] and value['schema'] == 'rook2-colors-readiness-v1'
    if budget < 3:
        assert value == {'schema': 'rook2-colors-readiness-v1', 'enabled': False}
        return value
    assert value['enabled'] is True
    assert value['sample_stride'] == 512 and value['samples_capped'] == 0
    assert value['storage'] == 'fixed_log2_histograms'
    assert value['histogram_bucket_rule'] == 'zero_else_bit_length_capped_63'
    counters = ['dispatches', 'sampled_dispatches', 'completed_samples', 'discarded_samples',
        'failed_samples', 'owner_missing_samples', 'paired_samples',
        'owner_ready_at_or_after_both', 'sides_after_owner', 'white_last', 'black_last', 'sides_tied']
    for key in counters:
        assert type(value[key]) is int and 0 <= value[key] < 2**64
    sampled = value['dispatches']//512
    assert sampled == value['sampled_dispatches']
    assert sampled == value['completed_samples']+value['discarded_samples']+value['failed_samples']
    paired = value['completed_samples']-value['owner_missing_samples']
    assert paired >= 0 and paired == value['paired_samples']
    assert paired == value['owner_ready_at_or_after_both']+value['sides_after_owner']
    assert paired == value['white_last']+value['black_last']+value['sides_tied']
    # Successful synchronous FULL calls leave no abandoned/error sample behind.
    assert value['discarded_samples'] == value['failed_samples'] == value['owner_missing_samples'] == 0
    completed_names = {'white_ready', 'black_ready', 'white_kernel', 'black_kernel',
                       'white_copy', 'black_copy', 'reader_imbalance', 'join_elapsed'}
    paired_names = {'owner_ready', 'join_wait', 'owner_after_sides'}
    assert set(value['metrics']) == completed_names | paired_names
    for name, metric in value['metrics'].items():
        expected = value['completed_samples'] if name in completed_names else paired
        assert set(metric) == {'count', 'sum_ns', 'min_ns', 'max_ns', 'log2_ns'}
        assert metric['count'] == expected
        assert all(type(metric[key]) is int and metric[key] >= 0 for key in ['count', 'sum_ns', 'min_ns', 'max_ns'])
        bins = metric['log2_ns']
        assert len(bins) == 64 and all(type(n) is int and n >= 0 for n in bins)
        assert sum(bins) == expected
        if expected == 0:
            assert metric['sum_ns'] == metric['min_ns'] == metric['max_ns'] == 0
            continue
        minimum, maximum = metric['min_ns'], metric['max_ns']
        assert 0 <= minimum <= maximum < 2**64
        assert expected*minimum <= metric['sum_ns'] <= expected*maximum
        occupied = [index for index, count in enumerate(bins) if count]
        assert min(minimum.bit_length(), 63) == occupied[0]
        assert min(maximum.bit_length(), 63) == occupied[-1]
        lower, upper = 0, 0
        for index, count in enumerate(bins):
            low = 0 if index == 0 else 2**(index-1)
            high = 0 if index == 0 else (2**index-1 if index < 63 else 2**64-1)
            lower += count*low; upper += count*high
        assert lower <= metric['sum_ns'] <= upper
    # The successful runs have a paired owner observation for every completed
    # sample. Aggregate max(white,black) follows exactly from their sums and the
    # absolute-gap sum, independently checking the saturated wait arithmetic.
    metrics = value['metrics']
    twice_latest = (metrics['white_ready']['sum_ns']+metrics['black_ready']['sum_ns']
                    +metrics['reader_imbalance']['sum_ns'])
    assert twice_latest % 2 == 0
    assert metrics['join_wait']['sum_ns']-metrics['owner_after_sides']['sum_ns'] == (
        twice_latest//2-metrics['owner_ready']['sum_ns'])
    assert metrics['join_wait']['log2_ns'][0] == value['owner_ready_at_or_after_both']
    assert metrics['reader_imbalance']['log2_ns'][0] == value['sides_tied']
    assert metrics['owner_after_sides']['log2_ns'][0] >= value['sides_after_owner']
    assert value['dispatches'] == 0 if idle else value['dispatches'] > 0
    return value


def housekeeping_audit(path):
    record = read(path)
    assert record['schema'] == 'rook2-colors-three-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus'] == sorted(HELPERS)
    assert len(record['applies']) == 52 and record['restored'] is not None
    originals, leaders, observed = {}, {}, {}
    for row in record['originals']:
        key = (row['pid'], row['tid'], row['starttime'])
        assert key not in originals and row['affinity']
        originals[key] = row['affinity']
    for row in record['leaders']:
        key = (row['pid'], row['starttime'])
        assert key not in leaders and row['affinity']
        leaders[key] = row['affinity']
    for event in record['applies']:
        assert event['cpus'] == event['selfAffinity'] == sorted(HELPERS)
        for row in event['selectedTasks']:
            key = (row['pid'], row['tid'], row['starttime'])
            assert row['after'] == sorted(HELPERS)
            if key in observed:
                assert row['before'] == sorted(HELPERS)
            else:
                assert originals[key] == row['before']
                observed[key] = row['before']
    assert observed == originals
    for row in record['restored']:
        key = (row['pid'], row['tid'], row['starttime'])
        if key in originals:
            assert not row['inheritedNewThread'] and row['restored'] == originals[key]
        else:
            masks = [mask for (pid, _), mask in leaders.items() if pid == row['pid']]
            assert len(masks) == 1 and row['inheritedNewThread'] and row['restored'] == masks[0]
    assert record['postRestoreSelfAffinity'] == sorted(HELPERS)
    return dict(selectedOriginalTasks=len(originals), restoredTasks=len(record['restored']),
                applyCount=len(record['applies']), receiptSha256=sha(path))


def readiness_summary(rows):
    counters = ['dispatches', 'sampled_dispatches', 'completed_samples', 'discarded_samples',
        'failed_samples', 'owner_missing_samples', 'paired_samples',
        'owner_ready_at_or_after_both', 'sides_after_owner', 'white_last', 'black_last', 'sides_tied']
    reports = [row['colors']['report'] for row in rows]
    result = dict(counters={key: sum(v[key] for v in reports) for key in counters}, metrics={})
    for name in reports[0]['metrics']:
        values = [v['metrics'][name] for v in reports]
        count = sum(v['count'] for v in values)
        total = sum(v['sum_ns'] for v in values)
        bins = [sum(v['log2_ns'][i] for v in values) for i in range(64)]
        occupied = [v for v in values if v['count']]
        result['metrics'][name] = dict(count=count, sum_ns=total,
            mean_ns=total/count if count else None,
            min_ns=min(v['min_ns'] for v in occupied) if occupied else 0,
            max_ns=max(v['max_ns'] for v in occupied) if occupied else 0, log2_ns=bins)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-colors-three-generic-v1'
    assert result['complete'] and result['failure'] is None
    expected = []
    for case in CASES:
        expected += [dict(case=case, variant=name, warmup=True, repeat=0) for name in NAMES]
        for rotation in range(3):
            order = NAMES[rotation:]+NAMES[:rotation]
            expected += [dict(case=case, variant=name, warmup=False, repeat=rotation+1) for name in order]
    assert len(result['runs']) == len(expected) == 48 and plan['schedule'] == expected
    assert plan['helperAffinity'] == sorted(HELPERS) and plan['idleOwnedSiblings'] == [5, 7, 15]
    assert plan['coordinatorCpu'] == 14 and plan['helperCpus'] == [6, 4]
    assert plan['nativePreExecAffinities'] == {'1': [6, 14], '2': [6, 14], '3': [4, 6, 14]}
    assert plan['limits'] == LIMITS
    hashes = plan['inputSha256']
    assert all(str(path) in hashes for path in code_paths())
    for path, digest in hashes.items():
        assert sha(path) == digest, path
    assert plan['protectedArtifacts'] == baseline()
    prepared_path = Path(plan['sourcePreparation'])
    prepared = preparation(prepared_path)
    assert hashes[str(prepared_path)] == sha(prepared_path)
    modes = plan['variants']
    assert list(modes) == NAMES
    control, candidate = Path(modes['preserved2']['path']), Path(modes['inline1']['path'])
    assert modes == variants(control, candidate)
    receipts = admission(Path(plan['controlBuild']), Path(plan['candidateBuild']), control, candidate, prepared)
    for directory, receipt in zip([Path(plan['controlBuild']), Path(plan['candidateBuild'])], receipts):
        for path in [directory/'receipt.json', directory/'build.stderr']:
            assert hashes[str(path)] == sha(path)
        for name, digest in (receipt['source_sha256_before'] | receipt['tool_sha256_before']).items():
            assert hashes[str(directory/'source-before'/name)] == digest
    assert 0 < result['streamEndMonotonicNs']-result['streamStartMonotonicNs'] <= 1800*10**9
    posts, prior_end, pids = 0, result['streamStartMonotonicNs'], set()
    for index, (step, row) in enumerate(zip(expected, result['runs'])):
        value = modes[step['variant']]
        directory = base/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        native, count = audit.lifetime(directory, row, step, Path(value['path']),
                                        value['budget'], value['options'], hashes)
        assert row['orderedPosts'] == count
        assert row['placement'] == audit_placement(directory, native, hashes)
        assert prior_end <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= result['streamEndMonotonicNs']
        assert native['wall_ns'] <= 180*10**9
        readiness(directory, row['colors'], value['budget'], value['report'])
        assert bool(native['colors_report_path']) == value['report']
        prior_end = row['controllerEndMonotonicNs']
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']); posts += count
    assert len(result['idle']) == 4
    for name, row in zip(NAMES, result['idle']):
        value, directory = modes[name], base/('idle-'+name)
        assert row['variant'] == name and read(directory/'probe.json') == row
        native = native_receipt(directory/'native.json', Path(value['path']),
                                value['budget'], value['options'], hashes)
        assert read(directory/'launch.json') == dict(argv=[native['python_executable'], str(ACCOUNT),
            '--engine', value['path'], '--record', str(directory/'native.json'), '--known-single-process',
            '--thread-budget', str(value['budget']), *value['options']], variant=name, kind='startup-idle-shutdown')
        assert row['nativePid'] == native['native_pid'] and row['supervisorPid'] == native['supervisor_pid']
        assert row['wholeCpuSeconds'] == native['total_cpu_s'] and row['wholeWallNs'] == native['wall_ns']
        assert row['rssKiB'] == native['maxrss_linux_kib'] and row['placement'] == audit_placement(directory, native, hashes)
        assert row['idleCpuTicks'] == row['shutdownStartCpuTicks']-row['startupCpuTicks'] >= 0
        assert row['tickHz'] == read(next(base.glob('*-r0'))/'tap-config.json')['tickHz']
        assert row['idleCpuSeconds'] == row['idleCpuTicks']/row['tickHz']
        assert row['idleNs'] == row['idleEndMonotonicNs']-row['idleStartMonotonicNs'] >= 250_000_000
        assert prior_end <= native['start_monotonic_ns'] < row['idleStartMonotonicNs'] < row['idleEndMonotonicNs'] < native['reaped_monotonic_ns'] <= result['streamEndMonotonicNs']
        assert row['startupReplyNs'] > 0 and row['shutdownSupervisorNs'] > 0
        assert (directory/'stdin.raw').read_bytes() == b'cm_parm\nquit\n'
        assert (directory/'stdout.raw').read_bytes() == b'cm_parm\n' and (directory/'stderr').read_bytes() == b''
        assert set(row['sha256']) == {'launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr'}
        for name_in_row, digest in row['sha256'].items():
            assert sha(directory/name_in_row) == digest
        readiness(directory, row['colors'], value['budget'], value['report'], idle=True)
        prior_end = native['reaped_monotonic_ns']
        assert native['native_pid'] not in pids
        pids.add(native['native_pid'])
    assert len(pids) == 52
    summaries = []
    for case in CASES:
        for name in NAMES:
            rows = [row for row in result['runs'] if row['case'] == case and row['variant'] == name and not row['warmup']]
            assert len(rows) == 3
            summaries.append(dict(case=case, variant=name, **{key: dist([row[key] for row in rows]) for key in METRICS}))
    assert summaries == result['summaries']
    by = {(row['case'], row['variant']): row for row in summaries}
    comparisons = []
    for case in CASES:
        row = dict(case=case)
        for numerator, denominator in [('current2', 'preserved2'), ('inline1', 'preserved2'),
                                        ('colors3', 'current2'), ('colors3', 'inline1'), ('colors3', 'preserved2')]:
            row[numerator+'Vs'+denominator] = {key: by[case, numerator][key]['median']/by[case, denominator][key]['median']
                                               for key in ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs']}
        comparisons.append(row)
    sums = {name: {key: sum(by[case, name][key]['median'] for case in CASES)
                   for key in METRICS[:3]} for name in NAMES}
    readiness_rows = [dict(case=case, **readiness_summary([row for row in result['runs']
        if row['case'] == case and row['variant'] == 'colors3' and not row['warmup']])) for case in CASES]
    cpus = {'cpu4', 'cpu5', 'cpu6', 'cpu7', 'cpu14', 'cpu15'}
    def ticks(path):
        return {items[0]: [int(x) for x in items[1:]] for line in path.read_text().splitlines()
                if (items := line.split()) and items[0] in cpus}
    before, after = ticks(base/'proc-stat-before'), ticks(base/'proc-stat-after')
    assert set(before) == set(after) == cpus
    deltas = {cpu: [y-x for x, y in zip(before[cpu], after[cpu])] for cpu in cpus}
    assert all(len(before[cpu]) == len(after[cpu]) and all(x >= 0 for x in deltas[cpu]) for cpu in cpus)
    output = dict(complete=True, replayLives=48, measured=36, warmups=12, idleProcesses=4,
        orderedPosts=posts, comparisons=comparisons, summedMedians=sums, summaries=summaries,
        readiness=readiness_rows, idle=result['idle'], housekeeping=housekeeping_audit(base/'housekeeping.json'),
        guestCpuTickDeltas=deltas, guestCpuTickFieldOrder='user nice system idle iowait irq softirq steal guest guest_nice',
        raw=str(base), rawSha256={name: sha(base/name) for name in ['plan.json', 'result.json',
            'proc-stat-before', 'proc-stat-after', 'housekeeping.json']}, reconcilerSha256=sha(Path(__file__)),
        scope='three-case generic instrumented discriminator; all-thread wait4; gated external placement; sparse timers and refactor costs included; no PGO/qualification/adoption/host-exclusivity claim; captured write() stdin excludes end(data) cleanup')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({key: output[key] for key in ['complete', 'replayLives', 'orderedPosts', 'summedMedians', 'comparisons']}, indent=2))


if __name__ == '__main__':
    main()
