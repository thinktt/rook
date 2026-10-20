"""Read-only own-image bounded binutils capture; no engine execution."""
from pathlib import Path
import hashlib,json,subprocess,re
P=Path(__file__).resolve().parent;E=P.parent
DIRS={'control':'ordinary-projected-bits-generic-build-20261018-01','candidate':'full-evaluation-phase-sharing-generic-build-20261018-01'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,x):
 with (P/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
pins={};receipts={};commands=[]
for side,dirname in DIRS.items():
 d=E/dirname;r=json.loads((d/'receipt.json').read_text());receipts[side]=r
 assert r['cargo_exit_code']==0 and r['mode']=='generic' and r['pgo']['mode']=='none'
 for path in [d/'rook2-exact',d/'receipt.json',d/'tool-terminal.json']:
  pins[str(path)]=sha(path)
 assert sha(d/'rook2-exact')==r['binary_output']['sha256']
 assert r['source_sha256_before']==r['source_sha256_after']
 assert r['tool_sha256_before']==r['tool_sha256_after']
 for path,h in {**r['source_sha256_before'],**r['tool_sha256_before']}.items():
  p=d/'source-before'/path;assert sha(p)==h;pins[str(p)]=h
c,t=receipts['control'],receipts['candidate']
for key in ['mode','target_triple','target_cpu','jobs','build_effective_environment','toolchain','rust_flags','pgo']:
 assert c[key]==t[key],key
assert c['tool_sha256_before']==t['tool_sha256_before']
changed=sorted(k for k,v in c['source_sha256_before'].items() if t['source_sha256_before'][k]!=v)
assert changed==['src/activity.rs','src/evaluator.rs','src/positional_terms.rs','src/shelter.rs']
for n in ['selection.json','parent-source-review.json','execution-binding.json']:
 p=E/'full-evaluation-phase-sharing-preparation-20261018-01'/n;pins[str(p)]=sha(p)
p=E/'full-evaluation-phase-sharing-source-review-20261018-01/review.md';pins[str(p)]=sha(p)
def run(argv,stem):
 out=P/(stem+'.stdout');err=P/(stem+'.stderr');out.parent.mkdir(exist_ok=True)
 with out.open('xb') as o,err.open('xb') as e:r=subprocess.run(argv,stdout=o,stderr=e)
 commands.append({'argv':argv,'exit_code':r.returncode,'stdout':str(out),'stderr':str(err)})
 assert r.returncode==0,(stem,r.returncode)
 return out.read_text()
functions={}
for side,dirname in DIRS.items():
 image=str(E/dirname/'rook2-exact')
 nm=run(['/usr/bin/nm','--numeric-sort','--print-size','--demangle',image],side+'/nm')
 run(['/usr/bin/size','-A',image],side+'/size')
 rows=[]
 for line in nm.splitlines():
  m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) ([tT]) (.*)$',line)
  if not m:continue
  address,size=int(m[1],16),int(m[2],16);name=m[4]
  targets=['::Position::phase','::activity::compute','::shelter::compute','::pawn_terms::compute','::positional_terms::patterns','::full_impl','::fast_impl']
  selected=any(s in name for s in targets)
  if selected or '::visit_ordinary_impl' in name or '::visit_q_impl' in name:
   row={'address':hex(address),'bytes':size,'symbol':name,'captured':selected}
   if selected:
    stem=side+'/body-'+format(address,'x');run(['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(address),'--stop-address='+hex(address+size),image],stem)
    row['assembly']=stem+'.stdout'
   rows.append(row)
 functions[side]=rows
assert all(sha(Path(p))==h for p,h in pins.items())
put('input-pins.json',pins);put('capture.json',{'complete':True,'commands':commands,'functions':functions,'only_source_changes':changed,'compiler_flags_and_tools_match':True,'all_inputs_unchanged':True,'new_native_engine_runs':0})
print(json.dumps({'images':{k:v['binary_output']['sha256'] for k,v in receipts.items()},'functions':functions,'commands':len(commands)},indent=2))
