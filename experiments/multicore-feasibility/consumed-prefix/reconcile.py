#!/usr/bin/env python3
"""Independent paired source/native/cap/disjoint-work audit; no native execution."""
import argparse
import collections
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, BASE_HELPER, FROZEN_DIR, FROZEN_TOOLS, baseline, snapshot, admit, sha, read
from collect import ACCOUNT, SPEC, CASES, CAPS, AS_BYTES, OUTPUT_BYTES, policy, materialization

# Reuse the frozen independent range/cap/native checks; importing runs no native work.
_spec = importlib.util.spec_from_file_location('closed_hierarchical_readonly_auditor', FROZEN_DIR/'reconcile.py')
legacy = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(legacy)
count, native_receipt = legacy.count, legacy.native_receipt
POLICIES = ['complete-order', 'consumed-prefix']


def checked_costs(value, common=False):
    fields = legacy.COST_FIELDS+['audit_counterfactual_ns', 'executor_observed_ns', 'audit_observed_ns']
    assert set(value) == set(fields)
    for number in value.values():
        count(number)
    shared = ['prefix_ns', 'snapshot_ns', 'recording_setup_ns', 'speculation_ns',
              'recording_finalize_ns', 'oracle_snapshot_ns', 'oracle_execute_ns']
    if common:
        assert all(value[k] == 0 for k in fields if k not in shared+['executor_observed_ns', 'audit_observed_ns'])
    else:
        assert all(value[k] == 0 for k in shared)
    inside = value['oracle_local_ns']+value['oracle_entry_ns']+value['audit_counterfactual_ns']
    assert inside <= value['canonical_execute_ns']
    executor = sum(value[k] for k in ['prefix_ns', 'snapshot_ns', 'recording_setup_ns',
        'speculation_ns', 'recording_finalize_ns', 'canonical_execute_ns'])-inside
    audit = sum(value[k] for k in ['oracle_snapshot_ns', 'oracle_execute_ns', 'oracle_compare_ns'])+inside
    assert value['executor_observed_ns'] == executor and value['audit_observed_ns'] == audit
    assert sum(value[k] for k in ['lookup_ns', 'staging_ns', 'validation_ns', 'commit_ns'])+inside <= value['recovery_hook_ns']
    assert value['native_fallback_estimate_ns'] == max(0, value['canonical_execute_ns']-value['recovery_hook_ns'])


def histogram(value, length=9):
    assert type(value) is list and len(value) == length
    for n in value:
        count(n)
    return value


def reason_sizes(rows, expected):
    assert type(rows) is list and len(rows) <= 32
    assert len({r['reason'] for r in rows}) == len(rows)
    for row in rows:
        assert type(row['reason']) is str and row['reason']
        assert sum(histogram(row['bins'])) == expected[row['reason']] > 0
    assert {r['reason'] for r in rows} == set(expected)
    return [sum(r['bins'][i] for r in rows) for i in range(9)]


def consumers(value, forest):
    for key in ['segments', 'eligible', 'proper_prefix', 'fully_consumed', 'eligible_nodes', 'eligible_relations']:
        count(value[key])
    assert value['segments'] == forest['segments']
    assert value['eligible'] == value['proper_prefix']+value['fully_consumed'] <= value['segments']
    assert value['eligible_nodes'] >= value['eligible']
    reasons = value['reasons']; assert len(reasons) <= 32
    assert len({r['reason'] for r in reasons}) == len(reasons)
    assert all(type(r['reason']) is str and r['reason'] and count(r['count']) > 0 for r in reasons)
    assert sum(r['count'] for r in reasons) == value['segments']
    assert sum(r['count'] for r in reasons if r['reason'] == 'eligible') == value['eligible']
    assert sum(histogram(value['prefix_length_bins'])) == sum(histogram(value['inventory_length_bins'])) == value['eligible']
    assert value['prefix_length_bins'][0] == value['inventory_length_bins'][0] == 0
    # Move inventories have at most512 entries, so bins above512..2047 are empty.
    assert all(n == 0 for n in value['prefix_length_bins'][7:]+value['inventory_length_bins'][7:])


