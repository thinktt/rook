#!/usr/bin/env python3
"""Offline conditional depth8 coverage/worker audit; executes no engine."""
import argparse
import collections
import json
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
from build import HERE, BASE_HELPER, HELPERS, baseline, snapshot, admit, sha, read

CASES = ['profile-35', 'profile-08', 'profile-43']
BUDGETS = [1, 2, 4, 8]
WORKER_CPUS = [6, 4, 2, 0, 8, 10, 12]
RAW_FILES = {'stdout', 'stderr', 'launch.json', 'terminal.json', 'native.json', 'housekeeping.json'}
METRIC_COUNTS = ['lookups', 'entry_candidates', 'entry_mismatches', 'exact_matches',
    'unmatched_calls', 'semantic_rejections', 'validation_censored', 'commits',
    'committed_nodes', 'committed_relations', 'censored', 'already_used',
    'touched_groups', 'touched_bytes', 'peak_staging_bytes', 'lookup_ns', 'staging_ns',
    'validation_ns', 'commit_ns', 'audit_entry_ns', 'audit_local_ns',
    'accepted_oracle_gross_ns', 'accepted_oracle_descendant_hooks_ns']
TIMINGS = ['search_wall_ns', 'search_process_cpu_ns', 'split_wall_ns',
    'split_process_cpu_ns', 'setup_ns', 'snapshot_ns', 'wait_ns', 'join_ns',
    'oracle_wall_ns', 'oracle_process_cpu_ns', 'oracle_compare_ns', 'startup_ns']


def count(value):
    assert type(value) is int and value >= 0, ('nonnegative integer', value)
    return value


def vector(value, length):
    assert type(value) is list and len(value) == length
    for n in value:
        count(n)
    return value


def size_bin(n):
    for i, upper in enumerate([0, 1, 7, 31, 127, 511, 2047, 8191]):
        if n <= upper:
            return i
    return 8


def reasons(rows, total):
    assert type(rows) is list and len(rows) <= 64
    assert len({r['reason'] for r in rows}) == len(rows)
    for row in rows:
        assert set(row) == {'reason', 'count'}
        assert type(row['reason']) is str and row['reason']
        assert count(row['count']) > 0
    assert sum(r['count'] for r in rows) == total
    return {r['reason']: r['count'] for r in rows}


def coverage_schedule():
    return [dict(case=case, threads=1, repeat=0, warmup=True) for case in CASES]


def expected_schedule(coverage):
    """Only the three observed hit flags may activate the declared follow-ups."""
    assert set(coverage) == set(CASES)
    assert all(type(value) is bool for value in coverage.values())
    hits = [case for case in CASES if coverage[case]]
    schedule = coverage_schedule()
    schedule += [dict(case=case, threads=threads, repeat=0, warmup=True)
                 for case in hits for threads in [2, 4, 8]]
    schedule += [dict(case=case, threads=threads, repeat=repeat, warmup=False)
                 for repeat in range(1, 4) for case in hits
                 for threads in (BUDGETS if repeat % 2 == 0 else BUDGETS[::-1])]
    return schedule


def activation_from_raw(base, runs):
    assert type(runs) is list and len(runs) >= 3
    activation = {}
    for i, step in enumerate(coverage_schedule()):
        row = runs[i]
        assert all(row[key] == value and type(row[key]) is type(value) for key, value in step.items())
        directory = base/f'{i:02d}-{step["case"]}-t1-r0'
        assert row['directory'] == str(directory)
        assert sha(directory/'stdout') == row['sha256']['stdout']
        report = read(directory/'stdout')
        assert report['schema'] == 'rook2-internal-split-v1' and report['threads'] == 1 and report['horizon'] == 8
        assert type(report['selector_miss']) is bool
        # Every coverage life is fully audited below before this derived
        # schedule can be admitted. No duration or work-size field activates it.
        hit = not report['selector_miss']
        uncensored = all(not task['oracle']['censored'] for task in report['tasks'])
        activation[step['case']] = dict(selectorHit=hit, oracleUncensored=uncensored, eligible=hit and uncensored)
    return activation


def audit_policy(chosen):
    assert chosen['schema'] == 'rook2-internal-horizon-policy-v1'
    assert chosen['reportSchema'] == 'rook2-internal-split-v1'
    assert chosen['maxDepth'] == 8
    assert chosen['schedule'] == expected_schedule(dict.fromkeys(CASES, True))
    assert chosen['activationRule'] == ('First three rows are budget1 depth8 excluded coverage/warmups in35/08/43 order. '
        'Only selector hits with successful uncensored oracle/control proceed. '
        'Filter all remaining potential rows to admitted cases; no miss repetition or retry.')
    assert chosen['tasks'] == 7 and chosen['budgets'] == BUDGETS
    assert chosen['workerCounts'] == [b-1 for b in BUDGETS]
    assert chosen['workerCpus'] == WORKER_CPUS
    assert chosen['coordinatorCpu'] == 14 and chosen['supervisorCpu'] == 13
    assert chosen['buildHelperCpus'] == sorted(HELPERS)
    assert chosen['selector'] == dict(firstInCanonicalOrder=True,
        afterChild0AndTailIio=True, finiteProperIncomingWindow=True,
        minRequestedDepth=3, minRemainingCandidates=8, minChild0Nodes=2048,
        bestAtMostIncomingLower=True, maxDepth=8)
    assert chosen['caps'] == dict(log_events=524288, max_segments=131072,
        max_recorded_nodes=262144, max_forest_bytes=268435456,
        max_touched_groups=131072, oracle_trace_cap=131072,
        batch_estimated_bytes=2147483648)
    assert chosen['limits'] == dict(perLifeSeconds=180, streamSeconds=1800,
        pipelineSeconds=3600, addressSpaceBytes=8589934592, reportBytes=33554432)
    return chosen


