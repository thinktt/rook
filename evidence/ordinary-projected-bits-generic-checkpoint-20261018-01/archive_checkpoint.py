"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-ordinary-projected-bits-generic.tar.gz'
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
 assert (len(ROOTS),len(rows),sum(row['bytes'] for row in rows),len(EXTRAS))==(14,preflight['regular_members'],preflight['source_bytes'],preflight['explicit_extra_regular_payloads'])
 assert rows==load(HERE/'preflight-member-manifest.json')['members']
 nv=E/'ordinary-projected-bits-native-validation-20261018-01';native=load(nv/'result.json')
 assert native['complete'] and native['total_tests']==178 and native['tests']['lib']['passed']==176 and native['tests']['dev']['passed']==2
 assert all(row['exit_code']==0 and row['actual_child_return_observed'] for row in native['commands'])
 for item in native['tests'].values():included(item['executable'],item['sha256'])
 generic=E/'ordinary-projected-bits-generic-build-20261018-01';basis=load(generic/'receipt.json')
 assert basis['binary_output']['sha256']=='2940ae5c003fa396b31639749b4c3ba29e52e8aebabfc96a7dde565b6d9abd04'
 included(generic/'rook2-exact',basis['binary_output']['sha256'])
 source=basis['source_sha256_before']|basis['tool_sha256_before'];assert len(source)==69
 assert basis['source_sha256_before']==basis['source_sha256_after'] and basis['tool_sha256_before']==basis['tool_sha256_after']
 for name,h in source.items():included(generic/'source-before'/name,h)
 ar=load(generic/'archive-receipt.json');assert ar['files']==69;included(generic/ar['archive'],ar['sha256'])
 proposal=E/'ordinary-projected-bits-proposal-20261018-01';proposal_plan=load(proposal/'plan.json')
 included(proposal/'source69.tar.gz',proposal_plan['source_archive_sha256'])
 assert proposal_plan['source69_graph']=='d4bb0f948c650f9675b050410a3a4d2811dcc58357ceb2fc1c4f99f21f2fff50'
 for archive_path in [generic/ar['archive'],proposal/'source69.tar.gz']:
  with tarfile.open(archive_path,'r:gz') as archive:
   found={}
   for member in archive:
    assert member.isfile() and member.name in source and member.name not in found
    found[member.name]=hashlib.sha256(archive.extractfile(member).read()).hexdigest()
   assert found==source
 reg=E/'ordinary-projected-bits-regression-20261018-01';rr=load(reg/'result.json')
 assert rr['complete'] and rr['strict54_pass'] and rr['interruption_fixtures']==8 and rr['interruption_searches']==24
 strict=load(reg/'strict54.stdout');assert len(strict['results'])==54 and strict['status']=='pass'
 wire=load(reg/'wire/receipt.json');assert wire['pass'] and len(wire['results'])==8 and sum(len(x['searches']) for x in wire['results'])==24
 for case in wire['results']:
  for name,item in case['raw'].items():included(reg/'wire'/case['id']/(name+'.raw'),item['sha256'])
 functional=E/'ordinary-projected-bits-independent-preparation-20261018-01/independent-verification.json';included(functional)
 assert load(functional)['complete'] and load(functional)['native_tests']==178 and len(load(functional)['dependencies'])==253
 pilot=E/'ordinary-projected-bits-cpu-pilot-20261018-01';plan=load(pilot/'plan.json')
 independent=E/'ordinary-projected-bits-cpu-independent-preparation-20261018-01/independent-reconciliation.json';ind=load(independent)
 included(independent,'e6ebbadd95bfdc5d0ebda5c670dbb01473ad9141edec372698bd476c0081367e')
 assert ind['complete'] and ind['normal_lifetimes']==ind['original_checkReplay']==70 and ind['warmups_excluded']==14 and ind['measured']==56
 assert len(ind['dependencies'])==757
 assert ind['advance_rule_satisfied'] and ind['lower_case_medians']==7 and ind['aggregate_ratio']<=0.995 and ind['worst_case_ratio']<=1.02
 assert ind['frozen_rule']==plan['advance_rule'] and all(x['range_relation']=='candidate-below' for x in ind['cases'])
 for variant in plan['variants'].values():included(variant['path'],variant['sha256'])
 assert plan['variants']['baseline']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 assert plan['variants']['candidate']['sha256']==basis['binary_output']['sha256']
 actual=load(pilot/'tool-terminal.json');assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0 and actual['session_id']==52227 and actual['terminal_chunk_id']=='f277f5'
 ia=load(independent.parent/'tool-terminal.json');assert ia['actual_tool_terminal_observed'] and ia['exit_code']==0 and ia['terminal_chunk_id']=='b0cfb0'
 records=sorted(pilot.glob('profile-*/*/native.json'));assert len(records)==70
 for record in records:
  included(record);data=load(record);assert data['native_exit_code']==0 and data['exec_error'] is None and data['failure'] is None
  assert data['engine_sha256_before']==data['engine_sha256_after']==plan['variants']['baseline' if record.parent.name.endswith('baseline') else 'candidate']['sha256']
  included(record.parent/'comparator.stdout');included(record.parent/'comparator.stderr')
 assert load(independent.parent/'original-checkReplay70-result.json')['original_oracle_calls']==70
 decision_path=E/'ordinary-projected-bits-generic-decision-20261018-01/decision.json';included(decision_path,'b4ea9a11841cb110cbf7d749b81b6a819a33c46cad67650e4149b6de22803014');decision=load(decision_path)
 assert not decision['source_promotion'] and not decision['performance_qualification']
 declaration=E/'ordinary-projected-bits-pgo-cpu-plan-20261018-01/plan.json';included(declaration,'83ad9ecca4ff5207dd362e3f2645465350e3e52e2e038d7f505bfc3a107cb27b')
 selected_pgo={p for p in by_path if '/ordinary-projected-bits-pgo-' in p}
 assert selected_pgo=={str(declaration)}
 return dict(whole_closed_trial_trees=14,reference_dependency_paths=len(SCOPE['reference_dependencies']),external_regular_payloads=len(EXTRAS),explicit_symlink_resolutions=SCOPE['explicit_symlink_resolutions'],native178_images_raw_tests_source69_archives_included=True,both_source69_archives_reopened=True,strict54_wire8_searches24_all_raw_included=True,pilot_actual=actual,independent_actual=ia,all70_lifetimes_and14_warmups_56measured_preserved=True,decision='Generic PASS: fresh own-source PGO preparation only; no source promotion or qualification',aggregate_ratio=ind['aggregate_ratio'],lower_case_medians=7,all7_ranges_candidate_below=True,variants=plan['variants'],all_regular_files_in_selected_trees=True,only_PGO_file_is_immutable_pretraining_declaration=True,no_unrelated_whole_tree_private_raw_census_opaque_root_git=True,parent_whitelist_approval_sha256=sha(HERE/'parent-whitelist-approval.json'),qualification=False)

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
