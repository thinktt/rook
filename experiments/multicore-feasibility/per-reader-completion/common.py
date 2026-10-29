"""Frozen generic replay/placement harness adapted for per-reader completion registration.

Importing starts no process. Original raw replay, wait4 and placement checks are reused unchanged.
"""
import importlib.util
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EPOCH=HERE.parent/'epoch-colors'
LEGACY=HERE.parent/'colors-three'
CONTROL_EXPERIMENT=HERE.parent/'single-owner-activation'
CONTROL_RAW=Path('/home/legolas/rook2-experiments/single-owner-20261028-01')
PGO_EXPERIMENT=HERE.parent/'single-owner-own-pgo'
PGO_RAW=Path('/home/legolas/rook2-experiments/single-owner-own-pgo-20261028-01')
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01')
DEFAULT_CRATE=Path('/home/legolas/rook2-experiments/workspaces/per-reader-completion-20261029-01')
CONTROL_IMAGE=CONTROL_RAW/'rook2-candidate'
CONTROL_BUILD=CONTROL_RAW/'candidate-build'
CONTROL_SHA='d71c4f9fa662af73c81d891f16c2b56ded2d2ccfbe982ed5ae81829a14fd573d'
CASES=['profile-35','profile-08','profile-43']
NAMES=['preserved1','preserved3','inline1','owner3']
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
LIMITS=dict(perLifeSeconds=180,totalSeconds=1800,supervisorPlacementSeconds=10,inputGateSeconds=12)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


epoch=module('per_reader_completion_frozen_epoch_common',EPOCH/'common.py')
sha,read,write,snapshot=epoch.sha,epoch.read,epoch.write,epoch.snapshot
HELPERS,ACCOUNT,GATE,TAP,SPEC=epoch.HELPERS,epoch.ACCOUNT,epoch.GATE,epoch.TAP,epoch.SPEC
BUILD_ADAPTER,FOCUSED=epoch.BUILD_ADAPTER,HERE/'focused.py'
LAYOUT=HERE/'layout.py'
admit_build=epoch.admit_build
check_task_masks=epoch.check_task_masks
SPEC=epoch.SPEC
stop_owned=epoch.stop_owned
native_receipt,audit_placement,audit=epoch.native_receipt,epoch.audit_placement,epoch.audit
image_layout,dist=epoch.image_layout,epoch.dist


def frozen_module(name,path):
    previous=sys.modules.get('common')
    try:
        sys.modules['common']=epoch
        return module(name,path)
    finally:
        if previous is None: sys.modules.pop('common',None)
        else: sys.modules['common']=previous


collector=frozen_module('per_reader_completion_frozen_epoch_collector',EPOCH/'collect.py')
run_lifetime,idle_probe=collector.run_lifetime,collector.idle_probe
housekeeping=epoch.housekeeping
observer=frozen_module('per_reader_completion_frozen_epoch_observer',EPOCH/'reconcile.py')
readiness,readiness_summary=observer.readiness,observer.readiness_summary
control=module('per_reader_completion_preserved_generic_common',CONTROL_EXPERIMENT/'common.py')


def pgo_evidence():
    """Resolve the latest concise closure to its immutable full terminal audit."""
    concise=read(PGO_EXPERIMENT/'closure.json')
    assert concise['schema']=='rook2-single-owner-own-pgo-concise-closure-v1' and concise['complete']
    for name in ['fullTerminalAudit','rawComparisonAudit','rawTrainingAudit','pipeline','metadataInvocationCorrection']:
        row=concise[name];path=Path(row['path'])
        assert sha(path)==row['sha256'] and path.stat().st_size==row['bytes'],path
    full=read(concise['fullTerminalAudit']['path'])
    assert full['schema']=='rook2-single-owner-own-pgo-closure-v1' and full['complete']
    assert full['sourceFiles']==69 and full['sourceChangesAgainstGeneric']==[]
    assert full['reusedGenericControls']==70 and full['freshControlsThisLane']==0
    assert full['terminalNativeReceipts']==full['rowBindingsVerified']==491
    assert full['profileSha256']==concise['profileSha256']=='1a81bdacaeee3ac4b949cb495f8a99f0d68c96579cca4e7b807f83a501169910'
    return concise,full


