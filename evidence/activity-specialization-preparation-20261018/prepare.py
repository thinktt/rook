#!/usr/bin/env python3
"""Prepare static piece-kind activity traversal; no native code is executed."""
import gzip,hashlib,io,json,shutil,subprocess,sys,tarfile
from pathlib import Path
PREP=Path(__file__).resolve().parent
ROOT=PREP.parents[1]
TARGET=Path('/tmp/imp2-activity-specialization-20261018')
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 baseline=source_snapshot(ROOT)
 reference=ROOT/'evidence/production-eval-kernels-use-build-20261018/receipt.json'
 assert baseline==json.loads(reference.read_text())['source_sha256_before']
 TARGET.mkdir()
 for n in ['Cargo.toml','Cargo.lock']:shutil.copy2(ROOT/n,TARGET/n)
 shutil.copytree(ROOT/'src',TARGET/'src')
 shutil.copytree(ROOT/'tools',TARGET/'tools',ignore=shutil.ignore_patterns('__pycache__'))
 old=(ROOT/'src/activity.rs').read_text()
 start=old.index('        for kind in [')
 end=old.index('    let pieces =',start)
 replacement=''
 for k in range(1,5):
  replacement+=f'        accumulate_kind::<{k}>(position, influence, color, &mut marks, phase.endgame, &mut raw_scores[color.index()], &mut relation_queries);\n'
 text=old[:start]+replacement+'    }\n'+old[end:]
 helper="""
#[inline]
fn accumulate_kind<const KIND: usize>(
    position: &Position, influence: &Influence, color: Color, marks: &mut Marks,
    endgame: u16, score: &mut i64, queries: &mut u64,
) {
    let kind = PieceKind::ALL[KIND];
    for &source in position.piece_squares(color, kind) {
        let mobility = destinations_kind::<KIND>(position, influence, color, source, marks);
        let (piece, work) = piece_score_kind::<KIND>(influence, color, source, mobility, endgame);
        *score += piece;
        *queries += work;
    }
}
"""
 at=text.index('#[inline]\nfn relative_rank')
 text=text[:at]+helper+'\n'+text[at:]
 for name in ['destinations','piece_score']:
  start=text.index('fn '+name+'(');end=text.index('\n}',start)+2
  body=text[start:end]
  body=body.replace('fn '+name+'(', 'fn '+name+'_kind<const KIND: usize>(')
  assert body.count('    kind: PieceKind,\n')==1
  body=body.replace('    kind: PieceKind,\n','',1)
  at=body.index(' {\n')+3
  body=body[:at]+'    let kind = PieceKind::ALL[KIND];\n'+body[at:]
  text=text[:start]+body+text[end:]
 # Keep existing admission/semantic unit probes on the same specialized kernels.
 wrappers="""
#[cfg(test)]
fn destinations(position: &Position, influence: &Influence, color: Color, kind: PieceKind, source: Square, marks: &mut Marks) -> Mobility {
    match kind {
        PieceKind::Knight => destinations_kind::<1>(position, influence, color, source, marks),
        PieceKind::Bishop => destinations_kind::<2>(position, influence, color, source, marks),
        PieceKind::Rook => destinations_kind::<3>(position, influence, color, source, marks),
        PieceKind::Queen => destinations_kind::<4>(position, influence, color, source, marks),
        _ => unreachable!("non-activity piece"),
    }
}
#[cfg(test)]
fn piece_score(influence: &Influence, color: Color, kind: PieceKind, source: Square, mobility: Mobility, endgame: u16) -> (i64, u64) {
    match kind {
        PieceKind::Knight => piece_score_kind::<1>(influence, color, source, mobility, endgame),
        PieceKind::Bishop => piece_score_kind::<2>(influence, color, source, mobility, endgame),
        PieceKind::Rook => piece_score_kind::<3>(influence, color, source, mobility, endgame),
        PieceKind::Queen => piece_score_kind::<4>(influence, color, source, mobility, endgame),
        _ => unreachable!("non-activity piece"),
    }
}
"""
 at=text.index('#[inline]\nfn pressure_value')
 text=text[:at]+wrappers+'\n'+text[at:]
 (TARGET/'src/activity.rs').write_text(text)
 subprocess.run(['rustfmt','--edition','2021','--config','skip_children=true',str(TARGET/'src/activity.rs')],check=True)
 after=source_snapshot(TARGET)
 assert [n for n in baseline if baseline[n]!=after[n]]==['src/activity.rs']
 assert source_snapshot(ROOT)==baseline
 files={str(p.relative_to(TARGET)):sha(p) for p in [TARGET/'Cargo.toml',TARGET/'Cargo.lock',*sorted((TARGET/'src').rglob('*.rs')),*sorted((TARGET/'tools').rglob('*'))] if p.is_file()}
 archive=PREP/'prepared-source.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as z:
   with tarfile.open(fileobj=z,mode='w') as out:
    for name,digest in sorted(files.items()):
     data=(TARGET/name).read_bytes();assert hashlib.sha256(data).hexdigest()==digest
     m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o644;out.addfile(m,io.BytesIO(data))
 with tarfile.open(archive,'r:gz') as a:assert {m.name:hashlib.sha256(a.extractfile(m).read()).hexdigest() for m in a}==files
 result=dict(status='Uncompiled static-kind activity prototype; correctness and cost unmeasured',path=str(TARGET),baseline_source_sha256=baseline,variant_source_sha256=after,modified_existing_files=['src/activity.rs'],generator_sha256=sha(Path(__file__)),archive=archive.name,archive_sha256=sha(archive),archive_files=files,scope='Only private activity traversal/scoring specialization. Existingi64/u64 arithmetic, source chronology, mark order, charge points and all external owners remain unchanged.',hypothesis='Expose fixed Knight/Bishop/Rook/Queen kinds to optimization within destination and piece-score kernels; additional machine-code size may offset branch simplification. Require independent coordinate/native/replay evidence and matched whole-native timing before adoption.')
 (PREP/'prepared.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','path','archive_sha256']}))
if __name__=='__main__':main()
