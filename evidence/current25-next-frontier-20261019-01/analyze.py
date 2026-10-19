"""Finite offline current25 exclusive-row partition; no subprocess or native runs."""
from pathlib import Path
from collections import Counter
import re,json,hashlib
P=Path(__file__).resolve().parent
O=Path('/home/legolas/rook2/evidence/candidate25-callgrind-20261018-01')
S=Path('/home/legolas/rook2/evidence/ordinary-projected-bits-pgo-use-build-20261018-01/source-before')
A=Path('/home/legolas/rook2/evidence/candidate25-callgrind-absolute-annotation-20261018-01')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(path):
 lines=path.read_text().splitlines();names={'file':{},'fn':{},'ob':{}}
 def value(kind,s):
  m=re.fullmatch(r'\((\d+)\)(?: (.*))?',s)
  if not m:return s
  index=int(m[1]);dictionary=names[kind]
  if m[2] is not None:
   assert index not in dictionary or dictionary[index]==m[2]
   dictionary[index]=m[2]
  return dictionary[index]
 for line in lines:
  m=re.match(r'^(fl|fi|fe|cfi|fn|cfn|ob|cob)=(.*)$',line)
  if m:value('fn' if m[1] in ['fn','cfn'] else 'ob' if m[1] in ['ob','cob'] else 'file',m[2])
 current_file=None;current_fn=None;callee_fn=None;position=0;pending=None;rows=[];arcs=[]
 for number,line in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe|cfi|fn|cfn|ob|cob)=(.*)$',line)
  if m:
   key,s=m.groups()
   if key in ['fl','fi','fe']:current_file=value('file',s)
   elif key=='fn':current_fn=value('fn',s)
   elif key=='cfn':callee_fn=value('fn',s)
   continue
  if line.startswith('calls='):
   assert pending is None
   pending=int(line.split('=',1)[1].split()[0]);assert pending>0
   continue
  m=re.fullmatch(r'([+\-]?\d+|\*|0x[0-9a-fA-F]+)\s+(\d+)\s*',line)
  if not m:continue
  token=m[1];position=position if token=='*' else position+int(token) if token[0] in '+-' else int(token,0) if token.startswith('0x') else int(token)
  assert current_file is not None and current_fn is not None
  row=dict(raw_line=number,file=current_file,function=current_fn,line=position,Ir=int(m[2]))
  if pending is None:rows.append(row)
  else:row.update(callee_function=callee_fn,explicit_calls=pending,inclusive_arc=True);arcs.append(row)
  pending=None
 assert pending is None
 total=int(next(s.split(':',1)[1] for s in lines if s.startswith('summary:')))
 assert sum(r['Ir'] for r in rows)==total==int(next(s.split(':',1)[1] for s in lines if s.startswith('totals:')))
 return rows,arcs,total

# Reuse only the accepted raw parser definitions above; original analysis main is excluded.
ROOT=Path('/home/legolas/rook2')
f=ROOT/'evidence/activity-kernel-current25-design-20261019-01/analyze.py'
OUT=ROOT/'evidence/current25-next-frontier-20261019-01'
pins={}; result={}
def pin(p):
 pins[str(p)]=sha(p)
 return p
provenance=json.loads(pin(O/'provenance.json').read_text())
assert provenance['engine_sha256']=='51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a'
for p,h in json.loads((ROOT/'evidence/activity-kernel-current25-design-20261019-01/input-pins.json').read_text()).items():
 assert sha(Path(p))==h
 pins[p]=h
continuity={}
for p,h in provenance['input_sha256'].items():
 if p.startswith(str(S)+'/'):
  rel=str(Path(p).relative_to(S));assert sha(ROOT/rel)==h and sha(Path(p))==h
  continuity[rel]=h;pins[str(ROOT/rel)]=h
assert len(continuity)==69
for p in [ROOT/'docs/research/remaining-performance.md',ROOT/'evidence/next-ordering-cost-review-20261019-01/review.md',ROOT/'evidence/next-ordering-cost-review-20261019-01/attribution.json',Path('/home/legolas/king-spec/spec/tactical-capture-order.md'),Path('/home/legolas/king-spec/spec/quiescence-candidates.md'),Path('/home/legolas/king-spec/spec/search-candidate-order.md'),f]:pin(p)
for p in (ROOT/'docs/decisions').glob('*.md'):
 if 16<=int(p.name[:4])<=26:pin(p)
for case in ['35','08']:
 rawpath=pin(O/f'profile-{case}.callgrind');rows,arcs,total=raw(rawpath)
 bands={
  'priority_load_250':lambda r:r['line']==250,
  'priority_control_252':lambda r:r['line']==252,
  'paired_shift_253_254':lambda r:253<=r['line']<=254,
  'paired_final_store_257_258':lambda r:257<=r['line']<=258,
  'ordering_partition_322_330':lambda r:322<=r['line']<=330,
  'direct_check_geometry_170_197':lambda r:170<=r['line']<=197,
  'nonpawn_enumeration_122_155':lambda r:122<=r['line']<=155,
 }
 buckets={};used=set()
 for name,pred in bands.items():
  selected=[r for r in rows if r['file'].endswith('/src/tactical.rs') and pred(r)]
  ids={r['raw_line'] for r in selected};assert not used&ids;used|=ids
  cost=sum(r['Ir'] for r in selected)
  buckets[name]={'Ir':cost,'whole_percent':100*cost/total,'rows':selected}
 native=[r for r in rows if r['file'].endswith('/src/tactical.rs')]
 owners=Counter()
 for r in rows:owners[r['function']]+=r['Ir']
 calls=[a for a in arcs if a['callee_function']=='rook2::tactical::generate']
 result[case]={'whole_Ir':total,'raw_exclusive_sum_reconciles':True,'bands':buckets,'tactical_file_line0_unassigned':sum(r['Ir'] for r in native if r['line']==0),'tactical_generate_all_file_self_Ir':owners['rook2::tactical::generate'],'explicit_generate_incoming_arcs':calls,'explicit_generate_call_sum':sum(a['explicit_calls'] for a in calls),'not_summed_inclusive_arcs':True}
 for name,b in buckets.items():print(case,name,b['Ir'],round(b['whole_percent'],6))
 print(case,'generate calls',result[case]['explicit_generate_call_sum'])
(OUT/'exclusive-attribution.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'source-continuity.json').write_text(json.dumps({'current_root69_equals_exact_profiled_source69':True,'source_graph':'d4bb0f948c650f9675b050410a3a4d2811dcc58357ceb2fc1c4f99f21f2fff50','files':continuity},indent=2)+'\n')
assert all(sha(Path(p))==h for p,h in pins.items())
(OUT/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Complete exclusive attribution,69-member continuity and original input recheck; no engines or new annotations.')
