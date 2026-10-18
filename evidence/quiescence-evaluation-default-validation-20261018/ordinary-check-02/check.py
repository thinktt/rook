"""Original strict54 and eight interruption fixtures, untimed housekeeping only."""
import json,hashlib,subprocess,sys,os,datetime
from pathlib import Path
OUT=Path(__file__).parent
ROOT=Path("/home/legolas/rook2")
SOURCE=Path('/tmp/imp2-quiescence-evaluation-default-validation-20261018')
BUILD=ROOT/'evidence/quiescence-evaluation-default-build-20261018'
VALIDATION=ROOT/'evidence/quiescence-evaluation-default-validation-20261018'
WIRE=VALIDATION/'interruption-wire-02'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
assert os.sched_getaffinity(0)=={0,1,2,3,4,5,8,9,10,11,12,13}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def snapshot(r):return {str(p.relative_to(r)):sha(p) for p in [r/'Cargo.toml',r/'Cargo.lock',*sorted(p for p in (r/'src').rglob('*') if p.is_file())]}
def run(cmd,stem):
 out,err=OUT/(stem+'.stdout'),OUT/(stem+'.stderr')
 with out.open('xb') as a,err.open('xb') as b:r=subprocess.run(cmd,cwd=SOURCE,stdout=a,stderr=b)
 stage={'command':cmd,'exit_code':r.returncode,'stdout_sha256':sha(out),'stderr_sha256':sha(err)}
 rec['stages'].append(stage);assert r.returncode==0,stem+' failed'
 return stage
native=load(VALIDATION/'native-verification.json');assert native['complete'] and native['inputs_stable'];assert native['units']['rook2']['passed']==140
gate=load(VALIDATION/'codegen/focused-referents-and-default-gate.json');assert gate['gate']['strict54_and_wire_authorized_gate_met']
build=load(BUILD/'receipt.json');before=snapshot(SOURCE);assert before==build['source_sha256_before']==build['source_sha256_after']
engine=BUILD/'rook2-exact';identity=sha(engine);assert identity==build['binary_output']['sha256']
archive=load(BUILD/'archive-receipt.json');assert archive['binary_sha256']==identity and archive['sha256']==sha(BUILD/archive['archive'])
profiling=Path('/home/legolas/king-spec/conformance/profiling')
deps=[Path(__file__),BUILD/'receipt.json',BUILD/'archive-receipt.json',VALIDATION/'codegen/focused-referents-and-default-gate.json',ROOT/'tools/check_live.py',Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json'),*[profiling/n for n in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']]]
dep_before={str(p):sha(p) for p in deps};write(OUT/'inputs-before.json',{'native':before,'dependencies':dep_before,'engine_sha256':identity,'helper_affinity':sorted(os.sched_getaffinity(0))})
rec={'complete':False,'failure':None,'stages':[],'scope':'Untimed strict54/eight interruption wire regression; no timing/PGO/profilers/qualification claim'}
try:
 run(['/usr/bin/node',str(profiling/'replay-check.mjs'),'--',str(engine)],'strict54')
 report=load(OUT/'strict54.stdout');assert report['status']=='pass' and len(report['results'])==54 and all(r['status']=='pass' and r['complete'] and r['exit']=={'code':0,'signal':None} for r in report['results']);assert not (OUT/'strict54.stderr').stat().st_size
 run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(engine),'--output',str(WIRE)],'wire')
 wire=load(WIRE/'receipt.json');assert wire['pass'] and len(wire['results'])==8 and sum(len(r['searches']) for r in wire['results'])==24
 assert wire['engine_sha256_before']==wire['engine_sha256_after']==identity
 assert all(r['observed_exit_code']==0 and r['complete_streams'] for r in wire['results'])
 rec.update(complete=True,native_artifact_sha256=identity,strict_replays=54,interruption_fixtures=8,interruption_searches=24,wire_receipt_sha256=sha(WIRE/'receipt.json'))
except BaseException as e:rec['failure']=type(e).__name__+': '+str(e)
finally:
 after=snapshot(SOURCE);dep_after={str(p):sha(p) for p in deps};stable=before==after and dep_before==dep_after and sha(engine)==identity
 rec['inputs_stable']=stable
 if not stable:rec.update(complete=False,failure='source/dependency/image changed')
 write(OUT/'inputs-after.json',{'native':after,'dependencies':dep_after,'engine_sha256':sha(engine)})
 write(OUT/'identity.json',rec)
 terminal={'exit_code':0 if rec['complete'] else 1,'complete':rec['complete'],'failure':rec['failure'],'identity_sha256':sha(OUT/'identity.json'),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(OUT/'tool-terminal.json',terminal)
print(json.dumps(rec))
sys.exit(0 if rec['complete'] else 1)
