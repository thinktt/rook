from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def clearance():
 c=load(HERE/'execution-clearance.json');assert c['authorized'] is True and c['scope']=='controlled-root108-untimed-validation'
 assert c['conflicting_cpu_windows_closed'] and all(c[k]['actual_tool_terminal_observed'] and c[k]['exit_code']==0 for k in ['pilot','independent'])
 plan=load(HERE/'plan.json');assert sorted(os.sched_getaffinity(0))==plan['affinity']
 assert os.environ.get('TMPDIR')==plan['TMPDIR'] and Path(plan['TMPDIR']).is_dir()
 return plan
def terminal(path):
 t=load(path);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0
 assert t['initial_chunk_id'] and t['terminal_chunk_id']
 return t
def check_sources(plan):
 source=Path(plan['home_source']);assert all(sha(source/name)==h for name,h in plan['source_sha256'].items())
 frozen=Path(plan['frozen_source']);assert all(sha(frozen/name)==h for name,h in plan['source_sha256'].items())
def check_dependencies(plan):
 before=load(Path(plan['output']['freeze'])/'dependencies.json');assert all(sha(Path(path))==h for path,h in before.items())
