"""Parent authorized exactly six whole bodies;262144B total, no truncation."""
from pathlib import Path
import json,re,subprocess,hashlib,os
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
d=json.loads((P/'discovery.json').read_text());pins=d['input_pins']
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13} and os.environ['PATH']=='/usr/bin:/bin'
assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
assert all(sha(f)==h for f,h in pins.items())
selfpin=sha(__file__);rows=[];commands=[];total=0
for side,base in [('control','pressure-value-static'),('candidate','shelter-ring-value-static')]:
 for symbol in ['rook2::shelter::compute','rook2::shelter::components','rook2::evaluator::Evaluator<_>::full_impl']:
  found=[m for l in (P/(side+'-nm.stdout')).read_text().splitlines() if (m:=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',l)) and m[3]==symbol]
  assert len(found)==1;f=found[0];start,size=int(f[1],16),int(f[2],16)
  argv=['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(start),'--stop-address='+hex(start+size),str(E/(base+'-generic-build-20261019-01')/'rook2-exact')]
  stem=side+'-complete-'+symbol.rsplit('::',1)[-1]
  with (P/(stem+'.stdout')).open('xb') as o,(P/(stem+'.stderr')).open('xb') as e:
   child=subprocess.Popen(argv,stdout=o,stderr=e);code=child.wait()
  command={'argv':argv,'pid':child.pid,'exit_code':code,'actual_child_return_observed':True,'stdout':stem+'.stdout','stdout_sha256':sha(P/(stem+'.stdout')),'stderr_sha256':sha(P/(stem+'.stderr'))}
  with (P/(stem+'-command.json')).open('x') as out:json.dump(command,out,indent=2);out.write('\n')
  commands.append(command);assert code==0,command
  total+=(P/(stem+'.stdout')).stat().st_size;assert total<=262144,('Parent cap exhausted; preserve/stop',total)
  rows.append({'side':side,'symbol':symbol,'address':start,'bytes':size,'whole_body':True,'stdout':stem+'.stdout'})
assert len(rows)==6 and sha(__file__)==selfpin and all(sha(f)==h for f,h in pins.items())
with (P/'bodies.json').open('x') as f:json.dump({'complete':True,'whole_bodies':rows,'commands':commands,'total_disassembly_bytes':total,'cap_bytes':262144,'exact_six_body_scope':True,'inputs_unchanged':True,'discovery_input_pins':pins,'body_helper_sha256':selfpin,'no_original_helper_mutation':True},f,indent=2);f.write('\n')
print(json.dumps({'complete':True,'whole_bodies':6,'disassembly_bytes':total,'all_inputs_unchanged':True}))
