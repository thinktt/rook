#!/usr/bin/env python3
"""Future explicit-feature diagnostic build only; no test or engine execution."""
from common import *
import shutil

def main():
    plan=guard('build');source=Path(plan['source']);out=Path(plan['build']);target=source/'target/placement-census-generic'
    assert not out.exists() and not target.exists();out.mkdir()
    snapshot=out/'source-before'
    for name,h in plan['source71'].items():
        q=snapshot/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,q);assert sha(q)==h
    for name in ['rustc','cargo']:
        child([plan['compiler'][name]['path'],*plan['compiler'][name]['version_args']],out/(name+'-version'))
        assert (out/(name+'-version.stdout')).read_text()==plan['compiler'][name]['version_stdout']
        assert (out/(name+'-version.stderr')).read_bytes()==b''
    argv=['/usr/bin/cargo','build','--offline','--locked','--release','--verbose','--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(target),'--manifest-path',str(source/'Cargo.toml'),'--features','placement-census','--bin','rook2-placement-census']
    env=dict(os.environ,RUSTC='/usr/bin/rustc',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4')
    receipt={'schema':'rook2-placement-census-build-v1','argv':argv,'environment_overrides':{k:v for k,v in env.items() if k not in os.environ or os.environ[k]!=v},'compiler':plan['compiler'],'source_sha256_before':plan['native48'],'tool_sha256_before':plan['tools23'],'pgo':{'mode':'none'},'rust_flags':['-C','target-cpu=x86-64'],'features':['placement-census'],'target_triple':'x86_64-unknown-linux-gnu','helper_affinity':sorted(os.sched_getaffinity(0)),'source_root':str(source),'native_runs':0}
    child(argv,out/'cargo',env=env,cwd=source)
    image=target/'x86_64-unknown-linux-gnu/release/rook2-placement-census';frozen=out/'rook2-exact';shutil.copy2(image,frozen)
    guard('build')
    receipt.update(source_sha256_after=plan['native48'],tool_sha256_after=plan['tools23'],binary_output={'path':str(image),'sha256':sha(image)},outcome='build-succeeded-with-stable-input-snapshot',cargo_exit_code=0)
    write(out/'receipt.json',receipt)
    child(['/usr/bin/python3',str(ROOT/'tools/archive_build.py'),str(out)],out/'archive')
    ar=load(out/'archive-receipt.json');assert ar['files']==71 and ar['binary_sha256']==sha(frozen) and ar['sha256']==sha(out/ar['archive'])
    print(json.dumps({'complete':True,'image_sha256':sha(frozen),'source_files':71,'native_runs':0}))
if __name__=='__main__':main()
