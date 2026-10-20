"""Offline parse of retained Ir rows/reports only; no subprocess/import of profiling drivers."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re
P=Path(__file__).resolve().parent
O=Path('/home/legolas/rook2-private/fullbyte-callgrind-20261018-01')
TOOL=Path('/home/legolas/.local/imp2-tools/valgrind/usr/bin/callgrind_annotate')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(n,x):
 with (P/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
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
cost_re=re.compile(r'^\s*([\d,]+)\s+\(\s*[\d.]+%\)\s+(.*)$')
def functions(path):
 result=Counter()
 for s in path.read_text().splitlines():
  m=cost_re.match(s)
  if not m:continue
  name=re.sub(r' \[.*\]$','',m[2])
  if name=='PROGRAM TOTALS':continue
  assert ':' in name,name
  file,fn=name.split(':',1);result[(file,fn)]+=int(m[1].replace(',',''))
 return result

def annotation(path):
 result=Counter();number=None;unidentified=0;annotated=None
 for s in path.read_text().splitlines():
  mark=re.fullmatch(r'-- line (\d+) -+',s)
  if mark:number=int(mark[1]);continue
  m=cost_re.match(s)
  if not m:continue
  amount=int(m[1].replace(',',''));text=m[2]
  if text.startswith('=>') or text.startswith('<=') or text=='PROGRAM TOTALS':continue
  if text.startswith('<counts for unidentified lines'):unidentified+=amount;continue
  if text=='events annotated':annotated=amount;continue
  assert number is not None,(path,s)
  result[number]+=amount
 return result,unidentified,annotated

def ordinary(fn):return fn.startswith('rook2::ordinary::') and '::visit_ordinary_impl' in fn

def main():
 proof=load(O/'independent-verification.json');assert proof['complete'] and proof['all_original_inputs_unchanged'] and proof['original_checkReplay_cases']==2
 pins={str(p):sha(p) for p in O.iterdir() if p.is_file()}
 pins[str(TOOL)]=sha(TOOL);result={}
 for case in ['35','08']:
  prefix='profile-'+case;rows,arcs,total=raw(O/(prefix+'.callgrind'))
  assert total==proof['cases'][prefix]['total_simulated_Ir']
  groups=Counter()
  for r in rows:groups[(r['file'],r['function'])]+=r['Ir']
  printed=functions(O/(prefix+'-functions.stdout'))
  assert {k:v for k,v in groups.items() if v}==dict(printed)
  assert sum(printed.values())==total
  reports={};compiled={}
  for source,info in proof['cases'][prefix]['source_annotations'].items():
   file=info['compiled_source'];compiled[source]=file;assert sha(Path(file))==info['source_sha256'];pins[file]=info['source_sha256']
   name=Path(source).stem;report=O/(prefix+'-'+name+'-lines.stdout');text=report.read_text()
   assert 'Thresholds:       0' in text
   actual=Counter()
   for row in rows:
    if row['file']==file:actual[row['line']]+=row['Ir']
   if not info['has_information']:
    assert not actual and 'No information has been collected' in text
    reports[source]={'has_information':False,'raw_file_exclusive_Ir':0};continue
   displayed,zero,annotated=annotation(report)
   assert dict(displayed)=={k:v for k,v in actual.items() if k!=0 and v},(prefix,source)
   assert zero==actual[0] and annotated==sum(v for k,v in actual.items() if k!=0)
   reports[source]={'has_information':True,'raw_file_exclusive_Ir':sum(actual.values()),'identified_positive_line_Ir':annotated,'line0_Ir':zero}
  move=compiled['src/movegen.rs'];ordfile=compiled['src/ordinary.rs']
  selected=[r for r in rows if ordinary(r['function']) and r['file']==move]
  buckets={'finder_and_boolean_69_132':lambda r:69<=r['line']<=132,'projection_157_188':lambda r:157<=r['line']<=188,'existing_entry_check_136_138':lambda r:136<=r['line']<=138,'unidentified_line0':lambda r:r['line']==0}
  assigned=set();sets={};metrics={}
  for name,predicate in buckets.items():
   subset=[r for r in selected if predicate(r)];ids={r['raw_line'] for r in subset};assert not assigned&ids;assigned|=ids;sets[name]=ids;metrics[name]=sum(r['Ir'] for r in subset)
  remainder=[r for r in selected if r['raw_line'] not in assigned];metrics['other_movegen_identified']=sum(r['Ir'] for r in remainder)
  assert sum(metrics.values())==sum(r['Ir'] for r in selected)
  mapped=metrics['finder_and_boolean_69_132']+metrics['projection_157_188']
  majors={}
  selectors={'ordinary_all_source_partitions':lambda f:ordinary(f),'Q_all_source_partitions':lambda f:f.startswith('rook2::quiescence::') and '::visit_q_impl' in f,'full_legal_generation_body_all_sources':lambda f:f=='rook2::movegen::generate_legal','activity_compute_all_sources':lambda f:f=='rook2::activity::compute','influence_build_all_sources':lambda f:f=='rook2::influence::Influence::build','full_evaluator_all_sources':lambda f:f.startswith('rook2::evaluator::') and '::full_impl' in f}
  claimed=set()
  for name,predicate in selectors.items():
   subset=[r for r in rows if predicate(r['function'])];ids={r['raw_line'] for r in subset};assert not claimed&ids;claimed|=ids;majors[name]={'Ir':sum(r['Ir'] for r in subset),'percent':100*sum(r['Ir'] for r in subset)/total}
  byline=Counter()
  for row in selected:byline[row['line']]+=row['Ir']
  ordsite={str(i):sum(r['Ir'] for r in rows if r['file']==ordfile and r['line']==i) for i in [888,890,964,966,967,849]}
  result[prefix]={'total_Ir':total,'raw_self_row_count':len(rows),'excluded_call_arc_rows':len(arcs),'function_threshold100_count':len(printed),'function_report_exclusive_sum_equals_total':True,'source_reports':reports,'ordinary_movegen_partition_total_Ir':sum(r['Ir'] for r in selected),'ordinary_movegen_partition_buckets_Ir':metrics,'direct_mapped_finder_plus_projection_Ir':mapped,'direct_mapped_percent':100*mapped/total,'ordinary_movegen_line_Ir':dict(sorted(byline.items())),'ordinary_callsite_line_Ir':ordsite,'major_exclusive_function_families':majors,'ordinary_movegen_raw_rows':selected,'all_other_ordinary_partitions':[{"file":f,"function":fn,"Ir":v} for (f,fn),v in groups.items() if ordinary(fn) and f!=move]}
  write(prefix+'-analysis.json',result[prefix])
 assert all(sha(Path(path))==h for path,h in pins.items())
 write('input-pins.json',pins)
 write('analysis-summary.json',{'complete':True,'cases':{c:{k:v for k,v in r.items() if k not in ['ordinary_movegen_raw_rows','all_other_ordinary_partitions','ordinary_movegen_line_Ir']} for c,r in result.items()},'all_raw_self_rows_partitioned_and_sum_equals_profile_totals':True,'all_printed_function_rows_match_raw_exclusive_partitions':True,'all13_source_reports_checked_against_raw':True,'all_inputs_unchanged':True,'new_native_or_profile_or_annotation_runs':0})
 print(json.dumps({c:{k:r[k] for k in ['total_Ir','ordinary_movegen_partition_total_Ir','ordinary_movegen_partition_buckets_Ir','direct_mapped_finder_plus_projection_Ir','direct_mapped_percent','ordinary_callsite_line_Ir','major_exclusive_function_families']} for c,r in result.items()}))
if __name__=='__main__':main()
