#!/usr/bin/env python3
"""Final identity after actual combined88 pipeline terminal; no engine work."""
from pathlib import Path
import datetime,hashlib,json,os,tarfile
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
plan=load(P/'plan.json');prep=load(P/'source-preparation.json');S=Path(plan['source_root']);O=E/'diagnostic-qtree-pawn-20261018';B=E/'diagnostic-qtree-pawn-build-20261018'
terminal=load(P/'20261018-actual-terminal.json');assert terminal['actual_exit_code']==0
pipe=load(P/'20261018-pipeline.json');assert pipe['complete'] and pipe['failure'] is None and all(s['exit_code']==0 for s in pipe['stages'])
identity=load(O/'identity.json');assert identity['cases']==6161 and identity['units']==133 and len(identity['operations'])==88 and identity['whole_fixture_files']==83 and identity['partial_files']==identity['duplicate_case_ids']==0
assert identity['independent_raw_response_equal']==6161 and identity['source_identity_stable']
for name,h in prep['full_source_sha256'].items():assert sha(S/name)==h
for name,h in plan['native_reuse_evidence_sha256'].items():assert sha(Path(name))==h
before,after=load(O/'inputs-before.json'),load(O/'inputs-after.json');assert all(before[k]==after[k] for k in after) and all(sha(Path(p))==h for p,h in before['dependencies'].items())
br=load(B/'receipt.json');assert br['source_identity_unchanged'] and br['tool_identity_unchanged'] and br['cargo_config_unchanged'] and br['pgo']['mode']=='none'
assert sha(B/'rook2-diag-exact')==br['binary_output']['sha256']==identity['adapter_sha256']
for name,manifest in [('prepared-source-closure.tar.gz',prep['full_source_sha256']),('prepared-adapter.tar.gz',prep['adapter_source_sha256'])]:
 with tarfile.open(P/name,'r:gz') as t:actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
 assert actual==manifest
ar=load(B/'archive-receipt.json');assert sha(B/ar['archive'])==ar['sha256'] and ar['binary_sha256']==identity['adapter_sha256']
with tarfile.open(B/ar['archive'],'r:gz') as t:actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
assert actual==prep['adapter_source_sha256']
known={str(P/n) for n in ['pipeline.py','run.py','record_case.py','reconcile.py']};known.update([str(B/'rook2-diag-exact'),str(O/'unit-bin/rook2-diag-exact')]);active=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
 try:
  argv=[x.decode(errors='replace') for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
  if any(x in known or x.startswith(str(S/'target')) or x.startswith(str(S/'diagnostic/target')) or x==str(S/'diagnostic/Cargo.toml') for x in argv):active.append(dict(pid=int(proc.name),argv=argv,affinity=sorted(os.sched_getaffinity(int(proc.name)))))
 except OSError:pass
assert not active
(O/'final-process-check.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_live_processes=active,all_owned_jobs_terminal=True,helper_affinity=sorted(os.sched_getaffinity(0))),indent=2)+'\n')
report=f"""All133 DIAG unit tests and6,161 unique original official cases passed across88 operations and83 whole files. Original run.mjs plus the literal raw recorder was used. Independent reconciliation checked every original request/expected response against both raw output and official actual response, with each actual child exit and signal, exact whole-file headers/counts, no partials/duplicates, and stable source/tool/dependency/image identities. The10 Q-tree cases include46 node records/92 trace events/49 actual evaluation stages. No combined validation failure or source fix occurred.

Frozen combined source: {S}. Frozen adapter SHA256: {identity['adapter_sha256']}. Native43/tools23 are exact corrected Qtree02; cold31 combines promoted root87 pawn_subtotals with the deterministic two-parent main merge and unchanged Qtree rights/EP visibility/parser/sink. The97-file closure, frontend31 and83 whole official inputs were archived before compilation, and the generic adapter build has its independent frozen pre-build source archive. Source graph and patches are in evidence/combined-qtree-pawn-proposal-20261018.

Native145, original strict54/eight-wire/24searches on exactfed8a40a artifact were reused by reference to final351d0d1d identity, not rerun or rebuilt. The original62538 failure, H193 test-only correction and bounded NoTrace codegen gate are preserved and bound. Default local frame+32bytes remains an explicit performance risk, with no CPU-neutrality claim. No ordinary binary build/replay, standalone86 run, PGO, CPU timing or profiler occurred here. All helpers/adapter children used0-5,8-13; raw receipts retain actual affinity. Actual pipeline terminal and zero owned live processes are bound separately.

Parent owns source review, root promotion and final integrated-artifact qualification. Root87 and previous proposals/evidence remain unchanged. Normal/High requested; actual speed readback unavailable.
"""
(O/'report.md').write_text(report)
final=dict(exit_code=0,complete=True,pipeline_actual_terminal=terminal,all_owned_jobs_terminal=True,owned_live_processes=0,identity_sha256=sha(O/'identity.json'),report_sha256=sha(O/'report.md'),final_process_check_sha256=sha(O/'final-process-check.json'),build_receipt_sha256=sha(B/'receipt.json'),source_graph_sha256=plan['source_graph_sha256'],native_reused_binary_sha256=plan['inherited_native_binary_sha256'],finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'tool-terminal.json').write_text(json.dumps(final,indent=2)+'\n')
for root in [P,B,O]:
 files=sorted(p for p in root.rglob('*') if p.is_file() and p!=root/'output-sha256.json')
 (root/'output-sha256.json').write_text(json.dumps({str(p.relative_to(root)):sha(p) for p in files},indent=2)+'\n')
print(json.dumps(dict(complete=True,cases=6161,units=133,operations=88,adapter_sha256=identity['adapter_sha256'],identity_sha256=sha(O/'identity.json'),report_sha256=sha(O/'report.md'),tool_terminal_sha256=sha(O/'tool-terminal.json'),owned_live_processes=0)))
