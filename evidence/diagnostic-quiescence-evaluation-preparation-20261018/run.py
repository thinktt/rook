"""Bounded untimed Qentry/disposition verification over frozen native closure."""
from pathlib import Path
import os,json,hashlib,subprocess,sys,shutil,re,datetime
HERE=Path(__file__).parent
ROOT=HERE.parents[1]
SOURCE=Path('/tmp/imp2-quiescence-evaluation-validation-20261018')
OUT=ROOT/'evidence/diagnostic-quiescence-evaluation-20261018'
BUILD=ROOT/'evidence/diagnostic-quiescence-evaluation-build-20261018'
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13}
os.environ['PYTHONDONTWRITEBYTECODE']='1'
assert os.sched_getaffinity(0)==HELPERS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def snapshot(r):return {str(p.relative_to(r)):sha(p) for p in [r/'Cargo.toml',r/'Cargo.lock',*sorted(p for p in (r/'src').rglob('*') if p.is_file())]}
def run(cmd,stem):
 out,err=OUT/(stem+'.stdout'),OUT/(stem+'.stderr')
 with out.open('xb') as a,err.open('xb') as b:r=subprocess.run(cmd,cwd=SOURCE,env=ENV,stdout=a,stderr=b)
 stage={'command':cmd,'exit_code':r.returncode,'stdout_sha256':sha(out),'stderr_sha256':sha(err)}
 rec['stages'].append(stage);assert r.returncode==0,stem+' failed'
 return stage
plan=load(HERE/'plan.json');preparation=load(HERE/'source-preparation.json')
assert load(ROOT/'evidence/quiescence-evaluation-validation-20261018/native-tool-terminal.json')['exit_code']==0
reference=load(Path(plan['native_build_reference']));native_before=snapshot(SOURCE);adapter_before=snapshot(SOURCE/'diagnostic')
assert native_before==reference['source_sha256_before']==reference['source_sha256_after']
assert adapter_before==preparation['adapter_source_sha256']
assert sha(HERE/preparation['archive'])==preparation['archive_sha256'] and sha(Path(__file__))==preparation['planned_verifier_sha256']
assert all(sha(Path(name))==h for name,h in plan['fixtures'].items())
assert not OUT.exists() and not BUILD.exists();OUT.mkdir()
ENV=dict(os.environ,RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4')
dependencies=[Path(__file__),HERE/'plan.json',HERE/'source-preparation.json',HERE/preparation['archive'],ROOT/'tools/build.py',ROOT/'tools/archive_build.py',Path(plan['native_build_reference']),Path('/home/legolas/king-spec/conformance/run.mjs'),*map(Path,plan['fixtures'])]
before={str(p):sha(p) for p in dependencies};write(OUT/'inputs-before.json',{'native':native_before,'adapter':adapter_before,'dependencies':before,'environment':{k:ENV[k] for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']},'helper_affinity':sorted(os.sched_getaffinity(0))})
rec={'complete':False,'failure':None,'stages':[]}
try:
 run(['cargo','test','--offline','--locked','--release','--no-run','--message-format=json','--target','x86_64-unknown-linux-gnu','--target-dir',str(SOURCE/'target/quiescence-diagnostic-tests-20261018'),'--manifest-path',str(SOURCE/'diagnostic/Cargo.toml')],'unit-build')
 artifacts=[]
 for line in (OUT/'unit-build.stdout').read_text().splitlines():
  item=json.loads(line)
  if item.get('reason')=='compiler-artifact' and item['profile']['test'] and item.get('executable'):artifacts.append(Path(item['executable']))
 assert len(artifacts)==1
 tests=OUT/'unit-bin/rook2-diag-exact';tests.parent.mkdir();shutil.copy2(artifacts[0],tests);unit_sha=sha(tests)
 run([str(tests),'--test-threads=1'],'unit-tests')
 match=re.search(r'test result: ok\. (\d+) passed; 0 failed;', (OUT/'unit-tests.stdout').read_text());assert match and int(match[1])==109;assert sha(tests)==unit_sha
 rec['unit_binary_sha256']=unit_sha;assert snapshot(SOURCE)==native_before and snapshot(SOURCE/'diagnostic')==adapter_before
 run([sys.executable,str(ROOT/'tools/build.py'),'--crate',str(SOURCE/'diagnostic'),'--bin','rook2-diag','--mode','generic','--output',str(BUILD)],'build-driver')
 build=load(BUILD/'receipt.json');frozen=BUILD/'rook2-diag-exact';shutil.copy2(build['binary_output']['path'],frozen);adapter_sha=sha(frozen);assert adapter_sha==build['binary_output']['sha256']
 write(BUILD/'tool-terminal.json',{'exit_code':0,'actual_build_return':True,'binary_frozen_sha256':adapter_sha,'stage':rec['stages'][-1]})
 run([sys.executable,str(ROOT/'tools/archive_build.py'),str(BUILD)],'archive')
 command=['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
 for name in plan['fixtures']:command+=['--fixtures',name]
 command+=['--',str(frozen)]
 stage=run(command,'conformance');shutil.copyfile(OUT/'conformance.stdout',OUT/'conformance.json')
 report=load(OUT/'conformance.json');assert report['pass'] and len(report['results'])==5187;assert not (OUT/'conformance.stderr').stat().st_size
 assert sha(frozen)==adapter_sha
 rec.update(complete=True,adapter_sha256=adapter_sha,cases=len(report['results']))
except BaseException as e:rec['failure']=type(e).__name__+': '+str(e)
finally:
 native_after=snapshot(SOURCE);adapter_after=snapshot(SOURCE/'diagnostic');after={str(p):sha(p) for p in dependencies};stable=native_after==native_before and adapter_after==adapter_before and after==before
 rec['inputs_stable']=stable
 if not stable:rec.update(complete=False,failure='source/dependency changed')
 write(OUT/'inputs-after.json',{'native':native_after,'adapter':adapter_after,'dependencies':after});write(OUT/'verification.json',rec)
 write(OUT/'tool-terminal.json',{'exit_code':0 if rec['complete'] else 1,'complete':rec['complete'],'failure':rec['failure'],'verification_sha256':sha(OUT/'verification.json'),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(json.dumps({'complete':rec['complete'],'failure':rec['failure'],'output':str(OUT)}))
sys.exit(0 if rec['complete'] else 1)
