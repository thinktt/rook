#!/usr/bin/env python3
"""Run existing released comparators against WASM; keep raw results outside Git."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--spec', required=True, type=Path)
p.add_argument('--output', required=True, type=Path)
p.add_argument('--resume', type=Path, help='reuse completed standard54/component reports with identical engine/Node/spec inputs')
p.add_argument('--dist', type=Path, default=ROOT/'wasm/dist')
a = p.parse_args()
a.spec = a.spec.resolve()
a.output = a.output.resolve()
a.dist = a.dist.resolve()
a.output.mkdir(parents=True, exist_ok=False)
os.sched_setaffinity(0, {14})
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
inputs = [p for p in (ROOT/'wasm').rglob('*') if p.is_file() and 'target' not in p.parts and p.suffix in {'.rs', '.mjs', '.js', '.py', '.toml', '.lock'}]
inputs += [ROOT/'wasm/package.json', ROOT/'Cargo.toml', ROOT/'Cargo.lock', ROOT/'diagnostic/Cargo.toml', ROOT/'diagnostic/Cargo.lock']
inputs += list(a.dist.glob('*.wasm'))
inputs += list((ROOT/'src').rglob('*.rs')) + list((ROOT/'diagnostic/src').rglob('*.rs'))
inputs += [p for p in (a.spec/'conformance').rglob('*') if p.is_file() and p.suffix in {'.mjs', '.json'}]
pins = {str(p): sha(p) for p in inputs}
(a.output/'inputs.json').write_text(json.dumps(pins, indent=2)+'\n')
deadline = time.monotonic() + 10800
summary = dict(complete=False, stages=[], cpu=14, measurementClaim=False, full3288=False,
               wireAffinity='CPU0 bootstrap; existing checker housekeeping policy',
               note='Released runner executable hashes identify Node/the launcher. inputs.json additionally binds the actual WASM modules and JS host.')

previous = None
if a.resume:
    a.resume = a.resume.resolve()
    previous = json.loads((a.resume/'summary.json').read_text())
    old_pins = json.loads((a.resume/'inputs.json').read_text())
    # A completed report qualifies exact module bytes and their execution host.
    # Browser-only changes are irrelevant to Node; a changed DIAG module requires
    # fresh component checks but does not invalidate an unchanged ordinary module.
    common_host = {'runtime.mjs', 'queue.mjs'}
    hosts = {
        'standard54': common_host | {'node-worker.mjs', 'rook.mjs', 'rook.wasm'},
        'mandatory': common_host | {'rook-diag.mjs', 'rook-diag.wasm'},
    }
    eligibility = {}
    for kind, names in hosts.items():
        required = {path: digest for path, digest in pins.items()
                    if Path(path).name in names or a.spec in Path(path).parents}
        eligibility[kind] = all(old_pins.get(path) == digest for path, digest in required.items())
    summary['resume'] = dict(path=str(a.resume), priorInputsSha256=sha(a.resume/'inputs.json'),
                             priorSummarySha256=sha(a.resume/'summary.json'), eligibility=eligibility)

def write():
    (a.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')

def run(name, command, timeout=3600):
    stage = a.output/name
    stage.mkdir()
    kind = 'standard54' if name == 'standard54' else 'mandatory' if name.startswith('mandatory-') else None
    if previous and kind and summary['resume']['eligibility'][kind]:
        match = next((x for x in previous['stages'] if x['name'] == name and x.get('exit') == 0), None)
        if match:
            assert match['command'] == command and not match.get('timeoutExpired')
            origin = a.resume/name
            assert (origin/'stderr').stat().st_size == 0
            for stream in ['stdout', 'stderr']: shutil.copyfile(origin/stream, stage/stream)
            summary['stages'].append(dict(name=name, command=command, exit=0, reusedFrom=str(origin),
                                          originalStart=match.get('start') or match['originalStart'],
                                          originalStop=match.get('stop') or match['originalStop'],
                                          stdoutSha256=sha(origin/'stdout')))
            write()
            return stage
    row = dict(name=name, command=command, start=time.time(), timeout=timeout)
    summary['stages'].append(row)
    write()
    with (stage/'stdout').open('xb') as out, (stage/'stderr').open('xb') as err:
        child = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err, start_new_session=True)
        row['pid'] = child.pid
        write()
        try:
            stage_deadline = min(deadline, time.monotonic() + timeout)
            while child.poll() is None:
                if time.monotonic() >= stage_deadline:
                    raise subprocess.TimeoutExpired(command, timeout)
                if sum(f.stat().st_size for f in a.output.rglob('*') if f.is_file()) > 2*1024**3:
                    raise RuntimeError('2 GiB evidence budget exceeded')
                try: child.wait(timeout=2)
                except (subprocess.TimeoutExpired, RuntimeError): pass
            row['exit'] = child.returncode
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            row['timeoutExpired'] = True
            raise
        finally:
            row['stop'] = time.time()
            write()
    assert row['exit'] == 0, name+' failed; see stage stdout/stderr'
    assert (stage/'stderr').stat().st_size == 0, name+' unexpected stderr'
    return stage

try:
    diag = ['/usr/bin/node', str(ROOT/'wasm/rook-diag.mjs'), str(a.dist/'rook-diag.wasm')]
    engine = ['/usr/bin/node', str(ROOT/'wasm/rook.mjs'), '--wasm', str(a.dist/'rook.wasm')]
    # Cheap integrated discriminator first, before thousands of fresh diagnostic VMs.
    stage = run('standard54', ['/usr/bin/node', str(a.spec/'conformance/profiling/replay-check.mjs'), '--', *engine])
    report = json.loads((stage/'stdout').read_text())
    assert report['status'] == 'pass' and len(report['results']) == 54
    summary['standard54'] = 54
    write()
    files = []
    for file in sorted((a.spec/'conformance/fixtures').glob('*.json')):
        cases = json.loads(file.read_text())['cases']
        if any(c['request']['operation'] in {'output.analysisCandidateReport', 'search.analysisRootSequence'} for c in cases):
            continue
        files.append((file, len(cases)))
    summary['mandatory'] = dict(files=0, cases=0)
    # One unchanged runner invocation per file gives durable progress without case polling.
    for file, count in files:
        stage = run('mandatory-'+file.stem, ['/usr/bin/node', str(a.spec/'conformance/run.mjs'), '--fixtures', str(file), '--timeout', '60000', '--', *diag], 3600)
        report = json.loads((stage/'stdout').read_text())
        assert report['pass'] and len(report['results']) == count
        summary['mandatory']['files'] += 1
        summary['mandatory']['cases'] += count
        write()
    gate = a.spec/'conformance/gate-replay'
    for name, tool in [('games12', 'run.mjs'), ('continuity', 'continuous.mjs')]:
        report = a.output/name/'report.json'
        run(name, ['/usr/bin/node', str(gate/tool), '--report', str(report), '--', *engine], 7200)
        assert json.loads(report.read_text())['pass']
    for name in ['seed-command', 'seed-persistence']:
        run(name, ['/usr/bin/node', str(gate/(name+'-controls.mjs')), '--', *engine], 300)
    run('combine', ['/usr/bin/node', str(gate/'combine.mjs'), '--report', str(a.output/'combined.json'), '--continuous', str(a.output/'continuity/report.json'), str(a.output/'games12/report.json')], 60)
    assert json.loads((a.output/'combined.json').read_text())['completeFocusedReplay']
    # This checker accepts a single executable; the shebang runner defaults to wasm/dist.
    assert a.dist == ROOT/'wasm/dist', 'wire checker currently uses the default dist'
    run('wire8', ['taskset', '-c', '0', '/usr/bin/python3', str(ROOT/'tools/check_live.py'), '--engine', str(ROOT/'wasm/rook.mjs'), '--output', str(a.output/'wire8/results')], 600)
    wire = json.loads((a.output/'wire8/results/receipt.json').read_text())
    assert wire['pass'] and len(wire['results']) == 8
    assert all(sha(Path(path)) == digest for path, digest in pins.items()), 'input changed during qualification'
    summary['complete'] = True
except BaseException as error:
    summary['failure'] = str(error)
    write()
    raise
write()
print(json.dumps(summary), flush=True)
