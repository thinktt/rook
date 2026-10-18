"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-full-byte-pair-relations-trial.tar.gz'
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
 nv=E/'full-byte-pair-relations-native-validation-20261018-01';native=load(nv/'result.json')
 assert native['complete'] and native['total_tests']==178 and native['tests']['lib']['passed']==176 and native['tests']['dev']['passed']==2
 assert all(row['exit_code']==0 and row['actual_child_return_observed'] for row in native['commands'])
 for item in native['tests'].values():included(item['executable'],item['sha256'])
 generic=E/'full-byte-pair-relations-generic-build-20261018-01';basis=load(generic/'receipt.json')
 assert basis['binary_output']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 for directory in [generic,E/'full-byte-pair-relations-pgo-instrumented-build-20261018-01',E/'full-byte-pair-relations-pgo-use-build-20261018-01']:
  receipt=load(directory/'receipt.json');included(directory/'rook2-exact',receipt['binary_output']['sha256'])
  source=receipt['source_sha256_before']|receipt['tool_sha256_before'];assert len(source)==69
  assert receipt['source_sha256_before']==receipt['source_sha256_after']==basis['source_sha256_before'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']==basis['tool_sha256_before']
  for name,h in source.items():included(directory/'source-before'/name,h)
  ar=load(directory/'archive-receipt.json');assert ar['files']==69;included(directory/ar['archive'],ar['sha256'])
 reg=E/'full-byte-pair-relations-regression-20261018-01';rr=load(reg/'result.json')
 assert rr['complete'] and rr['strict54_pass'] and rr['interruption_fixtures']==8 and rr['interruption_searches']==24
 strict=load(reg/'strict54.stdout');assert len(strict['results'])==54 and strict['status']=='pass'
 wire=load(reg/'wire/receipt.json');assert wire['pass'] and len(wire['results'])==8 and sum(len(x['searches']) for x in wire['results'])==24
 for case in wire['results']:
  for name,item in case['raw'].items():included(reg/'wire'/case['id']/(name+'.raw'),item['sha256'])
 pilots=[]
 for stem in ['full-byte-pair-relations-cpu','full-byte-pair-relations-pgo-cpu']:
  pilot=E/(stem+'-pilot-20261018-01');plan=load(pilot/'plan.json')
  independent=E/(stem+'-independent-preparation-20261018-01/independent-reconciliation.json');ind=load(independent)
  assert ind['complete'] and ind['normal_lifetimes']==70 and ind['original_checkReplay']==70 and ind['warmups_excluded']==14 and ind['measured']==56 and ind['advance_rule_satisfied']
  assert ind['frozen_rule']==plan['advance_rule']
  for variant in plan['variants'].values():included(variant['path'],variant['sha256'])
  actual=load(pilot/'tool-terminal.json');assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0
  records=sorted(pilot.glob('profile-*/*/native.json'));assert len(records)==70
  for record in records:
   included(record);data=load(record);assert data['native_exit_code']==0 and data['exec_error'] is None and data['failure'] is None
   assert data['engine_sha256_before']==data['engine_sha256_after']==plan['variants']['baseline' if record.parent.name.endswith('baseline') else 'candidate']['sha256']
   included(record.parent/'comparator.stdout');included(record.parent/'comparator.stderr')
  oracle=load(independent.parent/'original-checkReplay70-result.json');assert oracle['complete'] and oracle['original_oracle_calls']==70
  pilots.append(dict(path=str(pilot),normal_lifetimes=70,all_files_and_warmups_included=True,independent_sha256=included(independent)['sha256'],actual_terminal=actual))
 train=E/'full-byte-pair-relations-pgo-training-20261018-01';tr=load(train/'training.json');tv=load(train/'verification.json')
 assert tr['complete'] and tv['complete'] and tv['strict_replays']==54 and tv['raw_profiles_independently_hashed']==54 and tv['independent_remerge_byte_identical']
 assert len(tr['raw_profiles_sha256'])==54
 for path,h in tr['raw_profiles_sha256'].items():included(path,h)
 for path in [train/'merged.profdata',train/'independently-merged.profdata',E/'full-byte-pair-relations-pgo-reconciliation-20261018-01/full-byte-pair-relations-independently-merged.profdata']:included(path,tr['profile_sha256'])
 included(train/'merged.profdata.gz',tr['profile_archive_sha256'])
 ir=load(E/'full-byte-pair-relations-pgo-reconciliation-20261018-01/independent-verification.json')
 assert ir['complete'] and ir['own_profile_only'] and ir['strict_training54'] and ir['fresh_strict54'] and ir['wire8_searches24']
 controls={name:load(E/(stem+'-pilot-20261018-01/plan.json'))['variants']['baseline'] for name,stem in [('generic','full-byte-pair-relations-cpu'),('own_pgo','full-byte-pair-relations-pgo-cpu')]}
 return dict(whole_closed_trial_trees=23,selection_review_and_generator_included=True,reference_dependency_paths=len(SCOPE['reference_dependencies']),external_regular_payloads=len(EXTRAS),explicit_symlink_resolutions=SCOPE['explicit_symlink_resolutions'],native178_frozen_images_and_source69_builds_included=True,generic_native_candidate=basis['binary_output']['sha256'],strict54_wire8_searches24_all_raw_included=True,pilots=pilots,own_training54_raw_profiles_and_all_remerges_included=True,controls_explicitly_included=controls,backend_and_initial_failed_metadata_files_included_by_complete_tree_inventory=True,all_regular_files_in_selected_trees=True,active_complete117_and_other_trials_not_selected=True,qualification=False)

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
