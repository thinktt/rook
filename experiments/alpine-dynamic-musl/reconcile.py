import hashlib,json,statistics,subprocess,os
from pathlib import Path
B=Path(__file__).resolve().parent
R=Path('/home/legolas/rook2');SPEC=Path('/home/legolas/king-spec/conformance')
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def host(p):
 p=Path(p);assert p.is_relative_to('/work');return B/p.relative_to('/work')
status=load(B/'benchmark-status.json');assert status['allComplete'] and all(s['returncode']==0 for s in status['stages'])
use=load(B/'build-use/receipt.json');repeat=load(B/'build-repeat/receipt.json');image=B/'artifacts/rook2-musl';h=sha(image)
assert h==use['binary_output']['sha256']==repeat['binary_output']['sha256']==sha(B/'artifacts/rook2-musl-repeat')
training=load(B/'training.json');assert training['complete'] and training['independentRemergeIdentical']
assert sha(B/'merged.profdata')==training['profileSha256']
source=load(B/'source-map.json')
assert all(sha(B/'source'/p)==sha(R/p)==v for p,v in source.items())
for line in (B/'runtime-hashes.txt').read_text().splitlines():
 expected,p=line.split(maxsplit=1);assert sha(B/'rootfs'/p.lstrip('/'))==expected
native_seen=set()
def native(p):
 n=load(p)
 assert n['failure'] is None and n['native_exit_code']==0 and not n['supervisor_signals']
 assert n['engine_sha256_before']==n['engine_sha256_after']==h
 assert n['native_post_exec']['affinity']==n['native_pre_exec']['affinity']==[14]
 assert n['native_post_exec']['tasks']==[str(n['native_pid'])]
 assert n['native_pid'] not in native_seen;native_seen.add(n['native_pid'])
 assert not Path('/proc/'+str(n['native_pid'])).exists()
 assert abs(n['total_cpu_s']-n['user_cpu_s']-n['system_cpu_s'])<1e-9
 return n
standard=load(B/'standard54/summary.json');manifest=load(B/'standard54/manifest.json')
assert standard['complete'] and standard['failure'] is None and len(standard['runs'])==216
cases=load(SPEC/'profiling/workloads.json')['cases'];ids=[c['id'] for c in cases]
assert [(r['case'],r['repeat']) for r in standard['runs']]==[(c,i) for c in ids for i in range(4)]
medians={};table54=[]
for index,r in enumerate(standard['runs']):
 d=B/'standard54'/f'{index:03d}-{r["case"]}-r{r["repeat"]}'
 n=native(d/'native.json');c=load(d/'comparator.stdout');one=c['results'][0]
 assert c['status']=='pass' and c['selectedCases']==[r['case']] and len(c['results'])==1
 assert one['complete'] and not one['truncated'] and one['discardedObservedBytes']==0 and one['exit']=={'code':0,'signal':None}
 assert one['pid']==n['supervisor_pid'] and one['stderr']=='' and not (d/'comparator.stderr').stat().st_size
 assert n['total_cpu_s']==r['cpu_s'] and r['failure'] is None
for c in ids:
 samples=[r['cpu_s'] for r in standard['runs'] if r['case']==c and not r['warmup']]
 assert len(samples)==3
 m=statistics.median(samples);assert m==standard['case_summaries'][c]['median'];medians[c]=m
 table54.append(','.join([c,*[f'{v:.6f}' for v in samples],f'{m:.6f}']))
assert abs(sum(medians.values())-standard['sum_case_medians_s'])<1e-9
(B/'timings54.csv').write_text('case,cpu1_s,cpu2_s,cpu3_s,median_cpu_s\n'+'\n'.join(table54)+'\n')
games=load(B/'games12/summary.json');fixture=load(SPEC/'gate-replay/accepted-games-v1.json')
assert games['complete12'] and games['complete'] and games['searches']==632 and len(games['games'])==12
assert [g['id'] for g in games['games']]==[g['id'] for g in fixture['games']]
posts=0;reports=[];table12=[]
for row,g in zip(games['games'],fixture['games']):
 d=host(row['resultPath']).parent;n=native(d/'native.json');r=load(d/'replay.json');tap=load(d/'wire/receipt.json');result=load(d/'result.json')
 assert row['failure'] is None and result['failure'] is None and row['cpu_s']==n['total_cpu_s']
 assert r['pass'] and r['selectedGameIds']==[g['id']]
 assert len(tap['searches'])==len(g['plies'])==row['searches']
 assert tap['native']['pid']==n['native_pid']
 for name,item in tap['raw'].items():
  raw=d/'wire'/f'{name}.raw';assert sha(raw)==item['sha256'] and raw.stat().st_size==item['bytes']==item['observedBytes'] and item['discardedObservedBytes']==0
 for name,value in result['file_sha256'].items():assert sha(d/name)==value
 for search in tap['searches']:
  for boundary in ('beforeWrite','afterData'):assert search[boundary]['available'] and search[boundary]['pid']==n['native_pid'] and search[boundary]['lastProcessor']==14
 for ply in g['plies']:posts+=len(ply['expected']['posts'])
 reports.append('/work/'+str((d/'replay.json').relative_to(B)))
 table12.append(f'{g["id"]},{row["searches"]},{row["cpu_s"]:.6f},{row["wall_ns"]/1e9:.6f}')
assert abs(sum(g['cpu_s'] for g in games['games'])-games['sum_game_cpu_s'])<1e-9
(B/'timings12.csv').write_text('game,searches,cpu_s,wall_s\n'+'\n'.join(table12)+'\n')
(B/'combine-argv.json').write_text(json.dumps(['/usr/bin/node',str(SPEC/'gate-replay/combine.mjs'),'--report','/work/games12/combined.json',*reports],indent=2)+'\n')
result={'complete':True,'imageSha256':h,'bytes':image.stat().st_size,'dynamicMusl':True,'ownPgoTrainingCases':54,'independentRemergeIdentical':True,'repeatBuildExactMatch':True,'sourceFiles':len(source),'standard54':{'cases':54,'lifetimes':216,'posts':4*sum(len(c['posts']) for c in load(SPEC/'profiling/replay-oracle.json')['cases']),'sumCaseMedianCpuSeconds':sum(medians.values()),'warmupsPerCase':1,'measuredPerCase':3},'games12':{'games':12,'searches':632,'posts':posts,'repetitionsPerGame':1,'sumCpuSeconds':games['sum_game_cpu_s'],'sumWallSeconds':games['sum_game_wall_s']},'observedBenchmarkNativePids':len(native_seen),'originalCandidateUnchanged':sha(Path('/home/legolas/rook-bin/bin/rook-1.0.0-candidate68-linux-x86_64'))=='5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a','scope':'local dynamic-musl deployment trial; no promotion or final qualification'}
assert result['originalCandidateUnchanged'] and len(native_seen)==228
(B/'independent-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
