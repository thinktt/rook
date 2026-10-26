"""Own-PGO contracts and reuse of the frozen epoch placement/accounting tools.

Importing starts no process. Historical evidence is read, never rebuilt or rerun.
"""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPOCH = HERE.parent/'epoch-colors'
LEGACY = HERE.parent/'colors-three'
SOURCE_CHECKPOINT = '1c68dd32d5f323e09faf784ff4fc50a5b5fca47d'
GENERIC = HERE.parent/'whole-full-epoch'
LEAD_REVIEW = Path('/home/legolas/agent-memos/imp2-lead-to-imp2-whole-full-epoch-own-pgo-20261026.md')
GENERIC_RAW = Path('/home/legolas/rook2-experiments/whole-full-epoch-20261026-01')
SERIAL_BUILD = Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build')
PRIOR_BUILD = Path('/home/legolas/rook2-experiments/epoch-own-pgo-20261026-01/use-build')
PRACTICAL_BUILD = PRIOR_BUILD  # frozen training API alias; the comparison uses prior2/prior3
SERIAL_IMAGE = SERIAL_BUILD/'rook2-exact'
PRIOR_IMAGE = PRIOR_BUILD.parent/'rook2-pgo'
PRACTICAL_IMAGE = PRIOR_IMAGE
SERIAL_SHA = '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a'
PRIOR_SHA = '67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7'
PRACTICAL_SHA = PRIOR_SHA
PRIOR_PROFILE_SHA = '9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311'
NAMES = ['serial1', 'prior2', 'prior3', 'inline1', 'wholeepoch2', 'colorepoch3']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']
LIMITS = dict(perLifeSeconds=180, totalSeconds=1800,
              supervisorPlacementSeconds=10, inputGateSeconds=12)
PIPELINE_SECONDS = 3600
TRAIN_SECONDS = 2400


def module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


epoch = module('epoch_own_pgo_frozen_epoch_common', EPOCH/'common.py')
sha, read, write, snapshot = epoch.sha, epoch.read, epoch.write, epoch.snapshot
ACCOUNT, GATE, TAP, SPEC = epoch.ACCOUNT, epoch.GATE, epoch.TAP, epoch.SPEC
DEFAULT_CRATE = Path('/home/legolas/rook2-experiments/workspaces/whole-full-epoch-20261026-01')
HELPERS = epoch.HELPERS
BUILD_ADAPTER, FOCUSED = epoch.BUILD_ADAPTER, epoch.FOCUSED
native_receipt, audit_placement = epoch.native_receipt, epoch.audit_placement
supervisor = epoch.supervisor
# oldidle.ready_record imports common lazily; keep this export before any run.
check_task_masks = epoch.check_task_masks
housekeeping, stop_owned, audit = epoch.housekeeping, epoch.stop_owned, epoch.audit
image_layout, colors_report = epoch.image_layout, epoch.colors_report


def frozen_module(name, path, binding):
    previous = sys.modules.get('common')
    try:
        sys.modules['common'] = binding
        return module(name, path)
    finally:
        if previous is None:
            sys.modules.pop('common', None)
        else:
            sys.modules['common'] = previous


# The unchanged idle implementation emits its original gate digest. Its original
# common validates that digest, including both budget3 helper comm identities.
idle_probe = frozen_module('epoch_own_pgo_frozen_idle', EPOCH/'collect.py', epoch).idle_probe
observer = frozen_module('epoch_own_pgo_frozen_report_audit', EPOCH/'reconcile.py', epoch)
readiness, readiness_summary = observer.readiness, observer.readiness_summary


generic = module('whole_full_own_pgo_frozen_generic_common', GENERIC/'common.py')


def baseline():
    result = generic.baseline()
    result[str(GENERIC_RAW/'rook2-candidate')] = 'a30daa460780bd238c97b3c440b026975eceef13cb0cc498c4851df14ccc3e45'
    for directory in [SERIAL_BUILD, PRIOR_BUILD]:
        for path, digest in read(directory/'receipt.json')['pgo']['input_sha256_before'].items():
            assert path not in result or result[path] == digest
            result[path] = digest
    assert result[str(SERIAL_IMAGE)] == SERIAL_SHA
    assert result[str(PRIOR_IMAGE)] == PRIOR_SHA
    assert result[str(PRIOR_BUILD.parent/'training/merged.profdata')] == PRIOR_PROFILE_SHA
    for path, digest in result.items():
        assert sha(path) == digest, path
    return result