def audit_forest(f, caps, oracle=False):
    for k in ['segments', 'valid_segments', 'metadata_bytes', 'bytes', 'log_events',
              'log_attempted', 'log_bytes', 'recording_hook_ns', 'log_recording_ns']:
        count(f[k])
    assert f['segments'] <= caps['oracle_trace_cap' if oracle else 'max_segments']
    assert f['valid_segments'] <= f['segments']
    assert f['bytes'] == f['metadata_bytes']+f['log_bytes'] <= caps['max_forest_bytes']
    assert max(f['metadata_bytes'], f['log_bytes']) <= caps['max_forest_bytes']//2
    assert f['log_events'] <= caps['log_events'] and f['log_attempted'] >= f['log_events']
    for k in ['event_overflowed', 'byte_overflowed', 'censored']:
        assert type(f[k]) is bool
    assert f['censored'] == (f['cap_reason'] is not None)
    if f['censored']:
        assert f['cap_reason'] in ['journal-cap', 'segment-cap', 'recorded-node-cap', 'metadata-byte-cap']
    if f['event_overflowed'] or f['byte_overflowed']:
        assert f['censored'] and f['log_attempted'] > f['log_events']
    else:
        assert f['log_attempted'] == f['log_events']
    if f['event_overflowed']:
        assert f['log_events'] == caps['log_events']
    if oracle:
        assert f['log_events'] == f['log_attempted'] == f['log_bytes'] == f['log_recording_ns'] == 0
        assert not f['event_overflowed'] and not f['byte_overflowed']


def audit_recovery(task, caps, active):
    r, f = task['recovery'], task['forest']
    for k in METRIC_COUNTS:
        count(r[k])
    assert r['fatal_reason'] is None and r['maximal_ranges_disjoint'] is True
    assert r['exact_matches'] == r['semantic_rejections']+r['validation_censored']+r['commits'] <= r['lookups']
    assert r['lookups'] == r['unmatched_calls']+r['exact_matches']+r['censored']
    assert r['entry_candidates'] <= r['entry_mismatches']+r['already_used']+r['exact_matches'] <= r['entry_candidates']+r['lookups']
    assert r['touched_bytes'] == 48*r['touched_groups']
    assert r['touched_groups'] <= r['commits']*caps['max_touched_groups']
    assert r['peak_staging_bytes'] <= caps['batch_estimated_bytes']
    assert r['accepted_oracle_descendant_hooks_ns'] <= r['accepted_oracle_gross_ns']
    for metric in ['nodes', 'relations']:
        assert r['committed_'+metric] == task['committed_'+metric]
    status = vector(r['segment_status_counts'], 4)
    valid = vector(r['valid_segment_status_counts'], 4)
    depths, sizes = vector(r['matching_depth'], 64), vector(r['surviving_size'], 9)
    assert all(v <= a for v, a in zip(valid, status))
    if active:
        assert sum(status) == f['segments'] and sum(valid) == f['valid_segments']
        assert valid[1] == status[1] <= r['semantic_rejections']+r['validation_censored']
        assert r['lookups'] == task['fallback_nodes']+r['commits']
        assert r['censored'] == (r['lookups'] if task['oracle']['censored'] else 0)
        if task['oracle']['censored']:
            assert r['commits'] == 0
    else:
        assert all(r[k] == 0 for k in METRIC_COUNTS)
        assert not any(status+valid)
    ranges = r['committed_ranges']
    assert type(ranges) is list and len(ranges) == r['commits'] <= f['valid_segments']
    observed_depths, observed_sizes = [0]*64, [0]*9
    for row in ranges:
        vector(row, 6)
        begin, end, nodes, relations, ply, oracle_id = row
        assert begin < end <= f['segments'] and 0 < nodes <= caps['max_recorded_nodes'] and ply < 64
        assert oracle_id+nodes <= task['oracle']['segments'] <= task['canonical_nodes']
        observed_depths[ply] += 1
        observed_sizes[size_bin(nodes)] += 1
    ordered = sorted(ranges)
    assert all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), 'overlapping speculative credit'
    canonical = sorted((r[5], r[5]+r[2]) for r in ranges)
    assert all(a[1] <= b[0] for a, b in zip(canonical, canonical[1:])), 'overlapping canonical credit'
    assert [r[5] for r in ranges] == sorted({r[5] for r in ranges})
    assert sum(r[2] for r in ranges) == task['committed_nodes']
    assert sum(r[3] for r in ranges) == task['committed_relations']
    assert observed_depths == depths and observed_sizes == sizes
    assert r['commits'] <= valid[2] and status[2] == sum(r[1]-r[0] for r in ranges)
    assert task['whole_child_nodes'] == sum(r[2] for r in ranges if r[5] == 0)
    return dict(semantic=reasons(r['rejection_reasons'], r['semantic_rejections']),
        censor=reasons(r['censor_reasons'], r['validation_censored']),
        entryMismatch=reasons(r['entry_mismatch_reasons'], r['entry_mismatches']))


