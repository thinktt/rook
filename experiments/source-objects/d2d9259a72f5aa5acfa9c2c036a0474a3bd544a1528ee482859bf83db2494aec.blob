#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,resource
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
 assert plan['max_complete_bodies']==12 and plan['max_new_raw_disassembly_bytes']==4194304 and plan['per_read_or_command_wall_s']==30 and plan['total_elapsed_wall_s']==180
 if stage=='discover':
  DEADLINE=ENTERED+180
  save(P/'capture-clock.json',dict(started_monotonic=ENTERED,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),deadline=DEADLINE))
 else:
  c=json.loads((P/'capture-clock.json').read_text());DEADLINE=c['deadline']
  assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==c['boot_id'] and DEADLINE==c['started_monotonic']+180
 check()
 assert plan['allowed_body_labels']==['ordinary0','ordinary1','q0','q1','preferred','priority','order0','order1']
 assert plan['candidate_image_sha256'] and plan['candidate_receipt_sha256'] and plan['candidate_build_terminal'] and plan['candidate_source_graph_sha256']
 assert plan['expected_source_counts'] and plan['expected_added_native_files'] is not None and plan['candidate_source_freeze']['sha256'] and plan['runtime_sha256']
 assert all(sha(p)==h for p,h in plan['input_sha256'].items())
 assert all(sha(p)==h for p,h in plan['runtime_sha256'].items())
 terminal=plan['candidate_build_terminal'];assert sha(terminal['path'])==terminal['sha256']
 t=load(terminal['path']);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['terminal_chunk_id']
 return plan

def run(argv,stem,raw_cap=1048576):
 check();assert 0<raw_cap<=4194304
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
 assert failure is None and code==0 and elapsed<=30 and row['stderr_bytes']==0,row
 check();row.update(stdout_sha256=sha(P/(stem+'.stdout')),stderr_sha256=sha(P/(stem+'.stderr')))
 # Hash record is separate so the observed terminal record is never overwritten.
 save(P/(stem+'-output-pins.json'),{k:row[k] for k in ['stdout_sha256','stderr_sha256']})
 return row

