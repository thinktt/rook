#!/usr/bin/env python3
"""Future bounded static evidence capture; never auto-accepts codegen risk."""
import json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from guard import HERE,load,sha,write,clearance,terminal,check_sources,check_dependencies

def main():
 plan=clearance();paths={k:Path(v) for k,v in plan['output'].items()};out=paths['codegen']
 terminal(paths['native-validation']/'tool-terminal.json');check_sources(plan);check_dependencies(plan)
 assert out.is_dir() and not (out/'capture.json').exists()
 control=plan['codegen_control'];control_receipt=load(Path(control['build'])/'receipt.json');candidate_receipt=load(paths['generic-build']/'receipt.json')
 assert sha(Path(control['engine']))==control['engine_sha256']==control_receipt['binary_output']['sha256']
 assert sha(paths['generic-build']/'rook2-exact')==candidate_receipt['binary_output']['sha256']
 for key in ['mode','target_triple','target_cpu','rust_flags','toolchain']:
  assert candidate_receipt[key]==control_receipt[key],('unmatched compiler/build setting',key)
 assert candidate_receipt['pgo']['mode']==control_receipt['pgo']['mode']=='none'
 jobs=[]
 def run(argv,stem):
  with (out/(stem+'.stdout')).open('xb') as a,(out/(stem+'.stderr')).open('xb') as b:
   child=subprocess.run(argv,stdout=a,stderr=b)
  jobs.append(dict(command=argv,exit_code=child.returncode,actual_child_return_observed=True,stdout_sha256=sha(out/(stem+'.stdout')),stderr_sha256=sha(out/(stem+'.stderr'))))
  assert child.returncode==0,stem
  return (out/(stem+'.stdout')).read_text()
 for tool in ['/usr/bin/objdump','/usr/bin/nm','/usr/bin/readelf','/usr/bin/rustc']:
  run([tool,'--version'],Path(tool).name+'-version')
 tags={ 'generation2-e77':(Path(control['engine']),control_receipt),
        'combined102':(paths['generic-build']/'rook2-exact',candidate_receipt) }
 captured={};layouts={}
 needles=['::visit_ordinary','::visit_q_impl','::visit_q','::full_impl','::fast','::ordering_phase','::for_move','::continue_subtree','::bind']
 for tag,(engine,receipt) in tags.items():
  disassembly=run(['/usr/bin/objdump','-dCl','--no-show-raw-insn',str(engine)],tag+'-disassembly')
  run(['/usr/bin/nm','-S','-n','-C',str(engine)],tag+'-symbols')
  run(['/usr/bin/readelf','-rW',str(engine)],tag+'-relocations')
  functions=[];headers=list(re.finditer(r'^([0-9a-f]+) <(.+)>:\s*$',disassembly,re.M))
  for index,match in enumerate(headers):
   name=match[2]
   if not any(needle in name for needle in needles):continue
   body=disassembly[match.start():headers[index+1].start() if index+1<len(headers) else len(disassembly)]
   lines=body.splitlines();transfers=[line for line in lines if re.search(r'\b(?:callq?|jmpq?)\s',line)]
   stack=[line for line in lines if re.search(r'\b(?:sub|add|and|lea)\b.*%rsp|\b(?:push|pop)\b',line)]
   filename=f'{tag}-function-{len(functions):02d}.txt';(out/filename).write_text(body)
   functions.append(dict(symbol=name,address=match[1],instructions=sum(bool(re.match(r'^\s*[0-9a-f]+:',line)) for line in lines),static_transfers=transfers,stack_instructions=stack,text=filename))
  assert any('::visit_ordinary' in f['symbol'] for f in functions)
  assert any('::visit_q' in f['symbol'] for f in functions)
  captured[tag]=functions
  # No unchanged-control rebuild: use its existing generic rlib or stop/report.
  release=Path(receipt['binary_output']['path']).parent;rlibs=list((release/'deps').glob('librook2-*.rlib'))
  assert len(rlibs)==1,('need preserved exact generic rlib; do not rebuild control',tag,list(map(str,rlibs)))
  rlib=rlibs[0];probe_dir=out/(tag+'-layout');probe_dir.mkdir();probe=probe_dir/'layout-probe'
  run(['/usr/bin/rustc','--edition=2021','--target','x86_64-unknown-linux-gnu','-C','target-cpu=x86-64','-C','opt-level=3','--extern','rook2='+str(rlib),'-L','dependency='+str(release/'deps'),str(HERE/'layout_probe.rs'),'-o',str(probe)],tag+'-layout-compile')
  values=run([str(probe)],tag+'-layout-readout');layout={}
  for line in values.splitlines():
   name,size,alignment=line.split();layout[name]=dict(size=int(size),alignment=int(alignment))
  assert len(layout)==12;layouts[tag]=layout
  write(probe_dir/'identity.json',dict(rlib=str(rlib),rlib_sha256=sha(rlib),probe_sha256=sha(probe),source_sha256=sha(HERE/'layout_probe.rs')))
  assert sha(engine)==receipt['binary_output']['sha256']
 result=dict(status='CAPTURE_ONLY_REQUIRES_PARENT_REVIEW',artifacts={tag:sha(item[0]) for tag,item in tags.items()},matched_toolchain=True,functions=captured,full_impl_separate_symbol={tag:any('::full_impl' in item['symbol'] for item in items) for tag,items in captured.items()},layouts=layouts,layout_deltas={name:layouts['combined102'][name]['size']-layouts['generation2-e77'][name]['size'] for name in layouts['combined102']},actual_child_commands=jobs,review_required=['Verify actual D=false caller and specialization reachability, not symbol absence','Locate ordering fresh-extension operation and prove guarded counter/storage increment absent; no extra extension query','Ordinary/Q actual recursive calls and wrapper/tail transfers, arguments and frame usage','Full/fast default ownership and single evaluation scope, no observer/dispatch/allocation/query-charge additions','Stats/Search/outcome size growth, changed code/frames and return ABI are explicit material costs','Inspect changed reference/panic/rodata sites when text differences require it; no byte-equality chasing','Stop/report material expansion/call/frame/observer finding before speculative source edits or strict/DIAG'],no_neutrality_claim=True)
 check_sources(plan);check_dependencies(plan);write(out/'capture.json',result)
 print(json.dumps(dict(status=result['status'],layout_deltas=result['layout_deltas'],functions={tag:len(items) for tag,items in captured.items()})))
if __name__=='__main__':main()
