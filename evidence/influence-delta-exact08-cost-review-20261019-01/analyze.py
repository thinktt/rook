import re,json,hashlib,collections
from pathlib import Path
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

E=Path(__file__).parent
P=Path('/home/legolas/rook2/evidence/influence-delta-exact-image-ir-preparation-20261019-01/run')
B=Path('/home/legolas/rook2/evidence/influence-delta-inplace-generic-build-20261019-01/source-before/src')
A=Path('/home/legolas/rook2/evidence/influence-delta-inplace-generic-backend-review-20261019-01')
UPDATE='rook2::influence::Influence::update_ordinary'
RAY='rook2::influence::Influence::ray_signed'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(E/n).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
inputs=[P/'parent-construction-arcs.json',P/'provenance.json',P/'independent-verification.json',P/'verification-tool-terminal.json',P/'tool-terminal.json',B/'influence.rs',B/'attacks.rs',B/'types.rs',B/'position.rs',A/'update.asm',A/'review.md',A/'identity.json']
partitions={};raws={};totals={}
for name in ['baseline25','inplace30']:
 pp=P/name/'partition.json';rp=P/name/'profile.callgrind';inputs += [pp,rp]
 partitions[name]=json.loads(pp.read_text())
 rows,arcs,total=raw(rp);raws[name]=rows;totals[name]=total
 assert total==partitions[name]['whole_lifetime_Ir']
 assert len({r['raw_line'] for r in rows})==len(rows)
 lookup={r['raw_line']:r for r in rows}
 for r in partitions[name]['raw_self_rows']:
  assert {k:r[k] for k in ['raw_line','file','function','line','Ir']}==lookup[r['raw_line']]
 assert len(lookup)==len(partitions[name]['raw_self_rows'])
 assert sum(partitions[name]['disjoint_exclusive_Ir'].values())==total
u=[r for r in partitions['inplace30']['raw_self_rows'] if r['function']==UPDATE]
rays=[r for r in partitions['inplace30']['raw_self_rows'] if r['function']==RAY]
arcrows=[r for r in partitions['inplace30']['all_call_arcs'] if r['function']==UPDATE or r['callee']==UPDATE]
rawlines=(P/'inplace30/profile.callgrind').read_text().splitlines()
for r in u+rays+arcrows:
 r['raw_text']=rawlines[r['raw_line']-1]
 assert int(r['raw_text'].split()[-1])==r['Ir']
for r in arcrows:
 assert rawlines[r['raw_line']-2].startswith('calls=')
 assert int(rawlines[r['raw_line']-2].split('=',1)[1].split()[0])==r['calls']
assert len(u)==295 and sum(r['Ir'] for r in u)==74462229
assert len(rays)==118 and sum(r['Ir'] for r in rays)==21447647
assert not {r['raw_line'] for r in u}&{r['raw_line'] for r in rays}
assert not {r['raw_line'] for r in u+rays}&{r['raw_line'] for r in arcrows}
def category(r):
 f=Path(r['file']).name;l=r['line']
 if l==0:return 'unassigned_line0_all_files'
 if r['file'].startswith('/usr/src/'):return 'unassigned_core_nonzero_lines'
 if f=='attacks.rs':assert l in [141,143,144,145];return 'geometric_origin_discovery_native'
 if f=='position.rs':assert l==172;return 'attack_view_attributed_setup'
 if f=='types.rs':
  if l in [105,113]:return 'shared_piece_color_kind_helpers'
  assert l in [188,191];return 'entry_endpoints_exit'
 assert f=='influence.rs'
 if l in [156,202]:return 'entry_endpoints_exit'
 if l in [167,170]:return 'changed_origin_iteration_native'
 if l in [207,208]:return 'changed_piece_load_empty_dispatch_native'
 if l in [215,216,217,221,222,223,227,228,229]:return 'changed_nonray_targets_and_loop_native'
 if l in [234,239,244]:return 'changed_slider_ray_call_setup_native'
 if l in [182,188,194,197]:return 'selected_origin_loop_tag_and_ray_call_setup_native'
 assert l==319,(f,l);return 'nonray_weight_write_attributed_body'
