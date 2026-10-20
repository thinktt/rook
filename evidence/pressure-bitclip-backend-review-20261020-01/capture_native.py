from pathlib import Path
import hashlib,json,subprocess,resource,os,sys,time
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/legolas/rook2')
OUT=HERE/'capture'
OUT.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def record(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
plan=json.loads((HERE/'plan.json').read_text())
variants={'baseline':ROOT/'evidence/bitplane-pin-summary-generic-build-20261020-01','candidate':ROOT/'evidence/pressure-bitclip-generic-build-20261020-01'}
expected={'baseline':'5d10b2fa6b75b1eead79a444c5eaccd13f5e8b959e1d0469075be1ebabba27e6','candidate':'2c7d2bf57d8da9651a4eccb2f269e83637b8dd08a196eeb3fbd861ea7c7d3218'}
inputs={}
for label,b in variants.items():
 image=b/'rook2-exact';assert sha(image)==expected[label]
 receipt=json.loads((b/'receipt.json').read_text())
 assert receipt['mode']=='generic' and receipt['pgo']['mode']=='none'
 assert receipt['source_sha256_before']==receipt['source_sha256_after']
 assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
 for rel,h in (receipt['source_sha256_before']|receipt['tool_sha256_before']).items():
  q=Path(receipt['crate'])/rel;assert sha(q)==h,(label,rel)
  inputs[str(q)]=h
 inputs[str(image)]=expected[label]
 for name in ['receipt.json','frozen-image.json']:inputs[str(b/name)]=sha(b/name)
a=json.loads((variants['baseline']/'receipt.json').read_text());b=json.loads((variants['candidate']/'receipt.json').read_text())
for k in ['toolchain','rust_flags','target_cpu','tool_sha256_before']:assert a[k]==b[k],k
freeze=ROOT/'evidence/pressure-bitclip-parent-review-20261020-01/source-freeze.json'
assert sha(freeze)=='f5d1318a9b300fd1a8f1548837375a26e0db9708b593285a314bf4df2788046c'
inputs[str(freeze)]=sha(freeze)
archive=variants['candidate']/'verified-source-before.tar.gz';assert sha(archive)=='327b4f236a44edce65643a3140e52a6921fc4273901391c348bf86f2aed34ba8';inputs[str(archive)]=sha(archive)
for q in ['/usr/bin/nm','/usr/bin/readelf','/usr/bin/objdump']:inputs[q]=sha(Path(q))
started=time.monotonic();commands=[]
def run(name,argv,limit):
 assert time.monotonic()-started<180
 out=OUT/(name+'.stdout');err=OUT/(name+'.stderr')
 assert not out.exists() and not err.exists()
 def cap():resource.setrlimit(resource.RLIMIT_FSIZE,(limit,limit))
 with out.open('wb') as o,err.open('wb') as e:
  p=subprocess.Popen(argv,stdout=o,stderr=e,preexec_fn=cap,start_new_session=True)
  try:rc=p.wait(timeout=30)
  except BaseException:
   os.killpg(p.pid,9);p.wait(timeout=5);raise
 row={'argv':argv,'exit_code':rc,'pid':p.pid,'stdout_bytes':out.stat().st_size,'stdout_sha256':sha(out),'stderr_bytes':err.stat().st_size,'stderr_sha256':sha(err)}
 commands.append(row);record(OUT/(name+'.command.json'),row)
 assert rc==0 and out.stat().st_size<limit and err.stat().st_size<=65536,row
if sys.argv[1]=='metadata':
 for label,b in variants.items():
  run(label+'-nm',['/usr/bin/nm','-S','--defined-only','--demangle',str(b/'rook2-exact')],262144)
  run(label+'-sections',['/usr/bin/readelf','-h','-S',str(b/'rook2-exact')],65536)
elif sys.argv[1]=='native-bodies':
 bodies=json.loads((HERE/'native-body-selection.json').read_text());assert len(bodies)<=10
 for x in bodies:
  run(x['label'],['/usr/bin/objdump','-d','-C','--no-show-raw-insn','--start-address='+hex(x['start']),'--stop-address='+hex(x['end']),str(variants[x['variant']]/'rook2-exact')],2097152)
 assert sum((OUT/(x['label']+'.stdout')).stat().st_size for x in bodies)<=2097152
else:raise ValueError('unknown stage')
for path,h in inputs.items():assert sha(Path(path))==h,path
record(OUT/(sys.argv[1]+'-result.json'),{'complete':True,'commands':commands,'inputs_before_after_equal':inputs,'new_native_runs':0,'all_owned_children_reaped':True})
print(json.dumps({'stage':sys.argv[1],'commands':len(commands),'complete':True,'all_owned_children_reaped':True}))
