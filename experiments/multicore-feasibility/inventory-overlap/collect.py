#!/usr/bin/env python3
"""Exactly three original replay lives with fixed serial ordinary census."""
import argparse,json,os,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'full-split-production'))
from train import run_lifetime,sha,read,write,SPEC,ACCOUNT,HELPERS
CASES=['profile-35','profile-08','profile-43']
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build=a.build.resolve();receipt=read(build/'receipt.json');assert receipt['complete'] and receipt['sourceBefore']==receipt['sourceAfter'];binary=Path(receipt['binary']);assert sha(binary)==receipt['binarySha256'];out=a.output.resolve();out.mkdir()
 schedule=[dict(case=c,variant='census',warmup=False,repeat=1) for c in CASES];paths=[Path(__file__),HERE/'build.py',HERE.parent/'full-split-production/train.py',HERE.parent/'full-split-production/reconcile.py',ACCOUNT,ROOT/'tools/tap_wire.mjs',ROOT/'tools/compare_ordinary.py',SPEC/'workloads.json',SPEC/'replay-oracle.json',SPEC/'replay-check.mjs',SPEC/'benchmark.mjs',build/'receipt.json',binary]
 plan=dict(schema='rook2-inventory-overlap-census-v1',binary=str(binary),binarySha256=sha(binary),build=str(build),schedule=schedule,inputSha256={str(p):sha(p) for p in paths},budget=1,options=['--inventory-census'],coordinatorCpu=14,helperAffinity=sorted(os.sched_getaffinity(0)),sampling=dict(every=512,cap=16384,timerProbes=1024),limits=dict(perLifeSeconds=180,totalSeconds=900));assert plan['helperAffinity']==sorted(HELPERS);write(out/'plan.json',plan);rows=[];state=dict(complete=False,runs=rows);deadline=time.monotonic()+900
 (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
 try:
  for i,step in enumerate(schedule):
   assert time.monotonic()<deadline;d=out/f'{i:02d}-{step["case"]}'
   os.environ['ROOK2_INVENTORY_CENSUS_REPORT']=str(d/'census.json')
   row=run_lifetime(d,step,binary,1,['--inventory-census'],deadline);os.environ.pop('ROOK2_INVENTORY_CENSUS_REPORT')
   assert (d/'census.json').stat().st_size<=16*1024*1024
   report=read(d/'census.json');row.update(census=report,censusSha256=sha(d/'census.json'));rows.append(row);write(out/'progress.json',state);print('completed',step['case'],flush=True)
  assert all(sha(Path(f))==h for f,h in plan['inputSha256'].items());assert all(sha(ROOT/f)==h for f,h in receipt['sourceBefore'].items())
  state['complete']=True;write(out/'result.json',state)
 except BaseException as error:write(out/'failure.json',dict(error=repr(error),completed=len(rows)));raise
 finally:os.environ.pop('ROOK2_INVENTORY_CENSUS_REPORT',None);(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
if __name__=='__main__':main()
