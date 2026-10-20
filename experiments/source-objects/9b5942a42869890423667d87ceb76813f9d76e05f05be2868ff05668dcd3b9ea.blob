"""Inert four-case production-wire witness runner; main requires parent clearance."""
from pathlib import Path
import array, fcntl, hashlib, json, os, re, selectors, signal, subprocess, sys, termios, time

HERE=Path(__file__).resolve().parent
HELPERS=[0,1,2,3,4,5,8,9,10,11,12,13]

def load(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()

class WitnessError(Exception):category='observed_mismatch'
class Invalid(WitnessError):category='collection_invalid'
class Unavailable(WitnessError):category='coverage_precondition_unavailable'

class Budget:
 def __init__(self,plan):self.plan=plan;self.bytes=0;self.final_bytes=0;self.last_write_error=None
 def append(self,f,data,local_left):
  n=min(len(data),max(0,local_left),max(0,self.plan['total_bytes']-self.plan['result_reserve_bytes']-self.bytes))
  written=0
  try:
   while written<n:
    count=f.write(data[written:n])
    if count is None or count<=0:raise OSError('nonpositive retained-file write')
    written+=count;self.bytes+=count
  except OSError as e:self.last_write_error=f'{type(e).__name__}: {e}'
  return written
 def result(self,path,value):
  b=(json.dumps(value,indent=2)+'\n').encode()
  if self.final_bytes+len(b)>self.plan['result_reserve_bytes'] or self.bytes+len(b)>self.plan['total_bytes']:raise Invalid('reserved metadata/storage cap')
  with Path(path).open('xb') as f:assert f.write(b)==len(b)
  self.bytes+=len(b);self.final_bytes+=len(b)

class Process:
 def __init__(self,directory,plan,budget,study_deadline):
  self.directory=directory;self.plan=plan;self.budget=budget;self.study_deadline=study_deadline
  self.child=None;self.selector=selectors.DefaultSelector();self.pending=bytearray();self.raw={s:(directory/(s+'.raw')).open('xb',buffering=0) for s in ['stdin','stdout','stderr']}
  self.counts={s:dict(observed=0,retained=0,discarded_observed=0) for s in self.raw}
  self.events=(directory/'events.jsonl').open('xb',buffering=0);self.event_bytes=0;self.events_lost=0;self.event_logging_disabled=False
  self.started=None;self.deadline=None;self.hard_deadline=None;self.identity=None;self.unexpected_children=[];self.ownership_unknown=False
  self.cleanup_started=None;self.cleanup_completed=None;self.cleanup_errors=[];self.normal_exit=False
 def log(self,kind,**fields):
  if self.event_logging_disabled:self.events_lost+=1;return
  b=(json.dumps(dict(kind=kind,monotonic_ns=time.monotonic_ns(),**fields),separators=(',',':'))+'\n').encode()
  n=self.budget.append(self.events,b,self.plan['event_bytes']-self.event_bytes);self.event_bytes+=n
  if n!=len(b):self.events_lost+=1;self.event_logging_disabled=True;raise Invalid('timestamp/event log cap')
 def start(self,argv):
  self.started=time.monotonic();self.hard_deadline=min(self.study_deadline,self.started+self.plan['lifetime_seconds']);self.deadline=self.hard_deadline-self.plan['cleanup_seconds']
  self.child=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0,start_new_session=True)
  # No controller/Valgrind layer; the actual ordinary executable is this child.
  for stream in [self.child.stdin,self.child.stdout,self.child.stderr]:os.set_blocking(stream.fileno(),False)
  for name in ['stdout','stderr']:self.selector.register(getattr(self.child,name),selectors.EVENT_READ,name)
  pid=self.child.pid;fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
  self.identity=dict(pid=pid,start_ticks=fields[19],exe=os.readlink(f'/proc/{pid}/exe'),affinity=sorted(os.sched_getaffinity(pid)),pgid=os.getpgid(pid),sid=os.getsid(pid))
  if self.identity['exe']!=str(Path(argv[0]).resolve()) or self.identity['affinity']!=HELPERS or self.identity['pgid']!=pid or self.identity['sid']!=pid:raise Invalid('native identity/placement/session mismatch')
  self.log('native-start',argv=argv,identity=self.identity)
 def check(self,end):
  if time.monotonic()>=min(end,self.deadline,self.study_deadline):raise Invalid('record/lifetime/study deadline')
  if self.child.poll() is None:
   try:
    children=set()
    for task in Path(f'/proc/{self.child.pid}/task').iterdir():
     try:children.update(int(x) for x in (task/'children').read_text().split())
     except FileNotFoundError:continue
    if children:self.unexpected_children=sorted(children);self.ownership_unknown=True;raise Invalid('unexpected descendant: selected native is known single-process')
   except FileNotFoundError:
    if self.child.poll() is None:self.ownership_unknown=True;raise Invalid('native ownership observation unavailable')
   except OSError as e:
    self.ownership_unknown=True;raise Unavailable(f'owned native task/children observation unsupported: {e}') from e
 def capture(self,name,data,cleanup=False):
  row=self.counts[name];offset=row['retained'];row['observed']+=len(data)
  n=self.budget.append(self.raw[name],data,self.plan['raw_stream_bytes']-row['retained']);row['retained']+=n;row['discarded_observed']+=len(data)-n
  if name=='stdout':self.pending.extend(data[:n])
  try:self.log('read',stream=name,offset=offset,observed_bytes=len(data),retained_bytes=n,sha256=hashlib.sha256(data).hexdigest())
  except WitnessError:
   if not cleanup:raise
  if n!=len(data) and not cleanup:raise Invalid(name+' raw cap')
  if name=='stderr' and data and not cleanup:raise WitnessError('unexpected ordinary stderr; preserve for environment/behavior adjudication')
 def pump(self,end,quiet=False,cleanup=False):
  if not cleanup:
   self.check(self.deadline if quiet else end)
   if quiet and time.monotonic()>=end:return False
  remaining=max(0,min(end,self.deadline,self.study_deadline)-time.monotonic()) if not cleanup else max(0,end-time.monotonic())
  events=self.selector.select(min(0.05,remaining))
  for key,_ in events:
   try:data=os.read(key.fileobj.fileno(),65536)
   except BlockingIOError:continue
   if not data:
    self.selector.unregister(key.fileobj);key.fileobj.close()
    try:self.log('pipe-eof',stream=key.data)
    except WitnessError:
     if not cleanup:raise
   else:self.capture(key.data,data,cleanup)
  return bool(events)
 def before_write(self):
  # Retain any currently readable unsolicited output before the next request.
  for _ in range(4):
   if not self.selector.select(0):break
   self.pump(min(self.deadline,time.monotonic()+1))
  if self.pending:raise WitnessError('unexpected output before next host write')
 def send(self,text,atomic=False):
  self.before_write();data=text.encode('ascii');end=min(self.deadline,time.monotonic()+self.plan['record_seconds'])
  if self.counts['stdin']['observed']+len(data)>self.plan['stdin_bytes']:raise Invalid('stdin cap')
  if atomic and len(data)>os.fpathconf(self.child.stdin.fileno(),'PC_PIPE_BUF'):raise Unavailable('planned packet exceeds PIPE_BUF')
  self.log('write-request',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),atomic=atomic)
  offset=0
  while offset<len(data):
   self.check(end)
   try:n=os.write(self.child.stdin.fileno(),data[offset:])
   except BlockingIOError:self.pump(end);continue
   except InterruptedError:continue
   if n<=0:raise Invalid('nonpositive stdin write')
   actual=data[offset:offset+n];row=self.counts['stdin'];start=row['retained'];row['observed']+=n
   kept=self.budget.append(self.raw['stdin'],actual,self.plan['stdin_bytes']-row['retained']);row['retained']+=kept;row['discarded_observed']+=n-kept
   self.log('write',offset=start,actual_bytes=n,retained_bytes=kept,sha256=hashlib.sha256(actual).hexdigest())
   if kept!=n:raise Invalid('stdin retention/storage cap')
   offset+=n
   if atomic and n!=len(data):raise Unavailable('partial write invalidates planned atomic availability witness')
  self.child.stdin.flush();self.log('flush',stream='stdin')
 def expect(self,text):
  expected=text.encode('ascii');end=min(self.deadline,time.monotonic()+self.plan['record_seconds'])
  while len(self.pending)<len(expected):
   if not self.selector.get_map():raise WitnessError('process/streams ended before expected reply')
   self.pump(end)
   if not expected.startswith(bytes(self.pending[:len(expected)])):raise WitnessError('unexpected raw reply prefix')
  if bytes(self.pending[:len(expected)])!=expected:raise WitnessError('exact raw reply mismatch')
  del self.pending[:len(expected)];self.log('expected-bytes',bytes=len(expected),sha256=hashlib.sha256(expected).hexdigest())
 def line(self):
  end=min(self.deadline,time.monotonic()+self.plan['record_seconds'])
  while b'\n' not in self.pending:
   if not self.selector.get_map():raise WitnessError('missing output record')
   self.pump(end)
  i=self.pending.index(10)+1;line=bytes(self.pending[:i]);del self.pending[:i]
  if not line.isascii() or b'\r' in line:raise WitnessError('non-ASCII/CR output framing')
  return line
 def fragment_consumed(self,quiet_ms):
  command=getattr(termios,'FIONREAD',None)
  if command is None:raise Unavailable('FIONREAD unavailable: no fragment-consumption evidence')
  end=min(self.deadline,time.monotonic()+self.plan['record_seconds'])
  while True:
   self.check(end);value=array.array('i',[0])
   try:fcntl.ioctl(self.child.stdin.fileno(),command,value,True)
   except OSError as e:raise Unavailable(f'own-pipe FIONREAD unsupported: {e}') from e
   self.log('own-pipe-unread',bytes=value[0])
   if value[0]==0:break
   self.pump(end)
   if self.pending:raise WitnessError('reply to incomplete command')
  quiet_end=time.monotonic()+quiet_ms/1000
  self.log('fragment-consumed-quiet-begin',duration_ms=quiet_ms)
  while time.monotonic()<quiet_end:
   if self.pending:raise WitnessError('output before completing fragmented record')
   self.pump(min(quiet_end,self.deadline),quiet=True)
  if self.pending:raise WitnessError('output before final LF')
  self.log('fragment-consumed-quiet-end')
 def group_alive(self):
  if self.child is None:return False
  try:os.killpg(self.child.pid,0);return True
  except ProcessLookupError:return False
  except PermissionError:self.ownership_unknown=True;return True
 def finish(self,close_stdin):
  if close_stdin:self.child.stdin.close();self.log('stdin-eof')
  self.cleanup_started=time.monotonic();shared_end=min(self.hard_deadline,self.cleanup_started+self.plan['cleanup_seconds'])
  end=min(self.cleanup_started+self.plan['normal_completion_seconds'],shared_end-self.plan['term_grace_seconds']-self.plan['cleanup_observation_reserve_seconds'])
  while time.monotonic()<end:
   if self.child.poll() is not None and not self.selector.get_map() and not self.group_alive():
    self.cleanup_completed=time.monotonic();break
   self.pump(end,cleanup=True)
  if self.cleanup_completed is None:raise Invalid('normal completion timeout; remaining shared budget reserved for TERM/KILL and observation')
  if self.child.returncode!=0:raise WitnessError(f'unexpected native exit {self.child.returncode}')
  if self.pending:raise WitnessError('extra or partial shutdown stdout')
  if self.counts['stderr']['observed']:raise WitnessError('unexpected stderr')
  if any(r['discarded_observed'] for r in self.counts.values()) or self.events_lost:raise Invalid('incomplete raw/timestamp retention')
  self.normal_exit=True;self.log('normal-exit',returncode=0,stdin_kept_open=not close_stdin)
 def cleanup(self):
  if self.child is None:
   self.selector.close()
   for f in [*self.raw.values(),self.events]:f.close()
   return dict(confirmed=True,launched=False)
  self.cleanup_started=time.monotonic() if self.cleanup_started is None else self.cleanup_started
  end=min(self.hard_deadline,self.cleanup_started+self.plan['cleanup_seconds']);term_sent=False;kill_sent=False;term_at=None;kill_at=None
  def signal_group(sig):
   try:os.killpg(self.child.pid,sig)
   except ProcessLookupError:pass
   except OSError as e:
    self.ownership_unknown=True
    if len(self.cleanup_errors)<16:self.cleanup_errors.append(str(e))
  while self.cleanup_completed is None and time.monotonic()<end:
   if self.child.poll() is not None and not self.selector.get_map() and not self.group_alive():self.cleanup_completed=time.monotonic();break
   if not term_sent:
    term_at=time.monotonic();signal_group(signal.SIGTERM);term_sent=True
   if time.monotonic()-term_at>=self.plan['term_grace_seconds'] and not kill_sent:
    kill_at=time.monotonic();signal_group(signal.SIGKILL);kill_sent=True
   try:self.pump(end,cleanup=True)
   except BaseException as e:
    if len(self.cleanup_errors)<16:self.cleanup_errors.append(f'{type(e).__name__}: {e}')
  if self.cleanup_completed is None:
   kill_at=time.monotonic() if kill_at is None else kill_at;signal_group(signal.SIGKILL);kill_sent=True;self.child.poll()
   if self.child.returncode is not None and not self.selector.get_map() and not self.group_alive():self.cleanup_completed=time.monotonic()
  elapsed=(self.cleanup_completed or time.monotonic())-self.cleanup_started
  confirmed=self.cleanup_completed is not None and elapsed<=self.plan['cleanup_seconds'] and self.cleanup_completed<=self.hard_deadline and not self.ownership_unknown
  result=dict(confirmed=confirmed,launched=True,normal_exit=self.normal_exit,pid=self.child.pid,returncode=self.child.returncode,exit_code=self.child.returncode if self.child.returncode is not None and self.child.returncode>=0 else None,signal=-self.child.returncode if self.child.returncode is not None and self.child.returncode<0 else None,actual_return_observed=self.child.returncode is not None,cleanup_started_monotonic=self.cleanup_started,cleanup_completed_observed_monotonic=self.cleanup_completed,cleanup_elapsed_s=elapsed,term_sent=term_sent,kill_sent=kill_sent,term_attempted_monotonic=term_at,kill_attempted_monotonic=kill_at,unexpected_children=self.unexpected_children,ownership_unknown=self.ownership_unknown,errors=self.cleanup_errors)
  for key in list(self.selector.get_map().values()):
   try:self.selector.unregister(key.fileobj);key.fileobj.close()
   except OSError:pass
  self.selector.close()
  for f in [self.child.stdin,self.child.stdout,self.child.stderr,*self.raw.values(),self.events]:
   try:f.close()
   except OSError:pass
  return result

