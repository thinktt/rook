#!/usr/bin/env python3
# Frozen87 adapter verification; no ordinary engine rebuild/replay or measurement.
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;E=HERE.parent
SOURCE=Path(json.loads((HERE/'paths.json').read_text())['source_root'])
sys.dont_write_bytecode=True;sys.path.insert(0,str(SOURCE/'tools'))
from build import source_snapshot,tool_snapshot
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--label',default='20261018');args=parser.parse_args()
 if not re.fullmatch(r'[A-Za-z0-9_-]+',args.label):parser.error('invalid fresh attempt label')
 out=E/('diagnostic-retained-search-pawn-'+args.label);build=E/('diagnostic-retained-search-pawn-build-'+args.label)
 if out.exists() or build.exists():parser.error('fresh absent output/build required; preserve failed attempts')
 out.mkdir();rec={'complete':False,'failure':None,'stages':[],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};before=None
 def run(argv,stem,env):
  stdout=out/(stem+'.stdout');stderr=out/(stem+'.stderr')
  with stdout.open('xb') as a,stderr.open('xb') as b:r=subprocess.run(argv,cwd=SOURCE,env=env,stdout=a,stderr=b)
  stage={'command':argv,'exit_code':r.returncode,'stdout':stdout.name,'stderr':stderr.name,'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)};rec['stages'].append(stage)
  assert r.returncode==0,stem+' failed'
 try:
  assert os.sched_getaffinity(0)==HELPERS,'exact housekeeping affinity required'
  clear=load(HERE/'execution-clearance.json');assert clear['parent_cleared'] and clear['pilot_actual_exit_code']==0
  plan=load(HERE/'plan.json');prep=load(HERE/'source-preparation.json');reference=load(Path(plan['native_build_reference']))
  assert reference['binary_output']['sha256']==plan['inherited_native_binary_sha256']
  native=source_snapshot(SOURCE);adapter=source_snapshot(SOURCE/'diagnostic');tools=tool_snapshot(SOURCE)
  assert native==prep['native_source_sha256']==reference['source_sha256_before']==reference['source_sha256_after']
  assert tools==prep['tool_source_sha256']==reference['tool_sha256_before']==reference['tool_sha256_after']
  assert adapter==prep['adapter_source_sha256'];assert len(native)==43 and len(tools)==23 and len(adapter)==30
  assert sha(HERE/prep['archive'])==prep['archive_sha256'] and sha(HERE/'run.py')==prep['planned_verifier_sha256']
  for path,digest in plan['native_reuse_evidence_sha256'].items():assert sha(Path(path))==digest
  units=load(Path(plan['native_unit_evidence']));assert units['complete'] and units['inputs_stable'] and sum(v['passed'] for v in units['units'].values())==142
  ordinary=load(Path(plan['ordinary_identity']));assert ordinary['complete'] and ordinary['inputs_stable'] and ordinary['strict_replays']==54 and ordinary['interruption_fixtures']==8 and ordinary['interruption_searches']==24 and ordinary['native_artifact_sha256']==plan['inherited_native_binary_sha256']
  for path,digest in plan['fixtures'].items():assert sha(Path(path))==digest
  dependencies=[HERE/n for n in ['paths.json','execution-clearance.json','plan.json','source-preparation.json','run.py','record_case.py','reconcile.py','prepared-source-closure.tar.gz','prepared-adapter.tar.gz','exact-inputs.tar.gz','fixture-inventory.json','whole-fixture-case-map.json']]
  dependencies += [SOURCE/'tools/build.py',SOURCE/'tools/archive_build.py',Path('/home/legolas/king-spec/conformance/run.mjs'),Path(plan['native_build_reference']),*map(Path,plan['native_reuse_evidence_sha256']),*map(Path,plan['fixtures'])]
  dep={str(p):sha(p) for p in dependencies}
  env=dict(os.environ,RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4',PYTHONDONTWRITEBYTECODE='1')
  before={'native':native,'adapter':adapter,'native_tools':tools,'dependencies':dep,'helper_affinity':sorted(os.sched_getaffinity(0)),'environment':{k:env[k] for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']}}
  write(out/'inputs-before.json',before)
  run(['cargo','test','--offline','--locked','--release','--no-run','--message-format=json','--manifest-path',str(SOURCE/'diagnostic/Cargo.toml')],'unit-build',env)
  artifacts=[]
  for line in (out/'unit-build.stdout').read_text().splitlines():
   item=json.loads(line)
   if item.get('reason')=='compiler-artifact' and item['profile']['test'] and item.get('executable'):artifacts.append(Path(item['executable']))
  assert len(artifacts)==1
  (out/'unit-bin').mkdir();test=out/'unit-bin/rook2-diag-exact';shutil.copy2(artifacts[0],test);test_sha=sha(test)
  run([str(test),'--test-threads=1'],'unit-tests',env)
  match=re.search(r'test result: ok\. (\d+) passed; 0 failed;',(out/'unit-tests.stdout').read_text());assert match and int(match[1])==126
  assert sha(test)==test_sha;rec['unit_binary_sha256']=test_sha
  assert source_snapshot(SOURCE)==native and source_snapshot(SOURCE/'diagnostic')==adapter
  run([sys.executable,str(SOURCE/'tools/build.py'),'--crate',str(SOURCE/'diagnostic'),'--bin','rook2-diag','--mode','generic','--output',str(build)],'build-driver',env)
  br=load(build/'receipt.json');frozen=build/'rook2-diag-exact';shutil.copy2(br['binary_output']['path'],frozen);adapter_sha=sha(frozen);assert adapter_sha==br['binary_output']['sha256']
  write(build/'tool-terminal.json',{'exit_code':0,'build_child_return_observed':True,'frozen_adapter_sha256':adapter_sha,'build_driver_stage':rec['stages'][-1]})
  run([sys.executable,str(SOURCE/'tools/archive_build.py'),str(build)],'archive',env)
  raw=out/'raw-cases';raw.mkdir();command=['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
  for fixture in plan['fixtures']:command += ['--fixtures',fixture]
  command += ['--',sys.executable,str(HERE/'record_case.py'),'--adapter',str(frozen),'--records',str(raw)]
  run(command,'conformance',env)
  report=load(out/'conformance.stdout');assert report['pass'] and len(report['results'])==6151 and not (out/'conformance.stderr').stat().st_size
  assert sha(frozen)==adapter_sha
  rec.update(complete=True,adapter_sha256=adapter_sha,cases=len(report['results']),units=126,operations=87)
 except BaseException as error:rec['failure']=f'{type(error).__name__}: {error}'
 finally:
  if before is not None:
   after={'native':source_snapshot(SOURCE),'adapter':source_snapshot(SOURCE/'diagnostic'),'native_tools':tool_snapshot(SOURCE),'dependencies':{p:sha(Path(p)) for p in before['dependencies']}}
   stable=all(before[k]==after[k] for k in after);rec['inputs_stable']=stable
   if not stable:rec.update(complete=False,failure='source/dependency changed')
   write(out/'inputs-after.json',after)
  rec['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(out/'verification.json',rec)
  write(out/'driver-terminal.json',{'exit_code':0 if rec['complete'] else 1,'complete':rec['complete'],'failure':rec['failure'],'verification_sha256':sha(out/'verification.json'),'scope':'untimed native-backed adapter verification only'})
 print(json.dumps({'output':str(out),'complete':rec['complete'],'failure':rec['failure'],'adapter_sha256':rec.get('adapter_sha256')}));return 0 if rec['complete'] else 1
if __name__=='__main__':sys.exit(main())
