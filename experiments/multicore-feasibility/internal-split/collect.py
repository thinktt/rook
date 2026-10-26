#!/usr/bin/env python3
"""One fixed 48-life internal-split worker screen; no retries or retuning."""
import argparse,os,resource,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,ROOT,admit,baseline,snapshot,read,write,sha
from housekeeping import Placement
SPEC=Path('/home/legolas/king-spec/conformance/profiling/workloads.json')

def policy():
    p=read(HERE/'policy.json');assert p['schema']=='rook2-internal-split-policy-v1' and p['reportSchema']=='rook2-internal-split-v1';assert p['budgets']==[1,2,4,8] and p['tasks']==7
    assert len(p['schedule'])==48 and p['caps']['batch_estimated_bytes']==2*1024**3
    return p

def inputs():
    workloads=read(SPEC)['cases'];result={}
    for case in ['profile-35','profile-08','profile-43']:
        path=HERE/'inputs'/(case+'.txt');actual=dict(line.split('=',1) for line in path.read_text().splitlines() if line and not line.startswith('#'));w=next(x for x in workloads if x['id']==case);assert w['position']['initial']=='standard-start';p=w['personality']['parameters'];assert p['rnd']==0
        own=['myp','myn','myb','myr','myq','myk','mycc','mymob','myks','mypp','mypw'];opp=['opp','opn','opb','opr','opq','opk','opcc','opmob','opks','oppp','oppw']
        assert actual==dict(case=case,fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',moves=' '.join(w['position']['moves']),own=','.join(str(p[k]) for k in own),opponent=','.join(str(p[k]) for k in opp),evaluation=','.join(str(p[k]) for k in ['avd','cfd','sop']),search=','.join(str(p[k]) for k in ['sel','md','tts','ana']),randomness='0');result[case]=path
    return result

def main():
    def interrupted(signum,frame):raise InterruptedError("external signal "+str(signum))
    signal.signal(signal.SIGTERM,interrupted)
    signal.signal(signal.SIGINT,interrupted)
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--preparation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build=a.build.resolve();out=a.output.resolve();receipt=admit(build);chosen=policy();materialized=inputs();prep=read(a.preparation)
    assert prep['complete'] and prep['sourceBefore']==prep['sourceAfter']==receipt['sourceBefore'];assert prep['focusedTests']>0
    out.mkdir();paths=[*HERE.glob('*.py'),HERE/'policy.json',Path('/usr/bin/python3'),SPEC,build/'receipt.json',Path(receipt['binary']),a.preparation,*materialized.values()]
    for artifact in receipt['baselineBefore']['protectedArtifacts']:paths.append(Path(artifact))
    plan=dict(schema='rook2-internal-split-collection-v1',build=str(build),preparation=str(a.preparation.resolve()),binary=receipt['binary'],binarySha256=receipt['binarySha256'],sourcePins=receipt['sourceBefore'],baseline=receipt['baselineBefore'],policy=chosen,policyPath=str(HERE/'policy.json'),policySha256=sha(HERE/'policy.json'),schedule=chosen['schedule'],inputSha256={str(f.resolve()):sha(f) for f in paths},scope=chosen['scope']);write(out/'plan.json',plan)
    state=dict(schema='rook2-internal-split-collection-result-v1',complete=False,failure=None,runs=[],startMonotonicNs=time.monotonic_ns());write(out/'result.json',state);deadline=time.monotonic()+chosen['limits']['streamSeconds'];placement=Placement();start_affinity=sorted(os.sched_getaffinity(0))
    env=dict(os.environ,PATH='/usr/bin:/bin')
    for k in list(env):
        if k.startswith('ROOK2_') or k=='LLVM_PROFILE_FILE':env.pop(k,None)
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(chosen['limits']['addressSpaceBytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(chosen['limits']['reportBytes'],)*2)
    def verify():
        assert baseline()==plan['baseline'];assert snapshot(Path(receipt['crate']))==plan['sourcePins']
        for f,h in plan['inputSha256'].items():assert sha(f)==h,f
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for i,step in enumerate(plan['schedule']):
            verify();d=out/f'{i:02d}-{step["case"]}-t{step["threads"]}-r{step["repeat"]}';d.mkdir()
            cpus=chosen['runtimeHousekeepingCpusAt8'] if step['threads']==8 else chosen['runtimeHousekeepingCpus'];write(d/'housekeeping.json',placement.apply(cpus))
            args=['--input',str(materialized[step['case']]),'--threads',str(step['threads'])];argv=['/usr/bin/python3',str(HERE/'account.py'),'--engine',receipt['binary'],'--record',str(d/'native.json'),*args]
            write(d/'launch.json',dict(argv=argv,nativeArgv=[receipt['binary'],*args],step=step,policySha256=plan['policySha256']));start=time.monotonic_ns();code=None;cleanup=None
            with (d/'stdout').open('xb') as stdout,(d/'stderr').open('xb') as stderr:
                child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env,start_new_session=True,preexec_fn=limit)
                try:
                    remain=min(chosen['limits']['perLifeSeconds'],deadline-time.monotonic());assert remain>0;code=child.wait(timeout=remain)
                except BaseException:
                    cleanup='external deadline/interruption'
                    try:os.killpg(child.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                    try:code=child.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
                    raise
                finally:write(d/'terminal.json',dict(pid=child.pid,exit=code,cleanup=cleanup,startMonotonicNs=start,endMonotonicNs=time.monotonic_ns()))
            assert code==0 and cleanup is None;assert (d/'stderr').stat().st_size==0
            native=read(d/'native.json');report=read(d/'stdout');assert native['failure'] is None and native['native_exit_code']==0
            assert report['schema']==chosen['reportSchema'] and report['threads']==step['threads'];assert report['oracle_match'] and not report['unsafe_validation'] and report['fatal_reason'] is None and report['error'] is None
            assert report['completed_depth']==6 and report['coordinator_cpu']==14
            assert report['canonical_nodes']==report['oracle_nodes'] and report['canonical_relations']==report['oracle_relations']
            row=dict(**step,directory=str(d),nativePid=native['native_pid'],supervisorPid=child.pid,wholeCpuSeconds=native['total_cpu_s'],rssKiB=native['maxrss_linux_kib'],nativeWallNs=native['wall_ns'],sha256={n:sha(d/n) for n in ['launch.json','terminal.json','native.json','stdout','stderr','housekeeping.json']});state['runs'].append(row);write(out/'result.json',state)
            print(f'completed {i+1}/48 {step["case"]} threads{step["threads"]} repeat{step["repeat"]} selector_miss={report["selector_miss"]}',flush=True)
        verify();assert time.monotonic()<deadline;state.update(complete=True,endMonotonicNs=time.monotonic_ns());write(out/'result.json',state)
    except BaseException as error:state.update(failure=repr(error),endMonotonicNs=time.monotonic_ns());write(out/'result.json',state);raise
    finally:
        write(out/'housekeeping-restore.json',placement.restore());os.sched_setaffinity(0,set(start_affinity));(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
if __name__=='__main__':main()