def predicate_metrics(core, policy_name):
    r, timings = core['recovery'], core['timings']
    for key in ['order_main_prefix', 'order_main_complete', 'order_main_prefix_fallback', 'audit_counterfactual_ns']:
        count(r[key])
    assert r['audit_counterfactual_ns'] == timings['audit_counterfactual_ns']
    assert r['order_main_prefix_fallback'] <= r['order_main_complete']
    assert r['order_main_prefix']+r['order_main_complete'] <= r['exact_matches']*core['forest']['log_events']
    if policy_name == 'complete-order':
        assert r['order_main_prefix'] == r['order_main_prefix_fallback'] == 0
    order = histogram(r['order_rejections'])
    partitions = [histogram(r[k]) for k in ['order_suffix_only', 'order_prefix_changed', 'order_ineligible', 'order_inventory_changed']]
    assert all(order[i] == sum(row[i] for row in partitions) for i in range(9))
    rejected = {row['reason']: row['count'] for row in r['rejection_reasons']}
    assert sum(order) == rejected.get('ordinary-order', 0)
    semantic = histogram(r['semantic_rejection_size'])
    assert semantic == reason_sizes(r['rejection_size_by_reason'], rejected)
    mismatch_counts = {row['reason']: row['count'] for row in r['entry_mismatch_reasons'] if row['reason'] != 'epoch'}
    comparison_sizes = reason_sizes(r['entry_mismatch_size_by_reason'], mismatch_counts)
    assert comparison_sizes[0] == 0
    assert sum(semantic) == r['semantic_rejections']
    assert semantic[0] == order[0] == 0
    for key, total in [('order_consumer_rejections', order), ('order_depth_rejections', order),
                       ('semantic_consumer_rejections', semantic)]:
        matrix = r[key]; assert type(matrix) is list and len(matrix) == 3
        for row in matrix:
            histogram(row)
        assert all(sum(row[i] for row in matrix) == total[i] for i in range(9))
    prices = r['committed_range_oracle_costs']
    assert type(prices) is list and len(prices) == r['commits']
    for row in prices:
        assert type(row) is list and len(row) == 2
        assert count(row[1]) <= count(row[0])
    assert sum(row[0] for row in prices) == r['accepted_oracle_gross_ns']
    assert sum(row[1] for row in prices) == r['accepted_oracle_descendant_hooks_ns']


def interval_rows(core, canonical):
    rows = core['recovery']['committed_ranges']
    if canonical:
        assert not rows or not core['oracle']['censored']
        if not core['oracle']['censored']:
            assert core['oracle']['segments'] == core['canonical_nodes']
        result = [[r[5], r[5]+r[2], *r[2:5], r[0]] for r in rows]
        assert all(r[1] <= core['oracle']['segments'] for r in result)
    else:
        result = rows
    ordered = sorted(result)
    assert all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), 'accepted coverage overlaps'
    return result


