"""Offline whole-body summary and independent256-byte ELF/radix proof."""
from pathlib import Path
import re,json,struct,hashlib,os
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
d=json.loads((P/'discovery.json').read_text());assert all(sha(p)==h for p,h in d['input_pins'].items())
sym=[]
for l in (P/'candidate-nm.stdout').read_text().splitlines():
 m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) ([rR]) (.*)$',l)
 if m and m[4]=='rook2::shelter::RING_BASE_VALUE':sym.append(m)
assert len(sym)==1;address,size=int(sym[0][1],16),int(sym[0][2],16);assert size==256
image=E/'shelter-ring-value-static-generic-build-20261019-01/rook2-exact';b=image.read_bytes();assert b[:6]==b'\x7fELF\x02\x01'
shoff=struct.unpack_from('<Q',b,0x28)[0];entsize,num,strings=struct.unpack_from('<HHH',b,0x3a);sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*entsize) for i in range(num)];names=b[sections[strings][4]:sections[strings][4]+sections[strings][5]]
found=[s for s in sections if s[1]==1 and s[2]&2 and s[3]<=address and address+size<=s[3]+s[5]]
assert len(found)==1;s=found[0];assert not(s[2]&1)
sectionname=names[s[0]:].split(b'\0',1)[0].decode();offset=s[4]+address-s[3];payload=b[offset:offset+256]
expected=[]
for code in range(256):
 weak=code%2;queen=(code//2)%2;rook=(code//4)%4;minor=(code//16)%4;pawn=code//64
 expected.append((14*(rook%2)+24*(rook//2)+8*int(minor>0)) if queen==0 else ((48 if pawn+weak>0 else 20)+18*int(rook+minor>0)))
assert payload==bytes(expected)
with (P/'emitted-ring-base-256.bin').open('xb') as f:f.write(payload)
proof={'complete':True,'symbol':'rook2::shelter::RING_BASE_VALUE','address':hex(address),'bytes':size,'section':sectionname,'section_flags':s[2],'read_only_allocated_section':True,'file_offset':offset,'payload_sha256':hashlib.sha256(payload).hexdigest(),'all256_independent_division_radix_reference_equal':True,'minimum':min(expected),'maximum':max(expected),'no_global_uniqueness_claim':True}
with (P/'payload-proof.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
summary=[]
for body in json.loads((P/'bodies.json').read_text())['whole_bodies']:
 side=body['side'];t=(P/body['stdout']).read_text();lines=t.splitlines();instructions=[l for l in lines if re.match(r'^\s*[0-9a-f]+:\s',l)]
 relocs={};symbols={}
 for line in (P/(side+'-nm.stdout')).read_text().splitlines():
  m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [A-Za-z] (.*)$',line)
  if m:symbols[int(m[1],16)]=m[3]
 for line in (P/(side+'-relocations.stdout')).read_text().splitlines():
  fields=line.split()
  if len(fields)>3:
   try:place=int(fields[0],16)
   except ValueError:continue
   if fields[2]=='R_X86_64_RELATIVE':
    target=int(fields[3],16);relocs[place]={'address':hex(target),'symbol':symbols.get(target)}
   else:relocs[place]={'external':line.strip()}
 calls=[]
 for line in instructions:
  if re.search(r'\bcall\b',line):
   m=re.search(r'# ([0-9a-f]+)',line);calls.append({'instruction':line.strip(),'relocation':relocs.get(int(m[1],16)) if m else None})
 frames=[l.strip() for l in instructions if re.search(r'\b(?:sub|add)\s+rsp,',l)]
 references=[i+1 for i,l in enumerate(lines) if 'RING_BASE_VALUE' in l]
 summary.append({**body,'static_instruction_rows':len(instructions),'frames':frames,'calls':calls,'table_reference_physical_rows':references})
assert all(sha(p)==h for p,h in d['input_pins'].items())
with (P/'body-summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps({'payload':proof,'bodies':[{'side':r['side'],'symbol':r['symbol'],'bytes':r['bytes'],'frames':r['frames'],'calls':r['calls'],'table_reference_rows':r['table_reference_physical_rows']} for r in summary]},indent=2))
