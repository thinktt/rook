#!/usr/bin/env python3
"""Reported-only complete-game CPU collection under the unchanged released runner."""
import argparse
import datetime
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time

from compare_ordinary import children, sha, write
from measure import cgroup_snapshot

ROOT = Path(__file__).resolve().parents[1]
GATE = Path('/home/legolas/king-spec/conformance/gate-replay')
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
MIB = 1024 * 1024
LIMITS = dict(search_ms=300000, game_seconds=2700, aggregate_seconds=43200,
              cleanup_seconds=5, native_raw_bytes=32*MIB,
              comparator_raw_bytes=8*MIB, report_bytes=4*MIB,
              native_receipt_bytes=MIB, tap_receipt_bytes=4*MIB,
              artifact_pool_bytes=8*1024*MIB)


def context():
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                uname=list(os.uname()), helper_affinity=sorted(os.sched_getaffinity(0)),
                cgroups=cgroup_snapshot(), proc_stat=Path('/proc/stat').read_text(),
                loadavg=Path('/proc/loadavg').read_text(),
                scope='Local point observations; no assertion of exclusive host ownership',
                pmu='Unavailable; no instructions, cycles, CPI or terminal N/R',
                resource_profile='Observed inherited limits; no private memory/no-swap cgroup qualification')


def byte_count(directory):
    return sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())


def stop_within_five_seconds(process):
    start = time.monotonic()
    deadline = start + LIMITS['cleanup_seconds']
    owned = children(process.pid)
    owned += [pid for supervisor in list(owned) for pid in children(supervisor)]
    for supervisor in children(process.pid):
        try:
            os.kill(supervisor, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=max(0, deadline-time.monotonic()-1))
    except subprocess.TimeoutExpired:
        pass
    if process.poll() is None or any(Path(f'/proc/{pid}').exists() for pid in owned):
        try:
            # Popen created this process group; the known native supervisor and
            # its single child inherit it. Never signal an unrelated group.
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    while time.monotonic() < deadline:
        if process.poll() is not None and not any(Path(f'/proc/{pid}').exists() for pid in owned):
            return dict(elapsed_s=time.monotonic()-start, reconciled=True, observed_owned_pids=owned)
        time.sleep(min(0.01, max(0, deadline-time.monotonic())))
    return dict(elapsed_s=time.monotonic()-start, reconciled=False, observed_owned_pids=owned)


