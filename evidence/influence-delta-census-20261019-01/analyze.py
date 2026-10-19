"""Recorded current25 incoming influence edges only; no weighted-average attribution."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;E=P.parent;O=E/'candidate25-callgrind-20261018-01'
S=Path('/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
parser=E/'candidate26-checker-cost-review-20261018-01/analyze.py';ns={'__name__':'offline_defs','__file__':str(parser)}
exec(compile(parser.read_text(),str(parser),'exec'),ns)
inputs=[parser]+[O/n for n in ['profile-35.callgrind','profile-08.callgrind','provenance.json','independent-verification.json','tool-terminal.json']]+[S/n for n in ['influence.rs','ordinary.rs','quiescence.rs','evaluator.rs','timed.rs','position.rs']]+[E/'ordinary-projected-bits-pgo-codegen-review-20261018-01/identity.json']+[Path('/home/legolas/king-spec/spec')/n for n in ['evaluation-relations.md','ordinary-iterations.md','quiescence-tree.md']]
pins={str(p):sha(p) for p in inputs}
identity=json.loads((E/'ordinary-projected-bits-pgo-codegen-review-20261018-01/identity.json').read_text())
assert identity['images']['candidate']['image_sha256']=='51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a'
for n in ['influence.rs','ordinary.rs','quiescence.rs','evaluator.rs','timed.rs','position.rs']:
 frozen=E/'ordinary-projected-bits-pgo-use-build-20261018-01/source-before/src'/n
 assert identity['source_input_sha256'][str(frozen)]==sha(S/n)
 root=Path('/home/legolas/rook2/src')/n;assert sha(root)==sha(S/n);pins[str(root)]=sha(root)
cases={};build='rook2::influence::Influence::build'
for case in ['35','08']:
 rows,arcs,total=ns['raw'](O/f'profile-{case}.callgrind')
 inc=[r for r in arcs if r['callee_function']==build];out=[r for r in arcs if r['function']==build];own=[r for r in rows if r['function']==build]
 assert not out
 assert sum(r['Ir'] for r in inc)==sum(r['Ir'] for r in own)
 ensures=[r for r in arcs if 'ensure_influence' in r['callee_function']]
 assert not ensures
 groups={};used=set()
 for n,pred in [('ordinary',lambda r:'::visit_ordinary_impl' in r['function']),('Q',lambda r:'::visit_q_impl' in r['function']),('root_run',lambda r:r['function']=='rook2::run')]:
  a=[r for r in inc if pred(r)];ids={r['raw_line'] for r in a};assert not ids&used;used|=ids
  cost=sum(r['Ir'] for r in a)
  groups[n]={'recorded_calls':sum(r['explicit_calls'] for r in a),'recorded_inclusive_Ir':cost,'percent_total_simulated_Ir':100*cost/total,'raw_edges':a}
 assert len(used)==len(inc)
 cases[case]={'total_simulated_Ir':total,'build_all_inline_source_exclusive_Ir':sum(r['Ir'] for r in own),'recorded_build_calls':sum(r['explicit_calls'] for r in inc),'no_recorded_build_outgoing_arcs':True,'incoming_Ir_equals_exclusive_self':True,'groups':groups,'separately_recorded_ensure_edges':ensures,'ensure_interpretation':'Inlined in reached callers; absence of explicit call edges does not mean zero ensure calls/hits.','ordinary_MoveKind_eligibility_fraction':None,'ordinary_delta_replacement_cost':None}
assert all(sha(Path(p))==h for p,h in pins.items())
put('input-pins.json',pins);put('census.json',{'complete':True,'cases':cases,'all_inputs_unchanged':True,'new_native_binutils_build_profile_runs':0,'no_callee_weighted_average_attribution':True})
print(json.dumps({c:{'total':v['total_simulated_Ir'],'build_calls':v['recorded_build_calls'],'build_Ir':v['build_all_inline_source_exclusive_Ir'],'groups':{n:{k:x for k,x in g.items() if k!='raw_edges'} for n,g in v['groups'].items()}} for c,v in cases.items()},indent=2))
