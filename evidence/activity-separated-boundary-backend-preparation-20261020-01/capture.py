#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys
P=Path(__file__).resolve().parent;E=P.parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
SIDES={'control':('tactical-check-mask',None), 'candidate':('activity-separated-boundary',None)}
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
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
 for key in ['candidate_image_sha256','candidate_receipt_sha256','candidate_source_graph_sha256',
             'expected_source_counts','expected_changed_source_files','expected_added_source_files']:
  assert plan[key] is not None,key
 assert plan['candidate_source_freeze']['sha256'] and plan['candidate_build_terminal']
 assert sha(Path(plan['candidate_build_directory'])/'receipt.json')==plan['candidate_receipt_sha256']
 for path,h in plan['input_sha256'].items():assert sha(path)==h,path
 for row in [plan['candidate_build_terminal'],plan['candidate_source_freeze']]:
  assert sha(row['path'])==row['sha256'],row['path']
 terminal=load(plan['candidate_build_terminal']['path'])
 assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code']==0 and terminal['terminal_chunk_id']
 SIDES['control']=(SIDES['control'][0],plan['control_image_sha256'])
 SIDES['candidate']=(SIDES['candidate'][0],plan['candidate_image_sha256'])
 return plan

def discover():
 plan=admit()
 pins={str(P/'plan.json'):sha(P/'plan.json'),str(P/'capture.py'):sha(P/'capture.py'),str(P/'analyze.py'):sha(P/'analyze.py')};pins.update(plan['input_sha256']);pins[plan['candidate_build_terminal']['path']]=plan['candidate_build_terminal']['sha256'];pins[plan['candidate_source_freeze']['path']]=plan['candidate_source_freeze']['sha256'];receipts={};commands=[]
 for side,(name,expected) in SIDES.items():
  build=E/(name+'-generic-build-'+plan['build_dates'][side]);image=build/'rook2-exact';receipt=load(build/'receipt.json')
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
   if side=='control':
    prior=plan['control_saved_metadata'][stem]
    assert sha(prior['path'])==prior['sha256'] and sha(prior['command_path'])==prior['command_sha256']
    command=load(prior['command_path']);assert command['actual_child_return_observed'] and command['exit_code']==0
    assert str(image) in command['argv'] and sha(prior['path'])==command['stdout_sha256']
   else:commands.append(run(argv,side+'-'+stem))
 for exe in ['/usr/bin/nm','/usr/bin/objdump','/usr/bin/readelf','/usr/bin/size']:
  pins[exe]=sha(exe)
  prior=plan['saved_tool_versions'][Path(exe).name]
  assert sha(prior['path'])==prior['sha256'] and sha(prior['command_path'])==prior['command_sha256']
  command=load(prior['command_path']);assert command['actual_child_return_observed'] and command['exit_code']==0
  assert command['argv']==[exe,'--version'] and sha(prior['path'])==command['stdout_sha256']
 a,b=receipts.values()
 for key in ['toolchain','mode','target_triple','target_cpu','jobs','rust_flags','build_effective_environment','cargo_config_sha256_before']:
  assert a[key]==b[key],key
 assert a['tool_sha256_before']==b['tool_sha256_before']
 assert set(a['source_sha256_before'])<=set(b['source_sha256_before'])
 changed=sorted(n for n in a['source_sha256_before'] if a['source_sha256_before'][n]!=b['source_sha256_before'][n])
 added=sorted(set(b['source_sha256_before'])-set(a['source_sha256_before']))
 assert changed==plan['expected_changed_source_files'] and added==plan['expected_added_source_files']
 assert a['source_sha256_before']['Cargo.toml']==b['source_sha256_before']['Cargo.toml']
 assert a['source_sha256_before']['Cargo.lock']==b['source_sha256_before']['Cargo.lock']
 freeze=load(plan['candidate_source_freeze']['path'])
 assert sha(plan['candidate_source_freeze']['path'])==plan['candidate_source_freeze']['sha256']
 assert freeze['source_preparation_accepted'] is True and freeze['source_graph_sha256']==plan['candidate_source_graph_sha256']
 assert b['source_sha256_before']|b['tool_sha256_before']==freeze['files_sha256']
 assert len(a['source_sha256_before'])==51 and len(a['tool_sha256_before'])==23
 counts=plan['expected_source_counts']
 assert len(b['source_sha256_before'])==counts['native'] and len(b['tool_sha256_before'])==counts['tools']==23
 assert counts['total']==counts['native']+counts['tools']
 assert b['mode']=='generic' and b['pgo']['mode']=='none'
 assert all(sha(p)==h for p,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,compiler_settings_equal=True,changed_source_files=changed,added_source_files=added,source_counts=counts,tools23_equal=True))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),only_changed=changed)))

