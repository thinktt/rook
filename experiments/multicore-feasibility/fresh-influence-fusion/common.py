"""Frozen generic replay/placement harness extended for fresh Influence fusion.

Importing starts no process. The isolated coherent row producer, colors phases and private FULL seams change.
"""
import importlib.util
from pathlib import Path
import re
import sys
import ast
import types

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EPOCH=HERE.parent/'epoch-colors'
LEGACY=HERE.parent/'colors-three'
CONTROL_RAW=Path('/home/legolas/rook2-experiments/epoch-colors-20261026-01')
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01')
DEFAULT_CRATE=Path('/home/legolas/rook2-experiments/workspaces/fresh-influence-fusion-20261026-01')
CONTROL_IMAGE=CONTROL_RAW/'rook2-candidate'
CONTROL_BUILD=CONTROL_RAW/'candidate-build'
CONTROL_SHA='7ac72fc63cf4086944b3abfd71f45eb1f0347796f2520bb97aa87fc8de3fb65c'
CASES=['profile-35','profile-08','profile-43']
NAMES=['preserved3','unfused3','fused3']
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
LIMITS=dict(perLifeSeconds=180,totalSeconds=1800,supervisorPlacementSeconds=10,inputGateSeconds=12)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


epoch=module('fresh_fusion_frozen_epoch_common',EPOCH/'common.py')
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


collector=frozen_module('fresh_fusion_frozen_epoch_collector',EPOCH/'collect.py')
run_lifetime,idle_probe=collector.run_lifetime,collector.idle_probe
housekeeping=epoch.housekeeping
observer=frozen_module('fresh_fusion_frozen_epoch_observer',EPOCH/'reconcile.py')
readiness,readiness_summary=observer.readiness,observer.readiness_summary


def baseline():
    closure=read(HERE.parent/'fixed-layout-no-observations/closure.json')
    values=dict(closure['protectedArtifacts'])
    values.update({v['path']:v['sha256'] for v in closure['images'].values()})
    for path,digest in values.items(): assert sha(path)==digest,path
    return values


def code_paths():
    return sorted(set([HERE/name for name in ['common.py','prepare.py','collect.py','reconcile.py','focused.py']]+epoch.code_paths()))


def reused_evidence_paths():
    paths=[HERE.parent/'fixed-layout-no-observations/closure.json',EPOCH/'preparation.json',EPOCH/'closure.json',HERE.parent/'epoch-own-pgo/preparation.json',
        HERE.parent/'epoch-own-pgo/closure.json',HERE.parent/'epoch-inventory-four/closure.json',CONTROL_RAW/'pipeline.json',
        CONTROL_RAW/'prepared-run.json',CONTROL_RAW/'pilot/reconciled.json',CONTROL_BUILD/'receipt.json',CONTROL_BUILD/'build.stderr']
    pipeline=read(CONTROL_RAW/'pipeline.json')
    paths += [CONTROL_RAW/(row['stage']+'.'+suffix) for row in pipeline['stages']
        if row['stage'].startswith('tests-') for suffix in ['stdout','stderr']]
    return paths


def preparation(path):
    value=read(path)
    assert value['schema']=='rook2-fresh-influence-fusion-source-preparation-v1'
    assert Path(value['candidateCrate']).resolve()==DEFAULT_CRATE
    assert Path(value['controlCrate']).resolve()==CONTROL_CRATE
    assert value['controlSource']==read(EPOCH/'preparation.json')['candidateSource']==snapshot(CONTROL_CRATE)
    assert value['candidateSource']==snapshot(DEFAULT_CRATE)
    before,after=value['controlSource'],value['candidateSource']
    assert len(before)==64 and len(after)>=64
    assert sorted(name for name in before.keys() & after.keys() if before[name]!=after[name])==value['sourceChanges']
    assert sorted(after.keys()-before.keys())==value['sourceAdded']
    assert sorted(before.keys()-after.keys())==value['sourceRemoved']==[]
    for key in ['Cargo.toml','Cargo.lock','src/evaluator_worker.rs','src/activity.rs','src/shelter.rs']:
        assert before[key]==after[key],key
    for file in reused_evidence_paths(): assert value['reusedEvidenceSha256'][str(file)]==sha(file),file
    for file,digest in value['reusedEvidenceSha256'].items(): assert sha(file)==digest,file
    previous=read(CONTROL_RAW/'pipeline.json')
    assert previous['complete'] and previous['failure'] is None
    assert sum(len(row.get('passedTests',[])) for row in previous['stages'])==32
    assert read(CONTROL_RAW/'pilot/reconciled.json')['complete']
    assert value['protectedArtifacts']==baseline()
    assert value['evidenceReuse']['genericBaselinePassed']==32
    assert all(key in value['evidenceReuse'] for key in ['affected','rerun','retained'])
    assert value['readinessSemantics']['fused'].startswith('includes fresh map')
    assert value['focused'] and len({row['name'] for row in value['focused']})==len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'],['--bin','rook2']]
        assert row['selector'] and row['name'].replace('-','').replace('_','').isalnum()
        assert type(row['expectedPassed']) is int and row['expectedPassed']>0
        assert 0<row.get('limitSeconds',300)<=300
    required=code_paths()+[HERE/'plan.md',HERE/'policy.json',
        Path('/home/legolas/agent-memos/imp2-lead-to-imp2-fresh-influence-fusion-discriminator-20261026.md')]
    for file in required: assert value['inputSha256'][str(file)]==sha(file),file
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    return value


