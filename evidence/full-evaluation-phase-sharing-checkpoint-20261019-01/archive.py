from pathlib import Path
import hashlib,json,tarfile,time
r=Path('/home/legolas/rook2');o=r/'evidence/full-evaluation-phase-sharing-checkpoint-20261019-01'
m=json.loads((o/'member-manifest.json').read_text());a=o/'closed-experiment26.tar.gz'
assert not a.exists()
t=time.monotonic()
with tarfile.open(a,'w:gz',compresslevel=6) as archive:
 for rel,v in m.items():
  p=r/rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
  archive.add(p,arcname=rel,recursive=False)
print(json.dumps(dict(archive_written=True,members=len(m),elapsed_s=time.monotonic()-t)),flush=True)
with tarfile.open(a,'r:gz') as archive:
 members=archive.getmembers();assert [x.name for x in members]==list(m)
 for item in members:
  data=archive.extractfile(item).read();v=m[item.name]
  assert len(data)==v['size'] and hashlib.sha256(data).hexdigest()==v['sha256']
for rel,v in m.items():assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==v['sha256']
receipt=dict(complete=True,archive=str(a),sha256=hashlib.sha256(a.read_bytes()).hexdigest(),size=a.stat().st_size,members=len(m),member_manifest_sha256=hashlib.sha256((o/'member-manifest.json').read_bytes()).hexdigest(),all_reopened_member_hashes_match=True,originals_unchanged=True,elapsed_s=time.monotonic()-t)
with (o/'archive-receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt),flush=True)
