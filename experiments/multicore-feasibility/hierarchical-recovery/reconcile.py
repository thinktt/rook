#!/usr/bin/env python3
"""Read-only source/native/cap/disjoint-work audit of two serial pilot lives."""
import argparse
import collections
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, BASE_HELPER, baseline, snapshot, admit, sha, read
from collect import ACCOUNT, SPEC, CASES, CAPS, AS_BYTES, OUTPUT_BYTES, policy, materialization


def count(value):
    assert type(value) is int and value >= 0
    return value


COST_FIELDS = ['prefix_ns', 'snapshot_ns', 'recording_setup_ns', 'speculation_ns', 'recording_finalize_ns',
    'canonical_execute_ns', 'oracle_snapshot_ns', 'oracle_execute_ns', 'oracle_compare_ns',
    'oracle_local_ns', 'oracle_entry_ns', 'recovery_hook_ns', 'lookup_ns', 'staging_ns',
    'validation_ns', 'commit_ns', 'native_fallback_estimate_ns']


def costs(value, candidate=True):
    assert set(value) == set(COST_FIELDS+['executor_observed_ns', 'audit_observed_ns'])
    for n in value.values():
        count(n)
    audit_inside = value['oracle_local_ns']+value['oracle_entry_ns']
    assert audit_inside <= value['canonical_execute_ns']
    executor = sum(value[k] for k in ['prefix_ns', 'snapshot_ns', 'recording_setup_ns',
        'speculation_ns', 'recording_finalize_ns', 'canonical_execute_ns'])-audit_inside
    audit = sum(value[k] for k in ['oracle_snapshot_ns', 'oracle_execute_ns', 'oracle_compare_ns'])+audit_inside
    assert value['executor_observed_ns'] == executor and value['audit_observed_ns'] == audit
    assert sum(value[k] for k in ['lookup_ns', 'staging_ns', 'validation_ns', 'commit_ns'])+audit_inside <= value['recovery_hook_ns']
    if candidate:
        assert value['prefix_ns'] == 0
        assert value['native_fallback_estimate_ns'] == max(0, value['canonical_execute_ns']-value['recovery_hook_ns'])


def forest(value, oracle=False):
    for key in ['segments', 'valid_segments', 'metadata_bytes', 'bytes', 'log_events',
                'log_attempted', 'log_bytes', 'recording_hook_ns', 'log_recording_ns']:
        count(value[key])
    assert value['segments'] <= CAPS['oracle_trace_cap' if oracle else 'max_segments']
    assert value['valid_segments'] <= value['segments']
    assert value['metadata_bytes'] <= CAPS['max_forest_bytes']//2
    assert value['log_bytes'] <= CAPS['max_forest_bytes']//2
    assert value['bytes'] == value['metadata_bytes']+value['log_bytes'] <= CAPS['max_forest_bytes']
    assert value['log_events'] <= CAPS['log_events'] and value['log_attempted'] >= value['log_events']
    for key in ['event_overflowed', 'byte_overflowed', 'censored']:
        assert type(value[key]) is bool
    assert value['censored'] == (value['cap_reason'] is not None)
    if value['censored']:
        assert value['cap_reason'] in ['journal-cap', 'segment-cap', 'recorded-node-cap', 'metadata-byte-cap']
    if value['event_overflowed'] or value['byte_overflowed']:
        assert value['censored'] and value['log_attempted'] > value['log_events']
    else:
        assert value['log_attempted'] == value['log_events']
    if value['event_overflowed']:
        assert value['log_events'] == CAPS['log_events']
    if oracle:
        assert value['log_events'] == value['log_attempted'] == value['log_bytes'] == value['log_recording_ns'] == 0
        assert not value['event_overflowed'] and not value['byte_overflowed']


def bin_size(n):
    for i, upper in enumerate([0, 1, 7, 31, 127, 511, 2047, 8191]):
        if n <= upper:
            return i
    return 8


