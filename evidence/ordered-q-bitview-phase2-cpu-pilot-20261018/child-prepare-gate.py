from pathlib import Path
import hashlib,json,os,re,subprocess,tarfile,datetime
E=Path('/home/legolas/rook2/evidence');G=Path(__file__).parent;V=E/'ordered-q-bitview-phase2-validation-20261018';C=V/'codegen';P=E/'ordered-q-bitview-phase2-proposal-20261018';I=json.loads((C/'inputs.json').read_text());D={};checks={};variants={}
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13] and not (G/'regression-gate.json').exists()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def dep(p):D[str(p.resolve())]=h(p)
for label,count,source,N,O,W in [
 ('phase1',143,Path('/tmp/imp2-ordered-bit-checkers-phase1-validation-20261018-lys_zi80'),E/'ordered-bit-checkers-phase1-validation-20261018',E/'ordered-bit-checkers-phase1-strict-check-20261018',E/'ordered-bit-checkers-phase1-interruption-wire-20261018'),
 ('phase2',145,Path('/home/legolas/rook2-work/ordered-q-bitview-phase2-20261018-5v7mxmev'),V,V/'ordinary-check',V/'interruption-wire')]:
 item=I['artifacts'][label];B=Path(item['build']);b=load(B/'receipt.json');n=load(N/'native-verification.json');o=load(O/'identity.json');w=load(W/'receipt.json')
 assert h(Path(item['binary']))==item['binary_sha256'] and h(B/'receipt.json')==item['receipt_sha256'];assert n['complete'] and n['inputs_stable'] and sum(x['passed'] for x in n['units'].values())==count;assert b['source_sha256_before']==b['source_sha256_after']==n['source_before']==n['source_after']
 assert len(item['source_sha256'])==43 and len(item['tool_source_sha256'])==23;files={**item['source_sha256'],**item['tool_source_sha256']}
 for name,sha in files.items():
  for p in [source/name,B/'source-before'/name]:assert h(p)==sha;dep(p)
 a=load(B/'archive-receipt.json');assert a['binary_sha256']==item['binary_sha256'] and h(B/a['archive'])==a['sha256']
 with tarfile.open(B/a['archive']) as t:
  members=[m for m in t.getmembers() if m.isfile()];assert len(members)==66 and {m.name for m in members}==set(files);assert all(hashlib.sha256(t.extractfile(m).read()).hexdigest()==files[m.name] for m in members)
 for stem,expected in [('rook2',count-2),('rook2-dev',2)]:
  raw=(N/(stem+'-tests.stdout')).read_text();assert re.search(r'test result: ok\. '+str(expected)+r' passed; 0 failed;',raw);assert len(re.findall(r'^test .+ \.\.\. ok$',raw,re.M))==expected;assert h(N/'unit-bin'/stem/'rook2-exact')==n['units'][stem]['binary_sha256'];dep(N/(stem+'-tests.stdout'));dep(N/(stem+'-tests.stderr'))
 for stage,stem in zip(n['stages'],['unit-build','rook2-tests','rook2-dev-tests']):assert stage['exit_code']==0 and h(N/(stem+'.stdout'))==stage['stdout_sha256'] and h(N/(stem+'.stderr'))==stage['stderr_sha256']
 assert o['complete'] and o['inputs_stable'] and o['strict_replays']==54 and o['interruption_fixtures']==8 and o['interruption_searches']==24
 before=load(O/'inputs-before.json');after=load(O/'inputs-after.json');assert before['dependencies']==after['dependencies'] and before['native']==after['native']==n['source_before'];assert before['engine_sha256']==after['engine_sha256']==item['binary_sha256']
 for name,sha in before['dependencies'].items():assert h(Path(name))==sha;dep(Path(name))
 for stage,stem in zip(o['stages'],['strict54','wire']):assert stage['exit_code']==0 and h(O/(stem+'.stdout'))==stage['stdout_sha256'] and h(O/(stem+'.stderr'))==stage['stderr_sha256']
 fixture=load(V/'ordinary-check/interrupted-sessions-v1.json');assert w['pass'] and len(w['results'])==8 and w['engine_sha256_before']==w['engine_sha256_after']==item['binary_sha256'];assert w['fixture_sha256']==h(V/'ordinary-check/interrupted-sessions-v1.json')
 # Reparse original wire output without executing a checker or engine.
 def event(line):
  if line.startswith('move '):return {'type':'move','move':line[5:]}
  m=re.fullmatch(r'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?',line)
  if m:
   cs,sid,depth,remaining,total=map(int,m.groups()[:5]);return {'type':'status','engineCentiseconds':cs,'searchId':sid,'depthToken':depth,'remaining':remaining,'total':total,'pv':(m[6] or '').strip().replace('0','O')}
  m=re.fullmatch(r' *(-?\d+) +([+-]?\d+) +(\d+) +(\d+)(?: (.*))?',line);assert m,line
  depth,score,cs,sid=map(int,m.groups()[:4]);return {'type':'post','depthToken':depth,'evaluation':score,'engineCentiseconds':cs,'searchId':sid,'pv':(m[5] or '').strip().replace('0','O')}
 for case,row in zip(fixture['cases'],w['results']):
  assert case['id']==row['id'] and row['exit_code']==row['observed_exit_code']==0 and row['complete_streams'];raw={k:(W/case['id']/(k+'.raw')).read_bytes() for k in ['stdin','stdout','stderr']}
  for k,data in raw.items():assert row['raw'][k]=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};dep(W/case['id']/(k+'.raw'))
  assert not raw['stderr'] and raw['stdout'].endswith(b'\n');lines=raw['stdout'].decode().splitlines();commands=[];assert len(case['request']['input']['searches'])==len(case['expected']['results'])==len(row['searches'])==3
  for search,expected,actual in zip(case['request']['input']['searches'],case['expected']['results'],row['searches']):
   commands+=search['commands']+['time '+str(search['allowanceCs']),'cm_parm','go']+search['queued'];acks=[' '.join(c.split()) for c in search['commands'] if c.startswith('cm_parm ')]+['cm_parm'];assert lines[:len(acks)]==acks;del lines[:len(acks)];assert [event(lines.pop(0)) for _ in expected['events']]==expected['events']==actual['events'];abort=bool(search['queued'] and search['queued'][-1]=='force');assert actual['abort']==abort
   if abort:assert lines.pop(0)=='aborting search ...'
  assert not lines and raw['stdin']==('\n'.join(commands+['quit'])+'\n').encode()
 for p in [B/'receipt.json',B/'archive-receipt.json',B/a['archive'],N/'native-verification.json',N/'tool-terminal.json',O/'identity.json',O/'strict54.stdout',O/'inputs-before.json',O/'inputs-after.json',O/'tool-terminal.json',W/'receipt.json']:dep(p)
 variants['baseline' if label=='phase1' else 'q_bits']={'path':item['binary'],'sha256':item['binary_sha256']};checks[label]={'native_units':count,'strict54':True,'wire8_searches24':True,'source43_tools23_and_archive66':True}
