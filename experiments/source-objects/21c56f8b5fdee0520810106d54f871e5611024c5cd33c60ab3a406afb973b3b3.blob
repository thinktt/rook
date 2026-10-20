"""One original full corpus on the exact existing adapter; no build/unit/replay path."""
import json,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from guard import HERE,clearance,load,sha,write,check_sources,check_dependencies

def main():
 plan=clearance();check_sources(plan);check_dependencies(plan)
 out=Path(plan['output']['diagnostic']);assert not out.exists(),'one fresh corpus attempt only'
 out.mkdir();raw=out/'raw-cases';raw.mkdir();adapter=Path(plan['partial01']['build'])/'rook2-diag-exact'
 result=dict(complete=False,failure=None,stages=[],adapter_sha256=sha(adapter),units209_reused=True,build_and_archive_reused=True,failed01_outer_exit_preserved=1)
 try:
  command=['/usr/bin/node','/home/legolas/king-spec/conformance/run.mjs']
  for filename in plan['fixtures']:command+=['--fixtures',filename]
  command+=['--',sys.executable,str(HERE/'record_case.py'),'--adapter',str(adapter),'--records',str(raw)]
  with (out/'conformance.stdout').open('xb') as a,(out/'conformance.stderr').open('xb') as b:
   child=subprocess.Popen(command,cwd=plan['home_source'],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=a,stderr=b);code=child.wait()
  result['stages'].append(dict(command=command,pid=child.pid,exit_code=code,actual_child_return_observed=True,stdout_sha256=sha(out/'conformance.stdout'),stderr_sha256=sha(out/'conformance.stderr')))
  assert code==0,'original conformance runner failed'
  report=load(out/'conformance.stdout');assert report['pass'] and len(report['results'])==7673 and not (out/'conformance.stderr').stat().st_size
  check_sources(plan);check_dependencies(plan);assert sha(adapter)==result['adapter_sha256']
  result.update(complete=True,cases=7673,operations=117,whole_files=115)
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 finally:write(out/'verification.json',result)
 print(json.dumps(result));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
