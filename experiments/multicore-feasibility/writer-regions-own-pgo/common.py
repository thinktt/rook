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
SOURCE_CHECKPOINT = '12c6f0dac21e6b102f435deec1b816aea5737d36'
GENERIC = HERE.parent/'writer-regions'
LEAD_REVIEW = Path('/home/legolas/agent-memos/imp2-lead-to-imp2-writer-regions-own-pgo-20261026.md')
GENERIC_RAW = Path('/home/legolas/rook2-experiments/writer-regions-20261026-01')
SERIAL_BUILD = Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build')
PRIOR_BUILD = Path('/home/legolas/rook2-experiments/q-owner-local-own-pgo-20261026-01/use-build')
RETAINED_BUILD = PRIOR_BUILD
PRACTICAL_BUILD = PRIOR_BUILD  # frozen collector API alias
SERIAL_IMAGE = SERIAL_BUILD/'rook2-exact'
PRIOR_IMAGE = PRIOR_BUILD.parent/'rook2-pgo'
RETAINED_IMAGE = PRIOR_IMAGE
PRACTICAL_IMAGE = PRIOR_IMAGE
SERIAL_SHA = '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a'
PRIOR_SHA = 'f8b829a79e43a90a0396c3baacb8f44f23476f6d9e7a9661626f5c1e8b467c62'
RETAINED_SHA = PRIOR_SHA
PRACTICAL_SHA = PRIOR_SHA
PRIOR_PROFILE_SHA = 'bbb858b01018cea09311ac5fe3b5fb5bc18c3b716e2f6a7bb5df83c794527ed4'
NAMES = ['serial1', 'retained1', 'retained3', 'inline1', 'regions3']
TRAINING_MODES = [dict(variant='inline1', budget=1, options=['--threads=1','--owner-local-inventory','--q-owner-local-inventory']),
    dict(variant='current2', budget=2, options=['--threads=2','--owner-local-inventory','--q-owner-local-inventory']),
    dict(variant='q-off3', budget=3, options=['--threads=3','--owner-local-inventory']),
    dict(variant='q-on3', budget=3, options=['--threads=3','--owner-local-inventory','--q-owner-local-inventory'])]
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
DEFAULT_CRATE = Path('/home/legolas/rook2-experiments/workspaces/writer-regions-20261026-01')
HELPERS = epoch.HELPERS
BUILD_ADAPTER, FOCUSED = epoch.BUILD_ADAPTER, HERE/'focused.py'
LAYOUT = HERE/'layout.py'
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


generic = module('writer_regions_own_pgo_frozen_generic_common', GENERIC/'common.py')


def baseline():
    result = generic.baseline()
    assert result==read(GENERIC/'closure.json')['protectedArtifacts']
    result[str(GENERIC_RAW/'rook2-candidate')] = '8c217f96ceae16ea29e623276413145e976cbed6cf35e38fa38d029ce820e3ef'
    for directory in [SERIAL_BUILD, PRIOR_BUILD]:
        for path, digest in read(directory/'receipt.json')['pgo']['input_sha256_before'].items():
            assert path not in result or result[path] == digest
            assert sha(path) == digest, path
    assert result[str(SERIAL_IMAGE)] == SERIAL_SHA
    assert result[str(PRIOR_IMAGE)] == PRIOR_SHA
    assert result[str(PRIOR_BUILD.parent/'training/merged.profdata')] == PRIOR_PROFILE_SHA
    assert len(result)==34
    for path, digest in result.items():
        assert sha(path) == digest, path
    return result


def code_paths():
    paths = [HERE/name for name in ['common.py', 'prepare.py', 'train.py',
        'training_reconcile.py', 'collect.py', 'reconcile.py', 'focused.py', 'layout.py']]
    return sorted(set(paths+generic.code_paths()+[SERIAL_BUILD/'receipt.json', PRIOR_BUILD/'receipt.json']))