def discover():
 plan=setup('discover');pins={str(P/n):sha(P/n) for n in ['capture.py','analyze.py','plan.json']};pins.update(plan['input_sha256']);pins.update(plan['runtime_sha256']);commands=[];receipts={}
 freeze=load(plan['candidate_source_freeze']['path']);assert sha(plan['candidate_source_freeze']['path'])==plan['candidate_source_freeze']['sha256']
 assert freeze['source_preparation_accepted'] is True and freeze['source_graph_sha256']==plan['candidate_source_graph_sha256']
 pins[plan['candidate_source_freeze']['path']]=plan['candidate_source_freeze']['sha256'];pins[plan['candidate_build_terminal']['path']]=plan['candidate_build_terminal']['sha256']
 for side in ['control','candidate']:
  build=Path(plan[side+'_build']);image=build/'rook2-exact';r=load(build/'receipt.json');receipts[side]=r
  assert sha(image)==plan[side+'_image_sha256']==r['binary_output']['sha256']
  if side=='candidate':assert sha(build/'receipt.json')==plan['candidate_receipt_sha256']
  assert image.stat().st_mode&0o777==0o555
  assert r['mode']=='generic' and r['pgo']['mode']=='none' and r['target_cpu']=='x86-64'
  assert r['source_sha256_before']==r['source_sha256_after'] and r['tool_sha256_before']==r['tool_sha256_after']
  assert r['source_identity_unchanged'] and r['tool_identity_unchanged'] and r['cargo_config_unchanged']
  for p in [image,build/'receipt.json',build/'frozen-image.json']:pins[str(p)]=sha(p)
  for n,h in (r['source_sha256_before']|r['tool_sha256_before']).items():
   p=build/'source-before'/n;assert sha(p)==h;pins[str(p)]=h
  for stem,argv in [('nm',['/usr/bin/nm','-n','-S','--defined-only','--demangle',str(image)]),('nm-mangled',['/usr/bin/nm','-n','-S','--defined-only',str(image)]),('sections',['/usr/bin/readelf','-SW',str(image)]),('relocations',['/usr/bin/readelf','-rW',str(image)]),('size',['/usr/bin/size','-A',str(image)])]:commands.append(run(argv,side+'-'+stem))
 for exe in ['/usr/bin/nm','/usr/bin/objdump','/usr/bin/readelf','/usr/bin/size']:
  assert exe in plan['runtime_sha256'];pins[exe]=sha(exe);commands.append(run([exe,'--version'],Path(exe).name+'-version'))
 a,b=receipts.values()
 for key in ['toolchain','mode','target_triple','target_cpu','jobs','rust_flags','build_effective_environment','cargo_config_sha256_before']:assert a[key]==b[key],key
 assert a['tool_sha256_before']==b['tool_sha256_before'] and len(b['tool_sha256_before'])==23
 changed=sorted(n for n in a['source_sha256_before'] if a['source_sha256_before'][n]!=b['source_sha256_before'].get(n));assert changed==['src/tactical.rs']
 assert not (set(a['source_sha256_before'])-set(b['source_sha256_before']))
 added=sorted(set(b['source_sha256_before'])-set(a['source_sha256_before']));assert added==plan['expected_added_native_files']
 assert b['source_sha256_before']|b['tool_sha256_before']==freeze['files_sha256']
 counts=dict(native=len(b['source_sha256_before']),tools=len(b['tool_sha256_before']),total=len(b['source_sha256_before'])+len(b['tool_sha256_before']));assert counts==plan['expected_source_counts']
 assert len(a['source_sha256_before'])==51 and len(a['tool_sha256_before'])==23
 assert all(sha(p)==h for p,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,compiler_settings_equal=True,changed_existing_files=changed,added_files=added,candidate_source_counts=counts))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),changed=changed,added=added)))

def bodies():
 plan=setup('bodies');d=load(P/'discovery.json');assert all(sha(p)==h for p,h in d['pins'].items())
 request=load(P/'body-request.json');assert 4<=len(request)<=12
 roles={(r['side'],r['label']) for r in request}
 assert any(all((side,label) in roles for side in ['control','candidate']) for label in ['ordinary0','ordinary1'])
 assert any(all((side,label) in roles for side in ['control','candidate']) for label in ['q0','q1'])
 assert len({(r['side'],r['label']) for r in request})==len(request)
 total=0;rows=[]
 for row in request:
  assert row['side'] in ['control','candidate'] and row['label'] in ['ordinary0','ordinary1','q0','q1','preferred','priority','order0','order1'] and row['complete_body'] is True and row['source_role']
  side=row['side'];image=Path(plan[side+'_build'])/'rook2-exact';start=int(row['start'],16);size=int(row['bytes']);assert size>0
  selected=[]
  for line in read(P/(side+'-nm.stdout')).decode().splitlines():
   fields=line.split(maxsplit=3)
   if len(fields)==4 and fields[2] in ['t','T'] and int(fields[0],16)==start and int(fields[1],16)==size:selected.append(fields[3])
  assert row['actual_symbol'] in selected
  mangled=[]
  for line in read(P/(side+'-nm-mangled.stdout')).decode().splitlines():
   fields=line.split(maxsplit=3)
   if len(fields)==4 and fields[2] in ['t','T'] and int(fields[0],16)==start and int(fields[1],16)==size:mangled.append(fields[3])
  assert row['actual_mangled_symbol'] in mangled
  result=run(['/usr/bin/objdump','-d','-l','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)],side+'-'+row['label'],4194304-total)
  total+=result['stdout_bytes'];assert total<=4194304
  rows.append(dict(**row,command=result,raw_bytes=result['stdout_bytes']))
 assert all(sha(p)==h for p,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=total,all_discovery_inputs_unchanged=True))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=total)))
if __name__=='__main__':{'discover':discover,'bodies':bodies}[sys.argv[1]]()
