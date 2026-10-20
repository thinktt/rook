#!/usr/bin/env python3
"""Offline original three replay checks plus independent raw/counter closure; no engine."""
from raw_model import *
import os,subprocess
P=Path(__file__).resolve().parent
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def main():
 assert sorted(os.sched_getaffinity(0))==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 plan=load(P/'plan.json');out=Path(plan['output']);terminal=load(out/'tool-terminal.json')
 assert terminal['actual_tool_terminal_observed'] and terminal['exit_code']==0
 result=load(out/'result.json');assert result['complete'] and result['failure'] is None and result['attempted_cases']==result['engine_lifetimes']==3
 assert [x['case'] for x in result['cases']]==CASES and len({x['native_pid'] for x in result['cases']})==3
 pins=load(out/'input-closure.json');assert all(sha(p)==h for p,h in pins.items())
 target=out/'reconciliation';assert not target.exists();target.mkdir();report_paths=[];summaries=[]
 proof=dict(complete=False,failure=None,engine_execution_count=0,original_offline_checks=0,cases=[])
 try:
  for case,stored in zip(CASES,result['cases']):
   d=out/case;report=d/'checker.stdout';row,payloads=replay(report,plan['engine'],case)
   command=load(d/'command.json');assert command['argv']==['/usr/bin/node',str(SPEC/'profiling/replay-check.mjs'),'--case',case,'--','/usr/bin/taskset','-c','14',plan['engine']] and command['exit_code']==0 and command['cleanup'] is None
   assert (d/'checker.stderr').read_bytes()==b''
   for name,b in payloads.items():assert (d/name).read_bytes()==b
   probes=list((out/'probes'/case).iterdir());assert len(probes)==1 and probes[0].name==f"native-{row['pid']}.json" and probes[0].is_file() and not probes[0].is_symlink() and probes[0].stat().st_size<=1048576
   summary=counters(load(probes[0]),row['pid']);assert summary==stored['summary'] and row['pid']==stored['native_pid'] and sha(probes[0])==stored['probe_sha256'] and sha(report)==stored['checker_sha256']
   report_paths.append(str(report));proof['cases'].append(dict(case=case,native_pid=row['pid'],summary=summary,raw_sha256={name:sha(d/name) for name in payloads},probe_sha256=sha(probes[0])))
  argv=['/usr/bin/node',str(P/'recheck.mjs'),*report_paths]
  with (target/'original-check.stdout').open('xb') as stdout,(target/'original-check.stderr').open('xb') as stderr:
   child=subprocess.Popen(argv,stdout=stdout,stderr=stderr,start_new_session=True)
   try:code=child.wait(timeout=30)
   except BaseException:
    child.kill();child.wait();raise
  write(target/'original-check-command.json',dict(argv=argv,pid=child.pid,exit_code=code,actual_child_return_observed=True))
  assert code==0 and (target/'original-check.stderr').read_bytes()==b''
  checked=load(target/'original-check.stdout');assert checked==dict(offlineOnly=True,originalCheckReplayCount=3,selectedCases=CASES)
  proof['original_offline_checks']=3;assert all(sha(p)==h for p,h in pins.items());proof['input_pins_unchanged']=True;proof['complete']=True
 except BaseException as e:proof['failure']=repr(e);raise
 finally:write(target/'independent-reconciliation.json',proof)
 print(json.dumps(dict(complete=True,original_offline_checks=3,probe_rows=96,engine_execution_count=0,performance_claim=False)))
if __name__=='__main__':main()
