#!/usr/bin/env python3
"""Fresh focused/dual-build/depth2-audit preparation; stop before depth8 timing."""
import argparse
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode=True
from common import (HERE,ROOT,DEFAULT_CRATE,FEATURE,BINARY,HELPERS,CASES,baseline,
    code_paths,input_records,prepare_inputs,preparation,prepared_run,admit_build,
    read,sha,write,run_lifetime,stop_owned)
from build import environment


def main():
    def interrupted(signum,_frame):raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]:signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--stage',choices=['prepare','collect'],default='prepare')
    args=parser.parse_args();prepared_path=args.preparation.resolve();out=args.output.resolve()
    prepared=preparation(prepared_path);assert set(os.sched_getaffinity(0))==HELPERS
    if args.stage=='prepare':
        out.mkdir();inputs=prepare_inputs(out/'inputs');start=time.monotonic_ns()
        state=dict(schema='rook2-replicated-control-pipeline-v1',complete=False,prepared=False,collected=False,
            failure=None,active=None,stages=[],preparation=str(prepared_path),preparationSha256=sha(prepared_path),
            sourcePreparation=prepared,inputs=inputs,protectedArtifacts=baseline(),
            pipelineStartMonotonicNs=start,pipelineDeadlineMonotonicNs=start+3600*10**9,
            parentQuietAnnouncementRequired=True)
    else:
        state=read(out/'pipeline.json')
        assert state['schema']=='rook2-replicated-control-pipeline-v1' and state['prepared'] and not state['collected']
        assert state['failure'] is None and state['preparationSha256']==sha(prepared_path)
        assert state['sourcePreparation']==prepared
        prepared_run(out/'prepared-run.json',prepared_path,prepared)
        state['complete']=False
    write(out/'pipeline.json',state)
    def check():
        assert preparation(prepared_path)==prepared and sha(prepared_path)==state['preparationSha256']
        assert input_records(out/'inputs')==state['inputs'] and baseline()==state['protectedArtifacts']
        assert time.monotonic_ns()<state['pipelineDeadlineMonotonicNs'],'original pipeline deadline'
    def stage(name,command,cap,cwd=ROOT,tests=None):
        check();state['active']=name;write(out/'pipeline.json',state)
        started=time.monotonic_ns();deadline=min(state['pipelineDeadlineMonotonicNs'],started+cap*10**9)
        with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen([str(value) for value in command],cwd=cwd,env=environment(),stdout=stdout,stderr=stderr,start_new_session=True)
            try:
                remaining=(deadline-time.monotonic_ns())/1e9;assert remaining>0
                code=child.wait(timeout=remaining);assert time.monotonic_ns()<deadline
            except BaseException:stop_owned(child);raise
        ended=time.monotonic_ns()
        row=dict(stage=name,argv=[str(value) for value in command],cwd=str(cwd),pid=child.pid,exit=code,
            startedMonotonicNs=started,endedMonotonicNs=ended,deadlineMonotonicNs=deadline,elapsedNs=ended-started,
            stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr')))
        state['stages'].append(row);write(out/'pipeline.json',state);assert code==0,(name,code)
        if tests:
            text=(out/(name+'.stdout')).read_text()
            names=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
            assert len(names)==len(set(names))==tests['expectedPassed']
            assert re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)==[(str(len(names)),'0','0')]
            row['passedTests']=names;write(out/'pipeline.json',state)
        check();print(name+' exit '+str(code),flush=True)
    try:
        if args.stage=='prepare':
            for index,tests in enumerate(prepared['focused']):
                command=['/usr/bin/cargo','test','--offline','--locked',*tests['target'],'--features',FEATURE,
                    '--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(out/'test-target'),
                    tests['selector'],'--','--test-threads=1']
                if tests.get('exact',False):command.append('--exact')
                if tests.get('ignored',False):command.append('--ignored')
                stage(f'tests-{index:02d}-{tests["name"]}',command,tests.get('limitSeconds',300),DEFAULT_CRATE,tests)
            for variant in ['preserved','new']:
                stage(variant+'-build',['/usr/bin/python3',HERE/'build.py','--variant',variant,'--output',out/(variant+'-build')],330)
            builds={variant:admit_build(out/(variant+'-build'),variant,prepared) for variant in ['preserved','new']}
            images={variant:dict(path=value['binary'],sha256=value['binarySha256']) for variant,value in builds.items()}
            files=code_paths()+[prepared_path]+[Path(row['path']) for row in state['inputs'].values()]
            for field in ['inputSha256','reusedEvidenceSha256']:files += [Path(path) for path in prepared[field]]
            files += [Path(path) for path in baseline()]
            for variant,value in builds.items():
                directory=out/(variant+'-build');files += [directory/name for name in ['receipt.json','stdout','stderr']]
                files += [Path(value['binary'])]+[Path(path) for path in value['toolsBefore']]
                files += [directory/'source-before'/name for name in value['sourceBefore']]
            files += [out/(row['stage']+'.'+suffix) for row in state['stages'] for suffix in ['stdout','stderr']]
            hashes={str(path):sha(path) for path in sorted(set(files))}
            record=dict(schema='rook2-replicated-control-prepared-run-v1',complete=False,sourcePreparation=str(prepared_path),
                sourcePreparationSha256=sha(prepared_path),sourcePreparationValue=prepared,images=images,
                inputs=state['inputs'],stages=list(state['stages']),inputSha256=hashes,audits=[],
                pipelineStartMonotonicNs=state['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=state['pipelineDeadlineMonotonicNs'])
            (out/'audits').mkdir();write(out/'audit-progress.json',record)
            replica=dict(path=images['new']['path'],mode='replica',budget=3)
            state['active']='depth2-audits';write(out/'pipeline.json',state)
            for case in CASES:
                check()
                record['audits'].append(run_lifetime(out/'audits'/case,dict(case=case,variant='newreplica3-audit'),
                    Path(replica['path']),replica,state['pipelineDeadlineMonotonicNs']/1e9,hashes,
                    Path(state['inputs'][case]['path']),2,True))
                write(out/'audit-progress.json',record)
            check();record.update(complete=True,preparedMonotonicNs=time.monotonic_ns())
            write(out/'prepared-run.json',record);prepared_run(out/'prepared-run.json',prepared_path,prepared)
            state.update(prepared=True,complete=True,active=None)
        else:
            stage('collection',['/usr/bin/python3',HERE/'collect.py','--preparation',prepared_path,
                '--prepared-run',out/'prepared-run.json','--output',out/'timing'],1900)
            stage('reconcile',['/usr/bin/python3',HERE/'reconcile.py',out/'timing'],120)
            assert read(out/'timing/reconciled.json')['complete']
            state.update(collected=True,complete=True,active=None)
        check();write(out/'pipeline.json',state)
    except BaseException as error:
        state.update(complete=False,failure=repr(error));write(out/'pipeline.json',state);raise
    print('prepared matched images and three depth2 audits; stopped before timing' if args.stage=='prepare' else 'completed60 fixed-depth lives and saved-raw reconciliation',flush=True)


if __name__=='__main__':main()
