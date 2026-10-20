#!/usr/bin/env python3
"""Offline only: exact relation948c vs activity7cf seven-case frozen70-lifetime pilot."""
from pathlib import Path
import hashlib,json,math,os,statistics,subprocess
P=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence')
PRE=E/'full-byte-pair-relations-cpu-preparation-20261018-01'
RUN=E/'full-byte-pair-relations-cpu-pilot-20261018-01'
FUNCTIONAL=E/'full-byte-pair-relations-independent-preparation-20261018-01/independent-verification.json'
ROOT=Path('/home/legolas/rook2');KIT=Path('/home/legolas/king-spec/conformance/profiling')
H=[0,1,2,3,4,5,8,9,10,11,12,13]
CASES=['profile-01','profile-02','profile-04','profile-05','profile-29','profile-35','profile-08']
RULE='Consider own-source PGO only if sum-of-case-medians candidate/baseline<=0.995, at least5of7 case medians lower, and no individual median ratio>1.02; otherwise park absent an independently demonstrated collection or semantic defect'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write(chr(10))
def same_number(a,b):assert math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
def main():
 assert sorted(os.sched_getaffinity(0))==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 review=load(P/'review-clearance.json');assert review['parent_review_complete'] is True
 independent_plan=load(P/'plan.json');assert review['independent_plan_sha256']==sha(P/'plan.json')
 for path,h in independent_plan['dependencies'].items():assert sha(path)==h,path
 terminal=load(RUN/'tool-terminal.json');assert terminal==review['pilot_terminal']
 assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code']==0
 terminal_chunk=terminal.get('terminal_chunk_id') or terminal.get('chunk_id')
 assert isinstance(terminal_chunk,str) and terminal_chunk.strip()
 if terminal.get('session_id') is not None:assert isinstance(terminal['session_id'],int) and terminal['session_id']>0
 assert sha(RUN/'tool-terminal.json')==review['pilot_terminal_sha256']
 assert {str(P/'reconcile.py'),str(P/'replay70.mjs')}<=set(review['helpers'])
 for path,h in review['helpers'].items():assert sha(path)==h,path
 import sys
 sys.path.insert(0,str(PRE))
 from guard import validate_gate
 plan,clear,functional=validate_gate()
 FUNCTIONAL_SHA=sha(FUNCTIONAL)
 assert plan['cases']==CASES and list(plan['variants'])==['baseline','candidate'] and plan['advance_rule']==RULE
 assert plan['variants']['baseline']['sha256']=='7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'
 assert plan['variants']['candidate']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 assert clear['parent_review_complete'] and clear['all_owned_jobs_closed']
 assert sha(PRE/'plan.json')==clear['plan_sha256'] and sha(PRE/'run_pilot.py')==clear['driver_sha256']
 for required in [KIT/'benchmark.mjs',ROOT/'tools/measure.py',Path('/usr/bin/node'),Path('/usr/bin/python3')]:assert str(required) in clear['dependencies']
 assert sha(FUNCTIONAL)==FUNCTIONAL_SHA
 functional=load(FUNCTIONAL)
 assert functional['complete'] and functional['source46_tools23_archive69_equal'] and functional['only_influence_and_relation_table_changed_vs_activity_baseline'] and functional['activity_retained_pawn_unchanged']
 assert functional['native_tests']==178 and functional['strict54_original_checkReplay'] and functional['new_native_engine_runs']==0
 assert functional['engine_sha256']==plan['variants']['candidate']['sha256']
 assert functional['all_dependencies_stable'] and functional['compiler_cargo_generic_bound']
 assert len(functional['wire8_searches24_raw_protocol'])==8 and sum(x['searches'] for x in functional['wire8_searches24_raw_protocol'])==24
 assert str(FUNCTIONAL) in review['dependencies'] and review['dependencies'][str(FUNCTIONAL)]==FUNCTIONAL_SHA
 dependencies={Path(x) for x in clear['dependencies']}
 dependencies.update(Path(x) for x in review['dependencies'])
 dependencies.update(Path(x) for x in functional['dependencies'])
 dependencies.update(x for x in RUN.rglob('*') if x.is_file())
 dependencies.update([PRE/'plan.json',PRE/'launch-clearance.json',PRE/'run_pilot.py',P/'reconcile.py',P/'replay70.mjs',P/'review-clearance.json',P/'plan.json',PRE/'guard.py'])
 dependencies.update(Path(v['path']) for v in plan['variants'].values())
 before={str(x):sha(x) for x in sorted(dependencies)}
 for pins in [clear['dependencies'],review['dependencies'],functional['dependencies']]:
  for path,h in pins.items():assert before[path]==h,path
 assert load(RUN/'plan.json')==plan
 launch=load(RUN/'launch.json');assert launch['driver_sha256']==clear['driver_sha256'] and launch['clearance_sha256']==sha(PRE/'launch-clearance.json') and launch['plan_sha256']==clear['plan_sha256']
 result=load(RUN/'result.json');assert result['complete'] and result['failure'] is None and result['engine_lifetimes']==70 and [x['id'] for x in result['cases']]==CASES
 for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
 schedule=[dict(variant=x,warmup=True,repeat=0) for x in ['baseline','candidate']]
 for repeat in range(1,5):schedule += [dict(variant=x,warmup=False,repeat=repeat) for x in (['baseline','candidate'] if repeat%2 else ['candidate','baseline'])]
 cases=[];records=[];native_lifetimes=set();previous_reap=None
 oracle=load(KIT/'replay-oracle.json');workloads=load(KIT/'workloads.json')
 assert len(workloads['cases'])==54
 for case in CASES:
  directory=RUN/case;manifest=load(directory/'manifest.json');summary=load(directory/'summary.json')
  assert manifest['schedule']==schedule and manifest['case']==case and manifest['variants']==plan['variants']
  assert manifest['helper_affinity']==H and manifest['engine_cpu']==14
  assert manifest['limits']==dict(seconds_per_run=960,aggregate_seconds=1800,bytes_per_comparator_stream=8388608,cleanup_seconds=5)
  assert set(manifest['files'])=={str(ROOT/'tools/compare_ordinary.py'),str(ROOT/'tools/account_native.py'),str(KIT/'replay-check.mjs'),str(KIT/'workloads.json'),str(KIT/'replay-oracle.json')}
  for path,h in manifest['files'].items():assert path in clear['dependencies'] and clear['dependencies'][path]==h==sha(path)
  assert manifest['schema']=='rook2-balanced-ordinary-pilot-v1'
  assert summary['complete'] and summary['failure'] is None and len(summary['runs'])==10
  assert summary['input_hashes_after']==manifest['files']
  assert summary['artifact_hashes_after']=={k:v['sha256'] for k,v in plan['variants'].items()}
  outer=load(RUN/(case+'-terminal.json'))
  expected_outer=['/usr/bin/python3',str(ROOT/'tools/compare_ordinary.py'),'--case',case,'--output',str(directory)]
  for name,v in plan['variants'].items():expected_outer+=['--variant',name+'='+v['path']]
  assert outer['argv']==expected_outer and outer['exit_code']==0 and outer['actual_child_return_observed']
  assert isinstance(outer['pid'],int) and outer['pid']>0
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
   n=load(run/'native.json');c=load(run/'comparator.stdout');assert n['schema']=='rook2-native-wait4-v1'
   assert c['status']=='pass' and len(c['results'])==1 and c['selectedCases']==[case]
   cr=c['results'][0];assert cr['case']==case and cr['status']=='pass'
   assert cr['pid']==n['supervisor_pid'] and cr['exit']=={'code':0,'signal':None}
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
   assert isinstance(n['native_pid'],int) and n['native_pid']>0 and isinstance(n['supervisor_pid'],int) and n['supervisor_pid']>0
   assert n['native_pid']!=n['supervisor_pid']
   assert n['wall_ns']==n['reaped_monotonic_ns']-n['start_monotonic_ns']>0
   if previous_reap is not None:assert n['start_monotonic_ns']>=previous_reap
   previous_reap=n['reaped_monotonic_ns']
   assert n['user_cpu_s']>=0 and n['system_cpu_s']>=0 and n['total_cpu_s']>0
   same_number(n['user_cpu_s']+n['system_cpu_s'],n['total_cpu_s']);same_number(row['native_cpu_s'],n['total_cpu_s']);assert row['native_wall_ns']==n['wall_ns']
   identity=(n['native_pid'],n['start_monotonic_ns']);assert identity not in native_lifetimes;native_lifetimes.add(identity)
   if not step['warmup']:samples[step['variant']].append(n['total_cpu_s'])
   records.append(dict(case=case,index=index,variant=step['variant'],warmup=step['warmup'],repeat=step['repeat'],native_pid=n['native_pid'],supervisor_pid=n['supervisor_pid'],start_monotonic_ns=n['start_monotonic_ns'],cpu_s=n['total_cpu_s'],user_cpu_s=n['user_cpu_s'],system_cpu_s=n['system_cpu_s'],wall_ns=n['wall_ns'],native_pre_exec=n['native_pre_exec'],native_post_exec=n['native_post_exec'],native_wait_status=n['native_wait_status'],native_exit_code=n['native_exit_code'],argv=n['argv'],native_receipt=str(run/'native.json'),native_receipt_sha256=row['native_receipt_sha256'],comparator=str(run/'comparator.stdout'),comparator_sha256=row['comparator_sha256']))
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
 assert len(records)==70 and sum(x['warmup'] for x in records)==14 and sum(not x['warmup'] for x in records)==56 and len(native_lifetimes)==70
 contexts=[load(RUN/('context-'+part+'.json')) for part in ['before','after']]
 assert contexts[0]['utc']<=contexts[1]['utc']
 for context in contexts:assert context['helper_affinity']==H and context['native_jobs']==[]
 def ticks(context):
  line=next(x for x in context['proc_stat'].splitlines() if x.startswith('cpu15 '));return list(map(int,line.split()[1:]))
 start,end=map(ticks,contexts);assert len(start)==len(end)==10
 delta=[b-a for a,b in zip(start,end)];assert all(x>=0 for x in delta)
 sums={name:sum(x['variants'][name]['median'] for x in cases) for name in ['baseline','candidate']}
 ratio=sums['candidate']/sums['baseline'];lower=sum(x['median_ratio']<1 for x in cases);worst=max(x['median_ratio'] for x in cases)
 common=lower>=5 and worst<=1.02
 ratio08=next(x['median_ratio'] for x in cases if x['case']=='profile-08')
 advance=common and ratio<=0.995
 with (P/'checkReplay70.stdout').open('xb') as stdout,(P/'checkReplay70.stderr').open('xb') as stderr:
  argv=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/node',str(P/'replay70.mjs')];done=subprocess.run(argv,stdout=stdout,stderr=stderr)
 write('checkReplay70-terminal.json',dict(argv=argv,exit_code=done.returncode,actual_child_return_observed=True,new_engine_runs=0));assert done.returncode==0 and (P/'checkReplay70.stderr').read_bytes()==b''
 assert load(P/'original-checkReplay70-result.json')['original_oracle_calls']==70
 after={path:sha(Path(path)) for path in before};assert after==before
 write('independent-reconciliation.json',dict(complete=True,original_checkReplay=70,normal_lifetimes=70,warmups_excluded=14,measured=56,cases=cases,median_sums=sums,aggregate_ratio=ratio,aggregate_percent_lower=100*(1-ratio),lower_case_medians=lower,worst_case_ratio=worst,frozen_rule=RULE,common_gate_satisfied=common,profile08_ratio=ratio08,aggregate_gate_satisfied=ratio<=0.995,advance_rule_satisfied=advance,rule_outcome='eligible to consider fresh own-PGO' if advance else 'park',pilot_terminal=terminal,functional_result_sha256=FUNCTIONAL_SHA,cpu15=dict(before=start,after=end,tick_deltas=delta,total_first8=sum(delta[:8]),idle=delta[3],iowait=delta[4],nonidle_excluding_iowait=sum(delta[:8])-delta[3]-delta[4]),records=records,dependencies=before,all_inputs_stable=True,new_engine_runs=0,limits=['Custom7-case development set, no full54 CPU or qualification claim','No outlier deletion, confidence interval or significance claim','wait4 whole lifetime includes small Python child pre-exec prefix','One post-exec image/affinity/task observation, no continuous descendant/exclusivity proof','CPU15 ticks span whole suite; no per-variant attribution','No PMU, wall ratio or profile transfer']))
 print(json.dumps(dict(complete=True,lifetimes=70,aggregate_ratio=ratio,advance_rule_satisfied=advance,new_engine_runs=0)))
if __name__=='__main__':
 try:main()
 except BaseException as error:write('failure.json',dict(error=repr(error),new_engine_runs=0));raise
