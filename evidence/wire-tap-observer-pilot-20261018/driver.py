#!/usr/bin/env python3
"""Fixed balanced controller-tap overhead pilot on a complete published game."""
import hashlib,json,os,statistics,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from collect_games import run_lifetime,context,LIMITS
from compare_ordinary import sha,write
ENGINE=ROOT/'evidence/pgo-eval-geometry-use-build-20261018/rook2-exact'
BUILD=ROOT/'evidence/pgo-eval-geometry-use-build-20261018/receipt.json'
GAME=next(g for g in json.loads(Path('/home/legolas/king-spec/conformance/gate-replay/accepted-games-v1.json').read_text())['games'] if g['id']=='main-0168')
SCHEDULE=[dict(mode=m,warmup=True,repeat=0) for m in ['plain','tap']]
for repeat in range(1,5):
 SCHEDULE += [dict(mode=m,warmup=False,repeat=repeat) for m in (['plain','tap'] if repeat%2 else ['tap','plain'])]
def main():
 engine_sha=sha(ENGINE); assert json.loads(BUILD.read_text())['binary_output']['sha256']==engine_sha
 dependencies=[Path(__file__).resolve(),BUILD,ROOT/'tools/collect_games.py',ROOT/'tools/tap_wire.mjs',ROOT/'tools/account_native.py',ROOT/'tools/compare_ordinary.py',ROOT/'tools/measure.py',Path('/home/legolas/king-spec/conformance/gate-replay/run.mjs'),Path('/home/legolas/king-spec/conformance/gate-replay/accepted-games-v1.json')]
 before={str(p):sha(p) for p in dependencies}
 write(OUT/'manifest.json',dict(engine=str(ENGINE),engine_sha256=engine_sha,schedule=SCHEDULE,game=GAME['id'],inputs=before,limits=LIMITS,scope='Reported-only external observer pilot; no final tolerance/qualification'))
 write(OUT/'context-before.json',context())
 summary=dict(complete=False,failure=None,runs=[])
 deadline=time.monotonic()+1800
 for index,step in enumerate(SCHEDULE):
  directory=OUT/f"{index:02d}-{step['mode']}"
  result=run_lifetime(ENGINE,engine_sha,GAME,directory,deadline,capture=step['mode']=='tap')
  row=dict(**step,failure=result['failure'],cpu_s=result.get('cpu_s'),wall_ns=result.get('wall_ns'),result_sha256=sha(directory/'result.json'))
  summary['runs'].append(row);write(OUT/'summary.json',summary)
  print(json.dumps(row),flush=True)
  if result['failure']:
   summary['failure']=result['failure']; break
 summary['complete']=len(summary['runs'])==len(SCHEDULE) and summary['failure'] is None
 summary['input_sha256_after']={str(p):sha(p) for p in dependencies}
 summary['artifact_sha256_after']=sha(ENGINE)
 if summary['input_sha256_after']!=before or summary['artifact_sha256_after']!=engine_sha:
  summary.update(complete=False,failure='artifact/input changed')
 if summary['complete']:
  summary['metrics']={}
  for metric in ['cpu_s','wall_ns']:
   values={mode:[r[metric] for r in summary['runs'] if r['mode']==mode and not r['warmup']] for mode in ['plain','tap']}
   summary['metrics'][metric]={mode:dict(samples=v,median=statistics.median(v),minimum=min(v),maximum=max(v)) for mode,v in values.items()}
   summary['metrics'][metric]['tap_over_plain_median']=statistics.median(values['tap'])/statistics.median(values['plain'])
 write(OUT/'summary.json',summary);write(OUT/'context-after.json',context())
 return 0 if summary['complete'] else 1
if __name__=='__main__': raise SystemExit(main())