def range_comparison(complete, prefix, canonical=True):
    """Gross maximal grain and signed net coverage, using one common oracle/forest."""
    left, right = interval_rows(complete, canonical), interval_rows(prefix, canonical)
    old = {(r[0], r[1]): r for r in left}
    new = [r for r in right if (r[0], r[1]) not in old]
    for row in right:
        if (row[0], row[1]) in old:
            assert row[2:5] == old[(row[0], row[1])][2:5]
    a, b = sorted(left), sorted(right); ai = bi = shared_n = shared_r = 0
    absorbed, absorbed_r = collections.Counter(), collections.Counter()
    while ai < len(a) and bi < len(b):
        x, y = a[ai], b[bi]
        if x[1] <= y[0]:
            ai += 1; continue
        if y[1] <= x[0]:
            bi += 1; continue
        assert (x[0] <= y[0] and y[1] <= x[1]) or (y[0] <= x[0] and x[1] <= y[1]), 'non-laminar shared tree'
        inner = x if y[0] <= x[0] and x[1] <= y[1] else y
        shared_n += inner[2]; shared_r += inner[3]
        if y[0] <= x[0] and x[1] <= y[1] and (x[0], x[1]) != (y[0], y[1]):
            absorbed[(y[0], y[1])] += x[2]; absorbed_r[(y[0], y[1])] += x[3]
        if x[1] <= y[1]:
            ai += 1
        else:
            bi += 1
    for row in new:
        assert absorbed[(row[0], row[1])] <= row[2] and absorbed_r[(row[0], row[1])] <= row[3]
    assert shared_n <= min(complete['committed_nodes'], prefix['committed_nodes'])
    assert shared_r <= min(complete['committed_relations'], prefix['committed_relations'])
    sizes = [0]*9
    for row in new:
        sizes[legacy.bin_size(row[2])] += 1
    prices = prefix['recovery']['committed_range_oracle_costs']
    new_prices = [price for row, price in zip(right, prices) if (row[0], row[1]) not in old]
    if canonical:
        old_prices = {(r[0], r[1]): price for r, price in zip(left, complete['recovery']['committed_range_oracle_costs'])}
        assert all(price == old_prices[(r[0], r[1])] for r, price in zip(right, prices) if (r[0], r[1]) in old_prices)
    before, after = complete['recovery'], prefix['recovery']
    return dict(gross_new_maximal_ranges=len(new), gross_new_maximal_nodes=sum(r[2] for r in new),
        gross_new_maximal_relations=sum(r[3] for r in new), new_maximal_size_bins=sizes,
        new_maximal_containing_old_descendants=sum(n > 0 for n in absorbed.values()),
        old_descendant_nodes_inside_new_maximal=sum(absorbed.values()),
        old_descendant_relations_inside_new_maximal=sum(absorbed_r.values()),
        common_covered_nodes=shared_n, common_covered_relations=shared_r,
        complete_only_nodes=complete['committed_nodes']-shared_n,
        complete_only_relations=complete['committed_relations']-shared_r,
        newly_covered_nodes=prefix['committed_nodes']-shared_n,
        newly_covered_relations=prefix['committed_relations']-shared_r,
        net_committed_nodes=prefix['committed_nodes']-complete['committed_nodes'],
        net_committed_relations=prefix['committed_relations']-complete['committed_relations'],
        gross_new_oracle_gross_ns=sum(p[0] for p in new_prices),
        gross_new_oracle_hooks_ns=sum(p[1] for p in new_prices),
        gross_new_oracle_proxy_ns=sum(p[0]-p[1] for p in new_prices),
        net_oracle_gross_ns=after['accepted_oracle_gross_ns']-before['accepted_oracle_gross_ns'],
        net_oracle_hooks_ns=after['accepted_oracle_descendant_hooks_ns']-before['accepted_oracle_descendant_hooks_ns'])


def sum_costs(cores):
    assert cores
    return {key: sum(c['timings'][key] for c in cores) for key in cores[0]['timings']}


