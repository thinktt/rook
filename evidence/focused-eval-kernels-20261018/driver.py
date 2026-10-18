#!/usr/bin/env python3
"""Current exact artifact focused/continuous behavior only; no CPU timing claim."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot
GATE=Path('/home/legolas/king-spec/conformance/gate-replay')
BUILD=ROOT/'evidence/production-eval-kernels-use-build-20261018'
ENGINE=BUILD/'rook2-exact'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 build=json.loads((BUILD/'receipt.json').read_text())
 assert sha(ENGINE)==build['binary_output']['sha256']=='8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953'
 before=source_snapshot(ROOT);assert before==build['source_sha256_before']==build['source_sha256_after']
 paths=[ENGINE,BUILD/'receipt.json',Path(__file__),*[GATE/x for x in ['run.mjs','continuous.mjs','combine.mjs','accepted-games-v1.json','continuous-switching-v1.json']]]
 hashes={str(p):sha(p) for p in paths}
 write('preflight.json',dict(files=hashes,native_source=before,helper_affinity=sorted(os.sched_getaffinity(0)),engine_affinity='Inherits housekeeping affinity for this untimed behavioral check',scope='Current artifact behavior; not CPU timing, PMU or final qualification'))
 stages=[]
 for name,argv in [
  ('games',['/usr/bin/node',str(GATE/'run.mjs'),'--report',str(OUT/'games.json'),'--timeout-ms','300000','--',str(ENGINE)]),
  ('continuous',['/usr/bin/node',str(GATE/'continuous.mjs'),'--report',str(OUT/'continuous.json'),'--timeout-ms','300000','--',str(ENGINE)]),
  ('combine',['/usr/bin/node',str(GATE/'combine.mjs'),'--report',str(OUT/'combined.json'),'--continuous',str(OUT/'continuous.json'),str(OUT/'games.json')])]:
  with (OUT/(name+'.stdout')).open('xb') as out,(OUT/(name+'.stderr')).open('xb') as err:r=subprocess.run(argv,stdout=out,stderr=err,cwd=ROOT)
  stage=dict(name=name,command=argv,exit_code=r.returncode,stdout_sha256=sha(OUT/(name+'.stdout')),stderr_sha256=sha(OUT/(name+'.stderr')))
  stages.append(stage);write(name+'-terminal.json',stage)
  assert r.returncode==0 and (OUT/(name+'.stderr')).stat().st_size==0
  print(json.dumps(dict(stage=name,exit_code=r.returncode)),flush=True)
 combined=json.loads((OUT/'combined.json').read_text())
 assert combined['pass'] and combined['completeFocusedReplay'] and not combined['completeGameplayQualification']
 after=source_snapshot(ROOT);assert after==before
 assert hashes=={str(p):sha(p) for p in paths}
 write('verification.json',dict(complete=True,artifact_sha256=sha(ENGINE),source_before=before,source_after=after,inputs_sha256=hashes,stages=stages,complete_focused_replay=True,complete_gameplay_qualification=False,scope='Exact artifact behavioral evidence; no CPU time/PMU/calibration/final qualification claim'))
if __name__=='__main__':main()
