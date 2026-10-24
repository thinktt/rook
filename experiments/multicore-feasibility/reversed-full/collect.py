#!/usr/bin/env python3
"""One generic64-life comparison; no tuning, profile or replacement samples."""
import argparse,json,os,shlex,statistics,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'full-split-production'))
from train import sha,read,write,source_snapshot,run_lifetime,SPEC,ACCOUNT,HELPERS
from collect import idle_probe
CASES=['profile-35','profile-08','profile-04','profile-43']
NAMES=['control','inline','current','reversed']
CONTROL_SHA='64e01d986242f43f2063887b164e06e8201460fd5aefca5d6494a2f4b3634323'
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
def distribution(xs):return dict(samples=xs,median=statistics.median(xs),min=min(xs),max=max(xs))
def admit(build,control,candidate):
 r=read(build/'receipt.json');old=read(Path('/home/legolas/rook2-experiments/full-split-production-20261024-01/idle-build/receipt.json'))
 assert r['outcome']=='build-succeeded-with-stable-input-snapshot' and r['cargo_exit_code']==0
 assert r['target_cpu']==old['target_cpu']=='x86-64' and r['target_triple']==old['target_triple']=='x86_64-unknown-linux-gnu'
 assert r['rust_flags']==old['rust_flags']==['-C','target-cpu=x86-64'] and r['pgo']['mode']==old['pgo']['mode']=='none'
 assert r['source_sha256_before']==r['source_sha256_after']==source_snapshot(ROOT)
 for kind in ['rustc','cargo']:assert r['toolchain'][kind]==old['toolchain'][kind]
 assert sha(control)==old['binary_output']['sha256']==CONTROL_SHA
 assert sha(candidate)==r['binary_output']['sha256']==sha(Path(r['binary_output']['path']))
 for name,h in r['source_sha256_before'].items():assert sha(build/'source-before'/name)==h
 commands=[shlex.split(line.split('Running `',1)[1].rsplit('`',1)[0]) for line in (build/'build.stderr').read_text().splitlines() if 'Running `' in line and '--crate-name rook2 ' in line]
 for source in ['src/lib.rs','src/bin/rook2.rs']:
  xs=[x for x in commands if source in x];assert len(xs)==1
  options={}
  for i,x in enumerate(xs[0]):
   if x=='-C':key,_,value=xs[0][i+1].partition('=');options[key]=value or True
  for k,v in dict(opt_level='3',panic='abort',codegen_units='1',debuginfo='1',target_cpu='x86-64').items():assert options.get(k.replace('_','-'))==v
  assert not any(k.startswith('profile-') or k=='llvm-args' for k in options)
  if source.endswith('rook2.rs'):assert options['lto']=='thin'
  else:assert options['linker-plugin-lto'] is True
 return r

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['control','candidate','build','output']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();control=a.control.resolve();candidate=a.candidate.resolve();build=a.build.resolve();r=admit(build,control,candidate);out=a.output.resolve();out.mkdir()
 variants=dict(control=dict(path=str(control),budget=2,options=['--research-threads=2']),**{name:dict(path=str(candidate),budget=1 if name=='inline' else 2,options=['--research-full='+name]) for name in NAMES[1:]})
 schedule=[]
 for case in CASES:
  schedule += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
  for repeat in range(3):
   order=NAMES[repeat:]+NAMES[:repeat];schedule += [dict(case=case,variant=name,warmup=False,repeat=repeat+1) for name in order]
 paths=[Path(__file__)]
 paths += [HERE.parent/'full-split-production'/n for n in ['train.py','collect.py','reconcile.py']]
 paths += [ACCOUNT,ROOT/'tools/tap_wire.mjs',ROOT/'tools/compare_ordinary.py',SPEC/'replay-check.mjs',SPEC/'benchmark.mjs',SPEC/'workloads.json',SPEC/'replay-oracle.json',control,candidate,build/'receipt.json']
 plan=dict(schema='rook2-reversed-full-generic-v1',variants=variants,schedule=schedule,build=str(build),coordinatorCpu=14,workerCpu=6,idleOwnedSiblings=[7,15],helperAffinity=sorted(os.sched_getaffinity(0)),inputSha256={str(f):sha(f) for f in paths},limits=dict(perLifeSeconds=180,totalSeconds=1800),notes='matched preserved current-split generic control; four configurations, no PGO or retune')
 assert plan['helperAffinity']==sorted(HELPERS);write(out/'plan.json',plan);(out/'proc-stat-before').write_text(Path('/proc/stat').read_text());rows=[];state=dict(complete=False,runs=rows);deadline=time.monotonic()+1800
 try:
  for i,step in enumerate(schedule):
   assert time.monotonic()<deadline
   v=variants[step['variant']];d=out/f'{i:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
   rows.append(run_lifetime(d,step,Path(v['path']),v['budget'],v['options'],deadline));write(out/'progress.json',state)
  idle=[idle_probe(out/('idle-'+name),name,Path(v['path']),v['budget'],v['options']) for name,v in variants.items()]
  summaries=[]
  for case in CASES:
   for name in NAMES:
    selected=[r for r in rows if r['case']==case and r['variant']==name and not r['warmup']];assert len(selected)==3
    summaries.append(dict(case=case,variant=name,**{metric:distribution([r[metric] for r in selected]) for metric in METRICS}))
  assert all(sha(Path(f))==h for f,h in plan['inputSha256'].items());admit(build,control,candidate)
  state.update(complete=True,summaries=summaries,idle=idle,qualification='four-case generic research only; no PGO, full conformance, external delivery or adoption');write(out/'result.json',state);print('complete64 replay lives +4 idle processes',flush=True)
 except BaseException as error:write(out/'failure.json',dict(error=repr(error),completed=len(rows)));raise
 finally:(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
if __name__=='__main__':main()