def bodies():
 plan=admit()
 d=load(P/'discovery.json');assert all(sha(p)==h for p,h in d['pins'].items())
 request=load(P/'body-request.json');assert 0<len(request)<=plan['max_complete_bodies']==12
 assert len({(r['side'],r['start']) for r in request})==len(request)
 total=0;scope_total=0;rows=[]
 for row in request:
  side=row['side'];name,_=SIDES[side];image=E/(name+'-generic-build-'+plan['build_dates'][side])/'rook2-exact'
  start=int(row['start'],16);size=int(row['bytes']);assert size>0
  assert row['label'] in plan['allowed_body_labels'] and row['complete_body'] is True
  assert any(fragment in row['actual_symbol'] for fragment in plan['allowed_symbol_fragments'][row['label']])
  assert side in ('control','candidate')
  if row['label'] in plan['candidate_only_body_labels']:assert side=='candidate'
  assert row.get('role_provenance',{}).get('source_owner') and row['role_provenance'].get('actual_caller_or_entry_evidence'),row
  exact=' '.join([format(start,'016x'),format(size,'016x')])
  symbol_rows=[]
  nm_path=Path(plan['control_saved_metadata']['nm']['path']) if side=='control' else P/(side+'-nm.stdout')
  for line in nm_path.read_text().splitlines():
   parts=line.split(maxsplit=3)
   if len(parts)==4 and parts[2] in ['t','T'] and int(parts[0],16)==start and int(parts[1],16)==size:symbol_rows.append(parts[3])
  assert row['actual_symbol'] in symbol_rows,(row,symbol_rows)
  mangled_path=Path(plan['control_saved_metadata']['nm-mangled']['path']) if side=='control' else P/(side+'-nm-mangled.stdout')
  mangled_rows=[]
  for line in mangled_path.read_text().splitlines():
   parts=line.split(maxsplit=3)
   if len(parts)==4 and parts[2] in ['t','T'] and int(parts[0],16)==start and int(parts[1],16)==size:mangled_rows.append(parts[3])
  assert row['actual_mangled_symbol'] in mangled_rows,(row,mangled_rows)
  if row.get('reuse'):
   assert side=='control'
   prior=plan['reusable_control_bodies'][row['label']]
   assert prior['start']==row['start'] and prior['bytes']==size and prior['actual_symbol']==row['actual_symbol']
   assert row['reuse']==prior['stdout_path'] and sha(prior['stdout_path'])==prior['stdout_sha256']
   assert sha(prior['command_path'])==prior['command_sha256']
   result=load(prior['command_path']);assert result['actual_child_return_observed'] and result['exit_code']==0 and str(image) in result['argv']
   assert result['stdout_sha256']==prior['stdout_sha256']
   raw_path=Path(prior['stdout_path']);reused=True
  else:
   stem=side+'-'+row['label']
   result=run(['/usr/bin/objdump','-d','-l','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)],stem)
   raw_path=P/(stem+'.stdout');total+=raw_path.stat().st_size;reused=False
  assert total<=plan['max_new_raw_disassembly_bytes']==3145728,total
  scope_total+=raw_path.stat().st_size
  rows.append(dict(**row,command=result,raw_path=str(raw_path),raw_bytes=raw_path.stat().st_size,reused=reused))
 assert all(sha(p)==h for p,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=total,total_scope_raw_bytes=scope_total,all_discovery_inputs_unchanged=True))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=total)))
if __name__=='__main__':
 {'discover':discover,'bodies':bodies}[sys.argv[1]]()
