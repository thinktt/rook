#!/usr/bin/env python3
"""Read-only independent reconciliation; never starts a native process."""
import argparse,hashlib,json,math,os,re,statistics
from pathlib import Path
P=Path(__file__).resolve().parent
S=Path('/home/legolas/king-spec');H=[0,1,2,3,4,5,8,9,10,11,12,13]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def save(p,v):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 with Path(p).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def near(a,b):assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9),(a,b)
def lines(b):
 assert b.endswith(b'\n') and b'\r' not in b,'partial or unexpected CR raw stream'
 return b.decode('ascii').splitlines()
rx=re.compile(r'^\s*(\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)\s+(.+?)\s*$')
def post(line,game=False):
 m=rx.fullmatch(line);assert m,('invalid post',line);d,e,t,n,pv=m.groups();pv=pv.strip().replace('0','O')
 return dict(zip(['depthToken','evaluation','engineCentiseconds','searchId','pv'] if game else ['depth','score','workThousands','searchId','pv'],[int(d),int(e),int(t),int(n),pv]))
def stats(v):
 assert len(v)==3 and all(math.isfinite(x) and x>0 for x in v)
 return dict(samples=v,minimum=min(v),median=statistics.median(v),maximum=max(v))
def comparison(v,ref):
 a,b=stats(v),stats(ref);return dict(local=a,reference=b,median_ratio=a['median']/b['median'],descriptive_ratio_envelope=[a['minimum']/b['maximum'],a['maximum']/b['minimum']])
def inputs(plan):
 for f,h in plan['dependency_sha256'].items():assert sha(f)==h,('input changed',f)
 return dict(complete=True,files=len(plan['dependency_sha256']),native_sha256=plan['engine_sha256'])
def native(path,plan):
 n=load(path);assert n['failure'] is None and n['native_exit_code']==0 and os.waitstatus_to_exitcode(n['native_wait_status'])==0
 assert n['supervisor_signals']==[] and n['exec_error'] is None and n['known_single_process'] is True
 assert n['engine_sha256_before']==n['engine_sha256_after']==plan['engine_sha256']
 assert n['launcher_sha256']==plan['tools23_sha256']['tools/account_native.py']
 assert n['supervisor_affinity']==n['inherited_supervisor_affinity']==H
 assert n['native_pre_exec']['affinity']==n['native_post_exec']['affinity']==[14]
 assert n['native_post_exec']['tasks']==[str(n['native_pid'])]
 assert n['native_pre_exec']['pgid']==n['native_post_exec']['pgid']
 near(n['total_cpu_s'],n['user_cpu_s']+n['system_cpu_s']);assert n['total_cpu_s']>0 and n['wall_ns']>0
 return n

