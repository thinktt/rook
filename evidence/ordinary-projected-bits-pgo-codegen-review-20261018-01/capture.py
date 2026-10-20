"""Own frozen separately trained PGO images only. Inert until explicit parent authority is supplied."""
from pathlib import Path
import hashlib,json,os,subprocess
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'plan.json').read_text())
AFFINITY=PLAN['affinity']
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def guard():
 assert sorted(os.sched_getaffinity(0))==AFFINITY
 assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 for p,h in json.loads((HERE/'input-pins.json').read_text()).items():assert sha(p)==h,p
 for p,h in json.loads((HERE/'helper-pins.json').read_text()).items():assert sha(HERE/p)==h,p
 a=json.loads((HERE/'authority.json').read_text());assert a['capture'] is True,'capture lacks explicit parent clearance'
 assert len(a['candidate_image_sha256'])==len(a['candidate_receipt_sha256'])==64
 decision=a['parent_source_review'];assert decision and sha(decision['path'])==decision['sha256']
 for key in ['candidate_independent_proof','candidate_reconcile_tool_terminal','candidate_build_tool_terminal']:
  pin=a[key];assert pin and sha(pin['path'])==pin['sha256']
  data=json.loads(Path(pin['path']).read_text())
  if key=='candidate_independent_proof':
   assert data['complete'] is True and data['own_profile_only'] is True
   variant=data['variants']['ordinary-projected-bits']
   assert variant['artifact_sha256']==a['candidate_image_sha256']
   assert variant['build_receipt_sha256']==a['candidate_receipt_sha256']
  else:
   assert data.get('actual_tool_terminal_observed') is True and data['exit_code']==0
   chunk=data.get('terminal_chunk_id') or data.get('chunk_id');assert isinstance(chunk,str) and chunk.strip()
 return a

