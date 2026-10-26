#!/usr/bin/env python3
"""Finite focused checks and one generic build; collection is a separate frozen step."""
import argparse, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,ROOT,DEFAULT_CRATE,HELPERS,FEATURE,baseline,snapshot,read,write,sha
SELECTORS=['pure_observer::tests::','coarse_pure_salvage::tests::']
INHERITED=[Path('/home/legolas/rook2-experiments/internal-split-20261026-01/prepare/preparation-run.json'),Path('/home/legolas/rook2-experiments/internal-horizon-20261026-01/prepare/preparation-run.json'),Path('/home/legolas/rook2-experiments/wide-internal-20261026-01/prepare/preparation-run.json')]

def main():
    def interrupted(signum,frame):raise InterruptedError("external signal "+str(signum))
    signal.signal(signal.SIGTERM,interrupted)
    signal.signal(signal.SIGINT,interrupted)
    p=argparse.ArgumentParser();p.add_argument('--crate',type=Path,default=DEFAULT_CRATE);p.add_argument('--output',type=Path,required=True);a=p.parse_args();crate=a.crate.resolve();out=a.output.resolve();out.mkdir();assert crate!=ROOT and set(os.sched_getaffinity(0))==HELPERS
    before=snapshot(crate);original=baseline();inherited=[read(f) for f in INHERITED];assert all(x['complete'] for x in inherited);assert [x['focusedTests'] for x in inherited]==[36,3,11]
    delta=sorted(k for k in set(before)|set(inherited[2]['sourceBefore']) if before.get(k)!=inherited[2]['sourceBefore'].get(k));allowed=['Cargo.toml','src/bin/rook2-coarse-pure-census.rs','src/coarse_pure_salvage.rs','src/engine.rs','src/evaluator.rs','src/internal_split.rs','src/lib.rs','src/ordinary.rs','src/pure_observer.rs'];assert delta==allowed,delta
    pins={str(x):sha(x) for x in HERE.glob('*.py')};pins[str(HERE/'policy.json')]=sha(HERE/'policy.json');state=dict(schema='rook2-coarse-pure-preparation-run-v1',complete=False,crate=str(crate),sourceBefore=before,baselineBefore=original,inheritedControls=[dict(path=str(f),sha256=sha(f),focusedTests=x['focusedTests']) for f,x in zip(INHERITED,inherited)],reusedSourceDelta=delta,tools=pins,selectors=SELECTORS,stages=[],failure=None);write(out/'preparation-run.json',state)

    for n in before:
        d=out/'source-before'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(crate/n,d)
    env=dict(os.environ,PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_INCREMENTAL='0')
    for k in list(env):
        if k in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or k.startswith(('CARGO_PROFILE_','ROOK2_')):env.pop(k,None)
    deadline=time.monotonic()+1200
    def check():
        assert snapshot(crate)==before and baseline()==original
        for f,d in pins.items():assert sha(f)==d,f
    def stage(name,argv,cap):
        check();start=time.monotonic_ns();maximum=min(cap,deadline-time.monotonic());assert maximum>0
        with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
            proc=subprocess.Popen(argv,cwd=crate,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=proc.wait(timeout=maximum)
            except BaseException:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait();raise
        row=dict(stage=name,argv=argv,pid=proc.pid,exit=code,wallNs=time.monotonic_ns()-start,stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr')))
        if name.startswith('tests-') and code==0:
            text=(out/(name+'.stdout')).read_text();names=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M);summary=re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M);assert len(summary)==1 and int(summary[0][0])==len(names)>0 and summary[0][1:]==('0','0');row['passedTests']=names
        state['stages'].append(row);write(out/'preparation-run.json',state);print(name+' exit '+str(code),flush=True);assert code==0,(name,code);check()
    try:
        for i,s in enumerate(SELECTORS):stage(f'tests-{i:02d}',['/usr/bin/cargo','test','--offline','--locked','--lib','--features',FEATURE,'--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(out/'test-target'),s,'--','--test-threads=1'],240)
        tests=[n for r in state['stages'] for n in r.get('passedTests',[])];assert len(tests)==len(set(tests))
        stage('build',['/usr/bin/python3',str(HERE/'build.py'),'--crate',str(crate),'--output',str(out/'build')],330)
        state.update(complete=True,sourceAfter=snapshot(crate),baselineAfter=baseline(),focusedTests=len(tests));write(out/'preparation-run.json',state)
    except BaseException as error:state.update(failure=repr(error));write(out/'preparation-run.json',state);raise
if __name__=='__main__':main()
