"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(name) for name in SCOPE['directories']]
EXTRAS=[Path(name) for name in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/'closed-fullbyte-callgrind.tar.gz'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(path):return json.loads(path.read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,separators=(',',':'));f.write('\n')
def member_name(path):
 private=Path('/home/legolas/rook2-private')
 if private in path.parents:name='private/'+path.relative_to(private).as_posix()
 else:name=path.relative_to(REPO).as_posix()
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
 by_path={row['source_path']:row for row in rows};E=REPO/'evidence';private=Path('/home/legolas/rook2-private/fullbyte-callgrind-20261018-01')
 def included(path,digest=None):
  path=Path(path);assert path.resolve(strict=True)==path
  row=by_path[str(path)]
  if digest is not None:assert row['sha256']==digest,str(path)
  return row
 assert len(ROOTS)==3 and not EXTRAS and SCOPE['explicit_extra_files']==[]
 assert sha(Path(SCOPE['preservation_plan']))==SCOPE['preservation_plan_sha256']
 approval=load(HERE/'parent-whitelist-approval.json');assert approval['parent_approved'] is True
 assert approval['included_scope_sha256']==sha(HERE/'included-scope.json')
 assert approval['preflight_member_manifest_sha256']==sha(HERE/'preflight-member-manifest.json')
 assert approval['archive_writer_sha256']==sha(Path(__file__))
 assert rows==load(HERE/'preflight-member-manifest.json')['members']
 actual_analysis=load(Path(SCOPE['analysis_terminal_path']))
 included(SCOPE['analysis_terminal_path'],SCOPE['analysis_terminal_sha256'])
 assert actual_analysis==SCOPE['analysis_actual_terminal'] and actual_analysis['actual_tool_terminal_observed'] is True and actual_analysis['exit_code']==0
 prep=E/'fullbyte-callgrind-preparation-20261018-01';summary=load(prep/'execution-summary.json')
 assert summary['complete'] and summary['native_lifetimes']==2 and summary['first_failed_launch_native_lifetimes']==0
 assert summary['artifact_sha256']=='79d19ebe1b01fbe94dbf03025140b292807ecf6acdc181a52a5d1849bbc478df'
 assert summary['source69_graph']=='6aa2f8a1f81bc9c6b6f4ba26b987a259bca648a61a7b052f7d1166fcb1ea9b50'
 assert summary['independent_input_output_source_tool_profile_closure_passed'] and summary['original_replay_and_raw_bytes_match'] and summary['no_CPU_or_PMU_or_qualification_claim']
 profile_actual=load(private/'tool-terminal.json');verify_actual=load(private/'independent-verification-tool-terminal.json')
 assert profile_actual['actual_tool_terminal_observed'] and profile_actual['exit_code']==0 and profile_actual['session_id']==55574 and profile_actual['terminal_chunk_id']=='4840bb'
 assert verify_actual['actual_tool_terminal_observed'] and verify_actual['exit_code']==0 and verify_actual['terminal_chunk_id']=='f6056e'
 proof=load(private/'independent-verification.json');included(private/'independent-verification.json','65beaabeb6ce47cbcde3599333501aebcf93e02b7c0d1e82e90fa7e60a67a2e9')
 assert proof['complete'] and proof['all_original_inputs_unchanged'] and proof['original_checkReplay_exit_code']==0 and proof['original_checkReplay_cases']==2 and proof['native_engine_runs']==0 and not proof['qualification']
 provenance=load(private/'provenance.json');assert provenance['complete'] and provenance['failure'] is None and provenance['one_fixed_lifetime_per_case'] and not provenance['performance_claim']
 private_rows=[row for row in rows if private in Path(row['source_path']).parents]
 assert len(private_rows)==113 and sum(row['bytes'] for row in private_rows)==1668656
 assert SCOPE['external_payload_omissions']['not_self_contained'] is True
 return dict(complete_closed_trees=3,external_payloads=0,private_raw_output_files=113,private_raw_output_bytes=1668656,profile_actual=profile_actual,independent_actual=verify_actual,analysis_actual=actual_analysis,all_regular_files_without_omission=True,external_runtime_image_source_payloads_not_bundled=SCOPE['external_payload_omissions'],self_contained_runtime_bundle=False,event_scope='Whole-lifetime simulated user Ir diagnostic only; no PMU/CPU/qualification',parent_whitelist_approval_sha256=sha(HERE/'parent-whitelist-approval.json'))

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
