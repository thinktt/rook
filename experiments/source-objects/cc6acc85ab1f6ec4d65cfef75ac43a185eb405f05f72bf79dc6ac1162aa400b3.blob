"""Streaming deterministic closed conformance archive; never executes native code."""
from pathlib import Path
import gzip,hashlib,json,stat,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
ROOTS=[HERE,ROOT/'pressure-value-static-conformance-build-20261019-01',ROOT/'pressure-value-static-conformance-20261019-01']
EXCLUDED={HERE/n for n in ['closed-evidence.tar.gz','closed-member-manifest.json','closed-archive-receipt.json','closed-archive-tool-terminal.json']}
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while data:=f.read(1024*1024):h.update(data)
 return h.hexdigest()
def inventory():
 rows={}
 for root in ROOTS:
  assert root.is_dir() and not root.is_symlink()
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink(),p
   if p.is_dir() or p in EXCLUDED:continue
   s=p.stat();assert stat.S_ISREG(s.st_mode),p
   rows[p.relative_to(ROOT).as_posix()]={'path':str(p),'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode),'sha256':sha(p)}
 return dict(sorted(rows.items()))
def write(p,v):
 with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
def main():
 for p in [HERE/'finalizer-tool-terminal.json',HERE/'reconciliation/tool-terminal.json']:
  t=json.loads(p.read_text());assert t['actual_tool_terminal_observed'] and t['exit_code']==0
 expected=inventory();assert expected
 write(HERE/'closed-member-manifest.json',expected)
 out=HERE/'closed-evidence.tar.gz'
 with out.open('xb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
  for name,row in expected.items():
   ti=tarfile.TarInfo(name);ti.size=row['bytes'];ti.mode=row['mode'];ti.uid=ti.gid=ti.mtime=0;ti.uname=ti.gname=''
   with Path(row['path']).open('rb') as f:archive.addfile(ti,f)
 observed={}
 with tarfile.open(out,'r|gz') as archive:
  for m in archive:
   assert m.isfile() and m.name not in observed and m.name in expected
   row=expected[m.name];assert m.size==row['bytes'] and m.mode==row['mode'] and m.uid==m.gid==m.mtime==0 and not m.uname and not m.gname
   h=hashlib.sha256();f=archive.extractfile(m);size=0
   while data:=f.read(1024*1024):h.update(data);size+=len(data)
   assert size==row['bytes'] and h.hexdigest()==row['sha256'];observed[m.name]=True
 assert set(observed)==set(expected) and inventory()==expected
 result={'complete':True,'archive':str(out),'sha256':sha(out),'compressed_bytes':out.stat().st_size,'members':len(expected),'uncompressed_file_bytes':sum(r['bytes'] for r in expected.values()),'member_manifest_sha256':sha(HERE/'closed-member-manifest.json'),'all_reopened_headers_and_bytes_exact':True,'all_original_members_unchanged':True,'included_roots':list(map(str,ROOTS)),'explicit_generated_output_exclusions':list(map(str,sorted(EXCLUDED))),'scope':'Exact closed209/full117 conformance evidence including all raw7673, unit/adapter images, source115 and official115 archives; no production qualification claim'}
 write(HERE/'closed-archive-receipt.json',result);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
