#!/usr/bin/env python3
"""Bounded existing-image identity closure only; never invokes Cargo/build."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/legolas/rook2/evidence')
OLD=ROOT/'full-evaluation-phase-sharing-native-validation-20261018-01'
PRE=ROOT/'full-evaluation-phase-sharing-preparation-20261018-01'
BUILD=ROOT/'full-evaluation-phase-sharing-generic-build-20261018-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(p,d):
 with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def main():
 result=dict(complete=False,failure=None,source_and_tools_unchanged=False,total_tests=0,tests={},commands=[],scope='Existing Cargo-built frozen-image identity repeat, not new unique test coverage',original_cargo178_unchanged=True)
 try:
  affinity=sorted(os.sched_getaffinity(0));assert affinity==[0,1,2,3,4,5,8,9,10,11,12,13]
  assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
  binding=load(PRE/'execution-binding.json');review=load(PRE/'parent-source-review.json');receipt=load(BUILD/'receipt.json')
  source=Path(receipt['crate']);pins=binding['source69'];assert len(pins)==69 and binding['parent_source_review_complete'] and review['accepted'] and review['source69']==pins
  assert receipt['source_sha256_before']==receipt['source_sha256_after']=={k:v for k,v in pins.items() if not k.startswith('tools/')}
  assert receipt['tool_sha256_before']==receipt['tool_sha256_after']=={k:v for k,v in pins.items() if k.startswith('tools/')}
  assert receipt['mode']=='generic' and receipt['pgo']['mode']=='none' and receipt['rust_flags']==['-C','target-cpu=x86-64']
  inputs=[PRE/'execution-binding.json',PRE/'parent-source-review.json',PRE/'validate.py',BUILD/'receipt.json']+[OLD/name for name in ['native-tests-launch.json','native-tests-terminal.json','native-tests.stdout','native-tests.stderr','result.json']]
  input_pins={str(p):sha(p) for p in inputs}
  before={name:sha(source/name) for name in pins};assert before==pins
  old=load(OLD/'result.json');terminal=load(OLD/'native-tests-terminal.json');launch=load(OLD/'native-tests-launch.json')
  assert old['complete'] and old['stable_source_and_inputs'] and terminal['exit_code']==0 and terminal['pid']==launch['pid']
  assert terminal['stdout_sha256']==sha(OLD/'native-tests.stdout') and terminal['stderr_sha256']==sha(OLD/'native-tests.stderr')
  assert load(PRE/'execution-binding.json')['driver_sha256']==sha(PRE/'validate.py')
  assert len(re.findall(r'^test .* \.\.\. ok$',(OLD/'native-tests.stdout').read_text(),re.M))==178
  # Cargo printed relative executable paths; its recorded --target-dir and
  # actual validate.py Popen(cwd=TRIAL) identify the absolute paths unambiguously.
  target=Path(launch['command'][launch['command'].index('--target-dir')+1]);assert target==source/'target/native-tests-generic-01'
  assert 'cwd=TRIAL' in (PRE/'validate.py').read_text()
  paths=re.findall(r'^\s*Running unittests (src/[^ ]+) \(([^)]+)\)$',(OLD/'native-tests.stderr').read_text(),re.M)
  assert {name for name,p in paths}=={'src/lib.rs','src/bin/rook2-dev.rs'} and len(paths)==2
  provenance={};expected={'lib':176,'dev':2}
  for name,printed in paths:
   kind='lib' if name=='src/lib.rs' else 'dev';original=Path(printed)
   if not original.is_absolute():original=source/original
   original=original.resolve(strict=True);assert original.is_relative_to(target.resolve()) and original.is_file() and not original.is_symlink()
   identity=sha(original);frozen=HERE/('rook2-'+kind+'-tests-exact');assert not frozen.exists();shutil.copy2(original,frozen);assert sha(original)==sha(frozen)==identity
   provenance[kind]=dict(cargo_source=name,cargo_printed_path=printed,cargo_resolved_executable=str(original),frozen_path=str(frozen),sha256=identity,bytes=frozen.stat().st_size)
  write(HERE/'source69-before.json',before);write(HERE/'input-pins-before.json',input_pins);write(HERE/'frozen-image-provenance.json',provenance)
  result.update(source=str(source),source69_sha256=pins,affinity=affinity,TMPDIR=os.environ['TMPDIR'],generic_image_sha256=receipt['binary_output']['sha256'],compiler_settings=receipt['toolchain'])
  for kind in ['lib','dev']:
   row=provenance[kind];frozen=Path(row['frozen_path']);original=Path(row['cargo_resolved_executable']);assert sha(frozen)==sha(original)==row['sha256']
   assert {name:sha(source/name) for name in pins}==before
   command=[str(frozen),'--test-threads=1']
   with (HERE/(kind+'-tests.stdout')).open('xb') as out,(HERE/(kind+'-tests.stderr')).open('xb') as err:
    child=subprocess.Popen(command,cwd=source,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
    observed_affinity=sorted(os.sched_getaffinity(child.pid))
    write(HERE/(kind+'-launch.json'),dict(command=command,pid=child.pid,cwd=str(source),affinity=observed_affinity,image_sha256_before=row['sha256']))
    code=child.wait()
   record=dict(command=command,pid=child.pid,cwd=str(source),affinity=observed_affinity,exit_code=code,actual_child_return_observed=True,stdout_sha256=sha(HERE/(kind+'-tests.stdout')),stderr_sha256=sha(HERE/(kind+'-tests.stderr')),image_sha256_before=row['sha256'],image_sha256_after=sha(frozen),original_image_sha256_after=sha(original))
   result['commands'].append(record);write(HERE/(kind+'-terminal.json'),record)
   assert code==0 and observed_affinity==affinity and record['image_sha256_after']==record['original_image_sha256_after']==row['sha256']
   text=(HERE/(kind+'-tests.stdout')).read_text();count=expected[kind]
   assert len(re.findall(r'^test .* \.\.\. ok$',text,re.M))==count and f'test result: ok. {count} passed; 0 failed;' in text
   assert (HERE/(kind+'-tests.stderr')).read_bytes()==b''
   result['tests'][kind]=dict(passed=count,sha256=row['sha256'],frozen_executable=str(frozen),original_executable=str(original),pid=child.pid,actual_exit_code=code)
   result['total_tests']+=count
  after={name:sha(source/name) for name in pins};assert after==before==pins
  assert {p:sha(p) for p in input_pins}==input_pins
  write(HERE/'source69-after.json',after);write(HERE/'input-pins-after.json',input_pins)
  result.update(complete=True,source_and_tools_unchanged=True,total_tests=178,source69_count=69,original_inputs_unchanged=True)
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 finally:write(HERE/'result.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ['source69_sha256','compiler_settings','commands']}))
 return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
