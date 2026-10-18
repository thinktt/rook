from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def clearance():
 c=load(HERE/'execution-clearance.json');assert c['authorized'] is True and c['scope']=='iterations-clock102-regression-overlay'
 assert c['conflicting_cpu_windows_closed'] is True
 for name in ['phase2_cpu_pilot','phase2_independent_reconciliation']:
  record=c[name];assert record['actual_tool_terminal_observed'] is True and record['exit_code']==0
  assert record['terminal_chunk_id']
  if 'initial_chunk_id' in record:assert record['initial_chunk_id']
  if record.get('session_id') is not None:assert isinstance(record['session_id'],int) and record['session_id']>0
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
 overlay=load(Path(plan['overlay_harness_manifest']));assert all(sha(Path(path))==h for path,h in overlay.items())
 assert sha(Path(plan['original_plan']))==plan['original_plan_sha256']
