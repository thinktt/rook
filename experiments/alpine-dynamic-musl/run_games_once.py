import json,os,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,'/home/legolas/rook2/tools')
import collect_games as C
B=Path('/work');out=B/'games12';out.mkdir()
engine=B/'artifacts/rook2-musl';build=B/'build-use/receipt.json'
sha=C.sha(engine);r=json.loads(build.read_text());assert r['binary_output']['sha256']==sha and r['dynamicMuslVerified']
f=json.loads((C.GATE/'accepted-games-v1.json').read_text());games=f['games']
assert len(games)==12 and sum(len(g['plies']) for g in games)==632
summary={'complete':False,'complete12':False,'repetitionsPerGame':1,'medianEstimate':False,'engineSha256':sha,'games':[],'sourceScope':'unchanged candidate68 engine source, dynamic musl own-PGO variant','timingBoundary':'direct wait4 native whole lifetime; also quantized go-to-move intervals from existing tap','qualification':'finite local 12-game run only; no external or performance qualification'}
C.write(out/'context-before.json',C.context());deadline=time.monotonic()+14400
for index,g in enumerate(games):
 row=C.run_lifetime(engine,sha,g,out/f'{index:02d}-{g["id"]}',deadline,C.byte_count(out))
 summary['games'].append({'id':g['id'],'searches':len(g['plies']),'cpu_s':row.get('cpu_s'),'wall_ns':row.get('wall_ns'),'failure':row['failure'],'nativePid':row.get('native_pid'),'resultPath':str(out/f'{index:02d}-{g["id"]}'/'result.json')})
 C.write(out/'summary.json',summary)
 print(json.dumps(summary['games'][-1]),flush=True)
 assert row['failure'] is None,row['failure']
summary.update(complete=True,complete12=True,searches=sum(g['searches'] for g in summary['games']),sum_game_cpu_s=sum(g['cpu_s'] for g in summary['games']),sum_game_wall_s=sum(g['wall_ns'] for g in summary['games'])/1e9)
assert C.sha(engine)==sha
C.write(out/'summary.json',summary);C.write(out/'context-after.json',C.context())
print(json.dumps({k:v for k,v in summary.items() if k not in ['games']}),flush=True)
