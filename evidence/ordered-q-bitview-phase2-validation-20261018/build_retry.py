import datetime,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
V=Path(__file__).parent;S=Path('/home/legolas/rook2-work/ordered-q-bitview-phase2-20261018-5v7mxmev');B=Path('/home/legolas/rook2/evidence/ordered-q-bitview-phase2-build-02-20261018')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
n=json.loads((V/'native-verification.json').read_text());assert n['complete'] and n['inputs_stable'] and sum(v['passed'] for v in n['units'].values())==145
assert not B.exists()
r={'complete':False,'failure':None,'stages':[],'source':str(S),'build':str(B),'native_units_reused':145,'affinity':sorted(os.sched_getaffinity(0)),'TMPDIR':os.environ['TMPDIR']}
def run(cmd,stem):
 out=V/(stem+'.stdout');err=V/(stem+'.stderr')
 with out.open('xb') as a,err.open('xb') as b:done=subprocess.run(cmd,cwd=S,stdout=a,stderr=b)
 r['stages'].append({'command':cmd,'exit_code':done.returncode,'stdout_sha256':h(out),'stderr_sha256':h(err)})
 assert done.returncode==0,stem+' failed'
try:
 run([sys.executable,str(S/'tools/build.py'),'--crate',str(S),'--mode','generic','--bin','rook2','--output',str(B)],'generic-retry-build')
 receipt=json.loads((B/'receipt.json').read_text());assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['pgo']['mode']=='none'
 frozen=B/'rook2-exact';shutil.copy2(receipt['binary_output']['path'],frozen);assert h(frozen)==receipt['binary_output']['sha256']
 write(B/'tool-terminal.json',{'exit_code':0,'actual_build_return':True,'binary_frozen_sha256':h(frozen),'build_driver_stage':r['stages'][-1]})
 run([sys.executable,str(S/'tools/archive_build.py'),str(B)],'generic-retry-archive')
 r.update(complete=True,native_sha256=h(frozen),receipt_sha256=h(B/'receipt.json'))
except BaseException as e:r['failure']=type(e).__name__+': '+str(e)
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(V/'generic-retry-pipeline.json',r)
 write(V/'generic-retry-tool-terminal.json',{'exit_code':0 if r['complete'] else 1,'complete':r['complete'],'failure':r['failure'],'pipeline_sha256':h(V/'generic-retry-pipeline.json')})
print(json.dumps(r));sys.exit(0 if r['complete'] else 1)