def reused_evidence_paths():
    paths = [GENERIC/'preparation.json', GENERIC/'closure.json',
        GENERIC_RAW/'pipeline.json', GENERIC_RAW/'prepared-run.json',
        GENERIC_RAW/'pilot/plan.json', GENERIC_RAW/'pilot/result.json', GENERIC_RAW/'pilot/reconciled.json',
        GENERIC_RAW/'candidate-build/receipt.json', GENERIC_RAW/'candidate-build/build.stderr']
    proof, closure = read(GENERIC/'preparation.json'), read(GENERIC/'closure.json')
    paths += [Path(path) for key in ['inputSha256', 'reusedEvidenceSha256'] for path in proof[key]]
    paths += [Path(path) for path in closure['inputSha256']]
    previous=read(HERE.parent/'owner-local-own-pgo/closure.json')
    paths += [HERE.parent/'owner-local-own-pgo/closure.json',Path(previous['failedCloserReceipt']),
        Path(previous['closureAdapter']),HERE.parent/'owner-local-own-pgo/close_pipeline.py']
    for directory in [SERIAL_BUILD,PRIOR_BUILD]:
        paths += [Path(path) for path in read(directory/'receipt.json')['pgo']['input_sha256_before']]
    return sorted(set(paths))


def generic_evidence(prepared):
    pins = prepared['reusedEvidenceSha256']
    assert all(str(path) in pins for path in reused_evidence_paths())
    for path, digest in pins.items():
        assert sha(path) == digest, path
    proof = generic.preparation(GENERIC/'preparation.json')
    closure, pipeline = read(GENERIC/'closure.json'), read(GENERIC_RAW/'pipeline.json')
    reconciled = read(GENERIC_RAW/'pilot/reconciled.json')
    assert closure['schema']=='rook2-writer-regions-closure-v1' and closure['complete'] and reconciled['complete']
    assert pipeline['complete'] and pipeline['prepared'] and pipeline['collected'] and pipeline['failure'] is None
    assert proof['candidateSource'] == closure['candidateSource'] == prepared['candidateSource'] == snapshot(DEFAULT_CRATE)
    assert len(prepared['candidateSource']) == 68
    saved = generic.prepared_run(GENERIC_RAW/'prepared-run.json', GENERIC/'preparation.json', proof)
    assert isinstance(saved,dict)
    tests = [row for row in saved['stages'] if row['stage'].startswith('tests-')]
    assert sum(len(row['passedTests']) for row in tests) == closure['focusedPassed'] == 25
    assert proof['evidenceReuse']['genericBaselinePassed']==59 and proof['evidenceReuse']['retained']==35
    assert closure['cliControls']==14 and closure['fallbackLives']==2
    assert closure['replayLives']==reconciled['replayLives']==48
    assert closure['idleProcesses']==reconciled['idleProcesses']==4
    for path,digest in closure['inputSha256'].items(): assert sha(path)==digest,path
    for key in ['pipelineStartMonotonicNs','pipelineDeadlineMonotonicNs']:
        assert saved[key]==pipeline[key]==closure[key]
    assert closure['pipelineDeadlineMonotonicNs']==closure['pipelineStartMonotonicNs']+3600*10**9
    assert pipeline['pipelineEndedMonotonicNs']==closure['pipelineEndedMonotonicNs']<closure['pipelineDeadlineMonotonicNs']
    previous=read(HERE.parent/'owner-local-own-pgo/closure.json')
    assert previous['complete'] and previous['closureToolFailures']==1
    failed_path=Path(previous['failedCloserReceipt'])
    assert sha(failed_path)==previous['failedCloserReceiptSha256']
    assert sha(previous['closureAdapter'])==previous['closureAdapterSha256']
    failed=read(failed_path)
    assert failed['exitCode']==1 and 'tuple indices' in failed['error']
    assert failed['executedEngineOrBuildLives']==failed['completedRequestsRepeated']==0
    assert failed['nativePipelineChanged'] is False and failed['sourceProfileArtifactChanged'] is False
    assert sha(HERE.parent/'owner-local-own-pgo/close_pipeline.py')==failed['frozenCloserSha256']
    return dict(freshGenericControls=25, retainedGenericControls=35, genericReplayLives=48, genericIdleProcesses=4,
        genericImage=image_layout(GENERIC_RAW/'rook2-candidate'), genericLayout=saved['layout'], sourceChangesAgainstGeneric=[],
        evidenceReuse=proof['evidenceReuse'], sourceFiles=68,
        genericClosure=str(GENERIC/'closure.json'), genericClosureSha256=sha(GENERIC/'closure.json'),
        genericAudit=str(GENERIC_RAW/'pilot/reconciled.json'), genericAuditSha256=sha(GENERIC_RAW/'pilot/reconciled.json'),
        preservedMetadataFailure=dict(path=str(failed_path),sha256=sha(failed_path),
            adapter=previous['closureAdapter'],adapterSha256=previous['closureAdapterSha256'],
            repeatedNativeRequests=0),
        scope='unchanged source68 Q/ordinary/arithmetic/lifecycle evidence reused read-only; fresh25 plus retained35; prior metadata-only closer failure preserved; no repeated unit campaign')


