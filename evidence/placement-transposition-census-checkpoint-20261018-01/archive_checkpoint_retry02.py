"""Streaming deterministic preservation only; never execute native/parser/model/build/Git."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,traceback,sys,shutil
HERE=Path(__file__).resolve().parent
REPO=Path('/home/legolas/rook2');E=REPO/'evidence'
SCOPE=json.loads((HERE/'included-scope.json').read_text())
ROOTS=[Path(p) for p in SCOPE['directories']];EXTRAS=[Path(p) for p in SCOPE['explicit_extra_files']]
ARCHIVE=HERE/SCOPE['archive_name']
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(path):return json.loads(Path(path).read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,separators=(',',':'));f.write('\n')
def name_for(path):
 name=path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else 'external/'+path.relative_to('/').as_posix()
 assert not Path(name).is_absolute() and '..' not in Path(name).parts
 return name

def paths():
 files=[];directories=[];unsupported=[]
 for root in ROOTS:
  assert root.is_dir() and not root.is_symlink()
  for current,dirs,names in os.walk(root,followlinks=False,onerror=lambda e:(_ for _ in ()).throw(e)):
   directories.append(str(Path(current)))
   for name in dirs:
    p=Path(current)/name
    if not stat.S_ISDIR(p.lstat().st_mode):unsupported.append(str(p))
   for name in names:
    p=Path(current)/name
    if stat.S_ISREG(p.lstat().st_mode):files.append(p)
    else:unsupported.append(str(p))
 assert not unsupported,{'unsupported_entries':unsupported,'no_silent_exclusions':True}
 assert len(files)==len(set(files))
 for p in EXTRAS:
  assert p not in files
  assert stat.S_ISREG(p.stat().st_mode)
  if p.is_symlink():
   alias=next(x for x in SCOPE['explicit_runtime_aliases'] if x['source_path']==str(p))
   assert alias['link_text']==os.readlink(p) and alias['resolved_path']==str(p.resolve(strict=True))
  else:assert stat.S_ISREG(p.lstat().st_mode)
  files.append(p)
 return sorted(files,key=name_for),sorted(directories)

def metadata(path):
 l=path.lstat();s=path.stat()
 return {'source_path':str(path),'archive_member':name_for(path),'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode),'original_mtime_ns':s.st_mtime_ns,'source_lstat_mtime_ns':l.st_mtime_ns,'source_lstat_mode':l.st_mode,'resolved_source_path':str(path.resolve(strict=True)),'explicit_alias_link':os.readlink(path) if stat.S_ISLNK(l.st_mode) else None}

def inventory():
 files,dirs=paths();rows=[]
 for p in files:
  before=metadata(p);digest=sha(p);assert metadata(p)==before,str(p)
  rows.append(dict(before,sha256=digest))
 assert len({r['archive_member'] for r in rows})==len(rows)
 return rows,dirs

class HashReader:
 def __init__(self,file):self.file=file;self.hash=hashlib.sha256();self.bytes=0
 def read(self,size=-1):
  assert 0<=size<=1024*1024,'archive reader must use bounded chunks'
  chunk=self.file.read(size);self.hash.update(chunk);self.bytes+=len(chunk);return chunk

def coverage(rows):
 by={r['source_path']:r for r in rows};P=E/'placement-transposition-census-proposal-20261018-01';B=E/'placement-transposition-census-build-20261018-01';C=E/'placement-transposition-census-collection-20261018-01';M=E/'placement-transposition-census-model-20261018-01'
 for p,h in SCOPE['expected_extra_sha256'].items():assert by[p]['sha256']==h,p
 plan=load(P/'plan.json');proof=load(P/'source-proof.json');prep=load(P/'prepared.json');build=load(B/'receipt.json')
 assert len(plan['source71'])==71 and len(plan['native48'])==48 and len(plan['tools23'])==23
 assert proof['full_forward_and_inverse_patch_endpoints_reconstruct_exactly'] and proof['all_evaluator_arithmetic_pawn_selection_queries_retained_observers_finish_order_after_inverse_identical']
 for n,h in plan['source71'].items():assert by[str(Path(plan['source'])/n)]['sha256']==by[str(B/'source-before'/n)]['sha256']==h
 for p,h in plan['input_sha256'].items():assert by[p]['sha256']==h,p
 for n,h in load(P/'helper-pins.json').items():assert by[str(P/n)]['sha256']==h
 image=by[str(B/'rook2-exact')]['sha256'];assert image==build['binary_output']['sha256']=='9cebd7c08085aea983d4708239100cf895a5bbb1e2a336078ab6d31d273d022d'
 assert by[build['binary_output']['path']]['sha256']==image
 assert prep['probe_graph_sha256']=='ec30bc683df1aa0eb476bb7a3afec0d225fed158071f5cbb17a8ad93f3fc2a8d'
 assert by[str(B/'verified-source-before.tar.gz')]['sha256']==load(B/'archive-receipt.json')['sha256']
 controls=load(P/'offline-controls-01/result.json');assert controls['complete'] and len(controls['cases'])==27
 collection=load(C/'result.json');model=load(M/'summary.json');opportunity=load(M/'opportunity-summary.json')
 assert collection['complete'] and collection['native_runs']==54 and collection['total_private_bytes']==4599807459
 assert model['complete'] and model['original_oracle_calls_offline']==54 and model['new_native_runs']==0
 assert opportunity['complete'] and opportunity['native_total_encounters']==37094875 and opportunity['native_total_activity_R']==115801445
 assert opportunity['payload_mismatches']==opportunity['fingerprint_mismatches']==0
 assert [x['case'] for x in collection['cases']]==[x['case'] for x in model['cases']]==plan['case_order']
 assert len({x['native_pid'] for x in collection['cases']})==54
 total=0
 for row in collection['cases']:
  d=C/row['case'];raw=by[str(d/'encounters.bin')];report=by[str(d/'native-counts.jsonl')]
  assert raw['sha256']==row['raw_sha256'] and report['sha256']==row['report_sha256']
  assert raw['bytes']+report['bytes']==row['private_bytes']<=row['allowance'];total+=row['private_bytes']
  assert by[str(d/'comparator.stdout')]['sha256']==row['comparator_sha256']
  native=load(d/'comparator.stdout')['results'][0];child=load(d/'comparator.child-terminal.json')
  assert native['pid']==row['native_pid'] and native['exit']=={'code':0,'signal':None} and native['status']=='pass' and native['complete'] and not native['truncated'] and native['error'] is None
  assert child['actual_child_return_observed'] and child['exit_code']==0
  parsed=load(M/(row['case']+'.json'));assert parsed['complete'] and parsed['raw_sha256']==raw['sha256'] and parsed['report_sha256']==report['sha256']
  recorded=next(x for x in model['cases'] if x['case']==row['case']);assert by[str(M/(row['case']+'.json'))]['sha256']==recorded['parsed_sha256']
 assert total==4599807459
 actual={}
 for key,directory,session,chunk in [('build',B,93035,'fe2695'),('collection',C,30591,'ccb943'),('model',M,40052,'bbaea8')]:
  t=load(directory/'tool-terminal.json');assert t['actual_tool_terminal_observed'] and t['exit_code']==0 and t['session_id']==session and t['terminal_chunk_id']==chunk;actual[key]=t
 recheck=load(M/'original-oracle54.child-terminal.json');assert recheck['actual_child_return_observed'] and recheck['exit_code']==0
 assert load(M/'original-oracle54.stdout')['original_oracle_calls']==54 and by[str(M/'original-oracle54.stderr')]['bytes']==0
 history=E/'placement-transposition-census-design-20261018-score-context/review.md'
 assert str(history) in by and 'predeclared stable board-only digest' in history.read_text()
 assert 'earlier unexecuted BLAKE2 design' in (P/'review.md').read_text()
 assert plan['index']=='(primary ^ secondary.rotate_left(16)) & (capacity-1)'
 assert 'no BLAKE2 policy executed' in plan['index_predeclaration']
 return {'source71_and_inverse_patches_reproducible':True,'source_graph':prep['probe_graph_sha256'],'image_sha256':image,'compiler_and_runtime_paths_explicit':True,'strict54_all_original_raw_and_normal_exits':True,'private_raw_report_bytes':total,'original_offline54_child_return':recheck,'raw54_hashes_equal_collection_and_model':True,'native_encounters':opportunity['native_total_encounters'],'native_activity_R':opportunity['native_total_activity_R'],'epochs':opportunity['epoch_kinds'],'empty_epochs':opportunity['empty_epoch_kinds'],'capacities':opportunity['capacities'],'pure_payload_mismatches':0,'fingerprint_mismatches':0,'actual_stage_terminals':actual,'synthetic_controls':27,'historical_unexecuted_BLAKE2_design_preserved_and_actual_cheap_index_correction_included':True,'new_native_or_parser_model_runs':0,'scope':'Preservation only; no CPU benefit, production cache, architecture/advisor conclusion or qualification'}

def preflight():
 assert sorted(os.sched_getaffinity(0))==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert not ARCHIVE.exists()
 rows,dirs=inventory();proof=coverage(rows);total=sum(r['bytes'] for r in rows)
 assert shutil.disk_usage(HERE).free>2*total+1024**3
 manifest={'file_count':len(rows),'source_bytes':total,'scope':SCOPE,'directories_enumerated_not_tar_members':dirs,'regular_file_members_only':True,'runtime_aliases_explicitly_materialized':SCOPE['explicit_runtime_aliases'],'no_exclusions':True,'members':rows}
 write('member-manifest02.json',manifest);write('native-proof02.json',proof)
 write('preflight02.json',{'complete':True,'files':len(rows),'bytes':total,'manifest_sha256':sha(HERE/'member-manifest02.json'),'scope_sha256':sha(HERE/'included-scope.json'),'archive_authorized_by_parent_after_this_preflight':True,'all_input_content_pins_and_coverage_equal':True,'all_whole_trees_and_explicit_extras_included':True,'no_archive_created':True})
 print(json.dumps({'preflight_pass':True,'files':len(rows),'bytes':total,'manifest_sha256':sha(HERE/'member-manifest02.json')}),flush=True)

def archive():
 result={'complete':False,'failure':None,'affinity':sorted(os.sched_getaffinity(0)),'no_native_build_parser_model_profile_timing_git_subprocess':True}
 try:
  assert result['affinity']==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
  pre=load(HERE/'preflight02.json');assert pre['complete'] and pre['manifest_sha256']==sha(HERE/'member-manifest02.json') and pre['scope_sha256']==sha(HERE/'included-scope.json')
  manifest=load(HERE/'member-manifest02.json');rows=manifest['members'];total=manifest['source_bytes'];dirs=manifest['directories_enumerated_not_tar_members']
  files,now_dirs=paths();assert [str(p) for p in files]==[r['source_path'] for r in rows] and now_dirs==dirs
  for r in rows:assert metadata(Path(r['source_path']))=={k:v for k,v in r.items() if k!='sha256'},r['source_path']
  assert not ARCHIVE.exists();progress=0
  with ARCHIVE.open('xb') as compressed:
   with gzip.GzipFile(filename='',mode='wb',compresslevel=6,fileobj=compressed,mtime=0) as gz:
    with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as output:
     for i,row in enumerate(rows):
      p=Path(row['source_path']);before=metadata(p)
      assert before=={k:v for k,v in row.items() if k!='sha256'}
      info=tarfile.TarInfo(row['archive_member']);info.type=tarfile.REGTYPE;info.size=row['bytes'];info.mode=row['mode'];info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
      with p.open('rb') as f:
       reader=HashReader(f);output.addfile(info,reader)
       assert reader.bytes==row['bytes'] and reader.hash.hexdigest()==row['sha256'],row['source_path']
      assert metadata(p)==before
      progress+=row['bytes']
      if row['bytes']>=64*1024**2:print(json.dumps({'stage':'archive-write','members':i+1,'source_bytes_consumed':progress,'compressed_bytes_so_far':compressed.tell()}),flush=True)
  with ARCHIVE.open('rb') as f:
   header=f.read(10);assert header[:4]==b'\x1f\x8b\x08\x00' and header[4:8]==bytes(4) and header[8]==0 and header[9]==255
  expected={r['archive_member']:r for r in rows};seen=set();unpacked=0
  with ARCHIVE.open('rb') as compressed:
   with gzip.GzipFile(fileobj=compressed,mode='rb') as gz:
    with tarfile.open(fileobj=gz,mode='r|') as check:
     for m in check:
      assert m.isfile() and m.name in expected and m.name not in seen
      row=expected[m.name];assert m.size==row['bytes'] and m.mode==row['mode'] and m.type==tarfile.REGTYPE
      assert m.mtime==m.uid==m.gid==0 and m.uname==m.gname=='' and set(m.pax_headers)<={'path'}
      assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
      h=hashlib.sha256();count=0
      with check.extractfile(m) as f:
       for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk);count+=len(chunk)
      assert count==row['bytes'] and h.hexdigest()==row['sha256'];seen.add(m.name);unpacked+=count
    while gz.read(1024*1024):pass # consume gzip CRC/footer, not just tar end blocks
  assert seen==set(expected) and unpacked==total
  print(json.dumps({'stage':'archive-reopened','members':len(seen),'bytes':unpacked}),flush=True)
  after,after_dirs=inventory();assert after==rows and after_dirs==dirs
  proof=coverage(after);assert proof==load(HERE/'native-proof02.json')
  result.update(complete=True,archive=ARCHIVE.name,archive_sha256=sha(ARCHIVE),archive_bytes=ARCHIVE.stat().st_size,manifest='member-manifest02.json',manifest_sha256=sha(HERE/'member-manifest02.json'),manifest_bytes=(HERE/'member-manifest02.json').stat().st_size,member_count=len(rows),source_bytes=total,reopened_full_member_header_type_mode_hash_equality=True,gzip_header_and_crc_verified=True,original_inventory_timestamps_modes_aliases_bytes_unchanged=True,no_exclusions=True,bulk_artifact_local_only=True,native_proof_sha256=sha(HERE/'native-proof02.json'),scope_sha256=sha(HERE/'included-scope.json'),runtime_aliases_explicitly_materialized=SCOPE['explicit_runtime_aliases'])
 except BaseException as e:result['failure']=f'{type(e).__name__}: {e}';result['traceback']=traceback.format_exc()
 finally:write('verification02.json',result)
 print(json.dumps(result),flush=True)
 return 0 if result['complete'] else 1

if __name__=='__main__':
 if sys.argv[1:]==['--preflight']:
  try:preflight()
  except BaseException as e:
   write('preflight02-failure.json',{'error':repr(e),'traceback':traceback.format_exc()});raise
 elif sys.argv[1:]==['--archive']:raise SystemExit(archive())
 else:raise SystemExit('choose --preflight or --archive')
