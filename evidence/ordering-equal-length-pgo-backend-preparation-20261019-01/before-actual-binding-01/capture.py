#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
P=Path(__file__).resolve().parent;E=P.parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
SIDES={'control':('influence-bitsliced-sum',None), 'candidate':('ordering-equal-length',None)}
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
 assert plan['candidate_source_graph_sha256'] and plan['candidate_source_freeze']['sha256']
 assert plan['candidate_receipt_sha256'] and sha(E/'ordering-equal-length-pgo-use-build-20261019-01'/'receipt.json')==plan['candidate_receipt_sha256']
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 assert plan['profile_sha256']['candidate'] and plan['actual_stage_pins']['candidate']
 for path,h in plan['input_sha256'].items():assert sha(path)==h,path
 row=plan['candidate_build_terminal'];assert sha(row['path'])==row['sha256']
 terminal=load(row['path']);assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code']==0 and terminal['terminal_chunk_id']
 decision=load(plan['generic_advancement']['decision_path']);generic=load(plan['generic_advancement']['independent_path'])
 assert decision['experiment']==49 and decision['decision']=='ADVANCE_TO_OWN_PGO_ONLY' and decision['pgo_authorized'] is True
 assert decision['source_graph_sha256']==plan['candidate_source_graph_sha256']
 assert generic['complete'] is True and generic['advance_under_declared_rule'] is True and generic['lifetimes']==70 and generic['excluded_warmups']==14 and generic['measured']==56
 SIDES['control']=(SIDES['control'][0],plan['control_image_sha256'])
 SIDES['candidate']=(SIDES['candidate'][0],plan['candidate_image_sha256'])
 return plan

def own_pgo(side,name,receipt,plan,pins):
 build=E/(name+'-pgo-use-build-20261019-01');inst=E/(name+'-pgo-instrumented-build-20261019-01');training=E/(name+'-pgo-training-20261019-01');prep=E/(name+'-pgo-preparation-20261019-01')
 ir=load(inst/'receipt.json');tr=load(training/'training.json');v=load(training/'verification.json');r=receipt
 assert r['mode']=='generic' and r['pgo']['mode']=='profile-use' and r['cargo_exit_code']==0
 assert ir['mode']=='generic' and ir['pgo']['mode']=='instrumented' and ir['cargo_exit_code']==0
 assert r['source_sha256_before']==r['source_sha256_after']==ir['source_sha256_before']==ir['source_sha256_after']==tr['engine_source_sha256']
 assert r['tool_sha256_before']==r['tool_sha256_after']==ir['tool_sha256_before']==ir['tool_sha256_after']
 assert ir['toolchain']==r['toolchain']
 assert sha(inst/'receipt.json')==tr['instrumented_build_receipt']['sha256']
 assert ir['binary_output']['sha256']==tr['instrumented_engine_sha256']
 assert r['pgo']['input_sha256_before']==r['pgo']['input_sha256_after'] and r['pgo']['inputs_unchanged']
 profile=Path(r['pgo']['profile']);expected=plan['profile_sha256'][side]
 assert profile==training/'merged.profdata'
 assert sha(profile)==expected==tr['profile_sha256']==v['merged_profile_sha256']==v['independent_profile_sha256']
 assert set(r['pgo']['input_sha256_before'])=={str(profile),str(training/'training.json')}
 assert r['pgo']['input_sha256_before'][str(profile)]==expected
 assert v['complete'] and v['independent_remerge_byte_identical'] and v['independent_remerge_exit_code']==0
 assert all(v[k]==54 for k in ['strict_replays','original_checkReplay_count','raw_training_protocol_cases','raw_profiles_independently_hashed'])
 assert len(tr['raw_profiles_sha256'])==54 and tr['complete']
 assert sha(training/'training.json')==v['training_record_sha256']==r['pgo']['input_sha256_before'][str(training/'training.json')]
 paths={'instrumented':inst/'tool-terminal.json','training':training/'tool-terminal.json','verification':training/'verify-tool-terminal.json','use':build/'tool-terminal.json'}
 assert set(plan['actual_stage_pins'][side])==set(paths)
 stages={}
 for stage,path in paths.items():
  prior=plan['actual_stage_pins'][side][stage];assert prior['path']==str(path) and sha(path)==prior['sha256']
  term=load(path);assert term['actual_tool_terminal_observed'] is True and term['exit_code']==0 and (term.get('terminal_chunk_id') or term.get('chunk_id') or '').strip()
  pins[str(path)]=sha(path);stages[stage]=term
 for stage in ['instrumented','use']:
  path=prep/(stage+'-stage.json');meta=load(path);assert meta['complete'] and meta['missing_or_stale_profile_warnings']==0;pins[str(path)]=sha(path)
  assert meta['artifact_sha256']==(ir if stage=='instrumented' else r)['binary_output']['sha256']
  for unit,options in meta['effective_rustc_options'].items():
   assert options['opt-level']=='3' and options['panic']=='abort' and options['codegen-units']=='1' and options['debuginfo']=='1' and options['target-cpu']=='x86-64'
   if unit=='src/bin/rook2.rs':assert options['lto']=='thin'
   if stage=='use':assert options['profile-use']==str(profile)
 for path in [build/'archive-receipt.json',build/'build.stderr',inst/'receipt.json',inst/'frozen-image.json',training/'training.json',training/'verification.json',profile]:pins[str(path)]=sha(path)
 log=(build/'build.stderr').read_text();binary=[line for line in log.splitlines() if 'Running ' in line and '--crate-type bin' in line and 'src/bin/rook2.rs' in line]
 assert len(binary)==1 and '-C lto=thin ' in binary[0] and '-C codegen-units=1 ' in binary[0] and ('profile-use='+str(profile)+' ') in binary[0]
 assert not re.search(r'no profile data|mismatched.*profile|out[- ]of[- ]date.*profile|function control flow change detected|hash mismatch',log,re.I)
 assert r['rust_flags']==['-C','target-cpu=x86-64','-C','profile-use='+str(profile),'-C','llvm-args=-pgo-warn-missing-function']
 env=dict(r['build_effective_environment'])
 for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS']:
  assert isinstance(env[key],str) and env[key].count(str(profile))==1
  env[key]=env[key].replace(str(profile),'<OWN_PROFILE>')
 return env,dict(image=r['binary_output']['sha256'],profile=expected,actual_stages=stages,verified_original_training=54,independent_remerge_byte_identical=True,missing_stale_profile_warnings=0)

