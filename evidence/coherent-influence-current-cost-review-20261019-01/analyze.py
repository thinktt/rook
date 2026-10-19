"""Read-only existing raw Callgrind SELF selection; no subprocesses/native calls."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,os
E=Path(__file__).resolve().parent
O=Path('/home/legolas/rook2-private/pressure-value-static-callgrind-20261019-01')
W=Path('/home/legolas/rook2/evidence/pressure-value-static-pgo-use-build-20261019-01/source-before')
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
FN='rook2::influence::Influence::build_coherent'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda n,x:(E/n).write_text(json.dumps(x,indent=2)+'\n')
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
  if m:value('fn' if m[1] in ['fn','cfn'] else 'ob' if m[1] in ['ob','cob'] else 'file',m[2])
 current_file=None;current_fn=None;callee_fn=None;position=0;pending=None;rows=[];arcs=[]
 for number,line in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe|cfi|fn|cfn|ob|cob)=(.*)$',line)
  if m:
   key,s=m.groups()
   if key in ['fl','fi','fe']:current_file=value('file',s)
   elif key=='fn':current_fn=value('fn',s)
   elif key=='cfn':callee_fn=value('fn',s)
   continue
  if line.startswith('calls='):
   assert pending is None
   pending=int(line.split('=',1)[1].split()[0]);assert pending>0
   continue
  m=re.fullmatch(r'([+\-]?\d+|\*|0x[0-9a-fA-F]+)\s+(\d+)\s*',line)
  if not m:continue
  token=m[1];position=position if token=='*' else position+int(token) if token[0] in '+-' else int(token,0) if token.startswith('0x') else int(token)
  assert current_file is not None and current_fn is not None
  row=dict(raw_line=number,file=current_file,function=current_fn,line=position,Ir=int(m[2]))
  if pending is None:rows.append(row)
  else:row.update(callee_function=callee_fn,explicit_calls=pending,inclusive_arc=True);arcs.append(row)
  pending=None
 assert pending is None
 total=int(next(s.split(':',1)[1] for s in lines if s.startswith('summary:')))
 assert sum(r['Ir'] for r in rows)==total==int(next(s.split(':',1)[1] for s in lines if s.startswith('totals:')))
 return rows,arcs,total

provenance=json.loads((O/'provenance.json').read_text())
assert provenance['complete'] and provenance['engine_sha256']=='c3166899f9380812b0fcb114d613021ba308699e46b0f7de48ffafaf4ff0e5a7'
verification=json.loads((O/'independent-verification.json').read_text());assert verification['complete'] and verification['all_original_inputs_unchanged']
paths=[O/n for n in ['provenance.json','independent-verification.json','tool-terminal.json','verify-tool-terminal.json']]
paths += [W/n for n in ['src/influence/coherent.rs','src/influence.rs','src/position.rs','src/attacks.rs']]
for path in paths[4:]:
 relative=path.relative_to(W)
 assert sha(path)==sha(Path('/home/legolas/rook2')/relative)==provenance['input_sha256'][str(Path(provenance['compiled_source_root'])/relative)]
paths += [Path('/home/legolas/rook2')/p.relative_to(W) for p in paths[4:]]
results={}
for case,total in [('35',45372164975),('08',3916044228)]:
 path=O/f'profile-{case}.callgrind';paths += [path,O/f'profile-{case}-functions.stdout',O/f'profile-{case}-coherent-lines.stdout']
 rows,arcs,observed=raw(path);assert total==observed
 selected=[r for r in rows if r['function']==FN]
 fullfile=Counter();lines=defaultdict(list)
 for row in selected:fullfile[row['file']]+=row['Ir'];lines[(row['file'],row['line'])].append(row)
 printed=[]
 for number,line in enumerate((O/f'profile-{case}-functions.stdout').read_text().splitlines(),1):
  m=re.match(r'^\s*([\d,]+) \([^)]*\)\s+(.+)$',line)
  if m and ':'+FN in m[2]:
   label=m[2].split(':'+FN)[0];cost=int(m[1].replace(',',''));assert fullfile[label]==cost
   printed.append({'raw_row':number,'file':label,'Ir':cost})
 assert sum(x['Ir'] for x in printed)==sum(r['Ir'] for r in selected)
 native_lines=[]
 for (file,line),subset in lines.items():
  src=None
  if file.startswith(provenance['compiled_source_root']+'/src/') and line>0:
   src=(W/Path(file).relative_to(provenance['compiled_source_root'])).read_text().splitlines()[line-1]
  native_lines.append({'file':file,'line':line,'Ir':sum(r['Ir'] for r in subset),'source':src,'raw_rows':[r['raw_line'] for r in subset]})
 result={'total_Ir':total,'producer_exclusive_SELF':sum(r['Ir'] for r in selected),'file_partitions':dict(fullfile),'line_groups':native_lines,'raw_SELF_rows':selected,'function_display_rows':printed,'incoming_arcs_NOT_ADDED':[r for r in arcs if r['callee_function']==FN],'outgoing_arcs_NOT_ADDED':[r for r in arcs if r['function']==FN]}
 results[case]=result;save('profile-'+case+'-self-selection.json',result)
 print(case,'TOTAL',result['producer_exclusive_SELF'],'wholepct',100*result['producer_exclusive_SELF']/total)
 for row in native_lines:
  print(Path(row['file']).name,row['line'],row['Ir'],row['source'] or '')
for case in ('35','08'):
 assert sha(O/f'profile-{case}.callgrind')==provenance['cases']['profile-'+case]['profile_sha256']
save('input-pins.json',{str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths})
save('self-summary.json',{'complete':True,'inputs_match_closed_provenance':True,'exclusive_self_rows_only':True,'incoming_and_outgoing_arcs_never_added':True,'cases':{case:{k:v for k,v in result.items() if k not in ['line_groups','raw_SELF_rows','incoming_arcs_NOT_ADDED','outgoing_arcs_NOT_ADDED']} for case,result in results.items()},'engine_profile_annotation_build_runs':0})
