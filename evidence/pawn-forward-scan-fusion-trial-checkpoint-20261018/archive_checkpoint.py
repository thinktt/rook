"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-pawn-forward-scan-fusion-trial.tar.gz'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(path):return json.loads(path.read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,separators=(',',':'));f.write('\n')
def inventory():
 files=[];directories=[];unsupported=[]
 for root in ROOTS:
  assert root.is_dir() and not root.is_symlink()
  for current,dirs,names in os.walk(root,followlinks=False,onerror=lambda error:(_ for _ in ()).throw(error)):
   directories.append(str(Path(current)))
   for name in dirs:
    path=Path(current)/name
    if not stat.S_ISDIR(path.lstat().st_mode):unsupported.append(str(path))
   for name in names:
    path=Path(current)/name
    if stat.S_ISREG(path.lstat().st_mode):files.append(path)
    else:unsupported.append(str(path))
 assert not unsupported,dict(unsupported_entries=unsupported,no_silent_exclusion=True)
 for path in EXTRAS:
  assert stat.S_ISREG(path.lstat().st_mode);files.append(path)
 rows=[]
 for path in sorted(files,key=lambda path:path.relative_to(REPO).as_posix()):
  member=path.relative_to(REPO).as_posix();assert not Path(member).is_absolute() and '..' not in Path(member).parts
  before=path.stat();digest=sha(path);after=path.stat()
  assert (before.st_size,before.st_mtime_ns,before.st_mode)==(after.st_size,after.st_mtime_ns,after.st_mode),str(path)
  rows.append(dict(source_path=str(path),archive_member=member,bytes=after.st_size,sha256=digest,mode=stat.S_IMODE(after.st_mode)))
 assert len({row['archive_member'] for row in rows})==len(rows)
 return rows,sorted(directories)
class HashReader:
 def __init__(self,file):self.file=file;self.hash=hashlib.sha256();self.bytes=0
 def read(self,size=-1):
  chunk=self.file.read(size);self.hash.update(chunk);self.bytes+=len(chunk);return chunk

def coverage(rows):
 by_path={row['source_path']:row for row in rows};E=REPO/'evidence'
 nv=E/'pawn-forward-scan-fusion-native-validation-20261018-01';native=load(nv/'result.json')
 assert native['complete'] and native['total_tests']==178 and native['tests']['lib']['passed']==176 and native['tests']['dev']['passed']==2
 assert all(row['exit_code']==0 and row['actual_child_return_observed'] for row in native['commands'])
 for item in native['tests'].values():assert by_path[item['executable']]['sha256']==item['sha256']
 build=E/'pawn-forward-scan-fusion-generic-build-20261018-01';receipt=load(build/'receipt.json')
 assert by_path[str(build/'rook2-exact')]['sha256']==native['engine_sha256']==receipt['binary_output']['sha256']=='541d324cecf14a401c868d1a7910f13efc00241d27d5ed5db100d0449f86148f'
 source=receipt['source_sha256_before']|receipt['tool_sha256_before'];assert len(source)==69
 for name,h in source.items():assert by_path[str(build/'source-before'/name)]['sha256']==h
 assert str(build/'verified-source-before.tar.gz') in by_path
 reg=E/'pawn-forward-scan-fusion-regression-20261018-01';rr=load(reg/'result.json')
 assert rr['complete'] and rr['strict54_pass'] and rr['interruption_fixtures']==8 and rr['interruption_searches']==24
 strict=load(reg/'strict54.stdout');assert len(strict['results'])==54 and strict['status']=='pass'
 wire=load(reg/'wire/receipt.json');assert wire['pass'] and len(wire['results'])==8
 for case in wire['results']:
  for name,item in case['raw'].items():assert by_path[str(reg/'wire'/case['id']/(name+'.raw'))]['sha256']==item['sha256']
 assert str(E/'pawn-forward-scan-fusion-validation-preparation-20261018-01/parent-overlap-correction.json') in by_path
 pilot=E/'pawn-forward-scan-fusion-cpu-pilot-20261018-01';plan=load(pilot/'plan.json')
 independent=E/'pawn-forward-scan-fusion-cpu-independent-preparation-20261018-01/independent-reconciliation.json'
 assert by_path[str(independent)]['sha256']=='92aa0e357c0fa924040fa6aaeadf84bcc0104c0cf428aa99c766632bb2d4f373'
 ind=load(independent);assert ind['complete'] and ind['normal_lifetimes']==70 and ind['original_checkReplay']==70
 assert ind['warmups_excluded']==14 and ind['measured']==56 and not ind['branch_A_satisfied'] and not ind['branch_B_satisfied'] and not ind['advance_rule_satisfied'] and ind['rule_outcome']=='park'
 assert ind['frozen_rule']==plan['advance_rule']
 for variant in plan['variants'].values():assert by_path[variant['path']]['sha256']==variant['sha256']
 actual=load(pilot/'tool-terminal.json');assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0 and actual['terminal_chunk_id']=='0fbb5c'
 records=sorted(pilot.glob('profile-*/*/native.json'));assert len(records)==70
 for record in records:
  assert str(record) in by_path;data=load(record)
  assert data['native_exit_code']==0 and data['exec_error'] is None and data['failure'] is None
  assert data['engine_sha256_before']==data['engine_sha256_after']==plan['variants']['baseline' if record.parent.name.endswith('baseline') else 'candidate']['sha256']
 return dict(native178_frozen_images_included=True,source69_basis_and_archive_included=True,candidate_sha256=native['engine_sha256'],extra_baseline=plan['variants']['baseline'],strict54_original_raw_included=True,eightwire24_all_receipt_raw_hashes_equal=True,overlap_correction_included=True,backend_captures_entire_directory=True,pilot70_native_records_and_all_directory_contents=True,fixed_rule_and_independent_hash=by_path[str(independent)]['sha256'],pilot_actual_terminal=actual,rule_outcome='park',branch_A=False,branch_B=False,no_activity_composition_or_qualification=True)

