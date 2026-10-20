#!/usr/bin/env python3
"""Closed51 functional trees only; deterministic gzip, full reopen/original recheck."""
from pathlib import Path
import gzip,hashlib,json,os,stat,sys,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TREES=[
 'tactical-check-mask-conformance-preparation-20261020-01',
 'tactical-check-mask-conformance-20261020-01',
 'tactical-check-mask-conformance-build-20261020-01',
 'tactical-check-mask-postuse-validation-preparation-20261020-01',
 'tactical-check-mask-postuse-validation-20261020-01',
 'tactical-check-mask-pregate-preparation-20261020-01',
 'tactical-check-mask-pregate-20261020-01',
]
EXACT_EXCLUSIONS={
 'tactical-check-mask-conformance-preparation-20261020-01/full-native193/unit-bin/rook2/unit-exact':'native library unit ELF explicitly excluded',
 'tactical-check-mask-conformance-preparation-20261020-01/full-native193/unit-bin/rook2-dev/unit-exact':'native development unit ELF explicitly excluded',
 'tactical-check-mask-conformance-preparation-20261020-01/diagnostic-build-check/unit-bin/rook2-diag/unit-exact':'diagnostic unit ELF explicitly excluded',
 'tactical-check-mask-conformance-build-20261020-01/rook2-diag-exact':'diagnostic ELF explicitly excluded',
}
DUPLICATE_PREFIX='tactical-check-mask-conformance-build-20261020-01/source-before/'
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
   reason=EXACT_EXCLUSIONS.get(name)
   if name.startswith(DUPLICATE_PREFIX):reason='duplicate extracted frontend source-before; exact existing tar retained'
   if reason:
    with p.open('rb') as f:magic=f.read(4)
    if name in EXACT_EXCLUSIONS:assert magic==b'\x7fELF',name
    s=p.stat();excluded[name]=dict(bytes=s.st_size,mode=stat.S_IMODE(s.st_mode),sha256=sha(p),reason=reason)
    continue
   with p.open('rb') as f:
    assert f.read(4)!=b'\x7fELF',('unexpected selected ELF',name)
    f.seek(0);h,n=digest(f)
   s=p.stat();assert n==s.st_size
   rows[name]=dict(bytes=n,sha256=h,mode=stat.S_IMODE(s.st_mode))
 assert set(EXACT_EXCLUSIONS)<=set(excluded)
 assert sum(n.startswith(DUPLICATE_PREFIX) for n in excluded)==43
 return dict(sorted(rows.items())),dict(sorted(excluded.items()))
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 before,excluded=inventory();write('member-manifest.json',before);write('excluded-members.json',excluded)
 write('scope.json',dict(complete_closed_trees=TREES,exact_exclusions=EXACT_EXCLUSIONS,duplicate_prefix=DUPLICATE_PREFIX,external_payload_expansion=False,own_checkpoint_excluded=True,files=len(before),excluded_files=len(excluded),original_bytes=sum(x['bytes'] for x in before.values()),scope='Closed51 functional evidence only; excluded test/adapter ELF and duplicate extracted source; not self-contained deployment or qualification'))
 archive=HERE/'closed-tactical-check-mask-functional.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',compresslevel=6,fileobj=raw,mtime=0) as gz:
   with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as t:
    for name,row in before.items():
     source=ROOT/name;info=t.gettarinfo(str(source),arcname=name)
     assert info.isfile() and info.size==row['bytes'] and stat.S_IMODE(info.mode)==row['mode']
     info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';info.pax_headers={}
     with source.open('rb') as f:
      reader=HashReader(f);t.addfile(info,reader)
      assert reader.n==row['bytes'] and reader.h.hexdigest()==row['sha256'],name
 reopened={}
 with tarfile.open(archive,'r|gz') as t:
  for member in t:
   assert member.isfile() and member.name in before and member.name not in reopened
   assert member.uid==member.gid==member.mtime==0 and member.uname==member.gname==''
   with t.extractfile(member) as f:h,n=digest(f)
   reopened[member.name]=dict(bytes=n,sha256=h,mode=stat.S_IMODE(member.mode))
 assert reopened==before
 after,excluded_after=inventory();assert after==before,'original closed selected inputs changed'
 assert excluded_after==excluded,'excluded inventory changed'
 write('verification.json',dict(complete=True,archive=archive.name,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,file_count=len(before),original_bytes=sum(x['bytes'] for x in before.values()),member_manifest_sha256=sha(HERE/'member-manifest.json'),scope_sha256=sha(HERE/'scope.json'),all_members_reopened_and_hashed=True,member_manifest_exact=True,originals_rechecked_unchanged=True,all_selected_regular_files_captured=True,excluded_files=len(excluded),no_external_expansion=True,deterministic_metadata=dict(gzip_mtime=0,gzip_filename='',tar_mtime=0,uid=0,gid=0,uname='',gname='',pax_headers='empty except deterministic long-path handling',order='sorted relative names'),affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR']))
 print((HERE/'verification.json').read_text())
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),archive_attempt_preserved=True));raise
