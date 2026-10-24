#!/usr/bin/env python3
"""Bounded staged own-PGO survey. Stop on failure; no retries or profile retune."""
import argparse,hashlib,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CONTROL=Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build/rook2-exact')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):
 q=p.with_suffix('.pending');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert out.is_dir();assert not (out/'pipeline.json').exists()
 assert sha(CONTROL)=='5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a'
 env=dict(os.environ,PATH='/usr/bin:/bin');rows=[];state=dict(complete=False,stages=rows,sourceInputs={str(f):sha(f) for f in [ROOT/'Cargo.toml',ROOT/'Cargo.lock',*sorted((ROOT/'src').rglob('*.rs'))]},driverInputs={str(f):sha(f) for f in sorted(HERE.glob('*.py'))})
 write(out/'pipeline.json',state)
 def stage(name,cmd,limit):
  state['active']=name;write(out/'pipeline.json',state);start=time.monotonic()
  with (out/(name+'.stdout')).open('xb') as so,(out/(name+'.stderr')).open('xb') as se:
   child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=so,stderr=se,start_new_session=True)
   try:code=child.wait(timeout=limit)
   except BaseException:
    os.killpg(child.pid,signal.SIGINT)
    try:child.wait(timeout=15)
    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
    raise
  rows.append(dict(stage=name,argv=[str(x) for x in cmd],exit=code,elapsedSeconds=time.monotonic()-start,stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr'))));write(out/'pipeline.json',state)
  print(name,code,flush=True);assert code==0,(name,code)
 def freeze(build,name):
  r=read(build/'receipt.json');source=Path(r['binary_output']['path']);assert sha(source)==r['binary_output']['sha256'];dest=out/name;assert not dest.exists();shutil.copy2(source,dest);assert sha(dest)==sha(source);return dest
 try:
  stage('instrumented-build',['/usr/bin/python3',str(ROOT/'tools/build.py'),'--mode','generic','--bin','rook2','--jobs','4','--pgo-generate',str(out/'profile-raw'),'--output',str(out/'instrumented-build')],300)
  freeze(out/'instrumented-build','rook2-instrumented')
  stage('training',['/usr/bin/python3',str(HERE/'train.py'),'--build',str(out/'instrumented-build'),'--output',str(out/'training')],2500)
  stage('training-reconcile',['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'training')],120)
  stage('use-build',['/usr/bin/python3',str(ROOT/'tools/build.py'),'--mode','generic','--bin','rook2','--jobs','4','--pgo-use',str(out/'training/merged.profdata'),'--training-record',str(out/'training/training.json'),'--ext-tsp-profiled','--output',str(out/'use-build')],300)
  candidate=freeze(out/'use-build','rook2-pgo')
  base=['/usr/bin/python3',str(HERE/'collect.py'),'--control',str(CONTROL),'--candidate',str(candidate),'--build',str(out/'use-build')]
  stage('small',base+['--output',str(out/'small')],1900)
  stage('small-reconcile',['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'small')],120)
  gate=read(out/'small/result.json')['extensionGate'];state['extensionGate']=gate;write(out/'pipeline.json',state)
  if gate['passed']:
   stage('full54',base+['--output',str(out/'full54'),'--full54'],1900)
   stage('full54-reconcile',['/usr/bin/python3',str(HERE/'reconcile.py'),str(out/'full54')],120)
  assert all(sha(Path(f))==h for f,h in state['sourceInputs'].items())
  assert all(sha(Path(f))==h for f,h in state['driverInputs'].items())
  state['complete']=True;state['active']=None;write(out/'pipeline.json',state);print('pipeline complete',flush=True)
 except BaseException as error:
  state['failure']=repr(error);write(out/'pipeline.json',state);raise
if __name__=='__main__':main()
