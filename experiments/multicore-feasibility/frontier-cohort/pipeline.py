#!/usr/bin/env python3
"""Six new controls, one build, capture, cold expansion, observation and raw audit."""
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
from common import (HERE,ROOT,CRATE,HELPERS,BUILD_ADAPTER,PIPELINE_SECONDS,OPTIONS,TESTS,REPORT,COHORT_REPORT,cohort_env,step,
    admit_build,audit,baseline,code_paths,housekeeping,image_layout,preparation,read,run_lifetime,sha,write)


def observe(root,prepared_path,mode):
    prepared=preparation(prepared_path);state=read(root/'pipeline.json')
    assert mode in ['capture','observe'] and state['active']==mode and state['failure'] is None and not state['complete']
    expected=['unit-tests','candidate-build']+(['capture','expand'] if mode=='observe' else [])
    assert [row['stage'] for row in state['stages']]==expected
    assert state['preparation']==str(prepared_path) and state['preparationSha256']==sha(prepared_path)
    assert state['sourcePreparation']==prepared and time.monotonic_ns()<state['pipelineDeadlineMonotonicNs']
    image=root/'rook2-candidate';receipt,_=admit_build(root/'candidate-build',image,CRATE,prepared['candidateSource'])
    paths=code_paths()+[prepared_path,image,root/'candidate-build/receipt.json',root/'candidate-build/build.stderr']
    paths += [Path(path) for key in ['inputSha256','reusedEvidenceSha256','protectedArtifacts'] for path in prepared[key]]
    paths += [root/'candidate-build/source-before'/name for name in (receipt['source_sha256_before']|receipt['tool_sha256_before'])]
    if mode=='observe':paths += [root/'capture.bin',root/'pool.bin',root/'expand'/COHORT_REPORT]
    plan=dict(schema='rook2-frontier-cohort-observation-v1',case='profile-35',step=step(mode),mode=mode,
        engine=image_layout(image),options=OPTIONS,budget=3,source=prepared['candidateSource'],
        sourcePreparation=str(prepared_path),preparationSha256=sha(prepared_path),
        pipelineStartMonotonicNs=state['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=state['pipelineDeadlineMonotonicNs'],
        inputSha256={str(path):sha(path) for path in sorted(set(paths))},protectedArtifacts=baseline())
    write(root/(mode+'-plan.json'),plan)
    row=run_lifetime(root/mode,step(mode),image,dict(budget=3,options=OPTIONS,report=False),
        state['pipelineDeadlineMonotonicNs']/1e9,plan['inputSha256'])
    row['reports']={}
    for name in [REPORT,COHORT_REPORT]:
        path=root/mode/name
        assert path.is_file() and not path.is_symlink() and 0<path.stat().st_size<=65536
        row['reports'][name]=dict(path=str(path),sha256=sha(path))
    assert row['orderedPosts']==13 and row['replayRunnerExit']==0
    assert all(sha(path)==digest for path,digest in plan['inputSha256'].items())
    write(root/mode/'result.json',row)
    # Semantic mismatch halts before any subsequent selected request.
    from reconcile import qualify_search,cohort_summary,read_binary_footer
    _,row,scale=qualify_search(root,mode,prepared,plan)
    summary=cohort_summary(root/mode/COHORT_REPORT,mode)
    raw=root/('capture.bin' if mode=='capture' else 'ledger.bin')
    read_binary_footer(raw,mode,summary,scale)
    assert summary['boundariesNs'][3]<=row['searchWallNs']
    print(mode+' original35 replay joined and qualified',flush=True)


def main():
    def interrupted(signum,_frame):raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]:signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--search-mode',choices=['capture','observe']);args=parser.parse_args()
    prepared_path,root=args.preparation.resolve(),args.output.resolve()
    if args.search_mode:observe(root,prepared_path,args.search_mode);return
    prepared=preparation(prepared_path);assert set(os.sched_getaffinity(0))==HELPERS
    root.mkdir();start=time.monotonic_ns()
    state=dict(schema='rook2-frontier-cohort-pipeline-v1',complete=False,failure=None,active=None,stages=[],
        preparation=str(prepared_path),preparationSha256=sha(prepared_path),sourcePreparation=prepared,
        protectedArtifacts=baseline(),pipelineStartMonotonicNs=start,pipelineDeadlineMonotonicNs=start+PIPELINE_SECONDS*10**9)
    placement=housekeeping.Placement();house=dict(applies=[],restored=None,failure=None,helperCpus=sorted(HELPERS))
    env={key:value for key,value in os.environ.items() if not key.startswith(('ROOK2_','CARGO_PROFILE_')) and key not in
        ['LLVM_PROFILE_FILE','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']}
    env.update(PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_INCREMENTAL='0')
    def check():
        assert preparation(prepared_path)==prepared and sha(prepared_path)==state['preparationSha256']
        assert baseline()==state['protectedArtifacts'] and time.monotonic_ns()<state['pipelineDeadlineMonotonicNs']
    def stage(name,command,cap,extra_env=None):
        check();house['applies'].append(placement.apply(HELPERS));state['active']=name;write(root/'pipeline.json',state)
        began=time.monotonic_ns();deadline=min(state['pipelineDeadlineMonotonicNs'],began+cap*10**9)
        with (root/(name+'.stdout')).open('xb') as stdout,(root/(name+'.stderr')).open('xb') as stderr:
            stage_env=dict(env);stage_env.update(extra_env or {})
            child=subprocess.Popen([str(part) for part in command],cwd=ROOT,env=stage_env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True)
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
            stdoutSha256=sha(root/(name+'.stdout')),stderrSha256=sha(root/(name+'.stderr')),extraEnvironment=extra_env or {}))
        write(root/'pipeline.json',state);assert code==0 and ended<deadline,(name,code)
        if name=='unit-tests':
            text=(root/'unit-tests.stdout').read_text()
            passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
            assert sorted(passed)==TESTS and re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)==[('6','0','0')]
            state['stages'][-1]['passedTests']=passed
        print(name+' exit '+str(code),flush=True);check()
    try:
        stage('unit-tests',['/usr/bin/cargo','test','--offline','--locked','--lib','--target','x86_64-unknown-linux-gnu','--jobs','4',
            '--target-dir',root/'test-target','--manifest-path',CRATE/'Cargo.toml','frontier_cohort::tests','--','--test-threads=1'],300)
        stage('candidate-build',['/usr/bin/python3',BUILD_ADAPTER,'--crate',CRATE,'--mode','generic','--bin','rook2','--jobs','4','--output',root/'candidate-build'],300)
        receipt=read(root/'candidate-build/receipt.json');shutil.copy2(receipt['binary_output']['path'],root/'rook2-candidate')
        admit_build(root/'candidate-build',root/'rook2-candidate',CRATE,prepared['candidateSource'])
        stage('capture',['/usr/bin/python3',HERE/'pipeline.py','--preparation',prepared_path,'--output',root,'--search-mode','capture'],200)
        (root/'expand').mkdir()
        stage('expand',[root/'rook2-candidate'],300,cohort_env(root,'expand'))
        assert (root/'expand.stdout').stat().st_size==0
        from reconcile import cohort_summary,read_binary_footer
        summary=cohort_summary(root/'expand'/COHORT_REPORT,'expand')
        read_binary_footer(root/'pool.bin','expand',summary)
        stage('observe',['/usr/bin/python3',HERE/'pipeline.py','--preparation',prepared_path,'--output',root,'--search-mode','observe'],200)
        stage('audit',['/usr/bin/python3',HERE/'reconcile.py',root,'--during-pipeline'],300)
        assert read(root/'audit-before-restore.json')['complete'];state.update(complete=True,active=None)
    except BaseException as error:state['failure']=repr(error);raise
    finally:
        try:
            house['restored']=placement.restore();house['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
        except BaseException as error:house['failure']=repr(error);state.update(complete=False,failure=repr(error));raise
        finally:
            house['endedMonotonicNs']=time.monotonic_ns();write(root/'housekeeping.json',house)
            state['endedMonotonicNs']=time.monotonic_ns()
            if state['endedMonotonicNs']>=state['pipelineDeadlineMonotonicNs']:state.update(complete=False,failure='original1800s deadline')
            write(root/'pipeline.json',state)
    assert state['complete'] and state['failure'] is None
    from reconcile import audit_run
    terminal=audit_run(root)
    write(root/'reconciled.json',terminal)
    assert terminal['complete']
    print({'complete':True,'ceilingNs':terminal['cohort']['generousCeilingNs'],'actualReady':'unknown-no-producer'},flush=True)


if __name__=='__main__':main()