def code_paths():
    paths = [HERE/name for name in ['common.py', 'prepare.py', 'train.py',
        'training_reconcile.py', 'collect.py', 'reconcile.py']]
    return sorted(set(paths+generic.code_paths()+[GENERIC/'finish_idle.py',
        GENERIC/'repair_reconcile.py', SERIAL_BUILD/'receipt.json', PRIOR_BUILD/'receipt.json']))


def reused_evidence_paths():
    paths = [GENERIC/'preparation.json', GENERIC/'closure.json', GENERIC_RAW/'pipeline.json',
        GENERIC_RAW/'prepared-run.json', GENERIC_RAW/'pilot/plan.json',
        GENERIC_RAW/'pilot/result.json', GENERIC_RAW/'idle-completion-01/reconciled.json',
        GENERIC_RAW/'candidate-build/receipt.json', GENERIC_RAW/'candidate-build/build.stderr']
    proof = read(GENERIC/'preparation.json')
    paths += [Path(path) for key in ['inputSha256', 'reusedEvidenceSha256'] for path in proof[key]]
    pipeline = read(GENERIC_RAW/'pipeline.json')
    paths += [GENERIC_RAW/(row['stage']+'.'+suffix) for row in pipeline['stages']
        for suffix in ['stdout', 'stderr']]
    composed = read(GENERIC_RAW/'idle-completion-01/reconciled.json')
    paths += [Path(path) for path in composed['adapterInputSha256']]
    for root, key in [(GENERIC_RAW/'pilot', 'originalRawSha256'),
                      (GENERIC_RAW/'idle-completion-01', 'completionRawSha256')]:
        paths += [root/name for name in composed[key]]
    return sorted(set(paths))


def generic_evidence(prepared):
    pins = prepared['reusedEvidenceSha256']
    assert all(str(path) in pins for path in reused_evidence_paths())
    for path, digest in pins.items():
        assert sha(path) == digest, path
    proof = generic.preparation(GENERIC/'preparation.json')
    closure = read(GENERIC/'closure.json')
    composed = read(GENERIC_RAW/'idle-completion-01/reconciled.json')
    pipeline = read(GENERIC_RAW/'pipeline.json')
    assert closure['complete'] and composed['complete']
    assert proof['candidateSource'] == closure['candidateSource'] == prepared['candidateSource'] == snapshot(DEFAULT_CRATE)
    assert len(prepared['candidateSource']) == 64
    saved = generic.prepared_run(GENERIC_RAW/'prepared-run.json', GENERIC/'preparation.json', proof)
    tests = [row for row in saved['stages'] if row['stage'].startswith('tests-')]
    assert sum(len(row['passedTests']) for row in tests) == closure['focusedControls'] == 29
    assert pipeline['prepared'] and not pipeline['complete'] and not pipeline['collected']
    assert 'check_task_masks' in read(GENERIC_RAW/'pilot/result.json')['failure']
    assert closure['replayLives'] == composed['replayLives'] == 60
    assert closure['idleCompletionComplete'] and composed['idleProcesses'] == 5
    assert closure['failedPreinput'] == composed['failedPreinput']
    assert composed['adapter'] == 'common.check_task_masks = common.epoch.check_task_masks; original files unchanged'
    for path, digest in composed['adapterInputSha256'].items():
        assert sha(path) == digest, path
    for root, key in [(GENERIC_RAW/'pilot', 'originalRawSha256'),
                      (GENERIC_RAW/'idle-completion-01', 'completionRawSha256')]:
        for name, digest in composed[key].items():
            assert sha(root/name) == digest, root/name
    return dict(freshGenericControls=29, genericReplayLives=60,
        genericImage=image_layout(GENERIC_RAW/'rook2-candidate'), sourceChangesAgainstGeneric=[],
        evidenceReuse=proof['evidenceReuse'], sourceFiles=64,
        genericClosure=str(GENERIC/'closure.json'), genericClosureSha256=sha(GENERIC/'closure.json'),
        composedAudit=str(GENERIC_RAW/'idle-completion-01/reconciled.json'),
        composedAuditSha256=sha(GENERIC_RAW/'idle-completion-01/reconciled.json'),
        preservedSetupFailure=composed['failedPreinput'],
        scope='unchanged source numerical/color evidence reused read-only; generic failed setup and complete composed audit retained; no new unit campaign')


