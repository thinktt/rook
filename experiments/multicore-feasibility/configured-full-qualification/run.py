#!/usr/bin/env python3
"""One serial local qualification lane; source/image immutable, stop on mismatch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13}
IMAGE=Path('/home/legolas/rook2-experiments/configured-full-20261024-01/production/rook2-pgo')
SHA='8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,d):
    q=p.with_suffix('.pending');q.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n');q.replace(p)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw',type=Path)
    a=p.parse_args();raw=a.raw.resolve()
    assert raw.is_dir() and not (raw/'pipeline.json').exists()
    assert set(os.sched_getaffinity(0))==HELPERS and sha(IMAGE)==SHA
    ordinary=read(raw/'ordinary/setup.json');mandatory=read(raw/'mandatory/plan.json')
    assert ordinary['imageSha256']==mandatory['ordinarySha256']==SHA
    source=mandatory['engineSource']
    assert all(sha(ROOT/n)==h for n,h in source.items())
    pins={str(p):sha(p) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    pins.update({str(raw/n):sha(raw/n) for n in ['ordinary/setup.json','ordinary/mode2/plan.json',
                'ordinary/mode1/plan.json','mandatory/plan.json','mandatory/selection.json']})
    state=dict(schema='rook2-configured-full-qualification-pipeline-v1',complete=False,failure=None,
        sourceCommit='66f35e440b2180d4d22c2bcd0e5a8c99c0f1185d',image=str(IMAGE),imageSha256=SHA,
        source=source,pins=pins,stages=[],aggregateSeconds=4200,performanceMeasurement=False)
    write(raw/'pipeline.json',state)
    start=time.monotonic_ns();deadline=time.monotonic()+4200
    env=dict(os.environ,PATH='/usr/bin:/bin',PYTHONDONTWRITEBYTECODE='1')
    assert not any(env.get(k) for k in ['LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH','NODE_OPTIONS'])

    def check():
        assert sha(IMAGE)==SHA
        assert all(sha(ROOT/n)==h for n,h in source.items())
        assert all(sha(p)==h for p,h in pins.items())

    def stage(name,argv,cap):
        check();assert time.monotonic()<deadline
        state['active']=name;write(raw/'pipeline.json',state)
        begin=time.monotonic_ns()
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
                row=dict(stage=name,argv=argv,pid=child.pid,exit=child.returncode,cleanup=cleanup,
                    elapsedNs=time.monotonic_ns()-begin,stdoutSha256=sha(raw/(name+'.stdout')),
                    stderrSha256=sha(raw/(name+'.stderr')))
                state['stages'].append(row);write(raw/'pipeline.json',state)
        print(name,code,flush=True);assert code==0,(name,code)
        check()

    try:
        stage('exact-configuration',ordinary['configurationVerification'],450)
        stage('mandatory',['/usr/bin/python3',str(HERE/'mandatory/run_lane.py'),str(raw/'mandatory')],1850)
        assert read(raw/'mandatory/lane-outcome.json')['complete']
        # Use the normal (non-cfg(test)) library produced by the same-source
        # diagnostic test compilation; retain its literal Cargo artifact record.
        records=[]
        for line in (raw/'mandatory/diagnostic_tests/stdout').read_text().splitlines():
            try:row=json.loads(line)
            except json.JSONDecodeError:continue
            if row.get('reason')=='compiler-artifact' and row['target']['name']=='rook2' and 'lib' in row['target']['kind']:
                for filename in row['filenames']:
                    if filename.endswith('.rlib'):records.append((row,Path(filename)))
        assert len(records)==1,records
        artifact,rlib=records[0];assert artifact['target']['src_path']==str(raw/'mandatory/source/src/lib.rs')
        observer=raw/'observer';observer.mkdir()
        binding=dict(library=str(rlib),sha256=sha(rlib),cargoArtifact=artifact,
            frozenSource=source,sourceCommit=state['sourceCommit'],testSourceSha256=sha(HERE/'threaded_observer.rs'))
        write(observer/'binding.json',binding)
        test=observer/'threaded-observer'
        stage('observer-build',['/usr/bin/rustc','--edition=2021','--test',
            '--crate-name','rook2_threaded_observer','-C','target-cpu=x86-64',
            str(HERE/'threaded_observer.rs'),'--extern','rook2='+str(rlib),
            '-L','dependency='+str(rlib.parent),'-o',str(test)],120)
        assert sha(rlib)==binding['sha256']
        stage('threaded-observer',[str(test),'--test-threads=1'],120)
        state['observer']=dict(binding=str(observer/'binding.json'),sha256=sha(observer/'binding.json'),
            executable=str(test),executableSha256=sha(test),
            scope='Enabled Q observer,6 source examples x normal/stopped x configured1/2; public API and same-source normal library, not ordinary-PGO instrumentation')
        for lane in ordinary['lanes']:
            stage('ordinary-mode'+str(lane['threads']),lane['run'],1250 if lane['threads']==2 else 350)
        check();state.update(complete=True,active=None,elapsedNs=time.monotonic_ns()-start)
        write(raw/'pipeline.json',state)
        print('selected local qualification stages complete; no adoption/external action',flush=True)
    except BaseException as error:
        state.update(failure=repr(error),elapsedNs=time.monotonic_ns()-start)
        write(raw/'pipeline.json',state);raise


if __name__=='__main__':main()
