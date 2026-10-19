#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
d=load(P/'discovery.json');requests=load(P/'body-request.json');bodyproof=load(P/'bodies.json')
assert bodyproof['complete'] and bodyproof['all_discovery_inputs_unchanged']
images={side:Path(next(p for p in d['pins'] if p.endswith('/rook2-exact') and name in p)) for side,name in [('control','influence-bitsliced-sum-pgo-use-build'),('candidate','ordinary-position-borrow-pgo-use-build')]}
plan=load(P/'plan.json')
def metadata(side,stem):
 return Path(plan['control_saved_metadata'][stem]['path']) if side=='control' else P/(side+'-'+stem+'.stdout')
sections={};raw={};symbols={}
for side,image in images.items():
 raw[side]=image.read_bytes();assert sha(raw[side])==d['pins'][str(image)]
 sections[side]={}
 for line in metadata(side,'sections').read_text().splitlines():
  m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+',line)
  if m:
   name,kind,addr,offset,size=m.groups();sections[side][name]=dict(kind=kind,address=int(addr,16),offset=int(offset,16),bytes=int(size,16))
 symbols[side]={}
 for line in metadata(side,'nm').read_text().splitlines():
  m=re.match(r'([0-9a-f]+) ([0-9a-f]+) ([tT]) (.+)$',line)
  if m:symbols[side][int(m[1],16)]=dict(bytes=int(m[2],16),name=m[4])
def get(side,address,size):
 s=next(s for s in sections[side].values() if s['kind']=='PROGBITS' and s['address']<=address and address+size<=s['address']+s['bytes'])
 offset=s['offset']+address-s['address'];return raw[side][offset:offset+size]
def resolve(side,instruction):
 m=re.search(r'# ([0-9a-f]+)',instruction)
 if not m:return None
 slot=int(m[1],16)
 rows=[line for line in metadata(side,'relocations').read_text().splitlines() if re.match(r'^0*'+format(slot,'x')+r'\s',line)]
 if len(rows)!=1:return dict(slot=hex(slot),resolved=False)
 line=rows[0]
 if 'R_X86_64_RELATIVE' in line:
  address=int(line.split()[-1],16);return dict(slot=hex(slot),relocation=line,target_address=hex(address),symbol=symbols[side].get(address))
 return dict(slot=hex(slot),relocation=line)
functionproof={}
for label in sorted({r['label'] for r in requests}):
 pair={}
 for side in ['control','candidate']:
  matches=[r for r in requests if r['side']==side and r['label']==label]
  if not matches:continue
  assert len(matches)==1
  r=matches[0];address=int(r['start'],16);code=get(side,address,r['bytes'])
  assert symbols[side][address]==dict(bytes=r['bytes'],name=r['actual_symbol'])
  body=next(x for x in bodyproof['bodies'] if x['side']==side and x['label']==label)
  text=Path(body['raw_path']).read_text();assert hashlib.sha256(Path(body['raw_path']).read_bytes()).hexdigest()==body['command']['stdout_sha256']
  if '--no-show-raw-insn' in body['command']['argv']:
   ins=re.findall(r'^\s*([0-9a-f]+):\s+(.+)$',text,re.M)
  else:
   # Reused exact43 ordinary includes raw opcode columns; continuation byte rows are not instructions.
   ins=re.findall(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]*\b[^\n]*)$',text,re.M)
  calls=[dict(address=a,operand=i,resolved=resolve(side,i)) for a,i in ins if re.match(r'call\s',i)]
  refs=[dict(address=a,operand=i,resolved=resolve(side,i)) for a,i in ins if '# ' in i and resolve(side,i)]
  pair[side]=dict(address=hex(address),bytes=r['bytes'],machine_sha256=sha(code),stack_reservations=re.findall(r'\bsub\s+rsp,(0x[0-9a-f]+)',text),pushes=sum(bool(re.match(r'push\s',i)) for _,i in ins),call_sites=calls,resolved_RIP_references=refs,instructions=len(ins),AND_instructions=[dict(address=a,operand=i) for a,i in ins if re.match(r'and\s',i)],conditional_branches=[dict(address=a,operand=i) for a,i in ins if re.match(r'j(?!mp)[a-z]+\s',i)])
 functionproof[label]=dict(**pair)
 if set(pair)=={'control','candidate'}:
  functionproof[label].update(complete_machine_bytes_identical=pair['control']['machine_sha256']==pair['candidate']['machine_sha256'],size_delta=pair['candidate']['bytes']-pair['control']['bytes'])
sectionproof={name:{side:sections[side][name] for side in ['control','candidate']} for name in ['.text','.rodata','.data.rel.ro']}
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in d['pins'].items())
result=dict(complete=True,functions=functionproof,sections=sectionproof,all_inputs_unchanged=True,all_capture_children_exit0=all(r['exit_code']==0 for r in d['commands']) and all(r['command']['exit_code']==0 for r in bodyproof['bodies']),complete_function_count=len(requests),raw_complete_function_bytes=bodyproof['total_raw_bytes'],mechanism_verdict='Manual source-bound entry snapshot/relocation and shared full_parts/return/observer caller audit required; absence of one memcpy alone is insufficient.',limits=['No CPU or correctness execution, generic-to-PGO transfer or whole-binary equality.','Only requested complete linked bodies, at most4 total; source crosswalk covers absent public/observed/root/Q wrappers without inventing emitted counterparts.','Check entry160 copy versus relocation into wrappers/returns/child construction; actual frames/calls/size/ABI/spills and source alias/lifetime invariants. No dynamic copy cost or Callgrind suffix mapping inferred.'])
with (P/'analysis.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(complete=True,body_sizes={k:{s:v[s]['bytes'] for s in ['control','candidate'] if s in v} for k,v in functionproof.items()},all_inputs_unchanged=True)))
