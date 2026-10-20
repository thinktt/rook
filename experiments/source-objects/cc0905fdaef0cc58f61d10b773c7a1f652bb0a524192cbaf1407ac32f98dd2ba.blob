#!/usr/bin/env python3
"""Finite experiment29 checkpoint: source+small metadata; large originals indexed."""
from pathlib import Path, PurePosixPath
import argparse, gzip, hashlib, json, os, stat, tarfile
R=Path('/home/legolas/rook2'); E=R/'evidence'
C=E/'influence-delta-checkpoint-20261019-01'
S=Path('/home/legolas/rook2-work/imp2-influence-delta-20261019-01')
B=E/'influence-delta-generic-build-20261019-01'
SOURCE=E/'influence-delta-integration-source-review-20261019-01/source-manifest.json'
PREFIXES=[
 'influence-delta-integration-preparation-20261019-01',
 'influence-delta-integration-source-review-20261019-01',
 'influence-delta-kernel-source-review-20261019-01',
 'influence-delta-kernel-preparation-20261019-01',
 'influence-delta-kernel-tests-preparation-20261019-01',
 'influence-delta-kernel-native-validation-20261019-01',
 'influence-delta-integration-native-validation-20261019-01',
 'influence-delta-generic-build-20261019-01',
 'influence-delta-generic-backend-review-20261019-01',
 'influence-delta-generic-cpu-pilot-20261019-01',
 'influence-delta-provenance-plan-20261019-01',
 'influence-delta-integration-tests-preparation-20261019-01',
]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def save(n,d): (C/n).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def safe(n):
 p=PurePosixPath(n)
 assert not p.is_absolute() and '..' not in p.parts and str(p)==n and n not in ('','.'); return n
def regular(p): assert stat.S_ISREG(p.lstat().st_mode),str(p)
def record(p):
 assert p.is_file(),str(p)
 return dict(path=str(p),sha256=sha(p),size=p.stat().st_size,mode=stat.S_IMODE(p.stat().st_mode),
  symlink_target=os.readlink(p) if p.is_symlink() else None,resolved_path=str(p.resolve()))
def verify(rows):
 for x in rows:
  p=Path(x['path']); now=record(p)
  assert now=={k:x[k] for k in now},str(p)
def preflight():
 selected={}; external={}
 def add(p,n=None):
  regular(p); n=safe(n or p.relative_to(R).as_posix())
  assert n not in selected,n
  selected[n]=record(p)
 m=json.loads(SOURCE.read_text())['files']; assert len(m)==71
 for n,h in m.items():
  safe(n); p=B/'source-before'/n
  assert sha(p)==h and sha(S/n)==h,n
  add(p,'source71/'+n)
 # Fixed top-level small source/proof/helper files. Nested raw data is indexed,
 # with pilot JSON accounting explicitly included below.
 for name in PREFIXES:
  root=E/name
  assert root.is_dir()
  for p in sorted(root.iterdir()):
   if p.is_file() and p.suffix in ('.json','.md','.py','.mjs','.patch','.rs'):
    add(p)
  for p in sorted(root.rglob('*')):
   if not p.is_file() or 'source-before' in p.relative_to(root).parts: continue
   if name.endswith('generic-cpu-pilot-20261019-01') and p.suffix=='.json' and p.parent!=root:
    add(p)
   external[str(p)]=record(p)
 for p in [R/'docs/decisions/0019-influence-delta-trial.md',R/'docs/qualification-gaps.md',
           E/'influence-delta-decision-20261019-01/README.md']:
  add(p)
 plan=json.loads((E/'influence-delta-generic-cpu-pilot-20261019-01/plan.json').read_text())
 for n,h in plan['immutable_inputs'].items():
  p=Path(n); assert sha(p)==h,n; external[n]=record(p)
 for p in [
  E/'ordinary-projected-bits-generic-build-20261018-01/rook2-exact',
  E/'ordinary-projected-bits-pgo-use-build-20261018-01/rook2-exact',
 ]: external[str(p)]=record(p)
 # Included sources/metadata do not need a second archive copy. External index
 # still records the original logical path of every dependency above.
 for n,x in selected.items(): external.pop(x['path'],None)
 assert not any('opaque' in n.lower() or 'census' in n.lower() for n in external)
 external_rows=sorted(external.values(),key=lambda x:x['path'])
 save('retained-external-index.json',dict(scope='Retained originals outside this compact archive; not deleted or relocated',files=external_rows))
 add(C/'retained-external-index.json','checkpoint/retained-external-index.json')
 add(C/'archive_checkpoint.py','checkpoint/archive_checkpoint.py')
 rows=[dict(member=n,**x) for n,x in sorted(selected.items())]
 verify(rows); verify(external_rows)
 save('member-manifest.json',dict(source71_graph_sha256='7f604b27289adf889f83294e86300ae42c1a44507f64cf5946fe3a3fdb885637',members=rows))
 save('preflight.json',dict(complete=True,member_count=len(rows),raw_bytes=sum(x['size'] for x in rows),
  external_count=len(external_rows),external_bytes=sum(x['size'] for x in external_rows),
  writer_sha256=sha(C/'archive_checkpoint.py'),manifest_sha256=sha(C/'member-manifest.json'),
  external_index_sha256=sha(C/'retained-external-index.json'),source71_before_equal=True,
  whitelist=PREFIXES,large_images_logs_indexed_not_archived=True))
 print((C/'preflight.json').read_text())
