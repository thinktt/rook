#!/usr/bin/env python3
import json,hashlib,sys,subprocess,os,datetime
from pathlib import Path
OUT=Path(__file__).resolve().parent;E=OUT.parent;SOURCE=Path('/tmp/imp2-admission-combined95-native-validation-20261018-6eka5zwy');BUILD=E/'admission-combined95-native-build-20261018';NATIVE=E/'admission-combined95-native-validation-20261018';WIRE=E/'admission-combined95-interruption-wire-20261018'
sys.dont_write_bytecode=True;sys.path.insert(0,str(SOURCE/'tools'))
from build import source_snapshot,tool_snapshot
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def run(argv,stem):
 with (OUT/(stem+'.stdout')).open('xb') as a,(OUT/(stem+'.stderr')).open('xb') as b:r=subprocess.run(argv,cwd=SOURCE,stdout=a,stderr=b)
 stage=dict(command=argv,exit_code=r.returncode,stdout_sha256=sha(OUT/(stem+'.stdout')),stderr_sha256=sha(OUT/(stem+'.stderr')));record['stages'].append(stage);assert r.returncode==0,stem+' failed'
record=dict(complete=False,failure=None,stages=[],started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),affinity=sorted(os.sched_getaffinity(0)))
try:
 assert set(os.sched_getaffinity(0))=={0,1,2,3,4,5,8,9,10,11,12,13}
 br=load(BUILD/'receipt.json');native=load(NATIVE/'native-verification.json');actual=load(NATIVE/'actual-tool-terminal.json');assert actual['terminal']['exit_code']==0
 assert native['complete'] and native['inputs_stable'] and native['units']['rook2']['passed']==149 and native['units']['rook2-dev']['passed']==2
 engine=BUILD/'rook2-exact';identity=sha(engine);assert identity==br['binary_output']['sha256']=='6e7b29358eb3774f578308f79a2e83b20587e7bd5cdacae1ff762764e7b11ec5'
 before=source_snapshot(SOURCE);tools=tool_snapshot(SOURCE);assert before==br['source_sha256_before']==br['source_sha256_after'];assert tools==br['tool_sha256_before']==br['tool_sha256_after']
 ar=load(BUILD/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and ar['binary_sha256']==identity and sha(BUILD/ar['archive'])==ar['sha256']
 spec=Path('/home/legolas/king-spec/conformance');paths=[Path(__file__),BUILD/'receipt.json',BUILD/'archive-receipt.json',NATIVE/'native-verification.json',NATIVE/'actual-tool-terminal.json',E/'admission-combined95-codegen-review-20261018/bounded-gate.json',SOURCE/'tools/check_live.py',SOURCE/'tools/build.py']+[spec/'profiling'/name for name in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']]+[spec/'fixtures/interrupted-sessions-v1.json']
 closure={str(p):sha(p) for p in paths};write('input-closure.json',closure);copy=OUT/'input-closure';copy.mkdir()
 for p in paths:
  d=copy/str(p).lstrip('/');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(p.read_bytes())
 run(['/usr/bin/node',str(spec/'profiling/replay-check.mjs'),'--',str(engine)],'profile-all')
 replay=load(OUT/'profile-all.stdout');assert replay['status']=='pass' and len(replay['results'])==54 and not (OUT/'profile-all.stderr').stat().st_size
 assert len({row['case'] for row in replay['results']})==54
 for row in replay['results']:
  assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']=={'code':0,'signal':None} and row['error'] is None and row['stderr']=='' and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
 run([sys.executable,str(SOURCE/'tools/check_live.py'),'--engine',str(engine),'--output',str(WIRE)],'wire')
 wire=load(WIRE/'receipt.json');assert wire['pass'] and len(wire['results'])==8 and sum(len(x['searches']) for x in wire['results'])==24
 assert all(x['observed_exit_code']==0 and x['complete_streams'] for x in wire['results']);assert wire['engine_sha256_before']==wire['engine_sha256_after']==identity
 assert all(sha(Path(p))==h for p,h in closure.items());assert before==source_snapshot(SOURCE) and tools==tool_snapshot(SOURCE) and sha(engine)==identity
 record.update(complete=True,inputs_stable=True,native_artifact_sha256=identity,strict_replays=54,interruption_fixtures=8,interruption_searches=24,source_before=before,source_after=source_snapshot(SOURCE),build_receipt_sha256=sha(BUILD/'receipt.json'),wire_receipt_sha256=sha(WIRE/'receipt.json'))
except BaseException as error:record['failure']=f'{type(error).__name__}: {error}'
finally:
 record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write('identity.json',record)
print(json.dumps({k:record.get(k) for k in ['complete','failure','native_artifact_sha256','strict_replays','interruption_fixtures','interruption_searches']}));sys.exit(0 if record['complete'] else 1)
