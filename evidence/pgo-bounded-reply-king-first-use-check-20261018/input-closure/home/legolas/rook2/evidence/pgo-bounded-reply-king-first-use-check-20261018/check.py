#!/usr/bin/env python3
"""Exact own-PGO regression; no timing comparison. Frozen dependencies only."""
from pathlib import Path
import hashlib,json,subprocess,sys,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
VARIANT='king-first';SOURCE=Path('/tmp/imp2-bounded-reply-king-first85-20261018-zup28rca');EXPECTED_LIB=142
BUILD=ROOT/f'evidence/pgo-bounded-reply-{VARIANT}-use-build-20261018'
TRAIN=ROOT/f'evidence/pgo-bounded-reply-{VARIANT}-training-20261018'
NATIVE=ROOT/'evidence/bounded-reply-king-first-validation-20261018'
WIRE=ROOT/f'evidence/pgo-bounded-reply-{VARIANT}-interruption-wire-20261018'
SPEC=Path('/home/legolas/king-spec/conformance')
sys.path.insert(0,str(ROOT/'tools'));from build import source_snapshot

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def run(command,stem):
 out=OUT/(stem+'.stdout');err=OUT/(stem+'.stderr')
 with out.open('xb') as a,err.open('xb') as b:result=subprocess.run(command,cwd=ROOT,stdout=a,stderr=b)
 return dict(command=command,exit_code=result.returncode,stdout_sha256=sha(out),stderr_sha256=sha(err))

def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 build=load(BUILD/'receipt.json');training=load(TRAIN/'training.json');verified=load(TRAIN/'verification.json');native=load(NATIVE/'native-verification.json')
 assert native['complete'] and native['inputs_stable'] and native['units']['rook2']['passed']==EXPECTED_LIB and native['units']['rook2-dev']['passed']==2
 for q in [BUILD/'tool-terminal.json',TRAIN/'tool-terminal.json',TRAIN/'verify-tool-terminal.json']:
  assert load(q)['exit_code']==0
 assert verified['complete'] and training['complete'] and build['pgo']['mode']=='profile-use'
 before=source_snapshot(SOURCE)
 assert before==build['source_sha256_before']==build['source_sha256_after']==training['engine_source_sha256']==native['source_before']==native['source_after']
 expected_profile=sha(TRAIN/'merged.profdata');assert expected_profile==training['profile_sha256']==verified['merged_profile_sha256']
 assert build['pgo']['inputs_unchanged'] and build['pgo']['input_sha256_before']==build['pgo']['input_sha256_after']=={str(TRAIN/'merged.profdata'):expected_profile,str(TRAIN/'training.json'):sha(TRAIN/'training.json')}
 assert '-pgo-warn-missing-function' in ' '.join(build['rust_flags'])
 engine=BUILD/'rook2-exact';identity=sha(engine);assert identity==build['binary_output']['sha256']
 warning=(BUILD/'build.stderr').read_text().lower()
 assert all(x not in warning for x in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data'])
 paths=[Path(__file__),BUILD/'receipt.json',BUILD/'tool-terminal.json',TRAIN/'training.json',TRAIN/'verification.json',TRAIN/'tool-terminal.json',TRAIN/'verify-tool-terminal.json',TRAIN/'train.py',TRAIN/'verify.py',TRAIN/'plan.json',TRAIN/'merged.profdata',TRAIN/'merged.profdata.gz',NATIVE/'native-verification.json',NATIVE/'native-tool-terminal.json',ROOT/'tools/build.py',ROOT/'tools/archive_build.py',ROOT/'tools/check_live.py']
 paths += [SPEC/'profiling'/n for n in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']]+[SPEC/'fixtures/interrupted-sessions-v1.json']
 closure={str(p):sha(p) for p in paths};copy=OUT/'input-closure';copy.mkdir()
 for p in paths:
  q=copy/str(p).lstrip('/');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 write('input-closure.json',closure)
 archive=run([sys.executable,str(ROOT/'tools/archive_build.py'),str(BUILD)],'archive');assert archive['exit_code']==0
 # Training14 is terminal before this driver. Post-use development regression
 # follows the ordinary helper affinity, including root check_live's engines.
 replay=run(['/usr/bin/node',str(SPEC/'profiling/replay-check.mjs'),'--',str(engine)],'profile-all')
 report=load(OUT/'profile-all.stdout');assert replay['exit_code']==0 and report['status']=='pass' and len(report['results'])==54 and not (OUT/'profile-all.stderr').stat().st_size
 assert len({r['case'] for r in report['results']})==54
 for row in report['results']:
  assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']==dict(code=0,signal=None)
  assert row['error'] is None and row['stderr']=='' and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
 wire=run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(engine),'--output',str(WIRE)],'wire');wr=load(WIRE/'receipt.json')
 assert wire['exit_code']==0 and wr['pass'] and len(wr['results'])==8 and sum(len(r['searches']) for r in wr['results'])==24
 assert all(r['complete_streams'] and r['observed_exit_code']==r['exit_code']==0 for r in wr['results'])
 assert wr['engine_sha256_before']==wr['engine_sha256_after']==identity
 assert source_snapshot(SOURCE)==before and sha(engine)==identity and all(sha(Path(p))==h for p,h in closure.items())
 write('identity.json',dict(status='pass',variant=VARIANT,strict_replays=54,interruption_fixtures=8,interruption_searches=24,native_artifact_sha256=identity,build_receipt_sha256=sha(BUILD/'receipt.json'),training_record_sha256=sha(TRAIN/'training.json'),training_verification_sha256=sha(TRAIN/'verification.json'),profile_sha256=expected_profile,missing_function_warnings=0,source_before=before,source_after=source_snapshot(SOURCE),replay_sha256=sha(OUT/'profile-all.stdout'),wire_receipt_sha256=sha(WIRE/'receipt.json'),input_closure_sha256=sha(OUT/'input-closure.json'),stages=dict(archive=archive,replay=replay,wire=wire),scope='Own-profile matched preparation/regression only; all post-use engines/helpers housekeeping0-5,8-13. No CPU timing comparison or qualification claim.'))
 print(json.dumps(dict(variant=VARIANT,status='pass',strict54=54,wire8=8,searches24=24,artifact_sha256=identity,profile_sha256=expected_profile)))
if __name__=='__main__':main()
