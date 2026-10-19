#!/usr/bin/env python3
"""Exact closed47 generic trees only; inventory, stream, reopen and recheck originals."""
from pathlib import Path
import hashlib,json,os,stat,sys,tarfile,gzip
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TREES=['ordinary-position-borrow-backend-preparation-20261019-01', 'ordinary-position-borrow-parent-backend-review-20261019-01', 'ordinary-position-borrow-focused-native-check-20261019-01', 'ordinary-position-borrow-generic-screen-preparation-20261019-01', 'ordinary-position-borrow-generic-screen-20261019-01', 'ordinary-position-borrow-generic-screen-parent-review-20261019-01', 'ordinary-position-borrow-decision-20261019-01']
def digest(f):
 h=hashlib.sha256();n=0
 for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def sha(p):
 with Path(p).open('rb') as f:return digest(f)[0]
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def inventory():
 rows={}
 for tree in TREES:
  root=ROOT/tree;assert root.is_dir() and not root.is_symlink(),root
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink(),p
   if p.is_dir():continue
   assert p.is_file(),p
   name=p.relative_to(ROOT).as_posix();assert not name.startswith('/') and all(x not in ['.','..'] for x in Path(name).parts)
   assert name not in rows
   with p.open('rb') as f:h,n=digest(f)
   s=p.stat();assert n==s.st_size
   rows[name]=dict(bytes=n,sha256=h,mode=stat.S_IMODE(s.st_mode))
 return rows
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 before=inventory();write('member-manifest.json',before)
 write('scope.json',dict(complete_closed_trees=TREES,external_payload_expansion=False,own_checkpoint_excluded=True,all_regular_files_no_omissions=True,files=len(before),original_bytes=sum(x['bytes'] for x in before.values()),scope='Closed47 generic mechanism/focused13/fixed70 evidence; own-PGO only decision, no adoption or broad qualification; external runtime/source payloads referenced, not expanded'))
 archive=HERE/'closed-ordinary-position-borrow-generic.tar.gz'
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
   with t.extractfile(member) as f:h,n=digest(f)
   reopened[member.name]=dict(bytes=n,sha256=h,mode=member.mode)
 assert reopened==before
 assert inventory()==before,'original closed inputs changed'
 write('verification.json',dict(complete=True,archive=archive.name,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,file_count=len(before),original_bytes=sum(x['bytes'] for x in before.values()),member_manifest_sha256=sha(HERE/'member-manifest.json'),scope_sha256=sha(HERE/'scope.json'),all_members_reopened_and_hashed=True,member_manifest_exact=True,originals_rechecked_unchanged=True,all_selected_regular_files_captured=True,no_external_expansion=True,affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR']))
 print((HERE/'verification.json').read_text())
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),archive_attempt_preserved=True));raise
