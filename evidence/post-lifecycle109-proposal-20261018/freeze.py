#!/usr/bin/env python3
"""Source/inventory freeze only: never parses or runs Rust/native code."""
import collections,copy,difflib,gzip,hashlib,io,json,re,tarfile
from pathlib import Path
E=Path(__file__).resolve().parent
BASE=Path('/home/legolas/rook2-work/imp2-controlled-root108-combined-20261018-f5fjipe9')
SRC=Path('/home/legolas/rook2-work/imp2-post-lifecycle109-proposal-20261018-1d53e7es')
B=Path('/home/legolas/rook2/evidence/controlled-root108-combined-proposal-20261018')
SPEC=Path('/home/legolas/king-spec/spec/post-lifecycle.md')
POST=Path('/home/legolas/king-spec/conformance/fixtures/post-lifecycle-v1.json')
def sha(data):return hashlib.sha256(data).hexdigest()
def filehash(p):return sha(p.read_bytes())
def graph(m):return sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode())
def emit(name,data):
 (E/name).write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
base_manifest=json.loads((B/'source-manifest.json').read_text())
basefiles=base_manifest['files']
assert {r:filehash(BASE/r) for r in basefiles}==basefiles,'frozen108 source mismatch'
assert graph(basefiles)==base_manifest['files_graph_sha256']
files=sorted([str(p.relative_to(SRC)) for p in SRC.rglob('*') if p.is_file()])
assert set(files)==set(basefiles)|{'src/post_lifecycle.rs','diagnostic/src/post_captures.rs'}
m={r:filehash(SRC/r) for r in files}
changed=sorted(r for r in files if m[r]!=basefiles.get(r))
expected=['diagnostic/src/main.rs','diagnostic/src/post_captures.rs','src/lib.rs','src/output.rs','src/post_lifecycle.rs','src/session.rs','src/timed.rs']
assert changed==expected,changed
native={r:v for r,v in m.items() if not r.startswith(('tools/','diagnostic/'))}
tools={r:v for r,v in m.items() if r.startswith('tools/')}
cold={r:v for r,v in m.items() if r.startswith('diagnostic/')}
assert (len(native),len(tools),len(cold))==(45,23,39)
emit('source-manifest.json',{'files':m,'native45':native,'tools23':tools,'diagnostic39':cold,'files_graph_sha256':graph(m)})
patches={}
for name,predicate in [('trial.patch',lambda r:True),('native.patch',lambda r:r.startswith('src/')),('cold.patch',lambda r:r.startswith('diagnostic/'))]:
 text=''
 for r in changed:
  if not predicate(r):continue
  old=(BASE/r).read_text().splitlines(keepends=True) if r in basefiles else []
  new=(SRC/r).read_text().splitlines(keepends=True)
  text+=''.join(difflib.unified_diff(old,new,fromfile='a/'+r if r in basefiles else '/dev/null',tofile='b/'+r))
 (E/name).write_text(text);patches[name]=filehash(E/name)
# Endpoint reconstruction verifies every source identity in each direction.
forward=dict(basefiles);forward.update({r:m[r] for r in changed})
inverse=dict(m)
for r in changed:
 if r in basefiles:inverse[r]=basefiles[r]
 else:del inverse[r]
