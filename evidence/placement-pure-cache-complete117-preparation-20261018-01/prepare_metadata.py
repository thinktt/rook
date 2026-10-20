"""Source/input preparation only: no compiler, unit, engine or validation imports."""
from pathlib import Path
import collections,difflib,hashlib,json,os,shutil,tarfile,tempfile,uuid
HERE=Path(__file__).resolve().parent
E=Path('/home/legolas/rook2/evidence');ROOT=Path('/home/legolas/rook2')
OLD=E/'full-byte-pair-relations-complete117-preparation-20261018-01'
NATIVE=Path('/home/legolas/rook2-work/imp2-placement-pure-cache-20261018-x2gvi1c5')
BUILD=E/'placement-pure-cache-generic-build-20261018-01'
NV=E/'placement-pure-cache-native-validation-20261018-01'
REG=E/'placement-pure-cache-regression-20261018-01'
IND=E/'placement-pure-cache-independent-preparation-20261018-01'
PGO=None # future actual advancement path/hash remains unbound until parent pilot acceptance
PRO=E/'placement-pure-cache-proposal-20261018-01'
H=[0,1,2,3,4,5,8,9,10,11,12,13]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write(chr(10))
def terminal(path):
 d=load(path);assert d['actual_tool_terminal_observed'] is True and d['exit_code']==0
 chunk=d.get('terminal_chunk_id') or d.get('chunk_id');assert isinstance(chunk,str) and chunk.strip()
 return d

def archive(path,entries):
 assert not path.exists()
 with path.open('xb') as raw:
  with tarfile.open(fileobj=raw,mode='w:gz') as t:
   for name,source in entries.items():t.add(source,arcname=name,recursive=False)
 with tarfile.open(path,'r:gz') as t:
  rows=t.getmembers();assert len(rows)==len(entries) and all(m.isfile() for m in rows)
  actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in rows}
 expected={name:sha(source) for name,source in entries.items()};assert actual==expected
 return dict(path=str(path),sha256=sha(path),members=actual,reopened_members_exact=True)

