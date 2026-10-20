#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,resource,re
P=Path(__file__).resolve().parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
ENTERED=time.monotonic();DEADLINE=None

def check():
 assert DEADLINE is not None and time.monotonic()<DEADLINE, '180s whole-capture elapsed deadline'
def read(path):
 start=time.monotonic();chunks=[]
 with Path(path).open('rb') as f:
  while True:
   check();assert time.monotonic()-start<30, '30s read deadline'
   b=f.read(1048576)
   if not b:break
   chunks.append(b)
 check();return b''.join(chunks)
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def load(p):return json.loads(read(p))
def save(p,j):
 check()
 encoded=json.dumps(j,indent=2)+'\n';assert len(encoded.encode())<=8388608, '8MiB metadata file cap'
 with Path(p).open('x') as f:f.write(encoded)
def terminal(path):
 t=load(path)
 assert t.get('actual_tool_terminal_observed') is True and t['exit_code']==0
 assert t.get('terminal_chunk_id') or t.get('terminal_chunk') or t.get('chunk_id')
 return t

def setup(stage):
 global DEADLINE
 plan=json.loads((P/'plan.json').read_text())
 assert plan['launch'] is True and plan['parent_backend_activation'] is True
 assert os.sched_getaffinity(0)==H and os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
 assert plan['max_complete_bodies']==6 and plan['max_total_captured_text_bytes']==4194304
 assert plan['metadata_regular_file_cap_bytes']==8388608
 assert plan['per_read_or_command_wall_s']==30 and plan['total_elapsed_wall_s']==180
 if stage=='discover':
  DEADLINE=ENTERED+180
  save(P/'capture-clock.json',dict(started_monotonic=ENTERED,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),deadline=DEADLINE))
 else:
  c=json.loads((P/'capture-clock.json').read_text());DEADLINE=c['deadline']
  assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==c['boot_id'] and DEADLINE==c['started_monotonic']+180
 check()
 assert plan['parent_review'] and plan['quiet_clearance']
 for item in [plan['parent_review'],plan['quiet_clearance']]:assert sha(item['path'])==item['sha256']
 assert all(sha(x)==h for x,h in plan['input_sha256'].items())
 assert all(sha(x)==h for x,h in plan['runtime_sha256'].items())
 assert plan['candidate_actual_terminals'] and plan['candidate_prerequisite_records']
 for x in plan['candidate_actual_terminals']:terminal(x)
 for item in plan['candidate_prerequisite_records']:
  assert sha(item['path'])==item['sha256'] and item['checks']
  proof=load(item['path']);assert all(proof[k]==v for k,v in item['checks'].items())
 return plan

def captured_text_bytes():
 return sum(q.stat().st_size for suffix in ['*.stdout','*.stderr'] for q in P.glob(suffix))
