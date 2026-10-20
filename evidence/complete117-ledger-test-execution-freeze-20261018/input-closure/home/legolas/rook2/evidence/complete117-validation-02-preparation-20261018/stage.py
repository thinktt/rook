#!/usr/bin/env python3
"""Future exact complete117 validation; gated before every mutation/native job."""
import argparse,json,os,re,shutil,subprocess,sys,tarfile,time
from pathlib import Path
sys.dont_write_bytecode=True
from guard import HERE,load,sha,write,clearance,terminal,check_sources,check_dependencies

def run(argv,stem,out,env,cwd,stages):
 with (out/(stem+'.stdout')).open('xb') as a,(out/(stem+'.stderr')).open('xb') as b:
  child=subprocess.Popen(argv,cwd=cwd,env=env,stdout=a,stderr=b)
  if stem in ['strict54','wire']:
   engine=Path(clearance()['output']['generic-build'])/'rook2-exact';seen={}
   while child.poll() is None:
    for entry in Path('/proc').iterdir():
     if not entry.name.isdigit():continue
     try:
      if Path(os.readlink(entry/'exe'))!=engine:continue
      mask=sorted(os.sched_getaffinity(int(entry.name)));assert mask==sorted(os.sched_getaffinity(0))
      seen[entry.name]=mask
     except (FileNotFoundError,ProcessLookupError,PermissionError):continue
    time.sleep(0.01)
   write(out/(stem+'-actual-engine-affinity.json'),dict(actual_observed_pids=seen,expected_inherited_mask=sorted(os.sched_getaffinity(0)),scope='Observed actual executable PIDs; coverage count stated literally, no unobserved PID assumption'))
  child.wait()
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','generic','native','strict','diag']);args=parser.parse_args();plan=clearance('freeze' if args.stage=='freeze' else 'execution')
 source=Path(plan['home_source']);frozen=Path(plan['frozen_source']);paths={k:Path(v) for k,v in plan['output'].items()}
 key={'freeze':'freeze','generic':'generic-build','native':'native-validation','strict':'strict-check','diag':'diagnostic'}[args.stage];out=paths[key];assert not out.exists(), 'fresh stage output required'
 previous={'generic':'freeze','native':'generic-build','strict':'native-validation','diag':'strict-check'}
 if args.stage in previous:
  terminal(paths[previous[args.stage]]/'tool-terminal.json');check_sources(plan);check_dependencies(plan)
 if args.stage=='diag':terminal(paths['generic-build']/'tool-terminal.json')
 if args.stage=='generic':assert not (source/'target').exists(),'generic build precedes all native/unit compilation'
 if args.stage=='freeze':assert not source.exists() and not source.is_symlink(),'fresh absent HOME source required'
 # build.py requires an absent output directory; generic stage logs live separately.
 logs=out if args.stage!='generic' else HERE/'generic-stage-logs'
 if args.stage!='generic':out.mkdir()
 else:logs.mkdir()
 stages=[];result=dict(complete=False,stage=args.stage,failure=None,stages=stages,affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR'])
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-Ctarget-cpu=x86-64',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4');env.pop('LLVM_PROFILE_FILE',None)
 try:
  if args.stage=='freeze':
   assert all(sha(frozen/name)==h for name,h in plan['source_sha256'].items())
   source.parent.mkdir(parents=True,exist_ok=True);source.mkdir()
   for name,h in plan['source_sha256'].items():
    dest=source/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(frozen/name,dest);assert sha(dest)==h
   check_sources(plan)
   assert {str(q.relative_to(source)) for q in source.rglob('*') if q.is_file()}==set(plan['source_sha256'])
   with tarfile.open(out/'source-frozen.tar.gz','w:gz') as t:
    for name in plan['source_sha256']:t.add(source/name,arcname=name,recursive=False)
   proposal=Path(plan['proposal']);spec=Path('/home/legolas/king-spec/conformance')
   dependencies=[Path(path) for path in plan['immutable_dependencies']]
   dependencies += [Path(path) for path in plan['fixtures']]
   for name in plan['fixtures']:
    document=load(Path(name));assert len(document['cases'])==plan['fixture_counts'][name] and {k:v for k,v in document.items() if k!='cases'}==plan['fixture_headers'][name]
   assert all(sha(Path(path))==h for path,h in plan['fixtures'].items())
   dep={str(path):sha(path) for path in dependencies};write(out/'dependencies.json',dep);copy=out/'input-closure';copy.mkdir()
   for path,h in dep.items():
    dest=copy/path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest);assert sha(dest)==h
   with tarfile.open(out/'input-closure.tar.gz','w:gz') as t:
    for q in sorted(copy.rglob('*')):
     if q.is_file():t.add(q,arcname=str(q.relative_to(copy)),recursive=False)
   result.update(source_sha256=plan['source_sha256'],source_archive_sha256=sha(out/'source-frozen.tar.gz'),input_archive_sha256=sha(out/'input-closure.tar.gz'),dependencies_sha256=sha(out/'dependencies.json'))
  elif args.stage=='generic':
   result['artifact_sha256']=build(source,source,'rook2',out,logs,env,stages,plan['native_sha256']);assert load(out/'receipt.json')['tool_sha256_before']==load(out/'receipt.json')['tool_sha256_after']==plan['tools_sha256']
  elif args.stage=='native':
   result['units']=units(source,source,{'rook2':175,'rook2-dev':2},source/'target/complete117-native-unit',out,env,stages)
  elif args.stage=='strict':
   engine=paths['generic-build']/'rook2-exact';identity=sha(engine);assert identity==load(paths['generic-build']/'receipt.json')['binary_output']['sha256']
   run(['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--',str(engine)],'strict54',out,env,source,stages)
   report=load(out/'strict54.stdout');assert report['status']=='pass' and len(report['results'])==54 and not (out/'strict54.stderr').stat().st_size
   for row in report['results']:assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']==dict(code=0,signal=None) and row['error'] is None and row['stderr']=='' and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
   run([sys.executable,str(source/'tools/check_live.py'),'--engine',str(engine),'--output',str(paths['interruption-wire'])],'wire',out,env,source,stages)
   wr=load(paths['interruption-wire']/'receipt.json');assert wr['pass'] and len(wr['results'])==8 and sum(len(row['searches']) for row in wr['results'])==24 and all(row['complete_streams'] and row['exit_code']==row['observed_exit_code']==0 for row in wr['results'])
   assert wr['engine_sha256_before']==wr['engine_sha256_after']==sha(engine)==identity;result.update(artifact_sha256=identity,strict_replays=54,wire_fixtures=8,wire_searches=24)
  else:
   result['units']=units(source,source/'diagnostic',{'rook2-diag':209},source/'target/complete117-diag-unit',out,env,stages)
   result['artifact_sha256']=build(source,source/'diagnostic','rook2-diag',paths['diagnostic-build'],out,env,stages,{k.removeprefix('diagnostic/'):v for k,v in plan['diagnostic_sha256'].items()})
   raw=out/'raw-cases';raw.mkdir();command=['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
   for path in plan['fixtures']:command+=['--fixtures',path]
   command+=['--',sys.executable,str(HERE/'record_case.py'),'--adapter',str(paths['diagnostic-build']/'rook2-diag-exact'),'--records',str(raw)]
   run(command,'conformance',out,env,source,stages);report=load(out/'conformance.stdout');assert report['pass'] and len(report['results'])==7673 and not (out/'conformance.stderr').stat().st_size
   assert sha(paths['diagnostic-build']/'rook2-diag-exact')==result['artifact_sha256'];result.update(cases=7673,operations=117,whole_files=115)
  check_sources(plan)
  if args.stage!='freeze':check_dependencies(plan)
  result['complete']=True
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 finally:
  write(logs/'verification.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','stages']}));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