def audit_task(task, report, chosen):
    caps = chosen['caps']
    for k in ['id', 'speculative_nodes', 'speculative_relations', 'canonical_nodes',
              'canonical_relations', 'committed_nodes', 'committed_relations',
              'whole_child_nodes', 'descendant_nodes', 'fallback_nodes', 'wasted_nodes',
              'worker_ns', 'worker_setup_ns', 'worker_finalize_ns', 'wait_ns',
              'canonical_ns', 'overlay_groups', 'overlay_bytes', 'private_bytes',
              'started_ns', 'finished_ns', 'demand_ns']:
        count(task[k])
    assert task['id'] < 7
    for k in ['affinity_ok', 'complete', 'demanded', 'ready_at_demand', 'changed_window', 'local_oracle_match']:
        assert type(task[k]) is bool
    assert task['affinity_ok'] and task['local_oracle_match']
    assert task['speculative_nodes'] <= caps['max_recorded_nodes']
    assert task['overlay_groups'] <= caps['max_touched_groups']+64
    assert task['overlay_bytes'] == task['overlay_groups']*48
    assert task['private_bytes'] <= caps['batch_estimated_bytes']
    for metric in ['nodes', 'relations']:
        assert task['committed_'+metric] <= min(task['speculative_'+metric], task['canonical_'+metric])
    assert task['fallback_nodes'] == task['canonical_nodes']-task['committed_nodes']
    assert task['wasted_nodes'] == task['speculative_nodes']-task['committed_nodes']
    assert task['whole_child_nodes']+task['descendant_nodes'] == task['committed_nodes']
    if task['worker'] is None:
        assert task['cpu'] is None
        if report['threads'] == 1:
            assert task['stop'] == ('native-no-speculation' if task['demanded'] else 'native-not-demanded')
            assert task['complete'] == task['demanded']
        else:
            assert not task['complete'] and task['stop'] == 'not-started'
        assert not any(task[k] for k in ['speculative_nodes', 'speculative_relations',
            'worker_ns', 'worker_setup_ns', 'worker_finalize_ns', 'overlay_groups', 'overlay_bytes', 'private_bytes'])
        assert task['started_ns'] == task['finished_ns'] == 0
    else:
        assert type(task['worker']) is int and 0 <= task['worker'] < report['worker_count']
        assert task['cpu'] == WORKER_CPUS[task['worker']]
        assert task['stop'] in [None, 'cancelled', 'overlay-group-cap', 'executed-node-cap', 'task-lifetime-cap']
        assert task['complete'] == (task['stop'] is None)
        assert 0 < task['started_ns'] <= task['finished_ns'] <= report['timings']['split_wall_ns']
        assert task['worker_ns'] <= task['finished_ns']-task['started_ns']
    audit_forest(task['forest'], caps)
    audit_forest(task['oracle'], caps, oracle=True)
    if task['demanded'] and not task['oracle']['censored']:
        assert task['oracle']['segments'] == task['canonical_nodes']
    if task['worker'] is not None and not task['forest']['censored']:
        if task['complete']:
            assert task['forest']['segments'] == task['speculative_nodes']
        else:
            # Recording starts before the existing node-boundary cancellation
            # check charges N; an interrupted entry can have one extra record.
            assert task['speculative_nodes'] <= task['forest']['segments'] <= task['speculative_nodes']+1
    window = task['actual_window']
    assert type(window) is list and len(window) == 2 and all(type(v) is int for v in window)
    if task['demanded']:
        assert window[0] < window[1] and task['canonical_ns'] > 0
        assert 0 < task['demand_ns'] <= report['timings']['split_wall_ns']
        assert task['changed_window'] == (window != report['selector']['forecast_windows'][task['id']])
    else:
        assert window == [0, 0] and not task['changed_window'] and not task['ready_at_demand']
        assert not any(task[k] for k in ['canonical_nodes', 'canonical_relations', 'committed_nodes',
            'committed_relations', 'whole_child_nodes', 'descendant_nodes', 'fallback_nodes', 'canonical_ns', 'wait_ns', 'demand_ns'])
    assert task['wait_ns'] <= report['timings']['wait_ns']
    return audit_recovery(task, caps, task['demanded'] and task['worker'] is not None)


def audit_funnel(report):
    fields = ['post_child0', 'finite_window', 'depth_ge3', 'remaining_ge8',
              'best_le_lower', 'child0_ge2048']
    funnel = report['selector_funnel']
    assert type(funnel) is list and len(funnel) == 8
    assert report['oracle_selector_funnel'] == funnel
    for row in report['oracle_selector_funnel']:
        for value in row.values():
            count(value)
    total_hits = 0
    for iteration, row in enumerate(funnel, 1):
        assert set(row) == {'iteration', *fields, 'max_child0_nodes_other_conditions'}
        assert type(row['iteration']) is int and row['iteration'] == iteration
        counts = [count(row[key]) for key in fields]
        assert all(a >= b for a, b in zip(counts, counts[1:])), ('nonmonotone selector funnel', iteration)
        maximum = count(row['max_child0_nodes_other_conditions'])
        assert maximum <= report['canonical_nodes']
        assert counts[-1] in [0, 1]
        if counts[-2] == 0:
            assert maximum == 0
        assert (maximum >= 2048) == (counts[-1] == 1)
        if total_hits:
            assert not any(counts) and maximum == 0, 'funnel continued after first selected parent'
        total_hits += counts[-1]
    assert total_hits == int(not report['selector_miss'])
    assert sum(row['post_child0'] for row in funnel) <= report['canonical_nodes']
    if total_hits:
        selected = report['selector']
        row = funnel[selected['iteration']-1]
        assert row['child0_ge2048'] == 1
        assert row['max_child0_nodes_other_conditions'] == selected['child0_nodes']
    return funnel


