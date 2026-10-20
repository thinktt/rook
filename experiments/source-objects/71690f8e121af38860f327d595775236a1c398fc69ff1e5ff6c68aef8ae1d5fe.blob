#!/usr/bin/env python3
"""Run required seed controls; preserve original optional-control invocation failure."""
import hashlib,json,os,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
OLD=P.parent/'complete117-generic-pregate-20261018'
OUT=P.parent/'complete117-generic-seed-controls-20261018'
KIT=Path('/home/legolas/king-spec/conformance/gate-replay')
ENGINE=P.parent/'complete117-generic-build-20261018/rook2-exact'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def run(name,argv,env=None):
 with (OUT/(name+'.stdout')).open('xb') as o,(OUT/(name+'.stderr')).open('xb') as e:
  r=subprocess.run(argv,stdout=o,stderr=e,env=env)
 write(OUT/(name+'.terminal.json'),{'argv':argv,'exit_code':r.returncode})
 assert r.returncode==0,(name,r.returncode)
def main():
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 b=json.loads((OLD/'binding.json').read_text());assert sha(ENGINE)==b['engine_sha256']
 for path,h in b['before'].items():assert sha(path)==h
 c=json.loads((OLD/'combined.json').read_text());assert c['pass'] and c['completeFocusedReplay']
 OUT.mkdir()
 write(OUT/'binding.json',{'engineSha256':sha(ENGINE),'originalBindingSha256':sha(OLD/'binding.json'),
  'originalFailureSha256':sha(OLD/'failure.json'),'scripts':{str(p):sha(p) for p in [Path(__file__),P/'direct_wire_tap.mjs',KIT/'seed-command-controls.mjs',KIT/'seed-persistence-controls.mjs']},
  'scope':'Required controls only. Do not expose a new seed-sequence CLI to satisfy the optional check; it is outside this engine capability.'})
 run('seed-command-controls',['node',str(KIT/'seed-command-controls.mjs'),'--',str(ENGINE)])
 config=OUT/'seed-persistence-controls.tap.json'
 write(config,{'version':1,'argv':[str(ENGINE),'--diagnostic-seed-command'],'image':str(ENGINE),
  'directory':str(OUT/'seed-persistence-controls.raw'),'maxBytes':32*1024*1024})
 env=os.environ.copy();env['ROOK2_DIRECT_TAP_CONFIG']=str(config)
 run('seed-persistence-controls',['node','--import',str(P/'direct_wire_tap.mjs'),str(KIT/'seed-persistence-controls.mjs'),'--',str(ENGINE)],env)
 raw=json.loads((OUT/'seed-persistence-controls.raw/receipt.json').read_text());assert raw['failure'] is None and raw['native'] and raw['exit']=={'code':0,'signal':None}
 for path,h in b['before'].items():assert sha(path)==h
 write(OUT/'outcome.json',{'complete':True,'engineSha256':sha(ENGINE),'optionalSequenceControlApplicable':False,'requiredSeedControlsPassed':True,'scope':'Untimed generic117 candidate; old optional-control invocation failure retained'})
 print(json.dumps({'complete':True,'output':str(OUT)}))
if __name__=='__main__':main()
