#!/usr/bin/python3
"""Single900s monotonic lane; no retries, no additional native invocations."""
import ctypes, hashlib, json, os, signal, subprocess, sys, time, traceback
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):
    with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
B=Path(sys.argv[1]); plan=load(B/'plan.json')
assert sorted(os.sched_getaffinity(0))==plan['helperCpus']
for p,h in plan['pins'].items():assert sha(p)==h,p
assert load(B/'reuse-index.json')['customReconciliationPass']
assert not (B/'lane-start.json').exists()
libc=ctypes.CDLL(None,use_errno=True); assert libc.prctl(36,1,0,0,0)==0
state={'complete':False,'failure':None,'stages':[],'ownedGroups':[],'aggregateLimitSeconds':900,'performanceMeasurement':False}
started=time.monotonic_ns(); deadline=started+900_000_000_000
put(B/'lane-start.json',{'monotonicNs':started,'aggregateLimitSeconds':900,'driverPid':os.getpid()})
active=None

def reap_orphans():
    rows=[]
    while True:
        try:
            pid,status=os.waitpid(-1,os.WNOHANG)
            if pid==0:break
            rows.append({'pid':pid,'waitStatus':status})
        except ChildProcessError:break
    return rows

def stage(name,command,env):
    global active
    d=B/name; cleanup=None; code=None
    assert time.monotonic_ns()<deadline
    with (d/'comparator.stdout').open('xb') as out,(d/'comparator.stderr').open('xb') as err:
        active=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,start_new_session=True)
        pid=active.pid;state['ownedGroups'].append(pid)
        put(d/'launch.json',{'pid':pid,'pgid':pid,'argv':command,'helperAffinity':sorted(os.sched_getaffinity(pid))})
        try:
            while active.poll() is None:
                if time.monotonic_ns()>=deadline:raise TimeoutError('900-second aggregate deadline')
                if out.tell()+err.tell()>8*1024*1024:raise RuntimeError('Comparator receipt storage cap')
                time.sleep(0.05)
            code=active.wait()
        except BaseException:
            cleanup={'term':True,'kill':False}
            try:os.killpg(pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:code=active.wait(timeout=min(5,max(0.01,(deadline-time.monotonic_ns())/1e9)))
            except subprocess.TimeoutExpired:
                cleanup['kill']=True
                try:os.killpg(pid,signal.SIGKILL)
                except ProcessLookupError:pass
                code=active.wait(timeout=5)
            cleanup['reapedOrphans']=reap_orphans()
            raise
        finally:
            terminal={'pid':pid,'returncode':code,'cleanup':cleanup,'argv':command}
            put(d/'terminal.json',terminal);state['stages'].append({'name':name,**terminal});active=None
    assert code==0,f'{name}: exit {code}'
    try:os.killpg(pid,0)
    except ProcessLookupError:pass
    else:raise RuntimeError(f'{name}: owned group survives comparator exit')
    assert time.monotonic_ns()<deadline
    print(json.dumps({'stage':name,'returncode':code}),flush=True)

try:
    env={**os.environ,'PATH':'/usr/bin:/bin','TMPDIR':'/home/legolas/rook2-build-tmp','PYTHONDONTWRITEBYTECODE':'1'}
    for name in ['continuous','seed-command-controls','seed-persistence-controls']:
        d=B/name; local={**env,'ROOK2_FOCUSED_TAP_CONFIG':str(d/'tap-config.json'),'ROOK2_FOCUSED_NATIVE_DIR':str(d/'native')}
        stage(name,plan['stages'][name],local)
    stage('independent',['/usr/bin/python3',str(Path(__file__).with_name('reconcile.py')),str(B)],env)
    assert load(B/'independent-reconciliation.json')['customReconciliationPass']
    for p,h in plan['pins'].items():assert sha(p)==h,p
    assert time.monotonic_ns()<deadline
    state['complete']=True
except BaseException as error:
    state['failure']=repr(error)
    (B/'lane-error.txt').write_text(traceback.format_exc())
finally:
    state['orphanWaits']=reap_orphans()
    state['elapsedForResourceLimitNs']=time.monotonic_ns()-started
    state['deadlineSatisfied']=state['elapsedForResourceLimitNs']<900_000_000_000
    survivors=[]
    for pgid in state['ownedGroups']:
        try:os.killpg(pgid,0);survivors.append(pgid)
        except ProcessLookupError:pass
    state['forcedCleanupGroups']=survivors
    for pgid in survivors:
        try:os.killpg(pgid,signal.SIGKILL)
        except ProcessLookupError:pass
    cleanup_deadline=time.monotonic()+5
    while survivors and time.monotonic()<cleanup_deadline:
        state['orphanWaits']+=reap_orphans(); remaining=[]
        for pgid in survivors:
            try:os.killpg(pgid,0);remaining.append(pgid)
            except ProcessLookupError:pass
        survivors=remaining
        if survivors:time.sleep(0.05)
    state['allOwnedGroupsTerminal']=not survivors
    state['orphanWaits']+=reap_orphans()
    put(B/'lane-outcome.json',state)
    print(json.dumps(state),flush=True)
sys.exit(0 if state['complete'] and state['deadlineSatisfied'] and state['allOwnedGroupsTerminal'] else 1)
