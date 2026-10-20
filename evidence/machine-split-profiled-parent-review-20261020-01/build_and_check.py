from pathlib import Path
import json,hashlib,subprocess,shutil,importlib.util
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'machine-split-profiled-parent-review-20261020-01';W=Path('/home/legolas/rook2-work/imp2-machine-split-profiled-20261020-01');Q=E/'machine-split-profiled-recipe-20261020-01';B=E/'machine-split-profiled-pgo-use-build-20261020-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
baseline=json.loads((E/'exttsp-profiled-pgo-use-build-20261020-01/receipt.json').read_text());base=baseline['source_sha256_after']|baseline['tool_sha256_after']
assert len(base)==74 and all(sha(R/n)==h for n,h in base.items())
after=json.loads((Q/'source-after.json').read_text());before=json.loads((Q/'source-before.json').read_text());assert before==base
spec=importlib.util.spec_from_file_location('candidate63_build',W/'tools/build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
actual=mod.source_snapshot(W)|mod.tool_snapshot(W)
assert actual==after and set(actual)==set(base) and [n for n in base if actual[n]!=base[n]]==['tools/build.py']
assert sha(W/'tools/build.py')=='c1f4057003bc1073b6a51d17e259930ea935ace0a546fb0cf5615786b0589050'
checks=json.loads((Q/'dry-run-verification.json').read_text());assert checks['complete'] and checks['metadata_shim_or_mock'] is False and checks['Cargo_builds']==checks['engine_runs']==0
for row in checks['dry_runs']:
 assert row['exit_code']==row['expected_exit'] and row['child_reaped'] and row['failure'] is None
 for stream in ['stdout','stderr']:assert sha(Q/(row['label']+'.'+stream))==row[stream+'_sha256']
profile=E/'bitplane-pin-summary-pgo-training-20261020-01/merged.profdata';training=profile.parent/'training.json'
assert sha(profile)=='b4806420937681c8228903507018233d7176be0333ef98881a73d34c66df3a5c'
for path,h in baseline['pgo']['input_sha256_after'].items():assert sha(Path(path))==h,path
freeze={'files':actual,'source_sha256':mod.source_snapshot(W),'tool_source_sha256':mod.tool_snapshot(W),'source_graph_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'baseline_source74_graph':'9729230374cb947d3e469140f634b670edf4df6ae87d9af4ab394f5bbc4e9cd0','changed_existing_files':['tools/build.py'],'native_source51_exact62':True,'work_root':str(W),'profile_policy':'same immutable own57 profile use-only, no new training','production_stays':62}
save(P/'source-freeze.json',freeze)
save(P/'recipe-parent-acceptance.json',{'complete':True,'dryrun_checks':10,'exact_recorded_streams_rehashed':True,'only_helper_changed':True,'source74_graph':freeze['source_graph_sha256'],'native_source_unchanged':True,'build_authorized':True,'engine_timing_authorized':False,'known_warnings_policy':'Require exact existing62 compiler warning block; reject any new/missing/stale profile diagnostics.'})
assert not B.exists()
command=['/usr/bin/python3',str(W/'tools/build.py'),'--crate',str(W),'--mode','generic','--bin','rook2','--jobs','4','--pgo-use',str(profile),'--training-record',str(training),'--ext-tsp-profiled','--machine-split-profiled','--output',str(B)]
result=subprocess.run(command,cwd=W);save(P/'build-command.json',{'argv':command,'actual_child_exit_observed':True,'exit_code':result.returncode});assert result.returncode==0
receipt=json.loads((B/'receipt.json').read_text());assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['cargo_exit_code']==0
assert receipt['source_sha256_before']==receipt['source_sha256_after']==freeze['source_sha256']
assert receipt['tool_sha256_before']==receipt['tool_sha256_after']==freeze['tool_source_sha256']
assert receipt['toolchain']==baseline['toolchain'] and receipt['cargo_config_sha256_before']==receipt['cargo_config_sha256_after']=={}
expected=['-C','target-cpu=x86-64','-C','profile-use='+str(profile),'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false -enable-split-machine-functions=true']
assert receipt['rust_flags']==expected and receipt['environment_overrides']['CARGO_ENCODED_RUSTFLAGS'].split(chr(31))==expected
assert receipt['pgo']['inputs_unchanged'] and receipt['pgo']['input_sha256_before']==receipt['pgo']['input_sha256_after']==baseline['pgo']['input_sha256_after']
stderr=(B/'build.stderr').read_text();old=(E/'exttsp-profiled-pgo-use-build-20261020-01/build.stderr').read_text()
def warning_block(t):
 start=t.index('warning:');end=t.index('     Running ',start);return t[start:end]
assert warning_block(stderr)==warning_block(old) and stderr.count('warning:')==old.count('warning:')
assert not any(value in stderr.lower() for value in ['no profile data','hash mismatch','out of date'])
assert all(value in stderr for value in expected[-1].removeprefix('llvm-args=').split())
image=Path(receipt['binary_output']['path']);assert sha(image)==receipt['binary_output']['sha256']
shutil.copyfile(image,B/'rook2-exact');(B/'rook2-exact').chmod(0o555)
save(B/'frozen-image.json',{'sha256':sha(B/'rook2-exact'),'bytes':(B/'rook2-exact').stat().st_size,'mode':'0o555','source_freeze_sha256':sha(P/'source-freeze.json'),'source_graph_sha256':freeze['source_graph_sha256'],'new_training_runs':0,'profile_policy':freeze['profile_policy']})
result=subprocess.run(['/usr/bin/python3',str(W/'tools/archive_build.py'),str(B)],cwd=W);assert result.returncode==0
assert mod.source_snapshot(W)|mod.tool_snapshot(W)==actual
for n,h in base.items():assert sha(R/n)==h,n
save(P/'build-acceptance.json',{'complete':True,'native_source51_exact62':True,'only_helper_changed':True,'same_toolchain':True,'known_compiler_warnings_identical_to62':True,'zero_new_missing_stale_profile_diagnostics':True,'profile_inputs_unchanged':True,'flags':expected,'binary_sha256':sha(B/'rook2-exact'),'new_training_runs':0,'native_launch_authorized':False,'emitted_code_mechanism_still_pending':True})
print('PGO_USE_ONLY63_BUILD_CLOSED',sha(B/'rook2-exact'),flush=True)
