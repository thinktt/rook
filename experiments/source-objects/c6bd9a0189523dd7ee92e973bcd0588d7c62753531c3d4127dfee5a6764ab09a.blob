#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys
P=Path(__file__).resolve().parent;E=P.parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
SIDES={'control':('influence-bitsliced-sum',None), 'candidate':('influence-source-range',None)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(p,j):
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n')
def run(argv,stem):
 with (P/(stem+'.stdout')).open('xb') as out,(P/(stem+'.stderr')).open('xb') as err:
  child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
 row=dict(argv=argv,pid=child.pid,actual_child_return_observed=True,exit_code=code,stdout_sha256=sha(P/(stem+'.stdout')),stderr_sha256=sha(P/(stem+'.stderr')))
 save(P/(stem+'-command.json'),row);assert code==0,row
 return row

def admit():
 plan=load(P/'plan.json')
 assert plan['launch'] is True and plan['parent_backend_activation'] is True
 assert os.sched_getaffinity(0)==H and os.environ['PATH']=='/usr/bin:/bin'
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
 assert plan['candidate_image_sha256'] and plan['candidate_build_terminal'] is not None
 for path,h in plan['input_sha256'].items():assert sha(path)==h,path
 row=plan['candidate_build_terminal'];assert sha(row['path'])==row['sha256']
 terminal=load(row['path']);assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code']==0 and terminal['terminal_chunk_id']
 SIDES['control']=(SIDES['control'][0],plan['control_image_sha256'])
 SIDES['candidate']=(SIDES['candidate'][0],plan['candidate_image_sha256'])
 return plan

def discover():
 plan=admit()
 pins={str(P/'plan.json'):sha(P/'plan.json'),str(P/'capture.py'):sha(P/'capture.py'),str(P/'analyze.py'):sha(P/'analyze.py')};pins.update(plan['input_sha256']);pins[plan['candidate_build_terminal']['path']]=plan['candidate_build_terminal']['sha256'];receipts={};commands=[]
 for side,(name,expected) in SIDES.items():
  build=E/(name+'-generic-build-20261019-01');image=build/'rook2-exact';receipt=load(build/'receipt.json')
  assert sha(image)==expected==receipt['binary_output']['sha256']
  assert receipt['source_sha256_before']==receipt['source_sha256_after'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']
  assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged']
  assert receipt['mode']=='generic' and receipt['pgo']['mode']=='none'
  for p in [image,build/'receipt.json',build/'frozen-image.json']:
   pins[str(p)]=sha(p)
  for name2,h in (receipt['source_sha256_before']|receipt['tool_sha256_before']).items():
   q=build/'source-before'/name2;assert sha(q)==h;pins[str(q)]=h
  receipts[side]=receipt
  for stem,argv in [('nm',['/usr/bin/nm','-n','-S','--defined-only','--demangle',str(image)]),('nm-mangled',['/usr/bin/nm','-n','-S','--defined-only',str(image)]),('sections',['/usr/bin/readelf','-SW',str(image)]),('relocations',['/usr/bin/readelf','-rW',str(image)]),('size',['/usr/bin/size','-A',str(image)])]:
   commands.append(run(argv,side+'-'+stem))
 for exe in ['/usr/bin/nm','/usr/bin/objdump','/usr/bin/readelf','/usr/bin/size']:
  pins[exe]=sha(exe);commands.append(run([exe,'--version'],Path(exe).name+'-version'))
 a,b=receipts.values()
 for key in ['toolchain','mode','target_triple','target_cpu','jobs','rust_flags','build_effective_environment','cargo_config_sha256_before']:
  assert a[key]==b[key],key
 assert a['tool_sha256_before']==b['tool_sha256_before']
 changed=sorted(n for n in a['source_sha256_before'] if a['source_sha256_before'][n]!=b['source_sha256_before'][n]);assert changed==['src/attacks.rs']
 freeze=load(plan['candidate_source_freeze']['path'])
 assert sha(plan['candidate_source_freeze']['path'])==plan['candidate_source_freeze']['sha256']
 assert freeze['source_preparation_accepted'] is True and freeze['source_graph_sha256']==plan['candidate_source_graph_sha256']
 assert b['source_sha256_before']|b['tool_sha256_before']==freeze['files_sha256']
 assert len(b['source_sha256_before'])==49 and len(b['tool_sha256_before'])==23
 assert b['mode']=='generic' and b['pgo']['mode']=='none'
 assert all(sha(p)==h for p,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,compiler_settings_equal=True,only_attacks_source_changed=changed,source_files=72,native49_tools23=True))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),only_changed=changed)))

def bodies():
 plan=admit()
 d=load(P/'discovery.json');assert all(sha(p)==h for p,h in d['pins'].items())
 request=load(P/'body-request.json');assert len(request)<=12
 total=0;rows=[]
 for row in request:
  side=row['side'];name,_=SIDES[side];image=E/(name+'-generic-build-20261019-01')/'rook2-exact'
  start=int(row['start'],16);size=int(row['bytes']);assert size>0
  assert row['label'] in plan['allowed_body_labels'] and row['complete_body'] is True
  exact=' '.join([format(start,'016x'),format(size,'016x')])
  symbol_rows=[]
  for line in (P/(side+'-nm.stdout')).read_text().splitlines():
   parts=line.split(maxsplit=3)
   if len(parts)==4 and parts[2] in ['t','T'] and int(parts[0],16)==start and int(parts[1],16)==size:symbol_rows.append(parts[3])
  assert row['actual_symbol'] in symbol_rows,(row,symbol_rows)
  stem=side+'-'+row['label']
  result=run(['/usr/bin/objdump','-d','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)],stem)
  total+=(P/(stem+'.stdout')).stat().st_size;assert total<=1048576,total
  rows.append(dict(**row,command=result,raw_bytes=(P/(stem+'.stdout')).stat().st_size))
 assert all(sha(p)==h for p,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=total,all_discovery_inputs_unchanged=True))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=total)))
if __name__=='__main__':
 {'discover':discover,'bodies':bodies}[sys.argv[1]]()
