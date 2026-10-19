#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,sys
P=Path(__file__).resolve().parent;E=P.parent;B=E/'influence-bitsliced-sum-pgo-use-build-20261019-01';image=B/'rook2-exact'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def save(n,d):
 with (P/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def run(argv,stem):
 with (P/(stem+'.stdout')).open('xb') as o,(P/(stem+'.stderr')).open('xb') as e:
  child=subprocess.Popen(argv,stdout=o,stderr=e);code=child.wait()
 r=dict(argv=argv,pid=child.pid,actual_child_return_observed=True,exit_code=code,stdout_sha256=sha(P/(stem+'.stdout')),stderr_sha256=sha(P/(stem+'.stderr')));save(stem+'-command.json',r);assert code==0,r;return r
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13} and os.environ['PATH']=='/usr/bin:/bin'
if sys.argv[1]=='discover':
 receipt=load(B/'receipt.json');assert sha(image)==receipt['binary_output']['sha256']=='36251ecf12cfdc9437c9bfc5b7a571c1992471bee611cab024fc692ac79e91b2'
 assert receipt['pgo']['mode']=='profile-use' and receipt['source_sha256_before']==receipt['source_sha256_after'] and receipt['pgo']['inputs_unchanged']
 terminal=load(B/'tool-terminal.json');assert terminal['actual_tool_terminal_observed'] and terminal['exit_code']==0 and terminal['terminal_chunk_id']=='326a8f'
 paths=[image,B/'receipt.json',B/'tool-terminal.json',B/'frozen-image.json',E/'pawn-progress-next-cost-triage-20261019-01/review.md',E/'pawn-progress-next-cost-triage-20261019-01/source-proof.json',Path('/home/legolas/king-spec/spec/pawn-candidates.md'),P/'capture.py']
 for n in ['src/pawn_progress.rs','src/types.rs','src/position.rs','src/influence.rs']:
  q=B/'source-before'/n;assert sha(q)==receipt['source_sha256_before'][n];paths.append(q)
 commands=[]
 for exe in ['/usr/bin/nm','/usr/bin/objdump','/usr/bin/readelf']:
  paths.append(Path(exe));commands.append(run([exe,'--version'],Path(exe).name+'-version'))
 pins={str(q):sha(q) for q in paths}
 commands +=[run(['/usr/bin/nm','-n','-S','--defined-only','--demangle',str(image)],'nm'),run(['/usr/bin/nm','-n','-S','--defined-only',str(image)],'nm-mangled'),run(['/usr/bin/readelf','-SW',str(image)],'sections')]
 symbols=[]
 for line in (P/'nm.stdout').read_text().splitlines():
  a=line.split(maxsplit=3)
  if len(a)==4 and a[2] in ['t','T'] and a[3].startswith('rook2::pawn_progress::'):symbols.append(dict(start=a[0],bytes=int(a[1],16),actual_symbol=a[3]))
 assert all(sha(q)==h for q,h in pins.items());save('discovery.json',dict(complete=True,pins=pins,commands=commands,pawn_progress_symbols=symbols));print(json.dumps(symbols))
else:
 assert sys.argv[1]=='bodies';d=load(P/'discovery.json');assert all(sha(q)==h for q,h in d['pins'].items())
 selected=[r for r in d['pawn_progress_symbols'] if r['actual_symbol'] in ['rook2::pawn_progress::raw','rook2::pawn_progress::candidates','rook2::pawn_progress::selected']]
 assert selected and len(selected)<=3;rows=[];total=0
 for r in selected:
  stem=r['actual_symbol'].split('::')[-1];start=int(r['start'],16)
  command=run(['/usr/bin/objdump','-d','-l','--demangle','--no-show-raw-insn','-Mintel','--start-address='+hex(start),'--stop-address='+hex(start+r['bytes']),str(image)],stem)
  total+=(P/(stem+'.stdout')).stat().st_size;assert total<=1048576
  rows.append(dict(**r,complete_body=True,command=command,raw_bytes=(P/(stem+'.stdout')).stat().st_size))
 assert all(sha(q)==h for q,h in d['pins'].items());save('bodies.json',dict(complete=True,bodies=rows,total_raw_bytes=total,all_inputs_unchanged=True));print(json.dumps(dict(complete=True,bodies=len(rows),raw_bytes=total)))