def ordinary(plan):
 D=P/'ordinary54';m=load(D/'manifest.json');sm=load(D/'summary.json');assert sm['complete'] and sm['failure'] is None
 assert m['schedule']==plan['ordinary_schedule'] and len(sm['runs'])==216
 assert m['engine_sha256']==sm['artifact_sha256_after']==plan['engine_sha256']
 assert m['input_sha256']==sm['input_sha256_after']
 for f,h in m['input_sha256'].items():assert sha(f)==h,('collector input',f)
 w={r['id']:r for r in load(S/'conformance/profiling/workloads.json')['cases']};o={r['id']:r for r in load(S/'conformance/profiling/replay-oracle.json')['cases']}
 ref={r['caseId']:r for r in load(S/'performance/reference54.json')['casesData']};samples={k:[] for k in plan['ordered_cases']};all_runs=[]
 for i,(step,row) in enumerate(zip(plan['ordinary_schedule'],sm['runs'])):
  assert all(row[k]==v for k,v in step.items()) and row['failure'] is None and row['comparator_exit']==0
  d=D/f"{i:03d}-{step['case']}-r{step['repeat']}";assert (d/'comparator.stderr').read_bytes()==b''
  n=native(d/'native.json',plan);a=load(d/'comparator.stdout');assert a['status']=='pass' and a['selectedCases']==[step['case']] and len(a['results'])==1
  z=a['results'][0];e=o[step['case']];assert z['case']==step['case'] and z['status']=='pass' and z['error'] is None and z['complete'] is True and z['truncated'] is False and z['discardedObservedBytes']==0
  assert z['exit']==e['exit']==dict(code=0,signal=None) and z['stderr']==e['stderr']==''
  raw=z['stdout'].encode('ascii');near(len(raw),z['retainedBytes']);ls=lines(raw)
  acks=[q for q in w[step['case']]['protocol']['recordsBeforeSearch'] if q.startswith('cm_parm ')]+['cm_parm rnd=0']
  assert ls[:len(acks)]==acks;ls=ls[len(acks):];posts=[post(x) for x in ls[:len(e['posts'])]];assert posts==e['posts']
  assert ls[len(posts):]==['move '+e['move']]+e['resultRecords']
  assert n['supervisor_pid']==z['pid'] and n['argv']==[plan['engine'],*load(S/'conformance/profiling/replay-oracle.json')['mode']]
  assert sha(d/'native.json')==row['native_receipt_sha256'] and sha(d/'comparator.stdout')==row['comparator_sha256'];near(row['cpu_s'],n['total_cpu_s'])
  all_runs.append(dict(**step,cpu_s=n['total_cpu_s'],native_exit=0,comparator_exit=0,posts=len(posts)))
  if not step['warmup']:samples[step['case']].append(n['total_cpu_s'])
 out={k:comparison(samples[k],[x['e2e']['totalCpuMs']/1000 for x in ref[k]['samples']]) for k in plan['ordered_cases']}
 for k,v in out.items():near(v['local']['median'],sm['case_summaries'][k]['median'])
 return dict(lifetimes=216,warmups=54,measured=162,runs=all_runs,units=out)

def games(plan):
 D=P/'games12';m=load(D/'manifest.json');sm=load(D/'summary.json');assert sm['complete'] and sm['complete12'] and sm['failure'] is None
 assert m['schedule']==plan['games_schedule'] and len(sm['runs'])==48
 assert m['engine_sha256']==sm['artifact_sha256_after']==plan['engine_sha256'] and m['input_sha256']==sm['input_sha256_after']
 for f,h in m['input_sha256'].items():assert sha(f)==h,('collector input',f)
 gs={g['id']:g for g in load(S/'conformance/gate-replay/accepted-games-v1.json')['games']};rf={g['gameId']:g for g in load(S/'performance/selected-games-reference.json')['games']};samples={k:[] for k in plan['ordered_games']};runs=[];unresolved=0;total_posts=0
 for i,(step,row) in enumerate(zip(plan['games_schedule'],sm['runs'])):
  assert all(row[k]==v for k,v in step.items()) and row['failure'] is None
  d=D/f"{i:02d}-{step['game']}-r{step['repeat']}";n=native(d/'native.json',plan);z=load(d/'result.json');a=load(d/'replay.json');tap=load(d/'wire/receipt.json');g=gs[step['game']]
  assert z['failure'] is None and z['comparator_exit']==0 and (d/'comparator.stderr').read_bytes()==b'' and a['pass'] is True and a['selectedGameIds']==[g['id']]
  assert len(a['games'])==len(a['processes'])==1 and a['games'][0]=={'id':g['id'],'family':g['family'],'searches':len(g['plies']),'pass':True}
  owned=a['processes'][0];assert owned['code']==0 and owned['signal'] is None and owned['forced'] is False and owned['gameIds']==[g['id']]
  assert tap['failure'] is None and tap['pending'] is None and tap['launcherExit']==dict(code=0,signal=None) and tap['native']['pid']==n['native_pid']
  assert n['argv']==[plan['engine'],'--diagnostic-seed-command'];assert tap['launcherPid']==n['supervisor_pid']
  streams={k:(d/'wire'/f'{k}.raw').read_bytes() for k in ['stdin','stdout','stderr']}
  for k,b in streams.items():
   t=tap['raw'][k];assert t['sha256']==hashlib.sha256(b).hexdigest() and t['bytes']==t['observedBytes']==len(b) and t['discardedObservedBytes']==0
  out=lines(streams['stdout']);err=lines(streams['stderr']);inp=lines(streams['stdin']);assert out.pop(0)=='cm_parm default'
  expected_in=['xboard','new','force','post','easy','level 0 5 0',*g['initialMoves'],'cm_parm default'];seeds=[]
  for j,q in enumerate(g['plies']):
   cmds=g['personalityCommands'][q['personality']];assert out[:len(cmds)]==cmds;del out[:len(cmds)];assert out.pop(0)==f"king_seed {q['seed']}"
   e=q['expected'];ps=[post(v,True) for v in out[:len(e['posts'])]];assert ps==e['posts'];del out[:len(ps)];assert out.pop(0)=='move '+e['move']
   if e['result'] is not None:assert out.pop(0)==e['result']
   total_posts+=len(ps);seeds.append(f"KING_SEARCH_SEED seed={q['seed']}");expected_in+=['force',*cmds,f"king_seed {q['seed']}",f"time {q['clockCentiseconds']}",f"otim {q['clockCentiseconds']}",'go']
   t=tap['searches'][j];assert t['move']==e['move'] and t['wallNs']>0
   for b in ['beforeWrite','afterData']:assert t[b]['available'] and t[b]['pid']==n['native_pid'] and t[b]['lastProcessor']==14
   assert t['cpuSeconds'] is None or t['cpuSeconds']>0
   if not step['warmup'] and t['cpuSeconds'] is None:unresolved+=1
  assert out==[] and err==seeds and inp==expected_in+['quit'] and len(tap['searches'])==len(g['plies'])
  assert owned['stdoutRecords']==len(lines(streams['stdout'])) and owned['stderrRecords']==len(err) and owned['outputBytes']==len(streams['stdout'])+len(streams['stderr'])
  near(row['cpu_s'],n['total_cpu_s']);assert sha(d/'result.json')==row['result_sha256'];runs.append(dict(**step,cpu_s=n['total_cpu_s'],native_exit=0,comparator_exit=0,searches=len(g['plies'])))
  if not step['warmup']:samples[g['id']].append(n['total_cpu_s'])
 out={k:comparison(samples[k],[v/1000 for v in rf[k]['fullLifetimeCpuMs']['samples']]) for k in plan['ordered_games']}
 for k,v in out.items():near(v['local']['median'],sm['game_summaries'][k]['cpu_s']['median'])
 return dict(lifetimes=48,warmups=12,measured=36,searches=2528,semantic_posts=total_posts,unresolved_measured_search_cpu=unresolved,runs=runs,units=out)