def preparation(path):
    value = read(path)
    assert value['schema'] == 'rook2-writer-regions-own-pgo-source-preparation-v1'
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
    hooks=['--owner-local-inventory','--q-owner-local-inventory']
    return {'serial1':dict(path=str(SERIAL_IMAGE),budget=1,options=[],report=False),
        'retained1':dict(path=str(RETAINED_IMAGE),budget=1,options=['--threads=1',*hooks],report=True),
        'retained3':dict(path=str(RETAINED_IMAGE),budget=3,options=['--threads=3',*hooks],report=True),
        'inline1':dict(path=str(candidate),budget=1,options=['--threads=1',*hooks],report=True),
        'regions3':dict(path=str(candidate),budget=3,options=['--threads=3',*hooks],report=True)}


def schedule():
    steps = []
    for index, case in enumerate(cases()):
        order = NAMES[index % 5:]+NAMES[:index % 5]
        steps += [dict(case=case, variant=name, warmup=False, repeat=1) for name in order]
    assert len(steps) == 270
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
    for name, directory in [('serial1',SERIAL_BUILD),('retained1',RETAINED_BUILD),('retained3',RETAINED_BUILD)]:
        receipt = read(directory/'receipt.json')
        before, after = receipt['source_sha256_before'], prepared['candidateSource']
        source[name] = dict(changed=sorted(key for key in before.keys() & after.keys() if before[key]!=after[key]),
            added=sorted(after.keys()-before.keys()), removed=sorted(before.keys()-after.keys()))
        profiles[name] = dict(path=receipt['pgo']['profile'], sha256=sha(receipt['pgo']['profile']),
            trainingRecord=receipt['pgo']['training_record'], trainingRecordSha256=sha(receipt['pgo']['training_record']))
    source['genericWriterRegions'] = dict(changed=[],added=[],removed=[])
    profiles['candidate'] = dict(path=str(candidate_profile),sha256=sha(candidate_profile),modes=TRAINING_MODES,originalCasesPerMode=54)
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
        requestedThreads=budget,configuredThreads=len(receipt['native_post_exec']['task_affinities']),nativeOptions=list(options),
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
    assert record['schema'] == 'rook2-writer-regions-own-pgo-housekeeping-v1'
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



def layout_admission(path,candidate,prepared):
    """Revalidate the one saved use-image projection without invoking native code."""
    helper=module('writer_regions_own_pgo_saved_layout',LAYOUT)
    value=helper.audit_result(path,candidate,DEFAULT_CRATE)
    assert value['schema']=='rook2-writer-regions-own-pgo-layout-admission-v1' and value['complete']
    assert value['image']==image_layout(candidate) and value['crate']==str(DEFAULT_CRATE)
    assert value['sourceSha256']==prepared['candidateSource']
    assert value['requestedThreads']==value['configuredThreads']==3 and value['joined'] is True
    assert value['elapsedNs']==value['endedMonotonicNs']-value['startedMonotonicNs']>0
    assert value['endedMonotonicNs']<value['deadlineMonotonicNs']
    assert value['deadlineMonotonicNs']-value['startedMonotonicNs']<=120*10**9
    return value


