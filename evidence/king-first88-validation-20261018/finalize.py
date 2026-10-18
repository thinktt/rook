#!/usr/bin/env python3
import hashlib,json,re,tarfile
from pathlib import Path
E=Path(__file__).resolve().parents[1]
P=E/'king-first88-preparation-20261018';V=E/'king-first88-validation-20261018';B=E/'king-first88-build-20261018';C=E/'king-first88-check-02-20261018';D=E/'king-first88-diagnostic-20261018';DB=E/'king-first88-diagnostic-build-20261018'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def archive(path):
 with tarfile.open(path,'r:gz') as t:return {m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
def main():
 prep=load(P/'prepared.json');source=Path(prep['path']);base=Path(prep['baseline']);old=load(E/'bounded-reply-king-first-preparation-20261018/prepared.json')
 current={k:sha(source/k) for k in prep['full_source_sha256']};assert current==prep['full_source_sha256']
 expected=load(E/'combined-qtree-pawn-proposal-20261018/proposal-source-sha256.json');assert all(sha(base/k)==h for k,h in expected.items());assert [k for k in expected if current[k]!=expected[k]]==['src/movegen.rs']
 assert expected['src/movegen.rs']==old['baseline_source_sha256']['src/movegen.rs'] and current['src/movegen.rs']==old['variant_source_sha256']['src/movegen.rs']
 assert archive(P/'prepared-source-closure.tar.gz')==current
 br=load(B/'receipt.json');nr=load(V/'native-verification.json');ci=load(C/'identity.json');cr=load(C/'independent-verification.json');di=load(D/'identity.json');dv=load(D/'verification.json');dbr=load(DB/'receipt.json')
 assert br['source_sha256_before']==br['source_sha256_after']==nr['source_before']==nr['source_after']==ci['source_before']==ci['source_after']==prep['variant_source_sha256']
 assert br['tool_sha256_before']==br['tool_sha256_after']==prep['tool_source_sha256']
 assert nr['complete'] and nr['inputs_stable'] and cr['status']=='pass' and cr['native_tests']==147 and cr['strict_replays']==54 and cr['interruption_fixtures']==8 and cr['interruption_searches']==24
 for name,count in [('rook2',145),('rook2-dev',2)]:
  text=(V/(name+'-tests.stdout')).read_text();assert len(re.findall(r'^test .* \.\.\. ok$',text,re.M))==count;assert nr['units'][name]['passed']==count;assert sha(V/'unit-bin'/name/'rook2-exact')==nr['units'][name]['binary_sha256']
 assert di['cases']==6161 and di['units']==133 and len(di['operations'])==88 and di['whole_fixture_files']==83 and di['partial_files']==di['duplicate_case_ids']==0 and di['independent_raw_response_equal']==6161
 assert dbr['source_sha256_before']==dbr['source_sha256_after']==prep['adapter_source_sha256'];assert dv['complete'] and dv['inputs_stable']
 assert sha(B/'rook2-exact')==br['binary_output']['sha256']==ci['native_artifact_sha256']==cr['artifact_sha256']==di['native_binary_sha256']
 assert sha(DB/'rook2-diag-exact')==dbr['binary_output']['sha256']==di['adapter_sha256'];assert len(re.findall(r'^test .* \.\.\. ok$',(D/'unit-tests.stdout').read_text(),re.M))==133
 for directory in [B,DB]:
  ar=load(directory/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and sha(directory/ar['archive'])==ar['sha256'];rr=load(directory/'receipt.json');assert ar['binary_sha256']==rr['binary_output']['sha256']
  archived=archive(directory/ar['archive']);assert all(archived[k]==h for k,h in rr['source_sha256_before'].items())
 terminals=[B/'tool-terminal.json',V/'native-tool-terminal.json',C/'tool-terminal.json',C/'reconcile-tool-terminal.json',D/'tool-terminal.json',D/'reconcile-tool-terminal.json']
 for path in terminals:
  t=load(path);assert t['actual_tool_terminal_observed'] and t['exit_code']==0
 summary=dict(status='Frozen88 plus exact accepted king-first only; all fresh untimed validation passed',source_root=str(source),source_map=prep['full_source_sha256'],only_changed_path='src/movegen.rs',baseline_movegen_exact_original_king_baseline=True,accepted_king_movegen_exact=True,native_artifact_sha256=sha(B/'rook2-exact'),diagnostic_artifact_sha256=sha(DB/'rook2-diag-exact'),native_tests=147,diagnostic_unit_tests=133,strict_replays=54,interruption_fixtures=8,interruption_searches=24,diagnostic_cases=6161,diagnostic_operations=88,whole_fixture_files=83,all_raw_cases_independently_reconciled=True,terminal_records={str(p.relative_to(E.parent)):load(p) for p in terminals},preserved_failures=[str(P/'preparation-failure-01.json'),str(E/'king-first88-check-20261018/tool-terminal.json')],no_native_source_fixes=True,all_owned_processes_terminal=True,closure_basis='All external actual terminal exits observed; drivers synchronously awaited every native unit/build/replay/wire/DIAG child; raw6161 exits independently reconciled. No detached jobs launched.',scope='Untimed housekeeping0-5,8-13 only; no CPU timing/PGO/profiler/static scans; root unchanged; parent owns adoption.',preparation_sha256=sha(P/'prepared.json'),patch_sha256=sha(P/'king-first.patch'),prepared_archive_sha256=sha(P/'prepared-source-closure.tar.gz'),native_build_receipt_sha256=sha(B/'receipt.json'),native_verification_sha256=sha(V/'native-verification.json'),strict_identity_sha256=sha(C/'identity.json'),strict_independent_sha256=sha(C/'independent-verification.json'),diagnostic_identity_sha256=sha(D/'identity.json'),diagnostic_case_reconciliation_sha256=sha(D/'case-reconciliation.json'),finalizer_sha256=sha(Path(__file__)))
 with (V/'validation-summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
 dirs=[P,V,B,C,D,DB,E/'king-first88-check-20261018',E/'king-first88-interruption-wire-02-20261018',E/'king-first88-diagnostic-preparation-20261018']
 files={str(p.relative_to(E.parent)):sha(p) for d in dirs for p in sorted(d.rglob('*')) if p.is_file() and p.name!='file-manifest.json'}
 with (V/'file-manifest.json').open('x') as f:json.dump(files,f,indent=2);f.write('\n')
 print(json.dumps(dict(summary=str(V/'validation-summary.json'),summary_sha256=sha(V/'validation-summary.json'),file_manifest_sha256=sha(V/'file-manifest.json'),native_artifact_sha256=summary['native_artifact_sha256'],diagnostic_artifact_sha256=summary['diagnostic_artifact_sha256'],all_owned_processes_terminal=True)))
if __name__=='__main__':main()