def preparation(path):
    value = read(path)
    assert value['schema'] == 'rook2-whole-full-own-pgo-source-preparation-v1'
    assert value['sourceCheckpoint'] == SOURCE_CHECKPOINT
    assert Path(value['candidateCrate']).resolve() == DEFAULT_CRATE
    assert value['candidateSource'] == snapshot(DEFAULT_CRATE)
    assert value['protectedArtifacts'] == baseline()
    generic_evidence(value)
    assert value['readinessSemantics'] == read(GENERIC/'preparation.json')['readinessSemantics']
    required = code_paths()+[HERE/'plan.md', HERE/'policy.json', LEAD_REVIEW]
    for path in required:
        assert value['inputSha256'][str(path)] == sha(path), path
    for path, digest in value['inputSha256'].items():
        assert sha(path) == digest, path
    return value


def deadline_seconds(pipeline_start_ns, cap_seconds, stage_start_ns=None):
    assert type(pipeline_start_ns) is int and 0 < pipeline_start_ns <= time.monotonic_ns()
    stage_start_ns = time.monotonic_ns() if stage_start_ns is None else stage_start_ns
    assert pipeline_start_ns <= stage_start_ns <= time.monotonic_ns()
    return min(pipeline_start_ns/1e9+PIPELINE_SECONDS, stage_start_ns/1e9+cap_seconds)


def cases():
    values = [row['id'] for row in read(SPEC/'workloads.json')['cases']]
    assert len(values) == len(set(values)) == 54
    return values


def variants(candidate):
    return dict(serial1=dict(path=str(SERIAL_IMAGE), budget=1, options=[], report=False),
        prior2=dict(path=str(PRIOR_IMAGE), budget=2, options=['--threads=2'], report=True),
        prior3=dict(path=str(PRIOR_IMAGE), budget=3, options=['--threads=3'], report=True),
        inline1=dict(path=str(candidate), budget=1, options=['--threads=1'], report=True),
        wholeepoch2=dict(path=str(candidate), budget=2, options=['--threads=2'], report=True),
        colorepoch3=dict(path=str(candidate), budget=3, options=['--threads=3'], report=True))


def schedule():
    steps = []
    for index, case in enumerate(cases()):
        order = NAMES[index % 6:]+NAMES[:index % 6]
        steps += [dict(case=case, variant=name, warmup=False, repeat=1) for name in order]
    assert len(steps) == 324
    return steps


def admit_build(directory, image, mode, prepared):
    receipt, effective = audit.check_build(directory, mode)
    assert mode in ['instrumented', 'profile-use']
    assert receipt['source_sha256_before'] == prepared['candidateSource'] == snapshot(DEFAULT_CRATE)
    assert Path(receipt['crate']).resolve() == DEFAULT_CRATE
    assert sha(image) == receipt['binary_output']['sha256']
    assert receipt['mode'] == 'generic' and receipt['helper_sha256'] == sha(ROOT/'tools/build.py')
    assert receipt['initial_affinity'] == receipt['build_affinity'] == receipt['restored_affinity'] == sorted(HELPERS)
    assert receipt['affinity_adapter'] == dict(path=str(BUILD_ADAPTER), sha256=sha(BUILD_ADAPTER),
        original_tool=str(ROOT/'tools/build.py'), original_tool_sha256=sha(ROOT/'tools/build.py'),
        only_override='HELPERS', original_helpers=[0,1,2,3,4,5,8,9,10,11,12,13], helpers=sorted(HELPERS))
    for name, digest in receipt['tool_sha256_before'].items():
        assert sha(directory/'source-before'/name) == digest
    for expected, control_image, digest in [(SERIAL_BUILD, SERIAL_IMAGE, SERIAL_SHA),
            (PRIOR_BUILD, PRIOR_IMAGE, PRIOR_SHA)]:
        control = read(expected/'receipt.json')
        assert control['outcome'] == 'build-succeeded-with-stable-input-snapshot'
        assert control['binary_output']['sha256'] == sha(control_image) == digest
        assert control['pgo']['mode'] == 'profile-use'
        if expected == PRIOR_BUILD:
            assert control['pgo']['profile'] == str(PRIOR_BUILD.parent/'training/merged.profdata')
            assert sha(control['pgo']['profile']) == PRIOR_PROFILE_SHA
        assert control['target_cpu'] == receipt['target_cpu'] == 'x86-64'
        assert control['target_triple'] == receipt['target_triple']
        for tool in ['rustc', 'cargo']:
            assert control['toolchain'][tool] == receipt['toolchain'][tool]
            assert control['toolchain'][tool+'_executable_sha256'] == receipt['toolchain'][tool+'_executable_sha256']
    return receipt, effective


