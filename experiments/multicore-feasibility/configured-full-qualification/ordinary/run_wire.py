#!/usr/bin/python3
"""Keep the original Process initializer and checker; gate only first send."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import time

base = Path(sys.argv[1]).resolve()
plan = json.loads((base/'plan.json').read_text())
stage = base/'wire'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sorted(os.sched_getaffinity(0)) == plan['helperCpus']
for path, digest in plan['pins'].items():
    assert sha(path) == digest, path
namespace = runpy.run_path(plan['wireChecker'], run_name='original_wire_checker_metadata_observed')
Process = namespace['Process']
original_init, original_send = Process.__init__, Process.send
pids, released = [], set()


def init(self, engine, directory):
    original_init(self, engine, directory)
    pids.append(dict(case=directory.name, pid=self.child.pid, argv=self.child.args,
                     observer_after_original_init=True))


def send(self, records):
    if self.child.pid not in released:
        record = stage/'native'/f'{self.child.pid}.json'
        ready_path = Path(str(record)+'.ready')
        deadline = time.monotonic()+12
        while not ready_path.exists():
            assert time.monotonic() < deadline, 'external wire placement ready deadline'
            time.sleep(.001)
        ready = json.loads(ready_path.read_text())
        affinities = ready['native_post_exec']['task_affinities']
        assert ready['schema'] == 'rook2-external-placement-ready-v1'
        assert ready['engine'] == plan['image'] and ready['supervisor_pid'] == self.child.pid
        assert ready['expected_threads'] == plan['threads'] and len(affinities) == plan['threads']
        assert affinities[str(ready['native_pid'])] == [14]
        assert all(mask == [6] for tid, mask in affinities.items() if tid != str(ready['native_pid']))
        data = ('\n'.join(records)+'\n').encode('ascii')
        release = time.monotonic_ns()
        assert release >= int(ready['ready_monotonic_ns'])
        gate = dict(schema='rook2-placement-input-gate-v1', implementation='python-wire',
            gate_sha256=sha(__file__), ready_path=str(ready_path), ready_sha256=sha(ready_path),
            native_pid=ready['native_pid'], supervisor_pid=self.child.pid,
            release_monotonic_ns=str(release), first_write_bytes=len(data),
            first_write_sha256=hashlib.sha256(data).hexdigest())
        with Path(str(record)+'.input-gate.json').open('x') as stream:
            json.dump(gate, stream, indent=2)
            stream.write('\n')
        released.add(self.child.pid)
    return original_send(self, records)


Process.__init__, Process.send = init, send
sys.argv = [plan['wireChecker'], '--engine', plan['wireLauncher'], '--output', str(stage/'output')]
try:
    code = namespace['main']()
    assert code == 0, code
    receipt = json.loads((stage/'output/receipt.json').read_text())
    assert receipt['pass'] and len(receipt['results']) == 8
    assert sum(len(row['searches']) for row in receipt['results']) == 24
finally:
    with (stage/'native-pids.json').open('x') as stream:
        json.dump(pids, stream, indent=2)
        stream.write('\n')
