from pathlib import Path
import hashlib,json,tarfile,os,datetime
E=Path('/home/legolas/rook2/evidence');OUT=Path(__file__).parent;V=E/'ordered-q-seeded103-combined-validation-20261018';F=E/'ordered-q-seeded103-combined-proposal-20261018';P=E/'ordered-q-seeded103-combined-validation-preparation-20261018'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
deps={}
def add(p,h=None):
 p=Path(p);assert p.is_absolute();actual=sha(p)
 if h is not None:assert actual==h,(str(p),h,actual)
 deps[str(p)]=actual;return actual
# Exact whole-source archive member hashes; no executable or engine invocation.
def archive(p,mapping,expected=None):
 add(p,expected)
 with tarfile.open(p) as t:
  files=[x for x in t.getmembers() if x.isfile()];assert len(files)==len(mapping)
  actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in files}
 assert actual==mapping
 return len(mapping)
variants={};receipts={};sourceproof={}
for label,dirname,want,validation,count in [
 ('baseline','admission-combined95-native-build-20261018','6e7b29358eb3774f578308f79a2e83b20587e7bd5cdacae1ff762764e7b11ec5','admission-combined95-native-validation-20261018',151),
 ('combined','ordered-q-seeded103-combined-generic-build-20261018','1befaa6d9c439d3d806e6e189a27756ab86f4c5b5ce3b74f59ed302d98ee5c0d','ordered-q-seeded103-combined-validation-20261018',158)]:
 b=E/dirname;r=read(b/'receipt.json');nv=E/validation;u=read(nv/'native-verification.json');receipts[label]=r
 variants[label]={'path':str(b/'rook2-exact'),'sha256':add(b/'rook2-exact',want)}
 add(b/'receipt.json');add(b/'archive-receipt.json');assert r['binary_output']['sha256']==want and r['outcome']=='build-succeeded-with-stable-input-snapshot' and r['cargo_exit_code']==0
 native=r['source_sha256_before'];tools=r['tool_sha256_before'];assert len(native)==43 and len(tools)==23
 assert r['source_sha256_after']==native and r['tool_sha256_after']==tools
 for rel,h in dict(native,**tools).items():add(b/'source-before'/rel,h)
 ar=read(b/'archive-receipt.json');archive(b/ar['archive'],dict(native,**tools),ar['sha256'])
 assert u['complete'] and u['failure'] is None and sum(x['passed'] for x in u['units'].values())==count
 assert u['source_before']==native and u['source_after']==native
 add(nv/'native-verification.json')
 for key,value in u['units'].items():add(nv/'unit-bin'/key/'rook2-exact',value['binary_sha256'])
 for i,stage in enumerate(u['stages']):
  assert stage['exit_code']==0
  stem=['unit-build','rook2-tests','rook2-dev-tests'][i]
  add(nv/(stem+'.stdout'),stage['stdout_sha256']);add(nv/(stem+'.stderr'),stage['stderr_sha256'])
 for tool in ['rustc','cargo']:add('/usr/bin/'+tool,r['toolchain'][tool+'_executable_sha256'])
 sourceproof[label]={'source43':native,'tools23':tools,'native_units':count,'build_receipt':str(b/'receipt.json'),'archive':str(b/ar['archive'])}
base,combined=receipts['baseline'],receipts['combined']
for key in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain','build_effective_environment']:
 assert base[key]==combined[key],key
