from pathlib import Path
import json,hashlib,shutil,datetime,os
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'activity-kind-return-parent-review-20261020-01';Q=E/'activity-kind-return-generic-screen-preparation-20261020-01';X=E/'activity-kind-return-generic-screen-execution-20261020-01';B=E/'activity-kind-return-generic-build-20261020-01';N=E/'activity-kind-return-native-20261020-01';K=E/'activity-kind-return-backend-review-20261020-01';S=E/'activity-kind-return-selection-20261020-01';W=Path('/home/legolas/rook2-work/imp2-activity-kind-return-20261020-01')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
selection=read(S/'selection.json');now=datetime.datetime.now(datetime.timezone.utc);elapsed=(now-datetime.datetime.fromisoformat(selection['selected_utc'])).total_seconds();assert elapsed<1800,elapsed
assert read(P/'backend-parent-acceptance.json')['backend_gate_passed']
assert read(P/'tool-terminal.json')['exit_code']==0 and read(N/'proof.json')['exit_code']==0
freeze=read(P/'source-freeze.json');image=read(B/'frozen-image.json');assert sha(B/'rook2-exact')==image['sha256']
for n,h in freeze['files'].items():assert sha(W/n)==h,n
for n,h in selection['baseline_source74_sha256'].items():assert sha(R/n)==h,n
jobs=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  exe=os.readlink(d/'exe')
  if Path(exe).name.startswith(('rook2','cargo','rustc','callgrind','valgrind','git','objdump','readelf','llvm-profdata','nm','tar')):jobs.append({'pid':int(d.name),'exe':exe})
 except OSError:pass
assert not jobs,jobs
X.mkdir()
plan=read(Q/'plan.json');put(X/'inert-plan-before.json',plan)
for n in ['pilot.py','reconcile_pilot.py','check_pilot.mjs']:shutil.copyfile(Q/n,X/n);assert sha(Q/n)==sha(X/n)
plan.update(status='ACTIVE60 closed source/build/library/backend; one fixed70 launch',parent_review_complete=True,backend_review_complete=True,all_owned_jobs_closed=True,launch_authorized=True,quiet_point_verified=True,source_graph=freeze['source_graph_sha256'],source_counts={'candidate_native':51,'candidate_tools':23,'candidate_total':74,'control_native':51,'control_tools':23,'control_total':74},native_declarations=197,library_declarations=195,development_declarations=2,native_tests_executed=True,focused_native_tests_executed=195,expected_focused_native_tests=195,expected_focused_command_groups=1,expected_native_declarations=197,expected_library_declarations=195,expected_development_declarations=2,expected_changed_existing_native_files=['src/activity.rs'],expected_changed_existing_native_file_count=1,expected_added_native_files=[],prerequisites_pending=[])
plan['mechanism_prospectus']=selection['mechanism'];plan['variants']['candidate']['sha256']=image['sha256'];plan['driver_sha256']=sha(X/'pilot.py')
for key,path in {'actual_build':B/'receipt.json','actual_image_freeze':B/'frozen-image.json','actual_archive':B/'archive-receipt.json','actual_focused':N/'proof.json','focused_native_proof':N/'proof.json','actual_backend':K/'review.md','backend_parent_acceptance':P/'backend-parent-acceptance.json','parent_independent_build_provenance_actual':P/'tool-terminal.json','actual_full_freeze':P/'source-freeze.json'}.items():plan[key]={'path':str(path),'sha256':sha(path)}
plan['source_binding'].update(candidate_source={'path':str(P/'source-freeze.json'),'sha256':sha(P/'source-freeze.json'),'graph':freeze['source_graph_sha256']},candidate_receipt={'path':str(B/'receipt.json'),'sha256':sha(B/'receipt.json')},candidate_frozen_image=image,candidate_archive=read(B/'archive-receipt.json'),parent_full_freeze={'path':str(P/'source-freeze.json'),'sha256':sha(P/'source-freeze.json')},binding_mode='Actual60 frozen74/build/195 library passes/backend and selection budget; production remains57; no correction or PGO.')
inputs=plan['immutable_inputs']
for d in [P,N,B,K,S,E/'activity-kind-return-source-20261020-01',E/'current57-activity-kind-boundary-review-20261020-01',E/'current57-activity-boundary-discriminator-20261020-01']:
 for f in d.rglob('*'):
  if f.is_file():inputs[str(f)]=sha(f)
for n,h in freeze['files'].items():inputs[str(W/n)]=h
for n in ['pilot.py','reconcile_pilot.py','check_pilot.mjs']:inputs[str(X/n)]=sha(X/n)
for n,h in inputs.items():assert sha(Path(n))==h,n
plan['activation_utc']=now.isoformat();plan['selection_elapsed_at_activation_s']=elapsed
put(X/'plan.json',plan)
put(X/'execution-clearance.json',{'launch_authorized':True,'plan_sha256':sha(X/'plan.json'),'parent_review_complete':True,'backend_review_complete':True,'all_owned_jobs_closed':True,'quiet_point_verified':True,'point_only_no_host_exclusivity_claim':True,'selection_elapsed_s':elapsed,'cpu15_owned_jobs':[]})
print('ACTUAL60_SCREEN_ACTIVATED',sha(X/'plan.json'),elapsed,len(inputs))
