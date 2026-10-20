"""Offline original Callgrind line-only exclusive rows/caller arcs; no subprocesses."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
P=Path(__file__).resolve().parent
O=Path('/home/legolas/rook2/evidence/candidate25-callgrind-20261018-01')
SOURCE=Path('/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 with (P/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
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

def printed(path):
 groups=Counter()
 for line in path.read_text().splitlines():
  m=re.match(r'^\s*([\d,]+)\s+\(\s*[\d.]+%\)\s+(.*)$',line)
  if not m or m[2]=='PROGRAM TOTALS':continue
  file,fn=re.sub(r' \[.*\]$','',m[2]).split(':',1);groups[(file,fn)]+=int(m[1].replace(',',''))
 return groups

def main():
 inputs=[O/n for n in ['profile-35.callgrind','profile-08.callgrind','profile-35-functions.stdout','profile-08-functions.stdout','provenance.json','independent-verification.json','tool-terminal.json']]+[SOURCE/n for n in ['attacks.rs','movegen.rs','ordinary.rs','types.rs','position.rs']]
 pins={str(p):sha(p) for p in inputs};results={}
 for case in ['35','08']:
  rows,arcs,total=raw(O/f'profile-{case}.callgrind');groups=Counter()
  for r in rows:groups[(r['file'],r['function'])]+=r['Ir']
  displayed=printed(O/f'profile-{case}-functions.stdout')
  assert 'Thresholds:       99' in (O/f'profile-{case}-functions.stdout').read_text()
  assert all(groups[k]==v for k,v in displayed.items())
  assert 99*total<=100*sum(displayed.values())<=100*total
  selected=[r for r in rows if r['function']=='rook2::movegen::generate_legal'];assigned=set();buckets={}
  predicates={
   'ordered_attackers_unique_source_174_235':lambda r:r['file']==str(SOURCE/'attacks.rs') and 174<=r['line']<=235,
   'generator_checker_binding_674_677':lambda r:r['file']==str(SOURCE/'movegen.rs') and 674<=r['line']<=677,
   'GenerationSafety_pin_scan_307_337':lambda r:r['file']==str(SOURCE/'movegen.rs') and 307<=r['line']<=337,
   'GenerationSafety_setup_evasion_281_306':lambda r:r['file']==str(SOURCE/'movegen.rs') and 281<=r['line']<=306,
   'line0_all_source_partitions':lambda r:r['line']==0,
   'non_native_inline_source_positive_lines':lambda r:not r['file'].startswith(str(SOURCE)+'/') and r['line']>0,
  }
  for name,predicate in predicates.items():
   subset=[r for r in selected if predicate(r)];ids={r['raw_line'] for r in subset};assert not assigned&ids;assigned|=ids
   buckets[name]={'Ir':sum(r['Ir'] for r in subset),'raw_rows':subset}
  remaining=[r for r in selected if r['raw_line'] not in assigned]
  buckets['remaining_positive_native_source']={'Ir':sum(r['Ir'] for r in remaining),'raw_rows':remaining}
  assert sum(b['Ir'] for b in buckets.values())==sum(r['Ir'] for r in selected)
  byfile={}
  for r in selected:
   byfile.setdefault(r['file'],Counter())[r['line']]+=r['Ir']
  callers=[r for r in arcs if r['callee_function']=='rook2::movegen::generate_legal']
  check_elsewhere=Counter()
  for r in rows:
   if r['file']==str(SOURCE/'attacks.rs') and 174<=r['line']<=235:check_elsewhere[r['function']]+=r['Ir']
  results[case]={'total_Ir':total,'raw_self_rows':len(rows),'displayed_exclusive_function_rows_exact':True,'function_table_threshold':99,'function_table_displayed_Ir':sum(displayed.values()),'function_table_omitted_Ir':total-sum(displayed.values()),'full_generator_self_Ir':sum(r['Ir'] for r in selected),'buckets':buckets,'full_generator_source_lines':{f:dict(sorted(v.items())) for f,v in byfile.items()},'full_generator_incoming_explicit_call_arcs':callers,'ordered_source_cost_by_function':dict(check_elsewhere)}
  write(f'profile-{case}-rows.json',results[case])
 assert all(sha(Path(p))==h for p,h in pins.items())
 write('input-pins.json',pins)
 write('summary.json',{'complete':True,'cases':{c:{k:({n:{'Ir':v['Ir']} for n,v in x.items()} if k=='buckets' else x) for k,x in r.items() if k!='full_generator_source_lines'} for c,r in results.items()},'all_inputs_unchanged':True,'new_native_profile_or_annotation_runs':0})
 print(json.dumps({c:{k:({n:v['Ir'] for n,v in x.items()} if k=='buckets' else x) for k,x in r.items() if k in ['total_Ir','full_generator_self_Ir','buckets','full_generator_incoming_explicit_call_arcs','ordered_source_cost_by_function']} for c,r in results.items()}))
if __name__=='__main__':main()
