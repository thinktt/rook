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
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n')
def setup(stage):
 global DEADLINE
 # Read only the local small activation plan before the timed, pinned read API.
 start=time.monotonic();plan=json.loads((P/'plan.json').read_text());assert time.monotonic()-start<30
 assert plan['launch'] is True and plan['parent_backend_activation'] is True
 assert os.sched_getaffinity(0)==H and os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
 assert plan['max_complete_bodies']==12 and plan['max_control_complete_bodies']==3 and plan['max_candidate_complete_bodies']==9 and plan['max_total_captured_text_bytes']==3145728 and plan['per_read_or_command_wall_s']==30 and plan['total_elapsed_wall_s']==180
 if stage=='discover':
  DEADLINE=ENTERED+180
  save(P/'capture-clock.json',dict(started_monotonic=ENTERED,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),deadline=DEADLINE))
 else:
  c=json.loads((P/'capture-clock.json').read_text());DEADLINE=c['deadline']
  assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==c['boot_id'] and DEADLINE==c['started_monotonic']+180
 check()
 assert plan['candidate_image_sha256'] and plan['candidate_receipt_sha256'] and plan['candidate_build_terminal'] and plan['candidate_source_graph_sha256']
 assert plan['expected_source_counts'] and plan['candidate_source_freeze']['sha256'] and plan['runtime_sha256']
 assert plan['parent_build_acceptance'] and plan['parent_build_acceptance']['sha256']
 acceptance=load(plan['parent_build_acceptance']['path']);assert sha(plan['parent_build_acceptance']['path'])==plan['parent_build_acceptance']['sha256']
 assert all(acceptance[k]==v for k,v in plan['parent_acceptance_checks'].items())
 assert plan['quiet_clearance'] and sha(plan['quiet_clearance']['path'])==plan['quiet_clearance']['sha256']
 assert all(sha(p)==h for p,h in plan['input_sha256'].items())
 assert all(sha(p)==h for p,h in plan['runtime_sha256'].items())
 terminal=plan['candidate_build_terminal'];assert sha(terminal['path'])==terminal['sha256']
 t=load(terminal['path']);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['terminal_chunk_id']
 return plan

def captured_text_bytes():
 return sum(q.stat().st_size for suffix in ['*.stdout','*.stderr'] for q in P.glob(suffix))
