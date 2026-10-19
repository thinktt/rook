from pathlib import Path
import re,json,struct,collections,hashlib
E=Path(__file__).parent;capture=json.loads((E/'capture.json').read_text());pins=json.loads((E/'input-pins.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(E/n).write_text(json.dumps(d,indent=2)+'\n')
summary={};windows={};calls={}
for side in ['control','candidate']:
 image=Path(next(p for p in pins if p.endswith('/rook2-exact') and ('activity-mark-byte-generic-build' in p)==(side=='candidate')))
 b=image.read_bytes();assert b[:6]==b'\x7fELF\x02\x01'
 shoff=struct.unpack_from('<Q',b,40)[0];size,num=struct.unpack_from('<HH',b,58)
 rel={}
 for i in range(num):
  sec=struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*size)
  if sec[1]==4:
   for off in range(sec[4],sec[4]+sec[5],sec[9]):
    addr,info,addend=struct.unpack_from('<QQq',b,off)
    if info&0xffffffff==8:rel[addr]=addend
 symbols={}
 for line in (E/(side+'/nm.stdout')).read_text().splitlines():
  m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',line)
  if m:symbols[int(m[1],16)]=m[3]
 summary[side]=[]
 for f in capture['functions'][side]:
  text=(E/f['assembly']).read_text();ins=[]
  for line in text.splitlines():
   m=re.match(r'^\s*([0-9a-f]+):\s+(.*)',line)
   if m:ins.append((m[1],m[2]))
  row={k:f[k] for k in ['symbol','address','bytes','static_instructions']}
  row.update(entry_rsp_subtractions=f['rsp_adjustments'][:2],static_stack_memory_reference_instructions=len(f['stack_memory_reference_instructions']),call_sites=len(f['calls']))
  summary[side].append(row)
  resolved=[]
  for c in f['calls']:
   m=re.search(r'# ([0-9a-f]+)',c['instruction'])
   if m and int(m[1],16) in rel:
    addr=rel[int(m[1],16)];resolved.append(dict(**c,relocated_target=hex(addr),resolved_symbol=symbols.get(addr,'unresolved')))
   else:resolved.append(c)
  if 'activity::compute' in f['symbol']:
   calls[side]=resolved;ws=[]
   for i,(addr,op) in enumerate(ins):
    if re.search(r'\bor\s+BYTE PTR',op):ws.append({'mark_or_address':addr,'instructions':[{'address':a,'instruction':s} for a,s in ins[max(0,i-9):i+2]]})
   windows[side]=ws
  if '::full_impl' in f['symbol']:
   save(side+'-full-activity-call.json',[r for r in resolved if r.get('resolved_symbol')=='rook2::activity::compute'])
 assert sha(image)==pins[str(image)]
assert len(windows['control'])==len(windows['candidate'])==11
assert all(not any(re.search(r'\b(shl|shr)\s+[^,]+,cl$',r['instruction']) for r in w['instructions'][-8:]) for w in windows['candidate'])
for p,h in pins.items():assert sha(Path(p))==h,p
save('function-summary.json',summary);save('mark-windows.json',windows);save('resolved-activity-calls.json',calls)
print('commands',len(capture['commands']),'all0',all(c['exit_code']==0 for c in capture['commands']))
for s,v in calls.items():print(s,collections.Counter(r.get('resolved_symbol','direct king_pressure') for r in v))
for s in ['control','candidate']:print(s+' full activity',(E/(s+'-full-activity-call.json')).read_text())
