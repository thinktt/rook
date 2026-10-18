import json,hashlib,os,re,datetime
from pathlib import Path
HERE=Path(__file__).parent
EV=HERE.parent
ROOT=EV.parent
SOURCE=Path('/tmp/imp2-quiescence-evaluation-validation-20261018')
PROPOSAL=Path('/tmp/imp2-quiescence-evaluation-20261018-native-child')
NATIVE=EV/'quiescence-evaluation-build-20261018'
DIAG=EV/'diagnostic-quiescence-evaluation-20261018'
DIAGBUILD=EV/'diagnostic-quiescence-evaluation-build-20261018'
PREP=EV/'diagnostic-quiescence-evaluation-preparation-20261018'
CHECK=EV/'quiescence-evaluation-check-20261018'
WIRE=EV/'quiescence-evaluation-interruption-wire-20261018'
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.sched_getaffinity(0)==HELPERS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def source_files(r):return {str(p.relative_to(r)):sha(p) for p in sorted(r.rglob('*')) if p.is_file() and not any(x in ['target','evidence','.git','__pycache__'] for x in p.relative_to(r).parts)}
expected=load(HERE/'proposal-full-source-sha256.json')
assert source_files(SOURCE)==source_files(PROPOSAL)==expected
native=load(HERE/'native-verification.json');pipeline=load(HERE/'native-pipeline.json');diag=load(DIAG/'verification.json');identity=load(DIAG/'identity.json');check=load(CHECK/'identity.json')
assert native['complete'] and native['inputs_stable'] and pipeline['complete']
assert native['units']['rook2']['passed']==140 and native['units']['rook2-dev']['passed']==2
assert diag['complete'] and diag['inputs_stable'] and identity['cases']==5187 and identity['units']==109
assert check['complete'] and check['inputs_stable'] and check['strict_replays']==54 and check['interruption_fixtures']==8 and check['interruption_searches']==24
assert load(HERE/'native-tool-terminal.json')['exit_code']==0 and load(DIAG/'tool-terminal.json')['exit_code']==0 and load(DIAG/'reconcile-terminal.json')['exit_code']==0 and load(CHECK/'tool-terminal.json')['exit_code']==0
plan=load(PREP/'plan.json');report=load(DIAG/'conformance.json');ids=[];ops=set();new_cases=0;new_records=0
assert len(plan['fixtures'])==78
for name,h in plan['fixtures'].items():
 p=Path(name);assert p.parent==Path('/home/legolas/king-spec/conformance/fixtures') and sha(p)==h
 data=load(p)
 for c in data['cases']:
  ids.append(c['id']);ops.add(c['request']['operation'])
  if c['request']['operation'] in plan['new_routes']:new_cases+=1;new_records+=len(c['expected']['results'])
assert len(ids)==len(set(ids))==len(report['results'])==5187 and len(ops)==84
assert set(ids)=={r['id'] for r in report['results']} and all(r['pass'] and r['exit']=={'code':0,'signal':None} for r in report['results'])
assert new_cases==466 and new_records==7500
native_sha=sha(NATIVE/'rook2-exact');diag_sha=sha(DIAGBUILD/'rook2-diag-exact')
assert native_sha==load(NATIVE/'receipt.json')['binary_output']['sha256']==check['native_artifact_sha256']
assert diag_sha==load(DIAGBUILD/'receipt.json')['binary_output']['sha256']==identity['adapter_sha256']
for build in [NATIVE,DIAGBUILD]:
 ar=load(build/'archive-receipt.json');assert sha(build/ar['archive'])==ar['sha256']
 assert ar['binary_sha256']==load(build/'receipt.json')['binary_output']['sha256']
# Restrict process inspection to our owned scripts/images/cwd, never interrupt others.
dirs=[HERE,NATIVE,DIAG,DIAGBUILD,PREP,CHECK,WIRE,SOURCE]
prefixes=[str(d)+'/' for d in dirs];active=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
 try:
  args=(proc/'cmdline').read_bytes().decode().split('\0');exe=os.readlink(proc/'exe');cwd=os.readlink(proc/'cwd')
  if any(exe.startswith(pre) or (cwd+'/').startswith(pre) or any(a.startswith(pre) for a in args) for pre in prefixes):active.append({'pid':int(proc.name),'exe':exe,'argv':[a for a in args if a]})
 except (OSError,UnicodeError):pass
