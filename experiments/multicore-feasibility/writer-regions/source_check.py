"""Source-only check of the fixed field relocation; starts no process."""
from pathlib import Path
import re,hashlib,json

def normalize(t):
 t=t.replace('shared.cells.sides[0].output','shared.cells.white_output').replace('shared.cells.sides[1].output','shared.cells.black_output')
 t=t.replace('cells.input.value.get()', 'cells.input.get()').replace('shared.cells.sides','shared.readers').replace('shared.owner.value','shared.control')
 for f,prefix in [('request','publication'),('readers','lifecycle'),('stop','lifecycle'),('active_scopes','lifecycle'),('waiting','latch'),('wake','waits'),('sleep','waits'),('completed','waits')]:t=t.replace('shared.'+prefix+'.'+f,'shared.'+f)
 return t
def extract(t,n):
 m=re.search(r'^([ ]{0,4})(?:(?:pub\(crate\)|unsafe) )?fn '+n+r'\b',t,re.M);assert m,n
 first=t[m.start():].splitlines()[0]
 if first.rstrip().endswith('}'):return first
 end=re.search(r'^'+m[1]+r'}$',t[m.end():],re.M);assert end,n
 return t[m.start():m.end()+end.end()]

def check(control,candidate):
 a=(Path(control)/'src/colors_worker.rs').read_text()
 b=(Path(candidate)/'src/colors_worker.rs').read_text()
 names=['failed_spawn','start_active_scope','start_call_scope','dispatch','owner_ready','is_complete_now','complete','check_running','failure','readiness_report','shutdown','run_active','compute_input','all_state','quiescent','all_terminal','terminal','both_done','control_lock','signal_completion','wait_completion','publish_terminal','retire_flight','release_scope','park','wait_control']
 values={}
 for n in names:
  x,y=extract(a,n),normalize(extract(b,n));assert x==y,n;values[n]=hashlib.sha256(x.encode()).hexdigest()
 assert 'fence(Ordering::SeqCst)' not in b
 assert b.count('unsafe impl Sync')==a.count('unsafe impl Sync')==1
 for n in ['Packet','SideOutput','Metadata','Flight','Control','Metric','Readiness']:
  pattern=r'^(?:struct|enum) '+n+r'\b[\s\S]*?^}'
  assert re.search(pattern,a,re.M)[0]==re.search(pattern,b,re.M)[0],n
 return dict(identicalOperationalBodiesAfterFieldPathNormalization=len(values),sha256=values,originalRmwProtocol=True,narrowCellsSyncCount=1)

if __name__=='__main__':
 print(json.dumps(check('/home/legolas/rook2-experiments/workspaces/q-owner-local-20261026-01','/home/legolas/rook2-experiments/workspaces/writer-regions-20261026-01')))
