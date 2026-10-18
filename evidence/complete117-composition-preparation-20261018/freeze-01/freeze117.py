#!/usr/bin/env python3
# SOURCE composition/JSON inventory/hash/archive only; no Rust/native commands.
from pathlib import Path
import collections,difflib,hashlib,importlib.util,itertools,json,os,re,sys,tarfile,tempfile,time,traceback
ROOT=Path('/home/legolas/rook2');EV=ROOT/'evidence';HERE=Path(__file__).parent
AUTH=HERE.parent/'composition-authorization.json';OLD=EV/'generic-joined111-proposal-20261018'
sys.dont_write_bytecode=True
# Read-only reuse of already frozen text-patch/lexical inventory/archive utilities.
sys.path.insert(0,str(OLD))
spec=importlib.util.spec_from_file_location('closed111freeze',OLD/'freeze.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hb(b):return hashlib.sha256(b).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
graph=F.graph
def files(p,names):return {n:(Path(p)/n).read_bytes() for n in sorted(names)}
def ids(d):return {n:hb(b) for n,b in sorted(d.items())}
def diff(a,b,names=None):
 out=''
 for n in sorted(set(a)|set(b) if names is None else names):
  if a.get(n)==b.get(n):continue
  out+=''.join(difflib.unified_diff(a.get(n,b'').decode().splitlines(True),b.get(n,b'').decode().splitlines(True),fromfile='a/'+n if n in a else '/dev/null',tofile='b/'+n if n in b else '/dev/null'))
 return out
def apply(before,text):
 # Earlier draft difflib labels an empty newly added file a/name rather than
 # /dev/null. Accept only a real zero-old-lines creation; all context stays exact.
 seeded=dict(before);lines=text.splitlines()
 for i,line in enumerate(lines):
  if line.startswith('--- a/'):
   n=line[6:]
   if n not in seeded:
    assert lines[i+1]=='+++ b/'+n and lines[i+2].startswith('@@ -0,0 '),n
    seeded[n]=b''
 return F.apply_reviewed_patch(seeded,text)
def archive(p,members):
 expected={n:sha(s) for n,s in members.items()}
 receipt=F.archive(p,members)
 write(Path(str(p)+'.members.json'),expected)
 return receipt
def add(t,edits):
 for a,b in edits:
  assert t.count(a)==1 and b not in t,(a,b)
  t=t.replace(a,a+b,1)
 return t
def remove(t,edits):
 for a,b in reversed(edits):
  assert t.count(a+b)==1
  t=t.replace(a+b,a,1)
 return t
C=(('mod controlled_root;\n','mod controlled_timed;\n'),('        "search.genericTimedSearch" => generic_timed::dispatch(input),\n','        "search.timedRootSequence" | "search.workTimedRootSequence" => controlled_timed::dispatch(operation,input),\n'))
P=(('mod post_captures;\n','mod persistent_sessions;\n'),('    match operation {\n','        "session.searches" | "session.clockSeededSearches" | "session.interruptedSearches" | "session.ordinaryIterations" => persistent_sessions::dispatch(operation,input),\n'))
state={'complete':False,'scope':'COMPLETE117_SOURCE_FIXTURE_DECLARATION_ARCHIVE_FREEZE_ONLY','started_ns':time.time_ns(),'pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0)),'TMPDIR':os.environ.get('TMPDIR'),'rust_parsed':False,'native_executions':0,'failure':None}
try:
 authbytes=AUTH.read_bytes();auth=json.loads(authbytes)
 assert auth['authorized'] and auth['scope']=='complete117-source-fixture-declaration-archive-freeze-only'
 assert not auth['rust_parse_format_build_test_engine_codegen_authorized'] and not auth['timing_pgo_profiler_authorized']
 assert state['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13] and state['TMPDIR']=='/home/legolas/rook2-build-tmp'
 oldin=load(OLD/'composition-inputs.json');oldman=load(OLD/'source-manifest.json')
 paths={k:Path(v['path']) for k,v in oldin['parents'].items()}
 paths.update(original111=Path(auth['inputs']['base_failed111']),corrected111=Path(auth['inputs']['corrected111_test_source']),coupled112=Path(auth['inputs']['coupled112']),persistent_original=Path('/home/legolas/rook2-work/imp2-persistent-session113-proposal-20261018-ltjpdmt0'),persistent_rev02=Path(auth['inputs']['persistent113rev02']),go_revision=Path(auth['inputs']['go_revision']))
 names={k:set(v['source_sha256']) for k,v in oldin['parents'].items()}
 names.update(original111=set(oldman['files']),corrected111=set(oldman['files']),coupled112=names['generic110']|{'src/timed_sequence.rs','diagnostic/src/controlled_timed.rs'},persistent_original=names['base109']|{'diagnostic/src/persistent_sessions.rs'},persistent_rev02=names['base109']|{'diagnostic/src/persistent_sessions.rs'},go_revision=names['generic110'])
 parents={k:files(paths[k],n) for k,n in names.items()};before={k:ids(d) for k,d in parents.items()}
 for k,v in oldin['parents'].items():assert before[k]==v['source_sha256'],k
 assert before['original111']==oldman['files'] and graph(before['original111'])==auth['inputs']['base_source_graph_sha256']
 wanted=set(oldman['files'])|{'src/timed_sequence.rs','diagnostic/src/controlled_timed.rs','diagnostic/src/persistent_sessions.rs'}
 rootbefore={n:sha(ROOT/n) if (ROOT/n).is_file() else None for n in sorted(wanted|{'AGENTS.md'})}
 authorities={Path(p) for p in oldin['authority_dependencies']}
 dirs=['coupled-timed112-proposal-20261018','coupled-timed112-parent-review-20261018','coupled-timed112-score-context-review-20261018','persistent-session113-proposal-20261018','persistent-session113-revision02-proposal-20261018','persistent-session113-parent-review-20261018','go-outcome-revision-proposal-20261018','go-outcome-parent-review-20261018','go-outcome-domain-review-20261018','go-outcome-revision-score-context-review-20261018','generic-joined111-test-revision-20261018','generic-joined111-failure-review-20261018','generic-joined111-native-validation-20261018','generic-timed110-proposal-20261018','joined-search110-proposal-20261018']
 for d in dirs:authorities.update(p for p in (EV/d).iterdir() if p.is_file() and p.suffix in {'.json','.md','.patch','.py','.stdout','.stderr'})
 authorities.update({AUTH,HERE.parent/'parent-sequence-revision.md',ROOT/'AGENTS.md',Path('/home/legolas/imp-perf-mission.md'),HERE/'freeze117.py',OLD/'freeze.py',OLD/'guard.py'})
 for n in ['source-manifest.json','prepared.json','source-proof.json','whole-fixture-inventory.json','whole-fixture-map.json','test-declarations.json','trial.patch','native.patch','cold.patch','reviewed-patch-reconstruction.json','composition-inputs.json','tool-terminal.json']:authorities.add(OLD/n)
 for n in ['timed-root-sequence.md','work-timed-root-sequence.md','search-pawn-lifetime.md','seed-lifetime.md','interrupted-sessions.md','persistent-ordinary-session.md','ordinary-session-lifecycle.md','ordinary-xboard-wire.md','personality-configuration.md','root-go-outcome.md','iteration-terminal-stop.md']:authorities.add(Path('/home/legolas/king-spec/spec')/n)
 authorities.update({Path('/home/legolas/king-spec/conformance/run.mjs'),Path('/home/legolas/king-spec/conformance/README.md')})
 authoritybefore={str(p):sha(p) for p in sorted(authorities)}
 write(HERE/'parents-before.json',{'parents':{k:{'path':str(paths[k]),'files':v,'graph_sha256':graph(v)} for k,v in before.items()},'root_source_before':rootbefore,'authority_sha256':authoritybefore})
 recon=[]
 def prove(tag,basis,target,patch):
  made,changed=apply(parents[basis],Path(patch).read_text());assert made==parents[target],tag
  inverse=diff(parents[target],parents[basis]);assert apply(parents[target],inverse)[0]==parents[basis],tag+' inverse'
  (HERE/(tag+'-inverse.patch')).write_text(inverse)
  recon.append({'tag':tag,'basis':basis,'target':target,'patch':str(patch),'sha256':sha(patch),'changed':changed,'complete_endpoint_exact':True,'inverse_exact':True,'target_graph_sha256':graph(ids(made))})
 prove('generic110','base109','generic110',EV/'generic-timed110-proposal-20261018/proposal.patch')
 prove('joined110','base109','joined110',EV/'joined-search110-proposal-20261018/trial.patch')
 prove('original111','base109','original111',OLD/'trial.patch')
 prove('corrected111','original111','corrected111',EV/'generic-joined111-test-revision-20261018/test-only.patch')
 prove('coupled112','generic110','coupled112',EV/'coupled-timed112-proposal-20261018/proposal.patch')
 prove('persistent_original','base109','persistent_original',EV/'persistent-session113-proposal-20261018/trial-draft.patch')
 prove('persistent_rev02','base109','persistent_rev02',EV/'persistent-session113-revision02-proposal-20261018/trial-draft.patch')
 prove('persistent_revision02','persistent_original','persistent_rev02',EV/'persistent-session113-revision02-proposal-20261018/revision02-from-original113.patch')
 prove('go_revision','generic110','go_revision',EV/'go-outcome-revision-proposal-20261018/trial.patch')
 assert {n for n in names['original111'] if parents['original111'][n]!=parents['corrected111'][n]}=={'src/ordinary.rs'}
 a=parents['original111']['src/ordinary.rs'].decode();b=parents['corrected111']['src/ordinary.rs'].decode();marker='pub struct Iteration'
 assert a[a.index(marker):]==b[b.index(marker):] and a.count('#[test]')==b.count('#[test]')
 coupled={'src/engine.rs','src/lib.rs','src/timed.rs','src/timed_sequence.rs','src/timing.rs','src/work_clock.rs'};seed={'src/host.rs','src/session.rs','src/bin/rook2.rs'}
 cp=(EV/'coupled-timed112-proposal-20261018/native.patch').read_text();sp=(EV/'persistent-session113-revision02-proposal-20261018/native-draft.patch').read_text();tp=(EV/'generic-joined111-test-revision-20261018/test-only.patch').read_text()
 assert set(apply(parents['generic110'],cp)[1])==coupled and set(apply(parents['generic110'],sp)[1])==seed
 assert all(parents['go_revision'][n]==parents['persistent_rev02'][n] for n in seed)
 permutations=[]
 for order in itertools.permutations([cp,sp,tp]):
  d=dict(parents['original111'])
  for patch in order:d,_=apply(d,patch)
  permutations.append(d)
 assert all(d==permutations[0] for d in permutations)
 candidate=dict(permutations[0]);owners={n:{'owner':'corrected111','path':str(paths['corrected111']/n)} for n in names['corrected111']}
 for ns,tag in [(coupled,'coupled112'),(seed,'persistent_rev02'),({'src/ordinary.rs'},'corrected111')]:
  for n in ns:owners[n]={'owner':tag,'path':str(paths[tag]/n)}
 for n,tag in [('diagnostic/src/controlled_timed.rs','coupled112'),('diagnostic/src/persistent_sessions.rs','persistent_rev02'),('diagnostic/src/actual_timed.rs','go_revision')]:candidate[n]=parents[tag][n];owners[n]={'owner':tag,'path':str(paths[tag]/n)}
 main='diagnostic/src/main.rs';basemain=parents['corrected111'][main].decode()
 assert add(parents['generic110'][main].decode(),C)==parents['coupled112'][main].decode()
 assert add(parents['base109'][main].decode(),P)==parents['persistent_rev02'][main].decode()
 merged=add(add(basemain,C),P);assert merged==add(add(basemain,P),C)
 assert remove(remove(merged,P),C)==basemain and remove(remove(merged,C),P)==basemain
 candidate[main]=merged.encode();owners[main]={'owner':'commuting additive main merge','base':'corrected111','both_inverses_restore_base':True}
 assert set(candidate)==wanted
 native={n:b for n,b in candidate.items() if not n.startswith(('tools/','diagnostic/'))};tools={n:b for n,b in candidate.items() if n.startswith('tools/')};cold={n:b for n,b in candidate.items() if n.startswith('diagnostic/')}
 assert (len(candidate),len(native),len(tools),len(cold))==(112,46,23,43)
 assert tools=={n:b for n,b in parents['base109'].items() if n.startswith('tools/')}
 assert all(candidate[n]==parents['coupled112'][n] for n in coupled) and all(candidate[n]==parents['persistent_rev02'][n] for n in seed)
 assert all(candidate[n]==parents['original111'][n] for n in native if n not in coupled|seed|{'src/ordinary.rs'})
 assert all(candidate[n]==parents['original111'][n] for n in cold if n not in {main,'diagnostic/src/actual_timed.rs','diagnostic/src/controlled_timed.rs','diagnostic/src/persistent_sessions.rs'})
 source=Path(tempfile.mkdtemp(prefix='imp2-complete117-proposal-20261018-',dir='/home/legolas/rook2-work'));state['source']=str(source)
 for n,b in candidate.items():p=source/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 for tag in ['original111','corrected111','base109','coupled112','persistent_rev02','go_revision']:
  f=diff(parents[tag],candidate);r=diff(candidate,parents[tag]);assert apply(parents[tag],f)[0]==candidate and apply(candidate,r)[0]==parents[tag]
  (HERE/('against-'+tag+'.patch')).write_text(f);(HERE/('against-'+tag+'-inverse.patch')).write_text(r)
 (HERE/'native-from-original111.patch').write_text(diff(parents['original111'],candidate,native));(HERE/'native-from-corrected111.patch').write_text(diff(parents['corrected111'],candidate,native));(HERE/'cold-from-original111.patch').write_text(diff(parents['original111'],candidate,cold))
 write(HERE/'reviewed-patch-reconstruction.json',recon)
 manifest=ids(candidate);ni=ids(native);ti=ids(tools);ci=ids(cold)
 write(HERE/'source-manifest.json',{'files':manifest,'native46':ni,'tools23':ti,'diagnostic43':ci,'files_graph_sha256':graph(manifest),'graph_encoding':'SHA256 UTF8 json.dumps(files,sort_keys=True,separators=(comma,colon))'});write(HERE/'source-owner-map.json',owners)
 rows=F.declarations(source,candidate);counts=dict(collections.Counter(r['group'] for r in rows));assert counts=={'diagnostic':209,'native_lib':175,'native_dev':2},counts
 oldrows=load(OLD/'test-declarations.json')['all'];oldset={(r['file'],r['function']) for r in oldrows};nowset={(r['file'],r['function']) for r in rows};removed=oldset-nowset;added=nowset-oldset
 gd=load(EV/'go-outcome-revision-proposal-20261018/test-declarations.json')
 assert removed=={('diagnostic/src/actual_timed.rs',n) for n in gd['before_actual_timed_tests'][3:]}
 assert {r for r in added if r[0]=='diagnostic/src/actual_timed.rs'}=={('diagnostic/src/actual_timed.rs',n) for n in gd['after_actual_timed_tests'][3:]}
 assert len(added)==18 and len(removed)==4
 write(HERE/'test-declarations.json',{'all':rows,'counts':counts,'native_total':177,'diagnostic_total':209,'added_from_original111':[r for r in rows if (r['file'],r['function']) in added],'removed_renamed_go':[r for r in oldrows if (r['file'],r['function']) in removed],'ordinary_test_only_delta':0,'lexical_source_inventory':True,'rust_parsed':False,'executed':False})
 dispatch=merged[merged.index('fn dispatch('):merged.index('\nfn main(')];registered=set(re.findall(r'"([A-Za-z][A-Za-z0-9]*\.[A-Za-z][A-Za-z0-9]*)"',dispatch));assert len(registered)==117
 discovered={}
 for p in sorted(Path('/home/legolas/king-spec/conformance/fixtures').glob('*.json')):
  raw=p.read_bytes();doc=json.loads(raw);cs=doc.get('cases',[]) if isinstance(doc,dict) else [];selected=[c for c in cs if c.get('request',{}).get('operation') in registered]
  if selected:assert len(selected)==len(cs),('partial file',str(p));discovered[p]=(raw,doc)
 assert len(discovered)==115
 oldinv=load(OLD/'whole-fixture-inventory.json');oldpaths=[Path(r['fixture']) for r in oldinv];assert set(oldpaths)<=set(discovered)
 newpaths=sorted(set(discovered)-set(oldpaths));assert len(newpaths)==7
 fps=oldpaths+newpaths;inventory=[];cases=[];unique=set();ops=collections.Counter()
 for p in fps:
  raw,doc=discovered[p];assert doc['version']==1
  row={'fixture':str(p),'sha256':hb(raw),'bytes':len(raw),'header':{k:v for k,v in doc.items() if k!='cases'},'case_count':len(doc['cases'])}
  if p in oldpaths:assert row==oldinv[oldpaths.index(p)],str(p)
  inventory.append(row)
  for i,c in enumerate(doc['cases']):
   assert c['id'] not in unique,('duplicate',c['id']);unique.add(c['id']);op=c['request']['operation'];ops[op]+=1
   cases.append({'fixture':str(p),'index':i,'id':c['id'],'operation':op,'case_sha256':graph(c),'request_sha256':graph(c['request']),'expected_sha256':graph({k:v for k,v in c.items() if k not in {'id','request'}})})
 assert len(unique)==len(cases)==7673 and set(ops)==registered
 oldcases=load(OLD/'whole-fixture-map.json')['cases'];assert [{k:r[k] for k in ['fixture','index','id','operation']} for r in cases[:len(oldcases)]]==oldcases
 newops={'search.timedRootSequence':8,'search.workTimedRootSequence':26,'session.searches':8,'session.clockSeededSearches':8,'session.interruptedSearches':8,'session.ordinaryIterations':1};assert all(ops[k]==v for k,v in newops.items())
 write(HERE/'whole-fixture-inventory.json',inventory);write(HERE/'whole-fixture-map.json',{'case_count':7673,'whole_files':115,'operation_count':117,'duplicate_ids':0,'partial_files':0,'all_original_headers_preserved':True,'cases':cases});write(HERE/'operation-counts.json',dict(sorted(ops.items())))
 write(HERE/'new-case-selection.json',{'whole_files':[r for r in inventory if Path(r['fixture']) in newpaths],'cases':[r for r in cases if Path(r['fixture']) in newpaths],'case_count':59,'operations':newops})
 proof={'all_reviewed_endpoint_patches_and_complete_inverses_exact':True,'native_3_disjoint_deltas_commute_all_6_orders':True,'ordinary_test_only_correction_explicit':True,'whole_production_ordinary_suffix_exact_original111':True,'ordinary_declaration_delta':0,'native_seed3_exact_persistent_and_Go':True,'main_commutes_and_both_inverses_restore_base':True,'all_unowned_sources_exact_original111':True,'tools23_exact109':True,'registered_routes_equal_full_original_fixture_union':True,'original111_case_prefix_exact':True,'all_original_headers_bytes_verified':True,'failed111_and_both_historical_unapplied_proposals_preserved':True,'no_plane_child':True,'rust_parsed':False,'native_executions':0}
 write(HERE/'source-proof.json',proof)
 archives={}
 archives['source-112.tar.gz']=archive(HERE/'source-112.tar.gz',{n:source/n for n in candidate})
 archives['official-inputs-115.tar.gz']=archive(HERE/'official-inputs-115.tar.gz',{p.name:p for p in fps})
 archives['parent-source-snapshots.tar.gz']=archive(HERE/'parent-source-snapshots.tar.gz',{k+'/'+n:paths[k]/n for k,d in parents.items() for n in d})
 for n in ['source-manifest.json','source-owner-map.json','reviewed-patch-reconstruction.json','source-proof.json','test-declarations.json','whole-fixture-inventory.json','whole-fixture-map.json','operation-counts.json','new-case-selection.json','parents-before.json']:authorities.add(HERE/n)
 authorities.update(HERE.glob('*.patch'));authoritymap={str(p):sha(p) for p in sorted(authorities)}
 assert all(sha(p)==h for p,h in authoritybefore.items());write(HERE/'authority-manifest.json',authoritymap)
 archives['authority-inputs.tar.gz']=archive(HERE/'authority-inputs.tar.gz',{str(p).lstrip('/'):p for p in sorted(authorities)})
 assert files(source,candidate)==candidate and {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}==set(candidate)
 assert all(ids(files(paths[k],names[k]))==before[k] for k in parents)
 assert {n:sha(ROOT/n) if (ROOT/n).is_file() else None for n in rootbefore}==rootbefore
 assert all(sha(p)==h for p,h in authoritymap.items()) and AUTH.read_bytes()==authbytes
 assert all(sha(r['fixture'])==r['sha256'] for r in inventory)
 write(HERE/'stability-after.json',{'candidate_exact':True,'all_9_parents_exact_before_after':True,'root_source_and_AGENTS_exact_before_after':True,'authorities_exact_before_after':True,'original_fixture_bytes_and_headers_exact':True})
 prepared={'status':'FROZEN_COMPLETE117_SOURCE_ONLY_UNPARSED_UNRUN','source':str(source),'source_graph_sha256':graph(manifest),'native_graph_sha256':graph(ni),'tools_graph_sha256':graph(ti),'diagnostic_graph_sha256':graph(ci),'source_files':112,'native_source_files':46,'tools_source_files':23,'diagnostic_source_files':43,'native_tests_declared':177,'native_lib_tests_declared':175,'native_dev_tests_declared':2,'diagnostic_tests_declared':209,'operation_count':117,'cases':7673,'whole_files':115,'duplicate_ids':0,'partial_files':0,'corrected111_test_source':str(paths['corrected111']),'failed111_qualification_transfer':False,'parents_root_originals_stable':True,'archives':archives,'source_manifest_sha256':sha(HERE/'source-manifest.json'),'source_proof_sha256':sha(HERE/'source-proof.json'),'whole_fixture_map_sha256':sha(HERE/'whole-fixture-map.json'),'whole_fixture_inventory_sha256':sha(HERE/'whole-fixture-inventory.json'),'authority_manifest_sha256':sha(HERE/'authority-manifest.json'),'authorization_sha256':sha(AUTH),'execution_authorized':False,'rust_parsed':False,'native_executions':0,'codegen_timing_pgo_profiler_promotion':False,'commit_created':False,'AGENTS_attribution_read':True,'full3288_gate':'external only; local12pre-gate later separately authorized'}
 write(HERE/'prepared.json',prepared)
 (HERE/'review.md').write_text('Exact reviewed117 source-only composition in NEW HOME tree:112source=46native+23tools+43cold. Explicit accepted ordinary.rs test-only real-Q maximum_depth2 correction; production suffix exact original111/generic110. Native6+seed3+test contributions commute all6orders. Additive main commutes, both inverses restore111; every parent patch and full inverse reconstructed. All unowned files exact111, tools109; no projected child.\n\nIndependent full official scan yields115wholefiles/7673unique cases/117registered operations, complete original headers and111case prefix, no partial/duplicates. Added59cases over7wholefiles. Lexical177native=175lib+2dev and209DIAG declarations, not executed tests. Source/input/9parent/authority archives reopened with every member verified and all originals/parents/root stable. Failed111170pass/1fail and both historical unapplied test proposals preserved.\n\nNo Rust parse/format/build/test/engine/codegen/timing/PGO/profiler/promotion or commit. Separate execution clearance required for fresh117native/generic/default backend/strict54/eightwire/full209DIAG7673/independent closure.10917e75 primary codegen control;111efe541 optional failed-unit attribution only. Driver/unit charge/Terminal/IIO/seed/aggregate/frame/copy/PV-lifetime risks remain unqualified. AGENTS attribution and off-Vic3288/local12 policy read.\n')
 archives['freeze-metadata.tar.gz']=archive(HERE/'freeze-metadata.tar.gz',{p.name:p for p in HERE.iterdir() if p.is_file() and p.suffix in {'.json','.md','.patch','.py'}})
 write(HERE/'archive-final-manifest.json',archives)
 state.update(complete=True,source=str(source),source_graph_sha256=graph(manifest),prepared_sha256=sha(HERE/'prepared.json'),counts={'source':112,'native':46,'tools':23,'cold':43,'native_declarations':177,'DIAG_declarations':209,'operations':117,'cases':7673,'whole_files':115},archives=archives,all_owned_background_jobs=0,finished_ns=time.time_ns())
except BaseException as error:
 state.update(failure=f'{type(error).__name__}: {error}',traceback=traceback.format_exc(),finished_ns=time.time_ns())
write(HERE/'freeze-verification.json',state);print(json.dumps(state,sort_keys=True));sys.exit(0 if state['complete'] else 1)
