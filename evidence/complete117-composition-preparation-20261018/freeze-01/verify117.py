#!/usr/bin/env python3
# Independent read-only source/archive/original JSON reconciliation, no native work.
from pathlib import Path
import collections,hashlib,json,os,re,sys,tarfile,time,traceback
E=Path(__file__).parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
state={'complete':False,'pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0)),'source_native_jobs':0,'error':None,'started_ns':time.time_ns()}
try:
 assert state['affinity']==[0,1,2,3,4,5,8,9,10,11,12,13]
 p=read(E/'prepared.json');source=Path(p['source']);m=read(E/'source-manifest.json')
 assert p['status']=='FROZEN_COMPLETE117_SOURCE_ONLY_UNPARSED_UNRUN' and not p['execution_authorized']
 assert {str(x.relative_to(source)) for x in source.rglob('*') if x.is_file()}==set(m['files'])
 actual={n:sha(source/n) for n in m['files']};assert actual==m['files'] and digest(actual)==p['source_graph_sha256']
 before=read(E/'parents-before.json')
 for _,row in before['parents'].items():
  assert {n:sha(Path(row['path'])/n) for n in row['files']}==row['files']
  assert digest(row['files'])==row['graph_sha256']
 root=Path('/home/legolas/rook2')
 assert {n:sha(root/n) if (root/n).is_file() else None for n in before['root_source_before']}==before['root_source_before']
 assert all(sha(n)==h for n,h in before['authority_sha256'].items())
 authorities=read(E/'authority-manifest.json');assert all(sha(n)==h for n,h in authorities.items())
 old=Path(before['parents']['original111']['path'])/'src/ordinary.rs';new=source/'src/ordinary.rs';a=old.read_text();b=new.read_text()
 assert a.split('#[cfg(test)]',1)[0]==b.split('#[cfg(test)]',1)[0]
 assert a[a.index('pub struct Iteration'):]==b[b.index('pub struct Iteration'):]
 # Independent lexical declaration count; no Rust parser.
 counts=collections.Counter();declarations=set()
 for n in sorted(m['files']):
  if n.endswith('.rs') and not n.startswith('tools/'):
   t=(source/n).read_text()
   for at in re.finditer(r'#\[test\]',t):
    name=re.search(r'\bfn\s+(\w+)\s*\(',t[at.end():])[1];assert (n,name) not in declarations;declarations.add((n,name))
    counts['DIAG' if n.startswith('diagnostic/') else 'dev' if n=='src/bin/rook2-dev.rs' else 'lib']+=1
 assert counts=={'DIAG':209,'dev':2,'lib':175}
 main=(source/'diagnostic/src/main.rs').read_text();part=main[main.index('fn dispatch('):main.index('\nfn main(')]
 registered=set(re.findall(r'"([A-Za-z][A-Za-z0-9]*\.[A-Za-z][A-Za-z0-9]*)"',part))
 inv=read(E/'whole-fixture-inventory.json');cm=read(E/'whole-fixture-map.json');rows=[];seen=set();ops=collections.Counter();selected_files=set()
 for fixture in sorted(Path('/home/legolas/king-spec/conformance/fixtures').glob('*.json')):
  d=read(fixture);cases=d.get('cases',[]) if isinstance(d,dict) else []
  selected=[c for c in cases if c.get('request',{}).get('operation') in registered]
  if selected:
   assert len(selected)==len(cases);selected_files.add(str(fixture))
 assert selected_files=={r['fixture'] for r in inv} and len(selected_files)==115
 for row in inv:
  fixture=Path(row['fixture']);d=read(fixture);assert sha(fixture)==row['sha256'] and fixture.stat().st_size==row['bytes']
  assert {k:v for k,v in d.items() if k!='cases'}==row['header'] and len(d['cases'])==row['case_count']
  for i,c in enumerate(d['cases']):
   assert c['id'] not in seen;seen.add(c['id']);op=c['request']['operation'];ops[op]+=1
   rows.append({'fixture':str(fixture),'index':i,'id':c['id'],'operation':op,'case_sha256':digest(c),'request_sha256':digest(c['request']),'expected_sha256':digest({k:v for k,v in c.items() if k not in {'id','request'}})})
 assert rows==cm['cases'] and len(rows)==7673 and len(registered)==117 and set(ops)==registered
 assert dict(sorted(ops.items()))==read(E/'operation-counts.json')
 archives=read(E/'archive-final-manifest.json');archive_results={}
 for name,record in archives.items():
  path=E/name;assert sha(path)==record['sha256'] and path.stat().st_size==record['bytes']
  members=read(Path(str(path)+'.members.json'))
  with tarfile.open(path,'r:gz') as t:
   entries=t.getmembers();assert len(entries)==len(members)==record['entries'] and len({e.name for e in entries})==len(entries)
   assert all(e.isfile() for e in entries)
   got={e.name:hashlib.sha256(t.extractfile(e).read()).hexdigest() for e in entries}
  assert got==members;archive_results[name]={'sha256':record['sha256'],'members':len(got),'independent_every_member_verified':True}
 assert read(E/'tool-terminal.json')['actual_tool_terminal_observed'] and read(E/'tool-terminal.json')['exit_code']==0
 state.update(complete=True,source=str(source),source_graph_sha256=p['source_graph_sha256'],counts={'source':112,'native':46,'tools':23,'cold':43,'native_declarations':177,'DIAG_declarations':209,'operations':117,'cases':7673,'whole_files':115},all_9_parents_root_authorities_unchanged=True,ordinary_entire_production_prefix_and_suffix_exact=True,archives=archive_results,finished_ns=time.time_ns())
except BaseException as e:state.update(error=f'{type(e).__name__}: {e}',traceback=traceback.format_exc(),finished_ns=time.time_ns())
(E/'independent-verification.json').write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
print(json.dumps(state,sort_keys=True));sys.exit(0 if state['complete'] else 1)