def prepared_run(path, prepared_path, prepared):
    """Read-only exact-image/recipe/training/CLI admission after preparation."""
    value = read(path)
    assert value['schema'] == 'rook2-writer-regions-own-pgo-prepared-run-v1' and value['complete']
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
        'instrumented-build','training','training-audit','use-build','cli-affinity','layout']
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
        ['/usr/bin/python3', str(FOCUSED), '--engine', str(candidate), '--output', str(directory/'focused')],
        ['/usr/bin/python3', str(LAYOUT), '--engine', str(candidate), '--output', str(directory/'layout')]]
    previous_end = start
    for row, argv, cap in zip(stages, expected, [300,2500,120,300,420,120]):
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
    assert proof == value['trainingAudit'] and proof['complete'] and proof['nativeProcesses'] == 216
    assert proof['remerge']['byteIdentical'] is True
    assert proof['schema'] == 'rook2-writer-regions-own-pgo-training-audit-v1'
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
    assert training['original_lifetimes'] == 216 and training['engine_source_sha256'] == prepared['candidateSource']
    assert training['modes'] == [dict(**mode, originalCases=54) for mode in TRAINING_MODES]
    assert training['instrumented_engine_sha256'] == sha(instrumented)
    assert len(training['raw_profiles_sha256']) == len(training['runs']) == 216
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
    assert cli['schema'] == 'rook2-writer-regions-own-pgo-focused-cli-v1' and cli['complete']
    assert cli['engine'] == str(candidate) and cli['engineSha256'] == sha(candidate)
    assert len(cli['cli']) == 14 and len(cli['affinityReplays']) == 2
    positives = [([],1,1,sorted(HELPERS)), (['--threads=1'],1,1,sorted(HELPERS)),
        (['--threads=2'],2,2,sorted(HELPERS)), (['--threads=3'],3,3,sorted(HELPERS)),
        (['--threads=8'],8,3,sorted(HELPERS)), (['--threads=3'],3,1,[14]),
        (['--threads=3'],3,2,[6,14]), (['--threads=8'],8,2,[6,14]),
        (['--threads=3','--owner-local-inventory','--q-owner-local-inventory'],3,3,sorted(HELPERS))]
    import json
    for row, (options, requested, configured, mask) in zip(cli['cli'], positives):
        assert row['argv'] == [str(candidate), *options, '--inspect-threads']
        assert row['inheritedMask'] == mask and row['exit'] == 0 and row['stderr'] == ''
        assert json.loads(row['stdout']) == dict(requested_threads=requested, configured_threads=configured)
    for row, argument in zip(cli['cli'][9:], ['0','-1','','oops','184467440737095516160']):
        assert row['argv'] == [str(candidate), '--threads='+argument, '--inspect-threads']
        assert row['exit'] != 0 and row['stdout'] == '' and row['stderr']
    workload = next(row for row in read(SPEC/'workloads.json')['cases'] if row['id'] == 'profile-08')
    oracle = next(row for row in read(SPEC/'replay-oracle.json')['cases'] if row['id'] == 'profile-08')
    for row, name, mask, configured in zip(cli['affinityReplays'], ['one-cpu','two-cpu'], [[14],[6,14]], [1,2]):
        rawdir = directory/'focused'/name
        assert row['argv']==[str(candidate),'--threads=3','--owner-local-inventory',
            '--q-owner-local-inventory',*read(SPEC/'replay-oracle.json')['mode']]
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
    layout_path=directory/'layout/result.json'
    projected=layout_admission(layout_path,candidate,prepared)
    assert value['layout']==dict(path=str(layout_path),sha256=sha(layout_path),report=projected)
    assert stages[-1]['startedMonotonicNs']<=projected['startedMonotonicNs']<projected['endedMonotonicNs']<=stages[-1]['endedMonotonicNs']
    for file in (directory/'layout').rglob('*'):
        if file.is_file(): assert value['inputSha256'][str(file)]==sha(file),file
    housekeeping_audit(directory/'housekeeping-prepare.json', 6)
    return value, receipt, effective
