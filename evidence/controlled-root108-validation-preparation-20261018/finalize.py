from pathlib import Path
import json,hashlib,tarfile,re,os
from guard import load,sha,write,clearance,terminal,check_sources,check_dependencies,HERE
plan=clearance();paths={k:Path(v) for k,v in plan['output'].items()};check_sources(plan);check_dependencies(plan)
for key in ['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation']:terminal(paths[key]/'tool-terminal.json')
ind=load(paths['reconciliation']/'independent-verification.json');assert ind['status']=='pass' and ind['source_stable'] and ind['all_raw_expected_and_actual_equal'] and ind['all_native_child_exits_confirmed']
assert (ind['native_units'],ind['diagnostic_units'],ind['diagnostic_cases'],ind['diagnostic_operations'],ind['whole_fixture_files'])==(163,188,7584,108,105)
B=paths['generic-build'];D=paths['diagnostic-build'];g=load(B/'receipt.json');d=load(D/'receipt.json')
for k in ['toolchain','mode','target_triple','target_cpu','rust_flags']:assert g[k]==d[k],k
assert g['pgo']['mode']==d['pgo']['mode']=='none'
assert sha(B/'rook2-exact')==g['binary_output']['sha256']==ind['native_artifact_sha256']
assert sha(D/'rook2-diag-exact')==d['binary_output']['sha256']==ind['diagnostic_artifact_sha256']
assert all(sha(Path('/usr/bin')/name)==g['toolchain'][name+'_executable_sha256'] for name in ['rustc','cargo'])
for key,unitcounts in [('native-validation',{'rook2':161,'rook2-dev':2}),('diagnostic',{'rook2-diag':188})]:
 v=load(paths[key]/'verification.json');assert v['complete'] and v['failure'] is None
 for target,n in unitcounts.items():assert v['units'][target]['passed']==n and sha(paths[key]/'unit-bin'/target/'unit-exact')==v['units'][target]['binary_sha256']
for key in ['generic-build','diagnostic-build']:
 a=load(paths[key]/'archive-receipt.json');assert sha(paths[key]/a['archive'])==a['sha256']
C=Path('/home/legolas/rook2/evidence/controlled-root108-codegen-02-20261018');cap=load(C/'capture.json');gate=load(C/'bounded-gate.json');terminal(C/'tool-terminal.json')
assert cap['tags']['candidate']['engine_sha256']==sha(B/'rook2-exact') and gate['capture_sha256']==sha(C/'capture.json') and gate['report_sha256']==sha(C/'report.md')
assert gate['promotion_authorized'] is False and gate['cpu_neutrality_claim'] is False
for tag in ['control','candidate']:
 r=cap['tags'][tag];assert sha(Path(r['rlib']))==r['rlib_sha256'] and sha(C/(tag+'-probe'))==r['probe_sha256'] and sha(C/(tag+'-probe.rs'))==r['source_sha256']
summary={'status':'FUNCTIONAL_PASS_BACKEND_PARENT_DECISION_PENDING','source':plan['home_source'],'frozen_source':plan['frozen_source'],'source_graph_sha256':load(Path(plan['proposal'])/'prepared.json')['source_graph_sha256'],'source_files':105,'native_source_files':44,'tools_source_files':23,'cold_source_files':38,'native_units':163,'strict_replays':54,'wire_fixtures':8,'wire_searches':24,'diagnostic_units':188,'cases':7584,'operations':108,'whole_files':105,'duplicate_ids':0,'partial_files':0,'generic_sha256':sha(B/'rook2-exact'),'adapter_sha256':sha(D/'rook2-diag-exact'),'independent_sha256':sha(paths['reconciliation']/'independent-verification.json'),'codegen_capture_sha256':sha(C/'capture.json'),'codegen_gate_sha256':sha(C/'bounded-gate.json'),'codegen_report_sha256':sha(C/'report.md'),'codegen_material_risks':gate['material_risks'],'canonical_domain_audit_limit':plan['canonical_domain_audit_limit'],'source_stable':True,'compiler_and_settings_match':True,'all_original_expected_raw_actual_exits_reconciled':True,'native_reused':False,'native_source_fixes':False,'root_mutation':False,'cpu_pgo_profiler':False,'promotion_authorized':False,'all_native_jobs_terminal':True,'all_owned_processes_terminal':'actual final packaging terminal must be reported externally','preserved_failures':['preparation read lookup939ec4 exit1','codegen01f0038e exit1 thin-LTO probe linking','codegen reader d8c656 exit1 table extent analysis']}
write(HERE/'validation-summary.json',summary)
files={}
for directory in [HERE,paths['freeze'],paths['native-validation'],paths['strict-check'],paths['interruption-wire'],paths['diagnostic'],paths['reconciliation'],C]:
 for f in sorted(directory.rglob('*')):
  if f.is_file():files[str(f)]=sha(f)
write(HERE/'validation-file-manifest.json',files)
print(json.dumps({'status':summary['status'],'summary_sha256':sha(HERE/'validation-summary.json'),'manifest_sha256':sha(HERE/'validation-file-manifest.json'),'all_native_jobs_terminal':True}))
