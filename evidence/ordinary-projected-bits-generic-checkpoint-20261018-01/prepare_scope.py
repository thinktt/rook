"""Whitelist only: closed14 ordinary projected-bit generic trees plus explicit dependency bytes; no native runs."""
from pathlib import Path
import hashlib,json,os,stat,traceback
HERE=Path(__file__).resolve().parent;REPO=Path('/home/legolas/rook2');E=REPO/'evidence'
PLAN=HERE/'preservation-plan.json'
def load(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(name,d):
 with (HERE/name).open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
def member(p):
 try:r=p.relative_to(REPO).as_posix()
 except ValueError:r='external/'+p.as_posix().lstrip('/')
 assert r and not Path(r).is_absolute() and all(x not in ['.','..'] for x in Path(r).parts)
 return r
def links(path):
 rows=[]
 for p in [*reversed(path.parents),path]:
  if p.is_symlink():rows.append(dict(path=str(p),target=os.readlink(p)))
 return rows

member_name=member
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
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13] and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 plan=load(PLAN);roots=[Path(x) for x in plan['directories']]
 assert len(roots)==len(set(roots))==plan['expected_whole_trees']==14
 assert all(a==b or not(a in b.parents or b in a.parents) for a in roots for b in roots)
 assert all(p.is_dir() and not p.is_symlink() and p.resolve()==p for p in roots)
 def inside(path):return any(path==root or root in path.parents for root in roots)
 originals=set();dirs=[];unsupported=[]
 for root in roots:
  for current,children,names in os.walk(root,followlinks=False,onerror=lambda error:(_ for _ in ()).throw(error)):
   dirs.append(str(Path(current)))
   for name in children:
    p=Path(current)/name
    if not stat.S_ISDIR(p.lstat().st_mode):unsupported.append(str(p))
   for name in names:
    p=Path(current)/name
    if stat.S_ISREG(p.lstat().st_mode):originals.add(p)
    else:unsupported.append(str(p))
 assert not unsupported,dict(unsupported_nonregular_closed_tree_entries=unsupported)
 pins={};origins={}
 for reference in plan['reference_manifests']:
  ref=reference['path']
  data=load(Path(ref));data=data[reference['field']] if reference['field'] else data
  for name,h in data.items():
   assert name not in pins or pins[name]==h,dict(conflicting_reference=name)
   pins[name]=h;origins.setdefault(name,[]).append(ref)
 for name,h in plan['explicit_reference_pins'].items():
  assert name not in pins or pins[name]==h,dict(conflicting_explicit_reference=name)
  pins[name]=h;origins.setdefault(name,[]).append(str(PLAN)+'#explicit_reference_pins')
 extra=set();refs=[];aliases=[]
 for name,h in sorted(pins.items()):
  path=Path(name);assert path.is_absolute() and '..' not in path.parts
  assert not any(x in name.lower() for x in ['opaque','calibration','census','/.git/']),name
  resolved=path.resolve(strict=True);assert stat.S_ISREG(resolved.lstat().st_mode),name
  chain=links(path)
  if chain:aliases.append(dict(logical_path=name,resolved_regular_source=str(resolved),symlink_components=chain,expected_sha256=h,archive_member=member(resolved)))
  elif resolved!=path:raise AssertionError('unexplained path resolution: '+name)
  assert sha(path)==sha(resolved)==h,name
  if not inside(resolved):extra.add(resolved)
  refs.append(dict(path=name,sha256=h,resolved_regular_source=str(resolved),archive_member=member(resolved),symlink_components=chain,reference_manifests=origins[name]))
 files=originals|extra;members={member(p):str(p) for p in files};assert len(members)==len(files)
 assert not any(HERE==p or HERE in p.parents for p in files)
 assert all(Path(row['resolved_regular_source']) in files for row in refs)
 scope=dict(directories=[str(p) for p in roots],explicit_extra_files=[str(p) for p in sorted(extra)],external_logical_reference_paths=[row['path'] for row in refs if not inside(Path(row['path']))],reference_dependencies=refs,explicit_symlink_resolutions=aliases,preservation_plan=str(PLAN),preservation_plan_sha256=sha(PLAN),closed_tree_regular_files=sorted(str(p) for p in originals),closed_tree_directories=sorted(dirs),unsupported_nonregular_closed_tree_entries=[],archive_mapping='repository-relative paths; external/absolute-path-without-leading-slash for outside repository; explicit symlink aliases map to included canonical regular payload bytes',no_silent_exclusions=True,excluded_checkpoint=str(HERE),excluded_active_or_future_scope='No whole current-profile/private/census/opaque/calibration/PGO/root/Git/unrelated trial tree; individual consumed files only, including immutable PGO declaration',overlap='No timing active; all selected generic/decision trees closed; separate PGO text preparation has no timing interpretation.')
 write('included-scope.json',scope)
 write('preflight-verification.json',dict(complete=True,closed_trial_trees=14,whole_trees=14,reference_union_paths=len(refs),external_logical_paths=len(scope['external_logical_reference_paths']),explicit_extra_regular_payloads=len(extra),explicit_symlink_resolutions=aliases,unsupported_entries=[],duplicate_members=0,all_reference_hashes_equal=True,prospective_regular_members=len(files),source_bytes=sum(p.stat().st_size for p in files),no_native_execution=True))
 ROOTS=roots;EXTRAS=sorted(extra);SCOPE=scope
 rows,inventory_dirs=inventory()
 assert len(rows)==len(files) and inventory_dirs==sorted(dirs)
 write('preflight-member-manifest.json',dict(file_count=len(rows),source_bytes=sum(row['bytes'] for row in rows),members=rows))
 write('preflight-summary.json',dict(complete=True,archive_created=False,whole_trees=14,regular_members=len(rows),source_bytes=sum(row['bytes'] for row in rows),explicit_extra_regular_payloads=len(extra),reference_union_paths=len(refs),scope_sha256=sha(HERE/'included-scope.json'),member_manifest_sha256=sha(HERE/'preflight-member-manifest.json'),preservation_plan_sha256=sha(PLAN),symlink_resolution_count=len(aliases)))
 print(json.dumps(dict(complete=True,whole_trees=14,reference_union_paths=len(refs),explicit_extra_payloads=len(extra),members=len(files),source_bytes=sum(p.stat().st_size for p in files),symlink_resolution_count=len(aliases))))
if __name__=='__main__':
 try:main()
 except BaseException as error:write('preflight-failure.json',dict(error=repr(error),traceback=traceback.format_exc()));raise