def do_steps(p,steps):
 for step in steps:
  p.log('step',keys=sorted(step))
  if 'write' in step:p.send(step['write'])
  if 'wait_own_pipe_unread_bytes' in step:
   assert step['wait_own_pipe_unread_bytes']==0
   p.fragment_consumed(step['require_no_output_for_ms'])
  for key in ['expect_exact','expect_exact_before_next_write_or_eof']:
   if key in step:p.expect(step[key])
  if 'expect_exit_code' in step:
   assert step['expect_exit_code']==0 and step['expect_remaining_stdout']==step['expect_stderr']==''
   p.finish(close_stdin=step.get('close_stdin_between_commands',False))

def status(line,wanted,last_cs):
 text=line.decode('ascii').removesuffix('\n')
 if text.startswith('move '):raise Unavailable('natural completion before required fourth-poll observations; no automatic retry')
 match=re.fullmatch(r'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?',text)
 if not match:raise WitnessError('expected live status, got another record')
 cs,sid,depth,remaining,total=map(int,match.groups()[:5]);pv=match[6]
 if pv is not None and (not pv or ' '.join(pv.split())!=pv):raise WitnessError('status path spacing')
 canonical=f'stat01: {cs:>6} {sid:>9} {depth:>5} {remaining:>3} {total:>3}'+(' '+pv if pv is not None else '')
 if canonical!=text or sid!=wanted['searchId'] or total!=wanted['total'] or not wanted['remaining_range_inclusive'][0]<=remaining<=wanted['remaining_range_inclusive'][1] or cs<last_cs:raise WitnessError('status width/order/N/root-count mismatch')
 return cs

