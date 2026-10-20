"""Future complete117 FUNCTIONAL-only finalizer. Inert/unparsed/unrun."""
from pathlib import Path
import json,os
from guard import HERE,clearance,load,sha,write,terminal,check_sources,check_dependencies

def main():
 plan=clearance();paths={k:Path(v) for k,v in plan['output'].items()}
 keys=['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation']
 for k in keys:terminal(paths[k]/'tool-terminal.json')
 check_sources(plan);check_dependencies(plan)
 ind=load(paths['reconciliation']/'independent-verification.json')
 assert ind['status']=='pass' and ind['source_stable'] and ind['all_raw_expected_and_actual_equal'] and ind['all_native_child_exits_confirmed']
 assert tuple(ind[k] for k in ['native_units','diagnostic_units','strict_replays','interruption_fixtures','interruption_searches','diagnostic_cases','diagnostic_operations','whole_fixture_files'])==(177,209,54,8,24,7673,117,115)
 tests=(paths['native-validation']/'rook2-tests.stdout').read_text()
 assert 'test ordinary::tests::recursive_iio_defaults_true_and_false_initial_tail_errors_unwind_without_phase_subtrees ... ok' in tests
 g=load(paths['generic-build']/'receipt.json');d=load(paths['diagnostic-build']/'receipt.json')
 for key in ['toolchain','mode','target_triple','target_cpu','rust_flags']:assert g[key]==d[key]
 assert g['mode']=='generic' and g['pgo']['mode']==d['pgo']['mode']=='none'
 assert sha(paths['generic-build']/'rook2-exact')==g['binary_output']['sha256']==ind['native_artifact_sha256']
 assert sha(paths['diagnostic-build']/'rook2-diag-exact')==d['binary_output']['sha256']==ind['diagnostic_artifact_sha256']
 observed={n:load(paths['strict-check']/(n+'-actual-engine-affinity.json')) for n in ['strict54','wire']}
 assert len(observed['strict54']['actual_observed_pids'])==54 and len(observed['wire']['actual_observed_pids'])==8
 assert all(mask==plan['affinity'] for x in observed.values() for mask in x['actual_observed_pids'].values())
 exe_prefixes=[str(Path(plan['home_source']))+'/',str(paths['generic-build']/'rook2-exact'),str(paths['diagnostic-build']/'rook2-diag-exact'),str(paths['native-validation']/'unit-bin')+'/',str(paths['diagnostic']/'unit-bin')+'/'];live=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name) in [os.getpid(),os.getppid()]:continue
  try:exe=os.readlink(p/'exe');argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\0') if v]
  except OSError:continue
  if any(exe.startswith(x) for x in exe_prefixes) or ('python' in Path(exe).name and len(argv)>1 and argv[1].endswith('.py') and argv[1].startswith(str(HERE)+'/')):live.append({'pid':int(p.name),'exe':exe,'argv':argv})
 assert not live,live
 result={'status':'COMPLETE117_FUNCTIONAL_PASS_ONLY','source':plan['home_source'],'source_graph_sha256':plan['source_graph_sha256'],'native_units':177,'native_lib_units':175,'native_dev_units':2,'corrected_tail_witness_executed':True,'diagnostic_units':209,'strict54':54,'wire_fixtures':8,'wire_searches':24,'operations':117,'cases':7673,'whole_files':115,'native_sha256':ind['native_artifact_sha256'],'adapter_sha256':ind['diagnostic_artifact_sha256'],'live_owned_processes':live,'all_owned_native_jobs_terminal':True,'actual_terminals':{k:load(paths[k]/'tool-terminal.json') for k in keys},'canonical_domain_audit_limit':plan['canonical_domain_audit_limit'],'backend_review_separate_owner':True,'local_full3288_gate_separate':True,'cpu_pgo_profiler':False,'promotion_authorized':False,'final_packaging_outer_terminal_required':True}
 write(HERE/'validation-summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
