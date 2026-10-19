from pathlib import Path
from collections import Counter
import re,json
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
  if m:
   kind='fn' if m[1] in ['fn','cfn'] else ('ob' if m[1] in ['ob','cob'] else 'file')
   value(kind,m[2])
 current_file=None;current_fn=None;current_obj=None;position=0;pending=False;rows=[];arcs=[]
 for number,line in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe|cfi|fn|cfn|ob|cob)=(.*)$',line)
  if m:
   key,s=m.groups()
   if key in ['fl','fi','fe']:current_file=value('file',s)
   elif key=='fn':current_fn=value('fn',s)
   elif key=='ob':current_obj=value('ob',s)
   continue
  if line.startswith('calls='):
   assert not pending and int(line.split('=',1)[1].split()[0])>0;pending=True;continue
  m=re.fullmatch(r'([+\-]?\d+|\*|0x[0-9a-fA-F]+)\s+(\d+)\s*',line)
  if not m:continue
  token=m[1]
  position=position if token=='*' else (position+int(token) if token[0] in '+-' else int(token,0) if token.startswith('0x') else int(token))
  assert current_file is not None and current_fn is not None
  row={'raw_line':number,'file':current_file,'function':current_fn,'line':position,'Ir':int(m[2])}
  (arcs if pending else rows).append(row);pending=False
 assert not pending
 summary=int(next(s.split(':',1)[1] for s in lines if s.startswith('summary:')))
 totals=int(next(s.split(':',1)[1] for s in lines if s.startswith('totals:')))
 assert sum(r['Ir'] for r in rows)==summary==totals
 return rows,arcs,summary

R=Path('/home/legolas/rook2/evidence');E=Path(__file__).resolve().parent;result={}
for case in ['35','08']:
 rows,arcs,total=raw(R/'candidate25-callgrind-20261018-01'/('profile-'+case+'.callgrind'))
 selected=[r for r in rows if r['function']=='rook2::activity::compute' and r['file'].endswith('/src/activity.rs')]
 byline=Counter()
 for row in selected:byline[row['line']]+=row['Ir']
 groups={}
 for name,lo,hi in [('transparent',245,266),('additional_dispatch',311,311),('destination_loop',301,343),('pressure_traversal_only',441,479)]:
  subset=[r for r in selected if lo<=r['line']<=hi]
  groups[name]={'Ir':sum(r['Ir'] for r in subset),'percent':100*sum(r['Ir'] for r in subset)/total,'rows':subset}
 result[case]={'total_Ir':total,'all_raw_exclusive_sum_matches_total':sum(r['Ir'] for r in rows)==total,'activity_source_owner_Ir':sum(r['Ir'] for r in selected),'groups':groups,'activity_line_Ir':dict(sorted(byline.items()))}
(E/'activity-attribution.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({case:{'total':d['total_Ir'],'groups':{n:{k:v for k,v in g.items() if k!='rows'} for n,g in d['groups'].items()}} for case,d in result.items()},indent=2))
