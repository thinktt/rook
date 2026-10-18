"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-placement-pure-cache-own-pgo.tar.gz'
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
 preflight=load(HERE/'preflight-summary.json')
 assert preflight['complete'] and not preflight['archive_created']
 assert (len(ROOTS),len(rows),sum(row['bytes'] for row in rows),len(EXTRAS))==(14,preflight['regular_members'],preflight['source_bytes'],preflight['explicit_extra_regular_payloads'])
 assert rows==load(HERE/'preflight-member-manifest.json')['members']
 manifest=load(E/'placement-pure-cache-proposal-20261018-01/source-manifest.json')
 assert manifest['graph_sha256']=='e784334543d6045f6952ce5d2b636b6e185705ebfbcf633bdb499e5549996937'
 source=manifest['files'];assert len(source)==69
 generic=E/'placement-pure-cache-independent-preparation-20261018-01/independent-verification.json';included(generic)
 assert load(generic)['complete'] and load(generic)['native_tests']==184
 native_path=E/'placement-pure-cache-native-validation-20261018-01/result.json';included(native_path);native=load(native_path)
 assert native['complete'] and native['total_tests']==184 and native['tests']['lib']['passed']==182 and native['tests']['dev']['passed']==2
 for item in native['tests'].values():included(item['executable'],item['sha256'])
 prep=E/'placement-pure-cache-pgo-preparation-20261018-01';plan=load(prep/'plan.json')
 tr=Path(plan['training']);ib=Path(plan['instrumented_build']);ub=Path(plan['use_build']);check=Path(plan['use_check']);wire=Path(plan['wire']);reconciliation=Path(plan['reconciliation'])
 for directory in [ib,tr,ub,check,reconciliation]:
  actual=load(directory/'tool-terminal.json');assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0
 verifier=load(tr/'verify-tool-terminal.json');assert verifier['actual_tool_terminal_observed'] and verifier['exit_code']==0
 for directory in [ib,ub]:
  receipt=load(directory/'receipt.json')
  assert receipt['source_sha256_before']==receipt['source_sha256_after']==plan['engine_source_sha256']
  assert receipt['tool_sha256_before']==receipt['tool_sha256_after']==plan['tool_source_sha256']
  included(directory/'rook2-exact',receipt['binary_output']['sha256'])
  for name,h in source.items():included(directory/'source-before'/name,h)
  ar=load(directory/'archive-receipt.json');assert ar['files']==69;included(directory/ar['archive'],ar['sha256'])
  with tarfile.open(directory/ar['archive'],'r:gz') as archive:
   nested={}
   for member in archive:
    assert member.isfile() and member.name in source and member.name not in nested
    nested[member.name]=hashlib.sha256(archive.extractfile(member).read()).hexdigest()
   assert nested==source
 training=load(tr/'training.json');verified=load(tr/'verification.json');raws=training['raw_profiles_sha256']
 assert training['complete'] and len(raws)==54 and verified['complete'] and verified['independent_remerge_byte_identical']
 assert verified['strict_replays']==verified['raw_profiles_independently_hashed']==54
 for path,h in raws.items():included(path,h)
 included(tr/'merged.profdata',training['profile_sha256'])
 assert training['profile_sha256']=='42d43e87b27660a6626c44048c95c00cfce0e1012b92165ec4d97f3adfa8528c'
 assert training['profile_sha256']==verified['merged_profile_sha256']
 proof=load(reconciliation/'independent-verification.json');assert proof['complete'] and proof['own_profile_only'] and proof['strict_training54'] and proof['fresh_strict54'] and proof['wire8_searches24']
 assert set(proof['variants'])=={'placement-pure-cache'};row=proof['variants']['placement-pure-cache']
 assert row['artifact_sha256']=='abe793bbd11c1c24c020f8f9ba6af44f1e1f4ca0f62244481820804b546ed5ab'
 assert row['profile_sha256']==training['profile_sha256'] and row['profile_independently_remerged']
 assert row['training_strict_replays']==row['post_use_strict_replays']==row['raw_profiles']==54
 original=load(reconciliation/'original-checkReplay.stdout');assert original['offlineOnly'] and original['originalCheckReplayCount']==108
 strict=load(check/'profile-all.stdout');assert strict['status']=='pass' and len(strict['results'])==54
 wr=load(wire/'receipt.json');assert wr['pass'] and len(wr['results'])==8 and sum(len(x['searches']) for x in wr['results'])==24
 for case in wr['results']:
  for name,item in case['raw'].items():included(wire/case['id']/(name+'.raw'),item['sha256'])
 pilot=E/'placement-pure-cache-pgo-cpu-pilot-20261018-01';cpuplan=load(pilot/'plan.json')
 independent=E/'placement-pure-cache-pgo-cpu-independent-preparation-20261018-01/independent-reconciliation.json';ind=load(independent)
 included(independent,'587ca7a3d6d40882a5b1ca4376d7e53a146479ece7315340f36160e37d592c9c')
 assert ind['complete'] and ind['normal_lifetimes']==ind['original_checkReplay']==70 and ind['warmups_excluded']==14 and ind['measured']==56
 assert not ind['advance_rule_satisfied'] and ind['aggregate_ratio']>0.995 and ind['lower_case_medians']==5 and ind['worst_case_ratio']<=1.02
 assert ind['frozen_rule']==cpuplan['advance_rule']
 for variant in cpuplan['variants'].values():included(variant['path'],variant['sha256'])
 assert cpuplan['variants']['baseline']['sha256']=='79d19ebe1b01fbe94dbf03025140b292807ecf6acdc181a52a5d1849bbc478df'
 assert cpuplan['variants']['candidate']['sha256']==row['artifact_sha256']
 actual=load(pilot/'tool-terminal.json');assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0 and actual['session_id']==10663 and actual['terminal_chunk_id']=='a247d8'
 ia=load(independent.parent/'tool-terminal.json');assert ia['actual_tool_terminal_observed'] and ia['exit_code']==0 and ia['session_id']==92206 and ia['terminal_chunk_id']=='228361'
 records=sorted(pilot.glob('profile-*/*/native.json'));assert len(records)==70
 for record in records:
  data=load(record);assert data['native_exit_code']==0 and data['exec_error'] is None and data['failure'] is None
  assert data['engine_sha256_before']==data['engine_sha256_after']==cpuplan['variants']['baseline' if record.parent.name.endswith('baseline') else 'candidate']['sha256']
  included(record);included(record.parent/'comparator.stdout');included(record.parent/'comparator.stderr')
 assert load(independent.parent/'original-checkReplay70-result.json')['original_oracle_calls']==70
 decision_path=E/'placement-pure-cache-pgo-decision-20261018-01/decision.json';included(decision_path,'ee540633465f55db8e14d25ff1e73a46d36b0047030cba8903884fc33dae292b');decision=load(decision_path)
 assert decision['decision']=='park' and not decision['source_promotion'] and decision['no_resize_retry_relaxation_or_composition']
 assert decision['full117_preparation_unexecuted_and_unapproved'] and decision['full117_execution_copy_absent']
 future=E/'placement-pure-cache-complete117-preparation-20261018-01'
 selected_future={path for path in by_path if future in Path(path).parents}
 assert selected_future=={str(future/'execution-clearance.json'),str(future/'validation-plan.json')}
 return dict(whole_closed_trial_trees=14,reference_dependency_paths=len(SCOPE['reference_dependencies']),external_regular_payloads=len(EXTRAS),explicit_symlink_resolutions=SCOPE['explicit_symlink_resolutions'],native184_generic_proof_and_images_included=True,own54_raw_profiles_PIDs_remerge_use54_wire24_original108_included=True,both_source69_build_archives_reopened=True,pilot_actual=actual,independent_actual=ia,all70_lifetimes_14warmups_56measured_preserved=True,decision='PARK: own-PGO aggregate ratio misses frozen .995; no full117 execution/retry/promotion',aggregate_ratio=ind['aggregate_ratio'],lower_case_medians=ind['lower_case_medians'],worst_case_ratio=ind['worst_case_ratio'],control79d_and_candidateabe_included=cpuplan['variants'],failures_and_real_terminals_all_in_closed_trees=True,full117_whole_preparation_omitted_only_two_inert_inputs_individual=True,all_regular_files_in_selected_trees=True,no_unrelated_whole_tree_or_opaque_census_root_git=True,parent_whitelist_approval_sha256=sha(HERE/'parent-whitelist-approval.json'),qualification=False)

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