def recovery(candidate):
    r, t = candidate['recovery'], candidate['timings']
    for key in ['lookups', 'entry_candidates', 'entry_mismatches', 'unmatched_calls', 'exact_matches', 'semantic_rejections', 'validation_censored',
                'commits', 'committed_nodes', 'committed_relations', 'censored', 'already_used',
                'touched_groups', 'touched_bytes', 'peak_staging_bytes', 'lookup_ns', 'staging_ns',
                'validation_ns', 'commit_ns', 'audit_local_ns', 'audit_entry_ns',
                'accepted_oracle_gross_ns', 'accepted_oracle_descendant_hooks_ns']:
        count(r[key])
    assert r['fatal_reason'] is None and r['maximal_ranges_disjoint'] is True
    assert r['exact_matches'] == r['semantic_rejections']+r['validation_censored']+r['commits'] <= r['lookups']
    assert r['lookups'] == r['unmatched_calls']+r['exact_matches']+r['censored']
    assert r['lookups'] == candidate['fallback_nodes']+r['commits']
    assert r['entry_candidates'] <= r['entry_mismatches']+r['already_used']+r['exact_matches'] <= r['entry_candidates']+r['lookups']
    assert r['censored'] == (r['lookups'] if candidate['oracle']['censored'] else 0)
    if candidate['oracle']['censored']:
        assert r['commits'] == 0
    for metric in ['nodes', 'relations']:
        assert r['committed_'+metric] == candidate['committed_'+metric]
    assert r['touched_bytes'] == 48*r['touched_groups']
    assert r['touched_groups'] <= r['commits']*CAPS['max_touched_groups']
    status, valid_status = r['segment_status_counts'], r['valid_segment_status_counts']
    assert len(status) == len(valid_status) == 4
    assert all(type(n) is int and n >= 0 for n in status+valid_status)
    assert sum(status) == candidate['forest']['segments']
    assert sum(valid_status) == candidate['forest']['valid_segments']
    assert all(v <= a for v, a in zip(valid_status, status))
    assert r['commits'] <= valid_status[2]
    assert valid_status[1] == status[1] <= r['semantic_rejections']+r['validation_censored']
    assert len(r['matching_depth']) == 64 and len(r['surviving_size']) == 9
    assert all(type(n) is int and n >= 0 for n in r['matching_depth']+r['surviving_size'])
    ranges = r['committed_ranges']; assert len(ranges) == r['commits'] <= candidate['forest']['valid_segments']
    depths, sizes = [0]*64, [0]*9
    for row in ranges:
        assert len(row) == 6 and all(type(v) is int and v >= 0 for v in row)
        begin, end, nodes, relations, ply, oracle_id = row
        assert begin < end <= candidate['forest']['segments']
        assert nodes > 0 and nodes <= CAPS['max_recorded_nodes'] and ply < 64
        assert oracle_id < candidate['oracle']['segments']
        depths[ply] += 1; sizes[bin_size(nodes)] += 1
    ordered = sorted(ranges, key=lambda row: row[0])
    assert all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), 'accepted ancestor/descendant or duplicate range'
    oracle_ids = [row[5] for row in ranges]
    assert oracle_ids == sorted(set(oracle_ids))
    assert sum(row[2] for row in ranges) == candidate['committed_nodes']
    assert sum(row[3] for row in ranges) == candidate['committed_relations']
    assert depths == r['matching_depth'] and sizes == r['surviving_size']
    reasons = r['rejection_reasons']
    assert len({row['reason'] for row in reasons}) == len(reasons)
    assert all(type(row['reason']) is str and row['reason'] and count(row['count']) > 0 for row in reasons)
    assert sum(row['count'] for row in reasons) == r['semantic_rejections']
    censor_reasons = r['censor_reasons']
    assert len({row['reason'] for row in censor_reasons}) == len(censor_reasons)
    assert all(type(row['reason']) is str and row['reason'] and count(row['count']) > 0 for row in censor_reasons)
    assert sum(row['count'] for row in censor_reasons) == r['validation_censored']
    mismatch_reasons = r['entry_mismatch_reasons']
    assert len({row['reason'] for row in mismatch_reasons}) == len(mismatch_reasons)
    assert all(type(row['reason']) is str and row['reason'] and count(row['count']) > 0 for row in mismatch_reasons)
    assert sum(row['count'] for row in mismatch_reasons) == r['entry_mismatches']
    for key in ['lookup_ns', 'staging_ns', 'validation_ns', 'commit_ns']:
        assert r[key] == t[key]
    assert r['audit_local_ns'] == t['oracle_local_ns'] and r['audit_entry_ns'] == t['oracle_entry_ns']
    assert r['accepted_oracle_descendant_hooks_ns'] <= r['accepted_oracle_gross_ns'] <= t['oracle_execute_ns']
    return r['accepted_oracle_gross_ns']-r['accepted_oracle_descendant_hooks_ns']


