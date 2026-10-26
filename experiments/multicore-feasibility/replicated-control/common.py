"""Matched fixed-depth study contracts; frozen wait4/placement, no wire replay."""
import ast
import hashlib
import json
import os
import re
from pathlib import Path
import selectors
import subprocess
import sys
import time
import tomllib

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EPOCH=HERE.parent/'epoch-colors'
LEGACY=HERE.parent/'colors-three'
ACCOUNT=HERE/'common.py'
DEFAULT_CRATE=Path('/home/legolas/rook2-experiments/workspaces/replicated-control-20261026-01')
PRESERVED_CRATE=Path('/home/legolas/rook2-experiments/workspaces/replicated-control-preserved-20261026-01')
BASE_CRATE=Path('/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01')
FEATURE='replicated-control'
BINARY='rook2-replica-study'
DRIVER='src/bin/'+BINARY+'.rs'
HELPERS={0,1,2,3,8,9,10,11,12,13}
CASES=['profile-35','profile-08','profile-43']
NAMES=['preservedinline1','preservedpacket3','newinline1','newpacket3','newreplica3']
LIMITS=dict(perLifeSeconds=180,collectionSeconds=1800,pipelineSeconds=3600,
            placementSeconds=10,firstInputSeconds=12,auditTraceCap=32768)
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB','joinNs']
LEAD=Path('/home/legolas/agent-memos/imp2-lead-to-imp2-replicated-control-discriminator-20261026.md')
RESET_POLICY=Path('/home/legolas/agent-memos/imp2-lead-current-reset-stop-policy-20261026.md')


def module(name,path):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


epoch=module('replicated_study_frozen_epoch',EPOCH/'common.py')
sha,read,write,snapshot=epoch.sha,epoch.read,epoch.write,epoch.snapshot
SPEC,housekeeping,stop_owned,dist=epoch.SPEC,epoch.housekeeping,epoch.stop_owned,epoch.dist


def code_paths():
    return [HERE/name for name in ['common.py','build.py','prepare.py','collect.py','reconcile.py']]+[
        EPOCH/'common.py',LEGACY/'account_threads.py',Path(housekeeping.__file__)]


def reused_evidence_paths():
    return [HERE.parent/'type-disjoint-four/closure.json',EPOCH/'preparation.json',
        HERE.parent/'branch-transactions/inputs/profile-35.txt',
        HERE.parent/'branch-transactions/inputs/profile-08.txt',SPEC/'workloads.json']


def baseline():
    closure=read(HERE.parent/'type-disjoint-four/closure.json');assert closure['complete']
    values=dict(closure['protectedArtifacts'])
    for image in closure['images'].values():
        assert image['path'] not in values or values[image['path']]==image['sha256']
        values[image['path']]=image['sha256']
    for path,digest in values.items():assert sha(path)==digest,path
    return values


def input_text(case):
    workload=next(row for row in read(SPEC/'workloads.json')['cases'] if row['id']==case)
    assert case in CASES and workload['position']['initial']=='standard-start'
    p=workload['personality']['parameters'];assert p['rnd']==0
    own=['myp','myn','myb','myr','myq','myk','mycc','mymob','myks','mypp','mypw']
    opponent=['opp','opn','opb','opr','opq','opk','opcc','opmob','opks','oppp','oppw']
    values=dict(case=case,fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        moves=' '.join(workload['position']['moves']),own=','.join(str(p[key]) for key in own),
        opponent=','.join(str(p[key]) for key in opponent),evaluation=','.join(str(p[key]) for key in ['avd','cfd','sop']),
        search=','.join(str(p[key]) for key in ['sel','md','tts','ana']),randomness='0')
    text=''.join(key+'='+value+'\n' for key,value in values.items())
    prior=HERE.parent/'branch-transactions/inputs'/(case+'.txt')
    if prior.exists():assert prior.read_text()==text
    return text


def input_hashes():
    return {case:hashlib.sha256(input_text(case).encode()).hexdigest() for case in CASES}


