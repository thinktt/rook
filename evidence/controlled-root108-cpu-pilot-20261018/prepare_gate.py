from pathlib import Path
import hashlib,json,tarfile,os,ast
E=Path('/home/legolas/rook2/evidence');OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
assert not (OUT/'launch-authorization.json').exists()
for name in ['driver.py','reconcile.py','prepare_gate.py']:ast.parse((OUT/name).read_text(),filename=name)
deps={}
def add(p,want=None):
 p=Path(p);assert p.is_absolute();actual=sha(p)
 if want is not None:assert actual==want,(str(p),want,actual)
 deps[str(p)]=actual;return actual
def archive(p,mapping,want=None):
 add(p,want)
 with tarfile.open(p) as t:
  fs=[m for m in t.getmembers() if m.isfile()];assert len(fs)==len(mapping)
  assert {m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in fs}==mapping
# Control provenance is the immutable already-closed103 gate: retains some prior95
# anchors as history only. Control variant here is always103, never95.
old=E/'ordered-q-seeded103-combined-cpu-pilot-20261018';oldgate=read(old/'regression-gate.json')
assert oldgate['complete'] and oldgate['variants']['combined']['sha256']=='1befaa6d9c439d3d806e6e189a27756ab86f4c5b5ce3b74f59ed302d98ee5c0d'
for path,h in oldgate['dependencies'].items():add(path,h)
add(old/'regression-gate.json');add(old/'gate-proof.json');add(old/'gate-preparation-receipt.json');add(old/'gate-actual-terminal.json')
variants={};receipts={};sourceproof={}
for label,dirname,want,nativefiles,units in [
 ('baseline','ordered-q-seeded103-combined-generic-build-20261018','1befaa6d9c439d3d806e6e189a27756ab86f4c5b5ce3b74f59ed302d98ee5c0d',43,158),
 ('combined','controlled-root108-generic-build-20261018','96dc74f18083d3b9732ff1760031adee5b0774af6c2ae207c501f288557e4f75',44,163)]:
 b=E/dirname;r=read(b/'receipt.json');receipts[label]=r
 variants[label]={'path':str(b/'rook2-exact'),'sha256':add(b/'rook2-exact',want)}
 add(b/'receipt.json');add(b/'archive-receipt.json')
 assert r['binary_output']['sha256']==want and r['outcome']=='build-succeeded-with-stable-input-snapshot' and r['cargo_exit_code']==0
 native=r['source_sha256_before'];tools=r['tool_sha256_before'];assert len(native)==nativefiles and len(tools)==23
 assert r['source_sha256_after']==native and r['tool_sha256_after']==tools
 for rel,h in dict(native,**tools).items():add(b/'source-before'/rel,h)
 ar=read(b/'archive-receipt.json');archive(b/ar['archive'],dict(native,**tools),ar['sha256'])
 for tool in ['rustc','cargo']:add('/usr/bin/'+tool,r['toolchain'][tool+'_executable_sha256'])
 # Actual runtime comparator/accounting source must match both build tool closures.
 for rel,h in tools.items():add(Path('/home/legolas/rook2')/rel,h)
 sourceproof[label]={'native_source_files':nativefiles,'native_source':native,'tools23':tools,'native_units':units,'build_receipt':str(b/'receipt.json'),'archive':str(b/ar['archive'])}
a,b=receipts['baseline'],receipts['combined']
for key in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain','build_effective_environment']:assert a[key]==b[key],key
assert a['mode']=='generic' and a['pgo']['mode']=='none' and sourceproof['baseline']['tools23']==sourceproof['combined']['tools23']
normalize=lambda r:[x.replace(r['crate'],'SOURCE').replace(r['target_directory'],'TARGET') for x in r['argv']]
assert normalize(a)==normalize(b)
delta=sorted(n for n in a['source_sha256_before'].keys()|b['source_sha256_before'].keys() if a['source_sha256_before'].get(n)!=b['source_sha256_before'].get(n))
assert delta==['src/lib.rs','src/root_schedule.rs','src/timed.rs']
P=E/'controlled-root108-validation-preparation-20261018';plan=read(P/'plan.json');summary=read(P/'validation-summary.json');closure=read(P/'final-closure.json')
assert (summary['native_units'],summary['strict_replays'],summary['wire_fixtures'],summary['wire_searches'],summary['diagnostic_units'],summary['cases'],summary['operations'],summary['whole_files'])==(163,54,8,24,188,7584,108,105)
assert summary['generic_sha256']==variants['combined']['sha256'] and summary['source_stable'] and summary['all_original_expected_raw_actual_exits_reconciled']
assert closure['all_owned_processes_terminal'] and closure['source_stable'] and closure['no_source_fixes'] and closure['no_root_mutation']
for n in ['validation-summary.json','validation-file-manifest.json','final-closure.json','finalizer-actual-terminal.json','report.md','finalize.py','plan.json','stage.py','guard.py','reconcile.py','record_case.py','execution-clearance.json']:add(P/n)
assert sha(P/'validation-summary.json')==closure['summary_sha256'] and sha(P/'validation-file-manifest.json')==closure['validation_file_manifest_sha256'] and sha(P/'report.md')==closure['report_sha256']
# Verify all retained original raw records and frozen validation/codegen inputs NOW;
# gate pins their immutable file manifest afterward rather than re-reading every
# case during each timing sample. The native samples still each use strict oracle.
rawproof=read(P/'validation-file-manifest.json')
for path,h in rawproof.items():assert sha(path)==h,path
for path,h in plan['source_sha256'].items():
 add(Path(plan['frozen_source'])/path,h);add(Path(plan['home_source'])/path,h)
