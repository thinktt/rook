#!/usr/bin/env python3
"""Complete the same census after a proved bound repair; caps unchanged."""
import argparse,os,re,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,ROOT,DEFAULT_CRATE,FEATURE,HELPERS,baseline,snapshot,read,write,sha
FAILED=Path('/home/legolas/rook2-experiments/coarse-pure-salvage-20261026-01')
DIAGNOSTIC=Path('/home/legolas/rook2-experiments/coarse-pure-salvage-diagnostic-20261026-01')
SELECTORS=['pure_observer::tests::serialization_']
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir();crate=DEFAULT_CRATE;source=snapshot(crate);prior=read(FAILED/'prepare/preparation-run.json');diag=read(DIAGNOSTIC/'diagnostic.json');assert prior['complete'] and prior['focusedTests']==11 and diag['complete'] and diag['observerReason']=='pure-demand-json-cap' and diag['nativeExit']==1
    changed=sorted(k for k in source if prior['sourceBefore'].get(k)!=source[k]);assert changed==['src/coarse_pure_salvage.rs','src/pure_observer.rs'];assert sha(HERE/'policy.json')==prior['tools'][str(HERE/'policy.json')];original=baseline();assert original==prior['baselineBefore'];assert set(os.sched_getaffinity(0))==HELPERS
    prep=out/'prepare';prep.mkdir();tools={str(p):sha(p) for p in HERE.glob('*.py')};tools[str(HERE/'policy.json')]=sha(HERE/'policy.json');receipt=dict(schema='rook2-coarse-pure-completion-preparation-v1',complete=False,crate=str(crate),sourceBefore=source,baselineBefore=original,inheritedControls=prior['inheritedControls'],reusedCurrentControls=[dict(kind='first-census-preparation',path=str(FAILED/'prepare/preparation-run.json'),sha256=sha(FAILED/'prepare/preparation-run.json'),focusedTests=11),dict(kind='error-diagnostic',path=str(DIAGNOSTIC/'diagnostic.json'),sha256=sha(DIAGNOSTIC/'diagnostic.json'),focusedTests=1)],toolArchive=dict(path=str(FAILED/'frozen-tools/archive.json'),sha256=sha(FAILED/'frozen-tools/archive.json')),sourceChangeFromFailed=changed,reusedSourceDelta=prior['reusedSourceDelta'],tools=tools,selectors=SELECTORS,stages=[],failure=None)
    write(prep/'preparation-run.json',receipt)
    for n in source:
        d=prep/'source-before'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(crate/n,d)
    env=dict(os.environ,PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_INCREMENTAL='0')
    for k in list(env):
        if k in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or k.startswith(('CARGO_PROFILE_','ROOK2_')):env.pop(k,None)
    def verify():
        assert snapshot(crate)==source and baseline()==original
        for f,h in tools.items():assert sha(f)==h,f
    deadline=time.monotonic()+1800;state=dict(schema='rook2-coarse-pure-completion-stream-v1',complete=False,stages=[],failure=None);write(out/'stream.json',state)
    def stage(name,argv,cap,directory):
        verify();started=time.monotonic_ns()
        with (directory/(name+'.stdout')).open('xb') as stdout,(directory/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen(argv,cwd=crate,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=child.wait(timeout=max(.001,min(cap,deadline-time.monotonic())))
            except BaseException:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                raise
        row=dict(stage=name,argv=argv,pid=child.pid,exit=code,wallNs=time.monotonic_ns()-started,stdoutSha256=sha(directory/(name+'.stdout')),stderrSha256=sha(directory/(name+'.stderr')));state['stages'].append(row);write(out/'stream.json',state);assert code==0,(name,code);verify();print(name+' exit0',flush=True);return row
    try:
        row=stage('tests-00',['/usr/bin/cargo','test','--offline','--locked','--lib','--features',FEATURE,'--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(prep/'test-target'),SELECTORS[0],'--','--test-threads=1'],240,prep);text=(prep/'tests-00.stdout').read_text();names=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M);assert len(names)==3;assert re.search(r'^test result: ok\. 3 passed; 0 failed; 0 ignored;',text,re.M);row['passedTests']=names;receipt['stages'].append(row);write(prep/'preparation-run.json',receipt)
        row=stage('build',['/usr/bin/python3',str(HERE/'build.py'),'--crate',str(crate),'--output',str(prep/'build')],330,prep);receipt['stages'].append(row);receipt.update(complete=True,sourceAfter=snapshot(crate),baselineAfter=baseline(),focusedTests=3);write(prep/'preparation-run.json',receipt)
        stage('collect',['/usr/bin/python3',str(HERE/'collect.py'),'--build',str(prep/'build'),'--preparation',str(prep/'preparation-run.json'),'--output',str(out/'census')],200,out)
        stage('reconcile',['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'census')],180,out);assert read(out/'census/reconciled.json')['complete'];state['complete']=True;write(out/'stream.json',state)
    except BaseException as error:
        state['failure']=repr(error);write(out/'stream.json',state)
        if not receipt['complete']:receipt['failure']=repr(error);write(prep/'preparation-run.json',receipt)
        raise
if __name__=='__main__':main()
