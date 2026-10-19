#!/usr/bin/env python3
"""Close own43 PGO build/training only; no performance result is implied."""
from pathlib import Path
import json,hashlib,os,tarfile,gzip
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13}
summary=json.loads((E/'influence-bitsliced-sum-pgo-preparation-20261019-01/four-stage-summary.json').read_text());assert summary['complete'] and summary['independent_raw54_original54_remerge_byte_identical']
files={};excluded=[]
for suffix in ['pgo-preparation','pgo-instrumented-build','pgo-training','pgo-use-build']:
 base=E/('influence-bitsliced-sum-'+suffix+'-20261019-01')
 for q in sorted(base.rglob('*')):
  assert not q.is_symlink()
  if not q.is_file():continue
  if 'source-before' in q.relative_to(base).parts or q.name=='rook2-exact':excluded.append(str(q.relative_to(E)));continue
  assert q.read_bytes()[:4]!=b'\x7fELF'
  files[str(q.relative_to(E))]=dict(sha256=sha(q),bytes=q.stat().st_size,mode=q.stat().st_mode&0o7777)
archive=P/'closed43-pgo-build.tar.gz'
with archive.open('xb') as out:
 with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0) as z:
  with tarfile.open(mode='w|',fileobj=z) as tar:
   for n,a in sorted(files.items()):
    q=E/n;assert sha(q)==a['sha256'];t=tarfile.TarInfo(n);t.size=a['bytes'];t.mode=a['mode'];t.uid=t.gid=t.mtime=0;t.uname=t.gname=''
    with q.open('rb') as f:tar.addfile(t,f)
seen=set()
with tarfile.open(archive,'r:gz') as tar:
 for m in tar:
  assert m.isfile() and m.name in files and m.name not in seen;a=files[m.name];d=tar.extractfile(m).read();assert len(d)==m.size==a['bytes'] and hashlib.sha256(d).hexdigest()==a['sha256'] and m.mode==a['mode'];assert m.uid==m.gid==m.mtime==0 and m.uname==m.gname=='';assert sha(E/m.name)==a['sha256'];seen.add(m.name)
assert seen==set(files)
receipt=dict(complete=True,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members=len(files),unpacked_bytes=sum(a['bytes'] for a in files.values()),all_headers_modes_bytes_and_originals_verified=True,files_sha256=files,excluded_immutable_elf_and_duplicate_source=excluded,source_graph=summary['source_graph'],scope=summary['scope'])
with (P/'archive-receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['files_sha256','excluded_immutable_elf_and_duplicate_source']}))
