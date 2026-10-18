from pathlib import Path
import re,json
p=Path('/home/legolas/rook2/evidence/complete117-callgrind-absolute-annotation-20261018-02')
out=Path(__file__).resolve().parent
result={}
for case,total in [('35',48746346838),('08',4163216998)]:
 lines=(p/f'profile-{case}-movegen-lines.stdout').read_text().splitlines();start=next(i for i,l in enumerate(lines) if '-- User-annotated source:' in l)
 rows={};unidentified=0;annotated=0;current=None;inclusive=0
 for text in lines[start+1:]:
  match=re.match(r'-- line (\d+) ',text)
  if match:current=int(match.group(1));continue
  match=re.match(r'^\s*([\d,]+)\s+\([^)]*\)\s+(.*)$',text)
  if not match:continue
  value=int(match.group(1).replace(',',''));body=match.group(2)
  if body.startswith('=>'):inclusive+=1;continue
  if body.startswith('<counts for unidentified'):unidentified+=value;continue
  if body=='events annotated':annotated=value;continue
  assert current is not None,text
  assert current not in rows,(case,current)
  rows[current]={'Ir':value,'text':body}
 assert sum(row['Ir'] for row in rows.values())==annotated,(case,annotated,sum(row['Ir'] for row in rows.values()))
 sections={'pieces_all_565_605':(565,605),'occupancy_decisions_583_585':(583,585),'loop_source_direction_579_582':(579,582),'post_target_stop_598':(598,598),'safety_setup_281_340':(281,340),'safety_acceptance_344_370':(344,370),'legal_after_bits_203_217':(203,217),'list_store_and_cap_37_43':(37,43),'pawn_production_486_563':(486,563),'gen_wrapper_671_729':(671,729),'mailbox_checker_81_133':(81,133)}
 categories={name:{'Ir':sum(row['Ir'] for line,row in rows.items() if a<=line<=b),'whole_profile_percent':100*sum(row['Ir'] for line,row in rows.items() if a<=line<=b)/total} for name,(a,b) in sections.items()}
 result[case]={'total_Ir':total,'exclusive_source_rows':rows,'unidentified':unidentified,'annotated':annotated,'excluded_inclusive_call_rows':inclusive,'categories':categories}
 print('CASE',case,'annotated',annotated,'unidentified additional',unidentified)
 for name,value in categories.items():print(name,value)
 print('pieces rows', {line:row for line,row in rows.items() if 565<=line<=605})
with (out/'exclusive-source-rows.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
