from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def clearance(kind='execution'):
 assert kind in ['freeze','execution']
 c=load(HERE/'execution-clearance.json');plan=load(HERE/'validation-plan.json')
 assert c['authorized'] is True and c['scope']=='complete117-ledger-test-untimed-validation'
 assert c['functional_execution_authorized'] is True and c['conflicting_cpu_windows_closed'] is True
 assert c['source_graph_sha256']==plan['source_graph_sha256'] and c['prepared_sha256']==plan['prepared_sha256']
 assert plan['status']=='EXACT_COMPLETE117_PARENT_AUTHORIZED_UNTIMED'
 a=plan['execution_authority'];assert sha(Path(a['path']))==a['sha256']
 original=load(Path(a['path']));assert original['authorized'] and original['source_sha256']==plan['source_sha256']
 assert not c.get('timing_pgo_profiler_authorized',False)
 assert sorted(os.sched_getaffinity(0))==plan['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ.get('TMPDIR')==plan['TMPDIR']=='/home/legolas/rook2-build-tmp'
 return plan
def terminal(path):
 t=load(path);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['initial_chunk_id'] and t['terminal_chunk_id']
 return t
def check_sources(plan):
 for root in [Path(plan['home_source']),Path(plan['frozen_source'])]:
  assert all(sha(root/name)==h for name,h in plan['source_sha256'].items())
def check_dependencies(plan):
 before=load(Path(plan['output']['freeze'])/'dependencies.json');assert all(sha(Path(path))==h for path,h in before.items())