def drift(prepared, candidate_profile):
    source, profiles = {}, {}
    for name, directory in [('serial1',SERIAL_BUILD),('prior2',PRIOR_BUILD),('prior3',PRIOR_BUILD)]:
        receipt = read(directory/'receipt.json')
        before, after = receipt['source_sha256_before'], prepared['candidateSource']
        source[name] = dict(changed=sorted(key for key in before.keys() & after.keys() if before[key]!=after[key]),
            added=sorted(after.keys()-before.keys()), removed=sorted(before.keys()-after.keys()))
        profiles[name] = dict(path=receipt['pgo']['profile'], sha256=sha(receipt['pgo']['profile']),
            trainingRecord=receipt['pgo']['training_record'], trainingRecordSha256=sha(receipt['pgo']['training_record']))
    source['genericWholeFullEpoch'] = dict(changed=[],added=[],removed=[])
    profiles['candidate'] = dict(path=str(candidate_profile),sha256=sha(candidate_profile),modes=[1,2,3],originalCasesPerMode=54)
    return dict(source=source,profiles=profiles)


def environment(directory, report, profile_pattern=None):
    env = {key:value for key,value in os.environ.items()
           if not key.startswith('ROOK2_') and key != 'LLVM_PROFILE_FILE'}
    if report:
        env['ROOK2_COLORS_REPORT'] = str(directory/'colors.json')
    if profile_pattern is not None:
        env['LLVM_PROFILE_FILE'] = str(profile_pattern)
    return env


def run_lifetime(directory, step, image, variant, deadline, hashes, profile_pattern=None):
    directory.mkdir()
    started = time.monotonic_ns()
    budget, options = variant['budget'], variant['options']
    native = supervisor(image, budget, directory, options)
    mode = read(SPEC/'replay-oracle.json')['mode']
    config = dict(version=1, expectedArgv=native+mode, directory=str(directory/'wire'),
        nativeExecutable=str(image), maxRawBytes=8*1024*1024, tickHz=os.sysconf('SC_CLK_TCK'))
    write(directory/'tap-config.json', config)
    env = environment(directory, variant['report'], profile_pattern)
    env['ROOK2_WIRE_TAP_CONFIG'] = str(directory/'tap-config.json')
    command = ['/usr/bin/node', '--import', str(TAP), str(SPEC/'replay-check.mjs'),
        '--case', step['case'], '--', *native]
    write(directory/'launch.json', dict(argv=command, step=step,
        profileEnvironment={'LLVM_PROFILE_FILE': str(profile_pattern)} if profile_pattern else {}))
    run_deadline = min(deadline, time.monotonic()+LIMITS['perLifeSeconds'])
    with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        try:
            while child.poll() is None:
                assert time.monotonic() < run_deadline, 'per-life or aggregate deadline'
                assert (directory/'stdout').stat().st_size <= 8*1024*1024
                assert (directory/'stderr').stat().st_size <= 1024*1024
                assert not (directory/'wire/failure.json').exists(), 'raw tap failure'
                time.sleep(.05)
        except BaseException as error:
            stop_owned(child)
            write(directory/'failure.json', dict(exit=child.poll(), step=step, error=repr(error)))
            raise
    assert child.returncode == 0 and (directory/'stderr').stat().st_size == 0
    receipt = native_receipt(directory/'native.json', image, budget, options+mode, hashes)
    tap = read(directory/'wire/receipt.json')
    assert tap['failure'] is None and len(tap['searches']) == 1
    row = dict(**step, directory=str(directory), nativePid=receipt['native_pid'],
        searchWallNs=tap['searches'][0]['wallNs'], wholeCpuSeconds=receipt['total_cpu_s'],
        wholeWallNs=receipt['wall_ns'], nonSearchWallNs=receipt['wall_ns']-tap['searches'][0]['wallNs'],
        rssKiB=receipt['maxrss_linux_kib'], taskAffinities=receipt['native_post_exec']['task_affinities'],
        sha256={name:sha(directory/name) for name in ['native.json','stdout','stderr',
            'wire/receipt.json','tap-config.json','launch.json']},
        placement=audit_placement(directory, receipt, hashes), controllerStartMonotonicNs=started)
    if variant['report']:
        row['colors'] = dict(path=str(directory/'colors.json'), sha256=sha(directory/'colors.json'),
            report=colors_report(directory/'colors.json', budget))
    else:
        assert receipt['colors_report_path'] is None
        row['colors'] = None
    _, row['orderedPosts'] = audit.lifetime(directory, row, step, image, budget, options, hashes, profile_pattern)
    row['controllerEndMonotonicNs'] = time.monotonic_ns()
    return row


