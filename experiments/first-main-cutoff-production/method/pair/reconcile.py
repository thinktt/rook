#!/usr/bin/python3
"""Independent paired whole-native CPU and complete protocol/source reconciliation."""
import csv,hashlib,json,os,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;B=HERE.parent;R=Path('/home/legolas/rook2');SPEC=Path('/home/legolas/king-spec/conformance/profiling')
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 plan=load(HERE/'plan.json');summary=load(HERE/'collection/summary.json');schedule=load(HERE/'schedule.json');oracle=load(SPEC/'replay-oracle.json');work=load(SPEC/'workloads.json')
 assert load(HERE/'collector-terminal.json')['exit_code']==0
 assert summary['complete'] and summary['failure'] is None and len(summary['runs'])==432
 assert sum(x['warmup'] for x in schedule)==108
 rows=[];pids=set();posts=0
 for step,row in zip(schedule,summary['runs'],strict=True):
  assert all(row[k]==v for k,v in step.items());d=Path(row['directory']);n=load(d/'native.json');w=load(d/'wire/receipt.json');c=load(d/'comparator.stdout')
  v=plan['variants'][step['variant']];case=next(x for x in work['cases'] if x['id']==step['case']);answer=next(x for x in oracle['cases'] if x['id']==step['case'])
  assert row['failure'] is None and row['comparator_exit']==0 and c['status']=='pass' and c['selectedCases']==[step['case']] and len(c['results'])==1 and (d/'comparator.stderr').stat().st_size==0
  assert n['failure'] is None and n['exec_error'] is None and n['supervisor_signals']==[] and n['native_exit_code']==n['native_wait_status']==0
  assert n['engine_sha256_before']==n['engine_sha256_after']==v['sha256'] and n['argv']==[v['path'],*oracle['mode']]
  assert n['native_pre_exec']['affinity']==n['native_post_exec']['affinity']==[14] and n['native_post_exec']['tasks']==[str(n['native_pid'])]
  assert n['supervisor_affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
  assert n['native_pid'] not in pids;pids.add(n['native_pid'])
  assert not Path(f"/proc/{n['native_pid']}").exists() and not Path(f"/proc/{n['supervisor_pid']}").exists()
  assert w['failure'] is None and w['pending'] is None and w['launcherExit']=={'code':0,'signal':None} and w['launcherPid']==n['supervisor_pid']
  assert w['configSha256']==sha(d/'wire-config.json') and w['argv']==load(d/'wire-config.json')['expectedArgv']
  assert len(w['searches'])==1;search=w['searches'][0];before,after=search['beforeWrite'],search['afterData']
  assert before['available'] and after['available'] and before['pid']==after['pid']==n['native_pid']
  assert before['startTicks']==after['startTicks']==w['native']['startTicks'] and before['image']==after['image']==v['path']
  assert before['lastProcessor']==after['lastProcessor']==14
  ticks=after['userTicks']+after['systemTicks']-before['userTicks']-before['systemTicks'];assert ticks>0
  assert ticks==search['cpuTicks'] and ticks/w['tickHz']==search['cpuSeconds']==row['search_cpu_s'] and search['cpuUnavailableReason'] is None
  assert row['search_wall_ns']==search['wallNs']==int(search['endMonotonicNs'])-int(search['startMonotonicNs'])
  assert row['cpu_s']==n['total_cpu_s']==n['user_cpu_s']+n['system_cpu_s']
  assert row['user_s']==n['user_cpu_s'] and row['system_s']==n['system_cpu_s'] and row['wall_ns']==n['wall_ns']==n['reaped_monotonic_ns']-n['start_monotonic_ns']
  for name,meta in w['raw'].items():
   p=Path(meta['path']);assert sha(p)==meta['sha256'] and p.stat().st_size==meta['bytes']==meta['observedBytes'] and meta['discardedObservedBytes']==0
  expected='\n'.join(case['protocol']['recordsBeforeSearch']+['cm_parm rnd',case['protocol']['searchRecord'],case['protocol']['cleanupRecord']])+'\n'
  assert (d/'wire/stdin.raw').read_text()==expected
  assert (d/'wire/stdout.raw').read_text()==c['results'][0]['stdout'] and (d/'wire/stderr.raw').read_bytes()==b''
  for name,key in [('native.json','native_receipt_sha256'),('comparator.stdout','comparator_sha256'),('wire/receipt.json','wire_receipt_sha256')]:assert sha(d/name)==row[key]
  posts+=len(answer['posts']);rows.append({**step,**{k:row[k] for k in ['cpu_s','user_s','system_s','wall_ns','search_cpu_s','search_wall_ns']},'nativePid':n['native_pid']})
 cases=[]
 for case in [c['id'] for c in work['cases']]:
  stats={}
  for variant in ['control','candidate']:
   measured=[r for r in rows if r['case']==case and r['variant']==variant and not r['warmup']];assert len(measured)==3
   stats[variant]={}
   for metric in ['cpu_s','user_s','system_s','wall_ns','search_cpu_s','search_wall_ns']:
    values=[r[metric] for r in measured];stats[variant][metric]={'samples':values,'minimum':min(values),'median':statistics.median(values),'maximum':max(values)}
  ratio=stats['candidate']['cpu_s']['median']/stats['control']['cpu_s']['median']
  assert summary['case_summaries'][case]=={'statistics':stats,'candidate_div_control':ratio}
  cases.append({'case':case,'statistics':stats,'candidate_div_control':ratio})
 totals={v:sum(c['statistics'][v]['cpu_s']['median'] for c in cases) for v in ['control','candidate']};assert totals==summary['sum_case_medians_s']
 result=subprocess.run(['/usr/bin/node',str(HERE/'check-raw.mjs')],capture_output=True,text=True)
 (HERE/'offline-check.stdout').write_text(result.stdout);(HERE/'offline-check.stderr').write_text(result.stderr)
 assert result.returncode==0 and not result.stderr and load(HERE/'offline-oracle-reconciliation.json')=={'verified':True,'engineRuns':0,'lifetimes':432,'originalChecks':864,'semanticPosts':posts}
 source=load(B/'source-freeze.json')
 for name,h in source['candidateFiles'].items():assert sha(Path(source['root'])/name)==h
 for name,h in source['canonicalFiles'].items():assert sha(R/name)==h
 for p,h in plan['input_sha256'].items():assert sha(p)==h,p
 for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
 training=load(B/'training/training.json');use=load(B/'use-build/receipt.json')
 assert use['source_sha256_before']==use['source_sha256_after']==source['engineSourceFiles']
 assert use['binary_output']['sha256']==plan['variants']['candidate']['sha256']
 assert use['pgo']['mode']=='profile-use' and sha(B/'training/merged.profdata')==training['profile_sha256']
 assert use['rust_flags']==['-C','target-cpu=x86-64','-C',f"profile-use={B/'training/merged.profdata'}",'-C','llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false']
 assert load(B/'training/verification.json')['independent_remerge_byte_identical']
 contexts=[load(HERE/'collection'/f'context-{when}.json') for when in ['before','after']]
 def ticks(c):return [int(x) for x in next(s for s in c['proc_stat'].splitlines() if s.startswith('cpu15 ')).split()[1:]]
 delta=[a-b for a,b in zip(ticks(contexts[1]),ticks(contexts[0]))]
 proof={'verified':True,'lifetimes':432,'warmups':108,'measured':324,'semanticPosts':posts,'originalOfflineChecks':864,'sum_case_medians_s':totals,'candidate_div_control':totals['candidate']/totals['control'],'lowerCases':sum(c['candidate_div_control']<1 for c in cases),'worstCaseRatio':max(c['candidate_div_control'] for c in cases),'cases':cases,'nativeRows':rows,'cpu15GuestTickDelta':delta,'noOutlierDeletion':True,'numericalGainGate':None,'allNativeSupervisorPidsAbsent':True,'sourceCanonicalUnchanged':True,'scope':'Paired local descriptive whole native user+system CPU; three samples per image/case; no simultaneous confidence, private reference comparison, final performance acceptance or promotion.'}
 (HERE/'independent-reconciliation.json').write_text(json.dumps(proof,indent=2)+'\n')
 with (HERE/'timings.csv').open('x') as f:
  writer=csv.writer(f);writer.writerow(['case','control_sample1_s','control_sample2_s','control_sample3_s','control_min_s','control_median_s','control_max_s','candidate_sample1_s','candidate_sample2_s','candidate_sample3_s','candidate_min_s','candidate_median_s','candidate_max_s','candidate_div_control'])
  for c in cases:
   a,b=[c['statistics'][v]['cpu_s'] for v in ['control','candidate']];writer.writerow([c['case'],*a['samples'],a['minimum'],a['median'],a['maximum'],*b['samples'],b['minimum'],b['median'],b['maximum'],c['candidate_div_control']])
 print(json.dumps({k:v for k,v in proof.items() if k not in ['cases','nativeRows']}))
if __name__=='__main__':main()