def audit_report(report, chosen):
    assert report['schema'] == chosen['reportSchema']
    assert type(report['horizon']) is int and report['horizon'] == 8
    assert report['threads'] in BUDGETS and report['worker_count'] == report['threads']-1
    assert report['worker_cpu_plan'] == WORKER_CPUS[:report['worker_count']]
    assert report['coordinator_cpu'] == 14
    placements = report['worker_placements']
    if report['selector_miss']:
        assert placements == []
    else:
        assert len(placements) == report['worker_count']
        for i, placement in enumerate(placements):
            assert placement['worker'] == i and placement['target_cpu'] == placement['actual_cpu'] == WORKER_CPUS[i]
            assert placement['singleton_affinity_ok'] is True
            assert 0 < count(placement['startup_ns']) <= count(placement['exit_ns']) <= report['timings']['split_wall_ns']
    assert report['caps'] == dict(max_depth=8, task_nodes=262144, log_events=524288,
        segments=131072, forest_bytes=268435456, batch_estimated_bytes=2147483648,
        process_bytes=8589934592, lifetime_seconds=180)
    for k in ['fixed_completion', 'no_host', 'zero_randomness', 'complete_order_certificate', 'oracle_match']:
        assert report[k] is True
    assert report['unsafe_validation'] is False and report['fatal_reason'] is None and report['error'] is None
    assert type(report['selector_miss']) is bool
    assert report['completed_depth'] == 8
    for k in ['processId', 'canonical_nodes', 'canonical_relations', 'oracle_nodes',
              'oracle_relations', 'root_passes', 'speculative_nodes', 'committed_nodes',
              'committed_relations', 'wasted_nodes', 'queue_cancelled', 'worker_panics',
              'tt_base_copy_bytes', 'tt_base_bytes', 'snapshot_bytes', 'batch_estimated_bytes',
              'forest_bytes_total', 'peak_forest_bytes', 'oracle_forest_bytes', 'peak_rss_kib']:
        count(report[k])
    assert report['canonical_nodes'] == report['oracle_nodes'] > 0
    assert report['canonical_relations'] == report['oracle_relations']
    assert report['root_passes'] > 0 and report['worker_panics'] == 0
    assert report['peak_rss_kib']*1024 <= chosen['limits']['addressSpaceBytes']
    t = report['timings']; assert set(t) == set(TIMINGS)
    for n in t.values():
        count(n)
    assert t['search_wall_ns'] > 0 and t['search_process_cpu_ns'] > 0
    assert t['split_wall_ns'] <= t['search_wall_ns'] and t['split_process_cpu_ns'] <= t['search_process_cpu_ns']
    assert t['snapshot_ns'] <= t['setup_ns']
    assert t['setup_ns']+t['wait_ns']+t['join_ns'] <= t['split_wall_ns']
    assert report['batch_estimated_bytes'] <= chosen['caps']['batch_estimated_bytes']
    assert report['peak_forest_bytes'] <= 7*chosen['caps']['max_forest_bytes']
    assert report['forest_bytes_total'] <= 7*chosen['caps']['max_forest_bytes']
    tasks = report['tasks']; assert type(tasks) is list
    assert [task['id'] for task in tasks] == sorted({task['id'] for task in tasks})
    if report['selector_miss']:
        assert report['selector'] is None and not tasks
        assert all(t[k] == 0 for k in ['split_wall_ns', 'split_process_cpu_ns', 'setup_ns', 'snapshot_ns', 'wait_ns', 'join_ns'])
    else:
        s = report['selector']; lower, upper = s['window']
        assert all(type(v) is int for v in [lower, upper, s['best'], s['depth'], s['ply'], s['iteration']])
        assert -10000 < lower < upper < 10000 and s['best'] <= lower
        assert s['depth'] >= 3 and 1 <= s['iteration'] <= 8 and 1 <= s['ply'] < 64
        assert count(s['remaining']) >= 8 and count(s['child0_nodes']) >= 2048
        assert s['child0_nodes'] <= count(s['entry_nodes']) <= report['canonical_nodes']
        assert type(s['input_fingerprint']) is str and len(s['input_fingerprint']) == 16
        int(s['input_fingerprint'], 16)
        assert len(s['task_ids']) == len(set(s['task_ids'])) == len(s['movements']) == 7
        assert all(type(v) is int and v >= 0 for v in s['task_ids'])
        assert all(type(v) is str and v for v in s['movements'])
        assert s['forecast_windows'] == [[-upper, -lower]]*7
        assert t['split_wall_ns'] > 0 and t['split_process_cpu_ns'] > 0
        assert [task['id'] for task in tasks] == list(range(7))
        if report['threads'] > 1:
            assert report['tt_base_copy_bytes'] > 0
            # NativeBatchBase owns a Box<[Group]> and u8 (24 bytes on this
            # pinned x86_64 target); Arc contributes two usize counts (16).
            assert report['tt_base_bytes'] == report['tt_base_copy_bytes']+40
            assert report['snapshot_bytes'] > 0 and report['batch_estimated_bytes'] > 0
            expected_memory = (7*chosen['caps']['max_forest_bytes']+report['tt_base_bytes']
                +report['worker_count']*(report['snapshot_bytes']+131136*192)+64*1024*1024)
            assert report['batch_estimated_bytes'] == expected_memory
        else:
            assert all(task['worker'] is None for task in tasks)
            assert t['snapshot_ns'] == t['wait_ns'] == t['join_ns'] == 0
    if report['selector_miss'] or report['threads'] == 1:
        assert all(report[k] == 0 for k in ['tt_base_copy_bytes', 'tt_base_bytes', 'snapshot_bytes',
            'batch_estimated_bytes', 'speculative_nodes', 'committed_nodes', 'committed_relations',
            'wasted_nodes', 'queue_cancelled', 'forest_bytes_total', 'peak_forest_bytes'])
    reason_totals = {key: collections.Counter() for key in ['semantic', 'censor', 'entryMismatch']}
    for task in tasks:
        for key, values in audit_task(task, report, chosen).items():
            reason_totals[key].update(values)
    for placement in placements:
        produced = sorted((t['started_ns'], t['finished_ns']) for t in tasks if t['worker'] == placement['worker'])
        assert all(placement['startup_ns'] <= start <= end <= placement['exit_ns'] for start, end in produced)
        assert all(a[1] <= b[0] for a, b in zip(produced, produced[1:])), 'one worker ran overlapping tasks'
    for field in ['speculative_nodes', 'committed_nodes', 'committed_relations', 'wasted_nodes']:
        assert report[field] == sum(task[field] for task in tasks)
    assert report['forest_bytes_total'] == sum(task['forest']['bytes'] for task in tasks)
    assert report['peak_forest_bytes'] == report['forest_bytes_total']
    assert report['oracle_forest_bytes'] == sum(task['oracle']['bytes'] for task in tasks)
    assert report['oracle_forest_bytes'] <= 7*chosen['caps']['max_forest_bytes']
    assert t['wait_ns'] == sum(task['wait_ns'] for task in tasks)
    if report['threads'] > 1:
        assert report['queue_cancelled'] == sum(task['worker'] is None for task in tasks)
    else:
        assert report['queue_cancelled'] == 0
    demanded = [task['id'] for task in tasks if task['demanded']]
    assert demanded == list(range(len(demanded))), 'canonical children must be demanded in order'
    audit_funnel(report)
    return {k: dict(v) for k, v in reason_totals.items()}


