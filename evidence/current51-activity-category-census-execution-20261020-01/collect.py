#!/usr/bin/env python3
"""Three diagnostic-only direct released replays; no warmup/retry/CPU estimator."""
from raw_model import *
import os,signal,subprocess,time
P=Path(__file__).resolve().parent
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def identity(pid):
 try:
  a=Path(f'/proc/{pid}/stat').read_text().rsplit(') ',1)[1].split()
  return dict(pid=pid,start=a[19],pgid=int(a[2]),state=a[0])
 except (FileNotFoundError,ProcessLookupError):return None
def active(token):
 now=identity(token['pid']);return now is not None and now['start']==token['start'] and now['pgid']==token['pgid'] and now['state']!='Z'
def observe(child,owned):
 # Only this owned Node's direct detached native children, never shared process groups.
 try:ids=Path(f'/proc/{child.pid}/task/{child.pid}/children').read_text().split()
 except FileNotFoundError:ids=[]
 for x in ids:
  t=identity(int(x))
  if t and t['pgid']==t['pid'] and t['pgid']!=os.getpgrp():owned[(t['pid'],t['start'])]=t
 def same(t):return t['pgid']==t['pid'] and t['pgid']!=os.getpgrp()
 assert all(same(t) for t in owned.values())
def stop_owned(child,owned):
 observe(child,owned)
 def send(sig):
  for t in list(owned.values()):
   if active(t):
    try:os.killpg(t['pgid'],sig)
    except ProcessLookupError:pass
 send(signal.SIGTERM);until=time.monotonic()+5
 while time.monotonic()<until and any(active(t) for t in owned.values()):child.poll();time.sleep(.02)
 send(signal.SIGKILL);until=time.monotonic()+5
 while time.monotonic()<until and any(active(t) for t in owned.values()):child.poll();time.sleep(.02)
 try:code=child.wait(timeout=max(.01,until-time.monotonic()))
 except subprocess.TimeoutExpired:code=None
 return dict(node_returncode=code,node_reaped=code is not None,remaining_owned_active=[t for t in owned.values() if active(t)],tracked_owned=list(owned.values()))
