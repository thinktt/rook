#!/usr/bin/env python3
"""Independent frozen raw replay/wait4/placement audit; no native execution."""
import argparse
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
from common import (HERE, ROOT, USABLE, ORIGINAL, ACCOUNT, SPEC, HELPERS,
                    SERIAL_SHA, PREVIOUS_SHA, SERIAL_BUILD, PREVIOUS_BUILD,
                    audit, audit_placement, native_receipt, admission, guest_ticks, read, sha)

NAMES = ['serial1', 'previous2', 'cleaned1', 'cleaned2']
SMALL_CASES = ['profile-35', 'profile-08', 'profile-04', 'profile-43']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def dist(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-configured-full-pgo-v1'
    assert result['complete'] and result['failure'] is None and result['automaticExtension'] is False
    assert plan['study'] in ['four-case', 'original54']
    full = plan['study'] == 'original54'
    cases = [row['id'] for row in read(SPEC/'workloads.json')['cases']] if full else SMALL_CASES
    assert not full or len(cases) == len(set(cases)) == 54
    expected = []
    for index, case in enumerate(cases):
        if full:
            order = NAMES[index % 4:]+NAMES[:index % 4]
            expected += [dict(case=case, variant=n, warmup=False, repeat=1) for n in order]
        else:
            expected += [dict(case=case, variant=n, warmup=True, repeat=0) for n in NAMES]
            for repeat in range(3):
                order = NAMES[repeat:]+NAMES[:repeat]
                expected += [dict(case=case, variant=n, warmup=False, repeat=repeat+1) for n in order]
    count = 216 if full else 64
    assert len(expected) == len(result['runs']) == count and plan['schedule'] == expected
    assert plan['cases'] == cases and plan['idleVariants'] == ([] if full else NAMES)
    assert plan['helperAffinity'] == sorted(HELPERS) and plan['idleOwnedSiblings'] == [7, 15]
    assert plan['coordinatorCpu'] == 14 and plan['workerCpu'] == 6 and plan['nativePreExecAffinity'] == [6, 14]
    assert plan['limits'] == dict(perLifeSeconds=180, totalSeconds=1800,
                                 supervisorPlacementSeconds=10, inputGateSeconds=12)
    hashes = plan['inputSha256']
    required = [HERE/n for n in ['collect.py', 'reconcile.py', 'common.py']]
    required += [USABLE/n for n in ['common.py', 'collect.py', 'reconcile.py',
                                    'account_threads.py', 'placement_gate.mjs', 'tools/tap_wire.mjs']]
    required += [ORIGINAL/n for n in ['train.py', 'reconcile.py']]
    required += [ROOT/'tools/tap_wire.mjs', ROOT/'tools/compare_ordinary.py',
                 SPEC/'replay-check.mjs', SPEC/'benchmark.mjs', SPEC/'workloads.json', SPEC/'replay-oracle.json',
                 SERIAL_BUILD/'receipt.json', PREVIOUS_BUILD/'receipt.json']
    assert all(str(path) in hashes for path in required)
    for path, digest in hashes.items():
        assert sha(Path(path)) == digest
    modes = plan['variants']
    assert list(modes) == NAMES
    serial, previous, candidate = (Path(modes[n]['path']) for n in ['serial1', 'previous2', 'cleaned1'])
    assert sha(serial) == SERIAL_SHA and sha(previous) == PREVIOUS_SHA
    assert all(str(p) in hashes for p in [serial, previous, candidate])
    assert modes['serial1'] == dict(path=str(serial), budget=1, options=[])
    assert modes['previous2'] == dict(path=str(previous), budget=2, options=['--research-threads=2'])
    assert modes['cleaned1'] == dict(path=str(candidate), budget=1, options=['--threads=1'])
    assert modes['cleaned2'] == dict(path=str(candidate), budget=2, options=['--threads=2'])
    build = Path(plan['build'])
    receipt, effective, compatibility = admission(build, serial, previous, candidate)
    assert plan['effectiveRustcOptions'] == effective and plan['preservedArtifacts'] == compatibility
    # The original PGO admission verifies current/frozen source, own training
    # source/profile identity and the effective production compiler/ExtTSP flags.
    assert str(build/'receipt.json') in hashes and str(build/'build.stderr') in hashes
    assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged']
    assert str(Path(receipt['pgo']['profile'])) in hashes
    assert str(Path(receipt['pgo']['training_record'])) in hashes
    for name, digest in receipt['source_sha256_before'].items():
        assert hashes[str(build/'source-before'/name)] == digest
    assert 0 < result['streamEndMonotonicNs']-result['streamStartMonotonicNs'] <= 1800*10**9
    posts, prior_end = 0, result['streamStartMonotonicNs']
    pids = set()
    for i, (step, row) in enumerate(zip(expected, result['runs'])):
        v = modes[step['variant']]
        directory = base/f'{i:03d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        native, n = audit.lifetime(directory, row, step, Path(v['path']), v['budget'], v['options'], hashes)
        assert row['placement'] == audit_placement(directory, native, hashes)
        assert prior_end <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= result['streamEndMonotonicNs']
        assert native['wall_ns'] <= 180*10**9
        prior_end = row['controllerEndMonotonicNs']
        pids.add(native['native_pid']); posts += n
    assert len(pids) == count and len(result['idle']) == (0 if full else 4)
    for name, row in zip([] if full else NAMES, result['idle']):
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
        assert row['tickHz'] == read(base/f'000-{SMALL_CASES[0]}-serial1-r0'/'tap-config.json')['tickHz']
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
    assert len(pids) == count+(0 if full else 4)
    summaries = []
    for case in cases:
        for name in NAMES:
            rows = [row for row in result['runs'] if row['case'] == case and row['variant'] == name and not row['warmup']]
            assert len(rows) == (1 if full else 3)
            summaries.append(dict(case=case, variant=name, **{k: dist([row[k] for row in rows]) for k in METRICS}))
    assert summaries == result['summaries']
    by = {(row['case'], row['variant']): row for row in summaries}
    comparisons = []
    for case in cases:
        comparisons.append(dict(case=case, **{name: dict(
            searchWallVsSerial1=by[case, name]['searchWallNs']['median']/by[case, 'serial1']['searchWallNs']['median'],
            wholeCpuVsSerial1=by[case, name]['wholeCpuSeconds']['median']/by[case, 'serial1']['wholeCpuSeconds']['median'])
            for name in NAMES[1:]},
            cleaned2VsPrevious2SearchWall=by[case, 'cleaned2']['searchWallNs']['median']/by[case, 'previous2']['searchWallNs']['median'],
            cleaned2VsCleaned1SearchWall=by[case, 'cleaned2']['searchWallNs']['median']/by[case, 'cleaned1']['searchWallNs']['median'],
            cleaned2VsPrevious2WholeCpu=by[case, 'cleaned2']['wholeCpuSeconds']['median']/by[case, 'previous2']['wholeCpuSeconds']['median']))
    sums = {name: {metric: sum(by[case, name][metric]['median'] for case in cases)
                  for metric in METRICS[:3]} for name in NAMES}
    before, after = guest_ticks(base/'proc-stat-before'), guest_ticks(base/'proc-stat-after')
    assert set(before) == set(after) == {'cpu6', 'cpu7', 'cpu14', 'cpu15'}
    deltas = {cpu: [y-x for x, y in zip(before[cpu], after[cpu])] for cpu in before}
    assert all(len(before[cpu]) == len(after[cpu]) and all(x >= 0 for x in deltas[cpu]) for cpu in before)
    output = dict(complete=True, study=plan['study'], replayLives=count,
                  measured=216 if full else 48, warmups=0 if full else 16, idleProcesses=0 if full else 4,
                  orderedPosts=posts, comparisons=comparisons, summedMedians=sums,
                  summaries=summaries, idle=result['idle'], guestCpuTickDeltas=deltas,
                  guestCpuTickFieldOrder='user nice system idle iowait irq softirq steal guest guest_nice',
                  raw=str(base), rawSha256={n: sha(base/n) for n in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after']},
                  reconcilerSha256=sha(Path(__file__)), automaticExtension=False,
                  scope='own-PGO research; complete native all-thread CPU/RSS and tap search wall; configured before first-input external TID placement; point masks/guest ticks do not prove host exclusivity; stdin capture excludes end(data) cleanup; no numerical gate/automatic extension/qualification/adoption')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({k: output[k] for k in ['complete', 'study', 'replayLives', 'orderedPosts', 'summedMedians']}, indent=2))


if __name__ == '__main__':
    main()
