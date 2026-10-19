"""Offline only: original replay assertion plus exact disjoint raw Ir partition."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,os,re,subprocess
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def raw(path):
 lines=path.read_text().splitlines();names={'file':{},'fn':{},'ob':{}}
 assert [s for s in lines if s.startswith('events:')]==['events: Ir']
 assert [s for s in lines if s.startswith('positions:')]==['positions: line']
 def kind(k):return 'fn' if k in ['fn','cfn'] else 'ob' if k in ['ob','cob'] else 'file'
 # Definitions and references share dictionaries; forward references do not
 # require inventing names. This preserves the accepted parser's two passes.
 for line in lines:
  m=re.match(r'^(fl|fi|fe|cfi|cfl|fn|cfn|ob|cob)=\((\d+)\) (.*)$',line)
  if m:
   k,index,name=m.groups();d=names[kind(k)];index=int(index)
   assert index not in d or d[index]==name;d[index]=name
 def value(k,s):
  m=re.fullmatch(r'\((\d+)\)(?: (.*))?',s)
  return names[kind(k)][int(m[1])] if m else s
 current_file=current_fn=current_obj=callee=callee_file=None
 current_fn_id=callee_id=None
 position=0;pending=None;rows=[];arcs=[]
 for number,line in enumerate(lines,1):
  m=re.match(r'^(fl|fi|fe|cfi|cfl|fn|cfn|ob|cob)=(.*)$',line)
  if m:
   key,s=m.groups();v=value(key,s)
   if key in ['fl','fi','fe']:current_file=v
   elif key=='fn':current_fn=v;current_fn_id=s
   elif key=='ob':current_obj=v
   elif key=='cfn':callee=v;callee_id=s
   elif key in ['cfi','cfl']:callee_file=v
   continue
  if line.startswith('calls='):
   assert pending is None and callee is not None
   count=int(line.split('=',1)[1].split()[0]);assert count>0
   pending={'calls':count,'callee':callee,'callee_raw_id':callee_id,'callee_file':callee_file};continue
  m=re.fullmatch(r'([+\-]?\d+|\*|0x[0-9a-fA-F]+)\s+(\d+)\s*',line)
  if not m:continue
  token=m[1];position=position if token=='*' else position+int(token) if token[0] in '+-' else int(token,0) if token.startswith('0x') else int(token)
  assert current_file is not None and current_fn is not None
  row={'raw_line':number,'file':current_file,'function':current_fn,'function_raw_id':current_fn_id,'object':current_obj,'line':position,'Ir':int(m[2])}
  if pending is not None:row.update(pending);arcs.append(row);pending=None
  else:rows.append(row)
 assert pending is None
 summary=[int(s.split(':',1)[1]) for s in lines if s.startswith('summary:')]
 totals=[int(s.split(':',1)[1]) for s in lines if s.startswith('totals:')]
 assert len(summary)==1 and summary==totals and sum(r['Ir'] for r in rows)==summary[0]
 return rows,arcs,summary[0]
def family(fn):
 if 'Influence::build' in fn:return 'fresh'
 if 'Influence::update_ordinary' in fn:return 'update'
 if 'Influence::derive_ordinary' in fn:return 'derive_if_any'
 if 'Influence::ray_signed' in fn:return 'signed_rays'
 if 'CurrentInfluence' in fn and '::fill' in fn:return 'fill'
 if 'rook2::ordinary::' in fn and 'visit_ordinary_impl' in fn:return 'ordinary'
 if 'rook2::quiescence::' in fn and 'visit_q_impl' in fn:return 'Q'
 if any(t in fn for t in ['rook2::timed::','rook2::root_schedule::','rook2::session::']):return 'root_host'
 if any(t in fn for t in ['rook2::evaluator::','rook2::activity::','rook2::shelter::','rook2::evaluation::']):return 'evaluation_consumers'
 return 'rest'
def main():
 p=load(HERE/'plan.json');out=Path(p['output']);assert load(HERE/'execution-clearance.json')['verify'] is True
 assert sorted(os.sched_getaffinity(0))==p['helper_affinity'] and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 t=load(out/'tool-terminal.json');assert t['actual_tool_terminal_observed'] and t['exit_code']==0 and (t.get('terminal_chunk_id') or t.get('chunk_id'))
 record=load(out/'provenance.json');assert record['complete'] and record['exactly_two_fresh_engine_lifetimes']
 closure=load(out/'input-closure.json');assert closure==record['input_sha256'] and all(sha(f)==h for f,h in closure.items())
 for c in record['commands']:
  assert c['actual_child_return_observed'] and c['exit_code']==(255 if c['argv'][-1]=='--version' and 'callgrind_annotate' in c['argv'][0] else 0)
  stem=c['stem'];assert load(out/(stem+'-terminal.json'))==c
  stdout=out/(stem+'.stdout');stderr=out/(stem+'.stderr')
  assert sha(stdout)==c['stdout_sha256'] and sha(stderr)==c['stderr_sha256']
 results={}
 for name,v in p['variants'].items():
  target=out/name;row=load(target/'replay.json');assert sha(v['engine'])==v['engine_sha256']
  argv=[p['node'],str(HERE/'replay08.mjs'),'offline',str(HERE/'plan.json'),name,str(target)]
  with (target/'offline.stdout').open('xb') as x,(target/'offline.stderr').open('xb') as y:r=subprocess.run(argv,stdout=x,stderr=y,timeout=p['static_command_timeout_seconds'])
  write(target/'offline-terminal.json',{'argv':argv,'exit_code':r.returncode,'actual_child_return_observed':True})
  assert r.returncode==0 and (target/'offline.stderr').stat().st_size==0
  assert load(target/'offline.stdout')=={'complete':True,'engineRuns':0,'originalCheckReplay':1}
  data=target/'profile.callgrind';assert sha(data)==record['cases'][name]['profile_sha256']
  assert sha(target/'valgrind.log')==record['cases'][name]['log_sha256']
  rows,arcs,total=raw(data);assert total==record['cases'][name]['whole_lifetime_Ir']
  exclusive=Counter();fnself=Counter();incoming=Counter();arc_cost=Counter();outgoing=Counter();family_calls=Counter();family_inclusive=Counter()
  for x in rows:exclusive[family(x['function'])]+=x['Ir'];fnself[x['function']]+=x['Ir']
  for x in arcs:
   incoming[x['callee']]+=x['calls'];arc_cost[x['callee']]+=x['Ir'];outgoing[x['function']]+=x['calls']
   family_calls[family(x['callee'])]+=x['calls'];family_inclusive[family(x['callee'])]+=x['Ir']
  assert sum(exclusive.values())==total
  selected={fn:{'self_Ir':fnself[fn],'incoming_calls':incoming[fn],'incoming_arc_inclusive_Ir':arc_cost[fn],'outgoing_calls':outgoing[fn]} for fn in set(fnself)|set(incoming) if family(fn) not in ['rest','root_host','evaluation_consumers','Q']}
  # These exact expected counts are only evaluated AFTER original live/offline
  # replay and pinned input/image closure. They come from closed case08 census,
  # not from expected fixture outputs substituted for observed calls.
  expected={'baseline25':{'fresh':361836,'update':0},'inplace30':{'fresh':147171,'update':214665}}[name]
  assert family_calls['fresh']==expected['fresh'] and family_calls['update']==expected['update'],(name,dict(family_calls))
  assert family_calls['fresh']+family_calls['update']==361836
  assert family_calls['derive_if_any']==0
  # update-inclusive ALREADY includes signed rays: do not add ray-inclusive.
  # fill-self excludes fresh/update callees. Caller dispatch/copies remain in
  # ordinary-self and are deliberately not all relabeled as map work.
  map_ir=family_inclusive['fresh']+family_inclusive['update']+exclusive['fill']
  assert not any(family(a['function'])=='fresh' and a['Ir'] for a in arcs),'fresh unexpectedly has executed outgoing calls; revise attribution before interpreting'
  assert not any(family(a['function'])=='update' and family(a['callee'])!='signed_rays' and a['Ir'] for a in arcs),'unclassified executed update descendant'
  assert 0<=map_ir<=total
  details={'whole_lifetime_Ir':total,'disjoint_exclusive_Ir':dict(exclusive),'selected_function_self_and_calls':selected,'observed_stage_calls':dict(family_calls),'closed_census_expected_calls':expected,'map_family_non_double_counted_Ir':{'fresh_inclusive':family_inclusive['fresh'],'update_inclusive_including_signed_rays':family_inclusive['update'],'outlined_fill_self':exclusive['fill'],'sum':map_ir,'whole_lifetime_residual':total-map_ir},'all_call_arcs':arcs,'raw_self_rows':rows,'scope':'Incoming inclusive arcs generally include descendants and can overlap recursively. Only bounded nonrecursive fresh/update plus fill-self forms the separate map-family subtotal; ray-inclusive is never added again. Emitted call counts are not inlined logical invocation counts. Ordinary-self includes unrelated work and is not wholly assigned to maps.'}
  write(target/'partition.json',details);results[name]={k:v for k,v in details.items() if k not in ['all_call_arcs','raw_self_rows']}
 assert all(sha(f)==h for f,h in closure.items())
 write(out/'independent-verification.json',{'complete':True,'cases':results,'original_offline_checkReplay_count':2,'engine_runs':0,'all_inputs_unchanged':True,'no_CPU_or_qualification_claim':True,'outer_actual_terminal_required':True})
 print(json.dumps({k:{'whole_lifetime_Ir':v['whole_lifetime_Ir'],'exclusive':v['disjoint_exclusive_Ir']} for k,v in results.items()}))
if __name__=='__main__':main()
