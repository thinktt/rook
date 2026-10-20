from pathlib import Path
import json,hashlib,shutil,os,datetime,subprocess
R=Path('/home/legolas/rook2');E=R/'evidence';P=E/'exttsp-profiled-whole-workload-parent-review-20261020-01';Q=E/'exttsp-profiled-standard54-preparation-20261020-01';X=E/'exttsp-profiled-standard54-execution-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
assert read(P/'admission.json')['complete']
assert read(E/'exttsp-profiled-wire-parent-review-20261020-01/acceptance.json')['complete']
assert read(E/'exttsp-profiled-pgo-screen-20261020-01/independent-reconciliation.json')['advance_under_declared_rule']
jobs=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  exe=os.readlink(d/'exe')
  if Path(exe).name.startswith(('rook2','cargo','rustc','callgrind','valgrind','git','objdump','readelf','llvm-profdata','nm','tar')):jobs.append({'pid':int(d.name),'exe':exe})
 except OSError:pass
assert not jobs,jobs
for n,h in read(P/'admission.json')['source117_prior_files_sha256'].items():assert sha(R/n)==h
X.mkdir();plan=read(Q/'plan.json');put(X/'inert-plan-before.json',plan)
for n in ['collect54.py','verify.py','check-raw.mjs']:shutil.copyfile(Q/n,X/n);assert sha(Q/n)==sha(X/n)
plan.update(launch_authorized=True,parent_review_complete=True,all_owned_native_jobs_closed=True,quiet_point_approved=True,prerequisites_pending=[],collection_directory=str(X/'collection'),scope='ACTIVE one prospective62 original54 validation/timing; same own57 profile use-only; no promotion or qualification. Prior57 comparison descriptive separate-window only.',rook2_commit=subprocess.check_output(['/usr/bin/git','-C',str(R),'rev-parse','HEAD'],text=True).strip())
plan['root_validation_admission']={'path':str(P/'admission.json'),'sha256':sha(P/'admission.json')};plan['actual_wire8_24_proof']={'path':str(E/'exttsp-profiled-wire-parent-review-20261020-01/acceptance.json'),'sha256':sha(E/'exttsp-profiled-wire-parent-review-20261020-01/acceptance.json')}
# Preserve false source_promoted/broad_gates flags: the measured54 itself supplies actual main-artifact coverage.
assert not plan['source_promoted'] and not plan['broad_gates_complete']
inputs=plan['input_sha256_before']
for d in [Q,P,E/'exttsp-profiled-wire-regression-20261020-01',E/'exttsp-profiled-wire-parent-review-20261020-01']:
 for f in d.rglob('*'):
  if f.is_file():inputs[str(f)]=sha(f)
for n in ['collect54.py','verify.py','check-raw.mjs']:inputs[str(X/n)]=sha(X/n)
for n,h in inputs.items():assert sha(Path(n))==h,n
assert sha(Path(plan['engine']))==plan['engine_sha256']
plan['activation_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();put(X/'plan.json',plan)
put(X/'execution-clearance.json',{'launch_authorized':True,'plan_sha256':sha(X/'plan.json'),'quiet_point_approved':True,'all_owned_jobs_closed':True,'engine_cpu':14,'no_owned_cpu15_work':True,'point_only_no_host_exclusivity_claim':True,'source_promotion':False,'performance_qualification':False})
print('ACTUAL62_WHOLE54_ACTIVATED',sha(X/'plan.json'),len(inputs),flush=True)
