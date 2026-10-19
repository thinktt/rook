#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,re,subprocess
P=Path(__file__).resolve().parent;E=P.parent;B=E/'influence-bitsliced-sum-pgo-use-build-20261019-01';old=E/'pawn-progress-division-backend-review-20261019-01';image=B/'rook2-exact'
sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
load=lambda q:json.loads(Path(q).read_text())
def save(n,d):
 with (P/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13} and os.environ['PATH']=='/usr/bin:/bin'
receipt=load(B/'receipt.json');assert sha(image)==receipt['binary_output']['sha256']=='36251ecf12cfdc9437c9bfc5b7a571c1992471bee611cab024fc692ac79e91b2'
prior=load(old/'discovery.json');assert prior['pins'][str(image)]==sha(image)
assert sha('/usr/bin/objdump')==prior['pins']['/usr/bin/objdump']
assert receipt['pgo']['mode']=='profile-use' and receipt['pgo']['inputs_unchanged']
paths=[image,B/'receipt.json',B/'tool-terminal.json',B/'frozen-image.json',old/'nm.stdout',old/'nm-command.json',old/'discovery.json',old/'sections.stdout',old/'objdump-version.stdout',old/'objdump-version-command.json',Path('/usr/bin/objdump'),Path('/home/legolas/king-spec/spec/activity.md'),E/'activity-kernel-current25-design-20261019-01/review.md',P/'capture.py']
for n in ['src/activity.rs','src/influence.rs','src/types.rs','src/relation_table.rs']:
 q=B/'source-before'/n;assert sha(q)==receipt['source_sha256_before'][n];paths.append(q)
pins={str(q):sha(q) for q in paths}
rows=[]
for line in (old/'nm.stdout').read_text().splitlines():
 a=line.split(maxsplit=3)
 if len(a)==4 and a[3]=='rook2::activity::compute':rows.append(a)
assert len(rows)==1 and rows[0][2] in ['t','T'];r=rows[0];start=int(r[0],16);size=int(r[1],16);assert size<65536
argv=['/usr/bin/objdump','-d','-l','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)]
with (P/'activity.stdout').open('xb') as out,(P/'activity.stderr').open('xb') as err:
 child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
command=dict(argv=argv,pid=child.pid,actual_child_return_observed=True,exit_code=code,stdout_sha256=sha(P/'activity.stdout'),stderr_sha256=sha(P/'activity.stderr'));save('activity-command.json',command);assert code==0
assert (P/'activity.stdout').stat().st_size<=1048576
assert all(sha(q)==h for q,h in pins.items())
relation=[line for line in (old/'nm.stdout').read_text().splitlines() if line.endswith(' R rook2::relation_table::RELATIONS')];assert len(relation)==1
save('capture.json',dict(complete=True,image_sha256=sha(image),symbol=dict(address=hex(start),bytes=size,actual_symbol=r[3],complete_body=True),relation_table_actual_nm=relation[0],source_graph='e89dcb3315e4d8aaa5089ec445d0a7d0bda7f0928001c502c6343899a5195aa5',pins=pins,raw_disassembly_bytes=(P/'activity.stdout').stat().st_size,all_inputs_unchanged=True,command=command,cached_discovery='Closed same-image pawn division nm/sections/objdump version reused; no duplicate discovery/version calls.'))
print(json.dumps(dict(complete=True,address=hex(start),bytes=size,raw_bytes=(P/'activity.stdout').stat().st_size,exit_code=code,pins=len(pins))))
