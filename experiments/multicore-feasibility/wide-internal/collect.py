#!/usr/bin/env python3
"""Fixed three-case capture, or one externally frozen 16-life architecture fixture."""
import argparse,os,resource,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,ROOT,admit,baseline,snapshot,read,write,sha
from housekeeping import Placement
SPEC=Path('/home/legolas/king-spec/conformance/profiling/workloads.json')
CASES=['profile-35','profile-08','profile-43']
def policy():
    p=read(HERE/'policy.json');assert p['schema']=='rook2-wide-internal-policy-v1' and p['maxDepth']==8 and p['tasks']==7;assert len(p['schedule'])==16;return p

def inputs():
    result={};workloads=read(SPEC)['cases']
    for case in CASES:
        path=HERE/'inputs'/(case+'.txt');actual=dict(line.split('=',1) for line in path.read_text().splitlines() if line and not line.startswith('#'));w=next(c for c in workloads if c['id']==case);p=w['personality']['parameters'];assert w['position']['initial']=='standard-start' and p['rnd']==0
        own=['myp','myn','myb','myr','myq','myk','mycc','mymob','myks','mypp','mypw'];opp=['opp','opn','opb','opr','opq','opk','opcc','opmob','opks','oppp','oppw'];assert actual==dict(case=case,fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',moves=' '.join(w['position']['moves']),own=','.join(str(p[k]) for k in own),opponent=','.join(str(p[k]) for k in opp),evaluation=','.join(str(p[k]) for k in ['avd','cfd','sop']),search=','.join(str(p[k]) for k in ['sel','md','tts','ana']),randomness='0');result[case]=path
    return result

def fixture_fields(path):
    rows=path.read_text().splitlines();assert len(rows)==5;d=dict(x.split('=',1) for x in rows);assert len(d)==5 and set(d)=={'schema','case','horizon','parent_ordinal','binding_hex'};assert d['schema']=='rook2-wide-fixture-v1' and d['case'] in CASES and d['horizon']=='8';assert int(d['parent_ordinal'])>0;bytes.fromhex(d['binding_hex']).decode('utf-8');return d

def main():
    def interrupted(sig,frame):raise InterruptedError('external signal '+str(sig))
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--preparation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',choices=['capture','compare'],required=True);p.add_argument('--fixture',type=Path);p.add_argument('--capture-root',type=Path);a=p.parse_args();out=a.output.resolve();receipt=admit(a.build.resolve());chosen=policy();materialized=inputs();prep=read(a.preparation);assert prep['complete'] and prep['sourceBefore']==prep['sourceAfter']==receipt['sourceBefore']
    if a.mode=='capture':
        assert a.fixture is None and a.capture_root is None;schedule=[dict(case=c,threads=1,repeat=0,warmup=False) for c in CASES];limits=dict(chosen['limits'],**{'streamSeconds':chosen['captureLimits']['streamSeconds'],'reportBytes':chosen['captureLimits']['reportBytes']});fixture=None
    else:
        assert a.fixture is not None and a.capture_root is not None;fixture=fixture_fields(a.fixture.resolve());schedule=[dict(case=fixture['case'],**step) for step in chosen['schedule']];limits=chosen['limits']
    out.mkdir();paths=[*HERE.glob('*.py'),HERE/'policy.json',Path('/usr/bin/python3'),SPEC,a.build.resolve()/'receipt.json',Path(receipt['binary']),a.preparation.resolve(),*materialized.values()]
    if fixture is not None:paths+=[a.fixture.resolve(),a.capture_root.resolve()/'plan.json',a.capture_root.resolve()/'result.json',a.fixture.resolve().with_name('fixture-selection.json'),a.fixture.resolve().with_name('fixture-freeze.json')]
    paths += [Path(x) for x in receipt['baselineBefore']['protectedArtifacts']]
    plan=dict(schema='rook2-wide-collection-v1',mode=a.mode,build=str(a.build.resolve()),preparation=str(a.preparation.resolve()),binary=receipt['binary'],binarySha256=receipt['binarySha256'],sourcePins=receipt['sourceBefore'],baseline=receipt['baselineBefore'],policy=chosen,policyPath=str(HERE/'policy.json'),policySha256=sha(HERE/'policy.json'),schedule=schedule,fixture=fixture,fixturePath=str(a.fixture.resolve()) if a.fixture else None,captureRoot=str(a.capture_root.resolve()) if a.capture_root else None,fixtureFreezePath=str(a.fixture.resolve().with_name('fixture-freeze.json')) if a.fixture else None,inputSha256={str(f.resolve()):sha(f) for f in paths},limits=limits,scope=chosen['scope']);write(out/'plan.json',plan)
    state=dict(schema='rook2-wide-collection-result-v1',mode=a.mode,complete=False,failure=None,runs=[],startMonotonicNs=time.monotonic_ns());write(out/'result.json',state);deadline=time.monotonic()+limits['streamSeconds'];placement=Placement();affinity=sorted(os.sched_getaffinity(0));env=dict(os.environ,PATH='/usr/bin:/bin')
    for k in list(env):
        if k.startswith('ROOK2_') or k=='LLVM_PROFILE_FILE':env.pop(k,None)
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(limits['addressSpaceBytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(limits['reportBytes'],)*2)
    def verify():
        assert baseline()==plan['baseline'] and snapshot(Path(receipt['crate']))==plan['sourcePins']
        for f,h in plan['inputSha256'].items():assert sha(f)==h,f
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for i,step in enumerate(schedule):
            verify();d=out/f'{i:02d}-{step["case"]}-t{step["threads"]}-r{step["repeat"]}';d.mkdir();cpus=chosen['runtimeHousekeepingCpusAt8'] if step['threads']==8 else chosen['runtimeHousekeepingCpus'];write(d/'housekeeping.json',placement.apply(cpus))
            args=['--input',str(materialized[step['case']]),'--threads',str(step['threads']),'--max-depth','8']+(['--capture'] if a.mode=='capture' else ['--fixture',str(a.fixture.resolve())]);argv=['/usr/bin/python3',str(HERE/'account.py'),'--engine',receipt['binary'],'--record',str(d/'native.json'),*args];write(d/'launch.json',dict(argv=argv,nativeArgv=[receipt['binary'],*args],step=step,policySha256=plan['policySha256']));started=time.monotonic_ns();code=None;cleanup=None
            with (d/'stdout').open('xb') as stdout,(d/'stderr').open('xb') as stderr:
                child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env,start_new_session=True,preexec_fn=limit)
                try:
                    remain=min(limits['perLifeSeconds'],deadline-time.monotonic());assert remain>0;code=child.wait(timeout=remain)
                except BaseException:
                    cleanup='external deadline/interruption'
                    try:os.killpg(child.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                    try:code=child.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
                    raise
                finally:write(d/'terminal.json',dict(pid=child.pid,exit=code,cleanup=cleanup,startMonotonicNs=started,endMonotonicNs=time.monotonic_ns()))
            assert code==0 and cleanup is None;assert (d/'stderr').stat().st_size==0;native=read(d/'native.json');report=read(d/'stdout');assert native['failure'] is None and native['native_exit_code']==0
            if a.mode=='capture':assert report['schema']==chosen['captureSchema']
            else:assert report['schema']==chosen['reportSchema'] and report['threads']==step['threads'] and report['oracle_match'] and not report['unsafe_validation'] and report['fatal_reason'] is None and report['error'] is None and report['fixture_bound'] and report['completed_depth']==report['horizon']==8
            row=dict(**step,directory=str(d),nativePid=native['native_pid'],supervisorPid=child.pid,wholeCpuSeconds=native['total_cpu_s'],rssKiB=native['maxrss_linux_kib'],nativeWallNs=native['wall_ns'],sha256={n:sha(d/n) for n in ['launch.json','terminal.json','native.json','stdout','stderr','housekeeping.json']});state['runs'].append(row);write(out/'result.json',state);print(f'{a.mode} completed {i+1}/{len(schedule)} {step["case"]} threads{step["threads"]}',flush=True)
        verify();state.update(complete=True,endMonotonicNs=time.monotonic_ns());write(out/'result.json',state)
    except BaseException as error:state.update(failure=repr(error),endMonotonicNs=time.monotonic_ns());write(out/'result.json',state);raise
    finally:write(out/'housekeeping-restore.json',placement.restore());os.sched_setaffinity(0,set(affinity));(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
if __name__=='__main__':main()
