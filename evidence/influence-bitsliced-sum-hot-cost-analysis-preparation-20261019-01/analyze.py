"""Offline current43 raw SELF selection/ranking; never executes a native/tool."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,os
E=Path(__file__).resolve().parent
PLAN=json.loads((E/'plan.json').read_text())
O=Path(PLAN['input_root']);W=Path(PLAN['source_snapshot']);FN=PLAN['producer_function']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
 with (E/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def terminal(path):
 t=json.loads(path.read_text());assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['terminal_chunk_id']

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
 assert PLAN['launch'] is True and PLAN['parent_activation']
 assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
 for path,h in PLAN['input_sha256'].items():assert sha(path)==h,path
 for path in [O/'tool-terminal.json',O/'verify-tool-terminal.json']:terminal(path)
 provenance=json.loads((O/'provenance.json').read_text());verification=json.loads((O/'independent-verification.json').read_text())
 assert provenance['complete'] and provenance['failure'] is None and provenance['engine_sha256']==PLAN['expected_image_sha256']
 assert verification['complete'] and verification['all_original_inputs_unchanged'] and verification['original_checkReplay_exit_code']==0 and verification['original_checkReplay_cases']==2
 assert provenance['annotation_source_root']==str(W)
 for n,h in PLAN['source_sha256'].items():assert sha(W/n)==h,n
 results={}
 for case in ['35','08']:
  path=O/f'profile-{case}.callgrind';assert sha(path)==provenance['cases']['profile-'+case]['profile_sha256']
  rows,arcs,total=raw(path);assert total==PLAN['expected_total_Ir'][case]==provenance['cases']['profile-'+case]['total_simulated_Ir']
  selected=[r for r in rows if r['function']==FN];assert selected
  files=Counter();groups=defaultdict(list);rank=Counter();fn_files=defaultdict(Counter)
  for r in rows:
   key=(r['object'],r['function']);rank[key]+=r['Ir'];fn_files[key][r['file']]+=r['Ir']
  ranking=[dict(object=k[0],function=k[1],SELF_Ir=v,whole_percent=100*v/total,file_partitions=dict(fn_files[k])) for k,v in sorted(rank.items(),key=lambda kv:(-kv[1],str(kv[0])))]
  assert sum(r['SELF_Ir'] for r in ranking)==total
  for r in selected:files[r['file']]+=r['Ir'];groups[(r['file'],r['line'])].append(r)
  printed=[]
  for number,line in enumerate((O/f'profile-{case}-functions.stdout').read_text().splitlines(),1):
   m=re.match(r'^\s*([\d,]+) \([^)]*\)\s+(.+)$',line)
   if m and ':'+FN in m[2]:
    label=m[2].split(':'+FN)[0];cost=int(m[1].replace(',',''));assert files[label]==cost
    printed.append(dict(display_line=number,file=label,Ir=cost))
  assert sum(x['Ir'] for x in printed)==sum(r['Ir'] for r in selected)
  joined=[]
  for (file,line),subset in sorted(groups.items()):
   source=None;relative=None
   if file.startswith(provenance['compiled_source_root']+'/src/') and line>0:
    relative=str(Path(file).relative_to(provenance['compiled_source_root']));assert relative in PLAN['source_sha256']
    text=(W/relative).read_text().splitlines();assert line<=len(text);source=text[line-1]
   joined.append(dict(file=file,relative_source=relative,line=line,Ir=sum(r['Ir'] for r in subset),source=source,raw_rows=[r['raw_line'] for r in subset]))
  result=dict(total_Ir=total,producer_exclusive_SELF=sum(r['Ir'] for r in selected),file_partitions=dict(files),line_groups=joined,raw_SELF_rows=selected,function_display_rows=printed,incoming_arcs_NOT_ADDED=[r for r in arcs if r['callee_function']==FN],outgoing_arcs_NOT_ADDED=[r for r in arcs if r['function']==FN])
  save('profile-'+case+'-self-selection.json',result)
  save('profile-'+case+'-function-ranking.json',dict(whole_Ir=total,ranking=ranking,all_SELF_exactly_reconciled=True,scope='Object+recorded function-name grouping across inlined file partitions. No physical entry/call/address count is inferred.'))
  results[case]={k:v for k,v in result.items() if k not in ['line_groups','raw_SELF_rows','incoming_arcs_NOT_ADDED','outgoing_arcs_NOT_ADDED']}
  print(json.dumps(dict(case=case,total_Ir=total,producer_SELF=result['producer_exclusive_SELF'],whole_percent=100*result['producer_exclusive_SELF']/total,top_functions=ranking[:10])))
 assert all(sha(p)==h for p,h in PLAN['input_sha256'].items())
 save('self-summary.json',dict(complete=True,exclusive_SELF_only=True,all_program_and_function_file_totals_reconciled=True,arcs_preserved_never_added=True,cases=results,all_inputs_unchanged=True,engine_profile_annotation_build_runs=0))
if __name__=='__main__':
 try:main()
 except BaseException as error:
  save('self-analysis-failure.json',dict(complete=False,error=repr(error)));raise
