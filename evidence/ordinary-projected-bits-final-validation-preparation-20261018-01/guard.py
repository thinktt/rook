"""Ordinary projected-bit complete117 guard; no native launch from this module."""
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
def clearance(kind='execution'):
 assert kind in ['freeze','execution']
 c=load(HERE/'execution-clearance.json');plan=load(HERE/'validation-plan.json')
 assert c['authorized'] is True,'HOLD: explicit parent execution clearance absent'
 assert c['scope']=='ordinary-projected-bits-final117-untimed'
 assert c['source_graph_sha256']==plan['source_graph_sha256'] and c['plan_sha256']==sha(HERE/'validation-plan.json')
 assert c['conflicting_cpu_windows_closed'] is True and not c.get('timing_pgo_profiler_authorized',False)
 a=c['parent_final_validation_authorization'];assert a and sha(a['path'])==a['sha256']
 decision=load(a['path']);assert decision['candidate25_full117_required'] is True
 assert decision['source_graph_sha256']==plan['source_graph_sha256'] and decision['generic_image_sha256']==plan['native_reference']['image_sha256']
 # User explicitly requests candidate25 even if its performance pilot parks it.
 # No CPU rule result is an admission requirement for final conformance.
 assert sorted(os.sched_getaffinity(0))==plan['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ.get('TMPDIR')==plan['TMPDIR']=='/home/legolas/rook2-build-tmp'
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
 check_native_reuse(plan)
def check_dependencies(plan):
 for path,h in plan['immutable_dependencies'].items():assert sha(path)==h,path
 for path,h in plan['fixtures'].items():assert sha(path)==h,path
 for name,h in plan['harness_sha256'].items():assert sha(HERE/name)==h,name

def check_native_reuse(plan):
 ref=plan['native_reference'];receipt=load(ref['build_receipt']);assert receipt['source_sha256_before']==receipt['source_sha256_after']==plan['native_sha256']
 assert receipt['tool_sha256_before']==receipt['tool_sha256_after']==plan['tools_sha256']
 assert receipt['mode']=='generic' and receipt['rust_flags']==['-C','target-cpu=x86-64'] and receipt['pgo']['mode']=='none'
 assert sha(ref['image'])==ref['image_sha256']==receipt['binary_output']['sha256']
 result=load(ref['native_result']);assert result['complete'] and result['failure'] is None and result['source_and_tools_unchanged']
 assert result['total_tests']==178 and result['tests']['lib']['passed']==176 and result['tests']['dev']['passed']==2
 assert all(row['actual_child_return_observed'] and row['exit_code']==0 for row in result['commands'])
 for name,row in result['tests'].items():assert sha(ref['frozen_unit_images'][name])==row['sha256']
 independent=load(ref['independent']);assert independent['complete'] and independent['native_tests']==178 and independent['strict54_original_checkReplay'] and independent['source46_tools23_archive69_equal']
 assert independent['engine_sha256']==ref['image_sha256'] and len(independent['wire8_searches24_raw_protocol'])==8
 for path in ref['actual_terminals']:terminal(path)
