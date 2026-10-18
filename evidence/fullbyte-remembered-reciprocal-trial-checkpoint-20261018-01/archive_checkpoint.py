"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-fullbyte-remembered-reciprocal-trial.tar.gz'
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
 nv=E/'fullbyte-remembered-reciprocal-native-validation-20261018-01';native=load(nv/'result.json')
 assert native['complete'] and native['total_tests']==179 and native['tests']['lib']['passed']==177 and native['tests']['dev']['passed']==2
 assert all(row['exit_code']==0 and row['actual_child_return_observed'] for row in native['commands'])
 for item in native['tests'].values():included(item['executable'],item['sha256'])
 generic=E/'fullbyte-remembered-reciprocal-generic-build-20261018-01';basis=load(generic/'receipt.json')
 assert basis['binary_output']['sha256']=='40b26a4d8802c6f7124ae76f19e9898df911f0414438d63f38ba6dd1294566cc'
 included(generic/'rook2-exact',basis['binary_output']['sha256'])
 source=basis['source_sha256_before']|basis['tool_sha256_before'];assert len(source)==69
 assert basis['source_sha256_before']==basis['source_sha256_after'] and basis['tool_sha256_before']==basis['tool_sha256_after']
 for name,h in source.items():included(generic/'source-before'/name,h)
 ar=load(generic/'archive-receipt.json');assert ar['files']==69;included(generic/ar['archive'],ar['sha256'])
 reg=E/'fullbyte-remembered-reciprocal-regression-20261018-01';rr=load(reg/'result.json')
 assert rr['complete'] and rr['strict54_pass'] and rr['interruption_fixtures']==8 and rr['interruption_searches']==24
 strict=load(reg/'strict54.stdout');assert len(strict['results'])==54 and strict['status']=='pass'
 wire=load(reg/'wire/receipt.json');assert wire['pass'] and len(wire['results'])==8 and sum(len(x['searches']) for x in wire['results'])==24
 for case in wire['results']:
  for name,item in case['raw'].items():included(reg/'wire'/case['id']/(name+'.raw'),item['sha256'])
 functional=E/'fullbyte-remembered-reciprocal-independent-preparation-20261018-01/independent-verification.json'
 assert included(functional)['sha256']=='474d1db408a2da6c37590a55f1063c19203a7ef31afb9295869e0ab590ebfa79'
 assert load(functional)['complete'] and load(functional)['native_tests']==179
 pilot=E/'fullbyte-remembered-reciprocal-cpu-pilot-20261018-01';plan=load(pilot/'plan.json')
 independent=E/'fullbyte-remembered-reciprocal-cpu-independent-preparation-20261018-01/independent-reconciliation.json';ind=load(independent)
 assert included(independent)['sha256']=='d268a3684ae94fae3d0b85a15c857b77fa95661c26d927b8f9a63478388afb3a'
 assert ind['complete'] and ind['normal_lifetimes']==70 and ind['original_checkReplay']==70 and ind['warmups_excluded']==14 and ind['measured']==56
 assert not ind['advance_rule_satisfied'] and ind['rule_outcome']=='park' and ind['lower_case_medians']==4
 assert ind['frozen_rule']==plan['advance_rule'] and all(x['range_relation']=='overlap' for x in ind['cases'])
 for variant in plan['variants'].values():included(variant['path'],variant['sha256'])
 assert plan['variants']['baseline']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 actual=load(pilot/'tool-terminal.json');assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0
 assert actual['session_id']==95851 and actual['terminal_chunk_id']=='c795d0'
 independent_actual=load(independent.parent/'tool-terminal.json');assert independent_actual['actual_tool_terminal_observed'] and independent_actual['exit_code']==0 and independent_actual['terminal_chunk_id']=='d9aa6a'
 records=sorted(pilot.glob('profile-*/*/native.json'));assert len(records)==70
 for record in records:
  included(record);data=load(record);assert data['native_exit_code']==0 and data['exec_error'] is None and data['failure'] is None
  assert data['engine_sha256_before']==data['engine_sha256_after']==plan['variants']['baseline' if record.parent.name.endswith('baseline') else 'candidate']['sha256']
  included(record.parent/'comparator.stdout');included(record.parent/'comparator.stderr')
 oracle=load(independent.parent/'original-checkReplay70-result.json');assert oracle['complete'] and oracle['original_oracle_calls']==70
 prep=E/'fullbyte-remembered-reciprocal-cpu-preparation-20261018-01'
 for name in ['preparation-failure-e08b39.json','inverse-assertion-correction.md','launch-clearance.before-future-authority-fix.json','launch-clearance.before-parent-approval.json']:included(prep/name)
 backend=E/'fullbyte-remembered-reciprocal-codegen-review-20261018-01/review.md'
 assert included(backend)['sha256']=='f2826bb69afb1abf70761a74b0e950d5a93cc75aebdd76f46780e2028a2a807b'
 return dict(whole_closed_trial_trees=11,reference_dependency_paths=len(SCOPE['reference_dependencies']),external_regular_payloads=len(EXTRAS),explicit_symlink_resolutions=SCOPE['explicit_symlink_resolutions'],native179_images_raw_tests_source69_archive_included=True,strict54_wire8_searches24_all_raw_included=True,pilot_actual=actual,independent_actual=independent_actual,all70_lifetimes_and14_warmups_preserved=True,decision='park; no own-PGO/retry/composition',aggregate_ratio=ind['aggregate_ratio'],lower_case_medians=4,all7_ranges_overlap=True,control948_explicitly_included=plan['variants']['baseline'],initial_failure_and_authority_correction_snapshots_included=True,all_regular_files_in_selected_trees=True,no_unrelated_whole_tree_or_opaque_census=True,qualification=False)

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
