"""Bounded own-image experiment32 own-PGO static capture; no engine/search execution."""
from pathlib import Path
import hashlib,json,re,subprocess
P=Path(__file__).resolve().parent;E=P.parent
D={'control':E/'ordinary-projected-bits-pgo-use-build-20261018-01','candidate':E/'pressure-table-traversal-pgo-use-build-20261019-01'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
pins={};rs={};cmd=[];fs={}
for side,d in D.items():
 r=json.loads((d/'receipt.json').read_text());rs[side]=r
 assert r['source_sha256_before']==r['source_sha256_after'];assert r['tool_sha256_before']==r['tool_sha256_after']
 assert r['cargo_exit_code']==0 and r['pgo']['mode']=='profile-use'
 for p in [d/'receipt.json',d/'rook2-exact',d/'tool-terminal.json']:
  pins[str(p)]=sha(p)
 assert sha(d/'rook2-exact')==r['binary_output']['sha256']
 for n,h in {**r['source_sha256_before'],**r['tool_sha256_before']}.items():
  p=d/'source-before'/n;assert sha(p)==h;pins[str(p)]=h
profiles={};normalized_env={}
for side,r in rs.items():
 pgo=r['pgo'];assert pgo['input_sha256_before']==pgo['input_sha256_after'] and pgo['inputs_unchanged']
 for path,h in pgo['input_sha256_before'].items():assert sha(Path(path))==h;pins[path]=h
 t=json.loads(Path(pgo['training_record']).read_text());vpath=Path(pgo['training_record']).parent/'verification.json';v=json.loads(vpath.read_text());pins[str(vpath)]=sha(vpath)
 assert t['complete'] and len(t['raw_profiles_sha256'])==54 and t['engine_source_sha256']==r['source_sha256_before']
 assert v['complete'] and v['independent_remerge_byte_identical'] and v['strict_replays']==54
 assert sha(Path(pgo['profile']))==t['profile_sha256']==v['merged_profile_sha256']
 assert r['rust_flags']==['-C','target-cpu=x86-64','-C','profile-use='+pgo['profile'],'-C','llvm-args=-pgo-warn-missing-function']
 normalized_env[side]={k:(x.replace(pgo['profile'],'@OWN_PROFILE@') if isinstance(x,str) else x) for k,x in r['build_effective_environment'].items()}
 warnings=Path(D[side]/'build.stderr').read_text().lower();pins[str(D[side]/'build.stderr')]=sha(D[side]/'build.stderr')
 for needle in ['no profile data available for function','profile data may be out of date','profile data mismatch','malformed instrumentation profile data','hash mismatch','unprofiled function']:assert needle not in warnings,needle
 profiles[side]={'path':pgo['profile'],'sha256':t['profile_sha256'],'own_source46_bound':True,'training_raw_files':54,'independent_remerge_byte_identical':True}
for key in ['mode','target_triple','target_cpu','jobs','toolchain']:
 assert rs['control'][key]==rs['candidate'][key],key
assert normalized_env['control']==normalized_env['candidate']
assert profiles['control']['sha256']!=profiles['candidate']['sha256']
put('paired-provenance.json',{'own_profiles':profiles,'compiler_baseflags_normalized_environment_equal':True,'no_missing_or_stale_profile_warnings':True})
assert rs['control']['tool_sha256_before']==rs['candidate']['tool_sha256_before']
changed=[n for n,h in rs['control']['source_sha256_before'].items() if rs['candidate']['source_sha256_before'][n]!=h]
assert changed==['src/activity.rs']
for n in ['review.md','trial.patch','source-proof.json','source-manifest.json','closure.json','plan.json']:
 p=E/'pressure-table-traversal-preparation-20261019-01'/n;pins[str(p)]=sha(p)
for n in ['nm','objdump','size']:p=Path('/usr/bin')/n;pins[str(p)]=sha(p)
def run(argv,stem):
 o=P/(stem+'.stdout');e=P/(stem+'.stderr');o.parent.mkdir(exist_ok=True)
 with o.open('xb') as so,e.open('xb') as se:r=subprocess.run(argv,stdout=so,stderr=se)
 cmd.append({'argv':argv,'exit_code':r.returncode,'stdout':str(o),'stderr':str(e)})
 assert r.returncode==0
 return o.read_text()
for n in ['nm','objdump','size']:run(['/usr/bin/'+n,'--version'],n+'-version')
for side,d in D.items():
 image=str(d/'rook2-exact');nm=run(['/usr/bin/nm','--numeric-sort','--print-size','--demangle',image],side+'/nm')
 run(['/usr/bin/size','-A',image],side+'/size');rows=[]
 for line in nm.splitlines():
  m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',line)
  if not m:continue
  address,length,name=int(m[1],16),int(m[2],16),m[3]
  selected='rook2::activity::compute' in name or 'rook2::activity::king_pressure' in name
  if selected or any(x in name for x in ['::visit_ordinary_impl','::visit_q_impl','::full_impl','::run_work_timed_impl']) or name=='rook2::run':
   row={'address':hex(address),'bytes':length,'symbol':name,'captured':True}
   if True:
    stem=side+'/body-'+format(address,'x');text=run(['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(address),'--stop-address='+hex(address+length),image],stem)
    a=[(m[1],m[2]) for s in text.splitlines() if (m:=re.match(r'^\s*([0-9a-f]+):\s+(.*)',s))]
    row.update(assembly=stem+'.stdout',static_instructions=len(a),stack_memory_reference_instructions=[{'address':x,'instruction':y} for x,y in a if '[rsp' in y and not y.startswith(('lea','nop'))],rsp_adjustments=[{'address':x,'instruction':y} for x,y in a if re.match(r'(sub|add)\s+rsp,',y)],calls=[{'address':x,'instruction':y} for x,y in a if y.startswith('call')],imuls=[{'address':x,'instruction':y} for x,y in a if y.startswith('imul')])
   rows.append(row)
 fs[side]=rows
assert all(sha(Path(p))==h for p,h in pins.items())
put('input-pins.json',pins);put('capture.json',{'complete':True,'commands':cmd,'functions':fs,'only_changed_source':changed,'all_inputs_unchanged':True,'compiler_baseflags_normalized_environment_tools_equal':True})
print(json.dumps({'complete':True,'commands':len(cmd),'functions':{s:[{'symbol':r['symbol'],'address':r['address'],'bytes':r['bytes'],'static_instructions':r['static_instructions'],'stack_refs':len(r['stack_memory_reference_instructions']),'calls':len(r['calls']),'entry_rsp':r['rsp_adjustments'][:1]} for r in rows] for s,rows in fs.items()}},indent=2))