assert base['mode']=='generic' and base['pgo']['mode']=='none'
assert sourceproof['baseline']['tools23']==sourceproof['combined']['tools23']
assert base['source_sha256_before']['Cargo.toml']==combined['source_sha256_before']['Cargo.toml']
assert base['source_sha256_before']['Cargo.lock']==combined['source_sha256_before']['Cargo.lock']
normalize=lambda r:[s.replace(r['crate'],'SOURCE').replace(r['target_directory'],'TARGET') for s in r['argv']]
assert normalize(base)==normalize(combined)
# Accepted original95 closure and its actual terminals/failure, read-only exact hashes.
old=E/'diagnostic-admission-combined95-02-20261018';fi=read(old/'final-identity.json');assert fi['native_binary_sha256']==variants['baseline']['sha256']
assert (fi['native_units'],fi['diagnostic_units'],fi['cases'],fi['operations'],fi['whole_fixture_files'])==(151,149,7393,95,89)
assert fi['partial_files']==fi['duplicate_ids']==0 and fi['raw_original_expected_and_actual_exit_reconciled']==7393
for rel in ['final-identity.json','final-closure.json','report.md','finalizer-actual-terminal.json','owned-process-closure.json']:add(old/rel)
for path,h in fi['evidence_sha256'].items():add(path,h)
check=E/'admission-combined95-check-20261018';strict=read(check/'independent-verification.json');assert strict['status']=='pass' and strict['strict_replays']==54 and strict['interruption_fixtures']==8 and strict['interruption_searches']==24 and strict['artifact_sha256']==variants['baseline']['sha256']
for rel in ['input-closure.json','independent-verification.json','tool-terminal.json','reconcile-tool-terminal.json','identity.json','profile-all.stdout','profile-all.stderr','wire.stdout','wire.stderr']:add(check/rel)
assert read(check/'tool-terminal.json')['exit_code']==0
add(E/'admission-combined95-interruption-wire-20261018/receipt.json')
for path,h in read(check/'input-closure.json').items():
 # Temp execution source may be removed later; exact66 frozen build snapshots already bind identical native/tool bytes.
 if not path.startswith('/tmp/'):add(path,h)
oldprep=E/'diagnostic-admission-combined95-preparation-02-20261018';sp=read(oldprep/'source-preparation.json');archive(oldprep/sp['source_closure_archive'],sp['full_source_sha256'],sp['source_closure_archive_sha256']);add(oldprep/'exact-inputs.tar.gz',sp['exact_inputs_archive_sha256'])
add(oldprep/'whole-fixture-case-map.json');add(oldprep/'fixture-inventory.json');add(E/'admission-combined95-native-validation-20261018/final-native-identity.json')
# Current103 entire frozen source/whole-input archive and actual original independent verification.
prepared=read(F/'prepared.json')
for rel,h in prepared['artifacts'].items():add(F/rel,h)
add(F/'prepared.json');add(F/'review.md');add(F/'source-tool-terminal.json')
manifest=read(F/'source-manifest.json')['files'];assert len(manifest)==102
archive(F/'source-102.tar.gz',manifest,prepared['source_archive_sha256'])
paths=read(P/'paths.json')
for rel,h in manifest.items():add(Path(paths['frozen_proposal'])/rel,h)
recon=read(V/'reconciliation/independent-verification.json');assert recon['status']=='pass' and recon['all_raw_expected_and_actual_equal'] and recon['all_native_child_exits_confirmed']
assert (recon['native_units'],recon['diagnostic_units'],recon['strict_replays'],recon['interruption_fixtures'],recon['interruption_searches'],recon['diagnostic_cases'],recon['diagnostic_operations'],recon['whole_fixture_files'])==(158,175,54,8,24,7514,103,100)
assert recon['native_artifact_sha256']==variants['combined']['sha256'] and recon['source_sha256']==manifest
for rel in ['native-actual-terminal.json','generic-actual-terminal.json','strict-wire-actual-terminal.json','diagnostic-actual-terminal.json','independent-actual-terminal.json','final-packaging-actual-terminal.json']:
 t=read(V/rel);assert t['exit_code']==0 and t['actual_tool_terminal_observed'];add(V/rel)
