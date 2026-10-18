from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def clearance():
 plan=load(HERE/'plan.json');c=load(HERE/'execution-clearance.json')
 assert c['authorized'] is True and c['scope']=='exact105bits-diag-only' and c['no_cpu_or_profiler_live'] is True
 assert sorted(os.sched_getaffinity(0))==plan['affinity'] and os.environ.get('TMPDIR')==plan['TMPDIR'] and Path(plan['TMPDIR']).is_dir()
 return plan
def terminal(path):
 t=load(path);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['terminal_chunk_id'];return t
def check_sources(plan):
 assert all(sha(Path(plan['home_source'])/name)==h and sha(Path(plan['frozen_source'])/name)==h for name,h in plan['source_sha256'].items())
 ref=Path(plan['native_reference']);proof=load(ref/'reuse-proof.json');assert sha(ref/'rook2-exact')==proof['generic_sha256']
 assert all(sha(Path(name))==h for name,h in proof['original_reference_files'].items())
def check_dependencies(plan):
 deps=load(HERE/'dependencies.json');assert all(sha(Path(name))==h for name,h in deps.items())
