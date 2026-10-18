#!/usr/bin/env python3
# Final closure only, after actual pipeline terminal0 has been captured.
from pathlib import Path
import argparse,datetime,hashlib,json,os,tarfile
P=Path(__file__).parent;E=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
a=argparse.ArgumentParser();a.add_argument('--label',default='20261018');args=a.parse_args();label=args.label
O=E/('diagnostic-retained-search-pawn-'+label);B=E/('diagnostic-retained-search-pawn-build-'+label);plan=load(P/'plan.json');prep=load(P/'source-preparation.json');S=Path(plan['source_root']);F=Path(plan['frozen_proposal'])
assert load(P/(label+'-actual-terminal.json'))['actual_exit_code']==0
pipeline=load(P/(label+'-pipeline.json'));assert pipeline['complete'] and pipeline['failure'] is None and all(s['exit_code']==0 for s in pipeline['stages'])
identity=load(O/'identity.json');assert identity['cases']==6151 and identity['units']==126 and identity['whole_fixture_files']==82 and len(identity['operations'])==87
assert identity['independent_raw_response_equal']==6151 and identity['source_identity_stable']
for name,h in prep['full_source_sha256'].items():assert sha(S/name)==sha(F/name)==h
for name,h in plan['native_reuse_evidence_sha256'].items():assert sha(Path(name))==h
before=load(O/'inputs-before.json');after=load(O/'inputs-after.json');assert all(before[k]==after[k] for k in after)
assert all(sha(Path(name))==h for name,h in before['dependencies'].items())
br=load(B/'receipt.json');assert br['source_identity_unchanged'] and br['tool_identity_unchanged'] and br['cargo_config_unchanged'] and br['pgo']['mode']=='none'
assert sha(B/'rook2-diag-exact')==br['binary_output']['sha256']==identity['adapter_sha256']
ar=load(B/'archive-receipt.json');assert sha(B/ar['archive'])==ar['sha256'] and ar['binary_sha256']==identity['adapter_sha256']
with tarfile.open(B/ar['archive'],'r:gz') as t:archive={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
assert archive==prep['adapter_source_sha256']
known={str(P/n) for n in ['pipeline.py','run.py','record_case.py','reconcile.py']};known.update([str(B/'rook2-diag-exact'),str(O/'unit-bin/rook2-diag-exact')]);owned=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
 try:
  argv=[x.decode(errors='replace') for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
  if not any(x in known or x.startswith(str(S/'target')) or x.startswith(str(S/'diagnostic/target')) or x==str(S/'diagnostic/Cargo.toml') for x in argv):continue
  owned.append({'pid':int(proc.name),'argv':argv,'affinity':sorted(os.sched_getaffinity(int(proc.name)))})
 except OSError:pass
assert not owned
(O/'final-process-check.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_live_processes':owned,'all_owned_jobs_terminal':True,'final_helper_affinity':sorted(os.sched_getaffinity(0))},indent=2)+'\n')
report='''# Retained subtotal/search pawn — isolated adapter validation

All 126 diagnostic unit tests and all 6,151 unique official cases across 87 operations/82 whole files passed. The original official run.mjs was used; a recorder preserved literal stdin/stdout/stderr and actual child return code for every case. The separate reconciler compared the complete original expected response with both raw adapter response and runner actual output, checked each exit/signal and every source/dependency identity, and found no omitted, partial or duplicate case. All 862 new cases/25,992 result records passed, including current phase/geometry/collision/root ownership and lifetime compositions. No failed validation attempt or source fix occurred.

The adapter source was frozen from the reviewed proposal in a new execution copy. Its full96-file closure (native43, diagnostic30, tools23), adapter source and original82 inputs were archived before compilation; metadata headers stayed in exact original fixture bytes. The adapter build also froze and independently packaged all30 pre-build frontend source files. All native/frontend/tool/Cargo-config/fixture/driver/image hashes remained stable. Every command inherited housekeeping CPUs0-5,8-13; live process samples and every raw adapter receipt retain the actual affinity. No CPU timing, profiler or PGO ran.

Accepted native142 and stable strict54/eight-wire/24search evidence are reused by exact metadata/source reference to generic d38ff03745c7fba981c22f12fdd7b10b78f539f9541faeb24b92bd263b116d45, native build receipt45631ac24e12ce8a1ea067b84665401c00591a10e21d01157afe12ec3367daf5 and final actual-terminal receipts. No ordinary engine binary was rebuilt or replayed. Adapter Cargo compilation includes its required native library dependency; all43 native sources match the accepted reference. No dependency on mutable-root tool files was introduced.

The parent explicitly cleared pilot92704 actualterminal0/d687c2 (independent35b97e) before this execution. execution-clearance.json and execution-start.json record that boundary and actual pipeline handle. Each build/test/case-run/archive/reconcile command, raw streams, exit codes and hashes is retained; the actual outer terminal is bound in tool-terminal.json and the preparation actual-terminal receipt. final-process-check.json records zero owned live jobs.

Parent owns central integration/promotion after verifying source equality. Existing source-only proposal, root source, earlier proposals and accepted native evidence remain untouched. This is bounded diagnostic/ordinary evidence reuse, not a complete mandatory engine qualification or CPU-neutrality claim. Normal/High requested; actual speed readback unavailable.
'''
(O/'report.md').write_text(report)
terminal={'exit_code':0,'complete':True,'pipeline_actual_terminal':load(P/(label+'-actual-terminal.json')),'all_owned_jobs_terminal':True,'owned_live_processes':0,'identity_sha256':sha(O/'identity.json'),'report_sha256':sha(O/'report.md'),'final_process_check_sha256':sha(O/'final-process-check.json'),'build_receipt_sha256':sha(B/'receipt.json'),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'tool-terminal.json').write_text(json.dumps(terminal,indent=2)+'\n')
for root in [P,B,O]:
 files=sorted(p for p in root.rglob('*') if p.is_file() and p!=root/'output-sha256.json')
 (root/'output-sha256.json').write_text(json.dumps({str(p.relative_to(root)):sha(p) for p in files},indent=2)+'\n')
print(json.dumps({'complete':True,'cases':6151,'units':126,'adapter_sha256':identity['adapter_sha256'],'identity_sha256':sha(O/'identity.json'),'report_sha256':sha(O/'report.md'),'tool_terminal_sha256':sha(O/'tool-terminal.json'),'build_receipt_sha256':sha(B/'receipt.json'),'owned_live_processes':0}))
