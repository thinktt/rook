"""Current25 offline raw copy-call attribution; no binary tool or engine invocation."""
from pathlib import Path
from collections import Counter
import hashlib,json
P=Path(__file__).resolve().parent;E=P.parent
S=Path('/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src')
B=E/'ordinary-projected-bits-pgo-codegen-review-20261018-01'
O=E/'candidate25-callgrind-20261018-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
parser=E/'candidate26-checker-cost-review-20261018-01/analyze.py'
ns={'__name__':'offline_definitions','__file__':str(parser)}
exec(compile(parser.read_text(),str(parser),'exec'),ns)
inputs=[parser]+[O/n for n in ['profile-35.callgrind','profile-08.callgrind','provenance.json','independent-verification.json','tool-terminal.json']]+[B/n for n in ['identity.json','function-capture.json','candidate/body-14830.asm','candidate/body-2fb50.asm','candidate/body-2ace0.asm']]
inputs += [S/n for n in ['position.rs','evaluator.rs','ordinary.rs','quiescence.rs','history.rs','engine.rs']]
inputs += [Path('/home/legolas/king-spec/spec')/n for n in ['ordinary-iterations.md','quiescence-tree.md','move-sequence.md']]
pins={str(p):sha(p) for p in inputs}
identity=json.loads((B/'identity.json').read_text());capture=json.loads((B/'function-capture.json').read_text())
assert identity['images']['candidate']['image_sha256']=='51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a'
for name in ['body-14830','body-2fb50','body-2ace0']:
 assert capture['functions']['candidate'][name]['saved_asm_sha256']==sha(B/'candidate'/(name+'.asm'))
for name in ['position.rs','evaluator.rs','ordinary.rs','quiescence.rs','history.rs','engine.rs']:
 frozen=E/'ordinary-projected-bits-pgo-use-build-20261018-01/source-before/src'/name
 assert identity['source_input_sha256'][str(frozen)]==sha(S/name)
 current=Path('/home/legolas/rook2/src')/name;assert sha(current)==sha(frozen);pins[str(current)]=sha(current)
def recursion(r):return '::visit_ordinary_impl' in r['function'] or '::visit_q_impl' in r['function']
def nodepath(r):return recursion(r) or r['function']=='rook2::evaluator::Node::child'
cases={}
for case in ['35','08']:
 rows,arcs,total=ns['raw'](O/f'profile-{case}.callgrind')
 targets={r['callee_function'] for r in arcs if r['function']=='rook2::evaluator::Node::child' and r['file']==str(S/'position.rs') and r['line'] in [246,248]}
 assert len(targets)==1;target=targets.pop()
 copies=[r for r in arcs if r['callee_function']==target]
 copyself=[r for r in rows if r['function']==target]
 assert sum(r['Ir'] for r in copyself)==sum(r['Ir'] for r in copies)
 assert not any(r['function']==target for r in arcs),'Copy body must be a recorded leaf before incoming costs partition it'
 groups={};used_arcs=set();used_rows=set()
 predicates={
  'ordinary_entry_snapshot':lambda r:r['file']==str(S/'ordinary.rs') and r['line']==728 and '::visit_ordinary_impl' in r['function'],
  'Q_entry_snapshot':lambda r:r['file']==str(S/'quiescence.rs') and r['line']==234 and '::visit_q_impl' in r['function'],
  'required_parent_to_child_position_initialization':lambda r:r['file']==str(S/'position.rs') and r['line']==246 and nodepath(r),
  'temporary_to_child_position_transport':lambda r:r['file']==str(S/'position.rs') and r['line']==248 and nodepath(r),
 }
 for name,predicate in predicates.items():
  selected_arcs=[r for r in copies if predicate(r)];selected_rows=[r for r in rows if predicate(r)]
  aid={r['raw_line'] for r in selected_arcs};rid={r['raw_line'] for r in selected_rows}
  assert not aid&used_arcs and not rid&used_rows;used_arcs|=aid;used_rows|=rid
  assert all(r['Ir']==29*r['explicit_calls'] for r in selected_arcs)
  calleecost=sum(r['Ir'] for r in selected_arcs);caller=sum(r['Ir'] for r in selected_rows);calls=sum(r['explicit_calls'] for r in selected_arcs)
  groups[name]={'recorded_explicit_copy_calls':calls,'logical_bytes_at160_per_call':160*calls,'copy_leaf_Ir':calleecost,'exclusive_related_caller_source_rows_Ir':caller,'known_disjoint_Ir_sum':calleecost+caller,'percent_total_simulated_Ir':100*(calleecost+caller)/total,'raw_copy_arcs':selected_arcs,'raw_caller_rows':selected_rows}
 apply=[r for r in rows if r['function']=='rook2::position::Position::apply_unchecked']
 results=[r for r in rows if r['file'].endswith('/core/src/result.rs') and recursion(r)]
 cases[case]={'total_simulated_Ir':total,'resolved_copy_leaf':target,'all_copy_leaf_Ir':sum(r['Ir'] for r in copyself),'groups':groups,'apply_unchecked_all_exclusive_inline_partitions_Ir':sum(r['Ir'] for r in apply),'result_rs_positive_and_zero_rows_recursion_Ir':sum(r['Ir'] for r in results),'return_attribution_caution':'result.rs rows are not complete return-packing cost or a savings envelope','remaining_copy_Ir_not_selected':sum(r['Ir'] for r in copies)-sum(g['copy_leaf_Ir'] for g in groups.values())}
put('attribution.json',{'cases':cases,'row_and_copy_arc_partitions_disjoint':True,'leaf_incoming_Ir_sum_equals_exclusive_self':True,'note':'Inclusive call arcs partition a non-recursive leaf. They replace, never add to, its exclusive rows in the accounting. Their caller source rows are distinct exclusive instructions. This does not charge the entire child/apply or recursive owner as avoidable.'})
assert all(sha(Path(p))==h for p,h in pins.items())
put('input-pins.json',pins)
print(json.dumps({c:{'total':r['total_simulated_Ir'],'groups':{n:{k:v for k,v in g.items() if not k.startswith('raw_')} for n,g in r['groups'].items()},'apply_self':r['apply_unchecked_all_exclusive_inline_partitions_Ir'],'result_rs':r['result_rs_positive_and_zero_rows_recursion_Ir']} for c,r in cases.items()},indent=2))