def run_case(row,argv,directory,plan,budget,deadline):
 directory.mkdir();p=Process(directory,plan,budget,deadline);failure=None;category=None;checks=[]
 try:
  p.start(argv)
  if 'steps' in row:do_steps(p,row['steps'])
  else:
   p.send('\n'.join(row['setup'])+'\n');p.expect(row['setup_expected_stdout']);p.send(row['atomic_write'],atomic=True)
   if 'expect_order' in row:
    cs=-1
    for wanted in row['expect_order']:
     if 'exact' in wanted:p.expect(wanted['exact'])
     else:
      line=p.line();cs=status(line,wanted,cs);checks.append(dict(kind='observed-poll',search_id=wanted['searchId'],line_sha256=hashlib.sha256(line).hexdigest()))
    do_steps(p,row['after_abort_steps'])
   else:
    expected=HERE/row['expect_exact_file'];assert sha(expected)==row['expect_exact_file_sha256'];p.expect(expected.read_text('ascii'));do_steps(p,row['after_move_steps'])
 except BaseException as e:failure=f'{type(e).__name__}: {e}';category=getattr(e,'category','collection_invalid')
 finally:cleanup=p.cleanup()
 if not cleanup['confirmed']:failure=failure or 'whole-owned cleanup unconfirmed; parent intervention required';category='cleanup_unconfirmed'
 if failure is None and (not cleanup.get('normal_exit') or cleanup.get('returncode')!=0):failure='expected normal native completion was not observed';category='collection_invalid'
 raw={name:dict(path=str(directory/(name+'.raw')),**counts,sha256=sha(directory/(name+'.raw'))) for name,counts in p.counts.items()}
 result=dict(case=row['id'],complete=failure is None,failure=failure,disposition=category or 'directed_witness_pass',identity=p.identity,checks=checks,native=cleanup,raw=raw,event_bytes=p.event_bytes,events_discarded_observed=p.events_lost,retention_write_error=budget.last_write_error,performance_measurement=False,protocol_qualification=False)
 budget.result(directory/'result.json',result);return result

