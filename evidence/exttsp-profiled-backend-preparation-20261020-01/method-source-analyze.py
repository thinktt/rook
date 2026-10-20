#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
from capture import setup,read,sha as file_sha
plan=setup('analyze')
P=Path(__file__).resolve().parent
load=lambda p:json.loads(read(p))
sha=lambda b:hashlib.sha256(b).hexdigest()
d=load(P/'discovery.json');requests=load(P/'body-request.json');bodyproof=load(P/'bodies.json')
assert bodyproof['complete'] and bodyproof['all_discovery_inputs_unchanged']
images={side:Path(plan[side+'_build'])/'rook2-exact' for side in ['control','candidate']}
sections={};raw={};symbols={}
for side,image in images.items():
 raw[side]=read(image);assert sha(raw[side])==d['pins'][str(image)]
 sections[side]={}
 for line in read(P/(side+'-sections.stdout')).decode().splitlines():
  m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+',line)
  if m:
   name,kind,addr,offset,size=m.groups();sections[side][name]=dict(kind=kind,address=int(addr,16),offset=int(offset,16),bytes=int(size,16))
 symbols[side]={}
 for line in read(P/(side+'-nm.stdout')).decode().splitlines():
  m=re.match(r'([0-9a-f]+) ([0-9a-f]+) ([tT]) (.+)$',line)
  if m:symbols[side][int(m[1],16)]=dict(bytes=int(m[2],16),name=m[4])
def get(side,address,size):
 s=sections[side]['.text'];assert s['kind']=='PROGBITS' and s['address']<=address and address+size<=s['address']+s['bytes']
 offset=s['offset']+address-s['address'];return raw[side][offset:offset+size]
def resolve(side,instruction):
 m=re.search(r'# ([0-9a-f]+)',instruction)
 if not m:return None
 slot=int(m[1],16)
 rows=[line for line in read(P/(side+'-relocations.stdout')).decode().splitlines() if re.match(r'^0*'+format(slot,'x')+r'\s',line)]
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
  if not matches:continue  # No invented old counterpart for a newly outlined helper.
  assert len(matches)==1
  r=matches[0];address=int(r['start'],16);code=get(side,address,r['bytes'])
  assert symbols[side][address]==dict(bytes=r['bytes'],name=r['actual_symbol'])
  text=read(P/(side+'-'+label+'.stdout')).decode();ins=re.findall(r'^\s*([0-9a-f]+):\s+(.+)$',text,re.M)
  calls=[dict(address=a,operand=i,resolved=resolve(side,i)) for a,i in ins if re.match(r'call\s',i)]
  refs=[dict(address=a,operand=i,resolved=resolve(side,i)) for a,i in ins if '# ' in i and resolve(side,i)]
  pair[side]=dict(address=hex(address),bytes=r['bytes'],machine_sha256=sha(code),stack_reservations=re.findall(r'\bsub\s+rsp,(0x[0-9a-f]+)',text),pushes=sum(bool(re.match(r'push\s',i)) for _,i in ins),call_sites=calls,resolved_RIP_references=refs,instructions=len(ins),AND_instructions=[dict(address=a,operand=i) for a,i in ins if re.match(r'and\s',i)],conditional_branches=[dict(address=a,operand=i) for a,i in ins if re.match(r'j(?!mp)[a-z]+\s',i)])
 functionproof[label]=dict(**pair)
 if set(pair)=={'control','candidate'}:functionproof[label].update(complete_machine_bytes_identical=pair['control']['machine_sha256']==pair['candidate']['machine_sha256'],size_delta=pair['candidate']['bytes']-pair['control']['bytes'])
 else:functionproof[label]['unpaired_actual_owner']=True
sectionproof={name:{side:sections[side][name] for side in ['control','candidate']} for name in ['.text','.rodata','.data.rel.ro']}
assert all(file_sha(p)==h for p,h in d['pins'].items())
result=dict(complete=True,functions=functionproof,sections=sectionproof,all_inputs_unchanged=True,all_capture_children_exit0=all(r['exit_code']==0 for r in d['commands']) and all(r['command']['exit_code']==0 for r in bodyproof['bodies']),complete_function_count=len(requests),raw_complete_function_bytes=bodyproof['total_raw_bytes'],mechanism_verdict='Manual generic51-to56 complete Activity proof required: source-square own/opponent support counts share unconditional packed16bit-lane arithmetic in allfourkind/twocolor actual owners; retain comparison, attackpenalty, knight exemption, relation/R and supplied bytes. Public profile_sum unchanged; packing/extraction/register/frame/code/call costs disclosed. No53zero branch or speed inference.',limits=['No CPU or correctness execution, PGO transfer or whole-binary equality.','At most four requested complete paired Activity/common full bodies and1MiB new disassembly. No standalone publicprofile_sum/packed helper or otherbody capture without new authority; unpaired actual owner never gets an invented counterpart.','Actual unconditional packed lanes/shared arithmetic/extraction must survive source-square penalty for allfourkind/twocolor inline instances in the captured complete Activity owner; no53opponentzero branch. Public profile_sum source unchanged; actual commonfull route required if needed to establish consumer.','Packing/extraction/register lifetime/frame/spills/code/calls/copies remain costs; missing or unexpectedly outlined sharing is explicit scope limit, not a fabricated proof or automatic focused/timing authority.'])
with (P/'analysis.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(complete=True,body_sizes={k:{s:v[s]['bytes'] for s in ['control','candidate'] if s in v} for k,v in functionproof.items()},all_inputs_unchanged=True)))