def prepare_inputs(directory):
    directory=Path(directory);directory.mkdir()
    for case in CASES:
        with (directory/(case+'.txt')).open('x') as stream:stream.write(input_text(case))
    return input_records(directory)


def input_records(directory):
    values={case:dict(path=str(Path(directory)/(case+'.txt')),sha256=input_hashes()[case]) for case in CASES}
    for case,row in values.items():assert Path(row['path']).read_text()==input_text(case) and sha(row['path'])==row['sha256']
    return values


def preparation(path):
    value=read(path)
    assert value['schema']=='rook2-replicated-control-source-preparation-v1'
    assert Path(value['candidateCrate']).resolve()==DEFAULT_CRATE and Path(value['preservedCrate']).resolve()==PRESERVED_CRATE
    assert value['baseSource']==read(EPOCH/'preparation.json')['candidateSource']==snapshot(BASE_CRATE)
    assert value['candidateSource']==snapshot(DEFAULT_CRATE) and value['preservedSource']==snapshot(PRESERVED_CRATE)
    base,preserved,new=value['baseSource'],value['preservedSource'],value['candidateSource']
    assert all(preserved[name]==digest for name,digest in base.items() if name!='Cargo.toml')
    assert set(preserved)-set(base)=={DRIVER} and set(base)<=set(new)
    assert sha(DEFAULT_CRATE/DRIVER)==sha(PRESERVED_CRATE/DRIVER)
    for crate in [DEFAULT_CRATE,PRESERVED_CRATE]:
        manifest=tomllib.loads((crate/'Cargo.toml').read_text())
        assert manifest['features'][FEATURE]==[]
        assert manifest['profile']['release']==dict({'opt-level':3,'lto':'thin','codegen-units':1,'panic':'abort','debug':1})
    assert value['protectedArtifacts']==baseline() and value['inputTextSha256']==input_hashes()
    assert value['focused']
    assert len({row['name'] for row in value['focused']})==len(value['focused'])
    for row in value['focused']:
        assert row['target'] in [['--lib'],['--bin',BINARY]] and row['selector']
        assert type(row['expectedPassed']) is int and row['expectedPassed']>0
        assert 0<row.get('limitSeconds',300)<=300
    for file in code_paths()+[HERE/'plan.md',HERE/'policy.json',LEAD,RESET_POLICY]:
        assert value['inputSha256'][str(file)]==sha(file),file
    for file in reused_evidence_paths():assert value['reusedEvidenceSha256'][str(file)]==sha(file),file
    for field in ['inputSha256','reusedEvidenceSha256']:
        for file,digest in value[field].items():assert sha(file)==digest,file
    return value


def variants(preserved,candidate):
    return dict(preservedinline1=dict(path=str(preserved),mode='inline',budget=1),
        preservedpacket3=dict(path=str(preserved),mode='packet',budget=3),
        newinline1=dict(path=str(candidate),mode='inline',budget=1),
        newpacket3=dict(path=str(candidate),mode='packet',budget=3),
        newreplica3=dict(path=str(candidate),mode='replica',budget=3))


def schedule():
    rows=[]
    for case in CASES:
        rows += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            rows += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(rows)==60
    return rows


def peer_names(mode):return ['rook2-rep-1','rook2-rep-2'] if mode=='replica' else ['rook2-eval-whit','rook2-eval-blac']


