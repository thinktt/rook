"""Disjoint source-context grouping of extracted43 ordinary suffix2 SELF only."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,os
E=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
def save(n,x):
 with (E/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def band(n,a,b):return a<=n<=b
def owner(r,root):
 n=r['line'];f=r['file']
 if n==0:return 'unknown_line0_all_files'
 if not f.startswith(root+'/src/'):return 'unknown_positive_core_alloc_other'
 f=f[len(root)+1:]
 if f=='src/ordinary.rs':
  if band(n,665,683) or band(n,717,777) or band(n,816,820) or band(n,1091,1096):return 'TT_entry_bounds_completion_source_context'
  if band(n,865,898) or band(n,945,976) or band(n,1099,1150) or band(n,1177,1195):return 'candidate_ordering_extensions_source_context'
  if band(n,837,838) or band(n,899,913) or band(n,977,1012) or band(n,1151,1152):return 'child_construction_frontier_checks_history_source_context'
  if band(n,839,855) or band(n,914,943) or band(n,1013,1089) or band(n,1153,1176):return 'recursive_window_return_completion_source_context'
  if band(n,685,697) or band(n,778,815) or band(n,821,836) or band(n,856,863):return 'evaluation_null_cutoff_source_context'
  return 'unknown_positive_ordinary_header_or_other'
 if f=='src/ordinary_policy.rs':
  if band(n,18,115) or band(n,145,163) or band(n,403,439):return 'TT_entry_bounds_completion_source_context'
  if band(n,263,378) or band(n,442,576):return 'candidate_ordering_extensions_source_context'
  if band(n,236,261):return 'child_construction_frontier_checks_history_source_context'
  if band(n,122,143) or band(n,171,234):return 'evaluation_null_cutoff_source_context'
 if f=='src/tactical.rs' and (band(n,244,261) or band(n,313,337)):return 'candidate_ordering_extensions_source_context'
 if f=='src/remembered.rs' and band(n,24,255):return 'TT_entry_bounds_completion_source_context'
 if f=='src/engine.rs' and band(n,149,154):return 'TT_entry_bounds_completion_source_context'
 if f=='src/work_clock.rs' and band(n,5,14):return 'TT_entry_bounds_completion_source_context'
 if f=='src/history.rs':
  if band(n,31,36) or band(n,84,143):return 'TT_entry_bounds_completion_source_context'
  if band(n,18,27) or band(n,60,63) or band(n,75,82):return 'child_construction_frontier_checks_history_source_context'
 if f=='src/evaluator.rs':
  if band(n,48,111):return 'child_construction_frontier_checks_history_source_context'
  if band(n,240,708):return 'inlined_evaluation_numeric_producer_source_context'
 if f=='src/position.rs':
  if band(n,201,255) or band(n,275,360) or band(n,521,531):return 'child_construction_frontier_checks_history_source_context'
  if band(n,362,385):return 'inlined_evaluation_numeric_producer_source_context'
 if f in ['src/evaluation.rs','src/endgame.rs','src/pawn_structure.rs','src/pawn_progress.rs','src/pawn_terms.rs','src/positional_terms.rs','src/shelter.rs','src/activity.rs']:return 'inlined_evaluation_numeric_producer_source_context'
 if f=='src/types.rs':return 'unknown_positive_shared_types'
 if f in ['src/attacks.rs','src/movegen.rs']:return 'unknown_positive_shared_geometry'
 if f=='src/position.rs':return 'unknown_positive_shared_position_lists_or_other'
 if f=='src/influence.rs':return 'unknown_positive_shared_influence'
 return 'unknown_positive_native_other'
def subset(rows,file,a,b,root):return [r for r in rows if r['file']==root+'/'+file and a<=r['line']<=b]
def stats(rows,total,ordinary):
 return dict(Ir=sum(r['Ir'] for r in rows),whole_percent=100*sum(r['Ir'] for r in rows)/total,ordinary_SELF_percent=100*sum(r['Ir'] for r in rows)/ordinary,physical_rows=len(rows),raw_rows=rows)
def main():
 assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
 root='/home/legolas/rook2-work/imp2-influence-bitsliced-sum-20261019-01';result={}
 for c in ['35','08']:
  x=load(E/f'profile-{c}-rows.json');total=x['whole_Ir'];ordinary=x['ordinary_SELF_Ir'];rows=x['raw_SELF_rows'];groups=defaultdict(list)
  for r in rows:groups[owner(r,root)].append(r)
  ids=[r['raw_line'] for rs in groups.values() for r in rs];assert len(ids)==len(set(ids))==len(rows)
  partitions={k:stats(rs,total,ordinary) for k,rs in groups.items()};assert sum(g['Ir'] for g in partitions.values())==ordinary
  subsets={}
  defs=[('priority_sequence_all_positive','src/tactical.rs',244,261),('ordering_partition_transport_positive','src/tactical.rs',313,337),('priority_policy_positive','src/ordinary_policy.rs',442,576),('extensions_policy_positive','src/ordinary_policy.rs',263,378),('node_child_retained_square_positive','src/evaluator.rs',48,111),('position_child_wrapper_positive','src/position.rs',251,255),('position_apply_mutation_positive','src/position.rs',275,352),('phase_positive','src/position.rs',362,385)]
  for name,file,a,b in defs:subsets[name]=stats(subset(rows,file,a,b,root),total,ordinary)
  insertion=[]
  for r in rows:
   if r['file']==root+'/src/tactical.rs' and r['line'] in [250,252,253,254,257,258]:insertion.append(r)
  subsets['six_insertion_rows_positive']=stats(insertion,total,ordinary)
  result[c]=dict(whole_Ir=total,ordinary_SELF_Ir=ordinary,exact_function=x['exact_function'],disjoint_groups=partitions,subsets_NOT_ADDED=subsets,unknown_Ir=sum(g['Ir'] for k,g in partitions.items() if k.startswith('unknown_')),all_groups_exactly_sum_ordinary_SELF=True,all_physical_rows_partitioned_once=True,inclusive_arcs_added=False)
  print(json.dumps(dict(case=c,groups={k:{q:v for q,v in g.items() if q!='raw_rows'} for k,g in partitions.items()},subsets={k:{q:v for q,v in g.items() if q!='raw_rows'} for k,g in subsets.items()})))
 save('source-partition.json',dict(complete=True,cases=result,source_context_not_work_saved=True,subsets_NOT_ADDED_to_disjoint_groups=True,no_line0_or_inline_helper_costs_reassigned=True))
if __name__=='__main__':main()