def main():
 plan=load(HERE/'plan.json');assert plan['normal_completion_seconds']+plan['term_grace_seconds']+plan['cleanup_observation_reserve_seconds']<=plan['cleanup_seconds']==5
 clearance_path=HERE/'execution-clearance.json';clearance=load(clearance_path)
 assert clearance['launch'] is True and clearance['quiet_window_clearance'] is True, 'INERT: no parent launch clearance'
 review=clearance['parent_review'];assert review and sha(review['path'])==review['sha256']
 assert Path(sys.executable).resolve()==Path(plan['python']) and sha(sys.executable)==plan['python_sha256']
 assert sorted(os.sched_getaffinity(0))==HELPERS==plan['helper_affinity'] and os.environ.get('TMPDIR')==plan['TMPDIR']
 assert not any(os.environ.get(k) for k in ['LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH','LD_AUDIT','NODE_OPTIONS','PYTHONPATH','PYTHONHOME'])
 pins=load(HERE/'input-pins.json')
 assert all(sha(path)==h for path,h in pins.items()) and all(sha(HERE/name)==h for name,h in load(HERE/'helper-pins.json').items())
 cases=load(HERE/'cases.json');proof=load(plan['source_proof']);engine=Path(cases['artifact'])
 assert proof['source72_graph']==plan['source72_graph'] and proof['image_sha256']==plan['engine_sha256']
 assert len(cases['cases'])==plan['maximum_cases']==4 and cases['argv']==[str(engine),'--work-clock=kingwcr']
 assert [r['id'] for r in cases['cases']]==['boundary-lf-fragment-idle-eof','boundary-crlf-book-idle-quit','four-observed-polls-then-abort','graceful-stop-queued-idle-force-completion']
 for row in cases['cases']:
  text=''.join(step.get('write','') for step in row.get('steps',[]))
  if 'setup' in row:text='\n'.join(row['setup'])+'\n'+row['atomic_write']+''.join(step.get('write','') for step in row.get('after_abort_steps',row.get('after_move_steps',[])))
  data=text.encode('ascii');assert len(data)<=plan['stdin_bytes'] and data.endswith(b'\n')
  for record in data.splitlines(keepends=True):
   assert record.endswith(b'\n') and len(record)<=1023
   payload=record[:-1].removesuffix(b'\r');assert b'\r' not in payload and b'\x00' not in payload and len(payload.split())<=40
 assert sha(engine)==cases['artifact_sha256']==plan['engine_sha256'] and engine.stat().st_size==plan['engine_bytes'] and engine.stat().st_mode&0o777==0o555
 for root in proof['verified_source_roots']:
  assert all(sha(Path(root)/name)==h for name,h in proof['native49_tools23'].items())
 closure=dict(pins)
 for name in load(HERE/'helper-pins.json'):closure[str(HERE/name)]=sha(HERE/name)
 for p in [HERE/'helper-pins.json',clearance_path,Path(review['path']),engine]:closure[str(p)]=sha(p)
 out=Path(plan['output']);assert not out.exists();out.mkdir();budget=Budget(plan)
 budget.result(out/'input-closure.json',closure);budget.result(out/'request-plan.json',cases)
 expected=(HERE/'graceful-first-stop-expected.stdout').read_bytes()
 with (out/'graceful-first-stop-expected.stdout').open('xb') as f:assert budget.append(f,expected,len(expected))==len(expected)
 started=time.monotonic();deadline=started+plan['study_seconds'];rows=[];failure=None
 try:
  for row in cases['cases']:
   if time.monotonic()>=deadline-plan['cleanup_seconds']:raise Invalid('whole-study deadline/cleanup reserve before next case')
   result=run_case(row,cases['argv'],out/row['id'],plan,budget,deadline);rows.append(result)
   if not result['complete']:break
  if any(not r['native']['confirmed'] for r in rows):raise Invalid('cleanup unconfirmed: stop without further source/hash work; parent intervention required')
  assert all(sha(path)==h for path,h in closure.items()), 'before/after input/helper/image mismatch'
  for root in proof['verified_source_roots']:assert all(sha(Path(root)/name)==h for name,h in proof['native49_tools23'].items()), 'source changed'
 except BaseException as e:failure=f'{type(e).__name__}: {e}'
 complete=failure is None and len(rows)==4 and all(r['complete'] for r in rows)
 summary=dict(complete=complete,failure=failure,cases=rows,all_owned_cleanup_confirmed=all(r['native']['confirmed'] for r in rows),engine_sha256=plan['engine_sha256'],source72_graph=plan['source72_graph'],input_sha256=closure,elapsed_host_wall_s=time.monotonic()-started,performance_measurement=False,protocol_qualification=False,no_retries=True,actual_outer_terminal_required=True)
 budget.result(out/'result.json',summary)
 print(json.dumps(dict(complete=complete,completed_cases=sum(r['complete'] for r in rows),attempted_cases=len(rows),failed_case=next((r['case'] for r in rows if not r['complete']),None),all_owned_cleanup_confirmed=summary['all_owned_cleanup_confirmed'],performance_measurement=False)))
 return 0 if complete else 1

if __name__=='__main__':sys.exit(main())
