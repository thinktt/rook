#!/usr/bin/env python3
"""Resolve actual ELF call slots and compare relocation-normalized unchanged owners."""
import difflib,json,re,struct,subprocess
from pathlib import Path
B=Path('/home/legolas/rook2-experiments/compact48-tt-20261020-01')
r=json.loads((B/'capture/receipt.json').read_text())
result={}; normalized={}
for label,im in r['images'].items():
 data=Path(im['path']).read_bytes();assert data[:6]==b'\x7fELF\x02\x01'
 phoff=struct.unpack_from('<Q',data,32)[0]; phsize,phnum=struct.unpack_from('<HH',data,54)
 loads=[]
 for i in range(phnum):
  h=struct.unpack_from('<IIQQQQQQ',data,phoff+i*phsize)
  if h[0]==1:loads.append((h[3],h[3]+h[5],h[2]))
 def at(addr):
  for start,end,off in loads:
   if start<=addr and addr+8<=end:return struct.unpack_from('<Q',data,off+addr-start)[0]
  raise ValueError(hex(addr))
 relocs=B/'capture'/label/'relocations.txt'
 if not relocs.exists():
  with relocs.open('xb') as f: subprocess.run(['/usr/bin/readelf','-rW',im['path']],stdout=f,check=True,timeout=60)
 external={}
 for l in relocs.read_text().splitlines():
  m=re.match(r'([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_(?:GLOB_DAT|JUMP_SLOT)\s+[0-9a-f]+\s+(\S+)',l.strip())
  if m:external[int(m[1],16)]=m[2]
 names={}
 for l in (B/'capture'/label/'nm.txt').read_text().splitlines():
  m=re.fullmatch(r'([0-9a-f]+) ([0-9a-f]+) ([A-Za-z]) (.+)',l)
  if m:names[int(m[1],16)]=m[4]
 full=(B/'capture'/label/'full.disassembly').read_text().splitlines()
 calls=[]; owner='';allcalls=[]
 for line in full:
  m=re.match(r'^[0-9a-f]+ <(.+)>:',line)
  if m:owner=m[1]
  m=re.match(r'^\s+([0-9a-f]+):\s+call\s+(.*)',line)
  if not m:continue
  arg=m[2];slot=None;target=None
  if 'QWORD PTR [rip' in arg:
   slot=int(re.search(r'# ([0-9a-f]+)',arg)[1],16);target=at(slot)
  elif re.match(r'[0-9a-f]+ <',arg):target=int(arg.split()[0],16)
  name=external.get(slot,names.get(target,hex(target) if target is not None else arg))
  row=dict(caller=owner,address=m[1],slot=hex(slot) if slot else None,target=name)
  allcalls.append(row)
  if any(x['name']==owner for x in im['selected_owners']):calls.append(row)
 (B/'capture'/label/'resolved-calls.json').write_text(json.dumps(calls,indent=2)+'\n')
 consumers=[x for x in allcalls if 'rook2::remembered::' in x['target'] or 'ensure_table' in x['target']]
 result[label]={'tt_consumers':consumers,'selected_calls':calls}
 norms={}
 for sym in im['selected_owners']:
  norm=[]
  for line in Path(sym['capture']).read_text().splitlines():
   m=re.match(r'^\s+([0-9a-f]+):\s+(.*)',line)
   if not m or int(m[1],16)>=sym['address']+sym['size']:continue
   inst=m[2]
   if 'call'==inst.split()[0]:
    found=next(x for x in allcalls if x['address']==m[1]);inst='call '+found['target']
   else:
    inst=re.sub(r'\[rip[+-]0x[0-9a-f]+\]','[rip]',inst)
    inst=re.sub(r'(?<=# )[0-9a-f]+ ','',inst)
    inst=re.sub(r'^(j\w+)\s+[0-9a-f]+ <',r'\1 <',inst)
   norm.append(re.sub(r'\s+',' ',inst).strip())
  norms[sym['name']]=norm
 normalized[label]=norms
for name,a in normalized['control'].items():
 b=normalized['candidate'].get(name,[])
 if a!=b:
  dif=list(difflib.unified_diff(a,b,fromfile='control',tofile='candidate',n=2))
  file=B/'capture'/('comparison-'+re.sub(r'[^A-Za-z0-9]+','-',name)+'.diff')
  file.write_text('\n'.join(dif)+'\n')
result['instruction_shape_equal_owners']=[n for n in normalized['control'] if [x.split(' #')[0] for x in normalized['control'][n]] == [x.split(' #')[0] for x in normalized['candidate'].get(n,[])]]
result['normalization_scope']='Bounded nm size; exact instruction text after resolving call slots and replacing RIP relocations/branch absolute addresses. Not a binary-identity proof.'
result['normalized_equal_owners']=[n for n in normalized['control'] if normalized['control'][n]==normalized['candidate'].get(n,[])]
(B/'capture/call-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'consumers':{k:v['tt_consumers'] for k,v in result.items() if k in ('control','candidate')},'equal':result['normalized_equal_owners'],'instruction_shape_equal':result['instruction_shape_equal_owners']},indent=2))
