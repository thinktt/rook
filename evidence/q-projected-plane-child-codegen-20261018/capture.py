from pathlib import Path
import os,json,re,hashlib,subprocess,sys
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=load(Path('/home/legolas/rook2/evidence/q-projected-plane-child-validation-preparation-20261018/plan.json'))
assert sorted(os.sched_getaffinity(0))==plan['affinity'] and os.environ['TMPDIR']==plan['TMPDIR']
assert all(sha(Path(plan['home_source'])/n)==h and sha(Path(plan['frozen_source'])/n)==h for n,h in plan['source_sha256'].items())
assert load(Path(plan['output']['native-validation'])/'tool-terminal.json')['exit_code']==0
commands=[]
def run(a,n,env=None):
 with (P/(n+'.stdout')).open('xb') as out,(P/(n+'.stderr')).open('xb') as err:c=subprocess.run(a,stdout=out,stderr=err,env=env)
 commands.append({'command':a,'exit_code':c.returncode,'actual_child_return_observed':True,'stdout_sha256':sha(P/(n+'.stdout')),'stderr_sha256':sha(P/(n+'.stderr'))})
 (P/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert c.returncode==0,n
 return (P/(n+'.stdout')).read_text()
builds={'control':Path(plan['codegen_control']['build']),'candidate':Path(plan['output']['generic-build'])};receipts={t:load(b/'receipt.json') for t,b in builds.items()}
for k in ['toolchain','mode','target_triple','target_cpu','rust_flags','build_effective_environment']:assert receipts['control'][k]==receipts['candidate'][k]
assert all(r['pgo']['mode']=='none' for r in receipts.values()) and sha(builds['control']/'rook2-exact')==plan['codegen_control']['native_sha256']
result={'status':'BOUNDED_CAPTURE_ONLY_PARENT_REVIEW_REQUIRED','tags':{},'layout_probe_method':'Existing exact genericrlib; matchedpanicabort/target/LTO flags; RUSTC_BOOTSTRAP=1 -Zprint-type-sizes ONLY layout/default-public-constructor probe, no search executed'}
for tag,b in builds.items():
 r=receipts[tag];engine=b/'rook2-exact';assert sha(engine)==r['binary_output']['sha256']
 deps=Path(r['binary_output']['path']).parent/'deps';rlibs=list(deps.glob('librook2-*.rlib'));assert len(rlibs)==1;rlib=rlibs[0];probe=P/(tag+'-probe')
 args=['/usr/bin/rustc','--edition=2021','--crate-name','plane_layout_'+tag,'--target','x86_64-unknown-linux-gnu','-C','target-cpu=x86-64','-C','opt-level=3','-C','panic=abort','-C','lto=thin','-C','codegen-units=1','-C','debuginfo=1','-Zprint-type-sizes','--extern','rook2='+str(rlib),'-L','dependency='+str(deps),str(P/'layout-default-probe.rs'),'-o',str(probe)]
 run(args,tag+'-probe-compile',dict(os.environ,RUSTC_BOOTSTRAP='1'));layout=run([str(probe)],tag+'-layout');data={}
 for label,binary in [('engine',engine),('probe',probe)]:
  dis=run(['/usr/bin/objdump','-dC','--no-show-raw-insn',str(binary)],tag+'-'+label+'-disassembly');run(['/usr/bin/nm','-S','-n','-C',str(binary)],tag+'-'+label+'-symbols')
  hs=list(re.finditer(r'^([0-9a-f]+) <(.+)>:\s*$',dis,re.M));fs=[]
  needles=['::visit_ordinary','::visit_q','::full_impl','::ordering_phase','::Node::child','::apply_unchecked','::set_square','::played_','::child_with','default_node','default_position','::generate_legal','::legal_replies_up_to_two','::legal_after_bits','::projected','::check_routes_bits']
  for i,m in enumerate(hs):
   if not any(n in m[2] for n in needles):continue
   body=dis[m.start():hs[i+1].start() if i+1<len(hs) else len(dis)];ls=body.splitlines();f=tag+'-'+label+'-function-'+str(len(fs))+'.txt';(P/f).write_text(body)
   fs.append({'symbol':m[2],'address':m[1],'instructions':sum(bool(re.match(r'^\s*[a-f0-9]+:',l)) for l in ls),'static_calls':[l for l in ls if re.search(r'\bcall\s',l)],'stack':[l for l in ls if re.search(r'\b(?:sub|add|and|lea)\b.*%rsp|\b(?:push|pop)\b',l)],'file':f})
  data[label]=fs
 result['tags'][tag]={'engine_sha256':sha(engine),'rlib':str(rlib),'rlib_sha256':sha(rlib),'probe_sha256':sha(probe),'probe_source_sha256':sha(P/'layout-default-probe.rs'),'layouts':layout,'functions':data}
 assert sha(engine)==r['binary_output']['sha256']
result['commands']=commands
(P/'capture.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'layouts':{t:x['layouts'] for t,x in result['tags'].items()},'function_counts':{t:{k:len(v) for k,v in x['functions'].items()} for t,x in result['tags'].items()}}))
