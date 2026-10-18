import os,json,hashlib,subprocess,sys,shutil,datetime
from pathlib import Path
HERE=Path(__file__).parent
ROOT=HERE.parents[1]
SOURCE=Path('/tmp/imp2-ordered-bit-checkers-phase1-validation-20261018-lys_zi80')
BUILD=ROOT/'evidence/ordered-bit-checkers-phase1-build-20261018'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.sched_getaffinity(0)==HELPERS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def run(cmd,stem):
 out,err=HERE/(stem+'.stdout'),HERE/(stem+'.stderr')
 with out.open('xb') as a,err.open('xb') as b:r=subprocess.run(cmd,cwd=SOURCE,stdout=a,stderr=b)
 stage={'command':cmd,'exit_code':r.returncode,'stdout_sha256':sha(out),'stderr_sha256':sha(err)}
 rec['stages'].append(stage)
 assert r.returncode==0,stem+' failed'
 return stage
rec={'complete':False,'failure':None,'stages':[],'helper_affinity':sorted(os.sched_getaffinity(0))}
try:
 run([sys.executable,str(HERE/'check_native.py')],'native-tests-driver')
 tests=json.loads((HERE/'native-verification.json').read_text());assert tests['complete'] and tests['inputs_stable'];assert sum(x['passed'] for x in tests['units'].values())==143
 run([sys.executable,str(SOURCE/'tools/build.py'),'--crate',str(SOURCE),'--mode','generic','--bin','rook2','--output',str(BUILD)],'native-build-driver')
 receipt=json.loads((BUILD/'receipt.json').read_text());assert receipt['source_identity_unchanged'] and receipt['pgo']['mode']=='none'
 frozen=BUILD/'rook2-exact';shutil.copy2(receipt['binary_output']['path'],frozen);assert sha(frozen)==receipt['binary_output']['sha256']
 rec['native_sha256']=sha(frozen)
 write(BUILD/'tool-terminal.json',{'exit_code':0,'actual_build_return':True,'binary_frozen_sha256':sha(frozen),'build_driver_stage':rec['stages'][-1]})
 run([sys.executable,str(SOURCE/'tools/archive_build.py'),str(BUILD)],'native-archive')
 rec['complete']=True
except BaseException as e:rec['failure']=str(type(e).__name__)+': '+str(e)
finally:
 rec['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(HERE/'native-pipeline.json',rec)
 write(HERE/'native-tool-terminal.json',{'exit_code':0 if rec['complete'] else 1,'complete':rec['complete'],'failure':rec['failure'],'pipeline_sha256':sha(HERE/'native-pipeline.json')})
print(json.dumps(rec))
sys.exit(0 if rec['complete'] else 1)
