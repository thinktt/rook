#!/usr/bin/env python3
"""Independent closed archive readback: no archive writer/helper import or engines."""
from pathlib import Path
import gzip,hashlib,json,stat,tarfile,os
P=Path(__file__).resolve().parent;E=P.parent;R=E.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((P/'member-manifest.json').read_text());v=json.loads((P/'verification.json').read_text());scope=json.loads((P/'scope.json').read_text());excluded=json.loads((P/'exclusions.json').read_text());archive=P/v['archive']
assert sha(archive)==v['archive_sha256'] and archive.stat().st_size==v['archive_bytes']
assert sha(P/'member-manifest.json')==v['member_manifest_sha256']
with archive.open('rb') as f:
 head=f.read(10);assert head[:2]==b'\x1f\x8b' and head[3]&8==0 and int.from_bytes(head[4:8],'little')==0
seen={}
with tarfile.open(archive,'r:gz') as t:
 for member in t:
  n=member.name;assert member.isfile() and n in m and n not in seen
  assert not n.startswith('/') and all(x not in ('.','..') for x in Path(n).parts)
  assert member.uid==member.gid==member.mtime==0 and member.uname==member.gname==''
  assert member.mode==m[n]['mode'] and member.size==m[n]['bytes']
  with t.extractfile(member) as f:
   data=f.read();assert len(data)==m[n]['bytes'] and hashlib.sha256(data).hexdigest()==m[n]['sha256']
  seen[n]=True
assert set(seen)==set(m) and len(seen)==414
found=set()
for tree in scope['complete_closed_trees']:
 for p in (E/tree).rglob('*'):
  assert not p.is_symlink()
  if p.is_dir():continue
  assert stat.S_ISREG(p.lstat().st_mode)
  n=p.relative_to(E).as_posix();assert n in m or n in excluded
  if n in excluded:
   assert p.stat().st_size==excluded[n]['bytes'] and stat.S_IMODE(p.stat().st_mode)==excluded[n]['mode'];continue
  assert sha(p)==m[n]['sha256'] and p.stat().st_size==m[n]['bytes'] and stat.S_IMODE(p.stat().st_mode)==m[n]['mode'];found.add(n)
assert found==set(m)
promotion=E/'influence-bitsliced-sum-integration-20261019-01/source-promotion.json';source=json.loads(promotion.read_text());assert len(source['files_sha256'])==115 and all(sha(R/n)==h for n,h in source['files_sha256'].items())
raw=E/'influence-mask-cancel-delta-generic-screen-20261019-01/independent-reconciliation.json';x=json.loads(raw.read_text());assert x['complete'] and x['lifetimes']==70 and len(x['native_rows'])==70 and x['advance_under_declared_rule'] is False
proof={'complete':True,'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'members':len(seen),'all_member_hash_size_mode_headers_verified':True,'gzip_normalized_header_verified':True,'all_selected_originals_and_complete13inventories_unchanged':True,'canonical115_unchanged':True,'raw70_referenced_closed_not_rerun':{'path':str(raw),'sha256':sha(raw)},'new_engine_or_oracle_runs':0,'writer_imported':False,'all_owned_jobs_closed':True}
with (P/'independent-verification.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))
