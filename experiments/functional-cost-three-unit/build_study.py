#!/usr/bin/env python3
"""Finite, parent-invoked build/training stages for the functional three-unit study.

No stage runs without --execute. Example (after source/inputs are frozen):
  taskset -c 0-5,8-13 python3 build_study.py build-instrumented-wire \
    --source-manifest FROZEN.json --execute
Stages, in order: build-instrumented-wire, build-instrumented-functional, train,
build-use. Stage directories must be absent; failures are preserved, never retried.

B/inputs/{eval-scalar,eval-coherent,position,search}.json contains only the original
public request.input. B/expected/{row}.json contains only its public expectedProjection.
Expected answers are never passed to the native functional binary. Its verify CLI
is --mode verify --row ROW --input FILE --iterations 1. The parent supplies actual
outer tool-terminal observations separately; this script records child exits only.

Canonical and W/tools stay untouched. B-local build.py extends only its binary
PGO admission guard; B-local archive_build.py derives the actual frozen bin name.
Source/tool/config/CPU/profile checks and source archives remain canonical method.
The mixed 54 wire + 4 functional training profile is study-specific, NOT the
reference build's profile or a production-equivalent profile.
"""
from __future__ import annotations

import argparse
import ctypes
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import sys
import time
import tomllib

ROOT = Path('/home/legolas/rook2')
W = Path('/home/legolas/rook2-work/imp2-functional-cost-20261020-01')
B = Path('/home/legolas/rook2-experiments/functional-cost-three-unit-20261020-01')
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
TARGET = 'x86_64-unknown-linux-gnu'
ROWS = ('eval-scalar', 'eval-coherent', 'position', 'search')
EXPECTED_WORK = {'eval-scalar': (0, 39), 'eval-coherent': (0, 39),
                 'position': (0, 0), 'search': (54, 234)}
MAX_RUN_LOG = 8 * 1024 * 1024
MAX_ALL_LOG = 128 * 1024 * 1024
BUILD_TIMEOUT = 300
OTHER_TIMEOUT = 600
STAGES = ('build-instrumented-wire', 'build-instrumented-functional', 'train', 'build-use')
CANONICAL = {
    'build.py': '9ec72da0c15c07eee8c5ef1a63729ffdef6fc048baa37c58d9eed1bbe3d4df4e',
    'archive_build.py': 'ea3944cf7ce09a3e6c4476644083324ac8fabec12cd7436f8536a872f3ff4b86',
}

# This is an offline reuse of the ORIGINAL public checker, not an answer model.
RECHECK_JS = r"""import assert from 'node:assert/strict';
import fs from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const report=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
assert.equal(report.status,'pass');
assert.deepEqual(report.selectedCases,workloads.cases.map(c=>c.id));
assert.equal(report.results.length,54);
for(const [i,row] of report.results.entries()){
 const c=workloads.cases[i],e=oracle.cases.find(x=>x.id===c.id);
 assert.equal(row.case,c.id);checkReplay(row,c,e);
}
console.log(JSON.stringify({offlineOnly:true,originalCheckReplayCount:54}));
"""


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def snapshot():
    paths = [W / 'Cargo.toml', W / 'Cargo.lock']
    paths += sorted(p for p in (W / 'src').rglob('*') if p.is_file())
    paths += [W / n for n in ('build.rs', 'rust-toolchain', 'rust-toolchain.toml') if (W / n).is_file()]
    source = {str(p.relative_to(W)): sha(p) for p in paths}
    tools = {str(p.relative_to(W)): sha(p) for p in sorted((W / 'tools').rglob('*'))
             if p.is_file() and '__pycache__' not in p.parts
             and p.suffix in ('.py', '.c', '.rs', '.md', '.sh', '.mjs')}
    return source, tools