assert forward==m and inverse==basefiles
# Exact preservation of the sensitive capture observation prefix and host body.
def section(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
bt=(BASE/'src/timed.rs').read_text();st=(SRC/'src/timed.rs').read_text()
assert section(bt,'                    if completion.best_changed {','                        if depth >= 3 {')==section(st,'                    if completion.best_changed {','                        captures.capture(')
assert section(bt,'    fn publish_capture(', '    pub fn run_work_timed')==section(st,'    fn publish_capture(', '    pub fn run_work_timed')
def declarations(root):
 inventory=[]
 for r in sorted(p for p in root.rglob('*.rs') if p.is_file()):
  rel=str(r.relative_to(root))
  for match in re.finditer(r'#\[test\]\s*fn\s+(\w+)',r.read_text()):
   inventory.append({'file':rel,'function':match.group(1),'line':r.read_text()[:match.start()].count('\n')+1})
 return inventory
base_decl=declarations(BASE);decl=declarations(SRC)
def counts(rows):
 return {'native_lib':sum(r['file'].startswith('src/') and not r['file'].startswith('src/bin/') for r in rows),'native_dev':sum(r['file']=='src/bin/rook2-dev.rs' for r in rows),'diagnostic':sum(r['file'].startswith('diagnostic/') for r in rows)}
assert counts(base_decl)=={'native_lib':161,'native_dev':2,'diagnostic':188}
assert counts(decl)=={'native_lib':167,'native_dev':2,'diagnostic':192}
base_names={(r['file'],r['function']) for r in base_decl}
new_decl=[r for r in decl if (r['file'],r['function']) not in base_names]
assert len(new_decl)==10
emit('test-declarations.json',{'counts':counts(decl),'native_total':169,'new':new_decl,'all':decl,'executed':False,'rust_parsed':False})
emit('source-proof.json',{'base':str(BASE),'source':str(SRC),'base_graph_sha256':graph(basefiles),'source_graph_sha256':graph(m),'changed_files':changed,'forward_and_inverse_file_map_equal':True,'all_other_source_bytes_unchanged':True,'capture_observation_prefix_exact':True,'publish_capture_body_exact':True,'tools23_exact':True,'new_fields_in_existing_hot_or_outcome_types':False,'base_source_after_matches_frozen_manifest':True,'patches':patches})
# Rebuild every complete original fixture inventory/header/case map independently.
old_inventory=json.loads((B/'whole-fixture-inventory.json').read_text())
paths=[Path(x['fixture']) for x in old_inventory]+[POST]
assert len(paths)==len(set(paths))==106
inventory=[];cases=[];operations=collections.Counter();ids=[]
for p in paths:
 raw=p.read_bytes();data=json.loads(raw);rows=data['cases'];header={k:v for k,v in data.items() if k!='cases'}
 record={'fixture':str(p),'bytes':len(raw),'sha256':sha(raw),'case_count':len(rows),'header':header}
 inventory.append(record)
 for index,row in enumerate(rows):
  operation=row['request']['operation'];operations[operation]+=1;ids.append(row['id'])
  cases.append({'fixture':str(p),'id':row['id'],'index':index,'operation':operation})
assert inventory[:-1]==old_inventory,'old full headers/fixtures changed'
assert cases[:-22]==json.loads((B/'whole-fixture-map.json').read_text())['cases']
assert len(ids)==len(set(ids))==7606
assert len(operations)==109 and operations['output.postLifecycle']==22
emit('whole-fixture-inventory.json',inventory)
emit('whole-fixture-map.json',{'cases':cases,'case_count':len(cases),'duplicate_ids':0,'operation_count':len(operations),'partial_files':0,'whole_files':len(paths)})
emit('operation-counts.json',dict(sorted(operations.items())))
# Independently review the released22 supplied-event expected reports, not Rust.
original=json.loads(POST.read_text());reconciled=[]
for case in original['cases']:
 sequences=[]
 for query in case['request']['input']['queries']:
  after=[];published=False;latest=None
  for event in query['events']:
   score=event['rankingScore']
   if -9000<score<9000:score=max(-7900,min(7900,score-query['drawPreference']))
   elapsed=(event['clock']-query['startClock'])%2**32
   if elapsed>=2**31:elapsed-=2**32
   latest={'depthToken':1000*event['depth']+event['depthRemainder'],'reportedScore':score,'elapsed':elapsed,'searchId':event['searchId'],'principalVariation':copy.deepcopy(event['principalVariation'])}
   immediate=event['depth']>=3
   after.append([copy.deepcopy(latest)] if immediate else [])
   published=published or immediate
  sequences.append({'afterEach':after,'onFinish':[] if published else [latest],'clockReads':len(query['events'])})
 model={'sequences':sequences}
 assert model==case['expected'],case['id']
 reconciled.append({'id':case['id'],'matches_released_expected':True})
emit('post-fixture-contract-reconciliation.json',{'scope':'Python source-only contract arithmetic/lifecycle cross-check of released expected22; no Rust/native execution and no fixture-backed runtime adapter','fixture':str(POST),'fixture_sha256':filehash(POST),'spec_sha256':filehash(SPEC),'case_count':22,'all_match':True,'cases':reconciled})
# Deterministic byte archives, each member re-read and checked independently.
def archive(name,entries):
 path=E/name
 with path.open('wb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
   with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as tf:
    for label,p in entries:
     data=p.read_bytes();info=tarfile.TarInfo(label);info.size=len(data);info.mode=0o644;info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';tf.addfile(info,io.BytesIO(data))
 expected={label:filehash(p) for label,p in entries}
 with tarfile.open(path,'r:gz') as tf:
  actual={member.name:sha(tf.extractfile(member).read()) for member in tf.getmembers()}
 assert actual==expected
 return {'sha256':filehash(path),'bytes':path.stat().st_size,'entries':len(entries),'every_member_verified':True}
archives={'source-107.tar.gz':archive('source-107.tar.gz',[(r,SRC/r) for r in files]),'official-inputs-106.tar.gz':archive('official-inputs-106.tar.gz',[(p.name,p) for p in paths])}
emit('archives.json',archives)
assert {r:filehash(BASE/r) for r in basefiles}==basefiles
assert {r:filehash(SRC/r) for r in files}==m
emit('parent-input-anchors.json',{str(p):filehash(p) for p in [B/'prepared.json',B/'source-manifest.json',B/'whole-fixture-inventory.json',SPEC,POST]})
emit('freeze-result.json',{'status':'FROZEN_SOURCE_ONLY_UNPARSED_UNRUN','source':str(SRC),'base':str(BASE),'source_graph_sha256':graph(m),'source_files':107,'native_source_files':45,'tools_source_files':23,'diagnostic_source_files':39,'native_tests_declared':169,'diagnostic_tests_declared':192,'operation_count':109,'cases':7606,'whole_files':106,'archives':archives,'patches':patches,'native_executions':0,'rust_parsed':False,'all_original_headers_verified':True,'all_original_ids_unique':True,'base_and_current_after_equal':True})
print(json.dumps(json.loads((E/'freeze-result.json').read_text()),sort_keys=True))
