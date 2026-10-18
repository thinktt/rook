"""Read only two existing exclusive threshold99 annotation tables; no native calls."""
import json,re
from pathlib import Path
base=Path('/home/legolas/rook2/evidence/complete117-callgrind-20261018')
out=Path(__file__).parent
owners=['rook2::activity::compute','rook2::influence::Influence::build','rook2::shelter::compute','rook2::pawn_progress::selected','rook2::pawn_terms::structure_terms','rook2::pawn_terms::raw_piece_terms','rook2::pawn_structure::fresh_with_order']
result={'scope':'Exclusive disjoint displayed file:function rows, threshold99; lower-bound attribution, not calls or CPU savings. Source-line subsets must not be added.','cases':{}}
for case,total in [('35',48746346838),('08',4163216998)]:
 rows=[]
 for no,line in enumerate((base/f'profile-{case}-functions.stdout').read_text().splitlines(),1):
  m=re.match(r'^\s*([\d,]+)\s+\([^)]*\)\s+(.*)$',line)
  if m and ':' in m[2]:
   key=re.sub(r' \[.*\]$','',m[2]); file,fn=key.split(':',1)
   rows.append({'table_line':no,'Ir':int(m[1].replace(',','')),'file':file,'function':fn})
 assert len({(r['file'],r['function']) for r in rows})==len(rows)
 groups={}
 for owner in owners:
  chosen=[r for r in rows if r['function']==owner]
  value=sum(r['Ir'] for r in chosen)
  groups[owner]={'Ir':value,'percent_program_Ir':value*100/total,'rows':chosen,'zero_means_not_displayed':not chosen}
 result['cases'][case]={'total_Ir':total,'table':str(base/f'profile-{case}-functions.stdout'),'groups':groups}
(out/'displayed-owner-rows.json').write_text(json.dumps(result,indent=2)+'\n')
print('Closed tables reconciled: 7 disjoint owner groups per case; source-row membership preserved.')
