#!/usr/bin/env python3
"""Closed52 generic evidence only; stream/reopen all bytes and independently justify source duplicates."""
from pathlib import Path, PurePosixPath
import hashlib,json,os,stat,sys,tarfile,gzip
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREFIX='activity-separated-boundary-'
DATE='-20261020-01'
TREES=[PREFIX+s+DATE for s in ['feasibility','parent-selection','kernel-preparation','test-preparation','parent-review','backend-preparation','generic-build','focused-preparation','focused-native-check','generic-screen-preparation','generic-screen','generic-decision']]
BUILD=ROOT/(PREFIX+'generic-build'+DATE)
def digest(f):
 h=hashlib.sha256();n=0
 for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def sha(p):
 with Path(p).open('rb') as f:return digest(f)[0]
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def safe(name):
 p=PurePosixPath(name)
 assert not p.is_absolute() and p.as_posix()==name and all(x not in ['.','..'] for x in p.parts),name
 return name
def inventory():
 rows={}
 for tree in TREES:
  root=ROOT/tree;assert root.is_dir() and not root.is_symlink(),root
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink(),p
   s=p.lstat()
   if stat.S_ISDIR(s.st_mode):continue
   assert stat.S_ISREG(s.st_mode),p
   name=safe(p.relative_to(ROOT).as_posix());assert name not in rows
   with p.open('rb') as f:h,n=digest(f)
   assert n==s.st_size
   rows[name]=dict(bytes=n,sha256=h,mode=stat.S_IMODE(s.st_mode))
 return dict(sorted(rows.items()))
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b

