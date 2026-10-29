"""Fixed two-replay cohort adapters; imports never launch native work."""
import ast
import importlib.util
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];COUNT=HERE.parent/'frontier-scale-count'
CRATE=Path('/home/legolas/rook2-experiments/workspaces/frontier-cohort-20261029-01')
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/frontier-scale-count-20261029-01')
CHANGED=['src/bin/rook2.rs','src/evaluator.rs','src/frontier_scale.rs','src/lib.rs','src/ordinary.rs','src/quiescence.rs']
ADDED=['src/frontier_cohort.rs','src/frontier_cohort/io.rs','src/frontier_cohort/tests.rs']
OPTIONS=['--threads=3','--owner-local-inventory','--q-owner-local-inventory']
PIPELINE_SECONDS=1800;LIFE_SECONDS=180
REPORT='frontier-scale.json';COHORT_REPORT='frontier-cohort.json'
REPORT_ENV='ROOK2_FRONTIER_SCALE_REPORT';ENV_PREFIX='ROOK2_FRONTIER_COHORT_'
COUNTS=dict(E6=7963,S6=227806,M7=319911,F7=244603)
TESTS=sorted('frontier_cohort::tests::'+name for name in [
    'exact_keys_keep_chronology_actual_map_epoch_and_congruent_plane_filter',
    'position_root_binary_roundtrip_preserves_chronology_and_rejects_derived_disagreement',
    'duplicate_parent_occurrences_native_order_and_explicit_caps_are_not_samples',
    'cohort_skip_domain_repeats_exact_private_ordinary_depth_zero_admission',
    'component_histories_distinguish_prior_first_repeat_no_demand_and_disjoint_intervals',
    'root_before_prefix_and_actual_private_demand_hooks_keep_supplied_map_authority'])
MEMOS=[Path('/home/legolas/agent-memos')/name for name in [
    'imp2-lead-to-imp2-frontier-cohort-observation-20261029.md','imp2-frontier-cohort-leaf-contract-20261029.md']]
SERIALIZATION=dict(version=1,headerBytes=1660,footerBytes=108,parentBytes=125,
    captureJobBytes=6,poolJobBytes=14,ledgerJobBytes=30,mapPoolBytes=269,chainPoolBytes=257,
    mapHistoryBytes=150,chainHistoryBytes=191,captureMaxBytes=3622632,poolMaxBytes=143607528,
    ledgerMaxBytes=99305192,parentCap=16384,jobCap=262144,observerBytes=536870912,
    summaryTextMaxBytes=65535,summaryFileMaxBytes=65536,sampleStride=512,fixedReserveBytes=524288,
    auditWorkingStorageMaxBytes=134217728,auditJsonMaxBytes=1048576,auditFinalMetadataReserveBytes=262144)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


count=module('frontier_cohort_frozen_count_common',COUNT/'common.py')
sha,read,write,snapshot=count.sha,count.read,count.write,count.snapshot
HELPERS,ACCOUNT,GATE,TAP,SPEC=count.HELPERS,count.ACCOUNT,count.GATE,count.TAP,count.SPEC
BUILD_ADAPTER=count.BUILD_ADAPTER
housekeeping,audit,audit_placement=count.housekeeping,count.audit,count.audit_placement
image_layout,admit_build,check_task_masks=count.image_layout,count.admit_build,count.check_task_masks
collector=count.collector
original_environment=count.original_environment


def step(mode):
    assert mode in ['capture','observe']
    return dict(case='profile-35',variant='frontier-cohort-'+mode,warmup=False,repeat=1)


def cohort_env(root,mode):
    assert mode in ['capture','expand','observe']
    return {ENV_PREFIX+key:str(value) for key,value in dict(MODE=mode,CAPTURE=root/'capture.bin',
        POOL=root/'pool.bin',LEDGER=root/'ledger.bin',REPORT=root/mode/COHORT_REPORT).items()}


def environment(directory,report):
    env=original_environment(directory,report);mode=directory.name
    env.update(cohort_env(directory.parent,mode));env[REPORT_ENV]=str(directory/REPORT)
    write(directory/'frontier-env.json',dict(schema='rook2-frontier-cohort-environment-v1',
        variables={key:value for key,value in env.items() if key.startswith(ENV_PREFIX) or key==REPORT_ENV}))
    return env


collector.environment=environment
run_lifetime=collector.run_lifetime
previous=sys.modules.get('common')
try:
    sys.modules['common']=count;count_audit=module('frontier_cohort_frozen_count_audit',COUNT/'reconcile.py')
finally:
    if previous is None:sys.modules.pop('common',None)
    else:sys.modules['common']=previous


def prior_evidence():
    path=COUNT/'closure.json';concise=read(path)
    assert concise['schema']=='rook2-frontier-scale-count-concise-closure-v1' and concise['complete']
    row=concise['fullTerminalAudit'];assert sha(row['path'])==row['sha256']
    full=read(row['path']);assert full['complete'] and len(full['protectedArtifacts'])==42
    assert full['source']==snapshot(CONTROL_CRATE) and full['focusedPassed']==6
    return path,concise,full


