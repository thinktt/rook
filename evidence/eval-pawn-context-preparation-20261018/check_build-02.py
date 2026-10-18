#!/usr/bin/env python3
"""Freeze candidate and regress54; reuse the exact already-validated control image."""
import hashlib,json,os,shutil,signal,subprocess,sys
from pathlib import Path
PREP=Path(__file__).resolve().parent
ROOT=PREP.parents[1]
PROTO=Path('/tmp/imp2-eval-pawn-context-20261018')
OUT=ROOT/'evidence/eval-pawn-context-check-20261018-02'
BUILD=ROOT/'evidence/eval-pawn-context-build-20261018-02'
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def run(argv,stem):
 out,err=OUT/(stem+'.stdout'),OUT/(stem+'.stderr')
 with out.open('xb') as o,err.open('xb') as e:
  child=subprocess.Popen(argv,cwd=ROOT,stdout=o,stderr=e,start_new_session=True)
  try:child.wait(timeout=900)
  except BaseException:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=5)
   raise
 return dict(command=argv,exit_code=child.returncode,stdout_sha256=sha(out),stderr_sha256=sha(err))
def main():
 OUT.mkdir()
 prepared=json.loads((PREP/'prepared.json').read_text())
 native_path=PREP/'native-verification.json';native=json.loads(native_path.read_text())
 assert native['complete'] and native['inputs_stable'] and native['units']['rook2']['passed']==132
 diagnostic=ROOT/'evidence/diagnostic-eval-pawn-context-20261018'
 assert json.loads((diagnostic/'tool-terminal.json').read_text())['exit_code']==0
 diagnostic_identity=json.loads((diagnostic/'identity.json').read_text())
 assert diagnostic_identity['cases']==4177 and diagnostic_identity['units']==70
 assert diagnostic_identity['native_build_reference_sha256']==sha(BUILD/'receipt.json')
 assert native['source_before']==native['source_after']==prepared['variant_source_sha256']==source_snapshot(PROTO)
 # Reuse the identical frozen control whose complete54 replay already passed.
 prior=ROOT/'evidence/activity-specialization-check-20261018/verification.json';old=json.loads(prior.read_text())
 control=old['candidate'];control_build=ROOT/'evidence/activity-specialization-build-20261018'
 assert old['complete'] and control['cases']==54
 assert sha(control_build/'rook2-exact')==control['artifact_sha256']=='c946104a2ab1a4aa1a441b93406f8de591e42321277b519c8fed5478094ce5d2'
 assert sha(control_build/'receipt.json')==control['build_receipt_sha256']
 assert old['source_before']==old['source_after']==prepared['baseline_source_sha256']==source_snapshot(ROOT)
 control_replay=prior.parent/'candidate-replay.stdout';assert sha(control_replay)==control['replay']['stdout_sha256']
 control_report=json.loads(control_replay.read_text());assert control_report['status']=='pass' and len(control_report['results'])==54
 build=json.loads((BUILD/'receipt.json').read_text())
 assert build['outcome']=='build-succeeded-with-stable-input-snapshot'
 assert build['source_sha256_before']==build['source_sha256_after']==source_snapshot(PROTO)
 frozen=BUILD/'rook2-exact';identity=sha(frozen)
 assert identity==build['binary_output']['sha256']
 archive_path=BUILD/'archive-receipt.json';archive_record=json.loads(archive_path.read_text())
 assert archive_record['verified_against_build_before_hashes'] and archive_record['binary_sha256']==identity
 assert sha(BUILD/archive_record['archive'])==archive_record['sha256']
 archive=dict(scope='Reuse exact prior verified archive; no duplicate archive mutation',exit_code=0,archive_receipt_sha256=sha(archive_path),archive_sha256=archive_record['sha256'])
 replay=run(['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--',str(frozen)],'candidate-replay')
 report=json.loads((OUT/'candidate-replay.stdout').read_text());assert replay['exit_code']==0 and report['status']=='pass' and len(report['results'])==54
 assert not (OUT/'candidate-replay.stderr').stat().st_size
 assert sha(frozen)==identity and source_snapshot(PROTO)==prepared['variant_source_sha256'] and source_snapshot(ROOT)==prepared['baseline_source_sha256']
 wire_out=ROOT/'evidence/eval-pawn-context-interruption-wire-20261018-02'
 wire=run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(frozen),'--output',str(wire_out)],'candidate-wire')
 wire_receipt=json.loads((wire_out/'receipt.json').read_text());assert wire['exit_code']==0 and wire_receipt['pass'] and len(wire_receipt['results'])==8
 assert wire_receipt['engine_sha256_before']==wire_receipt['engine_sha256_after']==identity
 assert sha(frozen)==identity and source_snapshot(PROTO)==prepared['variant_source_sha256'] and source_snapshot(ROOT)==prepared['baseline_source_sha256']
 write(OUT/'verification.json',dict(complete=True,candidate=dict(artifact_sha256=identity,cases=54,build_receipt_sha256=sha(BUILD/'receipt.json'),archive=archive,replay=replay),baseline=dict(**control,verification_reference=str(prior),verification_sha256=sha(prior),replay_path=str(control_replay),scope='Previously completed strict replay on the identical frozen control; no duplicate control execution'),units_verification_sha256=sha(native_path),diagnostic_identity_sha256=sha(diagnostic/'identity.json'),wire=wire,wire_receipt_sha256=sha(wire_out/'receipt.json'),source_before=prepared['variant_source_sha256'],source_after=source_snapshot(PROTO),driver_sha256=sha(Path(__file__)),scope='Finite generic shared evaluation/score/pawn observation regression after native134 and71-op component checks; no timing/PGO/adoption/qualification claim'))
 print(json.dumps(dict(complete=True,candidate_sha256=identity,candidate_replays=54,interruption_fixtures=8,control_replays_reused=54)),flush=True)
if __name__=='__main__':main()
