#!/usr/bin/env python3
"""Read-only native/replay/accounting reconciliation and labeled sample estimates."""
import argparse,collections,json,statistics,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'full-split-production'))
from reconcile import lifetime,sha,read,HELPERS
CLASSES=['full_bound','cheap_threat_return','recursive_null_cutoff','original_inventory','stopped_unfinished']
NULL=['null_cutoff','null_continued','null_stopped','null_unfinished']
def stats(xs):
 if not xs:return dict(count=0)
 ys=sorted(xs);return dict(count=len(xs),sum=sum(xs),min=ys[0],median=statistics.median(ys),p95=ys[(len(ys)-1)*95//100],max=ys[-1],mean=sum(xs)/len(xs))
def sample_summary(xs):
 native=[x for x in xs if x['generation_kind']=='native'];paired=[x for x in native if x['full_interval_ns'] is not None];plain=[x for x in paired if x['null_outcome']=='not_entered']
 out=dict(samples=len(xs),outcomes=dict(collections.Counter(x['exit'] for x in xs)),nativeGen=stats([x['generation_ns'] for x in native]),discardShadowGen=stats([x['generation_ns'] for x in xs if x['generation_kind']=='discard_shadow']),exclusions=dict(collections.Counter(x['shadow_exclusion'] for x in xs if x['shadow_exclusion'])),fullInterval=stats([x['full_interval_ns'] for x in xs if x['full_interval_ns'] is not None]),consumedPairedOverlap=stats([min(x['full_interval_ns'],x['generation_ns']) for x in paired]),consumedNoNullPairedOverlap=stats([min(x['full_interval_ns'],x['generation_ns']) for x in plain]),consumedNoNullSlack=stats([x['full_interval_ns']-x['generation_ns'] for x in plain]),consumedNoNullGenFitsFull=sum(x['generation_ns']<=x['full_interval_ns'] for x in plain),consumedNoNullCount=len(plain),nullIntervals=stats([x['null_interval_ns'] for x in xs if x['null_interval_ns'] is not None]))
 out['scratchGroups']={str(flag):dict(count=sum(x['scratch_some']==flag for x in paired),fullInterval=stats([x['full_interval_ns'] for x in paired if x['scratch_some']==flag]),generation=stats([x['generation_ns'] for x in paired if x['scratch_some']==flag])) for flag in [False,True]};return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();base=a.raw.resolve();plan=read(base/'plan.json');data=read(base/'result.json');assert data['complete'];assert plan['schema']=='rook2-inventory-overlap-census-v1' and plan['sampling']==dict(every=512,cap=16384,timerProbes=1024)
 expected=[dict(case=c,variant='census',warmup=False,repeat=1) for c in ['profile-35','profile-08','profile-43']];assert plan['schedule']==expected and len(data['runs'])==3 and plan['budget']==1 and plan['options']==['--inventory-census'];assert plan['helperAffinity']==sorted(HELPERS)
 for f,h in plan['inputSha256'].items():assert sha(Path(f))==h
 receipt=read(Path(plan['build'])/'receipt.json');assert receipt['complete'] and receipt['binarySha256']==plan['binarySha256']==sha(Path(plan['binary']));assert receipt['sourceBefore']==receipt['sourceAfter']
 for f,h in receipt['sourceBefore'].items():assert sha(ROOT/f)==h
 summaries=[];posts=0
 for i,(step,row) in enumerate(zip(expected,data['runs'])):
  directory=base/f'{i:02d}-{step["case"]}';native,n=lifetime(directory,row,step,Path(plan['binary']),1,['--inventory-census'],plan['inputSha256']);posts+=n;report=read(directory/'census.json');assert report==row['census'] and sha(directory/'census.json')==row['censusSha256'];assert report['processId']==native['native_pid']
  assert report['schema']=='rook2-inventory-census-v1' and report['stride']==512 and report['sample_cap']==16384;c=report['counts'];assert c['eligible']==sum(c[k] for k in CLASSES) and c['null_entered']==sum(c[k] for k in NULL);assert c['null_cutoff']==c['recursive_null_cutoff']
  requests=c['eligible']//512;assert report['sample_requests']==requests and report['cap_skipped']==max(0,requests-16384);xs=report['samples'];assert report['samples_count']==len(xs)==min(requests,16384);assert [x['ordinal'] for x in xs]==[512*(i+1) for i in range(len(xs))]
  timer=report['timer_probe'];ts=timer['raw_ns'];assert timer['count']==len(ts)==1024 and timer['total_ns']==sum(ts);ordered=sorted(ts);assert timer['min_ns']==ordered[0] and timer['median_ns']==ordered[512] and timer['p95_ns']==ordered[1023*95//100] and timer['max_ns']==ordered[-1]
  for x in xs:
   assert x['exit'] in CLASSES and x['null_outcome'] in ['not_entered','cutoff','continued','stopped','unfinished'];assert x['setup_span_ns']>=0 and x['finish_span_ns']>=0
   if x['generation_kind']=='native':assert x['exit']=='original_inventory' and x['generation_ns'] is not None and x['generation_count'] is not None
   elif x['generation_kind']=='discard_shadow':assert x['exit'] in CLASSES[:3] and x['coherent'] and x['shadow_exclusion'] is None and x['generation_ns'] is not None
   elif x['generation_kind']=='excluded':assert x['exit'] in CLASSES[:3] and x['shadow_exclusion'] is not None and x['generation_ns'] is None
   else:assert x['generation_kind']=='none' and x['generation_ns'] is None and x['exit']=='stopped_unfinished'
   if x['null_outcome']=='cutoff':assert x['exit']=='recursive_null_cutoff'
   if x['null_outcome']=='continued':assert x['exit']=='original_inventory'
   if x['null_outcome']=='stopped':assert x['exit']=='stopped_unfinished'
  shadow=sum(x['generation_ns'] for x in xs if x['generation_kind']=='discard_shadow');admission=sum(x['shadow_admission_ns'] for x in xs);span=sum(x['setup_span_ns']+x['finish_span_ns'] for x in xs)
  assert report['shadow_generation_ns']==shadow and report['shadow_admission_ns']==admission and report['sampling_span_estimate_ns']==max(0,span-shadow-admission)
  summaries.append(dict(case=step['case'],counts=c,demandFraction=c['original_inventory']/c['eligible'],sampleRequests=requests,capSkipped=report['cap_skipped'],sampled=sample_summary(xs),observedCost=dict(timerProbe=stats(ts),enableNs=report['enable_span_ns'],shadowGenNs=shadow,shadowAdmissionNs=admission,partialSamplingSpanNs=report['sampling_span_estimate_ns']),instrumentedWholeCpuSeconds=row['wholeCpuSeconds'],instrumentedSearchWallNs=row['searchWallNs'],censusSha256=row['censusSha256']))
 result=dict(complete=True,replayLives=3,orderedPosts=posts,summaries=summaries,raw=str(base),rawBindings={n:sha(base/n) for n in ['plan.json','result.json']},reconcilerSha256=sha(Path(__file__)),limits='Systematic512 stride; bounded cap; paired min only consumed samples. Sequential/cache-warmed diagnostic estimate, no speed bound; null intervals include descendants/observers. No worker or repetition.')
 with (a.output or base/'reconciled.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print('reconciled3 lives',posts,'posts')
if __name__=='__main__':main()
