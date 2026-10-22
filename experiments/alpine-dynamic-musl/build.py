#!/usr/bin/python3
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
B=Path('/work');S=B/'source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(S)):sha(p) for p in sorted(S.rglob('*')) if p.is_file()}
expected=json.loads((B/'source-map.json').read_text());assert snapshot()==expected
stage=sys.argv[1];assert stage in ('instrumented','use','repeat')
O=B/('build-'+stage);O.mkdir();target=B/('target-'+stage);assert not target.exists()
(B/'cargo-home').mkdir(exist_ok=True);(B/'artifacts').mkdir(exist_ok=True)
flags=['-C','target-cpu=x86-64','-C','target-feature=-crt-static']
if stage=='instrumented':
 raw=B/'profile-raw';raw.mkdir();flags+=['-C','profile-generate='+str(raw)]
else:
 training=json.loads((B/'training.json').read_text());assert training['complete']
 assert training['source']==expected and training['target']=='x86_64-unknown-linux-musl'
 assert training['profileSha256']==sha(B/'merged.profdata')
 flags+=['-C','profile-use=/work/merged.profdata','-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false']
env=dict(os.environ,CARGO_HOME='/work/cargo-home',CARGO_NET_OFFLINE='true',CARGO_INCREMENTAL='0',CARGO_BUILD_JOBS='4',RUSTUP_TOOLCHAIN='1.85.1-x86_64-unknown-linux-musl',RUSTFLAGS=' '.join(flags),CARGO_ENCODED_RUSTFLAGS='\x1f'.join(flags),SOURCE_DATE_EPOCH='1742256000')
cmd=['/usr/local/cargo/bin/cargo','build','--offline','--locked','--release','--verbose','--target','x86_64-unknown-linux-musl','--jobs','4','--target-dir',str(target),'--manifest-path',str(S/'Cargo.toml'),'--bin','rook2']
record={'schema':'rook2-alpine-dynamic-musl-build-v1','stage':stage,'argv':cmd,'cwd':str(S),'source_sha256_before':expected,'target_triple':'x86_64-unknown-linux-musl','rust_flags':flags,'environment':{k:env[k] for k in ['PATH','RUSTUP_HOME','CARGO_HOME','CARGO_NET_OFFLINE','CARGO_INCREMENTAL','RUSTUP_TOOLCHAIN','CARGO_ENCODED_RUSTFLAGS','SOURCE_DATE_EPOCH']},'toolchain':subprocess.check_output(['/usr/local/cargo/bin/rustc','-vV'],env=env,text=True),'affinity':sorted(os.sched_getaffinity(0))}
(O/'plan.json').write_text(json.dumps(record,indent=2)+'\n')
t=time.monotonic()
with (O/'stdout').open('xb') as a,(O/'stderr').open('xb') as z:cp=subprocess.run(cmd,cwd=S,env=env,stdout=a,stderr=z,timeout=300)
record.update(cargo_exit_code=cp.returncode,elapsedSeconds=time.monotonic()-t)
assert cp.returncode==0,(O/'stderr').read_text()[-12000:]
assert snapshot()==expected
log=(O/'stderr').read_text().lower()
for warning in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data','hash mismatch','unprofiled function']:
 assert warning not in log,warning
image=target/'x86_64-unknown-linux-musl/release/rook2';frozen=B/'artifacts'/('rook2-instrumented' if stage=='instrumented' else 'rook2-musl'+('-repeat' if stage=='repeat' else ''))
shutil.copy2(image,frozen);assert sha(image)==sha(frozen)
program=subprocess.check_output(['/usr/bin/readelf','-lW',str(frozen)],text=True)
dynamic=subprocess.check_output(['/usr/bin/readelf','-dW',str(frozen)],text=True)
assert '/lib/ld-musl-x86_64.so.1' in program,program
assert '(NEEDED)' in dynamic and 'libc.musl-x86_64.so.1' in dynamic,dynamic
(O/'elf-program.txt').write_text(program);(O/'elf-dynamic.txt').write_text(dynamic)
record.update(outcome='build-succeeded-with-stable-input-snapshot',source_sha256_after=snapshot(),binary_output={'path':str(frozen),'sha256':sha(frozen),'bytes':frozen.stat().st_size},dynamicMuslVerified=True)
(O/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'stage':stage,'binary':record['binary_output'],'dynamicMuslVerified':True}),flush=True)
