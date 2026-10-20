from pathlib import Path
import os,json,re,hashlib,subprocess,sys
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=load(Path('/home/legolas/rook2/evidence/controlled-root108-validation-preparation-20261018/plan.json'))
assert sorted(os.sched_getaffinity(0))==plan['affinity'] and os.environ['TMPDIR']==plan['TMPDIR']
assert all(sha(Path(plan['home_source'])/n)==h and sha(Path(plan['frozen_source'])/n)==h for n,h in plan['source_sha256'].items())
commands=[]
def run(a,n,env=None):
 with (P/(n+'.stdout')).open('xb') as out,(P/(n+'.stderr')).open('xb') as err:
  c=subprocess.run(a,stdout=out,stderr=err,env=env)
 commands.append({'command':a,'exit_code':c.returncode,'actual_child_return_observed':True,'stdout_sha256':sha(P/(n+'.stdout')),'stderr_sha256':sha(P/(n+'.stderr'))})
 (P/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert c.returncode==0,n
 return (P/(n+'.stdout')).read_text()
builds={'control':Path(plan['codegen_control']['build']),'candidate':Path(plan['output']['generic-build'])}
receipts={t:load(b/'receipt.json') for t,b in builds.items()}
for key in ['toolchain','mode','target_triple','target_cpu','rust_flags']:
 assert receipts['control'][key]==receipts['candidate'][key]
assert all(r['pgo']['mode']=='none' for r in receipts.values())
assert sha(builds['control']/'rook2-exact')==plan['codegen_control']['native_sha256']
result={'status':'CAPTURE_ONLY_PARENT_REVIEW_REQUIRED','tags':{},'private_layout_method':'RUSTC_BOOTSTRAP=1 -Zprint-type-sizes ONLY standalone probe against existing exact generic rlib; engine unchanged; this is not a performance build'}
for tag,b in builds.items():
 receipt=receipts[tag];engine=b/'rook2-exact';assert sha(engine)==receipt['binary_output']['sha256']
 deps=Path(receipt['binary_output']['path']).parent/'deps';rlibs=list(deps.glob('librook2-*.rlib'));assert len(rlibs)==1
 rlib=rlibs[0];probe=P/(tag+'-probe');env=dict(os.environ,RUSTC_BOOTSTRAP='1')
 args=['/usr/bin/rustc','--edition=2021','--crate-name','root_layout_'+tag,'--target','x86_64-unknown-linux-gnu','-C','target-cpu=x86-64','-C','opt-level=3','-C','panic=abort','-C','debuginfo=1','-Zprint-type-sizes','--extern','rook2='+str(rlib),'-L','dependency='+str(deps),str(P/(tag+'-probe.rs')),'-o',str(probe)]
 run(args,tag+'-probe-compile',env)
 layout=run([str(probe)],tag+'-layout')
 data={}
 for label,binary in [('engine',engine),('probe',probe)]:
  dis=run(['/usr/bin/objdump','-dC','--no-show-raw-insn',str(binary)],tag+'-'+label+'-disassembly')
  symbols=run(['/usr/bin/nm','-S','-n','-C',str(binary)],tag+'-'+label+'-symbols')
  headers=list(re.finditer(r'^([0-9a-f]+) <(.+)>:\s*$',dis,re.M));functions=[]
  needles=['run_work_timed','default_root','::visit_ordinary','::visit_q','::full_impl','::ordering_phase','root_schedule','::ranking_score','::aspiration','::Clock::','::adjustment']
  for index,m in enumerate(headers):
   if not any(x in m[2] for x in needles):continue
   body=dis[m.start():headers[index+1].start() if index+1<len(headers) else len(dis)]
   f=tag+'-'+label+'-function-'+str(len(functions))+'.txt';(P/f).write_text(body)
   ls=body.splitlines();functions.append({'symbol':m[2],'address':m[1],'instructions':sum(bool(re.match(r'^\s*[0-9a-f]+:',l)) for l in ls),'static_calls':[l for l in ls if re.search(r'\bcallq?\s',l)],'stack':[l for l in ls if re.search(r'\b(?:sub|add|and|lea)\b.*%rsp|\b(?:push|pop)\b',l)],'file':f})
  data[label]=functions
 result['tags'][tag]={'engine_sha256':sha(engine),'rlib':str(rlib),'rlib_sha256':sha(rlib),'probe_sha256':sha(probe),'source_sha256':sha(P/(tag+'-probe.rs')),'layouts':layout,'functions':data}
 assert sha(engine)==receipt['binary_output']['sha256']
result['commands']=commands
(P/'capture.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'layouts':{t:r['layouts'] for t,r in result['tags'].items()},'function_counts':{t:{k:len(v) for k,v in r['functions'].items()} for t,r in result['tags'].items()}}))