def variants(candidate):
    return dict(preserved3=dict(path=str(CONTROL_IMAGE),budget=3,options=['--threads=3'],report=True),
        unfused3=dict(path=str(candidate),budget=3,options=['--threads=3'],report=True),
        fused3=dict(path=str(candidate),budget=3,options=['--threads=3','--fresh-influence-fusion'],report=True))


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
    assert value['schema']=='rook2-fresh-influence-fusion-prepared-run-v1' and value['complete']
    assert value['sourcePreparation']==str(prepared_path) and value['sourcePreparationSha256']==sha(prepared_path)
    assert value['source']==prepared['candidateSource'] and value['evidenceReuse']==prepared['evidenceReuse']
    assert value['candidate']==image_layout(directory/'rook2-candidate') and value['control']==image_layout(CONTROL_IMAGE)
    assert value['pipelineDeadlineMonotonicNs']==value['pipelineStartMonotonicNs']+3600*10**9
    assert value['pipelineStartMonotonicNs']<=value['preparedMonotonicNs']<value['pipelineDeadlineMonotonicNs']
    stages=value['stages']
    assert [row['stage'] for row in stages]==[f'tests-{i:02d}-{row["name"]}' for i,row in enumerate(prepared['focused'])]+['candidate-build','cli-affinity']
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    for row in stages:
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
    assert cli['schema']=='rook2-fresh-influence-fusion-focused-cli-v1' and cli['complete']
    assert cli['engine']==str(directory/'rook2-candidate') and cli['engineSha256']==sha(cli['engine'])
    assert len(cli['cli'])==14 and len(cli['affinityReplays'])==2
    assert cli['cli'][8]['argv']==[str(directory/'rook2-candidate'),'--threads=3','--fresh-influence-fusion','--inspect-threads']
    for row in cli['affinityReplays']:
        assert '--fresh-influence-fusion' in row['argv']
    for row,name,mask,configured in zip(cli['affinityReplays'],['one-cpu','two-cpu'],[[14],[6,14]],[1,2]):
        assert row['requestedThreads']==3 and row['configuredThreads']==configured and row['inheritedMask']==mask
        assert len(row['taskAffinities'])==configured and all(value==mask for value in row['taskAffinities'].values())
        for file,digest in row['sha256'].items(): assert sha(directory/'focused'/name/file)==digest
    return value


def housekeeping_audit(path):
    record = read(path)
    assert record['schema'] == 'rook2-fresh-influence-fusion-housekeeping-v1'
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


def _base_function(function, value):
    namespace=dict(function.__globals__)
    namespace['read']=lambda path:value
    return types.FunctionType(function.__code__,namespace,function.__name__,function.__defaults__,function.__closure__)


def colors_report(path,budget,idle=False):
    value=read(path)
    launch=read(Path(path).parent/'launch.json')
    name=launch.get('step',{}).get('variant',launch.get('variant'))
    if name=='preserved3':
        assert 'fusion' not in value
    else:
        witness=value['fusion'];assert set(witness)=={'enabled','rowReady'}
        assert witness['enabled'] is (name=='fused3')
        rows=witness['rowReady'];assert len(rows)==2 and all(type(v)is int and 0<=v<2**64 for v in rows)
        assert rows[0]==rows[1]
        if name=='fused3' and not idle: assert rows[0]>0,'no native fusion activation'
        else: assert rows==[0,0]
    base=dict(value);base.pop('fusion',None)
    _base_function(epoch.colors_report,base)(path,budget,idle)
    return value


def readiness(directory,row,budget,enabled=True,idle=False):
    path=directory/'colors.json';assert enabled and row['path']==str(path) and row['sha256']==sha(path)
    value=colors_report(path,budget,idle);assert row['report']==value
    base=dict(value);base.pop('fusion',None)
    projected=dict(row,report=base)
    _base_function(observer.readiness,base)(directory,projected,budget,True,idle)
    return value

# Keep old raw replay/placement logic; only the report view is extended.
collector.colors_report=colors_report
