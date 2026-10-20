"""SOURCE/INPUT PROVENANCE ONLY: never invokes compiler, engine or test binaries."""
from pathlib import Path
import collections,difflib,hashlib,json,os,re,shutil,tarfile
HERE=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence');ROOT=Path('/home/legolas/rook2')
OLD=E/'complete117-ledger-test-validation-preparation-20261018'
NATIVE=Path('/home/legolas/rook2-work/imp2-activity-value-inputs-20261018-4ea01f85')
BUILD=E/'activity-value-inputs-generic-build-20261018-01'
NV=E/'activity-value-inputs-native-validation-20261018-01'
REG=E/'activity-value-inputs-regression-20261018-01'
IND=E/'activity-value-inputs-independent-preparation-20261018-01'
PGO=E/'activity-value-inputs-pgo-cpu-reconciliation-20261018-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def terminal(path):
 d=load(path);assert d['actual_tool_terminal_observed'] and d['exit_code']==0 and d['initial_chunk_id'] and d['terminal_chunk_id'];return d

def archive(path,entries):
 with tarfile.open(path,'w:gz') as t:
  for name,source in entries.items():t.add(source,arcname=name,recursive=False)
 with tarfile.open(path,'r:gz') as t:
  actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
 expected={name:sha(source) for name,source in entries.items()};assert actual==expected
 return dict(path=str(path),sha256=sha(path),members=actual,reopened_members_exact=True)

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 assert not (HERE/'validation-plan.json').exists(),'preserve existing attempt; no overwrite'
 old=load(OLD/'validation-plan.json');br=load(BUILD/'receipt.json');nr=br['source_sha256_before'];tools=br['tool_sha256_before']
 assert len(nr)==46 and len(tools)==23 and nr==br['source_sha256_after'] and tools==br['tool_sha256_after']
 assert br['mode']=='generic' and br['pgo']['mode']=='none' and br['rust_flags']==['-C','target-cpu=x86-64']
 assert all(sha(NATIVE/name)==sha(BUILD/'source-before'/name)==h for name,h in (nr|tools).items())
 assert sha(BUILD/'rook2-exact')==br['binary_output']['sha256']=='7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'
 baseline=load(E/'complete117-pgo-use-build-20261018/receipt.json')
 assert tools==baseline['tool_sha256_before']==old['tools_sha256']
 native_delta=[name for name in nr if nr[name]!=baseline['source_sha256_before'][name]]
 assert native_delta==['src/activity.rs']
 assert [name for name,h in nr.items() if old['native_sha256'][name]!=h]==['src/activity.rs']
 cold=old['diagnostic_sha256'];assert len(cold)==43
 assert all(sha(ROOT/name)==h for name,h in cold.items()),'root frontend must equal exact old43'
 full=nr|tools|cold;assert len(full)==112
 source=HERE/'frozen-source';source.mkdir()
 for name,h in full.items():
  origin=(ROOT if name in cold else NATIVE)/name;dest=source/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,dest);assert sha(dest)==h
 assert {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}==set(full)
 tests_native=sum((source/name).read_text().count('#[test]') for name in nr if name.endswith('.rs'))
 tests_diag=sum((source/name).read_text().count('#[test]') for name in cold if name.endswith('.rs'))
 assert (tests_native,tests_diag)==(178,209)
 diff=''.join(difflib.unified_diff((E/'complete117-pgo-use-build-20261018/source-before/src/activity.rs').read_text().splitlines(keepends=True),(source/'src/activity.rs').read_text().splitlines(keepends=True),fromfile='a/src/activity.rs',tofile='b/src/activity.rs'))
 (HERE/'activity-only-from-6a.patch').write_text(diff)
 native=load(NV/'result.json');ind=load(IND/'independent-verification.json')
 assert native['complete'] and native['total_tests']==178 and native['tests']['lib']['passed']==176 and native['tests']['dev']['passed']==2 and native['source_and_tools_unchanged']
 assert ind['complete'] and ind['native_tests']==178 and ind['strict54_original_checkReplay'] and ind['source46_tools23_archive69_equal'] and ind['engine_sha256']==br['binary_output']['sha256']
 frozen_units={}
 for name,row in native['tests'].items():
  assert sha(row['executable'])==row['sha256'];f=HERE/'reuse-unit-bin'/name/'unit-exact';f.parent.mkdir(parents=True);shutil.copy2(row['executable'],f);assert sha(f)==row['sha256'];frozen_units[name]=str(f)
 actual=[BUILD/'tool-terminal.json',NV/'tool-terminal.json',REG/'tool-terminal.json',IND/'tool-terminal.json']
 actuals={str(p):terminal(p) for p in actual}
 pilot=load(PGO/'independent-reconciliation.json');assert pilot['complete'] and pilot['advance_rule_satisfied']
 assert sha(PGO/'independent-reconciliation.json')=='99dd586c3cdf06fcb91420287af703c1c10c46de54c133c16ca3027e11991127'
 terminal(PGO/'tool-terminal.json');terminal(E/'activity-value-inputs-pgo-cpu-pilot-20261018-01/tool-terminal.json')
 fixtures=old['fixtures'];inventory=[];ids=set();ops=collections.Counter();allcases=[]
 for filename,h in fixtures.items():
  assert sha(filename)==h;doc=load(filename);header={k:v for k,v in doc.items() if k!='cases'}
  assert header==old['fixture_headers'][filename] and len(doc['cases'])==old['fixture_counts'][filename]
  cases=[]
  for index,case in enumerate(doc['cases']):
   assert case['id'] not in ids;ids.add(case['id']);op=case['request']['operation'];ops[op]+=1
   item=dict(index=index,id=case['id'],operation=op,case_sha256=hashlib.sha256(json.dumps(case,sort_keys=True,separators=(',',':')).encode()).hexdigest());cases.append(item);allcases.append(item)
  inventory.append(dict(path=filename,sha256=h,header=header,cases=cases,count=len(cases)))
 assert len(fixtures)==115 and len(ids)==len(allcases)==7673 and len(ops)==117 and dict(ops)==old['operation_case_counts']
 write('whole-fixture-inventory.json',inventory)
 js=load(OLD/'public-js-import-closure.json');assert js['all_actual_literal_relative_imports_resolved']
 for filename,row in js['files'].items():assert sha(filename)==row['sha256']
 write('public-js-import-closure.json',js)
 # Preserve old failed histories as old proof pins; don't copy/rewrite obsolete execution authority.
 deps=[OLD/'validation-plan.json',OLD/'final-closure.json',OLD/'validation-summary.json',OLD/'public-js-import-closure.json',OLD/'stage.py',OLD/'guard.py',OLD/'reconcile.py',OLD/'record_case.py',OLD/'finalize.py',E/'complete117-functional-failure-review-20261018/failure-closure.json',E/'complete117-ledger-test-proposal-20261018/source-proof.json',E/'complete117-ledger-test-proposal-20261018/test-only.patch',BUILD/'receipt.json',BUILD/'archive-receipt.json',BUILD/'rook2-exact',NV/'result.json',IND/'independent-verification.json',REG/'result.json',REG/'wire/receipt.json',PGO/'independent-reconciliation.json',PGO/'tool-terminal.json',E/'activity-value-inputs-pgo-cpu-pilot-20261018-01/tool-terminal.json']+actual
 deps += [Path(x) for x in js['files']]
 deps += [Path('/home/legolas/king-spec/conformance/profiling')/x for x in ['workloads.json','replay-oracle.json']]
 deps += [Path('/usr/bin')/x for x in ['rustc','cargo','node','python3']]
 for d in [NV,REG]:deps += [f for f in d.iterdir() if f.is_file() and f.suffix in ['.json','.stdout','.stderr']]
 deps += [f for f in (REG/'wire').rglob('*.raw')]
 deps=list(dict.fromkeys(deps));pins={str(p):sha(p) for p in deps}
 graph=hashlib.sha256(json.dumps(full,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 harness={name:sha(HERE/name) for name in ['guard.py','stage.py','record_case.py','reconcile.py','finalize.py']}
 output={key:str(HERE/name) for key,name in [('freeze','execution-freeze'),('diagnostic','diagnostic'),('diagnostic-build','diagnostic-build'),('reconciliation','reconciliation')]}
 output.update({'generic-build':str(BUILD),'native-validation':str(NV),'strict-check':str(REG),'interruption-wire':str(REG/'wire')})
 plan={'status':'SOURCE_PREPARED_HOLD_NATIVE_EXECUTION','execution_authorized':False,'source_graph_sha256':graph,'source_sha256':full,'native_sha256':nr,'tools_sha256':tools,'diagnostic_sha256':cold,'frozen_source':str(source),'home_source':'/home/legolas/rook2-work/imp2-activity-complete117-diagnostic-20261018-0c2a731e','root_cold_source':str(ROOT/'diagnostic'),'harness_sha256':harness,'fixtures':fixtures,'fixture_headers':old['fixture_headers'],'fixture_counts':old['fixture_counts'],'operation_case_counts':dict(ops),'immutable_dependencies':pins,'output':output,'TMPDIR':'/home/legolas/rook2-build-tmp','affinity':[0,1,2,3,4,5,8,9,10,11,12,13],'expected':dict(source_files=112,native_files=46,tools_files=23,cold_files=43,native_tests_reused=178,native_lib_tests_reused=176,native_dev_tests_reused=2,strict_replays_reused=54,wire_fixtures_reused=8,wire_searches_reused=24,diagnostic_tests=209,cases=7673,operations=117,whole_files=115),'native_reference':{'crate_source':str(NATIVE),'build_receipt':str(BUILD/'receipt.json'),'image':str(BUILD/'rook2-exact'),'image_sha256':br['binary_output']['sha256'],'native_result':str(NV/'result.json'),'frozen_unit_images':frozen_units,'independent':str(IND/'independent-verification.json'),'actual_terminals':[str(p) for p in actual]},'pgo_advancement_reference':{'independent':str(PGO/'independent-reconciliation.json'),'independent_sha256':sha(PGO/'independent-reconciliation.json'),'actual_terminal':str(PGO/'tool-terminal.json'),'parent_acceptance_required':True},'canonical_domain_audit_limit':old['canonical_domain_audit_limit'],'runtime_overlap_disclosure':'Preparation only; parent may archive/commit closed trial evidence concurrently. No CPU conclusion or native launch here.'}
 write('validation-plan.json',plan)
 write('execution-clearance.json',dict(authorized=False,scope='activity-value-inputs-complete117-untimed-diagnostic',source_graph_sha256=graph,plan_sha256=sha(HERE/'validation-plan.json'),conflicting_cpu_windows_closed=False,parent_advancement_acceptance=None,timing_pgo_profiler_authorized=False,note='HOLD: parent must accept this concrete harness and bind advancement decision before any stage launch'))
 write('source-proof.json',dict(native46_equals_exact_verified_generic=True,tools23_equals_exact_verified_generic=True,root_cold43_equals_old117_plan=True,only_native_delta_from_6a=native_delta,no_pawn_fusion=True,source_files=112,test_declarations=dict(native=tests_native,diagnostic=tests_diag),actual_native_reuse_terminals=actuals))
 source_archive=archive(HERE/'source-112.tar.gz',{name:source/name for name in full})
 official_archive=archive(HERE/'official-inputs-115.tar.gz',{name.lstrip('/'):Path(name) for name in fixtures})
 # A lean snapshot of exact immutable proof/runner/raw inputs; runtime executables
 # stay externally byte-pinned, so the archive is not a toolchain installation.
 snapshot=HERE/'input-snapshot';snapshot.mkdir();snapshot_entries={}
 for filename,h in pins.items():
  origin=Path(filename)
  if filename.startswith('/usr/bin/') or origin==BUILD/'rook2-exact':continue
  dest=snapshot/filename.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,dest);assert sha(dest)==h;snapshot_entries[filename.lstrip('/')]=dest
 input_archive=archive(HERE/'proof-runner-raw-inputs.tar.gz',snapshot_entries)
 write('archive-verification.json',dict(source=source_archive,official_inputs=official_archive,proof_runner_raw_inputs=input_archive,external_runtime_and_image_pins={k:v for k,v in pins.items() if k.startswith('/usr/bin/') or k==str(BUILD/'rook2-exact')}))
 assert all(sha(NATIVE/name)==h for name,h in (nr|tools).items()) and all(sha(ROOT/name)==h for name,h in cold.items())
 assert all(sha(filename)==h for filename,h in pins.items())
 write('prepared.json',dict(status='SOURCE_INPUT_AND_HARNESS_PREPARED_NATIVE_HOLD',source_graph_sha256=graph,plan_sha256=sha(HERE/'validation-plan.json'),source_files=112,native=46,tools=23,cold=43,cases=7673,operations=117,whole_files=115,diagnostic_tests_unrun=209,native178_strict54_wire8_reused=True,source_proof_sha256=sha(HERE/'source-proof.json'),archives_verified=True,originals_unchanged=True,stage_execution_authorized=False,harness_sha256=harness))
 print(json.dumps(dict(source_graph_sha256=graph,source_files=112,whole_files=115,operations=117,cases=7673,native178_reused=True,fresh209DIAG_unrun=True,native_execution_authorized=False)))
if __name__=='__main__':main()