def main():
 assert sorted(os.sched_getaffinity(0))==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 assert not (HERE/'validation-plan.json').exists(),'preserve existing attempt; no overwrite'
 old=load(OLD/'validation-plan.json');br=load(BUILD/'receipt.json');nr=br['source_sha256_before'];tools=br['tool_sha256_before']
 assert len(nr)==46 and len(tools)==23 and nr==br['source_sha256_after'] and tools==br['tool_sha256_after']
 assert br['mode']=='generic' and br['pgo']['mode']=='none' and br['rust_flags']==['-C','target-cpu=x86-64']
 assert all(sha(NATIVE/name)==sha(BUILD/'source-before'/name)==h for name,h in (nr|tools).items())
 image='a9472bd0484968e5ff3a0a657c4a9b28df1f0a775f3fc6fc1ee6db6eb2f4b6e0'
 assert sha(BUILD/'rook2-exact')==br['binary_output']['sha256']==image
 assert tools==old['tools_sha256']
 # Verify current fullbyte root and immutable accepted112 base; do not use mutable root at runtime.
 baseline={name:sha(ROOT/name) for name in old['source_sha256']}
 assert baseline==old['source_sha256'],'current root must equal accepted fullbyte112 basis'
 base=Path(old['frozen_source']);assert all(sha(base/name)==h for name,h in baseline.items())
 root_native={name:baseline[name] for name in old['native_sha256']}
 cold={name:baseline[name] for name in old['diagnostic_sha256']};assert len(cold)==43
 native_delta=[name for name in nr if nr[name]!=root_native[name]]
 assert sorted(native_delta)==['src/activity.rs','src/evaluator.rs','src/ordinary.rs','src/quiescence.rs','src/shelter.rs']
 assert all(nr[name]==root_native[name] for name in ['src/pawn_progress.rs','src/influence.rs','src/relation_table.rs','src/remembered.rs','src/position.rs'])
 full=nr|tools|cold;assert len(full)==112
 source=Path(tempfile.mkdtemp(prefix='imp2-placement-cache-complete117-frozen-20261018-',dir='/home/legolas/rook2-work'))
 for name,h in full.items():
  origin=(NATIVE if name in native_delta else base)/name
  dest=source/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,dest);assert sha(dest)==h
 assert {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}==set(full)
 tests_native=sum((source/name).read_text().count('#[test]') for name in nr if name.endswith('.rs'))
 tests_diag=sum((source/name).read_text().count('#[test]') for name in cold if name.endswith('.rs'))
 assert (tests_native,tests_diag)==(184,209)
 for name in native_delta:assert (ROOT/name).read_bytes()==(PRO/'basis'/name).read_bytes() and (source/name).read_bytes()==(PRO/'proposed'/name).read_bytes()
 shutil.copy2(PRO/'trial.patch',HERE/'native-only-from-root.patch')
 native=load(NV/'result.json');ind=load(IND/'independent-verification.json')
 assert native['complete'] and native['total_tests']==184 and native['tests']['lib']['passed']==182 and native['tests']['dev']['passed']==2 and native['source_and_tools_unchanged']
 assert ind['complete'] and ind['native_tests']==184 and ind['strict54_original_checkReplay'] and ind['source46_tools23_archive69_equal'] and ind['engine_sha256']==image
 assert ind['only_declared_placement_cache_sources_changed_vs_fullbyte_baseline'] and ind['influence_relation_pawn_and_remembered_unchanged']
 frozen_units={name:row['executable'] for name,row in native['tests'].items()}
 assert all(sha(path)==native['tests'][name]['sha256'] for name,path in frozen_units.items())
 actual=[BUILD/'tool-terminal.json',NV/'tool-terminal.json',REG/'tool-terminal.json',IND/'tool-terminal.json']
 actuals={str(p):terminal(p) for p in actual}
 assert sha(IND/'independent-verification.json')=='8d67299298e3f2d5ccbdeea615243fb9de2692153b4c2c4ae303c83b8a18e10e'
 # Future own-PGO pilot/acceptance are absent; no invented path/hash/terminal or immutable pin.
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
 deps=[OLD/name for name in ['validation-plan.json','public-js-import-closure.json','stage.py','guard.py','reconcile.py','record_case.py','finalize.py']]
 deps += [E/'activity-value-inputs-complete117-continuation02-20261018'/name for name in ['validation-summary.json','crate-tool-scope-correction.patch'] if (E/'activity-value-inputs-complete117-continuation02-20261018'/name).exists()]
 deps += [PRO/name for name in ['prepared.json','source-manifest.json','source-proof.json','trial.patch','test-declarations.json','source69.tar.gz','review.md','final-closure.json']]
 deps += [BUILD/'receipt.json',BUILD/'archive-receipt.json',BUILD/'rook2-exact',NV/'result.json',IND/'independent-verification.json',REG/'result.json',REG/'wire/receipt.json']+actual
 deps += [Path(path) for path in ind['dependencies']]
 deps += [Path(x) for x in js['files']]
 deps += [Path('/home/legolas/king-spec/conformance/profiling')/x for x in ['workloads.json','replay-oracle.json']]
 deps += [Path('/usr/bin')/x for x in ['rustc','cargo','node','python3']]
 deps=list(dict.fromkeys(deps));pins={str(p):sha(p) for p in deps}
 graph=hashlib.sha256(json.dumps(full,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 harness={name:sha(HERE/name) for name in ['guard.py','stage.py','record_case.py','reconcile.py','finalize.py']}
 output={key:str(HERE/name) for key,name in [('freeze','execution-freeze'),('diagnostic','diagnostic'),('diagnostic-build','diagnostic-build'),('reconciliation','reconciliation')]}
 output.update({'generic-build':str(BUILD),'native-validation':str(NV),'strict-check':str(REG),'interruption-wire':str(REG/'wire')})
 home='/home/legolas/rook2-work/imp2-placement-cache-complete117-diagnostic-20261018-'+uuid.uuid4().hex[:8];assert not Path(home).exists()
 plan={'status':'SOURCE_PREPARED_HOLD_NATIVE_EXECUTION','execution_authorized':False,'source_graph_sha256':graph,'source_sha256':full,'native_sha256':nr,'tools_sha256':tools,'diagnostic_sha256':cold,'diagnostic_crate_tools_sha256':{},'frozen_source':str(source),'home_source':home,'root_cold_source':str(source/'diagnostic'),'harness_sha256':harness,'fixtures':fixtures,'fixture_headers':old['fixture_headers'],'fixture_counts':old['fixture_counts'],'operation_case_counts':dict(ops),'immutable_dependencies':pins,'output':output,'TMPDIR':'/home/legolas/rook2-build-tmp','affinity':H,'expected':dict(source_files=112,native_files=46,tools_files=23,cold_files=43,native_tests_reused=184,native_lib_tests_reused=182,native_dev_tests_reused=2,strict_replays_reused=54,wire_fixtures_reused=8,wire_searches_reused=24,diagnostic_tests=209,cases=7673,operations=117,whole_files=115),'native_reference':{'crate_source':str(NATIVE),'build_receipt':str(BUILD/'receipt.json'),'image':str(BUILD/'rook2-exact'),'image_sha256':image,'native_result':str(NV/'result.json'),'frozen_unit_images':frozen_units,'independent':str(IND/'independent-verification.json'),'actual_terminals':[str(p) for p in actual]},'pgo_advancement_reference':{'independent':None,'independent_sha256':None,'actual_terminal':None,'parent_acceptance_required':True,'status':'UNBOUND: own-PGO use build/pilot not yet accepted; parent must bind real passed pilot path/hash/terminal plus immutable proof pins and refresh plan/prepared hashes before any execution clearance'},'canonical_domain_audit_limit':old['canonical_domain_audit_limit'],'runtime_overlap_disclosure':'Preparation source/hash/archive only. No CPU conclusion or native launch. All runtime inputs use frozen source rather than mutable root.','baseline_root_declared_revision':'c3fd806fa/fullbyte source112','baseline_source_sha256':baseline,'baseline_source_graph_sha256':old['source_graph_sha256']}
 write('validation-plan.json',plan)
 write('execution-clearance.json',dict(authorized=False,scope='placement-pure-cache-complete117-untimed-diagnostic',source_graph_sha256=graph,plan_sha256=sha(HERE/'validation-plan.json'),conflicting_cpu_windows_closed=False,parent_advancement_acceptance=None,timing_pgo_profiler_authorized=False,note='HOLD exact parent harness review and advancement acceptance; no native validation executed'))
 write('source-proof.json',dict(native46_equals_verified_cache_generic=True,tools23_equals_verified_cache_generic=True,root112_equals_accepted_fullbyte112=True,root_cold43_unchanged=True,only_native_delta_from_root=native_delta,no_pawn_fusion=True,fullbyte_root_replaced_only_by_five_frozen_cache_native_files=True,source_files=112,frozen_source=str(source),test_declarations=dict(native=tests_native,diagnostic=tests_diag),actual_native_reuse_terminals=actuals,maintenance_generator_outside_source112='scripts/generate_relation_table.py; not composed or required'))
 source_archive=archive(HERE/'source-112.tar.gz',{name:source/name for name in full})
 official_archive=archive(HERE/'official-inputs-115.tar.gz',{name.lstrip('/'):Path(name) for name in fixtures})
 write('archive-verification.json',dict(source=source_archive,official_inputs=official_archive,native_raw_proof_reused_by_original_path_pins=True))
 assert all(sha(NATIVE/name)==h for name,h in (nr|tools).items())
 assert all(sha(ROOT/name)==h for name,h in baseline.items())
 assert all(sha(filename)==h for filename,h in pins.items())
 write('prepared.json',dict(status='SOURCE_INPUT_AND_HARNESS_PREPARED_NATIVE_HOLD',source_graph_sha256=graph,plan_sha256=sha(HERE/'validation-plan.json'),source_files=112,native=46,tools=23,cold=43,cases=7673,operations=117,whole_files=115,diagnostic_tests_unrun=209,native184_strict54_wire8_reused=True,source_proof_sha256=sha(HERE/'source-proof.json'),archives_verified=True,originals_unchanged=True,stage_execution_authorized=False,harness_sha256=harness))
 commands={stage:['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/env','TMPDIR=/home/legolas/rook2-build-tmp','PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3',str(HERE/('stage.py' if stage in ['freeze','diag'] else stage+'.py'))]+([stage] if stage in ['freeze','diag'] else []) for stage in ['freeze','diag','reconcile','finalize']}
 write('commands.json',commands)
 print(json.dumps(dict(source_graph_sha256=graph,frozen_source=str(source),future_execution_source=home,source_files=112,whole_files=115,operations=117,cases=7673,native184_reused=True,fresh209DIAG_unrun=True,native_execution_authorized=False)))
if __name__=='__main__':main()