def distribution(values):
    assert values
    return dict(median=statistics.median(values), minimum=min(values), maximum=max(values))


def checked_preparation(path):
    prep = read(path); directory = path.parent
    assert prep['schema'] == 'rook2-internal-split-preparation-run-v1'
    assert prep['complete'] is True and prep['failure'] is None
    assert prep['sourceBefore'] == prep['sourceAfter']
    assert prep['baselineBefore'] == prep['baselineAfter']
    for name, digest in prep['sourceBefore'].items():
        assert sha(directory/'source-before'/name) == digest
    for name, digest in prep['tools'].items():
        assert sha(name) == digest
    selectors = prep['selectors']
    assert selectors and len(selectors) == len(set(selectors))
    stages = prep['stages']; assert len(stages) == len(selectors)+1
    tests = []
    for i, stage in enumerate(stages):
        expected = f'tests-{i:02d}' if i < len(selectors) else 'build'
        assert stage['stage'] == expected and stage['exit'] == 0 and count(stage['wallNs']) > 0
        assert sha(directory/(expected+'.stdout')) == stage['stdoutSha256']
        assert sha(directory/(expected+'.stderr')) == stage['stderrSha256']
        if i < len(selectors):
            assert stage['argv'][-3:] == [selectors[i], '--', '--test-threads=1']
            names = stage['passedTests']; assert names
            assert all(name.startswith(selectors[i]) for name in names)
            text = (directory/(expected+'.stdout')).read_text()
            assert all(f'test {name} ... ok\n' in text for name in names)
            assert f'test result: ok. {len(names)} passed; 0 failed; 0 ignored;' in text
            tests.extend(names)
    assert len(tests) == len(set(tests)) == prep['focusedTests'] > 0
    return prep


def audit_preparation(path, receipt):
    prep = checked_preparation(path)
    assert prep['crate'] == receipt['crate']
    assert prep['sourceBefore'] == receipt['sourceBefore']
    assert prep['baselineBefore'] == receipt['baselineBefore']
    assert prep['selectors'] == ['internal_split::tests::horizon_']
    inherited = prep['inheritedControls']
    assert set(inherited) == {'path', 'sha256', 'focusedTests'}
    old_path = Path('/home/legolas/rook2-experiments/internal-split-20261026-01/prepare/preparation-run.json')
    assert inherited['path'] == str(old_path) and sha(old_path) == inherited['sha256']
    old = checked_preparation(old_path)
    assert old['focusedTests'] == inherited['focusedTests'] == 36
    assert old['selectors'][:3] == ['internal_split::tests::', 'remembered::native_overlay_tests::', 'remembered::sparse_tests::']
    assert old['baselineBefore'] == prep['baselineBefore']
    delta = sorted(key for key in set(old['sourceBefore']) | set(prep['sourceBefore'])
                   if old['sourceBefore'].get(key) != prep['sourceBefore'].get(key))
    assert delta == prep['reusedSourceDelta'] == ['src/bin/rook2-internal-split.rs', 'src/internal_split.rs']


def audit_inputs():
    spec_path = Path('/home/legolas/king-spec/conformance/profiling/workloads.json')
    cases = read(spec_path)['cases']
    for name in CASES:
        case, = [c for c in cases if c['id'] == name]
        assert case['position']['initial'] == 'standard-start'
        parameters = case['personality']['parameters']
        expected = dict(case=name, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            moves=' '.join(case['position']['moves']), randomness='0')
        fields = dict(own=['myp', 'myn', 'myb', 'myr', 'myq', 'myk', 'mycc', 'mymob', 'myks', 'mypp', 'mypw'],
            opponent=['opp', 'opn', 'opb', 'opr', 'opq', 'opk', 'opcc', 'opmob', 'opks', 'oppp', 'oppw'],
            evaluation=['avd', 'cfd', 'sop'], search=['sel', 'md', 'tts', 'ana'])
        for field, keys in fields.items():
            expected[field] = ','.join(str(parameters[k]) for k in keys)
        assert parameters['rnd'] == 0
        lines = (HERE/'inputs'/(name+'.txt')).read_text().splitlines()
        entries = [line.split('=', 1) for line in lines if line and not line.startswith('#')]
        assert len(entries) == len(dict(entries)) and dict(entries) == expected


