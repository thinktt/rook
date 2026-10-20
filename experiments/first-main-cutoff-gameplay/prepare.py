#!/usr/bin/python3
"""Freeze one exact corrected-image behavioral lane; no engines or builds."""
import ast,hashlib,json,os,subprocess,sys
from pathlib import Path
R=Path('/home/legolas/rook2');S=Path(__file__).resolve().parent;B=Path(sys.argv[1]);K=Path('/home/legolas/king-spec/conformance/gate-replay');P=R/'experiments/first-main-cutoff-production';PB=Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01')
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
assert B.is_dir() and not (B/'plan.json').exists()
production=load(P/'result.json');assert production['outcome']=='COMPLETE_DESCRIPTIVE_COMPARISON_NO_PROMOTION' and production['resourceClosure']['allOwnedJobsTerminal']
commit='a8dfb6562c486f7d3e631c3cd3fdf1d00d0c5f69'
assert subprocess.check_output(['git','show',f'{commit}:experiments/first-main-cutoff-production/result.json'],cwd=R)==(P/'result.json').read_bytes()
source=load(PB/'source-freeze.json')
for name,h in source['candidateFiles'].items():assert sha(Path(source['root'])/name)==h,name
for name,h in source['canonicalFiles'].items():assert sha(R/name)==h,name
image=PB/'use-build/rook2-exact';identity='5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a';assert sha(image)==identity
chain=production['artifactChain']
for row in chain.values():assert sha(row['path'])==row['sha256']
launcher=['/usr/bin/python3',str(S/'native_launch.py'),str(image),'--']
commands={
'games':['/usr/bin/node','--import',str(S/'capture.mjs'),str(K/'run.mjs'),'--report',str(B/'games/report.json'),'--',*launcher],
'continuous':['/usr/bin/node','--import',str(S/'capture.mjs'),str(K/'continuous.mjs'),'--report',str(B/'continuous/report.json'),'--',*launcher],
'seed-command-controls':['/usr/bin/node','--import',str(S/'capture.mjs'),str(K/'seed-command-controls.mjs'),'--',*launcher],
'seed-persistence-controls':['/usr/bin/node','--import',str(S/'capture.mjs'),str(K/'seed-persistence-controls.mjs'),'--',*launcher],
'wire':['/usr/bin/python3',str(S/'run_wire.py'),str(B)],
'combine':['/usr/bin/node',str(K/'combine.mjs'),'--report',str(B/'combine/report.json'),'--continuous',str(B/'continuous/report.json'),str(B/'games/report.json')]}
counts={'games':12,'continuous':1,'seed-command-controls':11,'seed-persistence-controls':1}
configs=[]
for name in ['games','continuous','seed-command-controls','seed-persistence-controls','wire','combine','independent']:
 d=B/name;d.mkdir()
 if name not in ['combine','independent']:(d/'native').mkdir()
 if name in counts:
  (d/'wire').mkdir();expected=[launcher+([] if name=='seed-command-controls' and i==10 else ['--diagnostic-seed-command']) for i in range(counts[name])]
  config=d/'tap-config.json';write(config,{'rawRoot':str(d/'wire'),'image':str(image),'expectedCalls':expected,'maxBytes':40*1024**2 if name=='games' else 9*1024**2});configs.append(config)
paths=list(S.iterdir())+configs+[P/'result.json',PB/'production-closure.json',PB/'source-freeze.json',PB/'use-build/receipt.json',PB/'training/training.json',PB/'training/verification.json',Path('/usr/bin/python3'),Path('/usr/bin/node'),Path('/home/legolas/agent-memos/rook2-lead-to-imp2-corrected-gameplay-closure-20261020-01.md')]
paths += [K/n for n in ['run.mjs','continuous.mjs','combine.mjs','seed-command-controls.mjs','seed-persistence-controls.mjs','accepted-games-v1.json','continuous-switching-v1.json','README.md']]
paths += [R/'tools/check_live.py',Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json'),R/'experiments/first-main-cutoff-correction/result.json',R/'experiments/first-main-cutoff-correction/mandatory-completion/result.json']
pins={str(p):sha(p) for p in paths if p.is_file()}
pins.update({x['path']:x['sha256'] for x in chain.values()})
for name,h in source['candidateFiles'].items():pins[str(Path(source['root'])/name)]=h
for name,h in source['canonicalFiles'].items():pins[str(R/name)]=h
plan={'schema':'rook2-corrected-own-pgo-gameplay-v1','repo':str(R),'kit':str(K),'rawRoot':str(B),'image':str(image),'imageSha256':identity,'imageBytes':image.stat().st_size,'diagnostic':chain['diagnostic'],'launcherCommand':launcher,'wireChecker':str(R/'tools/check_live.py'),'wireLauncher':str(S/'wire_engine.py'),'wireFixture':'/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json','sourceFreeze':str(PB/'source-freeze.json'),'productionClosureCommitted':commit,'productionResultSha256':sha(P/'result.json'),'helperCpus':[0,1,2,3,4,5,8,9,10,11,12,13],'nativeCpus':[14],'ownedCpu15':False,'selectedNativeLifetimes':33,'nativeStageOrder':['games','continuous','seed-command-controls','seed-persistence-controls','wire'],'aggregateSeconds':1200,'memoryPerProcessBytes':8*1024**3,'perFileBytes':256*1024**2,'retainedStreamBytes':512*1024**2,'originalLimitsPreserved':True,'performanceMeasurement':False,'retries':0,'optionalSequenceConflict':False,'reportCommandsIdentical':True,'nativeDirsPassedOutsideArgv':True,'wireLauncherBinding':'The unchanged checker accepts one executable path; this tiny exec-only binding calls the unchanged native supervisor, which executes the immutable image directly on14. Checker ELF hash identifies the binding; native receipts separately attest the actual image/argv/exit. No protocol relay.','runtime':{'python':{'path':'/usr/bin/python3','sha256':sha('/usr/bin/python3'),'version':sys.version},'node':{'path':'/usr/bin/node','sha256':sha('/usr/bin/node')},'uname':list(os.uname()),'environment':{k:os.environ.get(k) for k in ['PATH','TMPDIR','LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS']},'dynamicLoaderLibrariesIndependentlyBound':False},'pins':pins,'stages':commands,'scope':'One exact-image behavioral12/632,continuity8,seed11,persistence3,wire8/24 and literal original combined focused report; no timing, promotion, rebuild, external/full3288 or source acceptance.'}
fixture=load(K/'accepted-games-v1.json');assert len(fixture['games'])==12 and sum(len(g['plies']) for g in fixture['games'])==632
families={name:sum(g['family']==name for g in fixture['games']) for name in ['main','openings','switching']};assert families=={'main':4,'openings':4,'switching':4},families
for p in S.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in S.glob('*.mjs'):subprocess.run(['/usr/bin/node','--check',str(p)],check=True)
write(B/'plan.json',plan);print(json.dumps({'planSha256':sha(B/'plan.json'),'pins':len(pins),'lifetimes':33,'nativeRuns':0,'nativeClockNotStarted':True}))
