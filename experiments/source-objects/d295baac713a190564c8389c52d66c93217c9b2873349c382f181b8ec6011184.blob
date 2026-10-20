#!/usr/bin/env python3
"""Authorized111 source/fixture/declaration/archive freeze only; no Rust/native work."""
from pathlib import Path
import collections,hashlib,json,os,re,sys,tarfile,time
from guard import HERE,authorize,load,sha,write

def graph(files):return hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def declarations(root,files):
 rows=[]
 for name in sorted(files):
  if not name.endswith('.rs') or name.startswith('tools/'):continue
  text=(root/name).read_text()
  for m in re.finditer(r'#\[test\]',text):
   found=re.search(r'\bfn\s+(\w+)\s*\(',text[m.end():]);assert found,name
   rows.append({'file':name,'function':found[1],'line':text.count('\n',0,m.start())+1,'group':'diagnostic' if name.startswith('diagnostic/') else 'native_dev' if name=='src/bin/rook2-dev.rs' else 'native_lib'})
 return rows

def apply_reviewed_patch(before,text):
 lines=text.splitlines(True);i=0;result=dict(before);changed=[]
 while i<len(lines):
  if not lines[i].startswith('--- '):i+=1;continue
  old=lines[i][4:].strip();i+=1;assert lines[i].startswith('+++ ')
  new=lines[i][4:].strip();i+=1
  name=new.removeprefix('b/') if new!='/dev/null' else old.removeprefix('a/')
  original=[] if old=='/dev/null' else before[name].decode().splitlines(True)
  produced=[];cursor=0
  while i<len(lines) and not lines[i].startswith('--- '):
   if not lines[i].startswith('@@ '):i+=1;continue
   m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i]);assert m
   begin=int(m[1])-1 if int(m[1]) else 0;old_count=int(m[2] or 1);new_count=int(m[4] or 1)
   assert begin>=cursor;produced.extend(original[cursor:begin]);cursor=begin;i+=1;a=b=0
   while a<old_count or b<new_count:
    line=lines[i];i+=1;kind=line[:1];body=line[1:]
    if kind=='\\':continue
    assert kind in [' ','-','+'],line
    if kind in [' ','-']:assert cursor<len(original) and original[cursor]==body,(name,cursor,line);cursor+=1;a+=1
    if kind in [' ','+']:produced.append(body);b+=1
   assert (a,b)==(old_count,new_count)
  produced.extend(original[cursor:])
  if new=='/dev/null':result.pop(name)
  else:result[name]=''.join(produced).encode()
  changed.append(name)
 return result,changed

def archive(path,files):
 # Explicit source/original documents only, never targets or runtime databases.
 with tarfile.open(path,'w:gz') as t:
  for arc,source in sorted(files.items()):t.add(source,arcname=arc,recursive=False)
 with tarfile.open(path,'r:gz') as t:
  members=[m for m in t if m.isfile()];assert len(members)==len(files) and len({m.name for m in members})==len(files)
  actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in members}
 expected={arc:sha(source) for arc,source in files.items()};assert actual==expected
 return {'sha256':sha(path),'bytes':path.stat().st_size,'entries':len(files),'every_member_verified':True}

