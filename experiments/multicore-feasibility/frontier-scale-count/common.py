"""Fixed one-search adapters of the existing epoch replay/accounting tools.

Imports define functions only. Counts rely on frozen source and six controls;
the saved raw replay independently qualifies wire/work/placement and boundaries.
"""
import ast
import importlib.util
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EPOCH=HERE.parent/'epoch-colors'
CRATE=Path('/home/legolas/rook2-experiments/workspaces/frontier-scale-count-20261029-01')
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01')
CHANGED=['src/bin/rook2.rs','src/evaluator.rs','src/lib.rs','src/ordinary.rs','src/quiescence.rs','src/timed.rs']
OPTIONS=['--threads=3','--owner-local-inventory','--q-owner-local-inventory']
STEP=dict(case='profile-35',variant='frontier-scale',warmup=False,repeat=1)
PIPELINE_SECONDS=900;LIFE_SECONDS=180
REPORT='frontier-scale.json';REPORT_ENV='ROOK2_FRONTIER_SCALE_REPORT'
TESTS=sorted('frontier_scale::tests::'+name for name in [
    'actual_skip_domain_excludes_nonordinary_extended_untrusted_and_king_victim',
    'activation_cookie_counts_once_and_separate_activations_remain_distinct',
    'only_selected_iteration_and_coherent_map_full_domains_count',
    'boundaries_are_single_pairs_and_incomplete_or_duplicate_is_explicit',
    'counter_overflow_is_sticky_and_does_not_wrap_or_partially_admit',
    'cold_json_preserves_counts_pair_stop_and_bounded_storage'])


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


epoch=module('frontier_scale_frozen_epoch',EPOCH/'common.py')
sha,read,write,snapshot=epoch.sha,epoch.read,epoch.write,epoch.snapshot
HELPERS,ACCOUNT,GATE,TAP,SPEC=epoch.HELPERS,epoch.ACCOUNT,epoch.GATE,epoch.TAP,epoch.SPEC
BUILD_ADAPTER=epoch.BUILD_ADAPTER
housekeeping,audit,audit_placement=epoch.housekeeping,epoch.audit,epoch.audit_placement
image_layout,admit_build,check_task_masks=epoch.image_layout,epoch.admit_build,epoch.check_task_masks
previous=sys.modules.get('common')
try:
    sys.modules['common']=epoch;collector=module('frontier_scale_frozen_collector',EPOCH/'collect.py')
finally:
    if previous is None:sys.modules.pop('common',None)
    else:sys.modules['common']=previous
original_environment=collector.environment


def environment(directory,report):
    env=original_environment(directory,report)
    env[REPORT_ENV]=str(directory/REPORT)
    write(directory/'frontier-env.json',dict(schema='rook2-frontier-scale-environment-v1',variable=REPORT_ENV,path=env[REPORT_ENV]))
    return env


collector.environment=environment
# Reuse the original lifetime body, adding only the already-waited Node PID/exit
# to its cold row. Native wait4, wire, raw caps and placement remain unchanged.
source=(EPOCH/'collect.py').read_text()
node=next(item for item in ast.parse(source).body if isinstance(item,ast.FunctionDef) and item.name=='run_lifetime')
body=ast.get_source_segment(source,node)
needle="row = dict(**step, directory=str(directory), nativePid=receipt['native_pid'],"
assert body.count(needle)==1
exec(compile(body.replace(needle,needle+" replayRunnerPid=child.pid,replayRunnerExit=child.returncode,"),str(EPOCH/'collect.py'),'exec'),collector.__dict__)
run_lifetime=collector.run_lifetime


def prior_evidence():
    path=HERE.parent/'pre-map-geometry/closure.json';concise=read(path)
    assert concise['schema']=='rook2-pre-map-geometry-concise-closure-v1' and concise['complete']
    row=concise['fullTerminalAudit'];assert sha(row['path'])==row['sha256']
    full=read(row['path']);assert full['complete'] and len(full['protectedArtifacts'])==41
    return path,concise,full


