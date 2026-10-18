from pathlib import Path
import re,json
p=Path('/home/legolas/rook2/evidence/complete117-callgrind-20261018')
out=Path(__file__).resolve().parent
annotations=json.loads((out/'exclusive-source-rows.json').read_text())
results={}
for case in ['35','08']:
 lines=(p/f'profile-{case}.callgrind').read_text().splitlines();files={};functions={}
 for text in lines:
  m=re.match(r'^(?:fl|fi|fe|cfi|cfl)=\((\d+)\) (.+)$',text)
  if m:files[m.group(1)]=m.group(2)
  m=re.match(r'^(?:fn|cfn)=\((\d+)\) (.+)$',text)
  if m:functions[m.group(1)]=m.group(2)
 base=None;file=None;fn=None;position=0;call=False;total=0;rows={};context={};unknown=0
 for text in lines:
  m=re.match(r'^(fl|fi|fe)=\((\d+)\)',text)
  if m:
   file=files[m.group(2)]
   if m.group(1)=='fl':base=file
   continue
  m=re.match(r'^fn=\((\d+)\)',text)
  if m:fn=functions[m.group(1)];file=base;continue
  if text.startswith('calls='):call=True;continue
  m=re.match(r'^([*]|[+-]?\d+) (\d+)$',text)
  if not m:continue
  token=m.group(1)
  if token!='*':position=position+int(token) if token[0] in '+-' else int(token)
  cost=int(m.group(2))
  if call:call=False;continue
  total+=cost
  if not file or not file.endswith('/src/movegen.rs'):continue
  if position==0:unknown+=cost
  else:rows[position]=rows.get(position,0)+cost
  byline=context.setdefault(fn,{})
  byline[position]=byline.get(position,0)+cost
 assert total==annotations[case]['total_Ir'],(case,'whole exclusive total',total)
 assert unknown==annotations[case]['unidentified'],(case,'unidentified',unknown)
 assert rows=={int(k):v['Ir'] for k,v in annotations[case]['exclusive_source_rows'].items()},(case,'line counter mismatch')
 selected={}
 for fn,byline in context.items():
  pieces={line:cost for line,cost in byline.items() if 565<=line<=605}
  if pieces:
   selected[fn]={'pieces_source_rows':pieces,'pieces_rows_total':sum(pieces.values()),'occupancy_rows_583_585':sum(cost for line,cost in pieces.items() if 583<=line<=585),'post_target_stop_598':pieces.get(598,0),'source_direction_579_582':sum(cost for line,cost in pieces.items() if 579<=line<=582)}
 results[case]={'all_exclusive_Ir_matches_summary':True,'source_line_rows_match_canonical_annotation':True,'unidentified_matches_annotation':True,'contexts':selected}
 print(case,json.dumps(selected,indent=2))
with (out/'exclusive-function-contexts.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
