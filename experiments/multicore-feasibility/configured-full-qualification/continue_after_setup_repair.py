#!/usr/bin/env python3
"""Continue only unstarted checks after the preserved external-test compile error."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from run import HERE, ROOT, HELPERS, IMAGE, SHA, read, write, sha


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('raw',type=Path)
    args=parser.parse_args();raw=args.raw.resolve()
    initial=read(raw/'pipeline.json');repair=read(raw/'observer-setup-repair/repair.json')
    assert not initial['complete'] and initial['failure']=="AssertionError(('observer-build', 1))"
    assert [x['stage'] for x in initial['stages']]==['exact-configuration','mandatory','observer-build']
    assert [x['exit'] for x in initial['stages']]==[0,0,1]
    assert sha(raw/'pipeline.json')==repair['initialPipelineSha256']
    assert set(os.sched_getaffinity(0))==HELPERS
    source=initial['source'];testsource=HERE/'threaded_observer.rs'
    assert sha(testsource)==repair['afterSha256']
    archived=raw/'observer-setup-repair/threaded_observer-before.rs'
    assert sha(archived)==repair['beforeSha256']==initial['pins'][str(testsource)]
    for row in initial['stages']:
        for stream in ['stdout','stderr']:assert sha(raw/(row['stage']+'.'+stream))==row[stream+'Sha256']
    assert read(raw/'mandatory/lane-outcome.json')['complete']
    assert read(raw/'mandatory/independent-reconciliation.json')['pass']
    # Reserve60s before the captured mandatory start for the completed0.77s
    # configuration prefix and initial preservation checks. The conservative
    # original4200s allowance includes compile-repair gaps, not a fresh4200s.
    conservative_start=read(raw/'mandatory/lane-clock.json')['startMonotonicNs']-60*10**9
    deadline=(conservative_start+4200*10**9)/1e9
    assert time.monotonic()<deadline
    state=dict(schema='rook2-qualification-helper-repair-continuation-v1',complete=False,failure=None,
        initialPipelineSha256=sha(raw/'pipeline.json'),repairSha256=sha(raw/'observer-setup-repair/repair.json'),
        conservativeStartMonotonicNs=conservative_start,originalResourceSeconds=4200,
        stages=[],imageSha256=SHA,sourceCommit=initial['sourceCommit'])
    assert not (raw/'continuation.json').exists();write(raw/'continuation.json',state)
    binding=read(raw/'observer/binding.json');rlib=Path(binding['library'])
    assert sha(rlib)==binding['sha256']
    binding2=dict(originalBindingSha256=sha(raw/'observer/binding.json'),library=str(rlib),
        librarySha256=sha(rlib),testSourceSha256=sha(testsource),
        scope='Public successful Outcome.stats retained; stopped path compares public Work/EvalStats/trace without private-field access')
    write(raw/'observer/repaired-binding.json',binding2)
    env=dict(os.environ,PATH='/usr/bin:/bin',PYTHONDONTWRITEBYTECODE='1')

    def check():
        assert sha(IMAGE)==SHA and all(sha(ROOT/n)==h for n,h in source.items())
        for p,h in initial['pins'].items():
            if p==str(testsource):assert sha(p)==repair['afterSha256']
            else:assert sha(p)==h,p
        assert sha(rlib)==binding['sha256']

    def stage(name,argv,cap):
        check();state['active']=name;write(raw/'continuation.json',state)
        begin=time.monotonic_ns();assert time.monotonic()<deadline
        with (raw/(name+'.stdout')).open('xb') as stdout,(raw/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            cleanup=False
            try:code=child.wait(timeout=min(cap,max(.01,deadline-time.monotonic())))
            except BaseException:
                cleanup=True
                try:os.killpg(child.pid,signal.SIGINT)
                except ProcessLookupError:pass
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    try:os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    child.wait()
                raise
            finally:
                state['stages'].append(dict(stage=name,argv=argv,pid=child.pid,exit=child.returncode,
                    cleanup=cleanup,elapsedNs=time.monotonic_ns()-begin,
                    stdoutSha256=sha(raw/(name+'.stdout')),stderrSha256=sha(raw/(name+'.stderr'))))
                write(raw/'continuation.json',state)
        print(name,code,flush=True);assert code==0,(name,code);check()

    try:
        executable=raw/'observer/threaded-observer-corrected'
        stage('observer-build-corrected',['/usr/bin/rustc','--edition=2021','--test',
            '--crate-name','rook2_threaded_observer','-C','target-cpu=x86-64',str(testsource),
            '--extern','rook2='+str(rlib),'-L','dependency='+str(rlib.parent),'-o',str(executable)],120)
        stage('threaded-observer',[str(executable),'--test-threads=1'],120)
        state['observer']=dict(executable=str(executable),sha256=sha(executable),
            binding=str(raw/'observer/repaired-binding.json'),bindingSha256=sha(raw/'observer/repaired-binding.json'))
        for lane in read(raw/'ordinary/setup.json')['lanes']:
            stage('ordinary-mode'+str(lane['threads']),lane['run'],1250 if lane['threads']==2 else 350)
        check();state.update(complete=True,active=None,resourceElapsedNs=time.monotonic_ns()-conservative_start)
        assert state['resourceElapsedNs']<4200*10**9
        write(raw/'continuation.json',state)
        print('residual qualification complete; no completed native request repeated',flush=True)
    except BaseException as error:
        state.update(failure=repr(error),resourceElapsedNs=time.monotonic_ns()-conservative_start)
        write(raw/'continuation.json',state);raise


if __name__=='__main__':main()
