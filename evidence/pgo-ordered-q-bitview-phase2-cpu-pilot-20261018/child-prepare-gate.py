"""Saved evidence/source/profile hash gate only; never launches native commands."""
from pathlib import Path
import hashlib,json,re,gzip,tarfile,os,datetime
G=Path(__file__).parent;E=G.parent;D={};variants={};checks={};settings=[];maps=[];tools=[];corpora=[]
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13] and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp';assert not (G/'regression-gate.json').exists()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def dep(p):D[str(p.resolve())]=h(p)
def terminal(p):
 t=load(p);assert t['exit_code']==0 and t['actual_tool_terminal_observed'];dep(p);return t
def semantic(s,wire=False):
 if s.startswith('move '):return {'type':'move','move':s[5:]}
 if s.startswith('stat01: '):
  m=re.fullmatch(r'stat01:\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)(?: (.*))?',s);assert m
  a,b,c,d,e=map(int,m.groups()[:5]);return dict(type='status',engineCentiseconds=a,searchId=b,depthToken=c,remaining=d,total=e,pv=(m[6] or '').replace('0','O'))
 m=re.fullmatch(r'\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?',s);assert m,s
 a,b,c,d=map(int,m.groups()[:4]);pv=(m[5] or '').strip().replace('0','O');return dict(type='post',depthToken=a,evaluation=b,engineCentiseconds=c,searchId=d,pv=pv) if wire else dict(depth=a,score=b,workThousands=c,searchId=d,pv=pv)
SPEC=Path('/home/legolas/king-spec/conformance');work=load(SPEC/'profiling/workloads.json');oracle=load(SPEC/'profiling/replay-oracle.json');fixture=load(SPEC/'fixtures/interrupted-sessions-v1.json')['cases']
def replay(path,engine,training):
 report=load(path);assert report['status']=='pass' and len(report['results'])==len(work['cases'])==len(oracle['cases'])==54;assert report['selectedCases']==[c['id'] for c in work['cases']];assert len({r['pid'] for r in report['results']})==54
 for row,c in zip(report['results'],work['cases']):
  a=next(a for a in oracle['cases'] if a['id']==c['id']);assert row['case']==c['id'] and row['status']=='pass' and row['complete'] and not row['truncated'] and row['error'] is None;assert row['exit']==a['exit']==dict(code=0,signal=None) and row['stderr']==a['stderr']=='';assert not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0
  assert row['command']==(['/usr/bin/taskset','-c','14'] if training else [])+[str(engine),'--work-clock=kingwcr','--work-clock-post=work'];assert row['stdout'].endswith('\n');lines=row['stdout'].splitlines();acks=[s for s in c['protocol']['recordsBeforeSearch'] if s.startswith('cm_parm ')]+['cm_parm rnd=0'];assert lines[:len(acks)]==acks;lines=lines[len(acks):];assert [semantic(s) for s in lines[:len(a['posts'])]]==a['posts'];assert lines[len(a['posts']):]==['move '+a['move']]+a['resultRecords']
 dep(path);return report
