#!/usr/bin/env python3
"""Bounded supervisor canaries; no engine, profiler or build is invoked."""
import ast,hashlib,importlib.util,json,os,signal,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 with Path(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def emergency_teardown():
 # Independent test teardown: kill only this dedicated canary process's children.
 # Killing their parents makes detached orphans adoptable by our subreaper.
 start=time.monotonic();seen=set();reaped=[];errors=[]
 def direct():
  try:return [int(x) for x in Path(f'/proc/{os.getpid()}/task/{os.getpid()}/children').read_text().split()]
  except FileNotFoundError:return []
 initial=direct()
 while direct() and time.monotonic()-start<5:
  for pid in direct():
   fd=None
   try:
    fd=os.pidfd_open(pid);signal.pidfd_send_signal(fd,signal.SIGKILL);seen.add(pid)
   except ProcessLookupError:pass
   except BaseException as error:errors.append(repr(error))
   finally:
    if fd is not None:os.close(fd)
  while True:
   try:
    pid,status=os.waitpid(-1,os.WNOHANG)
    if not pid:break
    reaped.append({'pid':pid,'wait_status':status})
   except ChildProcessError:break
  if direct():time.sleep(0.01)
 return {'needed':bool(initial),'seen_pids':sorted(seen),'reaped':reaped,'errors':errors,'remaining':direct(),'elapsed_wall_s':time.monotonic()-start}
def main():
 plan=json.loads((P/'plan.json').read_text());clear=json.loads((P/'execution-clearance.json').read_text())
 assert set(os.sched_getaffinity(0))==H and os.environ['PATH']=='/usr/bin:/bin'
 assert plan['launch'] is True and clear['launch'] is True
 assert clear['plan_sha256']==sha(P/'plan.json') and clear['helper_sha256']==sha(__file__)
 helper=Path(plan['supervisor_path']);assert plan['supervisor_sha256'] and sha(helper)==plan['supervisor_sha256']
 assert clear['parent_source_review_actual'] and clear['engine_or_profiler_runs_authorized'] is False
 out=Path(plan['output']);out.mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('owned_supervision_canary',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 started=time.monotonic();results=[];failure=None
 try:
  for row in plan['cases']:
   assert time.monotonic()-started<plan['aggregate_wall_ms']/1000
   d=out/row['id'];d.mkdir();lim=dict(plan['supervision']);lim.update(row.get('limit_overrides',{}))
   runner=mod.BoundedRunner(d,{'supervision':lim})
   assert not runner._owned()
   caught=None
   try:
    result=runner.run(['/usr/bin/python3','-c',row['program']],row['id'],row['wall_ms'],cwd=d,env=dict(os.environ,PATH='/usr/bin:/bin',PYTHONDONTWRITEBYTECODE='1'))
   except RuntimeError as error:caught=str(error)
   proof=json.loads((d/(row['id']+'-supervision.json')).read_text())
   assert proof['actual_child_return_observed'] is True and proof['whole_owned_tree_cleanup_confirmed'] is True
   assert not proof['remaining_owned'] and not runner._owned()
   if row['expect_failure']:
    assert caught and proof['failure'] and row['reason_fragment'] in proof['failure'],(row['id'],proof)
   else:assert caught is None and proof['complete'] and proof['returncode']==0
   if row['id']=='detached-orphan':
    identity=json.loads((d/(row['id']+'.stdout')).read_text())
    orphan=identity['orphan_pid'];assert identity['orphan_pgid']==identity['orphan_sid']==orphan and orphan!=proof['pid']
    assert orphan in [z['pid'] for z in proof['seen_owned_processes']]
    statuses=[z['wait_status'] for z in proof['adopted_wait_statuses'] if z['pid']==orphan]
    assert len(statuses)==1 and os.WIFSIGNALED(statuses[0]) and os.WTERMSIG(statuses[0])==signal.SIGKILL
   if row['id']=='stream-cap':
    z=proof['stream_bytes']['stdout'];assert z['observed']>z['retained']==lim['captured_stream_bytes'] and z['discarded_observed']>0
   if row['expect_failure']:
    # The revised supervisor must expose actual cleanup timing, not only absence.
    assert proof['cleanup_elapsed_wall_s'] is not None and proof['cleanup_elapsed_wall_s']<=lim['cleanup_ms']/1000
    assert proof['cleanup_within_deadline'] is True
   results.append({'case':row['id'],'passed':True,'supervision_sha256':sha(d/(row['id']+'-supervision.json')),'native_engine_runs':0})
  assert len(results)==6 and sha(helper)==plan['supervisor_sha256']
 except BaseException as error:failure=repr(error)
 fallback=emergency_teardown()
 if fallback['needed'] or fallback['remaining'] or fallback['errors']:failure=failure or 'Independent canary teardown needed; supervisor checks did not suffice'
 save(out/'emergency-teardown.json',fallback)
 save(out/'result.json',{'complete':failure is None,'failure':failure,'cases':results,'supervisor_sha256':plan['supervisor_sha256'],'plan_sha256':sha(P/'plan.json'),'helper_sha256':sha(__file__),'clearance_sha256':sha(P/'execution-clearance.json'),'engine_runs':0,'profiler_runs':0,'scope':'Fixed supervisor canaries only; no timing/performance/engine qualification.'})
 print(json.dumps({'complete':failure is None,'failure':failure,'passed':len(results),'engine_runs':0,'profiler_runs':0}))
 return 0 if failure is None else 1
if __name__=='__main__':sys.exit(main())
