"""Influence bitplane57 complete117 guard; no native launch from this module."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def terminal(path):
 t=load(path);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0 and t['initial_chunk_id'] and t['terminal_chunk_id']
 return t
def clearance(kind='corpus'):
 assert kind in ['freeze','native','build','corpus','reconcile','finalize']
 c=load(HERE/'execution-clearance.json');plan=load(HERE/'validation-plan.json')
 assert c['authorized'] is True and c['stages'][kind] is True,'HOLD: explicit parent stage clearance absent'
 assert c['scope']=='bitplane-pin-summary-complete117-untimed'
 assert c['source_graph_sha256']==plan['source_graph_sha256'] and c['plan_sha256']==sha(HERE/'validation-plan.json')
 assert c['conflicting_cpu_windows_closed'] is True and not c.get('timing_pgo_profiler_authorized',False)
 a=c['parent_final_validation_authorization'];assert a and sha(a['path'])==a['sha256']
 decision=load(a['path']);assert decision['experiment']==57 and decision['decision']=='ADVANCE_TO_FULL_VALIDATION' and decision['allow_full_native_and_mandatory_diagnostic_validation'] is True
 assert decision['candidate_sha256']==plan['own_pgo_reference']['image_sha256'] and decision['profile_sha256']==plan['own_pgo_reference']['profile_sha256']
 assert sorted(os.sched_getaffinity(0))==plan['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ.get('TMPDIR')==plan['TMPDIR']=='/home/legolas/rook2-build-tmp'
 for key in os.environ:
  assert not key.startswith(('CARGO_PROFILE_','CARGO_TARGET_','CARGO_BUILD_')),key
 for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH','CARGO_HOME','RUSTUP_TOOLCHAIN']:
  assert not os.environ.get(key),key
 check_dependencies(plan)
 return plan
def check_sources(plan):
 for name,h in plan['source_sha256'].items():assert sha(plan['source_origins'][name])==h,name
 if Path(plan['home_source']).exists():
  assert all(sha(Path(plan['home_source'])/name)==h for name,h in plan['source_sha256'].items())
 for name,h in plan['native_sha256'].items():assert sha(Path(plan['native_reference']['crate_source'])/name)==h
 for name,h in plan['tools_sha256'].items():assert sha(Path(plan['native_reference']['crate_source'])/name)==h
 for name,h in plan['diagnostic_sha256'].items():assert sha(Path(plan['root_cold_source'])/name.removeprefix('diagnostic/'))==h
 for name,h in plan['harness_sha256'].items():assert sha(HERE/name)==h
 check_native_reference(plan)
def check_dependencies(plan):
 for path,h in plan['immutable_dependencies'].items():assert sha(path)==h,path
 for path,h in plan['fixtures'].items():assert sha(path)==h,path
 for name,h in plan['harness_sha256'].items():assert sha(HERE/name)==h,name

def check_native_reference(plan):
 ref=plan['native_reference'];receipt=load(ref['build_receipt'])
 assert receipt['source_sha256_before']==receipt['source_sha256_after']==plan['native_sha256']
 assert receipt['tool_sha256_before']==receipt['tool_sha256_after']==plan['tools_sha256']
 assert receipt['mode']=='generic' and receipt['rust_flags']==['-C','target-cpu=x86-64'] and receipt['pgo']['mode']=='none'
 assert sha(ref['image'])==ref['image_sha256']==receipt['binary_output']['sha256']
 # Fresh195 generic native units are a separate stage from the209 DIAG package units.
