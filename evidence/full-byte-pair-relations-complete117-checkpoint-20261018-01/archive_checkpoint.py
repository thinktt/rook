"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
FIRST=REPO/'evidence/full-byte-pair-relations-complete117-preparation-20261018-01'
ACCEPTANCE=REPO/'evidence/full-byte-pair-relations-complete117-parent-acceptance-20261018-01'
INTEGRATION=REPO/'evidence/full-byte-pair-relations-integration-20261018-01'
ROOTS=[FIRST,ACCEPTANCE,INTEGRATION]
PROMOTION=INTEGRATION/'source-promotion.json'
ARCHIVE=HERE/'closed-full-byte-pair-relations-complete117.tar.gz'
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
 assert len(files)==len(set(files))
 assert all(a==b or not(a in b.parents or b in a.parents) for a in ROOTS for b in ROOTS)
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
 by_path={row['source_path']:row for row in rows};plan=load(FIRST/'validation-plan.json')
 graph='917723673dccacb354ebea485be7e37e20d293bd168bbd7e21e3aa599dbcd895'
 assert plan['source_graph_sha256']==graph and len(plan['source_sha256'])==112
 diag=load(FIRST/'diagnostic/verification.json');assert diag['complete'] and diag['failure'] is None
 assert diag['units']['rook2-diag']['passed']==209 and all(row['exit_code']==0 and row['actual_child_return_observed'] for row in diag['stages'])
 adapter=FIRST/'diagnostic-build/rook2-diag-exact';unit=FIRST/'diagnostic/unit-bin/rook2-diag/unit-exact'
 ind=load(FIRST/'reconciliation/independent-verification.json');summary=load(FIRST/'validation-summary.json')
 assert ind['status']=='pass' and ind['diagnostic_cases']==7673 and ind['diagnostic_operations']==117 and ind['whole_fixture_files']==115
 assert summary['status']=='FULL_BYTE_PAIR_RELATIONS_COMPLETE117_FUNCTIONAL_PASS' and summary['source_graph_sha256']==graph
 assert by_path[str(adapter)]['sha256']==ind['diagnostic_artifact_sha256']==summary['adapter_sha256']==diag['artifact_sha256']
 assert by_path[str(unit)]['sha256']==diag['units']['rook2-diag']['binary_sha256']
 assert by_path[str(FIRST/'validation-summary.json')]['sha256']=='2a698956b76d34b857c39eab41f1c79f615aa8f433dd97c462fbc6bcbe21c550'
 assert by_path[str(FIRST/'reconciliation/independent-verification.json')]['sha256']=='589abaa6e53f92d30e3b5711918058162dff7dc6465cea81a2aca4a7fdfa16ad'
 raw=FIRST/'diagnostic/raw-cases';expected={f'{ordinal:06d}{ext}' for ordinal in range(7673) for ext in ['.stdin','.stdout','.stderr','.json']}|{'cursor'}
 assert {p.name for p in raw.iterdir()}==expected and (raw/'cursor').read_text()=='7673'
 raw_manifest=FIRST/'reconciliation/raw-case-sha256.json';assert by_path[str(raw_manifest)]['sha256']==ind['raw_case_manifest_sha256']
 hashes=load(raw_manifest);assert len(hashes)==7673*4
 for name,h in hashes.items():assert by_path[str(FIRST/'diagnostic'/name)]['sha256']==h
 actual={}
 for key,path in [('freeze',FIRST/'execution-freeze/tool-terminal.json'),('diag',FIRST/'diagnostic/tool-terminal.json'),('independent',FIRST/'reconciliation/tool-terminal.json'),('finalizer',FIRST/'finalizer-tool-terminal.json')]:
  actual[key]=load(path);assert actual[key]['actual_tool_terminal_observed'] and actual[key]['exit_code']==0
 acceptance=load(ACCEPTANCE/'acceptance.json');assert acceptance['accepted_for_complete117_diagnostic'] and acceptance['source_graph_sha256']==graph
 promotion=load(PROMOTION)
 assert by_path[str(PROMOTION)]['sha256']=='8d512b2ca8ca8ab173d5a509519d60a3f51e9e65745d48ca0b43d21195534935'
 assert promotion['source_promoted'] and promotion['root_source112_graph']==graph and promotion['source_sha256']==plan['source_sha256']
 assert promotion['functional_summary_sha256']==by_path[str(FIRST/'validation-summary.json')]['sha256']
 assert promotion['independent_verification_sha256']==by_path[str(FIRST/'reconciliation/independent-verification.json')]['sha256']
 assert promotion['changed_native']==['src/influence.rs','src/relation_table.rs'] and promotion['offline_maintenance_generator']['outside_build112']
 for path in [FIRST/'source-112.tar.gz',FIRST/'official-inputs-115.tar.gz',FIRST/'execution-freeze/source-frozen.tar.gz',FIRST/'diagnostic-build/verified-source-before.tar.gz']:
  assert str(path) in by_path
 return dict(source_graph_sha256=graph,unit209_sha256=by_path[str(unit)]['sha256'],adapter_sha256=by_path[str(adapter)]['sha256'],raw_case_files=7673*4,raw_cursor_included=True,all_raw_hashes_equal_original_independent_manifest=True,actual_success_terminals=actual,acceptance_sha256=by_path[str(ACCEPTANCE/'acceptance.json')]['sha256'],promotion_receipt_sha256=by_path[str(PROMOTION)]['sha256'],only_three_whole_trees=True,ordinary_native178_strict54_wire24_reused_by_source69_equality=True,new_engine_or_build_runs=0)

def main():
 result=dict(complete=False,failure=None,affinity=sorted(os.sched_getaffinity(0)),no_native_compiler_profiler_timing_git_subprocesses=True)
 try:
  assert result['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13] and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
  assert not ARCHIVE.exists() and not (HERE/'member-manifest.json').exists()
  rows,dirs=inventory();proof=coverage(rows);total=sum(row['bytes'] for row in rows)
  manifest=dict(scope={'complete_trees':[str(root) for root in ROOTS],'additional_files':[],'no_hidden_or_ignored_file_filter':True,'regular_file_members_only':True,'directories_omitted_as_tar_entries_but_enumerated':dirs,'unsupported_nonregular_entries':[],'exclusions':[]},file_count=len(rows),source_bytes=total,members=rows)
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