def main():
 authorize('freeze');inputs=load(HERE/'composition-inputs.json');source=Path(inputs['destination']);C=HERE/'composition';manifest=load(C/'source-manifest.json')
 state={'complete':False,'scope':'SOURCE_FIXTURE_DECLARATION_ARCHIVE_FREEZE_ONLY','rust_parsed':False,'native_executions':0,'failure':None,'affinity':sorted(os.sched_getaffinity(0)),'TMPDIR':os.environ['TMPDIR']}
 try:
  assert len(manifest)==109 and {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}==set(manifest)
  assert all(sha(source/n)==h for n,h in manifest.items())
  parent_data={tag:{n:(Path(info['path'])/n).read_bytes() for n in info['source_sha256']} for tag,info in inputs['parents'].items()}
  for tag,info in inputs['parents'].items():assert all(hashlib.sha256(parent_data[tag][n]).hexdigest()==h for n,h in info['source_sha256'].items())
  G=Path('/home/legolas/rook2/evidence/generic-timed110-proposal-20261018');J=Path('/home/legolas/rook2/evidence/joined-search110-proposal-20261018');B=Path('/home/legolas/rook2/evidence/post-lifecycle109-proposal-20261018')
  reconstructed_g,gfiles=apply_reviewed_patch(parent_data['base109'],(G/'proposal.patch').read_text())
  reconstructed_j,jfiles=apply_reviewed_patch(parent_data['base109'],(J/'trial.patch').read_text())
  assert reconstructed_g==parent_data['generic110'] and reconstructed_j==parent_data['joined110']
  write(HERE/'reviewed-patch-reconstruction.json',{'generic_complete_parent_reconstructed':True,'joined_updated_complete_parent_reconstructed':True,'generic_patch':{'path':str(G/'proposal.patch'),'sha256':sha(G/'proposal.patch'),'files':gfiles},'joined_updated_patch':{'path':str(J/'trial.patch'),'sha256':sha(J/'trial.patch'),'files':jfiles},'original_joined_reviewed_patch_preserved_sha256':sha(J/'trial-before-independent-strengthening.patch'),'rust_parsed':False})
  # Independent lexical declaration inventory, reconciled to accepted109 list.
  rows=declarations(source,manifest);counts=dict(collections.Counter(r['group'] for r in rows));assert counts=={'diagnostic':199,'native_dev':2,'native_lib':171},counts
  old=load(B/'test-declarations.json')['all'];oldset={(r['file'],r['function']) for r in old};nowset={(r['file'],r['function']) for r in rows}
  assert len(rows)==len(nowset) and oldset<=nowset
  generic_new=load(G/'test-declarations.json')['new_actual_declarations'];gset={(r['file'],r['function']) for r in generic_new};newset=nowset-oldset
  assert gset<=newset and len(newset)==11 and len(newset-gset)==3 and all(n=='diagnostic/src/joined_search.rs' for n,_ in newset-gset)
  write(HERE/'test-declarations.json',{'all':rows,'new':[r for r in rows if (r['file'],r['function']) in newset],'counts':counts,'native_total':173,'diagnostic_total':199,'lexical_source_inventory':True,'reconciled_all_inherited109_declarations':True,'rust_parsed':False,'executed':False})
  # Every original109 whole file plus two whole released documents.
  old_inventory=load(B/'whole-fixture-inventory.json');paths=[Path(r['fixture']) for r in old_inventory]+[Path('/home/legolas/king-spec/conformance/fixtures/generic-timed-search-v1.json'),Path('/home/legolas/king-spec/conformance/fixtures/ordinary-joined-search-v1.json')]
  assert len(paths)==len(set(paths))==108
  fixture_rows=[];cases=[];ids=set();ops=collections.Counter()
  for index,path in enumerate(paths):
   raw=path.read_bytes();doc=json.loads(raw);header={k:v for k,v in doc.items() if k!='cases'};identity=hashlib.sha256(raw).hexdigest();assert doc['version']==1 and isinstance(doc['cases'],list)
   row={'fixture':str(path),'sha256':identity,'bytes':len(raw),'header':header,'case_count':len(doc['cases'])}
   if index<len(old_inventory):assert row==old_inventory[index],str(path)
   fixture_rows.append(row)
   for ci,c in enumerate(doc['cases']):
    assert c['id'] not in ids,c['id'];ids.add(c['id']);op=c['request']['operation'];ops[op]+=1
    cases.append({'fixture':str(path),'index':ci,'id':c['id'],'operation':op})
  assert (len(ids),len(cases),len(ops))==(7614,7614,111),(len(ids),len(cases),len(ops))
  assert ops['search.genericTimedSearch']==ops['search.ordinaryJoinedSearch']==4
  # Independently ensure registered semantic routes equal the whole-file union.
  maintext=(source/'diagnostic/src/main.rs').read_text();dispatch=maintext[maintext.index('fn dispatch('):maintext.index('\nfn main(')]
  registered=set(re.findall(r'"([A-Za-z][A-Za-z0-9]*\.[A-Za-z][A-Za-z0-9]*)"',dispatch));assert registered==set(ops),(registered-set(ops),set(ops)-registered)
  write(HERE/'whole-fixture-inventory.json',fixture_rows);write(HERE/'operation-counts.json',dict(sorted(ops.items())))
  write(HERE/'whole-fixture-map.json',{'case_count':len(cases),'whole_files':len(paths),'operation_count':len(ops),'duplicate_ids':0,'partial_files':0,'cases':cases})
  native=load(C/'native-source-manifest.json');tools=load(C/'tools-source-manifest.json');cold=load(C/'cold-source-manifest.json')
  write(HERE/'source-manifest.json',{'files':manifest,'native45':native,'tools23':tools,'diagnostic41':cold,'files_graph_sha256':graph(manifest),'graph_encoding':'SHA256 UTF8 json.dumps(files,sort_keys=True,separators=(comma,colon))'})
  # Whole source map and exact archive, plus reviewed original input documents.
  archives={}
  archives['source-109.tar.gz']=archive(HERE/'source-109.tar.gz',{n:source/n for n in manifest})
  archives['official-inputs-108.tar.gz']=archive(HERE/'official-inputs-108.tar.gz',{p.name:p for p in paths})
  authorities=dict(inputs['authority_dependencies']);authorities.update({str(HERE/n):sha(HERE/n) for n in ['compose.py','guard.py','freeze.py','freeze-clearance.json','composition-inputs.json','authority-source-before.json']})
  authorities.update({str(B/n):sha(B/n) for n in ['test-declarations.json','whole-fixture-inventory.json','whole-fixture-map.json','prepared.json']})
  write(HERE/'authority-manifest.json',authorities)
  archives['authority-inputs.tar.gz']=archive(HERE/'authority-inputs.tar.gz',{name.lstrip('/'):Path(name) for name in authorities})
  # All sources, original bytes, reviews and closed-window receipts must stay stable.
  assert all(sha(source/n)==h for n,h in manifest.items())
  for tag,info in inputs['parents'].items():assert all(sha(Path(info['path'])/n)==h for n,h in info['source_sha256'].items())
  assert all(sha(Path(n))==h for n,h in authorities.items())
  assert all(sha(Path(r['fixture']))==r['sha256'] for r in fixture_rows)
  proof=load(C/'composition-proof.json');proof.update({'reviewed_parent_patches_reconstruct_exact_inputs':True,'source_and_all_parents_stable_before_after':True,'original_headers_bytes_stable':True,'registered_routes_equal_whole_fixture_operations':True,'plane_child_excluded':'Position/evaluator/attacks/movegen remain exact generic110/base109; native delta only reviewed ordinary/timed/Stopped','native_and_tools_exact_generic':all(manifest[n]==inputs['parents']['generic110']['source_sha256'][n] for n in native|tools)})
  write(HERE/'source-proof.json',proof)
  (HERE/'review.md').write_text('Exact reviewed generic110 plus strengthened joined110 composed in a NEW HOME tree. Additive main inverse recovers both complete endpoint main files and exact109; all other109-file sources select their reviewed owner exactly. Reviewed generic proposal.patch and updated joined trial.patch independently reconstruct the complete respective parent snapshots from109. Native45 and tools23 are exact generic110; tools also exact109. No plane-child transport is included.\n\nIndependently inventoried declarations173native=171lib+2dev and199DIAG, not test results. Whole original108 files yield7614 unique mandatory cases/111operations, exactly equal registered routes, with four complete cases for each new endpoint. Every109 inherited declaration/file/header/hash is reconciled; no partial files/duplicate IDs. Broad generic and joined domains remain separate. Source109=45native+23tools+41cold. Archives were reopened and every member hash checked; original parent/source/review/fixture hashes stable before/after.\n\nThis is a SOURCE FREEZE only: no Rust parse/format/compiler/build/test/engine/codegen/CPU/PGO/profiler/promotion. Functional and backend execution require separate parent clearance; all tests remain unrun. The new Stopped/Result ABI, true/false ordinary specialization, wrapper/inlining/frame/copy costs remain explicit future codegen gates against accepted10917e75. Root/frozen parents are untouched and all inherited failure history is preserved.\n')
  prepared={'status':'FROZEN_SOURCE_ONLY_UNPARSED_UNRUN','source':str(source),'base':inputs['parents']['base109']['path'],'generic_parent':inputs['parents']['generic110']['path'],'joined_parent':inputs['parents']['joined110']['path'],'source_files':109,'native_source_files':45,'tools_source_files':23,'diagnostic_source_files':41,'source_graph_sha256':graph(manifest),'native_graph_sha256':graph(native),'tools_graph_sha256':graph(tools),'diagnostic_graph_sha256':graph(cold),'native_tests_declared':173,'native_lib_tests_declared':171,'native_dev_tests_declared':2,'diagnostic_tests_declared':199,'operation_count':111,'cases':7614,'whole_files':108,'duplicate_ids':0,'partial_files':0,'all_original_headers_verified':True,'all_original_ids_unique':True,'native_exact_generic110':True,'tools_exact109':True,'all_source_parent_authority_fixture_inputs_stable':True,'archives':archives,'patches':{q.name:sha(q) for q in sorted(C.glob('against-*.patch'))},'authority_manifest_sha256':sha(HERE/'authority-manifest.json'),'source_proof_sha256':sha(HERE/'source-proof.json'),'source_manifest_sha256':sha(HERE/'source-manifest.json'),'rust_parsed':False,'native_executions':0,'execution_authorized':False,'plane_child_included':False,'cpu_pgo_profiler':False,'actual_outer_terminal_required':True}
  write(HERE/'prepared.json',prepared);state.update(complete=True,source=str(source),source_graph_sha256=graph(manifest),counts={'source':109,'native':173,'diagnostic':199,'operations':111,'cases':7614,'whole_files':108},archives=archives,prepared_sha256=sha(HERE/'prepared.json'))
 except BaseException as error:state['failure']=f'{type(error).__name__}: {error}'
 write(HERE/'freeze-verification.json',state);print(json.dumps(state));return 0 if state['complete'] else 1
if __name__=='__main__':sys.exit(main())