def mode_summary(cores, arm_timing, common_timing, annotation, policy_name):
    recovery = [c['recovery'] for c in cores]
    hist_keys = ['matching_depth', 'surviving_size', 'semantic_rejection_size', 'order_rejections',
                 'order_suffix_only', 'order_prefix_changed', 'order_ineligible', 'order_inventory_changed']
    reasons = {}
    for key in ['rejection_reasons', 'censor_reasons', 'entry_mismatch_reasons']:
        totals = collections.Counter()
        for r in recovery:
            for row in r[key]:
                totals[row['reason']] += row['count']
        reasons[key] = dict(totals)
    result = dict(policy=policy_name, canonicalNodes=sum(c['canonical_nodes'] for c in cores),
        canonicalRelations=sum(c['canonical_relations'] for c in cores),
        committedNodes=sum(c['committed_nodes'] for c in cores), committedRelations=sum(c['committed_relations'] for c in cores),
        fallbackNodes=sum(c['fallback_nodes'] for c in cores), fallbackRelations=sum(c['fallback_relations'] for c in cores),
        committedSegments=sum(r['commits'] for r in recovery),
        headCommittedNodes=sum(c['committed_nodes'] for c in cores if c['ahead_distance'] == 0),
        headCommittedRelations=sum(c['committed_relations'] for c in cores if c['ahead_distance'] == 0),
        aheadCommittedNodes=sum(c['committed_nodes'] for c in cores if c['ahead_distance'] > 0),
        aheadCommittedRelations=sum(c['committed_relations'] for c in cores if c['ahead_distance'] > 0),
        headCommittedSegments=sum(c['recovery']['commits'] for c in cores if c['ahead_distance'] == 0),
        aheadCommittedSegments=sum(c['recovery']['commits'] for c in cores if c['ahead_distance'] > 0),
        acceptedOracleGrossMinusDescendantHooksNs=sum(r['accepted_oracle_gross_ns']-r['accepted_oracle_descendant_hooks_ns'] for r in recovery),
        costsArmOnly=arm_timing,
        costsArmOnlyByDemand={label: {key: sum(c['timings'][key] for c in cores if (c['ahead_distance'] > 0) == ahead)
            for key in arm_timing} for label, ahead in [('head', False), ('ahead', True)]},
        speculativeNodesByDemand={label: sum(c['speculative_nodes'] for c in cores if (c['ahead_distance'] > 0) == ahead)
            for label, ahead in [('head', False), ('ahead', True)]},
        speculativeRelationsByDemand={label: sum(c['speculative_relations'] for c in cores if (c['ahead_distance'] > 0) == ahead)
            for label, ahead in [('head', False), ('ahead', True)]},
        standaloneExecutorProxyNs=common_timing['executor_observed_ns']+arm_timing['executor_observed_ns']+(annotation if policy_name == 'consumed-prefix' else 0),
        standaloneAuditProxyNs=common_timing['audit_observed_ns']+arm_timing['audit_observed_ns'],
        counters={key: sum(r[key] for r in recovery) for key in ['lookups', 'entry_candidates', 'entry_mismatches', 'unmatched_calls',
            'exact_matches', 'semantic_rejections', 'validation_censored', 'commits', 'already_used', 'censored',
            'order_main_prefix', 'order_main_complete', 'order_main_prefix_fallback', 'touched_groups', 'touched_bytes']},
        histograms={key: [sum(r[key][i] for r in recovery) for i in range(len(recovery[0][key]))] for key in hist_keys},
        matrices={key: [[sum(r[key][i][j] for r in recovery) for j in range(9)] for i in range(3)] for key in
            ['semantic_consumer_rejections', 'order_consumer_rejections', 'order_depth_rejections']},
        entryMismatchComparisonSizeBins={reason: [sum(row['bins'][i] for r in recovery for row in r['entry_mismatch_size_by_reason'] if row['reason'] == reason)
            for i in range(9)] for reason in reasons['entry_mismatch_reasons'] if reason != 'epoch'},
        entryMismatchSizeScope='recorded-candidate comparison counts; epoch mismatches have no candidate size and are excluded; neither distinct canonical calls nor additive work',
        semanticReasonSizeBins={reason: [sum(row['bins'][i] for r in recovery for row in r['rejection_size_by_reason'] if row['reason'] == reason)
            for i in range(9)] for reason in reasons['rejection_reasons']},
        reasonCounts=reasons, peakStagingBytes=max(r['peak_staging_bytes'] for r in recovery),
        cappedForests=sum(c['forest']['censored'] for c in cores), cappedOracles=sum(c['oracle']['censored'] for c in cores))
    return result


