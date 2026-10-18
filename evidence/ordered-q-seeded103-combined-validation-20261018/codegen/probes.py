from pathlib import Path
import json,subprocess,hashlib,os
C=Path(__file__).parent;E=C.parents[1];I=json.loads((C/'inputs.json').read_text());records=[];layouts={};offsets={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
def run(cmd,stem):
 with (C/(stem+'.stdout')).open('xb') as a,(C/(stem+'.stderr')).open('xb') as b:p=subprocess.run(cmd,stdout=a,stderr=b)
 records.append({'command':cmd,'exit_code':p.returncode,'stdout_sha256':sha(C/(stem+'.stdout')),'stderr_sha256':sha(C/(stem+'.stderr'))});assert p.returncode==0,stem
 return (C/(stem+'.stdout')).read_text()
for label,item in I['artifacts'].items():
 B=Path(item['build']);r=json.loads((B/'receipt.json').read_text());release=Path(r['binary_output']['path']).parent;libs=list((release/'deps').glob('librook2-*.rlib'));assert len(libs)==1;lib=libs[0];D=C/(label+'-probes');D.mkdir();base=['/usr/bin/rustc','--edition=2021','--target','x86_64-unknown-linux-gnu','-C','target-cpu=x86-64','-C','opt-level=3','-C','panic=abort','--extern','rook2='+str(lib),'-L','dependency='+str(release/'deps')]
 for source,stem in [('layout_probe.rs','layout'),('public_offset_probe.rs','offset')]:
  target=D/stem;run(base+[str(C/source),'-o',str(target)],label+'-'+stem+'-compile');text=run([str(target)],label+'-'+stem+'-readout')
  if stem=='layout':layouts[label]={line.split()[0]:{'size':int(line.split()[1]),'alignment':int(line.split()[2])} for line in text.splitlines()}
  else:offsets[label]={line.split()[0]:int(line.split()[1]) for line in text.splitlines()}
 obj=D/'default-fixed.o';run(base+['--crate-type=lib','--emit=obj',str(C/'default_fixed_probe.rs'),'-o',str(obj)],label+'-default-fixed-object-compile');run(['/usr/bin/nm','-S','-n','-C',str(obj)],label+'-default-fixed-symbols');run(['/usr/bin/objdump','-d','-r','-C','--no-show-raw-insn',str(obj)],label+'-default-fixed-disassembly');(D/'identity.json').write_text(json.dumps({'rlib':str(lib),'rlib_sha256':sha(lib),'default_fixed_object_sha256':sha(obj),'source_sha256':{name:sha(C/name) for name in ['layout_probe.rs','public_offset_probe.rs','default_fixed_probe.rs']},'scope':'No control rebuild; exact existing generic rlib; layout programs construct no search, fixed object never executed'},indent=2)+'\n')
 assert sha(Path(item['binary']))==item['binary_sha256']
assert layouts['control102']==layouts['combined103'] and offsets['control102']==offsets['combined103']
# Retain prior root95/generation2 risk without rebuilding it: source Stats/Work declarations and measured102 baseline.
old=json.loads((Path('/home/legolas/rook2/evidence/iterations-clock102-codegen-02-20261018/capture.json')).read_text());out={'complete':True,'layouts':layouts,'offsets':offsets,'current_layouts_and_offsets_equal':True,'preexisting102_vs_generation2_layout_deltas':old['layout_deltas'],'preexisting102_layouts_reproduced':layouts['control102']==old['layouts']['combined102'],'commands':records,'no_search_executions':True,'fixed_objects_never_executed':True};assert out['preexisting102_layouts_reproduced'];(C/'probes.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['commands','layouts','offsets']}))
