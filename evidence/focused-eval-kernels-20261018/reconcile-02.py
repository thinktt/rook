#!/usr/bin/env python3
"""Offline identity/inventory reconciliation of the unchanged released focused reports."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
GATE=Path('/home/legolas/king-spec/conformance/gate-replay')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
 verify=load(OUT/'verification.json');pre=load(OUT/'preflight.json')
 assert verify['complete'] and verify['source_before']==verify['source_after']==pre['native_source']
 assert all(sha(Path(p))==h for p,h in pre['files'].items())
 engine=ROOT/'evidence/production-eval-kernels-use-build-20261018/rook2-exact'
 assert sha(engine)==verify['artifact_sha256']=='8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953'
 fixture=load(GATE/'accepted-games-v1.json')
 games=load(OUT/'games.json');continuous=load(OUT/'continuous.json');combined=load(OUT/'combined.json')
 expected=[{'id':g['id'],'family':g['family'],'searches':len(g['plies']),'pass':True} for g in fixture['games']]
 assert len(expected)==12 and sum(x['searches'] for x in expected)==632
 assert games['pass'] and games['games']==expected and len(games['processes'])==12
 assert games['selectedGameIds']==[g['id'] for g in fixture['games']]
 assert games['command']==continuous['command']==[str(engine)]
 assert games['executableSha256']==continuous['executableSha256']==sha(engine)
 assert games['fixtureSha256']==continuous['fixtureSha256']==sha(GATE/'accepted-games-v1.json')
 assert games['runnerSha256']==continuous['comparatorSha256']==sha(GATE/'run.mjs')
 assert continuous['runnerSha256']==sha(GATE/'continuous.mjs')
 assert continuous['scheduleSha256']==sha(GATE/'continuous-switching-v1.json')
 assert continuous['pass'] and len(continuous['games'])==4 and sum(x['searches'] for x in continuous['games'])==8
 assert len(continuous['processes'])==1
 for report in [games,continuous]:
  assert all(p['code']==0 and p['signal'] is None and not p['forced'] for p in report['processes'])
 assert combined['pass'] and combined['completeIndependentGames'] and combined['completeFocusedReplay'] and not combined['completeGameplayQualification']
 for stage in verify['stages']:
  name=stage['name'];assert stage['exit_code']==0
  assert sha(OUT/(name+'.stdout'))==stage['stdout_sha256']
  assert sha(OUT/(name+'.stderr'))==stage['stderr_sha256'] and not (OUT/(name+'.stderr')).stat().st_size
 inputs={str(p):sha(p) for p in [OUT/'verification.json',OUT/'preflight.json',OUT/'games.json',OUT/'continuous.json',OUT/'combined.json',Path(__file__)]}
 result=dict(complete=True,artifact_sha256=sha(engine),independent_games=12,independent_searches=632,continuous_segments=4,continuous_searches=8,normal_native_lifetimes=13,complete_focused_replay=True,complete_gameplay_qualification=False,input_sha256=inputs,scope='Offline identity/inventory/normal-exit reconciliation. Semantic byte comparisons are assertions of the unchanged executed released runner; no independent raw-wire reconstruction, CPU timing or final qualification claim.')
 with (OUT/'identity.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'}))
if __name__=='__main__':main()
