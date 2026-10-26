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
LEGACY=HERE.parent/'colors-three'
CONTROL_CRATE=Path('/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01')
DEFAULT_CRATE=Path('/home/legolas/rook2-experiments/workspaces/epoch-inventory-four-20261026-01')
CONTROL_RAW=Path('/home/legolas/rook2-experiments/epoch-colors-20261026-01')
CONTROL_IMAGE=CONTROL_RAW/'rook2-candidate'
CONTROL_BUILD=CONTROL_RAW/'candidate-build'
CONTROL_SHA='7ac72fc63cf4086944b3abfd71f45eb1f0347796f2520bb97aa87fc8de3fb65c'
ACCOUNT=Path(__file__).resolve()
GATE=HERE/'placement_gate.mjs'
TAP=GATE
HELPERS={0,1,8,9,10,11,12,13}
CASES=['profile-35','profile-08','profile-43']
NAMES=['preserved3','inline1','current2','epoch3','inventory4']
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
LIMITS=dict(perLifeSeconds=180,totalSeconds=1800,supervisorPlacementSeconds=10,inputGateSeconds=12)


def module(name,path):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


epoch=module('inventory_four_frozen_epoch_common',EPOCH/'common.py')
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
    value=epoch.baseline()
    value[str(CONTROL_IMAGE)]=CONTROL_SHA
    value[str(epoch.CONTROL_IMAGE)]=epoch.CONTROL_SHA256
    value['/home/legolas/rook2-experiments/epoch-own-pgo-20261026-01/rook2-pgo']='67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7'
    value['/home/legolas/rook2-experiments/epoch-own-pgo-20261026-01/training/merged.profdata']='9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311'
    for path,digest in read(PGO/'closure.json')['protectedArtifacts'].items():
        assert path not in value or value[path]==digest
        value[path]=digest
    for path,digest in value.items(): assert sha(path)==digest,path
    return value


def code_paths():
    paths=[HERE/name for name in ['common.py','prepare.py','collect.py','reconcile.py','placement_gate.mjs']]
    return sorted(set(paths+epoch.code_paths()))


def reused_evidence_paths():
    paths=[EPOCH/'preparation.json',EPOCH/'closure.json',PGO/'closure.json',
        CONTROL_RAW/'pipeline.json',CONTROL_RAW/'prepared-run.json',CONTROL_RAW/'pilot/reconciled.json',
        CONTROL_BUILD/'receipt.json',CONTROL_BUILD/'build.stderr']
    prior=read(CONTROL_RAW/'pipeline.json')
    paths += [CONTROL_RAW/(row['stage']+'.'+suffix) for row in prior['stages']
        if row['stage'].startswith('tests-') for suffix in ['stdout','stderr']]
    return paths


def preparation(path):
    value=read(path)
    assert value['schema']=='rook2-epoch-inventory-four-source-preparation-v1'
    assert Path(value['candidateCrate']).resolve()==DEFAULT_CRATE
    assert Path(value['controlCrate']).resolve()==CONTROL_CRATE
    assert value['controlSource']==read(EPOCH/'preparation.json')['candidateSource']==snapshot(CONTROL_CRATE)
    assert value['candidateSource']==snapshot(DEFAULT_CRATE)
    before,after=value['controlSource'],value['candidateSource']
    for name in ['Cargo.toml','Cargo.lock','src/activity.rs','src/shelter.rs','src/evaluator_worker.rs']:
        assert before[name]==after[name],name
    assert value['sourceChanges']==sorted(key for key in before.keys() & after.keys() if before[key]!=after[key])
    assert value['sourceAdded']==sorted(after.keys()-before.keys()) and value['sourceRemoved']==sorted(before.keys()-after.keys())
    pins=value['reusedEvidenceSha256']
    assert all(str(path) in pins for path in reused_evidence_paths())
    for file,digest in pins.items(): assert sha(file)==digest,file
    prior=read(CONTROL_RAW/'pipeline.json')
    assert prior['complete'] and prior['failure'] is None
    assert sum(len(row.get('passedTests',[])) for row in prior['stages'])==32
    assert read(CONTROL_RAW/'pilot/reconciled.json')['complete']
    assert value['protectedArtifacts']==baseline()
    assert type(value['readinessSemantics']) is dict and value['readinessSemantics']
    assert value['evidenceReuse']['genericBaselinePassed']==32
    assert all(key in value['evidenceReuse'] for key in ['affected','rerun','retained'])
    assert value['focused'] and len({row['name'] for row in value['focused']})==len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'],['--bin','rook2']]
        assert row['name'].replace('-','').replace('_','').isalnum() and row['selector']
        assert type(row['expectedPassed']) is int and row['expectedPassed']>0
        assert 0<row.get('limitSeconds',300)<=300
    required=code_paths()+[HERE/'plan.md',HERE/'policy.json',
        Path('/home/legolas/agent-memos/imp2-lead-to-imp2-epoch-inventory-four-discriminator-20261026.md')]
    for file in required: assert value['inputSha256'][str(file)]==sha(file),file
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    return value


