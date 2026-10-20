from pathlib import Path
import runpy,sys,json,hashlib,os
E=Path(__file__).resolve().parent
PLAN=json.loads((E/'plan.json').read_text())
def sha(q):return hashlib.sha256(Path(q).read_bytes()).hexdigest()
def write(q,d):
 with Path(q).open('x') as s:json.dump(d,s,indent=2);s.write('\n')
assert set(os.sched_getaffinity(0))==set(PLAN['helper_cpus'])
image=Path(PLAN['engine']);build=image.parent
receipt=json.loads((build/'receipt.json').read_text());w=Path(receipt['crate'])
assert receipt['pgo']['mode']=='profile-use' and receipt['pgo']['inputs_unchanged']
assert receipt['source_sha256_before']==receipt['source_sha256_after']
assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
assert receipt['binary_output']['sha256']==PLAN['engine_sha256']
pins={str(w/k):v for k,v in (receipt['source_sha256_before']|receipt['tool_sha256_before']).items()}
pins.update({PLAN['engine']:PLAN['engine_sha256'],PLAN['fixture']:PLAN['fixture_sha256'],PLAN['checker']:PLAN['checker_sha256']})
for q in [build/'receipt.json',build/'frozen-image.json',E/'plan.json',E/'run_wire.py']:pins[str(q)]=sha(q)
for q,h in pins.items():assert sha(q)==h,q
write(E/'inputs-before.json',pins)
fixture=json.loads(Path(PLAN['fixture']).read_text());assert len(fixture['cases'])==8 and all(len(c['request']['input']['searches'])==3 for c in fixture['cases'])
namespace=runpy.run_path(PLAN['checker'],run_name='original_wire_checker_metadata_observed')
Process=namespace['Process'];original_init=Process.__init__;pids=[]
def init(self,engine,directory):
 original_init(self,engine,directory)
 pids.append({'case':directory.name,'pid':self.child.pid,'argv':self.child.args,'observer_after_original_init':True})
Process.__init__=init
sys.argv=[PLAN['checker'],'--engine',PLAN['engine'],'--output',str(E/'wire')]
try:
 rc=namespace['main']()
 write(E/'native-pids.json',pids)
 assert rc==0,rc
 out=json.loads((E/'wire/receipt.json').read_text())
 assert out['pass'] and len(out['results'])==8 and sum(len(x['searches']) for x in out['results'])==24
 assert [x['case'] for x in pids]==[c['id'] for c in fixture['cases']]
 assert len({x['pid'] for x in pids})==8
 for q,h in pins.items():assert sha(q)==h,q
 write(E/'identity.json',{'complete':True,'engine_sha256':sha(image),'fixture_count':8,'requests':24,'inputs_before_after_equal':pins,'native_pids':pids,'new_native_lifetimes':8,'no_retries':True,'performance_sample':False})
except BaseException as error:
 if not (E/'native-pids.json').exists():write(E/'native-pids.json',pids)
 write(E/'failure.json',{'complete':False,'error':repr(error),'native_pids':pids})
 raise
