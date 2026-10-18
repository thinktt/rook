import datetime,hashlib,json,os,re,subprocess,sys,tarfile
from pathlib import Path
V=Path(__file__).parent;O=V/'ordinary-check';W=V/'interruption-wire';S=Path('/home/legolas/rook2-work/ordered-q-bitview-phase2-20261018-5v7mxmev');B=Path('/home/legolas/rook2/evidence/ordered-q-bitview-phase2-build-02-20261018');P=Path('/home/legolas/rook2/evidence/ordered-q-bitview-phase2-proposal-20261018');CPUS=[0,1,2,3,4,5,8,9,10,11,12,13]
assert sorted(os.sched_getaffinity(0))==CPUS
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
r={'pass':False,'scope':'Independent original saved raw/exit/native-source/archive closure; no engines/builds/tests executed','affinity':CPUS}
try:
 native=load(V/'native-verification.json');assert native['complete'] and native['failure'] is None and native['inputs_stable'];assert native['source_before']==native['source_after'];assert len(native['source_before'])==43
 for name,expected in native['source_before'].items():assert h(S/name)==expected
 for stem,n in [('rook2',143),('rook2-dev',2)]:
  raw=(V/(stem+'-tests.stdout')).read_text();assert re.search(r'test result: ok\. '+str(n)+r' passed; 0 failed;',raw);assert len(re.findall(r'^test .+ \.\.\. ok$',raw,re.M))==n;assert h(V/'unit-bin'/stem/'rook2-exact')==native['units'][stem]['binary_sha256']
 for stage,stem in zip(native['stages'],['unit-build','rook2-tests','rook2-dev-tests']):
  assert stage['exit_code']==0 and h(V/(stem+'.stdout'))==stage['stdout_sha256'] and h(V/(stem+'.stderr'))==stage['stderr_sha256']
 build=load(B/'receipt.json');assert build['source_sha256_before']==build['source_sha256_after']==native['source_before']
 image=h(B/'rook2-exact');assert image==build['binary_output']['sha256']=='3462a87a37f90188808efbf5128e57eb65837aae0f2e6a23bbeec4c5392e2d24'
 for name,expected in native['source_before'].items():assert h(B/'source-before'/name)==expected
 archive=load(B/'archive-receipt.json');assert h(B/archive['archive'])==archive['sha256'] and archive['binary_sha256']==image
 with tarfile.open(B/archive['archive']) as t:
  files=[m for m in t.getmembers() if m.isfile()];assert len(files)==66 and len({m.name for m in files})==66
  for m in files:assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==h(B/'source-before'/m.name)==h(S/m.name)
 before=load(O/'inputs-before.json');after=load(O/'inputs-after.json');assert before['native']==after['native']==native['source_before'];assert before['engine_sha256']==after['engine_sha256']==image;assert before['dependencies']==after['dependencies']
 for name,expected in before['dependencies'].items():assert h(Path(name))==expected
 strict=subprocess.run(['/usr/bin/node',str(V/'reconcile-strict.mjs')],capture_output=True);(V/'reconcile-strict.stdout').write_bytes(strict.stdout);(V/'reconcile-strict.stderr').write_bytes(strict.stderr);assert strict.returncode==0,strict.stderr.decode();r['strict']=json.loads(strict.stdout)
 report=load(O/'strict54.stdout');identity=load(O/'identity.json');assert identity['complete'] and identity['inputs_stable'];assert len(identity['stages'])==2
 expected_pids={x['pid'] for x in report['results']};seen={x['pid'] for x in identity['stages'][0]['actual_engine_affinities']};assert expected_pids==seen and len(seen)==54
 for stage,stem in zip(identity['stages'],['strict54','wire']):
  assert stage['exit_code']==0 and h(O/(stem+'.stdout'))==stage['stdout_sha256'] and h(O/(stem+'.stderr'))==stage['stderr_sha256'];assert all(x['affinity']==CPUS for x in stage['actual_engine_affinities'])
 assert len(identity['stages'][1]['actual_engine_affinities'])==8
 fixture=load(O/'interrupted-sessions-v1.json');wire=load(W/'receipt.json');assert h(O/'interrupted-sessions-v1.json')==wire['fixture_sha256']==h(Path(wire['fixture']));assert wire['engine_sha256_before']==wire['engine_sha256_after']==image
 assert wire['pass'] and len(fixture['cases'])==len(wire['results'])==8
 def event(line):
  if line.startswith('move '):return {'type':'move','move':line[5:]}
  m=re.fullmatch(r'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?',line)
  if m:
   cs,sid,depth,remaining,total=map(int,m.groups()[:5]);return {'type':'status','engineCentiseconds':cs,'searchId':sid,'depthToken':depth,'remaining':remaining,'total':total,'pv':(m[6] or '').strip().replace('0','O')}
  m=re.fullmatch(r' *(-?\d+) +([+-]?\d+) +(\d+) +(\d+)(?: (.*))?',line);assert m,line
  depth,score,cs,sid=map(int,m.groups()[:4]);return {'type':'post','depthToken':depth,'evaluation':score,'engineCentiseconds':cs,'searchId':sid,'pv':(m[5] or '').strip().replace('0','O')}
 searches=0;wire_raw=[]
 for case,row in zip(fixture['cases'],wire['results']):
  assert row['id']==case['id'] and row['status']=='pass' and row['exit_code']==row['observed_exit_code']==0 and row['complete_streams']
  folder=W/case['id'];raw={key:(folder/(key+'.raw')).read_bytes() for key in ['stdin','stdout','stderr']}
  for key,data in raw.items():assert row['raw'][key]=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  assert not raw['stderr'];assert raw['stdout'].endswith(b'\n');lines=raw['stdout'].decode().splitlines();commands=[]
  for search,expected,observed in zip(case['request']['input']['searches'],case['expected']['results'],row['searches']):
   searches+=1;setup=search['commands']+['time '+str(search['allowanceCs']),'cm_parm'];commands+=setup+['go']+search['queued']
   acks=[' '.join(c.split()) for c in search['commands'] if c.startswith('cm_parm ')]+['cm_parm'];assert lines[:len(acks)]==acks;del lines[:len(acks)]
   parsed=[event(lines.pop(0)) for _ in expected['events']];assert parsed==expected['events']==observed['events']
   abort=bool(search['queued'] and search['queued'][-1]=='force');assert observed['abort']==abort
   if abort:assert lines.pop(0)=='aborting search ...'
  assert not lines;commands+=['quit'];assert raw['stdin']==('\n'.join(commands)+'\n').encode();wire_raw.append({'id':case['id'],'raw':row['raw'],'exit_code':row['observed_exit_code']})
 assert searches==24
 r.update(pass_=True,native_units=145,source_files=43,strict_cases=54,wire_fixtures=8,wire_searches=24,actual_engine_pids_observed=62,image_sha256=image,build_receipt_sha256=h(B/'receipt.json'),native_receipt_sha256=h(V/'native-verification.json'),wire=wire_raw,inputs_stable=True)
 r['pass']=r.pop('pass_')
except BaseException as e:
 import traceback
 r['failure']=type(e).__name__+': '+str(e);r['traceback']=traceback.format_exc()
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(V/'independent-reconciliation.json',r)
print(json.dumps({k:v for k,v in r.items() if k!='wire'}));sys.exit(0 if r['pass'] else 1)