def housekeeping_audit(path, expected_applies):
    record = read(path)
    assert record['schema'] == 'rook2-whole-full-own-pgo-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus'] == sorted(HELPERS)
    assert len(record['applies']) == expected_applies and record['restored'] is not None
    originals, leaders, observed = {}, {}, {}
    for row in record['originals']:
        key = (row['pid'], row['tid'], row['starttime'])
        assert key not in originals and row['affinity']
        originals[key] = row['affinity']
    for row in record['leaders']:
        key = (row['pid'], row['starttime'])
        assert key not in leaders and row['affinity']
        leaders[key] = row['affinity']
    for event in record['applies']:
        assert event['cpus'] == event['selfAffinity'] == sorted(HELPERS)
        for row in event['selectedTasks']:
            key = (row['pid'], row['tid'], row['starttime'])
            assert row['after'] == sorted(HELPERS)
            if key in observed:
                assert row['before'] == sorted(HELPERS)
            else:
                assert originals[key] == row['before']
                observed[key] = row['before']
    assert observed == originals
    for row in record['restored']:
        key = (row['pid'], row['tid'], row['starttime'])
        if key in originals:
            assert not row['inheritedNewThread'] and row['restored'] == originals[key]
        else:
            masks = [mask for (pid, _), mask in leaders.items() if pid == row['pid']]
            assert len(masks) == 1 and row['inheritedNewThread'] and row['restored'] == masks[0]
    assert record['postRestoreSelfAffinity'] == sorted(HELPERS)
    return dict(selectedOriginalTasks=len(originals), restoredTasks=len(record['restored']),
                applyCount=len(record['applies']), receiptSha256=sha(path))



