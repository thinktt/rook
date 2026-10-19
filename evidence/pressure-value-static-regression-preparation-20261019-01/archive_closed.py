#!/usr/bin/env python3
"""Preserve closed40 regression/pregate outputs; no engine execution."""
from pathlib import Path
import hashlib,json,stat,tarfile
E=Path('/home/legolas/rook2/evidence')
R=E/'pressure-value-static-regression-20261019-01';G=E/'pressure-value-static-pregate-20261019-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
for root in [R,G]:
 t=load(root/'tool-terminal.json');assert t['actual_tool_terminal_observed'] and t['exit_code']==0
assert load(G/'independent-raw-reconciliation.json')['complete']
archive=G/'closed-functional.tar.gz';manifest=G/'archive-manifest.json'
assert not archive.exists() and not manifest.exists()
files={}
for label,root in [('regression',R),('pregate',G)]:
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink()
  if p.is_file():
   name=label+'/'+str(p.relative_to(root));assert '..' not in Path(name).parts and not name.startswith('/')
   files[name]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,mode=stat.S_IMODE(p.stat().st_mode))
with tarfile.open(archive,'x:gz') as t:
 for name,r in files.items():t.add(r['path'],arcname=name,recursive=False)
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert len(members)==len(files) and {m.name for m in members}==set(files)
 for m in members:
  r=files[m.name];assert m.isfile() and m.size==r['bytes'] and stat.S_IMODE(m.mode)==r['mode']
  assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==r['sha256']
for r in files.values():
 p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'] and stat.S_IMODE(p.stat().st_mode)==r['mode']
result=dict(archive=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=len(files),all_reopened_member_sha256_equal=True,originals_rechecked=True,files=files,scope='Closed untimed40 post-use strict54/wire8/24 and regular12/continuity/seed raw only; no deployment or performance qualification.')
with manifest.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['sha256','bytes','members','all_reopened_member_sha256_equal','originals_rechecked']}))
