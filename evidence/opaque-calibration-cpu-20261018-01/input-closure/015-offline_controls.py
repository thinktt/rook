#!/usr/bin/env python3
"""Pure local files/metadata arithmetic controls. NEVER launches an engine."""
import argparse,copy,json,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from guard import authority_preflight,check_pins,file_identity,js_closure,status_fields,unprivileged,sha,load,SPEC
from reconcile import reference_reconcile,stats
HERE=Path(__file__).resolve().parent
def rejects(action):
 try:action()
 except (ValueError,AssertionError):return
 raise AssertionError('tampered control unexpectedly accepted')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 controls=[]
 with tempfile.TemporaryDirectory(prefix='offline-control-',dir=HERE) as directory:
  root=Path(directory);sample=root/'data.txt';sample.write_text('not an engine; never executed\n')
  check_pins({str(sample):sha(sample)});rejects(lambda:check_pins({str(sample):'0'*64}));controls.append('preexisting dependency mutation rejected')
  file=file_identity(sample);assert file['file_capability']=='absent-ENODATA';controls.append('read-only filecap absence on new plaintext fixture')
  authority=root/'authority.json';authority.write_text(json.dumps({'authorized':False}))
  output=root/'must-not-exist'
  rejects(lambda:authority_preflight(authority,sha(authority),output))
  assert not output.exists();controls.append('unauthorized launch rejected before any output or artifact read')
  profile=load(HERE/'profile.json')
  authority.write_text(json.dumps({'authorized':True,'scope':'opaque-fixed-calibrator-cpu-only','all_conflicting_owned_jobs_closed':True,'profile_path':str(HERE/'profile.json'),'profile_sha256':'0'*64}))
  rejects(lambda:authority_preflight(authority,sha(authority),output));assert not output.exists()
  expected=dict(profile['input_sha256']);expected[str(HERE/'profile.json')]=sha(HERE/'profile.json')
  bad={'authorized':True,'scope':'opaque-fixed-calibrator-cpu-only','all_conflicting_owned_jobs_closed':True,'profile_path':str(HERE/'profile.json'),'profile_sha256':sha(HERE/'profile.json'),'pins':dict(expected)}
  bad['pins'][str(HERE/'collect.py')]='0'*64;authority.write_text(json.dumps(bad))
  rejects(lambda:authority_preflight(authority,sha(authority),output));assert not output.exists()
  bad['pins']=expected;bad['collector_sha256']='0'*64;authority.write_text(json.dumps(bad))
  rejects(lambda:authority_preflight(authority,sha(authority),output));assert not output.exists()
  controls.append('profileSHA/dependency-map/collector-pin tampering fails before output or opaque artifact reads')
 status='Uid:\t1000\t1000\t1000\t1000\nCapInh:\t0\nCapPrm:\t0\nCapEff:\t0\nCapBnd:\tffffffff\nCapAmb:\t0\nPPid:\t123\n'
 assert unprivileged(status_fields(status));assert not unprivileged(status_fields(status.replace('CapEff:\t0','CapEff:\t1')))
 assert not unprivileged(status_fields(status.replace('1000\t1000\t1000\t1000','0\t0\t0\t0')));controls.append('actual status UID/capability parsing and negative controls')
 closure=js_closure(SPEC/'replay-check.mjs')
 assert {Path(name).name for name in closure}=={'replay-check.mjs','benchmark.mjs'};controls.append('complete current transitive publicJS closure includesbenchmark')
 reference=load('/home/legolas/spec-issues/v2.5.0/2026-10-16-performance-handoff/calibration/calibration-data.json')
 workloads=load(SPEC/'workloads.json');oracle=load(SPEC/'replay-oracle.json')
 result=reference_reconcile(reference,workloads,oracle);assert len(result['cases'])==54 and result['measured_rows']==162
 for mutate in [lambda r:r['measuredRows'][0]['lifetime'].__setitem__('totalMs',1),
  lambda r:r['cases'][0]['lifetime']['totalMs'].__setitem__('median',1),
  lambda r:r['measuredRows'][0].__setitem__('repeat',3),lambda r:r['candidate'].__setitem__('sha256','0'*64)]:
  bad=copy.deepcopy(reference);mutate(bad);rejects(lambda:reference_reconcile(bad,workloads,oracle))
 controls.append('reference all162rows/54summaries plus four independent tamper negatives')
 ids=[row['id'] for row in workloads['cases']];schedule=[(case,repeat,repeat==0) for case in ids for repeat in range(4)]
 assert len(schedule)==216 and sum(warm for _,_,warm in schedule)==54 and sum(not warm for _,_,warm in schedule)==162
 assert sum(len(case['posts'])*4 for case in oracle['cases'])==2496
 assert stats([1,2,3])['median']==2 and stats([0,0,0])['spreadPercentOfMedian'] is None
 controls.append('whole216 schedule/warmup exclusion/postcounts and no zero-denominator fill')
 report={'complete':True,'pure_offline_controls':controls,'reference_arithmetic_checks':result['arithmetic_checks'],
  'public_js_sha256':closure,'native_engine_executions':0,'PMU_admin_or_security_changes':0,'qualified_pass':False}
 with args.output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 print(json.dumps(report))
if __name__=='__main__':main()
