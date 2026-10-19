#!/usr/bin/env python3
"""Archive closed43-generic inputs/results, excluding preserved ELF and duplicate source tree."""
from pathlib import Path
import hashlib,json,gzip,tarfile,os
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13}
decision=json.loads((E/'influence-bitsliced-sum-generic-decision-20261019-01/decision.json').read_text());assert decision['status']=='PASS fixed generic screen; eligible for fresh own-source PGO only' and not decision['own_pgo_performed']
roots=['source-preparation','parent-review','generic-build','generic-build-execution','focused-native-check','backend-review','generic-cpu-pilot-preparation','generic-cpu-pilot','generic-decision']
files={};excluded=[]
for n in roots:
 base=E/('influence-bitsliced-sum-'+n+'-20261019-01');assert base.is_dir()
 for q in sorted(base.rglob('*')):
  assert not q.is_symlink()
  if not q.is_file():continue
  if 'source-before' in q.relative_to(base).parts or q.name=='rook2-exact':
   excluded.append(str(q.relative_to(E)));continue
  assert q.read_bytes()[:4]!=b'\x7fELF',str(q)
  files[str(q.relative_to(E))]=dict(sha256=sha(q),bytes=q.stat().st_size,mode=q.stat().st_mode&0o7777)
archive=P/'closed43-generic.tar.gz'
with archive.open('xb') as raw:
 with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
  with tarfile.open(mode='w|',fileobj=z) as tar:
   for n,a in sorted(files.items()):
    q=E/n;assert sha(q)==a['sha256'];t=tarfile.TarInfo(n);t.size=a['bytes'];t.mode=a['mode'];t.uid=t.gid=t.mtime=0;t.uname=t.gname=''
    with q.open('rb') as f:tar.addfile(t,f)
seen=set()
with tarfile.open(archive,'r:gz') as tar:
 for m in tar:
  assert m.isfile() and m.name in files and m.name not in seen;a=files[m.name];h=hashlib.sha256();size=0;f=tar.extractfile(m)
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b);size+=len(b)
  assert size==m.size==a['bytes'] and m.mode==a['mode'] and h.hexdigest()==a['sha256'];assert m.uid==m.gid==m.mtime==0 and m.uname==m.gname=='';assert sha(E/m.name)==a['sha256'];seen.add(m.name)
assert seen==set(files)
receipt=dict(complete=True,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members=len(files),unpacked_bytes=sum(a['bytes'] for a in files.values()),all_member_headers_modes_bytes_and_originals_verified=True,files_sha256=files,excluded_duplicate_source_and_preserved_elf=excluded,preserved_candidate_sha256=decision['candidate_generic_sha256'],scope='Closed generic43 raw70 and controls/source/codegen/metadata closure only. Source-before72 is separately in included verified-source-before archive; immutable candidate ELF retained outside Git. No promotion or PGO.')
with (P/'archive-receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['files_sha256','excluded_duplicate_source_and_preserved_elf']}))
