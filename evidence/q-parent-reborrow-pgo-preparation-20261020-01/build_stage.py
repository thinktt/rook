"""Future generic instrumented/use build, freeze and archive; no training."""
import argparse,os,shutil,sys
from guard import *

def main():
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['instrumented','use']);stage=a.parse_args().stage
 require_clearance()
 train=Path(PLAN['training']);out=Path(PLAN['instrumented_build' if stage=='instrumented' else 'use_build'])
 assert not out.exists() and not out.is_symlink()
 assert not (SOURCE/'target'/('dev-generic-pgo-generate' if stage=='instrumented' else 'dev-generic-pgo-use')).exists()
 command=[sys.executable,str(ROOT/'tools/build.py'),'--crate',str(SOURCE),'--mode','generic','--bin','rook2','--jobs','4','--output',str(out)]
 assert sha(ROOT/'tools/build.py')==PLAN['tool_source_sha256']['tools/build.py']
 if stage=='instrumented':
  assert not train.exists() # Separate raw root remains absent; build.py creates it.
  command+=['--pgo-generate',str(Path(PLAN['profile_raw']))]
 else:
  terminal(train/'tool-terminal.json');terminal(train/'verify-tool-terminal.json')
  t=load(train/'training.json');v=load(train/'verification.json')
  assert t['complete'] and v['complete'] and v['independent_remerge_byte_identical'] and v['original_checkReplay_count']==54 and v['raw_training_protocol_cases']==54
  assert sha(train/'merged.profdata')==t['profile_sha256']==v['merged_profile_sha256']
  command+=['--pgo-use',str(train/'merged.profdata'),'--training-record',str(train/'training.json'),'--ext-tsp-profiled']
 run(command,HERE/(stage+'-build'),env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 r=load(out/'receipt.json')
 assert r['outcome']=='build-succeeded-with-stable-input-snapshot' and r['cargo_exit_code']==0
 assert r['source_sha256_before']==r['source_sha256_after']==PLAN['engine_source_sha256']
 assert r['tool_sha256_before']==r['tool_sha256_after']==PLAN['tool_source_sha256']
 assert r['cargo_config_sha256_before']==r['cargo_config_sha256_after']==PLAN['cargo_config_sha256']
 assert r['toolchain']==PLAN['toolchain'] and r['mode']=='generic' and r['target_cpu']=='x86-64' and r['target_triple']==PLAN['target_triple'] and r['jobs']==4
 expected=PLAN['base_flags']+(['-C',f"profile-generate={Path(PLAN['profile_raw'])}"] if stage=='instrumented' else ['-C',f"profile-use={train/'merged.profdata'}",'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false'])
 assert r['rust_flags']==expected
 effective=check_thin_build(out,'instrumented' if stage=='instrumented' else 'profile-use')
 warning=(out/'build.stderr').read_text().lower()
 for x in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data','hash mismatch','unprofiled function']:
  assert x not in warning,x
 frozen=out/'rook2-exact';assert not frozen.exists();shutil.copy2(r['binary_output']['path'],frozen)
 assert sha(frozen)==r['binary_output']['sha256']
 run([sys.executable,str(ROOT/'tools/archive_build.py'),str(out)],HERE/(stage+'-archive'))
 ar=load(out/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and ar['binary_sha256']==sha(frozen) and sha(out/ar['archive'])==ar['sha256']
 check_inputs()
 write(HERE/(stage+'-stage.json'),dict(complete=True,artifact_sha256=sha(frozen),receipt_sha256=sha(out/'receipt.json'),archive_receipt_sha256=sha(out/'archive-receipt.json'),missing_or_stale_profile_warnings=0,effective_rustc_options=effective))
if __name__=='__main__':main()
