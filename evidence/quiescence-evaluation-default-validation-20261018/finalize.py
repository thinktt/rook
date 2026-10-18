from pathlib import Path
import json,hashlib,os,datetime
V=Path(__file__).parent;E=V.parent;P=E/'quiescence-evaluation-default-proposal-20261018';B=E/'quiescence-evaluation-default-build-20261018';C=V/'codegen'
F=Path('/tmp/imp2-quiescence-evaluation-default-20261018-native-child');S=Path('/tmp/imp2-quiescence-evaluation-default-validation-20261018')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def write(p,obj):
 with p.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
expected=load(P/'proposal-source-sha256.json')
assert {k:sha(F/k) for k in expected}==expected
assert {k:sha(S/k) for k in expected}==expected
native=load(V/'native-verification.json');assert native['complete'] and native['inputs_stable'];assert native['units']['rook2']['passed']==140 and native['units']['rook2-dev']['passed']==2
assert load(V/'native-actual-terminal.json')['actual_exit_code']==0
receipt=load(B/'receipt.json');identity=sha(B/'rook2-exact');assert identity==receipt['binary_output']['sha256']=='d38ff03745c7fba981c22f12fdd7b10b78f539f9541faeb24b92bd263b116d45'
assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged'] and receipt['pgo']['mode']=='none'
for group in ['source_sha256_before','tool_sha256_before']:
 assert {k:sha(B/'source-before'/k) for k in receipt[group]}==receipt[group]
 assert {k:sha(S/k) for k in receipt[group]}==receipt[group]
archive=load(B/'archive-receipt.json');assert archive['verified_against_build_before_hashes'] and archive['binary_sha256']==identity and sha(B/archive['archive'])==archive['sha256'] and archive['files']==66
for target in ['rook2','rook2-dev']:assert sha(V/'unit-bin'/target/'rook2-exact')==native['units'][target]['binary_sha256']
check=load(V/'ordinary-check-02/identity.json');assert check['complete'] and check['inputs_stable'];assert check['strict_replays']==54 and check['interruption_fixtures']==8 and check['interruption_searches']==24
assert load(V/'strict-wire-retry-actual-terminal.json')['actual_exit_code']==0
wire=load(V/'interruption-wire-02/receipt.json');assert wire['pass'] and wire['engine_sha256_before']==wire['engine_sha256_after']==identity and wire['effective_affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
inputs=load(C/'inputs.json');after={}
for label,artifact in inputs['artifacts'].items():
 image=Path(artifact['binary']);build=Path(artifact['build']);assert sha(image)==artifact['binary_sha256'] and sha(build/'receipt.json')==artifact['receipt_sha256']
 for group in ['source_sha256','tool_source_sha256']:assert {k:sha(build/'source-before'/k) for k in artifact[group]}==artifact[group]
 after[label]={'binary_sha256':sha(image),'receipt_sha256':sha(build/'receipt.json'),'native_source_files':len(artifact['source_sha256']),'tool_source_files':len(artifact['tool_source_sha256'])}
write(C/'inputs-after.json',{'stable':True,'artifacts':after})
assert load(C/'focused-referents-and-default-gate.json')['gate']['strict54_and_wire_authorized_gate_met']
first=load(V/'strict-wire-first-actual-terminal.json');assert first['exit_code']==1 and first['source_equal'] and first['engine_equal'] and len(first['dependency_changes'])==1
change=next(iter(first['dependency_changes'].values()));assert sha(C/'focused-referents-and-default-gate.json')==change['before'] and sha(C/'focused-referents-deep.json')==change['after']
known={str(B/'rook2-exact'),str(V/'native_pipeline.py'),str(V/'check_native.py'),str(V/'ordinary-check/check.py'),str(V/'ordinary-check-02/check.py'),str(C/'capture.py'),str(C/'analyze.py'),str(C/'focused_referents.py')};owned=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
 try:
  args=[x.decode(errors='replace') for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
  if not any(a in known or a.startswith(str(S/'target')) or a==str(S/'Cargo.toml') or a.startswith(str(V/'unit-bin')) for a in args):continue
  owned.append({'pid':int(proc.name),'argv':args,'affinity':sorted(os.sched_getaffinity(int(proc.name)))})
 except OSError:pass
write(V/'final-process-check.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_live_processes':owned,'helper_affinity':sorted(os.sched_getaffinity(0)),'all_owned_tools_terminal':not owned})
assert not owned
record={'status':'native142/build/codegen and stable strict54/eight-wire retry passed; owned processes terminal','native_sha256':identity,'native_build_receipt_sha256':sha(B/'receipt.json'),'source_manifest_sha256':sha(P/'proposal-source-sha256.json'),'source_root':str(S),'frozen_proposal':str(F),'native_library_units':140,'development_units':2,'native_total_units':142,'strict_replays':54,'interruption_fixtures':8,'interruption_searches':24,'first_strict_wire_wrapper_exit':1,'first_wrapper_failure':'dependency instability: codegen gate metadata; all raw behavior searches passed','retry_actual_exit':0,'retry_all_stage_inputs_stable':True,'proposal_sources_unchanged':True,'codegen_artifacts_sources_stable':True,'default_full_impl_raw_bytes_restored':True,'default_inline_fast_scope_restored':True,'whole_visit_q_exact_equivalence_claim':False,'diagnostic_rerun':False,'diagnostic_owner':'Parent combined85 validation','cpu_measurements':0,'profiler_runs':0,'pgo_runs':0,'owned_live_processes':0,'final_process_check_sha256':sha(V/'final-process-check.json')}
write(V/'identity.json',record)
write(V/'tool-terminal.json',{'exit_code':0,'complete':True,'owned_live_processes':0,'native_actual_terminal':load(V/'native-actual-terminal.json'),'strict_wire_retry_actual_terminal':load(V/'strict-wire-retry-actual-terminal.json'),'identity_sha256':sha(V/'identity.json'),'report_sha256':sha(V/'report.md'),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
for root in [C,V]:
 files=sorted(p for p in root.rglob('*') if p.is_file() and p!=root/'output-sha256.json')
 write(root/'output-sha256.json',{str(p.relative_to(root)):sha(p) for p in files})
print(json.dumps({'complete':True,'native_sha256':identity,'build_receipt_sha256':sha(B/'receipt.json'),'identity_sha256':sha(V/'identity.json'),'report_sha256':sha(V/'report.md'),'tool_terminal_sha256':sha(V/'tool-terminal.json'),'codegen_report_sha256':sha(C/'report.md'),'owned_live_processes':0},indent=2))
