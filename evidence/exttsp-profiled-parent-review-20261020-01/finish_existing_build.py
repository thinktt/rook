from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'exttsp-profiled-parent-review-20261020-01';W=Path('/home/legolas/rook2-work/imp2-exttsp-profiled-20261020-01')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
s=json.loads((E/'exttsp-profiled-selection-20261020-01/selection.json').read_text());base=s['baseline_files_sha256'];files={n:sha(W/n) for n in base}
assert len(files)==74 and [n for n in files if files[n]!=base[n]]==['tools/build.py']
assert all(sha(R/n)==h for n,h in base.items())
assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(s['selected_utc'])).total_seconds()<s['lane_seconds']
training=E/'bitplane-pin-summary-pgo-training-20261020-01';profile=training/'merged.profdata';record=training/'training.json'
baseline=json.loads((E/'bitplane-pin-summary-pgo-use-build-20261020-01/receipt.json').read_text())
assert sha(profile)==s['profile_sha256']
assert baseline['source_sha256_before']=={n:h for n,h in files.items() if not n.startswith('tools/')}
assert all(sha(Path(n))==h for n,h in baseline['pgo']['input_sha256_before'].items())
# Explicit same own57 source/profile use-only comparison, no new training claim.
freeze={'files':files,'source_sha256':baseline['source_sha256_before'],'tool_source_sha256':{n:h for n,h in files.items() if n.startswith('tools/')},'source_graph_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'work_root':str(W),'changed_existing_files':['tools/build.py'],'production_stays':57,'profile_policy':s['profile_policy']}
assert json.loads((P/'source-freeze.json').read_text())==freeze
B=E/'exttsp-profiled-pgo-use-build-20261020-01'
receipt=json.loads((B/'receipt.json').read_text());assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot'
assert receipt['source_sha256_before']|receipt['tool_sha256_before']==files
assert receipt['toolchain']==baseline['toolchain']
assert receipt['cargo_config_sha256_before']=={}
flags=receipt['rust_flags'];expected=['-C','target-cpu=x86-64','-C','profile-use='+str(profile),'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false']
assert flags==expected,flags
stderr=(B/'build.stderr').read_text()
def warning_block(text):
 start=text.index('warning:');end=text.index('     Running ',start);return text[start:end]
old_stderr=(E/'bitplane-pin-summary-pgo-use-build-20261020-01/build.stderr').read_text()
assert warning_block(stderr)==warning_block(old_stderr)
assert stderr.count('warning:')==3
assert 'no profile data' not in stderr.lower() and 'hash mismatch' not in stderr.lower() and 'out of date' not in stderr.lower()
for value in ['enable-ext-tsp-block-placement=true','ext-tsp-apply-without-profile=false','pgo-warn-missing-function']:
 assert value in stderr,value
image=Path(receipt['binary_output']['path']);assert sha(image)==receipt['binary_output']['sha256']
shutil.copyfile(image,B/'rook2-exact');(B/'rook2-exact').chmod(0o555)
put(B/'frozen-image.json',{'sha256':sha(B/'rook2-exact'),'bytes':(B/'rook2-exact').stat().st_size,'mode':'0o555','source_freeze_sha256':sha(P/'source-freeze.json'),'training':'own57 existing immutable profile; no fresh training','source_graph_sha256':freeze['source_graph_sha256']})
z=subprocess.run(['/usr/bin/python3',str(W/'tools/archive_build.py'),str(B)],cwd=W);assert z.returncode==0
assert all(sha(W/n)==h for n,h in files.items())
put(P/'build-acceptance.json',{'complete':True,'source51_exact57':True,'only_helper_changed':True,'same_toolchain':True,'compiler_warnings_identical_to_baseline57':True,'zero_missing_stale_profile_warnings':True,'profile_inputs_unchanged':receipt['pgo']['inputs_unchanged'],'flags':flags,'binary_sha256':sha(B/'rook2-exact'),'new_training_runs':0,'native_launch_authorized':False})
print('PGO_USE_ONLY_BUILD_CLOSED',sha(B/'rook2-exact'),flush=True)
