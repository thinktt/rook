#!/usr/bin/env python3
"""Future ordinary-projected-bits complete117 freeze/DIAG; blocked until parent clearance."""
import argparse,json,os,re,shutil,subprocess,sys,tarfile
from pathlib import Path
sys.dont_write_bytecode=True
from guard import HERE,load,sha,write,clearance,terminal,check_sources,check_dependencies

def run(argv,stem,out,env,cwd,stages):
 with (out/(stem+'.stdout')).open('xb') as a,(out/(stem+'.stderr')).open('xb') as b:
  child=subprocess.Popen(argv,cwd=cwd,env=env,stdout=a,stderr=b)
  code=child.wait()
 record=dict(command=argv,pid=child.pid,exit_code=code,actual_child_return_observed=True,stdout_sha256=sha(out/(stem+'.stdout')),stderr_sha256=sha(out/(stem+'.stderr')))
 stages.append(record);assert code==0,stem+' failed'
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','diag']);args=parser.parse_args()
 plan=clearance('freeze' if args.stage=='freeze' else 'execution')
 source=Path(plan['home_source']);paths={k:Path(v) for k,v in plan['output'].items()}
 out=paths['freeze' if args.stage=='freeze' else 'diagnostic'];assert not out.exists(),'fresh absent stage output required'
 check_sources(plan);check_dependencies(plan)
 if args.stage=='freeze':assert not source.exists() and not source.is_symlink(),'fresh absent HOME execution copy required'
 else:terminal(paths['freeze']/'tool-terminal.json');assert source.exists()
 out.mkdir();stages=[];result=dict(complete=False,stage=args.stage,failure=None,stages=stages,affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR'],native178_strict54_wire8_reused=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4');env.pop('LLVM_PROFILE_FILE',None)
 try:
  if args.stage=='freeze':
   source.mkdir()
   for name,h in plan['source_sha256'].items():
    dest=source/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(plan['source_origins'][name],dest);assert sha(dest)==h
   assert {str(q.relative_to(source)) for q in source.rglob('*') if q.is_file()}==set(plan['source_sha256'])
   with tarfile.open(out/'source-frozen.tar.gz','w:gz') as t:
    for name in plan['source_sha256']:t.add(source/name,arcname=name,recursive=False)
   result['source_archive_sha256']=sha(out/'source-frozen.tar.gz')
   with tarfile.open(out/'source-frozen.tar.gz','r:gz') as t:
    assert {m.name:__import__('hashlib').sha256(t.extractfile(m).read()).hexdigest() for m in t}==plan['source_sha256']
   with tarfile.open(out/'official-inputs-115.tar.gz','w:gz') as t:
    for name in plan['fixtures']:t.add(name,arcname=name.lstrip('/'),recursive=False)
   with tarfile.open(out/'official-inputs-115.tar.gz','r:gz') as t:
    assert {m.name:__import__('hashlib').sha256(t.extractfile(m).read()).hexdigest() for m in t}=={name.lstrip('/'):h for name,h in plan['fixtures'].items()}
   result['official_archive_sha256']=sha(out/'official-inputs-115.tar.gz')
   write(HERE/'archive-verification.json',dict(source112_sha256=result['source_archive_sha256'],official115_sha256=result['official_archive_sha256'],reopened_members_exact=True))
  else:
   # No generic ordinary build/native tests/strict replay branch exists here.
   result['units']=units(source,source/'diagnostic',{'rook2-diag':209},source/'target/ordinary-projected-bits-relations-complete117-diag-unit',out,env,stages)
   assert not paths['diagnostic-build'].exists(),'build.py output must be absent'
   result['artifact_sha256']=build(source,source/'diagnostic','rook2-diag',paths['diagnostic-build'],out,env,stages,{k.removeprefix('diagnostic/'):v for k,v in plan['diagnostic_sha256'].items()})
   br=load(paths['diagnostic-build']/'receipt.json');nr=load(plan['native_reference']['build_receipt'])
   for key in ['toolchain','mode','target_triple','target_cpu','rust_flags']:assert br[key]==nr[key]
   assert br['tool_sha256_before']==br['tool_sha256_after']==plan['diagnostic_crate_tools_sha256']=={}
   assert len(plan['tools_sha256'])==23 # separately checked in the full112 closure
   raw=out/'raw-cases';raw.mkdir();command=['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
   for path in plan['fixtures']:command+=['--fixtures',path]
   command+=['--',sys.executable,str(HERE/'record_case.py'),'--adapter',str(paths['diagnostic-build']/'rook2-diag-exact'),'--records',str(raw)]
   run(command,'conformance',out,env,source,stages)
   report=load(out/'conformance.stdout');assert report['pass'] and len(report['results'])==7673 and not (out/'conformance.stderr').stat().st_size
   assert sha(paths['diagnostic-build']/'rook2-diag-exact')==result['artifact_sha256'];result.update(cases=7673,operations=117,whole_files=115)
  check_sources(plan);check_dependencies(plan);result['complete']=True
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 finally:write(out/'verification.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='stages'}));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
