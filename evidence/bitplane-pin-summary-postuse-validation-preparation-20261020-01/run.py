#!/usr/bin/env python3
"""Inert experiment57 post-use regression; original strict/wire methods unchanged."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/legolas/rook2')
PLAN=json.loads((HERE/'plan.json').read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def write(p,v):
 with Path(p).open('x') as f: json.dump(v,f,indent=2);f.write('\n')
def terminal(p):
 t=load(p)
 assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and (t.get('terminal_chunk_id') or t.get('terminal_chunk')),p
def check_inputs():
 for p,h in PLAN['input_sha256'].items(): assert sha(p)==h,p
 for p,h in PLAN['source_and_tool_sha256'].items(): assert sha(p)==h,p
 assert sha(PLAN['engine'])==PLAN['engine_sha256']
 assert sha(PLAN['profile'])==PLAN['profile_sha256']
 assert set(os.sched_getaffinity(0)) <= set(PLAN['helper_cpus'])
def run(argv,stem):
 command=['/usr/bin/taskset','-c','0-5,8-13',*map(str,argv)]
 with Path(str(stem)+'.stdout').open('xb') as so,Path(str(stem)+'.stderr').open('xb') as se:
  child=subprocess.Popen(command,cwd=ROOT,stdout=so,stderr=se)
  code=child.wait()
 record=dict(argv=command,cwd=str(ROOT),pid=child.pid,exit_code=code,actual_child_return_observed=True,
             stdout_sha256=sha(str(stem)+'.stdout'),stderr_sha256=sha(str(stem)+'.stderr'))
 write(str(stem)+'.child-terminal.json',record)
 assert code==0,record
 return record
def main():
 clearance=load(HERE/'execution-clearance.json')
 assert clearance.get('launch') is True and clearance.get('parent_review_accepted') is True
 assert clearance.get('untimed_parent_authorized') is True
 assert clearance['plan_sha256']==sha(HERE/'plan.json')
 check_inputs()
 build=Path(PLAN['use_build']);train=Path(PLAN['training']);out=Path(PLAN['output']);wire=out/'wire'
 for p in [build/'tool-terminal.json',train/'tool-terminal.json',train/'verify-tool-terminal.json']:terminal(p)
 assert not out.exists()
 b=load(build/'receipt.json');t=load(train/'training.json');v=load(train/'verification.json')
 assert b['pgo']['mode']=='profile-use' and b['pgo']['inputs_unchanged'] and t['complete'] and v['independent_remerge_byte_identical']
 assert b['source_sha256_before']==b['source_sha256_after']==t['engine_source_sha256']==PLAN['engine_source_sha256']
 assert b['tool_sha256_before']==b['tool_sha256_after']==PLAN['tool_source_sha256']
 assert b['source_identity_unchanged'] and b['tool_identity_unchanged'] and b['cargo_config_unchanged']
 assert b['pgo']['input_sha256_before']==b['pgo']['input_sha256_after']=={str(train/'merged.profdata'):sha(train/'merged.profdata'),str(train/'training.json'):sha(train/'training.json')}
 engine=Path(PLAN['engine']);identity=sha(engine);assert identity==b['binary_output']['sha256']
 out.mkdir()
 try:
  command=['/usr/bin/taskset','-c','0-5,8-13',str(engine)]
  strict=run(['/usr/bin/node',PLAN['replay_checker'],'--',*command],out/'profile-all')
  r=load(out/'profile-all.stdout');assert r['status']=='pass' and r['selectedCases']==PLAN['case_order'] and len(r['results'])==54
  for row in r['results']:
   assert row['command']==command+PLAN['runtime_modes']
   assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']==dict(code=0,signal=None) and row['stderr']=='' and row['error'] is None and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
  assert not (out/'profile-all.stderr').stat().st_size
  wire_command=run(['/usr/bin/python3',str(ROOT/'tools/check_live.py'),'--engine',str(engine),'--output',str(wire)],out/'wire-driver')
  w=load(wire/'receipt.json');assert w['pass'] and len(w['results'])==8 and sum(len(x['searches']) for x in w['results'])==24
  assert all(x['complete_streams'] and x['observed_exit_code']==x['exit_code']==0 for x in w['results'])
  assert w['engine_sha256_before']==w['engine_sha256_after']==identity
  assert sha(engine)==identity;check_inputs()
  write(out/'identity.json',dict(complete=True,artifact_sha256=identity,profile_sha256=sha(train/'merged.profdata'),strict_replays=54,wire_fixtures=8,wire_searches=24,replay_sha256=sha(out/'profile-all.stdout'),wire_receipt_sha256=sha(wire/'receipt.json'),strict_command=strict,wire_command=wire_command,execution_clearance_sha256=sha(HERE/'execution-clearance.json'),scope=PLAN['scope']))
 except BaseException as e:
  write(out/'failure.json',dict(complete=False,error=repr(e),artifact_sha256=identity))
  raise
if __name__=='__main__':main()
