"""Offline exclusive annotation partition; no raw reannotation/native execution."""
from pathlib import Path
import re,json,hashlib,os
P=Path(__file__).resolve().parent
O=Path('/home/legolas/rook2-private/pressure-value-static-callgrind-20261019-01')
W=Path('/home/legolas/rook2/evidence/pressure-value-static-pgo-use-build-20261019-01/source-before')
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
pins={}
def consume(p):
 pins[str(p)]=sha(p);return p.read_text()
provenance=json.loads(consume(O/'provenance.json'))
verification=json.loads(consume(O/'independent-verification.json'))
consume(O/'tool-terminal.json')
assert provenance['complete'] and verification['complete'] and verification['all_original_inputs_unchanged']
assert provenance['engine_sha256']=='c3166899f9380812b0fcb114d613021ba308699e46b0f7de48ffafaf4ff0e5a7'
paths={'activity':'src/activity.rs','coherent':'src/influence/coherent.rs','influence':'src/influence.rs'}
sources={key:consume(W/name).splitlines() for key,name in paths.items()}
for key,name in paths.items():
 compiled=Path(provenance['compiled_source_root'])/name
 assert sha(compiled)==pins[str(W/name)]==provenance['input_sha256'][str(compiled)]
 pins[str(compiled)]=sha(compiled)
costrow=re.compile(r'^\s*([\d,]+) \([^)]*\)\s+(.+)$')
activity_bands={'setup_source_values_castling':(1,199),'direct_class_capture':(200,239),'marks':(240,244),'transparency':(245,268),'knight_all':(269,294),'slider_enumeration_with_victim':(295,310),'slider_retained_class_score':(311,335),'slider_blocker_transition':(336,344),'piece_score':(345,427),'pressure':(428,498),'weighted':(499,10000)}
coherent_bands={'init_leapers_source_dispatch':(1,76),'first_through_helpers':(77,90),'slider_masks':(91,130),'SIMD_expand_body':(131,10000)}
results={}
for case,total in [('35',45372164975),('08',3916044228)]:
 f=O/f'profile-{case}-functions.stdout';function_rows=[]
 for physical,line in enumerate(consume(f).splitlines(),1):
  m=costrow.match(line)
  if m and m[2]!='PROGRAM TOTALS':function_rows.append({'Ir':int(m[1].replace(',','')),'description':m[2],'raw_row':physical})
 assert sum(r['Ir'] for r in function_rows)==total
 groups={}
 for fn in ['rook2::activity::compute','rook2::influence::Influence::build_coherent']:
  rows=[r for r in function_rows if re.search(':'+re.escape(fn)+r'(?: \[|$)',r['description'])]
  groups[fn]={'Ir':sum(r['Ir'] for r in rows),'rows':rows}
 displays={}
 for owner,name in paths.items():
  f=O/f'profile-{case}-{owner}-lines.stdout';current=None;rows=[];unknown=None;annotated=None
  for physical,line in enumerate(consume(f).splitlines(),1):
   mark=re.match(r'-- line (\d+) ',line)
   if mark:current=int(mark[1]);continue
   m=costrow.match(line)
   if not m:continue
   cost=int(m[1].replace(',',''));text=m[2]
   if '<counts for unidentified lines' in text:unknown={'Ir':cost,'raw_row':physical}
   elif text=='events annotated':annotated=cost
   elif current is not None:
    assert text.strip()==sources[owner][current-1].strip(),(case,owner,current,text)
    rows.append({'line':current,'Ir':cost,'raw_row':physical,'source':text})
  assert len(set(r['line'] for r in rows))==len(rows)
  assert sum(r['Ir'] for r in rows)==annotated and unknown is not None
  fullfile=[r for r in function_rows if r['description'].startswith(str(Path(provenance['compiled_source_root'])/name)+':')]
  assert sum(r['Ir'] for r in fullfile)==annotated+unknown['Ir']
  bands=activity_bands if owner=='activity' else coherent_bands if owner=='coherent' else {'all_known_mixed_consumers':(1,10000)}
  partition={label:sum(r['Ir'] for r in rows if lo<=r['line']<=hi) for label,(lo,hi) in bands.items()}
  assert sum(partition.values())==annotated
  displays[owner]={'mapped_Ir':annotated,'unidentified':unknown,'file_total_Ir':annotated+unknown['Ir'],'partition':partition,'rows':rows,'file_function_rows':fullfile}
 a=displays['activity'];b=a['partition'];victim=sum(r['Ir'] for r in a['rows'] if r['line']==308)
 context=b['slider_enumeration_with_victim']+b['transparency']+b['slider_blocker_transition']
 geometry={'inclusive_mapped_context_Ir':context,'victim_load_line308_Ir_excluded_from_avoidability':victim,'context_minus_victim_Ir':context-victim,'whole_percent_context':100*context/total,'whole_percent_context_minus_victim':100*(context-victim)/total,'all_are_attribution_contexts_not_saved_instruction_estimates':True}
 results[case]={'total_simulated_Ir':total,'exclusive_function_table_sum_reconciles':True,'function_rows':len(function_rows),'groups':groups,'displays':displays,'slider_geometry':geometry,'raw_profile_sha256_from_closed_provenance':provenance['cases']['profile-'+case]['profile_sha256']}
assert all(sha(Path(p))==h for p,h in pins.items())
(P/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
(P/'analysis.json').write_text(json.dumps({'complete':True,'cases':results,'inputs_unchanged':True,'source_lines_exactly_joined':True,'all_exclusive_tables_and_partitions_reconciled':True,'no_native_or_annotation_runs':True},indent=2)+'\n')
print(json.dumps({c:{'total':v['total_simulated_Ir'],'slider_geometry':v['slider_geometry'],'activity_group':v['groups']['rook2::activity::compute']['Ir'],'activity_partitions':v['displays']['activity']['partition'],'activity_unknown':v['displays']['activity']['unidentified']['Ir'],'coherent_group':v['groups']['rook2::influence::Influence::build_coherent']['Ir'],'coherent_partitions':v['displays']['coherent']['partition'],'coherent_unknown':v['displays']['coherent']['unidentified']['Ir']} for c,v in results.items()},indent=2))