def run(argv,stem):
 check();raw_cap=3145728-captured_text_bytes();assert raw_cap>0
 started=time.monotonic();failure=None
 def cap():resource.setrlimit(resource.RLIMIT_FSIZE,(raw_cap,raw_cap))
 with (P/(stem+'.stdout')).open('xb') as out,(P/(stem+'.stderr')).open('xb') as err:
  child=subprocess.Popen(argv,stdout=out,stderr=err,preexec_fn=cap)
  try:code=child.wait(timeout=min(30,max(0.001,DEADLINE-time.monotonic())))
  except subprocess.TimeoutExpired:
   child.kill();code=child.wait();failure='command/aggregate deadline exceeded; stopped and reaped'
 elapsed=time.monotonic()-started
 # Preserve actual command/exit even when the deadline or output cap failed.
 row=dict(argv=argv,pid=child.pid,actual_child_return_observed=True,exit_code=code,elapsed_wall_s=elapsed,failure=failure,stdout_bytes=(P/(stem+'.stdout')).stat().st_size,stderr_bytes=(P/(stem+'.stderr')).stat().st_size)
 with (P/(stem+'-command.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 assert captured_text_bytes()<=3145728,'aggregate raw text cap exceeded; stop and preserve failure'
 assert failure is None and code==0 and elapsed<=30 and row['stderr_bytes']==0,row
 check();row.update(stdout_sha256=sha(P/(stem+'.stdout')),stderr_sha256=sha(P/(stem+'.stderr')))
 # Hash record is separate so the observed terminal record is never overwritten.
 save(P/(stem+'-output-pins.json'),{k:row[k] for k in ['stdout_sha256','stderr_sha256']})
 return row

def discover():
 plan=setup('discover');pins={str(P/n):sha(P/n) for n in ['capture.py','analyze.py','plan.json']};pins.update(plan['input_sha256']);pins.update(plan['runtime_sha256']);commands=[];receipts={}
 freeze=load(plan['candidate_source_freeze']['path']);assert sha(plan['candidate_source_freeze']['path'])==plan['candidate_source_freeze']['sha256']
 assert freeze['changed_existing_files']==['tools/build.py'] and freeze['source_graph_sha256']==plan['candidate_source_graph_sha256']
 pins[plan['candidate_source_freeze']['path']]=plan['candidate_source_freeze']['sha256'];pins[plan['candidate_build_terminal']['path']]=plan['candidate_build_terminal']['sha256'];pins[plan['parent_build_acceptance']['path']]=plan['parent_build_acceptance']['sha256']
 for side in ['control','candidate']:
  build=Path(plan[side+'_build']);image=build/'rook2-exact';r=load(build/'receipt.json');receipts[side]=r
  assert sha(image)==plan[side+'_image_sha256']==r['binary_output']['sha256']
  if side=='candidate':assert sha(build/'receipt.json')==plan['candidate_receipt_sha256']
  assert image.stat().st_mode&0o777==0o555
  assert r['mode']=='generic' and r['pgo']['mode']=='profile-use' and r['target_cpu']=='x86-64'
  assert r['source_sha256_before']==r['source_sha256_after'] and r['tool_sha256_before']==r['tool_sha256_after']
  assert r['source_identity_unchanged'] and r['tool_identity_unchanged'] and r['cargo_config_unchanged']
  assert r['build_effective_environment']['RUSTFLAGS']==' '.join(r['rust_flags'])
  assert r['build_effective_environment']['CARGO_ENCODED_RUSTFLAGS']=='\x1f'.join(r['rust_flags'])
  assert r['pgo']['inputs_unchanged'] and r['pgo']['input_sha256_before']==r['pgo']['input_sha256_after']
  assert r['pgo']['input_sha256_before'][r['pgo']['profile']]==plan['profile_sha256']
  for path,h in r['pgo']['input_sha256_before'].items():assert sha(path)==h;pins[path]=h
  for p in [image,build/'receipt.json',build/'frozen-image.json']:pins[str(p)]=sha(p)
  for n,h in (r['source_sha256_before']|r['tool_sha256_before']).items():
   p=build/'source-before'/n;assert sha(p)==h;pins[str(p)]=h
  for stem,argv in [('nm',['/usr/bin/nm','-n','-S','--defined-only','--demangle',str(image)]),('nm-mangled',['/usr/bin/nm','-n','-S','--defined-only',str(image)]),('sections',['/usr/bin/readelf','-SW',str(image)]),('relocations',['/usr/bin/readelf','-rW',str(image)]),('size',['/usr/bin/size','-A',str(image)])]:commands.append(run(argv,side+'-'+stem))
 for exe in ['/usr/bin/nm','/usr/bin/objdump','/usr/bin/readelf','/usr/bin/size']:
  assert exe in plan['runtime_sha256'];pins[exe]=sha(exe);commands.append(run([exe,'--version'],Path(exe).name+'-version'))
 a,b=receipts.values()
 for key in ['toolchain','mode','target_triple','target_cpu','jobs','cargo_config_sha256_before']:assert a[key]==b[key],key
 assert a['source_sha256_before']==b['source_sha256_before'] and len(b['source_sha256_before'])==51
 assert len(a['tool_sha256_before'])==len(b['tool_sha256_before'])==23
 changed_tools=sorted(n for n in a['tool_sha256_before'] if a['tool_sha256_before'][n]!=b['tool_sha256_before'].get(n));assert changed_tools==['tools/build.py']
 assert set(a['tool_sha256_before'])==set(b['tool_sha256_before'])
 expected_flags=list(a['rust_flags']);indices=[i for i,v in enumerate(expected_flags) if v.startswith('llvm-args=')];assert len(indices)==1
 assert '-enable-ext-tsp-block-placement=true' in expected_flags[indices[0]] and '-ext-tsp-apply-without-profile=false' in expected_flags[indices[0]]
 assert '-enable-split-machine-functions' not in expected_flags[indices[0]]
 expected_flags[indices[0]]+=' -enable-split-machine-functions=true'
 assert b['rust_flags']==expected_flags
 for key,value in a['build_effective_environment'].items():
  if key not in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS']:assert b['build_effective_environment'][key]==value,key
 changed=[];added=[]
 assert b['source_sha256_before']|b['tool_sha256_before']==freeze['source_sha256']|freeze['tool_source_sha256']
 counts=dict(native=len(b['source_sha256_before']),tools=len(b['tool_sha256_before']),total=len(b['source_sha256_before'])+len(b['tool_sha256_before']));assert counts==plan['expected_source_counts']
 assert len(a['source_sha256_before'])==51 and len(a['tool_sha256_before'])==23
 assert all(sha(p)==h for p,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,compiler_settings_equal=True,changed_existing_files=changed,changed_tools=changed_tools,added_files=added,candidate_source_counts=counts))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),changed=changed,added=added)))

def symbols(side):
 result=[]
 for line in read(P/(side+'-nm-mangled.stdout')).decode().splitlines():
  f=line.split(maxsplit=3)
  if len(f)==4 and f[2] in ['t','T']:result.append((int(f[0],16),int(f[1],16),f[3]))
 return result

