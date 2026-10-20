"""Prospective safety supervision. Import starts no processes/syscalls."""
from pathlib import Path
import ctypes, json, os, resource, selectors, signal, subprocess, time
from types import SimpleNamespace

class BoundedRunner:
 def __init__(self,out,plan,started=None,boot_id=None):
  self.out=Path(out);self.limits=plan['supervision'];self.started=time.monotonic() if started is None else started
  self.boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip();self.deadline=self.started+self.limits['study_wall_ms']/1000
  preflight={'complete':False,'pid':os.getpid(),'failure':None,'prior_subreaper':None}
  try:
   assert boot_id is None or boot_id==self.boot_id, 'study crossed reboot'
   assert hasattr(os,'pidfd_open') and hasattr(signal,'pidfd_send_signal'), 'pidfd APIs absent'
   fd=os.pidfd_open(os.getpid())
   try:signal.pidfd_send_signal(fd,0)
   finally:os.close(fd)
   preflight['self_pidfd_signal0_passed']=True
   # Process-local Linux child subreaper retains replay-check detached:true children.
   libc=ctypes.CDLL(None,use_errno=True);old=ctypes.c_int()
   assert libc.prctl(37,ctypes.byref(old),0,0,0)==0, 'GET_CHILD_SUBREAPER failed'
   preflight['prior_subreaper']=old.value
   assert libc.prctl(36,1,0,0,0)==0, 'SET_CHILD_SUBREAPER failed'
   new=ctypes.c_int();assert libc.prctl(37,ctypes.byref(new),0,0,0)==0 and new.value==1
   assert not self._owned(), 'preexisting helper child'
   preflight['complete']=True
  except BaseException as error:preflight['failure']=f'{type(error).__name__}: {error}'
  with (self.out/f'supervisor-preflight-{os.getpid()}.json').open('x') as f:json.dump(preflight,f,indent=2);f.write('\n')
  assert preflight['complete'],preflight['failure']
  self.prior_subreaper=preflight['prior_subreaper']

 def _files(self):
  total=0;bad=None
  for p in self.out.rglob('*'):
   if p.is_symlink():bad=f'output symlink: {p.name}';continue
   if not p.is_file():continue
   n=p.stat().st_size;total+=n
   cap=self.limits['profile_bytes'] if p.suffix=='.callgrind' else self.limits['log_bytes'] if p.suffix=='.log' else None
   if cap is not None and n>cap:bad=f'direct file cap: {p.name} ({n}>{cap})'
  if total>self.limits['total_storage_bytes']:bad=f'whole-study storage cap ({total})'
  return total,bad

 @staticmethod
 def _stat(pid):
  tail=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
  return tail[0],int(tail[19])

 @staticmethod
 def _owned():
  pending=[os.getpid()];seen=set();rows=[]
  # Only owned task/children lists, not arbitrary /proc PID resource scans.
  while pending:
   parent=pending.pop()
   try:tasks=list(Path(f'/proc/{parent}/task').iterdir())
   except FileNotFoundError:continue
   for task in tasks:
    try:kids=(task/'children').read_text().split()
    except FileNotFoundError:continue
    for raw in kids:
     pid=int(raw)
     if pid in seen:continue
     seen.add(pid);pending.append(pid)
     try:
      state,start=BoundedRunner._stat(pid)
      fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in x}
      rows.append({'pid':pid,'start_ticks':start,'state':state,'rss_bytes':int(fields.get('VmRSS','0 kB').split()[0])*1024,'swap_bytes':int(fields.get('VmSwap','0 kB').split()[0])*1024,'threads':int(fields['Threads'])})
     except (FileNotFoundError,ProcessLookupError):continue
  return rows

 def run(self,command,stem,wall_ms,cwd=None,env=None):
  assert '/' not in stem and time.monotonic()<self.deadline and not self._owned()
  _,bad=self._files();assert bad is None,bad
  cap=self.limits['captured_stream_bytes'];counts={s:{'observed':0,'retained':0,'discarded_observed':0} for s in ['stdout','stderr']}
  outputs={s:(self.out/(stem+'.'+s)).open('xb') for s in counts}
  limit=self.limits['child_rlimit_fsize_bytes']
  def child_limits():resource.setrlimit(resource.RLIMIT_FSIZE,(limit,limit))
  child=None;selector=selectors.DefaultSelector();failure=None;cleanup_at=None;term_at=None;pidfds={};adopted=[];errors=[];uncertain=False
  peak={'rss_bytes':0,'swap_bytes':0,'processes':0,'threads':0,'storage_bytes':0};last=[]
  begin=time.monotonic();end=min(self.deadline,begin+wall_ms/1000);last_sample=0
  def fault(where,error):
   nonlocal failure,uncertain
   uncertain=True;failure=failure or f'{where}: {type(error).__name__}: {error}'
   if len(errors)<32:errors.append(f'{where}: {type(error).__name__}: {error}')
  def sample():
   nonlocal last
   try:rows=self._owned()
   except BaseException as error:fault('owned scan',error);return last
   for row in rows:
    key=(row['pid'],row['start_ticks'])
    if key in pidfds:continue
    fd=None
    try:
     fd=os.pidfd_open(row['pid'])
     if self._stat(row['pid'])[1]!=row['start_ticks']:os.close(fd);continue
     if len(pidfds)>=256:
      # Known fixed tools should never churn this much; terminate this exact
      # freshly pinned task too, rather than failing before cleanup can see it.
      signal.pidfd_send_signal(fd,signal.SIGKILL);os.close(fd);fd=None
      raise RuntimeError('owned PID churn cap')
     pidfds[key]=fd
    except (FileNotFoundError,ProcessLookupError):
     if fd is not None:os.close(fd)
    except BaseException as error:
     if fd is not None:os.close(fd)
     fault('pidfd acquisition',error)
   last=rows;return rows
  def stop(sig):
   for fd in list(pidfds.values()):
    try:signal.pidfd_send_signal(fd,sig)
    except ProcessLookupError:pass
    except BaseException as error:fault('pidfd signal',error)
  def reap(rows):
   for row in rows:
    if child is None or row['pid']==child.pid:continue
    try:
     pid,status=os.waitpid(row['pid'],os.WNOHANG)
     if pid:adopted.append({'pid':pid,'wait_status':status})
    except (ChildProcessError,ProcessLookupError):pass
    except BaseException as error:fault('adopted wait',error)
  def drain(wait):
   nonlocal failure
   for key,_ in selector.select(wait):
    try:data=os.read(key.fileobj.fileno(),65536)
    except BlockingIOError:continue
    s=key.data
    if not data:selector.unregister(key.fileobj);key.fileobj.close();continue
    row=counts[s];row['observed']+=len(data);keep=min(len(data),max(0,cap-row['retained']))
    outputs[s].write(data[:keep]);outputs[s].flush();row['retained']+=keep;row['discarded_observed']+=len(data)-keep
    if keep!=len(data):failure=failure or f'captured {s} cap'
  try:
   child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=child_limits,cwd=cwd,env=env)
   sample() # Pin controller before the first poll; retains detached descendants.
   for s,pipe in [('stdout',child.stdout),('stderr',child.stderr)]:os.set_blocking(pipe.fileno(),False);selector.register(pipe,selectors.EVENT_READ,s)
   while True:
    now=time.monotonic()
    if now-last_sample>=self.limits['poll_ms']/1000:
     last_sample=now;rows=sample();active=[x for x in rows if x['state']!='Z'];reap(rows)
     values={'rss_bytes':sum(x['rss_bytes'] for x in active),'swap_bytes':sum(x['swap_bytes'] for x in active),'processes':len(active),'threads':sum(x['threads'] for x in active)}
     storage,bad=self._files();values['storage_bytes']=storage;failure=failure or bad
     for k,v in values.items():peak[k]=max(peak[k],v)
     for key,lim in [('rss_bytes','aggregate_group_rss_bytes'),('swap_bytes','max_group_swap_bytes'),('processes','max_group_processes'),('threads','max_group_threads')]:
      if values[key]>self.limits[lim]:failure=failure or f'owned-tree {key} cap ({values[key]})'
     if now>=end:failure=failure or 'command/whole-study deadline'
    code=child.poll()
    if code is not None:
     cleanup_at=time.monotonic() if cleanup_at is None else cleanup_at
     rows=sample();reap(rows) # Re-enumerate after reaping the primary controller.
     if any(x['pid']!=child.pid and x['state']!='Z' for x in rows):failure=failure or 'owned descendant outlived controller'
    if failure:
     cleanup_at=time.monotonic() if cleanup_at is None else cleanup_at
     term_at=time.monotonic() if term_at is None else term_at
     sample();stop(signal.SIGKILL if time.monotonic()-term_at>=self.limits['term_grace_ms']/1000 else signal.SIGTERM);reap(last)
    if cleanup_at is not None and time.monotonic()-cleanup_at>=self.limits['cleanup_ms']/1000:
     failure=failure or 'five-second cleanup deadline exceeded';stop(signal.SIGKILL);break
    drain(self.limits['poll_ms']/1000)
    if child.poll() is not None and not selector.get_map():
     rows=sample();reap(rows)
     if not sample():break
  except BaseException as error:failure=failure or f'{type(error).__name__}: {error}'
  finally:
   # No acquisition/observation error may escape this cleanup/preservation path.
   if child is not None:
    cleanup_at=time.monotonic() if cleanup_at is None else cleanup_at
    term_at=time.monotonic() if term_at is None else term_at
    while time.monotonic()-cleanup_at<self.limits['cleanup_ms']/1000:
     rows=sample()
     try:code=child.poll()
     except BaseException as error:fault('controller poll',error);code=None
     reap(rows)
     if code is not None and not sample():break
     stop(signal.SIGKILL if time.monotonic()-term_at>=self.limits['term_grace_ms']/1000 else signal.SIGTERM)
     try:drain(0.01)
     except BaseException as error:fault('cleanup drain',error)
    stop(signal.SIGKILL) # Final bounded attempt, not an extra cleanup allowance.
   for key in list(selector.get_map().values()):
    try:selector.unregister(key.fileobj);key.fileobj.close()
    except BaseException as error:fault('pipe close',error)
   selector.close()
   for f in outputs.values():
    try:f.close()
    except BaseException as error:fault('stream close',error)
  try:code=None if child is None else child.poll()
  except BaseException as error:fault('final poll',error);code=None
  rows=sample() if child is not None else [];reap(rows);rows=sample() if child is not None else []
  completed=time.monotonic();elapsed=0 if cleanup_at is None else completed-cleanup_at
  confirmed=not uncertain and not rows and (child is None or code is not None) and elapsed<=self.limits['cleanup_ms']/1000
  if not confirmed:failure=failure or 'owned cleanup unknown or observed later than five seconds'
  try:storage,bad=self._files();peak['storage_bytes']=max(peak['storage_bytes'],storage);failure=failure or bad
  except BaseException as error:fault('final storage observation',error)
  result={'argv':command,'pid':None if child is None else child.pid,'returncode':code,'actual_child_return_observed':code is not None,'complete':failure is None,'failure':failure,'whole_owned_tree_cleanup_confirmed':confirmed,'cleanup_started_monotonic':cleanup_at,'cleanup_completed_observed_monotonic':completed,'cleanup_elapsed_s':elapsed,'cleanup_elapsed_wall_s':elapsed,'cleanup_within_deadline':elapsed<=self.limits['cleanup_ms']/1000,'cleanup_deadline_s':self.limits['cleanup_ms']/1000,'remaining_owned':rows,'ownership_observation_errors':errors,'seen_owned_processes':[{'pid':p,'start_ticks':s} for p,s in pidfds],'adopted_wait_statuses':adopted,'subreaper_enabled':True,'prior_subreaper':self.prior_subreaper,'stream_bytes':counts,'sampled_peaks':peak,'sample_interval_ms':self.limits['poll_ms'],'limits_sampled_except_fsize_and_pipe_retention':True,'elapsed_wall_s':time.monotonic()-begin}
  for fd in pidfds.values():
   try:os.close(fd)
   except OSError:pass
  with (self.out/(stem+'-supervision.json')).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
  if failure:raise RuntimeError(f'{stem}: {failure}; preserved supervision/output')
  return SimpleNamespace(returncode=code)
