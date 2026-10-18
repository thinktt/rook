import json,os,re,shutil,subprocess,sys
from pathlib import Path
from guard import HERE,load,sha,write,check
def run(argv,stem,out,env,cwd,stages):
 with (out/(stem+'.stdout')).open('xb') as a,(out/(stem+'.stderr')).open('xb') as b:
  child=subprocess.run(argv,cwd=cwd,env=env,stdout=a,stderr=b)
 record=dict(command=argv,exit_code=child.returncode,actual_child_return_observed=True,stdout_sha256=sha(out/(stem+'.stdout')),stderr_sha256=sha(out/(stem+'.stderr')))
 stages.append(record);assert child.returncode==0,stem+' failed'
 return record

def units(source,crate,counts,target,out,env,stages):
 command=['/usr/bin/cargo','test','--offline','--locked','--release','--no-run','--message-format=json','--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(target),'--manifest-path',str(crate/'Cargo.toml')]
 if crate==source:command+=['--lib','--bin','rook2-dev']
 run(command,'unit-build',out,env,source,stages);artifacts={}
 for line in (out/'unit-build.stdout').read_text().splitlines():
  item=json.loads(line)
  if item.get('reason')=='compiler-artifact' and item['profile']['test'] and item.get('executable'):artifacts[item['target']['name']]=Path(item['executable'])
 assert set(artifacts)==set(counts),'unit target inventory'
 observed={}
 for name,count in counts.items():
  frozen=out/'unit-bin'/name/'unit-exact';frozen.parent.mkdir(parents=True);shutil.copy2(artifacts[name],frozen);identity=sha(frozen)
  run([str(frozen),'--test-threads=1'],name+'-tests',out,env,source,stages)
  text=(out/(name+'-tests.stdout')).read_text();match=re.search(r'test result: ok\. (\d+) passed; 0 failed;',text)
  assert match and int(match[1])==count and len(re.findall(r'^test .* \.\.\. ok$',text,re.M))==count
  assert sha(frozen)==identity;observed[name]=dict(passed=count,binary_sha256=identity)
 return observed

def build(source,crate,binary,out,logs,env,stages,expected):
 run([sys.executable,str(source/'tools/build.py'),'--crate',str(crate),'--mode','generic','--bin',binary,'--jobs','4','--output',str(out)],'build-driver',logs,env,source,stages)
 receipt=load(out/'receipt.json');assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['source_sha256_before']==receipt['source_sha256_after']==expected
 assert receipt['mode']=='generic' and receipt['rust_flags']==['-C','target-cpu=x86-64'] and receipt['pgo']['mode']=='none'
 frozen=out/(binary+'-exact');shutil.copy2(receipt['binary_output']['path'],frozen);assert sha(frozen)==receipt['binary_output']['sha256']
 run([sys.executable,str(source/'tools/archive_build.py'),str(out)],'archive',logs,env,source,stages)
 write(out/'child-build-terminal.json',dict(exit_code=0,actual_build_child_return_observed=True,frozen_sha256=sha(frozen),note='Actual outer tool terminal must be recorded externally before next stage'))
 return sha(frozen)


p=check();S=Path(p['source']);paths=p['paths'];V=Path(paths['validation']);assert load(V/'native-verification.json')['complete'];assert load(V/'generic-actual-terminal.json')['exit_code']==0;assert load(V/'ordinary-check/tool-terminal.json')['complete'];OUT=Path(paths['diagnostic_validation']);assert not OUT.exists();OUT.mkdir();BUILD=Path(paths['diagnostic_build']);assert not BUILD.exists();stages=[];result={'complete':False,'failure':None,'stages':stages,'scope':'Exact combined103bits cold175 + original whole100files7514cases; no sourcefix/CPU/PGO/profile'}
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4');env.pop('LLVM_PROFILE_FILE',None)
try:
 result['units']=units(S,S/'diagnostic',{'rook2-diag':175},S/'target/combined103bits-diagnostic-units',OUT,env,stages)
 result['artifact_sha256']=build(S,S/'diagnostic','rook2-diag',BUILD,OUT,env,stages,{n.removeprefix('diagnostic/'):v for n,v in p['diagnostic_sha256'].items()})
 raw=OUT/'raw-cases';raw.mkdir();command=['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
 for path in p['fixtures']:command+=['--fixtures',path]
 command+=['--',sys.executable,str(HERE/'record_case.py'),'--adapter',str(BUILD/'rook2-diag-exact'),'--records',str(raw)]
 run(command,'conformance',OUT,env,S,stages);r=load(OUT/'conformance.stdout');assert r['pass'] and len(r['results'])==7514 and not(OUT/'conformance.stderr').stat().st_size;assert sha(BUILD/'rook2-diag-exact')==result['artifact_sha256'];check();result.update(complete=True,cases=7514,operations=103,whole_files=100)
except BaseException as error:result['failure']=type(error).__name__+': '+str(error)
finally:write(OUT/'verification.json',result)
print(json.dumps({k:v for k,v in result.items() if k!='stages'}));sys.exit(0 if result['complete'] else 1)