def run_lifetime(engine, engine_sha, game, directory, aggregate_deadline,
                 retained_bytes=0, capture=True):
    """Also used by the bounded observer-control driver; no alternate engine path."""
    directory.mkdir()
    native_path, report_path = directory/'native.json', directory/'replay.json'
    supervisor = [sys.executable, str(ROOT/'tools/account_native.py'), '--engine', str(engine),
                  '--record', str(native_path), '--known-single-process']
    command = ['/usr/bin/node']
    env = dict(os.environ)
    if capture:
        config = dict(version=1, expectedArgv=supervisor+['--diagnostic-seed-command'],
                      directory=str(directory/'wire'), nativeExecutable=str(engine),
                      tickHz=os.sysconf('SC_CLK_TCK'), maxRawBytes=LIMITS['native_raw_bytes'])
        config_path = directory/'tap-config.json'
        write(config_path, config)
        env['ROOK2_WIRE_TAP_CONFIG'] = str(config_path)
        command += ['--import', str(ROOT/'tools/tap_wire.mjs')]
    else:
        env.pop('ROOK2_WIRE_TAP_CONFIG', None)
    command += [str(GATE/'run.mjs'), '--fixture', str(GATE/'accepted-games-v1.json'),
                '--game', game['id'], '--timeout-ms', str(LIMITS['search_ms']),
                '--report', str(report_path), '--', *supervisor]
    row = dict(game=game['id'], searches=len(game['plies']), capture=capture,
               command=command, failure=None, cleanup=None)
    write(directory/'launch.json', row)
    stdout_path, stderr_path = directory/'comparator.stdout', directory/'comparator.stderr'
    with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
        process = subprocess.Popen(command, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        row['comparator_pid'] = process.pid
        deadline = min(aggregate_deadline, time.monotonic()+LIMITS['game_seconds'])
        try:
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    row['failure'] = 'host-deadline'
                elif stdout_path.stat().st_size+stderr_path.stat().st_size > LIMITS['comparator_raw_bytes']:
                    row['failure'] = 'comparator-raw-byte-cap'
                elif report_path.exists() and report_path.stat().st_size > LIMITS['report_bytes']:
                    row['failure'] = 'report-byte-cap'
                elif retained_bytes+byte_count(directory) > LIMITS['artifact_pool_bytes']:
                    row['failure'] = 'artifact-pool-cap'
                elif (directory/'wire/failure.json').exists():
                    row['failure'] = 'wire-tap-failure'
                if row['failure']:
                    row['cleanup'] = stop_within_five_seconds(process)
                    break
                time.sleep(0.05)
        except BaseException as error:
            row['failure'] = f'{type(error).__name__}: {error}'
            row['cleanup'] = stop_within_five_seconds(process)
    row['comparator_exit'] = process.poll()
    try:
        assert row['failure'] is None, row['failure']
        assert process.returncode == 0 and stderr_path.stat().st_size == 0, 'comparator exit/stderr'
        assert stdout_path.stat().st_size+stderr_path.stat().st_size <= LIMITS['comparator_raw_bytes'], 'comparator cap at exit'
        assert report_path.stat().st_size <= LIMITS['report_bytes'], 'report cap at exit'
        assert native_path.stat().st_size <= LIMITS['native_receipt_bytes'], 'native receipt cap'
        report = json.loads(report_path.read_text())
        native = json.loads(native_path.read_text())
        assert report['pass'] is True and report['selectedGameIds'] == [game['id']], 'strict game assertions'
        assert report['command'] == supervisor, 'replay launch configuration'
        assert report['executableSha256'] == sha(Path(sys.executable)), 'launcher identity'
        assert report['runnerSha256'] == sha(GATE/'run.mjs'), 'released runner changed'
        assert report['fixtureSha256'] == sha(GATE/'accepted-games-v1.json'), 'released fixture changed'
        assert len(report['games']) == len(report['processes']) == 1, 'game/process inventory'
        result, owned = report['games'][0], report['processes'][0]
        assert result == {'id':game['id'], 'family':game['family'], 'searches':len(game['plies']), 'pass':True}, 'completed game'
        assert owned['gameIds'] == [game['id']] and owned['code'] == 0 and owned['signal'] is None and owned['forced'] is False, 'normal independent exit'
        assert native['failure'] is None and native['native_exit_code'] == 0, 'native accounting invalid'
        assert native['engine_sha256_before'] == native['engine_sha256_after'] == engine_sha, 'native artifact changed'
        assert native['launcher_sha256'] == sha(ROOT/'tools/account_native.py'), 'accounting supervisor changed'
        assert native['argv'] == [str(engine), '--diagnostic-seed-command'], 'native arguments'
        assert native['supervisor_signals'] == [], 'supervisor interrupted'
        assert not Path(f"/proc/{native['native_pid']}").exists(), 'native child unreconciled'
        assert not Path(f"/proc/{native['supervisor_pid']}").exists(), 'supervisor unreconciled'
        row.update(cpu_s=native['total_cpu_s'], user_s=native['user_cpu_s'], system_s=native['system_cpu_s'],
                   wall_ns=native['wall_ns'], native_pid=native['native_pid'], maxrss_linux_kib=native['maxrss_linux_kib'])
        if capture:
            tap_path = directory/'wire/receipt.json'
            assert tap_path.stat().st_size <= LIMITS['tap_receipt_bytes'], 'tap receipt cap'
            tap = json.loads(tap_path.read_text())
            assert tap['failure'] is None and tap['pending'] is None, 'incomplete wire capture'
            assert tap['launcherExit'] == dict(code=0, signal=None), 'tap launcher exit'
            assert tap['argv'] == supervisor+['--diagnostic-seed-command'], 'tap launch binding'
            assert tap['configSha256'] == sha(directory/'tap-config.json'), 'tap config binding'
            assert tap['native']['pid'] == native['native_pid'], 'tap native identity'
            assert len(tap['searches']) == len(game['plies']), 'search boundary count'
            assert [s['move'] for s in tap['searches']] == [p['expected']['move'] for p in game['plies']], 'captured selected moves'
            total_raw = 0
            for stream, item in tap['raw'].items():
                path = directory/'wire'/f'{stream}.raw'
                assert item['sha256'] == sha(path), 'raw stream hash'
                assert item['bytes'] == item['observedBytes'] == path.stat().st_size, 'raw byte inventory'
                assert item['discardedObservedBytes'] == 0, 'discarded raw bytes'
                total_raw += item['bytes']
            assert total_raw <= LIMITS['native_raw_bytes'], 'native raw cap'
            raw_stdout, raw_stderr = [(directory/'wire'/f'{s}.raw').read_bytes() for s in ['stdout','stderr']]
            assert raw_stdout.endswith(b'\n') and raw_stderr.endswith(b'\n'), 'partial output capture'
            assert len(raw_stdout.splitlines()) == owned['stdoutRecords'], 'stdout record reconciliation'
            assert len(raw_stderr.splitlines()) == owned['stderrRecords'], 'stderr record reconciliation'
            assert len(raw_stdout)+len(raw_stderr) == owned['outputBytes'], 'comparator/raw byte reconciliation'
            assert (directory/'wire/stdin.raw').read_bytes().splitlines().count(b'go') == len(game['plies']), 'go count'
            for search in tap['searches']:
                for boundary in ['beforeWrite', 'afterData']:
                    point = search[boundary]
                    assert point['available'] and point['pid'] == native['native_pid'] and point['lastProcessor'] == 14, 'native boundary identity/placement'
                assert search['wallNs'] > 0, 'search observation order'
                assert search['cpuTicks'] is None or search['cpuTicks'] > 0, 'nonpositive CPU rate'
            row['search_intervals'] = tap['searches']
            row['unresolved_search_cpu'] = sum(s['cpuSeconds'] is None for s in tap['searches'])
        assert retained_bytes+byte_count(directory) <= LIMITS['artifact_pool_bytes'], 'artifact cap at exit'
    except (AssertionError, OSError, ValueError, KeyError, TypeError) as error:
        row['failure'] = row['failure'] or str(error)
    row['retained_bytes_before_result'] = byte_count(directory)
    row['file_sha256'] = {str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file()}
    write(directory/'result.json', row)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--build-record', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--game', action='append', default=[], help='Explicit supporting subset; omitted means all12')
    args = parser.parse_args()
    engine, build_path = args.engine.resolve(strict=True), args.build_record.resolve(strict=True)
    build, engine_sha = json.loads(build_path.read_text()), sha(engine)
    if build['outcome'] != 'build-succeeded-with-stable-input-snapshot' or build['binary_output']['sha256'] != engine_sha:
        parser.error('native image must match its successful stable build')
    fixture = json.loads((GATE/'accepted-games-v1.json').read_text())
    games = [g for g in fixture['games'] if not args.game or g['id'] in args.game]
    if len(fixture['games']) != 12 or sum(len(g['plies']) for g in fixture['games']) != 632:
        parser.error('unexpected released game corpus')
    if len(set(args.game)) != len(args.game) or (args.game and len(games) != len(args.game)):
        parser.error('duplicate or unknown game selection')
    if args.output.exists() or not args.output.absolute().parent.is_dir():
        parser.error('output must be absent with an existing parent')
    args.output = args.output.absolute()
    args.output.mkdir()
    initial_affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, HELPERS & initial_affinity)
    dependencies = [Path(__file__).resolve(), ROOT/'tools/account_native.py', ROOT/'tools/tap_wire.mjs',
                    ROOT/'tools/compare_ordinary.py', ROOT/'tools/measure.py', GATE/'run.mjs',
                    GATE/'accepted-games-v1.json', build_path, Path('/usr/bin/node').resolve(), Path(sys.executable).resolve()]
    schedule = [dict(game=g['id'], repeat=i, warmup=i == 0) for g in games for i in range(4)]
    manifest = dict(schema='rook2-whole-native-games-v1', engine=str(engine), engine_sha256=engine_sha,
                    build_record=str(build_path), schedule=schedule, limits=LIMITS,
                    input_sha256={str(p):sha(p) for p in dependencies}, environment={k:os.environ.get(k) for k in
                    ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS']},
                    measurement='Reported-only; no calibrated reference or final resource/observer/uncertainty qualification',
                    accounting='Direct native wait4 lifetime; controller byte listeners preserve native pipes; external quantized per-search CPU observations',
                    missing='PMU instructions/cycles, exact terminal N/R, descendant-complete continuous ownership monitoring',
                    qualifications='Replay report names the Python launcher; actual native hash/PID and byte capture are bound separately')
    write(args.output/'manifest.json', manifest)
    write(args.output/'context-before.json', context())
    summary = dict(complete=False, complete12=False, failure=None, runs=[], game_summaries={})
    deadline = time.monotonic()+LIMITS['aggregate_seconds']
    try:
        for index, step in enumerate(schedule):
            game = next(g for g in games if g['id'] == step['game'])
            directory = args.output/f"{index:02d}-{game['id']}-r{step['repeat']}"
            row = run_lifetime(engine, engine_sha, game, directory, deadline, byte_count(args.output))
            summary['runs'].append(dict(**step, result=str(directory/'result.json'), result_sha256=sha(directory/'result.json'),
                                       failure=row['failure'], cpu_s=row.get('cpu_s'), wall_ns=row.get('wall_ns')))
            if row['failure']:
                summary['failure'] = row['failure']
                break
            if step['repeat'] == 3:
                measured = [r for r in summary['runs'] if r['game'] == step['game'] and not r['warmup']]
                result = {}
                for metric in ['cpu_s','wall_ns']:
                    samples = [r[metric] for r in measured]
                    result[metric] = dict(samples=samples, median=statistics.median(samples), minimum=min(samples), maximum=max(samples))
                summary['game_summaries'][step['game']] = result
                print(json.dumps(dict(game=step['game'], **result)), flush=True)
            write(args.output/'summary.json', summary)
        summary['complete'] = len(summary['runs']) == len(schedule) and summary['failure'] is None
        summary['artifact_sha256_after'] = sha(engine)
        summary['input_sha256_after'] = {str(p):sha(p) for p in dependencies}
        if summary['artifact_sha256_after'] != engine_sha or summary['input_sha256_after'] != manifest['input_sha256']:
            summary.update(complete=False, failure='artifact/input changed')
        if summary['complete']:
            summary['sum_game_medians_cpu_s'] = sum(v['cpu_s']['median'] for v in summary['game_summaries'].values())
        summary['complete12'] = summary['complete'] and len(games) == 12
        summary['retained_bytes_before_final_summary'] = byte_count(args.output)
        write(args.output/'summary.json', summary)
        write(args.output/'context-after.json', context())
    finally:
        os.sched_setaffinity(0, initial_affinity)
    print(json.dumps(dict(complete=summary['complete'], complete12=summary['complete12'], failure=summary['failure'],
                          sum_game_medians_cpu_s=summary.get('sum_game_medians_cpu_s'))))
    return 0 if summary['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
