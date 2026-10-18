#!/usr/bin/env python3
"""Bounded readonly offline verification of exact activity7cf398; no engines."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,tarfile
P=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence')
PRE=E/'activity-value-inputs-validation-preparation-20261018-01'
B=E/'activity-value-inputs-generic-build-20261018-01'
N=E/'activity-value-inputs-native-validation-20261018-01'
R=E/'activity-value-inputs-regression-20261018-01'
REF=E/'complete117-pgo-use-build-20261018'
KIT=Path('/home/legolas/king-spec/conformance')
EXPECTED='7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'
H={0,1,2,3,4,5,8,9,10,11,12,13}
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d):
 with (P/name).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def command_receipt(path):
 d=load(path);assert d['exit_code']==0 and d['actual_child_return_observed'],path
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
 assert os.sched_getaffinity(0)==H
 clearance=load(P/'launch-clearance.json')
 assert clearance['session_id']==47314 and clearance['exit_code']==0 and clearance['actual_terminal_chunk']
 for required in [PRE/'source-manifest.json',B/'receipt.json',B/'archive-receipt.json',N/'result.json',N/'tool-terminal.json',R/'result.json',R/'tool-terminal.json',REF/'receipt.json']:
  assert str(required) in clearance['dependencies'],required
 for path,h in clearance['dependencies'].items():assert sha(path)==h,path
 m=load(PRE/'source-manifest.json');s=Path(m['source_root']);b=load(B/'receipt.json');reference=load(REF/'receipt.json')
 # Snapshot the complete bounded input closure before any source/raw checks.
 dependencies={Path(path) for path in clearance['dependencies']}
 dependencies.update(s/name for name in [*m['source_sha256'],*m['tool_sha256']])
 for tree in [B,N,R]:dependencies.update(x for x in tree.rglob('*') if x.is_file())
 dependencies.update(Path(x['executable']) for x in load(N/'result.json')['tests'].values())
 dependencies.update(Path(path) for path in load(R/'result.json')['input_sha256_before'])
 dependencies.update(Path(b['toolchain'][name]['argv'][0]) for name in ['rustc','cargo'])
 dependencies.update([REF/'verified-source-before.tar.gz',Path(b['binary_output']['path']),P/'verify.py',P/'original-replay54.mjs',P/'launch-clearance.json'])
 before={str(path):sha(path) for path in sorted(dependencies)}
 assert before[str(PRE/'source-manifest.json')]==clearance['dependencies'][str(PRE/'source-manifest.json')]
 rt=load(R/'tool-terminal.json');assert rt['session_id']==47314 and rt['terminal_chunk_id']==clearance['actual_terminal_chunk'] and rt['exit_code']==0
 assert len(m['source_sha256'])==46 and len(m['tool_sha256'])==23
 assert m['changed_native']==['src/activity.rs'] and m['unchanged_native']==45 and m['unchanged_tools']==23
 assert m['basis_source_archive_sha256']=='ea8963b2f5d082e2d12f026f9a14e84df9d38a8f9b3bfb78014cbb3dea555652'
 assert sha(REF/'verified-source-before.tar.gz')==m['basis_source_archive_sha256']
 assert b['source_sha256_before']==b['source_sha256_after']==m['source_sha256']
 assert b['tool_sha256_before']==b['tool_sha256_after']==m['tool_sha256']==reference['tool_sha256_before']
 assert [k for k,h in m['source_sha256'].items() if reference['source_sha256_before'][k]!=h]==['src/activity.rs']
 assert b['cargo_config_sha256_before']==b['cargo_config_sha256_after']=={}
 assert b['crate']==str(s) and b['mode']=='generic' and b['pgo']['mode']=='none'
 assert b['rust_flags']==['-C','target-cpu=x86-64'] and b['engine_runs']==0
 assert b['toolchain']==reference['toolchain']
 assert b['outcome']=='build-succeeded-with-stable-input-snapshot' and b['cargo_exit_code']==0
 assert b['binary_output']['sha256']==EXPECTED==sha(B/'rook2-exact')==sha(Path(b['binary_output']['path']))
 assert b['build_affinity']==sorted(H)
 for name in ['rustc','cargo']:
  t=b['toolchain'][name];assert t['exit_code']==0
  assert sha(t['argv'][0])==b['toolchain'][name+'_executable_sha256']
 allmap={**m['source_sha256'],**m['tool_sha256']}
 actual={'Cargo.toml','Cargo.lock'}|{str(x.relative_to(s)) for root in [s/'src',s/'tools'] for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
 assert actual==set(allmap)
 for name,h in allmap.items():
  for path in [s/name,B/'source-before'/name]:assert sha(path)==h,name;dependencies.add(path)
 for row in b['logs'].values():
  path=B/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'];dependencies.add(path)
 archive=load(B/'archive-receipt.json');assert archive['files']==69 and archive['binary_sha256']==EXPECTED
 assert archive['helper_sha256']==m['tool_sha256']['tools/archive_build.py']
 assert sha(B/archive['archive'])==archive['sha256'];dependencies.add(B/archive['archive'])
 with tarfile.open(B/archive['archive'],'r:gz') as tar:
  entries=tar.getmembers();assert len(entries)==69 and {x.name for x in entries}==set(allmap)
  for entry in entries:
   assert entry.isfile();assert hashlib.sha256(tar.extractfile(entry).read()).hexdigest()==allmap[entry.name]
 native=load(N/'result.json');assert native['complete'] and native['failure'] is None and native['total_tests']==178 and native['engine_sha256']==EXPECTED
 nt=load(N/'tool-terminal.json');assert nt['session_id']==40196 and nt['terminal_chunk_id']=='63c139' and nt['exit_code']==0
 artifacts=[json.loads(line) for line in (N/'cargo-tests.stdout').read_text().splitlines()]
 assert len([d for d in artifacts if d.get('reason')=='build-finished' and d['success']])==1
 test_paths={d['executable'] for d in artifacts if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable')}
 assert test_paths=={d['executable'] for d in native['tests'].values()}
 for key,count in [('lib',176),('dev',2)]:
  row=native['tests'][key];path=Path(row['executable']);assert row['passed']==count and sha(path)==row['sha256'];dependencies.add(path)
  terminal=command_receipt(N/(key+'-tests-terminal.json'));assert terminal['argv']==[str(path),'--test-threads=1']
  assert terminal in native['commands']
  stdout=(N/(key+'-tests.stdout')).read_text();assert (N/(key+'-tests.stderr')).read_bytes()==b''
  assert len(re.findall(r'^test .+ \.\.\. ok$',stdout,re.M))==count
  assert re.search(rf'test result: ok\. {count} passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;',stdout)
 cargo=command_receipt(N/'cargo-tests-terminal.json');assert cargo in native['commands']
 assert cargo['argv']==['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--manifest-path',str(s/'Cargo.toml'),'--target-dir',str(s/'target/native-tests-generic-01'),'--jobs','4','--lib','--bin','rook2-dev','--no-run','--message-format=json-render-diagnostics']
 assert len(native['commands'])==3
 regression=load(R/'result.json');assert regression['complete'] and regression['failure'] is None and regression['engine_sha256']==EXPECTED
 assert regression['input_sha256_before']==regression['input_sha256_after']
 for path,h in regression['input_sha256_before'].items():assert sha(path)==h,path;dependencies.add(Path(path))
 strict=command_receipt(R/'strict54-terminal.json');live=command_receipt(R/'wire-driver-terminal.json')
 assert strict['argv']==['/usr/bin/node',str(KIT/'profiling/replay-check.mjs'),'--',str(B/'rook2-exact')]
 assert live['argv']==['/usr/bin/python3','/home/legolas/rook2/tools/check_live.py','--engine',str(B/'rook2-exact'),'--output',str(R/'wire')]
 assert regression['commands']==[strict,live]
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
 # All dynamically consumed inputs must already belong to the start snapshot.
 assert {str(path) for path in dependencies}==set(before)
 assert all(sha(Path(path))==h for path,h in before.items())
 with (P/'original-replay54.stdout').open('xb') as stdout,(P/'original-replay54.stderr').open('xb') as stderr:
  argv=['/usr/bin/node',str(P/'original-replay54.mjs')]
  done=subprocess.run(argv,stdout=stdout,stderr=stderr)
 write('original-replay54-terminal.json',{'argv':argv,'exit_code':done.returncode,'engine_runs':0})
 assert done.returncode==0 and (P/'original-replay54.stderr').read_bytes()==b''
 assert load(P/'original-replay54-result.json')['original_checkReplay_calls']==54
 after={path:sha(Path(path)) for path in before};assert before==after
 write('independent-verification.json',{'complete':True,'engine_sha256':EXPECTED,'native_tests':178,'strict54_original_checkReplay':True,'wire8_searches24_raw_protocol':checked,'source46_tools23_archive69_equal':True,'compiler_cargo_generic_bound':True,'all_dependencies_stable':True,'dependencies':before,'new_native_engine_runs':0,'limits':['Strict stdin is bound via original runner/workloads; no separate native stdin byte stream was retained by that original strict runner','Wire receipt has observed direct native exit codes but no individual native PID field','Cross-stream wall ordering is not reconstructed; exact streams and unchanged original scheduler are bound','No timing/PGO/adoption or whole-component/full-game qualification claim']})
 print(json.dumps({'complete':True,'native':178,'strict':54,'wire_cases':8,'wire_searches':24,'new_engine_runs':0}))
if __name__=='__main__':
 try:main()
 except BaseException as error:
  write('failure.json',{'error':repr(error),'new_engine_runs':0});raise
