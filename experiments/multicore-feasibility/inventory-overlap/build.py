#!/usr/bin/env python3
"""One isolated generic inventory-census image with archived native source."""
import argparse,hashlib,json,os,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'Cargo.toml',ROOT/'Cargo.lock',*sorted((ROOT/'src').rglob('*'))] if p.is_file()}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir();before=snapshot();archive=out/'source-before';archive.mkdir()
 for name,h in before.items():
  dest=archive/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest);assert sha(dest)==h
 env=dict(os.environ,PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',RUSTFLAGS='-C target-cpu=x86-64')
 for k in list(env):
  if k in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or k.startswith('CARGO_PROFILE_'):env.pop(k,None)
 cmd=['/usr/bin/cargo','build','--offline','--verbose','--release','--features','inventory-census','--target','x86_64-unknown-linux-gnu','--bin','rook2','--target-dir',str(out/'target')]
 start=time.monotonic()
 with (out/'stdout').open('xb') as so,(out/'stderr').open('xb') as se:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=so,stderr=se,timeout=300)
 receipt=dict(argv=cmd,exit=r.returncode,wallSeconds=time.monotonic()-start,sourceBefore=before,sourceAfter=snapshot(),toolchain={n:dict(path='/usr/bin/'+n,sha256=sha(Path('/usr/bin/'+n)),version=subprocess.check_output(['/usr/bin/'+n,'-Vv' if n=='rustc' else '--version'],text=True)) for n in ['rustc','cargo']},flags=['-C','target-cpu=x86-64'])
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert r.returncode==0 and receipt['sourceBefore']==receipt['sourceAfter']
 commands=[shlex.split(line.split('Running `',1)[1].rsplit('`',1)[0]) for line in (out/'stderr').read_text().splitlines() if 'Running `' in line and '--crate-name rook2 ' in line]
 effective={}
 for source in ['src/lib.rs','src/bin/rook2.rs']:
  matches=[x for x in commands if source in x];assert len(matches)==1
  xs=matches[0];assert 'feature="inventory-census"' in xs;opts={}
  for i,x in enumerate(xs):
   if x=='-C':k,_,v=xs[i+1].partition('=');opts[k]=v or True
  for k,v in [('opt-level','3'),('panic','abort'),('codegen-units','1'),('debuginfo','1'),('target-cpu','x86-64')]:assert opts[k]==v
  assert not any(k.startswith('profile-') or k=='llvm-args' for k in opts)
  assert opts.get('lto')=='thin' if source.endswith('rook2.rs') else opts.get('linker-plugin-lto') is True
  effective[source]=opts
 binary=out/'target/x86_64-unknown-linux-gnu/release/rook2';frozen=out/'rook2-census';shutil.copy2(binary,frozen)
 receipt.update(effectiveOptions=effective,binary=str(frozen),binarySha256=sha(frozen),complete=True);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('built',receipt['binarySha256'])
if __name__=='__main__':main()