def baseline():
    concise,full=pgo_evidence()
    values=dict(full['protectedArtifacts'])
    assert len(values)==37 and values[str(CONTROL_IMAGE)]==CONTROL_SHA
    image=full['images']['inline1']
    assert image==full['images']['owner3'] and image['path']==str(PGO_RAW/'rook2-pgo')
    assert image['sha256']=='c242f0e498ceeddb9aa2532cbace46730ffebcb6a0e756274179b3297c1b40da'
    values[image['path']]=image['sha256']
    values[str(PGO_RAW/'training/merged.profdata')]=full['profileSha256']
    assert len(values)==39
    for path,digest in values.items(): assert sha(path)==digest,path
    return values


def code_paths():
    return sorted(set([HERE/name for name in ['common.py','prepare.py','collect.py','reconcile.py','close_pipeline.py','focused.py','layout.py','native.py','source_check.py','freeze_source.py']]+epoch.code_paths()+[CONTROL_EXPERIMENT/'common.py']))


def reused_evidence_paths():
    paths=[CONTROL_EXPERIMENT/'preparation.json',CONTROL_EXPERIMENT/'closure.json',
        CONTROL_RAW/'pipeline.json',CONTROL_RAW/'prepared-run.json',CONTROL_RAW/'pilot/reconciled.json',
        CONTROL_RAW/'layout/result.json',CONTROL_RAW/'layout/stdout.raw',
        CONTROL_BUILD/'receipt.json',CONTROL_BUILD/'build.stderr',
        PGO_EXPERIMENT/'preparation.json',PGO_EXPERIMENT/'closure.json',PGO_RAW/'pipeline.json',
        PGO_RAW/'prepared-run.json',PGO_RAW/'use-build/receipt.json',PGO_RAW/'instrumented-build/receipt.json',
        PGO_RAW/'training/training.json',PGO_RAW/'training/reconciled.json',PGO_RAW/'full54/reconciled.json']
    proof=read(CONTROL_EXPERIMENT/'preparation.json')
    record=read(CONTROL_RAW/'prepared-run.json')
    paths += [Path(path) for path in record['inputSha256']]
    paths += [Path(path) for key in ['inputSha256','reusedEvidenceSha256'] for path in proof[key]]
    paths += [Path(path) for path in proof['repair']['archiveSha256']]
    concise,full=pgo_evidence()
    paths += [Path(concise[name]['path']) for name in
        ['fullTerminalAudit','rawComparisonAudit','rawTrainingAudit','pipeline','metadataInvocationCorrection']]
    return sorted(set(paths))


def retained_control_tests(record):
    """Recover the43 unchanged passing test identities, including the repaired fixture."""
    passed=[]
    for row in record['stages']:
        if row['stage'].startswith('tests-'):
            path=CONTROL_RAW/(row['stage']+'.stdout')
            assert sha(path)==row['stdoutSha256']
            passed+=re.findall(r'^test (\S+) \.\.\. ok$',path.read_text(),re.M)
    assert len(passed)==len(set(passed))==70
    retained=sorted(name for name in passed if not name.startswith('colors_worker::lifecycle_tests::'))
    assert len(retained)==43
    return retained


