import hashlib,json,os,subprocess
from pathlib import Path
B=Path('/work');out=B/'training';out.mkdir();(out/'native').mkdir()
S=Path('/home/legolas/king-spec/conformance/profiling')
cmd=['/usr/bin/node',str(S/'replay-check.mjs'),'--','/usr/bin/python3','/work/training-launch.py']
env=dict(os.environ,LLVM_PROFILE_FILE='/work/profile-raw/native-%m-%p.profraw')
(out/'plan.json').write_text(json.dumps({'argv':cmd,'affinity':sorted(os.sched_getaffinity(0)),'LLVM_PROFILE_FILE':env['LLVM_PROFILE_FILE']},indent=2)+'\n')
with (out/'replay.json').open('xb') as a,(out/'stderr').open('xb') as z:p=subprocess.run(cmd,env=env,stdout=a,stderr=z,timeout=1200)
assert p.returncode==0,(p.returncode,(out/'stderr').read_text())
r=json.loads((out/'replay.json').read_text());cases=json.loads((S/'workloads.json').read_text())['cases']
assert r['status']=='pass' and r['selectedCases']==[c['id'] for c in cases] and len(r['results'])==54
assert not (out/'stderr').stat().st_size
native=[]
for row in r['results']:
 assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']=={'code':0,'signal':None}
 assert row['error'] is None and row['discardedObservedBytes']==0 and row['stderr']==''
 n=json.loads((out/'native'/str(row['pid'])).with_suffix('.json').read_text())
 assert n['failure'] is None and n['native_exit_code']==0 and n['native_post_exec']['affinity']==[14]
 native.append(n)
raw=sorted((B/'profile-raw').glob('*.profraw'));assert len(raw)==54
assert {int(p.stem.rsplit('-',1)[1]) for p in raw}=={n['native_pid'] for n in native}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
x={'complete':True,'strictCases':54,'nativeCount':54,'nativePids':[n['native_pid'] for n in native],'source':json.loads((B/'source-map.json').read_text()),'target':'x86_64-unknown-linux-musl','rawProfileSha256':{str(p):sha(p) for p in raw},'instrumentedSha256':sha(B/'artifacts/rook2-instrumented'),'replaySha256':sha(out/'replay.json')}
(out/'result.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'trainingCases':54,'profiles':54,'allPass':True}),flush=True)
