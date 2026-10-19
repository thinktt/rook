from pathlib import Path
import json,hashlib,os,subprocess,datetime,sys
R=Path('/home/legolas/rook2');E=R/'evidence';O=Path(__file__).resolve().parent
W=Path('/home/legolas/rook2-work/imp2-coherent-influence-masks-20261019-01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')
f=json.loads((E/'coherent-influence-masks-parent-review-20261019-01/source-freeze.json').read_text())
def check():
 assert {p:sha(W/p) for p in f['files_sha256']}==f['files_sha256']
 return True
assert check() and set(os.sched_getaffinity(0))=={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ['PATH']=='/usr/bin:/bin'
x=json.loads((E/'coherent-influence-masks-pgo-cpu-pilot-20261019-01/independent-reconciliation.json').read_text());assert x['advance_under_declared_rule']
b=json.loads((E/'coherent-influence-masks-generic-build-20261019-01/receipt.json').read_text())
env=os.environ.copy();env.update(b['environment_overrides']);env['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUNNER']='taskset -c 14'
cmd=['/usr/bin/cargo','test','--offline','--locked','--release','--target',b['target_triple'],'--jobs','4','--target-dir',b['target_directory'],'--manifest-path',str(W/'Cargo.toml'),'--lib','--bin','rook2-dev','--','--test-threads=1']
save(O/'command.json',dict(command=cmd,environment_overrides=b['environment_overrides'],native_runner=env['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUNNER'],source72_graph='568e87374b41ac30aabf5f1222ba5375d9426b5c263c0c9c49486be5753c8c2f',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
with (O/'stdout').open('xb') as o,(O/'stderr').open('xb') as e:
 child=subprocess.Popen(cmd,cwd=W,env=env,stdout=o,stderr=e);code=child.wait()
t=(O/'stdout').read_text();unchanged=check();ok=code==0 and unchanged and 'test result: ok. 183 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;' in t and 'test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;' in t
save(O/'result.json',dict(complete=ok,exit_code=code,pid=child.pid,source_unchanged=unchanged,library_passed=183 if ok else None,development_passed=2 if ok else None,total_passed=185 if ok else None,logs={p:sha(O/p) for p in ['stdout','stderr']},scope='All native tests on source37 generic lib/development builds; no PGO test-binary claim. Frozen PGO37 image unchanged.'))
print(json.dumps(dict(complete=ok,exit_code=code,total_passed=185 if ok else None)));sys.exit(0 if ok else 1)