def variants(candidate):
    return dict(preserved3=dict(path=str(CONTROL_IMAGE),budget=3,options=['--threads=3'],report=True),
        inline1=dict(path=str(candidate),budget=1,options=['--threads=1'],report=True),
        current2=dict(path=str(candidate),budget=2,options=['--threads=2'],report=True),
        epoch3=dict(path=str(candidate),budget=3,options=['--threads=3'],report=True),
        inventory4=dict(path=str(candidate),budget=4,options=['--threads=4'],report=True))


def schedule():
    rows=[]
    for case in CASES:
        rows += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            rows += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(rows)==60
    return rows


def preexec_mask(budget):
    return {1:[6,14],2:[6,14],3:[4,6,14],4:[2,4,6,14]}[budget]


def check_task_masks(masks,pid,budget):
    assert len(masks)==budget and masks[str(pid)]==[14]
    helpers=sorted(mask for tid,mask in masks.items() if tid!=str(pid))
    assert helpers=={1:[],2:[[6]],3:[[4],[6]],4:[[2],[4],[6]]}[budget]


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
        ("schema='rook2-colors-three-focused-cli-v1'","schema='rook2-epoch-inventory-four-focused-cli-v1'")])
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


def admission(candidate_build,candidate,prepared):
    old,old_options=admit_build(CONTROL_BUILD,CONTROL_IMAGE,CONTROL_CRATE,prepared['controlSource'],control=True)
    new,new_options=admit_build(candidate_build,candidate,DEFAULT_CRATE,prepared['candidateSource'])
    assert old_options==new_options
    for tool in ['rustc','cargo']:
        assert old['toolchain'][tool]==new['toolchain'][tool]
        assert old['toolchain'][tool+'_executable_sha256']==new['toolchain'][tool+'_executable_sha256']
    return old,new


# Preserve the exact original colors histogram validation while removing only
# the new sibling inventory subobject from its local view.
_colors=types.ModuleType('inventory_four_colors_validator')
_colors.__dict__.update(epoch.__dict__)
replace_function(_colors,EPOCH/'common.py','colors_report',[
    ('value = read(path)',"value = dict(read(path)); value.pop('inventory', None)"),
    ('if budget != 3:','if budget < 3:')])


def metric_audit(value,count):
    assert set(value)=={'count','sum_ns','min_ns','max_ns','log2_ns'}
    assert value['count']==count
    assert all(type(value[key]) is int and value[key]>=0 for key in ['count','sum_ns','min_ns','max_ns'])
    bins=value['log2_ns'];assert len(bins)==64 and all(type(item) is int and item>=0 for item in bins)
    assert sum(bins)==count
    if not count:
        assert value['sum_ns']==value['min_ns']==value['max_ns']==0
        return
    minimum,maximum=value['min_ns'],value['max_ns']
    assert 0<=minimum<=maximum<2**64 and count*minimum<=value['sum_ns']<=count*maximum
    occupied=[index for index,item in enumerate(bins) if item]
    assert min(minimum.bit_length(),63)==occupied[0] and min(maximum.bit_length(),63)==occupied[-1]
    low=sum(n*(0 if i==0 else 2**(i-1)) for i,n in enumerate(bins))
    high=sum(n*(0 if i==0 else (2**i-1 if i<63 else 2**64-1)) for i,n in enumerate(bins))
    assert low<=value['sum_ns']<=high


def inventory_report(value,color_dispatches,idle=False):
    """Concrete sparse inventory partitions; field list freezes with source."""
    assert value['schema']=='rook2-conditional-inventory-v1' and value['enabled'] is True
    assert value['sample_stride']==512 and value['sampling']=='color_epoch_mod_512'
    fields=['requested','nonparticipants','completed','generated','domainUnavailable','generatedMoves',
        'settled','installed','settledUnavailable','demanded','discarded','unsettledDiscarded','failed','pendingReceipts','demandedMoves',
        'interposedDemanded','interposedDiscarded',
        'sampledRequested','sampledCompleted','sampledSettled','sampledInstalled','sampledUnavailable','sampledDemanded',
        'sampledDiscarded','sampledUnsettledDiscarded','sampledFailed','sampledPendingReceipts']
    assert all(type(value[key]) is int and 0<=value[key]<2**64 for key in fields)
    assert value['nonparticipants']==color_dispatches-value['requested']>=0
    assert value['sampledRequested']<=color_dispatches//512
    for sampled,total in [('sampledRequested','requested'),('sampledCompleted','completed'),
        ('sampledSettled','settled'),('sampledInstalled','installed'),('sampledUnavailable','settledUnavailable'),
        ('sampledDemanded','demanded'),('sampledDiscarded','discarded'),
        ('sampledUnsettledDiscarded','unsettledDiscarded'),('sampledFailed','failed'),('sampledPendingReceipts','pendingReceipts')]:
        assert value[sampled]<=value[total]
    assert value['demandedMoves']<=value['generatedMoves']
    assert value['requested']==value['settled']+value['unsettledDiscarded']+value['failed']
    assert value['completed']==value['generated']+value['domainUnavailable']<=value['requested']
    assert value['settled']==value['installed']+value['settledUnavailable']<=value['completed']
    assert value['installed']==value['demanded']+value['discarded']+value['pendingReceipts']
    assert value['sampledRequested']==value['sampledSettled']+value['sampledUnsettledDiscarded']+value['sampledFailed']
    assert value['sampledSettled']==value['sampledInstalled']+value['sampledUnavailable']<=value['sampledCompleted']<=value['sampledRequested']
    assert value['sampledInstalled']==value['sampledDemanded']+value['sampledDiscarded']+value['sampledPendingReceipts']
    populations=dict(ready='sampledSettled',generation='sampledSettled',numerical_full_complete='sampledSettled',
        acquire='sampledSettled',acquire_wait='sampledSettled',ready_after_full='sampledSettled',full_after_ready='sampledSettled',
        install='sampledInstalled',install_duration='sampledInstalled',demand='sampledDemanded',demand_after_install='sampledDemanded',
        discard='sampledDiscarded',discard_after_install='sampledDiscarded')
    assert set(value['metrics'])==set(populations)
    for name,field in populations.items(): metric_audit(value['metrics'][name],value[field])
    assert 0<=value['interposedDemanded']<=value['demanded'] and 0<=value['interposedDiscarded']<=value['discarded']
    assert value['failed']==value['pendingReceipts']==value['sampledPendingReceipts']==0
    if idle: assert value['requested']==0
    return value


