"""Prospective supervision; importing defines code and starts no process."""
from pathlib import Path
import ctypes, json, os, resource, selectors, signal, subprocess, time
from types import SimpleNamespace

class BoundedRunner:
 def __init__(self, out, plan, started=None, boot_id=None):
  self.out=Path(out);self.limits=plan['supervision'];self.started=time.monotonic() if started is None else started
  self.boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  assert boot_id is None or boot_id==self.boot_id, 'study crossed reboot'
  self.deadline=self.started+self.limits['study_wall_ms']/1000
  assert hasattr(os,'pidfd_open') and hasattr(signal,'pidfd_send_signal'), 'pidfd supervision unavailable'
  # replay-check spawns detached:true; a controller process group is insufficient.
  # This changes this helper process only, never host settings or native code.
  self.libc=ctypes.CDLL(None,use_errno=True);old=ctypes.c_int()
  assert self.libc.prctl(37,ctypes.byref(old),0,0,0)==0, 'GET_CHILD_SUBREAPER failed'
  self.prior_subreaper=old.value
  assert self.libc.prctl(36,1,0,0,0)==0, 'SET_CHILD_SUBREAPER failed'
  new=ctypes.c_int();assert self.libc.prctl(37,ctypes.byref(new),0,0,0)==0 and new.value==1
  assert not self._owned(), 'unrelated/preexisting helper child'

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
  # Enumerate only this helper's descendants, across every owned parent thread.
  # Detached sessions remain children; after controller death, subreaper adopts.
  pending=[os.getpid()];seen=set();rows=[]
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
      rows.append({'pid':pid,'start_ticks':start,'state':state,
       'rss_bytes':int(fields.get('VmRSS','0 kB').split()[0])*1024,
       'swap_bytes':int(fields.get('VmSwap','0 kB').split()[0])*1024,'threads':int(fields['Threads'])})
     except (FileNotFoundError,ProcessLookupError):continue
  return rows

 def run(self, command, stem, wall_ms, cwd=None, env=None):
  assert '/' not in stem and time.monotonic()<self.deadline and not self._owned()
  _,bad=self._files();assert bad is None,bad
  cap=self.limits['captured_stream_bytes'];counts={s:{'observed':0,'retained':0,'discarded_observed':0} for s in ['stdout','stderr']}
  outputs={s:(self.out/(stem+'.'+s)).open('xb') for s in counts}
  limit=self.limits['child_rlimit_fsize_bytes']
  def child_limits():resource.setrlimit(resource.RLIMIT_FSIZE,(limit,limit))
  child=None;selector=selectors.DefaultSelector();failure=None;stop_at=None;pidfds={};adopted=[]
  peak={'rss_bytes':0,'swap_bytes':0,'processes':0,'threads':0,'storage_bytes':0};last=[]
  begin=time.monotonic();end=min(self.deadline,begin+wall_ms/1000);last_sample=0
  def sample():
   rows=self._owned()
   for row in rows:
    key=(row['pid'],row['start_ticks'])
    if key not in pidfds:
     assert len(pidfds)<256, 'owned PID churn cap'
     fd=None
     try:
      fd=os.pidfd_open(row['pid']);same=self._stat(row['pid'])[1]==row['start_ticks']
      if not same:os.close(fd);continue
      pidfds[key]=fd
     except (FileNotFoundError,ProcessLookupError):
      if fd is not None:os.close(fd)
      continue
   return rows
  def stop(rows,sig):
   for row in reversed(rows):
    fd=pidfds.get((row['pid'],row['start_ticks']))
    if fd is not None:
     try:signal.pidfd_send_signal(fd,sig)
     except ProcessLookupError:pass
  def reap(rows):
   for row in rows:
    if row['pid']==child.pid:continue # Popen alone observes the controller exit.
    try:
     pid,status=os.waitpid(row['pid'],os.WNOHANG)
     if pid:adopted.append({'pid':pid,'wait_status':status})
    except ChildProcessError:pass # Still owned/reaped by the live controller.
  def drain(wait):
   nonlocal failure
   for key,_ in selector.select(wait):
    data=os.read(key.fileobj.fileno(),65536);s=key.data
    if not data:selector.unregister(key.fileobj);key.fileobj.close();continue
    row=counts[s];row['observed']+=len(data);keep=min(len(data),max(0,cap-row['retained']))
    outputs[s].write(data[:keep]);outputs[s].flush();row['retained']+=keep;row['discarded_observed']+=len(data)-keep
    if keep!=len(data):failure=failure or f'captured {s} cap'
  try:
   child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=child_limits,cwd=cwd,env=env)
   for s,pipe in [('stdout',child.stdout),('stderr',child.stderr)]:os.set_blocking(pipe.fileno(),False);selector.register(pipe,selectors.EVENT_READ,s)
   while True:
    now=time.monotonic()
    if now-last_sample>=self.limits['poll_ms']/1000:
     last_sample=now;last=sample();active=[x for x in last if x['state']!='Z'];reap(last)
     observed={'rss_bytes':sum(x['rss_bytes'] for x in active),'swap_bytes':sum(x['swap_bytes'] for x in active),'processes':len(active),'threads':sum(x['threads'] for x in active)}
     storage,bad=self._files();observed['storage_bytes']=storage
     for k,v in observed.items():peak[k]=max(peak[k],v)
     failure=failure or bad
     for key,lim in [('rss_bytes','aggregate_group_rss_bytes'),('swap_bytes','max_group_swap_bytes'),('processes','max_group_processes'),('threads','max_group_threads')]:
      if observed[key]>self.limits[lim]:failure=failure or f'owned-tree {key} cap ({observed[key]})'
     if now>=end:failure=failure or 'command/whole-study deadline'
     if child.poll() is not None and any(x['state']!='Z' for x in self._owned()):failure=failure or 'owned descendant outlived controller'
    if failure and stop_at is None:stop_at=now;stop(last,signal.SIGTERM)
    if stop_at is not None:
     last=sample();stop(last,signal.SIGKILL if now-stop_at>=self.limits['term_grace_ms']/1000 else signal.SIGTERM);reap(last)
     if now-stop_at>=self.limits['cleanup_ms']/1000:break
    drain(self.limits['poll_ms']/1000)
    if child.poll() is not None and not selector.get_map():
     last=sample();reap(last)
     if not self._owned():break
  except BaseException as error:failure=failure or f'{type(error).__name__}: {error}'
  finally:
   if child is not None and (child.poll() is None or self._owned()):
    stop_at=time.monotonic() if stop_at is None else stop_at
    while time.monotonic()-stop_at<self.limits['cleanup_ms']/1000:
     last=sample();stop(last,signal.SIGKILL if time.monotonic()-stop_at>=self.limits['term_grace_ms']/1000 else signal.SIGTERM)
     drain(0.01);child.poll();reap(last)
     if child.returncode is not None and not self._owned():break
   for key in list(selector.get_map().values()):selector.unregister(key.fileobj);key.fileobj.close()
   selector.close()
   for f in outputs.values():f.close()
  code=None if child is None else child.poll();last=self._owned()
  confirmed=code is not None and not last
  if not confirmed:failure=failure or 'five-second whole-owned-tree cleanup unconfirmed'
  storage,bad=self._files();peak['storage_bytes']=max(peak['storage_bytes'],storage);failure=failure or bad
  result={'argv':command,'pid':None if child is None else child.pid,'returncode':code,'actual_child_return_observed':code is not None,'complete':failure is None,'failure':failure,'whole_owned_tree_cleanup_confirmed':confirmed,'remaining_owned':last,'seen_owned_processes':[{'pid':p,'start_ticks':s} for p,s in pidfds],'adopted_wait_statuses':adopted,'subreaper_enabled':True,'prior_subreaper':self.prior_subreaper,'stream_bytes':counts,'sampled_peaks':peak,'sample_interval_ms':self.limits['poll_ms'],'limits_sampled_except_fsize_and_pipe_retention':True,'elapsed_wall_s':time.monotonic()-begin}
  for fd in pidfds.values():os.close(fd)
  with (self.out/(stem+'-supervision.json')).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
  if failure:raise RuntimeError(f'{stem}: {failure}; preserved supervision/output')
  return SimpleNamespace(returncode=code)
