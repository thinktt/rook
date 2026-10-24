"""Scoped adapters for unchanged collection and independent raw replay auditors.

Importing this module does not launch processes or mutate imported source files.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL = HERE.parent/'full-split-production'
ACCOUNT = HERE/'account_threads.py'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
CONTROL_SHA = '64e01d986242f43f2063887b164e06e8201460fd5aefca5d6494a2f4b3634323'
CASES = ['profile-35', 'profile-08', 'profile-04', 'profile-43']
NAMES = ['control', 'cleaned1', 'cleaned2']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def bad(value):
        raise ValueError('nonfinite JSON: '+value)
    return json.loads(path.read_text(), parse_constant=bad)


def write(path, value):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temporary.replace(path)


def schedule():
    result = []
    for case in CASES:
        result += [dict(case=case, variant=name, warmup=True, repeat=0) for name in NAMES]
        for repeat in range(3):
            result += [dict(case=case, variant=name, warmup=False, repeat=repeat+1)
                       for name in NAMES[repeat:]+NAMES[:repeat]]
    assert len(result) == 48
    return result


def variants(control, candidate):
    return dict(control=dict(path=str(control), budget=2, options=['--research-threads=2']),
                cleaned1=dict(path=str(candidate), budget=1, options=['--threads=1']),
                cleaned2=dict(path=str(candidate), budget=2, options=['--threads=2']))


def ready_record(directory, supervisor_pid, image, budget, deadline):
    path = directory/'native.json.ready'
    while not path.exists():
        if time.monotonic() >= deadline:
            raise RuntimeError('external placement ready deadline')
        time.sleep(.001)
    ready = read(path)
    assert ready['schema'] == 'rook2-external-placement-ready-v1'
    assert ready['supervisor_pid'] == supervisor_pid and ready['engine'] == str(image)
    assert ready['engine_sha256'] == sha(image) and ready['launcher_sha256'] == sha(ACCOUNT)
    assert ready['expected_threads'] == budget
    affinities = ready['native_post_exec']['task_affinities']
    assert len(affinities) == budget and affinities[str(ready['native_pid'])] == [14]
    assert all(mask == [6] for tid, mask in affinities.items() if tid != str(ready['native_pid']))
    return ready


def audit_placement(directory, native, hashes):
    ready_path, gate_path = directory/'native.json.ready', directory/'native.json.input-gate.json'
    ready, gate = read(ready_path), read(gate_path)
    assert native['placement_error'] is None
    assert native['ready_path'] == str(ready_path) and native['ready_sha256'] == sha(ready_path)
    assert ready['schema'] == 'rook2-external-placement-ready-v1'
    for key in ['native_pid', 'supervisor_pid', 'expected_threads', 'native_pre_exec', 'native_post_exec']:
        assert ready[key] == native[key]
    assert ready['engine'] == native['engine']
    assert ready['engine_sha256'] == native['engine_sha256_before']
    assert ready['launcher_sha256'] == native['launcher_sha256'] == hashes[str(ACCOUNT)]
    before = ready['task_affinities_before_pinning']
    assert set(before) == set(native['native_post_exec']['task_affinities'])
    assert all(mask and set(mask) <= {6, 14} for mask in before.values())
    assert gate['schema'] == 'rook2-placement-input-gate-v1'
    assert gate['ready_path'] == str(ready_path) and gate['ready_sha256'] == sha(ready_path)
    assert gate['native_pid'] == native['native_pid'] and gate['supervisor_pid'] == native['supervisor_pid']
    raw_path = directory/('wire/stdin.raw' if gate['implementation'] == 'node-sync' else 'stdin.raw')
    raw = raw_path.read_bytes()
    size = gate['first_write_bytes']
    assert type(size) is int and 0 < size <= len(raw)
    assert hashlib.sha256(raw[:size]).hexdigest() == gate['first_write_sha256']
    if gate['implementation'] == 'node-sync':
        assert gate['gate_sha256'] == hashes[str(HERE/'placement_gate.mjs')]
        case = read(directory/'launch.json')['step']['case']
        workload = next(row for row in read(SPEC/'workloads.json')['cases'] if row['id'] == case)
        setup = ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
        assert raw[:size] == setup
    else:
        assert gate['implementation'] == 'python-idle'
        assert gate['gate_sha256'] == hashes[str(HERE/'collect.py')]
        assert raw[:size] == b'cm_parm\n'
    assert native['start_monotonic_ns'] <= int(ready['ready_monotonic_ns']) <= int(gate['release_monotonic_ns']) < native['reaped_monotonic_ns']
    if (directory/'wire/receipt.json').exists():
        tap = read(directory/'wire/receipt.json')
        assert int(gate['release_monotonic_ns']) <= int(tap['searches'][0]['startMonotonicNs'])
    return dict(readySha256=sha(ready_path), inputGateSha256=sha(gate_path))


def native_receipt(path, image, budget, options, hashes):
    native = read(path)
    assert native['schema'] == 'rook2-native-wait4-v1' and native['known_single_process']
    assert native['failure'] is None and native['native_exit_code'] == native['native_wait_status'] == 0
    assert native['exec_error'] is None and native['supervisor_signals'] == []
    assert native['engine'] == str(image)
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
    assert native['launcher_sha256'] == hashes[str(ACCOUNT)]
    assert sha(Path(native['python_executable'])) == native['python_executable_sha256']
    assert native['argv'] == [str(image), *options] and native['expected_threads'] == budget
    assert set(native['supervisor_affinity']) and set(native['supervisor_affinity']) <= HELPERS
    assert native['inherited_supervisor_affinity'] == sorted(HELPERS)
    assert native['native_pre_exec'] == dict(pid=native['native_pid'], pgid=native['supervisor_pid'], affinity=[6, 14])
    observed = native['native_post_exec']
    assert observed['path'] == str(image) and observed['pgid'] == native['supervisor_pid'] and observed['affinity'] == [14]
    affinities = observed['task_affinities']
    assert sorted(observed['tasks']) == sorted(affinities)
    assert len(affinities) == budget and affinities[str(native['native_pid'])] == [14]
    assert all(mask == [6] for tid, mask in affinities.items() if tid != str(native['native_pid']))
    assert native['wall_ns'] == native['reaped_monotonic_ns']-native['start_monotonic_ns'] > 0
    assert native['total_cpu_s'] == native['user_cpu_s']+native['system_cpu_s'] > 0
    assert native['maxrss_linux_kib'] > 0
    for pid in [native['native_pid'], native['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists(), 'recorded PID currently live; inspect possible reuse'
    audit_placement(path.parent, native, hashes)
    return native


# Only these imported module objects are adapted. Their files remain unchanged.
train = module('usable_full_original_train', ORIGINAL/'train.py')
train.ACCOUNT, train.ROOT = ACCOUNT, HERE
audit = module('usable_full_original_reconcile', ORIGINAL/'reconcile.py')
audit.ACCOUNT, audit.ROOT, audit.native_receipt = ACCOUNT, HERE, native_receipt


def run_lifetime(directory, step, image, budget, options, deadline, hashes):
    started = time.monotonic_ns()
    row = train.run_lifetime(directory, step, image, budget, options, deadline)
    # Verify ready/gate artifacts before admitting this row, using the independent auditor.
    native = native_receipt(directory/'native.json', image, budget,
                            [*options, *read(SPEC/'replay-oracle.json')['mode']], hashes)
    row['placement'] = audit_placement(directory, native, hashes)
    row['controllerStartMonotonicNs'] = started
    row['controllerEndMonotonicNs'] = time.monotonic_ns()
    return row


def admission(build, control, candidate):
    # Explicit-path import avoids name collisions with this directory's collect.py.
    # The original reversed-full import resolves its original train/collect modules.
    old_path = list(sys.path)
    try:
        sys.path.insert(0, str(ORIGINAL))
        old = module('usable_full_reversed_admission', HERE.parent/'reversed-full/collect.py')
        return old.admit(build, control, candidate)
    finally:
        sys.path[:] = old_path
