#!/usr/bin/env python3
"""Offline checkpoint audit of recorded47 evidence; only original offline JS oracle runs."""
from pathlib import Path
import hashlib,json,stat,statistics,subprocess,os
E=Path(__file__).resolve().parent
R=E.parent
S=R/'ordinary-position-borrow-generic-screen-20261019-01'
B=R/'ordinary-position-borrow-backend-preparation-20261019-01'
P=R/'ordinary-position-borrow-generic-screen-preparation-20261019-01'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,d):
 with (E/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
closure=read(B/'runtime-closure.json');members=closure['members_excluding_runtime_closure']
assert closure['complete'] and closure['all_owned_jobs_closed']
assert len(members)==closure['member_count_excluding_runtime_closure']==50
assert {p.name for p in B.iterdir() if p.is_file() and p.name!='runtime-closure.json'}==set(members)
for name,row in members.items():
 p=B/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'] and oct(stat.S_IMODE(p.stat().st_mode))==row['mode']
F=R/'ordinary-position-borrow-focused-native-check-20261019-01';focused=read(F/'result.json')
assert focused['complete'] and focused['failure'] is None and focused['focused_passed']==13
assert not focused['full_native_suite_executed'] and focused['source_unchanged'];assert len(focused['commands'])==13
for i,row in enumerate(focused['commands']):
 assert row['exit_code']==0 and row['actual_child_return_observed'] and row['pid']>0
 for stream in ['stdout','stderr']:assert sha(F/f'focused-{i}.{stream}')==row[stream+'_sha256']
 text=(F/f'focused-{i}.stdout').read_text();assert 'test result: ok. 1 passed; 0 failed;' in text
plan=read(S/'plan.json');assert plan==read(P/'plan.json');assert plan['cases']==['profile-01','profile-02','profile-04','profile-05','profile-29','profile-35','profile-08']
ind=read(S/'independent-reconciliation.json');assert ind['complete'] and ind['original_checkReplay_count']==70
rows=[];cases=[]
for case in plan['cases']:
 d=S/case;report=read(d/'summary.json');manifest=read(d/'manifest.json')
 assert report['complete'] and report['failure'] is None and len(report['runs'])==len(manifest['schedule'])==10
 assert manifest['variants']==plan['variants']
 for i,(step,row) in enumerate(zip(manifest['schedule'],report['runs'])):
  assert all(row[k]==v for k,v in step.items());run=d/f'{i:02d}-{row["variant"]}';native=read(run/'native.json');comp=read(run/'comparator.stdout')
  assert row['failure'] is None and row['comparator_exit']==0
  assert sha(run/'native.json')==row['native_receipt_sha256'] and sha(run/'comparator.stdout')==row['comparator_sha256']
  assert not (run/'comparator.stderr').stat().st_size
  assert native['failure'] is None and native['native_exit_code']==native['native_wait_status']==0
  assert native['engine_sha256_before']==native['engine_sha256_after']==plan['variants'][row['variant']]['sha256']
  assert native['total_cpu_s']==native['user_cpu_s']+native['system_cpu_s']==row['native_cpu_s']
  assert native['native_pre_exec']['affinity']==native['native_post_exec']['affinity']==[14]
  assert native['native_post_exec']['tasks']==[str(native['native_pid'])]
  assert comp['status']=='pass' and comp['selectedCases']==[case] and len(comp['results'])==1
  rows.append(dict(case=case,repeat=row['repeat'],variant=row['variant'],warmup=row['warmup'],cpu_s=native['total_cpu_s'],native_pid=native['native_pid']))
 stats={}
 for variant in ['baseline','candidate']:
  vals=[x['cpu_s'] for x in rows if x['case']==case and x['variant']==variant and not x['warmup']];assert len(vals)==4
  stats[variant]=dict(samples=vals,median=statistics.median(vals),minimum=min(vals),maximum=max(vals));assert stats[variant]==report['summaries'][variant]
 cases.append(dict(case=case,statistics=stats,ratio=stats['candidate']['median']/stats['baseline']['median']))
assert rows==ind['native_rows'] and cases==ind['cases'];assert len(rows)==70 and len({x['native_pid'] for x in rows})==70 and sum(x['warmup'] for x in rows)==14
sums={v:sum(c['statistics'][v]['median'] for c in cases) for v in ['baseline','candidate']};ratio=sums['candidate']/sums['baseline'];lower=sum(x['ratio']<1 for x in cases);worst=max(x['ratio'] for x in cases)
assert sums==ind['sum_case_medians_s'] and ratio==ind['candidate_div_baseline'] and lower==7 and worst==ind['worst_case_ratio']
assert ratio<=.995 and lower>=5 and worst<=1.02 and ind['advance_under_declared_rule']
assert read(S/'independent-checkReplay.stdout')==dict(complete=True,originalCheckReplayCount=70,engineRuns=0)
assert not (S/'independent-checkReplay.stderr').stat().st_size
# Check transitive public JS/current checker inputs before running the same original offline oracle.
oracle_pins={path:h for path,h in plan['immutable_inputs'].items() if path.endswith('.mjs') or path.endswith('workloads.json') or path.endswith('oracle.json')}
assert str(P/'check_pilot.mjs') in oracle_pins
for path,h in oracle_pins.items():assert sha(path)==h,path
command=['/usr/bin/node',str(P/'check_pilot.mjs'),str(S/'plan.json')]
with (E/'original-checkReplay.stdout').open('xb') as out,(E/'original-checkReplay.stderr').open('xb') as err:
 child=subprocess.Popen(command,stdout=out,stderr=err);pid=child.pid;exit_code=child.wait()
assert exit_code==0 and not (E/'original-checkReplay.stderr').stat().st_size
assert read(E/'original-checkReplay.stdout')==dict(complete=True,originalCheckReplayCount=70,engineRuns=0)
for path,h in oracle_pins.items():assert sha(path)==h
put('original-checkReplay-command.json',dict(argv=command,pid=pid,exit_code=exit_code,actual_child_return_observed=True,engine_runs=0,source_pins=oracle_pins))
# Canonical root115 remains accepted43, independently of the47 trial.
cmp=R/'influence-bitsliced-sum-conformance-preparation-20261019-01/source-manifest.json';cm=read(cmp);assert len(cm['files'])==115
for rel,h in cm['files'].items():assert sha(R.parent/rel)==h,rel
assert hashlib.sha256(json.dumps(cm['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==cm['graph_sha256']
for term in [S/'tool-terminal.json',S/'independent-tool-terminal.json',F/'tool-terminal.json',B/'runtime-tool-terminal.json']:
 t=read(term);assert t['actual_tool_terminal_observed'] and t['exit_code']==0
put('independent-summary.json',dict(complete=True,runtime_schema='members_excluding_runtime_closure',runtime_members_verified=50,focused_logs_verified=13,full_native_suite_executed=False,lifetimes=70,warmups=14,measured=56,distinct_native_pids=70,original_offline_checkReplay_rechecked=70,new_engine_runs=0,sum_case_medians_s=sums,candidate_div_baseline=ratio,percent_lower=(1-ratio)*100,lower_cases=lower,worst_case_ratio=worst,advance_under_fixed_rule=True,canonical115_source_unchanged=True,canonical_source_graph=cm['graph_sha256'],canonical_manifest=str(cmp),canonical_manifest_sha256=sha(cmp),historical_preparation_closure_is_not_current_active_plan=True,scope='Closed generic development evidence only; no adoption, full-native, whole54/12 or qualification claim'))
print((E/'independent-summary.json').read_text())
