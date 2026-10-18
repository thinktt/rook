#!/usr/bin/env python3
"""Independently reconcile both own profiles and retained original native streams."""
from pathlib import Path
import hashlib,json,gzip,re,subprocess,sys,tarfile
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'pgo-ordered-bit-checkers-phase1-reconciliation-20261018';ROOT=HERE.parents[1];SPEC=Path('/home/legolas/king-spec/conformance')
sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE));from guard import require_clearance,terminal
sys.path.insert(0,'/tmp/imp2-ordered-bit-checkers-phase1-validation-20261018-lys_zi80/tools');from build import source_snapshot

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def semantic(s,wire=False):
 if s.startswith('move '):return dict(type='move',move=s[5:])
 if s.startswith('stat01: '):
  m=re.fullmatch(r'stat01:\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)(?: (.*))?',s);assert m
  a,b,c,d,e=map(int,m.groups()[:5]);return dict(type='status',engineCentiseconds=a,searchId=b,depthToken=c,remaining=d,total=e,pv=(m[6] or '').replace('0','O'))
 m=re.fullmatch(r'\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?',s);assert m,s
 a,b,c,d=map(int,m.groups()[:4]);pv=(m[5] or '').strip().replace('0','O')
 return dict(type='post',depthToken=a,evaluation=b,engineCentiseconds=c,searchId=d,pv=pv) if wire else dict(depth=a,score=b,workThousands=c,searchId=d,pv=pv)

def replay(report_path,engine,training,raw_out):
 report=load(report_path);work=load(SPEC/'profiling/workloads.json');oracle=load(SPEC/'profiling/replay-oracle.json')
 assert report['status']=='pass' and len(report['results'])==len(work['cases'])==len(oracle['cases'])==54
 assert report['selectedCases']==[c['id'] for c in work['cases']]
 expected_command=(['/usr/bin/taskset','-c','14'] if training else [])+[str(engine),'--work-clock=kingwcr','--work-clock-post=work']
 for row,c in zip(report['results'],work['cases']):
  answer=next(x for x in oracle['cases'] if x['id']==c['id'])
  assert row['case']==c['id'] and row['command']==expected_command and row['status']=='pass' and row['exit']==answer['exit']==dict(code=0,signal=None)
  assert row['error'] is None and row['complete'] and not row['truncated'] and not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0
  assert row['stderr']==answer['stderr']=='' and row['stdout'].endswith('\n')
  lines=row['stdout'].splitlines();acks=[x for x in c['protocol']['recordsBeforeSearch'] if x.startswith('cm_parm ')]+['cm_parm rnd=0'];assert lines[:len(acks)]==acks;lines=lines[len(acks):]
  assert [semantic(x) for x in lines[:len(answer['posts'])]]==answer['posts']
  assert lines[len(answer['posts']):]==['move '+answer['move']]+answer['resultRecords']
  d=raw_out/c['id'];d.mkdir(parents=True);(d/'stdout.raw').write_text(row['stdout']);(d/'stderr.raw').write_text(row['stderr'])
  (d/'stdin.reconstructed').write_text('\n'.join(c['protocol']['recordsBeforeSearch']+['cm_parm rnd',c['protocol']['searchRecord'],c['protocol']['cleanupRecord']])+'\n')
 return report