def run(argv,stem):
 check();raw_cap=4194304-captured_text_bytes();file_cap=8388608 if stem=='analysis' else raw_cap//2;assert raw_cap>0 and file_cap>0
 started=time.monotonic();failure=None
 def cap():resource.setrlimit(resource.RLIMIT_FSIZE,(file_cap,file_cap))
 with (P/(stem+'.stdout')).open('xb') as out,(P/(stem+'.stderr')).open('xb') as err:
  child=subprocess.Popen(argv,stdout=out,stderr=err,preexec_fn=cap)
  try:code=child.wait(timeout=min(30,max(0.001,DEADLINE-time.monotonic())))
  except subprocess.TimeoutExpired:
   child.kill();code=child.wait();failure='command/aggregate deadline exceeded; stopped and reaped'
 elapsed=time.monotonic()-started
 # Preserve actual command/exit even when the deadline or output cap failed.
 row=dict(argv=argv,pid=child.pid,remaining_combined_raw_cap_before=raw_cap,per_regular_file_byte_cap=file_cap,analysis_metadata_cap_distinct_from_raw=(stem=='analysis'),actual_child_return_observed=True,exit_code=code,elapsed_wall_s=elapsed,failure=failure,stdout_bytes=(P/(stem+'.stdout')).stat().st_size,stderr_bytes=(P/(stem+'.stderr')).stat().st_size)
 with (P/(stem+'-command.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 assert captured_text_bytes()<=4194304,'aggregate raw text cap exceeded; stop and preserve failure'
 assert failure is None and code==0 and elapsed<=30 and row['stderr_bytes']==0,row
 check();row.update(stdout_sha256=sha(P/(stem+'.stdout')),stderr_sha256=sha(P/(stem+'.stderr')))
 # Hash record is separate so the observed terminal record is never overwritten.
 save(P/(stem+'-output-pins.json'),{k:row[k] for k in ['stdout_sha256','stderr_sha256']})
 return row

def effective_options(build):
 commands=[__import__('shlex').split(line.split('Running `',1)[1].rsplit('`',1)[0]) for line in read(build/'build.stderr').decode().splitlines() if 'Running `' in line and '--crate-name rook2 ' in line]
 result={}
 for source,kind in [('src/lib.rs','lib'),('src/bin/rook2.rs','bin')]:
  matches=[x for x in commands if source in x];assert len(matches)==1,(source,len(matches))
  argv=matches[0];assert argv[argv.index('--crate-type')+1]==kind
  opts={}
  for i,x in enumerate(argv):
   value=argv[i+1] if x=='-C' else x[2:] if x.startswith('-C') and len(x)>2 else None
   if value is None:continue
   k,sep,v=value.partition('=');assert k not in opts;opts[k]=v if sep else True
  for k,v in [('opt-level','3'),('panic','abort'),('codegen-units','1'),('debuginfo','1'),('target-cpu','x86-64')]:assert opts.get(k)==v
  assert opts.get('lto')=='thin' if kind=='bin' else opts.get('linker-plugin-lto') is True
  assert opts['llvm-args']=='-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false'
  result[source]=opts
 return result

def discover():
 plan=setup('discover');pins={str(P/n):sha(P/n) for n in ['capture.py','analyze.py','select_complete_families.py','plan.json']};pins.update(plan['input_sha256']);pins.update(plan['runtime_sha256']);commands=[];receipts={};options={}
 freeze=load(plan['candidate_source_freeze']['path']);assert sha(plan['candidate_source_freeze']['path'])==plan['candidate_source_freeze']['sha256']
 assert freeze['source74_graph']==plan['candidate_source_graph_sha256'] and freeze['changed_files']==['src/quiescence.rs']
 for side in ['control','candidate']:
  build=Path(plan[side+'_build']);image=build/'rook2-exact';r=load(build/'receipt.json');receipts[side]=r
  assert sha(image)==plan[side+'_image_sha256']==r['binary_output']['sha256'] and image.stat().st_mode&0o777==0o555
  assert r['mode']=='generic' and r['pgo']['mode']=='profile-use' and r['target_cpu']=='x86-64'
  assert r['outcome']=='build-succeeded-with-stable-input-snapshot' and r['cargo_exit_code']==0
  assert r['source_sha256_before']==r['source_sha256_after'] and r['tool_sha256_before']==r['tool_sha256_after']
  assert r['source_identity_unchanged'] and r['tool_identity_unchanged'] and r['cargo_config_unchanged']
  assert r['build_effective_environment']['RUSTFLAGS']==' '.join(r['rust_flags']) and r['build_effective_environment']['CARGO_ENCODED_RUSTFLAGS']=='\x1f'.join(r['rust_flags'])
  assert r['pgo']['inputs_unchanged'] and r['pgo']['input_sha256_before']==r['pgo']['input_sha256_after']
  assert r['pgo']['input_sha256_before'][r['pgo']['profile']]==plan[side+'_profile_sha256']
  t=load(r['pgo']['training_record']);assert t['complete'] and t['engine_source_sha256']==r['source_sha256_before'] and t['profile_sha256']==plan[side+'_profile_sha256']
  for x,h in r['pgo']['input_sha256_before'].items():assert sha(x)==h;pins[x]=h
  for x in [image,build/'receipt.json',build/'frozen-image.json']:pins[str(x)]=sha(x)
  for n,h in (r['source_sha256_before']|r['tool_sha256_before']).items():
   x=build/'source-before'/n;assert sha(x)==h;pins[str(x)]=h
  profile=r['pgo']['profile'];assert r['rust_flags']==['-C','target-cpu=x86-64','-C','profile-use='+profile,'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false']
  options[side]=effective_options(build)
  for opt in options[side].values():assert opt['profile-use']==profile and 'profile-generate' not in opt
  warnings=read(build/'build.stderr').decode().lower()
  for bad in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data','hash mismatch','unprofiled function']:assert bad not in warnings,bad
  for stem,argv in [('nm',['/usr/bin/nm','-n','-S','--defined-only','--demangle',str(image)]),('nm-mangled',['/usr/bin/nm','-n','-S','--defined-only',str(image)]),('sections',['/usr/bin/readelf','-SW',str(image)]),('relocations',['/usr/bin/readelf','-rW',str(image)]),('size',['/usr/bin/size','-A',str(image)])]:commands.append(run(argv,side+'-'+stem))
 for exe in ['/usr/bin/nm','/usr/bin/objdump','/usr/bin/readelf','/usr/bin/size']:
  assert exe in plan['runtime_sha256'];commands.append(run([exe,'--version'],Path(exe).name+'-version'))
 a,b=receipts['control'],receipts['candidate']
 for k in ['toolchain','mode','target_triple','target_cpu','jobs','cargo_config_sha256_before']:assert a[k]==b[k],k
 assert a['tool_sha256_before']==b['tool_sha256_before'] and len(b['tool_sha256_before'])==23
 assert set(a['source_sha256_before'])==set(b['source_sha256_before']) and len(b['source_sha256_before'])==51
 changed=sorted(n for n in a['source_sha256_before'] if a['source_sha256_before'][n]!=b['source_sha256_before'][n]);assert changed==['src/quiescence.rs']
 assert b['source_sha256_before']|b['tool_sha256_before']==freeze['files_sha256']
 for side,r in receipts.items():
  assert r['rust_flags'][3]=='profile-use='+r['pgo']['profile']
 # Only the EXACT per-side profile path is normalized in use flags/environment.
 def norm_flags(r):return [x if x!='profile-use='+r['pgo']['profile'] else 'profile-use=<OWN_PROFILE>' for x in r['rust_flags']]
 assert norm_flags(a)==norm_flags(b)
 for k in set(a['build_effective_environment'])|set(b['build_effective_environment']):
  av=a['build_effective_environment'].get(k);bv=b['build_effective_environment'].get(k)
  if k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS']:
   av=av.replace('profile-use='+a['pgo']['profile'],'profile-use=<OWN_PROFILE>');bv=bv.replace('profile-use='+b['pgo']['profile'],'profile-use=<OWN_PROFILE>')
  assert av==bv,k
 instr=load(plan['candidate_instrumented_receipt']);training=load(plan['candidate_training_record']);v=load(plan['candidate_verification'])
 assert instr['source_sha256_before']==instr['source_sha256_after']==b['source_sha256_before']==training['engine_source_sha256']
 assert instr['tool_sha256_before']==instr['tool_sha256_after']==b['tool_sha256_before'] and instr['toolchain']==b['toolchain']
 assert instr['pgo']['mode']=='instrumented' and not any('llvm-args=' in x or 'profile-use=' in x for x in instr['rust_flags'])
 assert v['complete'] and v['independent_remerge_byte_identical'] and v['original_checkReplay_count']==v['raw_training_protocol_cases']==v['raw_profiles_independently_hashed']==54
 assert v['merged_profile_sha256']==v['independent_profile_sha256']==training['profile_sha256']==plan['candidate_profile_sha256']
 assert len(training['raw_profiles_sha256'])==54
 assert training['instrumented_build_receipt']['path']==plan['candidate_instrumented_receipt'] and training['instrumented_build_receipt']['sha256']==sha(plan['candidate_instrumented_receipt'])
 assert training['instrumented_engine_sha256']==instr['binary_output']['sha256']
 assert v['training_record_sha256']==sha(plan['candidate_training_record'])
 assert all(sha(x)==h for x,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,changed_existing_files=changed,added_files=[],compiler_settings_equal_except_declared_own_profile_path=True,effective_options=options,candidate_source_counts=dict(native=51,tools=23,total=74)))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),changed=changed)))

