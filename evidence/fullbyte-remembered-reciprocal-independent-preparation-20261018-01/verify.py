#!/usr/bin/env python3
"""Bounded offline verification of exact fullbyte reciprocal40b26a4d; no engine execution."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,tarfile
P=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence')
PRE=E/'fullbyte-remembered-reciprocal-validation-preparation-20261018-01'
B=E/'fullbyte-remembered-reciprocal-generic-build-20261018-01'
N=E/'fullbyte-remembered-reciprocal-native-validation-20261018-01'
R=E/'fullbyte-remembered-reciprocal-regression-20261018-01'
REF=E/'full-byte-pair-relations-generic-build-20261018-01'
PRO=E/'fullbyte-remembered-reciprocal-proposal-20261018-01'
KIT=Path('/home/legolas/king-spec/conformance')
EXPECTED='40b26a4d8802c6f7124ae76f19e9898df911f0414438d63f38ba6dd1294566cc'
FUNCTIONAL_SHA='fd706572f894be25e41f47430d207e2127c44a60594853b7d05710f34347389c'
H={0,1,2,3,4,5,8,9,10,11,12,13}
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d):
 with (P/name).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def command_receipt(path):
 d=load(path);assert d['exit_code']==0 and d['actual_child_return_observed'],path
 return d

def outer(path,key,clearance):
 d=load(path);assert d==clearance['stage_terminals'][key]
 assert d['actual_tool_terminal_observed'] is True and d['exit_code']==0
 chunk=d.get('terminal_chunk_id') or d.get('chunk_id');assert isinstance(chunk,str) and chunk.strip()
 if d.get('session_id') is not None:assert isinstance(d['session_id'],int) and d['session_id']>0
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
 assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 clearance=load(P/'launch-clearance.json')
 assert clearance['authorized'] is True and clearance['scope']=='fullbyte-remembered-reciprocal-offline-verification-no-engine'
 assert clearance['helpers_sha256']=={name:sha(P/name) for name in ['verify.py','original-replay54.mjs']}
 for required in [PRE/'functional-result.json',PRO/'source-manifest.json',PRO/'prepared.json',PRO/'source-proof.json',PRE/'build-result.json',PRE/'stages.py',PRE/'execution-clearance.json',PRE/'execution-binding.json',PRE/'generic-build-driver-terminal.json',PRE/'generic-archive-terminal.json',B/'receipt.json',B/'archive-receipt.json',B/'tool-terminal.json',N/'result.json',N/'tool-terminal.json',R/'result.json',R/'tool-terminal.json',REF/'receipt.json',REF/'archive-receipt.json',REF/'verified-source-before.tar.gz']:
  assert str(required) in clearance['dependencies'],required
 for path,h in clearance['dependencies'].items():assert sha(path)==h,path
 m=load(PRO/'source-manifest.json');s=Path(m['path']);b=load(B/'receipt.json');reference=load(REF/'receipt.json')
 # Snapshot the complete bounded input closure before any source/raw checks.
 dependencies={Path(path) for path in clearance['dependencies']}
 dependencies.update(s/name for name in [*m['native46'],*m['tools23']])
 for tree in [B,N,R]:dependencies.update(x for x in tree.rglob('*') if x.is_file())
 dependencies.update(Path(x['executable']) for x in load(N/'result.json')['tests'].values())
 dependencies.update(Path(x['original_executable']) for x in load(N/'result.json')['tests'].values())
 dependencies.update(Path(path) for path in load(R/'result.json')['input_sha256_before'])
 dependencies.update(Path(b['toolchain'][name]['argv'][0]) for name in ['rustc','cargo'])
 dependencies.update([REF/'verified-source-before.tar.gz',Path(b['binary_output']['path']),P/'verify.py',P/'original-replay54.mjs',P/'launch-clearance.json'])
 before={str(path):sha(path) for path in sorted(dependencies)}
 assert before[str(PRO/'source-manifest.json')]==clearance['dependencies'][str(PRO/'source-manifest.json')]
 terminals={key:outer(directory/'tool-terminal.json',key,clearance) for key,directory in [('build',B),('native',N),('regression',R)]}
 built=load(PRE/'build-result.json')
 assert built['complete'] and built['engine_sha256']==EXPECTED and built['source46_tools23_stable'] and built['archive69_reopened'] and built['compiler_generic_equal_control']
 assert built['build_receipt']==str(B/'receipt.json')
 assert sha(PRE/'functional-result.json')==FUNCTIONAL_SHA
 functional=load(PRE/'functional-result.json')
 assert functional['status']=='GENERIC179_STRICT54_EIGHTWIRE24_PASS' and functional['source']==str(s) and functional['image']==str(B/'rook2-exact') and functional['image_sha256']==EXPECTED
 assert functional['source_graph_sha256']==m['source_graph_sha256'] and functional['source_and_authorities_unchanged'] and functional['all_owned_jobs_closed']
 assert (functional['native_tests'],functional['library_tests'],functional['development_tests'],functional['original_strict_cases'],functional['original_wire_fixtures'],functional['original_wire_searches'])==(179,177,2,54,8,24) and functional['new_modulo_oracle_pass']
 for key,path in [('build_receipt_sha256',B/'receipt.json'),('archive_receipt_sha256',B/'archive-receipt.json'),('native_result_sha256',N/'result.json'),('regression_result_sha256',R/'result.json')]:assert functional[key]==sha(path)
 assert s==Path('/home/legolas/rook2-work/imp2-fullbyte-remembered-reciprocal-20261018-ebbxxgu4')
 assert len(m['native46'])==46 and len(m['tools23'])==23 and m['source69']=={**m['native46'],**m['tools23']}
 assert m['source_graph_sha256']=='5db8a6bcbfda4bcdd896ede97b8402bafd450ef7f539b706d41c5b67829b0efa'
 assert m['source_graph_sha256']==hashlib.sha256(json.dumps(m['source69'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert reference['binary_output']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 refarchive=load(REF/'archive-receipt.json');assert refarchive['files']==69 and refarchive['binary_sha256']==reference['binary_output']['sha256']
 assert sha(REF/refarchive['archive'])==refarchive['sha256']
 assert b['source_sha256_before']==b['source_sha256_after']==m['native46']
 assert b['tool_sha256_before']==b['tool_sha256_after']==m['tools23']==reference['tool_sha256_before']
 assert [k for k,h in m['native46'].items() if reference['source_sha256_before'][k]!=h]==['src/remembered.rs']
 for name in ['src/activity.rs','src/pawn_progress.rs','src/influence.rs','src/relation_table.rs']:assert m['native46'][name]==reference['source_sha256_before'][name]
 assert b['cargo_config_sha256_before']==b['cargo_config_sha256_after']=={}
 assert b['crate']==str(s) and b['mode']=='generic' and b['pgo']['mode']=='none'
 assert b['rust_flags']==['-C','target-cpu=x86-64'] and b['engine_runs']==0
 assert b['target_triple']=='x86_64-unknown-linux-gnu' and b['target_cpu']=='x86-64' and b['jobs']==4
 assert b['toolchain']==reference['toolchain']
 assert reference['mode']=='generic' and reference['pgo']['mode']=='none' and reference['rust_flags']==b['rust_flags']
 assert reference['source_sha256_before']==reference['source_sha256_after'] and reference['tool_sha256_before']==reference['tool_sha256_after']
 assert b['outcome']=='build-succeeded-with-stable-input-snapshot' and b['cargo_exit_code']==0
 assert b['binary_output']['sha256']==EXPECTED==sha(B/'rook2-exact')==sha(Path(b['binary_output']['path']))
 assert b['build_affinity']==sorted(H)
 for name in ['rustc','cargo']:
  t=b['toolchain'][name];assert t['exit_code']==0
  assert sha(t['argv'][0])==b['toolchain'][name+'_executable_sha256']
 allmap={**m['native46'],**m['tools23']}
 actual={'Cargo.toml','Cargo.lock'}|{str(x.relative_to(s)) for root in [s/'src',s/'tools'] for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
 assert actual==set(allmap)
 for name,h in allmap.items():
  for path in [s/name,B/'source-before'/name]:assert sha(path)==h,name;dependencies.add(path)
 for row in b['logs'].values():
  path=B/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'];dependencies.add(path)
 archive=load(B/'archive-receipt.json');assert archive['files']==69 and archive['binary_sha256']==EXPECTED
 assert functional['archive69_sha256']==archive['sha256']
 assert archive['helper_sha256']==m['tools23']['tools/archive_build.py']
 assert sha(B/archive['archive'])==archive['sha256'];dependencies.add(B/archive['archive'])
 with tarfile.open(B/archive['archive'],'r:gz') as tar:
  entries=tar.getmembers();assert len(entries)==69 and {x.name for x in entries}==set(allmap)
  for entry in entries:
   assert entry.isfile();assert hashlib.sha256(tar.extractfile(entry).read()).hexdigest()==allmap[entry.name]
 reference_map=reference['source_sha256_before']|reference['tool_sha256_before']
 with tarfile.open(REF/'verified-source-before.tar.gz','r:gz') as tar:
  entries=tar.getmembers();assert len(entries)==69 and {x.name for x in entries}==set(reference_map)
  for entry in entries:
   assert entry.isfile();data=tar.extractfile(entry).read();assert hashlib.sha256(data).hexdigest()==reference_map[entry.name]
   if entry.name=='src/influence.rs':baseline_influence=data.decode()
 marker='\n#[cfg(test)]\nmod tests {';current_influence=(s/'src/influence.rs').read_text()
 assert current_influence.count(marker)==baseline_influence.count(marker)==1 and current_influence.split(marker)[1]==baseline_influence.split(marker)[1]
 native=load(N/'result.json');assert native['complete'] and native['failure'] is None and native['total_tests']==179 and native['engine_sha256']==EXPECTED
 assert native['source_root']==str(s) and native['source_and_tools_unchanged'] is True
 assert set(native['tests'])=={'lib','dev'}
 assert native['test_environment']==b['build_effective_environment']
 artifacts=[json.loads(line) for line in (N/'cargo-tests.stdout').read_text().splitlines()]
 assert len([d for d in artifacts if d.get('reason')=='build-finished' and d['success']])==1
 test_paths={d['executable'] for d in artifacts if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable')}
 assert test_paths=={d['original_executable'] for d in native['tests'].values()}
 for key,count in [('lib',177),('dev',2)]:
  row=native['tests'][key];path=Path(row['executable']);assert row['passed']==count and sha(path)==sha(row['original_executable'])==row['sha256'];dependencies.add(path)
  terminal=command_receipt(N/(key+'-tests-terminal.json'));assert terminal['argv']==[str(path),'--test-threads=1']
  assert terminal in native['commands']
  stdout=(N/(key+'-tests.stdout')).read_text();assert (N/(key+'-tests.stderr')).read_bytes()==b''
  assert len(re.findall(r'^test .+ \.\.\. ok$',stdout,re.M))==count
  assert re.search(rf'test result: ok\. {count} passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;',stdout)
 assert 'remembered::tests::reciprocal_group_remainders_match_builtin_modulo_and_survive_clear ... ok' in (N/'lib-tests.stdout').read_text()
 assert 'influence::tests::all_byte_pairs_and_exclusions_match_independent_digit_reference ... ok' in (N/'lib-tests.stdout').read_text()
 cargo=command_receipt(N/'cargo-tests-terminal.json');assert cargo in native['commands']
 assert cargo['argv']==['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--manifest-path',str(s/'Cargo.toml'),'--target-dir',str(s/'target/native-tests-generic-01'),'--jobs','4','--lib','--bin','rook2-dev','--no-run','--message-format=json-render-diagnostics']
 assert native['commands']==[cargo,load(N/'dev-tests-terminal.json'),load(N/'lib-tests-terminal.json')]
 regression=load(R/'result.json');assert regression['complete'] and regression['failure'] is None and regression['engine_sha256']==EXPECTED
 assert regression['input_sha256_before']==regression['input_sha256_after']==load(PRE/'execution-binding.json')['authority_sha256']
 for path,h in regression['input_sha256_before'].items():assert sha(path)==h,path;dependencies.add(Path(path))
 strict=command_receipt(R/'strict54-terminal.json');live=command_receipt(R/'wire-driver-terminal.json')
 assert strict['argv']==['/usr/bin/node',str(KIT/'profiling/replay-check.mjs'),'--',str(B/'rook2-exact')]
 assert live['argv']==['/usr/bin/python3','/home/legolas/rook2/tools/check_live.py','--engine',str(B/'rook2-exact'),'--output',str(R/'wire')]
 assert regression['commands']==[strict,live]
 build_driver=command_receipt(PRE/'generic-build-driver-terminal.json');archive_driver=command_receipt(PRE/'generic-archive-terminal.json')
 assert build_driver['argv']==['/usr/bin/python3','/home/legolas/rook2/tools/build.py','--crate',str(s),'--mode','generic','--jobs','4','--bin','rook2','--output',str(B)]
 assert archive_driver['argv']==['/usr/bin/python3','/home/legolas/rook2/tools/archive_build.py',str(B)]
 dependencies.update([PRE/'generic-build-driver-terminal.json',PRE/'generic-archive-terminal.json'])
 expected_children=[build_driver,archive_driver,*native['commands'],*regression['commands']]
 strict_report=load(R/'strict54.stdout');assert strict_report['status']=='pass' and len(strict_report['results'])==54
 expected_children += [dict(pid=x['pid'],argv=x['command'],exit_code=x['exit']['code']) for x in strict_report['results']]
 assert len({x['pid'] for x in expected_children})==len(expected_children)
 for child in expected_children:assert isinstance(child['pid'],int) and child['pid']>0 and child['exit_code']==0 and child['argv']
 assert regression['strict54_pass'] and regression['interruption_fixtures']==8 and regression['interruption_searches']==24 and regression['untimed']
 assert regression['source_and_tool_identity_unchanged'] and regression['helper_and_engine_inherited_affinity']==sorted(H)
 assert (R/'strict54.stderr').read_bytes()==b'' and (R/'wire-driver.stderr').read_bytes()==b''
 fixture=load(KIT/'fixtures/interrupted-sessions-v1.json');wire=load(R/'wire/receipt.json')
 assert wire['engine']==str(B/'rook2-exact') and wire['engine_sha256_before']==wire['engine_sha256_after']==EXPECTED
 assert wire['effective_affinity']==sorted(H) and wire['fixture_sha256']==sha(KIT/'fixtures/interrupted-sessions-v1.json')
 assert wire['checker_sha256']==m['tools23']['tools/check_live.py']
 assert wire['pass'] and wire['diagnostic_transport'] is False and wire['performance_sample'] is False
 assert [row['observed_exit_code'] for row in wire['results']]==[0]*8
 assert len(wire['results'])==len(fixture['cases'])==8
 checked=[];total_searches=0
 for case,row in zip(fixture['cases'],wire['results']):
  assert row['id']==case['id'] and row['status']=='pass' and row['observed_exit_code']==row['exit_code']==0 and row['complete_streams']
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
  for got,recorded in zip(searches,row['searches']):assert recorded['status']=='pass' and got['events']==recorded['events'] and got['abort']==recorded['abort']
  checked.append({'id':case['id'],'searches':3,'all_stdin_stdout_stderr_bytes_consumed':True,'normal_exit':0})
 assert total_searches==24
 # All dynamically consumed inputs must already belong to the start snapshot.
 assert {str(path) for path in dependencies}==set(before)
 assert all(sha(Path(path))==h for path,h in before.items())
 with (P/'original-replay54.stdout').open('xb') as stdout,(P/'original-replay54.stderr').open('xb') as stderr:
  argv=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/node',str(P/'original-replay54.mjs')]
  done=subprocess.run(argv,stdout=stdout,stderr=stderr)
 write('original-replay54-terminal.json',{'argv':argv,'exit_code':done.returncode,'actual_child_return_observed':True,'engine_runs':0})
 assert done.returncode==0 and (P/'original-replay54.stderr').read_bytes()==b''
 assert load(P/'original-replay54-result.json')['original_checkReplay_calls']==54
 after={path:sha(Path(path)) for path in before};assert before==after
 write('independent-verification.json',{'complete':True,'engine_sha256':EXPECTED,'build_result_sha256':sha(PRE/'build-result.json'),'stage_terminals':terminals,'recorded_completed_children':expected_children,'functional_result_sha256':FUNCTIONAL_SHA,'native_tests':179,'strict54_original_checkReplay':True,'wire8_searches24_raw_protocol':checked,'source46_tools23_archive69_equal':True,'only_remembered_changed_vs_fullbyte_baseline':True,'fullbyte_activity_retained_pawn_unchanged':True,'independent_influence_test_module_unchanged':True,'compiler_cargo_generic_bound':True,'all_dependencies_stable':True,'dependencies':before,'new_native_engine_runs':0,'limits':['Strict stdin is bound via original runner/workloads; no separate native stdin byte stream was retained by that original strict runner','Wire receipt has observed direct native exit codes but no individual native PID field','Cross-stream wall ordering is not reconstructed; exact streams and unchanged original scheduler are bound','This offline verifier makes no exclusive-housekeeping or historical concurrency claim','No timing/PGO/adoption or whole-component/full-game qualification claim']})
 print(json.dumps({'complete':True,'native':179,'strict':54,'wire_cases':8,'wire_searches':24,'new_engine_runs':0}))
if __name__=='__main__':
 try:main()
 except BaseException as error:
  write('failure.json',{'error':repr(error),'new_engine_runs':0});raise
