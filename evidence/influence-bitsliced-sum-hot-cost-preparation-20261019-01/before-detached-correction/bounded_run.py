"""Prospective safety supervision only. Import defines helpers; launches nothing."""
from pathlib import Path
import json, os, resource, selectors, signal, subprocess, time
from types import SimpleNamespace

class BoundedRunner:
 def __init__(self, out, plan, started=None, boot_id=None):
  self.out=Path(out);self.limits=plan['supervision']
  self.started=time.monotonic() if started is None else started
  self.boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  assert boot_id is None or boot_id==self.boot_id, 'study crossed reboot'
  self.deadline=self.started+self.limits['study_wall_ms']/1000

 def _files(self):
  total=0;failure=None
  for p in self.out.rglob('*'):
   if p.is_symlink():failure=f'output symlink: {p.name}';continue
   if not p.is_file():continue
   n=p.stat().st_size;total+=n
   cap=self.limits['profile_bytes'] if p.suffix=='.callgrind' else self.limits['log_bytes'] if p.suffix=='.log' else None
   if cap is not None and n>cap:failure=f'direct file cap: {p.name} ({n}>{cap})'
  if total>self.limits['total_storage_bytes']:failure=f'whole-study storage cap ({total})'
  return total,failure

 @staticmethod
 def _group(pgid):
  # Read only pgrp identity for unrelated PIDs; retain resource/state only for
  # this newly created owned group. No host settings, cgroups or /proc writes.
  rows=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    tail=(p/'stat').read_text().rsplit(')',1)[1].split()
    if int(tail[2])!=pgid:continue
    fields={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in (p/'status').read_text().splitlines() if ':' in line}
    rows.append({'pid':int(p.name),'state':tail[0],
       'rss_bytes':int(fields.get('VmRSS','0 kB').split()[0])*1024,
       'swap_bytes':int(fields.get('VmSwap','0 kB').split()[0])*1024,
       'threads':int(fields['Threads'])})
   except (FileNotFoundError,ProcessLookupError):continue
  return rows

 @staticmethod
 def _signal(pgid,sig):
  try:os.killpg(pgid,sig)
  except ProcessLookupError:pass

 def run(self, command, stem, wall_ms, cwd=None, env=None):
  assert '/' not in stem and time.monotonic()<self.deadline
  _,bad=self._files();assert bad is None,bad
  cap=self.limits['captured_stream_bytes'];counts={s:{'observed':0,'retained':0,'discarded_observed':0} for s in ['stdout','stderr']}
  outputs={s:(self.out/(stem+'.'+s)).open('xb') for s in counts}
  limit=self.limits['child_rlimit_fsize_bytes']
  def child_limits():resource.setrlimit(resource.RLIMIT_FSIZE,(limit,limit))
  child=None;selector=selectors.DefaultSelector();failure=None;stop_at=None;killed=False;seen=set();peak={'rss_bytes':0,'swap_bytes':0,'processes':0,'threads':0,'storage_bytes':0};last_group=[]
  begin=time.monotonic();end=min(self.deadline,begin+wall_ms/1000);last_sample=0
  try:
   child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=child_limits,cwd=cwd,env=env)
   for s,pipe in [('stdout',child.stdout),('stderr',child.stderr)]:os.set_blocking(pipe.fileno(),False);selector.register(pipe,selectors.EVENT_READ,s)
   while True:
    now=time.monotonic()
    if now-last_sample>=self.limits['poll_ms']/1000:
     last_sample=now;last_group=self._group(child.pid);active=[x for x in last_group if x['state']!='Z'];seen.update(x['pid'] for x in last_group)
     sample={'rss_bytes':sum(x['rss_bytes'] for x in active),'swap_bytes':sum(x['swap_bytes'] for x in active),'processes':len(active),'threads':sum(x['threads'] for x in active)}
     storage,bad=self._files();sample['storage_bytes']=storage
     for k,v in sample.items():peak[k]=max(peak[k],v)
     if bad:failure=failure or bad
     for key,lim in [('rss_bytes','aggregate_group_rss_bytes'),('swap_bytes','max_group_swap_bytes'),('processes','max_group_processes'),('threads','max_group_threads')]:
      if sample[key]>self.limits[lim]:failure=failure or f'owned-group {key} cap ({sample[key]})'
     if len(seen)>256:failure=failure or 'owned-group PID churn cap';seen=set(sorted(seen)[:256])
     if now>=end:failure=failure or 'command/whole-study deadline'
     if child.poll() is not None and active:failure=failure or 'owned group outlived controller'
    if failure and stop_at is None:stop_at=now;self._signal(child.pid,signal.SIGTERM)
    if stop_at is not None and not killed and now-stop_at>=self.limits['term_grace_ms']/1000:self._signal(child.pid,signal.SIGKILL);killed=True
    if stop_at is not None and now-stop_at>=self.limits['cleanup_ms']/1000:break
    for key,_ in selector.select(self.limits['poll_ms']/1000):
     data=os.read(key.fileobj.fileno(),65536);s=key.data
     if not data:selector.unregister(key.fileobj);key.fileobj.close();continue
     row=counts[s];row['observed']+=len(data);keep=min(len(data),max(0,cap-row['retained']))
     outputs[s].write(data[:keep]);outputs[s].flush();row['retained']+=keep;row['discarded_observed']+=len(data)-keep
     if keep!=len(data):failure=failure or f'captured {s} cap'
    if child.poll() is not None and not selector.get_map():
     last_group=self._group(child.pid)
     if not any(x['state']!='Z' for x in last_group):break
  except BaseException as error:
   failure=failure or f'{type(error).__name__}: {error}'
  finally:
   # Includes Python-side errors/interrupts. Never delete retained outputs.
   if child is not None and (child.poll() is None or any(x['state']!='Z' for x in self._group(child.pid))):
    stop_at=time.monotonic() if stop_at is None else stop_at;self._signal(child.pid,signal.SIGTERM)
    while time.monotonic()-stop_at<self.limits['cleanup_ms']/1000:
     if time.monotonic()-stop_at>=self.limits['term_grace_ms']/1000:self._signal(child.pid,signal.SIGKILL)
     for key,_ in selector.select(0.01):
      data=os.read(key.fileobj.fileno(),65536);s=key.data
      if not data:selector.unregister(key.fileobj);key.fileobj.close();continue
      row=counts[s];row['observed']+=len(data);keep=min(len(data),max(0,cap-row['retained']));outputs[s].write(data[:keep]);row['retained']+=keep;row['discarded_observed']+=len(data)-keep
     child.poll();last_group=self._group(child.pid)
     if child.returncode is not None and not any(x['state']!='Z' for x in last_group):break
   for key in list(selector.get_map().values()):selector.unregister(key.fileobj);key.fileobj.close()
   selector.close()
   for f in outputs.values():f.close()
  code=None if child is None else child.poll();last_group=[] if child is None else self._group(child.pid)
  cleanup_confirmed=code is not None and not any(x['state']!='Z' for x in last_group)
  if not cleanup_confirmed:failure=failure or 'five-second owned-group cleanup unconfirmed'
  storage,bad=self._files();peak['storage_bytes']=max(peak['storage_bytes'],storage);failure=failure or bad
  result={'argv':command,'pid':None if child is None else child.pid,'returncode':code,'actual_child_return_observed':code is not None,'complete':failure is None,'failure':failure,'whole_owned_group_cleanup_confirmed':cleanup_confirmed,'remaining_group':last_group,'seen_owned_pids':sorted(seen),'stream_bytes':counts,'sampled_peaks':peak,'sample_interval_ms':self.limits['poll_ms'],'limits_are_sampled_except_fsize_and_pipe_retention':True,'elapsed_wall_s':time.monotonic()-begin}
  with (self.out/(stem+'-supervision.json')).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
  if failure:raise RuntimeError(f'{stem}: {failure}; preserved supervision/output')
  return SimpleNamespace(returncode=code)
