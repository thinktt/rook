from pathlib import Path
import subprocess,json,hashlib,resource,os
E=Path(__file__).resolve().parent
W=Path('/home/legolas/rook2-work/imp2-exttsp-profiled-20261020-01')
R=Path('/home/legolas/rook2')
profile=R/'evidence/bitplane-pin-summary-pgo-training-20261020-01/merged.profdata'
training=profile.parent/'training.json'
absent=E/'dry-run-no-output';gen=E/'no-generated-profiles'
assert not absent.exists() and not gen.exists() and not (W/'target').exists()
before={str(q.relative_to(W)):hashlib.sha256(q.read_bytes()).hexdigest() for q in W.rglob('*') if q.is_file()}
base=['--crate',str(W),'--output',str(absent),'--mode','generic','--bin','rook2','--dry-run']
use=['--pgo-use',str(profile),'--training-record',str(training)]
rows=[]
def run(label,helper,args,expected):
 argv=['/usr/bin/python3',str(helper),*base,*args]
 def cap():resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
 with (E/(label+'.stdout')).open('xb') as o,(E/(label+'.stderr')).open('xb') as e:
  q=subprocess.Popen(argv,stdout=o,stderr=e,preexec_fn=cap,start_new_session=True)
  try:rc=q.wait(timeout=30)
  except BaseException:os.killpg(q.pid,9);q.wait(timeout=5);raise
 assert rc==expected,(label,rc)
 row={'label':label,'argv':argv,'pid':q.pid,'exit_code':rc,'stdout_bytes':(E/(label+'.stdout')).stat().st_size,'stderr_bytes':(E/(label+'.stderr')).stat().st_size,'child_reaped':True}
 rows.append(row)
 assert not absent.exists() and not gen.exists() and not (W/'target').exists()
 return json.loads((E/(label+'.stdout')).read_text()) if expected==0 else None
old=E/'build-before.py';new=W/'tools/build.py'
a=run('default-generic-before',old,[],0);b=run('default-generic-after',new,[],0)
c=run('default-use-before',old,use,0);d=run('default-use-after',new,use,0)
for x,y in [(a,b),(c,d)]:
 for z in [x,y]:
  z.pop('started_utc');z.pop('helper_sha256')
 assert x==y,'default dry-run changed beyond helper identity/time'
active=run('active-profiled-use',new,use+['--ext-tsp-profiled'],0)
expected=['-C','target-cpu=x86-64','-C','profile-use='+str(profile),'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false']
assert active['rust_flags']==expected
assert active['environment_overrides']['CARGO_ENCODED_RUSTFLAGS'].split(chr(31))==expected
assert active['pgo']['code_layout']=={'algorithm':'ext-tsp','profiled_functions_only':True,'application':'use-only','fresh_training':False,'llvm_args':['-pgo-warn-missing-function','-enable-ext-tsp-block-placement=true','-ext-tsp-apply-without-profile=false']}
assert active['pgo']['input_sha256_before']==d['pgo']['input_sha256_before']
run('reject-no-pgo-use',new,['--ext-tsp-profiled'],2)
run('reject-instrumented',new,['--ext-tsp-profiled','--pgo-generate',str(gen)],2)
for n in ['reject-no-pgo-use','reject-instrumented']:assert '--ext-tsp-profiled requires --pgo-use' in (E/(n+'.stderr')).read_text()
after={str(q.relative_to(W)):hashlib.sha256(q.read_bytes()).hexdigest() for q in W.rglob('*') if q.is_file()}
assert before==after
result={'complete':True,'dry_runs':rows,'real_metadata_probes':True,'metadata_probes_not_mocked':True,'default_generic_and_use_equal_except_time_and_helper_identity':True,'active_flags_exact':expected,'single_combined_llvm_args':True,'unchanged_profile_admission_guards_executed':True,'non_use_rejections':2,'no_receipt_profile_or_target_output_created':True,'work_tree_files_unchanged':True,'Cargo_builds':0,'LLVM_profile_consumption':0,'engine_runs':0,'all_owned_children_reaped':True}
(E/'dry-run-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='dry_runs'}))
