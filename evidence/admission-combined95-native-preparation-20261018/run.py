#!/usr/bin/env python3
"""Authorized native151/build/archive/codegen only; no strict/DIAG execution."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'plan.json').read_text())
SOURCE=Path(PLAN['validation_copy'])
OUT=Path(PLAN['output']); BUILD=Path(PLAN['build']); CODEGEN=Path(PLAN['codegen'])
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def source_snapshot(root):
 files=[root/'Cargo.toml',root/'Cargo.lock']+sorted(p for p in (root/'src').rglob('*') if p.is_file())
 for f in ['build.rs','rust-toolchain','rust-toolchain.toml']:
  if (root/f).is_file():files.append(root/f)
 return {str(p.relative_to(root)):sha(p) for p in files}
def tools_snapshot(root):
 return {str(p.relative_to(root)):sha(p) for p in sorted((root/'tools').rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py','.c','.rs','.md','.sh','.mjs']}
def run(argv,stem,env):
 stdout,stderr=OUT/(stem+'.stdout'),OUT/(stem+'.stderr')
 with stdout.open('xb') as a,stderr.open('xb') as b:r=subprocess.run(argv,cwd=SOURCE,env=env,stdout=a,stderr=b)
 stage=dict(command=argv,exit_code=r.returncode,stdout_sha256=sha(stdout),stderr_sha256=sha(stderr))
 receipt['stages'].append(stage)
 assert r.returncode==0,stem+' failed'
 return stage
assert os.sched_getaffinity(0)==HELPERS,'helper affinity must be exact'
clearance=json.loads((HERE/'clearance.json').read_text())
assert clearance['measurement_clear'] and clearance['pilot_exit_code']==0,'explicit parent clearance missing'
assert not OUT.exists() and not BUILD.exists() and not CODEGEN.exists(),'preserve original attempts; use a new plan/output for a retry'
prepared=json.loads((HERE/'prepared.json').read_text())
reference_path=Path(PLAN['native_build_reference']);reference=json.loads(reference_path.read_text())
native_before=source_snapshot(SOURCE); tools_before=tools_snapshot(SOURCE); frontend_before=source_snapshot(SOURCE/'diagnostic')
assert native_before==prepared['variant_source_sha256'] and len(native_before)==43
assert tools_before==prepared['tools_sha256']==reference['tool_sha256_before'] and len(tools_before)==23
assert frontend_before==prepared['frontend_sha256']
assert sha(HERE/prepared['source_archive'])==prepared['source_archive_sha256']
assert reference['binary_output']['sha256']==PLAN['expected_reference_binary_sha256']
reference_binary=reference_path.parent/'rook2-exact'
assert sha(reference_binary)==PLAN['expected_reference_binary_sha256']
dependencies=[HERE/f for f in ['run.py','check_native.py','capture_codegen.py','analyze_codegen.py','plan.json','prepared.json','clearance.json','prepared-source.tar.gz','driver-source-manifest.json']]+[reference_path,reference_binary]
before={str(p):sha(p) for p in dependencies}
OUT.mkdir()
env=dict(os.environ,RUSTC='/usr/bin/rustc',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4',PYTHONDONTWRITEBYTECODE='1')
write(OUT/'inputs-before.json',dict(native=native_before,tools=tools_before,frontend=frontend_before,dependencies=before,helper_affinity=sorted(os.sched_getaffinity(0)),environment={k:env[k] for k in ['RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']},clearance=clearance))
receipt=dict(complete=False,failure=None,stages=[],scope=PLAN['scope'],codegen_gate='pending-manual-review')
try:
 run([sys.executable,str(HERE/'check_native.py')],'native-tests-driver',env)
 tests=json.loads((OUT/'native-verification.json').read_text())
 assert tests['complete'] and tests['inputs_stable'] and sum(v['passed'] for v in tests['units'].values())==151
 run([sys.executable,str(SOURCE/'tools/build.py'),'--crate',str(SOURCE),'--mode','generic','--bin','rook2','--output',str(BUILD)],'native-build-driver',env)
 build=json.loads((BUILD/'receipt.json').read_text())
 assert build['source_identity_unchanged'] and build['pgo']['mode']=='none'
 assert build['source_sha256_before']==build['source_sha256_after']==native_before
 assert build['tool_sha256_before']==build['tool_sha256_after']==tools_before
 frozen=BUILD/'rook2-exact';shutil.copy2(build['binary_output']['path'],frozen)
 assert sha(frozen)==build['binary_output']['sha256']
 receipt['native_binary_sha256']=sha(frozen)
 run([sys.executable,str(SOURCE/'tools/archive_build.py'),str(BUILD)],'native-archive',env)
 CODEGEN.mkdir()
 run([sys.executable,str(HERE/'capture_codegen.py')],'codegen-capture',env)
 run([sys.executable,str(HERE/'analyze_codegen.py')],'codegen-analysis',env)
 receipt['codegen_gate']=json.loads((CODEGEN/'manual-gate.json').read_text())['status']
 receipt['complete']=True
except BaseException as error:
 receipt['failure']=f'{type(error).__name__}: {error}'
finally:
 native_after,tools_after,frontend_after=source_snapshot(SOURCE),tools_snapshot(SOURCE),source_snapshot(SOURCE/'diagnostic')
 after={str(p):sha(p) for p in dependencies}
 stable=native_before==native_after and tools_before==tools_after and frontend_before==frontend_after and before==after
 receipt['inputs_stable']=stable
 if not stable:receipt.update(complete=False,failure='source/tool/frontend/dependency drift')
 write(OUT/'inputs-after.json',dict(native=native_after,tools=tools_after,frontend=frontend_after,dependencies=after))
 receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 write(OUT/'native-pipeline.json',receipt)
print(json.dumps(dict(complete=receipt['complete'],failure=receipt['failure'],codegen_gate=receipt['codegen_gate'],output=str(OUT))))
raise SystemExit(0 if receipt['complete'] else 1)
