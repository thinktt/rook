"""Bounded live synthetic validation, not an engine/calibration benchmark."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/home/legolas/rook2')
DEST = ROOT / 'evidence/runner-controls'
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
start = time.monotonic()
original = os.sched_getaffinity(0)
receipt = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'scope': 'live synthetic known-single-process controls only; no engine, calibrator, PMU or administrative changes',
           'driver_initial_affinity': sorted(original),
           'pre_fix_preflight_control': {'command': 'taskset -c 0-5,8-13 python3 tools/measure.py [plan-only arguments] --dry-run -- /bin/true',
               'observed_error': 'inherited affinity must permit CPU14 and all helper CPUs',
               'child_launched': False,
               'fix': 'allow helper-pinned recorder; independently request/verify CPU14 in child'},
           'checks': [], 'cases': []}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_bounded(command, prefix):
    if time.monotonic() - start > 12:
        raise RuntimeError('live-control total budget exhausted before launch')
    began = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=1.9)
    (DEST / (prefix + '.stdout')).write_bytes(result.stdout)
    (DEST / (prefix + '.stderr')).write_bytes(result.stderr)
    return {'command': command, 'exit_code': result.returncode,
            'elapsed_s': time.monotonic() - began,
            'stdout_artifact': prefix + '.stdout',
            'stderr_artifact': prefix + '.stderr'}

try:
    os.sched_setaffinity(0, HELPERS)
    receipt['driver_collection_affinity'] = sorted(os.sched_getaffinity(0))
    source = ROOT / 'tools/runner-control.c'
    binary = DEST / 'runner-control'
    compile_command = ['/usr/bin/cc', '-O2', '-Wall', '-Wextra', '-std=c11',
                       str(source), '-o', str(binary)]
    receipt['compile'] = run_bounded(compile_command, 'compile')
    assert receipt['compile']['exit_code'] == 0
    receipt['source_sha256'] = digest(source)
    receipt['binary_sha256'] = digest(binary)
    receipt['runner_sha256'] = digest(ROOT / 'tools/measure.py')
    receipt['controller_sha256'] = digest(Path(__file__))
    for mode, expected, cap, timeout in [
            ('normal', None, 4096, '0.3'),
            ('nonzero', 'nonzero-or-signal-exit', 4096, '0.3'),
            ('timeout', 'deadline', 4096, '0.12'),
            ('flood', 'stream-cap', 1024, '0.3')]:
        output = DEST / mode
        command = [sys.executable, str(ROOT / 'tools/measure.py'),
                   '--output', str(output), '--label', 'synthetic-' + mode,
                   '--fidelity', 'F0', '--known-single-process',
                   '--semantic-description', 'Synthetic recorder control; no chess or equivalence claim',
                   '--input-file', str(source), '--warmups', '1' if mode == 'normal' else '0',
                   '--repeats', '3', '--timeout-s', timeout,
                   '--aggregate-timeout-s', '1.1', '--cleanup-s', '0.3',
                   '--stream-cap-bytes', str(cap), '--', str(binary), mode]
        run = run_bounded(command, 'controller-' + mode)
        summary = json.loads((output / 'summary.json').read_text())
        manifest = json.loads((output / 'manifest.json').read_text())
        records = summary['records']
        assert run['elapsed_s'] < 2
        assert summary['affinity_restored'] == sorted(HELPERS)
        assert summary['recorder_affinity_during_collection'] == sorted(HELPERS)
        assert manifest['initial_recorder_affinity'] == sorted(HELPERS)
        assert os.sched_getaffinity(0) == HELPERS
        assert manifest['executable_sha256'] == receipt['binary_sha256']
        assert summary['failure'] == expected
        assert summary['behavior'] == 'not-checked'
        assert summary['performance'] == 'reported-only'
        for record in records:
            assert record['placement_before_exec']['affinity'] == [14]
            assert record['reaped_monotonic_ns'] is not None
            assert record['wait_status'] is not None
            assert record['streams']['stdout']['retained'] <= cap
            assert record['streams']['stderr']['retained'] <= cap
            assert record['executable_sha256_after'] == receipt['binary_sha256']
        if mode == 'normal':
            assert run['exit_code'] == 0 and summary['complete_schedule']
            assert len(records) == 4 and sum(r['warmup'] for r in records) == 1
            assert len(summary['summaries']['total_cpu_s']['samples']) == 3
            assert summary['summaries']['total_cpu_s']['range_over_median'] is not None
            for record in records:
                raw = (output / record['id'] / 'stdout.raw').read_text()
                observed = json.loads(raw.splitlines()[0])
                assert observed['affinity'] == [14] and observed['pid'] == record['pid']
                assert 'cpu-work-completed:' in raw
                assert (output / record['id'] / 'stderr.raw').read_text() == 'synthetic-stderr:normal\n'
                assert record['total_cpu_s'] >= 0.025
                assert record['exit_code'] == 0 and record['stream_eof']
        else:
            assert run['exit_code'] == 1 and not summary['complete_schedule']
            assert len(records) == 1, 'failure must stop later launches'
            assert all(value is None for value in summary['summaries'].values())
            if mode == 'nonzero':
                assert records[0]['exit_code'] == 7
            if mode == 'timeout':
                assert records[0]['exit_code'] == -9
            if mode == 'flood':
                assert records[0]['streams']['stdout']['discarded'] > 0
                assert len((output / records[0]['id'] / 'stdout.raw').read_bytes()) == cap
        run['assertions'] = 'passed'
        run['record_ids'] = [record['id'] for record in records]
        run['failure_expected'] = expected
        receipt['cases'].append(run)
    receipt['checks'] = [
        'native helper independently observed CPU14 only',
        'normal stdout/stderr retained and positive kernel CPU recorded',
        'one excluded warmup plus three measured native lifetimes retained',
        'nonzero/timeout/cap preserve failed record and stop subsequent launches',
        'failed schedules emit no partial performance summary',
        'recorder helper affinity and exact inherited affinity restoration checked',
        'driver helper affinity unchanged across subprocess runs']
    receipt['passed'] = True
except BaseException as error:
    receipt['passed'] = False
    receipt['error'] = f'{type(error).__name__}: {error}'
    raise
finally:
    os.sched_setaffinity(0, original)
    receipt['driver_restored_affinity'] = sorted(os.sched_getaffinity(0))
    receipt['total_elapsed_s'] = time.monotonic() - start
    receipt['within_15s_total_budget'] = receipt['total_elapsed_s'] <= 15
    (DEST / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'passed': receipt.get('passed'),
                      'elapsed_s': receipt['total_elapsed_s'],
                      'receipt': str(DEST / 'receipt.json')}))
