#!/usr/bin/env python3
"""One exact public CLI witness, blocked without explicit post-CPU clearance."""
from pathlib import Path
import fcntl,hashlib,json,os,selectors,signal,subprocess,sys,time
HERE=Path(__file__).resolve().parent
H=[0,1,2,3,4,5,8,9,10,11,12,13]
ENGINE=Path('/home/legolas/rook2/evidence/pressure-value-static-pgo-use-build-20261019-01/rook2-exact')
ENGINE_SHA='c3166899f9380812b0fcb114d613021ba308699e46b0f7de48ffafaf4ff0e5a7'
COMMANDS=['xboard','force','setboard 8/8/8/3Pk3/8/8/8/K7 w - e6 0 1','d5e6','go']
WALL_SECONDS=10;CLEANUP_SECONDS=5;SOFT_RAW=65536;MAX_PIPE=1048576;CHUNK=4096
HARD_RAW=SOFT_RAW+2*MAX_PIPE+CHUNK
load=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def save(p,v):
 with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
def guard():
 c=load(HERE/'execution-clearance.json');p=load(HERE/'plan.json')
 assert c['authorized'] is True and c['cpu_window_closed'] is True and c['all_conflicting_jobs_terminal'] is True
 assert c['scope']=='exact40-king-victim-one-public-process-no-timing'
 for key in ['parent_explicit_clearance_actual','cpu_window_actual_terminal','cpu_window_independent_terminal']:
  assert isinstance(c[key],str) and c[key].strip(),key
 assert c['plan_sha256']==sha(HERE/'plan.json') and c['runner_sha256']==sha(Path(__file__))
 assert c['engine_sha256']==ENGINE_SHA==p['engine_sha256']==sha(ENGINE)
 assert p['commands']==COMMANDS and p['expected']==dict(stdout_hex='',stderr_hex='',exit_code=1,signal=None)
 assert sorted(os.sched_getaffinity(0))==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 for key in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS','ROOK2_WIRE_TAP_CONFIG']:
  assert not os.environ.get(key),key
 for path,digest in p['input_sha256'].items():assert sha(Path(path))==digest,path
 return p

def cleanup(child):
 deadline=time.monotonic()+CLEANUP_SECONDS;signals=[]
 if child.poll() is None:
  try:os.killpg(child.pid,signal.SIGTERM);signals.append('SIGTERM')
  except ProcessLookupError:pass
  try:child.wait(timeout=min(.5,max(0,deadline-time.monotonic())))
  except subprocess.TimeoutExpired:pass
 if child.poll() is None:
  try:os.killpg(child.pid,signal.SIGKILL);signals.append('SIGKILL')
  except ProcessLookupError:pass
  try:child.wait(timeout=max(0,deadline-time.monotonic()))
  except subprocess.TimeoutExpired:pass
 return dict(signals=signals,reconciled=child.poll() is not None,returncode=child.returncode)

