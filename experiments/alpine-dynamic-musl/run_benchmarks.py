import hashlib,json,os,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent
container=['/usr/bin/python3',str(B/'container.py')]
use=json.loads((B/'build-use/receipt.json').read_text());repeat=json.loads((B/'build-repeat/receipt.json').read_text())
assert use['binary_output']['sha256']==repeat['binary_output']['sha256']
assert (B/'artifacts/rook2-musl').read_bytes()==(B/'artifacts/rook2-musl-repeat').read_bytes()
stages=[('standard54',['/usr/bin/python3','/home/legolas/rook2/tools/collect_ordinary.py','--engine','/work/artifacts/rook2-musl','--build-record','/work/build-use/receipt.json','--output','/work/standard54']),('games12',['/usr/bin/python3','/work/run_games_once.py'])]
status={'allComplete':False,'engineSha256':use['binary_output']['sha256'],'repeatBuildExactMatch':True,'stages':[]}
(B/'benchmark-status.json').write_text(json.dumps(status,indent=2)+'\n')
for name,args in stages:
 argv=container+args;t=time.monotonic();stage={'name':name,'argv':argv,'startMonotonic':t,'returncode':None}
 status['stages'].append(stage);(B/'benchmark-status.json').write_text(json.dumps(status,indent=2)+'\n')
 with (B/(name+'-collector.stdout')).open('xb') as a,(B/(name+'-collector.stderr')).open('xb') as z:
  p=subprocess.run(argv,stdout=a,stderr=z,timeout=14400 if name=='games12' else 4000)
 stage.update(returncode=p.returncode,elapsedSeconds=time.monotonic()-t)
 (B/'benchmark-status.json').write_text(json.dumps(status,indent=2)+'\n')
 print(json.dumps(stage),flush=True)
 if p.returncode:raise SystemExit(p.returncode)
status['allComplete']=True;(B/'benchmark-status.json').write_text(json.dumps(status,indent=2)+'\n')
print('Both selected lanes completed.',flush=True)