def tooling():
    """Write/revalidate two explicit private helper deltas, never canonical tools."""
    directory = B / 'build-study-tools'
    texts = {}
    patches = []
    for name, expected in CANONICAL.items():
        origin = ROOT / 'tools' / name
        need(sha(origin) == expected, 'canonical helper changed: ' + name)
        need(sha(W / 'tools' / name) == expected, 'W helper changed: ' + name)
        original = origin.read_text()
        if name == 'build.py':
            old = 'if (args.pgo_generate or args.pgo_use) and args.binary_name != "rook2":'
            new = 'if (args.pgo_generate or args.pgo_use) and args.binary_name not in ("rook2", "rook2-functional-cost"):'
        else:
            old = "frozen = args.build / 'rook2-exact'\n    if not frozen.exists():\n        frozen = args.build / 'rook2-diag-exact'"
            new = "frozen = args.build / (record['binary_name'] + '-exact')"
        need(original.count(old) == 1, 'private helper adaptation anchor changed')
        changed = original.replace(old, new, 1)
        texts[name] = changed
        patches.extend(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
                       fromfile='canonical/tools/' + name, tofile='private/' + name))
    texts['helper-adaptation.patch'] = ''.join(patches)
    texts['recheck.mjs'] = RECHECK_JS
    if not directory.exists():
        directory.mkdir()
        for name, text in texts.items():
            (directory / name).write_text(text)
    need({p.name for p in directory.iterdir()} == set(texts), 'unexpected private tooling files')
    for name, text in texts.items():
        need((directory / name).read_text() == text, 'private helper bytes changed: ' + name)
    return {str(directory / n): sha(directory / n) for n in texts}


def input_guard(manifest_path):
    source, tools = snapshot()
    frozen = load(manifest_path)
    need(frozen.get('files_sha256') == source | tools,
         'parent manifest must bind exact current source+tool snapshot via files_sha256')
    lock = tomllib.loads((W / 'Cargo.lock').read_text())
    versions = [p['version'] for p in lock['package'] if p['name'] == 'serde_json']
    need(versions == ['1.0.154'], 'expected locked serde_json1.0.154')
    inputs = [B / family / (row + '.json') for row in ROWS for family in ('inputs', 'expected')]
    inputs += [SPEC / n for n in ('workloads.json', 'replay-oracle.json', 'replay-check.mjs', 'benchmark.mjs')]
    inputs += [manifest_path, Path(__file__).resolve(), ROOT / 'tools/build.py', ROOT / 'tools/archive_build.py']
    pins = {str(p): sha(p) for p in inputs}
    need(load(B / 'inputs/eval-scalar.json') == load(B / 'inputs/eval-coherent.json'), 'evaluation input mismatch')
    need(load(B / 'expected/eval-scalar.json') == load(B / 'expected/eval-coherent.json'), 'evaluation expected mismatch')
    record = dict(schema='rook2-functional-cost-build-inputs-v1', source_root=str(W),
                  engine_source_sha256=source, tool_source_sha256=tools,
                  input_sha256=pins, private_tool_sha256=tooling(), rows=list(ROWS),
                  expected_work={k: dict(zip(('chargedSearchUnits', 'chargedRelationQueries'), v))
                                 for k, v in EXPECTED_WORK.items()},
                  training='54 original wire lifetimes plus4 explicit functional verify lifetimes',
                  identity_limit='Canonical build source/tool/lock/config receipts; not a bundled registry/runtime closure',
                  performance='Training only; no production/reference equivalence or timing claim')
    path = B / 'build-study-inputs.json'
    if path.exists():
        need(load(path) == record, 'frozen study inputs changed')
    else:
        save(path, record)
    return record


def descendants():
    """Only this stage's own descendants/adoptees; no process-name matching."""
    states = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            text = (path / 'stat').read_text()
            fields = text[text.rfind(')') + 2:].split()
            states[int(path.name)] = (int(fields[1]), int(fields[19]), fields[0])
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    owned = {os.getpid()}
    changed = True
    while changed:
        children = {pid for pid, (parent, _, _) in states.items() if parent in owned}
        changed = not children <= owned
        owned |= children
    return {pid: states[pid] for pid in owned - {os.getpid()}}