def check_ready(path,image,budget,mode,supervisor_pid):
    value=read(path)
    assert value['schema']=='rook2-external-placement-ready-v1' and value['supervisor_pid']==supervisor_pid
    assert value['engine']==str(image) and value['engine_sha256']==sha(image) and value['launcher_sha256']==sha(ACCOUNT)
    assert value['expected_threads']==budget
    assert value['native_pre_exec']==dict(pid=value['native_pid'],pgid=supervisor_pid,affinity=[4,6,14] if budget==3 else [6,14])
    observed=value['native_post_exec'];masks=observed['task_affinities'];pid=value['native_pid']
    assert observed['path']==str(image) and observed['pgid']==supervisor_pid and observed['affinity']==[14]
    assert len(masks)==budget and masks[str(pid)]==[14]
    peers=sorted(int(tid) for tid in masks if tid!=str(pid))
    assert [masks[str(tid)] for tid in peers]==([[6],[4]] if budget==3 else [])
    assert [observed['task_names'][str(tid)] for tid in peers]==(peer_names(mode) if budget==3 else [])
    before=value['task_affinities_before_pinning'];assert set(before)==set(masks)
    assert all(mask and set(mask)<=set(value['native_pre_exec']['affinity']) for mask in before.values())
    return value


def options(mode,input_path,depth,auditing=False):
    return ['--mode',mode,'--input',str(input_path),'--depth',str(depth),'--gated']+(['--audit'] if auditing else [])


def supervisor(image,budget,directory,args):
    return ['/usr/bin/python3',str(ACCOUNT),'--account','--engine',str(image),'--record',str(directory/'native.json'),
        '--known-single-process','--thread-budget',str(budget),*args]


def account_main():
    """Original direct wait4 supervisor; only the replica helper names differ."""
    value=module('replicated_frozen_account',LEGACY/'account_threads.py');value.__file__=str(ACCOUNT)
    source=(LEGACY/'account_threads.py').read_text()
    node=next(item for item in ast.parse(source).body if isinstance(item,ast.FunctionDef) and item.name=='run')
    source=ast.get_source_segment(source,node)
    before="assert [observed['task_names'][tid] for tid in helper_tasks] == ['rook2-eval-whit', 'rook2-eval-blac']"
    after="assert [observed['task_names'][tid] for tid in helper_tasks] == (['rook2-rep-1', 'rook2-rep-2'] if engine_args[engine_args.index('--mode')+1] == 'replica' else ['rook2-eval-whit', 'rook2-eval-blac'])"
    assert source.count(before)==1;source=source.replace(before,after)
    exec(compile(source,str(LEGACY/'account_threads.py'),'exec'),value.__dict__)
    return value.run()


def parse_report(directory,mode,depth,auditing):
    raw=(directory/'stdout.raw').read_bytes();lines=raw.splitlines()
    assert len(lines)==2 and lines[0]==b'READY' and raw.endswith(b'\n')
    def pairs(items):
        result={}
        for key,value in items:assert key not in result;result[key]=value
        return result
    def nonfinite(value):raise ValueError(value)
    value=json.loads(lines[1],object_pairs_hook=pairs,parse_constant=nonfinite)
    assert value['schema']=='rook2-replicated-control-study-v1'
    assert value['mode']==mode and value['depth']==depth and value['audit'] is auditing
    for field in ['searchWallNs','joinNs']:assert type(value[field]) is int and value[field]>=0
    assert 0<value['searchWallNs'] and value['joinNs']<=value['searchWallNs']
    assert value['allReplicasEqual'] is True and type(value['outcome']) is dict and value['outcome']
    assert type(value['collectiveStorageBytes']) is int
    assert value['collectiveStorageBytes']>0 if mode=='replica' else value['collectiveStorageBytes']==0
    assert set(value['outcome'])=={'score','pv','initialCandidates','nodes','relations','rawRootReturns','iterations'}
    assert type(value['outcome']['score']) is int
    assert all(type(value['outcome'][key]) is int and value['outcome'][key]>=0 for key in ['nodes','relations'])
    for key in ['pv','initialCandidates','rawRootReturns']:
        assert type(value['outcome'][key]) is list and all(type(item) is int for item in value['outcome'][key])
    assert type(value['outcome']['iterations']) is list
    for iteration in value['outcome']['iterations']:
        assert set(iteration)=={'depth','candidates','score','pv','nodes','relations','steps'}
        assert type(iteration['steps']) is list
        assert all(type(iteration[key]) is int for key in ['depth','score','nodes','relations'])
        for key in ['pv','candidates']:
            assert type(iteration[key]) is list and all(type(item) is int for item in iteration[key])
        if not auditing:assert iteration['steps']==[]
    if auditing:
        assert mode=='replica' and depth==2
        assert type(value['auditCheckedFulls']) is int and 0<value['auditCheckedFulls']<=32768
        assert value['auditFinalStateEqual'] is value['pawnOwnerEqual'] is True
    else:assert all(value[key] is None for key in ['auditCheckedFulls','auditFinalStateEqual','pawnOwnerEqual'])
    if mode=='replica':
        participation=value['participation'];assert set(participation)=={'epochs','roles'}
        epochs=participation['epochs'];assert type(epochs) is list and len(epochs)==3
        assert all(type(epoch) is int and 0<epoch<2**64 for epoch in epochs) and len(set(epochs))==1
        assert participation['roles']==[0,1,2] and all(type(role) is int for role in participation['roles'])
    else:assert value['participation'] is None
    return value


