#!/usr/bin/env python3
"""Bounded prepare/capture/external-freeze/conditional-single-fixture stream."""
import argparse,os,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,DEFAULT_CRATE,read,write,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--crate',type=Path,default=DEFAULT_CRATE);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir();policy=read(HERE/'policy.json');deadline=time.monotonic()+policy['limits']['pipelineSeconds'];state=dict(schema='rook2-wide-stream-v1',complete=False,stages=[],failure=None,policySha256=sha(HERE/'policy.json'));write(out/'stream.json',state)
    def stage(name,argv,cap):
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
    common=['--build',str(out/'prepare/build'),'--preparation',str(out/'prepare/preparation-run.json')]
    try:
        stage('prepare',['/usr/bin/python3',str(HERE/'prepare.py'),'--crate',str(a.crate.resolve()),'--output',str(out/'prepare')],1250)
        stage('capture',['/usr/bin/python3',str(HERE/'collect.py'),*common,'--mode','capture','--output',str(out/'capture')],930)
        stage('select',['/usr/bin/python3',str(HERE/'select_fixture.py'),str(out/'capture'),'--output',str(out/'fixture.txt')],180)
        selection=read(out/'fixture-selection.json');assert selection['complete']
        if selection['selected'] is not None:
            build=read(out/'prepare/build/receipt.json');freeze=dict(schema='rook2-wide-fixture-freeze-v1',fixture=str(out/'fixture.txt'),fixtureSha256=sha(out/'fixture.txt'),selectionSha256=sha(out/'fixture-selection.json'),binarySha256=build['binarySha256'],source=build['sourceBefore'],schedule=policy['schedule'],frozenMonotonicNs=time.monotonic_ns());write(out/'fixture-freeze.json',freeze)
            stage('compare',['/usr/bin/python3',str(HERE/'collect.py'),*common,'--mode','compare','--fixture',str(out/'fixture.txt'),'--capture-root',str(out/'capture'),'--output',str(out/'compare')],1850)
            assert sha(out/'fixture.txt')==freeze['fixtureSha256'] and sha(out/'fixture-selection.json')==freeze['selectionSha256']
            stage('reconcile',['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'compare')],180);assert read(out/'compare/reconciled.json')['complete']
        else:assert not (out/'fixture.txt').exists();state['stopReason']=selection['stopReason']
        state.update(complete=True);write(out/'stream.json',state);print('wide-internal frozen stream complete',flush=True)
    except BaseException as error:state.update(failure=repr(error));write(out/'stream.json',state);raise
if __name__=='__main__':main()