def source_archive_proof(originals):
 receipt=json.loads((BUILD/'receipt.json').read_text())
 archived=json.loads((BUILD/'archive-receipt.json').read_text())
 frozen=json.loads((BUILD/'frozen-image.json').read_text())
 assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot'
 assert receipt['source_sha256_before']==receipt['source_sha256_after']
 assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
 expected=receipt['source_sha256_before']|receipt['tool_sha256_before']
 assert len(receipt['source_sha256_before'])==52 and len(receipt['tool_sha256_before'])==23 and len(expected)==75
 source_archive=BUILD/'verified-source-before.tar.gz'
 assert sha(source_archive)==archived['sha256']
 assert archived['files']==75
 actual={}
 with tarfile.open(source_archive,'r:gz') as t:
  members=t.getmembers();assert len(members)==75
  for member in members:
   name=safe(member.name)
   assert member.isfile() and name in expected and name not in actual,name
   with t.extractfile(member) as stream:h,n=digest(stream)
   assert h==expected[name] and n==member.size,name
   original_name=(BUILD/'source-before'/name).relative_to(ROOT).as_posix()
   row=dict(bytes=n,sha256=h,archive_mode=stat.S_IMODE(member.mode),current_source_mode=originals[original_name]['mode'])
   assert originals[original_name]['bytes']==n and originals[original_name]['sha256']==h,name
   actual[name]=row
 prefix=(BUILD/'source-before').relative_to(ROOT).as_posix()+'/'
 assert {name for name in originals if name.startswith(prefix)}=={prefix+name for name in expected}
 image_name=(BUILD/'rook2-exact').relative_to(ROOT).as_posix()
 image=originals[image_name]
 assert image['sha256']==frozen['sha256']==receipt['binary_output']['sha256']==archived['binary_sha256']=='62c52b3d1c56c538940ae15045de60698e40a69b6ab53406226c1602a26cea09'
 assert image['bytes']==frozen['bytes']==7092264 and image['mode']==int(frozen['mode'],8)==0o555
 proof=dict(complete=True,source_archive=str(source_archive),source_archive_sha256=sha(source_archive),source_archive_bytes=source_archive.stat().st_size,member_count=75,all_regular=True,no_extra_or_duplicate_members=True,all_member_bytes_hashes_equal_current_source_before=True,archive_and_current_source_modes_recorded_separately=True,all_source_hashes_equal_build_before_after=True,members=actual,excluded_image=dict(path=str(BUILD/'rook2-exact'),**image),limit='Exact ELF retained externally and excluded by assignment. Source-before files are byte-exact duplicates of the included verified75-source archive; historical source archive headers normalize modes0644 while current snapshot modes are recorded separately per member. Reconstruct payload from source archive then chmod to current_source_mode. Source archive independently reopened, not receipt-only.')
 return proof,{prefix+name for name in expected}|{image_name}

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 original_before=inventory()
 proof,excluded=source_archive_proof(original_before)
 assert len(excluded)==76 and excluded<=original_before.keys()
 before={k:v for k,v in original_before.items() if k not in excluded}
 write('original-scope-manifest.json',original_before)
 write('source-archive-duplicate-proof.json',proof)
 write('excluded-manifest.json',{k:dict(**original_before[k],reason='Exact ELF excluded by assignment' if k.endswith('/rook2-exact') else 'Exact duplicate source payload independently reopened in included verified-source-before.tar.gz; reconstruct with recorded original mode',reconstruction_mode=original_before[k]['mode']) for k in sorted(excluded)})
 write('member-manifest.json',before)
 decision_terminal=(ROOT/(PREFIX+'generic-decision'+DATE)/'tool-terminal.json').relative_to(ROOT).as_posix()
 assert decision_terminal in before
 write('scope.json',dict(complete_closed_trees=TREES,external_payload_expansion=False,own_checkpoint_excluded=True,all_selected_regular_files_captured_except_exact76=True,files=len(before),captured_original_bytes=sum(x['bytes'] for x in before.values()),original_scope_files=len(original_before),excluded_files=76,duplicate_source_files=75,source_archive_proof_sha256=sha(HERE/'source-archive-duplicate-proof.json'),decision_tool_terminal_included=decision_terminal,scope='Closed52 generic source/backend/focused13/fixed70 PARK evidence only; no ownPGO/full199/broad-suite/promotion. Referenced external runtime payloads are not expanded.'))
 archive=HERE/'closed-activity-separated-boundary-generic.tar.gz'
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
 with archive.open('rb') as f:
  header=f.read(10);assert header[:3]==b'\x1f\x8b\x08' and header[3]==0 and header[4:8]==b'\x00'*4
 with tarfile.open(archive,'r:gz') as t:
  members=t.getmembers();assert len(members)==len(before)
  for member in members:
   assert member.isfile() and safe(member.name) in before and member.name not in reopened
   assert member.mtime==0 and member.uid==member.gid==0 and member.uname==member.gname==''
   assert set(member.pax_headers)<= {'path'},member.pax_headers
   with t.extractfile(member) as f:h,n=digest(f)
   assert member.size==n
   reopened[member.name]=dict(bytes=n,sha256=h,mode=stat.S_IMODE(member.mode))
 assert reopened==before
 assert inventory()==original_before,'original closed inputs or exclusions changed'
 proof_after,excluded_after=source_archive_proof(original_before)
 assert proof_after==proof and excluded_after==excluded
 write('verification.json',dict(complete=True,archive=archive.name,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,file_count=len(before),original_bytes=sum(x['bytes'] for x in before.values()),member_manifest_sha256=sha(HERE/'member-manifest.json'),original_scope_manifest_sha256=sha(HERE/'original-scope-manifest.json'),excluded_manifest_sha256=sha(HERE/'excluded-manifest.json'),scope_sha256=sha(HERE/'scope.json'),source_archive_duplicate_proof_sha256=sha(HERE/'source-archive-duplicate-proof.json'),all_members_reopened_and_hashed=True,all_member_headers_modes_sizes_hashes_exact=True,gzip_mtime_zero=True,deterministic_sorted_tar_headers=True,member_manifest_exact=True,originals_and_exclusions_rechecked_unchanged=True,source75_archive_independently_reopened_twice=True,all_selected_regular_files_captured_except_exact76=True,no_external_expansion=True,affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ['TMPDIR']))
 print((HERE/'verification.json').read_text())
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure-02.json',dict(error=repr(error),archive_attempt_preserved=True));raise