def prepared_run(path, prepared_path, prepared):
    """Read-only exact-image/recipe/training/CLI admission after preparation."""
    value = read(path)
    assert value['schema'] == 'rook2-whole-full-own-pgo-prepared-run-v1' and value['complete']
    assert value['sourcePreparation'] == str(prepared_path)
    assert value['sourcePreparationSha256'] == sha(prepared_path)
    assert value['source'] == prepared['candidateSource']
    assert value['evidenceReuse'] == generic_evidence(prepared)
    start, deadline = value['pipelineStartMonotonicNs'], value['pipelineDeadlineMonotonicNs']
    assert deadline == start+PIPELINE_SECONDS*10**9
    assert 0 < start <= value['preparedMonotonicNs'] < deadline
    directory = path.parent
    candidate, instrumented = directory/'rook2-pgo', directory/'rook2-instrumented'
    assert value['candidate'] == image_layout(candidate)
    assert value['instrumented'] == image_layout(instrumented)
    for file, digest in value['inputSha256'].items():
        assert sha(file) == digest, file
    stages = value['stages']
    assert [row['stage'] for row in stages] == [
        'instrumented-build','training','training-audit','use-build','cli-affinity']
    clock = ['--pipeline-start-ns', str(start), '--pipeline-deadline-ns', str(deadline)]
    expected = [
        ['/usr/bin/python3', str(BUILD_ADAPTER), '--crate', str(DEFAULT_CRATE), '--mode', 'generic',
         '--bin', 'rook2', '--jobs', '4', '--pgo-generate', str(directory/'profile-raw'),
         '--output', str(directory/'instrumented-build')],
        ['/usr/bin/python3', str(HERE/'train.py'), '--build', str(directory/'instrumented-build'),
         '--engine', str(instrumented), '--preparation', str(prepared_path), *clock,
         '--output', str(directory/'training')],
        ['/usr/bin/python3', str(HERE/'training_reconcile.py'), str(directory/'training'),
         '--pipeline-deadline-ns', str(deadline)],
        ['/usr/bin/python3', str(BUILD_ADAPTER), '--crate', str(DEFAULT_CRATE), '--mode', 'generic',
         '--bin', 'rook2', '--jobs', '4', '--pgo-use', str(directory/'training/merged.profdata'),
         '--training-record', str(directory/'training/training.json'), '--ext-tsp-profiled',
         '--output', str(directory/'use-build')],
        ['/usr/bin/python3', str(FOCUSED), '--engine', str(candidate), '--output', str(directory/'focused')]]
    previous_end = start
    for row, argv, cap in zip(stages, expected, [300,2500,120,300,420]):
        assert previous_end <= row['startedMonotonicNs'] < row['endedMonotonicNs'] <= value['preparedMonotonicNs']
        assert row['elapsedNs'] == row['endedMonotonicNs']-row['startedMonotonicNs'] > 0
        assert row['endedMonotonicNs'] <= row['deadlineMonotonicNs'] <= deadline
        assert row['deadlineMonotonicNs']-row['startedMonotonicNs'] <= cap*10**9
        previous_end = row['endedMonotonicNs']
        assert row['argv'] == argv and row['exit'] == 0 and row['cwd'] == str(ROOT)
        for suffix in ['stdout','stderr']:
            file = directory/(row['stage']+'.'+suffix)
            assert value['inputSha256'][str(file)] == sha(file) == row[suffix+'Sha256']
    admit_build(directory/'instrumented-build', instrumented, 'instrumented', prepared)
    receipt, effective = admit_build(directory/'use-build', candidate, 'profile-use', prepared)
    assert receipt['pgo']['profile'] == str(directory/'training/merged.profdata')
    assert receipt['pgo']['training_record'] == str(directory/'training/training.json')
    training, proof = read(directory/'training/training.json'), read(directory/'training/reconciled.json')
    assert proof == value['trainingAudit'] and proof['complete'] and proof['nativeProcesses'] == 162
    assert proof['remerge']['byteIdentical'] is True
    assert proof['schema'] == 'rook2-whole-full-own-pgo-training-audit-v1'
    assert proof['canonicalMergeCount'] == proof['independentAuditMergeCount'] == 1
    assert proof['pipelineStartMonotonicNs'] == start and proof['pipelineDeadlineMonotonicNs'] == deadline
    assert training['streamEndMonotonicNs'] <= proof['auditStartMonotonicNs'] < proof['auditEndMonotonicNs'] <= value['preparedMonotonicNs']
    assert proof['auditEndMonotonicNs'] <= proof['auditDeadlineMonotonicNs'] <= deadline
    assert proof['auditDeadlineMonotonicNs']-proof['auditStartMonotonicNs'] <= 120*10**9
    for name, digest in proof['rawSha256'].items():
        assert sha(directory/'training'/name) == digest
    remerge = proof['remerge']
    assert sha(remerge['receipt']) == remerge['receiptSha256']
    assert sha(remerge['profile']) == remerge['profileSha256'] == value['profileSha256']
    assert Path(remerge['profile']).stat().st_size == remerge['profileBytes']
    saved_remerge = read(remerge['receipt'])
    assert all(remerge[key] == entry for key, entry in saved_remerge.items())
    for name in ['stdout','stderr']:
        assert sha(Path(remerge['receipt']).parent/name) == remerge[name+'Sha256']
    assert proof['profileSha256'] == training['profile_sha256'] == value['profileSha256']
    assert value['profileSha256'] == sha(directory/'training/merged.profdata')
    assert training['original_lifetimes'] == 162 and training['engine_source_sha256'] == prepared['candidateSource']
    assert training['modes'] == [dict(budget=budget, originalCases=54) for budget in [1,2,3]]
    assert training['instrumented_engine_sha256'] == sha(instrumented)
    assert len(training['raw_profiles_sha256']) == len(training['runs']) == 162
    for file, digest in training['raw_profiles_sha256'].items():
        assert sha(file) == digest
    for file, digest in training['input_sha256'].items():
        assert sha(file) == digest
    assert training['canonical_merge_count'] == 1
    for row in training['runs']:
        rawdir = Path(row['directory'])
        for file, digest in row['sha256'].items():
            assert sha(rawdir/file) == digest
        wire = read(rawdir/'wire/receipt.json')
        for raw in wire['raw'].values():
            assert sha(raw['path']) == raw['sha256']
        assert sha(row['colors']['path']) == row['colors']['sha256']
    cli = read(directory/'focused/result.json')
    assert cli['schema'] == 'rook2-colors-three-focused-cli-v1' and cli['complete']
    assert cli['engine'] == str(candidate) and cli['engineSha256'] == sha(candidate)
    assert len(cli['cli']) == 13 and len(cli['affinityReplays']) == 2
    positives = [([],1,1,sorted(HELPERS)), (['--threads=1'],1,1,sorted(HELPERS)),
        (['--threads=2'],2,2,sorted(HELPERS)), (['--threads=3'],3,3,sorted(HELPERS)),
        (['--threads=8'],8,3,sorted(HELPERS)), (['--threads=3'],3,1,[14]),
        (['--threads=3'],3,2,[6,14]), (['--threads=8'],8,2,[6,14])]
    import json
    for row, (options, requested, configured, mask) in zip(cli['cli'], positives):
        assert row['argv'] == [str(candidate), *options, '--inspect-threads']
        assert row['inheritedMask'] == mask and row['exit'] == 0 and row['stderr'] == ''
        assert json.loads(row['stdout']) == dict(requested_threads=requested, configured_threads=configured)
    for row, argument in zip(cli['cli'][8:], ['0','-1','','oops','184467440737095516160']):
        assert row['argv'] == [str(candidate), '--threads='+argument, '--inspect-threads']
        assert row['exit'] != 0 and row['stdout'] == '' and row['stderr']
    workload = next(row for row in read(SPEC/'workloads.json')['cases'] if row['id'] == 'profile-08')
    oracle = next(row for row in read(SPEC/'replay-oracle.json')['cases'] if row['id'] == 'profile-08')
    for row, name, mask, configured in zip(cli['affinityReplays'], ['one-cpu','two-cpu'], [[14],[6,14]], [1,2]):
        rawdir = directory/'focused'/name
        assert row['requestedThreads'] == 3 and row['configuredThreads'] == configured and row['inheritedMask'] == mask
        assert len(row['taskAffinities']) == configured and all(value == mask for value in row['taskAffinities'].values())
        for file, digest in row['sha256'].items():
            assert sha(rawdir/file) == digest
        raw = dict(stdin=(rawdir/'stdin.raw').read_bytes(), stdout=(rawdir/'stdout.raw').read_bytes(),
                   stderr=(rawdir/'stderr.raw').read_bytes())
        assert raw['stdin'].startswith(b'cm_parm\n') and raw['stdin'].endswith(b'quit\n')
        assert raw['stdout'].startswith(b'cm_parm\n') and raw['stderr'] == b''
        projected = dict(stdin=raw['stdin'][8:-5], stdout=raw['stdout'][8:], stderr=raw['stderr'])
        actual = dict(stdout=projected['stdout'].decode(), stderr='', exit=dict(code=0,signal=None))
        assert audit.original_streams(actual, workload, oracle, projected) == row['orderedPosts']
    housekeeping_audit(directory/'housekeeping-prepare.json', 5)
    return value, receipt, effective