def pid_and_group_gone(pids, groups):
    for pid in pids:
        assert not Path(f'/proc/{pid}').exists(), ('recorded PID is live; inspect reuse', pid)
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            stat = (proc/'stat').read_text()
        except (FileNotFoundError, ProcessLookupError):
            continue
        group = int(stat[stat.rfind(')')+2:].split()[2])
        assert group not in groups, ('recorded process group is live; inspect reuse', group)


def audit_native(directory, image, options, row, chosen):
    native, terminal = read(directory/'native.json'), read(directory/'terminal.json')
    assert native['schema'] == 'rook2-internal-native-wait4-v1'
    assert native['failure'] is None and native['native_exit_code'] == native['native_wait_status'] == 0
    assert native['engine'] == str(image) and native['argv'] == [str(image), *options]
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
    assert native['supervisor_affinity'] == [chosen['supervisorCpu']]
    assert native['native_pid'] == row['nativePid'] and native['supervisor_pid'] == row['supervisorPid']
    assert native['native_pid'] != native['supervisor_pid']
    assert native['native_pre_exec'] == [dict(pid=native['native_pid'], pgid=native['supervisor_pid'], affinity=[14])]
    observed = native['native_post_exec']
    # /proc observation can race a very short process; these lives enclose two
    # fixed searches, so require the actual native image to have been observed.
    assert observed is not None and observed['exe'] == str(image)
    assert observed['tasks'] == [str(native['native_pid'])]
    status = dict(line.split(':', 1) for line in observed['status'].splitlines() if ':' in line)
    assert int(status['Pid']) == int(status['Tgid']) == native['native_pid']
    assert int(status['PPid']) == native['supervisor_pid'] and status['Cpus_allowed_list'].strip() == '14'
    assert terminal['pid'] == native['supervisor_pid'] and terminal['exit'] == 0 and terminal['cleanup'] is None
    start, end = count(terminal['startMonotonicNs']), count(terminal['endMonotonicNs'])
    assert 0 < count(native['wall_ns']) <= end-start <= chosen['limits']['perLifeSeconds']*10**9
    for k in ['total_cpu_s', 'user_cpu_s', 'system_cpu_s']:
        assert type(native[k]) in [float, int] and math.isfinite(native[k]) and native[k] >= 0
    assert native['total_cpu_s'] == native['user_cpu_s']+native['system_cpu_s'] > 0
    assert row['wholeCpuSeconds'] == native['total_cpu_s']
    assert row['nativeWallNs'] == native['wall_ns']
    assert row['rssKiB'] == count(native['maxrss_linux_kib']) > 0
    assert native['maxrss_linux_kib']*1024 <= chosen['limits']['addressSpaceBytes']
    for k in ['voluntary_context_switches', 'involuntary_context_switches']:
        count(native[k])
    return native, terminal


def audit_housekeeping(record, chosen, threads, originals):
    cpus = chosen['runtimeHousekeepingCpusAt8'] if threads == 8 else chosen['runtimeHousekeepingCpus']
    assert cpus == ([13] if threads == 8 else list(range(8, 14)))
    assert record['cpus'] == record['selfAffinity'] == cpus
    keys = set()
    for task in record['selectedTasks']:
        key = tuple(count(task[k]) for k in ['pid', 'tid', 'starttime'])
        assert key not in keys; keys.add(key)
        assert task['after'] == cpus and task['before'] == sorted(set(task['before']))
        assert task['before'] and all(type(c) is int and 0 <= c < 16 for c in task['before'])
        originals.setdefault(key, task['before'])


def canonical_identity(report):
    return dict(selector=report['selector'], selectorMiss=report['selector_miss'],
        canonicalNodes=report['canonical_nodes'], canonicalRelations=report['canonical_relations'],
        rootPasses=report['root_passes'], completedDepth=report['completed_depth'],
        horizon=report['horizon'], selectorFunnel=report['selector_funnel'],
        demanded=[dict(id=t['id'], window=t['actual_window'], nodes=t['canonical_nodes'],
            relations=t['canonical_relations']) for t in report['tasks'] if t['demanded']])


