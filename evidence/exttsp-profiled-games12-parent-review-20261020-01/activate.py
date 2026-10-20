from pathlib import Path
import json,hashlib,shutil,os,datetime,subprocess
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'exttsp-profiled-games12-parent-review-20261020-01';Q=E/'exttsp-profiled-games12-preparation-20261020-01';X=E/'exttsp-profiled-games12-execution-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
report=read(E/'exttsp-profiled-standard54-results-20261020-01/report.json');assert report['complete'] and report['ordinary_sha256']=='01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d' and report['original_offline_checks']==432
assert read(E/'exttsp-profiled-wire-parent-review-20261020-01/acceptance.json')['complete']
assert read(E/'exttsp-profiled-standard54-checkpoint-20261020-01/postcommit-verification.json')['complete']
# Preserve accepted production while this new artifact undergoes regular12.
prior=read(E/'bitplane-pin-summary-integration-20261020-01/source-promotion.json')['files_sha256']
for n,h in prior.items():assert sha(R/n)==h,n
jobs=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  exe=os.readlink(d/'exe')
  if Path(exe).name.startswith(('rook2','cargo','rustc','callgrind','valgrind','git','objdump','readelf','llvm-profdata','nm','tar')):jobs.append({'pid':int(d.name),'exe':exe})
 except OSError:pass
assert not jobs,jobs
X.mkdir();plan=read(Q/'plan.json');put(X/'inert-plan-before.json',plan)
for n in ['reconcile.py','observe_placement.py']:shutil.copyfile(Q/n,X/n);assert sha(Q/n)==sha(X/n)
plan.update(status='ACTIVE62_REGULAR12_VALIDATION_AND_WHOLE_CPU',launch_authorized=True,quiet_window_authorized=True,launch_prerequisites='Root admits one fixed48-lifetime regular12 validation/timing after actual62full54/wire24; unchanged native51 and prior source-bound diagnostic facts; production remains57, no source promotion or qualification.')
fp=plan['future_prerequisites'];fp['current54_actual_terminal']={'path':str(E/'exttsp-profiled-standard54-execution-20261020-01/collector-terminal.json'),'sha256':sha(E/'exttsp-profiled-standard54-execution-20261020-01/collector-terminal.json')};fp['current54_independent_closure']={'path':str(E/'exttsp-profiled-standard54-results-20261020-01/report.json'),'sha256':sha(E/'exttsp-profiled-standard54-results-20261020-01/report.json')};fp['postuse54_wire24']={'whole54':fp['current54_independent_closure'],'wire24':{'path':str(E/'exttsp-profiled-wire-parent-review-20261020-01/acceptance.json'),'sha256':sha(E/'exttsp-profiled-wire-parent-review-20261020-01/acceptance.json')}};fp['note']='Actual62full54/wire24 close; this fixed12 measurement itself validates regular12. No completed12 or source promotion asserted before actual execution.'
plan['commands_serial']=[[str(value).replace(str(Q),str(X)) for value in row] for row in plan['commands_serial']]
inputs=plan['dependency_sha256']
for d in [P,Q,E/'exttsp-profiled-standard54-results-20261020-01',E/'exttsp-profiled-wire-parent-review-20261020-01']:
 for f in d.rglob('*'):
  if f.is_file():inputs[str(f)]=sha(f)
for n in ['reconcile.py','observe_placement.py']:inputs[str(X/n)]=sha(X/n)
for n,h in inputs.items():assert sha(Path(n))==h,n
assert sha(Path(plan['engine']))==plan['engine_sha256']
plan['activation_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();put(X/'plan.json',plan)
put(X/'execution-clearance.json',{'launch_authorized':True,'plan_sha256':sha(X/'plan.json'),'quiet_point_approved':True,'all_owned_jobs_closed':True,'engine_cpu':14,'no_owned_cpu15_work':True,'point_only_no_host_exclusivity_claim':True,'source_promotion':False,'performance_qualification':False})
print('ACTUAL62_REGULAR12_ACTIVATED',sha(X/'plan.json'),len(inputs),flush=True)