def main():
 result=dict(complete=False,failure=None,affinity=sorted(os.sched_getaffinity(0)),no_native_compiler_profiler_timing_git_subprocesses=True)
 try:
  assert result['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
  assert not ARCHIVE.exists() and not (HERE/'member-manifest.json').exists()
  rows,dirs=inventory();proof=coverage(rows);total=sum(row['bytes'] for row in rows)
  manifest=dict(scope={'complete_trees':[str(root) for root in ROOTS],'explicit_extra_files':[str(path) for path in EXTRAS],'checkpoint_self_excluded':str(HERE),'no_hidden_or_ignored_file_filter':True,'regular_file_members_only':True,'directories_omitted_as_tar_entries_but_enumerated':dirs,'unsupported_nonregular_entries':[],'exclusions':[]},file_count=len(rows),source_bytes=total,members=rows)
  write('member-manifest.json',manifest)
  print(json.dumps(dict(stage='original_inventory_closed',files=len(rows),bytes=total)),flush=True)
  # Deterministic ordering, canonical header ownership/time and gzip header.
  with ARCHIVE.open('xb') as compressed:
   with gzip.GzipFile(filename='',mode='wb',compresslevel=6,fileobj=compressed,mtime=0) as gz:
    with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as archive:
     for row in rows:
      info=tarfile.TarInfo(row['archive_member']);info.type=tarfile.REGTYPE;info.size=row['bytes'];info.mode=row['mode'];info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
      with Path(row['source_path']).open('rb') as f:
       reader=HashReader(f);archive.addfile(info,reader)
       assert reader.bytes==row['bytes'] and reader.hash.hexdigest()==row['sha256'],row['source_path']
  expected={row['archive_member']:row for row in rows};seen=set();unpacked=0
  with tarfile.open(ARCHIVE,'r:gz') as archive:
   for member in archive:
    assert member.isfile() and member.name in expected and member.name not in seen
    assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
    row=expected[member.name];assert member.size==row['bytes'] and member.mode==row['mode']
    assert member.mtime==member.uid==member.gid==0 and member.uname==member.gname==''
    h=hashlib.sha256();count=0
    with archive.extractfile(member) as f:
     for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk);count+=len(chunk)
    assert count==row['bytes'] and h.hexdigest()==row['sha256'];seen.add(member.name);unpacked+=count
  assert seen==set(expected) and unpacked==total
  after,after_dirs=inventory();assert after==rows and after_dirs==dirs
  assert coverage(after)==proof
  result.update(complete=True,archive=ARCHIVE.name,archive_sha256=sha(ARCHIVE),archive_bytes=ARCHIVE.stat().st_size,manifest='member-manifest.json',manifest_sha256=sha(HERE/'member-manifest.json'),manifest_bytes=(HERE/'member-manifest.json').stat().st_size,member_count=len(rows),source_bytes=total,reopened_full_member_equality=True,source_original_hashes_and_inventory_unchanged=True,all_regular_files_included=True,no_exclusions=True,determinism='Sorted repository-relative names; fixed uid/gid/uname/gname/mtime and gzip mtime/filename; source mode/bytes manifest-bound',coverage=proof)
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}';result['traceback']=traceback.format_exc()
 finally:write('verification.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='coverage'}),flush=True)
 return 0 if result['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