def symbols(side):
 result=[]
 for line in read(P/(side+'-nm-mangled.stdout')).decode().splitlines():
  f=line.split(maxsplit=3)
  if len(f)==4 and f[2] in ['t','T']:result.append((int(f[0],16),int(f[1],16),f[3]))
 return result

def select_bodies():
 plan=setup('select');request=[]
 from select_complete_families import select_complete_families
 selection=load(P/'role-selection.json')
 assert selection['parent_confirmed'] is True and selection['discovery_sha256']==sha(P/'discovery.json')
 assert selection['normal_consumed_Q_role_evidence'] and selection['alternate_Q_and_ordinary_scope_review']
 for side in ['control','candidate']:
  syms=symbols(side);dem=[]
  for line in read(P/(side+'-nm.stdout')).decode().splitlines():
   f=line.split(maxsplit=3)
   if len(f)==4 and f[2] in ['t','T']:dem.append((int(f[0],16),int(f[1],16),f[3]))
  roles=selection['roles'][side]
  assert 1<=len(roles)<=3 and any(x['role']=='q_primary' for x in roles)
  assert len({x['role'] for x in roles})==len(roles)
  for role in roles:
   assert role['role'] in ['q_primary','q_alternate','ordinary']
   assert role['actual_mangled_symbol'] and role['source_and_call_role_evidence']
   assert isinstance(role['expected_start'],str) and int(role['expected_start'],16)>=0 and role['expected_bytes']>0
   expected='src/ordinary.rs' if role['role']=='ordinary' else 'src/quiescence.rs'
   assert role['source']==expected
   marker='visit_ordinary_impl' if role['role']=='ordinary' else 'visit_q_impl'
   assert marker in role['display_name']
  rows=select_complete_families(syms,dem,roles,side)
  for j,row in enumerate(rows):
   row['start']=hex(row['start']);row['label']=row['role']+'-'+str(j);row['complete_body']=True
  request+=rows
 assert 2<=len(request)<=6,'more than6 complete actual Q/ordinary/cold bodies: STOP BEFORE BODY CAPTURE'
 assert {x['side'] for x in request if x['role']=='q_primary'}=={'control','candidate'}
 save(P/'body-request.json',request)
 save(P/'body-selection-proof.json',dict(role_selection_sha256=sha(P/'role-selection.json'),discovery_sha256=sha(P/'discovery.json'),body_request_sha256=sha(P/'body-request.json')))
 return request

