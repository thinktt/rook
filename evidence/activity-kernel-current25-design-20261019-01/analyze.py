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

summary={};pins={}
for case in ['35','08']:
 p=O/f'profile-{case}.callgrind';pins[str(p)]=sha(p)
 rows,arcs,total=raw(p)
 owner=[r for r in rows if r['function']=='rook2::activity::compute']
 groups={
  'destination_value_gate':lambda r:53<=r['line']<=67,
  'direct_category_capture_priority':lambda r:201<=r['line']<=238,
  'direct_mark_creation':lambda r:240<=r['line']<=243,
  'slider_transparency':lambda r:245<=r['line']<=267,
  'knight_destination_walk':lambda r:279<=r['line']<=292,
  'slider_destination_walk':lambda r:299<=r['line']<=341,
  'piece_score_and_source_penalty':lambda r:347<=r['line']<=386,
  'pressure_consumer':lambda r:429<=r['line']<=484,
 }
 native=[r for r in owner if r['file'].endswith('/src/activity.rs')];used=set();buckets={}
 for name,pred in groups.items():
  subset=[r for r in native if pred(r)];ids={r['raw_line'] for r in subset};assert not used&ids;used|=ids
  buckets[name]={'Ir':sum(r['Ir'] for r in subset),'whole_percent':100*sum(r['Ir'] for r in subset)/total,'rows':subset}
 for name,subset in [('other_activity_source_positive',[r for r in native if r['raw_line'] not in used and r['line']>0]),('activity_source_line0',[r for r in native if r['line']==0]),('other_source_partitions',[r for r in owner if r not in native])]:
  buckets[name]={'Ir':sum(r['Ir'] for r in subset),'whole_percent':100*sum(r['Ir'] for r in subset)/total,'rows':subset}
 assert sum(b['Ir'] for b in buckets.values())==sum(r['Ir'] for r in owner)
 # Reconcile every native positive line to absolute annotation's exclusive source section.
 annotation=A/f'profile-{case}-activity.stdout';pins[str(annotation)]=sha(annotation)
 lines=annotation.read_text().split('-- User-annotated source:',1)[1].splitlines();printed={};line_no=None
 for text in lines:
  if m:=re.match(r'^-- line (\d+) ',text):line_no=int(m[1])
  elif (m:=re.match(r'^\s*([\d,]+) \(\s*[\d.]+%\)',text)) and '<counts for unidentified lines' not in text and 'events annotated' not in text:
   assert line_no is not None;printed[line_no]=int(m[1].replace(',',''))
 byline=Counter()
 for r in native:byline[r['line']]+=r['Ir']
 assert all(byline[k]==v for k,v in printed.items())
 incoming=[r for r in arcs if r['callee_function']=='rook2::activity::compute']
 result={'whole_Ir':total,'owner_all_file_self_Ir':sum(r['Ir'] for r in owner),'owner_whole_percent':100*sum(r['Ir'] for r in owner)/total,'exclusive_native_activity_file_Ir':sum(r['Ir'] for r in native),'buckets':buckets,'incoming_explicit_call_arcs':incoming,'explicit_incoming_call_sum':sum(r['explicit_calls'] for r in incoming),'annotation_reconciled':True,'raw_summary_totals_reconciled':True}
 (P/f'profile-{case}-partition.json').write_text(json.dumps(result,indent=2)+'\n')
 summary[case]={k:({n:{'Ir':v['Ir'],'whole_percent':v['whole_percent']} for n,v in x.items()} if k=='buckets' else x) for k,x in result.items() if k!='incoming_explicit_call_arcs'}
for name in ['src/activity.rs','src/influence.rs','src/attacks.rs','src/position.rs','src/types.rs']:
 p=S/name;pins[str(p)]=sha(p);assert p.read_bytes()==(Path('/home/legolas/rook2')/name).read_bytes()
for path in [O/'provenance.json',O/'independent-verification.json',A/'receipt.json',Path('/home/legolas/king-spec/spec/activity.md'),Path('/home/legolas/king-spec/spec/evaluation-relations.md')]:pins[str(path)]=sha(path)
assert all(sha(Path(p))==h for p,h in pins.items())
(P/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
(P/'numeric-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
