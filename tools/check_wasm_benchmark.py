"""Independently reconcile a completed matched54 CPU/wall collection; no native execution."""
import argparse,hashlib,json,statistics
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);a=p.parse_args();root=a.directory.resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((root/'summary.json').read_text());plan=json.loads((root/'plan.json').read_text())
assert s['complete'] and not s.get('failure')
assert len(s['runs'])==len(plan['schedule'])==648
assert len(s['caseSummaries'])==54
assert all(sha(root/'collector.mjs' if Path(p).name=='benchmark_wasm.mjs' else Path(p))==h for p,h in plan['pins'].items())
values={};chrome_pids=set();maximum_cpu_wall=0;raw_hashes={}
for row,step in zip(s['runs'],plan['schedule']):
 assert all(row[k]==v for k,v in step.items())
 d=json.loads((root/row['file']).read_text())
 assert all(d[k]==v for k,v in step.items())
 assert d['error'] is None and d['complete'] and d['exit']=={'code':0,'signal':None} and d['stderr']==''
 assert d['before']['pid']==d['after']['pid']==d['pid']
 cpu=(int(d['after']['cpuNs'])-int(d['before']['cpuNs']))/1e9
 assert cpu==d['cpuSeconds']==row['cpuSeconds'] and cpu>0 and d['wallSeconds']>0
 assert all(t['cpus']=='14' for t in d['tasksBefore']+d['tasksAfter'])
 maximum_cpu_wall=max(maximum_cpu_wall,cpu/d['wallSeconds'])
 if d['variant']=='chromium':
  assert d['quitCommandStatus']==2 and d['workerTasks'] and d['pid'] not in chrome_pids
  chrome_pids.add(d['pid'])
 if not d['warmup']:values.setdefault(d['case'],{}).setdefault(d['variant'],[]).append(d)
 raw_hashes[row['file']]=sha(root/row['file'])
totals={};ranges={}
for variant in ['native','node','chromium']:
 total={}
 for metric,key in [('cpu','cpuSeconds'),('wall','wallSeconds')]:
  medians=[]
  for case,groups in values.items():
   data=groups[variant];assert len(data)==3
   samples=[d[key] for d in data];v={'minimum':min(samples),'median':statistics.median(samples),'maximum':max(samples)}
   assert s['caseSummaries'][case][variant][metric]==v
   medians.append(v['median'])
  total[metric]=sum(medians)
  assert abs(total[metric]-s['totals'][variant][metric])<1e-10
 totals[variant]=total
 widths=[(max(d['cpuSeconds'] for d in groups[variant])-min(d['cpuSeconds'] for d in groups[variant]))/statistics.median(d['cpuSeconds'] for d in groups[variant]) for groups in values.values()]
 ranges[variant]={'medianCaseRangeOverMedian':statistics.median(widths),'maximumCaseRangeOverMedian':max(widths)}
result=dict(pass_=True,runs=648,warmups=162,measured=486,cases=54,uniqueChromiumRenderers=len(chrome_pids),totals=totals,ranges=ranges,maximumCpuWallRatio=maximum_cpu_wall,
 ratios={v:{metric:totals[v][metric]/totals['native'][metric] for metric in ['cpu','wall']} for v in ['node','chromium']},
 hashes={name:sha(root/name) for name in ['plan.json','summary.json','clock-control.json','logging-control.json']},rawReceiptSha256=hashlib.sha256(json.dumps(raw_hashes,sort_keys=True).encode()).hexdigest())
(root/'independent-closure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
