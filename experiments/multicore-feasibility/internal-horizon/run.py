#!/usr/bin/env python3
"""Supervise selected checks/build, fixed collection, then independent offline audit."""
import argparse,os,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,DEFAULT_CRATE,read,write,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--crate',type=Path,default=DEFAULT_CRATE);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir();policy=read(HERE/'policy.json');deadline=time.monotonic()+policy['limits']['pipelineSeconds'];state=dict(schema='rook2-internal-split-stream-v1',complete=False,stages=[],failure=None,policySha256=sha(HERE/'policy.json'));write(out/'stream.json',state)
    stages=[('prepare',['/usr/bin/python3',str(HERE/'prepare.py'),'--crate',str(a.crate.resolve()),'--output',str(out/'prepare')],1250),('collect',['/usr/bin/python3',str(HERE/'collect.py'),'--build',str(out/'prepare/build'),'--preparation',str(out/'prepare/preparation-run.json'),'--output',str(out/'collection')],1850),('reconcile',['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'collection')],180)]
    try:
        for name,argv,cap in stages:
            start=time.monotonic_ns()
            with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
                child=subprocess.Popen(argv,stdout=stdout,stderr=stderr,start_new_session=True)
                try:code=child.wait(timeout=max(.001,min(cap,deadline-time.monotonic())))
                except BaseException:
                    os.killpg(child.pid,signal.SIGTERM)
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                    raise
            row=dict(stage=name,argv=argv,pid=child.pid,exit=code,wallNs=time.monotonic_ns()-start,stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr')));state['stages'].append(row);write(out/'stream.json',state);print(name+' exit '+str(code),flush=True);assert code==0,(name,code)
        assert read(out/'collection/reconciled.json')['complete'];state.update(complete=True);write(out/'stream.json',state);print('internal-split frozen stream complete',flush=True)
    except BaseException as error:state.update(failure=repr(error));write(out/'stream.json',state);raise
if __name__=='__main__':main()
