#!/usr/bin/env python3
"""Independent raw replay/wait4/placement audit; launches no native process."""
import argparse
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
from common import (HERE, ROOT, ORIGINAL, ACCOUNT, SPEC, HELPERS, CONTROL_SHA,
                    audit, admission, audit_placement, native_receipt, read, sha)

CASES = ['profile-35', 'profile-08', 'profile-04', 'profile-43']
NAMES = ['control', 'cleaned1', 'cleaned2']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def dist(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def guest_ticks(path):
    return {items[0]: [int(x) for x in items[1:]] for line in path.read_text().splitlines()
            if (items := line.split()) and items[0] in ['cpu6', 'cpu7', 'cpu14', 'cpu15']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-usable-full-generic-v1' and result['complete'] and result['failure'] is None
    expected = []
    for case in CASES:
        expected += [dict(case=case, variant=n, warmup=True, repeat=0) for n in NAMES]
        for repeat in range(3):
            order = NAMES[repeat:]+NAMES[:repeat]
            expected += [dict(case=case, variant=n, warmup=False, repeat=repeat+1) for n in order]
    assert len(expected) == len(result['runs']) == 48 and plan['schedule'] == expected
    assert plan['helperAffinity'] == sorted(HELPERS) and plan['idleOwnedSiblings'] == [7, 15]
    assert plan['coordinatorCpu'] == 14 and plan['workerCpu'] == 6 and plan['nativePreExecAffinity'] == [6, 14]
    assert plan['limits'] == dict(perLifeSeconds=180, totalSeconds=1800,
                                 supervisorPlacementSeconds=10, inputGateSeconds=12)
    hashes = plan['inputSha256']
    required = [HERE/n for n in ['collect.py', 'reconcile.py', 'common.py', 'account_threads.py',
                                 'placement_gate.mjs', 'tools/tap_wire.mjs']]
    required += [ORIGINAL/n for n in ['train.py', 'collect.py', 'reconcile.py']]
    required += [HERE.parent/'reversed-full/collect.py', ROOT/'tools/tap_wire.mjs',
                 ROOT/'tools/compare_ordinary.py', SPEC/'replay-check.mjs', SPEC/'benchmark.mjs',
                 SPEC/'workloads.json', SPEC/'replay-oracle.json']
    assert all(str(path) in hashes for path in required)
    for path, digest in hashes.items():
        assert sha(Path(path)) == digest
    modes = plan['variants']
    assert list(modes) == NAMES
    control, candidate = Path(modes['control']['path']), Path(modes['cleaned1']['path'])
    assert sha(control) == CONTROL_SHA and str(control) in hashes and str(candidate) in hashes
    assert modes['control'] == dict(path=str(control), budget=2, options=['--research-threads=2'])
    assert modes['cleaned1'] == dict(path=str(candidate), budget=1, options=['--threads=1'])
    assert modes['cleaned2'] == dict(path=str(candidate), budget=2, options=['--threads=2'])
    build = Path(plan['build'])
    receipt = admission(build, control, candidate)
    assert str(build/'receipt.json') in hashes and str(build/'build.stderr') in hashes
    assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged']
    assert receipt['cargo_config_unchanged']
    for name, digest in receipt['source_sha256_before'].items():
        path = build/'source-before'/name
        assert hashes[str(path)] == digest
    assert 0 < result['streamEndMonotonicNs']-result['streamStartMonotonicNs'] <= 1800*10**9
    posts, prior_end = 0, result['streamStartMonotonicNs']
    pids = set()
    for i, (step, row) in enumerate(zip(expected, result['runs'])):
        v = modes[step['variant']]
        directory = base/f'{i:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        native, count = audit.lifetime(directory, row, step, Path(v['path']), v['budget'], v['options'], hashes)
        assert row['placement'] == audit_placement(directory, native, hashes)
        assert prior_end <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= result['streamEndMonotonicNs']
        # The frozen collector enforces180s around its comparator. This outer
        # row also includes collection/audit overhead, so only native wall is
        # independently bounded here; no invented controller-boundary claim.
        assert native['wall_ns'] <= 180*10**9
        prior_end = row['controllerEndMonotonicNs']
        pids.add(native['native_pid']); posts += count
    assert len(pids) == 48 and len(result['idle']) == 3
    for name, row in zip(NAMES, result['idle']):
        assert row['variant'] == name
        directory, v = base/('idle-'+name), modes[name]
        assert read(directory/'probe.json') == row
        native = native_receipt(directory/'native.json', Path(v['path']), v['budget'], v['options'], hashes)
        assert row['nativePid'] == native['native_pid'] and row['supervisorPid'] == native['supervisor_pid']
        assert read(directory/'launch.json') == dict(argv=[native['python_executable'], str(ACCOUNT),
            '--engine', v['path'], '--record', str(directory/'native.json'),
            '--known-single-process', '--thread-budget', str(v['budget']), *v['options']],
            variant=name, kind='startup-idle-shutdown')
        assert row['wholeCpuSeconds'] == native['total_cpu_s'] and row['wholeWallNs'] == native['wall_ns']
        assert row['rssKiB'] == native['maxrss_linux_kib']
        assert row['placement'] == audit_placement(directory, native, hashes)
        assert row['idleCpuTicks'] == row['shutdownStartCpuTicks']-row['startupCpuTicks'] >= 0
        assert row['tickHz'] == read(next(base.glob('*-r0'))/'tap-config.json')['tickHz']
        assert row['idleCpuSeconds'] == row['idleCpuTicks']/row['tickHz']
        assert row['idleNs'] == row['idleEndMonotonicNs']-row['idleStartMonotonicNs'] >= 250_000_000
        assert prior_end <= native['start_monotonic_ns'] < row['idleStartMonotonicNs'] < row['idleEndMonotonicNs'] < native['reaped_monotonic_ns'] <= result['streamEndMonotonicNs']
        assert row['startupReplyNs'] > 0 and row['shutdownSupervisorNs'] > 0
        assert (directory/'stdin.raw').read_bytes() == b'cm_parm\nquit\n'
        assert (directory/'stdout.raw').read_bytes() == b'cm_parm\n' and (directory/'stderr').read_bytes() == b''
        assert set(row['sha256']) == {'launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr'}
        for path, digest in row['sha256'].items():
            assert sha(directory/path) == digest
        prior_end = native['reaped_monotonic_ns']
        pids.add(native['native_pid'])
    assert len(pids) == 51
    summaries = []
    for case in CASES:
        for name in NAMES:
            rows = [row for row in result['runs'] if row['case'] == case and row['variant'] == name and not row['warmup']]
            assert len(rows) == 3
            summaries.append(dict(case=case, variant=name, **{k: dist([row[k] for row in rows]) for k in METRICS}))
    assert summaries == result['summaries']
    by = {(row['case'], row['variant']): row for row in summaries}
    comparisons = []
    for case in CASES:
        comparisons.append(dict(case=case, **{name: dict(
            searchWallVsControl=by[case, name]['searchWallNs']['median']/by[case, 'control']['searchWallNs']['median'],
            wholeCpuVsControl=by[case, name]['wholeCpuSeconds']['median']/by[case, 'control']['wholeCpuSeconds']['median'])
            for name in NAMES[1:]},
            cleaned2VsCleaned1SearchWall=by[case, 'cleaned2']['searchWallNs']['median']/by[case, 'cleaned1']['searchWallNs']['median']))
    sums = {name: {metric: sum(by[case, name][metric]['median'] for case in CASES)
                  for metric in METRICS[:3]} for name in NAMES}
    before, after = guest_ticks(base/'proc-stat-before'), guest_ticks(base/'proc-stat-after')
    assert set(before) == set(after) == {'cpu6', 'cpu7', 'cpu14', 'cpu15'}
    deltas = {cpu: [y-x for x, y in zip(before[cpu], after[cpu])] for cpu in before}
    assert all(len(before[cpu]) == len(after[cpu]) and all(x >= 0 for x in deltas[cpu]) for cpu in before)
    output = dict(complete=True, replayLives=48, measured=36, warmups=12, idleProcesses=3,
                  orderedPosts=posts, comparisons=comparisons, summedMedians=sums,
                  summaries=summaries, idle=result['idle'], guestCpuTickDeltas=deltas,
                  guestCpuTickFieldOrder='user nice system idle iowait irq softirq steal guest guest_nice',
                  raw=str(base), rawSha256={n: sha(base/n) for n in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after']},
                  reconcilerSha256=sha(Path(__file__)),
                  scope='four-case generic; direct native all-thread wait4; first input externally gated after TID placement; point placement/guest ticks do not prove continuous host exclusivity; captured stdin excludes end(data) cleanup; no accepted-serial comparison/PGO/qualification/adoption')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({k: output[k] for k in ['complete', 'replayLives', 'orderedPosts', 'summedMedians', 'comparisons']}, indent=2))


if __name__ == '__main__':
    main()