def main():
 plan=guard();out=HERE/'run';assert not out.exists();out.mkdir()
 planned=('\n'.join(COMMANDS)+'\n').encode('ascii');(out/'stdin.planned.raw').write_bytes(planned)
 result=dict(complete=False,pass_witness=False,failure=None,command=[str(ENGINE)],native_children_started=0,
  expected=plan['expected'],go_fully_flushed=False,quit_sent=False,stdin_eof_sent_before_exit=False,
  stdout_bytes=0,stderr_bytes=0,capture_complete=False,capture_truncated=False,cleanup=None,
  limits=dict(wall_seconds=WALL_SECONDS,cleanup_seconds=CLEANUP_SECONDS,soft_raw_bytes=SOFT_RAW,hard_raw_bytes=HARD_RAW),
  measurement='Functional protocol/exit witness only; operational deadlines are not CPU benchmark data')
 child=None;sel=selectors.DefaultSelector();streams={};opened=[];deadline=time.monotonic()+WALL_SECONDS
 try:
  raw={name:(out/(name+'.raw')).open('xb') for name in ['stdout','stderr']};opened.extend(raw.values())
  sent=(out/'stdin.sent.raw').open('xb');opened.append(sent)
  child=subprocess.Popen([str(ENGINE)],cwd='/home/legolas/rook2',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0,start_new_session=True)
  result.update(native_children_started=1,native_pid=child.pid,native_inherited_affinity=sorted(os.sched_getaffinity(child.pid)))
  assert result['native_inherited_affinity']==H
  save(out/'launch.json',dict(command=[str(ENGINE)],native_pid=child.pid,engine_sha256=ENGINE_SHA,stdin_bytes=len(planned),normal_cli=True,seed_override=False,helper_affinity=H))
  for name,pipe in [('stdout',child.stdout),('stderr',child.stderr)]:
   capacity=fcntl.fcntl(pipe.fileno(),fcntl.F_GETPIPE_SZ);assert 0<capacity<=MAX_PIPE
   result[name+'_pipe_capacity']=capacity;os.set_blocking(pipe.fileno(),False);sel.register(pipe,selectors.EVENT_READ,name);streams[name]=pipe
  for command in COMMANDS:
   assert child.poll() is None,'native exited before full command sequence/go flush'
   remaining=memoryview((command+'\n').encode('ascii'))
   while remaining:
    written=child.stdin.write(remaining);assert written and written>0
    sent.write(remaining[:written]);remaining=remaining[written:]
   child.stdin.flush();sent.flush()
   if command=='go':result['go_fully_flushed']=True
  total=0
  while sel.get_map() or child.poll() is None:
   if time.monotonic()>=deadline:raise TimeoutError('native wall/drain deadline')
   for key,_ in sel.select(timeout=min(.05,max(0,deadline-time.monotonic()))):
    data=os.read(key.fileobj.fileno(),min(CHUNK,HARD_RAW-total+1))
    if not data:sel.unregister(key.fileobj);continue
    raw[key.data].write(data);raw[key.data].flush();result[key.data+'_bytes']+=len(data);total+=len(data)
    if total>SOFT_RAW:raise RuntimeError('raw byte admission cap exceeded; owned cleanup and bounded drain required')
  result['native_returncode']=child.wait(timeout=max(.001,deadline-time.monotonic()))
  result['capture_complete']=True
 except BaseException as error:
  result['failure']=f'{type(error).__name__}: {error}'
  if child is not None:
   result['cleanup']=cleanup(child)
   # Keep all observed bytes, including the cap-triggering chunk. Drain buffered
   # bytes after owned cleanup; HARD_RAW is finite and any truncation is fatal.
   drain_deadline=time.monotonic()+1
   total=result['stdout_bytes']+result['stderr_bytes']
   while sel.get_map() and time.monotonic()<drain_deadline and total<=HARD_RAW:
    for key,_ in sel.select(timeout=.02):
     if total>HARD_RAW:break
     data=os.read(key.fileobj.fileno(),min(CHUNK,HARD_RAW-total+1))
     if not data:sel.unregister(key.fileobj);continue
     raw[key.data].write(data);raw[key.data].flush();result[key.data+'_bytes']+=len(data);total+=len(data)
   result['capture_complete']=not bool(sel.get_map())
   result['capture_truncated']=not result['capture_complete'] or total>HARD_RAW
   result['native_returncode']=child.poll()
 finally:
  # Success must be an actual child exit while stdin stayed open. Only now
  # close stdin; EOF/quit cannot cause the expected exit1.
  if child is not None:
   alive=child.poll() is None
   result['stdin_eof_sent_before_exit']=alive
   if alive:result['cleanup_after_unreconciled_exit']=cleanup(child)
   if child.stdin is not None:child.stdin.close()
   result['native_returncode']=child.poll()
  for stream in opened:stream.close()
  sel.close()
  for stream in streams.values():stream.close()
 code=result.get('native_returncode');result['native_exit']=dict(code=code if code is not None and code>=0 else None,signal=-code if code is not None and code<0 else None)
 result['native_exit_actually_observed']=child is not None and code is not None
 result['engine_sha256_after']=sha(ENGINE)
 result['raw_sha256']={name:sha(out/name) for name in ['stdin.planned.raw','stdin.sent.raw','stdout.raw','stderr.raw'] if (out/name).exists()}
 if result['failure'] is None:
  try:
   assert result['native_children_started']==1 and result['go_fully_flushed'] and not result['stdin_eof_sent_before_exit']
   assert result['native_exit_actually_observed'] and result['native_exit']==dict(code=1,signal=None)
   assert result['capture_complete'] and not result['capture_truncated'] and result['engine_sha256_after']==ENGINE_SHA
   assert (out/'stdin.sent.raw').read_bytes()==planned and (out/'stdout.raw').read_bytes()==(out/'stderr.raw').read_bytes()==b''
   result['pass_witness']=True
  except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 result['complete']=result['native_exit_actually_observed'] and result['capture_complete']
 save(out/'result.json',result);print(json.dumps(result,sort_keys=True));return 0 if result['pass_witness'] else 1
if __name__=='__main__':sys.exit(main())