groups=collections.defaultdict(list)
for r in u:groups[category(r)].append(r)
summary={k:{'Ir':sum(x['Ir'] for x in rows),'row_count':len(rows),'raw_lines':[x['raw_line'] for x in rows]} for k,rows in groups.items()}
assert sum(x['Ir'] for x in summary.values())==74462229
for x in summary.values():x['percent_trial_whole_Ir']=100*x['Ir']/totals['inplace30'];x['percent_update_self_Ir']=100*x['Ir']/74462229
files=collections.defaultdict(lambda:dict(Ir=0,raw_lines=[]))
for r in u:files[r['file']]['Ir']+=r['Ir'];files[r['file']]['raw_lines'].append(r['raw_line'])
line_groups=collections.defaultdict(lambda:dict(Ir=0,raw_lines=[]))
for r in u:
 k=r['file']+':'+str(r['line']);line_groups[k]['Ir']+=r['Ir'];line_groups[k]['raw_lines'].append(r['raw_line'])
incoming=[r for r in arcrows if r['callee']==UPDATE]
outgoing=[r for r in arcrows if r['function']==UPDATE]
assert sum(x['calls'] for x in incoming)==214665
assert sum(x['Ir'] for x in incoming)==74462229+21447647==95909876
assert sum(x['calls'] for x in outgoing)==358988
assert sum(x['Ir'] for x in outgoing)==21447647
parent=json.loads((P/'parent-construction-arcs.json').read_text())
ordinary={}
for name,d in parent.items():ordinary[name]=sum(x['Ir'] for x in d['construction_incoming'] if 'ordinary::' in x['caller'])
assert ordinary=={'baseline25':94288813,'inplace30':99328933}
metrics={'event_scope':'exclusive whole-lifetime simulated Ir; not PMU, cycles, CPU or physical traffic',
 'whole_Ir':totals,'whole_delta':totals['inplace30']-totals['baseline25'],
 'ordinary_map_production_inclusive_Ir':ordinary,'ordinary_map_delta':ordinary['inplace30']-ordinary['baseline25'],
 'ordinary_self_Ir':{n:d['disjoint_exclusive_Ir']['ordinary'] for n,d in partitions.items()},
 'update_self':74462229,'signed_rays_exclusive':21447647,'update_inclusive_once':95909876,
 'update_calls':214665,'ray_calls':358988,'outlined_fill_calls':parent['inplace30']['observed_stage_calls']['fill'],
 'groups':summary,'file_partitions':files,'line_groups':line_groups,
 'fifty_basis_points_trial_Ir':totals['inplace30']*.005,
 'fifty_basis_points_baseline_Ir':totals['baseline25']*.005,
 'needed_Ir_reduction_from_trial_to_baseline_minus_half_percent':totals['inplace30']-totals['baseline25']*.995,
 'eight_direction_discoveries_source_fixed_per_update':8,'source_fixed_discoveries':214665*8,
 'ray_weight_write_attributed_line319_Ir':sum(x['Ir'] for x in rays if x['file'].endswith('/influence.rs') and x['line']==319),
 'unknown_core_and_line0_Ir':summary['unassigned_line0_all_files']['Ir']+summary['unassigned_core_nonzero_lines']['Ir']}
save('raw-selection-proof.json',{'update_exclusive_rows':u,'signed_ray_exclusive_rows':rays,'update_incoming_and_outgoing_arcs_not_added_to_self':arcrows,'source_rows_verified_against_raw_lines':True,'all_raw_self_rows_independently_reparsed_and_equal':True,'no_overlap_self_and_arc_sets':True,'exact_update_self_sum':74462229,'exact_ray_self_sum':21447647})
save('cost-summary.json',metrics)
save('input-pins.json',{str(p):{'sha256':sha(p),'size':p.stat().st_size} for p in inputs})
print(json.dumps({k:v for k,v in metrics.items() if k not in ['groups','line_groups','file_partitions']},indent=2))
for k,v in summary.items(): print(k,v['Ir'],round(v['percent_trial_whole_Ir'],6))
