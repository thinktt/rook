from pathlib import Path
import json,hashlib,subprocess,os,shutil,datetime,difflib
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'deferred-capture-clear-parent-review-20261020-01';W=Path('/home/legolas/rook2-work/imp2-deferred-capture-clear-20261020-01')
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
s=json.loads((E/'deferred-capture-clear-selection-20261020-01/selection.json').read_text());base=s['baseline_source74_sha256'];files={n:sha((W/n).read_bytes()) for n in base}
assert len(files)==74 and all(sha((R/n).read_bytes())==h for n,h in base.items())
changed=sorted(n for n in base if base[n]!=files[n]);assert changed==sorted(s['source_scope']),changed
old=(R/'src/position.rs').read_text();new=(W/'src/position.rs').read_text();test_start=old.index('#[cfg(test)]');assert old[test_start:] in new,'All existing Position tests must remain literal'
assert 'if victim_square != to {' in new
patch=''.join(''.join(difflib.unified_diff((R/n).read_text().splitlines(True),(W/n).read_text().splitlines(True),fromfile='accepted57/'+n,tofile='candidate59/'+n)) for n in changed);(P/'source.patch').write_text(patch)
native={n:h for n,h in files.items() if not n.startswith('tools/')};tools={n:h for n,h in files.items() if n.startswith('tools/')}
# Use the established sorted JSON graph encoding.
graph=sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode())
freeze={'files':files,'source_sha256':native,'tool_source_sha256':tools,'source_graph_sha256':graph,'work_root':str(W),'changed_existing_files':changed,'added_files':[],'production_stays':57,'all_existing_position_tests_literal':True,'one_runtime_design':True}
put(P/'source-freeze.json',freeze)
B=E/'deferred-capture-clear-generic-build-20261020-01'
cmd=['/usr/bin/python3',str(W/'tools/build.py'),'--crate',str(W),'--mode','generic','--bin','rook2','--jobs','4','--output',str(B)]
z=subprocess.run(cmd,cwd=W);assert z.returncode==0
receipt=json.loads((B/'receipt.json').read_text());assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['source_sha256_before']|receipt['tool_sha256_before']==files
image=Path(receipt['binary_output']['path']);assert sha(image.read_bytes())==receipt['binary_output']['sha256'];shutil.copyfile(image,B/'rook2-exact');(B/'rook2-exact').chmod(0o555)
put(B/'frozen-image.json',{'sha256':sha((B/'rook2-exact').read_bytes()),'bytes':(B/'rook2-exact').stat().st_size,'mode':'0o555','source_graph':graph,'source_freeze_sha256':sha((P/'source-freeze.json').read_bytes())})
z=subprocess.run(['/usr/bin/python3',str(W/'tools/archive_build.py'),str(B)],cwd=W);assert z.returncode==0
T=E/'deferred-capture-clear-native-20261020-01';T.mkdir()
cmd=['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(W/'target/dev-generic'),'--manifest-path',str(W/'Cargo.toml'),'--lib','--','--test-threads=1']
env=os.environ.copy();env.update(RUSTC='/usr/bin/rustc',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',RUSTFLAGS='-C target-cpu=x86-64')
with (T/'stdout').open('xb') as out,(T/'stderr').open('xb') as err:z=subprocess.run(cmd,cwd=W,env=env,stdout=out,stderr=err)
assert all(sha((W/n).read_bytes())==h for n,h in files.items());assert sha((B/'rook2-exact').read_bytes())==receipt['binary_output']['sha256']
put(T/'proof.json',{'argv':cmd,'exit_code':z.returncode,'source74_unchanged':True,'source_freeze_sha256':sha((P/'source-freeze.json').read_bytes()),'stdout_sha256':sha((T/'stdout').read_bytes()),'stderr_sha256':sha((T/'stderr').read_bytes())})
print((T/'stdout').read_text()[-1600:]);assert z.returncode==0
print('GENERIC_BUILD_AND_LIB_TESTS_CLOSED',receipt['binary_output']['sha256'],graph,flush=True)
