#!/usr/bin/env python3
"""One fixed serial pure-salvage census on the existing frozen wide35 fixture."""
import argparse,os,resource,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
from build import HERE,ROOT,admit,baseline,snapshot,read,write,sha
from housekeeping import Placement
SPEC=Path('/home/legolas/king-spec/conformance/profiling/workloads.json')
def fixture_fields(path):
    rows=path.read_text().splitlines();assert len(rows)==5;v=dict(x.split('=',1) for x in rows);assert len(v)==5 and set(v)=={'schema','case','horizon','parent_ordinal','binding_hex'};assert v['schema']=='rook2-wide-fixture-v1' and v['case']=='profile-35' and v['horizon']=='8' and int(v['parent_ordinal'])==428548;bytes.fromhex(v['binding_hex']).decode('utf-8');return dict(v,horizon=8,parent_ordinal=int(v['parent_ordinal']))
def materialized_input():
    path=HERE/'inputs/profile-35.txt';actual=dict(x.split('=',1) for x in path.read_text().splitlines() if x);case=next(x for x in read(SPEC)['cases'] if x['id']=='profile-35');p=case['personality']['parameters'];assert case['position']['initial']=='standard-start' and p['rnd']==0
    own=['myp','myn','myb','myr','myq','myk','mycc','mymob','myks','mypp','mypw'];opp=['opp','opn','opb','opr','opq','opk','opcc','opmob','opks','oppp','oppw'];assert actual==dict(case='profile-35',fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',moves=' '.join(case['position']['moves']),own=','.join(str(p[k]) for k in own),opponent=','.join(str(p[k]) for k in opp),evaluation=','.join(str(p[k]) for k in ['avd','cfd','sop']),search=','.join(str(p[k]) for k in ['sel','md','tts','ana']),randomness='0');return path

def main():
    def interrupted(sig,frame):raise InterruptedError('external signal '+str(sig))
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--preparation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();receipt=admit(a.build.resolve());policy=read(HERE/'policy.json');assert policy['schema']=='rook2-coarse-pure-policy-v1';fixture=Path(policy['fixture']);identity=fixture_fields(fixture);input_path=materialized_input();prep=read(a.preparation);assert prep['complete'] and prep['sourceBefore']==prep['sourceAfter']==receipt['sourceBefore'];out.mkdir()
    paths=[*HERE.glob('*.py'),HERE/'policy.json',Path('/usr/bin/python3'),SPEC,a.build.resolve()/'receipt.json',Path(receipt['binary']),a.preparation.resolve(),input_path,fixture,Path(policy['fixtureSelection']),Path(policy['fixtureFreeze'])];paths+=[Path(p) for p in receipt['baselineBefore']['protectedArtifacts']];step=dict(case='profile-35',threads=1,repeat=1,warmup=False)
    plan=dict(schema='rook2-coarse-pure-collection-v1',build=str(a.build.resolve()),preparation=str(a.preparation.resolve()),binary=receipt['binary'],binarySha256=receipt['binarySha256'],sourcePins=receipt['sourceBefore'],baseline=receipt['baselineBefore'],policy=policy,policyPath=str(HERE/'policy.json'),policySha256=sha(HERE/'policy.json'),fixture=identity,fixturePath=str(fixture),fixtureSelectionPath=policy['fixtureSelection'],fixtureFreezePath=policy['fixtureFreeze'],schedule=[step],inputSha256={str(p.resolve()):sha(p) for p in paths},limits=policy['limits'],scope=policy['scope']);write(out/'plan.json',plan)
    state=dict(schema='rook2-coarse-pure-collection-result-v1',complete=False,failure=None,runs=[],startMonotonicNs=time.monotonic_ns());write(out/'result.json',state);placement=Placement();affinity=sorted(os.sched_getaffinity(0));env=dict(os.environ,PATH='/usr/bin:/bin')
    for k in list(env):
        if k.startswith('ROOK2_') or k=='LLVM_PROFILE_FILE':env.pop(k,None)
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(policy['limits']['addressSpaceBytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(policy['limits']['reportBytes'],)*2)
    def verify():
        assert baseline()==plan['baseline'] and snapshot(Path(receipt['crate']))==plan['sourcePins']
        for p,h in plan['inputSha256'].items():assert sha(p)==h,p
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        verify();d=out/'00-profile-35-t1-r1';d.mkdir();write(d/'housekeeping.json',placement.apply(policy['housekeepingCpus']));args=['--input',str(input_path),'--fixture',str(fixture)];argv=['/usr/bin/python3',str(HERE/'account.py'),'--engine',receipt['binary'],'--record',str(d/'native.json'),*args];write(d/'launch.json',dict(argv=argv,nativeArgv=[receipt['binary'],*args],step=step,policySha256=plan['policySha256']));started=time.monotonic_ns();code=None;cleanup=None
        with (d/'stdout').open('xb') as stdout,(d/'stderr').open('xb') as stderr:
            child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env,start_new_session=True,preexec_fn=limits)
            try:code=child.wait(timeout=policy['limits']['perLifeSeconds'])
            except BaseException:
                cleanup='external deadline/interruption'
                try:os.killpg(child.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:code=child.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
                raise
            finally:write(d/'terminal.json',dict(pid=child.pid,exit=code,cleanup=cleanup,startMonotonicNs=started,endMonotonicNs=time.monotonic_ns()))
        assert code==0 and cleanup is None and (d/'stderr').stat().st_size==0;native=read(d/'native.json');report=read(d/'stdout');assert native['failure'] is None and native['native_exit_code']==0;assert report['schema']==policy['reportSchema'] and report['serial_threads']==1 and report['fixture_bound'] and report['canonical_fidelity'] and report['producer_native_fidelity'];assert report['canonical_nodes']==report['second_canonical_nodes'] and report['canonical_relations']==report['second_canonical_relations']
        row=dict(**step,directory=str(d),nativePid=native['native_pid'],supervisorPid=child.pid,wholeCpuSeconds=native['total_cpu_s'],rssKiB=native['maxrss_linux_kib'],nativeWallNs=native['wall_ns'],sha256={p:sha(d/p) for p in ['launch.json','terminal.json','native.json','stdout','stderr','housekeeping.json']});state['runs'].append(row);verify();state.update(complete=True,endMonotonicNs=time.monotonic_ns());write(out/'result.json',state);print('completed one serial coarse-pure census',flush=True)
    except BaseException as error:state.update(failure=repr(error),endMonotonicNs=time.monotonic_ns());write(out/'result.json',state);raise
    finally:write(out/'housekeeping-restore.json',placement.restore());os.sched_setaffinity(0,set(affinity));(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
if __name__=='__main__':main()
