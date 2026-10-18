"""Archive closed evidence only; no native, compiler, Git or profiling subprocesses."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2')
FIRST=REPO/'evidence/activity-value-inputs-complete117-preparation-20261018-01'
SECOND=REPO/'evidence/activity-value-inputs-complete117-continuation02-20261018'
PROMOTION=REPO/'evidence/activity-value-inputs-integration-20261018/source-promotion.json'
ARCHIVE=HERE/'closed-activity-complete117.tar.gz'
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
 for root in [FIRST,SECOND]:
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
 assert stat.S_ISREG(PROMOTION.lstat().st_mode);files.append(PROMOTION)
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
 by_path={row['source_path']:row for row in rows}
 old=load(FIRST/'diagnostic/verification.json');oldterminal=load(FIRST/'diagnostic/tool-terminal.json')
 assert old['complete'] is False and oldterminal['exit_code']==1 and oldterminal['terminal_chunk_id']=='588af9'
 assert len(old['stages'])==4 and all(row['exit_code']==0 and row['actual_child_return_observed'] for row in old['stages'])
 assert old['units']['rook2-diag']['passed']==209
 assert not (FIRST/'diagnostic/raw-cases').exists() and not (FIRST/'diagnostic/conformance.stdout').exists()
 adapter=FIRST/'diagnostic-build/rook2-diag-exact';unit=FIRST/'diagnostic/unit-bin/rook2-diag/unit-exact'
 assert by_path[str(adapter)]['sha256']=='0e5eb3e074e81835ae791f00b0f98c838cbd9c5cdf01ef7f5b74965a355a9e80'
 assert by_path[str(unit)]['sha256']=='e9a720a631c572d327bca9df95f07a0aac90757cecc8685fa316d89d66296aae'
 raw=SECOND/'corpus/raw-cases';expected={f'{ordinal:06d}{ext}' for ordinal in range(7673) for ext in ['.stdin','.stdout','.stderr','.json']}|{'cursor'}
 assert {p.name for p in raw.iterdir()}==expected and (raw/'cursor').read_text()=='7673'
 ind=load(SECOND/'reconciliation/independent-verification.json');assert ind['status']=='pass' and ind['diagnostic_cases']==7673
 raw_manifest=SECOND/'reconciliation/raw-case-sha256.json';assert sha(raw_manifest)==ind['raw_case_manifest_sha256']
 hashes=load(raw_manifest);assert len(hashes)==7673*4
 for name,h in hashes.items():assert by_path[str(SECOND/'corpus'/name)]['sha256']==h
 actual={}
 for key,path in [('corpus',SECOND/'corpus/tool-terminal.json'),('independent',SECOND/'reconciliation/tool-terminal.json'),('finalizer',SECOND/'finalizer-tool-terminal.json')]:
  actual[key]=load(path);assert actual[key]['actual_tool_terminal_observed'] and actual[key]['exit_code']==0
 p=load(PROMOTION)
 assert p['source_graph_sha256']=='d49e7e3fb4b2af77da9ab5e9ee801ba3e9d6673d00be8e73e0389afba9260b03'
 assert p['functional_summary_sha256']==by_path[str(SECOND/'validation-summary.json')]['sha256']
 assert p['independent_corpus_sha256']==by_path[str(SECOND/'reconciliation/independent-verification.json')]['sha256']
 for path in [FIRST/'source-112.tar.gz',FIRST/'official-inputs-115.tar.gz',FIRST/'execution-freeze/source-frozen.tar.gz',FIRST/'diagnostic-build/verified-source-before.tar.gz',FIRST/'reuse-unit-bin/lib/unit-exact',FIRST/'reuse-unit-bin/dev/unit-exact']:
  assert str(path) in by_path
 return dict(failed01_outer=oldterminal,green01_children=4,unit209_sha256=by_path[str(unit)]['sha256'],adapter_sha256=by_path[str(adapter)]['sha256'],raw_case_files=7673*4,raw_cursor_included=True,all_raw_hashes_equal_original_independent_manifest=True,actual_success_terminals=actual,promotion_receipt_sha256=by_path[str(PROMOTION)]['sha256'],source_graph_sha256=p['source_graph_sha256'])

def main():
 result=dict(complete=False,failure=None,affinity=sorted(os.sched_getaffinity(0)),no_native_compiler_profiler_timing_git_subprocesses=True)
 try:
  assert result['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
  assert not ARCHIVE.exists() and not (HERE/'member-manifest.json').exists()
  rows,dirs=inventory();proof=coverage(rows);total=sum(row['bytes'] for row in rows)
  manifest=dict(scope={'complete_trees':[str(FIRST),str(SECOND)],'additional_single_file':str(PROMOTION),'no_hidden_or_ignored_file_filter':True,'regular_file_members_only':True,'directories_omitted_as_tar_entries_but_enumerated':dirs,'unsupported_nonregular_entries':[],'exclusions':[]},file_count=len(rows),source_bytes=total,members=rows)
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