def main():
 require_clearance();assert not OUT.exists();OUT.mkdir();variants={}
 for variant,source in [('baseline','/tmp/imp2-move-q-evaluation-combined-20261018'),('phase1','/tmp/imp2-ordered-bit-checkers-phase1-validation-20261018-lys_zi80')]:
  prefix='pgo-bounded-reply-baseline' if variant=='baseline' else 'pgo-ordered-bit-checkers-phase1'
  tr=ROOT/f'evidence/{prefix}-training-20261018';ib=ROOT/f'evidence/{prefix}-instrumented-build-20261018';build=ROOT/f'evidence/{prefix}-use-build-20261018';check=ROOT/f'evidence/{prefix}-use-check-20261018';wire=ROOT/f'evidence/{prefix}-interruption-wire-20261018'
  for q in [ib/'tool-terminal.json',tr/'tool-terminal.json',tr/'verify-tool-terminal.json',build/'tool-terminal.json',check/'tool-terminal.json']:assert load(q)['exit_code']==0
  training=load(tr/'training.json');tb=load(ib/'receipt.json');br=load(build/'receipt.json');identity=load(check/'identity.json');tv=load(tr/'verification.json')
  source_map=source_snapshot(Path(source));assert source_map==training['engine_source_sha256']==tb['source_sha256_before']==tb['source_sha256_after']==br['source_sha256_before']==br['source_sha256_after']==identity['source_before']==identity['source_after']
  assert training['complete'] and tv['complete'] and tv['training_record_sha256']==sha(tr/'training.json')
  for closure_path in [tr/'input-closure.json',check/'input-closure.json']:
   assert all(sha(Path(p))==h for p,h in load(closure_path).items())
  assert training['instrumented_engine_sha256']==sha(ib/'rook2-exact')==tb['binary_output']['sha256']
  assert sha(ib/'receipt.json')==training['instrumented_build_receipt']['sha256']
  raw_paths=sorted((tr/'raw').glob('*.profraw'));assert len(raw_paths)==54 and {str(p):sha(p) for p in raw_paths}==training['raw_profiles_sha256']
  train_report=replay(tr/'replay.json',ib/'rook2-exact',True,OUT/'raw'/variant/'training')
  assert len({row['pid'] for row in train_report['results']})==54
  assert {int(p.stem.rsplit('-',1)[1]) for p in raw_paths}=={row['pid'] for row in train_report['results']}
  assert not (tr/'replay.stderr').stat().st_size
  profile=tr/'merged.profdata';assert sha(profile)==training['profile_sha256']==tv['merged_profile_sha256']==identity['profile_sha256']
  assert gzip.decompress((tr/'merged.profdata.gz').read_bytes())==profile.read_bytes()
  assert sha(tr/'merged.profdata.gz')==training['profile_archive_sha256']
  merge_tool=Path('/usr/bin/llvm-profdata-19');assert sha(merge_tool.resolve())==training['merge_tool_sha256']
  profile_out=OUT/(variant+'-independently-merged.profdata');command=[str(merge_tool),'merge','-o',str(profile_out),*map(str,raw_paths)]
  with (OUT/(variant+'-remerge.stdout')).open('xb') as a,(OUT/(variant+'-remerge.stderr')).open('xb') as b:result=subprocess.run(command,stdout=a,stderr=b)
  assert result.returncode==0 and sha(profile_out)==sha(profile),'independent profile merge differs'
  assert br['pgo']['mode']=='profile-use' and br['pgo']['inputs_unchanged']
  assert br['pgo']['input_sha256_before']==br['pgo']['input_sha256_after']=={str(profile):sha(profile),str(tr/'training.json'):sha(tr/'training.json')}
  assert sha(build/'rook2-exact')==br['binary_output']['sha256']==identity['native_artifact_sha256']
  warning=(build/'build.stderr').read_text().lower();assert all(s not in warning for s in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data'])
  assert identity['missing_function_warnings']==0
  for directory,receipt in [(ib,tb),(build,br)]:
   with tarfile.open(directory/'verified-source-before.tar.gz','r:gz') as archive:
    members={m.name:hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in archive}
   assert members==receipt['source_sha256_before']|receipt['tool_sha256_before']
  use_report=replay(check/'profile-all.stdout',build/'rook2-exact',False,OUT/'raw'/variant/'profile-use')
  assert not (check/'profile-all.stderr').stat().st_size
  wr=load(wire/'receipt.json');fixtures=load(SPEC/'fixtures/interrupted-sessions-v1.json')['cases'];assert wr['pass'] and len(wr['results'])==len(fixtures)==8
  assert wr['engine_sha256_before']==wr['engine_sha256_after']==sha(build/'rook2-exact')
  searches=0
  for row,c in zip(wr['results'],fixtures):
   assert row['id']==c['id'] and row['status']=='pass' and row['complete_streams'] and row['exit_code']==row['observed_exit_code']==0
   for key,value in row['raw'].items():
    q=wire/c['id']/(key+'.raw');assert sha(q)==value['sha256'] and q.stat().st_size==value['bytes']
   assert (wire/c['id']/'stderr.raw').read_bytes()==b''
   text=(wire/c['id']/'stdout.raw').read_text();assert text.endswith('\n');lines=iter(text.splitlines());stdin=[]
   for request,answer in zip(c['request']['input']['searches'],c['expected']['results']):
    commands=request['commands'];stdin+=commands+[f"time {request['allowanceCs']}",'cm_parm','go']+request['queued']
    for command in commands:
     if command.startswith('cm_parm '):assert next(lines)==' '.join(command.split())
    assert next(lines)=='cm_parm'
    assert [semantic(next(lines),True) for _ in answer['events']]==answer['events']
    if request['queued'] and request['queued'][-1]=='force':assert next(lines)=='aborting search ...'
    searches+=1
   assert list(lines)==[] and (wire/c['id']/'stdin.raw').read_text()=='\n'.join(stdin+['quit'])+'\n'
  assert searches==24
  variants[variant]=dict(artifact_sha256=sha(build/'rook2-exact'),profile_sha256=sha(profile),profile_independently_remerged=True,profile_remerge_exit_code=result.returncode,profile_remerge_command=command,profile_remerge_stdout_sha256=sha(OUT/(variant+'-remerge.stdout')),profile_remerge_stderr_sha256=sha(OUT/(variant+'-remerge.stderr')),training_replay_sha256=sha(tr/'replay.json'),post_use_replay_sha256=sha(check/'profile-all.stdout'),training_verification_sha256=sha(tr/'verification.json'),training_strict_replays=54,post_use_strict_replays=54,raw_profiles=54,wire_fixtures=8,wire_searches=24,source_sha256=source_map,training_record_sha256=sha(tr/'training.json'),build_receipt_sha256=sha(build/'receipt.json'),strict_identity_sha256=sha(check/'identity.json'),wire_receipt_sha256=sha(wire/'receipt.json'))
 assert variants['baseline']['artifact_sha256']==load(HERE/'control-reuse.json')['artifact_sha256']
 assert variants['baseline']['source_sha256']==load(HERE/'plan.json')['control_source_sha256']
 assert variants['phase1']['source_sha256']==load(HERE/'plan.json')['engine_source_sha256']
 changed=[n for n,h in variants['baseline']['source_sha256'].items() if variants['phase1']['source_sha256'][n]!=h];assert changed==['src/attacks.rs','src/movegen.rs']
 out=dict(status='pass',variants=variants,changed_source_paths=changed,compiler_training_replays=108,post_use_replays=108,wire_fixtures=16,wire_searches=48,raw_profiles=108,verifier_sha256=sha(Path(__file__)),control_reuse=True, control_same_artifact=True, candidate_own_profile_only=True, scope='Independent baseline reused-artifact and phase1 own raw/source/profile remerge/archive/artifact reconciliation; no CPU timing or adoption claim')
 with (OUT/'independent-verification.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in out.items() if k!='variants'}))
if __name__=='__main__':main()