def archive():
 pre=json.loads((C/'preflight.json').read_text())
 assert sha(C/'archive_checkpoint.py')==pre['writer_sha256']
 assert sha(C/'member-manifest.json')==pre['manifest_sha256']
 assert sha(C/'retained-external-index.json')==pre['external_index_sha256']
 rows=json.loads((C/'member-manifest.json').read_text())['members']
 ext=json.loads((C/'retained-external-index.json').read_text())['files']
 verify(rows);verify(ext)
 target=C/'influence-delta29-source-and-results.tar.gz';assert not target.exists()
 with target.open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as gz:
   with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
    for x in rows:
     p=Path(x['path']); regular(p)
     info=tarfile.TarInfo(safe(x['member']));info.size=x['size'];info.mode=x['mode'];info.mtime=0;info.uid=0;info.gid=0;info.uname='';info.gname=''
     with p.open('rb') as f: tar.addfile(info,f)
 expected={x['member']:x for x in rows};seen=set()
 with tarfile.open(target,'r|gz') as tar:
  for info in tar:
   n=safe(info.name);assert info.isfile() and n not in seen and n in expected,n
   x=expected[n];assert info.size==x['size'] and info.mode==x['mode'],n
   f=tar.extractfile(info);h=hashlib.sha256();size=0
   for b in iter(lambda:f.read(1<<20),b''):h.update(b);size+=len(b)
   assert size==x['size'] and h.hexdigest()==x['sha256'],n;seen.add(n)
 assert seen==set(expected)
 verify(rows);verify(ext)
 m=json.loads(SOURCE.read_text())['files']
 for n,h in m.items(): assert sha(S/n)==h and sha(B/'source-before'/n)==h,n
 receipt=dict(complete=True,archive=str(target),sha256=sha(target),compressed_bytes=target.stat().st_size,
  member_count=len(rows),raw_bytes=sum(x['size'] for x in rows),every_member_reopened_and_digest_verified=True,
  every_original_and_external_unchanged=True,source71_after_equal=True,
  manifest_sha256=sha(C/'member-manifest.json'),writer_sha256=sha(C/'archive_checkpoint.py'),external_index_sha256=sha(C/'retained-external-index.json'))
 save('archive-receipt.json',receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['preflight','archive']);a=p.parse_args()
 (preflight if a.stage=='preflight' else archive)()