def admission(plan):
 assert sorted(os.sched_getaffinity(0))==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert plan['cases']==CASES and plan['lifetimes']==3 and plan['overall_seconds']==180 and plan['probe_cap_bytes']==1048576 and plan['no_retries']
 clearance=load(P/'execution-clearance.json');assert clearance['launch_authorized'] is True and clearance['plan_sha256']==sha(P/'plan.json') and clearance['parent_review_sha256']
 assert all(plan[x] is True for x in ['parent_review_complete','source_review_complete','focused_complete','all_owned_jobs_closed','launch_authorized'])
 pins=dict(plan['immutable_inputs'])
 for name in ['parent_review','source_freeze','source_manifest','source_review','build_receipt','image_freeze','build_terminal','focused_proof','focused_terminal','source_archive_receipt']:
  row=plan[name];assert row and row['sha256'] and sha(row['path'])==row['sha256'];pins[row['path']]=row['sha256']
 assert clearance['parent_review_sha256']==plan['parent_review']['sha256']
 assert plan['engine_sha256'] and sha(plan['engine'])==plan['engine_sha256'];pins[plan['engine']]=plan['engine_sha256']
 receipt=load(plan['build_receipt']['path']);frozen=load(plan['image_freeze']['path'])
 assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot' and receipt['binary_output']['sha256']==frozen['sha256']==plan['engine_sha256']
 assert receipt['source_sha256_before']==receipt['source_sha256_after'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']
 assert receipt['source_sha256_before']==plan['source_sha256'] and receipt['tool_sha256_before']==plan['tool_source_sha256']
 assert len(receipt['tool_sha256_before'])==23 and frozen['mode']=='0555' and Path(plan['engine']).stat().st_mode & 0o777==0o555
 assert receipt['mode']=='generic' and receipt['target_cpu']=='x86-64' and receipt['target_triple']=='x86_64-unknown-linux-gnu'
 assert 'profile-' not in receipt['environment_overrides']['RUSTFLAGS']
 assert plan['source_graph_sha256'] and plan['native_test_scope']=='Focused diagnostic guards only; no full-native/broad qualification' 
 for rel,h in (receipt['source_sha256_before']|receipt['tool_sha256_before']).items():pins[str(Path(plan['build_receipt']['path']).parent/'source-before'/rel)]=h
 for name in ['build_terminal','focused_terminal']:
  t=load(plan[name]['path']);assert t['actual_tool_terminal_observed'] and t['exit_code']==0
 assert all(sha(p)==h for p,h in pins.items())
 pins[str(P/'plan.json')]=sha(P/'plan.json');pins[str(P/'execution-clearance.json')]=sha(P/'execution-clearance.json')
 return pins

def main():
 plan=load(P/'plan.json');pins=admission(plan);output=Path(plan['output']);assert not output.exists();output.mkdir()
 write(output/'input-closure.json',pins);write(output/'plan.json',plan)
 result=dict(complete=False,failure=None,cases=[],attempted_cases=0,performance_claim=False,engine_lifetimes=0);deadline=time.monotonic()+180
 try:
  for case in CASES:
   assert time.monotonic()<deadline
   d=output/case;d.mkdir();probes=output/'probes'/case;probes.mkdir(parents=True);assert not list(probes.iterdir())
   env=dict(os.environ)
   assert not any(env.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','NODE_OPTIONS','LLVM_PROFILE_FILE',plan['env_key']])
   pattern=str((probes/'native-%p.json').resolve());env[plan['env_key']]=pattern
   argv=['/usr/bin/node',str(SPEC/'profiling/replay-check.mjs'),'--case',case,'--','/usr/bin/taskset','-c','14',plan['engine']]
   command=dict(argv=argv,env={plan['env_key']:pattern},node_pid=None,exit_code=None,cleanup=None,owned_observations=[])
   child=None;owned={};result['attempted_cases']+=1
   try:
    with (d/'checker.stdout').open('xb') as out,(d/'checker.stderr').open('xb') as err:
     child=subprocess.Popen(argv,stdout=out,stderr=err,env=env,start_new_session=True);command['node_pid']=child.pid
     t=identity(child.pid);assert t and t['pgid']==child.pid;owned[(t['pid'],t['start'])]=t
     while child.poll() is None:
      observe(child,owned);assert time.monotonic()<deadline,'overall180s deadline'
      files=list(probes.iterdir());assert len(files)<=1 and all(x.is_file() and not x.is_symlink() and x.stat().st_size<=1048576 for x in files),'probe cap/nonregular'
      assert (d/'checker.stdout').stat().st_size<=33554432 and (d/'checker.stderr').stat().st_size<=1048576,'wrapper report cap'
      time.sleep(.02)
     code=child.wait();command['exit_code']=code;command['owned_observations']=list(owned.values())
    assert code==0 and (d/'checker.stderr').stat().st_size==0
    row,_=replay(d/'checker.stdout',plan['engine'],case,d)
    files=list(probes.iterdir());assert len(files)==1 and files[0].name==f"native-{row['pid']}.json" and files[0].is_file() and not files[0].is_symlink() and files[0].stat().st_size<=1048576
    summary=counters(load(files[0]),row['pid']);assert not any(active(t) for t in owned.values())
    result['engine_lifetimes']+=1;result['cases'].append(dict(case=case,native_pid=row['pid'],exit=row['exit'],probe=str(files[0]),probe_sha256=sha(files[0]),checker_sha256=sha(d/'checker.stdout'),summary=summary))
   except BaseException:
    if child is not None:command['cleanup']=stop_owned(child,owned)
    raise
   finally:write(d/'command.json',command)
  assert len(result['cases'])==result['engine_lifetimes']==result['attempted_cases']==3 and [x['case'] for x in result['cases']]==CASES
  assert len({x['native_pid'] for x in result['cases']})==3
  assert all(sha(p)==h for p,h in pins.items());result['complete']=True
 except BaseException as e:result['failure']=repr(e);raise
 finally:write(output/'result.json',result)
 print(json.dumps(dict(complete=True,cases=CASES,engine_lifetimes=3,performance_claim=False,output=str(output))))
if __name__=='__main__':main()
