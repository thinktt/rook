"""Shared constants and explicit adapters; importing starts no native process.

The released tap/comparator and full-split-production raw stream auditor are
unchanged. Only the auditor's ROOT, ACCOUNT and native_receipt globals are adapted
to this directory's gated tap and three-budget external placement supervisor.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
from pathlib import Path
import shlex
import statistics
import struct
import sys
import tomllib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL = HERE.parent/'full-split-production'
LEGACY = HERE.parent/'colors-three'
ACCOUNT = LEGACY/'account_threads.py'
GATE = LEGACY/'placement_gate.mjs'
TAP = LEGACY/'tools/tap_wire.mjs'
BUILD_ADAPTER = LEGACY/'build_adapter.py'
FOCUSED = LEGACY/'focused.py'
OLD_RAW = Path('/home/legolas/rook2-experiments/colors-three-20261026-01')
CONTROL_IMAGE = OLD_RAW/'rook2-candidate'
CONTROL_BUILD = OLD_RAW/'candidate-build'
CONTROL_SHA256 = 'b837361a4c00a57a29bedf2ccace3e7d13a5bcd025c1d8bf35c215f696449a82'
LEAD_REVIEW = Path('/home/legolas/agent-memos/imp2-lead-to-imp2-epoch-proof-review-20261026.md')
EVIDENCE_REUSE = dict(baselinePassed=38, supersededOldProtocol=10,
    rerunColorsIntegration=11, reusedUnchanged=17,
    scope='saved baseline evidence; old protocol checks do not qualify the epoch transport')
HOUSEKEEPING = HERE.parent/'coarse-pure-salvage/housekeeping.py'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
DEFAULT_CRATE = Path('/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01')
CONTROL_CRATE = Path('/home/legolas/rook2-experiments/workspaces/colors-three-20261026-01')
HELPERS = {0, 1, 2, 3, 8, 9, 10, 11, 12, 13}
CASES = ['profile-35', 'profile-08', 'profile-43']
NAMES = ['oldcolors3', 'inline1', 'current2', 'epoch3']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']
LIMITS = dict(perLifeSeconds=180, totalSeconds=1800,
              supervisorPlacementSeconds=10, inputGateSeconds=12)
PROTECTED = {
    '/home/legolas/rook2-experiments/configured-full-20261024-01/production/rook2-pgo':
        '8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b',
    '/home/legolas/rook2-experiments/configured-full-20261024-01/production/training/merged.profdata':
        'b7bd8ca21e8b9f64426af124be95bfc14feadd9b01bb94fb14bbefc7c550c6be',
    '/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build/rook2-exact':
        '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a',
    '/home/legolas/rook2-experiments/full-split-production-20261024-01/rook2-pgo':
        'a977bb0031b1beeb6fb50f8c391968f6e2d959ae86d648727442bdf027c88763',
    '/home/legolas/rook2-experiments/full-split-production-20261024-01/training/merged.profdata':
        'f9eefbd025c74a3247449c10fa0074fc5f178bcc49f1d623bed36cd9dcbdcadc',
}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    def bad(value):
        raise ValueError('nonfinite JSON: '+value)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), parse_constant=bad, object_pairs_hook=pairs)


def write(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix+'.pending')
    with temporary.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
    temporary.replace(path)


def snapshot(crate):
    paths = [crate/'Cargo.toml', crate/'Cargo.lock']
    paths += sorted(p for p in (crate/'src').rglob('*') if p.is_file())
    paths += [crate/n for n in ['build.rs', 'rust-toolchain', 'rust-toolchain.toml'] if (crate/n).is_file()]
    return {str(p.relative_to(crate)): sha(p) for p in paths}


def baseline():
    for path, digest in PROTECTED.items():
        assert sha(path) == digest, path
    return dict(PROTECTED)


def code_paths():
    paths = [HERE/name for name in ['common.py', 'prepare.py', 'collect.py', 'reconcile.py']]
    # Reuse the repaired Linux comm identities, gate, direct wait4 supervisor,
    # generic build recipe and CLI controls without copying or changing them.
    paths += [ACCOUNT, GATE, TAP, BUILD_ADAPTER, FOCUSED, LEGACY/'common.py',
        ORIGINAL/'reconcile.py', HOUSEKEEPING, ROOT/'tools/build.py',
        ROOT/'tools/tap_wire.mjs', ROOT/'tools/compare_ordinary.py',
        SPEC/'replay-check.mjs', SPEC/'benchmark.mjs', SPEC/'workloads.json', SPEC/'replay-oracle.json']
    return paths


def old_evidence_paths():
    paths = [LEGACY/'preparation.json', LEGACY/'closure.json', OLD_RAW/'pipeline.json',
        OLD_RAW/'frozen-tools/manifest.json', CONTROL_BUILD/'receipt.json', CONTROL_BUILD/'build.stderr',
        Path('/home/legolas/rook2-experiments/colors-three-20261026-02/reconciled.json')]
    pipeline = read(OLD_RAW/'pipeline.json')
    paths += [OLD_RAW/(row['stage']+'.'+suffix) for row in pipeline['stages']
              if row['stage'].startswith('tests-') for suffix in ['stdout', 'stderr']]
    return paths


def old_evidence(prepared):
    """Recheck saved evidence, never rerun the old process or build its image."""
    pins = prepared['oldEvidenceSha256']
    assert all(str(path) in pins for path in old_evidence_paths())
    for path, digest in pins.items():
        assert sha(path) == digest, path
    prior = read(LEGACY/'preparation.json')
    pipeline = read(OLD_RAW/'pipeline.json')
    assert pipeline['sourcePreparation'] == prior
    assert pipeline['preparationSha256'] == sha(LEGACY/'preparation.json')
    assert pipeline['prepared'] is True
    tests = [row for row in pipeline['stages'] if row['stage'].startswith('tests-')]
    assert len(tests) == 7 and all(row['exit'] == 0 for row in tests)
    passed = []
    for row in tests:
        for suffix in ['stdout', 'stderr']:
            path = OLD_RAW/(row['stage']+'.'+suffix)
            assert pins[str(path)] == row[suffix+'Sha256'] == sha(path)
        output = (OLD_RAW/(row['stage']+'.stdout')).read_text()
        names = re.findall(r'^test (\S+) \.\.\. ok$', output, re.M)
        summaries = re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;', output, re.M)
        assert len(summaries) == 1 and summaries[0] == (str(len(names)), '0', '0')
        assert names == row['passedTests']
        passed += names
    assert len(passed) == len(set(passed)) == 38
    reused = prepared['reusedFocusedEvidence']
    assert reused['pipeline'] == str(OLD_RAW/'pipeline.json') and reused['passed'] == 38
    assert reused['protocolEvidenceSuperseded'] is True
    closure = read(LEGACY/'closure.json')
    assert closure['complete'] and closure['controls']['focusedPassed'] == 38
    assert closure['images']['candidate']['path'] == str(CONTROL_IMAGE)
    assert closure['images']['candidate']['sha256'] == sha(CONTROL_IMAGE) == CONTROL_SHA256
    assert read(closure['raw']+'/reconciled.json')['complete'] is True
    assert prior['candidateSource'] == prepared['controlSource'] == snapshot(CONTROL_CRATE)
    return prior


def preparation(path):
    value = read(path)
    assert value['schema'] == 'rook2-epoch-colors-source-preparation-v1'
    assert value['baseCommit'] and len(value['baseCommit']) == 40
    assert Path(value['candidateCrate']).resolve() == DEFAULT_CRATE
    assert Path(value['controlCrate']).resolve() == CONTROL_CRATE
    assert Path(value['controlImage']).resolve() == CONTROL_IMAGE
    assert Path(value['controlBuild']).resolve() == CONTROL_BUILD
    assert value['controlImageSha256'] == CONTROL_SHA256 == sha(CONTROL_IMAGE)
    assert value['candidateSource'] == snapshot(DEFAULT_CRATE)
    old_evidence(value)
    before, after = value['controlSource'], value['candidateSource']
    assert set(before) == set(after)
    changed = sorted(name for name in before if before[name] != after[name])
    assert changed == value['sourceChanges'] == ['src/colors_worker.rs']
    assert value['focused'] and len({row['name'] for row in value['focused']}) == len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'], ['--bin', 'rook2']]
        assert row['selector'] and row['name'].replace('-', '').replace('_', '').isalnum()
        assert type(row['expectedPassed']) is int and row['expectedPassed'] > 0
        assert 0 < row.get('limitSeconds', 300) <= 300
    assert [(row['target'], row['selector']) for row in value['focused']] == [
        (['--lib'], 'colors_worker::lifecycle_tests'),
        (['--lib'], 'evaluator::colors_tests'),
        (['--lib'], 'evaluator::colors_lifecycle_tests')]
    assert [row['expectedPassed'] for row in value['focused'][1:]] == [8, 3]
    assert all(not row.get('exact', False) and not row.get('ignored', False) for row in value['focused'])
    semantics = value['readinessSemantics']
    assert set(semantics) == {'oldcolors3', 'epoch3'}
    for variant in semantics.values():
        assert set(variant) == {'publication', 'sideReady', 'inputAcquisition'}
        assert all(type(text) is str and text.strip() for text in variant.values())
    required = code_paths()+[HERE/'plan.md', HERE/'policy.json', HERE/'prototype.patch',
        HERE/'ownership-proof.md', LEAD_REVIEW]
    for item in required:
        assert value['inputSha256'][str(item)] == sha(item), item
    for item, digest in value['inputSha256'].items():
        assert sha(item) == digest, item
    assert value['protectedArtifacts'] == baseline()
    return value


def variants(control, candidate):
    assert Path(control) == CONTROL_IMAGE
    return dict(oldcolors3=dict(path=str(control), budget=3, options=['--threads=3'], report=True),
        inline1=dict(path=str(candidate), budget=1, options=['--threads=1'], report=True),
        current2=dict(path=str(candidate), budget=2, options=['--threads=2'], report=True),
        epoch3=dict(path=str(candidate), budget=3, options=['--threads=3'], report=True))


def schedule():
    rows = []
    for case in CASES:
        rows += [dict(case=case, variant=name, warmup=True, repeat=0) for name in NAMES]
        for repeat in range(3):
            rows += [dict(case=case, variant=name, warmup=False, repeat=repeat+1)
                     for name in NAMES[repeat:]+NAMES[:repeat]]
    assert len(rows) == 48
    return rows


def dist(samples):
    assert samples and all(type(x) in [int, float] and math.isfinite(x) for x in samples)
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def preexec_mask(budget):
    return [4, 6, 14] if budget == 3 else [6, 14]


def check_task_masks(affinities, pid, budget):
    assert len(affinities) == budget and affinities[str(pid)] == [14]
    others = sorted(mask for tid, mask in affinities.items() if tid != str(pid))
    assert others == {1: [], 2: [[6]], 3: [[4], [6]]}[budget]


def native_receipt(path, image, budget, options, hashes):
    native = read(path)
    assert native['schema'] == 'rook2-native-wait4-v1' and native['known_single_process']
    assert native['failure'] is None and native['native_exit_code'] == native['native_wait_status'] == 0
    assert native['exec_error'] is None and native['supervisor_signals'] == []
    assert native['engine'] == str(image)
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
    assert native['launcher_sha256'] == hashes[str(ACCOUNT)]
    assert sha(native['python_executable']) == native['python_executable_sha256']
    assert native['argv'] == [str(image), *options] and native['expected_threads'] == budget
    assert native['inherited_supervisor_affinity'] == sorted(HELPERS)
    assert set(native['supervisor_affinity']) == HELPERS
    assert native['native_pre_exec'] == dict(pid=native['native_pid'],
        pgid=native['supervisor_pid'], affinity=preexec_mask(budget))
    observed = native['native_post_exec']
    assert observed['path'] == str(image) and observed['pgid'] == native['supervisor_pid']
    assert observed['affinity'] == [14]
    assert sorted(observed['tasks'], key=int) == sorted(observed['task_affinities'], key=int)
    check_task_masks(observed['task_affinities'], native['native_pid'], budget)
    if budget == 3:
        names = observed['task_names']
        helpers = sorted((int(tid), name) for tid, name in names.items() if tid != str(native['native_pid']))
        assert [name for _, name in helpers] == ['rook2-eval-whit', 'rook2-eval-blac']
        assert [observed['task_affinities'][str(tid)] for tid, _ in helpers] == [[6], [4]]
    assert native['wall_ns'] == native['reaped_monotonic_ns']-native['start_monotonic_ns'] > 0
    assert native['total_cpu_s'] == native['user_cpu_s']+native['system_cpu_s'] > 0
    assert native['maxrss_linux_kib'] > 0
    report_path = path.parent/'colors.json'
    if native['colors_report_path'] is not None:
        assert native['colors_report_path'] == str(report_path)
        assert native['colors_report_sha256'] == sha(report_path)
    else:
        assert native['colors_report_sha256'] is None and not report_path.exists()
    for pid in [native['native_pid'], native['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists(), 'recorded PID currently live; inspect possible reuse'
    audit_placement(path.parent, native, hashes)
    return native


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
    assert all(mask and set(mask) <= set(preexec_mask(native['expected_threads'])) for mask in before.values())
    check_task_masks(ready['native_post_exec']['task_affinities'], ready['native_pid'], ready['expected_threads'])
    assert gate['schema'] == 'rook2-placement-input-gate-v1'
    assert gate['ready_path'] == str(ready_path) and gate['ready_sha256'] == sha(ready_path)
    assert gate['native_pid'] == native['native_pid'] and gate['supervisor_pid'] == native['supervisor_pid']
    raw_path = directory/('wire/stdin.raw' if gate['implementation'] == 'node-sync' else 'stdin.raw')
    raw = raw_path.read_bytes()
    size = gate['first_write_bytes']
    assert type(size) is int and 0 < size <= len(raw)
    assert hashlib.sha256(raw[:size]).hexdigest() == gate['first_write_sha256']
    if gate['implementation'] == 'node-sync':
        assert gate['gate_sha256'] == hashes[str(GATE)]
        case = read(directory/'launch.json')['step']['case']
        workload = next(r for r in read(SPEC/'workloads.json')['cases'] if r['id'] == case)
        assert raw[:size] == ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
    else:
        assert gate['implementation'] == 'python-idle'
        assert gate['gate_sha256'] == hashes[str(HERE/'collect.py')]
        assert raw[:size] == b'cm_parm\n'
    assert native['start_monotonic_ns'] <= int(ready['ready_monotonic_ns']) <= int(gate['release_monotonic_ns']) < native['reaped_monotonic_ns']
    if (directory/'wire/receipt.json').exists():
        tap = read(directory/'wire/receipt.json')
        assert int(gate['release_monotonic_ns']) <= int(tap['searches'][0]['startMonotonicNs'])
    return dict(readySha256=sha(ready_path), inputGateSha256=sha(gate_path))


def effective_options(directory):
    commands = [shlex.split(line.split('Running `', 1)[1].rsplit('`', 1)[0])
        for line in (directory/'build.stderr').read_text().splitlines()
        if 'Running `' in line and '--crate-name rook2 ' in line]
    result = {}
    for source, kind in [('src/lib.rs', 'lib'), ('src/bin/rook2.rs', 'bin')]:
        matching = [cmd for cmd in commands if source in cmd]
        assert len(matching) == 1, (source, len(matching))
        command, options = matching[0], {}
        assert command[command.index('--crate-type')+1] == kind
        for index, token in enumerate(command):
            if token == '-C':
                value = command[index+1]
            elif token.startswith('-C') and len(token) > 2:
                value = token[2:]
            else:
                continue
            key, separator, value = value.partition('=')
            assert key not in options
            options[key] = value if separator else True
        for key, value in [('opt-level', '3'), ('panic', 'abort'), ('codegen-units', '1'),
                           ('debuginfo', '1'), ('target-cpu', 'x86-64')]:
            assert options.get(key) == value, (source, key, options)
        assert not any(key.startswith('profile-') or key == 'llvm-args' for key in options)
        if kind == 'bin':
            assert options.get('lto') == 'thin' and 'linker-plugin-lto' not in options
        else:
            assert options.get('linker-plugin-lto') is True and 'lto' not in options
        result[source] = options
    return result


def admit_build(directory, image, crate, expected):
    receipt = read(directory/'receipt.json')
    assert receipt['schema'] == 'rook2-development-build-v1'
    assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot' and receipt['cargo_exit_code'] == 0
    assert Path(receipt['crate']).resolve() == crate
    assert receipt['mode'] == 'generic' and receipt['target_cpu'] == 'x86-64'
    assert receipt['target_triple'] == 'x86_64-unknown-linux-gnu' and receipt['binary_name'] == 'rook2'
    assert receipt['pgo']['mode'] == 'none' and receipt['rust_flags'] == ['-C', 'target-cpu=x86-64']
    assert receipt['helper_sha256'] == sha(ROOT/'tools/build.py')
    assert receipt['initial_affinity'] == receipt['build_affinity'] == receipt['restored_affinity'] == sorted(HELPERS)
    assert receipt['affinity_adapter'] == dict(path=str(BUILD_ADAPTER),
        sha256=sha(BUILD_ADAPTER), original_tool=str(ROOT/'tools/build.py'),
        original_tool_sha256=sha(ROOT/'tools/build.py'), only_override='HELPERS',
        original_helpers=[0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13], helpers=sorted(HELPERS))
    assert receipt['source_sha256_before'] == receipt['source_sha256_after'] == expected == snapshot(crate)
    assert receipt['tool_sha256_before'] == receipt['tool_sha256_after']
    assert receipt['cargo_config_sha256_before'] == receipt['cargo_config_sha256_after']
    assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged']
    assert receipt['toolchain']['rustc']['exit_code'] == receipt['toolchain']['cargo']['exit_code'] == 0
    assert 'release: 1.85.1\n' in receipt['toolchain']['rustc']['stdout']
    assert 'LLVM version: 19.1.7\n' in receipt['toolchain']['rustc']['stdout']
    for name, digest in (expected | receipt['tool_sha256_before']).items():
        assert sha(directory/'source-before'/name) == digest
    assert tomllib.loads((directory/'source-before/Cargo.toml').read_text())['profile']['release'] == {
        'opt-level': 3, 'lto': 'thin', 'codegen-units': 1, 'panic': 'abort', 'debug': 1}
    assert sha(image) == receipt['binary_output']['sha256'] == sha(receipt['binary_output']['path'])
    return receipt, effective_options(directory)


def admission(control_build, candidate_build, control, candidate, prepared):
    assert control_build == CONTROL_BUILD and control == CONTROL_IMAGE
    old_evidence(prepared)
    old, old_options = admit_build(control_build, control, CONTROL_CRATE, prepared['controlSource'])
    new, new_options = admit_build(candidate_build, candidate, DEFAULT_CRATE, prepared['candidateSource'])
    assert old_options == new_options
    for tool in ['rustc', 'cargo']:
        assert old['toolchain'][tool] == new['toolchain'][tool]
        assert old['toolchain'][tool+'_executable_sha256'] == new['toolchain'][tool+'_executable_sha256']
    assert old['rust_flags'] == new['rust_flags']
    assert old['finished_utc'] <= new['started_utc'], 'preserved old image must predate candidate build'
    return old, new


def image_layout(path):
    """Saved ELF section identities disclose image/layout drift without a helper."""
    data = Path(path).read_bytes()
    assert data[:6] == b'\x7fELF\x02\x01', 'expected64-bit little-endian ELF'
    offset, entry_size, count, names_index = (struct.unpack_from('<Q', data, 40)[0],
        *struct.unpack_from('<HHH', data, 58))
    assert entry_size == 64 and 0 < names_index < count
    assert offset+entry_size*count <= len(data)
    headers = [struct.unpack_from('<IIQQQQIIQQ', data, offset+index*entry_size) for index in range(count)]
    names = headers[names_index]
    strings = data[names[4]:names[4]+names[5]]
    sections = {}
    for row in headers:
        name = strings[row[0]:].split(b'\0', 1)[0].decode('ascii')
        if name in ['.text', '.rodata']:
            assert row[4]+row[5] <= len(data) and name not in sections
            sections[name] = dict(address=row[3], fileOffset=row[4], bytes=row[5],
                sha256=hashlib.sha256(data[row[4]:row[4]+row[5]]).hexdigest())
    assert set(sections) == {'.text', '.rodata'}
    return dict(path=str(path), sha256=sha(path), bytes=len(data), sections=sections)


def prepared_run(path, prepared_path, prepared, candidate):
    """Audit the saved successful preparation; this function starts no process."""
    value = read(path)
    assert value['schema'] == 'rook2-epoch-colors-prepared-run-v1'
    assert value['sourcePreparation'] == str(prepared_path)
    assert value['sourcePreparationSha256'] == sha(prepared_path)
    assert value['source'] == prepared['candidateSource']
    assert value['candidate'] == image_layout(candidate)
    assert value['control'] == image_layout(CONTROL_IMAGE)
    assert value['reusedFocusedEvidence'] == prepared['reusedFocusedEvidence']
    assert value['pipelineSeconds'] == 3600
    assert 0 < value['pipelineStartMonotonicNs'] <= value['preparedMonotonicNs']
    assert value['preparedMonotonicNs']-value['pipelineStartMonotonicNs'] < 3600*10**9
    directory = path.parent
    stages = value['stages']
    names = [f'tests-{index:02d}-{row["name"]}' for index, row in enumerate(prepared['focused'])]
    assert [row['stage'] for row in stages] == names+['candidate-build', 'cli-affinity']
    for row in stages:
        assert row['exit'] == 0
        for suffix in ['stdout', 'stderr']:
            file = directory/(row['stage']+'.'+suffix)
            assert sha(file) == row[suffix+'Sha256'] == value['inputSha256'][str(file)]
    for row, expected in zip(stages, prepared['focused']):
        assert row['argv'] == ['/usr/bin/cargo', 'test', '--offline', '--locked', *expected['target'],
            '--target', 'x86_64-unknown-linux-gnu', '--jobs', '4',
            '--target-dir', str(directory/'test-target'), expected['selector'], '--', '--test-threads=1']
        assert row['cwd'] == str(DEFAULT_CRATE)
        output = (directory/(row['stage']+'.stdout')).read_text()
        passed = re.findall(r'^test (\S+) \.\.\. ok$', output, re.M)
        summaries = re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;', output, re.M)
        assert passed == row['passedTests'] and len(passed) == expected['expectedPassed']
        assert len(passed) == len(set(passed))
        assert summaries == [(str(len(passed)), '0', '0')]
    assert stages[-2]['argv'] == ['/usr/bin/python3', str(BUILD_ADAPTER),
        '--crate', str(DEFAULT_CRATE), '--mode', 'generic', '--bin', 'rook2',
        '--jobs', '4', '--output', str(directory/'candidate-build')]
    assert stages[-1]['argv'] == ['/usr/bin/python3', str(FOCUSED),
        '--engine', str(candidate), '--output', str(directory/'focused')]
    assert all(row['cwd'] == str(ROOT) for row in stages[-2:])
    cli = read(directory/'focused/result.json')
    assert cli['schema'] == 'rook2-colors-three-focused-cli-v1' and cli['complete']
    assert cli['engine'] == str(candidate) and cli['engineSha256'] == sha(candidate)
    assert len(cli['cli']) == 13 and len(cli['affinityReplays']) == 2
    for row, name in zip(cli['affinityReplays'], ['one-cpu', 'two-cpu']):
        for file, digest in row['sha256'].items():
            assert sha(directory/'focused'/name/file) == digest
    for file, digest in value['inputSha256'].items():
        assert sha(file) == digest
    return value


def supervisor(image, budget, directory, options):
    return [sys.executable, str(ACCOUNT), '--engine', str(image), '--record', str(directory/'native.json'),
        '--known-single-process', '--thread-budget', str(budget), *options]


COMPLETED_METRICS = ['white_ready', 'black_ready', 'white_kernel', 'black_kernel',
                     'white_copy', 'black_copy', 'reader_imbalance', 'join_elapsed']
PAIRED_METRICS = ['owner_ready', 'join_wait', 'owner_after_sides']


def colors_report(path, budget, idle=False):
    value = read(path)
    assert value['schema'] == 'rook2-colors-readiness-v1'
    if budget != 3:
        assert value == dict(schema='rook2-colors-readiness-v1', enabled=False)
        return value
    assert value['enabled'] is True and value['sample_stride'] == 512
    assert value['storage'] == 'fixed_log2_histograms' and value['samples_capped'] == 0
    assert value['histogram_bucket_rule'] == 'zero_else_bit_length_capped_63'
    counters = ['dispatches', 'sampled_dispatches', 'completed_samples', 'discarded_samples',
        'failed_samples', 'owner_missing_samples', 'paired_samples',
        'owner_ready_at_or_after_both', 'sides_after_owner', 'white_last', 'black_last', 'sides_tied']
    assert all(type(value[key]) is int and 0 <= value[key] < (1 << 64) for key in counters)
    assert value['sampled_dispatches'] == value['dispatches']//512
    assert value['sampled_dispatches'] == sum(value[key] for key in [
        'completed_samples', 'discarded_samples', 'failed_samples'])
    assert value['owner_missing_samples'] <= value['completed_samples']
    assert value['paired_samples'] == value['completed_samples']-value['owner_missing_samples']
    assert value['paired_samples'] == value['owner_ready_at_or_after_both']+value['sides_after_owner']
    assert value['paired_samples'] == value['white_last']+value['black_last']+value['sides_tied']
    assert set(value['metrics']) == set(COMPLETED_METRICS+PAIRED_METRICS)
    for key, metric in value['metrics'].items():
        count = value['completed_samples'] if key in COMPLETED_METRICS else value['paired_samples']
        assert set(metric) == {'count', 'sum_ns', 'min_ns', 'max_ns', 'log2_ns'}
        assert metric['count'] == count
        assert all(type(metric[name]) is int and metric[name] >= 0 for name in ['count', 'sum_ns', 'min_ns', 'max_ns'])
        buckets = metric['log2_ns']
        assert len(buckets) == 64 and all(type(n) is int and n >= 0 for n in buckets)
        assert sum(buckets) == count
        if count == 0:
            assert metric['sum_ns'] == metric['min_ns'] == metric['max_ns'] == 0
            continue
        assert metric['min_ns'] <= metric['max_ns'] <= (1 << 64)-1
        assert metric['min_ns']*count <= metric['sum_ns'] <= metric['max_ns']*count
        occupied = [i for i, n in enumerate(buckets) if n]
        bucket = lambda ns: min(ns.bit_length(), 63)
        assert bucket(metric['min_ns']) == occupied[0] and bucket(metric['max_ns']) == occupied[-1]
        lower = sum(n*(0 if i == 0 else 1 << (i-1)) for i, n in enumerate(buckets))
        upper = sum(n*(0 if i == 0 else ((1 << i)-1 if i < 63 else (1 << 64)-1))
                    for i, n in enumerate(buckets))
        assert lower <= metric['sum_ns'] <= upper
    if idle:
        assert value['dispatches'] == 0
    else:
        assert value['dispatches'] > 0
    return value


audit = module('epoch_colors_original_raw_auditor', ORIGINAL/'reconcile.py')
audit.ROOT, audit.ACCOUNT, audit.native_receipt = LEGACY, ACCOUNT, native_receipt
housekeeping = module('epoch_colors_reversible_housekeeping', HOUSEKEEPING)
cleanup = module('epoch_colors_owned_cleanup', ROOT/'tools/compare_ordinary.py')
stop_owned = cleanup.stop_owned
