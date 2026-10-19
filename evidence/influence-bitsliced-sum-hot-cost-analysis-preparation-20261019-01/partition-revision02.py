"""Disjoint current43 source-context partition of frozen raw SELF; no runtime/tool."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,os
E=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
 with (E/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def owner(row,root):
 line=row['line'];file=row['file']
 if line==0:return 'unknown_line0_all_files'
 if file==root+'/src/influence/coherent.rs':
  if line in [15,16,17,18,74]:return 'initial_result_placement_color_return_context'
  if line in [19,20,21,22,24,31,38,48,52,56,60,64,68]:return 'list_counts_source_dispatch_context'
  if 25<=line<=30 or 32<=line<=37 or 39<=line<=45:return 'scalar_no_slider_PNK_context'
  if 49<=line<=51 or 53<=line<=55 or 57<=line<=59:return 'active_PNK_geometry_carry_callsite_context'
  if line in [61,65,69] or 78<=line<=88 or 93<=line<=129:return 'slider_geometry_context'
  if line in [47,62,66,70] or 134<=line<=161:return 'shared_counter_setup_accumulation_context'
  if line==72 or 162<=line<=203:return 'counter_transpose_output_source_context'
 if file==root+'/src/influence.rs':
  if 42<=line<=44:return 'initial_result_placement_color_return_context'
  if 165<=line<=167:return 'scalar_no_slider_PNK_context'
 if file==root+'/src/position.rs':
  if 175<=line<=179:return 'initial_result_placement_color_return_context'
  if 182<=line<=194:return 'list_counts_source_dispatch_context'
 if file==root+'/src/attacks.rs':
  if 69<=line<=73:return 'slider_geometry_context'
  if 78<=line<=88:return 'active_PNK_geometry_carry_callsite_context'
  if 91<=line<=95:return 'initial_result_placement_color_return_context'
 if '/stdarch/' in file:return 'unknown_positive_stdarch_intrinsic_context'
 if file.startswith(root+'/src/'):return 'unknown_positive_native_context'
 return 'unknown_positive_core_or_other_context'

def main():
 plan=load(E/'plan.json');assert plan['launch'] is True and plan['parent_activation']
 assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
 assert all(sha(p)==h for p,h in plan['input_sha256'].items())
 source_plan=load(E/'source-context-plan-revision02.json');assert sha(Path(plan['source_snapshot'])/'src/influence/coherent.rs')==source_plan['coherent_source_sha256']
 provenance=load(Path(plan['input_root'])/'provenance.json');root=provenance['compiled_source_root'];results={}
 for case in ['35','08']:
  raw=load(E/('profile-'+case+'-self-selection.json'));groups=defaultdict(list)
  for row in raw['raw_SELF_rows']:groups[owner(row,root)].append(row)
  ids=[r['raw_line'] for rows in groups.values() for r in rows]
  assert len(ids)==len(set(ids))==len(raw['raw_SELF_rows'])
  sums={name:dict(Ir=sum(r['Ir'] for r in rows),whole_percent=100*sum(r['Ir'] for r in rows)/raw['total_Ir'],producer_SELF_percent=100*sum(r['Ir'] for r in rows)/raw['producer_exclusive_SELF'],raw_rows=[r['raw_line'] for r in rows],rows=rows) for name,rows in groups.items()}
  assert sum(x['Ir'] for x in sums.values())==raw['producer_exclusive_SELF']
  position_rows=[r for r in raw['raw_SELF_rows'] if r['file']==root+'/src/position.rs' and 182<=r['line']<=194]
  detail=dict(Ir=sum(r['Ir'] for r in position_rows),whole_percent=100*sum(r['Ir'] for r in position_rows)/raw['total_Ir'],raw_rows=[r['raw_line'] for r in position_rows],note='Subset of list/source bucket, not added again; includes count/prefix/slice source context, not exact removable guards.')
  unknown=sum(v['Ir'] for k,v in sums.items() if k.startswith('unknown_'))
  results[case]=dict(whole_Ir=raw['total_Ir'],producer_SELF=raw['producer_exclusive_SELF'],disjoint_groups=sums,position_list_context_subset=detail,unknown_Ir=unknown,unknown_producer_percent=100*unknown/raw['producer_exclusive_SELF'],all_groups_exactly_sum_SELF=True,all_cost_rows_partitioned_once=True,no_arcs_added=True)
  print(json.dumps(dict(case=case,producer_SELF=raw['producer_exclusive_SELF'],groups={k:dict(Ir=v['Ir'],whole_percent=v['whole_percent']) for k,v in sums.items()},position_list_subset=detail,unknown_Ir=unknown)))
 assert all(sha(p)==h for p,h in plan['input_sha256'].items())
 save('partition-revision02.json',dict(complete=True,event_scope='Exact exclusive whole-lifetime simulated Ir/source contexts, not PMU/cycles/CPU/traffic or saving estimates.',cases=results,unknowns_retained=True,all_rows_disjoint=True,all_inputs_unchanged=True,shared_carry_not_assigned_between_PNK_and_sliders=True,absence_of_positive_attribution_is_not_free=True,old40_costs_or_line_numbers_transferred=False))
if __name__=='__main__':
 try:main()
 except BaseException as error:
  save('partition-revision02-failure.json',dict(complete=False,error=repr(error)));raise
