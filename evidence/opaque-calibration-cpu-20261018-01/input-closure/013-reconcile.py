#!/usr/bin/env python3
"""Independent CPU/raw calibration reconciliation; no engine execution."""
import argparse,json,math,os,statistics,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from guard import authority_preflight,check_pins,load,sha,unprivileged,OPAQUE,SPEC
HERE=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise ValueError(message)
def close(a,b):
 need(isinstance(a,(int,float)) and not isinstance(a,bool) and math.isfinite(a),'nonfinite/nonnumeric')
 need(isinstance(b,(int,float)) and math.isfinite(b),'invalid comparison')
 need(math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-8),'arithmetic mismatch: '+repr((a,b)))
def stats(values):
 need(len(values)==3 and all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in values),'three finite samples required')
 median=statistics.median(values);span=max(values)-min(values)
 return {'samples':values,'min':min(values),'median':median,'max':max(values),'range':span,
  'spreadPercentOfMedian':span/median*100 if median else None}
def compare_stats(actual,values):
 expected=stats(values);need(actual['samples']==values,'sample order/value mismatch')
 for key in ['min','median','max','range','spreadPercentOfMedian']:
  if expected[key] is None:need(actual[key] is None,'unresolved spread must stay unavailable')
  else:close(actual[key],expected[key])
 return expected
