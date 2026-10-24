#!/usr/bin/env python3
"""One fixed generic64-life inventory trial, using the established native machinery."""
import argparse,importlib.util,os,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'full-split-production'))
from train import run_lifetime,sha,read,write,SPEC,ACCOUNT,HELPERS
from collect import idle_probe,distribution
prior=HERE.parent/'reversed-full/collect.py'
spec=importlib.util.spec_from_file_location('prior_generic_admission',prior);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
CASES=['profile-35','profile-08','profile-04','profile-43'];NAMES=['control','inline','current','inventory'];METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['control','candidate','build','output']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();control=a.control.resolve();candidate=a.candidate.resolve();build=a.build.resolve();module.admit(build,control,candidate);out=a.output.resolve();out.mkdir()
 variants=dict(control=dict(path=str(control),budget=2,options=['--research-threads=2']),**{n:dict(path=str(candidate),budget=1 if n=='inline' else 2,options=['--research-full='+n]) for n in NAMES[1:]})
 schedule=[]
 for case in CASES:
  schedule += [dict(case=case,variant=n,warmup=True,repeat=0) for n in NAMES]
  for repeat in range(3):schedule += [dict(case=case,variant=n,warmup=False,repeat=repeat+1) for n in NAMES[repeat:]+NAMES[:repeat]]
 paths=[Path(__file__),HERE/'reconcile.py',prior,*[HERE.parent/'full-split-production'/n for n in ['train.py','collect.py','reconcile.py']],ACCOUNT,ROOT/'tools/tap_wire.mjs',ROOT/'tools/compare_ordinary.py',SPEC/'workloads.json',SPEC/'replay-oracle.json',SPEC/'replay-check.mjs',SPEC/'benchmark.mjs',control,candidate,build/'receipt.json']
 plan=dict(schema='rook2-same-node-inventory-generic-v1',variants=variants,schedule=schedule,build=str(build),helperAffinity=sorted(os.sched_getaffinity(0)),coordinatorCpu=14,workerCpu=6,idleOwnedSiblings=[7,15],inputSha256={str(p):sha(p) for p in paths},limits=dict(perLifeSeconds=180,totalSeconds=1800),policy='READY-only at original demand; otherwise inline then drain; unconditional null-boundary settle with owned local Box; no Q/FULL worker')
 assert plan['helperAffinity']==sorted(HELPERS);write(out/'plan.json',plan);(out/'proc-stat-before').write_text(Path('/proc/stat').read_text());rows=[];state=dict(complete=False,runs=rows);deadline=time.monotonic()+1800
 try:
  for i,step in enumerate(schedule):
   assert time.monotonic()<deadline;v=variants[step['variant']];d=out/f'{i:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
   if step['variant']!='control':os.environ['ROOK2_INVENTORY_WORKER_REPORT']=str(d/'stats.json')
   else:os.environ.pop('ROOK2_INVENTORY_WORKER_REPORT',None)
   row=run_lifetime(d,step,Path(v['path']),v['budget'],v['options'],deadline);os.environ.pop('ROOK2_INVENTORY_WORKER_REPORT',None)
   if step['variant']!='control':
    assert (d/'stats.json').stat().st_size<=1024*1024;report=read(d/'stats.json');assert report['schema']=='rook2-inventory-worker-v1' and report['processId']==row['nativePid'];row.update(inventory=report,inventorySha256=sha(d/'stats.json'))
   else:assert not (d/'stats.json').exists()
   rows.append(row);write(out/'progress.json',state)
  idle=[idle_probe(out/('idle-'+n),n,Path(v['path']),v['budget'],v['options']) for n,v in variants.items()]
  summaries=[]
  for case in CASES:
   for n in NAMES:
    selected=[r for r in rows if r['case']==case and r['variant']==n and not r['warmup']];assert len(selected)==3;summaries.append(dict(case=case,variant=n,**{k:distribution([r[k] for r in selected]) for k in METRICS}))
  assert all(sha(Path(p))==h for p,h in plan['inputSha256'].items());module.admit(build,control,candidate)
  state.update(complete=True,summaries=summaries,idle=idle,limits='generic four-case mechanism experiment, no PGO or broad qualification');write(out/'result.json',state);print('complete64 replay lives+4 idle',flush=True)
 except BaseException as error:write(out/'failure.json',dict(error=repr(error),completed=len(rows)));raise
 finally:os.environ.pop('ROOK2_INVENTORY_WORKER_REPORT',None);(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
if __name__=='__main__':main()