def audit_report(report, chosen):
    assert report['schema'] == chosen['reportSchema'] and report['caps'] == chosen['caps'] == CAPS
    assert report['unsafe_validation'] is False and report['fatal_reason'] is None
    for field in ['zero_randomness', 'fixed_completion', 'no_host', 'inline_full']:
        assert report[field] is True
    assert count(report['restricted_entry_nodes']) >= 25000 and 1 <= report['restricted_depth'] <= 6
    assert report['prefix_nodes'] >= report['restricted_entry_nodes']
    assert count(report['abandoned_speculative_nodes']) == 0
    assert 1 <= report['max_queue_len'] <= 2
    assert count(report['peak_queue_forest_bytes']) <= 2*CAPS['max_forest_bytes']
    assert type(report['incomplete_iteration']) is bool
    assert report['stopped_reason'] == ('tail-candidate-cap' if report['incomplete_iteration'] else 'first-restricted-iteration-complete')
    assert report['completed_depth'] == report['restricted_depth']-int(report['incomplete_iteration'])
    common = report['common_timings']; checked_costs(common, common=True)
    pairs = report['pairs']; assert 0 < len(pairs) <= 8
    arms = {name: [] for name in POLICIES}; differences = []
    annotation = clone_ns = compare_ns = clone_bytes = 0
    difference_audit_ns = count(report['difference_audit_ns'])
    for turn, pair in enumerate(pairs):
        assert pair['turn'] == turn
        assert pair['execution_order'] == (POLICIES if turn % 2 == 0 else list(reversed(POLICIES)))
        for flag in ['same_input_state', 'same_input_epoch', 'same_input_history', 'shared_data_identical']:
            assert pair[flag] is True
        for key in ['shared_forest_id', 'shared_oracle_id', 'comparison_clone_ns', 'comparison_clone_bytes', 'input_compare_ns', 'annotation_ns']:
            count(pair[key])
        assert pair['shared_forest_id'] == pair['shared_oracle_id'] == turn
        assert pair['comparison_clone_bytes'] > 0 and count(pair['common_snapshot_bytes']) > 0
        checked_costs(pair['common_timings'], common=True)
        assert pair['common_timings']['prefix_ns'] == 0
        annotation += pair['annotation_ns']; clone_ns += pair['comparison_clone_ns']
        compare_ns += pair['input_compare_ns']; clone_bytes += pair['comparison_clone_bytes']
        variants = pair['variants']; assert len(variants) == 2
        assert sorted(v['policy'] for v in variants) == sorted(POLICIES)
        by_policy = {v['policy']: v['core'] for v in variants}
        cores = [by_policy[name] for name in POLICIES]
        for field in ['depth', 'index', 'id', 'movement', 'ahead_distance', 'enqueued_at_turn', 'consumed_at_turn',
                      'speculative_nodes', 'speculative_relations', 'canonical_nodes', 'canonical_relations', 'completed_passes', 'forest', 'oracle']:
            assert cores[0][field] == cores[1][field], ('paired canonical/common mismatch', turn, field)
        for name, core in zip(POLICIES, cores):
            assert core['depth'] == report['restricted_depth']
            assert 0 <= count(core['ahead_distance']) < 2
            assert core['consumed_at_turn'] == turn and core['index'] == turn+1
            assert core['enqueued_at_turn'] <= turn and core['ahead_distance'] == turn-core['enqueued_at_turn']
            assert core['oracle_match'] is True and core['rollback_unchanged'] is True and core['unsafe_validation'] is False
            assert count(core['completed_passes']) in [1, 2] and count(core['snapshot_bytes']) == 0
            for metric in ['nodes', 'relations']:
                canonical = count(core['canonical_'+metric]); committed = count(core['committed_'+metric])
                assert count(core['speculative_'+metric]) >= committed
                assert canonical == committed+count(core['fallback_'+metric])
            assert count(core['discarded_speculative_nodes']) == core['speculative_nodes']-core['committed_nodes']
            legacy.forest(core['forest']); legacy.forest(core['oracle'], oracle=True)
            if not core['forest']['censored']:
                assert core['forest']['segments'] == core['speculative_nodes']
            checked_costs(core['timings'])
            # The frozen independent recovery check receives a bound for the shared
            # oracle. This projection is validation-only, never a charged mode cost.
            projected = copy.deepcopy(core)
            projected['timings']['oracle_execute_ns'] = pair['common_timings']['oracle_execute_ns']
            legacy.recovery(projected)
            predicate_metrics(core, name); interval_rows(core, canonical=True)
            arms[name].append(core)
        consumers(pair['consumers'], cores[0]['forest'])
        canonical_diff = range_comparison(*cores, canonical=True)
        for key, value in pair['differences'].items():
            assert key in canonical_diff and type(value) is int and value == canonical_diff[key], (turn, key)
        required_differences = ['gross_new_maximal_nodes', 'gross_new_maximal_relations', 'gross_new_maximal_ranges',
            'net_committed_nodes', 'net_committed_relations', 'newly_covered_nodes', 'newly_covered_relations',
            'gross_new_oracle_gross_ns', 'gross_new_oracle_hooks_ns', 'net_oracle_gross_ns', 'net_oracle_hooks_ns']
        assert set(pair['differences']) == set(required_differences)
        differences.append(dict(turn=turn, id=cores[0]['id'], aheadDistance=cores[0]['ahead_distance'],
            executionOrder=pair['execution_order'], canonical=canonical_diff,
            recordedForest=range_comparison(*cores, canonical=False), consumers=pair['consumers'],
            comparisonCloneNs=pair['comparison_clone_ns'], comparisonCloneBytes=pair['comparison_clone_bytes'],
            inputCompareNs=pair['input_compare_ns'], annotationNs=pair['annotation_ns'],
            commonSnapshotBytes=pair['common_snapshot_bytes'], commonCostsPhysicalOnce=pair['common_timings']))
    assert count(report['annotation_ns']) == annotation
    assert len({c['id'] for c in arms[POLICIES[0]]}) == len(pairs)
    for metric in ['nodes', 'relations']:
        assert count(report['canonical_'+metric]) == count(report['prefix_'+metric])+sum(c['canonical_'+metric] for c in arms[POLICIES[0]])
        assert count(report['candidate_'+metric]) == sum(c['speculative_'+metric] for c in arms[POLICIES[0]])
    for key in common:
        if key not in ['prefix_ns', 'executor_observed_ns']:
            assert common[key] == sum(p['common_timings'][key] for p in pairs), ('common timing sum', key)
    assert common['executor_observed_ns'] == common['prefix_ns']+sum(p['common_timings']['executor_observed_ns'] for p in pairs)
    totals = report['mode_totals']; assert len(totals) == 2 and sorted(t['policy'] for t in totals) == sorted(POLICIES)
    totals = sorted(totals, key=lambda t: POLICIES.index(t['policy']))
    summaries = []
    for row in totals:
        name = row['policy']; cores = arms[name]
        for base in ['canonical', 'committed', 'fallback']:
            for metric in ['nodes', 'relations']:
                key = base+'_'+metric; assert count(row[key]) == sum(c[key] for c in cores)
        assert row['timings'] == sum_costs(cores); checked_costs(row['timings'])
        assert sum(c['recovery']['accepted_oracle_gross_ns'] for c in cores) <= common['oracle_execute_ns']
        summaries.append(mode_summary(cores, row['timings'], common, annotation, name))
    physical_executor = common['executor_observed_ns']+sum(t['timings']['executor_observed_ns'] for t in totals)+annotation
    physical_audit = common['audit_observed_ns']+sum(t['timings']['audit_observed_ns'] for t in totals)+clone_ns+compare_ns+difference_audit_ns
    assert physical_executor+physical_audit <= count(report['elapsed_ns'])
    buckets = {}
    for category, predicate in [('head', lambda d: d['aheadDistance'] == 0), ('ahead', lambda d: d['aheadDistance'] > 0)]:
        selected = [d['canonical'] for d in differences if predicate(d)]
        buckets[category] = {key: sum(d[key] for d in selected) for key in differences[0]['canonical'] if key != 'new_maximal_size_bins'}
        buckets[category]['new_maximal_size_bins'] = [sum(d['new_maximal_size_bins'][i] for d in selected) for i in range(9)]
    return dict(pairs=len(pairs), modes=summaries, pairComparisons=differences, canonicalGrainByDemand=buckets,
        commonCostsPhysicalOnce=common,
        commonCostsPhysicalOnceByDemand={label: {key: sum(p['common_timings'][key] for p in pairs if (p['variants'][0]['core']['ahead_distance'] > 0) == ahead)
            for key in common} for label, ahead in [('head', False), ('ahead', True)]},
        prefixOutsidePairedTurnsNs=common['prefix_ns'],
        annotationNs=annotation, comparisonCloneNs=clone_ns, differenceAuditNs=difference_audit_ns,
        peakCommonShadowSnapshotBytes=max(p['common_snapshot_bytes'] for p in pairs),
        comparisonCloneBytes=clone_bytes, peakComparisonCloneBytes=max(p['comparison_clone_bytes'] for p in pairs), inputCompareNs=compare_ns,
        consumerClassRows=['no-proof', 'full-inventory-prefix', 'proper-prefix'], orderDepthRows=['requested-depth-1', 'requested-depth-2', 'other'],
        physicalExecutorObservedNs=physical_executor, physicalAuditObservedNs=physical_audit,
        unclassifiedElapsedNs=report['elapsed_ns']-physical_executor-physical_audit,
        prefixNodes=report['prefix_nodes'], prefixRelations=report['prefix_relations'],
        canonicalNodes=report['canonical_nodes'], canonicalRelations=report['canonical_relations'],
        speculativeNodes=report['candidate_nodes'], speculativeRelations=report['candidate_relations'],
        peakQueueForestBytes=report['peak_queue_forest_bytes'],
        counterfactualScope='Only the first rejected ordinary-order operation is classified. Suffix-only does not prove the remainder of a certificate would pass; actual accepted ranges come from the separate policy replay.',
        rollbackEvidence='private-stage source ownership plus focused before/after controls; rollback_unchanged is a construction invariant, not an independently measured runtime check for every rejection',
        sharedStateAuditBoundary='local oracle outputs/N/R and root-candidate final shared state; transient wrong writes later overwritten may escape the independent audit',
        limitations='Gross new canonical maximal ranges can contain complete-order accepted descendants. Signed net committed credit and exact newly covered canonical intervals are separate. Oracle gross minus descendant hooks is an instrumented wall proxy, not clean CPU saved. Shared costs occur once physically; standalone per-policy proxies reuse common costs and add annotation only for consumed-prefix. Nested consumer/record populations are not additive native work. No parallel speedup or per-rejection full-state audit is claimed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-consumed-prefix-collection-v1' and result['complete'] and result['failure'] is None
    expected = [dict(case=c, queue_depth=2, repeat=1) for c in ['profile-08', 'profile-35']]
    assert plan['schedule'] == expected and len(result['runs']) == 2
    assert plan['nativeCpu'] == 14 and plan['helperAffinity'] == sorted(HELPERS) and plan['quietSiblings'] == [7, 15]
    assert plan['limits'] == dict(perLifeSeconds=180, streamSeconds=900, addressSpaceBytes=AS_BYTES, stdoutBytesPerCase=OUTPUT_BYTES)
    chosen = policy(base/'policy.json')
    assert chosen == plan['policy'] == policy(Path(plan['policyPath']))
    assert sha(base/'policy.json') == sha(plan['policyPath']) == plan['policySha256']
    hashes = plan['inputSha256']
    required = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']]
    required += [BASE_HELPER, *FROZEN_TOOLS, ACCOUNT, SPEC/'workloads.json', Path(plan['policyPath'])]
    assert all(str(path) in hashes for path in required)
    for path, digest in hashes.items():
        assert sha(path) == digest
    receipt = admit(Path(plan['build'])); image = Path(plan['binary'])
    assert receipt['baselineBefore'] == plan['baseline'] == baseline()
    assert receipt['sourceBefore'] == plan['sourcePins'] == snapshot(Path(receipt['crate']))
    assert receipt['binary'] == str(image) and receipt['binarySha256'] == plan['binarySha256'] == sha(image)
    assert 0 < result['endMonotonicNs']-result['startMonotonicNs'] <= 900*10**9
    rows, pids = [], set(); previous = result['startMonotonicNs']
    for i, (step, row) in enumerate(zip(expected, result['runs'])):
        assert all(row[key] == value for key, value in step.items())
        directory = base/f'{i:02d}-{step["case"]}-q2'; assert row['directory'] == str(directory)
        input_path = materialization(step['case']); assert str(input_path) in hashes
        options = ['--input', str(input_path), *chosen['driverOptions']]
        native = native_receipt(directory, image, options, hashes)
        command = [native['python_executable'], str(ACCOUNT), '--engine', str(image),
                   '--record', str(directory/'native.json'), '--known-single-process', *options]
        assert read(directory/'launch.json') == dict(argv=command, nativeArgv=[str(image), *options], step=step,
            policySha256=plan['policySha256'], addressSpaceBytes=AS_BYTES, stdoutBytes=OUTPUT_BYTES)
        terminal = read(directory/'terminal.json')
        assert terminal['pid'] == native['supervisor_pid'] == row['supervisorPid']
        assert terminal['exit'] == 0 and terminal['cleanup'] is None
        assert previous <= terminal['startMonotonicNs'] <= native['start_monotonic_ns'] < native['reaped_monotonic_ns'] <= terminal['endMonotonicNs'] <= result['endMonotonicNs']
        assert native['wall_ns'] <= 180*10**9
        assert row['nativePid'] == native['native_pid'] and row['wholeCpuSeconds'] == native['total_cpu_s']
        assert row['rssKiB'] == native['maxrss_linux_kib'] and row['nativeWallNs'] == native['wall_ns']
        assert row['controllerWallNs'] == terminal['endMonotonicNs']-terminal['startMonotonicNs']
        assert set(row['sha256']) == {'launch.json', 'terminal.json', 'native.json', 'stdout', 'stderr'}
        for name, digest in row['sha256'].items():
            assert sha(directory/name) == digest
        assert (directory/'stderr').read_bytes() == b'' and 0 < (directory/'stdout').stat().st_size <= OUTPUT_BYTES
        report = read(directory/'stdout'); assert report['processId'] == native['native_pid']
        summary = audit_report(report, chosen)
        rows.append(dict(**step, counts=summary,
            wholeNative=dict(cpuSeconds=row['wholeCpuSeconds'], rssKiB=row['rssKiB'], wallNs=row['nativeWallNs']),
            reportSha256=sha(directory/'stdout')))
        previous = terminal['endMonotonicNs']; pids.add(native['native_pid'])
    assert len(pids) == 2
    output = dict(complete=True, nativeLives=2, serialSimulations=True, standardReplayClaim=False,
        rows=rows, raw=str(base), rawSha256={n: sha(base/n) for n in ['plan.json', 'result.json', 'policy.json', 'proc-stat-before', 'proc-stat-after']},
        reconcilerSha256=sha(Path(__file__)),
        rollbackEvidence='source ownership and focused before/after controls; no independent per-rejection runtime rollback audit',
        sharedStateAuditBoundary='root-candidate final state only; local checks cover outputs/N/R, with a remaining transient overwritten-effect assurance limit',
        scope='Fixed-completion NoHost/rnd0/inline serial recovery feasibility, not parallel execution or ordinary wire qualification. Whole native CPU includes speculative and audit work; point placement is not continuous isolation.')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print('reconciled 2 paired consumed-prefix recovery simulations', flush=True)


if __name__ == '__main__':
    main()
