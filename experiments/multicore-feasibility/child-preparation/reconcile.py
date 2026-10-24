#!/usr/bin/env python3
"""Independently reconcile retained child-preparation evidence; never launch an engine."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
CASES = ['profile-35', 'profile-08', 'profile-04']
VARIANTS = ['control', 'budget1', 'budget2', 'budget4']
HELPERS = {0, 1, 8, 9, 10, 11, 12, 13}
WORKERS = {1: [], 2: [6], 4: [6, 4, 2]}
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']
STAT_FIELDS = {
    'scopes_started', 'scopes_blocked', 'published', 'started', 'completed',
    'map_demands', 'chain_demands', 'map_uses', 'chain_uses', 'unique_map_used',
    'unique_chain_used', 'unique_any_used', 'not_ready', 'mismatched', 'discarded',
    'chain_discarded', 'cancelled', 'stale_completed', 'worker_failures', 'max_queue',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def nonfinite(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(path.read_text(), parse_constant=nonfinite)


def distribution(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def numeric(value, prefix=''):
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            name = prefix + str(key)
            if isinstance(item, dict):
                result.update(numeric(item, name+'.'))
            elif isinstance(item, (int, float)) and not isinstance(item, bool):
                assert math.isfinite(item), name
                result[name] = item
    return result


def ratio(numerator, denominator):
    return numerator/denominator if denominator else None


def check_stats(stats, threads):
    assert isinstance(stats, dict)
    expected = STAT_FIELDS | ({'pool_reserved_bytes'} if threads > 1 else set())
    assert set(stats) == expected, 'unexpected preparation counter schema'
    assert all(type(value) is int and value >= 0 for value in stats.values())
    if threads == 1:
        assert all(value == 0 for value in stats.values()), 'budget1 unexpectedly prepared work'
    else:
        assert stats['pool_reserved_bytes'] >= (threads-1)*256*1024
    assert stats['worker_failures'] == 0
    assert stats['published'] == stats['started'] + stats['cancelled']
    assert stats['started'] == stats['completed'], 'shutdown did not finish every started job'
    assert stats['started'] == stats['unique_any_used'] + stats['discarded']
    assert stats['started'] == stats['unique_chain_used'] + stats['chain_discarded']
    assert stats['map_demands'] + stats['chain_demands'] == (
        stats['map_uses'] + stats['chain_uses'] + stats['not_ready'] + stats['mismatched'])
    assert stats['unique_map_used'] <= stats['map_uses'] <= stats['map_demands']
    assert stats['unique_chain_used'] <= stats['chain_uses'] <= stats['chain_demands']
    assert max(stats['unique_map_used'], stats['unique_chain_used']) <= stats['unique_any_used']
    assert stats['unique_any_used'] <= stats['unique_map_used'] + stats['unique_chain_used']
    assert stats['unique_any_used'] <= stats['started']
    assert stats['stale_completed'] <= stats['discarded'] <= stats['chain_discarded']
    assert stats['mismatched'] <= stats['chain_demands'] - stats['chain_uses']
    assert stats['scopes_started'] <= stats['published'] <= 6*stats['scopes_started']
    assert stats['max_queue'] <= min(6, stats['published'])
    assert bool(stats['max_queue']) == bool(stats['published'])
    return dict(uniqueAnyUsedFraction=ratio(stats['unique_any_used'], stats['started']),
                uniqueChainUsedFraction=ratio(stats['unique_chain_used'], stats['started']),
                discardedChainFraction=ratio(stats['chain_discarded'], stats['started']),
                mapDemandDeliveryFraction=ratio(stats['map_uses'], stats['map_demands']),
                chainDemandDeliveryFraction=ratio(stats['chain_uses'], stats['chain_demands']),
                exactDemandNotReadyFraction=ratio(stats['not_ready'], stats['map_demands']+stats['chain_demands']))


def check_original_streams(actual, input_case, oracle_case, stdin, stdout, stderr):
    # Recheck the released checker's semantic rule from the retained raw bytes,
    # rather than treating its recorded status="pass" as sufficient evidence.
    assert actual['stdout'].encode() == stdout and actual['stderr'].encode() == stderr
    assert stderr.decode() == oracle_case['stderr']
    assert actual['exit'] == oracle_case['exit'] == dict(code=0, signal=None)
    protocol = input_case['protocol']
    # The pinned tap wraps stdin.write(), while the released runner sends
    # cleanup with stdin.end(data). Node's end path does not invoke that public
    # write wrapper. Check every captured byte exactly, without claiming the
    # raw file contains the uncaptured cleanup send. Complete output/exit checks
    # below and the pinned runner source retain the separate shutdown contract.
    expected_input = '\n'.join([*protocol['recordsBeforeSearch'], 'cm_parm rnd',
                                protocol['searchRecord']])+'\n'
    assert stdin == expected_input.encode(), 'original protocol input differs'
    text = stdout.decode()
    assert text.endswith('\n')
    lines = text.split('\n')[:-1]
    acknowledgments = [line for line in protocol['recordsBeforeSearch'] if line.startswith('cm_parm ')]
    acknowledgments.append('cm_parm rnd=0')
    assert lines[:len(acknowledgments)] == acknowledgments
    lines = lines[len(acknowledgments):]
    posts = []
    pattern = re.compile(r'^\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?$')
    for expected in oracle_case['posts']:
        match = pattern.fullmatch(lines.pop(0))
        assert match, 'missing or invalid semantic post'
        post = dict(depth=int(match[1]), score=int(match[2]), workThousands=int(match[3]),
                    searchId=int(match[4]), pv=(match[5] or '').strip().replace('0', 'O'))
        assert post == expected, 'original post/work/PV differs'
        posts.append(post)
    assert lines.pop(0) == 'move '+oracle_case['move']
    assert lines == oracle_case['resultRecords'], 'original shutdown records differ'
    return len(posts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.directory.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-child-preparation-pilot-v1'
    assert result['complete'] and result['failure'] is None and len(result['runs']) == 48
    expected_schedule = []
    for case in CASES:
        expected_schedule += [dict(case=case, variant=name, warmup=True, repeat=0) for name in VARIANTS]
        for repeat in range(3):
            order = VARIANTS[repeat:] + VARIANTS[:repeat]
            expected_schedule += [dict(case=case, variant=name, warmup=False, repeat=repeat+1) for name in order]
    assert plan['schedule'] == expected_schedule
    assert sum(row['warmup'] for row in result['runs']) == 12
    assert set(plan['variants']) == set(VARIANTS)
    assert plan['coordinatorCpu'] == 14
    assert plan['workerCpus'] == {str(key): value for key, value in WORKERS.items()}
    assert set(plan['helperAffinity']) and set(plan['helperAffinity']) <= HELPERS
    assert plan['excludedSiblings'] == [3, 5, 7, 15]
    assert plan['limits']['perLifetimeSeconds'] == 180 and plan['limits']['aggregateSeconds'] == 1800
    for name, digest in plan['inputSha256'].items():
        assert sha(Path(name)) == digest, 'input changed: '+name
    for name in VARIANTS:
        variant = plan['variants'][name]
        threads = 1 if name == 'control' else int(name.removeprefix('budget'))
        assert variant['threads'] == threads
        assert variant['args'] == ([] if name == 'control' else [f'--child-preparation={threads}'])
        assert sha(Path(variant['path'])) == variant['sha256']
    oracle = read(SPEC/'replay-oracle.json')
    inputs = read(SPEC/'workloads.json')
    mode = oracle['mode']
    total_posts = 0
    derived_runs = []
    for index, (step, row) in enumerate(zip(expected_schedule, result['runs'])):
        assert all(row[key] == value for key, value in step.items())
        directory = base/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        assert Path(row['directory']).resolve() == directory
        variant = plan['variants'][step['variant']]
        native = read(directory/'native.json')
        replay = read(directory/'stdout')
        config = read(directory/'tap-config.json')
        tap = read(directory/'wire/receipt.json')
        launch = read(directory/'launch.json')
        assert (directory/'stderr').read_bytes() == b''
        assert (directory/'stdout').stat().st_size <= plan['limits']['comparatorStdoutBytes']
        assert replay['status'] == 'pass' and replay['selectedCases'] == [step['case']]
        assert replay['workloadSha256'] == sha(SPEC/'workloads.json')
        assert replay['oracleSha256'] == sha(SPEC/'replay-oracle.json')
        assert len(replay['results']) == 1
        actual = replay['results'][0]
        assert actual['case'] == step['case'] and actual['status'] == 'pass'
        assert actual['complete'] and not actual['truncated'] and actual['error'] is None
        assert actual['discardedObservedBytes'] == 0
        assert native['schema'] == 'rook2-child-preparation-wait4-v1'
        assert native['failure'] is None and native['native_exit_code'] == 0
        assert native['native_wait_status'] == 0 and native['supervisor_signals'] == []
        assert native['exec_error'] is None and native['known_single_process'] is True
        assert native['engine'] == variant['path']
        assert native['engine_sha256_before'] == native['engine_sha256_after'] == variant['sha256']
        assert native['launcher_sha256'] == plan['inputSha256'][str(HERE/'account.py')]
        assert sha(Path(native['python_executable'])) == native['python_executable_sha256']
        assert native['argv'] == [variant['path'], *variant['args'], *mode]
        supervisor = [native['python_executable'], str(HERE/'account.py'), '--engine', variant['path'],
                      '--record', str(directory/'native.json'), '--known-single-process',
                      '--thread-budget', str(variant['threads'])]
        if step['variant'] != 'control':
            supervisor += ['--preparation-report', str(directory/'stats.json')]
        supervisor += variant['args']
        assert config['expectedArgv'] == [*supervisor, *mode] == tap['argv'] == actual['command']
        assert config['directory'] == str(directory/'wire') and config['nativeExecutable'] == variant['path']
        assert config['maxRawBytes'] == plan['limits']['nativeRawBytes']
        assert tap['configSha256'] == sha(directory/'tap-config.json')
        assert launch == dict(step=step, argv=['/usr/bin/node', '--import', str(ROOT/'tools/tap_wire.mjs'),
                                             str(SPEC/'replay-check.mjs'), '--case', step['case'], '--', *supervisor])
        assert tap['launcherPid'] == native['supervisor_pid']
        assert tap['launcherExit'] == dict(code=0, signal=None)
        assert native['expected_threads'] == variant['threads']
        assert native['expected_worker_cpus'] == WORKERS[variant['threads']]
        assert native['inherited_supervisor_affinity'] == plan['helperAffinity']
        assert set(native['supervisor_affinity']) and set(native['supervisor_affinity']) <= HELPERS
        assert native['native_pre_exec'] == dict(pid=native['native_pid'], pgid=native['supervisor_pid'], affinity=[14])
        observed = native['native_post_exec']
        assert observed['path'] == variant['path'] and observed['pgid'] == native['supervisor_pid']
        assert observed['affinity'] == [14]
        affinities = observed['task_affinities']
        assert sorted(observed['tasks']) == sorted(affinities)
        assert len(affinities) == variant['threads'] and affinities[str(native['native_pid'])] == [14]
        assert sorted(cpus for tid, cpus in affinities.items() if tid != str(native['native_pid'])) == (
            sorted([[cpu] for cpu in WORKERS[variant['threads']]]))
        assert row['taskAffinities'] == affinities and row['nativePid'] == native['native_pid']
        assert native['preparation_report_error'] is None
        stats = native['preparation_report']
        if step['variant'] == 'control':
            assert stats is None and row['preparation'] is None
            assert native['preparation_report_path'] is None and native['preparation_report_sha256'] is None
            assert not (directory/'stats.json').exists()
            useful = None
        else:
            assert native['preparation_report_path'] == str(directory/'stats.json')
            assert (directory/'stats.json').stat().st_size <= plan['limits']['preparationReportBytes']
            assert sha(directory/'stats.json') == native['preparation_report_sha256']
            assert read(directory/'stats.json') == stats == row['preparation']
            useful = check_stats(stats, variant['threads'])
        assert native['wall_ns'] == native['reaped_monotonic_ns'] - native['start_monotonic_ns'] > 0
        assert native['total_cpu_s'] == native['user_cpu_s'] + native['system_cpu_s'] > 0
        assert native['total_cpu_s'] == row['wholeCpuSeconds']
        assert native['wall_ns'] == row['wholeWallNs'] and native['maxrss_linux_kib'] == row['rssKiB']
        assert tap['failure'] is None and tap['pending'] is None and len(tap['searches']) == 1
        assert tap['native']['pid'] == native['native_pid'] and tap['native']['image'] == variant['path']
        search = tap['searches'][0]
        assert search['wallNs'] == int(search['endMonotonicNs']) - int(search['startMonotonicNs']) > 0
        assert search['wallNs'] == row['searchWallNs']
        assert native['wall_ns'] - search['wallNs'] == row['nonSearchWallNs'] >= 0
        for boundary in ['beforeWrite', 'afterData']:
            assert search[boundary]['available'] and search[boundary]['pid'] == native['native_pid']
            assert search[boundary]['image'] == variant['path'] and search[boundary]['lastProcessor'] == 14
            assert search[boundary]['startTicks'] == tap['native']['startTicks']
        assert set(tap['raw']) == {'stdin', 'stdout', 'stderr'}
        raw = {}
        for stream, item in tap['raw'].items():
            path = directory/'wire'/f'{stream}.raw'
            assert item['path'] == str(path)
            assert sha(path) == item['sha256']
            assert path.stat().st_size == item['bytes'] == item['observedBytes']
            assert item['discardedObservedBytes'] == 0
            raw[stream] = path.read_bytes()
        assert sum(len(data) for data in raw.values()) <= plan['limits']['nativeRawBytes']
        input_case = next(value for value in inputs['cases'] if value['id'] == step['case'])
        oracle_case = next(value for value in oracle['cases'] if value['id'] == step['case'])
        total_posts += check_original_streams(actual, input_case, oracle_case,
                                               raw['stdin'], raw['stdout'], raw['stderr'])
        assert search['move'] == oracle_case['move']
        expected_hashes = {'native.json', 'stdout', 'stderr', 'wire/receipt.json'}
        if stats is not None:
            expected_hashes.add('stats.json')
        assert set(row['sha256']) == expected_hashes
        for name, digest in row['sha256'].items():
            assert sha(directory/name) == digest
        for pid in [native['native_pid'], native['supervisor_pid']]:
            assert not Path(f'/proc/{pid}').exists(), 'recorded owned PID is currently live; inspect possible PID reuse'
        derived_runs.append(dict(case=step['case'], variant=step['variant'], warmup=step['warmup'],
                                 repeat=step['repeat'], usefulness=useful))

    summaries = []
    for case in CASES:
        for name in VARIANTS:
            selected = [row for row in result['runs'] if (row['case'], row['variant'], row['warmup']) == (case, name, False)]
            assert len(selected) == 3
            original = next(item for item in result['summaries'] if (item['case'], item['variant']) == (case, name))
            summary = dict(case=case, variant=name)
            for metric in METRICS:
                samples = [row[metric] for row in selected]
                regenerated = distribution(samples)
                assert original[metric] == regenerated
                summary[metric] = dict(**regenerated, mean=statistics.mean(samples))
            counters = [numeric(row['preparation']) for row in selected]
            assert all(set(value) == set(counters[0]) for value in counters)
            regenerated_stats = {key: distribution([value[key] for value in counters]) for key in counters[0]}
            assert original['preparation'] == regenerated_stats
            summary['preparation'] = {key: dict(**value, mean=statistics.mean(value['samples']))
                                      for key, value in regenerated_stats.items()}
            summary['counterTotals'] = {key: sum(value[key] for value in counters) for key in counters[0]
                                        if key not in {'pool_reserved_bytes', 'max_queue'}}
            summaries.append(summary)
    assert len(result['summaries']) == len(summaries) == 12
    by = {(row['case'], row['variant']): row for row in summaries}
    comparisons = []
    for case in CASES:
        control, one = by[case, 'control'], by[case, 'budget1']
        comparison = dict(case=case,
                          serialHookWallRatio=one['searchWallNs']['median']/control['searchWallNs']['median'],
                          serialHookCpuRatio=one['wholeCpuSeconds']['median']/control['wholeCpuSeconds']['median'])
        for name in ['budget2', 'budget4']:
            worker = by[case, name]
            comparison[name] = dict(wallRatioVsBudget1=worker['searchWallNs']['median']/one['searchWallNs']['median'],
                                    wallRatioVsControl=worker['searchWallNs']['median']/control['searchWallNs']['median'],
                                    wholeCpuRatioVsBudget1=worker['wholeCpuSeconds']['median']/one['wholeCpuSeconds']['median'],
                                    rssRatioVsBudget1=worker['rssKiB']['median']/one['rssKiB']['median'])
        comparisons.append(comparison)
    sums = {name: {metric: sum(by[case, name][metric]['median'] for case in CASES)
                   for metric in ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs']}
            for name in VARIANTS}
    output = dict(complete=True, rawDirectory=str(base), nativeProcesses=48, strictSearchComparisons=48,
                  measuredSearchComparisons=36, excludedWarmups=12, orderedPostsIncludingWarmups=total_posts,
                  comparisons=comparisons, summedMedians=sums, summaries=summaries, runs=derived_runs,
                  accounting=['published=started+cancelled', 'started=completed',
                              'started=unique_any_used+discarded', 'started=unique_chain_used+chain_discarded',
                              'map_demands+chain_demands=map_uses+chain_uses+not_ready+mismatched'],
                  notes='Use counts can exceed unique tasks on retry; stale_completed is a subset of discarded work. Pool reserved bytes include requested stacks, not whole RSS. Summed case medians are only this selected set.',
                  stdinCapture='Exact setup/query/search write() bytes. Cleanup is sent via end(data), outside this pinned tap; the pinned runner and complete raw output/exit checks retain the shutdown contract.',
                  rawSha256={name: sha(base/name) for name in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after']},
                  reconcilerSha256=sha(Path(__file__)),
                  limits='Original cases35/08/04 only; point affinity observations; no PGO, broad qualification or actual host-isolation proof')
    destination = args.output.resolve() if args.output else base/'reconciled.json'
    with destination.open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(complete=True, nativeProcesses=48, measured=36, warmups=12,
                         comparisons=comparisons, summedMedians=sums), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
