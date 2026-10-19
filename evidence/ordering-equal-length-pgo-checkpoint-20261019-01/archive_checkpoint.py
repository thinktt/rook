#!/usr/bin/env python3
"""Exact closed49 own-PGO trees with explicit requested exclusions; inventory, stream, reopen and recheck originals."""
from pathlib import Path
import hashlib,json,os,stat,sys,tarfile,gzip
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TREES=['ordering-equal-length-pgo-preparation-20261019-01', 'ordering-equal-length-pgo-training-20261019-01', 'ordering-equal-length-pgo-instrumented-build-20261019-01', 'ordering-equal-length-pgo-use-build-20261019-01', 'ordering-equal-length-pgo-backend-preparation-20261019-01', 'ordering-equal-length-pgo-parent-backend-review-20261019-01', 'ordering-equal-length-pgo-screen-preparation-20261019-01', 'ordering-equal-length-pgo-screen-20261019-01', 'ordering-equal-length-pgo-screen-parent-review-20261019-01', 'ordering-equal-length-pgo-decision-20261019-01', 'ordering49-generic-pass-parent-commit-20261019-01']
BOUNDS={'max_included_regular_files': 10000, 'max_included_bytes': 67108864, 'max_archive_bytes': 67108864}
def digest(f):
 h=hashlib.sha256();n=0
 for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def sha(p):
 with Path(p).open('rb') as f:return digest(f)[0]
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def inventory():
 rows={};excluded={}
 for tree in TREES:
  root=ROOT/tree;assert root.is_dir() and not root.is_symlink(),root
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink(),p
   if p.is_dir():continue
   assert p.is_file(),p
   name=p.relative_to(ROOT).as_posix();assert not name.startswith('/') and all(x not in ['.','..'] for x in Path(name).parts)
   assert name not in rows and name not in excluded
   st=p.stat();reason=None
   if 'source-before' in p.relative_to(root).parts:
    assert tree in ['ordering-equal-length-pgo-instrumented-build-20261019-01','ordering-equal-length-pgo-use-build-20261019-01']
    reason='duplicate source-before tree; exact72-member archive retained and independently reopened'
   else:
    with p.open('rb') as f:magic=f.read(4)
    if magic==b'\x7fELF':reason='actual ELF excluded by requested checkpoint scope; metadata/receipt retained'
   if reason:
    excluded[name]=dict(source_path=str(p),bytes=st.st_size,mode=stat.S_IMODE(st.st_mode),reason=reason)
    continue
   with p.open('rb') as f:h,n=digest(f)
   assert n==st.st_size
   rows[name]=dict(source_path=str(p),bytes=n,sha256=h,mode=stat.S_IMODE(st.st_mode),type='regular')
 assert len(rows)<=BOUNDS['max_included_regular_files'] and sum(x['bytes'] for x in rows.values())<=BOUNDS['max_included_bytes']
 assert len([x for x in excluded.values() if x['reason'].startswith('actual ELF')])==2
 assert len(excluded)==146
 return rows,excluded
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 before,excluded=inventory();write('member-manifest.json',before);write('excluded-manifest.json',excluded)
 write('scope.json',dict(complete_closed_trees=TREES,external_payload_expansion=False,own_checkpoint_excluded=True,exclusions_exact=146,included_regular_files=len(before),original_bytes=sum(x['bytes'] for x in before.values()),bounds=BOUNDS,scope='Closed49 own-PGO PARK; includes raw54/profile and70screen lifetimes, not140; actualELFs and duplicate source-before trees explicitly excluded, no broad qualification'))
 archive=HERE/'closed-ordering-equal-length-pgo.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed:
   with tarfile.open(fileobj=compressed,mode='w',format=tarfile.PAX_FORMAT) as t:
    for name,row in before.items():
     source=ROOT/name;info=t.gettarinfo(str(source),arcname=name)
     assert info.isfile() and info.size==row['bytes'] and stat.S_IMODE(info.mode)==row['mode']
     info.mtime=0;info.uid=0;info.gid=0;info.uname='';info.gname='';info.pax_headers={}
     with source.open('rb') as f:
      reader=HashReader(f);t.addfile(info,reader)
      assert reader.n==row['bytes'] and reader.h.hexdigest()==row['sha256'],name
 reopened={}
 with tarfile.open(archive,'r:gz') as t:
  members=t.getmembers();assert len(members)==len(before)
  for member in members:
   assert member.isfile() and member.name in before and member.name not in reopened
   assert member.uid==member.gid==member.mtime==0 and member.uname==member.gname==''
   with t.extractfile(member) as f:h,n=digest(f)
   reopened[member.name]=dict(source_path=str(ROOT/member.name),bytes=n,sha256=h,mode=member.mode,type='regular')
 assert reopened==before
 assert inventory()==(before,excluded),'original closed inputs changed'
 assert archive.stat().st_size<=BOUNDS['max_archive_bytes']
 write('verification.json',dict(complete=True,archive=archive.name,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,file_count=len(before),original_bytes=sum(x['bytes'] for x in before.values()),member_manifest_sha256=sha(HERE/'member-manifest.json'),scope_sha256=sha(HERE/'scope.json'),all_members_reopened_and_hashed=True,member_manifest_exact=True,originals_rechecked_unchanged=True,all_selected_regular_files_captured=True,excluded_file_count=len(excluded),excluded_manifest_sha256=sha(HERE/'excluded-manifest.json'),no_external_expansion=True,affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR']))
 print((HERE/'verification.json').read_text())
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),archive_attempt_preserved=True));raise
