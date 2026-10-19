from pathlib import Path
import re,json,struct,collections,hashlib
E=Path(__file__).parent;capture=json.loads((E/'capture.json').read_text());pins=json.loads((E/'input-pins.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(E/n).write_text(json.dumps(d,indent=2)+'\n')
summary={};calls={};tables={};windows={}
for side in ['control','candidate']:
 image=Path(next(p for p in pins if p.endswith('/rook2-exact') and ('pressure-table-traversal-generic-build' in p)==(side=='candidate')))
 b=image.read_bytes();assert b[:6]==b'\x7fELF\x02\x01'
 shoff=struct.unpack_from('<Q',b,40)[0];size,num=struct.unpack_from('<HH',b,58);rel={}
 for i in range(num):
  sec=struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*size)
  if sec[1]==4:
   for off in range(sec[4],sec[4]+sec[5],sec[9]):
    addr,info,addend=struct.unpack_from('<QQq',b,off)
    if info&0xffffffff==8:rel[addr]=addend
 symbols={}
 for line in (E/(side+'/nm.stdout')).read_text().splitlines():
  m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tTrRdDbB] (.*)$',line)
  if m:symbols[int(m[1],16)]=m[3]
 def resolve(c):
  m=re.search(r'# ([0-9a-f]+)',c['instruction'])
  if m and int(m[1],16) in rel:
   addr=rel[int(m[1],16)];return dict(**c,relocated_target=hex(addr),resolved_symbol=symbols.get(addr,'unresolved'))
  return c
 summary[side]=[]
 for f in capture['functions'][side]:
  text=(E/f['assembly']).read_text();ins=[]
  for line in text.splitlines():
   m=re.match(r'^\s*([0-9a-f]+):\s+(.*)',line)
   if m:ins.append((m[1],m[2]))
  row={k:f[k] for k in ['symbol','address','bytes','static_instructions']}
  row.update(entry_rsp_subtractions=f['rsp_adjustments'][:2],static_stack_memory_reference_instructions=len(f['stack_memory_reference_instructions']),call_sites=len(f['calls']),imul_count=len(f['imuls']))
  summary[side].append(row)
  if 'activity::king_pressure' in f['symbol']:
   calls[side]=[resolve(c) for c in f['calls']]
   tables[side]=[resolve({'address':a,'instruction':s}) for a,s in ins if '# ' in s and ('geometry::' in s or 'QWORD PTR [rip' in s)]
   ranges=([(0x1a88b,0x1a89b),(0x1a91f,0x1a974),(0x1a990,0x1a9ef)] if side=='control' else [(0x1a81c,0x1a83d),(0x1a8c9,0x1a8ee),(0x1a97e,0x1a9b5),(0x1aa26,0x1aa87)])
   windows[side]=[[{'address':a,'instruction':s} for a,s in ins if start<=int(a,16)<=end] for start,end in ranges]
  if '::full_impl' in f['symbol']:
   save(side+'-full-activity-call.json',[resolve(c) for c in f['calls'] if resolve(c).get('resolved_symbol')=='rook2::activity::compute'])
for p,h in pins.items():assert sha(Path(p))==h,p
save('function-summary.json',summary);save('resolved-pressure-calls.json',calls);save('table-operands.json',tables);save('traversal-windows.json',windows)
for s,v in calls.items():print(s,collections.Counter(r.get('resolved_symbol','unresolved/direct') for r in v))
for s,v in tables.items():print(s+' tables',json.dumps([x for x in v if 'geometry::' in x.get('resolved_symbol','') or 'geometry::' in x['instruction']]))
for s in ['control','candidate']:
 print(s,'sections',{l.split()[0]:int(l.split()[1]) for l in (E/(s+'/size.stdout')).read_text().splitlines() if l.startswith(('.text ','.rodata '))})