def tick_delta(d):
 a=load(d/'context-before.json');b=load(d/'context-after.json');ans={}
 for cpu in ['cpu14','cpu15']:
  read=lambda c:[int(v) for v in next(x for x in c['proc_stat'].splitlines() if x.startswith(cpu+' ')).split()[1:]]
  x,y=read(a),read(b);ds=[v-u for u,v in zip(x,y)];assert min(ds)>=0
  ans[cpu]=dict(all_field_deltas=ds,whole_nonidle_ticks=sum(ds[i] for i in [0,1,2,5,6,7]),iowait_ticks=ds[4])
 assert a['helper_affinity']==b['helper_affinity']==H
 return ans

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--check-inputs-only',action='store_true');pa.add_argument('--output',type=Path,required=True);args=pa.parse_args();plan=load(P/'plan.json');report=dict(complete=False,failures=[],scope='reported-only; no performance acceptance, PMU or universal calibration')
 try:
  report['inputs']=inputs(plan)
  if not args.check_inputs_only:
   terminals=load(P/'collector-terminals.json')
   for k in ['ordinary54','games12']:assert terminals[k]['exit_code']==0 and terminals[k]['actual_terminal_chunk'],('missing actual terminal',k)
   report['terminals']=terminals;report['ordinary54']=ordinary(plan);report['games12']=games(plan)
   for k in ['ordinary54','games12']:
    units=report[k]['units'];a=sum(v['local']['median'] for v in units.values());b=sum(v['reference']['median'] for v in units.values());report[k]['sum_unit_medians_s']=a;report[k]['reference_sum_unit_medians_s']=b;report[k]['ratio_of_sums']=a/b;report[k]['cpu_context']=tick_delta(P/k)
   report['descriptive_only']=True;report['qualified_performance_pass']=False
  report['complete']=True
 except Exception as e:
  report['failures'].append(dict(type=type(e).__name__,message=str(e)));save(args.output,report);raise
 save(args.output,report);print(json.dumps(dict(complete=True,output=str(args.output))))
if __name__=='__main__':main()
