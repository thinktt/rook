#!/usr/bin/python3
"""Run the unchanged eight-fixture wire checker; observe existing helper PIDs."""
import hashlib,json,os,runpy,sys
from pathlib import Path
B=Path(sys.argv[1]);plan=json.loads((B/'plan.json').read_text());stage=B/'wire'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sorted(os.sched_getaffinity(0))==plan['helperCpus']
for p,h in plan['pins'].items():assert sha(p)==h,p
namespace=runpy.run_path(plan['wireChecker'],run_name='original_wire_checker_metadata_observed')
Process=namespace['Process'];original=Process.__init__;pids=[]
def init(self,engine,directory):
 original(self,engine,directory)
 pids.append({'case':directory.name,'pid':self.child.pid,'argv':self.child.args,'observer_after_original_init':True})
Process.__init__=init
sys.argv=[plan['wireChecker'],'--engine',plan['wireLauncher'],'--output',str(stage/'output')]
try:
 code=namespace['main']()
 assert code==0,code
 receipt=json.loads((stage/'output/receipt.json').read_text())
 assert receipt['pass'] and len(receipt['results'])==8 and sum(len(x['searches']) for x in receipt['results'])==24
finally:
 with (stage/'native-pids.json').open('x') as f:json.dump(pids,f,indent=2);f.write('\n')
