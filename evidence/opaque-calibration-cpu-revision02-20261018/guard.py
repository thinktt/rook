"""Read-only calibration launch pins; no engine execution or output creation."""
import errno,hashlib,json,os,re,stat,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=Path('/home/legolas/king-spec/conformance/profiling')
HELPERS=[0,1,2,3,4,5,8,9,10,11,12,13]
OPAQUE='4f647377c176c9fe454f369b0698efa6c9f20d0324d4c54d5c5907189cbde370'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def require(ok,message):
 if not ok:raise ValueError(message)
def check_pins(pins):
 for name,digest in pins.items():require(sha(name)==digest,'pinned dependency changed: '+name)
def status_fields(text):
 fields=dict(line.split(':',1) for line in text.splitlines() if ':' in line)
 return {'uids':[int(x) for x in fields['Uid'].split()],
  'capabilities':{name:int(fields[name].strip(),16) for name in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb'] if name in fields},
  'ppid':int(fields['PPid']) if 'PPid' in fields else None}
def unprivileged(fields):
 # Bounding set is not an acquired capability set; retain it, do not requirezero.
 return fields['uids']==[1000]*4 and all(fields['capabilities'].get(k)==0 for k in ['CapInh','CapPrm','CapEff','CapAmb'])
def file_identity(path):
 path=Path(path);s=path.stat()
 require(stat.S_ISREG(s.st_mode) and not s.st_mode&0o6000,'not a regular non-set-ID executable')
 try:
  value=os.getxattr(path,'security.capability')
 except OSError as error:
  require(error.errno==errno.ENODATA,'file capability absence could not be established')
 else:raise ValueError('security.capability xattr present, including empty value')
 return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'file_capability':'absent-ENODATA'}
def js_closure(entry):
 pending=[Path(entry).resolve()];found={}
 while pending:
  path=pending.pop()
  if str(path) in found:continue
  require(path.is_relative_to(SPEC),'JS dependency escapes public profiling directory')
  text=path.read_text();found[str(path)]=sha(path)
  names=re.findall(r"\bfrom\s*['\"]([^'\"]+)['\"]",text)
  names+=re.findall(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]",text)
  names+=re.findall(r"^\s*import\s*['\"]([^'\"]+)['\"]",text,re.M)
  for name in names:
   if name.startswith('node:'):continue
   require(name.startswith('.'),'unreviewed external JS import: '+name)
   pending.append((path.parent/name).resolve(strict=True))
 return found
def authority_preflight(authority_path,authority_sha,output,fresh=True):
 authority_path=Path(authority_path).resolve(strict=True)
 require(sha(authority_path)==authority_sha,'launch authority SHA mismatch')
 authority=load(authority_path)
 require(authority.get('authorized') is True and authority.get('scope')=='opaque-fixed-calibrator-cpu-only','not authorized')
 require(authority.get('all_conflicting_owned_jobs_closed') is True,'conflicting owned jobs not closed')
 require(authority.get('profile_path')==str(HERE/'profile.json'),'wrong profile path')
 profile=load(HERE/'profile.json')
 require(sha(HERE/'profile.json')==authority['profile_sha256'],'profile pin mismatch')
 expected=dict(profile['input_sha256']);expected[str(HERE/'profile.json')]=authority['profile_sha256']
 require(authority['pins']==expected,'authority dependency map differs from exact profile closure')
 check_pins(expected)
 require(authority['collector_sha256']==expected[str(HERE/'collect.py')],'collector pin missing')
 require(authority['supervisor_sha256']==expected[str(HERE/'account_native.py')],'supervisor pin missing')
 require(authority['identity_record_sha256']==expected[str(HERE/'artifact-identity.json')],'identity record pin missing')
 identity=load(HERE/'artifact-identity.json')
 require(authority['artifact_identity']==identity==profile['artifact'],'artifact identity record mismatch')
 require(identity['kind']=='approved-opaque-calibrator' and identity['sha256']==OPAQUE,'wrong opaque artifact')
 engine=Path(identity['path']).resolve(strict=True)
 require(str(engine)==identity['path'] and sha(engine)==OPAQUE,'opaque path/hash mismatch')
 actual_file=file_identity(engine)
 require(actual_file==authority['engine_file_identity'],'file owner/mode/xattr identity changed')
 require(unprivileged(status_fields(Path('/proc/self/status').read_text())),'controller UID/capability mismatch')
 require(sorted(os.sched_getaffinity(0))==HELPERS,'collector must run on exact housekeeping mask')
 require(os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp','TMPDIR mismatch')
 environment={k:os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS']}
 require(environment==authority['environment'] and all(v is None for v in environment.values()),'unreviewed process environment')
 require(str(Path(sys.executable).resolve())==authority['python'] and expected[authority['python']]==sha(sys.executable),'Python identity mismatch')
 require(authority['node']=='/usr/bin/node' and expected[str(Path(authority['node']).resolve())]==sha(authority['node']),'Node identity mismatch')
 require(js_closure(SPEC/'replay-check.mjs')==profile['public_js_sha256'],'transitive publicJS closure mismatch')
 require(all(expected[name]==digest for name,digest in profile['public_js_sha256'].items()),'JS closure missing independent pins')
 work=load(SPEC/'workloads.json');oracle=load(SPEC/'replay-oracle.json')
 cases=[row['id'] for row in work['cases']]
 require(len(cases)==54 and len(set(cases))==54 and cases==profile['cases']==authority['cases'],'case order mismatch')
 require([row['id'] for row in oracle['cases']]==cases,'oracle case correspondence')
 require(oracle['mode']==profile['engine_options']==authority['engine_options'],'mode mismatch')
 require(profile['reference']==authority['reference'],'reference pin mismatch')
 require(expected[profile['reference']['path']]==profile['reference']['sha256'],'reference not in closure')
 require(authority['schedule']=={'warmups_per_case':1,'measured_per_case':3,'lifetimes':216,'measured':162},'schedule mismatch')
 require(authority['limits']==profile['limits']=={'seconds_per_run':960,'aggregate_seconds':3600,'bytes_per_comparator_stream':8388608,'bytes_per_native_receipt':262144,'aggregate_stream_bytes':268435456,'outer_cleanup_seconds':10,'released_cleanup_seconds':5},'limits mismatch')
 output=Path(output).absolute();require(str(output)==authority['output'],'output authority mismatch')
 require(not output.is_symlink(),'output must not be a symlink')
 require(not output.exists() if fresh else output.is_dir(),'output freshness/type mismatch')
 for ancestor in output.parents:require(ancestor.is_dir() and not ancestor.is_symlink(),'unsafe output ancestor')
 return authority,profile,identity,actual_file
