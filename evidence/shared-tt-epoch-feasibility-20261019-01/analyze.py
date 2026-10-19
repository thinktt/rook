"""Existing raw Callgrind parsing only; no executable/compiler/profiler."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
P=Path(__file__).resolve().parent
O=P.parent/'candidate25-callgrind-20261018-01'
S=Path('/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src')
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

inputs=[O/f'profile-{c}.callgrind' for c in ['35','08']]+[O/'provenance.json',O/'independent-verification.json',S/'remembered.rs',Path('/home/legolas/rook2/src/remembered.rs')]
pins={str(p):sha(p) for p in inputs};assert pins[str(S/'remembered.rs')]==pins['/home/legolas/rook2/src/remembered.rs']
results={}
for c in ['35','08']:
 rows,arcs,total=raw(O/f'profile-{c}.callgrind')
 native=[r for r in rows if r['file']==str(S/'remembered.rs')]
 selected=[]
 for r in rows:
  if r['file']==str(S/'remembered.rs') or 'rook2::remembered::' in r['function']:selected.append(r)
 assert len({r['raw_line'] for r in selected})==len(selected)
 functions={}
 for r in selected:
  fn=functions.setdefault(r['function'],{'all_selected_self_Ir':0,'partitions':{}})
  fn['all_selected_self_Ir']+=r['Ir'];fn['partitions'][r['file']]=fn['partitions'].get(r['file'],0)+r['Ir']
 regions={'construct_layout':(1,92),'matches_epoch_plus_identity':(93,97),'bound_decode':(98,108),'consider_payload_mate_metadata':(109,137),'table_construction':(138,171),'clear':(172,179),'group_for_unchanged':(180,191),'store':(192,229),'probe_dispatch':(230,248),'capacity_prime':(249,288)}
 buckets={};used=set()
 for name,(lo,hi) in regions.items():
  sub=[r for r in native if lo<=r['line']<=hi];ids={r['raw_line'] for r in sub};assert not used&ids;used|=ids
  buckets[name]={'Ir':sum(r['Ir'] for r in sub),'rows':sub}
 rest=[r for r in native if r['raw_line'] not in used];buckets['unassigned_native_line0_or_other']={'Ir':sum(r['Ir'] for r in rest),'rows':rest}
 assert sum(v['Ir'] for v in buckets.values())==sum(r['Ir'] for r in native)
 incoming=[r for r in arcs if 'rook2::remembered::' in (r['callee_function'] or '')]
 results[c]={'total_simulated_Ir':total,'mapped_remembered_all_functions_Ir':sum(r['Ir'] for r in native),'selected_disjoint_self_Ir':sum(r['Ir'] for r in selected),'functions':functions,'source_buckets':buckets,'explicit_incoming_arcs':incoming}
 (P/f'profile-{c}-selection.json').write_text(json.dumps({'raw_self_rows':selected,**results[c]},indent=2)+'\n')
assert all(sha(Path(p))==h for p,h in pins.items())
(P/'profile-summary.json').write_text(json.dumps({'scope':'whole-lifetime simulated exclusive Ir, no hardware cache/cycle/CPU claim','cases':{k:{n:v for n,v in r.items() if n not in ['source_buckets','explicit_incoming_arcs']} for k,r in results.items()},'all_inputs_unchanged':True},indent=2)+'\n')
(P/'profile-input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
for c,r in results.items():
 print(c,'mapped',r['mapped_remembered_all_functions_Ir'],'union',r['selected_disjoint_self_Ir'],'pct',100*r['selected_disjoint_self_Ir']/r['total_simulated_Ir'])
 print({n:v['Ir'] for n,v in r['source_buckets'].items()})
 print(r['functions'])
 print('arcs',r['explicit_incoming_arcs'])