def bodies():
 plan=setup('bodies');d=load(P/'discovery.json');assert all(sha(p)==h for p,h in d['pins'].items())
 request=load(P/'body-request.json');assert 6<=len(request)<=12
 assert len({(r['side'],r['label']) for r in request})==len(request)
 assert sum(r['side']=='control' for r in request)==3 and 3<=sum(r['side']=='candidate' for r in request)<=9
 for side in ['control','candidate']:
  syms=symbols(side)
  for role in ['ordinary','activity','q']:
   rs=[r for r in request if r['side']==side and r['role']==role];hot=[r for r in rs if r['fragment_kind']=='hot'];assert len(hot)==1
   stem=hot[0]['actual_mangled_symbol'];assert all(r['owner_mangled_symbol']==stem for r in rs)
   family=[x for x in syms if x[2]==stem or re.fullmatch(re.escape(stem)+r'\.cold(?:\.\d+)?',x[2])]
   assert not [x for x in syms if x[2].startswith(stem+'.') and x not in family],'unrecognized owner suffix'
   assert all(x[1]>0 for x in family),'unsized fragment'
   assert {(int(r['start'],16),r['bytes'],r['actual_mangled_symbol']) for r in rs}==set(family),'incomplete fragment coverage'
   assert all(r['source_role_evidence'] and r['mapping_evidence'] for r in rs)
 intervals=sorted((r['side'],int(r['start'],16),r['bytes']) for r in request)
 assert all(side!=side2 or start+size<=start2 for (side,start,size),(side2,start2,size2) in zip(intervals,intervals[1:])),'overlapping captures'
 rows=[]
 for r in request:
  assert r['side'] in ['control','candidate'] and r['role'] in ['ordinary','activity','q'] and r['fragment_kind'] in ['hot','cold'] and r['complete_body'] is True
  assert re.fullmatch(r'(ordinary|activity|q)-(hot|cold[0-9]+)',r['label'])
  side=r['side'];start=int(r['start'],16);size=r['bytes'];assert size>0
  matching=[]
  for line in read(P/(side+'-nm.stdout')).decode().splitlines():
   f=line.split(maxsplit=3)
   if len(f)==4 and f[2] in ['t','T'] and int(f[0],16)==start and int(f[1],16)==size:matching.append(f[3])
  assert r['actual_symbol'] in matching
  image=Path(plan[side+'_build'])/'rook2-exact'
  result=run(['/usr/bin/objdump','-d','-l','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)],side+'-'+r['label'])
  rows.append(dict(**r,command=result,raw_bytes=result['stdout_bytes']))
 assert all(sha(p)==h for p,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=captured_text_bytes(),all_discovery_inputs_unchanged=True,body_request_sha256=sha(P/'body-request.json')))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=captured_text_bytes())))
def select_bodies():
 plan=setup('select');request=[]
 for side in ['control','candidate']:
  syms=symbols(side);demangled=[]
  for line in read(P/(side+'-nm.stdout')).decode().splitlines():
   f=line.split(maxsplit=3)
   if len(f)==4 and f[2] in ['t','T']:demangled.append((int(f[0],16),int(f[1],16),f[3]))
  for role,known in plan['control_owner_symbols'].items():
   # Exact closed namespace/name, not suffix stripping or first regex hit.
   hot=[x for x in demangled if x[2]==known['actual_symbol']];assert len(hot)==1,'missing/ambiguous exact normal owner'
   start,size,name=hot[0]
   if side=='control':assert start==int(known['start'],16) and size==known['bytes']
   mangled=[x for x in syms if x[:2]==(start,size)];assert len(mangled)==1,'symbol aliases make owner ambiguous'
   stem=mangled[0][2]
   if side=='control':assert stem==known['actual_mangled_symbol']
   family=[x for x in syms if x[2]==stem or re.fullmatch(re.escape(stem)+r'\.cold(?:\.\d+)?',x[2])]
   assert not [x for x in syms if x[2].startswith(stem+'.') and x not in family],'unrecognized owner suffix'
   for index,(address,extent,symbol) in enumerate(sorted(family,key=lambda x:(x[2]!=stem,x[0]))):
    assert extent>0,'unsized fragment'
    names=[x[2] for x in demangled if x[:2]==(address,extent)];assert len(names)==1
    kind='hot' if symbol==stem else 'cold';label=role+'-'+('hot' if kind=='hot' else 'cold'+str(index))
    request.append(dict(side=side,label=label,role=role,fragment_kind=kind,start=hex(address),bytes=extent,actual_symbol=names[0],actual_mangled_symbol=symbol,owner_mangled_symbol=stem,complete_body=True,source_role_evidence=known['source_role'],mapping_evidence='Unique exact closed normal namespace/name + sized hot symbol; cold suffix shares exact mangled stem. Native source is byte-equal. Source/call-role manual confirmation remains mandatory.'))
 assert len(request)<=12 and sum(r['side']=='control' for r in request)==3 and sum(r['side']=='candidate' for r in request)<=9
 save(P/'body-request.json',request)
 return request

def gate():
 discover();select_bodies();bodies()
 run(['/usr/bin/python3',str(P/'analyze.py')],'analysis')
if __name__=='__main__':{'discover':discover,'select':select_bodies,'bodies':bodies,'gate':gate}[sys.argv[1]]()
