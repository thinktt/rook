from pathlib import Path
import json,hashlib,subprocess,os,shutil,difflib
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'deferred-capture-clear-parent-review-20261020-01';W=Path('/home/legolas/rook2-work/imp2-deferred-capture-clear-20261020-01')
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
old=json.loads((P/'source-freeze.json').read_text());files={n:sha((W/n).read_bytes()) for n in old['files']};changed=[n for n,h in old['files'].items() if files[n]!=h];assert changed==['src/position.rs'],changed
oldtest=(E/'deferred-capture-clear-generic-build-20261020-01/source-before/src/position.rs').read_text();newtest=(W/'src/position.rs').read_text();assert newtest==oldtest.replace('fen.push(piece.fen());','fen.push(piece.fen_char());',1),'Only test-only helper spelling may change'
assert oldtest[:oldtest.index('#[cfg(test)]')]==newtest[:newtest.index('#[cfg(test)]')]
(P/'test-correction.patch').write_text(''.join(difflib.unified_diff(oldtest.splitlines(True),newtest.splitlines(True),fromfile='initial59/position.rs',tofile='corrected59/position.rs')))
freeze=dict(old);freeze.update(files=files,source_sha256={n:h for n,h in files.items() if not n.startswith('tools/')},source_graph_sha256=sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode()),test_admission_correction_only=True,initial_source_freeze_sha256=sha((P/'source-freeze.json').read_bytes()));put(P/'source-freeze-after-test-correction.json',freeze)
T=E/'deferred-capture-clear-native-test-corrected-20261020-01';T.mkdir();cmd=['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(W/'target/dev-generic'),'--manifest-path',str(W/'Cargo.toml'),'--lib','--','--test-threads=1']
env=os.environ.copy();env.update(RUSTC='/usr/bin/rustc',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',RUSTFLAGS='-C target-cpu=x86-64')
with (T/'stdout').open('xb') as out,(T/'stderr').open('xb') as err:z=subprocess.run(cmd,cwd=W,env=env,stdout=out,stderr=err)
put(T/'proof.json',{'argv':cmd,'exit_code':z.returncode,'source74_unchanged':all(sha((W/n).read_bytes())==h for n,h in files.items()),'source_freeze_sha256':sha((P/'source-freeze-after-test-correction.json').read_bytes()),'stdout_sha256':sha((T/'stdout').read_bytes()),'stderr_sha256':sha((T/'stderr').read_bytes())});print((T/'stdout').read_text()[-500:]);assert z.returncode==0
B=E/'deferred-capture-clear-generic-build-test-corrected-20261020-01';cmd=['/usr/bin/python3',str(W/'tools/build.py'),'--crate',str(W),'--mode','generic','--bin','rook2','--jobs','4','--output',str(B)];z=subprocess.run(cmd,cwd=W);assert z.returncode==0
receipt=json.loads((B/'receipt.json').read_text());assert receipt['source_sha256_before']|receipt['tool_sha256_before']==files
image=Path(receipt['binary_output']['path']);initial=E/'deferred-capture-clear-generic-build-20261020-01/rook2-exact';assert image.read_bytes()==initial.read_bytes(),'Test-only correction must preserve ordinary image bytes'
shutil.copyfile(image,B/'rook2-exact');(B/'rook2-exact').chmod(0o555)
put(B/'frozen-image.json',{'sha256':sha(image.read_bytes()),'bytes':image.stat().st_size,'mode':'0o555','source_graph':freeze['source_graph_sha256'],'source_freeze_sha256':sha((P/'source-freeze-after-test-correction.json').read_bytes()),'byte_identical_to_initial_generic':True})
z=subprocess.run(['/usr/bin/python3',str(W/'tools/archive_build.py'),str(B)],cwd=W);assert z.returncode==0
assert all(sha((W/n).read_bytes())==h for n,h in files.items())
put(P/'test-correction-acceptance.json',{'complete':True,'initial_failure_terminal':'57e7ca/1','only_changed_file_from_initial':changed,'runtime_source_files_unchanged':True,'ordinary_image_byte_identical':True,'image_sha256':sha(image.read_bytes()),'final_source_graph':freeze['source_graph_sha256'],'performance_source_designs':1,'native_measurements_before_correction':0,'performance_retries':0,'reason':'Correct only new cfg(test)helper method spelling fen tofen_char; no runtime or oracle/formula change.'})
print('CORRECTED196_LIB_PASS_ORDINARY_BYTE_EQUAL',sha(image.read_bytes()),freeze['source_graph_sha256'],flush=True)