for rel in ['report.md','final-summary.json','final-packaging.json','source-final-stability.json','owned-process-closure.json','supplemental-metadata-manifest.json','supplemental-metadata.tar.gz','final-packaging-attempt01-actual-terminal.json','finalize.py','finalize-02.py','finalizer-02-delta.patch','reconciliation/independent-verification.json','reconciliation/raw-case-sha256.json','reconciliation/case-reconciliation.json','ordinary-check/identity.json','ordinary-check/inputs-before.json','ordinary-check/inputs-after.json','ordinary-check/tool-terminal.json','interruption-wire/receipt.json','codegen/report.md','codegen/inputs.json','codegen/inputs-after.json','codegen/actual-terminals.json','codegen/output-hashes.json','codegen/default-false-analysis.json','codegen/default-false-register-referents.json','codegen/source-anchors.json','codegen/probes.json','codegen/focused-analysis.json']:add(V/rel)
for path,h in read(V/'supplemental-metadata-manifest.json').items():add(path,h)
for rel in ['plan.json','diagnostic-native-binding.json','execution-input-closure.json','execution-input-closure.tar.gz','execution-clearance.json','functional-overlap.json','reconcile.py']:add(P/rel)
for path,h in read(V/'ordinary-check/inputs-before.json')['dependencies'].items():add(path,h)
plan=read(P/'plan.json');assert len(plan['fixtures'])==100
for path,h in plan['fixtures'].items():add(path,h)
# Bounded codegen accepted by parent; this immutable review is not performance evidence.
judgment=E/'ordered-q-seeded103-combined-parent-review-20261018/codegen-judgment.json';add(judgment)
D=E/'ordered-q-seeded103-combined-diagnostic-20261018';DB=E/'ordered-q-seeded103-combined-diagnostic-build-20261018'
for p in [D/'verification.json',D/'conformance.stdout',D/'conformance.stderr',DB/'receipt.json',DB/'archive-receipt.json',DB/'rook2-diag-exact']:add(p)
proof={'complete':True,'source_builds':sourceproof,'compiler_settings_equal':{k:base[k] for k in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain','build_effective_environment']},'normalized_build_argv':normalize(base),'exact_tools23_equal':True,'source43_diff':[n for n in sorted(base['source_sha256_before']) if base['source_sha256_before'][n]!=combined['source_sha256_before'][n]],'original95_scope':{'native':151,'DIAG':149,'operations':95,'cases':7393,'whole_files':89,'strict':54,'wire':8,'wire_searches':24},'combined_scope':{'native':158,'DIAG':175,'operations':103,'cases':7514,'whole_files':100,'strict':54,'wire':8,'wire_searches':24},'own_pgo_or_profile_transfer':False,'static_review_only_no_neutrality':True,'engine_or_profiler_runs':0,'preserved_failures':['95 originalDIAG01 ENOSPC; exactretry02 passed','103 metadata-finalizer01 fa17d2 exit1; correctedfinalizer02 9c44a2 exit0'],'actual_stage_closures_bound':True,'affinity':sorted(os.sched_getaffinity(0))}
write(OUT/'gate-proof.json',proof);add(OUT/'gate-proof.json');add(Path(__file__).resolve())
gate={'complete':True,'variants':variants,'dependencies':dict(sorted(deps.items())),'scope':'Matched GENERIC root95 versus frozen103bits cumulative interaction gate; preparation only, no CPU/engine runs. Parent owns pilot launch after every sibling actual closure. Not a promotion or neutrality claim.','material_codegen_risk':'Stats/outcomes+8 vs95; defaultQ+226/frame-32 andordinary+144 vs102; forceddefaultfixedobject+178/sameframe, no inferred dynamic cost equivalence; full evaluation scope retained.','native_source_changes':proof['source43_diff']}
assert list(gate['variants'])==['baseline','combined']
write(OUT/'regression-gate.json',gate)
# Rehash immutable dependencies once after publication. No receipt in the gate is written afterwards.
for path,h in gate['dependencies'].items():assert sha(path)==h,path
write(OUT/'gate-preparation-receipt.json',{'complete':True,'gate_sha256':sha(OUT/'regression-gate.json'),'dependencies':len(deps),'variants':variants,'proof_sha256':sha(OUT/'gate-proof.json'),'all_dependencies_stable_before_after':True,'native_build_test_engine_codegen_profiler_runs':0,'actual_terminal':'outer tool terminal must be observed separately','no_gate_dependency_will_be_updated':True})
print(json.dumps(read(OUT/'gate-preparation-receipt.json'),indent=2))
