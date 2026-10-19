"""Read existing43 profiles only; exact ordinary suffix2 SELF rows, no native tool."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,os
E=Path(__file__).resolve().parent
P=Path('/home/legolas/rook2/evidence/influence-bitsliced-sum-hot-cost-analysis-preparation-20261019-01')
plan=json.loads((P/'plan.json').read_text());O=Path(plan['input_root']);W=Path(plan['source_snapshot'])
FN="rook2::ordinary::<impl rook2::engine::Search<_,H>>::visit_ordinary_impl'2"
OBJ='/home/legolas/rook2/evidence/influence-bitsliced-sum-pgo-use-build-20261019-01/rook2-exact'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):
 with (E/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')

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
 prov=json.loads((O/'provenance.json').read_text());root=prov['compiled_source_root']
 assert prov['complete'] and prov['failure'] is None and prov['engine_sha256']==plan['expected_image_sha256']
 pins={str(p):sha(p) for p in [P/'analyze.py',P/'plan.json',O/'provenance.json',O/'independent-verification.json',O/'tool-terminal.json',O/'verify-tool-terminal.json']}
 result={}
 for c in ['35','08']:
  path=O/f'profile-{c}.callgrind';pins[str(path)]=sha(path);assert pins[str(path)]==plan['input_sha256'][str(path)]==prov['cases']['profile-'+c]['profile_sha256']
  rows,arcs,total=raw(path);assert total==plan['expected_total_Ir'][c]
  rankpath=P/f'profile-{c}-function-ranking.json';pins[str(rankpath)]=sha(rankpath);rank=json.loads(rankpath.read_text())['ranking']
  names=[x for x in rank if 'visit_ordinary_impl' in x['function']]
  rs=[r for r in rows if r['object']==OBJ and r['function']==FN];assert rs
  counts=Counter();groups=defaultdict(list)
  for r in rs:counts[r['file']]+=r['Ir'];groups[(r['file'],r['line'])].append(r)
  matched=next(x for x in names if x['function']==FN and x['object']==OBJ)
  assert dict(counts)==matched['file_partitions'] and sum(x['Ir'] for x in rs)==matched['SELF_Ir']
  joined=[]
  for (file,line),subset in sorted(groups.items()):
   text=None;relative=None
   if file.startswith(root+'/src/') and line>0:
    relative=str(Path(file).relative_to(root));p=W/relative;assert sha(p)==plan['source_sha256'][relative];pins[str(p)]=sha(p);ls=p.read_text().splitlines();assert line<=len(ls);text=ls[line-1]
   joined.append(dict(file=file,line=line,relative_source=relative,source=text,Ir=sum(r['Ir'] for r in subset),raw_rows=subset))
  saved=dict(whole_Ir=total,ordinary_SELF_Ir=matched['SELF_Ir'],exact_function=FN,object=OBJ,other_ordinary_records_NOT_MERGED=[x for x in names if x['function']!=FN or x['object']!=OBJ],file_partitions=dict(counts),raw_SELF_rows=rs,line_groups=joined,all_whole_SELF_exactly_reconciled=True,selected_matches_closed_ranking=True,inclusive_arcs_added=False)
  save('profile-'+c+'-rows.json',saved)
  result[c]={k:v for k,v in saved.items() if k not in ['raw_SELF_rows','line_groups']}
  print(json.dumps(dict(case=c,whole=total,SELF=matched['SELF_Ir'],other_records=[dict(function=x['function'],SELF=x['SELF_Ir']) for x in saved['other_ordinary_records_NOT_MERGED']],line0=sum(r['Ir'] for r in rs if r['line']==0),top_native_groups=[dict(file=g['relative_source'],line=g['line'],Ir=g['Ir'],source=g['source']) for g in sorted(joined,key=lambda g:-g['Ir']) if g['source']][:22])))
 assert all(sha(p)==h for p,h in pins.items())
 save('input-pins.json',dict(inputs=pins,all_inputs_unchanged=True,image_sha256=plan['expected_image_sha256'],source72_graph=plan['source_native72_graph'],no_runtime=True))
 save('selection-summary.json',dict(complete=True,cases=result,no_suffix_merging=True,no_inclusive_arcs_added=True,all_inputs_unchanged=True))
if __name__=='__main__':main()