for label,prefix,image,profile,nativeprefix,units in [
 ('baseline','pgo-ordered-bit-checkers-phase1','7b17c00030363da52ce797e41cbbc29de4433ede4491c80d3799c7d08383d200','e55270f63f4683752f4f4255cd192d2b280cdff22deb44ee41a4d29bc90a06fa','ordered-bit-checkers-phase1',143),
 ('q_bits','pgo-ordered-q-bitview-phase2','737a0946184faf1b2c326d14542f12971960382457ea6b3b67a08a32f42da513','1db7591fd5177943902d802d4597c928d323d5f862209080cd92deacf428defe','ordered-q-bitview-phase2',145)]:
 P=E/(prefix+'-preparation-20261018');T=E/(prefix+'-training-20261018');I=E/(prefix+'-instrumented-build-20261018');B=E/(prefix+'-use-build-20261018');U=E/(prefix+'-use-check-20261018');W=E/(prefix+'-interruption-wire-20261018');N=E/(nativeprefix+'-validation-20261018');R=E/(prefix+'-reconciliation-20261018')
 summary=load(P/'validation-summary.json');final=terminal(P/'finalize-tool-terminal.json');assert final['validation_summary_sha256']==h(P/'validation-summary.json') and final['validation_file_manifest_sha256']==h(P/'validation-file-manifest.json');assert summary['all_owned_processes_terminal'];source=Path(summary['candidate_source_root']);native=load(N/'native-verification.json');assert native['complete'] and native['inputs_stable'] and sum(r['passed'] for r in native['units'].values())==units
 training=load(T/'training.json');verification=load(T/'verification.json');ci=load(U/'identity.json');br=load(B/'receipt.json');ib=load(I/'receipt.json');assert training['complete'] and verification['complete'] and verification['independent_remerge_byte_identical'];assert verification['training_record_sha256']==h(T/'training.json');assert ci['status']=='pass' and ci['strict_replays']==54 and ci['interruption_fixtures']==8 and ci['interruption_searches']==24 and ci['missing_function_warnings']==0;assert summary['missing_or_stale_function_warnings']==0
 assert h(B/'rook2-exact')==br['binary_output']['sha256']==ci['native_artifact_sha256']==summary['candidate_artifact_sha256']==image;assert h(I/'rook2-exact')==ib['binary_output']['sha256']==training['instrumented_engine_sha256']==summary['candidate_instrumented_artifact_sha256'];assert h(I/'receipt.json')==training['instrumented_build_receipt']['sha256']
 native_map=br['source_sha256_before'];tool_map=br['tool_sha256_before'];assert len(native_map)==43 and len(tool_map)==23;assert native_map==br['source_sha256_after']==ib['source_sha256_before']==ib['source_sha256_after']==training['engine_source_sha256']==native['source_before']==native['source_after']==ci['source_before']==ci['source_after']==summary['candidate_source_sha256'];assert tool_map==br['tool_sha256_after']==ib['tool_sha256_before']==ib['tool_sha256_after']==summary['tool_source_sha256'];maps.append(native_map);tools.append(tool_map)
 for name,sha in {**native_map,**tool_map}.items():assert h(source/name)==sha;dep(source/name)
 for directory,receipt in [(B,br),(I,ib)]:
  assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot'
  for name,sha in {**native_map,**tool_map}.items():assert h(directory/'source-before'/name)==sha;dep(directory/'source-before'/name)
  ar=load(directory/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and ar['binary_sha256']==receipt['binary_output']['sha256'] and h(directory/ar['archive'])==ar['sha256']
  with tarfile.open(directory/ar['archive']) as t:
   members=[m for m in t.getmembers() if m.isfile()];assert len(members)==66 and {m.name for m in members}==set(native_map)|set(tool_map);assert all(hashlib.sha256(t.extractfile(m).read()).hexdigest()==(native_map|tool_map)[m.name] for m in members)
  for p in [directory/'receipt.json',directory/'archive-receipt.json',directory/ar['archive'],directory/'rook2-exact',directory/'build.stdout',directory/'build.stderr']:dep(p)
  terminal(directory/'tool-terminal.json')
 assert br['pgo']['mode']=='profile-use' and br['pgo']['inputs_unchanged'];assert br['pgo']['input_sha256_before']==br['pgo']['input_sha256_after']=={str(T/'merged.profdata'):profile,str(T/'training.json'):h(T/'training.json')};assert '-pgo-warn-missing-function' in ' '.join(br['rust_flags'])
 warning=(B/'build.stderr').read_text().lower();assert not any(s in warning for s in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data'])
 settings.append({k:br[k] for k in ['mode','target_triple','target_cpu','jobs','toolchain','cargo_config_sha256_before']});assert br['toolchain']==ib['toolchain'] and br['rust_flags'][:2]==ib['rust_flags'][:2]==training['base_rust_flags']==['-C','target-cpu=x86-64']
 assert h(T/'merged.profdata')==verification['merged_profile_sha256']==training['profile_sha256']==ci['profile_sha256']==summary['candidate_profile_sha256']==profile;assert h(T/'independently-merged.profdata')==profile and (T/'independently-merged.profdata').read_bytes()==(T/'merged.profdata').read_bytes();assert gzip.decompress((T/'merged.profdata.gz').read_bytes())==(T/'merged.profdata').read_bytes() and h(T/'merged.profdata.gz')==training['profile_archive_sha256'];assert h(T/'replay.json')==training['replay_sha256'];assert h(T/'launch.json')==training['launch_sha256'];assert h(T/'train.py')==training['driver_sha256']
 raw=sorted((T/'raw').glob('*.profraw'));assert len(raw)==54 and {str(p):h(p) for p in raw}==training['raw_profiles_sha256'];train_report=replay(T/'replay.json',I/'rook2-exact',True);assert {int(p.stem.rsplit('-',1)[1]) for p in raw}=={row['pid'] for row in train_report['results']};assert not (T/'replay.stderr').stat().st_size
 for p in raw:dep(p)
 for p in [T/'merged.profdata',T/'independently-merged.profdata',T/'merged.profdata.gz',T/'training.json',T/'verification.json',T/'launch.json',T/'plan.json',T/'train.py',T/'verify.py',T/'input-closure.json']:dep(p)
 terminal(T/'tool-terminal.json');terminal(T/'verify-tool-terminal.json');terminal(U/'tool-terminal.json');terminal(R/'tool-terminal.json')
 for closure in [T/'input-closure.json',U/'input-closure.json']:
  assert all(h(Path(p))==sha for p,sha in load(closure).items())
  for p in load(closure):dep(Path(p))
 corpora.append(training['input_sha256']);assert all(h(Path(p))==sha for p,sha in training['input_sha256'].items());use_report=replay(U/'profile-all.stdout',B/'rook2-exact',False);assert h(U/'profile-all.stdout')==ci['replay_sha256'] and not (U/'profile-all.stderr').stat().st_size
 if label=='q_bits':
  seen=load(T/'actual-engine-affinities.json');assert {r['pid'] for r in seen}=={r['pid'] for r in train_report['results']} and all(r['affinity']==[14] for r in seen);dep(T/'actual-engine-affinities.json')
  for stem,number in [('replay',54),('wire',8)]:assert len(ci['stages'][stem]['actual_engine_affinities'])==number and all(r['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13] for r in ci['stages'][stem]['actual_engine_affinities'])
 wr=load(W/'receipt.json');assert wr['pass'] and len(wr['results'])==len(fixture)==8;assert wr['engine_sha256_before']==wr['engine_sha256_after']==image and wr['fixture_sha256']==h(SPEC/'fixtures/interrupted-sessions-v1.json')
 for row,c in zip(wr['results'],fixture):
  assert row['id']==c['id'] and row['status']=='pass' and row['complete_streams'] and row['exit_code']==row['observed_exit_code']==0
  for key,value in row['raw'].items():
   p=W/c['id']/(key+'.raw');assert h(p)==value['sha256'] and p.stat().st_size==value['bytes'];dep(p)
  assert not (W/c['id']/'stderr.raw').stat().st_size;text=(W/c['id']/'stdout.raw').read_text();assert text.endswith('\n');lines=iter(text.splitlines());stdin=[];assert len(c['request']['input']['searches'])==len(c['expected']['results'])==len(row['searches'])==3
  for request,answer,actual in zip(c['request']['input']['searches'],c['expected']['results'],row['searches']):
   commands=request['commands'];stdin+=commands+[f"time {request['allowanceCs']}",'cm_parm','go']+request['queued']
   for command in commands:
    if command.startswith('cm_parm '):assert next(lines)==' '.join(command.split())
   assert next(lines)=='cm_parm';assert [semantic(next(lines),True) for _ in answer['events']]==answer['events']==actual['events']
   abort=bool(request['queued'] and request['queued'][-1]=='force');assert actual['abort']==abort
   if abort:assert next(lines)=='aborting search ...'
  assert list(lines)==[] and (W/c['id']/'stdin.raw').read_text()=='\n'.join(stdin+['quit'])+'\n'
 for p in [P/'validation-summary.json',P/'validation-file-manifest.json',P/'finalize-tool-terminal.json',P/'control-reuse.json',P/'plan.json',P/'readiness.json',P/'readiness-tool-terminal.json',P/'execution-clearance.json',P/'execution-context.json',N/'native-verification.json',U/'identity.json',U/'input-closure.json',U/'profile-all.stderr',W/'receipt.json',R/'independent-verification.json']:dep(p)
 for name in ['final-process-check.json','report.md']:
  if(P/name).exists():dep(P/name)
 for path,record in summary['terminal_records'].items():assert load(Path(path))==record;terminal(Path(path))
 checks[label]={'own_native_units_reused':units,'own_training_replays':54,'pid_raw_profiles':54,'independent_merge_byte_identical':True,'strict54':True,'wire8_searches24':True,'source43_tools23_and_two_archives66':True,'zero_missing_stale_warnings':True,'actual_closures':True};variants[label]={'path':str(B/'rook2-exact'),'sha256':image}
assert settings[0]==settings[1] and tools[0]==tools[1] and corpora[0]==corpora[1];changed=[n for n in sorted(maps[0]) if maps[0][n]!=maps[1][n]];assert changed==['src/attacks.rs','src/movegen.rs','src/quiescence.rs']
P=E/'pgo-ordered-q-bitview-phase2-preparation-20261018';reuse=load(P/'control-reuse.json');assert reuse['artifact_sha256']==variants['baseline']['sha256'];assert reuse['profile_sha256']=='e55270f63f4683752f4f4255cd192d2b280cdff22deb44ee41a4d29bc90a06fa';assert all(h(Path(p))==sha for p,sha in reuse['metadata_sha256'].items())
for p in reuse['metadata_sha256']:dep(Path(p))
R=E/'pgo-ordered-q-bitview-phase2-reconciliation-20261018';ind=load(R/'independent-verification.json');assert ind['status']=='pass' and ind['candidate_own_profile_only'] and ind['control_same_artifact'] and ind['changed_source_paths']==changed
for role,profile in [('baseline','e55270f63f4683752f4f4255cd192d2b280cdff22deb44ee41a4d29bc90a06fa'),('phase2','1db7591fd5177943902d802d4597c928d323d5f862209080cd92deacf428defe')]:assert h(R/(role+'-independently-merged.profdata'))==profile;dep(R/(role+'-independently-merged.profdata'))
for p in [SPEC/'fixtures/interrupted-sessions-v1.json',*[SPEC/'profiling'/n for n in ['workloads.json','replay-oracle.json','replay-check.mjs','benchmark.mjs']],Path(__file__),E/'ordered-q-bitview-phase2-proposal-20261018/scoped-source-proof.json',E/'ordered-q-bitview-phase2-proposal-20261018/source-manifest.json',E/'ordered-q-bitview-phase2-proposal-20261018/proposal.patch',E/'ordered-q-bitview-phase2-validation-20261018/native-first-actual-terminal.json',E/'ordered-q-bitview-phase2-validation-20261018/generic-retry-actual-terminal.json']:dep(p)
for p,sha in D.items():assert h(Path(p))==sha
write(G/'child-gate-review.json',{'complete':True,'variants':variants,'checks':checks,'compiler_settings_corpus_equal':True,'source_delta':changed,'source_scope':'Frozen phase2 proof: attacks test-only; movegen thin owner/test transport+cfg gate; Q3sites; full/capped/Boolean/projector/maintenance/ordinary source unchanged','control_exact_reuse':True,'candidate_own_profile_only':True,'native_engine_cpu_profiler_jobs_launched':0,'scope':'Frozen semantic and own-profile provenance prerequisites only; no CPU neutrality, speedup or adoption claim. Parent owns later driver/pilot. Dependencies immutable after this write.','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});dep(G/'child-gate-review.json')
write(G/'regression-gate.json',{'complete':True,'variants':variants,'dependencies':D});print(json.dumps({'complete':True,'gate_sha256':h(G/'regression-gate.json'),'dependencies':len(D),'variants':variants,'native_engine_cpu_profiler_jobs_launched':0}))
