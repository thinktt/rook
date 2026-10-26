#!/usr/bin/env python3
"""One cold-error diagnostic attempt, unchanged keys/caps; no timing conclusion."""
import argparse,os,re,resource,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,DEFAULT_CRATE,HELPERS,FEATURE,snapshot,baseline,read,write,sha
from housekeeping import Placement
FAILED=Path('/home/legolas/rook2-experiments/coarse-pure-salvage-20261026-01')
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir();crate=DEFAULT_CRATE;old=read(FAILED/'prepare/preparation-run.json');source=snapshot(crate);delta=sorted(k for k in source if old['sourceBefore'].get(k)!=source[k]);assert delta==['src/coarse_pure_salvage.rs'];assert set(os.sched_getaffinity(0))==HELPERS
    chosen=read(HERE/'policy.json');assert sha(HERE/'policy.json')==old['tools'][str(HERE/'policy.json')];original=baseline();state=dict(schema='rook2-coarse-pure-error-diagnostic-v1',complete=False,diagnosticOnly=True,failedAttempt=str(FAILED),sourceBefore=source,sourceDelta=delta,policySha256=sha(HERE/'policy.json'),patchSha256=sha(HERE/'diagnostic-error.patch'),baseline=original,stages=[],failure=None);write(out/'diagnostic.json',state)
    env=dict(os.environ,PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_INCREMENTAL='0')
    for k in list(env):
        if k in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or k.startswith(('CARGO_PROFILE_','ROOK2_')):env.pop(k,None)
    def stage(name,argv,cap):
        started=time.monotonic_ns()
        with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
            proc=subprocess.Popen(argv,cwd=crate,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=proc.wait(timeout=cap)
            except BaseException:os.killpg(proc.pid,signal.SIGKILL);proc.wait();raise
        state['stages'].append(dict(stage=name,argv=argv,pid=proc.pid,exit=code,wallNs=time.monotonic_ns()-started,stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr'))));write(out/'diagnostic.json',state);assert code==0,(name,code);return out/(name+'.stdout')
    placement=Placement();affinity=sorted(os.sched_getaffinity(0))
    try:
        tests=stage('test',['/usr/bin/cargo','test','--offline','--locked','--lib','--features',FEATURE,'--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(out/'test-target'),'coarse_pure_salvage::tests::dispatcher_root_error_surfaces_observer_cap_or_key_failure','--','--test-threads=1'],240)
        names=re.findall(r'^test (\S+) \.\.\. ok$',tests.read_text(),re.M);assert len(names)==1;state['newDiagnosticTest']=names[0]
        stage('build',['/usr/bin/python3',str(HERE/'build.py'),'--crate',str(crate),'--output',str(out/'build')],330);receipt=read(out/'build/receipt.json');assert receipt['sourceBefore']==receipt['sourceAfter']==source
        d=out/'native';d.mkdir();write(d/'housekeeping.json',placement.apply(chosen['housekeepingCpus']));args=['--input',str(HERE/'inputs/profile-35.txt'),'--fixture',chosen['fixture']];argv=['/usr/bin/python3',str(HERE/'account.py'),'--engine',receipt['binary'],'--record',str(d/'native.json'),*args];write(d/'launch.json',dict(argv=argv,nativeArgv=[receipt['binary'],*args],source=source,policySha256=state['policySha256']));code=None;started=time.monotonic_ns();cleanup=None
        def limits():resource.setrlimit(resource.RLIMIT_AS,(chosen['limits']['addressSpaceBytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(chosen['limits']['reportBytes'],)*2)
        with (d/'stdout').open('xb') as stdout,(d/'stderr').open('xb') as stderr:
            proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env,start_new_session=True,preexec_fn=limits)
            try:code=proc.wait(timeout=chosen['limits']['perLifeSeconds'])
            except BaseException:
                cleanup='external deadline/interruption'
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:code=proc.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
                raise
            finally:write(d/'terminal.json',dict(pid=proc.pid,exit=code,cleanup=cleanup,startMonotonicNs=started,endMonotonicNs=time.monotonic_ns()))
        text=(d/'stderr').read_text();reason=re.search(r'observer=Some\("([^"]+)"\)',text);state.update(nativeExit=code,observerReason=reason.group(1) if reason else None,stdoutBytes=(d/'stdout').stat().st_size,nativeBindings={str(d/n):sha(d/n) for n in ['launch.json','terminal.json','native.json','stdout','stderr','housekeeping.json']});assert cleanup is None
        assert snapshot(crate)==source and baseline()==original;state.update(complete=True);write(out/'diagnostic.json',state);print('diagnostic native exit '+str(code)+' observer='+str(state['observerReason']),flush=True)
    except BaseException as error:state['failure']=repr(error);write(out/'diagnostic.json',state);raise
    finally:write(out/'housekeeping-restore.json',placement.restore());os.sched_setaffinity(0,set(affinity))
if __name__=='__main__':main()