write(HERE/'final-process-check.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_live_processes':active,'affinity':sorted(os.sched_getaffinity(0))})
assert not active,'owned processes remain'
receipt={'status':'all authorized untimed validation passed; owned processes stopped','native_sha256':native_sha,'diagnostic_sha256':diag_sha,'native_library_units':140,'development_units':2,'native_total_units':142,'diagnostic_units':109,'diagnostic_operations':84,'whole_official_fixture_files':78,'partial_fixture_files':0,'duplicate_case_ids':0,'diagnostic_cases':5187,'new_route_cases':466,'new_route_records':7500,'strict_replays':54,'interruption_fixtures':8,'interruption_searches':24,'proposal_sources_unchanged':True,'all_stage_inputs_stable':True,'owned_live_processes':0,'cpu_measurements':0,'pgo_runs':0,'profiler_runs':0,'complete_mandatory_qualification':False,'source_root':str(SOURCE),'frozen_proposal':str(PROPOSAL),'original_proposal_manifest_sha256':sha(EV/'quiescence-evaluation-proposal-20261018/proposal-source-sha256.json'),'native_build_receipt_sha256':sha(NATIVE/'receipt.json'),'diagnostic_build_receipt_sha256':sha(DIAGBUILD/'receipt.json'),'diagnostic_identity_sha256':sha(DIAG/'identity.json'),'strict_wire_identity_sha256':sha(CHECK/'identity.json'),'final_process_check_sha256':sha(HERE/'final-process-check.json')}
write(HERE/'identity.json',receipt)
text=f"""# Quiescence evaluation — completed untimed isolated validation

The frozen proposal passed 140 library and 2 development tests (142 total), 109 diagnostic tests, all 5,187 cases for 84 operations across 78 whole official fixture files, the original strict54 production replay, and eight interruption fixtures with 24 retained-process searches. The expansion contributes exactly 466 cases and 7,500 ordered result records. No partial fixture or duplicate case ID was selected. Native/adapter sources, bound dependencies and frozen image identities remained stable. No failure or source correction occurred.

Native generic SHA256: `{native_sha}`. Diagnostic generic SHA256: `{diag_sha}`. Both images were frozen immediately after actual successful build-helper return and before another build could overwrite their target paths; pre-build source archives and verified tar archives are retained in the respective build directories. Native test images and the diagnostic test image were also frozen before execution and their raw unit outputs retained.

The execution copy `/tmp/imp2-quiescence-evaluation-validation-20261018` exactly matches the frozen proposal full-source manifest before/after. The original `/tmp/imp2-quiescence-evaluation-20261018-native-child` and its proposal evidence remain unchanged. Current `/home/legolas/rook2/tools/build.py` performed generic `--bin rook2` and `--bin rook2-diag` builds. The explicit native path dependency is bound by the native build receipt/source map; the frontend's 29 manifest/lock/source files are separately archived and hashed. Root source/docs/other proposals were not edited.

The diagnostic preparation's plan independently inventories baseline82 plus both new whole official fixture files: every source index, case ID and operation, original top-level field names and exact official file hashes are recorded. The official runner received those original whole-file paths directly, preserving their metadata headers. Its complete JSON output and raw exits are reconciled independently against the inventory, all frozen images, unit counts and before/after source/dependency snapshots. The successful full response comparisons cover every field of all 7,500 new records; no summary/score-only comparison was substituted.

Evidence paths under `/home/legolas/rook2/evidence/`:

- `quiescence-evaluation-validation-20261018/`: native test artifacts/commands, actual native pipeline/terminal records, full proposal identity and this final reconciliation.
- `quiescence-evaluation-build-20261018/`: frozen ordinary engine, build/terminal/source/archive receipts.
- `diagnostic-quiescence-evaluation-preparation-20261018/`: original whole-fixture plan, frontend preparation/archive, bounded verifier and independent reconciler.
- `diagnostic-quiescence-evaluation-build-20261018/`: frozen diagnostic image and build/terminal/source/archive receipts.
- `diagnostic-quiescence-evaluation-20261018/`: 109-test frozen image/raw output, all 5,187 raw official case exits and complete reports, stable input snapshots, identity and actual terminal receipts.
- `quiescence-evaluation-check-20261018/`: original strict54 full stdout/semantic work/exit report, wire-driver outputs, source/dependency snapshots and actual terminal identity.
- `quiescence-evaluation-interruption-wire-20261018/`: eight fixture receipts and literal stdin/stdout/stderr chunks for all 24 searches, with clean observed exits.

All helpers/tests/engines were confined to housekeeping CPUs 0-5,8-13. The active-process sample records the strict driver and native engine with that exact mask. The final owned-process check is empty; all owned subprocesses had reached actual terminal return before this handoff. No CPU/cycle/retired-instruction timing, PGO, Callgrind or other profiler was run. This is semantic/component/ordinary-wire regression evidence, not CPU neutrality, gameplay, complete mandatory coverage or final qualification.
"""
(HERE/'report.md').write_text(text)
write(HERE/'tool-terminal.json',{'exit_code':0,'complete':True,'owned_processes_stopped':True,'identity_sha256':sha(HERE/'identity.json'),'report_sha256':sha(HERE/'report.md'),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
manifest={}
for d in dirs[:-1]:
 for f in sorted(d.rglob('*')):
  if f.is_file() and f.name!='output-sha256.json':manifest[str(f)]=sha(f)
write(HERE/'output-sha256.json',manifest)
print(json.dumps(receipt))
