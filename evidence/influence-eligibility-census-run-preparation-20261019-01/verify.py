#!/usr/bin/env python3
"""Independent stored-output/PID/aggregate reconciliation; no engine launches."""
from pathlib import Path
import hashlib,json,os,subprocess
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(p,j):
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n')
BASELINE_FIELDS=['producer_calls', 'zero_result_payload_bytes', 'output_payload_bytes', 'bitplane_colors', 'scalar_colors', 'counter_plane_words_initialized', 'transpose_colors', 'full_sources', 'sources.0', 'sources.1', 'sources.2', 'sources.3', 'sources.4', 'sources.5', 'full_slider_sources', 'full_slider_directions', 'slider.source_calls', 'slider.slider_sources', 'slider.directions', 'slider.normal_targets', 'slider.weak_targets', 'slider.targets', 'slider.weak_nonempty_sources', 'slider.scalar_slider_target_counts_unknown', 'pnk_targets', 'carry_plane_updates', 'slider.source_kind.2', 'slider.source_kind.3', 'slider.source_kind.4']
EDGE_NAMES=['root_child','main_child','iio_child','null_child','mate_q_child','scout_retry','q_child','same_node_handoff']
def check_census(c,contract):
 assert contract['hook_version']==c['hook_version']==1 and contract['source_sha256'] and contract['all_work_fields']
 assert contract['baseline_fields']==BASELINE_FIELDS
 assert c['diagnostic_only'] is True and c['complete'] is True and c['engine_success'] is True and c['invalid_or_overflow'] is False
 assert c['live_frames']==c['pending_edges']==0
 t=c['totals'];bins=c['joint_bins'];assert isinstance(t,dict) and isinstance(bins,list) and len(bins)<=2048
 integer=lambda n:type(n) is int and 0<=n<2**64
 assert all(isinstance(k,str) and integer(v) for k,v in t.items())
 assert len({r['cohort'] for r in bins})==len(bins)
 for row in bins:
  assert set(row)=={'cohort','counts'} and isinstance(row['counts'],dict)
  assert row['cohort'].startswith(('frame/','demand/','producer/'))
  assert all(isinstance(k,str) and integer(v) for k,v in row['counts'].items()) and row['counts'].get('samples',0)>0
  allowed={'samples','native_demands','some_events','unassociated_events','same_node_handoff',*[f'frame_map_status.{name}' for name in ['native_map','some_only','unassociated_map_activity','no_map_events']]} if row['cohort'].startswith('frame/') else {'samples',*BASELINE_FIELDS} if row['cohort'].startswith('producer/') else {'samples',*contract['all_work_fields']}
  assert set(row['counts'])<=allowed,(row['cohort'],set(row['counts'])-allowed)
 V=lambda k:t.get(k,0)
 rows=lambda p:[r for r in bins if r['cohort'].startswith(p)]
 S=lambda rs,k:sum(r['counts'].get(k,0) for r in rs)
 frames=rows('frame/');demands=rows('demand/');producers=rows('producer/')
 assert V('frames_entered')==V('frames_left')==V('frames_with_native_map')+V('frames_without_native_map')==S(frames,'samples')
 assert sum(V('frames_entered.'+k) for k in ['root','ordinary','q'])==V('frames_entered')
 for kind in ['root','ordinary','q']:assert V('frames_entered.'+kind)==V('frames_left.'+kind)==S(rows('frame/'+kind+'/'),'samples')
 assert sum(v for k,v in t.items() if k.startswith('immediate_edge.'))==V('frames_entered')
 assert sum(v for k,v in t.items() if k.startswith('immediate_changes.'))==V('frames_entered')
 assert V('edges_opened')==V('edges_closed')==V('edges_consumed')+V('edges_unconsumed')
 assert V('edges_consumed')==sum(V('immediate_edge.'+k) for k in EDGE_NAMES)
 assert V('native_none_attempts')==V('native_none_completed')==S(demands,'samples')
 assert V('native_none_completed')==V('native_none_associated')+V('native_none_unassociated')+V('native_owner_position_mismatch')
 assert V('demand_not_certified')==V('native_none_unassociated')+V('native_owner_position_mismatch')
 assert S(frames,'native_demands')==V('native_none_associated')>=V('frames_with_native_map')
 assert V('ensure_some_events')==V('ensure_some_associated')+V('ensure_some_unassociated')
 assert S(frames,'some_events')==V('ensure_some_associated')
 statuses=['native_map','some_only','unassociated_map_activity','no_map_events']
 assert sum(V('frame_map_status.'+k) for k in statuses)==V('frames_left')
 assert V('frame_map_status.native_map')==V('frames_with_native_map')
 assert sum(V('frame_map_status.'+k) for k in statuses[1:])==V('frames_without_native_map')
 for k in statuses:assert V('frame_map_status.'+k)==S(frames,'frame_map_status.'+k)
 for row in frames:
  v=lambda k:row['counts'].get(k,0)
  assert sum(v('frame_map_status.'+k) for k in statuses)==v('samples')
  assert v('native_demands')>=v('frame_map_status.native_map') and v('some_events')>=v('frame_map_status.some_only') and v('unassociated_events')>=v('frame_map_status.unassociated_map_activity')
 assert S(frames,'unassociated_events')+V('unassociated_event_without_frame')==V('native_none_unassociated')+V('native_owner_position_mismatch')+V('ensure_some_unassociated')
 assert S(frames,'same_node_handoff')==V('immediate_edge.same_node_handoff')
 assert sum(V('owned_child_constructions.'+k) for k in ['null','ordinary','promotion','en_passant','castle'])==V('owned_child_constructions')

 assert V('producer_completed')==V('producer_coherent')+V('producer_scalar')==S(producers,'samples')==V('native_none_completed')+V('unassociated_direct_producer')
 native_producers=rows('producer/native_ensure/');direct=rows('producer/unassociated_direct/')
 assert S(native_producers,'samples')==V('native_none_completed') and S(direct,'samples')==V('unassociated_direct_producer')
 assert S([r for r in producers if r['cohort'].endswith('/coherent')],'samples')==V('producer_coherent')
 assert S([r for r in producers if r['cohort'].endswith('/scalar')],'samples')==V('producer_scalar')
 # Every completed None demand receives the same complete fresh-producer Work;
 # eligibility fields are cumulative annotations, never an alternative producer.
 for field in BASELINE_FIELDS:assert S(native_producers,field)==S(demands,field),field
 for row in producers+demands:
  v=lambda k:row['counts'].get(k,0)
  assert v('producer_calls')==v('samples')
  assert v('zero_result_payload_bytes')==v('output_payload_bytes')==128*v('samples')
  assert v('bitplane_colors')+v('scalar_colors')==2*v('samples')
  assert v('counter_plane_words_initialized')==8*v('bitplane_colors') and v('transpose_colors')==v('bitplane_colors')
  assert v('full_sources')==sum(v('sources.'+str(k)) for k in range(6))
  assert v('full_slider_sources')==v('sources.2')+v('sources.3')+v('sources.4')==v('slider.source_calls')==v('slider.slider_sources')
  assert v('full_slider_directions')==4*(v('sources.2')+v('sources.3'))+8*v('sources.4')==v('slider.directions')
  for kind in [2,3,4]:assert v('slider.source_kind.'+str(kind))==v('sources.'+str(kind))
  assert v('slider.targets')==v('slider.normal_targets')+v('slider.weak_targets')<=64*v('full_slider_sources')
  assert v('slider.weak_nonempty_sources')<=v('full_slider_sources')
  assert v('pnk_targets')<=2*v('sources.0')+8*(v('sources.1')+v('sources.5'))
  assert v('carry_plane_updates')<=8*v('full_sources')
  if not v('bitplane_colors'):assert v('carry_plane_updates')==0
  if row['cohort'].startswith('producer/'):
   scalar=row['cohort'].endswith('/scalar')
   assert v('slider.scalar_slider_target_counts_unknown')==(v('full_slider_sources') if scalar else 0)
   if scalar:assert v('bitplane_colors')==0
 for row in demands:
  v=lambda k:row['counts'].get(k,0)
  exclusive=['no_parent_context','no_movement','not_two_cell_shape','parent_native_unavailable','mask_coherence_unavailable','certified_two_cell_for_masks']
  assert sum(v(k) for k in exclusive)==v('samples')
  assert v('ordinary_or_promotion')+v('special_not_two_cell_candidate')==v('two_cell_shape')+v('not_two_cell_shape')
  assert v('two_cell_shape')==v('parent_native_unavailable')+v('parent_native_available_two_cell')
  assert v('parent_native_available_two_cell')==v('mask_coherence_unavailable')+v('certified_two_cell_for_masks')
  assert v('promotion')<=v('certified_two_cell_for_masks') and v('parent_checked')<=v('certified_two_cell_for_masks')
  assert v('remove_mover.source_calls')==v('add_mover.source_calls')==v('certified_two_cell_for_masks')
  assert v('remove_victim.source_calls')<=v('certified_two_cell_for_masks')
  assert v('affected_origins')==v('affected_origins.color0')+v('affected_origins.color1')
  assert v('affected_origins')<=v('affected_directions')<=v('replay_old_complete_source.directions')
  assert v('replay_old_complete_source.directions')==v('replay_new_complete_source.directions')
  for prefix in ['replay_old_complete_source','replay_new_complete_source']:
   assert v(prefix+'.source_calls')==v(prefix+'.slider_sources')==v('affected_origins')
  for prefix in ['remove_mover','remove_victim','add_mover','replay_old_complete_source','replay_new_complete_source']:
   assert v(prefix+'.normal_targets')+v(prefix+'.weak_targets')<=64*v(prefix+'.slider_sources')
   assert sum(v(prefix+'.source_kind.'+str(k)) for k in range(6))==v(prefix+'.source_calls')
   assert sum(v(prefix+'.source_kind.'+str(k)) for k in [2,3,4])==v(prefix+'.slider_sources')
   assert 4*(v(prefix+'.source_kind.2')+v(prefix+'.source_kind.3'))+8*v(prefix+'.source_kind.4')==v(prefix+'.directions')
  assert v('same_node_handoff')<=v('samples')
  assert v('changed_normal_targets')==v('normal_remove_only_targets')+v('normal_add_only_targets')
  assert v('changed_weak_targets')==v('weak_remove_only_targets')+v('weak_add_only_targets')
  assert v('replay_old_complete_source.normal_targets')+v('replay_new_complete_source.normal_targets')==v('changed_normal_targets')+2*v('same_normal_targets')
  assert v('replay_old_complete_source.weak_targets')+v('replay_new_complete_source.weak_targets')==v('changed_weak_targets')+2*v('same_weak_targets')
  assert max(v('changed_normal_targets'),v('changed_weak_targets'))<=v('changed_union_targets')<=v('changed_normal_targets')+v('changed_weak_targets')
  assert v('changed_union_targets')<=64*v('affected_origins')

 return dict(frames=V('frames_left'),frames_without_native_map=V('frames_without_native_map'),native_none_completed=V('native_none_completed'),associated=V('native_none_associated'),unassociated=V('native_none_unassociated'),owner_position_mismatch=V('native_owner_position_mismatch'),producer_completed=V('producer_completed'),producer_coherent=V('producer_coherent'),producer_scalar=V('producer_scalar'),frame_map_status={k:V('frame_map_status.'+k) for k in statuses},same_node_handoffs=V('immediate_edge.same_node_handoff'),owned_child_constructions=V('owned_child_constructions'),eligible_mask_demands=S(demands,'certified_two_cell_for_masks'),cohort_names=[r['cohort'] for r in bins],all_declared_balances_passed=True,logical_count_only=True)
