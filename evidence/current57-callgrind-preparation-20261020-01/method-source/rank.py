"""Future offline SELF/caller reconciliation only; no native/tool execution."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,os,sys
from bounded_run import BoundedRunner
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
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

def worker():
 plan=load(HERE/'plan.json');assert load(HERE/'execution-clearance.json')['analysis'] is True
 assert sorted(os.sched_getaffinity(0))==plan['helper_affinity'] and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert all(sha(HERE/n)==h for n,h in load(HERE/'helper-pins.json').items())
 out=Path(plan['output'])
 for n in ['tool-terminal.json','verify-tool-terminal.json']:
  t=load(out/n);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and (t.get('terminal_chunk_id') or t.get('chunk_id'))
 p=load(out/'provenance.json');v=load(out/'independent-verification.json')
 assert p['complete'] and p['failure'] is None and v['complete'] and v['all_original_inputs_unchanged'] and v['original_checkReplay_cases']==1
 assert p['engine_sha256']==plan['engine_sha256'] and list(p['cases'])==plan['cases']==['profile-35']
 assert all(sha(n)==h for n,h in p['input_sha256'].items())
 data=out/'profile-35.callgrind';assert sha(data)==p['cases']['profile-35']['profile_sha256']
 rows,arcs,total=raw(data);assert total==p['cases']['profile-35']['total_simulated_Ir']
 rank=Counter();parts=defaultdict(Counter)
 for r in rows:rank[(r['object'],r['function'])]+=r['Ir'];parts[(r['object'],r['function'])][r['file']]+=r['Ir']
 ranking=[dict(object=k[0],function=k[1],SELF_Ir=z,file_partitions=dict(parts[k])) for k,z in sorted(rank.items(),key=lambda kv:(-kv[1],str(kv[0])))]
 assert sum(x['SELF_Ir'] for x in ranking)==total
 result=dict(complete=True,case='profile-35',engine_sha256=plan['engine_sha256'],total_simulated_Ir=total,exclusive_SELF_exactly_reconciled=True,ranking=ranking,raw_SELF_rows=rows,raw_inclusive_call_arcs_NOT_ADDED=arcs,scope='Recorded object+function identities across inline file partitions; no physical call/address inference from suffix or Ir',native_runs=0,performance_claim=False)
 with (out/'self-ranking.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 assert all(sha(n)==h for n,h in p['input_sha256'].items())
 print(json.dumps(dict(complete=True,total_simulated_Ir=total,SELF_sum=total,functions=len(ranking),raw_SELF_rows=len(rows),raw_arcs=len(arcs),native_runs=0)))
def main():
 if sys.argv[1:]==['--worker']:worker();return
 assert sys.argv[1:]==[]
 plan=load(HERE/'plan.json');assert load(HERE/'execution-clearance.json')['analysis'] is True
 out=Path(plan['output']);p=load(out/'provenance.json')
 runner=BoundedRunner(out,plan,started=p['study_started_monotonic'],boot_id=p['study_boot_id'])
 argv=['/usr/bin/taskset','-c','0-5,8-13',sys.executable,str(HERE/'rank.py'),'--worker']
 result=runner.run(argv,'independent-SELF-ranking',plan['supervision']['offline_checker_wall_ms'],cwd=HERE)
 record=dict(argv=argv,exit_code=result.returncode,actual_child_return_observed=True,output_sha256={k:sha(out/('independent-SELF-ranking.'+k)) for k in ['stdout','stderr']})
 with (out/'independent-SELF-ranking-child-terminal.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
 assert result.returncode==0 and not (out/'independent-SELF-ranking.stderr').stat().st_size
 assert load(out/'self-ranking.json')['exclusive_SELF_exactly_reconciled'] is True
 _,failure=runner._files();assert failure is None,failure
 print((out/'independent-SELF-ranking.stdout').read_text().strip())
if __name__=='__main__':main()
