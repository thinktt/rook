#!/usr/bin/env python3
"""Six focused tests, one build and one original35 observation; no retries."""
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
from common import (HERE,ROOT,CRATE,HELPERS,BUILD_ADAPTER,PIPELINE_SECONDS,OPTIONS,STEP,TESTS,REPORT,
    admit_build,audit,baseline,code_paths,housekeeping,image_layout,preparation,read,run_lifetime,sha,write)


def observe(root,prepared_path):
    prepared=preparation(prepared_path);state=read(root/'pipeline.json')
    assert state['active']=='observe' and state['failure'] is None and not state['complete']
    assert [row['stage'] for row in state['stages']]==['unit-tests','candidate-build']
    assert state['preparation']==str(prepared_path) and state['preparationSha256']==sha(prepared_path)
    assert state['sourcePreparation']==prepared and time.monotonic_ns()<state['pipelineDeadlineMonotonicNs']
    image=root/'rook2-candidate';receipt,_=admit_build(root/'candidate-build',image,CRATE,prepared['candidateSource'])
    paths=code_paths()+[prepared_path,image,root/'candidate-build/receipt.json',root/'candidate-build/build.stderr']
    paths += [Path(path) for key in ['inputSha256','reusedEvidenceSha256','protectedArtifacts'] for path in prepared[key]]
    paths += [root/'candidate-build/source-before'/name for name in (receipt['source_sha256_before']|receipt['tool_sha256_before'])]
    plan=dict(schema='rook2-frontier-scale-count-observation-v1',case='profile-35',step=STEP,
        engine=image_layout(image),options=OPTIONS,budget=3,source=prepared['candidateSource'],
        sourcePreparation=str(prepared_path),preparationSha256=sha(prepared_path),
        pipelineStartMonotonicNs=state['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=state['pipelineDeadlineMonotonicNs'],
        inputSha256={str(path):sha(path) for path in sorted(set(paths))},protectedArtifacts=baseline())
    write(root/'observation-plan.json',plan)
    row=run_lifetime(root/'replay',STEP,image,dict(budget=3,options=OPTIONS,report=False),
        state['pipelineDeadlineMonotonicNs']/1e9,plan['inputSha256'])
    report=root/'replay'/REPORT
    assert report.is_file() and not report.is_symlink() and 0<report.stat().st_size<=1024*1024
    row['frontierReport']=dict(path=str(report),sha256=sha(report))
    assert row['orderedPosts']==13 and row['replayRunnerExit']==0
    assert all(sha(path)==digest for path,digest in plan['inputSha256'].items())
    write(root/'replay/result.json',row)
    print('one original35 replay joined; saved counter report',flush=True)


def main():
    def interrupted(signum,_frame):raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]:signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--observe-only',action='store_true');args=parser.parse_args()
    prepared_path,root=args.preparation.resolve(),args.output.resolve()
    if args.observe_only:observe(root,prepared_path);return
    prepared=preparation(prepared_path);assert set(os.sched_getaffinity(0))==HELPERS
    root.mkdir();start=time.monotonic_ns()
    state=dict(schema='rook2-frontier-scale-count-pipeline-v1',complete=False,failure=None,active=None,stages=[],
        preparation=str(prepared_path),preparationSha256=sha(prepared_path),sourcePreparation=prepared,
        protectedArtifacts=baseline(),pipelineStartMonotonicNs=start,pipelineDeadlineMonotonicNs=start+PIPELINE_SECONDS*10**9)
    placement=housekeeping.Placement();house=dict(applies=[],restored=None,failure=None,helperCpus=sorted(HELPERS))
    env={key:value for key,value in os.environ.items() if not key.startswith(('ROOK2_','CARGO_PROFILE_')) and key not in
        ['LLVM_PROFILE_FILE','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']}
    env.update(PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_INCREMENTAL='0')
    def check():
        assert preparation(prepared_path)==prepared and sha(prepared_path)==state['preparationSha256']
        assert baseline()==state['protectedArtifacts'] and time.monotonic_ns()<state['pipelineDeadlineMonotonicNs']
    def stage(name,command,cap):
        check();house['applies'].append(placement.apply(HELPERS));state['active']=name;write(root/'pipeline.json',state)
        began=time.monotonic_ns();deadline=min(state['pipelineDeadlineMonotonicNs'],began+cap*10**9)
        with (root/(name+'.stdout')).open('xb') as stdout,(root/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen([str(part) for part in command],cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=child.wait(timeout=max(.001,(deadline-time.monotonic_ns())/1e9))
            except BaseException:
                try:os.killpg(child.pid,signal.SIGINT)
                except ProcessLookupError:pass
                try:child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    try:os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    child.wait()
                raise
        ended=time.monotonic_ns()
        state['stages'].append(dict(stage=name,argv=[str(part) for part in command],cwd=str(ROOT),pid=child.pid,exit=code,
            startedMonotonicNs=began,endedMonotonicNs=ended,deadlineMonotonicNs=deadline,
            stdoutSha256=sha(root/(name+'.stdout')),stderrSha256=sha(root/(name+'.stderr'))))
        write(root/'pipeline.json',state);assert code==0 and ended<deadline,(name,code)
        if name=='unit-tests':
            text=(root/'unit-tests.stdout').read_text()
            passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
            assert sorted(passed)==TESTS and re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)==[('6','0','0')]
            state['stages'][-1]['passedTests']=passed
        print(name+' exit '+str(code),flush=True);check()
    try:
        stage('unit-tests',['/usr/bin/cargo','test','--offline','--locked','--lib','--target','x86_64-unknown-linux-gnu','--jobs','4',
            '--target-dir',root/'test-target','--manifest-path',CRATE/'Cargo.toml','frontier_scale::tests','--','--test-threads=1'],300)
        stage('candidate-build',['/usr/bin/python3',BUILD_ADAPTER,'--crate',CRATE,'--mode','generic','--bin','rook2','--jobs','4','--output',root/'candidate-build'],300)
        receipt=read(root/'candidate-build/receipt.json');shutil.copy2(receipt['binary_output']['path'],root/'rook2-candidate')
        admit_build(root/'candidate-build',root/'rook2-candidate',CRATE,prepared['candidateSource'])
        stage('observe',['/usr/bin/python3',HERE/'pipeline.py','--preparation',prepared_path,'--output',root,'--observe-only'],200)
        stage('audit',['/usr/bin/python3',HERE/'reconcile.py',root,'--during-pipeline'],60)
        assert read(root/'audit-before-restore.json')['complete'];state.update(complete=True,active=None)
    except BaseException as error:state['failure']=repr(error);raise
    finally:
        try:
            house['restored']=placement.restore();house['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
        except BaseException as error:house['failure']=repr(error);state.update(complete=False,failure=repr(error));raise
        finally:
            house['endedMonotonicNs']=time.monotonic_ns();write(root/'housekeeping.json',house)
            state['endedMonotonicNs']=time.monotonic_ns()
            if state['endedMonotonicNs']>=state['pipelineDeadlineMonotonicNs']:state.update(complete=False,failure='original900s deadline')
            write(root/'pipeline.json',state)
    assert state['complete'] and state['failure'] is None
    from reconcile import audit_run
    terminal=audit_run(root)
    write(root/'reconciled.json',terminal)
    assert terminal['complete']
    print({'complete':True,'counts':terminal['counts'],'pairComplete':not terminal['censored']},flush=True)


if __name__=='__main__':main()
