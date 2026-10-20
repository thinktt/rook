"""Actual CLI dry-run metadata/admission verification; never builds or runs an engine."""
from pathlib import Path
import subprocess,json,hashlib,resource,os,time,signal
E=Path(__file__).resolve().parent
W=Path('/home/legolas/rook2-work/imp2-machine-split-profiled-20261020-01')
R=Path('/home/legolas/rook2')
profile=R/'evidence/bitplane-pin-summary-pgo-training-20261020-01/merged.profdata'
training=profile.parent/'training.json'
absent=E/'dry-run-no-output';gen=E/'no-generated-profiles'
assert os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp' and os.environ['PYTHONDONTWRITEBYTECODE']=='1'
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13}
assert not any(os.environ.get(k) for k in ['LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH'])
assert not absent.exists() and not gen.exists() and not (W/'target').exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before={str(q.relative_to(W)):sha(q) for q in W.rglob('*') if q.is_file()}
base=['--crate',str(W),'--output',str(absent),'--mode','generic','--bin','rook2','--dry-run']
use=['--pgo-use',str(profile),'--training-record',str(training)]
rows=[];used=0

def run(label,helper,args,expected,error_text=None):
 global used
 argv=['/usr/bin/python3',str(helper),*base,*args]
 assert '--dry-run' in argv and used<60
 def cap():resource.setrlimit(resource.RLIMIT_FSIZE,(16777216,16777216))
 start=time.monotonic();failure=None
 with (E/(label+'.stdout')).open('xb') as o,(E/(label+'.stderr')).open('xb') as e:
  q=subprocess.Popen(argv,stdout=o,stderr=e,preexec_fn=cap,start_new_session=True)
  try:rc=q.wait(timeout=min(15,60-used))
  except BaseException as exc:
   os.killpg(q.pid,signal.SIGKILL);rc=q.wait(timeout=5);failure=type(exc).__name__+': '+str(exc)
 used+=time.monotonic()-start
 row={'label':label,'argv':argv,'pid':q.pid,'exit_code':rc,'expected_exit':expected,'child_reaped':True,'failure':failure,'cumulative_direct_child_wall_s':used,'stdout_bytes':(E/(label+'.stdout')).stat().st_size,'stderr_bytes':(E/(label+'.stderr')).stat().st_size,'stdout_sha256':sha(E/(label+'.stdout')),'stderr_sha256':sha(E/(label+'.stderr'))}
 rows.append(row)
 with (E/(label+'-terminal.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 assert failure is None and rc==expected and used<=60,row
 assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())<=16777216
 assert not absent.exists() and not gen.exists() and not (W/'target').exists()
 if expected==0:
  assert row['stderr_bytes']==0
  result=json.loads((E/(label+'.stdout')).read_text());assert result['outcome']=='plan-only; no Cargo build or receipt writes' and result['engine_runs']==0 and result['binary_output'] is None
  assert result['toolchain']['rustc']['argv']==['/usr/bin/rustc','-vV'] and result['toolchain']['rustc']['exit_code']==0
  assert result['toolchain']['cargo']['argv']==['/usr/bin/cargo','--version'] and result['toolchain']['cargo']['exit_code']==0
  assert all(x['argv'][0]=='/usr/bin/git' and x['argv'][1] in ['rev-parse','status'] for x in result['git_before'].values())
  return result
 assert not row['stdout_bytes'] and error_text in (E/(label+'.stderr')).read_text()
 return None

old=E/'build-before.py';new=W/'tools/build.py'
plans={}
for name,args in [('default-generic',[]),('default-use',use),('retained62-use',use+['--ext-tsp-profiled'])]:
 a=run(name+'-before',old,args,0);b=run(name+'-after',new,args,0)
 normalized=[]
 for row in [a,b]:normalized.append({k:v for k,v in row.items() if k not in ['started_utc','helper_sha256']})
 assert normalized[0]==normalized[1],name
 plans[name]=b
active=run('active63-use',new,use+['--ext-tsp-profiled','--machine-split-profiled'],0)
expected=['-C','target-cpu=x86-64','-C','profile-use='+str(profile),'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false -enable-split-machine-functions=true']
assert active['rust_flags']==expected
assert active['environment_overrides']['CARGO_ENCODED_RUSTFLAGS'].split(chr(31))==expected
assert active['pgo']['code_layout']['llvm_args']==expected[-1].removeprefix('llvm-args=').split()
assert active['pgo']['partitioning']=={'algorithm':'machine-function-splitter','profiled_functions_only':True,'application':'use-only','fresh_training':False,'cutoff_and_EH_defaults_unchanged':True,'llvm_option':'-enable-split-machine-functions=true'}
assert active['pgo']['input_sha256_before']==plans['retained62-use']['pgo']['input_sha256_before']
run('reject-no-pgo-use',new,['--machine-split-profiled'],2,'--machine-split-profiled requires --pgo-use')
run('reject-no-ExtTSP',new,use+['--machine-split-profiled'],2,'--machine-split-profiled requires --ext-tsp-profiled')
run('reject-instrumented',new,['--machine-split-profiled','--ext-tsp-profiled','--pgo-generate',str(gen)],2,'--machine-split-profiled requires --pgo-use')
after={str(q.relative_to(W)):sha(q) for q in W.rglob('*') if q.is_file()}
assert before==after
result={'complete':True,'dry_runs':rows,'real_metadata_probes':True,'metadata_shim_or_mock':False,'read_only_Git_authorization':'Parent explicitly permits only existing helper rev-parse/status in new private crate','default_generic_plain_use_and_retained62_equal_except_time_helper_identity':True,'active_flags_exact':expected,'single_combined_llvm_args':True,'profile_inputs_identical':True,'unchanged_actual_training_provenance_guard_executed':True,'non_use_or_no_ExtTSP_rejections':3,'work_tree_files_unchanged':True,'receipt_profile_target_outputs_created':False,'Cargo_builds':0,'compiler_code_generation':0,'engine_runs':0,'all_owned_children_reaped':True,'cumulative_direct_child_wall_s':used,'metadata_direct_child_budget_s':60}
with (E/'dry-run-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='dry_runs'}))
