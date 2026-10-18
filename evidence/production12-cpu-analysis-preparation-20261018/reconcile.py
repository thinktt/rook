#!/usr/bin/env python3
"""Reconcile completed game evidence and raw public protocol; runs no engine."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT/'evidence/production12-cpu-20261018-pgo'
FIXTURE = Path('/home/legolas/king-spec/conformance/gate-replay/accepted-games-v1.json')
REFERENCE = Path('/home/legolas/king-spec/performance/selected-games-reference.json')
POST = re.compile(r'^\s*(\d+)\s+([+-]?\d+)\s+([+-]?\d+)\s+(\d+)\s+(.+)$')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def stats(samples):
    complete = all(value is not None for value in samples)
    return dict(samples=samples,resolved_samples=sum(v is not None for v in samples),
                median=statistics.median(samples) if complete else None,
                minimum=min(samples) if complete else None,maximum=max(samples) if complete else None)


def semantic(line):
    match = POST.fullmatch(line)
    if not match or int(match[1]) < 1000: return line
    return dict(depthToken=int(match[1]),evaluation=int(match[2]),engineCentiseconds=int(match[3]),
                searchId=int(match[4]),pv=match[5].strip().replace('0','O'))


def expected_streams(game):
    stdin = ['xboard','new','force','post','easy','level 0 5 0',*game['initialMoves'],'cm_parm default']
    stdout,stderr = ['cm_parm default'],[]
    for row in game['plies']:
        commands = game['personalityCommands'][row['personality']]
        seed,clock = row['seed'],row['clockCentiseconds']
        stdin += ['force',*commands,f'king_seed {seed}',f'time {clock}',f'otim {clock}','go']
        stdout += [*commands,f'king_seed {seed}',*row['expected']['posts'],f"move {row['expected']['move']}"]
        stderr.append(f'KING_SEARCH_SEED seed={seed}')
        if row['expected']['result'] is not None: stdout.append(row['expected']['result'])
    return dict(stdin=stdin+['quit'],stdout=stdout,stderr=stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='Fresh analysis file; never overwrite prior attempts')
    args = parser.parse_args()
    if args.output.exists(): parser.error('output must be absent')
    terminal_path = COLLECTION/'terminal.json'
    if not terminal_path.exists(): parser.error('collector is not authoritatively terminal')
    terminal,launch = read(terminal_path),read(COLLECTION/'launch.json')
    assert terminal['exit_code'] == 0,'collection terminal failure'
    assert terminal['driver_sha256_after'] == launch['driver_sha256'] == sha(COLLECTION/'driver.py')
    assert terminal['collector_stdout_sha256'] == sha(COLLECTION/'collector.stdout')
    assert terminal['collector_stderr_sha256'] == sha(COLLECTION/'collector.stderr')
    assert not (COLLECTION/'collector.stderr').stat().st_size,'collector stderr'
    collection = COLLECTION/'collection'
    manifest,summary = read(collection/'manifest.json'),read(collection/'summary.json')
    assert summary['complete'] and summary['complete12'] and summary['failure'] is None
    assert sha(Path(manifest['engine'])) == manifest['engine_sha256'] == terminal['engine_sha256_after'] == launch['engine_sha256']
    assert sha(Path(manifest['build_record'])) == launch['build_record_sha256']
    assert summary['artifact_sha256_after'] == manifest['engine_sha256']
    assert summary['input_sha256_after'] == manifest['input_sha256']
    assert all(sha(Path(p)) == digest for p,digest in manifest['input_sha256'].items())
    fixture,reference = read(FIXTURE),read(REFERENCE)
    assert len(fixture['games']) == 12 and sum(len(g['plies']) for g in fixture['games']) == 632
    assert len(manifest['schedule']) == len(summary['runs']) == 48
    assert reference['workload']['fixtureSha256'] == sha(FIXTURE),'raw reference workload differs'
    report = dict(complete=False,native_sha256=manifest['engine_sha256'],
        analysis_helper_sha256=sha(Path(__file__)),collection_terminal_sha256=sha(terminal_path),
        fixture_sha256=sha(FIXTURE),raw_reference_sha256=sha(REFERENCE),
        lifetimes=0,total_searches=0,measured_searches=0,measured_unresolved_search_cpu=0,
        raw_semantic_posts=0,games=[],artifact_records={},
        scope='Reported-only direct native wait4 plus small Python child pre-exec prefix; quantized external search observations.',
        qualification='No calibration/PMU/resource/observer/uncertainty qualification; no focused-continuity or full3288-game claim.',
        helper_affinity_observation_sha256=sha(Path(__file__).parent/'helper-affinity-observation.json'),
        helper_affinity_limit='Lead Codex/shell permit all16 CPUs; some short inherited-affinity source/status commands overlapped. Engine pinned14 and heavy owned work held; guest exclusivity and interference cost not established.',
        per_search_policy='All three raw CPU samples retained, including null unresolved zero ticks. CPU statistics/rates require all three positive resolved samples.',
        raw_reference_policy='Uncalibrated cross-machine descriptive cost ratios only; no performance pass/fail.')
    grouped = {g['id']:[] for g in fixture['games']}
    native_pids,supervisor_pids = set(),set()
    for index,(step,row) in enumerate(zip(manifest['schedule'],summary['runs'])):
        assert all(row[k] == step[k] for k in ['game','repeat','warmup'])
        assert step['repeat'] == index % 4 and step['warmup'] == (index % 4 == 0)
        game = next(g for g in fixture['games'] if g['id'] == step['game'])
        directory = collection/f"{index:02d}-{step['game']}-r{step['repeat']}"
        result_path = directory/'result.json'
        assert str(result_path) == row['result'] and sha(result_path) == row['result_sha256']
        result = read(result_path)
        assert result['failure'] is None and result['comparator_exit'] == 0 and result['cleanup'] is None
        assert result['capture'] and result['searches'] == len(game['plies'])
        assert all(sha(directory/path) == digest for path,digest in result['file_sha256'].items())
        replay,native,tap = [read(directory/path) for path in ['replay.json','native.json','wire/receipt.json']]
        owned = replay['processes'][0]
        assert replay['pass'] and replay['selectedGameIds'] == [game['id']]
        assert len(replay['games']) == len(replay['processes']) == 1
        assert replay['games'][0] == {'id':game['id'],'family':game['family'],'searches':len(game['plies']),'pass':True}
        assert owned['code'] == 0 and owned['signal'] is None and owned['forced'] is False and owned['gameIds'] == [game['id']]
        assert native['failure'] is None and native['native_exit_code'] == native['native_wait_status'] == 0
        assert native['supervisor_signals'] == [] and native['exec_error'] is None
        assert native['engine_sha256_before'] == native['engine_sha256_after'] == manifest['engine_sha256']
        assert native['argv'] == [manifest['engine'],'--diagnostic-seed-command']
        assert native['launcher_sha256'] == sha(ROOT/'tools/account_native.py')
        supervisor = [native['python_executable'],str(ROOT/'tools/account_native.py'),'--engine',manifest['engine'],
                      '--record',str(directory/'native.json'),'--known-single-process']
        assert replay['command'] == supervisor and replay['executableSha256'] == sha(Path(native['python_executable']))
        assert replay['runnerSha256'] == sha(FIXTURE.parent/'run.mjs') and replay['fixtureSha256'] == sha(FIXTURE)
        assert native['native_post_exec']['affinity'] == [14] and native['native_post_exec']['tasks'] == [str(native['native_pid'])]
        assert native['native_pid'] not in native_pids and native['supervisor_pid'] not in supervisor_pids
        native_pids.add(native['native_pid']); supervisor_pids.add(native['supervisor_pid'])
        assert math.isclose(native['total_cpu_s'],native['user_cpu_s']+native['system_cpu_s'],abs_tol=1e-12)
        assert row['cpu_s'] == result['cpu_s'] == native['total_cpu_s'] and row['wall_ns'] == result['wall_ns'] == native['wall_ns']
        assert tap['failure'] is None and tap['pending'] is None and tap['launcherExit'] == dict(code=0,signal=None)
        assert tap['native']['pid'] == native['native_pid'] and tap['native']['image'] == manifest['engine']
        assert tap['launcherPid'] == native['supervisor_pid'] and tap['argv'] == supervisor+['--diagnostic-seed-command']
        assert tap['configSha256'] == sha(directory/'tap-config.json')
        expected = expected_streams(game); raw = {}
        for stream,item in tap['raw'].items():
            path = directory/'wire'/(stream+'.raw'); data = path.read_bytes()
            assert item['path'] == str(path) and item['sha256'] == sha(path)
            assert len(data) == item['bytes'] == item['observedBytes'] and item['discardedObservedBytes'] == 0
            assert data.endswith(b'\n'),'partial raw record'
            lines = data.decode('utf8').splitlines(); raw[stream] = lines
            assert ([semantic(line) for line in lines] if stream == 'stdout' else lines) == expected[stream],f'{game["id"]} {stream} public protocol mismatch'
        assert len(raw['stdout']) == owned['stdoutRecords'] and len(raw['stderr']) == owned['stderrRecords']
        assert sum(tap['raw'][s]['bytes'] for s in ['stdout','stderr']) == owned['outputBytes']
        assert len(tap['searches']) == len(game['plies']) and result['search_intervals'] == tap['searches']
        for search,ply in zip(tap['searches'],game['plies']):
            assert search['move'] == ply['expected']['move']
            assert int(search['endMonotonicNs'])-int(search['startMonotonicNs']) == search['wallNs'] > 0
            before,after = search['beforeWrite'],search['afterData']
            for point in [before,after]:
                assert point['available'] and point['pid'] == native['native_pid'] and point['lastProcessor'] == 14
                assert point['startTicks'] == tap['native']['startTicks'] and point['image'] == manifest['engine']
            ticks = after['userTicks']+after['systemTicks']-before['userTicks']-before['systemTicks']
            assert ticks >= 0
            assert search['cpuTicks'] == (ticks if ticks else None)
            assert search['cpuSeconds'] == (ticks/tap['tickHz'] if ticks else None)
        report['lifetimes'] += 1; report['total_searches'] += len(game['plies'])
        report['raw_semantic_posts'] += sum(len(p['expected']['posts']) for p in game['plies'])
        if not step['warmup']:
            report['measured_searches'] += len(game['plies'])
            report['measured_unresolved_search_cpu'] += sum(s['cpuSeconds'] is None for s in tap['searches'])
            grouped[game['id']].append((native,tap))
        report['artifact_records'][str(result_path)] = sha(result_path)
    for game in fixture['games']:
        samples = grouped[game['id']]; assert len(samples) == 3
        cpu,wall = [n['total_cpu_s'] for n,t in samples],[n['wall_ns']/1e9 for n,t in samples]
        published = next(g for g in reference['games'] if g['gameId'] == game['id'])
        item = dict(id=game['id'],searches=len(game['plies']),lifetime_cpu_s=stats(cpu),lifetime_wall_s=stats(wall),
                    reference_lifetime_cpu_s=published['fullLifetimeCpuMs']['median']/1000,
                    maximum_observed_rss_kib=max(n['maxrss_linux_kib'] for n,t in samples),searches_detail=[])
        item['raw_uncalibrated_cpu_ratio'] = item['lifetime_cpu_s']['median']/item['reference_lifetime_cpu_s']
        for index,ply in enumerate(game['plies']):
            cpu = stats([t['searches'][index]['cpuSeconds'] for n,t in samples])
            item['searches_detail'].append(dict(index=index,move=ply['expected']['move'],cpu_s=cpu,
                wall_s=stats([t['searches'][index]['wallNs']/1e9 for n,t in samples]),
                completed_searches_per_cpu_second=1/cpu['median'] if cpu['median'] is not None else None))
        assert item['lifetime_cpu_s']['median'] == summary['game_summaries'][game['id']]['cpu_s']['median']
        report['games'].append(item)
    report['sum_game_medians_cpu_s'] = sum(g['lifetime_cpu_s']['median'] for g in report['games'])
    assert report['sum_game_medians_cpu_s'] == summary['sum_game_medians_cpu_s']
    report['reference_sum_game_medians_cpu_s'] = reference['totals']['sumPerGameMedianCpuMs']/1000
    report['raw_uncalibrated_aggregate_cpu_ratio'] = report['sum_game_medians_cpu_s']/report['reference_sum_game_medians_cpu_s']
    assert report['lifetimes'] == 48 and report['total_searches'] == 2528 and report['measured_searches'] == 1896
    report['complete'] = True
    with args.output.open('x') as stream: json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({key:report[key] for key in ['complete','lifetimes','total_searches','measured_unresolved_search_cpu','sum_game_medians_cpu_s','raw_uncalibrated_aggregate_cpu_ratio']}))


if __name__ == '__main__':
    main()
