#!/usr/bin/env python3
# Run the authorized attempt, preserve every failed stage, reconcile separately.
import argparse,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
P=Path(__file__).parent;E=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--label',default='02-20261018');args=a.parse_args();label=args.label
assert all(c.isalnum() or c in '_-' for c in label)
rec={'complete':False,'failure':None,'stages':[],'affinity':sorted(os.sched_getaffinity(0))}
try:
 for stage in ['run','reconcile']:
  cmd=[sys.executable,str(P/(stage+'.py')),'--label',label];stdout=P/(label+'-'+stage+'.stdout');stderr=P/(label+'-'+stage+'.stderr')
  with stdout.open('xb') as out,stderr.open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  rec['stages'].append({'command':cmd,'exit_code':r.returncode,'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)})
  assert r.returncode==0,stage+' failed'
 rec['complete']=True
except BaseException as error:rec['failure']=f'{type(error).__name__}: {error}'
finally:
 rec['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest=P/(label+'-pipeline.json')
 with dest.open('x') as f:json.dump(rec,f,indent=2);f.write('\n')
print(json.dumps(rec));sys.exit(0 if rec['complete'] else 1)
