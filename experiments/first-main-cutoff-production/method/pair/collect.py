#!/usr/bin/python3
"""One frozen paired54 comparison; original checker/recorder, no gain gate."""
import datetime,json,os,statistics,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/legolas/rook2');sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'tools'))
from compare_ordinary import sha,stop_owned,write
from measure import cgroup_snapshot
HERE=Path(__file__).resolve().parent;B=HERE.parent;SPEC=Path('/home/legolas/king-spec/conformance/profiling')
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def jobs():
 rows=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   exe=os.readlink(p/'exe')
   if Path(exe).name.startswith(('rook2','cargo','rustc','perf','objdump','llvm-profdata','tar','git')):rows.append({'pid':int(p.name),'exe':exe})
  except OSError:pass
 return rows
def context():return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uname':list(os.uname()),'helperAffinity':sorted(os.sched_getaffinity(0)),'cgroups':cgroup_snapshot(),'proc_stat':Path('/proc/stat').read_text(),'loadavg':Path('/proc/loadavg').read_text(),'meminfo':Path('/proc/meminfo').read_text(),'nativeJobs':jobs(),'scope':'Point guest observations only; no exclusive host, formal no-swap/private-memory, PMU or confidence claim.'}
def main():
 plan=json.loads((HERE/'plan.json').read_text());schedule=json.loads((HERE/'schedule.json').read_text());oracle=json.loads((SPEC/'replay-oracle.json').read_text())
 assert sorted(os.sched_getaffinity(0))==H and not jobs()
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS'])
 assert len(schedule)==432 and sum(r['warmup'] for r in schedule)==108
 for p,h in plan['input_sha256'].items():assert sha(p)==h,p
 for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
 out=HERE/'collection';out.mkdir();write(out/'manifest.json',plan);write(out/'context-before.json',context())
 clock=json.loads((B/'lane-clock.json').read_text());deadline=clock['start_monotonic']+1800
 result={'complete':False,'failure':None,'runs':[],'case_summaries':{}};retained=0
 try:
  for index,step in enumerate(schedule):
   engine=plan['variants'][step['variant']]['path'];d=out/f"{index:03d}-{step['case']}-{step['variant']}-r{step['repetition']}";d.mkdir()
   receipt=d/'native.json';cmd=['/usr/bin/node','--import',str(HERE/'tap_wire.mjs'),str(SPEC/'replay-check.mjs'),'--case',step['case'],'--','/usr/bin/python3',str(ROOT/'tools/account_native.py'),'--engine',engine,'--record',str(receipt),'--known-single-process']
   config={'version':1,'expectedArgv':cmd[7:]+oracle['mode'],'maxRawBytes':8388608,'tickHz':os.sysconf('SC_CLK_TCK'),'directory':str(d/'wire'),'nativeExecutable':engine};write(d/'wire-config.json',config)
   env={**os.environ,'ROOK2_WIRE_TAP_CONFIG':str(d/'wire-config.json')};failure=None
   with (d/'comparator.stdout').open('xb') as a,(d/'comparator.stderr').open('xb') as b:
    child=subprocess.Popen(cmd,cwd=ROOT,stdout=a,stderr=b,start_new_session=True,env=env)
    write(d/'launch.json',{'pid':child.pid,'pgid':child.pid,'command':cmd})
    try:
     run_deadline=min(deadline,time.monotonic()+960)
     while child.poll() is None:
      sizes=[(d/n).stat().st_size for n in ['comparator.stdout','comparator.stderr']]
      if time.monotonic()>=run_deadline:failure='host-deadline'
      elif max(sizes)>8388608 or retained+sum(sizes)>268435456:failure='stream-cap'
      if failure:stop_owned(child);break
      time.sleep(.02)
    except BaseException:stop_owned(child);raise
    child.wait()
   retained+=sum((d/n).stat().st_size for n in ['comparator.stdout','comparator.stderr'])
   row={**step,'directory':str(d),'command':cmd,'comparator_exit':child.returncode,'failure':failure}
   try:
    assert failure is None and child.returncode==0 and (d/'comparator.stderr').stat().st_size==0
    assert retained<=268435456 and receipt.stat().st_size<=262144
    n=json.loads(receipt.read_text());c=json.loads((d/'comparator.stdout').read_text());w=json.loads((d/'wire/receipt.json').read_text())
    assert c['status']=='pass' and c['selectedCases']==[step['case']] and len(c['results'])==1
    assert n['failure'] is None and n['native_exit_code']==0 and n['engine_sha256_before']==n['engine_sha256_after']==plan['variants'][step['variant']]['sha256']
    assert n['launcher_sha256']==plan['input_sha256'][str(ROOT/'tools/account_native.py')]
    assert w['failure'] is None and w['pending'] is None and w['launcherExit']=={'code':0,'signal':None} and len(w['searches'])==1
    search=w['searches'][0];assert search['cpuSeconds'] is not None and search['cpuUnavailableReason'] is None
    assert search['beforeWrite']['pid']==search['afterData']['pid']==n['native_pid']
    assert (d/'wire/stdout.raw').read_text()==c['results'][0]['stdout'] and w['raw']['stderr']['bytes']==0
    row.update(cpu_s=n['total_cpu_s'],user_s=n['user_cpu_s'],system_s=n['system_cpu_s'],wall_ns=n['wall_ns'],search_cpu_s=search['cpuSeconds'],search_wall_ns=search['wallNs'],native_receipt_sha256=sha(receipt),comparator_sha256=sha(d/'comparator.stdout'),wire_receipt_sha256=sha(d/'wire/receipt.json'))
   except (AssertionError,OSError,ValueError,KeyError) as e:row['failure']=row['failure'] or repr(e)
   result['runs'].append(row);write(out/'summary.json',result)
   if row['failure']:raise RuntimeError(row['failure'])
   if index%8==7:
    case=step['case'];stats={}
    for variant in ['control','candidate']:
     measured=[r for r in result['runs'] if r['case']==case and r['variant']==variant and not r['warmup']];assert len(measured)==3
     stats[variant]={}
     for metric in ['cpu_s','user_s','system_s','wall_ns','search_cpu_s','search_wall_ns']:
      values=[r[metric] for r in measured];stats[variant][metric]={'samples':values,'minimum':min(values),'median':statistics.median(values),'maximum':max(values)}
    result['case_summaries'][case]={'statistics':stats,'candidate_div_control':stats['candidate']['cpu_s']['median']/stats['control']['cpu_s']['median']}
    print(json.dumps({'case':case,**result['case_summaries'][case]}),flush=True)
  assert len(result['runs'])==432 and len(result['case_summaries'])==54 and not jobs()
  for p,h in plan['input_sha256'].items():assert sha(p)==h,p
  for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
  result['sum_case_medians_s']={v:sum(c['statistics'][v]['cpu_s']['median'] for c in result['case_summaries'].values()) for v in ['control','candidate']}
  result['candidate_div_control']=result['sum_case_medians_s']['candidate']/result['sum_case_medians_s']['control'];result['complete']=True
 except BaseException as e:result['failure']=repr(e);raise
 finally:write(out/'summary.json',result);write(out/'context-after.json',context())
 print(json.dumps({'complete':True,'lifetimes':432,'sum_case_medians_s':result['sum_case_medians_s'],'candidate_div_control':result['candidate_div_control']}),flush=True)
if __name__=='__main__':main()
