#!/usr/bin/env python3
"""Recheck the frozen64-life raw streams and native receipts, without engines."""
import argparse,json,sys,statistics,shlex
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'full-split-production'))
from reconcile import lifetime,native_receipt,sha,read,HELPERS,SPEC
CASES=['profile-35','profile-08','profile-04','profile-43']
NAMES=['control','inline','current','reversed']
METRICS=['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']
def dist(xs):return dict(samples=xs,median=statistics.median(xs),min=min(xs),max=max(xs))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();base=a.raw.resolve();plan=read(base/'plan.json');r=read(base/'result.json');assert plan['schema']=='rook2-reversed-full-generic-v1' and r['complete']
 for name,h in plan['inputSha256'].items():assert sha(Path(name))==h
 expected=[]
 for case in CASES:
  expected += [dict(case=case,variant=n,warmup=True,repeat=0) for n in NAMES]
  for i in range(3):expected += [dict(case=case,variant=n,warmup=False,repeat=i+1) for n in NAMES[i:]+NAMES[:i]]
 assert expected==plan['schedule'] and len(r['runs'])==64;assert plan['helperAffinity']==sorted(HELPERS) and plan['idleOwnedSiblings']==[7,15]
 variants=plan['variants'];assert list(variants)==NAMES and variants['control']['options']==['--research-threads=2'] and variants['control']['budget']==2
 assert sha(Path(variants['control']['path']))=='64e01d986242f43f2063887b164e06e8201460fd5aefca5d6494a2f4b3634323'
 for n in NAMES[1:]:assert variants[n]['options']==['--research-full='+n] and variants[n]['budget']==(1 if n=='inline' else 2)
 build=Path(plan['build']);receipt=read(build/'receipt.json');assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['pgo']['mode']=='none'
 assert receipt['rust_flags']==['-C','target-cpu=x86-64'] and receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged']
 assert receipt['source_sha256_before']==receipt['source_sha256_after'];assert sha(Path(variants['inline']['path']))==receipt['binary_output']['sha256']
 for name,h in receipt['source_sha256_before'].items():assert sha(ROOT/name)==sha(build/'source-before'/name)==h
 posts=0
 for i,(step,row) in enumerate(zip(expected,r['runs'])):
  v=variants[step['variant']];d=base/f'{i:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}';_,n=lifetime(d,row,step,Path(v['path']),v['budget'],v['options'],plan['inputSha256']);posts+=n
 assert len(r['idle'])==4
 for name,row in zip(NAMES,r['idle']):
  assert row['variant']==name;d=base/('idle-'+name);v=variants[name];assert read(d/'probe.json')==row
  n=native_receipt(d/'native.json',Path(v['path']),v['budget'],v['options'],plan['inputSha256'])
  assert row['nativePid']==n['native_pid'] and row['supervisorPid']==n['supervisor_pid']
  assert row['wholeCpuSeconds']==n['total_cpu_s'] and row['wholeWallNs']==n['wall_ns']
  assert row['idleCpuSeconds']==row['idleCpuTicks']/row['tickHz'] and row['idleCpuTicks']>=0
  for file,h in row['sha256'].items():assert sha(d/file)==h
 summaries=[]
 for case in CASES:
  for name in NAMES:
   selected=[x for x in r['runs'] if x['case']==case and x['variant']==name and not x['warmup']];assert len(selected)==3
   summaries.append(dict(case=case,variant=name,**{k:dist([x[k] for x in selected]) for k in METRICS}))
 assert summaries==r['summaries'];by={(x['case'],x['variant']):x for x in summaries};comparisons=[]
 for case in CASES:
  row=dict(case=case)
  for name in NAMES[1:]:
   row[name]=dict(wallVsControl=by[case,name]['searchWallNs']['median']/by[case,'control']['searchWallNs']['median'],cpuVsControl=by[case,name]['wholeCpuSeconds']['median']/by[case,'control']['wholeCpuSeconds']['median'])
  row['reversedVsCurrentWall']=by[case,'reversed']['searchWallNs']['median']/by[case,'current']['searchWallNs']['median'];comparisons.append(row)
 sums={name:{k:sum(by[c,name][k]['median'] for c in CASES) for k in METRICS[:3]} for name in NAMES}
 result=dict(complete=True,replayLives=64,measured=48,warmups=16,idleProcesses=4,orderedPosts=posts,comparisons=comparisons,summedMedians=sums,summaries=summaries,idle=r['idle'],raw=str(base),rawSha256={n:sha(base/n) for n in ['plan.json','result.json']},reconcilerSha256=sha(Path(__file__)),scope='four-case generic only; captured stdin write bytes exclude end(data) cleanup; no qualification')
 output=a.output or base/'reconciled.json'
 with output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:result[k] for k in ['complete','replayLives','orderedPosts','summedMedians','comparisons']},indent=2))
if __name__=='__main__':main()
