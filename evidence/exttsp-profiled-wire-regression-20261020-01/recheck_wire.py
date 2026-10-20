from pathlib import Path
import hashlib,json,os,re
P=Path(__file__).resolve().parent
PLAN=json.loads((P/'plan.json').read_text())
R=P;KIT=Path('/home/legolas/king-spec/conformance');EXPECTED=PLAN['engine_sha256'];H=set(PLAN['helper_cpus'])
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
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
 assert set(os.sched_getaffinity(0))==H
 terminal=load(R/'tool-terminal.json');assert terminal['actual_tool_terminal_observed'] and terminal['exit_code']==0
 before={str(q):sha(q) for q in R.rglob('*') if q.is_file() and q.name not in ['independent.stdout','independent.stderr']}
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

 assert wire['pass'] and wire['checker_sha256']==PLAN['checker_sha256']
 assert (R/'wire-driver.stderr').read_bytes()==b''
 driver=load(R/'wire-driver.stdout');assert driver['passed'] and driver['cases']==8
 pids=load(R/'native-pids.json');assert [x['case'] for x in pids]==[x['id'] for x in checked]
 assert len({x['pid'] for x in pids})==8 and all(x['pid']>0 and x['argv']==[PLAN['engine']] for x in pids)
 for path,h in load(R/'inputs-before.json').items():assert sha(path)==h,path
 assert {path:sha(path) for path in before}==before
 result={'complete':True,'artifact_sha256':EXPECTED,'wire_fixtures':8,'wire_requests':24,'wire_raw_reconciliation':checked,'all_stdin_stdout_stderr_bytes_consumed':True,'native_pids':pids,'native_exit_codes':[x['observed_exit_code'] for x in wire['results']],'raw_bytes':sum((R/'wire'/c['id']/(s+'.raw')).stat().st_size for c in fixture['cases'] for s in ['stdin','stdout','stderr']),'inputs_before_after_equal':before,'original57_event_parser_and_raw_loop_literal':True,'engine_runs':0,'performance_sample':False,'limits':['Cross-stream timing is not reconstructed from separate raw files.','Original checker normal cleanup/wait observed all native exits; metadata hook retains PIDs without changing protocol.']}
 with (R/'independent-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'complete':True,'wire_fixtures':8,'wire_requests':24,'raw_bytes':result['raw_bytes'],'extra_engine_runs':0}))
if __name__=='__main__':main()
