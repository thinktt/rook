from pathlib import Path
import json,re,hashlib
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

paths=[O/f'profile-{c}.callgrind' for c in ['35','08']]+[O/'provenance.json',O/'independent-verification.json',S/'activity.rs',S/'attacks.rs',S/'position.rs']
pins={str(x):sha(x) for x in paths};out={}
for c in ['35','08']:
 rows,arcs,total=raw(O/f'profile-{c}.callgrind');owner=[r for r in rows if r['function']=='rook2::activity::compute'];native=[r for r in owner if r['file']==str(S/'activity.rs')]
 bands={'knight_enumeration_context_280_287':(280,287),'slider_direction_and_enumeration_context_295_310':(295,310),'slider_blocker_transition_context_336_341':(336,341),'transparency_helper_245_267':(245,267),'retained_direct_class_and_capture_201_238':(201,238),'retained_mark_owner_240_243':(240,243),'retained_knight_class_sum_value_mark_calls_288_292':(288,292),'retained_slider_class_sum_value_charge_mark_311_334':(311,334),'retained_piece_score_347_386':(347,386),'retained_king_pressure_429_484':(429,484)}
 groups={};used=set()
 for name,(lo,hi) in bands.items():
  selected=[r for r in native if lo<=r['line']<=hi];ids={r['raw_line'] for r in selected};assert not used&ids;used|=ids
  groups[name]={'Ir':sum(r['Ir'] for r in selected),'whole_percent':100*sum(r['Ir'] for r in selected)/total,'raw_rows':selected}
 remaining=[r for r in owner if r['raw_line'] not in used];assert sum(g['Ir'] for g in groups.values())+sum(r['Ir'] for r in remaining)==sum(r['Ir'] for r in owner)
 old=json.loads((P.parent/f'activity-kernel-current25-design-20261019-01/profile-{c}-partition.json').read_text())
 assert old['owner_all_file_self_Ir']==sum(r['Ir'] for r in owner)
 out[c]={'whole_Ir':total,'activity_all_file_self_Ir':sum(r['Ir'] for r in owner),'bands':groups,'remaining_all_file_self_Ir':sum(r['Ir'] for r in remaining),'all_selected_disjoint':True,'legacy_owner_reconciled':True}
 (P/f'profile-{c}-geometry-rows.json').write_text(json.dumps(out[c],indent=2)+'\n')
 print(c,{n:(v['Ir'],v['whole_percent']) for n,v in groups.items()})
assert all(sha(Path(k))==v for k,v in pins.items())
(P/'profile-input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
(P/'profile-summary.json').write_text(json.dumps({c:{**r,'bands':{n:{k:v for k,v in g.items() if k!='raw_rows'} for n,g in r['bands'].items()}} for c,r in out.items()},indent=2)+'\n')