def saved_lifetime(directory,step,image,variant,hashes,input_path,depth,auditing=False):
    assert (directory/'stdin.raw').read_bytes()==b'go\n' and (directory/'stderr').read_bytes()==b''
    args=options(variant['mode'],input_path,depth,auditing);native=read(directory/'native.json')
    assert native['schema']=='rook2-native-wait4-v1' and native['known_single_process']
    assert native['failure'] is native['placement_error'] is native['exec_error'] is None
    assert native['native_exit_code']==native['native_wait_status']==0 and native['supervisor_signals']==[]
    assert native['argv']==[str(image),*args] and native['engine']==str(image)
    assert native['engine_sha256_before']==native['engine_sha256_after']==sha(image)
    assert native['launcher_sha256']==hashes[str(ACCOUNT)]==sha(ACCOUNT)
    assert sha(native['python_executable'])==native['python_executable_sha256']
    assert native['inherited_supervisor_affinity']==native['supervisor_affinity']==sorted(HELPERS)
    assert native['colors_report_path'] is native['colors_report_sha256'] is None
    ready=check_ready(directory/'native.json.ready',image,variant['budget'],variant['mode'],native['supervisor_pid'])
    for key in ['native_pid','supervisor_pid','expected_threads','native_pre_exec','native_post_exec']:assert native[key]==ready[key]
    assert native['ready_path']==str(directory/'native.json.ready')
    assert native['ready_sha256']==sha(directory/'native.json.ready')
    gate=read(directory/'go.json')
    assert gate['readySha256']==sha(directory/'native.json.ready') and gate['stdinSha256']==sha(directory/'stdin.raw')
    assert gate['nativePid']==native['native_pid'] and gate['supervisorPid']==native['supervisor_pid']
    assert native['start_monotonic_ns']<=int(ready['ready_monotonic_ns'])<=gate['releaseMonotonicNs']<native['reaped_monotonic_ns']
    assert gate['readyPrefix']==[82,69,65,68,89,10]
    assert native['wall_ns']==native['reaped_monotonic_ns']-native['start_monotonic_ns']>0
    assert 0<native['wall_ns']<=180*10**9 and native['total_cpu_s']==native['user_cpu_s']+native['system_cpu_s']>0
    report=parse_report(directory,variant['mode'],depth,auditing)
    assert report['searchWallNs']<=native['wall_ns'] and native['maxrss_linux_kib']>0
    launch=read(directory/'launch.json')
    assert launch==dict(argv=supervisor(image,variant['budget'],directory,args),step=step,inputSha256=sha(input_path),audit=auditing)
    for pid in [native['native_pid'],native['supervisor_pid']]:assert not Path('/proc',str(pid)).exists(),'recorded PID live; inspect reuse'
    return native,report