def preparation(path):
    """Source-only freeze admission. Selectors/counts are supplied before native work."""
    value=read(path)
    assert value['schema']=='rook2-per-reader-completion-source-preparation-v1'
    assert Path(value['candidateCrate']).resolve()==DEFAULT_CRATE
    assert Path(value['controlCrate']).resolve()==CONTROL_CRATE
    previous=sys.modules.get('common')
    try:
        sys.modules['common']=control
        control_proof=control.preparation(CONTROL_EXPERIMENT/'preparation.json')
        control_record=control.prepared_run(CONTROL_RAW/'prepared-run.json',CONTROL_EXPERIMENT/'preparation.json',control_proof)
    finally:
        if previous is None: sys.modules.pop('common',None)
        else: sys.modules['common']=previous
    assert isinstance(control_record,dict)
    assert value['controlSource']==control_proof['candidateSource']==control_record['source']==snapshot(CONTROL_CRATE)
    assert value['candidateSource']==snapshot(DEFAULT_CRATE)
    before,after=value['controlSource'],value['candidateSource']
    assert len(before)==len(after)==69
    assert sorted(name for name in before if before[name]!=after[name])==value['sourceChanges']==['src/colors_worker.rs']
    assert sorted(after.keys()-before.keys())==value['sourceAdded']==[]
    assert sorted(before.keys()-after.keys())==value['sourceRemoved']==[]
    for file in reused_evidence_paths(): assert value['reusedEvidenceSha256'][str(file)]==sha(file),file
    for file,digest in value['reusedEvidenceSha256'].items(): assert sha(file)==digest,file
    previous=read(CONTROL_RAW/'pipeline.json');closed=read(CONTROL_EXPERIMENT/'closure.json')
    assert previous['complete'] and previous['failure'] is None and previous.get('currentFailure') is None
    summary=dict(selectedLogicalControls=70,executions=71,passed=70,failed=1,
        passedBeforeRepair=69,repairPassed=1,completedControlsRepeated=0)
    assert control_record['testExecutionSummary']==closed['testExecutionSummary']==summary
    assert len(previous['stages'])==closed['stagesRun']==14
    assert [(row['stage'],row['exit']) for row in previous['stages'] if row['exit']]==[('tests-07-q-owner',101)]
    assert closed['candidateSource']==before and closed['focusedPassed']==70
    assert closed['replayLives']==48 and closed['idleProcesses']==4 and closed['orderedPosts']==560
    assert closed['repair']==control_proof['repair']==previous['repair']==control_record['repair']
    assert read(CONTROL_RAW/'pilot/reconciled.json')['complete']
    concise,pgo=pgo_evidence()
    assert pgo['candidateSource']==before and pgo['sourceChangesAgainstGeneric']==[]
    assert value['protectedArtifacts']==baseline()
    for key,expected in dict(priorGenericPassed=70,affectedExisting=27,newWorkerControls=7,rerun=34,retained=43).items():
        assert value['evidenceReuse'][key]==expected,key
    assert value['evidenceReuse']['retainedTestIdentities']==retained_control_tests(control_record)
    assert value['evidenceReuse']['priorTestExecutionSummary']==summary
    assert value['evidenceReuse']['priorTestRepair']==control_proof['repair']
    assert value['readinessSemantics']==control_proof['readinessSemantics']
    assert isinstance(value['sourceChallenge'],dict) and value['sourceChallenge']
    assert 'repair' not in value,'no continuation or repair in this new selected lane'
    assert isinstance(value['focused'],list) and value['focused']
    assert len(value['focused'])==1 and value['focused'][0]['selector']=='colors_worker::lifecycle_tests'
    assert value['focused'][0]['expectedPassed']==34
    assert value['focused'][0]['expectedTests']==value['sourceChallenge']['sourceBodyCheck']['affectedWorkerTests']
    assert len({row['name'] for row in value['focused']})==len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'],['--bin','rook2']]
        assert row['selector'] and row['name'].replace('-','').replace('_','').isalnum()
        assert type(row['expectedPassed']) is int and row['expectedPassed']>0
        assert len(row['expectedTests'])==len(set(row['expectedTests']))==row['expectedPassed']
        assert row['expectedTests']==sorted(row['expectedTests'])
        assert 0<row.get('limitSeconds',300)<=300
        for flag in ['exact','ignored']:
            if flag in row: assert type(row[flag]) is bool
    policy=read(HERE/'policy.json')
    assert policy['schema']=='rook2-per-reader-completion-policy-v1'
    for key,expected in dict(sourceFiles=len(after),sourceChanged=value['sourceChanges'],sourceAdded=value['sourceAdded'],
            focused=value['focused'],cases=CASES,names=NAMES,budgets=[1,3,1,3],
            warmupsPerCell=1,measuredPerCell=3,replayLives=48,measuredLives=36,idleProbes=4,idleMs=250,
            ownerCpu=14,helperCpus=[6,4],housekeepingCpus=sorted(HELPERS),unusedOwnedSiblings=[15,7,5],
            pipelineSeconds=3600,collectionSeconds=1800,perLifeSeconds=180,
            bothHooksRequested=True,candidateVariants=1,comparisonConfigurations=4,layoutSeconds=120,
            tuning=False,pgo=False).items(): assert policy[key]==expected,key
    required=code_paths()+[HERE/'plan.md',HERE/'policy.json',
        Path('/home/legolas/agent-memos/imp2-lead-to-imp2-per-reader-generic-discriminator-20261029.md'),
        ROOT/'docs/research/per-reader-completion-registration.md']
    for file in required: assert value['inputSha256'][str(file)]==sha(file),file
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    return value