class Runner:
    """Finite pipes and pidfd ownership; detached replay children remain owned."""
    def __init__(self, directory, seconds):
        self.directory = directory
        self.deadline = time.monotonic() + seconds - 5  # reserve5s cleanup
        self.log_bytes = sum(p.stat().st_size for p in (B / 'stage-records').rglob('*')
                             if p.is_file() and p.suffix in ('.stdout', '.stderr'))
        libc = ctypes.CDLL(None, use_errno=True)
        need(libc.prctl(36, 1, 0, 0, 0) == 0, 'cannot establish stage-owned subreaper')
        need(hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'), 'pidfd support required')

    def run(self, name, command, env=None, timeout=None):
        need(time.monotonic() < self.deadline, 'stage deadline exhausted')
        prefix = self.directory / name
        need(not prefix.with_suffix('.child.json').exists(), 'command already recorded')
        save(prefix.with_suffix('.command.json'), dict(argv=command, cwd=str(W),
             environment_delta=env or {}, helper_affinity=sorted(os.sched_getaffinity(0))))
        cap = min(MAX_RUN_LOG, MAX_ALL_LOG - self.log_bytes)
        need(cap > 0, 'aggregate captured-log cap exhausted')
        end = min(self.deadline, time.monotonic() + (timeout or OTHER_TIMEOUT))
        proc = subprocess.Popen(command, cwd=W, env={**os.environ, **(env or {})},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        pid = proc.pid
        known = {}
        observed = kept = 0
        failure = None
        selector = selectors.DefaultSelector()
        streams = {proc.stdout: prefix.with_suffix('.stdout').open('xb'),
                   proc.stderr: prefix.with_suffix('.stderr').open('xb')}
        for stream in streams:
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ)

        def watch():
            for child, (_, start, _) in descendants().items():
                key = (child, start)
                if key not in known:
                    try:
                        known[key] = os.pidfd_open(child)
                    except ProcessLookupError:
                        pass

        def kill_owned():
            watch()
            for fd in known.values():
                try:
                    signal.pidfd_send_signal(fd, signal.SIGKILL)
                except ProcessLookupError:
                    pass

        began = time.monotonic()
        cleanup_end = None
        try:
            while selector.get_map() or proc.poll() is None:
                watch()
                if failure is None and time.monotonic() >= end:
                    failure = 'deadline'
                if failure:
                    kill_owned()
                    if cleanup_end is None:
                        cleanup_end = time.monotonic() + 5
                    need(time.monotonic() < cleanup_end, 'owned-child cleanup exceeded5s')
                for key, _ in selector.select(0.05):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    observed += len(data)
                    take = data[:max(0, cap - kept)]
                    streams[key.fileobj].write(take)
                    kept += len(take)
                    if observed > cap:
                        failure = 'combined stdout/stderr cap; retained prefix only'
            code = proc.wait(timeout=max(0.01, end + 5 - time.monotonic()))
            # No build/replay descendant may survive a successful helper return.
            live = {p: v for p, v in descendants().items() if v[2] != 'Z'}
            if live:
                failure = failure or 'live descendant after helper exit'
                kill_owned()
            for child in list(descendants()):
                if child != pid:
                    try:
                        os.waitpid(child, os.WNOHANG)
                    except ChildProcessError:
                        pass
        except BaseException:
            kill_owned()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            raise
        finally:
            for stream, output in streams.items():
                output.close()
                stream.close()
            selector.close()
            for fd in known.values():
                os.close(fd)
            self.log_bytes += kept
            save(prefix.with_suffix('.child.json'), dict(actual_child_return_observed=proc.returncode is not None,
                 pid=pid, exit_code=proc.returncode, argv=command, elapsed_s=time.monotonic() - began,
                 captured_bytes=kept, observed_pipe_bytes_lower_bound=observed,
                 capture_complete=failure is None, failure=failure,
                 outer_tool_terminal_observed=False,
                 stdout_sha256=sha(prefix.with_suffix('.stdout')),
                 stderr_sha256=sha(prefix.with_suffix('.stderr'))))
        need(code == 0 and failure is None, 'failed child: ' + name)
        return dict(pid=pid, exit_code=code, stdout=prefix.with_suffix('.stdout'),
                    stderr=prefix.with_suffix('.stderr'), terminal=prefix.with_suffix('.child.json'))


def verify_build(name, expected_mode, inputs):
    directory = B / name
    receipt = load(directory / 'receipt.json')
    need(receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot', 'unstable build')
    need(receipt['mode'] == 'generic' and receipt['target_cpu'] == 'x86-64'
         and receipt['target_triple'] == TARGET and receipt['jobs'] == 4, 'build recipe mismatch')
    for suffix in ('before', 'after'):
        need(receipt['source_sha256_' + suffix] == inputs['engine_source_sha256'], 'build source mismatch')
        need(receipt['tool_sha256_' + suffix] == inputs['tool_source_sha256'], 'build tools mismatch')
    need(receipt['pgo']['mode'] == expected_mode, 'wrong PGO stage')
    need(receipt['cargo_config_unchanged'], 'cargo configuration changed')
    need(receipt['rust_flags'][:2] == ['-C', 'target-cpu=x86-64'], 'wrong base flags')
    need(receipt['helper_sha256'] == sha(B / 'build-study-tools/build.py'), 'wrong private helper')
    return receipt


def build(stage, runner, inputs):
    wire = stage == 'build-instrumented-wire'
    instrumented = stage != 'build-use'
    binary = 'rook2' if wire else 'rook2-functional-cost'
    directory = B / stage
    need(not directory.exists(), 'build output must be absent')
    command = ['/usr/bin/python3', str(B / 'build-study-tools/build.py'), '--crate', str(W),
               '--output', str(directory), '--mode', 'generic', '--jobs', '4', '--bin', binary]
    if instrumented:
        raw = B / ('raw-wire' if wire else 'raw-functional')
        need(not raw.exists(), 'profile generation root must be absent')
        command += ['--pgo-generate', str(raw)]
    else:
        training = load(B / 'train/training.json')
        verification = load(B / 'train/verification.json')
        need(training['complete'] and verification['complete'], 'training incomplete')
        need(verification['training_record_sha256'] == sha(B / 'train/training.json'), 'verification binding mismatch')
        need(verification['independent_remerge_byte_identical'], 'independent merge did not match')
        need(training['profile_sha256'] == sha(B / 'train/merged.profdata'), 'profile changed')
        command += ['--pgo-use', str(B / 'train/merged.profdata'), '--training-record',
                    str(B / 'train/training.json'), '--ext-tsp-profiled']
    runner.run('build', command, timeout=BUILD_TIMEOUT)
    receipt = verify_build(stage, 'instrumented' if instrumented else 'profile-use', inputs)
    need(receipt['binary_name'] == binary, 'binary target mismatch')
    frozen = directory / (receipt['binary_name'] + '-exact')
    shutil.copyfile(receipt['binary_output']['path'], frozen)
    os.chmod(frozen, 0o555)
    need(sha(frozen) == receipt['binary_output']['sha256'], 'frozen image mismatch')
    save(directory / 'frozen-image.json', dict(path=str(frozen), sha256=sha(frozen),
         bytes=frozen.stat().st_size, mode='0555', receipt_sha256=sha(directory / 'receipt.json')))
    runner.run('archive', ['/usr/bin/python3', str(B / 'build-study-tools/archive_build.py'), str(directory)])
    if not instrumented:
        need(receipt['pgo']['code_layout']['application'] == 'use-only'
             and receipt['pgo']['code_layout']['profiled_functions_only'] is True, 'missing ExtTSP use setting')
    return dict(build=str(directory), frozen=str(frozen), sha256=sha(frozen))


def train(runner, inputs):
    directory = B / 'train'
    need(not directory.exists(), 'training output must be absent')
    wire = verify_build('build-instrumented-wire', 'instrumented', inputs)
    functional = verify_build('build-instrumented-functional', 'instrumented', inputs)
    need(wire['toolchain'] == functional['toolchain'], 'instrumented toolchain differs')
    need(wire['cargo_config_sha256_before'] == functional['cargo_config_sha256_before'], 'instrumented cargo configs differ')
    # Flags differ ONLY by their deliberate, separate instrumentation directory.
    need(wire['rust_flags'] == ['-C', 'target-cpu=x86-64', '-C', 'profile-generate=' + str(B / 'raw-wire')], 'wire flags mismatch')
    need(functional['rust_flags'] == ['-C', 'target-cpu=x86-64', '-C', 'profile-generate=' + str(B / 'raw-functional')], 'functional flags mismatch')
    for name in ('raw-wire', 'raw-functional'):
        need((B / name).is_dir() and not list((B / name).iterdir()), 'raw directory must be empty before training')
    directory.mkdir()
    engine = B / 'build-instrumented-wire/rook2-exact'
    func = B / 'build-instrumented-functional/rook2-functional-cost-exact'
    need(sha(engine) == wire['binary_output']['sha256'] and sha(func) == functional['binary_output']['sha256'], 'instrumented bytes changed')
    command = ['/usr/bin/node', str(SPEC / 'replay-check.mjs'), '--', '/usr/bin/taskset', '-c', '14', str(engine)]
    replay = runner.run('wire-original54', command,
                        {'LLVM_PROFILE_FILE': str(B / 'raw-wire/n-%m-%p.profraw')})
    report = load(replay['stdout'])
    workloads = load(SPEC / 'workloads.json')
    need(report['status'] == 'pass' and len(report['results']) == 54, 'original54 training failed')
    need(report['selectedCases'] == [x['id'] for x in workloads['cases']], 'case order changed')
    need(replay['stderr'].stat().st_size == 0, 'original checker stderr')
    pids = []
    for row, case in zip(report['results'], workloads['cases']):
        need(row['case'] == case['id'] and row['status'] == 'pass' and row['complete']
             and not row['truncated'] and row['error'] is None
             and row['exit'] == {'code': 0, 'signal': None} and row['stderr'] == ''
             and row['discardedObservedBytes'] == 0 and not row.get('cleanupUnconfirmed', False), 'raw replay failure')
        need(row['command'] == ['/usr/bin/taskset', '-c', '14', str(engine), '--work-clock=kingwcr', '--work-clock-post=work'], 'native training command changed')
        pids.append(row['pid'])
        raw = directory / case['id']
        raw.mkdir()
        (raw / 'stdout.raw').write_bytes(row['stdout'].encode('ascii'))
        (raw / 'stderr.raw').write_bytes(row['stderr'].encode('ascii'))
        save(raw / 'original-row.json', row)
    shutil.copyfile(replay['stdout'], directory / 'replay.json')
    original = runner.run('offline-original-checkReplay', ['/usr/bin/node', str(B / 'build-study-tools/recheck.mjs'), str(directory / 'replay.json')])
    need(load(original['stdout']) == dict(offlineOnly=True, originalCheckReplayCount=54), 'offline original54 check failed')
    functional_rows = []
    for row in ROWS:
        args = ['/usr/bin/taskset', '-c', '14', str(func), '--mode', 'verify', '--row', row,
                '--input', str(B / 'inputs' / (row + '.json')), '--iterations', '1']
        actual = runner.run('functional-' + row, args,
                            {'LLVM_PROFILE_FILE': str(B / 'raw-functional/n-%m-%p.profraw')})
        value = load(actual['stdout'])
        need(set(value) == {'row', 'completed', 'projection', 'sink', 'work'}, 'verify envelope changed')
        need(value['row'] == row and type(value['completed']) is int and value['completed'] == 1, 'verify row incomplete')
        need(type(value['sink']) is int and 0 <= value['sink'] <= (1 << 64) - 1, 'invalid sink')
        need(value['projection'] == load(B / 'expected' / (row + '.json')), 'original public projection mismatch')
        work = dict(zip(('chargedSearchUnits', 'chargedRelationQueries'), EXPECTED_WORK[row]))
        need(value['work'] == work and actual['stderr'].stat().st_size == 0, 'functional work/stderr mismatch')
        pids.append(actual['pid'])
        functional_rows.append(dict(row=row, pid=actual['pid'], command=args,
             output_sha256=sha(actual['stdout']), child_terminal_sha256=sha(actual['terminal']),
             expected_projection_sha256=sha(B / 'expected' / (row + '.json')), work=work))
    need(len(pids) == len(set(pids)) == 58, 'training native PID duplicated')
    raw = sorted((B / 'raw-wire').glob('*.profraw')) + sorted((B / 'raw-functional').glob('*.profraw'))
    need(len(list((B / 'raw-wire').iterdir())) == 54 and len(list((B / 'raw-functional').iterdir())) == 4
         and len(raw) == 58, 'expected54 wire+4 functional raw profiles')
    raw_pids = []
    for path in raw:
        match = re.fullmatch(r'n-.+-(\d+)\.profraw', path.name)
        need(match is not None and path.stat().st_size > 0, 'malformed/empty raw profile')
        raw_pids.append(int(match[1]))
    need(set(raw_pids) == set(pids) and len(raw_pids) == len(set(raw_pids)), 'raw/native PID mismatch')
    raw_hashes = {str(p): sha(p) for p in raw}
    all_raw = sorted(raw_hashes)
    merged = directory / 'merged.profdata'
    merge_command = ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(merged), *all_raw]
    first = runner.run('merge', merge_command)
    need(first['stderr'].stat().st_size == 0, 'profile merge warning/error')
    # Independent filesystem inventory/hash reconstruction, no reuse of first path list.
    again = sorted(p for root in (B / 'raw-wire', B / 'raw-functional') for p in root.iterdir())
    independently_hashed = {str(p): sha(p) for p in again}
    need(independently_hashed == raw_hashes, 'raw profiles changed')
    remerged = directory / 'independently-merged.profdata'
    second_command = ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(remerged), *map(str, again)]
    second = runner.run('independent-merge', second_command)
    need(second['stderr'].stat().st_size == 0 and merged.read_bytes() == remerged.read_bytes(), 'independent remerge differs')
    record = dict(schema='rook2-pgo-training-v1', complete=True,
        engine_source_sha256=inputs['engine_source_sha256'], target_triple=TARGET,
        base_rust_flags=['-C', 'target-cpu=x86-64'], profile_sha256=sha(merged),
        input_sha256=inputs['input_sha256'], private_tool_sha256=inputs['private_tool_sha256'],
        raw_profiles_sha256=raw_hashes, native_training_pids=pids,
        instrumented_build_receipts={name: dict(path=str(B / name / 'receipt.json'),
            sha256=sha(B / name / 'receipt.json'), engine_sha256=receipt['binary_output']['sha256'])
            for name, receipt in [('build-instrumented-wire', wire), ('build-instrumented-functional', functional)]},
        replay_sha256=sha(directory / 'replay.json'), original_wire_training_cases=54,
        extra_functional_coverage_rows=functional_rows, merge_command=merge_command,
        merge_tool_sha256=sha(Path('/usr/bin/llvm-profdata-19').resolve()),
        study_input_record_sha256=sha(B / 'build-study-inputs.json'), driver_sha256=sha(Path(__file__)),
        provenance='Own exact W source,54 original wire+4 separately declared functional coverage runs; not equivalent reference PGO',
        performance='Instrumented training only; not production CPU or functional measurement')
    save(directory / 'training.json', record)
    save(directory / 'verification.json', dict(complete=True, independent_remerge_byte_identical=True,
         training_record_sha256=sha(directory / 'training.json'), original_checkReplay_count=54,
         functional_projection_checks=4, unique_native_PIDs=58, raw_profiles_independently_hashed=58,
         independently_merged_profile_sha256=sha(remerged), independent_merge_command=second_command,
         actual_outer_tool_terminal_observed=False))
    return dict(training=str(directory / 'training.json'), profile_sha256=sha(merged), raw_profiles=58)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=STAGES)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', help='explicit parent invocation after review; otherwise refuses')
    args = parser.parse_args()
    need(args.execute, 'inert preparation: explicit parent --execute required')
    need(set(os.sched_getaffinity(0)) == H, 'run helper on housekeeping CPUs exactly')
    need(B.is_dir() and W.is_dir(), 'parent must create fixed study roots')
    need(os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp', 'unexpected TMPDIR')
    began = time.monotonic()
    records = B / 'stage-records'
    records.mkdir(exist_ok=True)
    directory = records / args.stage
    directory.mkdir()  # no overwrite, continuation or favorable rerun
    inputs = input_guard(args.source_manifest.resolve(strict=True))
    runner = Runner(directory, BUILD_TIMEOUT if args.stage != 'train' else OTHER_TIMEOUT)
    try:
        result = train(runner, inputs) if args.stage == 'train' else build(args.stage, runner, inputs)
        need(input_guard(args.source_manifest.resolve(strict=True)) == inputs, 'study inputs changed during stage')
        save(directory / 'result.json', dict(complete=True, stage=args.stage, result=result,
             elapsed_s=time.monotonic() - began, source_inputs_stable=True,
             child_terminals_only=True, actual_outer_tool_terminal_observed=False))
        print(json.dumps(dict(complete=True, stage=args.stage, result=result)))
        return 0
    except BaseException as error:
        save(directory / 'failure.json', dict(complete=False, stage=args.stage,
             error=type(error).__name__ + ': ' + str(error), elapsed_s=time.monotonic() - began,
             raw_outputs_preserved=True, no_automatic_retry=True,
             actual_outer_tool_terminal_observed=False))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