def summarize_group(lives):
    assert len(lives) == 3 and {r['step']['repeat'] for r in lives} == {1, 2, 3}
    first = lives[0]; reports = [r['report'] for r in lives]
    out = dict(case=first['step']['case'], threads=first['step']['threads'], observations=3,
        selectorMiss=reports[0]['selector_miss'])
    if out['selectorMiss']:
        out['finding'] = 'Coverage miss; no internal split or scaling timing claim.'
        return out
    out['timingsNs'] = {key: distribution([r['timings'][key] for r in reports]) for key in TIMINGS}
    out['wholeNativeWait4CpuSeconds'] = distribution([r['native']['total_cpu_s'] for r in lives])
    out['wholeNativeWait4WallNs'] = distribution([r['native']['wall_ns'] for r in lives])
    out['wholeNativePeakRssKiB'] = distribution([r['native']['maxrss_linux_kib'] for r in lives])
    fields = ['canonical_nodes', 'canonical_relations', 'speculative_nodes',
              'committed_nodes', 'committed_relations', 'wasted_nodes', 'queue_cancelled',
              'tt_base_copy_bytes', 'tt_base_bytes', 'snapshot_bytes', 'batch_estimated_bytes',
              'forest_bytes_total', 'peak_forest_bytes', 'oracle_forest_bytes', 'peak_rss_kib']
    out['counts'] = {key: distribution([r[key] for r in reports]) for key in fields}
    task_fields = ['whole_child_nodes', 'descendant_nodes', 'fallback_nodes',
        'worker_ns', 'worker_setup_ns', 'worker_finalize_ns', 'overlay_groups', 'overlay_bytes']
    out['taskTotals'] = {key: distribution([sum(t[key] for t in r['tasks']) for r in reports]) for key in task_fields}
    for key, predicate in [('demanded', lambda t: t['demanded']),
        ('readyAtDemand', lambda t: t['demanded'] and t['ready_at_demand']),
        ('changedWindow', lambda t: t['demanded'] and t['changed_window']),
        ('started', lambda t: t['worker'] is not None),
        ('complete', lambda t: t['complete']), ('cappedForests', lambda t: t['forest']['censored'])]:
        out['taskTotals'][key] = distribution([sum(predicate(t) for t in r['tasks']) for r in reports])
    out['recoveryTotals'] = {key: distribution([sum(t['recovery'][key] for t in r['tasks']) for r in reports])
        for key in METRIC_COUNTS}
    out['oracleGrossMinusDescendantHooksNs'] = distribution([sum(
        t['recovery']['accepted_oracle_gross_ns']-t['recovery']['accepted_oracle_descendant_hooks_ns']
        for t in r['tasks']) for r in reports])
    out['reasonCountsAcrossObservations'] = {key: dict(sum((collections.Counter(r['reasons'][key]) for r in lives), collections.Counter()))
        for key in ['semantic', 'censor', 'entryMismatch']}
    out['taskStopCountsAcrossObservations'] = dict(collections.Counter(t['stop'] or 'complete' for r in reports for t in r['tasks']))
    out['tasks'] = [dict(id=i,
        speculativeNodes=distribution([r['tasks'][i]['speculative_nodes'] for r in reports]),
        committedNodes=distribution([r['tasks'][i]['committed_nodes'] for r in reports]),
        workerNs=distribution([r['tasks'][i]['worker_ns'] for r in reports]),
        demandWaitNs=distribution([r['tasks'][i]['wait_ns'] for r in reports]),
        readyObservations=sum(r['tasks'][i]['demanded'] and r['tasks'][i]['ready_at_demand'] for r in reports),
        demandedObservations=sum(r['tasks'][i]['demanded'] for r in reports),
        changedWindowObservations=sum(r['tasks'][i]['changed_window'] for r in reports)) for i in range(7)]
    out['workers'] = []
    for i in range(first['step']['threads']-1):
        def interval(r):
            placement = r['worker_placements'][i]
            lifetime = placement['exit_ns']-placement['startup_ns']
            busy = sum(t['finished_ns']-t['started_ns'] for t in r['tasks'] if t['worker'] == i)
            return lifetime, busy
        intervals = [interval(r) for r in reports]
        out['workers'].append(dict(worker=i, cpu=WORKER_CPUS[i],
            startupNs=distribution([r['worker_placements'][i]['startup_ns'] for r in reports]),
            lifetimeNs=distribution([row[0] for row in intervals]),
            taskIntervalNs=distribution([row[1] for row in intervals]),
            outsideTaskIntervalNs=distribution([row[0]-row[1] for row in intervals])))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-internal-horizon-collection-v1'
    assert result['schema'] == 'rook2-internal-horizon-result-v1'
    assert result['complete'] is True and result['failure'] is None
    chosen = audit_policy(plan['policy'])
    assert read(plan['policyPath']) == chosen and sha(plan['policyPath']) == plan['policySha256']
    activation = activation_from_raw(base, result['runs'])
    assert result['activation'] == activation
    coverage = {case: row['eligible'] for case, row in activation.items()}
    schedule = expected_schedule(coverage)
    assert plan['schedule'] == chosen['schedule'] and result['realizedSchedule'] == schedule
    assert len(result['runs']) == len(schedule)
    assert plan['scope'] == chosen['scope']
    pins = plan['inputSha256']; assert type(pins) is dict
    required = [*HERE.glob('*.py'), HERE/'policy.json', Path('/usr/bin/python3'),
        Path('/home/legolas/king-spec/conformance/profiling/workloads.json'),
        Path(plan['build'])/'receipt.json', Path(plan['binary']), Path(plan['preparation'])]
    required += [HERE/'inputs'/(case+'.txt') for case in CASES]
    assert all(str(p.resolve()) in pins for p in required)
    for path, digest in pins.items():
        assert sha(path) == digest, ('input changed', path)
    receipt = admit(Path(plan['build'])); image = Path(plan['binary'])
    assert receipt['sourceBefore'] == plan['sourcePins'] == snapshot(Path(receipt['crate']))
    assert receipt['baselineBefore'] == plan['baseline'] == baseline()
    assert receipt['binary'] == str(image) and receipt['binarySha256'] == plan['binarySha256'] == sha(image)
    assert all(path in pins and pins[path] == digest for path, digest in plan['baseline']['protectedArtifacts'].items())
    audit_preparation(Path(plan['preparation']), receipt)
    audit_inputs()
    assert 0 < result['endMonotonicNs']-result['startMonotonicNs'] <= chosen['limits']['streamSeconds']*10**9
    previous = result['startMonotonicNs']; lives = []; identities = {}; pids = set(); groups = set(); originals = {}
    for i, (step, row) in enumerate(zip(schedule, result['runs'])):
        assert all(row[k] == v and type(row[k]) is type(v) for k, v in step.items())
        potential_index = plan['schedule'].index(step)
        directory = base/f'{potential_index:02d}-{step["case"]}-t{step["threads"]}-r{step["repeat"]}'
        assert row['directory'] == str(directory) and directory.is_dir() and not directory.is_symlink()
        assert set(row['sha256']) == RAW_FILES
        for name, digest in row['sha256'].items():
            assert (directory/name).is_file() and not (directory/name).is_symlink()
            assert sha(directory/name) == digest
        assert (directory/'stderr').read_bytes() == b''
        assert 0 < (directory/'stdout').stat().st_size <= chosen['limits']['reportBytes']
        input_path = HERE/'inputs'/(step['case']+'.txt')
        options = ['--input', str(input_path), '--threads', str(step['threads']), '--max-depth', '8']
        command = ['/usr/bin/python3', str(HERE/'account.py'), '--engine', str(image), '--record', str(directory/'native.json'), *options]
        assert read(directory/'launch.json') == dict(argv=command, nativeArgv=[str(image), *options],
            step=step, policySha256=plan['policySha256'])
        native, terminal = audit_native(directory, image, options, row, chosen)
        assert previous <= terminal['startMonotonicNs'] < terminal['endMonotonicNs'] <= result['endMonotonicNs']
        previous = terminal['endMonotonicNs']
        assert native['native_pid'] not in pids and native['supervisor_pid'] not in pids
        pids.update([native['native_pid'], native['supervisor_pid']]); groups.add(native['supervisor_pid'])
        audit_housekeeping(read(directory/'housekeeping.json'), chosen, step['threads'], originals)
        report = read(directory/'stdout')
        assert report['processId'] == native['native_pid'] and report['threads'] == step['threads']
        reasons_by_kind = audit_report(report, chosen)
        # Both executor and independent oracle are charged to whole wait4 CPU.
        assert report['timings']['search_process_cpu_ns']+report['timings']['oracle_process_cpu_ns'] <= native['total_cpu_s']*10**9+2_000_000
        assert report['timings']['search_wall_ns']+report['timings']['oracle_wall_ns'] <= native['wall_ns']
        identity = canonical_identity(report)
        assert identities.setdefault(step['case'], identity) == identity, ('canonical/selector drift', step)
        lives.append(dict(step=step, report=report, native=native, reasons=reasons_by_kind))
    pid_and_group_gone(pids, groups)
    restore = read(base/'housekeeping-restore.json'); restored = set()
    for row in restore:
        key = tuple(count(row[k]) for k in ['pid', 'tid', 'starttime'])
        assert key not in restored; restored.add(key)
        assert type(row['inheritedNewThread']) is bool
        if not row['inheritedNewThread']:
            assert key in originals and row['restored'] == originals[key]
    hits = [case for case in CASES if coverage[case]]
    output = dict(schema='rook2-internal-horizon-reconciled-v1', complete=True,
        raw=str(base), nativeLives=len(schedule), excludedWarmups=3+3*len(hits), observations=12*len(hits),
        activatedCases=hits, activation=activation, realizedSchedule=schedule,
        rawSha256={n: sha(base/n) for n in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after', 'housekeeping-restore.json']},
        reconcilerSha256=sha(Path(__file__)), canonicalIdentities=identities,
        summaries=[summarize_group([r for r in lives if not r['step']['warmup'] and r['step']['case'] == case and r['step']['threads'] == threads])
            for case in hits for threads in BUDGETS],
        timingScope='Raw wall and all-thread process CPU include setup, recording, validation, demand waits, cancellation/drain/join and in-interval oracle hooks. The independent oracle prepass and final compare are outside executor intervals. Whole native wait4 CPU includes oracle/startup and is never executor CPU. Nested costs and summed worker wall intervals are not additive CPU savings. Worker outsideTaskIntervalNs includes queue/channel/owner-drop overhead and waiting, not measured idle CPU.',
        workScope='Maximal accepted ranges are independently disjoint in each private speculative forest and canonical child tree; child task identities are distinct. Useful N/R and whole-child/descendant credit are recomputed. Oracle gross minus descendant hook nanoseconds is an instrumented native wall proxy, not CPU saved. peak_forest_bytes is the conservative sum of all produced private forest bytes, not measured simultaneous retention.',
        auditLimit='Independent native local output/work and whole-root final shared-state equality; transient incorrect shared writes later overwritten may escape this audit. Affinity receipts establish placement observations, not exclusive guest or host isolation.',
        scope='Depth8 horizon only; one prospective internal parent and seven fixed tasks, actual total budgets1/2/4/8 activated solely by three budget1 coverage hit and oracle-uncensored flags. Misses and censored coverage hits run once and receive no scaling timing claim. Complete-order exact-entry recovery, fixed completion/NoHost/rnd0. No selector retuning, PGO, qualification or adoption claim.')
    destination = args.output or base/'reconciled.json'
    with destination.open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    misses = sum(value['selectorMiss'] for value in identities.values())
    print(f'reconciled {len(schedule)} native lives; {3+3*len(hits)} warmups excluded; selector misses {misses}/3 workloads', flush=True)


if __name__ == '__main__':
    main()

