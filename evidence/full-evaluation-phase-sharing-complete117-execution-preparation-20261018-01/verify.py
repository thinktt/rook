#!/usr/bin/env python3
"""Bounded offline phase-sharing native/strict/wire identity proof; no engines."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,tarfile
P=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence')
PRE=E/'full-evaluation-phase-sharing-preparation-20261018-01'
B=E/'full-evaluation-phase-sharing-generic-build-20261018-01'
N=E/'full-evaluation-phase-sharing-native-frozen-validation-20261018-01'
OLD=E/'full-evaluation-phase-sharing-native-validation-20261018-01'
R=E/'full-evaluation-phase-sharing-regression-validation-20261018-01'
KIT=Path('/home/legolas/king-spec/conformance')
EXPECTED='a26e8bef2fc8e0a39112d38c68c0b23c7efa964eb30cb899bb50935bc55c1a65'
H={0,1,2,3,4,5,8,9,10,11,12,13}
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d):
 with (P/name).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def outer(path,session,final):
 d=load(path);assert d['actual_tool_terminal_observed'] and d['exit_code']==0 and d['session_id']==session and d['terminal_chunk_id']==final,path
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
 assert os.sched_getaffinity(0)==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 binding=load(PRE/'execution-binding.json');m=binding['source69'];b=load(B/'receipt.json');s=Path(b['crate'])
 assert binding['parent_source_review_complete'] and len(m)==69
 dependencies={PRE/name for name in ['execution-binding.json','parent-source-review.json','validate.py','selection.json']}
 dependencies.update(Path(path) for path in binding['helpers_and_inputs'])
 for tree in [B,N,OLD,R]:dependencies.update(x for x in tree.rglob('*') if x.is_file())
 dependencies.update(s/name for name in m)
 dependencies.add(Path(b['binary_output']['path']))
 dependencies.update(Path(row['original_executable']) for row in load(N/'result.json')['tests'].values())
 dependencies.update([P/'verify.py',P/'original-replay54.mjs',Path('/usr/bin/node'),Path('/usr/bin/python3'),Path('/usr/bin/taskset')])
 for name in ['rustc','cargo']:dependencies.add(Path(b['toolchain'][name]['argv'][0]))
 dependencies.update([KIT/'profiling/workloads.json',KIT/'profiling/replay-oracle.json',KIT/'fixtures/interrupted-sessions-v1.json',KIT/'run.mjs'])
 # Recursive closure of actual relative imports, including parsePost's benchmark.mjs.
 queue=[KIT/'profiling/replay-check.mjs',KIT/'run.mjs'];js=set()
 while queue:
  path=queue.pop().resolve()
  if path in js:continue
  js.add(path)
  for rel in re.findall(r"(?:from\s*|import\s*\(?\s*)['\"](\.[^'\"]+)['\"]",path.read_text()):queue.append((path.parent/rel).resolve())
 dependencies.update(js)
 before={str(path):sha(path) for path in sorted(dependencies)}
 write('input-sha256-before.json',before);write('public-js-import-closure.json',{str(p):sha(p) for p in sorted(js)})
 for path,h in binding['helpers_and_inputs'].items():assert sha(path)==h,path
 outer(B/'tool-terminal.json',24846,'1ca8e8');outer(OLD/'tool-terminal.json',74138,'529558');outer(N/'tool-terminal.json',None,'e4d2b4');outer(R/'tool-terminal.json',33995,'cc7219')
 native_map={k:v for k,v in m.items() if not k.startswith('tools/')};tool_map={k:v for k,v in m.items() if k.startswith('tools/')}
 assert len(native_map)==46 and len(tool_map)==23
 assert b['source_sha256_before']==b['source_sha256_after']==native_map
 assert b['tool_sha256_before']==b['tool_sha256_after']==tool_map
 assert b['cargo_config_sha256_before']==b['cargo_config_sha256_after']=={}
 assert b['mode']=='generic' and b['pgo']['mode']=='none' and b['rust_flags']==['-C','target-cpu=x86-64'] and b['engine_runs']==0
 assert b['outcome']=='build-succeeded-with-stable-input-snapshot' and b['cargo_exit_code']==0 and b['build_affinity']==sorted(H)
 assert b['binary_output']['sha256']==EXPECTED==sha(B/'rook2-exact')==sha(b['binary_output']['path'])
 for name in ['rustc','cargo']:
  assert b['toolchain'][name]['exit_code']==0 and sha(b['toolchain'][name]['argv'][0])==b['toolchain'][name+'_executable_sha256']
 actual={'Cargo.toml','Cargo.lock'}|{str(x.relative_to(s)) for root in [s/'src',s/'tools'] for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
 assert actual==set(m)
 for name,h in m.items():assert sha(s/name)==sha(B/'source-before'/name)==h
 for row in b['logs'].values():assert (B/row['path']).stat().st_size==row['bytes'] and sha(B/row['path'])==row['sha256']
 ar=load(B/'archive-receipt.json');assert ar['files']==69 and ar['binary_sha256']==EXPECTED and ar['verified_against_build_before_hashes']
 assert ar['helper_sha256']==tool_map['tools/archive_build.py'] and sha(B/ar['archive'])==ar['sha256']
 with tarfile.open(B/ar['archive'],'r:gz') as tar:
  entries=tar.getmembers();assert len(entries)==69 and {x.name for x in entries}==set(m)
  for entry in entries:assert entry.isfile() and hashlib.sha256(tar.extractfile(entry).read()).hexdigest()==m[entry.name]
 native=load(N/'result.json');assert native['complete'] and native['failure'] is None and native['total_tests']==178 and native['source_and_tools_unchanged']
 assert native['source69_sha256']==m and native['generic_image_sha256']==EXPECTED and native['original_inputs_unchanged']
 assert load(N/'source69-before.json')==load(N/'source69-after.json')==m
 assert load(N/'input-pins-before.json')==load(N/'input-pins-after.json')
 for path,h in load(N/'input-pins-before.json').items():assert str(Path(path)) in before and sha(path)==h
 provenance=load(N/'frozen-image-provenance.json');assert len(native['commands'])==2
 for kind,count in [('lib',176),('dev',2)]:
  row=native['tests'][kind];image=Path(row['frozen_executable']);origin=Path(row['original_executable']);record=load(N/(kind+'-terminal.json'));launch=load(N/(kind+'-launch.json'))
  assert row['passed']==count and row['actual_exit_code']==0 and sha(image)==sha(origin)==row['sha256']==provenance[kind]['sha256']
  assert record in native['commands'] and record['actual_child_return_observed'] and record['exit_code']==0 and record['command']==[str(image),'--test-threads=1']
  assert record['pid']==launch['pid']==row['pid']>0 and record['affinity']==launch['affinity']==sorted(H)
  assert record['stdout_sha256']==sha(N/(kind+'-tests.stdout')) and record['stderr_sha256']==sha(N/(kind+'-tests.stderr'))
  assert record['image_sha256_before']==record['image_sha256_after']==record['original_image_sha256_after']==row['sha256']
  assert (N/(kind+'-tests.stderr')).read_bytes()==b''
  text=(N/(kind+'-tests.stdout')).read_text();assert len(re.findall(r'^test .* \.\.\. ok$',text,re.M))==count and f'test result: ok. {count} passed; 0 failed;' in text
 old=load(OLD/'result.json');assert old['complete'] and old['stable_source_and_inputs']
 assert len(re.findall(r'^test .* \.\.\. ok$',(OLD/'native-tests.stdout').read_text(),re.M))==178
 regression=load(R/'result.json');assert regression['complete'] and regression['stable_source_and_inputs'] and len(regression['records'])==2
 for record,stem in zip(regression['records'],['strict54','wire']):
  assert record['exit_code']==0 and record['pid']>0
  assert record['stdout_sha256']==sha(R/(stem+'.stdout')) and record['stderr_sha256']==sha(R/(stem+'.stderr'))
 assert regression['records'][0]['command']==['/usr/bin/node',str(KIT/'profiling/replay-check.mjs'),'--','/usr/bin/taskset','-c','14',str(B/'rook2-exact')]
 assert regression['records'][1]['command']==['/usr/bin/python3','/home/legolas/rook2/tools/check_live.py','--engine',str(B/'rook2-exact'),'--output',str(R/'wire')]
 assert (R/'strict54.stderr').read_bytes()==(R/'wire.stderr').read_bytes()==b''
 fixture=load(KIT/'fixtures/interrupted-sessions-v1.json');wire=load(R/'wire/receipt.json')
 assert wire['engine']==str(B/'rook2-exact') and wire['engine_sha256_before']==wire['engine_sha256_after']==EXPECTED
 assert wire['effective_affinity']==sorted(H) and wire['fixture_sha256']==sha(KIT/'fixtures/interrupted-sessions-v1.json')
 assert len(wire['results'])==len(fixture['cases'])==8
 checked=[];total_searches=0
 for case,row in zip(fixture['cases'],wire['results']):
  assert row['id']==case['id'] and row['observed_exit_code']==row['exit_code']==0 and row['complete_streams']
  directory=R/'wire'/case['id'];raw={}
  for stream in ['stdin','stdout','stderr']:
   path=directory/(stream+'.raw');data=path.read_bytes();rec=row['raw'][stream]
   assert len(data)==rec['bytes'] and hashlib.sha256(data).hexdigest()==rec['sha256'];assert data.isascii();raw[stream]=data;dependencies.add(path)
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

 assert {str(path) for path in dependencies}==set(before)
 assert all(sha(path)==h for path,h in before.items())
 with (P/'original-replay54.stdout').open('xb') as stdout,(P/'original-replay54.stderr').open('xb') as stderr:
  argv=['/usr/bin/node',str(P/'original-replay54.mjs')];child=subprocess.Popen(argv,stdout=stdout,stderr=stderr);code=child.wait()
 write('original-replay54-terminal.json',dict(argv=argv,pid=child.pid,exit_code=code,actual_child_return_observed=True,engine_runs=0))
 assert code==0 and (P/'original-replay54.stderr').read_bytes()==b'' and load(P/'original-replay54-result.json')['original_checkReplay_calls']==54
 after={path:sha(path) for path in before};assert before==after;write('input-sha256-after.json',after)
 write('independent-verification.json',dict(complete=True,engine_sha256=EXPECTED,native_tests=178,strict54_original_checkReplay=True,wire8_searches24_raw_protocol=checked,source46_tools23_archive69_equal=True,compiler_cargo_generic_bound=True,all_dependencies_stable=True,dependencies=before,new_native_engine_runs=0,limits=['Original178 Cargo pass and copied-image178 repeat are the same unique tests','Strict stored argv includes taskset -c14; this offline review makes no measured CPU claim','Strict stdin is bound runner/workloads reconstruction, not separately captured strict native stdin','Wire direct native exits retained but no per-native PID field; driver PID and original raw command/reply streams are bound','No timing/PGO/promotion/whole-game qualification claim']))
 print(json.dumps(dict(complete=True,native=178,strict=54,wire_cases=8,wire_searches=24,new_engine_runs=0,dependencies=len(before))))
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),new_engine_runs=0));raise
