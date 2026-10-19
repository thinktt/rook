"""Two exact-image case35 runs only. Never imports account_native."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,time,sys
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
 plan=load(HERE/'plan.json');clear=load(HERE/'execution-clearance.json')
 assert clear['profile'] is True and clear['all_native_and_CPU_windows_closed'] is True
 review=clear['parent_review'];assert review and sha(review['path'])==review['sha256']
 assert sorted(os.sched_getaffinity(0))==plan['helper_affinity']
 assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert not any(os.environ.get(k) for k in ['LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH','NODE_OPTIONS'])
 pins=load(HERE/'input-pins.json');pins.update({str(HERE/n):h for n,h in load(HERE/'helper-pins.json').items()})
 pins[str(HERE/'plan.json')]=sha(HERE/'plan.json');pins[str(HERE/'execution-clearance.json')]=sha(HERE/'execution-clearance.json');pins[review['path']]=review['sha256']
 assert all(sha(p)==h for p,h in pins.items())
 out=Path(plan['output']);assert not out.exists();out.mkdir();write(out/'input-closure.json',pins)
 records=[];result={'complete':False,'cases':{},'failure':None,'event_scope':plan['event_scope']}
 def run(argv,stem,cwd,monitor=False,expected=0):
  x=out/(stem+'.stdout');y=out/(stem+'.stderr');observations=[];owned={};failure=None;cleanup=[]
  # Only the unique new Node/static process group and its directly observed
  # detached children are ours. Never signal the helper/Herdr process group.
  def token(pid):
   return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
  def discover(p):
   try:
    ids=Path(f'/proc/{p.pid}/task/{p.pid}/children').read_text().split()
    for raw in ids:
     child=int(raw)
     try:
      stamp=token(child)
      if os.getpgid(child)==child:owned.setdefault(child,stamp)
     except (FileNotFoundError,ProcessLookupError):pass
    return ids
   except FileNotFoundError:return []
  def send_owned(sig):
   for pid,stamp in list(owned.items()):
    try:
     if token(pid)==stamp and os.getpgid(pid)==pid:
      os.killpg(pid,sig);cleanup.append({'pgid':pid,'signal':int(sig)})
    except (FileNotFoundError,ProcessLookupError):pass
  def stop_owned(p):
   discover(p);send_owned(signal.SIGTERM)
   # Keep Node alive first so original runReplay can close/reap its child.
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:
    send_owned(signal.SIGKILL)
    if p.poll() is None:
     assert os.getpgid(p.pid)==p.pid and p.pid!=os.getpgrp()
     os.killpg(p.pid,signal.SIGTERM);cleanup.append({'pgid':p.pid,'signal':int(signal.SIGTERM)})
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:
     assert os.getpgid(p.pid)==p.pid and p.pid!=os.getpgrp()
     os.killpg(p.pid,signal.SIGKILL);cleanup.append({'pgid':p.pid,'signal':int(signal.SIGKILL)});p.wait(timeout=5)
   # Node can exit before its detached child. Always finish still-owned groups,
   # even when the first wait returned promptly, and bound the final PID check.
   send_owned(signal.SIGKILL)
   deadline=time.monotonic()+5
   while True:
    remaining=[]
    for pid,stamp in owned.items():
     try:
      if token(pid)==stamp:remaining.append(pid)
     except FileNotFoundError:pass
    if not remaining or time.monotonic()>=deadline:break
    time.sleep(0.05)
   cleanup.append({'outer_reaped':p.returncode is not None,'owned_native_pids_still_present':remaining})
   return remaining
  with x.open('xb') as stdout,y.open('xb') as stderr:
   env=dict(os.environ,VALGRIND_LIB=str(Path(plan['valgrind_prefix'])/'libexec/valgrind'))
   p=subprocess.Popen(argv,cwd=cwd,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
   deadline=time.monotonic()+(plan['timeout_ms']['aggregateMs']/1000+30 if monitor else plan['static_command_timeout_seconds'])
   try:
    while p.poll() is None:
     assert time.monotonic()<deadline,'bounded command deadline'
     if monitor:
      children=discover(p);assert len(children)<=1,children
      for child in children:
       q=Path('/proc')/child
       try:
        status=q.joinpath('status').read_text();threads=int(next(z.split(':',1)[1] for z in status.splitlines() if z.startswith('Threads:')))
        affinity=sorted(os.sched_getaffinity(int(child)))
        executable=os.readlink(q/'exe');command=q.joinpath('cmdline').read_bytes().split(b'\0')
        backend=str(Path(plan['valgrind_prefix'])/'libexec/valgrind/callgrind-amd64-linux')
        if executable==backend:
         assert affinity==[14] and threads==1,(affinity,threads)
         observations.append({'pid':int(child),'exe':executable,'affinity':affinity,'threads':threads,'cmdline':[z.decode() for z in command if z]})
       except (FileNotFoundError,ProcessLookupError):pass
     time.sleep(1)
    code=p.wait()
   except BaseException as error:
    failure=f'{type(error).__name__}: {error}'
   finally:
    if failure is not None or p.poll() is None:
     try:
      remaining=stop_owned(p)
      if remaining:failure=(failure or '')+f'; owned detached PIDs remain after bounded kill: {remaining}'
     except BaseException as error:failure=(failure or '')+f'; cleanup {type(error).__name__}: {error}'
    code=p.wait() if p.poll() is not None else None
  record={'stem':stem,'argv':argv,'cwd':str(cwd),'pid':p.pid,'exit_code':code,'actual_child_return_observed':code is not None,'stdout_sha256':sha(x),'stderr_sha256':sha(y),'observations':observations,'failure':failure,'cleanup':cleanup}
  records.append(record);write(out/(stem+'-terminal.json'),record)
  assert code==expected and failure is None,(stem,code,failure)
  return record

 try:
  prefix=Path(plan['valgrind_prefix'])
  run([str(prefix/'bin/valgrind'),'--version'],'valgrind-version',HERE)
  assert (out/'valgrind-version.stdout').read_text()=='valgrind-3.24.0\n'
  run([str(prefix/'bin/callgrind_annotate'),'--version'],'annotator-version',HERE,expected=255)
  assert (out/'annotator-version.stderr').read_bytes()==b'callgrind_annotate-3.24.0\n' and not (out/'annotator-version.stdout').stat().st_size
  for name,v in plan['variants'].items():
   target=out/name;target.mkdir()
   argv=[plan['node'],str(HERE/'replay35.mjs'),'live',str(HERE/'plan.json'),name,str(target)]
   rec=run(argv,name+'-live',Path(v['source_root']),monitor=True)
   row=load(target/'replay.json');assert any(o['pid']==row['pid'] for o in rec['observations'])
   assert v['engine'] in row['command']
   assert row['exit']=={'code':0,'signal':None} and row['complete'] and row['stderr']==''
   data=target/'profile.callgrind';assert 0<data.stat().st_size<=plan['profile_size_cap']
   lines=data.read_text().splitlines();assert [l for l in lines if l.startswith('events:')]==['events: Ir']
   totals=[int(l.split(':',1)[1]) for l in lines if l.startswith('summary:')];assert len(totals)==1 and totals[0]>0
   for inclusive in ['no','yes']:
    run([str(prefix/'bin/callgrind_annotate'),'--auto=no','--inclusive='+inclusive,'--threshold=100',str(data)],name+'-functions-'+inclusive,Path(v['source_root']))
   result['cases'][name]={'pid':row['pid'],'whole_lifetime_Ir':totals[0],'profile_sha256':sha(data),'log_sha256':sha(target/'valgrind.log'),'original_live_replay_pass':True}
  assert all(sha(p)==h for p,h in pins.items())
  result.update(complete=True,commands=records,input_sha256=pins,exactly_two_fresh_engine_lifetimes=True,outer_actual_terminal_required=True)
 except BaseException as e:result['failure']=f'{type(e).__name__}: {e}'
 finally:write(out/'provenance.json',result)
 print(json.dumps({'complete':result['complete'],'failure':result['failure'],'cases':result['cases'],'provenance':str(out/'provenance.json')}));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
