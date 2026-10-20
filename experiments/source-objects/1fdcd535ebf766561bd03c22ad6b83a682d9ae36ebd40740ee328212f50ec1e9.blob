"""Fail-closed shared admission; importing never executes tools or writes files."""
import hashlib,json,os,sys,subprocess,shlex,tomllib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
PLAN=load(HERE/'plan.json')
SOURCE=Path(PLAN['source_root'])
sys.dont_write_bytecode=True
sys.path.insert(0,str(SOURCE/'tools'))
from build import source_snapshot,tool_snapshot,cargo_configs

def terminal(path):
 t=load(path)
 assert t.get('actual_tool_terminal_observed') is True and t['exit_code']==0
 chunk=t.get('terminal_chunk_id') or t.get('chunk_id')
 assert isinstance(chunk,str) and chunk.strip()
 # Retain the real session_id when exec yielded; fast terminal execs have none.
 # The parent checks yielded-session linkage against the observed actual handle;
 # never fabricate a session merely to satisfy this terminal-shape admission.
 return t

def validate_authority(c):
 assert c.get('authorized') is True and c.get('all_conflicting_native_work_terminal') is True
 assert c.get('scope')=='ordering-equal-length-own-pgo-build-train-no-cpu'
 assert c['plan_sha256']==sha(HERE/'plan.json')
 assert c['source_root']==str(SOURCE)
 assert c['prepared_scripts_sha256']==load(HERE/'script-pins.json')
 assert c['source_candidate_accepted'] is True
 assert c['focused_native6_accepted'] is True
 assert c['generic_pilot_independent_terminal_path'] in c['generic_pilot_actual_terminals']
 assert c['generic_pilot_advance_accepted'] is True
 assert isinstance(PLAN['generic_candidate_sha256'],str) and len(PLAN['generic_candidate_sha256'])==64
 assert c['generic_candidate_sha256']==PLAN['generic_candidate_sha256']
 assert c['generic_pilot_evidence'] and c['generic_pilot_actual_terminals']
 for path,digest in c['generic_pilot_evidence'].items():assert sha(path)==digest
 for path,digest in c['generic_pilot_actual_terminals'].items():assert sha(path)==digest;terminal(path)
 assert c['source_and_build_evidence'] and c['actual_terminals']
 for path,digest in c['source_and_build_evidence'].items():assert sha(path)==digest
 for path,digest in c['actual_terminals'].items():assert sha(path)==digest;terminal(path)
 assert c['training_cpu']==14 and c['sibling15_no_owned_task'] is True
 assert c['quiet_window_and_interference_review']
 return c

def check_inputs():
 assert source_snapshot(SOURCE)==PLAN['engine_source_sha256']
 assert tool_snapshot(SOURCE)==PLAN['tool_source_sha256']
 assert tool_snapshot(ROOT)==PLAN['tool_source_sha256']
 assert cargo_configs(SOURCE)==PLAN['cargo_config_sha256']
 manifest=tomllib.loads((SOURCE/'Cargo.toml').read_text())
 assert manifest['profile']['release']==PLAN['manifest_release_profile']
 assert manifest['profile']['release']['lto']=='thin'
 assert all(sha(path)==digest for path,digest in PLAN['input_sha256'].items())
 assert all(sha(HERE/name)==digest for name,digest in load(HERE/'script-pins.json').items())


def check_thin_build(out,mode):
 # Source hashing prevents a changed manifest; verbose rustc lines prove the
 # effective Cargo setting, including an otherwise silent profile override.
 r=load(Path(out)/'receipt.json')
 assert r['pgo']['mode']==mode
 assert r['source_sha256_before']==r['source_sha256_after']==PLAN['engine_source_sha256']
 assert r['toolchain']==PLAN['toolchain'] and r['cargo_config_sha256_before']==r['cargo_config_sha256_after']==PLAN['cargo_config_sha256']
 commands=[shlex.split(line.split('Running `',1)[1].rsplit('`',1)[0]) for line in (Path(out)/'build.stderr').read_text().splitlines() if 'Running `' in line and '--crate-name rook2 ' in line]
 observed={}
 for source,kind in [('src/lib.rs','lib'),('src/bin/rook2.rs','bin')]:
  matches=[argv for argv in commands if source in argv]
  assert len(matches)==1,(source,len(matches))
  argv=matches[0]; assert argv[argv.index('--crate-type')+1]==kind
  options={}
  for i,token in enumerate(argv):
   if token=='-C': item=argv[i+1]
   elif token.startswith('-C') and len(token)>2: item=token[2:]
   else: continue
   key,sep,value=item.partition('=');assert key not in options,(source,key)
   options[key]=value if sep else True
  for key,value in [('opt-level','3'),('panic','abort'),('codegen-units','1'),('debuginfo','1'),('target-cpu','x86-64')]:assert options.get(key)==value,(source,key,options)
  if kind=='bin': assert options.get('lto')=='thin' and 'linker-plugin-lto' not in options
  else: assert options.get('linker-plugin-lto') is True and 'lto' not in options
  profile='profile-generate' if mode=='instrumented' else 'profile-use'
  expected=str(Path(PLAN['training'])/('raw' if mode=='instrumented' else 'merged.profdata'))
  assert options.get(profile)==expected and ('profile-use' if mode=='instrumented' else 'profile-generate') not in options
  observed[source]=options
 return observed

def require_clearance():
 c=validate_authority(load(HERE/'execution-clearance.json'))
 assert sorted(os.sched_getaffinity(0))==PLAN['helper_affinity']
 assert os.environ.get('TMPDIR')==PLAN['tempdir']
 assert Path(PLAN['tempdir']).is_dir()
 for k in os.environ:
  assert not k.startswith(('CARGO_PROFILE_','CARGO_TARGET_','CARGO_BUILD_')),k
 for k in ['CC','CFLAGS','CXX','CXXFLAGS','AR','LDFLAGS','CARGO_HOME','RUSTC','LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH','NODE_OPTIONS','PYTHONPATH','PYTHONHOME','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTUP_TOOLCHAIN']:
  assert not os.environ.get(k),k
 check_inputs()
 return c

def check_merge_tool():
 assert sha(Path(PLAN['merge_tool']).resolve())==PLAN['merge_tool_sha256']
 r=subprocess.run([PLAN['merge_tool'],'--version'],capture_output=True,text=True)
 assert r.returncode==0 and not r.stderr and r.stdout==PLAN['merge_tool_version']
 assert 'LLVM version: 19.1.7' in PLAN['toolchain']['rustc']['stdout']


def write(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')


def run(argv,stem,cwd=ROOT,env=None):
 # Parent observes the outer actual terminal separately; these are actual child returns.
 with Path(str(stem)+'.stdout').open('xb') as a,Path(str(stem)+'.stderr').open('xb') as b:
  r=subprocess.run(['/usr/bin/taskset','-c','0-5,8-13',*map(str,argv)],cwd=cwd,env=env,stdout=a,stderr=b)
 record=dict(argv=list(map(str,argv)),exit_code=r.returncode,actual_child_return_observed=True)
 write(Path(str(stem)+'.child-terminal.json'),record)
 assert r.returncode==0,record
 return record
