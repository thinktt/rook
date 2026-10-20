"""Future functional-only metadata finalizer; no engine or compiler invocation."""
from pathlib import Path
import json,os,tarfile
from guard import HERE,clearance,load,sha,write,terminal,check_sources,check_dependencies

def main():
 plan=clearance();paths={k:Path(v) for k,v in plan['output'].items()}
 for key in ['freeze','diagnostic','reconciliation']:terminal(paths[key]/'tool-terminal.json')
 check_sources(plan);check_dependencies(plan)
 ind=load(paths['reconciliation']/'independent-verification.json')
 assert ind['status']=='pass' and ind['source_stable'] and ind['all_raw_expected_and_actual_equal'] and ind['all_native_child_exits_confirmed']
 assert tuple(ind[k] for k in ['native_units','diagnostic_units','strict_replays_reused','interruption_fixtures_reused','interruption_searches_reused','diagnostic_cases','diagnostic_operations','whole_fixture_files'])==(178,209,54,8,24,7673,117,115)
 assert sha(plan['native_reference']['image'])==ind['native_artifact_sha256']==plan['native_reference']['image_sha256']
 assert sha(paths['diagnostic-build']/'rook2-diag-exact')==ind['diagnostic_artifact_sha256']
 prefixes=[plan['home_source']+'/',str(paths['diagnostic-build']/'rook2-diag-exact'),str(paths['diagnostic']/'unit-bin')+'/'];live=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name) in [os.getpid(),os.getppid()]:continue
  try:exe=os.readlink(p/'exe');argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\0') if v]
  except OSError:continue
  if any(exe.startswith(x) for x in prefixes) or ('python' in Path(exe).name and len(argv)>1 and argv[1].endswith('.py') and argv[1].startswith(str(HERE)+'/')):live.append({'pid':int(p.name),'exe':exe,'argv':argv})
 assert not live,live
 result=dict(status='ACTIVITY_ONLY_COMPLETE117_FUNCTIONAL_PASS',source=plan['home_source'],source_graph_sha256=plan['source_graph_sha256'],native_reused=True,fresh_ordinary_native_runs=0,native_units=178,native_lib_units=176,native_dev_units=2,diagnostic_units=209,strict54_reused=54,wire_fixtures_reused=8,wire_searches_reused=24,operations=117,cases=7673,whole_files=115,native_sha256=ind['native_artifact_sha256'],adapter_sha256=ind['diagnostic_artifact_sha256'],all_original_raw_expected_actual_and_exits_reconciled=True,all_owned_native_jobs_terminal=True,live_owned_processes=live,actual_terminals={k:load(paths[k]/'tool-terminal.json') for k in ['freeze','diagnostic','reconciliation']},canonical_domain_audit_limit=plan['canonical_domain_audit_limit'],cpu_pgo_profiler_or_promotion_authorized=False,finalizer_outer_actual_terminal_required=True)
 write(HERE/'validation-summary.json',result)
 entries=[HERE/name for name in ['validation-plan.json','execution-clearance.json','prepared.json','source-proof.json','archive-verification.json','validation-summary.json','guard.py','stage.py','record_case.py','reconcile.py','finalize.py']]
 entries += [paths['reconciliation']/name for name in ['independent-verification.json','case-reconciliation.json','raw-case-sha256.json','tool-terminal.json']]
 manifest={str(p):sha(p) for p in entries};write(HERE/'final-metadata-manifest.json',manifest)
 with tarfile.open(HERE/'final-metadata.tar.gz','w:gz') as t:
  for p in entries:t.add(p,arcname=str(p.relative_to(HERE)),recursive=False)
 print(json.dumps(result))
if __name__=='__main__':main()
