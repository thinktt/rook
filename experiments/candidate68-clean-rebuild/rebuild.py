#!/usr/bin/python3
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, time
parser=argparse.ArgumentParser(description='Rebuild candidate68 from preserved source and receipts; do not alter packaged artifacts.')
parser.add_argument('--output', required=True, type=Path, help='fresh absent raw-output directory outside the repository')
BASE=parser.parse_args().output.absolute()
assert not BASE.exists()
assert not BASE.is_relative_to(Path('/home/legolas/rook2'))
BASE.mkdir(parents=False)
PROD=Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01')
CORR=Path('/home/legolas/rook2-experiments/first-main-cutoff-correction-20261020-01')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=json.loads((PROD/'use-build/receipt.json').read_text())
plan=json.loads((CORR/'plan.json').read_text())
root=Path(receipt['crate'])
for name,h in (receipt['source_sha256_before']|receipt['tool_sha256_before']).items(): assert sha(root/name)==h,name
source_map=json.loads((CORR/'candidate-source-map.json').read_text())['files']
for name,value in source_map.items():
 expected=value if isinstance(value,str) else value['sha256']
 assert sha(root/name)==expected,name
for name,h in receipt['pgo']['input_sha256_before'].items(): assert sha(name)==h,name
for name in ('cargo','rustc'):
 assert sha(Path('/usr/bin')/name)==receipt['toolchain'][name+'_executable_sha256']
assert subprocess.check_output(['/usr/bin/rustc','-vV'],text=True)==receipt['toolchain']['rustc']['stdout']
assert not receipt['cargo_config_sha256_before']
for parent in [root,*root.parents,Path.home()]:
 for filename in ('config','config.toml'): assert not (parent/'.cargo'/filename).exists()
expected={'ordinary':'5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a','diagnostic':'68a1c304f76435e4c100086d1a303b8dc94d8b5ecd63d26be834e3737bca2dda'}
original_paths={'ordinary':PROD/'use-build/rook2-exact','diagnostic':CORR/'diagnostic-target/x86_64-unknown-linux-gnu/release/rook2-diag'}
for k,p in original_paths.items():assert sha(p)==expected[k]
results={}
for kind in ('ordinary','diagnostic'):
 out=BASE/kind;out.mkdir()
 target=out/'target';assert not target.exists()
 env=dict(os.environ)
 for key in list(env):
  if key.startswith(('CARGO_','RUST','LLVM_PROFILE','CFLAGS','CXXFLAGS','LDFLAGS')) or key in ('CC','CXX','AR'):env.pop(key)
 env.update(plan['environment'])
 if kind=='ordinary':
  argv=list(receipt['argv']);env.update(receipt['environment_overrides'])
 else:argv=list(plan['stages']['diagnostic-build']['argv'])
 argv[argv.index('--target-dir')+1]=str(target)
 data={'argv':argv,'cwd':str(root),'targetInitiallyAbsent':True,'environment':{k:env[k] for k in sorted(set(plan['environment'])|set(receipt['environment_overrides'])) if k in env},'affinity':sorted(os.sched_getaffinity(0)),'startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceFilesVerified':len(source_map),'ownProfileReused':kind=='ordinary','pgoTrainingRuns':0}
 (out/'plan.json').write_text(json.dumps(data,indent=2)+'\n')
 t=time.monotonic()
 with (out/'stdout').open('xb') as so,(out/'stderr').open('xb') as se:
  cp=subprocess.run(argv,cwd=root,env=env,stdout=so,stderr=se,timeout=300)
 data.update(returncode=cp.returncode,elapsedSeconds=time.monotonic()-t)
 if cp.returncode==0:
  binary=target/'x86_64-unknown-linux-gnu/release'/('rook2' if kind=='ordinary' else 'rook2-diag')
  data.update(binary=str(binary),sha256=sha(binary),bytes=binary.stat().st_size,expectedSha256=expected[kind],exactMatch=sha(binary)==expected[kind])
 (out/'result.json').write_text(json.dumps(data,indent=2)+'\n')
 results[kind]=data
 print(json.dumps({'kind':kind,**{k:v for k,v in data.items() if k in ('returncode','elapsedSeconds','sha256','bytes','exactMatch')}}),flush=True)
 if cp.returncode!=0:break
for name,value in source_map.items():assert sha(root/name)==(value if isinstance(value,str) else value['sha256']),name
for kind,path in original_paths.items():assert sha(path)==expected[kind]
summary={'schema':'candidate68-clean-rebuild-v1','results':results,'originalImagesAndSourceUnchanged':True,'engineExecutions':0,'sourceLocationReused':str(root),'buildDirectoriesFresh':True,'binaryPromotion':False}
(BASE/'result.json').write_text(json.dumps(summary,indent=2)+'\n')