def run_lifetime(directory,step,image,variant,deadline,hashes,input_path,depth=8,auditing=False):
    directory.mkdir();started=time.monotonic_ns();args=options(variant['mode'],input_path,depth,auditing)
    command=supervisor(image,variant['budget'],directory,args)
    write(directory/'launch.json',dict(argv=command,step=step,inputSha256=sha(input_path),audit=auditing))
    (directory/'stdin.raw').touch(exist_ok=False)
    env={key:value for key,value in os.environ.items() if not key.startswith('ROOK2_') and key!='LLVM_PROFILE_FILE'}
    cap=128*1024*1024 if auditing else 4*1024*1024
    life_deadline=min(deadline,time.monotonic()+180);output=bytearray();released=False;eof=False
    with (directory/'stderr').open('xb') as stderr,(directory/'stdout.raw').open('xb') as stdout:
        child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,env=env,start_new_session=True)
        selector=selectors.DefaultSelector();selector.register(child.stdout,selectors.EVENT_READ)
        try:
            while child.poll() is None or not eof:
                assert time.monotonic()<life_deadline,'native life/pipeline deadline'
                assert (directory/'stderr').stat().st_size<=1024*1024
                for key,_ in selector.select(.01):
                    data=os.read(key.fileobj.fileno(),65536)
                    if not data:eof=True;selector.unregister(key.fileobj);continue
                    output.extend(data);stdout.write(data);stdout.flush();assert len(output)<=cap
                if not released and b'\n' in output:
                    assert output==b'READY\n','unexpected output before GO'
                    ready_path=directory/'native.json.ready'
                    if ready_path.exists():
                        ready=check_ready(ready_path,image,variant['budget'],variant['mode'],child.pid)
                        (directory/'stdin.raw').write_bytes(b'go\n')
                        write(directory/'go.json',dict(releaseMonotonicNs=time.monotonic_ns(),readySha256=sha(ready_path),
                            nativePid=ready['native_pid'],supervisorPid=child.pid,stdinSha256=sha(directory/'stdin.raw'),readyPrefix=list(output)))
                        child.stdin.write(b'go\n');child.stdin.close();released=True
                if not released:assert time.monotonic_ns()-started<12*10**9,'READY/placement deadline'
            assert released and child.wait(timeout=max(.01,life_deadline-time.monotonic()))==0
        except BaseException as error:
            stop_owned(child);write(directory/'failure.json',dict(error=repr(error),exit=child.poll(),released=released));raise
        finally:
            selector.close();child.stdout.close()
            if child.stdin is not None and not child.stdin.closed:child.stdin.close()
    native,report=saved_lifetime(directory,step,image,variant,hashes,input_path,depth,auditing)
    row=dict(**step,directory=str(directory),nativePid=native['native_pid'],report=report,
        searchWallNs=report['searchWallNs'],joinNs=report['joinNs'],wholeCpuSeconds=native['total_cpu_s'],
        wholeWallNs=native['wall_ns'],nonSearchWallNs=native['wall_ns']-report['searchWallNs'],rssKiB=native['maxrss_linux_kib'],
        controllerStartMonotonicNs=started,controllerEndMonotonicNs=time.monotonic_ns(),
        sha256={name:sha(directory/name) for name in ['launch.json','stdin.raw','stdout.raw','stderr','go.json','native.json','native.json.ready']})
    return row


def admit_build(directory,variant,prepared):
    builder=module('replicated_study_build_admission',HERE/'build.py')
    value=builder.admit(directory)
    expected=prepared['preservedSource' if variant=='preserved' else 'candidateSource']
    assert value['variant']==variant and value['sourceBefore']==expected
    return value


