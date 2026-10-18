"""Future closed-three-tree inventory only; never archives or runs native/tools."""
from pathlib import Path
import argparse,hashlib,json,os,stat,traceback
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2');PRIVATE=Path('/home/legolas/rook2-private')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def load(path):return json.loads(path.read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write(chr(10))
def member_name(path):
 if PRIVATE in path.parents:name='private/'+path.relative_to(PRIVATE).as_posix()
 else:name=path.relative_to(REPO).as_posix()
 assert name and not Path(name).is_absolute() and all(x not in ['.','..'] for x in Path(name).parts)
 return name
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

def main():
 global ROOTS,EXTRAS,SCOPE
 parser=argparse.ArgumentParser()
 parser.add_argument('--analysis-terminal',required=True,type=Path)
 parser.add_argument('--analysis-terminal-sha256',required=True)
 args=parser.parse_args()
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13] and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 plan=load(HERE/'preservation-plan.json');ROOTS=[Path(p) for p in plan['directories']];EXTRAS=[]
 assert len(ROOTS)==len(set(ROOTS))==3 and not plan['explicit_extra_files']
 analysis=ROOTS[2];terminal=args.analysis_terminal
 assert analysis in terminal.parents and terminal.is_file() and sha(terminal)==args.analysis_terminal_sha256
 actual=load(terminal);assert actual['actual_tool_terminal_observed'] is True and actual['exit_code']==0
 assert isinstance(actual.get('terminal_chunk_id') or actual.get('chunk_id'),str)
 files=[];dirs=[];unsupported=[]
 for root in ROOTS:
  assert root.is_dir() and not root.is_symlink() and root.resolve()==root
  for current,children,names in os.walk(root,followlinks=False,onerror=lambda error:(_ for _ in ()).throw(error)):
   dirs.append(str(Path(current)))
   for name in children:
    path=Path(current)/name
    if not stat.S_ISDIR(path.lstat().st_mode):unsupported.append(str(path))
   for name in names:
    path=Path(current)/name
    if stat.S_ISREG(path.lstat().st_mode):files.append(path)
    else:unsupported.append(str(path))
 assert not unsupported,unsupported
 assert len(files)==len(set(files))
 assert all(HERE not in path.parents for path in files)
 for name,h in plan['known_closed_pins'].items():assert sha(Path(name))==h
 SCOPE=dict(directories=[str(p) for p in ROOTS],explicit_extra_files=[],closed_tree_regular_files=sorted(str(p) for p in files),closed_tree_directories=sorted(dirs),preservation_plan=str(HERE/'preservation-plan.json'),preservation_plan_sha256=sha(HERE/'preservation-plan.json'),analysis_terminal_path=str(terminal),analysis_terminal_sha256=args.analysis_terminal_sha256,analysis_actual_terminal=actual,external_payload_omissions=plan['external_payload_omissions'],no_silent_exclusions=True,excluded_checkpoint=str(HERE),reference_dependencies=[],explicit_symlink_resolutions=[],scope_limits=plan['scope_limits'])
 rows,after_dirs=inventory();assert after_dirs==sorted(dirs)
 private=[row for row in rows if PRIVATE in Path(row['source_path']).parents]
 assert len(private)==plan['expected_private_output_files_from_parent']==113
 assert sum(row['bytes'] for row in private)==plan['expected_private_output_bytes_from_parent']==1668656
 write('included-scope.json',SCOPE)
 write('preflight-member-manifest.json',dict(file_count=len(rows),source_bytes=sum(row['bytes'] for row in rows),members=rows))
 write('preflight-summary.json',dict(complete=True,archive_created=False,whole_trees=3,regular_members=len(rows),source_bytes=sum(row['bytes'] for row in rows),private_members=len(private),private_bytes=sum(row['bytes'] for row in private),explicit_external_payloads=0,scope_sha256=sha(HERE/'included-scope.json'),member_manifest_sha256=sha(HERE/'preflight-member-manifest.json')))
 print(json.dumps(dict(complete=True,archive_created=False,whole_trees=3,members=len(rows),bytes=sum(row['bytes'] for row in rows))))
if __name__=='__main__':
 try:main()
 except BaseException as error:write('preflight-failure.json',dict(error=repr(error),traceback=traceback.format_exc()));raise