def baseline():
    _,_,full=prior_evidence();result=dict(full['protectedArtifacts']);image=full['image']
    assert image['sha256']=='3a0347b7e859a5900c6602f617cfb98be94e011a545485a687f0ab2cc17cb0d8'
    result[image['path']]=image['sha256'];assert len(result)==43
    for path,digest in result.items():assert sha(path)==digest,path
    return result


def code_paths():
    return sorted(set([HERE/name for name in ['common.py','pipeline.py','reconcile.py','freeze_source.py']]+count.code_paths()))


def reused_paths():
    path,concise,_=prior_evidence()
    return count.reused_paths()+[path,Path(concise['fullTerminalAudit']['path']),COUNT/'preparation.json',
        Path(concise['pipeline']['path']),Path(concise['buildReceipt']['path'])]


def source_admission():
    before,after=snapshot(CONTROL_CRATE),snapshot(CRATE)
    assert before==read(COUNT/'preparation.json')['candidateSource'] and len(before)==70 and len(after)==73
    assert sorted(name for name in before if before[name]!=after[name])==CHANGED
    assert sorted(after.keys()-before.keys())==ADDED and not before.keys()-after.keys()
    old=(CONTROL_CRATE/'src/frontier_scale.rs').read_text();new=(CRATE/'src/frontier_scale.rs').read_text()
    # Only globals route the SAME optional original Instants; State and all six
    # aggregate test bodies remain exact and their closed executions are reused.
    assert old.split('pub(crate) fn begin_search()')[0]==new.split('pub(crate) fn begin_search()')[0]
    assert old.split('#[cfg(test)]',1)[1]==new.split('#[cfg(test)]',1)[1]
    tests=sorted('frontier_cohort::tests::'+name for name in re.findall(r'#\[test\]\s*fn\s+(\w+)\s*\(',
        (CRATE/'src/frontier_cohort/tests.rs').read_text()))
    assert tests==TESTS
    binary=(CRATE/'src/bin/rook2.rs').read_text();assert REPORT_ENV in binary
    core=(CRATE/'src/frontier_cohort.rs').read_text();io=(CRATE/'src/frontier_cohort/io.rs').read_text()
    assert 'rook2-frontier-cohort-v1' in io and ENV_PREFIX in core
    return before,after


def preparation(path):
    value=read(path);before,after=source_admission();policy=read(HERE/'policy.json')
    assert value['schema']=='rook2-frontier-cohort-preparation-v1'
    assert value['controlSource']==before and value['candidateSource']==after
    assert value['sourceChanges']==CHANGED and value['sourceAdded']==ADDED and value['sourceRemoved']==[]
    assert value['candidateCrate']==str(CRATE) and value['controlCrate']==str(CONTROL_CRATE)
    assert value['focused']==dict(target=['--lib'],selector='frontier_cohort::tests',expectedTests=TESTS,expectedPassed=6)
    assert value['reusedAggregateTests']==count.TESTS and value['serialization']==SERIALIZATION
    assert value['protectedArtifacts']==baseline() and value['options']==OPTIONS and value['case']=='profile-35'
    assert value['pipelineSeconds']==1800 and value['perLifeSeconds']==180
    assert policy['schema']=='rook2-frontier-cohort-policy-v1'
    for key,expected in dict(sourceFiles=73,sourceChanged=CHANGED,sourceAdded=ADDED,case='profile-35',
            iterations=[6,7],counts=list(COUNTS),expectedCounts=list(COUNTS.values()),expectedN=3746843,expectedR=10506351,
            mode=3,bothHooksRequested=True,replayLives=2,orderedPosts=13,pipelineSeconds=1800,perLifeSeconds=180,
            ownerCpu=14,helperCpus=[6,4],housekeepingCpus=sorted(HELPERS),unusedOwnedSiblings=[15,7,5],
            parentCap=16384,jobCap=262144,observerByteCap=536870912,indexSlots=524288,sampleStride=512,
            reusedAggregateTests=6,sourceTestReuseOnly=True,producer=False,consumer=False,pgo=False).items():assert policy[key]==expected,key
    assert policy['focused']==dict(selector='frontier_cohort::tests',expectedPassed=6,limitSeconds=300)
    for source,pins in [(code_paths()+[HERE/'plan.md',HERE/'policy.json',HERE/'source-review.md',HERE/'source.patch']+MEMOS,value['inputSha256']),
                        (reused_paths(),value['reusedEvidenceSha256'])]:
        for item in source:assert pins[str(item)]==sha(item),item
        for name,digest in pins.items():assert sha(name)==digest,name
    assert str(HERE/'README.md') not in value['inputSha256']
    return value
