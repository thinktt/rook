#!/usr/bin/env python3
"""Independent count partitions, original raw replay and native placement audit."""
import argparse
import collections
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, FEATURE, admit, baseline, load_usable, read, sha, snapshot

THRESHOLDS = [32, 128, 512, 2048, 8192]
EDGES = ['root', 'ordinary-main', 'null', 'iio', 'mate-q', 'q-main', 'other']
GROUPS = ['ordinary-main', 'iio-pass', 'mate-q', 'q-main']
REASONS = ['draw', 'tt', 'fast', 'full-bound', 'threat', 'null', 'terminal', 'main-complete',
           'q-draw', 'q-max-ply', 'q-static', 'q-empty', 'q-check-bound', 'q-recurse', 'stopped', 'unfinished']
MAIN_CLASSES = ['all-direct-q-full-window-no-retry-no-tail-iio', 'all-direct-q-other',
                'all-ordinary', 'mixed', 'no-demand']


def natural(value):
    assert type(value) is int and 0 <= value <= 2**64-1
    return value


def vec(value, size):
    assert type(value) is list and len(value) == size
    return [natural(v) for v in value]


def plus(*values):
    return [sum(xs) for xs in zip(*values)] if values else [0]*5


def sum_vec(values):
    return plus(*list(values))


def hist(value, complete=None, partial=None, nodes=None):
    assert len(value) == 2
    rows = [vec(row, 9) for row in value]
    if complete is not None:
        assert sum(rows[0]) == complete and sum(rows[1]) == partial
    if nodes is not None:
        lower = [0, 1, 2, 8, 32, 128, 512, 2048, 8192]
        upper = [0, 1, 7, 31, 127, 511, 2047, 8191]
        counts = [sum(xs) for xs in zip(*rows)]
        assert sum(n*b for n, b in zip(counts, lower)) <= nodes
        if counts[-1] == 0:
            assert nodes <= sum(n*b for n, b in zip(counts, upper))
    return rows


def handoff_widths(row, entered):
    widths = vec(row['handoffFutureWidths'], 6)
    assert sum(widths) == entered
    for k in range(1, 6):
        assert sum(widths[k:]) <= sum(row['futureWidths'][k:])
    a, b, na, nb = (natural(row[k]) for k in ['handoffCurrentFuture3', 'handoffCurrentFuture7',
        'handoffCurrentFuture3NoTailIio', 'handoffCurrentFuture7NoTailIio'])
    assert b <= a <= row['substantialCurrentFuture3'] and b <= row['substantialCurrentFuture7']
    assert a <= sum(widths[3:]) and b <= widths[5]
    assert na <= a and nb <= min(na, b)