F=Path(plan['output']['freeze']);archive(F/'source-105.tar.gz',plan['source_sha256'])
for path,h in read(F/'dependencies.json').items():add(path,h)
add(F/'dependencies.json');archive(F/'input-closure.tar.gz',{p.lstrip('/'):h for p,h in read(F/'dependencies.json').items()})
for key in ['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation']:
 t=read(Path(plan['output'][key])/'tool-terminal.json');assert t['actual_tool_terminal_observed'] and t['exit_code']==0;add(Path(plan['output'][key])/'tool-terminal.json')
N=Path(plan['output']['native-validation']);v=read(N/'verification.json');assert v['complete'] and v['failure'] is None and sum(x['passed'] for x in v['units'].values())==163
add(N/'verification.json')
for name,item in v['units'].items():add(N/'unit-bin'/name/'unit-exact',item['binary_sha256']);add(N/(name+'-tests.stdout'))
for stage,stem in zip(v['stages'],['unit-build','rook2-tests','rook2-dev-tests']):
 assert stage['exit_code']==0 and stage['actual_child_return_observed'];add(N/(stem+'.stdout'),stage['stdout_sha256']);add(N/(stem+'.stderr'),stage['stderr_sha256'])
S=Path(plan['output']['strict-check']);add(S/'verification.json');add(S/'strict54.stdout');add(S/'strict54.stderr');add(S/'wire.stdout');add(S/'wire.stderr')
W=Path(plan['output']['interruption-wire']);wr=read(W/'receipt.json');assert wr['pass'] and len(wr['results'])==8 and sum(len(x['searches']) for x in wr['results'])==24
add(W/'receipt.json')
for r in wr['results']:
 assert r['exit_code']==r['observed_exit_code']==0 and r['complete_streams']
 for name,x in r['raw'].items():add(W/r['id']/(name+'.raw'),x['sha256'])
