#!/usr/bin/env python3
# Cold existing-text analysis only; accepted raw() is copied verbatim.
from pathlib import Path
import re, json
def raw(path):
 lines=path.read_text().splitlines();assert 'positions: line' in lines and 'events: Ir' in lines;names={'file':{},'fn':{},'ob':{}}
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
 current_file=None;current_fn=None;callee_fn=None;current_object=None;callee_object=None;fn_token=None;position=0;pending=None;rows=[];arcs=[]
 for number,line in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe|cfi|fn|cfn|ob|cob)=(.*)$',line)
  if m:
   key,s=m.groups()
   if key in ['fl','fi','fe']:current_file=value('file',s)
   elif key=='fn':current_fn=value('fn',s);fn_token=s
   elif key=='cfn':callee_fn=value('fn',s)
   elif key=='ob':current_object=value('ob',s)
   elif key=='cob':callee_object=value('ob',s)
   continue
  if line.startswith('calls='):
   assert pending is None
   pending=int(line.split('=',1)[1].split()[0]);assert pending>0
   continue
  m=re.fullmatch(r'([+\-]?\d+|\*|0x[0-9a-fA-F]+)\s+(\d+)\s*',line)
  if not m:continue
  token=m[1];position=position if token=='*' else position+int(token) if token[0] in '+-' else int(token,0) if token.startswith('0x') else int(token)
  assert current_file is not None and current_fn is not None
  row=dict(raw_line=number,raw_cost_text=line,object=current_object,file=current_file,function=current_fn,fn_name_token=fn_token,line=position,Ir=int(m[2]))
  if pending is None:rows.append(row)
  else:row.update(callee_function=callee_fn,callee_object=callee_object,explicit_calls=pending,inclusive_arc=True);arcs.append(row)
  pending=None
 assert pending is None
 total=int(next(s.split(':',1)[1] for s in lines if s.startswith('summary:')))
 assert sum(r['Ir'] for r in rows)==total==int(next(s.split(':',1)[1] for s in lines if s.startswith('totals:')))
 return rows,arcs,total


ROOT=Path('/home/legolas/rook2')
HERE=ROOT/'evidence/post50-whole-search-direction-review-20261019-01'
PRIVATE=Path('/home/legolas/rook2-private/influence-bitsliced-sum-hot-cost-20261019-01')
summary={}
for case in ['35','08']:
 rows,arcs,total=raw(PRIVATE/f'profile-{case}.callgrind')
 selected=[r for r in rows if r['function']=='rook2::activity::compute' and r['file'].endswith('/src/types.rs') and 111<=r['line']<=122]
 activity=[r for r in rows if r['function']=='rook2::activity::compute']
 ranking=json.loads((ROOT/f'evidence/influence-bitsliced-sum-hot-cost-analysis-preparation-20261019-01/profile-{case}-function-ranking.json').read_text())
 expected=next(r for r in ranking['ranking'] if r['function']=='rook2::activity::compute')
 assert sum(r['Ir'] for r in activity)==expected['SELF_Ir']
 # Source-file bands below may contain multiple owner instantiations; each physical SELF row is counted once.
 contexts={
  'activity_kind_decoder_context':selected,
  'tactical_generate_loop122_160':[r for r in rows if r['file'].endswith('/src/tactical.rs') and 122<=r['line']<=160],
  'tactical_direct_check163_201':[r for r in rows if r['file'].endswith('/src/tactical.rs') and 163<=r['line']<=201],
 }
 result={name:{'Ir':sum(r['Ir'] for r in group),'whole_percent':100*sum(r['Ir'] for r in group)/total,'rows':group} for name,group in contexts.items()}
 assert len({r['raw_line'] for group in contexts.values() for r in group})==sum(len(group) for group in contexts.values())
 (HERE/f'profile-{case}-selected-rows.json').write_text(json.dumps({'whole_Ir':total,'exclusive_SELF_only':True,'inclusive_arcs_not_added':True,'activity_owner_exact':True,'contexts':result},indent=2)+'\n')
 summary[case]={'whole_Ir':total,'contexts':{k:{'Ir':v['Ir'],'whole_percent':v['whole_percent'],'physical_rows':len(v['rows'])} for k,v in result.items()}}
(HERE/'summary.json').write_text(json.dumps({'complete':True,'same_current43_image_only':True,'cases':summary,'scope':'Simulated Ir source contexts, not call counts, isolated guard instructions, removable savings or CPU predictions'},indent=2)+'\n')
print(json.dumps(summary))