def audit_census(report):
    assert report['schema'] == 'rook2-branch-work-census-v1'
    assert report['overflow'] is False and report['accountingFailures'] == 0
    assert report['counterOrder'] == ['N', 'R', 'FULL', 'FAST', 'map']
    total = vec(report['totalEpochWork'], 5)
    assert total == vec(report['forestWork'], 5) == vec(report['exclusiveWork'], 5)
    assert report['nativeBoundaryCount'] == 1
    native = vec(report['nativeBoundaryWork'], 5)
    assert native[:2] == total[:2] and native[2:] == [0, 0, 0]
    process = vec(report['processActualDemand'], 5)
    assert process[:2] == [0, 0] and all(p >= n for p, n in zip(process[2:], total[2:]))
    outside = vec(report['outsideEpochDemand'], 5)
    assert outside[:2] == [0, 0] and outside[2:] == [p-n for p, n in zip(process[2:], total[2:])]
    assert [row['ply'] for row in report['cuts']] == [0, 2, 4]
    for row in report['cuts']:
        assert plus(vec(row['exclusivePrefix'], 5), vec(row['inclusiveBoundary'], 5)) == total
    assert report['epochRowsSkipped'] == 0
    assert len(report['epochs']) == report['epochCount'] > 0
    for i, epoch in enumerate(report['epochs']):
        assert epoch['ordinal'] == i+1
        assert vec(epoch['work'], 5) == vec(epoch['forest'], 5) == vec(epoch['exclusive'], 5)
        assert natural(epoch['roots']) == natural(epoch['completeRoots'])+natural(epoch['partialRoots'])
    assert sum_vec(e['work'] for e in report['epochs']) == total
    cohorts = report['cohorts']
    assert [(r['kind'], r['exit']) for r in cohorts] == [(k, e) for k in ['ordinary', 'q'] for e in REASONS]
    for row in cohorts:
        c = row['counts']; calls, complete, partial = (natural(c[k]) for k in ['calls', 'complete', 'partial'])
        assert calls == complete+partial
        if row['exit'] == 'unfinished':
            assert calls == 0, 'a normal return lacks an exit-reason hook'
        inclusive, exclusive = vec(c['inclusive'], 5), vec(c['exclusive'], 5)
        assert all(a >= b for a, b in zip(inclusive, exclusive)) and exclusive[0] <= calls
        hist(c['sizeHistCompletePartial'], complete, partial, inclusive[0])
        assert sum(vec(c['depthBins'], 6)) == calls
        assert len(c['fullByRecursiveChildDemand']) == 2
        demand = [vec(x, 2) for x in c['fullByRecursiveChildDemand']]
        assert sum(map(sum, demand)) == calls and sum(demand[1]) <= exclusive[2]
        assert (sum(demand[1]) == 0) == (exclusive[2] == 0)
        assert natural(c['admissionZero']) <= calls and natural(c['creditedStop']) <= partial
        assert natural(c['checked'])+natural(c['checkUnknown']) <= calls
    assert sum_vec(c['counts']['exclusive'] for c in cohorts) == total
    edges = report['edges']
    assert [(r['incoming'], r['callee']) for r in edges] == [(e, k) for e in EDGES for k in ['ordinary', 'q']]
    for edge in edges:
        calls = natural(edge['calls']); inclusive = vec(edge['inclusive'], 5)
        h = hist(edge['sizeHistCompletePartial'], nodes=inclusive[0])
        assert sum(map(sum, h)) == calls and sum(vec(edge['demandRFullMapBits'], 8)) == calls
        assert natural(edge['handoffs']) <= calls
    for kind in ['ordinary', 'q']:
        cs = [c['counts'] for c in cohorts if c['kind'] == kind]
        es = [e for e in edges if e['callee'] == kind]
        assert sum(c['calls'] for c in cs) == sum(e['calls'] for e in es)
        assert sum_vec(c['inclusive'] for c in cs) == sum_vec(e['inclusive'] for e in es)
        for part in range(2):
            assert [sum(c['sizeHistCompletePartial'][part][i] for c in cs) for i in range(9)] == [sum(e['sizeHistCompletePartial'][part][i] for e in es) for i in range(9)]
    roots = [e for e in edges if e['incoming'] == 'root']
    assert sum_vec(e['inclusive'] for e in roots) == total
    assert sum(e['calls'] for e in roots) == sum(e['roots'] for e in report['epochs'])
    assert report['thresholds'] == THRESHOLDS and report['widthBuckets'] == ['0', '1', '2', '3', '4-6', '7+']
    assert report['skipReasons'] == ['q-depth', 'q-initial-eligibility', 'q-not-checking', 'q-many-replies',
                                     'q-unsafe', 'ordinary-frontier', 'mate-nonordinary', 'mate-not-checking']
    groups = report['groups']; assert [g['kind'] for g in groups] == GROUPS
    for group in groups:
        for key in ['groups', 'complete', 'partial', 'inventory', 'examined', 'entered', 'retries',
                    'untouched', 'withTail', 'stableTailWindows', 'sameFirstWindowTasks', 'changedFirstWindowTasks',
                    'sampleSelected', 'sampleSelectedComplete', 'nonEmptyGroups',
                    'ordinaryAttempts', 'qAttempts', 'handoffAttempts', 'retriedTasks', 'groupsWithTailIio']:
            natural(group[key])
        assert group['groups'] == group['complete']+group['partial']
        assert group['inventory'] == group['examined']+group['untouched']
        assert group['examined'] == group['entered']+sum(vec(group['skips'], 8))
        assert group['nonEmptyGroups'] <= group['groups'] and group['withTail'] <= group['nonEmptyGroups']
        assert group['stableTailWindows'] <= group['withTail']
        assert group['sameFirstWindowTasks']+group['changedFirstWindowTasks'] == group['entered']-group['nonEmptyGroups']
        assert group['sampleSelectedComplete'] <= min(group['sampleSelected'], group['complete'])
        assert group['ordinaryAttempts']+group['qAttempts'] == group['entered']+group['retries']
        assert group['handoffAttempts'] <= group['qAttempts']
        assert group['retriedTasks'] <= min(group['retries'], group['entered'])
        assert group['groupsWithTailIio'] <= group['groups']
        assert len(group['mainWindowByCallee']) == 2
        matrix = [vec(row, 3) for row in group['mainWindowByCallee']]
        assert sum(map(sum, matrix)) == (group['entered'] if group['kind'] == 'ordinary-main' else 0)
        work = vec(group['inclusiveTaskWork'], 5)
        h = hist(group['childSizeHistCompletePartial'], nodes=work[0]); assert sum(map(sum, h)) == group['entered']
        edge_kind = 'iio' if group['kind'] == 'iio-pass' else group['kind']
        es = [e for e in edges if e['incoming'] == edge_kind]
        assert sum_vec(e['inclusive'] for e in es) == work
        assert sum(e['calls'] for e in es) == group['entered']+group['retries']
        assert sum(e['calls'] for e in es if e['callee'] == 'ordinary') == group['ordinaryAttempts']
        assert sum(e['calls'] for e in es if e['callee'] == 'q') == group['qAttempts']
        assert sum(e['handoffs'] for e in es) == group['handoffAttempts']
        rows = group['thresholdRows']; assert [r['threshold'] for r in rows] == THRESHOLDS
        previous = None
        for row in rows:
            widths = vec(row['futureWidths'], 6); after = vec(row['afterFirstWidths'], 6)
            same = vec(row['afterFirstSameWindowWidths'], 6)
            assert sum(widths) == group['entered'] and sum(after) == sum(same) == group['nonEmptyGroups']
            for tail in range(1, 6):
                assert sum(same[tail:]) <= sum(after[tail:])
                if previous is not None:
                    assert sum(widths[tail:]) <= sum(previous['futureWidths'][tail:])
            a, b, fa, fb = (natural(row[k]) for k in ['substantialCurrentFuture3', 'substantialCurrentFuture7',
                'substantialCurrentFullFuture3', 'substantialCurrentFullFuture7'])
            assert b <= a <= sum(widths[3:]) and b <= widths[5]
            assert fb <= min(fa, b) and fa <= a
            assert natural(row['overlappingMaxFutureNodes']) <= natural(row['overlappingFutureNodes'])
            handoff_widths(row, group['entered'])
            previous = row
    classes = report['mainClasses']; assert [c['class'] for c in classes] == MAIN_CLASSES
    main = groups[0]
    for cls in classes:
        assert natural(cls['groups']) == natural(cls['complete'])+natural(cls['partial'])
        work = vec(cls['inclusiveTaskWork'], 5)
        h = hist(cls['childSizeHistCompletePartial'], nodes=work[0]); assert sum(map(sum, h)) == natural(cls['entered'])
        barriers = vec(cls['barriersScoutRetryTailIioPartial'], 4)
        assert all(b <= cls['groups'] for b in barriers) and barriers[3] == cls['partial']
        assert [r['threshold'] for r in cls['thresholdRows']] == THRESHOLDS
        for row in cls['thresholdRows']:
            assert sum(vec(row['futureWidths'], 6)) == cls['entered']
            after, same = vec(row['afterFirstWidths'], 6), vec(row['afterFirstSameWindowWidths'], 6)
            assert sum(after) == sum(same) <= cls['groups']
            handoff_widths(row, cls['entered'])
        if cls['class'] == MAIN_CLASSES[0]:
            assert cls['partial'] == 0 and barriers == [0, 0, 0, 0]
        if cls['class'] == 'no-demand':
            assert cls['entered'] == 0 and work == [0]*5
    for key in ['groups', 'complete', 'partial', 'entered']:
        assert sum(c[key] for c in classes) == main[key]
    assert sum_vec(c['inclusiveTaskWork'] for c in classes) == main['inclusiveTaskWork']
    for part in range(2):
        assert [sum(c['childSizeHistCompletePartial'][part][i] for c in classes) for i in range(9)] == main['childSizeHistCompletePartial'][part]
    for i, row in enumerate(main['thresholdRows']):
        for key, value in row.items():
            parts = [c['thresholdRows'][i][key] for c in classes]
            if key == 'threshold':
                assert all(part == value for part in parts)
            elif type(value) is list:
                assert [sum(xs) for xs in zip(*parts)] == value
            else:
                assert sum(natural(part) for part in parts) == value
    assert sum(c['barriersScoutRetryTailIioPartial'][2] for c in classes) == main['groupsWithTailIio']
    assert sum(c['barriersScoutRetryTailIioPartial'][3] for c in classes) == main['partial']
    assert report['sampleStride'] == 512 and report['sampleCap'] == 16
    assert sum(g['sampleSelected'] for g in groups) == sum(g['groups'] for g in groups)//512
    samples = report['samples']
    assert report['sampleRetained'] == len(samples) == min(16, sum(g['sampleSelectedComplete'] for g in groups))
    assert natural(report['sampleCompleteSkipped']) == sum(g['sampleSelectedComplete'] for g in groups)-len(samples)
    assert len({g['ordinal'] for g in samples}) == len(samples)
    sampled_by_kind = collections.Counter()
    for sample in samples:
        assert sample['kind'] in GROUPS and 0 < sample['ordinal'] <= sum(g['groups'] for g in groups)
        assert sample['ordinal'] % 512 == 0 and type(sample['checked']) is bool
        assert type(sample['tailIio']) is bool
        assert type(sample['depth']) is int and 0 <= sample['ply'] < 64
        assert 0 <= sample['examined'] <= sample['inventory'] <= 512
        assert sample['examined'] == len(sample['tasks'])+sum(vec(sample['skips'], 8))
        assert len(sample['tasks']) <= 512
        ranks = [task['rank'] for task in sample['tasks']]
        assert ranks == sorted(set(ranks))
        if ranks:
            # IIO tail inventory is count-start, while native ranks retain
            # absolute list indices. They are not local slot numbers.
            assert ranks[-1]-ranks[0] < sample['inventory']
        for task in sample['tasks']:
            assert type(task['complete']) is bool and task['complete']
            assert type(task['rank']) is int and 0 <= task['rank'] < 512 and natural(task['attempts']) >= 1
            assert natural(task['ordinaryAttempts'])+natural(task['qAttempts']) == task['attempts']
            assert natural(task['handoffAttempts']) <= task['qAttempts']
            assert task['fullWindow'] is None or type(task['fullWindow']) is bool
            assert (task['fullWindow'] is not None) == (sample['kind'] == 'ordinary-main')
            assert len(task['window']) == 2 and all(type(v) is int for v in task['window'])
            # Preserve internal transformed/collapsed windows; this census is
            # not a new public request-domain validator.
            assert all(-2**31 <= v < 2**31 for v in task['window'])
            vec(task['work'], 5)
        sampled_by_kind[sample['kind']] += 1
    for g in groups:
        assert sampled_by_kind[g['kind']] <= g['sampleSelectedComplete']
    assert 0 <= report['maxLiveGroups'] <= 192
    assert [(q['incoming'], q['ordinaryHandoff']) for q in report['qRoots']] == [(e, h) for e in EDGES for h in [False, True]]
    for q in report['qRoots']:
        assert type(q['ordinaryHandoff']) is bool
        n, p = natural(q['complete']), natural(q['partial'])
        hist(q['sizeHistCompletePartial'], n, p, sum(vec(q['nodesCompletePartial'], 2)))
        spans = vec(q['idealNodeSpanCompletePartial'], 2)
        assert all(s <= n for s, n in zip(spans, q['nodesCompletePartial']))
    assert sum(sum(q['nodesCompletePartial']) for q in report['qRoots']) == sum(
        c['counts']['exclusive'][0] for c in cohorts if c['kind'] == 'q')
    assert classes[0]['inclusiveTaskWork'][0]+classes[1]['inclusiveTaskWork'][0] <= sum(
        sum(q['nodesCompletePartial']) for q in report['qRoots'])
    return dict(totalEpochWork=total, processActualDemand=process,
                outsideEpochDemand=outside, epochs=report['epochCount'], groups=groups, mainClasses=classes, qRoots=report['qRoots'],
                cohorts=cohorts, cuts=report['cuts'], nativeBoundaryWork=native,
                retainedIllustrations=len(samples),
                limits='All-parent inclusive histograms/widths overlap; each fixed-ply cut is a separate partition. Retrospective demand/windows do not prove independent runnable tasks; Q node span is not CPU span.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json'); usable = load_usable()
    expected = [dict(case=c, variant='count-census', warmup=False, repeat=1) for c in ['profile-35', 'profile-08', 'profile-43']]
    assert plan['schema'] == 'rook2-beyond-two-count-plan-v1' and result['complete'] and result['failure'] is None
    assert plan['schedule'] == expected and len(result['runs']) == 3
    assert plan['budget'] == 2 and plan['options'] == ['--threads=2'] and plan['feature'] == FEATURE
    assert plan['coordinatorCpu'] == 14 and plan['workerCpu'] == 6 and plan['nativePreExecAffinity'] == [6, 14]
    assert plan['helperAffinity'] == sorted(HELPERS) and plan['quietSiblings'] == [7, 15]
    assert plan['limits'] == dict(perLifeSeconds=180, totalSeconds=900, censusBytesPerCase=4*1024*1024)
    assert plan['reportEnvironment'] == 'ROOK2_BRANCH_WORK_CENSUS_REPORT' and plan['reportSchema'] == 'rook2-branch-work-census-v1'
    hashes = plan['inputSha256']
    required = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']]
    required += [HERE.parent/'usable-full'/n for n in ['common.py', 'account_threads.py', 'placement_gate.mjs', 'tools/tap_wire.mjs']]
    required += [HERE.parent/'full-split-production'/n for n in ['train.py', 'reconcile.py']]
    required += [ROOT/'tools/tap_wire.mjs', ROOT/'tools/compare_ordinary.py']
    required += [usable.SPEC/n for n in ['replay-check.mjs', 'benchmark.mjs', 'workloads.json', 'replay-oracle.json']]
    assert all(str(p) in hashes for p in required)
    for path, digest in hashes.items():
        assert sha(path) == digest
    receipt = admit(Path(plan['build'])); image = Path(plan['binary'])
    assert receipt['baselineBefore'] == plan['baseline'] == baseline()
    assert receipt['sourceBefore'] == plan['sourcePins'] == snapshot(Path(plan['crate']))
    assert receipt['binary'] == str(image) and receipt['binarySha256'] == plan['binarySha256'] == sha(image)
    assert 0 < result['streamEndMonotonicNs']-result['streamStartMonotonicNs'] <= 900*10**9
    summaries, posts, pids = [], 0, set(); previous = result['streamStartMonotonicNs']
    for i, (step, row) in enumerate(zip(expected, result['runs'])):
        directory = base/f'{i:02d}-{step["case"]}'
        native, count = usable.audit.lifetime(directory, row, step, image, 2, ['--threads=2'], hashes)
        assert row['placement'] == usable.audit_placement(directory, native, hashes)
        assert previous <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= result['streamEndMonotonicNs']
        assert native['wall_ns'] <= 180*10**9
        previous = row['controllerEndMonotonicNs']; posts += count; pids.add(native['native_pid'])
        path = directory/'census.json'; size = path.stat().st_size
        assert 0 < size <= 4*1024*1024
        assert row['censusReport'] == dict(path=str(path), bytes=size, sha256=sha(path),
            environment={'ROOK2_BRANCH_WORK_CENSUS_REPORT': str(path)})
        census = read(path); assert census['processId'] == native['native_pid']
        summaries.append(dict(case=step['case'], censusSha256=sha(path), counts=audit_census(census),
            instrumentedAccounting={k: row[k] for k in ['wholeCpuSeconds', 'rssKiB', 'searchWallNs', 'wholeWallNs', 'nonSearchWallNs']}))
    assert len(pids) == 3
    output = dict(complete=True, replayLives=3, orderedPosts=posts, summaries=summaries,
                  raw=str(base), rawSha256={n: sha(base/n) for n in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after']},
                  reconcilerSha256=sha(Path(__file__)),
                  scope='Count-only opportunity/dependency discriminator; no performance, independence or reuse claim; original streams and all-thread lifetime accounting verified, point placement is not continuous host isolation')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print(f'reconciled 3 count-only original lives, {posts} ordered posts', flush=True)


if __name__ == '__main__':
    main()