def discover():
 plan=admit()
 pins={str(P/'plan.json'):sha(P/'plan.json'),str(P/'capture.py'):sha(P/'capture.py'),str(P/'analyze.py'):sha(P/'analyze.py')};pins.update(plan['input_sha256']);pins[plan['candidate_build_terminal']['path']]=plan['candidate_build_terminal']['sha256'];receipts={};commands=[];normalized_env={};bindings={}
 for side,(name,expected) in SIDES.items():
  build=E/(name+'-pgo-use-build-20261019-01');image=build/'rook2-exact';receipt=load(build/'receipt.json')
  assert sha(image)==expected==receipt['binary_output']['sha256']
  assert receipt['source_sha256_before']==receipt['source_sha256_after'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']
  assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged']
  assert receipt['mode']=='generic' and receipt['pgo']['mode']=='profile-use'
  normalized_env[side],bindings[side]=own_pgo(side,name,receipt,plan,pins)
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
 for key in ['toolchain','mode','target_triple','target_cpu','jobs','cargo_config_sha256_before']:
  assert a[key]==b[key],key
 assert normalized_env['control']==normalized_env['candidate']
 assert a['tool_sha256_before']==b['tool_sha256_before']
 assert set(a['source_sha256_before'])==set(b['source_sha256_before'])
 changed=sorted(n for n in a['source_sha256_before'] if a['source_sha256_before'][n]!=b['source_sha256_before'][n]);assert changed==['src/tactical.rs']
 freeze=load(plan['candidate_source_freeze']['path'])
 assert sha(plan['candidate_source_freeze']['path'])==plan['candidate_source_freeze']['sha256']
 assert freeze['source_preparation_accepted'] is True and freeze['source_graph_sha256']==plan['candidate_source_graph_sha256']
 assert b['source_sha256_before']|b['tool_sha256_before']==freeze['files_sha256']
 assert len(b['source_sha256_before'])==49 and len(b['tool_sha256_before'])==23
 assert b['mode']=='generic' and b['pgo']['mode']=='profile-use'
 assert all(sha(p)==h for p,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,own_pgo_bindings=bindings,only_own_profile_paths_normalized=True,compiler_settings_equal=True,only_tactical_source_changed=changed,source_files=72,native49_tools23=True))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),only_changed=changed)))

def bodies():
 plan=admit()
 d=load(P/'discovery.json');assert all(sha(p)==h for p,h in d['pins'].items())
 request=load(P/'body-request.json');assert 0<len(request)<=plan['max_complete_bodies']==6
 primary=[(row['side'],row['label']) for row in request if row['label']!='sorting-helper']
 assert len(primary)==4 and set(primary)=={(side,label) for side in ['control','candidate'] for label in ['ordinary','q']}
 total=0;scope_total=0;rows=[]
 for row in request:
  side=row['side'];name,_=SIDES[side];image=E/(name+'-pgo-use-build-20261019-01')/'rook2-exact'
  start=int(row['start'],16);size=int(row['bytes']);assert size>0
  assert row['label'] in plan['allowed_body_labels'] and row['complete_body'] is True
  exact=' '.join([format(start,'016x'),format(size,'016x')])
  symbol_rows=[]
  nm_path=Path(plan['control_saved_metadata']['nm']['path']) if side=='control' else P/(side+'-nm.stdout')
  for line in nm_path.read_text().splitlines():
   parts=line.split(maxsplit=3)
   if len(parts)==4 and parts[2] in ['t','T'] and int(parts[0],16)==start and int(parts[1],16)==size:symbol_rows.append(parts[3])
  assert row['actual_symbol'] in symbol_rows,(row,symbol_rows)
  role={'ordinary':'rook2::ordinary::','q':'rook2::quiescence::','sorting-helper':'rook2::tactical::'}[row['label']]
  assert role in row['actual_symbol']
  if row['label']=='sorting-helper':assert any(part in row['actual_symbol'] for part in ['priority_sequence','order_by','order_with_scratch'])
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
  assert total<=plan['max_new_raw_disassembly_bytes']==2097152,total
  scope_total+=raw_path.stat().st_size
  rows.append(dict(**row,command=result,raw_path=str(raw_path),raw_bytes=raw_path.stat().st_size,reused=reused))
 assert all(sha(p)==h for p,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=total,total_scope_raw_bytes=scope_total,all_discovery_inputs_unchanged=True))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=total)))
if __name__=='__main__':
 {'discover':discover,'bodies':bodies}[sys.argv[1]]()
