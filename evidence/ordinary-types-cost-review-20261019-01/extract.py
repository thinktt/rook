"""Pure-data compressed Callgrind types-row extraction; no native/helper imports."""
from pathlib import Path
import json,re
P=Path(__file__).resolve().parent
RAW=Path('/home/legolas/rook2-private/pressure-value-static-callgrind-20261019-01')
ATTR=json.loads(Path('/home/legolas/rook2/evidence/pressure-value-static-hot-cost-results-20261019-01/function-attribution.json').read_text())
FN="rook2::ordinary::<impl rook2::engine::Search<_,H>>::visit_ordinary_impl'2"
EXPECTED={'35':1303471751,'08':109171669}
results={}
for case in ['35','08']:
 lines=(RAW/f'profile-{case}.callgrind').read_text().splitlines()
 assert 'positions: line' in lines and 'events: Ir' in lines
 files={};functions={}
 for text in lines:
  m=re.match(r'^(?:fl|fi|fe|cfi|cfl)=\((\d+)\) (.+)$',text)
  if m:files[m[1]]=m[2]
  m=re.match(r'^(?:fn|cfn)=\((\d+)\) (.+)$',text)
  if m:functions[m[1]]=m[2]
 base=None;file=None;fn=None;fnid=None;position=0;call=False;total=0;physical=[];arcs=[];byline={}
 for number,text in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe)=\((\d+)\)',text)
  if m:
   file=files[m[2]]
   if m[1]=='fl':base=file
   continue
  m=re.match(r'^fn=\((\d+)\)',text)
  if m:fnid=m[1];fn=functions[fnid];file=base;continue
  if text.startswith('calls='):assert not call;call=True;continue
  m=re.match(r'^([*]|[+-]?\d+) (\d+)$',text)
  if not m:continue
  token=m[1]
  if token!='*':position=position+int(token) if token[0] in '+-' else int(token)
  cost=int(m[2]);selected=fn==FN and file and file.endswith('/src/types.rs')
  if call:
   if selected:arcs.append(dict(physical_line=number,source_line=position,Ir_inclusive=cost,function_id=fnid))
   call=False;continue
  total+=cost
  if selected:
   physical.append(dict(physical_line=number,source_line=position,Ir_self=cost,function_id=fnid,file=file,function=fn))
   byline[position]=byline.get(position,0)+cost
 assert not call
 assert total==ATTR['profile-'+case]['program_simulated_Ir']==int(next(x.split(':',1)[1] for x in lines if x.startswith('summary:')))==int(next(x.split(':',1)[1] for x in lines if x.startswith('totals:')))
 assert sum(byline.values())==EXPECTED[case]
 own=[r for r in ATTR['profile-'+case]['rows'] if r['function']==FN and r['file'].endswith('/src/types.rs')]
 assert len(own)==1 and own[0]['Ir']==sum(byline.values())
 ranges={'Color index/opponent':[(12,21)],'PieceKind index':[(35,47)],'Square file/rank':[(54,59)],'Square offset':[(68,76)],'Piece new':[(95,98)],'Piece empty':[(99,101)],'Piece color':[(102,110)],'Piece kind':[(111,122)],'Move new':[(173,186)],'Move from/to':[(187,192)],'Move kind':[(193,204)],'Move same_endpoints':[(205,207)],'unidentified line0':[(0,0)]}
 used=set();parts={}
 for name,intervals in ranges.items():
  chosen={n for n in byline if any(a<=n<=b for a,b in intervals)};assert not used&chosen;used|=chosen
  count=sum(byline[n] for n in chosen);parts[name]=dict(Ir=count,percent_program=100*count/total,percent_overlay=100*count/EXPECTED[case],rows={n:byline[n] for n in sorted(chosen)})
 rest={n:v for n,v in byline.items() if n not in used};parts['other types lines']=dict(Ir=sum(rest.values()),rows=rest)
 assert sum(p['Ir'] for p in parts.values())==EXPECTED[case]
 results[case]=dict(program_ir=total,exact_types_ordinary_overlay_ir=EXPECTED[case],target_function=FN,exclusive_whole_total_reconciled=True,known_overlay_reconciled=True,parts=parts,source_rows=byline,physical_self_rows=physical,physical_inclusive_rows_excluded=arcs,parser_basis='Accepted shelter-ring-profile-review extract.py compressed file/function/position decoder; same resets and call-row exclusion, instrumented here with physical-row retention and exact current overlay oracle.')
 print(case,json.dumps({k:v['Ir'] for k,v in parts.items()}),flush=True)
with (P/'source-row-partition.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
