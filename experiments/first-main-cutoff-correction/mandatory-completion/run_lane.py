#!/usr/bin/python3
"""One1200s correctness lane from first native build/test through offline closure."""
import ctypes,hashlib,json,os,resource,signal,subprocess,sys,time,traceback
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,value):
    with Path(p).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
B=Path(sys.argv[1]); plan=load(B/'plan.json'); assert sorted(os.sched_getaffinity(0))==plan['helperCpus']
for p,h in plan['pins'].items():assert sha(p)==h,p
for name,h in load(plan['candidateSourceMap'])['files'].items():assert sha(Path(plan['worktree'])/name)==h
assert not (B/'lane-clock.json').exists()
libc=ctypes.CDLL(None,use_errno=True);assert libc.prctl(36,1,0,0,0)==0
state={'complete':False,'failure':None,'stages':[],'ownedGroups':[],'performanceMeasurement':False,'aggregateSeconds':1200}
started=time.monotonic_ns();deadline=started+1200_000_000_000
put(B/'lane-clock.json',{'startMonotonicNs':started,'driverPid':os.getpid(),'seconds':1200,'basis':'Immediately before first native Cargo test/build stage; gaps and independent closure included.'})
artifacts={}

def reap():
    rows=[]
    while True:
        try:
            pid,status=os.waitpid(-1,os.WNOHANG)
            if not pid:break
            rows.append({'pid':pid,'waitStatus':status})
        except ChildProcessError:break
    return rows

def limits():
    resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(512*1024**2,512*1024**2))

def stage(name):
    cfg=plan['stages'][name]; d=B/name;cleanup=None;code=None
    env={**os.environ,**plan['environment']}
    if name=='fixtures':env.update(ROOK2_FOCUSED_TAP_CONFIG=str(d/'tap-config.json'),ROOK2_FOCUSED_NATIVE_DIR=str(d/'native'))
    stage_deadline=min(deadline,time.monotonic_ns()+cfg['maximumSeconds']*1_000_000_000)
    assert time.monotonic_ns()<stage_deadline
    with (d/'stdout').open('xb') as out,(d/'stderr').open('xb') as err:
        proc=subprocess.Popen(cfg['argv'],cwd=cfg['cwd'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,start_new_session=True,preexec_fn=limits)
        pid=proc.pid;state['ownedGroups'].append(pid)
        put(d/'launch.json',{'pid':pid,'pgid':pid,'argv':cfg['argv'],'cwd':cfg['cwd'],'expectedExit':cfg['expectedExit'],'affinity':sorted(os.sched_getaffinity(pid))})
        try:
            while proc.poll() is None:
                if time.monotonic_ns()>=stage_deadline:raise TimeoutError('Per-stage or aggregate deadline')
                if out.tell()+err.tell()>512*1024**2:raise RuntimeError('Stage output storage cap')
                time.sleep(.05)
            code=proc.wait()
        except BaseException:
            cleanup={'term':True,'kill':False}
            try:os.killpg(pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:code=proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                cleanup['kill']=True
                try:os.killpg(pid,signal.SIGKILL)
                except ProcessLookupError:pass
                code=proc.wait(timeout=5)
            cleanup['orphanWaits']=reap();raise
        finally:
            terminal={'pid':pid,'returncode':code,'expectedExit':cfg['expectedExit'],'cleanup':cleanup,'argv':cfg['argv']}
            put(d/'terminal.json',terminal);state['stages'].append({'name':name,**terminal})
    assert code==cfg['expectedExit'],(name,code,cfg['expectedExit'])
    try:os.killpg(pid,0)
    except ProcessLookupError:pass
    else:raise RuntimeError('Owned group survives stage exit')
    assert time.monotonic_ns()<deadline
    print(json.dumps({'stage':name,'returncode':code,'expectedExit':cfg['expectedExit']}),flush=True)


def artifact(stage_name,key,kind):
    rows=[]
    for line in (B/stage_name/'stdout').read_text().splitlines():
        try:row=json.loads(line)
        except ValueError:continue
        if row.get('reason')=='compiler-artifact' and row.get('executable') and kind in row['target']['kind']:
            rows.append(row)
    assert len(rows)==1,(stage_name,len(rows))
    row=rows[0];path=Path(row['executable']);assert path.is_file()
    artifacts[key]={'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'target':row['target'],'profile':row['profile']}
    put(B/stage_name/'artifact.json',artifacts[key])

try:
    stage('diagnostic-tests');artifact('diagnostic-tests','diagnosticTests','bin')
    assert '209 passed; 0 failed; 0 ignored' in (B/'diagnostic-tests/stdout').read_text()
    stage('development-tests');artifact('development-tests','developmentTests','bin')
    assert '2 passed; 0 failed; 0 ignored' in (B/'development-tests/stdout').read_text()
    put(B/'test-artifacts.json',artifacts)
    assert sha(plan['diagnosticImage'])==plan['diagnosticSha256']
    stage('fixtures')
    stage('independent')
    assert load(B/'independent-reconciliation.json')['pass']
    assert time.monotonic_ns()<deadline
    state['complete']=True
except BaseException as error:
    state['failure']=repr(error);(B/'lane-error.txt').write_text(traceback.format_exc())
finally:
    survivors=[]
    for pgid in state['ownedGroups']:
        try:os.killpg(pgid,0);survivors.append(pgid)
        except ProcessLookupError:pass
    state['forcedCleanupGroups']=list(survivors)
    for pgid in survivors:
        try:os.killpg(pgid,signal.SIGKILL)
        except ProcessLookupError:pass
    state['orphanWaits']=reap();until=time.monotonic()+5
    while survivors and time.monotonic()<until:
        state['orphanWaits']+=reap();remaining=[]
        for pgid in survivors:
            try:os.killpg(pgid,0);remaining.append(pgid)
            except ProcessLookupError:pass
        survivors=remaining
        if survivors:time.sleep(.05)
    state['allOwnedGroupsTerminal']=not survivors
    state['elapsedResourceLimitNs']=time.monotonic_ns()-started
    state['deadlineSatisfied']=state['elapsedResourceLimitNs']<1200_000_000_000
    put(B/'lane-outcome.json',state);print(json.dumps(state),flush=True)
sys.exit(0 if state['complete'] and state['deadlineSatisfied'] and state['allOwnedGroupsTerminal'] else 1)
