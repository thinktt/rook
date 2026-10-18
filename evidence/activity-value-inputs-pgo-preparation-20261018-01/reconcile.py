"""Independent activity-value source/profile/artifact/raw reconciliation; no engine runs."""
from guard import *
import gzip,re,tarfile
from raw_model import replay,semantic
OUT=Path(PLAN['reconciliation'])
SPEC=Path('/home/legolas/king-spec/conformance')
def main():
 require_clearance();check_inputs();assert not OUT.exists();OUT.mkdir();variants={}
 for variant,source in [('activity-value-inputs',PLAN['source_root'])]:
  tr=Path(PLAN['training']);ib=Path(PLAN['instrumented_build']);build=Path(PLAN['use_build']);check=Path(PLAN['use_check']);wire=Path(PLAN['wire'])
  for q in [ib/'tool-terminal.json',tr/'tool-terminal.json',tr/'verify-tool-terminal.json',build/'tool-terminal.json',check/'tool-terminal.json']:terminal(q)
  training=load(tr/'training.json');tb=load(ib/'receipt.json');br=load(build/'receipt.json');identity=load(check/'identity.json');tv=load(tr/'verification.json')
  source_map=source_snapshot(Path(source));assert source_map==training['engine_source_sha256']==tb['source_sha256_before']==tb['source_sha256_after']==br['source_sha256_before']==br['source_sha256_after']==PLAN['engine_source_sha256']
  assert training['complete'] and tv['complete'] and tv['training_record_sha256']==sha(tr/'training.json')
  for closure_path in [tr/'input-closure.json']:
   assert all(sha(Path(p))==h for p,h in load(closure_path).items())
  assert training['instrumented_engine_sha256']==sha(ib/'rook2-exact')==tb['binary_output']['sha256']
  assert sha(ib/'receipt.json')==training['instrumented_build_receipt']['sha256']
  assert tb['tool_sha256_before']==tb['tool_sha256_after']==br['tool_sha256_before']==br['tool_sha256_after']==PLAN['tool_source_sha256']
  raw_paths=sorted((tr/'raw').glob('*.profraw'));assert len(raw_paths)==54 and {str(p):sha(p) for p in raw_paths}==training['raw_profiles_sha256']
  train_report=replay(tr/'replay.json',ib/'rook2-exact',True,OUT/'raw'/variant/'training')
  assert len({row['pid'] for row in train_report['results']})==54
  assert {int(p.stem.rsplit('-',1)[1]) for p in raw_paths}=={row['pid'] for row in train_report['results']}
  assert not (tr/'replay.stderr').stat().st_size
  profile=tr/'merged.profdata';assert sha(profile)==training['profile_sha256']==tv['merged_profile_sha256']==identity['profile_sha256']
  assert gzip.decompress((tr/'merged.profdata.gz').read_bytes())==profile.read_bytes()
  assert sha(tr/'merged.profdata.gz')==training['profile_archive_sha256']
  merge_tool=Path('/usr/bin/llvm-profdata-19');assert sha(merge_tool.resolve())==training['merge_tool_sha256']
  profile_out=OUT/(variant+'-independently-merged.profdata');merge_argv=[str(merge_tool),'merge','-o',str(profile_out),*map(str,raw_paths)]
  with (OUT/(variant+'-remerge.stdout')).open('xb') as a,(OUT/(variant+'-remerge.stderr')).open('xb') as b:result=subprocess.run(merge_argv,stdout=a,stderr=b)
  assert result.returncode==0 and sha(profile_out)==sha(profile),'independent profile merge differs'
  assert br['pgo']['mode']=='profile-use' and br['pgo']['inputs_unchanged']
  assert br['pgo']['input_sha256_before']==br['pgo']['input_sha256_after']=={str(profile):sha(profile),str(tr/'training.json'):sha(tr/'training.json')}
  assert br['toolchain']==tb['toolchain']==PLAN['toolchain']
  assert sha(build/'rook2-exact')==br['binary_output']['sha256']==identity['artifact_sha256']
  warning=(build/'build.stderr').read_text().lower();assert all(s not in warning for s in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data'])
  assert load(HERE/'use-stage.json')['missing_or_stale_profile_warnings']==0
  for directory,receipt in [(ib,tb),(build,br)]:
   with tarfile.open(directory/'verified-source-before.tar.gz','r:gz') as archive:
    members={m.name:hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in archive}
   assert members==receipt['source_sha256_before']|receipt['tool_sha256_before']
  use_report=replay(check/'profile-all.stdout',build/'rook2-exact',False,OUT/'raw'/variant/'profile-use')
  run(['/usr/bin/node',str(HERE/'recheck.mjs'),str(tr/'replay.json'),str(check/'profile-all.stdout')],OUT/'original-checkReplay')
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
  variants[variant]=dict(artifact_sha256=sha(build/'rook2-exact'),profile_sha256=sha(profile),profile_independently_remerged=True,profile_remerge_exit_code=result.returncode,profile_remerge_command=merge_argv,profile_remerge_stdout_sha256=sha(OUT/(variant+'-remerge.stdout')),profile_remerge_stderr_sha256=sha(OUT/(variant+'-remerge.stderr')),training_replay_sha256=sha(tr/'replay.json'),post_use_replay_sha256=sha(check/'profile-all.stdout'),training_verification_sha256=sha(tr/'verification.json'),training_strict_replays=54,post_use_strict_replays=54,raw_profiles=54,wire_fixtures=8,wire_searches=24,source_sha256=source_map,training_record_sha256=sha(tr/'training.json'),build_receipt_sha256=sha(build/'receipt.json'),strict_identity_sha256=sha(check/'identity.json'),wire_receipt_sha256=sha(wire/'receipt.json'))
 check_inputs()
 write(OUT/'independent-verification.json',dict(complete=True,variants=variants,own_profile_only=True,strict_training54=True,fresh_strict54=True,wire8_searches24=True,scope='Compiler-training/regression provenance only; no CPU or qualification claim'))
if __name__=='__main__':main()
