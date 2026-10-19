#!/usr/bin/env python3
"""Exact closed50 evidence only; finite ignored payload exclusions, streaming reopen and original checks."""
from pathlib import Path
import hashlib,json,os,stat,sys,tarfile,gzip
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TREES=['influence-mask-cancel-delta-parent-selection-20261019-01', 'influence-mask-cancel-delta-kernel-preparation-20261019-01', 'influence-mask-cancel-delta-integration-preparation-20261019-01', 'influence-mask-cancel-delta-parent-review-20261019-01', 'influence-mask-cancel-delta-generic-build-20261019-01', 'influence-mask-cancel-delta-backend-preparation-20261019-01', 'influence-mask-cancel-delta-focused-preparation-20261019-01', 'influence-mask-cancel-delta-focused-native-check-20261019-01', 'influence-mask-cancel-delta-generic-screen-preparation-20261019-01', 'influence-mask-cancel-delta-generic-screen-20261019-01', 'influence-mask-cancel-delta-generic-screen-parent-review-20261019-01', 'influence-mask-cancel-delta-decision-20261019-01', 'influence-census-parent-commit-20261019-01']
EXCLUDED_ELF='influence-mask-cancel-delta-generic-build-20261019-01/rook2-exact'
EXCLUDED_SOURCE='influence-mask-cancel-delta-generic-build-20261019-01/source-before/'

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
   assert p.is_file() and stat.S_ISREG(p.lstat().st_mode),p
   name=p.relative_to(ROOT).as_posix();assert not name.startswith('/') and all(x not in ['.','..'] for x in Path(name).parts)
   assert not any(c in name for c in '\r\n\0'),name
   if name==EXCLUDED_ELF or name.startswith(EXCLUDED_SOURCE):
    s=p.stat();excluded[name]=dict(bytes=s.st_size,mode=stat.S_IMODE(s.st_mode),reason='Existing ignored ELF/source-before payload; selected verified75source archive retains source')
    continue
   assert '__pycache__' not in p.parts and 'target' not in p.parts
   with p.open('rb') as check:assert check.read(4)!=b'\x7fELF',name
   assert name not in rows
   with p.open('rb') as f:h,n=digest(f)
   s=p.stat();assert n==s.st_size
   rows[name]=dict(bytes=n,sha256=h,mode=stat.S_IMODE(s.st_mode))
 return rows,excluded
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 before,excluded=inventory();write('member-manifest.json',before);write('exclusions.json',excluded)
 assert EXCLUDED_ELF in excluded
 assert 'influence-mask-cancel-delta-generic-build-20261019-01/verified-source-before.tar.gz' in before
 write('scope.json',dict(complete_closed_trees=TREES,external_payload_expansion=False,own_checkpoint_excluded=True,all_selected_regular_files_no_omissions=True,ignored_payloads_excluded=len(excluded),files=len(before),original_bytes=sum(x['bytes'] for x in before.values()),scope='Closed50 source75/kernel/integration/backend/focused13/raw70/decision and prior census commit receipts. Park, no retry/PGO/broad/adoption; no external dependency expansion'))
 archive=HERE/'closed-influence-mask-cancel-delta.tar.gz'
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
   assert not member.name.startswith('/') and all(x not in ['.','..'] for x in Path(member.name).parts)
   assert member.mtime==0 and member.uid==member.gid==0 and member.uname==member.gname==''
   assert member.size==before[member.name]['bytes'] and member.mode==before[member.name]['mode']
   with t.extractfile(member) as f:h,n=digest(f)
   reopened[member.name]=dict(bytes=n,sha256=h,mode=member.mode)
 assert reopened==before
 assert inventory()==(before,excluded),'original closed inputs changed'
 write('verification.json',dict(complete=True,archive=archive.name,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,file_count=len(before),original_bytes=sum(x['bytes'] for x in before.values()),member_manifest_sha256=sha(HERE/'member-manifest.json'),scope_sha256=sha(HERE/'scope.json'),all_members_reopened_and_hashed=True,member_manifest_exact=True,originals_rechecked_unchanged=True,all_selected_regular_files_captured=True,excluded_ignored_files=len(excluded),member_headers_verified=True,no_external_expansion=True,affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR']))
 print((HERE/'verification.json').read_text())
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),archive_attempt_preserved=True));raise
