"""Frozen generic replay/placement harness extended for Q owner-local tactical inventory.

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
CONTROL_EXPERIMENT=HERE.parent/'owner-local-inventory'
CONTROL_RAW=Path('/home/legolas/rook2-experiments/owner-local-inventory-20261026-01')
PGO_EXPERIMENT=HERE.parent/'owner-local-own-pgo'
PGO_RAW=Path('/home/legolas/rook2-experiments/owner-local-own-pgo-20261026-01')
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/owner-local-inventory-20261026-01')
DEFAULT_CRATE=Path('/home/legolas/rook2-experiments/workspaces/q-owner-local-20261026-01')
CONTROL_IMAGE=CONTROL_RAW/'rook2-candidate'
CONTROL_BUILD=CONTROL_RAW/'candidate-build'
CONTROL_SHA='4b40e2b541bea6e2dd0a8f760bdc9a85ea498ca77f1f108ef24259de33efdc8c'
CASES=['profile-35','profile-08','profile-43']
NAMES=['preserved3','q-off3','q-on3']
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
LIMITS=dict(perLifeSeconds=180,totalSeconds=1800,supervisorPlacementSeconds=10,inputGateSeconds=12)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


epoch=module('q_owner_local_frozen_epoch_common',EPOCH/'common.py')
sha,read,write,snapshot=epoch.sha,epoch.read,epoch.write,epoch.snapshot
HELPERS,ACCOUNT,GATE,TAP,SPEC=epoch.HELPERS,epoch.ACCOUNT,epoch.GATE,epoch.TAP,epoch.SPEC
BUILD_ADAPTER,FOCUSED=epoch.BUILD_ADAPTER,HERE/'focused.py'
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


collector=frozen_module('q_owner_local_frozen_epoch_collector',EPOCH/'collect.py')
run_lifetime,idle_probe=collector.run_lifetime,collector.idle_probe
housekeeping=epoch.housekeeping
observer=frozen_module('q_owner_local_frozen_epoch_observer',EPOCH/'reconcile.py')
readiness,readiness_summary=observer.readiness,observer.readiness_summary
control=module('q_owner_local_preserved_generic_common',CONTROL_EXPERIMENT/'common.py')


def baseline():
    closure=read(PGO_EXPERIMENT/'closure.json')
    record=read(PGO_RAW/'prepared-run.json')
    assert closure['schema']=='rook2-owner-local-own-pgo-closure-v1' and closure['complete']
    assert record['complete'] and record['source']==closure['candidateSource']
    image=closure['images']['hook-on3']
    assert image==closure['images']['hook-off3']==closure['images']['inline1']==record['candidate']
    assert image['path']==str(PGO_RAW/'rook2-pgo')
    assert image['sha256']=='3d914cddf415cfb109bdabaf6eaf5b2384c3ca537a37a2f37a691c28ac5e91cc'
    assert closure['profileSha256']==record['profileSha256']=='bf909cd4b9a489f3de23e1b0b2d5bb45c0069f690354d76510636c8fed54cd1f'
    instrumented=record['instrumented']
    assert instrumented['path']==str(PGO_RAW/'rook2-instrumented')
    assert instrumented['sha256']=='6fdcc3ac2336819b3ec0fb65ed7247cb704cdea8bf45e9f56de726b2dcb9b9ee'
    values=dict(closure['protectedArtifacts'])
    values.update({image['path']:image['sha256'],instrumented['path']:instrumented['sha256'],
        str(PGO_RAW/'training/merged.profdata'):closure['profileSha256']})
    assert values[str(CONTROL_IMAGE)]==CONTROL_SHA
    assert len(values)==28
    for path,digest in values.items(): assert sha(path)==digest,path
    return values


def code_paths():
    return sorted(set([HERE/name for name in ['common.py','prepare.py','collect.py','reconcile.py','close_pipeline.py','focused.py']]+epoch.code_paths()))


def reused_evidence_paths():
    paths=[CONTROL_EXPERIMENT/'preparation.json',CONTROL_EXPERIMENT/'closure.json',
        CONTROL_EXPERIMENT/'compile-repair.json',CONTROL_RAW/'pipeline.json',CONTROL_RAW/'prepared-run.json',
        CONTROL_RAW/'pilot/reconciled.json',CONTROL_BUILD/'receipt.json',CONTROL_BUILD/'build.stderr',
        PGO_EXPERIMENT/'preparation.json',PGO_EXPERIMENT/'closure.json',PGO_RAW/'pipeline.json',
        PGO_RAW/'prepared-run.json',PGO_RAW/'use-build/receipt.json',PGO_RAW/'instrumented-build/receipt.json',
        PGO_RAW/'training/training.json',PGO_RAW/'training/reconciled.json']
    proof=read(CONTROL_EXPERIMENT/'preparation.json')
    record=read(CONTROL_RAW/'prepared-run.json')
    paths += [Path(path) for path in record['inputSha256']]
    paths += [Path(path) for key in ['inputSha256','reusedEvidenceSha256'] for path in proof[key]]
    pipeline=read(CONTROL_RAW/'pipeline.json')
    paths += [CONTROL_RAW/(row['stage']+'.'+suffix) for row in pipeline['stages']
        if row['stage'].startswith('tests-') for suffix in ['stdout','stderr']]
    return sorted(set(paths))


def preparation(path):
    value=read(path)
    assert value['schema']=='rook2-q-owner-local-source-preparation-v1'
    assert Path(value['candidateCrate']).resolve()==DEFAULT_CRATE
    assert Path(value['controlCrate']).resolve()==CONTROL_CRATE
    control_proof=control.preparation(CONTROL_EXPERIMENT/'preparation.json')
    control_record=control.prepared_run(CONTROL_RAW/'prepared-run.json',CONTROL_EXPERIMENT/'preparation.json',control_proof)
    assert isinstance(control_record,dict)
    assert value['controlSource']==control_proof['candidateSource']==control_record['source']==snapshot(CONTROL_CRATE)
    assert value['candidateSource']==snapshot(DEFAULT_CRATE)
    before,after=value['controlSource'],value['candidateSource']
    assert len(before)==66 and len(after)>=66
    assert sorted(name for name in before.keys() & after.keys() if before[name]!=after[name])==value['sourceChanges']
    assert sorted(after.keys()-before.keys())==value['sourceAdded']
    assert sorted(before.keys()-after.keys())==value['sourceRemoved']==[]
    affected={'src/quiescence.rs','src/evaluator.rs','src/session.rs','src/bin/rook2.rs'}
    for key in before:
        if key not in affected and not key.endswith('_tests.rs'):
            assert before[key]==after[key],key
    for file in reused_evidence_paths(): assert value['reusedEvidenceSha256'][str(file)]==sha(file),file
    for file,digest in value['reusedEvidenceSha256'].items(): assert sha(file)==digest,file
    previous=read(CONTROL_RAW/'pipeline.json')
    assert previous['complete'] and previous['failure'] is None
    assert sum(len(row.get('passedTests',[])) for row in previous['stages'])==47
    assert sum(len(row.get('passedTests',[])) for row in control_record['stages'])==47
    assert read(CONTROL_RAW/'pilot/reconciled.json')['complete']
    control_closure=read(CONTROL_EXPERIMENT/'closure.json')
    assert control_closure['complete'] and control_closure['focusedPassed']==47
    assert control_closure['candidateSource']==before
    assert control_closure['replayLives']==36 and control_closure['idleProcesses']==3
    pgo_proof,pgo_closure=read(PGO_EXPERIMENT/'preparation.json'),read(PGO_EXPERIMENT/'closure.json')
    pgo_record=read(PGO_RAW/'prepared-run.json')
    assert pgo_proof['candidateSource']==pgo_closure['candidateSource']==pgo_record['source']==before
    assert pgo_closure['complete'] and pgo_closure['sourceFiles']==66
    assert pgo_closure['sourceChangesAgainstGeneric']==[] and pgo_closure['reusedGenericControls']==47
    assert value['protectedArtifacts']==baseline()
    assert value['evidenceReuse']['genericBaselinePassed']==47
    assert all(key in value['evidenceReuse'] for key in ['affected','rerun','retained'])
    assert isinstance(value['readinessSemantics'],dict) and value['readinessSemantics']
    assert isinstance(value['sourceChallenge'],dict) and value['sourceChallenge']
    assert value['focused'] and len({row['name'] for row in value['focused']})==len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'],['--bin','rook2']]
        assert row['selector'] and row['name'].replace('-','').replace('_','').isalnum()
        assert type(row['expectedPassed']) is int and row['expectedPassed']>0
        assert 0<row.get('limitSeconds',300)<=300
    required=code_paths()+[HERE/'plan.md',HERE/'policy.json',
        Path('/home/legolas/agent-memos/imp2-lead-to-imp2-q-owner-local-discriminator-20261026.md')]
    for file in required: assert value['inputSha256'][str(file)]==sha(file),file
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    return value


def variants(candidate):
    ordinary=['--threads=3','--owner-local-inventory']
    return {'preserved3':dict(path=str(CONTROL_IMAGE),budget=3,options=list(ordinary),report=True),
        'q-off3':dict(path=str(candidate),budget=3,options=list(ordinary),report=True),
        'q-on3':dict(path=str(candidate),budget=3,options=[*ordinary,'--q-owner-local-inventory'],report=True)}


def schedule():
    rows=[]
    for case in CASES:
        rows += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            rows += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(rows)==36
    return rows


def admission(build,candidate,prepared):
    old,old_options=epoch.admit_build(CONTROL_BUILD,CONTROL_IMAGE,CONTROL_CRATE,prepared['controlSource'])
    new,new_options=epoch.admit_build(build,candidate,DEFAULT_CRATE,prepared['candidateSource'])
    assert old_options==new_options
    for tool in ['rustc','cargo']:
        assert old['toolchain'][tool]==new['toolchain'][tool]
        assert old['toolchain'][tool+'_executable_sha256']==new['toolchain'][tool+'_executable_sha256']
    return old,new


def prepared_run(path,prepared_path,prepared):
    value=read(path);directory=path.parent
    assert value['schema']=='rook2-q-owner-local-prepared-run-v1' and value['complete']
    assert value['sourcePreparation']==str(prepared_path) and value['sourcePreparationSha256']==sha(prepared_path)
    assert value['source']==prepared['candidateSource'] and value['evidenceReuse']==prepared['evidenceReuse']
    assert value['candidate']==image_layout(directory/'rook2-candidate') and value['control']==image_layout(CONTROL_IMAGE)
    assert value['pipelineDeadlineMonotonicNs']==value['pipelineStartMonotonicNs']+3600*10**9
    assert value['pipelineStartMonotonicNs']<=value['preparedMonotonicNs']<value['pipelineDeadlineMonotonicNs']
    stages=value['stages']
    assert [row['stage'] for row in stages]==[f'tests-{i:02d}-{row["name"]}' for i,row in enumerate(prepared['focused'])]+['candidate-build','cli-affinity']
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    previous_end=value['pipelineStartMonotonicNs']
    caps=[row.get('limitSeconds',300) for row in prepared['focused']]+[300,420]
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
        argv=['/usr/bin/cargo','test','--offline','--locked',*tests['target'],'--target','x86_64-unknown-linux-gnu',
            '--jobs','4','--target-dir',str(directory/'test-target'),tests['selector'],'--','--test-threads=1']
        if tests.get('exact',False): argv.append('--exact')
        if tests.get('ignored',False): argv.append('--ignored')
        assert row['argv']==argv and row['cwd']==str(DEFAULT_CRATE)
    assert stages[-2]['argv']==['/usr/bin/python3',str(BUILD_ADAPTER),'--crate',str(DEFAULT_CRATE),
        '--mode','generic','--bin','rook2','--jobs','4','--output',str(directory/'candidate-build')]
    assert stages[-1]['argv']==['/usr/bin/python3',str(FOCUSED),'--engine',str(directory/'rook2-candidate'),
        '--output',str(directory/'focused')]
    admission(directory/'candidate-build',directory/'rook2-candidate',prepared)
    cli=read(directory/'focused/result.json')
    assert cli['schema']=='rook2-q-owner-local-focused-cli-v1' and cli['complete']
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
    assert record['schema'] == 'rook2-q-owner-local-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus'] == sorted(HELPERS)
    assert len(record['applies']) == 39 and record['restored'] is not None
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
