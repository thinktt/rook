"""Own frozen generic images only. Inert until explicit parent authority is supplied."""
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
 assert a['plan_sha256']==sha(HERE/'plan.json')
 assert len(a['candidate_image_sha256'])==len(a['candidate_receipt_sha256'])==64
 assert isinstance(a['candidate_source_graph_sha256'],str) and len(a['candidate_source_graph_sha256'])==64
 for key in ['parent_source_review','candidate_source_manifest','candidate_build_actual']:
  pin=a[key];assert pin and sha(pin['path'])==pin['sha256'],key
 t=json.loads(Path(a['candidate_build_actual']['path']).read_text())
 assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0
 assert t.get('terminal_chunk_id') or t.get('chunk_id')
 return a

def main():
 authority=guard();inputs={};receipts={};identities={};commands=[]
 manifest=json.loads(Path(authority['candidate_source_manifest']['path']).read_text())
 source_manifest=manifest.get('source69',manifest.get('files'))
 assert isinstance(source_manifest,dict) and len(source_manifest)==69
 assert all(isinstance(v,str) and len(v)==64 for v in source_manifest.values())
 # Unknown source-release schema stops before binary tools; no guessed source pin.
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
  archive=json.loads((build/'archive-receipt.json').read_text())
  assert archive['files']==69 and archive['verified_against_build_before_hashes']
  assert archive['binary_sha256']==expected
  archived=build/archive['archive'];assert sha(archived)==archive['sha256']
  for p in [image,rp,build/'build.stderr',build/'archive-receipt.json',archived]:inputs[str(p)]=sha(p)
  dest=HERE/side;dest.mkdir()
  for name,argv in [('nm-demangled',['/usr/bin/nm','-n','-S','-C',str(image)]),('nm-mangled',['/usr/bin/nm','-n','-S',str(image)]),('sections',['/usr/bin/readelf','-W','-S',str(image)]),('relocations',['/usr/bin/readelf','-W','-r',str(image)])]:
   cmd=['/usr/bin/taskset','-c','0-5,8-13',*argv]
   with (dest/(name+'.stdout')).open('xb') as out,(dest/(name+'.stderr')).open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
   commands.append({'side':side,'name':name,'argv':cmd,'exit_code':r.returncode,'actual_child_return_observed':True});assert r.returncode==0
  identities[side]={'image':str(image),'image_sha256':expected,'receipt':str(rp),'receipt_sha256':sha(rp)}
 for field in ['mode','target_triple','target_cpu','jobs','rust_flags','environment_overrides','build_effective_environment','toolchain','pgo','cargo_config_sha256_before','cargo_config_sha256_after']:assert receipts['control'][field]==receipts['candidate'][field],field
 assert receipts['candidate']['pgo']['mode']=='none'
 assert receipts['control']['tool_sha256_before']==receipts['candidate']['tool_sha256_before']
 changes=[p for p,h in receipts['control']['source_sha256_before'].items() if h!=receipts['candidate']['source_sha256_before'][p]]
 assert sorted(changes)==sorted(PLAN['expected_changed_native_files'])
 versions={}
 for name in ['nm','readelf','objdump']:
  tool='/usr/bin/'+name;inputs[tool]=sha(tool);cmd=['/usr/bin/taskset','-c','0-5,8-13',tool,'--version']
  with (HERE/(name+'-version.stdout')).open('xb') as out,(HERE/(name+'-version.stderr')).open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
  assert r.returncode==0;versions[name]={'argv':cmd,'exit_code':r.returncode,'actual_child_return_observed':True,'sha256':inputs[tool]}
 assert all(sha(p)==h for p,h in inputs.items())
 write(HERE/'identity.json',{'complete':True,'images':identities,'source_input_sha256':inputs,'changed_native_sources':changes,'commands':commands,'versions':versions,'engine_runs':0,'build_runs':0,'performance_claim':False})
 print(json.dumps({'complete':True,'changed_sources':changes,'native_engine_runs':0}))
if __name__=='__main__':main()