def colors_report(path,budget,idle=False,preserved=False):
    value=read(path)
    _colors.colors_report(path,budget,idle)
    if preserved:
        assert 'inventory' not in value
    elif budget<4:
        assert value['inventory']==dict(enabled=False)
    else:
        inventory_report(value['inventory'],value['dispatches'],idle)
    return value




def prepared_run(path,prepared_path,prepared):
    value=read(path);directory=path.parent
    assert value['schema']=='rook2-epoch-inventory-four-prepared-run-v1' and value['complete']
    assert value['sourcePreparation']==str(prepared_path) and value['sourcePreparationSha256']==sha(prepared_path)
    assert value['source']==prepared['candidateSource']
    assert value['candidate']==image_layout(directory/'rook2-candidate') and value['control']==image_layout(CONTROL_IMAGE)
    assert value['pipelineDeadlineMonotonicNs']==value['pipelineStartMonotonicNs']+3600*10**9
    assert value['pipelineStartMonotonicNs']<=value['preparedMonotonicNs']<value['pipelineDeadlineMonotonicNs']
    assert value['evidenceReuse']==prepared['evidenceReuse']
    for file,digest in value['inputSha256'].items(): assert sha(file)==digest,file
    stages=value['stages']
    assert [row['stage'] for row in stages]==[f'tests-{i:02d}-{row["name"]}' for i,row in enumerate(prepared['focused'])]+['candidate-build','cli-affinity']
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
    assert stages[-2]['argv']==['/usr/bin/python3',str(ACCOUNT),'--build-adapter','--crate',str(DEFAULT_CRATE),
        '--mode','generic','--bin','rook2','--jobs','4','--output',str(directory/'candidate-build')]
    assert stages[-1]['argv']==['/usr/bin/python3',str(ACCOUNT),'--focused','--engine',str(directory/'rook2-candidate'),
        '--output',str(directory/'focused')]
    admission(directory/'candidate-build',directory/'rook2-candidate',prepared)
    cli=read(directory/'focused/result.json')
    assert cli['schema']=='rook2-epoch-inventory-four-focused-cli-v1' and cli['complete']
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


_previous_common=sys.modules.get('common')
try:
    sys.modules['common']=epoch
    _observer=module('inventory_four_independent_colors_observer',EPOCH/'reconcile.py')
finally:
    if _previous_common is None: sys.modules.pop('common',None)
    else: sys.modules['common']=_previous_common
replace_function(_observer,EPOCH/'reconcile.py','readiness',[
    ('value = read(path)',"value = dict(read(path)); value.pop('inventory', None)"),
    ("assert value == row['report'] and", "assert value == {key:item for key,item in row['report'].items() if key!='inventory'} and")])


readiness_summary=_observer.readiness_summary


def readiness(directory,row,budget,preserved=False,idle=False):
    value=_observer.readiness(directory,row,budget,True,idle)
    full=read(directory/'colors.json')
    if preserved: assert 'inventory' not in full
    elif budget<4: assert full['inventory']==dict(enabled=False)
    else: inventory_report(full['inventory'],value['dispatches'],idle)
    return full


def housekeeping_audit(path):
    record=read(path)
    assert record['schema']=='rook2-epoch-inventory-four-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus']==sorted(HELPERS)
    assert len(record['applies'])==65 and record['restored'] is not None
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
    return dict(applyCount=65,selectedOriginalTasks=len(originals),restoredTasks=len(record['restored']),receiptSha256=sha(path))

if __name__=='__main__':
    mode=sys.argv.pop(1)
    if mode=='--account': raise SystemExit(account_main())
    if mode=='--build-adapter': raise SystemExit(build_main())
    if mode=='--focused': raise SystemExit(focused_main())
    raise ValueError('unknown narrow adapter '+mode)