def baseline():
    _,_,full=prior_evidence();result=dict(full['protectedArtifacts'])
    image=full['images']['staged3'];assert image['sha256']=='e2fbdad54643e9577e8475fa12e7a7b153d7aaf4e460042c2b1923c6ffb9fdaa'
    result[image['path']]=image['sha256'];assert len(result)==42
    for path,digest in result.items():assert sha(path)==digest,path
    return result


def code_paths():
    return sorted(set([HERE/name for name in ['common.py','pipeline.py','reconcile.py','freeze_source.py']]+epoch.code_paths()))


def reused_paths():
    path,concise,_=prior_evidence()
    generic=HERE.parent/'single-owner-activation'
    return [path,Path(concise['fullTerminalAudit']['path']),generic/'preparation.json',generic/'closure.json',
        Path('/home/legolas/rook2-experiments/single-owner-20261028-01/prepared-run.json')]


def source_admission():
    before,after=snapshot(CONTROL_CRATE),snapshot(CRATE)
    assert before==read(HERE.parent/'single-owner-activation/preparation.json')['candidateSource']
    assert len(before)==69 and len(after)==70
    assert sorted(name for name in before if before[name]!=after[name])==CHANGED
    assert sorted(after.keys()-before.keys())==['src/frontier_scale.rs'] and not before.keys()-after.keys()
    module_text=(CRATE/'src/frontier_scale.rs').read_text()
    tests=sorted('frontier_scale::tests::'+name for name in re.findall(r'#\[test\]\s*fn\s+(\w+)\s*\(',module_text))
    assert tests==TESTS
    assert REPORT_ENV in (CRATE/'src/bin/rook2.rs').read_text()
    assert 'rook2-frontier-scale-v1' in module_text
    return before,after


def preparation(path):
    value=read(path);before,after=source_admission()
    assert value['schema']=='rook2-frontier-scale-count-preparation-v1'
    assert value['controlSource']==before and value['candidateSource']==after
    assert value['sourceChanges']==CHANGED and value['sourceAdded']==['src/frontier_scale.rs']
    assert value['sourceRemoved']==[] and value['candidateCrate']==str(CRATE)
    assert value['focused']==dict(target=['--lib'],selector='frontier_scale::tests',expectedTests=TESTS,expectedPassed=6)
    assert value['protectedArtifacts']==baseline()
    assert value['options']==OPTIONS and value['case']=='profile-35'
    assert value['pipelineSeconds']==900 and value['perLifeSeconds']==180
    policy=read(HERE/'policy.json')
    assert policy['schema']=='rook2-frontier-scale-count-policy-v1'
    for key,expected in dict(sourceFiles=70,sourceChanged=CHANGED,sourceAdded=['src/frontier_scale.rs'],
            case='profile-35',iterations=[6,7],counts=['E6','S6','M7','F7'],mode=3,bothHooksRequested=True,
            replayLives=1,orderedPosts=13,pipelineSeconds=900,perLifeSeconds=180,ownerCpu=14,
            helperCpus=[6,4],housekeepingCpus=sorted(HELPERS),unusedOwnedSiblings=[15,7,5]).items():assert policy[key]==expected,key
    assert policy['focused']==dict(selector='frontier_scale::tests',expectedPassed=6,limitSeconds=300)
    required=code_paths()+[HERE/'plan.md',HERE/'policy.json',HERE/'source-review.md',Path('/home/legolas/agent-memos/imp2-lead-to-imp2-frontier-scale-count-20261029.md')]
    for path in required:assert value['inputSha256'][str(path)]==sha(path),path
    for name,digest in value['inputSha256'].items():assert sha(name)==digest,name
    for path in reused_paths():assert value['reusedEvidenceSha256'][str(path)]==sha(path),path
    for name,digest in value['reusedEvidenceSha256'].items():assert sha(name)==digest,name
    return value
