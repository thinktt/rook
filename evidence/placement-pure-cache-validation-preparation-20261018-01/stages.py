#!/usr/bin/env python3
"""Exact isolated placement pure-component cache generic functional trial; no timing."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tarfile
P=Path(__file__).resolve().parent;E=P.parent;ROOT=E.parent
B=E/'placement-pure-cache-generic-build-20261018-01'
N=E/'placement-pure-cache-native-validation-20261018-01'
R=E/'placement-pure-cache-regression-20261018-01'
REF=E/'full-byte-pair-relations-generic-build-20261018-01'
PRO=E/'placement-pure-cache-proposal-20261018-01'
KIT=Path('/home/legolas/king-spec/conformance')
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
def manifest():
 raw=load(PRO/'source-manifest.json');prepared=load(PRO/'prepared.json')
 assert raw['schema']=='relative-path-sha256-v1' and raw['counts']=={'native_and_manifests':46,'tools':23,'total':69}
 assert prepared['complete_source_proposal'] is True and prepared['source_graph_sha256']==raw['graph_sha256']
 assert prepared['source_manifest_sha256']==sha(PRO/'source-manifest.json')
 files=raw['files'];assert raw['graph_sha256']==hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 native={k:h for k,h in files.items() if not k.startswith('tools/')};tools={k:h for k,h in files.items() if k.startswith('tools/')}
 return {'path':prepared['source'],'native46':native,'tools23':tools,'source69':files,'source_graph_sha256':raw['graph_sha256']}
def authorized():
 assert sorted(os.sched_getaffinity(0))==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 c=load(P/'execution-clearance.json');assert c['authorized'] is True and c['parent_review_complete'] is True
 assert c['stages_sha256']==sha(P/'stages.py')
def guard():
 authorized();bound=load(P/'execution-binding.json');m=manifest();s=Path(m['path'])
 for path,h in bound['authority_sha256'].items():assert sha(path)==h,path
 for name,h in {**m['native46'],**m['tools23']}.items():assert sha(s/name)==h,name
 if (B/'receipt.json').exists():
  b=load(B/'receipt.json')
  if b.get('outcome')=='build-succeeded-with-stable-input-snapshot':
   for tool in ['rustc','cargo']:assert sha(b['toolchain'][tool]['argv'][0])==b['toolchain'][tool+'_executable_sha256']
 return m,s

def run(directory,stem,argv,env=None):
 guard();print('START '+stem,flush=True)
 write(directory/(stem+'-launch.json'),{'argv':argv,'affinity':sorted(os.sched_getaffinity(0)),'env_overrides':{k:env.get(k) for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','LLVM_PROFILE_FILE']} if env else {}})
 with (directory/(stem+'.stdout')).open('xb') as stdout,(directory/(stem+'.stderr')).open('xb') as stderr:
  child=subprocess.Popen(argv,stdout=stdout,stderr=stderr,cwd=ROOT,env=env);code=child.wait()
 row={'argv':argv,'pid':child.pid,'exit_code':code,'actual_child_return_observed':True}
 write(directory/(stem+'-terminal.json'),row);print('TERMINAL '+stem+' '+str(code),flush=True)
 assert code==0,(stem,code);guard();return row

def initialize():
 authorized();assert sorted(os.sched_getaffinity(0))==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 m=manifest();s=Path(m['path']);reference=load(REF/'receipt.json')
 assert len(m['native46'])==46 and len(m['tools23'])==23
 assert m['path']=='/home/legolas/rook2-work/imp2-placement-pure-cache-20261018-x2gvi1c5'
 assert m['source69']=={**m['native46'],**m['tools23']}
 assert m['source_graph_sha256']=='e784334543d6045f6952ce5d2b636b6e185705ebfbcf633bdb499e5549996937'
 assert reference['binary_output']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 assert sha(REF/'rook2-exact')==reference['binary_output']['sha256']
 assert m['tools23']==reference['tool_sha256_before']
 assert sorted(k for k,h in m['native46'].items() if reference['source_sha256_before'][k]!=h)==['src/activity.rs', 'src/evaluator.rs', 'src/ordinary.rs', 'src/quiescence.rs', 'src/shelter.rs']
 archive=load(REF/'archive-receipt.json');assert sha(REF/archive['archive'])==archive['sha256']
 assert load(PRO/'prepared.json')['changed_files']==['src/activity.rs', 'src/evaluator.rs', 'src/ordinary.rs', 'src/quiescence.rs', 'src/shelter.rs']
 for name in ['src/activity.rs', 'src/evaluator.rs', 'src/ordinary.rs', 'src/quiescence.rs', 'src/shelter.rs']:assert (s/name).read_bytes()==(PRO/'proposed'/name).read_bytes()
 expected={**m['native46'],**m['tools23']}
 actual={'Cargo.toml','Cargo.lock'}|{str(q.relative_to(s)) for d in [s/'src',s/'tools'] for q in d.rglob('*') if q.is_file() and '__pycache__' not in q.parts}
 assert actual==set(expected)
 for name,h in expected.items():assert sha(s/name)==h,name
 for name in ['build.py','archive_build.py','check_live.py']:assert sha(ROOT/'tools'/name)==m['tools23']['tools/'+name]
 files=[P/'stages.py',P/'execution-clearance.json',PRO/'source-manifest.json',PRO/'prepared.json',PRO/'source-proof.json',PRO/'test-declarations.json',PRO/'trial.patch',PRO/'archive-manifest.json',PRO/'source69.tar.gz',REF/'receipt.json',REF/'archive-receipt.json',REF/archive['archive'],REF/'rook2-exact']
 files += [PRO/'proposed'/name for name in ['src/activity.rs', 'src/evaluator.rs', 'src/ordinary.rs', 'src/quiescence.rs', 'src/shelter.rs']]
 files += [ROOT/'tools'/name for name in ['build.py','archive_build.py','check_live.py']]
 files += [KIT/'profiling'/name for name in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']]
 files += [KIT/'fixtures/interrupted-sessions-v1.json',Path('/usr/bin/node'),Path('/usr/bin/python3')]
 write(P/'execution-binding.json',{'source_root':str(s),'authority_sha256':{str(f):sha(f) for f in files},'source_sha256':m['native46'],'tool_sha256':m['tools23'],'scope':'Explicitly authorized isolated generic functional trial only, activity/fullbyte math retained, trusted pure-component cache only, no pawn fusion or TT reciprocal/timing/profiling/Git/adoption; original proposal manifest unchanged','source_proposal_actual':'63578d/0; parent execution review still required'})
 guard()

def build():
 initialize();assert not B.exists();m,s=guard()
 run(P,'generic-build-driver',['/usr/bin/python3',str(ROOT/'tools/build.py'),'--crate',str(s),'--mode','generic','--jobs','4','--bin','rook2','--output',str(B)])
 b=load(B/'receipt.json');assert b['outcome']=='build-succeeded-with-stable-input-snapshot' and b['cargo_exit_code']==0
 assert b['source_sha256_before']==b['source_sha256_after']==m['native46'] and b['tool_sha256_before']==b['tool_sha256_after']==m['tools23']
 assert b['mode']=='generic' and b['pgo']['mode']=='none' and b['rust_flags']==['-C','target-cpu=x86-64'] and b['engine_runs']==0
 assert b['toolchain']==load(REF/'receipt.json')['toolchain'] and b['cargo_config_sha256_before']==b['cargo_config_sha256_after']=={}
 image=B/'rook2-exact'
 with image.open('xb') as f:f.write(Path(b['binary_output']['path']).read_bytes())
 image.chmod(0o755);assert sha(image)==b['binary_output']['sha256']
 run(P,'generic-archive',['/usr/bin/python3',str(ROOT/'tools/archive_build.py'),str(B)])
 archive=load(B/'archive-receipt.json');assert archive['files']==69 and archive['binary_sha256']==sha(image)
 assert sha(B/archive['archive'])==archive['sha256']
 with tarfile.open(B/archive['archive'],'r:gz') as t:
  actual={member.name:hashlib.sha256(t.extractfile(member).read()).hexdigest() for member in t}
 assert actual=={**m['native46'],**m['tools23']}
 guard();write(P/'build-result.json',{'complete':True,'engine_sha256':sha(image),'source46_tools23_stable':True,'archive69_reopened':True,'compiler_generic_equal_control':True,'build_receipt':str(B/'receipt.json')})
 print('BUILD IMAGE '+sha(image),flush=True)

def native():
 m,s=guard();assert load(P/'build-result.json')['complete'];N.mkdir()
 b=load(B/'receipt.json');env=os.environ.copy()
 for k,v in b['build_effective_environment'].items():
  if v is None:env.pop(k,None)
  else:env[k]=v
 target=s/'target/native-tests-generic-01'
 argv=['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--manifest-path',str(s/'Cargo.toml'),'--target-dir',str(target),'--jobs','4','--lib','--bin','rook2-dev','--no-run','--message-format=json-render-diagnostics']
 commands=[run(N,'cargo-tests',argv,env)]
 artifacts=[json.loads(line) for line in (N/'cargo-tests.stdout').read_text().splitlines() if line.strip()]
 assert any(x.get('reason')=='build-finished' and x['success'] for x in artifacts)
 tests={}
 for a in artifacts:
  if a.get('reason')!='compiler-artifact' or not a.get('profile',{}).get('test') or not a.get('executable'):continue
  name=a['target']['name'];key='lib' if name=='rook2' and 'lib' in a['target']['kind'] else ('dev' if name=='rook2-dev' else None)
  if key:
   assert key not in tests
   original=Path(a['executable']);frozen=N/('rook2-'+key+'-tests-exact')
   with frozen.open('xb') as f:f.write(original.read_bytes())
   frozen.chmod(0o755);assert sha(frozen)==sha(original)
   tests[key]={'original_executable':str(original),'executable':str(frozen),'sha256':sha(frozen)}
 assert set(tests)=={'lib','dev'}
 for key,count in [('dev',2),('lib',182)]:
  commands.append(run(N,key+'-tests',[tests[key]['executable'],'--test-threads=1'],env))
  text=(N/(key+'-tests.stdout')).read_text();assert (N/(key+'-tests.stderr')).read_bytes()==b''
  assert len([x for x in text.splitlines() if x.startswith('test ') and x.endswith(' ... ok')])==count
  assert f'test result: ok. {count} passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;' in text
  tests[key]['passed']=count
 for name in ['pure_cache_exact_collision_clear_and_heap_entry_layout', 'pure_cache_placement_reuse_ignores_chronology_rules_and_reweights_live', 'pure_cache_hit_still_replaces_interfering_pawn_cache_and_charges_all_work', 'pure_cache_all_public_custom_map_paths_bypass_reads_and_writes', 'pure_cache_trusted_default_and_observed_selectors_keep_native_stages', 'pure_cache_matches_uncached_whole_evaluation_through_special_children']:assert 'evaluator::tests::'+name+' ... ok' in (N/'lib-tests.stdout').read_text()
 assert 'influence::tests::all_byte_pairs_and_exclusions_match_independent_digit_reference ... ok' in (N/'lib-tests.stdout').read_text()
 guard();write(N/'result.json',{'complete':True,'failure':None,'source_root':str(s),'commands':commands,'tests':tests,'total_tests':184,'engine_sha256':sha(B/'rook2-exact'),'source_and_tools_unchanged':True,'test_environment':{k:env.get(k) for k in b['build_effective_environment']}})
 print('NATIVE184 PASS',flush=True)

def regression():
 guard();assert load(N/'result.json')['total_tests']==184;R.mkdir()
 binding=load(P/'execution-binding.json');before={path:sha(path) for path in binding['authority_sha256']};image=B/'rook2-exact';digest=sha(image)
 commands=[run(R,'strict54',['/usr/bin/node',str(KIT/'profiling/replay-check.mjs'),'--',str(image)])]
 report=load(R/'strict54.stdout');workloads=load(KIT/'profiling/workloads.json')
 assert len(workloads['cases'])==54 and report['selectedCases']==[x['id'] for x in workloads['cases']]
 assert report['status']=='pass' and len(report['results'])==54 and (R/'strict54.stderr').read_bytes()==b''
 for row in report['results']:assert row['status']=='pass' and row['complete'] and row['error'] is None and row['exit']=={'code':0,'signal':None}
 commands.append(run(R,'wire-driver',['/usr/bin/python3',str(ROOT/'tools/check_live.py'),'--engine',str(image),'--output',str(R/'wire')]))
 wire=load(R/'wire/receipt.json');assert wire['pass'] and len(wire['results'])==8
 assert sum(len(x['searches']) for x in wire['results'])==24
 assert wire['engine_sha256_before']==wire['engine_sha256_after']==digest==sha(image) and wire['effective_affinity']==H
 for row in wire['results']:
  assert row['observed_exit_code']==0 and row['complete_streams']
  for name,record in row['raw'].items():
   file=R/'wire'/row['id']/(name+'.raw');assert file.stat().st_size==record['bytes'] and sha(file)==record['sha256']
 after={path:sha(path) for path in before};assert after==before;guard()
 write(R/'result.json',{'complete':True,'failure':None,'engine_sha256':digest,'commands':commands,'input_sha256_before':before,'input_sha256_after':after,'helper_and_engine_inherited_affinity':H,'strict54_pass':True,'interruption_fixtures':8,'interruption_searches':24,'source_and_tool_identity_unchanged':True,'untimed':True,'scope':'Isolated placement pure-component cache functional checks on activity/fullbyte baseline; no pawn fusion/TT reciprocal/timing/adoption'})
 print('STRICT54 WIRE8/24 PASS',flush=True)
if __name__=='__main__':
 authorized();stage=sys.argv[1];assert stage in ['build','native','regression']
 try:globals()[stage]()
 except BaseException as error:write(P/(stage+'-failure.json'),{'stage':stage,'failure':repr(error),'halt_dependent_stages':True});raise
