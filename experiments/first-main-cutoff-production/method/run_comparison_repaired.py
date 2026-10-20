#!/usr/bin/python3
"""One immutable1800-second clock across sequential native stages and gaps."""
import ctypes,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent;stage=sys.argv[1]
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
resources=load(B/'resources.json');plan=load(B/'comparison-repair-pipeline-plan.json');assert stage in resources['stageSeconds']
assert sorted(os.sched_getaffinity(0))==resources['helpers'] and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
for p,h in plan['pins'].items():assert sha(p)==h,p
assert ctypes.CDLL(None).prctl(36,1,0,0,0)==0
clock=B/'lane-clock.json'
if stage=='instrumented':
 assert not clock.exists();save(clock,{'start_monotonic':time.monotonic(),'seconds':1800,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'basis':'Immediately before first instrumented native build; all gaps/stages/closure included; no resets.'})
c=load(clock);assert c['seconds']==1800 and c['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
deadline=min(c['start_monotonic']+1800,time.monotonic()+resources['stageSeconds'][stage]);assert time.monotonic()<deadline
out=B/'stages'/(stage+'-prelaunch-repair');out.mkdir();cfg=plan['stages'][stage]
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));resource.setrlimit(resource.RLIMIT_FSIZE,(256*1024**2,256*1024**2))
owned={}
def scan(pid):
 try:
  fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split();owned.setdefault(pid,fields[19])
  children=Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
 except (FileNotFoundError,ProcessLookupError):return
 for child in children:scan(int(child))
def live():
 rows=[]
 for pid,start in owned.items():
  try:
   fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
   if fields[19]==start and fields[0]!='Z':rows.append(pid)
  except (FileNotFoundError,ProcessLookupError):pass
 return rows
def reap():
 rows=[]
 while True:
  try:
   pid,status=os.waitpid(-1,os.WNOHANG)
   if not pid:break
   rows.append({'pid':pid,'status':status})
  except ChildProcessError:break
 return rows
failure=None;cleanup=[]
with (out/'stdout').open('xb') as a,(out/'stderr').open('xb') as b:
 child=subprocess.Popen(cfg['argv'],cwd=cfg['cwd'],stdout=a,stderr=b,stdin=subprocess.DEVNULL,start_new_session=True,preexec_fn=limits)
 save(out/'launch.json',{'argv':cfg['argv'],'cwd':cfg['cwd'],'pid':child.pid,'pgid':child.pid,'stageLimitSeconds':resources['stageSeconds'][stage],'remainingAggregateSeconds':c['start_monotonic']+1800-time.monotonic(),'resourceSha256':sha(B/'resources.json'),'clockSha256':sha(clock)})
 try:
  while child.poll() is None:
   scan(child.pid)
   if time.monotonic()>=deadline:failure='stage-or-aggregate-deadline'
   elif a.tell()+b.tell()>64*1024**2:failure='outer-stream-cap'
   if failure:break
   time.sleep(.05)
 except BaseException as error:failure=repr(error)
 if failure:
  scan(child.pid)
  # Pair comparators use their own sessions; declared launch records close
  # the interval between a spawn and the next observed-tree sample.
  groups=[child.pid]
  for p in (B/'pair/collection').glob('*/launch.json'):
   try:groups.append(load(p)['pgid'])
   except (OSError,ValueError,KeyError):pass
  for sig in [signal.SIGTERM,signal.SIGKILL]:
   for pid in reversed(live()):
    try:os.kill(pid,sig)
    except ProcessLookupError:pass
   for pgid in groups:
    try:os.killpg(pgid,sig)
    except ProcessLookupError:pass
   try:child.wait(timeout=2 if sig==signal.SIGTERM else 5)
   except subprocess.TimeoutExpired:pass
  child.wait(timeout=2)
 else:child.wait()
cleanup+=reap();remaining=live()
if remaining:failure=failure or 'observed-owned-process-remains'
if time.monotonic()>c['start_monotonic']+1800:failure=failure or 'aggregate-deadline'
result={'stage':stage,'pid':child.pid,'actualChildReturnObserved':True,'exit_code':child.returncode,'failure':failure,'remainingOwnedPids':remaining,'observedOwnedPids':sorted(owned),'orphanWaits':cleanup,'elapsedLaneSeconds':time.monotonic()-c['start_monotonic'],'clockSha256':sha(clock)}
save(out/'child-terminal.json',result);print(json.dumps(result),flush=True)
print((out/'stdout').read_text()[-2400:],flush=True);print((out/'stderr').read_text()[-2000:],flush=True)
sys.exit(0 if child.returncode==0 and failure is None else 1)