def main():
 authority=guard();inputs={};receipts={};identities={};commands=[];profile_bindings={}
 source_manifest=json.loads((Path(PLAN['proposal'])/'source-manifest.json').read_text())['source69']
 assert len(source_manifest)==69
 for side in ['control','candidate']:
  build=Path(PLAN[side+'_build']);rp=build/'receipt.json';receipt=json.loads(rp.read_text());receipts[side]=receipt
  image=build/'rook2-exact';expected=PLAN['control_image_sha256'] if side=='control' else authority['candidate_image_sha256']
  if side=='candidate':assert sha(rp)==authority['candidate_receipt_sha256']
  assert sha(image)==expected==receipt['binary_output']['sha256']
  assert receipt['cargo_exit_code']==0 and receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged']
  assert receipt['source_sha256_before']==receipt['source_sha256_after'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']
  assert len(receipt['source_sha256_before'])==46 and len(receipt['tool_sha256_before'])==23
  smap=receipt['source_sha256_before']|receipt['tool_sha256_before']
  if side=='candidate':assert smap==source_manifest
  for rel,digest in smap.items():
   p=build/'source-before'/rel;assert sha(p)==digest,str(p);inputs[str(p)]=digest
  for p in [image,rp,build/'build.stderr',build/'archive-receipt.json',build/'verified-source-before.tar.gz']:inputs[str(p)]=sha(p)
  assert receipt['pgo']['mode']=='profile-use'
  assert receipt['pgo']['input_sha256_before']==receipt['pgo']['input_sha256_after']
  assert receipt['pgo']['inputs_unchanged']
  for path, digest in receipt['pgo']['input_sha256_before'].items():
      assert sha(path)==digest;inputs[path]=digest
  training_path=Path(receipt['pgo']['training_record'])
  verification_path=training_path.parent/'verification.json'
  training=json.loads(training_path.read_text())
  verification=json.loads(verification_path.read_text())
  assert training['complete'] and training['engine_source_sha256']==receipt['source_sha256_before']
  assert len(training['raw_profiles_sha256'])==54
  assert training['profile_sha256']==sha(receipt['pgo']['profile'])==verification['merged_profile_sha256']
  assert verification['complete'] and verification['independent_remerge_byte_identical']
  assert verification['training_record_sha256']==sha(training_path)
  assert receipt['rust_flags']==['-C','target-cpu=x86-64','-C',
      'profile-use='+receipt['pgo']['profile'],'-C','llvm-args=-pgo-warn-missing-function']
  warnings=(build/'build.stderr').read_text().lower()
  for token in ['no profile data available for function','profile data may be out of date',
                'profile data mismatch','malformed instrumentation profile data','hash mismatch','unprofiled function']:
      assert token not in warnings
  inputs[str(verification_path)]=sha(verification_path)
  profile_bindings[side]=dict(profile=receipt['pgo']['profile'],
      profile_sha256=sha(receipt['pgo']['profile']),training_record=str(training_path),
      training_record_sha256=sha(training_path),verification=str(verification_path),
      verification_sha256=sha(verification_path),training_input_sha256=training['input_sha256'],
      own_source_training54=True,independent_remerge_byte_identical=True)
  dest=HERE/side;dest.mkdir()
  for name,argv in [('nm-demangled',['/usr/bin/nm','-n','-S','-C',str(image)]),('nm-mangled',['/usr/bin/nm','-n','-S',str(image)]),('sections',['/usr/bin/readelf','-W','-S',str(image)]),('relocations',['/usr/bin/readelf','-W','-r',str(image)])]:
   cmd=['/usr/bin/taskset','-c','0-5,8-13',*argv]
   with (dest/(name+'.stdout')).open('xb') as out,(dest/(name+'.stderr')).open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
   commands.append({'side':side,'name':name,'argv':cmd,'exit_code':r.returncode,'actual_child_return_observed':True});assert r.returncode==0
  identities[side]={'image':str(image),'image_sha256':expected,'receipt':str(rp),'receipt_sha256':sha(rp)}
 def normalize(value,profile):
  if isinstance(value,str):return value.replace(profile,'<OWN-PROFILE>')
  if isinstance(value,list):return [normalize(x,profile) for x in value]
  if isinstance(value,dict):return {k:normalize(v,profile) for k,v in value.items()}
  return value
 for field in ['mode','target_triple','target_cpu','jobs','rust_flags','environment_overrides','build_effective_environment','toolchain','cargo_config_sha256_before','cargo_config_sha256_after']:
  assert normalize(receipts['control'][field],receipts['control']['pgo']['profile'])==normalize(receipts['candidate'][field],receipts['candidate']['pgo']['profile']),field
 assert profile_bindings['control']['profile_sha256']!=profile_bindings['candidate']['profile_sha256']
 assert profile_bindings['control']['training_input_sha256']==profile_bindings['candidate']['training_input_sha256']
 assert receipts['control']['tool_sha256_before']==receipts['candidate']['tool_sha256_before']
 changes=[p for p,h in receipts['control']['source_sha256_before'].items() if h!=receipts['candidate']['source_sha256_before'][p]]
 assert sorted(changes)==sorted(PLAN['expected_changed_native_files'])
 versions={}
 for name in ['nm','readelf','objdump']:
  tool='/usr/bin/'+name;inputs[tool]=sha(tool);cmd=['/usr/bin/taskset','-c','0-5,8-13',tool,'--version']
  with (HERE/(name+'-version.stdout')).open('xb') as out,(HERE/(name+'-version.stderr')).open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
  assert r.returncode==0;versions[name]={'argv':cmd,'exit_code':r.returncode,'actual_child_return_observed':True,'sha256':inputs[tool]}
 assert all(sha(p)==h for p,h in inputs.items())
 write(HERE/'identity.json',{'complete':True,'images':identities,'source_input_sha256':inputs,'changed_native_sources':changes,'own_profile_bindings':profile_bindings,'commands':commands,'versions':versions,'engine_runs':0,'build_runs':0,'performance_claim':False})
 print(json.dumps({'complete':True,'changed_sources':changes,'native_engine_runs':0}))
if __name__=='__main__':main()
