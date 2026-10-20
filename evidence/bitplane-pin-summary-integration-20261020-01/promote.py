#!/usr/bin/env python3
"""Promote only the exact tested two-file57 change after independently closed gates."""
import json,hashlib
from pathlib import Path
R=Path('/home/legolas/rook2'); E=R/'evidence'; P=Path(__file__).resolve().parent
W=Path('/home/legolas/rook2-work/imp2-bitplane-pin-summary-20261020-01')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def graph(m):return hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def terminal(p):
 d=load(p);assert d['actual_tool_terminal_observed'] and d['exit_code']==0
 assert d.get('terminal_chunk_id') or d.get('terminal_chunk')
def main():
 old=load(E/'tactical-check-mask-integration-20261020-01/source-promotion.json')['files_sha256']
 freeze=load(E/'bitplane-pin-summary-parent-review-20261020-01/source-freeze.json')
 expected={**old,**freeze['files']}
 assert len(old)==len(expected)==117 and graph(expected)=='a58e7cad979e4f17ea27bc412a5dbb6e6511fc814afd20fc9f8f1763726a17dd'
 changed=['src/attacks.rs','src/movegen.rs']
 assert sorted(k for k in expected if expected[k]!=old[k])==changed
 assert {k:sha(R/k) for k in old}==old,'Unexpected canonical source changes: stop without overwrite'
 assert {k:sha(W/k) for k in freeze['files']}==freeze['files']
 post=E/'bitplane-pin-summary-postuse-validation-preparation-20261020-01'
 assert load(post/'recheck-result.json')['complete'];terminal(post/'recheck-tool-terminal.json')
 con=E/'bitplane-pin-summary-conformance-preparation-20261020-01'
 assert load(con/'validation-summary.json')['all_original_raw_expected_actual_and_exits_reconciled'];terminal(con/'finalizer-tool-terminal.json')
 preg=E/'bitplane-pin-summary-pregate-20261020-01'
 checks=load(preg/'independent-raw-reconciliation.json')
 assert checks['complete'] and checks['independentGames']==12 and checks['independentSearches']==632
 assert checks['continuousSearches']==8 and checks['requiredControlChildren']==11 and checks['persistenceSearches']==3
 terminal(preg/'tool-terminal.json');terminal(preg/'reconcile-tool-terminal.json')
 review=load(E/'bitplane-pin-summary-production-review-20261020-01/review.json')
 assert review['verdict']=='SCOPED_PASS_UNDER_IMPORTED_POSITION_INVARIANT'
 for name,row in review['inputs'].items():assert sha(Path(name))==row['sha256']
 for name in changed:
  target=P/'source-before'/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:f.write((R/name).read_bytes())
 for name in changed:(R/name).write_bytes((W/name).read_bytes())
 actual={k:sha(R/k) for k in expected};assert actual==expected
 result={'complete':True,'experiment':57,'previous_retained':51,'source_graph_sha256':graph(actual),'native_source_graph_sha256':graph(freeze['files']),'files_sha256':actual,'changed_existing':changed,'added':[],'untouched_prior_files':115,'ordinary_image_sha256':'af849f920897ec1f174b16718be5d6886158913ee4819f84273f15bd8c23e5b8','diagnostic_image_sha256':'eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2','all_gates_reviewed_pass':True,'canonical_rebuild_claimed':False,'whole54_12_timing_pending':True,'final_qualification':False,'qualification_limits':['Finite conformance/pregate do not prove all production-domain compositions.','Canonical Position coherence premise imported; public stale mutations outside it.','Uncertified empty-source cutoff-hint composed admission remains unresolved.','No PMU/final performance or external3288 completion.']}
 with (P/'source-promotion.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k!='files_sha256'}))
if __name__=='__main__':main()