for key in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain']:assert I['artifacts']['phase1']['build_settings'][key]==I['artifacts']['phase2']['build_settings'][key]
assert I['artifacts']['phase1']['tool_source_sha256']==I['artifacts']['phase2']['tool_source_sha256'];assert I['changed_source_paths']==['src/attacks.rs','src/movegen.rs','src/quiescence.rs']
# Exact inverse-scoping proofs copied verbatim from the frozen source-only freeze assertions, without rerunning freeze.
A=Path(I['artifacts']['phase1']['build'])/'source-before';B=Path(I['artifacts']['phase2']['build'])/'source-before';q=(B/'src/quiescence.rs').read_text()
for new,old in [
('                let projected = position.attack_view().projected(&position, movement);','                let board = movegen::projected_board(&position, movement);'),
('                    movegen::check_routes_bits(&projected, enemy_king, position.side, movement.to());','                    movegen::check_routes(&board, enemy_king, position.side, movement.to());'),
('                if projected.attacked(king_after, position.side.opponent()) {','                if movegen::attacked(&board, king_after, position.side.opponent()) {')]:assert q.count(new)==1;q=q.replace(new,old)
assert q==(A/'src/quiescence.rs').read_text();a=(B/'src/attacks.rs').read_text();old=(A/'src/attacks.rs').read_text();assert a.split('\n#[cfg(test)]\n',1)[0]==old.split('\n#[cfg(test)]\n',1)[0];index=a.index('\n    /// Compare before own-king legality:');assert a[:index]+a[a.rfind('\n}'):]==old
m=(B/'src/movegen.rs').read_text();start=m.index('/// Q supplies its one projected tag-plane view.');end=m.index('/// The tactical caller supplies a projected board',start);assert (m[:start]+m[end:]).replace('#[cfg(test)]\npub(crate) fn check_routes(', 'pub(crate) fn check_routes(',1)==(A/'src/movegen.rs').read_text()
s=subprocess.run(['/usr/bin/node',str(G/'child-baseline-strict.mjs')],capture_output=True);(G/'child-baseline-strict.stdout').write_bytes(s.stdout);(G/'child-baseline-strict.stderr').write_bytes(s.stderr);assert s.returncode==0,s.stderr.decode()
assert load(V/'independent-reconciliation.json')['pass'];assert load(C/'tool-terminal.json')['complete'];assert load(V/'final-process-check.json')['all_owned_native_build_test_engine_codegen_processes_terminal']
for base,names in [(E/'ordered-bit-checkers-phase1-strict-check-20261018',['actual-tool-terminal.json','independent-verification.json','independent-tool-terminal.json']), (E/'ordered-bit-checkers-phase1-validation-20261018',['native-actual-terminal.json','final-process-check.json']), (P,['prepared.json','source-manifest.json','proposal.patch','scoped-source-proof.json']), (V,['native-first-actual-terminal.json','native-build-driver.stderr','generic-retry-actual-terminal.json','strict-wire-actual-terminal.json','independent-actual-terminal.json','independent-reconciliation.json','report.md','identity.json','tool-terminal.json','final-process-check.json']), (C,['inputs.json','inputs-after.json','actual-terminals.json','focused-analysis.json','analysis-summary.json','output-sha256.json','report.md','tool-terminal.json']), (G,['child-prepare-gate.py','child-baseline-strict.mjs','child-baseline-strict.stdout','child-baseline-strict.stderr'])]:
 for name in names:dep(base/name)
for p in sorted((V/'ordinary-check/profiling').glob('*')):dep(p)
for p in sorted(C.glob('*version.txt')):dep(p)
for p,sha in D.items():assert h(Path(p))==sha
write(G/'child-gate-review.json',{'complete':True,'checks':checks,'same_compiler_settings':True,'source_delta':'attacks test-only; movegen thin route + test transport/cfg gate; Q exactly3sites. Full/capped/Boolean/projector/maintenance/ordinary source unchanged. No state/layout/API changes.','no_engine_cpu_profile_run':True,'scope':'Exact passed semantic prerequisite and source-only performance role; no CPU neutrality, gain, or adoption claim','preserved_failure':'81147/38b720 exit1, empty precreated build output; native145 retained, retry67855/83efd9 exit0 binds build02','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});dep(G/'child-gate-review.json')
write(G/'regression-gate.json',{'complete':True,'variants':variants,'dependencies':D});print(json.dumps({'complete':True,'gate_sha256':h(G/'regression-gate.json'),'dependencies':len(D),'variants':variants,'engine_runs':0,'cpu_runs':0}))