def variants(candidate):
    hooks=['--owner-local-inventory','--q-owner-local-inventory']
    return {'preserved1':dict(path=str(CONTROL_IMAGE),budget=1,options=['--threads=1',*hooks],report=True),
        'preserved3':dict(path=str(CONTROL_IMAGE),budget=3,options=['--threads=3',*hooks],report=True),
        'inline1':dict(path=str(candidate),budget=1,options=['--threads=1',*hooks],report=True),
        'owner3':dict(path=str(candidate),budget=3,options=['--threads=3',*hooks],report=True)}


def schedule():
    rows=[]
    for case in CASES:
        rows += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            rows += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(rows)==48
    return rows


def admission(build,candidate,prepared):
    old,old_options=epoch.admit_build(CONTROL_BUILD,CONTROL_IMAGE,CONTROL_CRATE,prepared['controlSource'])
    new,new_options=epoch.admit_build(build,candidate,DEFAULT_CRATE,prepared['candidateSource'])
    assert old_options==new_options
    for tool in ['rustc','cargo']:
        assert old['toolchain'][tool]==new['toolchain'][tool]
        assert old['toolchain'][tool+'_executable_sha256']==new['toolchain'][tool+'_executable_sha256']
    return old,new


def layout_admission(path,candidate,prepared):
    """Validate the one saved production-layout projection without a process."""
    helper=module('per_reader_completion_saved_layout',LAYOUT)
    value=helper.audit_result(path,candidate,DEFAULT_CRATE)
    assert value['schema']=='rook2-per-reader-completion-layout-admission-v1' and value['complete']
    assert value['image']==image_layout(candidate) and value['crate']==str(DEFAULT_CRATE)
    assert value['sourceSha256']==prepared['candidateSource']
    assert value['requestedThreads']==value['configuredThreads']==3 and value['joined'] is True
    assert value['elapsedNs']==value['endedMonotonicNs']-value['startedMonotonicNs']>0
    assert value['endedMonotonicNs']<value['deadlineMonotonicNs']
    assert value['deadlineMonotonicNs']-value['startedMonotonicNs']<=120*10**9
    return value


