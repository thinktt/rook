#!/usr/bin/env python3
"""Bounded exact-output runtime screen; fresh Rust state, optional resident WASM."""
import argparse,ctypes,hashlib,json,os,selectors,signal,statistics,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--wasm',type=Path,default=ROOT/'wasm/dist/rook.wasm')
p.add_argument('--modes',type=Path)
p.add_argument('--cases',default='profile-03,profile-04,profile-12,profile-17,profile-35,profile-43')
p.add_argument('--cpu',type=int,default=14)
p.add_argument('--repeats',type=int,default=3)
a=p.parse_args();a.output.mkdir();os.sched_setaffinity(0,{0});deadline=time.monotonic()+900
spec=Path('/home/legolas/king-spec/conformance/profiling')
work=json.loads((spec/'workloads.json').read_text());oracle=json.loads((spec/'replay-oracle.json').read_text())
cases=[next(c for c in work['cases'] if c['id']==name) for name in a.cases.split(',')]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
libc=ctypes.CDLL(None);libc.clock_getcpuclockid.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_int)]
clock=lambda pid:cpu_clock(pid)
def cpu_clock(pid):
 c=ctypes.c_int();assert libc.clock_getcpuclockid(pid,ctypes.byref(c))==0
 return time.clock_gettime_ns(c.value)
def placement(pid):
 rows=[]
 for task in (Path('/proc')/str(pid)/'task').iterdir():
  try:
   mask=(task/'status').read_text().split('Cpus_allowed_list:')[1].splitlines()[0].strip()
   assert mask==str(a.cpu),(task.name,mask)
   rows.append(int(task.name))
  except FileNotFoundError:pass
 assert rows;return rows
class Host:
 def __init__(self,flags,wasm=None):
  started=time.monotonic()
  self.child=subprocess.Popen(['node',*flags,str(ROOT/'experiments/wasm-tuning/session.mjs'),str(Path(wasm or a.wasm).resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=lambda:os.sched_setaffinity(0,{a.cpu}))
  self.buffer=b'';self.selector=selectors.DefaultSelector();self.selector.register(self.child.stdout,selectors.EVENT_READ)
  assert self.recv().get('started');self.startup=time.monotonic()-started;self.startupCpu=clock(self.child.pid)
 def recv(self):
  end=min(deadline,time.monotonic()+120)
  while b'\n' not in self.buffer:
   assert self.selector.select(max(0,end-time.monotonic())),'host deadline'
   chunk=os.read(self.child.stdout.fileno(),65536);assert chunk,'host exited: '+self.child.stderr.read().decode()
   self.buffer+=chunk
  line,self.buffer=self.buffer.split(b'\n',1);value=json.loads(line);assert 'error' not in value,value.get('error');return value
 def send(self,obj):self.child.stdin.write((json.dumps(obj)+'\n').encode());self.child.stdin.flush()
 def run(self,c):
  self.send(dict(op='prepare',lines=c['protocol']['recordsBeforeSearch']+['cm_parm rnd']));assert self.recv().get('ready')
  beforeTasks=placement(self.child.pid);before=clock(self.child.pid);start=time.monotonic_ns();self.send(dict(op='go'));assert self.recv()=={'event':'move'}
  stop=time.monotonic_ns();after=clock(self.child.pid);afterTasks=placement(self.child.pid);actual=self.recv();assert actual['complete'] and actual['quitStatus']==2 and actual['stderr']==''
  # The unchanged released comparator rechecks full posts/work/move below.
  return dict(cpuSeconds=(after-before)/1e9,wallSeconds=(stop-start)/1e9,beforeCpuNs=before,afterCpuNs=after,pid=self.child.pid,beforeTasks=beforeTasks,afterTasks=afterTasks,stdout=actual['stdout'],stderr=actual['stderr'],exit={'code':0,'signal':None},complete=True,error=None,startupSeconds=self.startup,startupCpuSeconds=self.startupCpu/1e9)
 def close(self):
  self.send(dict(op='close'));assert self.recv().get('closed');self.child.stdin.close();assert self.child.wait(timeout=5)==0;assert self.child.stderr.read()==b'';self.selector.close()
 def kill(self):
  if self.child.poll() is None:os.killpg(self.child.pid,signal.SIGKILL);self.child.wait()
  self.selector.close()
default_modes={'cold':dict(flags=[],warm=0),'resident':dict(flags=[],warm=2),'eager':dict(flags=['--no-liftoff','--no-wasm-tier-up','--no-wasm-lazy-compilation'],warm=0)}
modes=json.loads(a.modes.read_text()) if a.modes else default_modes
(a.output/'screen.py').write_bytes(Path(__file__).read_bytes())
source=[p for folder in [ROOT/'src',ROOT/'diagnostic/src',ROOT/'wasm/engine/src',ROOT/'wasm/diagnostic/src'] for p in folder.rglob('*.rs')]+[ROOT/'wasm/abi.rs']
pins={str(f):sha(f) for f in source+[Path(c.get('wasm',a.wasm)).resolve() for c in modes.values()]+([a.modes.resolve()] if a.modes else [])+[Path('/usr/bin/node'),ROOT/'wasm/runtime.mjs',Path(__file__),ROOT/'experiments/wasm-tuning/session.mjs',ROOT/'experiments/wasm-tuning/recheck.mjs',spec/'workloads.json',spec/'replay-oracle.json',spec/'replay-check.mjs']}
plan=dict(nodeVersion=subprocess.check_output(['node','--version'],text=True).strip(),modes=modes,cases=[c['id'] for c in cases],repeats=a.repeats,cpu=a.cpu,pins=pins,scope='Search CPU to selected-move JSON receipt; complete fresh Rust Session per search, compiled WASM retained only in resident mode. Logical quit2 projected to clean comparator exit. No chess caches retained between searches.')
(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
summary=dict(complete=False,runs=[],medians={},startedAt=time.time());hosts=[]
try:
 for i,c in enumerate(cases):
  for r in range(a.repeats):
   names=list(modes);shift=(i+r)%len(names);names=names[shift:]+names[:shift]
   for mode in names:
    config=modes[mode];h=Host(config['flags'],config.get('wasm'));hosts.append(h)
    for warm in range(config['warm']):
     row=h.run(c);row.update(case=c['id'],mode=mode,repeat=r,warmup=True,warmIndex=warm);summary['runs'].append(row)
    row=h.run(c);row.update(case=c['id'],mode=mode,repeat=r,warmup=False);summary['runs'].append(row);h.close();hosts.remove(h)
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 for mode in modes:
  medians={c['id']:statistics.median(x['cpuSeconds'] for x in summary['runs'] if x['mode']==mode and x['case']==c['id'] and not x['warmup']) for c in cases}
  summary['medians'][mode]=dict(cases=medians,total=sum(medians.values()))
 assert all(sha(Path(path))==digest for path,digest in pins.items()),'input changed'
 subprocess.run(['node',str(ROOT/'experiments/wasm-tuning/recheck.mjs'),str(a.output)],check=True,timeout=30)
 summary['complete']=True
except BaseException as error:summary['failure']=str(error);raise
finally:
 for h in hosts:h.kill()
 summary['finishedAt']=time.time();(a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary['medians']),flush=True)
