"""Extract exclusive numeric source rows from already closed absolute annotations."""
import json,re
from pathlib import Path
base=Path('/home/legolas/rook2/evidence/complete117-callgrind-absolute-annotation-20261018-02')
out=Path(__file__).parent
result={}
for case in ('35','08'):
 result[case]={}
 for name in ('activity','influence'):
  path=base/f'profile-{case}-{name}-lines.stdout'
  active=False;current=None;rows=[];unidentified=None;annotated=None
  for number,line in enumerate(path.read_text().splitlines(),1):
   if '-- User-annotated source:' in line: active=True
   if not active: continue
   m=re.match(r'-- line (\d+) ',line)
   if m:current=int(m[1]);continue
   m=re.match(r'^\s*([\d,]+)\s+\([^)]*\)\s+(.*)$',line)
   if not m:continue
   value=int(m[1].replace(',','')); text=m[2]
   if text.startswith('<counts for unidentified lines'):unidentified=value;continue
   if text=='events annotated':annotated=value;continue
   if '=>' in text or current is None:continue
   rows.append({'source_line':current,'Ir':value,'display_line':number,'source_text':text})
  result[case][name]={'annotation':str(path),'rows':rows,'unidentified_Ir':unidentified,'events_annotated_Ir':annotated}
  print(case,name,'annotated',annotated,'unidentified',unidentified)
  if name=='activity':
   for label,low,high in [('orchestration',55,132),('rank',137,137),('capture/direct category',156,190),('mark',194,196),('transparency',198,220),('destinations',223,307),('piece score',310,350),('pressure',388,440),('weighting',444,450)]:
    chosen=[r for r in rows if low<=r['source_line']<=high]
    print(label,sum(r['Ir'] for r in chosen))
   for r in sorted(rows,key=lambda r:r['Ir'],reverse=True)[:12]:print(r['source_line'],r['Ir'],r['source_text'])
(out/'exclusive-source-lines.json').write_text(json.dumps(result,indent=2)+'\n')
