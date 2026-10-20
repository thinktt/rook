from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def authorize(kind):
 assert kind in ['freeze','execution']
 c=load(HERE/(kind+'-clearance.json'))
 assert c['authorized'] is True and c['scope']==('generic-joined111-source-freeze' if kind=='freeze' else 'generic-joined111-untimed-validation')
 assert c['parent_authority'] and c['conflicting_cpu_windows_closed'] is True and c['actual_closed_windows']
 for window in c['actual_closed_windows']:
  for role in ['pilot','independent']:
   t=window[role];assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['terminal_chunk_id']
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 return c
def clearance(kind='execution'):
 authorize(kind);plan=load(HERE/'validation-plan.json')
 assert plan['status']=='FROZEN_EXACT111_EXECUTION_CLEARANCE_REQUIRED' and plan['affinity']==sorted(os.sched_getaffinity(0)) and plan['TMPDIR']==os.environ['TMPDIR']
 return plan
def terminal(path):
 t=load(path);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['initial_chunk_id'] and t['terminal_chunk_id']
 return t
def check_sources(plan):
 for root in [Path(plan['home_source']),Path(plan['frozen_source'])]:
  assert all(sha(root/name)==h for name,h in plan['source_sha256'].items())
def check_dependencies(plan):
 before=load(Path(plan['output']['freeze'])/'dependencies.json');assert all(sha(Path(path))==h for path,h in before.items())