D=Path(plan['output']['diagnostic']);DB=Path(plan['output']['diagnostic-build']);iv=read(Path(plan['output']['reconciliation'])/'independent-verification.json')
assert iv['status']=='pass' and iv['source_stable'] and iv['all_raw_expected_and_actual_equal'] and iv['all_native_child_exits_confirmed']
assert (iv['native_units'],iv['diagnostic_units'],iv['strict_replays'],iv['interruption_fixtures'],iv['interruption_searches'],iv['diagnostic_cases'],iv['diagnostic_operations'],iv['whole_fixture_files'])==(163,188,54,8,24,7584,108,105)
for n in ['verification.json','conformance.stdout','conformance.stderr','rook2-diag-tests.stdout','unit-build.stdout','unit-build.stderr']:add(D/n)
dv=read(D/'verification.json');add(D/'unit-bin/rook2-diag/unit-exact',dv['units']['rook2-diag']['binary_sha256'])
for n in ['receipt.json','archive-receipt.json','rook2-diag-exact']:add(DB/n)
dbr=read(DB/'receipt.json');dar=read(DB/'archive-receipt.json');archive(DB/dar['archive'],dbr['source_sha256_before']|dbr['tool_sha256_before'],dar['sha256'])
for n in ['independent-verification.json','raw-case-sha256.json','case-reconciliation.json']:add(Path(plan['output']['reconciliation'])/n)
C=E/'controlled-root108-codegen-02-20261018'
for n in ['report.md','bounded-gate.json','capture.json','commands.json','retry-authorization.json','tool-terminal.json','active-host-scope.json','selected-type-layouts.json','recursive-owner-comparison.json','recursive-call-abi-windows.json','recursive-reference-provenance.json','q-jump-table-referents.json','native-production-owner-delta.json','analysis-reader-failure01.json','capture.py','control-probe.rs','candidate-probe.rs']:add(C/n)
for n in ['capture.py','commands.json','tool-terminal.json','control-probe-compile.stdout','control-probe-compile.stderr']:add(E/'controlled-root108-codegen-20261018'/n)
judgment=E/'controlled-root108-combined-parent-review-20261018/backend-cost-judgment.json';add(judgment,'30358eb7f00d0976e3162a32dfc0b1606a9ea95b7008575bbe78351bfb785533')
j=read(judgment);assert j['status']=='ACCEPTED_FOR_MATCHED_GENERIC_CPU_EXPERIMENT_ONLY' and j['cpu_execution_requires_parent_separate_gate'] and not j['promotion_authorized'] and not j['neutrality_claim']
assert j['report_sha256']==sha(C/'report.md') and j['bounded_gate_sha256']==sha(C/'bounded-gate.json') and j['validation_summary_sha256']==sha(P/'validation-summary.json') and j['final_closure_sha256']==sha(P/'final-closure.json')
for n in ['driver.py','reconcile.py','README.md','prepare_gate.py']:add(OUT/n)
# Exact current six-case original oracle and accounting/measurement helpers are
# already tools23-bound; independently pin released input files too.
for n in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']:add(Path('/home/legolas/king-spec/conformance/profiling')/n)
proof={'complete':True,'preparation_only':True,'variants':variants,'source_builds':sourceproof,'compiler_settings_equal':{k:a[k] for k in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain','build_effective_environment']},'normalized_build_argv':normalize(a),'native_source_changes':delta,'runtime_helpers_tools23_equal':True,'control_scope':{'native':158,'DIAG':175,'strict':54,'wire':8,'wire_searches':24,'operations':103,'cases':7514,'whole_files':100},'candidate_scope':{'native':163,'DIAG':188,'strict':54,'wire':8,'wire_searches':24,'operations':108,'cases':7584,'whole_files':105},'candidate_all_retained_validation_files_reverified_at_preparation':len(rawproof),'raw_sample_bytes_runtime_check':'every future timed lifetime uses strict original comparator; raw validation manifest pinned','backend_judgment':str(judgment),'actual_stage_terminals_bound':True,'separate_parent_launch_required':True,'launch_authorization_file_absent':True,'native_or_engine_or_cpu_or_profiler_runs':0,'preserved_failures':['codegen01f0038e thinLTO standalone probe linker failure','analysis-reader d8c656 incorrect second-table extent; native tag0..6 bound; no source repair'],'no_neutrality_or_adoption_claim':True,'affinity':sorted(os.sched_getaffinity(0))}
write(OUT/'gate-proof.json',proof);add(OUT/'gate-proof.json')
gate={'complete':True,'variants':variants,'dependencies':dict(sorted(deps.items())),'scope':'PREPARATION ONLY exact103bits1bef versus shared-root10896dc generic matched pilot. Twelve excluded warmups+48 measured lifetimes across six established cases; strict original oracle/direct wait4. Separate explicit parent launch authorization still required. No PGO/profiler/promotion/neutrality.','material_codegen_risk':'Actual active-Host root outlined GOT helper/aggregate ABI/identity lookup cost; enclosing frame-32B is not prediction; separate forcedNoHost+80B distinct.','native_source_changes':delta,'launch_guard':'Absent launch-authorization.json; must bind gate/driver hashes and explicit all-native/Git/large-hash/archive/109-codegen closure.'}
write(OUT/'regression-gate.json',gate)
for path,h in gate['dependencies'].items():assert sha(path)==h,path
write(OUT/'gate-preparation-receipt.json',{'complete':True,'preparation_only':True,'gate_sha256':sha(OUT/'regression-gate.json'),'driver_sha256':sha(OUT/'driver.py'),'reconciler_sha256':sha(OUT/'reconcile.py'),'dependencies':len(deps),'variants':variants,'proof_sha256':sha(OUT/'gate-proof.json'),'all_dependencies_stable_before_after':True,'native_build_test_engine_codegen_cpu_profiler_runs':0,'separate_parent_launch_required':True,'launch_authorization_file_absent':True,'actual_terminal':'outer tool terminal must be observed separately','no_gate_dependency_will_be_updated':True})
print(json.dumps(read(OUT/'gate-preparation-receipt.json'),indent=2))
