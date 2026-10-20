#!/usr/bin/env python3
"""Four fixed functional rows; source/projection checked, descriptive CPU only."""
import argparse
import csv
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PUBLIC = Path('/home/legolas/king-spec/performance')
ACCOUNT = Path('/home/legolas/rook2/tools/account_native.py')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
ROWS = [
    ('eval-scalar', 'functional-evaluation-opening', 256, 1000000),
    ('eval-coherent', 'functional-evaluation-opening', 256, 1000000),
    ('position', 'functional-position-history-opening', 256, 1000000),
    ('search', 'functional-search-light-start', 1024, 65536),
]
TARGET_NS = 400000000
TIMEOUT_S, CLEANUP_S, BYTE_CAP = 30, 5, 4 * 1024 * 1024


def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(p):
    # Duplicate keys and nonfinite values cannot silently normalize an observation.
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate JSON key: ' + k)
            d[k] = v
        return d
    return json.loads(Path(p).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def save(p, value):
    with Path(p).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def exact(actual, expected, where='projection'):
    need(type(actual) is type(expected), where + ': type mismatch')
    if isinstance(expected, dict):
        need(actual.keys() == expected.keys(), where + ': keys differ')
        for k in expected:
            exact(actual[k], expected[k], where + '.' + k)
    elif isinstance(expected, list):
        need(len(actual) == len(expected), where + ': length differs')
        for i, (a, b) in enumerate(zip(actual, expected)):
            exact(a, b, where + '[' + str(i) + ']')
    else:
        need(actual == expected, where + ': value differs')


def uint(v, name):
    need(type(v) is int and 0 <= v < 2**64, name + ': expected u64')
    return v


def context():
    def read(p):
        try:
            return Path(p).read_text()
        except OSError as e:
            return {'error': str(e)}
    return {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'proc_stat': read('/proc/stat'), 'self_status': read('/proc/self/status'),
            'cgroup': read('/proc/self/cgroup'),
            'scope': 'Point observations; no continuous host or sibling exclusivity proof'}


def bindings(engine, authority):
    graph = authority.get('source_graph')
    need(isinstance(graph, str) and len(graph) == 64
         and all(c in '0123456789abcdef' for c in graph), 'source graph unbound')
    files = {str(HERE / 'collect.py'): authority['collector_sha256'],
             str(ACCOUNT): authority['account_native_sha256'],
             str(Path(sys.executable).resolve()): authority['python_sha256'],
             str(PUBLIC / 'functional-workloads.json'): authority['workloads_sha256'],
             str(PUBLIC / 'functional-reference.json'): authority['reference_sha256']}
    sources = authority.get('source_inputs')
    need(isinstance(sources, dict) and sources, 'frozen derivative source closure unbound')
    provenance = authority.get('provenance_inputs')
    need(isinstance(provenance, dict) and provenance, 'build/profile/source proof unbound')
    for group in (sources, provenance):
        for p, h in group.items():
            need(p not in files or files[p] == h, 'contradictory input pin')
            files[p] = h
    for p, h in files.items():
        need(Path(p).is_absolute() and isinstance(h, str) and len(h) == 64,
             'invalid frozen input binding: ' + p)
        need(digest(p) == h, 'input changed: ' + p)
    need(engine.is_file() and not engine.is_symlink(), 'engine must be regular immutable ELF')
    need(engine.stat().st_mode & 0o777 == 0o555, 'engine mode must be0555')
    with engine.open('rb') as f:
        need(f.read(4) == b'\x7fELF', 'not ELF')
    need(digest(engine) == authority['engine_sha256'], 'engine identity changed/unbound')
    return {'engine': str(engine), 'engine_sha256': authority['engine_sha256'],
            'files': files, 'source_graph': authority['source_graph']}


def run_child(engine, row, mode, iterations, input_path, folder, closure):
    folder.mkdir()
    command = [sys.executable, str(ACCOUNT), '--engine', str(engine), '--record',
               str(folder / 'native.json'), '--known-single-process', '--mode', mode,
               '--row', row, '--input', str(input_path), '--iterations', str(iterations)]
    need(digest(engine) == closure['engine_sha256'], 'engine changed before launch')
    save(folder / 'command.json', {'argv': command, 'input_sha256': digest(input_path),
                                 'timeout_s': TIMEOUT_S, 'cleanup_s': CLEANUP_S,
                                 'combined_output_cap': BYTE_CAP})
    p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    start = time.monotonic()
    deadline = start + TIMEOUT_S
    cleanup_start, killed, failure, raw_complete = None, False, None, True
    selector = selectors.DefaultSelector()
    streams = {}
    for name, pipe in [('stdout', p.stdout), ('stderr', p.stderr)]:
        os.set_blocking(pipe.fileno(), False)
        selector.register(pipe, selectors.EVENT_READ, name)
        streams[name] = (folder / name).open('xb')
    seen = 0
    try:
        while selector.get_map() or p.poll() is None:
            now = time.monotonic()
            if failure is None and now >= deadline:
                failure, cleanup_start = 'outer timeout', now
            if cleanup_start is not None:
                if not killed:
                    try:
                        os.killpg(p.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    killed = True
                if now - cleanup_start >= 1:
                    try:
                        os.killpg(p.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                if now - cleanup_start >= CLEANUP_S:
                    raw_complete = False
                    break
            for key, _ in selector.select(0.05):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                streams[key.data].write(data)
                seen += len(data)
                if seen > BYTE_CAP:
                    failure = failure or 'combined output cap exceeded'
                    cleanup_start = cleanup_start or time.monotonic()
                    raw_complete = False
                    # Retain the complete observed cap-crossing chunk. Subsequent
                    # unread pipe bytes are explicitly incomplete, not omitted PASS data.
                    for active in list(selector.get_map().values()):
                        selector.unregister(active.fileobj)
                        active.fileobj.close()
                    break
        if p.poll() is None:
            if cleanup_start is None:
                cleanup_start = time.monotonic()
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                p.wait(timeout=max(0, CLEANUP_S - (time.monotonic() - cleanup_start)))
            except subprocess.TimeoutExpired:
                failure = failure or 'controller reap unconfirmed'
    except BaseException as error:
        failure = failure or 'supervision exception: ' + repr(error)
        raw_complete = False
    finally:
        # Every exceptional exit takes the same bounded owned-group teardown.
        # The initial cleanup clock is never reset, including after a cap/timeout.
        if failure is not None or p.poll() is None:
            cleanup_start = cleanup_start or time.monotonic()
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            while time.monotonic() - cleanup_start < CLEANUP_S:
                p.poll()
                try:
                    os.killpg(p.pid, 0)
                    alive = True
                except ProcessLookupError:
                    alive = False
                if p.returncode is not None and not alive:
                    break
                if time.monotonic() - cleanup_start >= 1:
                    try:
                        os.killpg(p.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                time.sleep(0.01)
            p.poll()
        selector.close()
        for pipe in [p.stdout, p.stderr]:
            if not pipe.closed:
                pipe.close()
        for f in streams.values():
            f.close()
    elapsed = None if cleanup_start is None else time.monotonic() - cleanup_start
    group_gone = True
    if cleanup_start is not None:
        try:
            os.killpg(p.pid, 0)
            group_gone = False
        except ProcessLookupError:
            pass
    terminal = {'controller_pid': p.pid, 'returncode': p.returncode,
                'elapsed_wall_s': time.monotonic() - start, 'failure': failure,
                'raw_capture_complete': raw_complete, 'retained_bytes': seen,
                'cleanup_elapsed_wall_s': elapsed,
                'cleanup_confirmed': p.returncode is not None and group_gone,
                'cleanup_within_deadline': elapsed is None or elapsed <= CLEANUP_S}
    save(folder / 'child-terminal.json', terminal)
    need(p.returncode == 0 and failure is None and raw_complete,
         'native launch failed; retained ' + str(folder))
    need(terminal['cleanup_confirmed'] and terminal['cleanup_within_deadline'], 'cleanup unconfirmed')
    n = load(folder / 'native.json')
    need(n['failure'] is None and n['native_exit_code'] == 0 and n['native_wait_status'] == 0,
         'account_native failure: ' + str(n.get('failure')))
    need(n['supervisor_pid'] == p.pid and n['engine_sha256_before'] == closure['engine_sha256']
         and n['engine_sha256_after'] == closure['engine_sha256'], 'native identity mismatch')
    need(n['argv'] == [str(engine), *command[7:]], 'native argv mismatch')
    need(n['supervisor_affinity'] == sorted(H), 'supervisor affinity mismatch')
    need(n['native_pre_exec']['affinity'] == [14]
         and n['native_post_exec']['affinity'] == [14]
         and n['native_post_exec']['tasks'] == [str(n['native_pid'])]
         and n['native_pre_exec']['pgid'] == p.pid
         and n['native_post_exec']['pgid'] == p.pid, 'native placement mismatch')
    need((folder / 'stderr').stat().st_size == 0, 'unexpected native stderr')
    need(digest(engine) == closure['engine_sha256'], 'engine changed after launch')
    return load(folder / 'stdout'), n


def checked_observation(obs, row, count, expected_work, projection=None):
    fields = {'row', 'completed', 'sink', 'work'} | ({'projection'} if projection is not None
                                                        else {'local_cpu_ns', 'local_wall_ns'})
    need(type(obs) is dict and set(obs) == fields, 'driver output schema mismatch')
    need(obs['row'] == row and uint(obs['completed'], 'completed') == count, 'completed/row mismatch')
    uint(obs['sink'], 'sink')
    exact(obs['work'], {k: v * count for k, v in expected_work.items()}, 'work')
    if projection is not None:
        exact(obs['projection'], projection)
    else:
        need(uint(obs['local_cpu_ns'], 'cpu') > 0 and uint(obs['local_wall_ns'], 'wall') > 0,
             'unresolved zero clock')
    return obs


def reference_report(samples, reference):
    local = [Fraction(x['local_cpu_ns'], x['completed']) for x in samples]
    wall = [Fraction(x['local_wall_ns'], x['completed']) for x in samples]
    guard = [Fraction(str(x['guard_cpu_s'])) * 10**9 / x['completed'] for x in samples]
    stats = reference['measuredStatisticsPerSequence']['localCpuNanoseconds']
    ref = {k: Fraction(v['numerator']) / Fraction(v['denominator']) for k, v in stats.items()}
    def describe(values):
        return {'min': float(min(values)), 'median': float(statistics.median(values)),
                'max': float(max(values))}
    return {'local_cpu_ns_per_sequence': describe(local), 'local_wall_ns_per_sequence': describe(wall),
            'guard_cpu_ns_per_sequence': describe(guard),
            'reference_local_cpu_ns_per_sequence': {k: float(v) for k, v in ref.items()},
            'descriptive_local_div_reference': {
                'median_ratio': float(statistics.median(local) / ref['median']),
                'observed_range_envelope': [float(min(local) / ref['maximum']),
                                            float(max(local) / ref['minimum'])]},
            'controlled_inner_search_ratio': None,
            'scope': 'Cross-host/artifact descriptive only; search local is Rook2 owned-call including '
                     'root preparation, compared with reference enclosing local scope. No inner ratio, '
                     'synthetic subtraction, PMU inference or performance qualification.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--stage', choices=['calibrate', 'collect'], required=True)
    ap.add_argument('--calibration', type=Path)
    a = ap.parse_args()
    engine, out = a.engine.absolute(), a.output.resolve()
    need(engine == engine.resolve(), 'use canonical nonsymlink engine path')
    need(out.is_absolute() and not out.exists(), 'output must be fresh')
    need(not out.is_relative_to(Path('/home/legolas/rook2')), 'raw output must be external to repo')
    need(os.sched_getaffinity(0) == H, 'collector must run on exact H affinity')
    need(os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp', 'TMPDIR mismatch')
    for k in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'LLVM_PROFILE_FILE', 'PYTHONPATH', 'PYTHONSTARTUP']:
        need(not os.environ.get(k), 'unsupported environment: ' + k)
    authority_path = HERE / 'execution-clearance.json'
    authority = load(authority_path)
    need(authority.get('launch_authorized') is True and authority.get('all_owned_jobs_closed') is True
         and authority.get('quiet_point_verified') is True and authority.get('known_single_process') is True
         and authority.get('allow_' + a.stage) is True, 'INERT: root activation required')
    closure = bindings(engine, authority)
    workloads = load(PUBLIC / 'functional-workloads.json')
    reference = load(PUBLIC / 'functional-reference.json')
    units = {u['id']: u for u in workloads['units']}
    refs = {u['id']: u for u in reference['units']}
    if a.stage == 'collect':
        need(a.calibration is not None, 'collection requires closed calibration')
        calibration = load(a.calibration)
        need(calibration['complete'] and calibration['stage'] == 'calibrate'
             and calibration['input_closure'] == closure, 'calibration identity mismatch')
        t = load(a.calibration.parent / 'tool-terminal.json')
        need(t['actual_tool_terminal_observed'] and t['exit_code'] == 0, 'actual calibration terminal pending')
        counts = calibration['counts']
        need(set(counts) == {r[0] for r in ROWS}, 'calibration count rows mismatch')
    else:
        need(a.calibration is None, 'calibration stage accepts no previous probe')
        counts = {}
    out.mkdir(parents=True)
    save(out / 'input-closure.json', closure)
    save(out / 'authority-used.json', authority)
    save(out / 'context-before.json', context())
    result = {'complete': False, 'stage': a.stage, 'failure': None, 'input_closure': closure,
              'authority_sha256': digest(authority_path), 'counts': counts, 'rows': [],
              'native_launches': 0, 'performance_qualification': False}
    try:
        for row, unit_id, probe_count, max_count in ROWS:
            d = out / row
            d.mkdir()
            unit = units[unit_id]
            save(d / 'input.json', unit['workload']['request']['input'])
            expected = unit['expectedProjection']
            work = ({'chargedSearchUnits': 54, 'chargedRelationQueries': 234} if row == 'search'
                    else {'chargedSearchUnits': 0, 'chargedRelationQueries': sum(
                        x['relationQueries'] for x in expected['results']) if row.startswith('eval-') else 0})
            samples, verify_sinks = [], []
            schedule = [('probe', probe_count)] if a.stage == 'calibrate' else [
                ('warmup', counts[row]), ('measured-1', counts[row]),
                ('measured-2', counts[row]), ('measured-3', counts[row])]
            for role, count in schedule:
                need(type(count) is int and 1 <= count <= max_count, 'invalid frozen count')
                if a.stage == 'collect':
                    result['native_launches'] += 1
                    before, _ = run_child(engine, row, 'verify', 1, d / 'input.json', d / (role + '-before'), closure)
                    checked_observation(before, row, 1, work, expected)
                    verify_sinks.append(before['sink'])
                result['native_launches'] += 1
                obs, native = run_child(engine, row, 'measure', count, d / 'input.json', d / role, closure)
                checked_observation(obs, row, count, work)
                if a.stage == 'collect':
                    need(obs['local_cpu_ns'] >= 50000000, 'batch CPU unresolved below50ms; no retiming')
                    result['native_launches'] += 1
                    after, _ = run_child(engine, row, 'verify', 1, d / 'input.json', d / (role + '-after'), closure)
                    checked_observation(after, row, 1, work, expected)
                    verify_sinks.append(after['sink'])
                    need(before['sink'] == after['sink'], 'before/after full consumer sink differs')
                samples.append({**obs, 'role': role, 'native_pid': native['native_pid'],
                                'guard_user_cpu_s': native['user_cpu_s'],
                                'guard_system_cpu_s': native['system_cpu_s'],
                                'guard_cpu_s': native['total_cpu_s'], 'guard_wall_ns': native['wall_ns']})
                need(bindings(engine, authority) == closure, 'input closure changed')
            if a.stage == 'calibrate':
                cpu = samples[0]['local_cpu_ns']
                need(cpu >= 100000, 'probe resolution below100us; no second probe')
                count = min(max_count, max(512 if row == 'search' else 256,
                                         (TARGET_NS * probe_count + cpu - 1) // cpu))
                prediction = Fraction(cpu * count, probe_count)
                need(250000000 <= prediction <= 1000000000, 'count clamp cannot resolve target; stop')
                counts[row] = count
                summary = {'probe': samples[0], 'frozen_iterations': count,
                           'predicted_cpu_ns': float(prediction), 'target_cpu_ns': TARGET_NS}
            else:
                need(len({x['sink'] for x in samples}) == 1 and len(set(verify_sinks)) == 1,
                     'same-count consumer sink differs across batches')
                summary = {'iterations': counts[row], 'samples': samples,
                           **reference_report(samples[1:], refs[unit_id])}
            result['rows'].append({'row': row, 'unit': unit_id, **summary})
            save(d / 'summary.json', result['rows'][-1])
        need(result['native_launches'] == (4 if a.stage == 'calibrate' else 48), 'launch count mismatch')
        result['complete'] = True
    except BaseException as error:
        result['failure'] = repr(error)
        raise
    finally:
        try:
            result['input_closure_after_exact'] = bindings(engine, authority) == closure
        except BaseException as error:
            result['input_closure_after_exact'] = False
            result['failure'] = result['failure'] or repr(error)
        result['complete'] = result['complete'] and result['input_closure_after_exact']
        save(out / 'context-after.json', context())
        save(out / ('calibration.json' if a.stage == 'calibrate' else 'result.json'), result)
    need(result['complete'], 'study incomplete')
    if a.stage == 'collect':
        with (out / 'summary.csv').open('x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['row', 'iterations', 'local_cpu_ns_min', 'local_cpu_ns_median',
                             'local_cpu_ns_max', 'guard_cpu_ns_median', 'reference_cpu_ns_median',
                             'descriptive_ratio', 'controlled_inner_search_ratio'])
            for x in result['rows']:
                t = x['local_cpu_ns_per_sequence']
                writer.writerow([x['row'], x['iterations'], t['min'], t['median'], t['max'],
                                 x['guard_cpu_ns_per_sequence']['median'],
                                 x['reference_local_cpu_ns_per_sequence']['median'],
                                 x['descriptive_local_div_reference']['median_ratio'], 'unavailable'])
    print(json.dumps({'complete': result['complete'], 'stage': a.stage,
                      'rows': len(result['rows']), 'native_launches': result['native_launches']}))


if __name__ == '__main__':
    main()