def native_receipt(directory, image, options, hashes):
    n = read(directory/'native.json')
    assert n['schema'] == 'rook2-native-wait4-v1' and n['known_single_process']
    assert n['failure'] is None and n['exec_error'] is None and n['supervisor_signals'] == []
    assert n['native_wait_status'] == n['native_exit_code'] == 0
    assert n['engine'] == str(image) and n['argv'] == [str(image), *options]
    assert n['engine_sha256_before'] == n['engine_sha256_after'] == sha(image)
    assert n['launcher_sha256'] == hashes[str(ACCOUNT)]
    assert sha(n['python_executable']) == n['python_executable_sha256']
    assert n['inherited_supervisor_affinity'] == n['supervisor_affinity'] == sorted(HELPERS)
    assert n['native_pre_exec'] == dict(pid=n['native_pid'], pgid=n['supervisor_pid'], affinity=[14])
    observed = n['native_post_exec']
    assert observed['path'] == str(image) and observed['pgid'] == n['supervisor_pid']
    assert observed['affinity'] == [14] and observed['tasks'] == [str(n['native_pid'])]
    assert n['wall_ns'] == n['reaped_monotonic_ns']-n['start_monotonic_ns'] > 0
    assert n['total_cpu_s'] == n['user_cpu_s']+n['system_cpu_s'] > 0 and n['maxrss_linux_kib'] > 0
    for pid in [n['native_pid'], n['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists(), 'recorded PID currently live; inspect possible reuse'
    return n


def audit_report(report, chosen):
    assert report['schema'] == chosen['reportSchema'] and report['caps'] == chosen['caps'] == CAPS
    assert report['unsafe_validation'] is False and report['fatal_reason'] is None
    for field in ['zero_randomness', 'fixed_completion', 'no_host', 'inline_full']:
        assert report[field] is True
    candidates = report['candidates']; proxies = []
    assert count(report['restricted_entry_nodes']) >= 25000 and 1 <= report['restricted_depth'] <= 6
    assert 0 < len(candidates) <= 8
    assert report['prefix_nodes'] >= report['restricted_entry_nodes']
    assert count(report['abandoned_speculative_nodes']) == 0
    assert 1 <= report['max_queue_len'] <= 2
    assert count(report['peak_queue_forest_bytes']) <= 2*CAPS['max_forest_bytes']
    assert type(report['incomplete_iteration']) is bool
    assert report['stopped_reason'] == ('tail-candidate-cap' if report['incomplete_iteration'] else 'first-restricted-iteration-complete')
    assert report['completed_depth'] == report['restricted_depth']-int(report['incomplete_iteration'])
    assert len({c['id'] for c in candidates}) == len(candidates)
    for turn, candidate in enumerate(candidates):
        assert candidate['depth'] == report['restricted_depth']
        assert 0 <= count(candidate['ahead_distance']) < 2
        assert candidate['consumed_at_turn'] == turn and candidate['index'] == turn+1
        assert candidate['enqueued_at_turn'] <= turn and candidate['ahead_distance'] == turn-candidate['enqueued_at_turn']
        assert candidate['oracle_match'] is True and candidate['rollback_unchanged'] is True
        assert candidate['unsafe_validation'] is False
        assert count(candidate['completed_passes']) in [1, 2] and count(candidate['snapshot_bytes']) > 0
        for metric in ['nodes', 'relations']:
            canonical = count(candidate['canonical_'+metric])
            committed = count(candidate['committed_'+metric])
            fallback = count(candidate['fallback_'+metric])
            assert count(candidate['speculative_'+metric]) >= committed
            assert canonical == committed+fallback
        assert count(candidate['discarded_speculative_nodes']) == candidate['speculative_nodes']-candidate['committed_nodes']
        forest(candidate['forest']); forest(candidate['oracle'], oracle=True)
        costs(candidate['timings']); proxies.append(recovery(candidate))
    for metric in ['nodes', 'relations']:
        assert count(report['canonical_'+metric]) == count(report['prefix_'+metric])+sum(c['canonical_'+metric] for c in candidates)
        assert count(report['candidate_'+metric]) == sum(c['speculative_'+metric] for c in candidates)
        assert count(report['committed_'+metric]) == sum(c['committed_'+metric] for c in candidates)
        assert count(report['fallback_'+metric]) == sum(c['fallback_'+metric] for c in candidates)
        assert report['canonical_'+metric] == report['prefix_'+metric]+report['committed_'+metric]+report['fallback_'+metric]
    costs(report['timings'], candidate=False)
    for key in COST_FIELDS:
        if key != 'prefix_ns':
            assert report['timings'][key] == sum(c['timings'][key] for c in candidates)
    outer = report['timings']['executor_observed_ns']+report['timings']['audit_observed_ns']
    assert count(report['elapsed_ns']) >= outer
    rejected, censored, mismatched = collections.Counter(), collections.Counter(), collections.Counter()
    for candidate in candidates:
        for row in candidate['recovery']['rejection_reasons']:
            rejected[row['reason']] += row['count']
        for row in candidate['recovery']['censor_reasons']:
            censored[row['reason']] += row['count']
        for row in candidate['recovery']['entry_mismatch_reasons']:
            mismatched[row['reason']] += row['count']
    return dict(candidates=len(candidates), committedNodes=sum(c['committed_nodes'] for c in candidates),
        committedRelations=sum(c['committed_relations'] for c in candidates),
        fallbackNodes=sum(c['fallback_nodes'] for c in candidates),
        fallbackRelations=sum(c['fallback_relations'] for c in candidates),
        aheadCommittedNodes=sum(c['committed_nodes'] for c in candidates if c['ahead_distance'] > 0),
        aheadCommittedRelations=sum(c['committed_relations'] for c in candidates if c['ahead_distance'] > 0),
        headCommittedNodes=sum(c['committed_nodes'] for c in candidates if c['ahead_distance'] == 0),
        headCommittedRelations=sum(c['committed_relations'] for c in candidates if c['ahead_distance'] == 0),
        acceptedOracleGrossMinusDescendantHooksNs=sum(proxies),
        aheadAcceptedOracleGrossMinusDescendantHooksNs=sum(p for c, p in zip(candidates, proxies) if c['ahead_distance'] > 0),
        executorObservedNs=report['timings']['executor_observed_ns'], auditObservedNs=report['timings']['audit_observed_ns'],
        unclassifiedElapsedNs=report['elapsed_ns']-outer,
        speculativeNodes=report['candidate_nodes'], discardedSpeculativeNodes=sum(c['discarded_speculative_nodes'] for c in candidates),
        speculativeRelations=report['candidate_relations'],
        discardedSpeculativeRelations=report['candidate_relations']-report['committed_relations'],
        committedSegments=sum(c['recovery']['commits'] for c in candidates),
        aheadCommittedSegments=sum(c['recovery']['commits'] for c in candidates if c['ahead_distance'] > 0),
        matchingDepth=[sum(c['recovery']['matching_depth'][i] for c in candidates) for i in range(64)],
        survivingSize=[sum(c['recovery']['surviving_size'][i] for c in candidates) for i in range(9)],
        segmentOutcomes={key: sum(c['recovery'][key] for c in candidates) for key in
            ['lookups', 'entry_candidates', 'entry_mismatches', 'unmatched_calls', 'exact_matches', 'semantic_rejections', 'validation_censored', 'commits', 'already_used', 'censored']},
        segmentStatusCounts=[sum(c['recovery']['segment_status_counts'][i] for c in candidates) for i in range(4)],
        validSegmentStatusCounts=[sum(c['recovery']['valid_segment_status_counts'][i] for c in candidates) for i in range(4)],
        segmentStatusScope='nested record populations: untried, attempted-no-commit, consumed-by-maximal-commit, blocked-ancestor; untried does not independently prove canonical no-demand',
        cappedForests=sum(c['forest']['censored'] for c in candidates), cappedOracleTraces=sum(c['oracle']['censored'] for c in candidates),
        forestCapReasons=dict(collections.Counter(c['forest']['cap_reason'] for c in candidates if c['forest']['censored'])),
        touchedGroups=sum(c['recovery']['touched_groups'] for c in candidates), touchedBytes=sum(c['recovery']['touched_bytes'] for c in candidates),
        peakStagingBytes=max(c['recovery']['peak_staging_bytes'] for c in candidates),
        maxShadowSnapshotBytes=max(c['snapshot_bytes'] for c in candidates),
        semanticRejections=dict(rejected), validationCensorReasons=dict(censored), entryMismatchReasons=dict(mismatched), peakQueueForestBytes=report['peak_queue_forest_bytes'],
        costs=report['timings'],
        rollbackEvidence='private-stage source ownership plus focused before/after controls; rollback_unchanged is a construction invariant, not an independently measured runtime check for every rejection',
        sharedStateAuditBoundary='local oracle compares outputs/N/R; shared state is compared at each root-candidate final boundary only; transient effects later overwritten may escape this audit',
        limitations='Accepted ranges are maximal/disjoint. Oracle gross minus measured descendant hooks is an instrumented wall proxy, not clean CPU removed. Recording/recovery subcosts are already inside outer speculation/canonical intervals; forest byte models exclude allocator metadata and other snapshots.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-hierarchical-collection-v1' and result['complete'] and result['failure'] is None
    expected = [dict(case=c, queue_depth=2, repeat=1) for c in ['profile-08', 'profile-35']]
    assert plan['schedule'] == expected and len(result['runs']) == 2
    assert plan['nativeCpu'] == 14 and plan['helperAffinity'] == sorted(HELPERS) and plan['quietSiblings'] == [7, 15]
    assert plan['limits'] == dict(perLifeSeconds=180, streamSeconds=900, addressSpaceBytes=AS_BYTES, stdoutBytesPerCase=OUTPUT_BYTES)
    chosen = policy(base/'policy.json')
    assert chosen == plan['policy'] == policy(Path(plan['policyPath']))
    assert sha(base/'policy.json') == sha(plan['policyPath']) == plan['policySha256']
    hashes = plan['inputSha256']
    required = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']]
    required += [BASE_HELPER, ACCOUNT, SPEC/'workloads.json', Path(plan['policyPath'])]
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
    print('reconciled 2 serial hierarchical recovery simulations', flush=True)


if __name__ == '__main__':
    main()
