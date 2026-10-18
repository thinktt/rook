"""Frozen original strict54/eight-wire; no CPU timings or native source changes."""
import datetime,hashlib,json,os,subprocess,sys,threading,time
from pathlib import Path
O=Path(__file__).parent;V=O.parent;S=Path('/home/legolas/rook2-work/imp2-ordered-q-seeded103-validation-20261018-9jtrql1m');B=Path('/home/legolas/rook2/evidence/ordered-q-seeded103-combined-generic-build-20261018');WIRE=V/'interruption-wire';PROF=O/'profiling';ORIGINAL=Path('/home/legolas/king-spec/conformance/profiling')
HELPERS={0,1,2,3,4,5,8,9,10,11,12,13};assert os.sched_getaffinity(0)==HELPERS;assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def snapshot():return {str(p.relative_to(S)):h(p) for p in [S/'Cargo.toml',S/'Cargo.lock',*sorted(p for p in (S/'src').rglob('*') if p.is_file())]}
build=load(B/'receipt.json');native=load(V/'native-verification.json');assert native['complete'] and native['inputs_stable'] and sum(row['passed'] for row in native['units'].values())==158
before=snapshot();assert before==build['source_sha256_before']==build['source_sha256_after']
engine=B/'rook2-exact';identity=h(engine);assert identity==build['binary_output']['sha256']
archive=load(B/'archive-receipt.json');assert archive['binary_sha256']==identity and h(B/archive['archive'])==archive['sha256']
deps=[Path(__file__),B/'receipt.json',B/'archive-receipt.json',V/'native-verification.json',S/'tools/check_live.py',O/'interrupted-sessions-v1.json',Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json'),*[folder/name for folder in [PROF,ORIGINAL] for name in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']]]
for name in ['replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json']:assert h(PROF/name)==h(ORIGINAL/name)
assert h(O/'interrupted-sessions-v1.json')==h(Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json'))
dep_before={str(p):h(p) for p in deps};write(O/'inputs-before.json',{'native':before,'dependencies':dep_before,'engine_sha256':identity,'helper_affinity':sorted(HELPERS),'TMPDIR':os.environ['TMPDIR']})
r={'complete':False,'failure':None,'stages':[],'scope':'Untimed original strict54/eight interruption wire; exact combined103bits generic; no CPU/PGO/profile claim'}
def run(command,stem):
 stdout=O/(stem+'.stdout');stderr=O/(stem+'.stderr');observed={};stop=threading.Event()
 with stdout.open('xb') as out,stderr.open('xb') as err:
  p=subprocess.Popen(command,cwd=S,stdout=out,stderr=err)
  def watch():
   while not stop.is_set():
    try:children=(Path('/proc')/str(p.pid)/'task'/str(p.pid)/'children').read_text().split()
    except OSError:children=[]
    for child in children:
     try:
      args=[x.decode(errors='replace') for x in (Path('/proc')/child/'cmdline').read_bytes().split(b'\0') if x]
      if args and args[0]==str(engine):observed[int(child)]={'pid':int(child),'argv':args,'affinity':sorted(os.sched_getaffinity(int(child)))}
     except OSError:pass
    stop.wait(.001)
  thread=threading.Thread(target=watch);thread.start()
  code=p.wait();stop.set();thread.join()
 stage={'command':command,'exit_code':code,'stdout_sha256':h(stdout),'stderr_sha256':h(stderr),'actual_engine_affinities':list(observed.values())}
 r['stages'].append(stage);assert code==0,stem+' failed';assert all(set(row['affinity'])==HELPERS for row in observed.values()),'unexpected actual engine affinity'
 return stage
try:
 stage=run(['/usr/bin/node',str(PROF/'replay-check.mjs'),'--',str(engine)],'strict54')
 report=load(O/'strict54.stdout');assert report['status']=='pass' and len(report['results'])==54
 assert all(row['status']=='pass' and row['complete'] and row['exit']=={'code':0,'signal':None} and not row['error'] and not row['truncated'] for row in report['results'])
 assert not (O/'strict54.stderr').stat().st_size
 pids={row['pid'] for row in report['results']};seen={row['pid'] for row in stage['actual_engine_affinities']};r['strict_affinity_coverage']={'expected_pids':sorted(pids),'observed_pids':sorted(seen),'unobserved_pids':sorted(pids-seen)}
 raw=O/'strict-raw';raw.mkdir()
 for row in report['results']:
  folder=raw/row['case'];folder.mkdir();(folder/'stdout.raw').write_bytes(row['stdout'].encode());(folder/'stderr.raw').write_bytes(row['stderr'].encode());write(folder/'exit.json',row['exit'])
 stage=run([sys.executable,str(S/'tools/check_live.py'),'--engine',str(engine),'--output',str(WIRE)],'wire')
 wire=load(WIRE/'receipt.json');assert wire['pass'] and len(wire['results'])==8 and sum(len(row['searches']) for row in wire['results'])==24
 assert wire['engine_sha256_before']==wire['engine_sha256_after']==identity and wire['effective_affinity']==sorted(HELPERS)
 assert all(row['observed_exit_code']==0 and row['complete_streams'] for row in wire['results'])
 r.update(complete=True,native_sha256=identity,strict_replays=54,interruption_fixtures=8,interruption_searches=24,wire_receipt_sha256=h(WIRE/'receipt.json'))
except BaseException as error:r['failure']=type(error).__name__+': '+str(error)
finally:
 after=snapshot();dep_after={str(p):h(p) for p in deps};stable=before==after and dep_before==dep_after and h(engine)==identity;r['inputs_stable']=stable
 if not stable:r.update(complete=False,failure='source/dependency/image changed')
 write(O/'inputs-after.json',{'native':after,'dependencies':dep_after,'engine_sha256':h(engine)})
 write(O/'identity.json',r);write(O/'tool-terminal.json',{'exit_code':0 if r['complete'] else 1,'complete':r['complete'],'failure':r['failure'],'identity_sha256':h(O/'identity.json'),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(json.dumps(r));sys.exit(0 if r['complete'] else 1)
