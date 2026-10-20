from pathlib import Path
import json,hashlib,shutil,datetime,os
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'exttsp-profiled-parent-review-20261020-01';Q=E/'exttsp-profiled-pgo-screen-preparation-20261020-01';X=E/'exttsp-profiled-pgo-screen-execution-20261020-01';B=E/'exttsp-profiled-pgo-use-build-20261020-01';K=E/'exttsp-profiled-backend-review-20261020-01';S=E/'exttsp-profiled-selection-20261020-01';W=Path('/home/legolas/rook2-work/imp2-exttsp-profiled-20261020-01')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
selection=read(S/'selection.json');now=datetime.datetime.now(datetime.timezone.utc);elapsed=(now-datetime.datetime.fromisoformat(selection['selected_utc'])).total_seconds();assert elapsed<1800,elapsed
assert read(P/'backend-parent-acceptance.json')['backend_gate_passed']
assert read(P/'build-acceptance.json')['complete'] and read(P/'tool-terminal.json')['exit_code']==0
freeze=read(P/'source-freeze.json');image=read(B/'frozen-image.json');assert sha(B/'rook2-exact')==image['sha256']
for n,h in freeze['files'].items():assert sha(W/n)==h,n
for n,h in selection['baseline_files_sha256'].items():assert sha(R/n)==h,n
jobs=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  exe=os.readlink(d/'exe')
  if Path(exe).name.startswith(('rook2','cargo','rustc','callgrind','valgrind','git','objdump','readelf','llvm-profdata','nm','tar')):jobs.append({'pid':int(d.name),'exe':exe})
 except OSError:pass
assert not jobs,jobs
X.mkdir();plan=read(Q/'plan.json');put(X/'inert-plan-before.json',plan)
for n in ['pilot.py','reconcile_pilot.py','check_pilot.mjs']:shutil.copyfile(Q/n,X/n);assert sha(Q/n)==sha(X/n)
plan.update(status='ACTIVE62 same-profile PGO use-only build and changed actual hot layout admitted; one fixed70 launch',parent_review_complete=True,backend_review_complete=True,all_owned_jobs_closed=True,launch_authorized=True,quiet_point_verified=True,source_graph=freeze['source_graph_sha256'],source_counts={'candidate_native':51,'candidate_tools':23,'candidate_total':74,'control_native':51,'control_tools':23,'control_total':74},native_tests_executed=False,actual_tests={'new_artifact_library_tests':0,'native_source51_identical_to_production57':True,'behavioral_artifact_validation':'Each pilot lifetime checked by original oracle; broad validation only if this fixed screen passes'},expected_changed_existing_native_files=[],expected_changed_existing_native_file_count=0,expected_added_native_files=[],prerequisites_pending=[])
plan['frozen_rule']['otherwise']='PARK without retry, retune, additional build/training or broad qualification'
plan['variants']['candidate']={'path':str(B/'rook2-exact'),'sha256':image['sha256']};plan['driver_sha256']=sha(X/'pilot.py')
for key,path in {'actual_build':B/'receipt.json','actual_image_freeze':B/'frozen-image.json','actual_archive':B/'archive-receipt.json','actual_backend':K/'review.md','backend_parent_acceptance':P/'backend-parent-acceptance.json','parent_independent_build_provenance_actual':P/'tool-terminal.json','actual_full_freeze':P/'source-freeze.json'}.items():plan[key]={'path':str(path),'sha256':sha(path)}
plan['source_binding'].update(candidate_source={'path':str(P/'source-freeze.json'),'sha256':sha(P/'source-freeze.json'),'graph':freeze['source_graph_sha256']},candidate_receipt=plan['actual_build'],candidate_frozen_image=image,candidate_archive=read(B/'archive-receipt.json'),parent_full_freeze=plan['actual_full_freeze'],binding_mode=selection['profile_policy'])
plan['actual_selection']=plan['selection'];plan['clock_selection']=plan['selection_budget'];plan['source_freeze']=plan['actual_full_freeze'];plan['candidate_profile']={'path':str(E/'bitplane-pin-summary-pgo-training-20261020-01/merged.profdata'),'sha256':selection['profile_sha256']};plan['candidate_own_profile_sha256']=selection['profile_sha256'];plan['expected_build']['candidate_actual_effective_flags']=read(B/'receipt.json')['rust_flags']
inputs=plan['immutable_inputs']
for d in [P,B,K,S,Q,E/'exttsp-profiled-recipe-20261020-01',E/'exttsp-profiled-backend-preparation-20261020-01',E/'current57-code-layout-feasibility-20261020-01']:
 for f in d.rglob('*'):
  if f.is_file():inputs[str(f)]=sha(f)
for n,h in freeze['files'].items():inputs[str(W/n)]=h
for n in ['pilot.py','reconcile_pilot.py','check_pilot.mjs']:inputs[str(X/n)]=sha(X/n)
for n,h in inputs.items():assert sha(Path(n))==h,n
plan['activation_utc']=now.isoformat();plan['selection_elapsed_at_activation_s']=elapsed
put(X/'plan.json',plan)
put(X/'execution-clearance.json',{'launch_authorized':True,'plan_sha256':sha(X/'plan.json'),'parent_review_complete':True,'backend_review_complete':True,'all_owned_jobs_closed':True,'quiet_point_verified':True,'point_only_no_host_exclusivity_claim':True,'selection_elapsed_s':elapsed,'cpu15_owned_jobs':[]})
print('ACTUAL62_SCREEN_ACTIVATED',sha(X/'plan.json'),elapsed,len(inputs))
