#!/usr/bin/env python3
"""Read-only audit of original3+repaired45 replay lives and4 idle probes."""
import argparse
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
from common import (HERE, HELPERS, ACCOUNT, audit, audit_placement, baseline,
                    module, native_receipt, read, sha)
from completion_common import (completion_paths, epoch_binding, failed_startup,
                               inspect)

CASES = ['profile-35', 'profile-08', 'profile-43']
NAMES = ['preserved2', 'inline1', 'current2', 'colors3']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def dist(values):
    return dict(samples=values, median=statistics.median(values), min=min(values), max=max(values))


def housekeeping(path, expected_applies):
    value = read(path)
    assert value['schema'] == 'rook2-colors-three-housekeeping-v1'
    assert value['helperCpus'] == sorted(HELPERS) and value['failure'] is None
    assert len(value['applies']) == expected_applies and value['restored'] is not None
    original = {(row['pid'], row['tid'], row['starttime']): row['affinity'] for row in value['originals']}
    leaders = {(row['pid'], row['starttime']): row['affinity'] for row in value['leaders']}
    assert len(original) == len(value['originals']) and len(leaders) == len(value['leaders'])
    seen = {}
    for event in value['applies']:
        assert event['cpus'] == event['selfAffinity'] == sorted(HELPERS)
        for row in event['selectedTasks']:
            key = (row['pid'], row['tid'], row['starttime'])
            assert row['after'] == sorted(HELPERS)
            if key in seen:
                assert row['before'] == sorted(HELPERS)
            else:
                assert original[key] == row['before']
                seen[key] = row['before']
    assert seen == original
    for row in value['restored']:
        key = (row['pid'], row['tid'], row['starttime'])
        if key in original:
            assert not row['inheritedNewThread'] and row['restored'] == original[key]
        else:
            masks = [mask for (pid, _), mask in leaders.items() if pid == row['pid']]
            assert len(masks) == 1 and row['inheritedNewThread'] and row['restored'] == masks[0]
    assert value['postRestoreSelfAffinity'] == sorted(HELPERS)
    return dict(applies=expected_applies, selectedOriginalTasks=len(original),
                restoredTasks=len(value['restored']), sha256=sha(path))


