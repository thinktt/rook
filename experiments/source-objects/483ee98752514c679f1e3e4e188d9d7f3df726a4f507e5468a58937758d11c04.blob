#!/usr/bin/env python3
"""Offline original54 and literal8/24 raw reconciliation; never launches an engine."""
from pathlib import Path
import hashlib,json,os,re,subprocess
P=Path(__file__).resolve().parent
PLAN=json.loads((P/'plan.json').read_text())
R=Path(PLAN['output']);KIT=Path('/home/legolas/king-spec/conformance')
EXPECTED=PLAN['engine_sha256'];H=set(PLAN['helper_cpus'])
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d):
 with (P/name).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def command_receipt(path):
 d=load(path);assert d['exit_code']==0 and d['actual_child_return_observed'],path
 assert isinstance(d['pid'],int) and d['pid']>0
 for name in ['stdout','stderr']:
  stem=str(path).removesuffix('.child-terminal.json')
  assert sha(stem+'.'+name)==d[name+'_sha256']
 return d

def event(line):
 if line.startswith('move '):
  assert re.fullmatch(r'move [a-h][1-8][a-h][1-8][qrbn]?',line),line
  return {'type':'move','move':line[5:]}
 if line.startswith('stat01: '):
  m=re.fullmatch(r'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?',line);assert m,line
  cs,sid,depth,remaining,total=map(int,m.groups()[:5])
  return dict(type='status',engineCentiseconds=cs,searchId=sid,depthToken=depth,remaining=remaining,total=total,pv=(m[6] or '').replace('0','O'))
 m=re.fullmatch(r' *(-?\d+) +([+-]?\d+) +(\d+) +(\d+)(?: (.*))?',line);assert m,line
 depth,score,cs,sid=map(int,m.groups()[:4])
 return dict(type='post',depthToken=depth,evaluation=score,engineCentiseconds=cs,searchId=sid,pv=(m[5] or '').replace('0','O'))