def prepared_run(path,prepared_path,prepared):
    value=read(path);directory=path.parent
    assert value['schema']=='rook2-per-reader-completion-prepared-run-v1' and value['complete']
    assert value['sourcePreparation']==str(prepared_path) and value['sourcePreparationSha256']==sha(prepared_path)
    assert value['source']==prepared['candidateSource'] and value['evidenceReuse']==prepared['evidenceReuse']
    assert value['candidate']==image_layout(directory/'rook2-candidate') and value['control']==image_layout(CONTROL_IMAGE)
    assert value['pipelineDeadlineMonotonicNs']==value['pipelineStartMonotonicNs']+3600*10**9
    assert value['pipelineStartMonotonicNs']<=value['preparedMonotonicNs']<value['pipelineDeadlineMonotonicNs']
    stages=value['stages']
    assert [row['stage'] for row in stages]==[f'tests-{i:02d}-{row["name"]}' for i,row in enumerate(prepared['focused'])]+['candidate-build','cli-affinity','layout']
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    previous_end=value['pipelineStartMonotonicNs']
    caps=[row.get('limitSeconds',300) for row in prepared['focused']]+[300,420,120]
    for row,cap in zip(stages,caps):
        assert previous_end<=row['startedMonotonicNs']<row['endedMonotonicNs']<=value['preparedMonotonicNs']
        assert row['elapsedNs']==row['endedMonotonicNs']-row['startedMonotonicNs']
        assert row['deadlineMonotonicNs']==min(value['pipelineDeadlineMonotonicNs'],row['startedMonotonicNs']+cap*10**9)
        assert row['endedMonotonicNs']<row['deadlineMonotonicNs']
        previous_end=row['endedMonotonicNs']
        assert row['exit']==0
        for suffix in ['stdout','stderr']:
            file=directory/(row['stage']+'.'+suffix)
            assert value['inputSha256'][str(file)]==sha(file)==row[suffix+'Sha256']
    for row,tests in zip(stages,prepared['focused']):
        text=(directory/(row['stage']+'.stdout')).read_text()
        passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
        summaries=re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)
        assert passed==row['passedTests'] and len(passed)==len(set(passed))==tests['expectedPassed']
        assert summaries==[(str(len(passed)),'0','0')]
        assert sorted(passed)==tests['expectedTests']
        argv=['/usr/bin/cargo','test','--offline','--locked',*tests['target'],'--target','x86_64-unknown-linux-gnu',
            '--jobs','4','--target-dir',str(directory/'test-target'),tests['selector'],'--','--test-threads=1']
        if tests.get('exact',False): argv.append('--exact')
        if tests.get('ignored',False): argv.append('--ignored')
        assert row['argv']==argv and row['cwd']==str(DEFAULT_CRATE)
    assert stages[-3]['argv']==['/usr/bin/python3',str(BUILD_ADAPTER),'--crate',str(DEFAULT_CRATE),
        '--mode','generic','--bin','rook2','--jobs','4','--output',str(directory/'candidate-build')]
    assert stages[-2]['argv']==['/usr/bin/python3',str(FOCUSED),'--engine',str(directory/'rook2-candidate'),
        '--output',str(directory/'focused')]
    assert stages[-1]['argv']==['/usr/bin/python3',str(LAYOUT),
        '--engine',str(directory/'rook2-candidate'),'--output',str(directory/'layout')]
    layout_path=directory/'layout/result.json'
    projected=layout_admission(layout_path,directory/'rook2-candidate',prepared)
    assert value['layout']==dict(path=str(layout_path),sha256=sha(layout_path),report=projected)
    assert stages[-1]['startedMonotonicNs']<=projected['startedMonotonicNs']<projected['endedMonotonicNs']<=stages[-1]['endedMonotonicNs']
    for file in (directory/'layout').rglob('*'):
        if file.is_file(): assert value['inputSha256'][str(file)]==sha(file),file
    summary=dict(selectedLogicalControls=sum(row['expectedPassed'] for row in prepared['focused']),
        executions=sum(row['expectedPassed'] for row in prepared['focused']),
        passed=sum(row['expectedPassed'] for row in prepared['focused']),failed=0,completedControlsRepeated=0)
    assert value['testExecutionSummary']==summary
    admission(directory/'candidate-build',directory/'rook2-candidate',prepared)
    cli=read(directory/'focused/result.json')
    assert cli['schema']=='rook2-per-reader-completion-focused-cli-v1' and cli['complete']
    assert cli['engine']==str(directory/'rook2-candidate') and cli['engineSha256']==sha(cli['engine'])
    assert len(cli['cli'])==14 and len(cli['affinityReplays'])==2
    assert cli['cli'][8]['argv']==[str(directory/'rook2-candidate'),'--threads=3','--owner-local-inventory','--q-owner-local-inventory','--inspect-threads']
    for row in cli['affinityReplays']:
        assert row['argv']==[str(directory/'rook2-candidate'),'--threads=3','--owner-local-inventory',
            '--q-owner-local-inventory',*read(SPEC/'replay-oracle.json')['mode']]
    for row,name,mask,configured in zip(cli['affinityReplays'],['one-cpu','two-cpu'],[[14],[6,14]],[1,2]):
        assert row['requestedThreads']==3 and row['configuredThreads']==configured and row['inheritedMask']==mask
        assert len(row['taskAffinities'])==configured and all(value==mask for value in row['taskAffinities'].values())
        for file,digest in row['sha256'].items(): assert sha(directory/'focused'/name/file)==digest
    return value


def housekeeping_audit(path):
    record = read(path)
    assert record['schema'] == 'rook2-per-reader-completion-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus'] == sorted(HELPERS)
    assert len(record['applies']) == 52 and record['restored'] is not None
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


# Reports and sparse512 readiness semantics are the original epoch format.
colors_report=epoch.colors_report