def ticks(directory):
    cpus = {'cpu4', 'cpu5', 'cpu6', 'cpu7', 'cpu14', 'cpu15'}
    def read_ticks(path):
        return {fields[0]: [int(x) for x in fields[1:]] for line in path.read_text().splitlines()
                if (fields := line.split()) and fields[0] in cpus}
    before, after = read_ticks(directory/'proc-stat-before'), read_ticks(directory/'proc-stat-after')
    assert set(before) == set(after) == cpus
    result = {cpu: [y-x for x, y in zip(before[cpu], after[cpu])] for cpu in cpus}
    assert all(len(before[cpu]) == len(after[cpu]) and all(x >= 0 for x in result[cpu]) for cpu in cpus)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-colors-three-completion-v1'
    assert result['complete'] and result['failure'] is None
    context = inspect(Path(plan['original']))
    original, old_plan, old = context['original'], context['plan'], context['old']
    assert plan['originalPlanSha256'] == sha(original/'pilot/plan.json')
    assert plan['originalPipelineSha256'] == sha(original/'pipeline.json')
    assert plan['originalResultSha256'] == sha(original/'pilot/result.json')
    assert plan['frozenManifest'] == str(context['frozen']/'manifest.json')
    assert plan['frozenManifestSha256'] == sha(context['frozen']/'manifest.json')
    assert plan['repairs'] == context['repairs'] and plan['originalInputSha256'] == old_plan['inputSha256']
    assert plan['protectedArtifacts'] == baseline()
    assert plan['failedStartup'] == failed_startup(context)
    assert plan['historicalReplayLives'] == 3 and plan['remainingReplayLives'] == 45 and plan['remainingIdleLives'] == 4
    assert result['reusedReplayLives'] == 3 and result['executedReplayLives'] == 45 and result['executedIdleLives'] == 4
    assert plan['pipelineSeconds'] == 3600 and plan['collectionSeconds'] == 1800 and plan['perLifeSeconds'] == 180
    assert plan['pipelineStartMonotonicNs'] == context['pipeline']['pipelineStartMonotonicNs'] == result['pipelineStartMonotonicNs']
    assert plan['collectionStartMonotonicNs'] == context['result']['streamStartMonotonicNs'] == result['streamStartMonotonicNs']
    end = result['streamEndMonotonicNs']
    assert 0 < end-plan['pipelineStartMonotonicNs'] <= 3600*10**9
    assert 0 < end-plan['collectionStartMonotonicNs'] <= 1800*10**9
    assert result['resumeStartMonotonicNs'] > context['result']['runs'][-1]['controllerEndMonotonicNs']
    current_hashes, old_hashes = plan['inputSha256'], old_plan['inputSha256']
    for path in completion_paths():
        assert current_hashes[str(path)] == sha(path)
    for path, digest in current_hashes.items():
        assert sha(path) == digest, path
    assert plan['controlBuild'] == old_plan['controlBuild'] and plan['candidateBuild'] == old_plan['candidateBuild']
    assert plan['sourcePreparation'] == str(HERE/'preparation.json')
    assert plan['variants'] == old_plan['variants']
    # Rebuild the fixed order independently; no unavailable lifetime is inferred.
    expected = []
    for case in CASES:
        expected += [dict(case=case, variant=name, warmup=True, repeat=0) for name in NAMES]
        for rotation in range(3):
            expected += [dict(case=case, variant=name, warmup=False, repeat=rotation+1)
                         for name in NAMES[rotation:]+NAMES[:rotation]]
    assert plan['schedule'] == old_plan['schedule'] == expected
    assert len(result['runs']) == len(result['bindings']) == len(expected) == 48
    assert result['runs'][:3] == context['result']['runs']
    legacy = module('colors_three_unchanged_counter_auditor_for_completion', HERE/'reconcile.py')
    posts, prior_end, pids = 0, result['streamStartMonotonicNs'], set()
    for index, (step, row, binding) in enumerate(zip(expected, result['runs'], result['bindings'])):
        value = plan['variants'][step['variant']]
        epoch = 'original' if index < 3 else 'repaired'
        hashes = old_hashes if index < 3 else current_hashes
        directory = (original/'pilot' if index < 3 else base)/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        assert binding == epoch_binding(index, row, epoch, hashes) and row['directory'] == str(directory)
        auditor = old.audit if index < 3 else audit
        native, count = auditor.lifetime(directory, row, step, Path(value['path']),
                                        value['budget'], value['options'], hashes)
        assert native['launcher_sha256'] == binding['launcherSha256']
        placement = old.audit_placement if index < 3 else audit_placement
        assert row['placement'] == placement(directory, native, hashes)
        assert row['orderedPosts'] == count
        assert prior_end <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= end
        if index >= 3:
            assert row['controllerStartMonotonicNs'] >= result['resumeStartMonotonicNs']
        assert native['wall_ns'] <= 180*10**9
        legacy.readiness(directory, row['colors'], value['budget'], value['report'])
        assert bool(native['colors_report_path']) == value['report']
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']); posts += count
        prior_end = row['controllerEndMonotonicNs']
    assert len(result['idle']) == len(result['idleBindings']) == 4
    for name, row, binding in zip(NAMES, result['idle'], result['idleBindings']):
        value, directory = plan['variants'][name], base/('idle-'+name)
        wanted = epoch_binding(-1, dict(directory=str(directory)), 'repaired', current_hashes)
        wanted.pop('scheduleIndex'); wanted['variant'] = name
        assert binding == wanted
        assert row['variant'] == name and read(directory/'probe.json') == row
        native = native_receipt(directory/'native.json', Path(value['path']), value['budget'], value['options'], current_hashes)
        assert native['launcher_sha256'] == binding['launcherSha256']
        assert row['nativePid'] == native['native_pid'] and row['supervisorPid'] == native['supervisor_pid']
        assert read(directory/'launch.json') == dict(argv=[native['python_executable'], str(ACCOUNT),
            '--engine', value['path'], '--record', str(directory/'native.json'), '--known-single-process',
            '--thread-budget', str(value['budget']), *value['options']], variant=name, kind='startup-idle-shutdown')
        assert row['wholeCpuSeconds'] == native['total_cpu_s'] and row['wholeWallNs'] == native['wall_ns']
        assert row['rssKiB'] == native['maxrss_linux_kib'] and row['placement'] == audit_placement(directory, native, current_hashes)
        assert row['idleCpuTicks'] == row['shutdownStartCpuTicks']-row['startupCpuTicks'] >= 0
        assert row['tickHz'] == read(base/'03-profile-35-colors3-r0/tap-config.json')['tickHz']
        assert row['idleCpuSeconds'] == row['idleCpuTicks']/row['tickHz']
        assert row['idleNs'] == row['idleEndMonotonicNs']-row['idleStartMonotonicNs'] >= 250_000_000
        assert prior_end <= native['start_monotonic_ns'] < row['idleStartMonotonicNs'] < row['idleEndMonotonicNs'] < native['reaped_monotonic_ns'] <= end
        assert row['startupReplyNs'] > 0 and row['shutdownSupervisorNs'] > 0
        assert (directory/'stdin.raw').read_bytes() == b'cm_parm\nquit\n'
        assert (directory/'stdout.raw').read_bytes() == b'cm_parm\n' and (directory/'stderr').read_bytes() == b''
        assert set(row['sha256']) == {'launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr'}
        for path, digest in row['sha256'].items():
            assert sha(directory/path) == digest
        legacy.readiness(directory, row['colors'], value['budget'], value['report'], idle=True)
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']); prior_end = native['reaped_monotonic_ns']
    assert len(pids) == 52 and plan['failedStartup']['nativePid'] not in pids
    summaries = []
    for case in CASES:
        for name in NAMES:
            rows = [row for row in result['runs'] if row['case'] == case and row['variant'] == name and not row['warmup']]
            assert len(rows) == 3
            summaries.append(dict(case=case, variant=name, **{metric: dist([row[metric] for row in rows]) for metric in METRICS}))
    assert summaries == result['summaries']
    by = {(row['case'], row['variant']): row for row in summaries}
    comparisons = []
    for case in CASES:
        row = dict(case=case)
        for numerator, denominator in [('current2', 'preserved2'), ('inline1', 'preserved2'),
                                        ('colors3', 'current2'), ('colors3', 'inline1'), ('colors3', 'preserved2')]:
            row[numerator+'Vs'+denominator] = {key: by[case, numerator][key]['median']/by[case, denominator][key]['median']
                                               for key in METRICS[:3]}
        comparisons.append(row)
    sums = {name: {key: sum(by[case, name][key]['median'] for case in CASES) for key in METRICS[:3]} for name in NAMES}
    readiness = [dict(case=case, **legacy.readiness_summary([row for row in result['runs']
        if row['case'] == case and row['variant'] == 'colors3' and not row['warmup']])) for case in CASES]
    result = dict(complete=True, replayLives=48, reusedWarmups=3, newReplayLives=45,
        measured=36, warmups=12, idleProcesses=4, failedStartupProcesses=1, physicalNativeProcesses=53,
        reusedFocusedControls=38, reusedAffinityReplayControls=2, orderedPosts=posts,
        comparisons=comparisons, summedMedians=sums, summaries=summaries, readiness=readiness,
        originalHousekeeping=housekeeping(original/'pilot/housekeeping.json', 4),
        completionHousekeeping=housekeeping(base/'housekeeping.json', 49),
        originalIntervalGuestTicks=ticks(original/'pilot'), completionIntervalGuestTicks=ticks(base),
        failedStartup=plan['failedStartup'], rowToolBindings=read(base/'result.json')['bindings'],
        originalCapsPreserved=True, repairs=plan['repairs'], raw=str(base),
        rawSha256={name: sha(base/name) for name in ['plan.json', 'result.json', 'housekeeping.json', 'proc-stat-before', 'proc-stat-after']},
        reconcilerSha256=sha(Path(__file__)),
        scope='same frozen48+4 schedule;3 original excluded warmups retained; metadata repair only; no repeated completed life, rebuild, PGO, qualification or adoption; two guest-tick intervals exclude intervening repair gap')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({key: result[key] for key in ['complete', 'replayLives', 'orderedPosts', 'summedMedians', 'comparisons']}, indent=2))


if __name__ == '__main__':
    main()