def main():
 assert os.sched_getaffinity(0)<=H
 # Gate precedes every regression raw-file read.
 terminal=load(R/'tool-terminal.json')
 assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code']==0 and (terminal.get('terminal_chunk_id') or terminal.get('terminal_chunk'))
 dependencies={Path(p) for p in PLAN['input_sha256']}
 dependencies.update(Path(p) for p in PLAN['source_and_tool_sha256'])
 dependencies.update([Path(PLAN['engine']),Path(PLAN['profile']),P/'plan.json',P/'execution-clearance.json',P/'recheck.py',P/'recheck.mjs'])
 dependencies.update(p for p in R.rglob('*') if p.is_file())
 before={str(p):sha(p) for p in sorted(dependencies)}
 for p,h in {**PLAN['input_sha256'],**PLAN['source_and_tool_sha256']}.items():assert before[p]==h,p
 assert before[PLAN['engine']]==EXPECTED and before[PLAN['profile']]==PLAN['profile_sha256']
 identity=load(R/'identity.json');assert identity['complete'] and identity['artifact_sha256']==EXPECTED and identity['profile_sha256']==PLAN['profile_sha256']
 assert (identity['strict_replays'],identity['wire_fixtures'],identity['wire_searches'])==(54,8,24)
 assert identity['replay_sha256']==sha(R/'profile-all.stdout') and identity['wire_receipt_sha256']==sha(R/'wire/receipt.json')
 assert identity['execution_clearance_sha256']==sha(P/'execution-clearance.json')
 strict=command_receipt(R/'profile-all.child-terminal.json');live=command_receipt(R/'wire-driver.child-terminal.json')
 assert identity['strict_command']==strict and identity['wire_command']==live
 prefix=['/usr/bin/taskset','-c','0-5,8-13']
 assert strict['argv']==prefix+['/usr/bin/node',str(KIT/'profiling/replay-check.mjs'),'--','/usr/bin/taskset','-c','0-5,8-13',PLAN['engine']]
 assert live['argv']==prefix+['/usr/bin/python3','/home/legolas/rook2/tools/check_live.py','--engine',PLAN['engine'],'--output',str(R/'wire')]
 assert (R/'profile-all.stderr').read_bytes()==b'' and (R/'wire-driver.stderr').read_bytes()==b''
 fixture=load(KIT/'fixtures/interrupted-sessions-v1.json');wire=load(R/'wire/receipt.json')
 assert wire['engine']==PLAN['engine'] and wire['engine_sha256_before']==wire['engine_sha256_after']==EXPECTED
 assert wire['effective_affinity']==sorted(H) and wire['fixture_sha256']==sha(KIT/'fixtures/interrupted-sessions-v1.json')
 assert len(wire['results'])==len(fixture['cases'])==8
 checked=[];total_searches=0
 for case,row in zip(fixture['cases'],wire['results']):
  assert row['id']==case['id'] and row['observed_exit_code']==row['exit_code']==0 and row['complete_streams']
  directory=R/'wire'/case['id'];raw={}
  for stream in ['stdin','stdout','stderr']:
   path=directory/(stream+'.raw');data=path.read_bytes();rec=row['raw'][stream]
   assert len(data)==rec['bytes'] and hashlib.sha256(data).hexdigest()==rec['sha256'];assert data.isascii();raw[stream]=data;None # raw file is already in the closed-tree snapshot
  assert raw['stderr']==b'' and raw['stdout'].endswith(b'\n') and b'\r' not in raw['stdout']
  output=raw['stdout'].decode('ascii').splitlines();at=0;commands=[];searches=[]
  assert len(case['request']['input']['searches'])==len(case['expected']['results'])==3
  for request,answer in zip(case['request']['input']['searches'],case['expected']['results']):
   commands.extend(request['commands']+[f"time {request['allowanceCs']}",'cm_parm','go']+request['queued'])
   for text in request['commands']:
    if text.startswith('cm_parm '):assert output[at]==' '.join(text.split());at+=1
   assert output[at]=='cm_parm';at+=1
   events=[]
   for expected_event in answer['events']:
    actual_event=event(output[at]);at+=1;assert actual_event==expected_event;events.append(actual_event)
   abort=bool(request['queued'] and request['queued'][-1]=='force')
   if abort:assert output[at]=='aborting search ...';at+=1
   searches.append({'events':events,'abort':abort});total_searches+=1
  commands.append('quit');assert raw['stdin']==('\n'.join(commands)+'\n').encode('ascii')
  assert at==len(output);assert len(searches)==len(row['searches'])==3
  for got,recorded in zip(searches,row['searches']):assert got['events']==recorded['events'] and got['abort']==recorded['abort']
  checked.append({'id':case['id'],'searches':3,'all_stdin_stdout_stderr_bytes_consumed':True,'normal_exit':0})
 assert total_searches==24

 argv=['/usr/bin/node',str(P/'recheck.mjs')]
 with (P/'recheck-original54.stdout').open('xb') as so,(P/'recheck-original54.stderr').open('xb') as se:
  child=subprocess.Popen(argv,stdout=so,stderr=se);code=child.wait()
 write('recheck-original54-terminal.json',dict(argv=argv,pid=child.pid,exit_code=code,actual_child_return_observed=True,engine_runs=0))
 assert code==0 and (P/'recheck-original54.stderr').read_bytes()==b''
 original=load(P/'recheck-original54-result.json');assert original['complete'] and original['original_checkReplay_calls']==54 and original['engine_runs']==0
 assert {p:sha(p) for p in before}==before
 write('recheck-result.json',dict(complete=True,exact_artifact_sha256=EXPECTED,strict54=54,original_checkReplay_calls=54,wire_fixtures=8,wire_searches=24,wire_raw_reconciliation=checked,strict_raw_bytes=sum(x['stdoutBytes']+x['stderrBytes'] for x in original['checked']),wire_raw_bytes=sum((R/'wire'/c['id']/(stream+'.raw')).stat().st_size for c in fixture['cases'] for stream in ['stdin','stdout','stderr']),dependencies_before_after=before,engine_runs=0,native_test_runs=0,limits=['Strict stdin is bound via original runner/workloads; no separate strict stdin file was retained.','All wire stdin/stdout/stderr bytes reconciled to original fixtures; cross-stream timing is not reconstructed.','Wire native exit codes retained; receipt exposes no individual native PIDs.','No native tests executed here; generic193-library proof is not full195; no new qualification.']))
 print(json.dumps(dict(complete=True,artifact_sha256=EXPECTED,strict54=54,wire8=8,wire_searches24=24,engine_runs=0)))
if __name__=='__main__':
 try:main()
 except BaseException as e:
  write('recheck-failure.json',dict(complete=False,error=repr(e),engine_runs=0))
  raise
