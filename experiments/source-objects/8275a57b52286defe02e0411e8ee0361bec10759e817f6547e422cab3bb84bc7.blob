"""Activity-only complete117 guard; no native launch from this module."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def terminal(path,expected=0):
 t=load(path);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==expected and t['initial_chunk_id'] and t['terminal_chunk_id']
 return t
def clearance(kind='execution'):
 assert kind in ['freeze','execution']
 c=load(HERE/'execution-clearance.json');plan=load(HERE/'validation-plan.json')
 assert c['authorized'] is True,'HOLD: explicit parent execution clearance absent'
 assert c['scope']=='activity-value-inputs-complete117-corpus-continuation02'
 assert c['source_graph_sha256']==plan['source_graph_sha256'] and c['plan_sha256']==sha(HERE/'validation-plan.json')
 assert c['conflicting_cpu_windows_closed'] is True and not c.get('timing_pgo_profiler_authorized',False)
 a=c['parent_advancement_acceptance'];assert a and sha(a['path'])==a['sha256']
 decision=load(a['path']);assert decision['accepted_for_complete117_diagnostic'] is True
 assert decision['source_graph_sha256']==plan['source_graph_sha256'] and decision['generic_image_sha256']==plan['native_reference']['image_sha256']
 assert decision['pgo_pilot_independent_reconciliation_sha256']==plan['pgo_advancement_reference']['independent_sha256']
 pilot=load(plan['pgo_advancement_reference']['independent']);assert pilot['complete'] and pilot['advance_rule_satisfied']
 assert sorted(os.sched_getaffinity(0))==plan['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert os.environ.get('TMPDIR')==plan['TMPDIR']=='/home/legolas/rook2-build-tmp'
 check_dependencies(plan)
 return plan
def check_sources(plan):
 roots=[Path(plan['frozen_source'])]
 if Path(plan['home_source']).exists():roots.append(Path(plan['home_source']))
 for root in roots:
  assert all(sha(root/name)==h for name,h in plan['source_sha256'].items()),str(root)
 for name,h in plan['native_sha256'].items():assert sha(Path(plan['native_reference']['crate_source'])/name)==h
 for name,h in plan['tools_sha256'].items():assert sha(Path(plan['native_reference']['crate_source'])/name)==h
 for name,h in plan['diagnostic_sha256'].items():assert sha(Path(plan['root_cold_source'])/name.removeprefix('diagnostic/'))==h
 for name,h in plan['harness_sha256'].items():assert sha(HERE/name)==h
 check_native_reuse(plan)
 check_partial(plan)
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

def check_partial(plan):
 """Reuse green children without relabeling failed01 outer as successful."""
 import re,tarfile
 ref=plan['partial01'];diag=Path(ref['diagnostic']);build=Path(ref['build'])
 terminal(diag/'tool-terminal.json',expected=1)
 terminal(Path(plan['output']['freeze'])/'tool-terminal.json')
 vr=load(diag/'verification.json');assert vr['complete'] is False and vr['failure'].startswith('AssertionError:')
 assert len(vr['stages'])==4 and all(row['actual_child_return_observed'] and row['exit_code']==0 for row in vr['stages'])
 for stem,row in zip(['unit-build','rook2-diag-tests','build-driver','archive'],vr['stages']):
  assert sha(diag/(stem+'.stdout'))==row['stdout_sha256'] and sha(diag/(stem+'.stderr'))==row['stderr_sha256']
 assert not (diag/'raw-cases').exists() and not (diag/'conformance.stdout').exists() and not (diag/'conformance.stderr').exists()
 text=(diag/'rook2-diag-tests.stdout').read_text();assert len(re.findall(r'^test .* \.\.\. ok$',text,re.M))==209 and 'test result: ok. 209 passed; 0 failed;' in text
 assert sha(diag/'unit-bin/rook2-diag/unit-exact')==vr['units']['rook2-diag']['binary_sha256']==ref['unit_sha256']
 br=load(build/'receipt.json');cold={k.removeprefix('diagnostic/'):v for k,v in plan['diagnostic_sha256'].items()}
 assert br['source_sha256_before']==br['source_sha256_after']==cold and br['source_identity_unchanged']
 # build.py snapshots tools inside --crate, not the root helper's directory.
 assert br['tool_sha256_before']==br['tool_sha256_after']==plan['diagnostic_crate_tools_sha256']=={}
 assert len(plan['tools_sha256'])==23 # separately checked by check_sources/native reuse
 assert br['outcome']=='build-succeeded-with-stable-input-snapshot' and br['cargo_exit_code']==0
 nr=load(plan['native_reference']['build_receipt'])
 for key in ['toolchain','mode','target_triple','target_cpu','rust_flags']:assert br[key]==nr[key]
 assert br['mode']=='generic' and br['pgo']['mode']=='none'
 assert sha(build/'rook2-diag-exact')==br['binary_output']['sha256']==vr['artifact_sha256']==ref['adapter_sha256']
 ar=load(build/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and ar['files']==43 and ar['binary_sha256']==ref['adapter_sha256']
 assert sha(build/ar['archive'])==ar['sha256']
 with tarfile.open(build/ar['archive'],'r:gz') as t:
  members={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
 assert members==cold #43 crate files +0 crate-local tools, not root23