def prepared_run(path,prepared_path,prepared):
    value=read(path);base=path.parent
    assert value['schema']=='rook2-replicated-control-prepared-run-v1' and value['complete']
    assert value['sourcePreparation']==str(prepared_path) and value['sourcePreparationSha256']==sha(prepared_path)
    assert value['sourcePreparationValue']==prepared and value['inputs']==input_records(base/'inputs')
    assert value['pipelineDeadlineMonotonicNs']==value['pipelineStartMonotonicNs']+3600*10**9
    assert value['pipelineStartMonotonicNs']<=value['preparedMonotonicNs']<value['pipelineDeadlineMonotonicNs']
    for file,digest in value['inputSha256'].items():assert sha(file)==digest,file
    builds={variant:admit_build(base/(variant+'-build'),variant,prepared) for variant in ['preserved','new']}
    for source in ['src/lib.rs',DRIVER]:
        old={key:item for key,item in builds['preserved']['effectiveOptions'][source].items() if key not in ['metadata','extra-filename']}
        new={key:item for key,item in builds['new']['effectiveOptions'][source].items() if key not in ['metadata','extra-filename']}
        assert old==new
    assert builds['preserved']['toolchain']==builds['new']['toolchain']
    for variant,build in builds.items():
        assert value['images'][variant]==dict(path=build['binary'],sha256=build['binarySha256'])
    stages=value['stages'];expected=['tests-'+str(i).zfill(2)+'-'+row['name'] for i,row in enumerate(prepared['focused'])]+['preserved-build','new-build']
    assert [row['stage'] for row in stages]==expected and all(row['exit']==0 for row in stages)
    previous_end=value['pipelineStartMonotonicNs']
    for index,row in enumerate(stages):
        assert previous_end<=row['startedMonotonicNs']<row['endedMonotonicNs']<=value['preparedMonotonicNs']
        assert row['elapsedNs']==row['endedMonotonicNs']-row['startedMonotonicNs']
        cap=prepared['focused'][index].get('limitSeconds',300) if index<len(prepared['focused']) else 330
        assert row['endedMonotonicNs']<=row['deadlineMonotonicNs']<=value['pipelineDeadlineMonotonicNs']
        assert row['deadlineMonotonicNs']<=row['startedMonotonicNs']+cap*10**9
        previous_end=row['endedMonotonicNs']
        for suffix in ['stdout','stderr']:
            file=base/(row['stage']+'.'+suffix)
            assert sha(file)==row[suffix+'Sha256']==value['inputSha256'][str(file)]
        if index<len(prepared['focused']):
            tests=prepared['focused'][index]
            argv=['/usr/bin/cargo','test','--offline','--locked',*tests['target'],'--features',FEATURE,
                '--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(base/'test-target'),
                tests['selector'],'--','--test-threads=1']
            if tests.get('exact',False):argv.append('--exact')
            if tests.get('ignored',False):argv.append('--ignored')
            assert row['argv']==argv and row['cwd']==str(DEFAULT_CRATE)
            text=(base/(row['stage']+'.stdout')).read_text()
            passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
            assert passed==row['passedTests'] and len(passed)==len(set(passed))==tests['expectedPassed']
            assert re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)==[(str(len(passed)),'0','0')]
        else:
            variant=['preserved','new'][index-len(prepared['focused'])]
            assert row['argv']==['/usr/bin/python3',str(HERE/'build.py'),'--variant',variant,'--output',str(base/(variant+'-build'))]
            assert row['cwd']==str(ROOT)
    assert len(value['audits'])==3
    replica=dict(path=value['images']['new']['path'],mode='replica',budget=3)
    for case,row in zip(CASES,value['audits']):
        assert row['case']==case and row['variant']=='newreplica3-audit'
        directory=base/'audits'/case
        native,report=saved_lifetime(directory,dict(case=case,variant='newreplica3-audit'),Path(replica['path']),replica,
            value['inputSha256'],Path(value['inputs'][case]['path']),2,True)
        assert report==row['report'] and previous_end<=row['controllerStartMonotonicNs']<=native['start_monotonic_ns']
        assert native['reaped_monotonic_ns']<=row['controllerEndMonotonicNs']<=value['preparedMonotonicNs']
        previous_end=row['controllerEndMonotonicNs']
        for name,digest in row['sha256'].items():assert sha(directory/name)==digest
    return value


if __name__=='__main__':
    assert sys.argv.pop(1)=='--account'
    raise SystemExit(account_main())
