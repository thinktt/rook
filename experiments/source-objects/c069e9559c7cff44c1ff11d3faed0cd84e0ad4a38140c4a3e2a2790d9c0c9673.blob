"""Bounded authorized42 static comparison; no engine or source mutation."""
from pathlib import Path
import json,hashlib,os,subprocess,sys,re
P=Path(__file__).resolve().parent;E=P.parent
D={"control":E/'pressure-value-static-generic-build-20261019-01',"candidate":E/'activity-borrowed-geometry-generic-build-20261019-01'}
EXPECTED={"control":"adbf66a39b710bc0f44db2ceb99cac7b823fc02962e4c23a2d6ec12dfa92d664","candidate":"7177275ade2989d139998fcc667b0953a4b0edcd2617c1101bc51906a2bab3b3"}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
def save(n,q):
 with (P/n).open('x') as f:json.dump(q,f,indent=2);f.write('\n')
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
pins={str(P/'capture.py'):sha(P/'capture.py')};receipts={}
freeze=E/'activity-borrowed-geometry-parent-review-20261019-01/source-freeze.json';q=load(freeze);pins[str(freeze)]=sha(freeze)
assert q['source_graph']=='64cef0f22818677df07aebc20c1e7072e53c1efcc1cf1e2d87274fb585ed48cd'
for side,b in D.items():
 r=load(b/'receipt.json');receipts[side]=r
 assert r['cargo_exit_code']==0 and r['mode']=='generic' and r['pgo']['mode']=='none'
 assert r['rust_flags']==['-C','target-cpu=x86-64']
 assert r['source_sha256_before']==r['source_sha256_after'] and len(r['source_sha256_before'])==49
 assert r['tool_sha256_before']==r['tool_sha256_after'] and len(r['tool_sha256_before'])==23
 assert sha(b/'rook2-exact')==EXPECTED[side]==r['binary_output']['sha256']
 terminal_path=b/'tool-terminal.json'
 term=load(terminal_path);pins[str(terminal_path)]=sha(terminal_path)
 if side=='candidate':
  assert term['exit_code']==0 and term['actual_terminal_chunk']=='43e72e' and term['session_id']==84692 and term['launch_actual_chunk']=='947b92'
  assert term['artifact_sha256']==EXPECTED[side] and term['result_sha256']==sha(E/'activity-borrowed-geometry-generic-build-execution-20261019-01/result.json')
 else:assert term['actual_tool_terminal_observed'] and term['exit_code']==0 and (term.get('terminal_chunk_id') or term.get('chunk_id'))
 for n in ['receipt.json','rook2-exact','frozen-image.json','build.stderr']:pins[str(b/n)]=sha(b/n)
 for n,h in (r['source_sha256_before']|r['tool_sha256_before']).items():
  f=b/'source-before'/n;assert sha(f)==h;pins[str(f)]=h
 log=(b/'build.stderr').read_text();lines=[l for l in log.splitlines() if 'Running ' in l and '--crate-type bin' in l and 'src/bin/rook2.rs' in l]
 assert len(lines)==1 and '-C lto=thin ' in lines[0] and '-C codegen-units=1 ' in lines[0]
execution=E/'activity-borrowed-geometry-generic-build-execution-20261019-01/result.json';pins[str(execution)]=sha(execution);assert load(execution)['complete'] and load(execution)['source_unchanged']
a,b=receipts.values()
for k in ['mode','target_triple','target_cpu','jobs','toolchain','build_effective_environment']:assert a[k]==b[k],k
assert a['tool_sha256_before']==b['tool_sha256_before']
assert set(a['source_sha256_before'])==set(b['source_sha256_before'])
assert sorted(n for n,h in a['source_sha256_before'].items() if h!=b['source_sha256_before'][n])==['src/activity.rs','src/evaluator.rs','src/ordinary.rs','src/quiescence.rs']
assert q['files_sha256']==b['source_sha256_before']|b['tool_sha256_before']
for t in ['nm','objdump','readelf','size']:pins['/usr/bin/'+t]=sha('/usr/bin/'+t)
def run(argv,stem):
 with (P/(stem+'.stdout')).open('xb') as o,(P/(stem+'.stderr')).open('xb') as e:
  c=subprocess.Popen(argv,stdout=o,stderr=e);code=c.wait()
 row={'argv':argv,'pid':c.pid,'exit_code':code,'actual_child_return_observed':True,'stdout_sha256':sha(P/(stem+'.stdout')),'stderr_sha256':sha(P/(stem+'.stderr'))}
 save(stem+'-command.json',row);assert code==0,row
 return row
stage=sys.argv[1]
if stage=='discover':
 commands=[]
 for t in ['nm','objdump','readelf','size']:commands.append(run(['/usr/bin/'+t,'--version'],t+'-version'))
 for side,b in D.items():
  for t,args,suffix in [('nm',['--numeric-sort','--print-size','--demangle'],'nm'),('nm',['--numeric-sort','--print-size'],'nm-mangled'),('size',['-A'],'size'),('readelf',['-rW'],'relocations'),('readelf',['-SW'],'sections')]:commands.append(run(['/usr/bin/'+t,*args,str(b/'rook2-exact')],side+'-'+suffix))
 assert all(sha(p)==h for p,h in pins.items());save('discovery.json',{'complete':True,'commands':commands,'input_pins':pins})
elif stage=='bodies':
 d=load(P/'discovery.json');assert d['input_pins']==pins
 commands=[];bodies=[]
 for spec in sys.argv[2:]:
  side,addr=spec.split(':');addr=int(addr,16);assert side in D
  rows=[m for l in (P/(side+'-nm.stdout')).read_text().splitlines() if (m:=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',l)) and int(m[1],16)==addr]
  assert len(rows)==1;r=rows[0];size=int(r[2],16);name=r[3]
  assert any(x in name for x in ['rook2::activity::','full_impl','full_for_search'])
  stem=side+'-body-'+format(addr,'x');commands.append(run(['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(addr),'--stop-address='+hex(addr+size),str(D[side]/'rook2-exact')],stem))
  bodies.append({'side':side,'address':addr,'bytes':size,'symbol':name,'stdout':stem+'.stdout'})
 assert len(bodies)<=12 and sum((P/r['stdout']).stat().st_size for r in bodies)<=1048576
 assert all(sha(p)==h for p,h in pins.items());save('bodies.json',{'complete':True,'bodies':bodies,'commands':commands,'all_inputs_unchanged':True})
else:raise ValueError(stage)
print(json.dumps({'complete':True,'stage':stage,'engine_runs':0}))