def reference_reconcile(reference,workloads,oracle):
 ids=[row['id'] for row in workloads['cases']]
 need(reference['candidate']['sha256']==OPAQUE,'reference opaque identity')
 need((reference['processes'],reference['warmups'],reference['measured'],reference['posts'])==(216,54,162,2496),'reference counts')
 need([row['id'] for row in reference['cases']]==ids and len(reference['measuredRows'])==162,'reference full order/count')
 result={};checks=0
 for index,(case,input) in enumerate(zip(reference['cases'],workloads['cases'])):
  need(case['index']==index and case['personalityId']==input['personality']['id'],'reference case/personality')
  rows=reference['measuredRows'][3*index:3*index+3]
  need([(row['index'],row['id'],row['personalityId'],row['repeat'],row['warmup']) for row in rows]
   ==[(index,case['id'],case['personalityId'],repeat,False) for repeat in [1,2,3]],'reference measuredRows ordering')
  expected=next(row for row in oracle['cases'] if row['id']==case['id'])
  for row in rows:
   close(row['lifetime']['userMs']+row['lifetime']['systemMs'],row['lifetime']['totalMs']);checks+=1
   close(row['search']['userMs']+row['search']['systemMs'],row['search']['cpuMs']);checks+=1
   for scope in ['search','lifetime']:
    close(row[scope]['instructions']/row[scope]['cycles'],row[scope]['ipc']);checks+=1
   semantic={key:row['lastPost'][key] for key in ['depth','score','workThousands','searchId','pv']}
   semantic['pv']=semantic['pv'].strip().replace('0','O')
   need(semantic==expected['posts'][-1],'reference last semantic post')
   close(row['lastPost']['userMs']+row['lastPost']['systemMs'],row['lastPost']['cpuMs']);checks+=1
  for scope in ['search','lifetime']:
   for metric,summary in case[scope].items():
    compare_stats(summary,[row[scope][metric] for row in rows]);checks+=1
  efficiency=case['lastPostWorkEfficiency']
  compare_stats(efficiency['workField'],[row['lastPost']['workThousands'] for row in rows]);checks+=1
  for field,denominator in [('perCpuSecond','cpuMs'),('perWallSecond','wallMs')]:
   need(len(efficiency[field])==3,'reference per-post sample count')
   for value,row in zip(efficiency[field],rows):
    close(value,(row['lastPost']['workThousands']/3000000)/(row['lastPost'][denominator]/1000));checks+=1
  result[case['id']]=compare_stats(case['lifetime']['totalMs'],[row['lifetime']['totalMs'] for row in rows])
  need(result[case['id']]['min']>0,'positive reference lifetime denominator')
 return {'cases':result,'arithmetic_checks':checks,'measured_rows':162,'source':'public reference only; search/PMU/per-post checks are internal-reference arithmetic, NOT local telemetry'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--collection',type=Path,required=True)
 parser.add_argument('--launch-authority',type=Path,required=True);parser.add_argument('--launch-authority-sha256',required=True)
 parser.add_argument('--collector-terminal',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args();collection=args.collection.absolute()
 authority,profile,identity,file=authority_preflight(args.launch_authority,args.launch_authority_sha256,collection,fresh=False)
 terminal=load(args.collector_terminal)
 need(terminal.get('actual_tool_terminal_observed') is True and terminal.get('exit_code')==0,'actual collector outer terminal required')
 need(bool(terminal.get('terminal_chunk_id')) and terminal['collection']==str(collection),'collector terminal binding')
 need(terminal['collector_sha256']==authority['collector_sha256'] and terminal['engine_sha256']==OPAQUE,'collector terminal exact identities')
 manifest=load(collection/'manifest.json');summary=load(collection/'summary.json')
 need(manifest['schema']=='rook2-opaque-calibration54-cpu-revision02','manifest schema')
 need(manifest['profile']==profile and manifest['engine_sha256']==OPAQUE and manifest['engine_file_identity']==file,'profile/sourceartifact identity')
 expected_pins=dict(authority['pins']);expected_pins[str(args.launch_authority.resolve())]=args.launch_authority_sha256
 need(manifest['input_sha256']==summary['input_sha256_after']==expected_pins,'before/after exact dependency closure')
 for name,row in manifest['input_snapshots'].items():need(sha(collection/row['snapshot'])==expected_pins[name]==row['sha256'],'original snapshot bytes')
 need(set(manifest['input_snapshots'])==set(expected_pins),'snapshot closure incomplete')
 check_pins(expected_pins)
 need(summary['complete'] is True and summary['failure'] is None and len(summary['runs'])==216,'whole collection completion')
 ids=profile['cases'];schedule=[dict(case=case,repeat=repeat,warmup=repeat==0) for case in ids for repeat in range(4)]
 need(manifest['schedule']==schedule,'full216 schedule')
 expected_directories={f"{index:03d}-{step['case']}-r{step['repeat']}" for index,step in enumerate(schedule)}
 actual_directories={path.name for path in collection.iterdir() if path.is_dir() and path.name[:3].isdigit()}
 need(actual_directories==expected_directories,'raw lifetime directory closure')
 reference=load(profile['reference']['path']);workloads=load(SPEC/'workloads.json');oracle=load(SPEC/'replay-oracle.json')
 references=reference_reconcile(reference,workloads,oracle)
 args.output.mkdir();command=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/node',str(HERE/'reconcile_raw.mjs'),str(collection),str(args.output/'raw-replay')]
 with (args.output/'raw-check.stdout').open('xb') as out,(args.output/'raw-check.stderr').open('xb') as err:
  child=subprocess.run(command,stdout=out,stderr=err)
 write=lambda path,value:Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
 write(args.output/'raw-check-exit.json',{'command':command,'exit_code':child.returncode,'actual_child_return_observed':True})
 need(child.returncode==0 and not (args.output/'raw-check.stderr').stat().st_size,'independent original checkReplay failed')
 raw=load(args.output/'raw-replay/verification.json');need(raw['complete'] is True and raw['lifetimes']==216,'raw216 proof')
 samples={case:[] for case in ids};user={case:[] for case in ids};system={case:[] for case in ids};warmups=0
 for index,step in enumerate(schedule):
  directory=collection/f"{index:03d}-{step['case']}-r{step['repeat']}";native=load(directory/'native.json');row=summary['runs'][index]
  for key in ['case','repeat','warmup']:need(row[key]==step[key],'collector row schedule')
  need(native['failure'] is None and native['native_exit_code']==native['native_wait_status']==0,'actual native terminal')
  need(native['supervisor_signals']==[] and native['exec_error'] is None and native['native_post_exec_observation_error'] is None,'native/supervisor interruption or readback failure')
  need(native['engine_sha256_before']==native['engine_sha256_after']==OPAQUE,'native artifact changed')
  need(native['engine_file_before']==native['engine_file_after']==file and native['engine_file_after_error'] is None,'native owner/mode/xattr changed')
  need(native['launcher_sha256']==authority['supervisor_sha256'],'local supervisor pin')
  need(native['python_executable_sha256']==authority['pins'][authority['python']],'supervisor Python pin')
  need(native['supervisor_affinity']==profile['helpers'],'supervisor housekeeping')
  pre=native['native_pre_exec'];post=native['native_post_exec'];pid=native['native_pid'];supervisor=native['supervisor_pid']
  need(pre=={'pid':pid,'pgid':supervisor,'affinity':[14]},'pre-exec placement')
  need(post['path']==identity['path'] and post['affinity']==[14] and post['pgid']==supervisor and post['tasks']==[str(pid)],'single post-exec task placement')
  need(unprivileged(post['privileges']) and post['privileges']['ppid']==supervisor,'post-execUID/capabilities/parent')
  close(native['user_cpu_s']+native['system_cpu_s'],native['total_cpu_s'])
  need(native['total_cpu_s']>0,'positive lifetimeCPU')
  for key,native_key in [('cpu_s','total_cpu_s'),('user_s','user_cpu_s'),('system_s','system_cpu_s')]:close(row[key],native[native_key])
  if step['warmup']:warmups+=1
  else:
   samples[step['case']].append(native['total_cpu_s']);user[step['case']].append(native['user_cpu_s']);system[step['case']].append(native['system_cpu_s'])
 need(warmups==54,'exact excluded warmups')
 ratios=[]
 for case in ids:
  local=stats(samples[case]);recorded=summary['case_summaries'][case]
  need(recorded['samples']==local['samples'],'local sample summary')
  for old,new in [('minimum','min'),('median','median'),('maximum','max')]:close(recorded[old],local[new])
  close(recorded['range_over_median'],local['range']/local['median'])
  ref=references['cases'][case]
  ratios.append({'case':case,'local_lifetime_cpu_s':local,'local_user_s_samples':user[case],'local_system_s_samples':system[case],
   'reference_lifetime_totalMs':ref,'median_cpu_ratio':local['median']*1000/ref['median'],
   'descriptive_sample_endpoint_ratio_envelope':[local['min']*1000/ref['max'],local['max']*1000/ref['min']],
   'unit_conversion':'local seconds *1000 / reference lifetime.totalMs; no wall ratio'})
 close(summary['sum_case_medians_s'],sum(statistics.median(samples[case]) for case in ids))
 check_pins(expected_pins);authority_preflight(args.launch_authority,args.launch_authority_sha256,collection,fresh=False)
 write(args.output/'verification.json',{'complete':True,'lifetimes':216,'warmups_excluded':54,'measured':162,'cases':54,
  'raw_checkReplay_lifetimes':216,'actual_raw_check_child_exit':child.returncode,'reference_arithmetic':references,
  'ratios':ratios,'qualified_pass':False,'universal_hardware_factor':None,'wall_ratios':None,
  'captured_local_search_cpu_wall_pmu':'unavailable; do not derive terminalN/R orperpostCPU from rawposts',
  'scope_differences':['local nativewait4 includes small Python child pre-exec prefix','one post-exec task/affinity/UID/capability observation only; no continuous descendants','reference externalPMU attach stop and dedicated cgroup setup absent; existing local cgroups recorded only','reference whole-lifetime wall boundary incompatible; no wallratio'],
  'collector_terminal_sha256':sha(args.collector_terminal),'engine_sha256':OPAQUE,'input_pins':expected_pins,
  'outer_reconciler_actual_tool_terminal_required':True})
 print(json.dumps({'complete':True,'cases':54,'measured':162,'calibration_only':True}))
if __name__=='__main__':main()
