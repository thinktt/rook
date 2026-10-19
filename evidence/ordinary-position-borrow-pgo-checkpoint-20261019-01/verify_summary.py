#!/usr/bin/env python3
"""Offline checkpoint audit of recorded47 evidence; only original offline JS oracle runs."""
from pathlib import Path
import hashlib,json,stat,statistics,subprocess,os
E=Path(__file__).resolve().parent
R=E.parent
S=R/'ordinary-position-borrow-pgo-screen-20261019-01'
B=R/'ordinary-position-borrow-pgo-backend-preparation-20261019-01'
P=R/'ordinary-position-borrow-pgo-screen-preparation-20261019-01'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,d):
 with (E/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
closure=read(B/'runtime-closure.json');members=closure['members_excluding_runtime_closure']
assert closure['complete'] and closure['all_owned_jobs_closed']
assert len(members)==closure['member_count_excluding_runtime_closure']
assert {p.name for p in B.iterdir() if p.is_file() and p.name!='runtime-closure.json'}==set(members)
for name,row in members.items():
 p=B/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'] and oct(stat.S_IMODE(p.stat().st_mode))==row['mode']
# Generic13 is historical finite scope only, not a new PGO test run.
F=R/'ordinary-position-borrow-focused-native-check-20261019-01';focused=read(F/'result.json')
assert focused['complete'] and focused['focused_passed']==13 and not focused['full_native_suite_executed']
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
assert sums==ind['sum_case_medians_s'] and ratio==ind['candidate_div_baseline'] and lower==4 and worst==ind['worst_case_ratio']
assert ratio>.995 and lower<5 and worst<=1.02 and not ind['advance_under_declared_rule']
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
# Independently bind all four PGO stages/profile/archive origins, no engine/merge rerun.
I=R/'ordinary-position-borrow-pgo-instrumented-build-20261019-01';U=R/'ordinary-position-borrow-pgo-use-build-20261019-01';T=R/'ordinary-position-borrow-pgo-training-20261019-01';PG=R/'ordinary-position-borrow-pgo-preparation-20261019-01'
summary=read(PG/'four-stage-summary.json');training=read(T/'training.json');verification=read(T/'verification.json')
assert summary['complete'] and training['complete'] and verification['complete'] and verification['independent_remerge_byte_identical']
assert verification['strict_replays']==verification['original_checkReplay_count']==verification['raw_training_protocol_cases']==54
assert len(training['raw_profiles_sha256'])==54
assert set(training['raw_profiles_sha256'])=={str(p) for p in (T/'raw').glob('*.profraw')}
for path,h in training['raw_profiles_sha256'].items():assert sha(path)==h
profile=sha(T/'merged.profdata');assert profile==summary['profile_sha256']==training['profile_sha256']==verification['merged_profile_sha256']==sha(T/'independently-merged.profdata')
assert read(T/'original-checkReplay.stdout')==dict(offlineOnly=True,originalCheckReplayCount=54)
assert not (T/'original-checkReplay.stderr').stat().st_size
replay=read(T/'replay.json');assert replay['status']=='pass' and len(replay['results'])==54
assert {r['pid'] for r in replay['results']}=={int(Path(x).stem.rsplit('-',1)[1]) for x in training['raw_profiles_sha256']}
for row in replay['results']:
 assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']==dict(code=0,signal=None)
 assert row['stderr']=='' and row['error'] is None and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
for path,h in read(T/'input-closure.json').items():assert sha(path)==h
assert sha(T/'replay.json')==training['replay_sha256'] and sha(T/'training.json')==verification['training_record_sha256']
import tarfile
source_archives=[]
for build in (I,U):
 receipt=read(build/'receipt.json');ar=read(build/'archive-receipt.json');frozen=read(build/'frozen-image.json');expect=receipt['source_sha256_before']|receipt['tool_sha256_before']
 assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged']
 assert receipt['source_sha256_before']==training['engine_source_sha256'] and len(expect)==72
 assert frozen['mode']=='0555' and frozen['sha256']==receipt['binary_output']['sha256']
 assert sha(build/ar['archive'])==ar['sha256'] and ar['verified_against_build_before_hashes']
 observed={}
 with tarfile.open(build/ar['archive'],'r:gz') as archive:
  for member in archive.getmembers():
   assert member.isfile() and member.name in expect and member.name not in observed
   with archive.extractfile(member) as stream:observed[member.name]=hashlib.file_digest(stream,'sha256').hexdigest()
 assert observed==expect;source_archives.append(dict(path=str(build/ar['archive']),sha256=ar['sha256'],files=72))
use=read(U/'receipt.json');assert use['binary_output']['sha256']==summary['candidate_image_sha256']==plan['variants']['candidate']['sha256']
assert use['pgo']['profile']==str(T/'merged.profdata') and use['pgo']['input_sha256_before'][str(T/'merged.profdata')]==profile
assert use['pgo']['input_sha256_after']==use['pgo']['input_sha256_before']
actuals={}
for path,chunk in [(I/'tool-terminal.json','56a1d7'),(T/'tool-terminal.json','6b39d1'),(T/'verify-tool-terminal.json','c1d7c1'),(U/'tool-terminal.json','c7a4c5'),(S/'tool-terminal.json','bba723'),(S/'independent-tool-terminal.json','8f3c8b')]:
 actual=read(path);assert actual['actual_tool_terminal_observed'] and actual['exit_code']==0 and actual['terminal_chunk_id']==chunk;actuals[str(path)]=actual
backend=read(R/'ordinary-position-borrow-pgo-parent-backend-review-20261019-01/decision.json');assert backend['candidate_sha256']==summary['candidate_image_sha256'] and backend['own_profile_sha256']==profile
park=read(R/'ordinary-position-borrow-pgo-decision-20261019-01/decision.json');assert park['decision']=='PARK_FAILED_FIXED_PGO_AGGREGATE_AND_LOWER_CASE_GATES'
assert park['reconciliation_sha256']==sha(S/'independent-reconciliation.json') and not park['retry_authorized'] and not park['rebuild_authorized'] and not park['broad_validation_authorized']
assert park['candidate_div_baseline']==ratio and park['lower_cases']==lower and park['worst_case_ratio']==worst
put('independent-summary.json',dict(complete=True,runtime_members_verified=len(members),generic_focused_scope_only=13,new_PGO_focused_tests=0,full_native_suite_executed=False,lifetimes=70,warmups=14,measured=56,distinct_native_pids=70,original_offline_checkReplay_rechecked=70,new_engine_runs=0,training54_original_check_and_profile_binding_verified=True,new_profile_merge_runs=0,source72_archives_reopened=source_archives,four_stage_actuals=actuals,candidate_sha256=summary['candidate_image_sha256'],own_profile_sha256=profile,sum_case_medians_s=sums,candidate_div_baseline=ratio,percent_lower=(1-ratio)*100,lower_cases=lower,worst_case_ratio=worst,advance_under_fixed_rule=False,park=True,canonical115_source_unchanged=True,canonical_source_graph=cm['graph_sha256'],canonical_manifest=str(cmp),canonical_manifest_sha256=sha(cmp),historical_preparation_closures_preserved_not_current_active_scope=True,backend_caveats=dict(ordinary_frame_delta_bytes=backend['ordinary']['frame_delta_bytes'],outlined_full_frame_delta_bytes=backend['outlined_full']['frame_delta_bytes'],preserved_copy_roles=backend['preserved_copy_roles'],limits=backend['limits']),scope='Closed own-PGO development screen PARK. Exactly70 PGO original outputs rechecked, not140; generic13 historical only. No retry/adoption/broad/full54/12 qualification.'))
print((E/'independent-summary.json').read_text())
