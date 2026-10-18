#!/usr/bin/env python3
"""Prepare D=true null-transition influence opportunity counters; no cache or native execution."""
import gzip,hashlib,io,json,shutil,sys,tarfile
from pathlib import Path
PREP=Path(__file__).resolve().parent
ROOT=PREP.parents[1]
TARGET=Path('/tmp/imp2-null-opportunity-20261018')
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 baseline=source_snapshot(ROOT);ref=ROOT/'evidence/production-eval-kernels-use-build-20261018/receipt.json'
 assert baseline==json.loads(ref.read_text())['source_sha256_before']
 TARGET.mkdir()
 for n in ['Cargo.toml','Cargo.lock']:shutil.copy2(ROOT/n,TARGET/n)
 shutil.copytree(ROOT/'src',TARGET/'src');shutil.copytree(ROOT/'tools',TARGET/'tools',ignore=shutil.ignore_patterns('__pycache__'))
 p=TARGET/'src/quiescence.rs';t=p.read_text();needle='pub struct Stats {\n';assert needle in t
 t=t.replace(needle,needle+'    pub null_positive_map: u64,\n    pub null_to_quiescence: u64,\n',1);p.write_text(t)
 p=TARGET/'src/ordinary.rs';t=p.read_text();needle='if request.depth <= 0 || p == 63 || p >= self.config.maximum_depth {\n';assert t.count(needle)==1
 t=t.replace(needle,needle+'            if DIAGNOSTICS && previous.movement.is_none() { self.stats.null_to_quiescence += 1; }\n',1)
 needle='        let mut scratch = None;\n';assert t.count(needle)==1
 t=t.replace(needle,'        if DIAGNOSTICS && previous.movement.is_none() { self.stats.null_positive_map += 1; }\n'+needle,1);p.write_text(t)
 p=TARGET/'src/session.rs';t=p.read_text();needle='impl<const D: bool> Session<D> {\n';assert t.count(needle)==1
 t=t.replace(needle,needle+"""    pub fn diagnostic_null_probe(&self) -> Option<[u64; 6]> {
        self.search.as_ref().map(|search| [search.stats.null_trials,
            search.stats.null_positive_map, search.stats.null_to_quiescence,
            search.evaluator.stats.influence_builds, search.evaluator.stats.full,
            search.evaluator.stats.fast])
    }
""",1);p.write_text(t)
 t=(TARGET/'src/bin/rook2.rs').read_text().replace('Session::<false>','Session::<true>')
 t=t.replace('    // Disable development counters and root traces in the ordinary binary.\n','')
 needle='            Action::Quit => return Ok(()),';assert t.count(needle)==1
 block="""            Action::Quit => {
                let counts = session.diagnostic_null_probe().ok_or_else(|| io::Error::other("missing probe stats"))?;
                let path = std::env::var_os("ROOK2_NULL_PROBE").ok_or_else(|| io::Error::other("missing private probe file"))?;
                let mut file = std::fs::OpenOptions::new().write(true).create_new(true).open(path)?;
                writeln!(file, "{{\\\"null_trials\\\":{},\\\"null_positive_map\\\":{},\\\"null_to_quiescence\\\":{},\\\"influence_builds\\\":{},\\\"full\\\":{},\\\"fast\\\":{}}}", counts[0],counts[1],counts[2],counts[3],counts[4],counts[5])?;
                return Ok(());
            }"""
 t=t.replace(needle,block)
 (TARGET/'src/bin/rook2-null-probe.rs').write_text(t)
 after=source_snapshot(TARGET);assert source_snapshot(ROOT)==baseline
 files={str(p.relative_to(TARGET)):sha(p) for p in [TARGET/'Cargo.toml',TARGET/'Cargo.lock',*sorted((TARGET/'src').rglob('*.rs')),*sorted((TARGET/'tools').rglob('*'))] if p.is_file()}
 archive=PREP/'prepared-source.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as z:
   with tarfile.open(fileobj=z,mode='w') as out:
    for name,h in sorted(files.items()):
     data=(TARGET/name).read_bytes();assert hashlib.sha256(data).hexdigest()==h
     m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o644;out.addfile(m,io.BytesIO(data))
 with tarfile.open(archive,'r:gz') as a:assert {m.name:hashlib.sha256(a.extractfile(m).read()).hexdigest() for m in a}==files
 result=dict(status='Uncompiled diagnostic counters only; no cache, reuse or benefit claim',path=str(TARGET),baseline_source_sha256=baseline,variant_source_sha256=after,modified_existing_files=[n for n in baseline if baseline[n]!=after[n]],new_files=[n for n in after if n not in baseline],archive=archive.name,archive_sha256=sha(archive),archive_files=files,generator_sha256=sha(Path(__file__)),scope='Counter after positive ordinary/table admission where every continuation requires influence, plus null-to-quiescence boundary count. Incoming absent movement is produced only by null trial in ordinary wire. No replacement of any calculation; semantic N/R parity must still be checked on all54 replays.')
 (PREP/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','path','archive_sha256']}))
if __name__=='__main__':main()
