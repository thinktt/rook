"""Read-only current25 line-position sort attribution; no native/tools/profiling."""
from pathlib import Path
from collections import Counter
import json,hashlib
P=Path(__file__).resolve().parent;E=P.parent
O=E/'candidate25-callgrind-20261018-01';S=Path('/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src')
parser=E/'candidate26-checker-cost-review-20261018-01/analyze.py';ns={'__name__':'offline_defs','__file__':str(parser)}
exec(compile(parser.read_text(),str(parser),'exec'),ns)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
B=E/'ordinary-projected-bits-pgo-codegen-review-20261018-01'
inputs=[parser]+[O/n for n in ['profile-35.callgrind','profile-08.callgrind','provenance.json','independent-verification.json']]+[B/n for n in ['identity.json','function-capture.json','candidate/body-2fb50.asm','candidate/body-2ace0.asm']]+[S/n for n in ['tactical.rs','ordinary.rs','quiescence.rs']]+[Path('/home/legolas/king-spec/spec')/n for n in ['tactical-capture-order.md','search-candidate-order.md','quiescence-candidates.md']]
pins={str(p):sha(p) for p in inputs}
identity=json.loads((B/'identity.json').read_text());capture=json.loads((B/'function-capture.json').read_text())
assert identity['images']['candidate']['image_sha256']=='51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a'
for n in ['body-2fb50','body-2ace0']:assert capture['functions']['candidate'][n]['saved_asm_sha256']==sha(B/'candidate'/(n+'.asm'))
for name in ['tactical.rs','ordinary.rs','quiescence.rs']:
 frozen=E/'ordinary-projected-bits-pgo-use-build-20261018-01/source-before/src'/name
 assert identity['source_input_sha256'][str(frozen)]==sha(S/name)
 root=Path('/home/legolas/rook2/src')/name;assert sha(root)==sha(S/name);pins[str(root)]=sha(root)
allcases={}
for case in ['35','08']:
 rows,arcs,total=ns['raw'](O/f'profile-{case}.callgrind')
 selected=[r for r in rows if r['file']==str(S/'tactical.rs') and ('::visit_ordinary_impl' in r['function'] or '::visit_q_impl' in r['function'])]
 categories={'sort_priority_load_250':{250},'sort_comparison_bounds_cursor_252':{252},'sort_move_and_priority_shifts_253_254':{253,254},'sort_final_item_stores_257_258':{257,258},'preferred_low_partition_322_330':set(range(322,331)),'Q_preference_209_241':set(range(209,242)),'direct_final_copy_setup_336':{336},'unidentified_tactical_line0':{0}}
 buckets={};used=set()
 for name,lines in categories.items():
  a=[r for r in selected if r['line'] in lines];ids={r['raw_line'] for r in a};assert not ids&used;used|=ids;buckets[name]={'Ir':sum(r['Ir'] for r in a),'raw_rows':a}
 remaining=[r for r in selected if r['raw_line'] not in used];assert not remaining
 packets={}
 for fn in sorted({r['function'] for r in selected}):
  f=[r for r in selected if r['function']==fn]
  starts=[r['raw_line'] for r in f if r['line']==250];ends=[r['raw_line'] for r in f if r['line']==258]
  assert len(starts)==4 and len(ends)==2,(fn,starts,ends)
  packets[fn]=[]
  for label,lo,hi in [('A',starts[0],ends[0]),('B',starts[2],ends[1])]:
   a=[r for r in f if lo<=r['raw_line']<=hi and r['line']!=0];counter=Counter()
   for r in a:counter[r['line']]+=r['Ir']
   packets[fn].append({'cluster':label,'raw_first':lo,'raw_last':hi,'positive_tactical_source_Ir':sum(counter.values()),'line_Ir':dict(sorted(counter.items())),'comparison_252_raw_components':[r for r in a if r['line']==252],'rows':a,'stage_interpretation':'consistent with gap6' if label=='A' else 'consistent with gap1','interpretation_is_inferred_not_instruction_address_counter':True})
 costs={n:b['Ir'] for n,b in buckets.items()};sort=sum(v for n,v in costs.items() if n.startswith('sort_'))
 allcases[case]={'total_simulated_Ir':total,'recursive_tactical_file_exclusive_Ir':sum(costs.values()),'buckets':buckets,'priority_sequence_positive_rows_Ir':sort,'priority_sequence_positive_rows_percent':100*sort/total,'comparison_252_combined_both_stages_percent':100*costs['sort_comparison_bounds_cursor_252']/total,'clusters':packets,'gap_specific_cost_limit':'Raw positions:line do not carry instruction addresses. A/B phase interpretation is consistent with two unrolled saved loops, but unconditional exact gap attribution is not claimed. Combined source rows and raw disjoint clusters are exact.'}
assert all(sha(Path(p))==h for p,h in pins.items())
put('input-pins.json',pins);put('attribution.json',{'complete':True,'cases':allcases,'all_inputs_unchanged':True,'new_native_binutils_profile_runs':0})
print(json.dumps({c:{'total':v['total_simulated_Ir'],'tactical_recursive_Ir':v['recursive_tactical_file_exclusive_Ir'],'buckets':{n:b['Ir'] for n,b in v['buckets'].items()},'sort_percent':v['priority_sequence_positive_rows_percent'],'comparison_percent':v['comparison_252_combined_both_stages_percent'],'cluster_sums':{label:sum(p['positive_tactical_source_Ir'] for fs in v['clusters'].values() for p in fs if p['cluster']==label) for label in ['A','B']}} for c,v in allcases.items()},indent=2))
