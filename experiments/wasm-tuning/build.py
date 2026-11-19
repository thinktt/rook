#!/usr/bin/env python3
"""Build isolated WASM compiler variants; never overwrite qualified outputs or Rust source."""
import argparse,hashlib,json,os,signal,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--sysroot',type=Path,required=True)
p.add_argument('--variants',type=Path)
p.add_argument('--linker',default='/usr/bin/wasm-ld-19')
a=p.parse_args();a.output.mkdir();os.sched_setaffinity(0,{0,1,8,9,10,11,12,13})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[f for base in [ROOT/'src',ROOT/'diagnostic/src',ROOT/'wasm/engine/src',ROOT/'wasm/diagnostic/src'] for f in base.rglob('*.rs')]
files += [ROOT/'wasm/abi.rs',ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'wasm/engine/Cargo.toml',ROOT/'wasm/engine/Cargo.lock',ROOT/'wasm/dist/rook.wasm']
pins={str(f):sha(f) for f in files}
default_variants={'control':dict(lto='thin',simd=False),'fat':dict(lto='fat',simd=False),'simd':dict(lto='thin',simd=True),'fat-simd':dict(lto='fat',simd=True)}
variants=json.loads(a.variants.read_text()) if a.variants else default_variants
report=dict(complete=False,pins=pins,variants={},rustc=subprocess.check_output(['rustc','-vV'],text=True),started=time.time())
deadline=time.monotonic()+900
try:
 for name,config in variants.items():
  out=a.output/name;out.mkdir()
  flags=['--sysroot='+str(a.sysroot.resolve()),'-C','linker='+a.linker,'-C','link-arg=-zstack-size=8388608']
  features=config.get('features',['simd128'] if config.get('simd') else [])
  if features:flags+=['-C','target-feature='+','.join('+'+x for x in features)]
  env=dict(os.environ,CARGO_TARGET_DIR=str((out/'target').resolve()),CARGO_ENCODED_RUSTFLAGS='\x1f'.join(flags),CARGO_PROFILE_RELEASE_LTO=config['lto'])
  env.pop('RUSTFLAGS',None)
  command=['cargo','build','--offline','--locked','--release','--target','wasm32-unknown-unknown','--manifest-path',str(ROOT/'wasm/engine/Cargo.toml')]
  with (out/'stdout').open('xb') as so,(out/'stderr').open('xb') as se:
   child=subprocess.Popen(command,env=env,stdout=so,stderr=se,start_new_session=True)
   try:code=child.wait(timeout=max(1,deadline-time.monotonic()))
   except subprocess.TimeoutExpired:
    os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  assert code==0,name+' build failed'
  binary=out/'target/wasm32-unknown-unknown/release/rook_wasm.wasm'
  report['variants'][name]=dict(config=config,flags=flags,command=command,path=str(binary),sha256=sha(binary),bytes=binary.stat().st_size)
  (a.output/'build.json').write_text(json.dumps(report,indent=2)+'\n')
 assert all(sha(Path(path))==digest for path,digest in pins.items()),'input or qualified artifact changed'
 report['controlMatchesQualifiedBytes']=(report['variants']['control']['sha256']==pins[str(ROOT/'wasm/dist/rook.wasm')]) if 'control' in report['variants'] else None
 report['complete']=True
finally:
 report['finished']=time.time();(a.output/'build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['variants']),flush=True)
