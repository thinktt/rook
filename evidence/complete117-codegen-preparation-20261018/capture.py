# INERT preparation. No tool runs without independent117 pass and parent clearance.
# Adapted from closed109/111 captures; no automated code-equivalence decision.
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess
from elf_reader import ELF
HERE=Path(__file__).resolve().parent
AFFINITY=[0,1,2,3,4,5,8,9,10,11,12,13]
PREFIX=['/usr/bin/taskset','-c','0-5,8-13']
def load(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def terminal(path):
 value=load(path)
 assert value.get('actual_tool_terminal_observed') is True and value.get('exit_code')==0,path
 assert value.get('terminal_chunk_id') or value.get('chunk_id'),path
 return value
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--binding',required=True)
 args=parser.parse_args();binding=load(args.binding)
 # Fail CLOSED before output creation, binary reads, tool discovery or invocation.
 assert binding.get('execution_authorized') is True,'not authorized'
 assert binding.get('functional_pass_accepted') is True,'117 functional pass not accepted'
 clearance=load(binding['parent_execution_clearance'])
 assert clearance.get('authorized_by_parent') is True and clearance.get('scope')=='complete117-codegen','parent clearance'
 assert clearance['candidate_engine_sha256']==binding['builds']['candidate']['engine_sha256']
 assert binding['functional_terminals'],'no actual functional terminals'
 for path in binding['functional_terminals']:terminal(path)
 assert sorted(os.sched_getaffinity(0))==AFFINITY and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 output=Path(binding['output']);assert not output.exists();output.mkdir()
 commands=[]
 def run(argv,label,env=None):
  actual=PREFIX+argv
  with (output/(label+'.stdout')).open('xb') as stdout,(output/(label+'.stderr')).open('xb') as stderr:
   child=subprocess.run(actual,stdout=stdout,stderr=stderr,env=env)
  commands.append({'command':actual,'exit_code':child.returncode,'actual_child_return_observed':True,
   'stdout_sha256':sha(output/(label+'.stdout')),'stderr_sha256':sha(output/(label+'.stderr'))})
  write(output/'commands.json',commands)
  assert child.returncode==0,label
  return (output/(label+'.stdout')).read_text()
 def check_closure():
  assert sha(binding['functional_summary'])==binding['functional_summary_sha256']
  assert binding['source_closure'] and binding['metadata_closure']
  for mapping in [binding['source_closure'],binding['metadata_closure']]:
   for path,digest in mapping.items():assert sha(path)==digest,path
  for tag,item in binding['builds'].items():
   assert sha(item['engine'])==item['engine_sha256'],tag
   assert sha(item['rlib'])==item['rlib_sha256'],tag
  candidate=binding['builds']['candidate'];assert sha(candidate['diagnostic'])==candidate['diagnostic_sha256']
 def capture(tag,image,binary):
  label=tag+'-'+image
  dis=run(['/usr/bin/objdump','-dC','--no-show-raw-insn',str(binary)],label+'-disassembly')
  run(['/usr/bin/nm','-S','-n','-C',str(binary)],label+'-symbols')
  run(['/usr/bin/readelf','--wide','--sections','--relocs',str(binary)],label+'-sections-relocations')
  run(['/usr/bin/size','-A',str(binary)],label+'-sections-size')
  elf=ELF(binary,output/(label+'-symbols.stdout'))
  headers=list(re.finditer(r'^([0-9a-f]+) <(.+)>:\s*$',dis,re.M));functions=[]
  needles=['rook2::run','run_work_timed','default_root','guarded_root','timed_sequence::drive','ActualEffects','ActualChild',
   'charge_node','charge_search_unit','TerminalPrefix','Terminal::','visit_ordinary','visit_q','ordering_phase','full_impl',
   'root_schedule','Clock::','publish_capture','go_live','seed_from_seconds','completed_events','capture_fields','captured_fields',
   'post_lifecycle','generic_timed','InternalIterativeOrdering','drop_in_place<rook2::timed','drop_in_place<rook2::root_schedule']
  for index,header in enumerate(headers):
   if not any(needle in header[2] for needle in needles):continue
   addr=int(header[1],16)
   matches=[symbol for symbol in elf.symbols if symbol['address']==addr and symbol['name']==header[2] and symbol['size']]
   if len(matches)!=1:
    functions.append({'symbol':header[2],'address':header[1],'status':'NM_BOUND_UNRESOLVED','matches':matches});continue
   size=matches[0]['size'];end=addr+size
   raw=dis[header.start():headers[index+1].start() if index+1<len(headers) else len(dis)]
   rows=[]
   for line in raw.splitlines():
    match=re.match(r'\s*([0-9a-f]+):\s*(.*)',line)
    if match and addr<=int(match[1],16)<end:rows.append({'address':match[1],'instruction':match[2],'raw':line})
   stem=label+'-function-'+str(len(functions));(output/(stem+'.txt')).write_text(raw)
   calls=[];references=[];stack=[];copies=[]
   for i,row in enumerate(rows):
    ins=row['instruction'];entry={'site':row['address'],'instruction':ins,
      'window':[item['raw'] for item in rows[max(0,i-24):i+13]]}
    if '%rsp' in ins or '%rbp' in ins or re.match(r'(push|pop)\b',ins):stack.append(entry)
    if re.search(r'\b(?:rep|movups|movaps|movdqu|movdqa|memcpy|memmove|memset)\b',ins):copies.append(entry)
    if re.match(r'callq?\b',ins) or (re.match(r'jmpq?\b',ins) and ('*' in ins or '<' in ins)):
     calls.append({**entry,'classification':'raw direct/tail/indirect transfer; no dynamic count inferred'})
    referent=re.search(r'#\s+([0-9a-f]+)',ins)
    if referent and '(%rip)' in ins:
     target=int(referent[1],16);resolved=elf.resolve(target);width=None
     mnemonic=ins.split()[0]
     if mnemonic in ['movsd','mulsd','ucomisd','comisd','addsd','subsd','divsd']:width=8
     if mnemonic in ['movss','mulss','ucomiss','comiss','addss','subss','divss']:width=4
     if mnemonic in ['movups','movaps','movdqu','movdqa']:width=16
     if re.match(r'callq?\b',ins):width=8
     ref={**entry,'target':hex(target),'initial_resolution':resolved,
      'operand_width':width,'width_status':'opcode-derived; review actual use' if width else 'UNRESOLVED_DATAFLOW_REQUIRED'}
     if width:ref['exact_operand_bytes_hex']=elf.read(target,width).hex()
     # Address-taken descriptors/table bases remain UNRESOLVED: no arbitrary32byte equality.
     location=elf.location(target)
     if location:ref['possible_source_location']=location
     references.append(ref)
   write(output/(stem+'-calls.json'),calls);write(output/(stem+'-references.json'),references)
   write(output/(stem+'-stack-copy.json'),{'stack':stack,'copies':copies})
   functions.append({'symbol':header[2],'address':header[1],'bytes':size,'instructions':len(rows),
    'static_transfers':len(calls),'frame_status':'raw all-path stack windows; reviewer computes actual frame/live ranges',
    'body':stem+'.txt','calls':stem+'-calls.json','references':stem+'-references.json','stack_copy':stem+'-stack-copy.json'})
  write(output/(label+'-index.json'),{'binary':str(binary),'sha256':sha(binary),'functions':functions,
   'unresolved_references_must_be_reviewed':True,'normalized_equality_computed':False})
  return {'binary':str(binary),'sha256':sha(binary),'index':label+'-index.json'}
 try:
  check_closure()
  receipts={tag:load(item['receipt']) for tag,item in binding['builds'].items()}
  assert set(receipts)=={'control','candidate'}
  for key in ['toolchain','mode','target_triple','target_cpu','rust_flags']:
   assert receipts['control'][key]==receipts['candidate'][key],key
  for tag,receipt in receipts.items():
   assert receipt['pgo']['mode']=='none' and receipt['binary_output']['sha256']==binding['builds'][tag]['engine_sha256']
  assert sha('/usr/bin/rustc')==receipts['control']['toolchain']['rustc_executable_sha256']
  assert run(['/usr/bin/rustc','-vV'],'rustc-vV')==receipts['control']['toolchain']['rustc']['stdout']
  diagnostic_receipt=load(binding['diagnostic_receipt'])
  assert diagnostic_receipt['binary_output']['sha256']==binding['builds']['candidate']['diagnostic_sha256']
  for key in ['toolchain','mode','target_triple','target_cpu','rust_flags']:
   assert diagnostic_receipt[key]==receipts['candidate'][key],('diagnostic',key)
  assert diagnostic_receipt['pgo']['mode']=='none'
  assert binding['builds']['control']['engine_sha256']=='17e75a5a60bcfe31f75ae9ea49859dead1b6fec542a405b0280b9b54e2e9c823'
  assert binding['release_profile']=={'opt_level':3,'lto':'thin','codegen_units':1,'panic':'abort','debuginfo':1}
  assert binding['release_profile_source_equality_verified'] is True
  for tool in ['/usr/bin/rustc','/usr/bin/objdump','/usr/bin/nm','/usr/bin/readelf','/usr/bin/size']:
   run([tool,'--version'],Path(tool).name+'-version')
  # PRIMARY images first. Never execute either ordinary engine.
  captured={}
  for tag in ['control','candidate']:
   captured[tag+'-engine']=capture(tag,'engine',binding['builds'][tag]['engine'])
  if binding.get('optional111'):
   item=binding['optional111'];assert item['qualified'] is False
   assert item['sha256']=='efe5419564b867dfac1d6fdcef922d4380b586f00637629badd898f190649377'
   assert sha(item['engine'])==item['sha256']
   captured['failed111-attribution-only']=capture('failed111-attribution-only','engine',item['engine'])
  # Supplemental matching NoHost monomorphs from exact existing generic rlibs.
  for tag,template in [('control','capture-layout-default.rs'),('candidate','capture-layout-default.rs'),
    ('candidate-guarded','capture-layout-guarded.rs'),('candidate-types','capture-layout-candidate-types.rs')]:
   item=binding['builds']['control' if tag=='control' else 'candidate']
   probe_source=output/(tag+'-probe.rs');probe_source.write_bytes((HERE/template).read_bytes())
   probe=output/(tag+'-probe');environment=dict(os.environ,RUSTC_BOOTSTRAP='1')
   argv=['/usr/bin/rustc','--edition=2021','--crate-name','complete117_layout_'+tag.replace('-','_'),
    '--target',receipts['control']['target_triple'],'-C','target-cpu='+receipts['control']['target_cpu'],
    '-C','opt-level=3','-C','panic=abort','-C','lto=thin','-C','codegen-units=1','-C','debuginfo=1',
    '-Zprint-type-sizes','--extern','rook2='+item['rlib'],'-L','dependency='+str(Path(item['rlib']).parent),str(probe_source),'-o',str(probe)]
   run(argv,tag+'-probe-compile',environment)
   # This main prints sizes/alignments only. It NEVER calls either retained root pointer.
   run([str(probe)],tag+'-layout-only')
   if tag!='candidate-types':captured[tag+'-probe']=capture(tag,'probe',probe)
  # Separately label false-guard DIAG image: no109 counterpart exists.
  captured['candidate-diagnostic']=capture('candidate','diagnostic',binding['builds']['candidate']['diagnostic'])
  check_closure()
  write(output/'capture.json',{'status':'CAPTURE_ONLY_REVIEW_REQUIRED','images':captured,
   'primary':'actual WireHost ordinary images','supplemental':'matching NoHost probes, candidate-only guarded/DIAG',
   'scope':'No normalized equivalence, dynamic copy/call/allocation count, CPU or promotion claim. Resolve all operands/ABI and review failures manually.',
   'commands':commands,'all_child_return_codes_observed':True,'outer_actual_tool_terminal_required':True})
 except BaseException as error:
  write(output/'failure.json',{'type':type(error).__name__,'message':str(error),'commands':commands,
   'outputs_preserved':True,'retry_requires_new_label':True,'native_source_fix_authorized':False})
  raise
if __name__=='__main__':main()
