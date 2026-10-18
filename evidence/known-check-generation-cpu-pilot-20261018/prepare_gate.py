from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1];E=ROOT/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def main():
 config=load(OUT/'config.json');slug=config['slug'];dependencies={}
 def read(p):
  dependencies[str(p)]=sha(p);return load(p)
 prep=read(E/config['prepare'])
 control=read(E/config['control_build']/'receipt.json')
 trial=read(E/(slug+'-build-20261018')/'receipt.json')
 for build in [control,trial]:
  assert build['source_identity_unchanged'] and build['tool_identity_unchanged'] and build['pgo']['mode']=='none'
  assert build['source_sha256_before']==build['source_sha256_after']
  assert build['rust_flags']==['-C','target-cpu=x86-64'] and build['target_triple']=='x86_64-unknown-linux-gnu'
 assert control['tool_sha256_before']==trial['tool_sha256_before']
 baseline={k:prep['baseline_source_sha256'][k] for k in control['source_sha256_before']}
 candidate={k:prep[config['candidate_field']][k] for k in trial['source_sha256_before']}
 assert baseline==control['source_sha256_before'] and candidate==trial['source_sha256_before']
 assert sorted(k for k,h in baseline.items() if h!=candidate[k])==config['changed']
 native=read(E/(slug+'-validation-20261018')/'native-verification.json')
 assert native['complete'] and native['inputs_stable'] and native['failure'] is None
 assert native['source_before']==native['source_after']==candidate
 assert sum(x['passed'] for x in native['units'].values())==config['candidate_tests']
 assert read(E/(slug+'-validation-20261018')/'tool-terminal.json')['exit_code']==0
 assert read(E/config['control_terminal'])['exit_code']==0
 composed=read(E/'king-first88-validation-20261018/validation-summary.json')
 assert composed['all_owned_processes_terminal'] and composed['native_tests']==147 and composed['strict_replays']==54 and composed['diagnostic_cases']==6161
 for filename,record in composed['terminal_records'].items():assert read(ROOT/filename)==record and record['exit_code']==0
 variants={}
 for name,builddir,checkdir,wirepath,replayname,receipt in [('baseline',config['control_build'],config['control_check'],config['control_wire'],config['control_replay'],control),(config['name'],slug+'-build-20261018',slug+'-strict-check-20261018',slug+'-interruption-wire-20261018','strict54.stdout',trial)]:
  build=E/builddir;check=E/checkdir;image=build/'rook2-exact'
  identity=read(check/'identity.json');report=read(check/replayname);wire=read(E/wirepath/'receipt.json')
  assert sha(image)==identity['native_artifact_sha256']==receipt['binary_output']['sha256']
  assert report['status']=='pass' and len(report['results'])==54
  assert all(row['status']=='pass' and row['complete'] and not row['truncated'] and row['error'] is None and row['exit']=={'code':0,'signal':None} and row['stderr']=='' and row['discardedObservedBytes']==0 for row in report['results'])
  assert wire['pass'] and len(wire['results'])==8 and sum(len(row['searches']) for row in wire['results'])==24
  assert all(row['complete_streams'] and row['observed_exit_code']==0 for row in wire['results'])
  assert sha(E/wirepath/'receipt.json')==identity['wire_receipt_sha256']
  assert wire['engine_sha256_before']==wire['engine_sha256_after']==sha(image)
  archive=read(build/'archive-receipt.json');assert archive['binary_sha256']==sha(image) and sha(build/archive['archive'])==archive['sha256']
  dependencies[str(build/archive['archive'])]=sha(build/archive['archive'])
  if name==config['name']:
   assert identity['complete'] and identity['inputs_stable'] and identity['failure'] is None
   assert read(check/'actual-tool-terminal.json')['exit_code']==0
   assert read(check/'independent-verification.json')['complete']
   inputs=read(check/'inputs-before.json');assert inputs['dependencies']==read(check/'inputs-after.json')['dependencies']
   for p,h in inputs['dependencies'].items():assert sha(Path(p))==h
   dependencies.update(inputs['dependencies'])
  variants[name]={'path':str(image),'sha256':sha(image)}
 dependencies[str(OUT/'config.json')]=sha(OUT/'config.json');dependencies[str(Path(__file__))]=sha(Path(__file__))
 with (OUT/'regression-gate.json').open('x') as stream:json.dump({'complete':True,'variants':variants,'dependencies':dependencies,'changed':config['changed'],'scope':config['scope']},stream,indent=2);stream.write('\n')
 print(json.dumps({'complete':True,'variants':variants,'dependencies':len(dependencies)}))
if __name__=='__main__':main()
