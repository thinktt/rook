"""Pure future raw-vector/model inspection; import launches no processes."""
from pathlib import Path
import hashlib,importlib.util,re,sys

def inspect_profile(path,plan):
 parser=Path(plan['vector_parser']);assert plan['vector_parser_sha256'] and hashlib.sha256(parser.read_bytes()).hexdigest()==plan['vector_parser_sha256']
 spec=importlib.util.spec_from_file_location('rook2_branch_cache_vector_parser',parser);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
 parsed=module.parse_file(path,expected_events=plan['event_names'])
 events=parsed['events'];assert len(events)==13 and len(set(events))==13 and set(events)==set(plan['event_names'])
 vectors={key:parsed[key] for key in ['summary','totals','SELF_sum']}
 for vec in vectors.values():assert set(vec)==set(events) and all(type(x) is int and 0<=x<=2**64-1 for x in vec.values())
 assert vectors['summary']==vectors['totals']==vectors['SELF_sum'] and vectors['summary']['Ir']>0
 model={};pids=[];position_headers=[]
 with Path(path).open() as f:
  for line in f:
   if line.startswith('pid:'):pids.append(int(line.split(':',1)[1]))
   if line.startswith('positions:'):position_headers.append(line.split(':',1)[1].split())
   match=re.fullmatch(r'desc:\s+(I1|D1|LL) cache:\s+([0-9,]+) B,\s+([0-9,]+) B,\s+(\d+)-way associative\s*',line)
   if match:
    name,size,width,ways=match.groups();assert name not in model
    model[name]=dict(bytes=int(size.replace(',','')),associativity=int(ways),line_bytes=int(width.replace(',','')))
 assert len(pids)==1 and (not position_headers or position_headers==[['line']])
 assert model==plan['hypothetical_cache_model'],model
 return dict(events=events,summary=vectors['summary'],totals=vectors['totals'],SELF_sum=vectors['SELF_sum'],profile_pid=pids[0],hypothetical_cache_model=model,raw_SELF_row_count=len(parsed['raw_SELF_rows']),raw_inclusive_call_arc_count=len(parsed['raw_inclusive_call_arcs_NOT_ADDED']),inclusive_arcs_added_to_SELF=False)

def inspect_annotator_totals(text,events):
 headers=[];totals=[]
 for line in text.splitlines():
  words=line.split();names=[x for x in words if x in events]
  if len(words) in (len(events),len(events)+1) and words[:len(events)]==names and set(names)==set(events) and (len(words)==len(events) or words[-1]=='file:function'):headers.append(names)
  if line.rstrip().endswith('PROGRAM TOTALS'):
   values=line.rsplit('PROGRAM TOTALS',1)[0].split();assert len(values)==len(events)
   assert all(re.fullmatch(r'[0-9][0-9,]*',x) for x in values);totals.append([int(x.replace(',','')) for x in values])
 assert headers and all(x==headers[0] for x in headers) and len(totals)==1
 return dict(zip(headers[0],totals[0]))
