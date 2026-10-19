"""Bounded closed43 pawn arithmetic SELF-row extraction, no native/tool execution."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,os
E=Path(__file__).resolve().parent
P=Path('/home/legolas/rook2/evidence/influence-bitsliced-sum-hot-cost-analysis-preparation-20261019-01')
PLAN=json.loads((P/'plan.json').read_text())
O=Path(PLAN['input_root']);W=Path(PLAN['source_snapshot'])
FN='rook2::pawn_progress::selected';TARGET=[78,80,82,141,144]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):
 with (E/name).open('x') as f:json.dump(x,f,indent=2);f.write('\n')

def raw(path):
 lines=path.read_text().splitlines();assert 'positions: line' in lines and 'events: Ir' in lines;names={'file':{},'fn':{},'ob':{}}
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
 current_file=None;current_fn=None;callee_fn=None;current_object=None;callee_object=None;fn_token=None;position=0;pending=None;rows=[];arcs=[]
 for number,line in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe|cfi|fn|cfn|ob|cob)=(.*)$',line)
  if m:
   key,s=m.groups()
   if key in ['fl','fi','fe']:current_file=value('file',s)
   elif key=='fn':current_fn=value('fn',s);fn_token=s
   elif key=='cfn':callee_fn=value('fn',s)
   elif key=='ob':current_object=value('ob',s)
   elif key=='cob':callee_object=value('ob',s)
   continue
  if line.startswith('calls='):
   assert pending is None
   pending=int(line.split('=',1)[1].split()[0]);assert pending>0
   continue
  m=re.fullmatch(r'([+\-]?\d+|\*|0x[0-9a-fA-F]+)\s+(\d+)\s*',line)
  if not m:continue
  token=m[1];position=position if token=='*' else position+int(token) if token[0] in '+-' else int(token,0) if token.startswith('0x') else int(token)
  assert current_file is not None and current_fn is not None
  row=dict(raw_line=number,raw_cost_text=line,object=current_object,file=current_file,function=current_fn,fn_name_token=fn_token,line=position,Ir=int(m[2]))
  if pending is None:rows.append(row)
  else:row.update(callee_function=callee_fn,callee_object=callee_object,explicit_calls=pending,inclusive_arc=True);arcs.append(row)
  pending=None
 assert pending is None
 total=int(next(s.split(':',1)[1] for s in lines if s.startswith('summary:')))
 assert sum(r['Ir'] for r in rows)==total==int(next(s.split(':',1)[1] for s in lines if s.startswith('totals:')))
 return rows,arcs,total


def main():
 assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
 prov=json.loads((O/'provenance.json').read_text());verify=json.loads((O/'independent-verification.json').read_text())
 assert prov['complete'] and prov['failure'] is None and prov['engine_sha256']==PLAN['expected_image_sha256']
 assert verify['complete'] and verify['all_original_inputs_unchanged'] and verify['original_checkReplay_exit_code']==0 and verify['original_checkReplay_cases']==2
 source=W/'src/pawn_progress.rs';source_sha=PLAN['source_sha256']['src/pawn_progress.rs'];assert sha(source)==source_sha
 text=source.read_text().splitlines();root=prov['compiled_source_root'];nativefile=root+'/src/pawn_progress.rs';typesfile=root+'/src/types.rs'
 pins={str(p):sha(p) for p in [P/'analyze.py',P/'plan.json',O/'provenance.json',O/'independent-verification.json',O/'tool-terminal.json',O/'verify-tool-terminal.json',source]}
 results={}
 for c in ['35','08']:
  path=O/f'profile-{c}.callgrind';digest=sha(path)
  assert digest==PLAN['input_sha256'][str(path)]==prov['cases']['profile-'+c]['profile_sha256'];pins[str(path)]=digest
  rankpath=P/f'profile-{c}-function-ranking.json';pins[str(rankpath)]=sha(rankpath);ranking=json.loads(rankpath.read_text())
  rows,arcs,total=raw(path);assert total==PLAN['expected_total_Ir'][c]
  selected=[r for r in rows if r['function']==FN and r['object']==str(O.parent.parent/'rook2/evidence/influence-bitsliced-sum-pgo-use-build-20261019-01/rook2-exact')]
  # Pin the object explicitly; do not merge different images or demangled suffixes.
  expected_object='/home/legolas/rook2/evidence/influence-bitsliced-sum-pgo-use-build-20261019-01/rook2-exact'
  assert selected==[r for r in rows if r['function']==FN and r['object']==expected_object]
  assert selected
  old=next(x for x in ranking['ranking'] if x['function']==FN and x['object']==expected_object)
  parts=Counter()
  for r in selected:parts[r['file']]+=r['Ir']
  selftotal=sum(r['Ir'] for r in selected);assert selftotal==old['SELF_Ir'] and dict(parts)==old['file_partitions']
  groups={f'line{n}':[] for n in TARGET};groups.update(excluded_top_two174=[],other_pawn_positive=[],unknown_types_positive=[],unknown_line0_all_files=[],unknown_other_inline_positive=[])
  for r in selected:
   if r['line']==0:k='unknown_line0_all_files'
   elif r['file']==nativefile and r['line'] in TARGET:k='line'+str(r['line'])
   elif r['file']==nativefile and r['line']==174:k='excluded_top_two174'
   elif r['file']==nativefile:k='other_pawn_positive'
   elif r['file']==typesfile:k='unknown_types_positive'
   else:k='unknown_other_inline_positive'
   groups[k].append(r)
  ids=[r['raw_line'] for subset in groups.values() for r in subset];assert len(ids)==len(set(ids))==len(selected)
  grouped={k:dict(Ir=sum(r['Ir'] for r in rs),whole_percent=100*sum(r['Ir'] for r in rs)/total,selected_SELF_percent=100*sum(r['Ir'] for r in rs)/selftotal,raw_rows=rs) for k,rs in groups.items()}
  assert sum(g['Ir'] for g in grouped.values())==selftotal
  target=sum(grouped['line'+str(n)]['Ir'] for n in TARGET)
  rowdetail=[]
  for n in TARGET:
   rowdetail.append(dict(source_line=n,source_text=text[n-1],Ir=grouped['line'+str(n)]['Ir'],whole_percent=grouped['line'+str(n)]['whole_percent'],selected_SELF_percent=grouped['line'+str(n)]['selected_SELF_percent'],rows=grouped['line'+str(n)]['raw_rows']))
  result=dict(whole_Ir=total,selected_SELF_Ir=selftotal,selected_whole_percent=100*selftotal/total,file_partitions=dict(parts),target_context_Ir=target,target_whole_percent=100*target/total,target_selected_SELF_percent=100*target/selftotal,target_lines=rowdetail,disjoint_partition=grouped,all_selected_rows_partitioned_once=True,whole_SELF_exactly_reconciled=True,selected_matches_closed_ranking=True,all_inclusive_arcs_excluded=True,selected_function_tokens=sorted(set(r['fn_name_token'] for r in selected)),other_selected_name_variants=sorted(set(r['function'] for r in rows if 'pawn_progress::selected' in r['function'] and r['function']!=FN)),adjacent_pawn_source_rows_NOT_ADDED=[r for r in selected if r['file']==nativefile and r['line'] in [77,79,81,140,142,143,145]],outgoing_arcs_NOT_ADDED=[r for r in arcs if r['function']==FN])
  save('profile-'+c+'-rows.json',result);results[c]={k:v for k,v in result.items() if k in ['whole_Ir','selected_SELF_Ir','selected_whole_percent','target_context_Ir','target_whole_percent','target_selected_SELF_percent','all_selected_rows_partitioned_once','whole_SELF_exactly_reconciled']}
  print(json.dumps(dict(case=c,summary=results[c],line_context={n:grouped['line'+str(n)]['Ir'] for n in TARGET},unknown_line0=grouped['unknown_line0_all_files']['Ir'],types_unknown=grouped['unknown_types_positive']['Ir'])))
 assert all(sha(p)==h for p,h in pins.items())
 save('input-pins.json',dict(inputs=pins,all_inputs_unchanged=True,source_native72_graph=PLAN['source_native72_graph'],image_sha256=PLAN['expected_image_sha256'],native_execution_or_new_annotation=False))
 save('summary.json',dict(complete=True,cases=results,scope='Exclusive SELF source-row context only: mixed source instructions, not signed-correction cost/removable envelope/CPU/PMU.',target_lines=TARGET,top_two174_excluded=True,all_inputs_unchanged=True,no_native_or_annotation_execution=True))
if __name__=='__main__':main()
