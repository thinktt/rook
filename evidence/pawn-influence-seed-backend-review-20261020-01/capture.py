#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,re,stat
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
plan=json.loads((HERE/'plan.active.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,v):
 with (HERE/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def stable():
 for p,h in json.loads((HERE/'runtime-input-pins.json').read_text()).items():assert sha(p)==h,p
def command(label,argv):
 before=time.monotonic()
 with (HERE/(label+'.stdout')).open('xb') as out,(HERE/(label+'.stderr')).open('xb') as err:
  done=subprocess.run(argv,stdout=out,stderr=err,timeout=30,check=False)
 write(label+'-command.json',dict(argv=argv,exit_code=done.returncode,elapsed_seconds=time.monotonic()-before,affinity=sorted(os.sched_getaffinity(0)),stdout_sha256=sha(HERE/(label+'.stdout')),stderr_sha256=sha(HERE/(label+'.stderr'))))
 assert done.returncode==0,(label,done.returncode)
def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 assert plan['execution_authorized'] is True
 images={s:Path(plan[s]['image_path']) for s in ['control','candidate']}
 if sys.argv[1]=='discover':
  pins={str(HERE/'capture.py'):sha(HERE/'capture.py'),str(HERE/'plan.active.json'):sha(HERE/'plan.active.json')}
  receipts={}
  for side,image in images.items():
   expected=plan[side].get('image_sha256') or plan[side]['expected_image_sha256']
   assert sha(image)==expected and stat.S_IMODE(image.stat().st_mode)==0o555
   pins[str(image)]=expected
   receipt=json.loads((image.parent/'receipt.json').read_text());receipts[side]=receipt
   assert receipt['cargo_exit_code']==0 and receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged']
   assert receipt['source_sha256_before']==receipt['source_sha256_after']
   assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
   for field in ['source_sha256_before','tool_sha256_before']:
    for name,h in receipt[field].items():
     frozen=image.parent/'source-before'/name
     assert sha(frozen)==h,frozen
     pins[str(frozen)]=h
   for name in ['receipt.json','frozen-image.json','archive-receipt.json','build.stderr']:
    file=image.parent/name;pins[str(file)]=sha(file)
  for key in ['mode','target_triple','target_cpu','jobs','environment_overrides','build_effective_environment','toolchain','rust_flags','pgo']:
   assert receipts['control'][key]==receipts['candidate'][key],key
  assert receipts['control']['tool_sha256_before']==receipts['candidate']['tool_sha256_before']
  a=receipts['control']['source_sha256_before'];b=receipts['candidate']['source_sha256_before']
  assert set(a)==set(b) and sorted(k for k in a if a[k]!=b[k])==['src/attacks.rs','src/influence/coherent.rs','src/influence/coherent_tests.rs']
  freeze=ROOT/'pawn-influence-seed-parent-review-20261020-01/source-freeze.json';assert sha(freeze)==plan['candidate']['source_freeze_sha256'];pins[str(freeze)]=sha(freeze)
  for tool in ['nm','objdump','readelf','size']:pins[str(Path('/usr/bin')/tool)]=sha(Path('/usr/bin')/tool)
  write('runtime-input-pins.json',pins)
  for tool in ['nm','objdump','readelf','size']:command(tool+'-version',['/usr/bin/'+tool,'--version'])
  for side,image in images.items():
   command(side+'-nm',['/usr/bin/nm','-n','-S','--defined-only','--demangle',str(image)])
   command(side+'-nm-mangled',['/usr/bin/nm','-n','-S','--defined-only',str(image)])
   command(side+'-sections',['/usr/bin/readelf','-SW',str(image)])
   command(side+'-relocations',['/usr/bin/readelf','-rW',str(image)])
   command(side+'-size',['/usr/bin/size','-A',str(image)])
  stable();write('discovery.json',dict(complete=True,settings_equal=True,source_delta_exact=True,inputs_unchanged=True,pins=len(pins)))
 elif sys.argv[1]=='bodies':
  stable();request=json.loads((HERE/'body-request.json').read_text());assert len(request)<=4
  total=0
  for row in request:
   image=images[row['side']];start=int(row['start'],16);size=int(row['bytes']);assert size>0
   names=(HERE/(row['side']+'-nm.stdout')).read_text().splitlines();assert any(line.startswith(f'{start:016x} {size:016x} ') and row['owner'] in line for line in names)
   label=row['side']+'-'+row['role']
   command(label,['/usr/bin/objdump','-d','-l','-C','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)])
   total+=(HERE/(label+'.stdout')).stat().st_size;assert total<=1048576
  stable();write('capture.json',dict(complete=True,bodies=len(request),raw_disassembly_bytes=total,inputs_unchanged=True,request_sha256=sha(HERE/'body-request.json')))
 else:raise AssertionError(sys.argv[1])
if __name__=='__main__':
 try:main()
 except BaseException as e:
  name='failure-'+sys.argv[1]+'.json'
  if not (HERE/name).exists():write(name,dict(error=repr(e),preserved=True))
  raise
