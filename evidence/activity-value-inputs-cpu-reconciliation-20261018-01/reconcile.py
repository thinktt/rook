#!/usr/bin/env python3
"""Offline only: exact activity7cf vs39c seven-case frozen70-lifetime pilot."""
from pathlib import Path
import hashlib,json,math,os,statistics,subprocess
P=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence')
PRE=E/'activity-value-inputs-cpu-preparation-20261018-01'
RUN=E/'activity-value-inputs-cpu-pilot-20261018-01'
ROOT=Path('/home/legolas/rook2');KIT=Path('/home/legolas/king-spec/conformance/profiling')
H=[0,1,2,3,4,5,8,9,10,11,12,13]
CASES=['profile-01','profile-02','profile-04','profile-05','profile-29','profile-35','profile-08']
RULE='Exploratory only: consider a fresh own-PGO comparison if aggregate median-sum ratio<=0.995, at least5of7 median ratios<1.0 and no individual median ratio>1.02. Otherwise park this narrow candidate unless independent evidence identifies a concrete invalid collection or semantic issue. No favorable-case reruns or tuning to timing results.'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write(chr(10))
def same_number(a,b):assert math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
def main():
 assert sorted(os.sched_getaffinity(0))==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 review=load(P/'review-clearance.json');assert review['parent_review_complete'] and review['pilot_actual_terminal']=='041daf/0'
 assert {str(P/'reconcile.py'),str(P/'replay70.mjs')}<=set(review['helpers'])
 for path,h in review['helpers'].items():assert sha(path)==h,path
 plan=load(PRE/'plan.json');clear=load(PRE/'launch-clearance.json')
 assert plan['cases']==CASES and list(plan['variants'])==['baseline','candidate'] and plan['advance_rule']==RULE
 assert plan['variants']['baseline']['sha256']=='39cadc627f110e651410933525ee7ab28dcb7f0eb1d9dc1fe25aad1d74e6bb2e'
 assert plan['variants']['candidate']['sha256']=='7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'
 assert clear['parent_review_complete'] and clear['all_owned_jobs_closed']
 assert sha(PRE/'plan.json')==clear['plan_sha256'] and sha(PRE/'run_pilot.py')==clear['driver_sha256']
 assert str(KIT/'benchmark.mjs') in clear['dependencies']
 dependencies={Path(x) for x in clear['dependencies']}
 dependencies.update(x for x in RUN.rglob('*') if x.is_file())
 dependencies.update([PRE/'plan.json',PRE/'launch-clearance.json',PRE/'run_pilot.py',P/'reconcile.py',P/'replay70.mjs',P/'review-clearance.json'])
 dependencies.update(Path(v['path']) for v in plan['variants'].values())
 before={str(x):sha(x) for x in sorted(dependencies)}
 for path,h in clear['dependencies'].items():assert before[path]==h,path
 assert load(RUN/'plan.json')==plan
 launch=load(RUN/'launch.json');assert launch['driver_sha256']==clear['driver_sha256'] and launch['clearance_sha256']==sha(PRE/'launch-clearance.json') and launch['plan_sha256']==clear['plan_sha256']
 terminal=load(RUN/'tool-terminal.json');assert terminal['session_id']==54227 and terminal['initial_chunk_id']=='f660c8' and terminal['terminal_chunk_id']=='041daf' and terminal['exit_code']==0
 result=load(RUN/'result.json');assert result['complete'] and result['failure'] is None and result['engine_lifetimes']==70 and [x['id'] for x in result['cases']]==CASES
 for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
 schedule=[dict(variant=x,warmup=True,repeat=0) for x in ['baseline','candidate']]
 for repeat in range(1,5):schedule += [dict(variant=x,warmup=False,repeat=repeat) for x in (['baseline','candidate'] if repeat%2 else ['candidate','baseline'])]
 cases=[];records=[];native_lifetimes=set()
 oracle=load(KIT/'replay-oracle.json');workloads=load(KIT/'workloads.json')
 assert len(workloads['cases'])==54
 for case in CASES:
  directory=RUN/case;manifest=load(directory/'manifest.json');summary=load(directory/'summary.json')
  assert manifest['schedule']==schedule and manifest['case']==case and manifest['variants']==plan['variants']
  assert manifest['helper_affinity']==H and manifest['engine_cpu']==14
  assert manifest['limits']==dict(seconds_per_run=960,aggregate_seconds=1800,bytes_per_comparator_stream=8388608,cleanup_seconds=5)
  assert set(manifest['files'])=={str(ROOT/'tools/compare_ordinary.py'),str(ROOT/'tools/account_native.py'),str(KIT/'replay-check.mjs'),str(KIT/'workloads.json'),str(KIT/'replay-oracle.json')}
  for path,h in manifest['files'].items():assert path in clear['dependencies'] and clear['dependencies'][path]==h==sha(path)
  assert summary['complete'] and summary['failure'] is None and len(summary['runs'])==10
  assert summary['input_hashes_after']==manifest['files']
  assert summary['artifact_hashes_after']=={k:v['sha256'] for k,v in plan['variants'].items()}
  outer=load(RUN/(case+'-terminal.json'))
  expected_outer=['/usr/bin/python3',str(ROOT/'tools/compare_ordinary.py'),'--case',case,'--output',str(directory)]
  for name,v in plan['variants'].items():expected_outer+=['--variant',name+'='+v['path']]
  assert outer['argv']==expected_outer and outer['exit_code']==0 and outer['actual_child_return_observed']
  assert (RUN/(case+'.stderr')).read_bytes()==b''
  outer_stdout=load(RUN/(case+'.stdout'));assert outer_stdout['complete'] and outer_stdout['failure'] is None and outer_stdout['output']==str(directory)
  assert {x.name for x in directory.iterdir() if x.is_dir()}=={f'{i:02d}-{step["variant"]}' for i,step in enumerate(schedule)}
  samples={'baseline':[],'candidate':[]}
  for index,(step,row) in enumerate(zip(schedule,summary['runs'])):
   assert {k:row[k] for k in step}==step and row['failure'] is None and row['comparator_exit']==0
   run=directory/f'{index:02d}-{step["variant"]}';engine=plan['variants'][step['variant']]
   expected=['/usr/bin/node',str(KIT/'replay-check.mjs'),'--case',case,'--','/usr/bin/python3',str(ROOT/'tools/account_native.py'),'--engine',engine['path'],'--record',str(run/'native.json'),'--known-single-process']
   assert row['command']==expected and sha(run/'native.json')==row['native_receipt_sha256'] and sha(run/'comparator.stdout')==row['comparator_sha256']
   assert (run/'comparator.stderr').read_bytes()==b''
   n=load(run/'native.json');c=load(run/'comparator.stdout');assert len(c['results'])==1 and c['selectedCases']==[case]
   cr=c['results'][0];assert cr['pid']==n['supervisor_pid'] and cr['exit']=={'code':0,'signal':None}
   assert c['workloadSha256']==clear['dependencies'][str(KIT/'workloads.json')] and c['oracleSha256']==clear['dependencies'][str(KIT/'replay-oracle.json')]
   assert n['engine']==engine['path'] and n['engine_sha256_before']==n['engine_sha256_after']==engine['sha256']
   assert n['launcher_sha256']==clear['dependencies'][str(ROOT/'tools/account_native.py')]
   assert n['python_executable']=='/usr/bin/python3' and sha(n['python_executable'])==n['python_executable_sha256']
   assert n['argv']==[engine['path'],*oracle['mode']]
   assert n['failure'] is None and n['exec_error'] is None and n['supervisor_signals']==[] and n['known_single_process']
   assert n['native_wait_status']==0 and os.waitstatus_to_exitcode(n['native_wait_status'])==n['native_exit_code']==0
   assert n['supervisor_affinity']==n['inherited_supervisor_affinity']==H
   assert n['native_pre_exec']==dict(pid=n['native_pid'],pgid=n['supervisor_pid'],affinity=[14])
   assert n['native_post_exec']==dict(path=engine['path'],affinity=[14],pgid=n['supervisor_pid'],tasks=[str(n['native_pid'])])
   assert n['wall_ns']==n['reaped_monotonic_ns']-n['start_monotonic_ns']>0
   assert n['user_cpu_s']>=0 and n['system_cpu_s']>=0
   same_number(n['user_cpu_s']+n['system_cpu_s'],n['total_cpu_s']);same_number(row['native_cpu_s'],n['total_cpu_s']);assert row['native_wall_ns']==n['wall_ns']
   identity=(n['native_pid'],n['start_monotonic_ns']);assert identity not in native_lifetimes;native_lifetimes.add(identity)
   if not step['warmup']:samples[step['variant']].append(n['total_cpu_s'])
   records.append(dict(case=case,index=index,variant=step['variant'],warmup=step['warmup'],repeat=step['repeat'],native_pid=n['native_pid'],cpu_s=n['total_cpu_s']))
  calculated={}
  for name,values in samples.items():
   assert len(values)==4
   calculated[name]=dict(samples=values,median=statistics.median(values),minimum=min(values),maximum=max(values))
   saved=summary['summaries'][name];assert saved['samples']==values
   for k in ['median','minimum','maximum']:same_number(calculated[name][k],saved[k])
  assert outer_stdout['summaries']==summary['summaries']
  assert next(x for x in result['cases'] if x['id']==case)['summaries']==summary['summaries']
  b=calculated['baseline'];c=calculated['candidate'];ratio=c['median']/b['median']
  relation='candidate-below' if c['maximum']<b['minimum'] else ('candidate-above' if b['maximum']<c['minimum'] else 'overlap')
  cases.append(dict(case=case,variants=calculated,median_ratio=ratio,range_relation=relation))
 assert len(records)==70 and sum(x['warmup'] for x in records)==14 and len(native_lifetimes)==70
 contexts=[load(RUN/('context-'+part+'.json')) for part in ['before','after']]
 assert contexts[0]['utc']<=contexts[1]['utc']
 for context in contexts:assert context['helper_affinity']==H and context['native_jobs']==[]
 def ticks(context):
  line=next(x for x in context['proc_stat'].splitlines() if x.startswith('cpu15 '));return list(map(int,line.split()[1:]))
 start,end=map(ticks,contexts);delta=[b-a for a,b in zip(start,end)];assert len(delta)==10 and all(x>=0 for x in delta)
 sums={name:sum(x['variants'][name]['median'] for x in cases) for name in ['baseline','candidate']}
 ratio=sums['candidate']/sums['baseline'];lower=sum(x['median_ratio']<1 for x in cases);worst=max(x['median_ratio'] for x in cases)
 advance=ratio<=0.995 and lower>=5 and worst<=1.02
 with (P/'checkReplay70.stdout').open('xb') as stdout,(P/'checkReplay70.stderr').open('xb') as stderr:
  argv=['/usr/bin/node',str(P/'replay70.mjs')];done=subprocess.run(argv,stdout=stdout,stderr=stderr)
 write('checkReplay70-terminal.json',dict(argv=argv,exit_code=done.returncode,new_engine_runs=0));assert done.returncode==0 and (P/'checkReplay70.stderr').read_bytes()==b''
 assert load(P/'original-checkReplay70-result.json')['original_oracle_calls']==70
 after={path:sha(Path(path)) for path in before};assert after==before
 write('independent-reconciliation.json',dict(complete=True,original_checkReplay=70,normal_lifetimes=70,warmups_excluded=14,measured=56,cases=cases,median_sums=sums,aggregate_ratio=ratio,aggregate_percent_lower=100*(1-ratio),lower_case_medians=lower,worst_case_ratio=worst,frozen_rule=RULE,advance_rule_satisfied=advance,rule_outcome='eligible to consider fresh own-PGO' if advance else 'park',cpu15=dict(tick_deltas=delta,total_first8=sum(delta[:8]),idle=delta[3],iowait=delta[4],nonidle_excluding_iowait=sum(delta[:8])-delta[3]-delta[4]),records=records,dependencies=before,all_inputs_stable=True,new_engine_runs=0,limits=['Custom7-case development set, no full54 CPU or qualification claim','No outlier deletion, confidence interval or significance claim','wait4 whole lifetime includes small Python child pre-exec prefix','One post-exec image/affinity/task observation, no continuous descendant/exclusivity proof','CPU15 ticks span whole suite; no per-variant attribution','No PMU, wall ratio or profile transfer']))
 print(json.dumps(dict(complete=True,lifetimes=70,aggregate_ratio=ratio,advance_rule_satisfied=advance,new_engine_runs=0)))
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),new_engine_runs=0));raise
