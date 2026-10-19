#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys
P=Path(__file__).resolve().parent;E=P.parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
SIDES={'control':('influence-bitsliced-sum','ea057f6a4a0c57ddc3ed35667d01363c7f2fc68d2de1d2fa745d2ba16f6e4a23'), 'candidate':('influence-direct-fill','470d7eac0b8522fc518e1fd8590b2565a418eb519dbecace8e3021f39bf17e8c')}
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

def discover():
 assert os.sched_getaffinity(0)==H
 pins={};receipts={};commands=[]
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
 changed=sorted(n for n in a['source_sha256_before'] if a['source_sha256_before'][n]!=b['source_sha256_before'][n]);assert changed==['src/influence.rs','src/influence/coherent.rs']
 for p in [E/'influence-direct-fill-parent-selection-20261019-01/decision.json',E/'influence-direct-fill-parent-review-20261019-01/source-freeze.json',E/'influence-direct-fill-generic-build-execution-20261019-01/tool-terminal.json',E/'influence-direct-fill-generic-build-execution-20261019-01/result.json']:
  pins[str(p)]=sha(p)
 terminal=load(E/'influence-direct-fill-generic-build-execution-20261019-01/tool-terminal.json');assert terminal['actual_tool_terminal_observed'] and terminal['exit_code']==0 and terminal['terminal_chunk_id']=='621ff9'
 assert all(sha(p)==h for p,h in pins.items())
 save(P/'discovery.json',dict(complete=True,pins=pins,commands=commands,compiler_settings_equal=True,only_two_source_files_changed=changed,source_files=72,native49_tools23=True))
 print(json.dumps(dict(complete=True,commands=len(commands),pins=len(pins),only_changed=changed)))

def bodies():
 assert os.sched_getaffinity(0)==H
 d=load(P/'discovery.json');assert all(sha(p)==h for p,h in d['pins'].items())
 request=load(P/'body-request.json');assert len(request)<=12
 total=0;rows=[]
 for row in request:
  side=row['side'];name,_=SIDES[side];image=E/(name+'-generic-build-20261019-01')/'rook2-exact'
  start=int(row['start'],16);size=int(row['bytes']);assert size>0
  stem=side+'-'+row['label']
  result=run(['/usr/bin/objdump','-d','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)],stem)
  total+=(P/(stem+'.stdout')).stat().st_size;assert total<=1048576,total
  rows.append(dict(**row,command=result,raw_bytes=(P/(stem+'.stdout')).stat().st_size))
 assert all(sha(p)==h for p,h in d['pins'].items())
 save(P/'bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=total,all_discovery_inputs_unchanged=True))
 print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=total)))
if __name__=='__main__':
 {'discover':discover,'bodies':bodies}[sys.argv[1]]()