def bodies():
 plan=setup('bodies');d=load(P/'discovery.json');assert all(sha(x)==h for x,h in d['pins'].items())
 request=load(P/'body-request.json');assert 2<=len(request)<=6
 selection=load(P/'body-selection-proof.json')
 assert selection['role_selection_sha256']==sha(P/'role-selection.json') and selection['discovery_sha256']==sha(P/'discovery.json') and selection['body_request_sha256']==sha(P/'body-request.json')
 assert len({(x['side'],x['label']) for x in request})==len(request)
 for side in ['control','candidate']:
  syms=symbols(side)
  for role in {x['role'] for x in request if x['side']==side}:
   rows=[x for x in request if x['side']==side and x['role']==role];hot=[x for x in rows if x['fragment_kind']=='hot'];assert len(hot)==1
   stem=hot[0]['owner_mangled_symbol'];family=[x for x in syms if x[2]==stem or re.fullmatch(re.escape(stem)+r'\.cold(?:\.[0-9]+)?',x[2])]
   assert {(int(x['start'],16),x['bytes'],x['actual_mangled_symbol']) for x in rows}==set(family)
 rows=[]
 for x in request:
  start=int(x['start'],16);extent=x['bytes'];assert extent>0
  image=Path(plan[x['side']+'_build'])/'rook2-exact'
  result=run(['/usr/bin/objdump','-d','-l','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+extent),str(image)],x['side']+'-'+x['label'])
  rows.append(dict(**x,command=result,raw_bytes=result['stdout_bytes']))
 assert all(sha(x)==h for x,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=captured_text_bytes(),all_discovery_inputs_unchanged=True,body_request_sha256=sha(P/'body-request.json'),raw_complete_before_feature_analysis=True))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=captured_text_bytes())))

def gate():
 raise AssertionError('Manual actual role-selection required between discover/select; use staged commands within one original180s clock')
def analyze():
 setup('analyze');run(['/usr/bin/python3',str(P/'analyze.py')],'analysis')
if __name__=='__main__':{'discover':discover,'select':select_bodies,'bodies':bodies,'analyze':analyze,'gate':gate}[sys.argv[1]]()
