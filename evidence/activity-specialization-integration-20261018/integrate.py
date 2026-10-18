#!/usr/bin/env python3
"""Adopt exact measured private activity specialization; no trial timing transfer."""
import hashlib,json,shutil,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PROTO=Path('/tmp/imp2-activity-specialization-20261018')
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 controls=ROOT/'evidence/production-eval-kernels-use-build-20261018/receipt.json'
 old=json.loads(controls.read_text());before=source_snapshot(ROOT)
 assert before==old['source_sha256_before']==old['source_sha256_after']
 pilot=ROOT/'evidence/pgo-activity-specialization-cpu-pilot-20261018'
 analysis=json.loads((pilot/'analysis.json').read_text())
 assert json.loads((pilot/'tool-terminal.json').read_text())['exit_code']==0
 assert analysis['complete'] and analysis['lifetimes_independently_reconciled']==60
 assert all(c['ratio']<1 for c in analysis['cases'])
 build=ROOT/'evidence/pgo-activity-specialization-use-build-20261018/receipt.json'
 candidate=json.loads(build.read_text());source=source_snapshot(PROTO)
 assert source==candidate['source_sha256_before']==candidate['source_sha256_after']
 assert [n for n in before if before[n]!=source[n]]==['src/activity.rs']
 check=ROOT/'evidence/pgo-activity-specialization-use-check-20261018/identity.json'
 assert json.loads(check.read_text())['native_artifact_sha256']==candidate['binary_output']['sha256']
 shutil.copy2(PROTO/'src/activity.rs',ROOT/'src/activity.rs')
 after=source_snapshot(ROOT);assert after==source
 record=dict(status='Exact measured private activity source integrated; canonical checks/build/profile remain separate',before=before,after=after,modified_existing_files=['src/activity.rs'],pilot_analysis_sha256=sha(pilot/'analysis.json'),candidate_build_receipt_sha256=sha(build),candidate_check_sha256=sha(check),driver_sha256=sha(Path(__file__)),scope='Only static private piece-kind traversal/scoring. Position160/Node176, ownership, arithmetic, chronology, marks, counters, reset/interruption and all semantic N/R charges unchanged. Trial timing does not identify or qualify the new canonical artifact.')
 with (OUT/'source-integration.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
 print(json.dumps(dict(integrated=True,native_source_files=len(after),changed=['src/activity.rs'])))
if __name__=='__main__':main()
