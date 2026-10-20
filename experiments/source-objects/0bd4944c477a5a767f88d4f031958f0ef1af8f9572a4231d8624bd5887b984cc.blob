#!/usr/bin/env python3
"""Build/freeze/archive once, after parent clearance; no training in this helper."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
from guard import HERE,load,sha,require_clearance,terminal

def main():
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['instrumented','use']);args=a.parse_args();require_clearance();terminal(HERE/'readiness-tool-terminal.json')
 plan=load(HERE/'plan.json');assert load(HERE/'readiness.json')['complete'];source=Path(plan['source_root']);train=Path(plan['training']);out=Path(plan['instrumented_build' if args.stage=='instrumented' else 'use_build'])
 assert not out.exists() and not out.is_symlink();sys.dont_write_bytecode=True;sys.path.insert(0,str(source/'tools'));from build import source_snapshot,tool_snapshot
 assert source_snapshot(source)==plan['engine_source_sha256'] and tool_snapshot(source)==plan['tool_source_sha256']
 command=[sys.executable,str(source/'tools/build.py'),'--crate',str(source),'--mode','generic','--bin','rook2','--jobs','4','--output',str(out)]
 if args.stage=='instrumented':
  assert not (train/'raw').exists();command+=['--pgo-generate',str(train/'raw')]
 else:
  terminal(train/'tool-terminal.json');terminal(train/'verify-tool-terminal.json');training=load(train/'training.json');verified=load(train/'verification.json')
  assert verified['complete'] and verified['independent_remerge_byte_identical'] and training['complete'] and sha(train/'merged.profdata')==training['profile_sha256']==verified['merged_profile_sha256']
  command+=['--pgo-use',str(train/'merged.profdata'),'--training-record',str(train/'training.json')]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('LLVM_PROFILE_FILE',None)
 result=dict(complete=False,stage=args.stage,command=command,failure=None,stages=[])
 try:
  for argv,stem in [(command,args.stage+'-build')]:
   with (HERE/(stem+'.stdout')).open('xb') as a,(HERE/(stem+'.stderr')).open('xb') as b:child=subprocess.run(argv,cwd=source,env=env,stdout=a,stderr=b)
   result['stages'].append(dict(command=argv,actual_child_return_observed=True,exit_code=child.returncode));assert child.returncode==0,'build failed'
  receipt=load(out/'receipt.json');assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['source_sha256_before']==receipt['source_sha256_after']==plan['engine_source_sha256'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']==plan['tool_source_sha256']
  control=load(HERE.parent/'pgo-ordered-bit-checkers-phase1-use-build-20261018/receipt.json');assert receipt['toolchain']==control['toolchain'];assert all(receipt[k]==control[k] for k in ['target_triple','target_cpu','mode','jobs','cargo_config_sha256_before'])
  assert receipt['rust_flags'][:2]==plan['base_flags'];frozen=out/'rook2-exact';assert not frozen.exists();shutil.copy2(receipt['binary_output']['path'],frozen);assert sha(frozen)==receipt['binary_output']['sha256']
  warnings=(out/'build.stderr').read_text().lower();assert not any(x in warnings for x in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data'])
  archive=[sys.executable,str(source/'tools/archive_build.py'),str(out)]
  with (HERE/(args.stage+'-archive.stdout')).open('xb') as a,(HERE/(args.stage+'-archive.stderr')).open('xb') as b:child=subprocess.run(archive,cwd=source,env=env,stdout=a,stderr=b)
  result['stages'].append(dict(command=archive,actual_child_return_observed=True,exit_code=child.returncode));assert child.returncode==0
  assert source_snapshot(source)==plan['engine_source_sha256'] and tool_snapshot(source)==plan['tool_source_sha256'];result.update(complete=True,artifact_sha256=sha(frozen),receipt_sha256=sha(out/'receipt.json'),archive_receipt_sha256=sha(out/'archive-receipt.json'),missing_or_stale_profile_warnings=0)
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 finally:
  with (HERE/(args.stage+'-stage.json')).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