def main():
 plan=load(P/'plan.json');output=Path(plan['output'])
 assert plan['verify'] is True and plan['census_schema_contract'] and plan['census_source_review']
 assert sorted(os.sched_getaffinity(0))==plan['helper_affinity'] and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 terminal=load(output/'tool-terminal.json');assert terminal['actual_tool_terminal_observed'] is True and terminal['exit_code']==0 and (terminal.get('terminal_chunk_id') or terminal.get('chunk_id'))
 result=load(output/'result.json');assert result['complete'] is True and result['failure'] is None and result['engine_runs']==2 and result['attempted_cases']==2
 assert load(output/'plan.json')==plan and plan['cases']==['profile-35','profile-08'] and [r['case'] for r in result['cases']]==plan['cases']
 pins=load(output/'input-closure.json');assert all(sha(p)==h for p,h in pins.items())
 assert pins[str(P/'plan.json')]==sha(P/'plan.json') and all(pins[p]==h for p,h in plan['known_inputs'].items())
 for name,h in plan['expected_script_sha256'].items():assert sha(P/name)==h and pins[str(P/name)]==h
 reference=load(plan['strict_reference']);mode=load('/home/legolas/king-spec/conformance/profiling/replay-oracle.json')['mode']
 cases=[]
 for case,record in zip(plan['cases'],result['cases']):
  d=output/case;assert (d/'census.json').stat().st_size<=plan['census_file_cap_bytes']
  command=load(d/'command.json');report=load(d/'checker.stdout');native=load(d/'native.json');census=load(d/'census.json')
  expected=['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--case',case,'--','/usr/bin/python3','/home/legolas/rook2/tools/account_native.py','--engine',plan['engine'],'--record',str((d/'native.json').resolve()),'--known-single-process']
  assert command['argv']==expected and command['actual_child_return_observed'] is True and command['exit_code']==0
  assert command['census_env']=={plan['env_key']:str((d/'census.json').resolve())} and not (d/'checker.stderr').stat().st_size
  assert report['status']=='pass' and report['selectedCases']==[case] and len(report['results'])==1
  fixtures=load(d/'input-expected.json')
  assert fixtures['input']==next(x for x in load('/home/legolas/king-spec/conformance/profiling/workloads.json')['cases'] if x['id']==case) and fixtures['expected']==next(x for x in load('/home/legolas/king-spec/conformance/profiling/replay-oracle.json')['cases'] if x['id']==case)
  row=report['results'][0];ref=next(x for x in reference['results'] if x['case']==case)
  assert row['command']==expected[5:]+mode
  assert row['status']=='pass' and row['complete'] and row['error'] is None and not row['truncated'] and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
  assert row['exit']==dict(code=0,signal=None) and row['stdout']==ref['stdout'] and row['stderr']==ref['stderr']==''
  for stream in ['stdout','stderr']:assert (d/(stream+'.raw')).read_bytes()==row[stream].encode() and sha(d/(stream+'.raw'))==record[stream+'_sha256']
  assert native['schema']=='rook2-native-wait4-v1' and native['failure'] is None and native['known_single_process'] is True
  assert native['native_exit_code']==0 and native['native_wait_status']==0 and not native['supervisor_signals'] and native['exec_error'] is None
  assert native['argv']==[plan['engine'],*mode] and native['engine_sha256_before']==native['engine_sha256_after']==plan['engine_sha256']
  assert native['supervisor_pid']==row['pid'] and native['native_pid']!=row['pid'] and native['native_pid']==record['native_pid']==census['native_pid']
  assert native['supervisor_affinity']==plan['helper_affinity'] and native['native_pre_exec']['affinity']==native['native_post_exec']['affinity']==[14] and native['native_post_exec']['tasks']==[str(native['native_pid'])]
  assert census['schema']==plan['census_schema'] and census['complete'] is True and census['engine_success'] is True
  assert sha(d/'census.json')==record['census_sha256'] and sha(d/'native.json')==record['native_receipt_sha256'] and sha(d/'checker.stdout')==record['checker_sha256']
  details=check_census(census,plan['census_schema_contract'])
  cases.append(dict(case=case,native_pid=native['native_pid'],raw_original_bytes_equal=True,aggregate_checks=details))
 assert len({r['native_pid'] for r in cases})==2
 before=load(output/'cpu15-before.json');after=load(output/'cpu15-after.json');delta=[b-a for a,b in zip(before,after)]
 assert delta==result['cpu15_point_delta'] and all(n>=0 for n in delta)
 busy=sum(delta[i] for i in [0,1,2,5,6,7]);assert busy==result['cpu15_point_nonidle_ticks']
 argv=['/usr/bin/node',str(P/'check-raw.mjs'),str(P/'plan.json')]
 with (output/'independent-checkReplay.stdout').open('xb') as out,(output/'independent-checkReplay.stderr').open('xb') as err:
  child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
 write(output/'independent-checkReplay-command.json',dict(argv=argv,pid=child.pid,actual_child_return_observed=True,exit_code=code))
 assert code==0 and not (output/'independent-checkReplay.stderr').stat().st_size and load(output/'independent-checkReplay.stdout')==dict(complete=True,originalCheckReplayCount=2,engineRuns=0)
 assert all(sha(p)==h for p,h in pins.items())
 write(output/'independent-verification.json',dict(complete=True,cases=cases,original_checkReplay_count=2,native_engine_runs=0,all_inputs_unchanged=True,cpu15_point_nonidle_ticks=busy,cpu15_point_scope='Disclosure only; nonzero OS ticks do not reject correct counts.',performance_claim=False,scope='Count-only diagnostic source-hook reconciliation; census IDs are not production provenance tokens.'))
 print(json.dumps(dict(complete=True,cases=2,native_engine_runs=0,performance_claim=False)))
if __name__=='__main__':main()
