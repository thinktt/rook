"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-ordinary-projected-bits-candidate25-final.tar.gz'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(path):return json.loads(path.read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,separators=(',',':'));f.write('\n')
def member_name(path):
 try:name=path.relative_to(REPO).as_posix()
 except ValueError:name='external/'+path.as_posix().lstrip('/')
 assert name and not Path(name).is_absolute() and all(x not in ['.','..'] for x in Path(name).parts)
 return name
def symlink_components(path):
 return [dict(path=str(p),target=os.readlink(p)) for p in [*reversed(path.parents),path] if p.is_symlink()]
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
 assert len(files)==len(set(files))
 assert {str(path) for path in files}==set(SCOPE['closed_tree_regular_files'])|{str(path) for path in EXTRAS}
 assert sorted(directories)==SCOPE['closed_tree_directories']
 rows=[]
 for path in sorted(files,key=member_name):
  member=member_name(path);assert not Path(member).is_absolute() and '..' not in Path(member).parts
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
 def included(path,digest=None):
  path=Path(path);resolved=path.resolve(strict=True);row=by_path[str(resolved)]
  if digest is not None:assert row['sha256']==digest,str(path)
  return row
 for ref in SCOPE['reference_dependencies']:
  path=Path(ref['path']);assert path.resolve(strict=True)==Path(ref['resolved_regular_source'])
  assert symlink_components(path)==ref['symlink_components']
  assert included(path,ref['sha256'])['archive_member']==ref['archive_member']
 assert sha(Path(SCOPE['preservation_plan']))==SCOPE['preservation_plan_sha256']
 approval=load(HERE/'parent-whitelist-approval.json');assert approval['parent_approved'] is True
 assert approval['included_scope_sha256']==sha(HERE/'included-scope.json')
 assert approval['preflight_member_manifest_sha256']==sha(HERE/'preflight-member-manifest.json')
 assert approval['archive_writer_sha256']==sha(Path(__file__))
 preflight=load(HERE/'preflight-summary.json');assert preflight['complete'] and not preflight['archive_created']
 assert (len(ROOTS),len(rows),sum(row['bytes'] for row in rows),len(EXTRAS))==(17,preflight['regular_members'],preflight['source_bytes'],preflight['explicit_extra_regular_payloads'])
 assert rows==load(HERE/'preflight-member-manifest.json')['members']
 cpu_path=E/'ordinary-projected-bits-pgo-cpu-independent-preparation-20261018-01/independent-reconciliation.json'
 included(cpu_path,'895e58549474bc1385188b459fd75c6e0b647bf9ee33b10d90c4a59ce704aa4d');cpu=load(cpu_path)
 assert cpu['complete'] and cpu['normal_lifetimes']==cpu['original_checkReplay']==70 and cpu['warmups_excluded']==14 and cpu['measured']==56
 assert len(cpu['dependencies'])==2030 and cpu['advance_rule_satisfied'] and cpu['lower_case_medians']==7
 F=E/'ordinary-projected-bits-final-validation-preparation-20261018-01';final=load(F/'validation-summary.json');ind=load(F/'reconciliation/independent-verification.json');gate=load(F/'pregate/independent-raw-reconciliation.json')
 assert final['cases']==ind['diagnostic_cases']==7673 and final['diagnostic_units']==ind['diagnostic_units']==209
 assert final['native_units']==178 and final['operations']==117 and final['whole_files']==115
 assert ind['status']=='pass' and ind['all_raw_expected_and_actual_equal'] and ind['all_native_child_exits_confirmed']
 assert gate['complete'] and gate['independentGames']==12 and gate['independentSearches']==632 and gate['continuousSearches']==8
 pgo=E/'ordinary-projected-bits-pgo-use-build-20261018-01';included(pgo/'rook2-exact','51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a')
 included(F/'diagnostic-build/rook2-diag-exact','f1f7f5d9c899ebf3881d4033f437f7780e8f9bcf542d10db14a7f37d804ebb79')
 raw=[p for p in by_path if str(F/'diagnostic/raw-cases')+'/' in p];assert len(raw)==30693
 training=load(E/'ordinary-projected-bits-pgo-training-20261018-01/training.json');assert training['complete'] and len(training['raw_profiles_sha256'])==54
 for path,digest in training['raw_profiles_sha256'].items():included(path,digest)
 hand=load(E/'candidate25-binary-handoff-20261018-01/manifest.json');assert hand['candidate']==25 and len(hand['package_members'])==2
 for item in hand['package_members'].values():included(item['path'],item['sha256']);included(item['origin'],item['sha256'])
 declaration=E/'ordinary-projected-bits-pgo-cpu-plan-20261018-01/plan.json';included(declaration,'83ad9ecca4ff5207dd362e3f2645465350e3e52e2e038d7f505bfc3a107cb27b')
 return dict(whole_closed_trial_trees=17,reference_dependency_paths=len(SCOPE['reference_dependencies']),external_regular_payloads=len(EXTRAS),explicit_symlink_resolutions=SCOPE['explicit_symlink_resolutions'],own54_profile_raw_and_both_builds_preserved=True,all70_cpu_lifetimes_preserved=True,full117_all_regular_raw_files_preserved=True,diagnostic_raw_case_files=len(raw),pregate12_searches632_continuity8_preserved=True,source_and_individual_consumed_dependencies_preserved=True,handoff_two_images_preserved=True,no_unrelated_whole_tree_private_raw_census_opaque_root_git=True,parent_whitelist_approval_sha256=sha(HERE/'parent-whitelist-approval.json'),qualification=False)

def main():
 result=dict(complete=False,failure=None,affinity=sorted(os.sched_getaffinity(0)),no_native_compiler_profiler_timing_git_subprocesses=True)
 try:
  assert result['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13] and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
  scope_sha256=sha(HERE/'included-scope.json')
  assert not ARCHIVE.exists() and not (HERE/'member-manifest.json').exists()
  rows,dirs=inventory();proof=coverage(rows);total=sum(row['bytes'] for row in rows)
  manifest=dict(scope={'complete_trees':[str(root) for root in ROOTS],'explicit_extra_files':[str(path) for path in EXTRAS],'checkpoint_self_excluded':str(HERE),'no_hidden_or_ignored_file_filter':True,'regular_file_members_only':True,'directories_omitted_as_tar_entries_but_enumerated':dirs,'unsupported_nonregular_entries':[],'exclusions':[],'included_scope_sha256':scope_sha256,'explicit_external_symlink_resolutions':SCOPE['explicit_symlink_resolutions']},file_count=len(rows),source_bytes=total,members=rows)
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
  assert sha(HERE/'included-scope.json')==scope_sha256
  result.update(complete=True,archive=ARCHIVE.name,archive_sha256=sha(ARCHIVE),archive_bytes=ARCHIVE.stat().st_size,manifest='member-manifest.json',manifest_sha256=sha(HERE/'member-manifest.json'),manifest_bytes=(HERE/'member-manifest.json').stat().st_size,member_count=len(rows),source_bytes=total,reopened_full_member_equality=True,source_original_hashes_and_inventory_unchanged=True,all_regular_files_included=True,no_exclusions=True,determinism='Sorted safe repository-relative or external/ names; fixed uid/gid/uname/gname/mtime and gzip mtime/filename; source mode/bytes manifest-bound; explicit external symlink resolution retained',coverage=proof)
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}';result['traceback']=traceback.format_exc()
 finally:write('verification.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='coverage'}),flush=True)
 return 0 if result['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
