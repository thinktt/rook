#!/usr/bin/env python3
"""Bind current exact engine's unchanged released seed controls."""
import hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
GATE=Path('/home/legolas/king-spec/conformance/gate-replay')
ENGINE=ROOT/'evidence/production-eval-kernels-use-build-20261018/rook2-exact'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 files=[ENGINE,Path(__file__),GATE/'seed-command-controls.mjs',GATE/'seed-persistence-controls.mjs']
 before={str(p):sha(p) for p in files}
 assert sha(ENGINE)=='8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953'
 assert json.loads((OUT/'verification.json').read_text())['complete']
 stages=[]
 for name in ['seed-command-controls','seed-persistence-controls']:
  command=['/usr/bin/node',str(GATE/(name+'.mjs')),'--',str(ENGINE)]
  stdout,stderr=OUT/(name+'.stdout'),OUT/(name+'.stderr')
  with stdout.open('xb') as out,stderr.open('xb') as err:r=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err)
  stage=dict(command=command,exit_code=r.returncode,stdout_sha256=sha(stdout),stderr_sha256=sha(stderr));stages.append(stage)
  assert r.returncode==0 and not stderr.stat().st_size
  assert json.loads(stdout.read_text())['pass']
 assert before=={str(p):sha(p) for p in files}
 with (OUT/'seed-controls-verification.json').open('x') as f:json.dump(dict(complete=True,inputs_sha256=before,stages=stages,scope='Current exact-artifact public seed controls; untimed behavior only'),f,indent=2);f.write('\n')
 print(json.dumps(dict(complete=True,controls=2,artifact_sha256=sha(ENGINE))))
if __name__=='__main__':main()
