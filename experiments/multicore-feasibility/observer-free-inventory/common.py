"""Narrow four-budget adapters of the frozen generic epoch experiment tools.

Imports start no process. Old helpers/source and preserved images stay unchanged.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import types

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EPOCH=HERE.parent/'epoch-colors'
PGO=HERE.parent/'epoch-own-pgo'
INVENTORY=HERE.parent/'epoch-inventory-four'
LEAD_REVIEW=Path('/home/legolas/agent-memos/imp2-lead-to-imp2-observer-free-inventory-discriminator-20261026.md')
LEGACY=HERE.parent/'colors-three'
NUMERICAL_CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01')
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/epoch-inventory-four-20261026-01')
DEFAULT_CRATE=Path('/home/legolas/rook2-experiments/workspaces/observer-free-inventory-20261026-01')
CONTROL_RAW=Path('/home/legolas/rook2-experiments/epoch-colors-20261026-01')
CONTROL_IMAGE=CONTROL_RAW/'rook2-candidate'
CONTROL_BUILD=CONTROL_RAW/'candidate-build'
CONTROL_SHA='7ac72fc63cf4086944b3abfd71f45eb1f0347796f2520bb97aa87fc8de3fb65c'
INVENTORY_RAW=Path('/home/legolas/rook2-experiments/epoch-inventory-four-20261026-01')
INVENTORY_IMAGE=INVENTORY_RAW/'rook2-candidate'
INVENTORY_BUILD=INVENTORY_RAW/'candidate-build'
INVENTORY_SHA='36c40aee75f8a93c773bc450f440ac14a2a94d8faa1057549805659ea4092e5f'
ACCOUNT=Path(__file__).resolve()
GATE=HERE/'placement_gate.mjs'
TAP=GATE
HELPERS={0,1,8,9,10,11,12,13}
CASES=['profile-35','profile-08','profile-43']
NAMES=['preserved3','preserved4','lean3','lean4']
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
LIMITS=dict(perLifeSeconds=180,totalSeconds=1800,supervisorPlacementSeconds=10,inputGateSeconds=12)


def module(name,path):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


epoch=module('observer_free_frozen_epoch_common',EPOCH/'common.py')
inventory=module('observer_free_frozen_inventory_common',INVENTORY/'common.py')
sha,read,write,snapshot=epoch.sha,epoch.read,epoch.write,epoch.snapshot
SPEC,housekeeping,stop_owned=epoch.SPEC,epoch.housekeeping,epoch.stop_owned
image_layout,dist=epoch.image_layout,epoch.dist


def changed(text,replacements):
    for before,after in replacements:
        assert text.count(before)==1,repr(before)
        text=text.replace(before,after)
    return text


def replace_function(value,path,name,replacements):
    source=Path(path).read_text()
    node=next(item for item in ast.parse(source).body if isinstance(item,ast.FunctionDef) and item.name==name)
    source=changed(ast.get_source_segment(source,node),replacements)
    exec(compile(source,str(path),'exec'),value.__dict__)


# All original raw parsing stays intact. Only the declared launcher switch and
# placement-gate import path differ from the frozen lifetime auditor.
audit=module('inventory_four_frozen_raw_auditor',epoch.ORIGINAL/'reconcile.py')
audit.ROOT,audit.ACCOUNT,audit.GATE=HERE,ACCOUNT,GATE
replace_function(audit,epoch.ORIGINAL/'reconcile.py','lifetime',[
    ("str(ACCOUNT), '--engine'","str(ACCOUNT), '--account', '--engine'"),
    ("str(ROOT/'tools/tap_wire.mjs')","str(GATE)")])


def baseline():
    value=inventory.baseline()
    value[str(INVENTORY_IMAGE)]=INVENTORY_SHA
    for folder in ['whole-full-epoch','whole-full-own-pgo']:
        closure=read(HERE.parent/folder/'closure.json')
        assert closure['complete']
        extra=dict(closure['protectedArtifacts'])
        extra.update({image['path']:image['sha256'] for image in closure['images'].values()})
        if 'profileSha256' in closure:
            extra[str(Path(closure['raw'])/'training/merged.profdata')]=closure['profileSha256']
        for path,digest in extra.items():
            assert path not in value or value[path]==digest
            value[path]=digest
    for path,digest in value.items(): assert sha(path)==digest,path
    return value


def code_paths():
    paths=[HERE/name for name in ['common.py','prepare.py','repair_prepare.py','collect.py','reconcile.py','placement_gate.mjs']]
    return sorted(set(paths+inventory.code_paths()))


def reused_evidence_paths():
    paths=inventory.reused_evidence_paths()+[INVENTORY/'preparation.json',INVENTORY/'closure.json',
        HERE.parent/'whole-full-epoch/closure.json',HERE.parent/'whole-full-own-pgo/closure.json',
        INVENTORY_RAW/'pipeline.json',INVENTORY_RAW/'prepared-run.json',
        INVENTORY_RAW/'pilot/reconciled.json',INVENTORY_BUILD/'receipt.json',INVENTORY_BUILD/'build.stderr']
    prior=read(INVENTORY_RAW/'pipeline.json')
    paths += [INVENTORY_RAW/(row['stage']+'.'+suffix) for row in prior['stages']
        if row['stage'].startswith('tests-') for suffix in ['stdout','stderr']]
    return sorted(set(paths))


def preparation(path):
    value=read(path)
    assert value['schema']=='rook2-observer-free-inventory-source-preparation-v1'
    assert Path(value['candidateCrate']).resolve()==DEFAULT_CRATE
    assert Path(value['controlCrate']).resolve()==CONTROL_CRATE
    assert value['numericalControlSource']==read(EPOCH/'preparation.json')['candidateSource']==snapshot(NUMERICAL_CONTROL_CRATE)
    assert value['controlSource']==read(INVENTORY/'preparation.json')['candidateSource']==snapshot(CONTROL_CRATE)
    assert value['candidateSource']==snapshot(DEFAULT_CRATE)
    before,after=value['controlSource'],value['candidateSource']
    assert len(before)==len(after)==65
    for name in ['Cargo.toml','Cargo.lock','src/activity.rs','src/shelter.rs','src/evaluator_worker.rs']:
        assert before[name]==after[name],name
    assert value['sourceChanges']==sorted(key for key in before.keys() & after.keys() if before[key]!=after[key])
    assert value['sourceAdded']==sorted(after.keys()-before.keys()) and value['sourceRemoved']==sorted(before.keys()-after.keys())
    assert not value['sourceAdded'] and not value['sourceRemoved']
    pins=value['reusedEvidenceSha256']
    assert all(str(path) in pins for path in reused_evidence_paths())
    for file,digest in pins.items(): assert sha(file)==digest,file
    prior=read(INVENTORY_RAW/'pipeline.json')
    assert prior['complete'] and prior['failure'] is None
    assert read(INVENTORY_RAW/'pilot/reconciled.json')['complete'] and read(INVENTORY/'closure.json')['complete']
    assert value['protectedArtifacts']==baseline()
    assert type(value['readinessSemantics']) is dict and value['readinessSemantics']
    assert all(key in value['evidenceReuse'] for key in ['affected','rerun','retained'])
    assert value['focused'] and len({row['name'] for row in value['focused']})==len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'],['--bin','rook2']]
        assert row['name'].replace('-','').replace('_','').isalnum() and row['selector']
        assert type(row['expectedPassed']) is int and row['expectedPassed']>0
        assert 0<row.get('limitSeconds',300)<=300
    required=code_paths()+[HERE/'plan.md',HERE/'policy.json',LEAD_REVIEW]
    for file in required: assert value['inputSha256'][str(file)]==sha(file),file
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    return value


def variants(candidate):
    return dict(preserved3=dict(path=str(CONTROL_IMAGE),budget=3,options=['--threads=3'],report=True),
        preserved4=dict(path=str(INVENTORY_IMAGE),budget=4,options=['--threads=4'],report=True),
        lean3=dict(path=str(candidate),budget=3,options=['--threads=3'],report=True),
        lean4=dict(path=str(candidate),budget=4,options=['--threads=4'],report=True))


def schedule():
    rows=[]
    for case in CASES:
        rows += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            rows += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(rows)==48
    return rows


def preexec_mask(budget):
    return {1:[6,14],2:[6,14],3:[4,6,14],4:[2,4,6,14]}[budget]


# The repaired idle helper imports common.check_task_masks lazily before input.
check_task_masks=inventory.check_task_masks


def supervisor(image,budget,directory,options):
    return [sys.executable,str(ACCOUNT),'--account','--engine',str(image),'--record',str(directory/'native.json'),
        '--known-single-process','--thread-budget',str(budget),*options]


def native_receipt(path,image,budget,options,hashes):
    native=read(path)
    assert native['schema']=='rook2-native-wait4-v1' and native['known_single_process']
    assert native['failure'] is None and native['native_exit_code']==native['native_wait_status']==0
    assert native['exec_error'] is None and native['supervisor_signals']==[]
    assert native['engine']==str(image) and native['engine_sha256_before']==native['engine_sha256_after']==sha(image)
    assert native['launcher_sha256']==hashes[str(ACCOUNT)]
    assert sha(native['python_executable'])==native['python_executable_sha256']
    assert native['argv']==[str(image),*options] and native['expected_threads']==budget
    assert native['inherited_supervisor_affinity']==native['supervisor_affinity']==sorted(HELPERS)
    assert native['native_pre_exec']==dict(pid=native['native_pid'],pgid=native['supervisor_pid'],affinity=preexec_mask(budget))
    observed=native['native_post_exec']
    assert observed['path']==str(image) and observed['pgid']==native['supervisor_pid'] and observed['affinity']==[14]
    assert sorted(observed['tasks'],key=int)==sorted(observed['task_affinities'],key=int)
    check_task_masks(observed['task_affinities'],native['native_pid'],budget)
    if budget>=3:
        helpers=sorted(int(tid) for tid in observed['tasks'] if tid!=str(native['native_pid']))
        assert [observed['task_names'][str(tid)] for tid in helpers]==['rook2-eval-whit','rook2-eval-blac','rook2-inventory'][:budget-1]
        assert [observed['task_affinities'][str(tid)] for tid in helpers]==[[6],[4],[2]][:budget-1]
    assert native['wall_ns']==native['reaped_monotonic_ns']-native['start_monotonic_ns']>0
    assert native['total_cpu_s']==native['user_cpu_s']+native['system_cpu_s']>0 and native['maxrss_linux_kib']>0
    assert native['colors_report_path']==str(path.parent/'colors.json')
    assert native['colors_report_sha256']==sha(path.parent/'colors.json')
    for pid in [native['native_pid'],native['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists(),'recorded PID live; inspect possible reuse'
    audit_placement(path.parent,native,hashes)
    return native


def audit_placement(directory,native,hashes):
    ready_path,gate_path=directory/'native.json.ready',directory/'native.json.input-gate.json'
    ready,gate=read(ready_path),read(gate_path)
    assert native['placement_error'] is None and native['ready_path']==str(ready_path)
    assert native['ready_sha256']==sha(ready_path)
    assert ready['schema']=='rook2-external-placement-ready-v1'
    for key in ['native_pid','supervisor_pid','expected_threads','native_pre_exec','native_post_exec']:
        assert ready[key]==native[key]
    assert ready['engine']==native['engine'] and ready['engine_sha256']==native['engine_sha256_before']
    assert ready['launcher_sha256']==native['launcher_sha256']==hashes[str(ACCOUNT)]
    before=ready['task_affinities_before_pinning']
    assert set(before)==set(native['native_post_exec']['task_affinities'])
    assert all(mask and set(mask)<=set(preexec_mask(native['expected_threads'])) for mask in before.values())
    check_task_masks(ready['native_post_exec']['task_affinities'],ready['native_pid'],ready['expected_threads'])
    assert gate['schema']=='rook2-placement-input-gate-v1'
    assert gate['ready_path']==str(ready_path) and gate['ready_sha256']==sha(ready_path)
    assert gate['native_pid']==native['native_pid'] and gate['supervisor_pid']==native['supervisor_pid']
    raw=(directory/('wire/stdin.raw' if gate['implementation']=='node-sync' else 'stdin.raw')).read_bytes()
    count=gate['first_write_bytes'];assert type(count) is int and 0<count<=len(raw)
    assert hashlib.sha256(raw[:count]).hexdigest()==gate['first_write_sha256']
    if gate['implementation']=='node-sync':
        assert gate['gate_sha256']==hashes[str(GATE)]
        case=read(directory/'launch.json')['step']['case']
        workload=next(row for row in read(SPEC/'workloads.json')['cases'] if row['id']==case)
        assert raw[:count]==('\n'.join([*workload['protocol']['recordsBeforeSearch'],'cm_parm rnd'])+'\n').encode()
    else:
        assert gate['implementation']=='python-idle' and gate['gate_sha256']==hashes[str(HERE/'collect.py')]
        assert raw[:count]==b'cm_parm\n'
    assert native['start_monotonic_ns']<=int(ready['ready_monotonic_ns'])<=int(gate['release_monotonic_ns'])<native['reaped_monotonic_ns']
    if (directory/'wire/receipt.json').exists():
        assert int(gate['release_monotonic_ns'])<=int(read(directory/'wire/receipt.json')['searches'][0]['startMonotonicNs'])
    return dict(readySha256=sha(ready_path),inputGateSha256=sha(gate_path))


audit.native_receipt=native_receipt


def account_main():
    """Old direct wait4 supervisor; only budget/mask/helper identity adapters."""
    value=module('inventory_four_account_template',LEGACY/'account_threads.py')
    value.HELPERS=set(HELPERS)
    value.__file__=str(ACCOUNT)
    replace_function(value,LEGACY/'account_threads.py','run',[
        ('choices=[1, 2, 3]','choices=[1, 2, 3, 4]'),
        ('native_mask = {4, 6, 14} if args.thread_budget == 3 else {6, 14}',
         'native_mask = {1:{6,14},2:{6,14},3:{4,6,14},4:{2,4,6,14}}[args.thread_budget]'),
        ('zip(helper_tasks, [6, 4])','zip(helper_tasks, [6, 4, 2])'),
        ('[6, 4][:len(helper_tasks)]','[6, 4, 2][:len(helper_tasks)]'),
        ("if args.thread_budget == 3:\n                assert [observed['task_names'][tid] for tid in helper_tasks] == ['rook2-eval-whit', 'rook2-eval-blac']",
         "if args.thread_budget >= 3:\n                assert [observed['task_names'][tid] for tid in helper_tasks] == ['rook2-eval-whit', 'rook2-eval-blac', 'rook2-inventory'][:args.thread_budget-1]"),
        ("helper_assignment='numeric TID order: first6, second4'","helper_assignment='numeric TID order: first6, second4, third2'")])
    return value.run()


def build_main():
    """Use unchanged generic build recipe; only its housekeeping mask changes."""
    original=ROOT/'tools/build.py';digest=sha(original)
    build=module('inventory_four_original_build',original)
    previous=sorted(build.HELPERS);build.HELPERS=set(HELPERS)
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    try: return build.main()
    finally:
        assert sha(original)==digest
        receipt=output/'receipt.json'
        if receipt.exists():
            value=read(receipt)
            value['affinity_adapter']=dict(path=str(ACCOUNT),sha256=sha(ACCOUNT),
                original_tool=str(original),original_tool_sha256=digest,only_override='HELPERS',
                original_helpers=previous,helpers=sorted(HELPERS))
            write(receipt,value)


def focused_main():
    """Baseline13 CLI controls plus explicit4/three-CPU cap; two08 fallbacks."""
    previous=sys.modules.get('common')
    try:
        sys.modules['common']=sys.modules[__name__]
        value=module('inventory_four_original_focused',LEGACY/'focused.py')
    finally:
        if previous is None: sys.modules.pop('common',None)
        else: sys.modules['common']=previous
    replace_function(value,LEGACY/'focused.py','affinity_replay',[
        ("options = ['--threads=3', *oracle_file['mode']]","options = ['--threads=4', *oracle_file['mode']]"),
        ('requestedThreads=3,','requestedThreads=4,')])
    replace_function(value,LEGACY/'focused.py','main',[
        ("(['--threads=8'], 8, 3, sorted(HELPERS)),","(['--threads=8'], 8, 4, sorted(HELPERS)),\n        (['--threads=4'], 4, 4, sorted(HELPERS)), (['--threads=4'], 4, 3, [4, 6, 14]),"),
        ("schema='rook2-colors-three-focused-cli-v1'","schema='rook2-observer-free-inventory-focused-cli-v1'")])
    return value.main()


def admit_build(directory,image,crate,expected,control=False):
    if control:
        return epoch.admit_build(directory,image,crate,expected)
    receipt=read(directory/'receipt.json')
    assert receipt['schema']=='rook2-development-build-v1'
    assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['cargo_exit_code']==0
    assert Path(receipt['crate']).resolve()==crate
    assert receipt['mode']=='generic' and receipt['target_cpu']=='x86-64' and receipt['target_triple']=='x86_64-unknown-linux-gnu'
    assert receipt['pgo']['mode']=='none' and receipt['rust_flags']==['-C','target-cpu=x86-64']
    assert receipt['binary_name']=='rook2' and sha(image)==receipt['binary_output']['sha256']==sha(receipt['binary_output']['path'])
    assert receipt['helper_sha256']==sha(ROOT/'tools/build.py')
    assert receipt['initial_affinity']==receipt['build_affinity']==receipt['restored_affinity']==sorted(HELPERS)
    assert receipt['affinity_adapter']==dict(path=str(ACCOUNT),sha256=sha(ACCOUNT),
        original_tool=str(ROOT/'tools/build.py'),original_tool_sha256=sha(ROOT/'tools/build.py'),only_override='HELPERS',
        original_helpers=[0,1,2,3,4,5,8,9,10,11,12,13],helpers=sorted(HELPERS))
    assert receipt['source_sha256_before']==receipt['source_sha256_after']==expected==snapshot(crate)
    for field in ['tool_sha256','cargo_config_sha256']:
        assert receipt[field+'_before']==receipt[field+'_after']
    assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged']
    for name,digest in (expected | receipt['tool_sha256_before']).items(): assert sha(directory/'source-before'/name)==digest
    for tool in ['rustc','cargo']: assert receipt['toolchain'][tool]['exit_code']==0
    assert 'release: 1.85.1\n' in receipt['toolchain']['rustc']['stdout'] and 'LLVM version: 19.1.7\n' in receipt['toolchain']['rustc']['stdout']
    return receipt,epoch.effective_options(directory)


def admit_controls(prepared):
    old3,options3=epoch.admit_build(CONTROL_BUILD,CONTROL_IMAGE,NUMERICAL_CONTROL_CRATE,prepared['numericalControlSource'])
    old4,options4=inventory.admit_build(INVENTORY_BUILD,INVENTORY_IMAGE,CONTROL_CRATE,prepared['controlSource'])
    assert sha(CONTROL_IMAGE)==CONTROL_SHA and sha(INVENTORY_IMAGE)==INVENTORY_SHA
    assert options3==options4
    for tool in ['rustc','cargo']:
        assert old3['toolchain'][tool]==old4['toolchain'][tool]
        assert old3['toolchain'][tool+'_executable_sha256']==old4['toolchain'][tool+'_executable_sha256']
    return old3,old4


def admission(candidate_build,candidate,prepared):
    old3,old4=admit_controls(prepared)
    new,new_options=admit_build(candidate_build,candidate,DEFAULT_CRATE,prepared['candidateSource'])
    assert epoch.effective_options(CONTROL_BUILD)==new_options
    for tool in ['rustc','cargo']:
        assert old3['toolchain'][tool]==new['toolchain'][tool]
        assert old3['toolchain'][tool+'_executable_sha256']==new['toolchain'][tool+'_executable_sha256']
    return old3,old4,new


def colors_report(path,budget,idle=False,preserved=False,disabled=False):
    if disabled:
        value=read(path)
        assert value==dict(enabled=False)
        return value
    return inventory.colors_report(path,budget,idle,preserved)


def reused_worker_record(original,frozen,prepared):
    """Read-only binding of completed worker29 and the preserved owner-test failure."""
    original,frozen=Path(original),Path(frozen)
    failed=read(original/'pipeline.json')
    old=read(frozen/'preparation.json');saved=read(frozen/'snapshot.json')
    assert failed==read(frozen/'pipeline.json') and old==failed['sourcePreparation']
    assert sha(frozen/'preparation.json')==failed['preparationSha256']
    assert not failed['complete'] and not failed['prepared'] and not failed['collected']
    assert failed['failure']=="AssertionError(('tests-01-ordinary-inventory-owners', 101))"
    assert not (original/'pilot').exists(), 'no completed benchmark lives may be replayed'
    assert len(failed['stages'])==2 and [row['exit'] for row in failed['stages']]==[0,101]
    assert sha(original/'housekeeping-prepare.json')==sha(frozen/'housekeeping-prepare.json')
    worker=failed['stages'][0]
    assert worker['stage']=='tests-00-lean-worker-ownership' and len(worker['passedTests'])==29
    assert old['focused']==prepared['focused'] and prepared['focused'][0]['expectedPassed']==29
    before,after=old['candidateSource'],prepared['candidateSource']
    assert set(before)==set(after) and len(before)==65
    changed=[name for name in before if before[name]!=after[name]]
    assert changed==['src/evaluator/inventory_four_tests.rs'], changed
    assert saved['source']==before==snapshot(frozen/'source-before')
    assert saved['stages']==failed['stages'] and saved['failure']==failed['failure']
    assert saved['pipelineStartMonotonicNs']==failed['pipelineStartMonotonicNs']
    assert saved['pipelineDeadlineMonotonicNs']==failed['pipelineDeadlineMonotonicNs']==failed['pipelineStartMonotonicNs']+3600*10**9
    assert set(saved['inputs'])==set(old['inputSha256'])
    paths=[original/'pipeline.json',original/'housekeeping-prepare.json',frozen/'snapshot.json',frozen/'preparation.json',
        frozen/'pipeline.json',frozen/'housekeeping-prepare.json']
    for path,entry in saved['inputs'].items():
        assert entry['sha256']==old['inputSha256'][path]==sha(entry['snapshot'])
        paths.append(Path(entry['snapshot']))
    paths += [frozen/'source-before'/name for name in before]
    for row in failed['stages']:
        for suffix in ['stdout','stderr']:
            path=original/(row['stage']+'.'+suffix)
            assert sha(path)==row[suffix+'Sha256']
            paths.append(path)
    return dict(original=str(original),snapshot=str(frozen),workerStage=worker,
        sourceChanges=changed,successfulReusedControls=29,repeatedWorkerControls=0,
        completedBenchmarkLives=0,pipelineStartMonotonicNs=failed['pipelineStartMonotonicNs'],
        pipelineDeadlineMonotonicNs=failed['pipelineDeadlineMonotonicNs'],
        inputSha256={str(path):sha(path) for path in sorted(set(paths))},
        explanation='Original worker29 accepted once before a test-assumption failure; only owner test changed; original failed records and source/input copies retained; no native timing life repeated or clock reset')


def prepared_run(path,prepared_path,prepared):
    value=read(path);directory=path.parent
    assert value['schema']=='rook2-observer-free-inventory-prepared-run-v1' and value['complete']
    assert value['sourcePreparation']==str(prepared_path) and value['sourcePreparationSha256']==sha(prepared_path)
    assert value['source']==prepared['candidateSource']
    assert value['candidate']==image_layout(directory/'rook2-candidate') and value['control']==image_layout(CONTROL_IMAGE)
    assert value['inventoryControl']==image_layout(INVENTORY_IMAGE)
    assert value['pipelineDeadlineMonotonicNs']==value['pipelineStartMonotonicNs']+3600*10**9
    assert value['pipelineStartMonotonicNs']<=value['preparedMonotonicNs']<value['pipelineDeadlineMonotonicNs']
    assert value['evidenceReuse']==prepared['evidenceReuse']
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    stages=value['stages']
    reused=value.get('reusedWorkerRecord')
    if reused is not None:
        assert reused==reused_worker_record(reused['original'],reused['snapshot'],prepared)
        assert stages[0]==reused['workerStage']
        assert value['pipelineStartMonotonicNs']==reused['pipelineStartMonotonicNs']
        assert value['pipelineDeadlineMonotonicNs']==reused['pipelineDeadlineMonotonicNs']
        assert all(value['inputSha256'][path]==digest for path,digest in reused['inputSha256'].items())
    assert [row['stage'] for row in stages]==[f'tests-{i:02d}-{row["name"]}' for i,row in enumerate(prepared['focused'])]+['candidate-build','cli-affinity']
    for index,row in enumerate(stages):
        stage_directory=Path(reused['original']) if reused is not None and index==0 else directory
        assert row['exit']==0
        for suffix in ['stdout','stderr']:
            file=stage_directory/(row['stage']+'.'+suffix)
            assert value['inputSha256'][str(file)]==sha(file)==row[suffix+'Sha256']
    for index,(row,tests) in enumerate(zip(stages,prepared['focused'])):
        stage_directory=Path(reused['original']) if reused is not None and index==0 else directory
        text=(stage_directory/(row['stage']+'.stdout')).read_text()
        passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
        summaries=re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)
        assert passed==row['passedTests'] and len(passed)==len(set(passed))==tests['expectedPassed']
        assert summaries==[(str(len(passed)),'0','0')]
        argv=['/usr/bin/cargo','test','--offline','--locked',*tests['target'],'--target','x86_64-unknown-linux-gnu',
            '--jobs','4','--target-dir',str(stage_directory/'test-target'),tests['selector'],'--','--test-threads=1']
        if tests.get('exact',False): argv.append('--exact')
        if tests.get('ignored',False): argv.append('--ignored')
        assert row['argv']==argv and row['cwd']==str(DEFAULT_CRATE)
    assert stages[-2]['argv']==['/usr/bin/python3',str(ACCOUNT),'--build-adapter','--crate',str(DEFAULT_CRATE),
        '--mode','generic','--bin','rook2','--jobs','4','--output',str(directory/'candidate-build')]
    assert stages[-1]['argv']==['/usr/bin/python3',str(ACCOUNT),'--focused','--engine',str(directory/'rook2-candidate'),
        '--output',str(directory/'focused')]
    admission(directory/'candidate-build',directory/'rook2-candidate',prepared)
    cli=read(directory/'focused/result.json')
    assert cli['schema']=='rook2-observer-free-inventory-focused-cli-v1' and cli['complete']
    assert cli['engine']==str(directory/'rook2-candidate') and cli['engineSha256']==sha(cli['engine'])
    assert len(cli['cli'])==15 and len(cli['affinityReplays'])==2
    positive=[([],1,1,sorted(HELPERS)),(['--threads=1'],1,1,sorted(HELPERS)),
        (['--threads=2'],2,2,sorted(HELPERS)),(['--threads=3'],3,3,sorted(HELPERS)),
        (['--threads=8'],8,4,sorted(HELPERS)),(['--threads=4'],4,4,sorted(HELPERS)),
        (['--threads=4'],4,3,[4,6,14]),(['--threads=3'],3,1,[14]),
        (['--threads=3'],3,2,[6,14]),(['--threads=8'],8,2,[6,14])]
    for row,(options,requested,configured,mask) in zip(cli['cli'],positive):
        assert row['argv']==[cli['engine'],*options,'--inspect-threads'] and row['inheritedMask']==mask
        assert row['exit']==0 and row['stderr']==''
        assert json.loads(row['stdout'])==dict(requested_threads=requested,configured_threads=configured)
    for row,arg in zip(cli['cli'][10:],['0','-1','','oops','184467440737095516160']):
        assert row['argv']==[cli['engine'],'--threads='+arg,'--inspect-threads']
        assert row['exit']!=0 and row['stdout']=='' and row['stderr']
    workload=next(row for row in read(SPEC/'workloads.json')['cases'] if row['id']=='profile-08')
    oracle=next(row for row in read(SPEC/'replay-oracle.json')['cases'] if row['id']=='profile-08')
    for row,name,mask,configured in zip(cli['affinityReplays'],['one-cpu','two-cpu'],[[14],[6,14]],[1,2]):
        rawdir=directory/'focused'/name
        assert row['requestedThreads']==4 and row['configuredThreads']==configured and row['inheritedMask']==mask
        assert len(row['taskAffinities'])==configured and all(item==mask for item in row['taskAffinities'].values())
        for file,digest in row['sha256'].items(): assert sha(rawdir/file)==digest
        incoming=(rawdir/'stdin.raw').read_bytes();outgoing=(rawdir/'stdout.raw').read_bytes()
        assert incoming.startswith(b'cm_parm\n') and incoming.endswith(b'quit\n') and outgoing.startswith(b'cm_parm\n')
        assert (rawdir/'stderr.raw').read_bytes()==b''
        raw=dict(stdin=incoming[8:-5],stdout=outgoing[8:],stderr=b'')
        actual=dict(stdout=raw['stdout'].decode(),stderr='',exit=dict(code=0,signal=None))
        assert audit.original_streams(actual,workload,oracle,raw)==row['orderedPosts']
    return value


readiness_summary=inventory.readiness_summary


def readiness(directory,row,budget,preserved=False,idle=False,disabled=False):
    if disabled:
        path=directory/'colors.json'
        assert row==dict(path=str(path),sha256=sha(path),report=dict(enabled=False))
        assert read(path)==dict(enabled=False)
        return row['report']
    return inventory.readiness(directory,row,budget,preserved,idle)


def housekeeping_audit(path):
    record=read(path)
    assert record['schema']=='rook2-observer-free-inventory-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus']==sorted(HELPERS)
    assert len(record['applies'])==52 and record['restored'] is not None
    originals,leaders,observed={},{},{}
    for row in record['originals']:
        key=(row['pid'],row['tid'],row['starttime']);assert key not in originals and row['affinity']
        originals[key]=row['affinity']
    for row in record['leaders']:
        key=(row['pid'],row['starttime']);assert key not in leaders and row['affinity']
        leaders[key]=row['affinity']
    for event in record['applies']:
        assert event['cpus']==event['selfAffinity']==sorted(HELPERS)
        for row in event['selectedTasks']:
            key=(row['pid'],row['tid'],row['starttime']);assert row['after']==sorted(HELPERS)
            if key in observed: assert row['before']==sorted(HELPERS)
            else: assert row['before']==originals[key];observed[key]=row['before']
    assert observed==originals
    for row in record['restored']:
        key=(row['pid'],row['tid'],row['starttime'])
        if key in originals: assert not row['inheritedNewThread'] and row['restored']==originals[key]
        else:
            masks=[mask for (pid,_),mask in leaders.items() if pid==row['pid']]
            assert len(masks)==1 and row['inheritedNewThread'] and row['restored']==masks[0]
    assert record['postRestoreSelfAffinity']==sorted(HELPERS)
    return dict(applyCount=52,selectedOriginalTasks=len(originals),restoredTasks=len(record['restored']),receiptSha256=sha(path))

if __name__=='__main__':
    mode=sys.argv.pop(1)
    if mode=='--account': raise SystemExit(account_main())
    if mode=='--build-adapter': raise SystemExit(build_main())
    if mode=='--focused': raise SystemExit(focused_main())
    raise ValueError('unknown narrow adapter '+mode)
