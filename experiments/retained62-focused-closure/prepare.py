#!/usr/bin/python3
"""Freeze finite scope and capture inputs before any native process is launched."""
import ast,hashlib,json,os,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def put(p,d):
    with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
R=Path('/home/legolas/rook2'); S=Path(__file__).parent
B=Path(sys.argv[1]); assert B.is_dir()
H=[0,1,2,3,4,5,8,9,10,11,12,13];assert sorted(os.sched_getaffinity(0))==H
handoff=R/'experiments/retained62-game-handoff/manifest.json'
assert sha(handoff)=='2a28ea0b5daaa3bb0d8911256e44d6b7ed6fa96648fc231cfb46422c8c362e16'
h=load(handoff);image=h['artifacts']['rook2']['origin'];identity=h['artifacts']['rook2']['sha256']
assert sha(image)==identity=='01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d'
assert Path(image).stat().st_size==7118376 and Path(image).stat().st_mode&0o777==0o555
pins={str(handoff):sha(handoff),image:identity,'/usr/bin/python3':sha('/usr/bin/python3'),'/usr/bin/node':sha('/usr/bin/node')}
for row in h['specification']['released_bindings']:
    assert sha(row['path'])==row['sha256'];pins[row['path']]=row['sha256']
for f in ['native_launch.py','capture.mjs','reconcile.py','run.py','prepare.py']:
    pins[str(S/f)]=sha(S/f)
for f in S.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
subprocess.run(['/usr/bin/node','--check',str(S/'capture.mjs')],check=True)
A=Path('/home/legolas/rook2-experiments/original-worktree/evidence')
old=A/'exttsp-profiled-games12-execution-20261020-01'
summary=old/'games12/summary.json'
assert sha(summary)=='b23fa241e210c98e7511172e5969a2e781eaceb53ab7a8797efe21bb0ba2d6f8'
for f in [summary,old/'collector-terminals.json',old/'independent-tool-terminals.json',R/'tools/account_native.py',R/'tools/tap_wire.mjs']:
    pins[str(f)]=sha(f)
K=Path('/home/legolas/king-spec/conformance/gate-replay')
launcher=['/usr/bin/python3',str(S/'native_launch.py'),image,'--']
stages={}
for name in ['continuous','seed-command-controls','seed-persistence-controls','independent']:
    d=B/name;d.mkdir()
    if name=='independent':continue
    (d/'native').mkdir();(d/'wire').mkdir()
    expected=[launcher+['--diagnostic-seed-command']]
    if name=='seed-command-controls':expected=expected*10+[launcher]
    config={'version':1,'image':image,'rawRoot':str(d/'wire'),'expectedCalls':expected,'maxBytes':64*1024*1024}
    put(d/'tap-config.json',config);pins[str(d/'tap-config.json')]=sha(d/'tap-config.json')
    args=['/usr/bin/node','--import',str(S/'capture.mjs'),str(K/(name+'.mjs'))]
    if name=='continuous':args+=['--report',str(d/'report.json')]
    args+=['--',*launcher];stages[name]=args
plan={'schema':'rook2-exact62-focused-lane-plan-v1','repo':str(R),'kit':str(K),'rawRoot':str(B),
      'image':image,'imageSha256':identity,'imageBytes':7118376,'launcherCommand':launcher,
      'helperCpus':H,'nativeCpus':[14],'ownedCpu15':False,'reuseSummary':str(summary),'pins':pins,
      'retainedSourceBuildIdentityFromFrozenHandoff':{'source':h['source'],'build':h['build']},
      'stages':stages,'aggregateSeconds':900,'nativeAttempts':13,'searches':11,
      'scope':'reuse original repeat0 independent12; one continuity8, standard seed11 and persistence3; no retries or timing/performance collection',
      'commandsUseUnchangedReleasedTools':True,'releasedPerControlLimitsUnchanged':True,'optionalSeedSequenceConflict':False}
put(B/'plan.json',plan)
print(json.dumps({'plan':str(B/'plan.json'),'planSha256':sha(B/'plan.json'),'nativeAttempts':13,'freshSearches':11}))
