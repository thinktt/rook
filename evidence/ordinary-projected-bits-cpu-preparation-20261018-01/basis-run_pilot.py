#!/usr/bin/env python3
"""One frozen matched full-byte-pair generic development pilot; unchanged strict comparator."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
OUT=ROOT/'evidence/full-byte-pair-relations-cpu-pilot-20261018-01'
H=[0,1,2,3,4,5,8,9,10,11,12,13]
sys.path.insert(0,str(ROOT/'tools'))
from measure import cgroup_snapshot
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
 with Path(p).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def native_jobs():
 found=[]
 for d in Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   exe=os.readlink(d/'exe');name=Path(exe).name
   if name.startswith(('rook2','cargo','rustc','callgrind','valgrind','git','objdump','readelf','llvm-profdata','nm','tar')):found.append({'pid':int(d.name),'executable':exe})
  except OSError:pass
 return found
def context():
 return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'helper_affinity':sorted(os.sched_getaffinity(0)),'uname':list(os.uname()),'proc_stat':Path('/proc/stat').read_text(),'loadavg':Path('/proc/loadavg').read_text(),'native_jobs':native_jobs(),'cgroups':cgroup_snapshot(),'scope':'Point guest observations only. No host/global isolation or continuous descendant/sibling exclusivity claim.'}
def main():
 assert sorted(os.sched_getaffinity(0))==H
 assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 from guard import validate_gate
 plan,clearance,_=validate_gate()
 assert clearance['parent_review_complete'] and clearance['all_owned_jobs_closed']
 assert clearance['plan_sha256']==sha(P/'plan.json') and clearance['driver_sha256']==sha(Path(__file__))
 assert plan['cases']==['profile-01','profile-02','profile-04','profile-05','profile-29','profile-35','profile-08']
 for path,h in clearance['dependencies'].items():assert sha(path)==h,path
 for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
 assert not native_jobs(),'Unclosed engine/build/profile/codegen/Git/archive job'
 OUT.mkdir()
 write(OUT/'context-before.json',context())
 write(OUT/'plan.json',plan)
 result={'complete':False,'failure':None,'engine_lifetimes':0,'cases':[]}
 write(OUT/'launch.json',{'driver_pid':os.getpid(),'driver_sha256':sha(Path(__file__)),'clearance_sha256':sha(P/'launch-clearance.json'),'plan_sha256':sha(P/'plan.json')})
 try:
  for case in plan['cases']:
   argv=[sys.executable,str(ROOT/'tools/compare_ordinary.py'),'--case',case,'--output',str(OUT/case)]
   for name,v in plan['variants'].items():argv+=['--variant',name+'='+v['path']]
   with (OUT/(case+'.stdout')).open('x') as out,(OUT/(case+'.stderr')).open('x') as err:
    child=subprocess.Popen(argv,cwd=ROOT,stdout=out,stderr=err)
    code=child.wait()
   write(OUT/(case+'-terminal.json'),{'argv':argv,'pid':child.pid,'exit_code':code,'actual_child_return_observed':True})
   summary=load(OUT/case/'summary.json')
   assert code==0 and summary['complete'] and summary['failure'] is None,(case,code,summary.get('failure'))
   assert (OUT/(case+'.stderr')).read_bytes()==b''
   assert len(summary['runs'])==10
   result['engine_lifetimes']+=10
   result['cases'].append({'id':case,'summaries':summary['summaries']})
   print(json.dumps({'case':case,'lifetimes':result['engine_lifetimes'],'summaries':summary['summaries']}),flush=True)
  write(OUT/'context-after.json',context());assert not native_jobs()
  for path,h in clearance['dependencies'].items():assert sha(path)==h,path
  for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
  assert clearance['plan_sha256']==sha(P/'plan.json') and clearance['driver_sha256']==sha(Path(__file__))
  result['complete']=True
 except BaseException as error:
  result['failure']=repr(error)
  write(OUT/'result.json',result)
  raise
 write(OUT/'result.json',result)
 print(json.dumps({'complete':True,'lifetimes':70}),flush=True)
if __name__=='__main__':main()
