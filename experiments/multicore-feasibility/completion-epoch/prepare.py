#!/usr/bin/env python3
"""Prepare one generic candidate, then collect the frozen48+4 on the same clock."""
import argparse
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
sys.dont_write_bytecode=True
from common import (HERE,ROOT,BUILD_ADAPTER,FOCUSED,LAYOUT,LOWERING,HELPERS,DEFAULT_CRATE,CONTROL_CRATE,CONTROL_BUILD,CONTROL_IMAGE,
    admit_build,admission,baseline,image_layout,layout_admission,lowering_admission,preparation,prepared_run,read,sha,write)


def main():
    def interrupted(signum,_frame): raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]: signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--stage',choices=['prepare','collect'],default='prepare')
    args=parser.parse_args()
    prepared_path,out=args.preparation.resolve(),args.output.resolve()
    prepared=preparation(prepared_path)
    assert set(os.sched_getaffinity(0))==HELPERS
    if args.stage=='prepare':
        out.mkdir();start=time.monotonic_ns()
        state=dict(schema='rook2-completion-epoch-pipeline-v1',complete=False,prepared=False,collected=False,
            failure=None,active=None,stages=[],preparation=str(prepared_path),preparationSha256=sha(prepared_path),
            sourcePreparation=prepared,protectedArtifacts=baseline(),pipelineStartMonotonicNs=start,
            pipelineDeadlineMonotonicNs=start+3600*10**9,parentQuietAnnouncementRequired=True)
    else:
        state=read(out/'pipeline.json')
        assert state['schema']=='rook2-completion-epoch-pipeline-v1'
        assert state['complete'] and state['active'] is None
        assert state['prepared'] and not state['collected'] and state['failure'] is None
        assert state['preparation']==str(prepared_path) and state['preparationSha256']==sha(prepared_path)
        assert state['sourcePreparation']==prepared and state['stages'][-1]['stage']=='lowering'
        prepared_run(out/'prepared-run.json',prepared_path,prepared)
        state['complete']=False;state.pop('pipelineEndedMonotonicNs',None)
    assert state['pipelineDeadlineMonotonicNs']==state['pipelineStartMonotonicNs']+3600*10**9
    env=dict(os.environ,PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or key.startswith(('CARGO_PROFILE_','ROOK2_')): env.pop(key,None)
    def check():
        assert preparation(prepared_path)==prepared and sha(prepared_path)==state['preparationSha256']
        assert state['protectedArtifacts']==baseline()
        assert time.monotonic_ns()<state['pipelineDeadlineMonotonicNs'],'persisted pipeline deadline'
    def stage(name,command,cap,cwd=ROOT,tests=None):
        check();state['active']=name;write(out/'pipeline.json',state)
        began=time.monotonic_ns();deadline=min(state['pipelineDeadlineMonotonicNs'],began+cap*10**9)
        with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen([str(x) for x in command],cwd=cwd,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:
                remaining=(deadline-time.monotonic_ns())/1e9;assert remaining>0
                code=child.wait(timeout=remaining)
                assert time.monotonic_ns()<deadline
            except BaseException:
                try: os.killpg(child.pid,signal.SIGINT)
                except ProcessLookupError: pass
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    try: os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError: pass
                    child.wait()
                raise
        ended=time.monotonic_ns()
        row=dict(stage=name,argv=[str(x) for x in command],cwd=str(cwd),pid=child.pid,exit=code,
            startedMonotonicNs=began,endedMonotonicNs=ended,elapsedNs=ended-began,deadlineMonotonicNs=deadline,
            stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr')))
        state['stages'].append(row);write(out/'pipeline.json',state)
        assert code==0,(name,code)
        if tests is not None:
            text=(out/(name+'.stdout')).read_text()
            passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
            summaries=re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)
            assert len(passed)==tests['expectedPassed'] and summaries==[(str(len(passed)),'0','0')]
            assert sorted(passed)==tests['expectedTests']
            row['passedTests']=passed;write(out/'pipeline.json',state)
        print(name+' exit '+str(code),flush=True);check()
    try:
        if args.stage=='prepare':
            admit_build(CONTROL_BUILD,CONTROL_IMAGE,CONTROL_CRATE,prepared['controlSource'])
            for index,tests in enumerate(prepared['focused']):
                command=['/usr/bin/cargo','test','--offline','--locked',*tests['target'],'--target','x86_64-unknown-linux-gnu',
                    '--jobs','4','--target-dir',str(out/'test-target'),tests['selector'],'--','--test-threads=1']
                if tests.get('exact',False): command.append('--exact')
                if tests.get('ignored',False): command.append('--ignored')
                stage(f'tests-{index:02d}-{tests["name"]}',command,tests.get('limitSeconds',300),DEFAULT_CRATE,tests)
            stage('candidate-build',['/usr/bin/python3',BUILD_ADAPTER,'--crate',DEFAULT_CRATE,
                '--mode','generic','--bin','rook2','--jobs','4','--output',out/'candidate-build'],300)
            receipt=read(out/'candidate-build/receipt.json');candidate=out/'rook2-candidate'
            shutil.copy2(Path(receipt['binary_output']['path']),candidate)
            admission(out/'candidate-build',candidate,prepared)
            stage('cli-affinity',['/usr/bin/python3',FOCUSED,'--engine',candidate,'--output',out/'focused'],420)
            stage('layout',['/usr/bin/python3',LAYOUT,'--engine',candidate,'--output',out/'layout'],120)
            projected=layout_admission(out/'layout/result.json',candidate,prepared)
            stage('lowering',['/usr/bin/python3',LOWERING,'--control',CONTROL_IMAGE,'--engine',candidate,
                '--control-crate',CONTROL_CRATE,'--candidate-crate',DEFAULT_CRATE,'--output',out/'lowering'],120)
            lowered=lowering_admission(out/'lowering/result.json',candidate,prepared)
            files=[out/(row['stage']+'.'+suffix) for row in state['stages'] for suffix in ['stdout','stderr']]
            files += [path for subdir in ['focused','layout','lowering'] for path in (out/subdir).rglob('*') if path.is_file()]
            record=dict(schema='rook2-completion-epoch-prepared-run-v1',complete=True,
                sourcePreparation=str(prepared_path),sourcePreparationSha256=sha(prepared_path),source=prepared['candidateSource'],
                candidate=image_layout(candidate),control=image_layout(CONTROL_IMAGE),stages=list(state['stages']),
                evidenceReuse=prepared['evidenceReuse'],
                testExecutionSummary=dict(selectedLogicalControls=32,executions=32,passed=32,failed=0,completedControlsRepeated=0),
                lowering=dict(path=str(out/'lowering/result.json'),sha256=sha(out/'lowering/result.json'),report=lowered),
                layout=dict(path=str(out/'layout/result.json'),sha256=sha(out/'layout/result.json'),report=projected),
                inputSha256={str(path):sha(path) for path in sorted(set(files))},
                pipelineStartMonotonicNs=state['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=state['pipelineDeadlineMonotonicNs'],
                preparedMonotonicNs=time.monotonic_ns())
            write(out/'prepared-run.json',record)
            checked=prepared_run(out/'prepared-run.json',prepared_path,prepared)
            assert isinstance(checked,dict) and checked==record
            state.update(prepared=True,complete=True,candidate=str(candidate),active=None)
        else:
            stage('collection',['/usr/bin/python3',HERE/'collect.py','--preparation',prepared_path,
                '--prepared-run',out/'prepared-run.json','--output',out/'pilot'],1900)
            stage('reconcile',['/usr/bin/python3',HERE/'reconcile.py',out/'pilot'],120)
            assert read(out/'pilot/reconciled.json')['complete']
            state.update(collected=True,complete=True,active=None)
        check();state['pipelineEndedMonotonicNs']=time.monotonic_ns();write(out/'pipeline.json',state)
    except BaseException as error:
        state.update(complete=False,failure=repr(error));write(out/'pipeline.json',state);raise
    print('prepared; stopped before timing' if args.stage=='prepare' else 'completed48+4 and independent audit',flush=True)


if __name__=='__main__': main()
