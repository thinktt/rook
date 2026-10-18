from pathlib import Path
import hashlib,json,re,struct,collections,difflib
C=Path(__file__).parent
load=lambda p:json.loads(p.read_text())
h=lambda x:hashlib.sha256(x).hexdigest()
I=load(C/'inputs.json');F=load(C/'analysis-summary.json')['phase1-to-phase2']
R={'scope':'Bounded static default-Q/ordinary/full emitted body/ABI/referent inspection; no CPU or neutrality claim','artifacts':{},'method':'Captured objdump no-raw-insn plus ELF section/RELATIVE relocation reads; explicit jump-table targets for Q CFG'}
for label in ['phase1','phase2']:
 data=Path(I['artifacts'][label]['binary']).read_bytes();sections=load(C/(label+'-section-hashes.json'))
 def read(addr,n):
  for s in sections.values():
   if s['kind']!='NOBITS' and s['address'] and s['address']<=addr and addr+n<=s['address']+s['size']:return data[s['offset']+addr-s['address']:s['offset']+addr-s['address']+n]
  raise ValueError(hex(addr))
 def loc(addr):
  p,n,line,col=struct.unpack('<QQII',read(addr,24));return {'filename':read(p,n).decode(),'line':line,'column':col}
 symbols={}
 for line in (C/(label+'-nm-demangled.txt')).read_text().splitlines():
  m=re.fullmatch(r'([0-9a-f]+) ([0-9a-f]+) [A-Za-z] (.*)',line)
  if m:symbols[m[3]]=(int(m[1],16),int(m[2],16))
 tables={}
 for name in ['rook2::attacks::MASKS','rook2::geometry::KNIGHT_SOURCES']:
  addr,n=symbols[name];tables[name]={'address':hex(addr),'size':n,'sha256':h(read(addr,n))}
 fullrefs=load(C/(label+'-full_impl-0-references.json'));panic=[loc(x['target_address']) for x in fullrefs if 'anon.' in x['resolved']]
 attackedloc={}
 for occurrence in range(2):
  path=C/(label+'-attacked-'+str(occurrence)+'-references.json')
  if path.exists():attackedloc[str(occurrence)]=[loc(x['target_address']) for x in load(path) if 'anon.' in x['resolved']]
 stats={}
 for name in ['visit_q','visit_ordinary','full_impl','ordered_attackers','attacked','generate_legal','legal_replies_up_to_two','projected_board']:
  matching=[x for x in F['focused_functions'] if x['name'].endswith('::'+name) and x['occurrence']==0]
  if matching:
   f=matching[0][label];calls=load(C/(label+'-'+name+'-0-calls.json'));normalized=(C/(label+'-'+name+'-0-normalized.txt')).read_text().splitlines()
   stats[name]={'address':hex(f['address']),'size':f['size'],'instruction_count':f['instruction_count'],'prologue':f['prologue'],'direct_or_indirect_calls':sum(bool(re.match(r'call\b',x['instruction'])) for x in calls),'stack_operand_instructions':sum('(%rsp' in x or '(%rbp' in x for x in normalized),'note':'Static instructions mentioning stack/frame operands, includes locals/outgoing args/address construction; not a spill count or retired work'}
 R['artifacts'][label]={'binary_sha256':h(data),'tables':tables,'full_impl_panic_locations':panic,'attacked_panic_locations':attackedloc,'functions':stats}
 if label=='phase2':
  chunks=re.split(r'(?m)^([0-9a-f]+) <(.+)>:\n',(C/(label+'-disassembly.txt')).read_text());body=next(chunks[i+2] for i in range(1,len(chunks),3) if '::visit_q' in chunks[i+1]);rows=[]
  for line in body.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s*(.*)',line)
   if m:rows.append((int(m[1],16),m[2]))
  ips={a for a,_ in rows};edges={a:set() for a,_ in rows};switches={0x399dc:(0x8a8c8,8),0x39ab8:(0x8a900,8),0x39e03:(0x8a8e8,6)};jump_tables=[]
  for idx,(addr,text) in enumerate(rows):
   op=text.split()[0];nxt=rows[idx+1][0] if idx+1<len(rows) else None
   if op=='jmp' and '*' in text:
    assert addr in switches,hex(addr);base,n=switches[addr];targets=[base+off for off in struct.unpack('<'+'i'*n,read(base,n*4))];assert set(targets)<=ips;edges[addr].update(targets);jump_tables.append({'instruction':hex(addr),'table':hex(base),'entries':n,'targets':[hex(x) for x in targets]})
   elif op.startswith('j'):
    m=re.match(r'j\w*\s+([0-9a-f]+)',text);assert m,text;target=int(m[1],16)
    if target in ips:edges[addr].add(target)
    if op!='jmp' and nxt:edges[addr].add(nxt)
   elif not (op.startswith('ret') or op in ['ud2','int3']) and nxt:edges[addr].add(nxt)
  def reachable_without(block):
   seen=set();todo=[rows[0][0]]
   while todo:
    ip=todo.pop()
    if ip in seen or ip==block:continue
    seen.add(ip);todo.extend(edges[ip]-seen)
   return seen
  route=0x39ca3;safety=0x39906
  assert route in reachable_without(None) and safety in reachable_without(None)
  dominates=safety not in reachable_without(route);assert dominates
  stores=[0x39c66,0x39c6e,0x39c76,0x39c7e];assert all(safety not in reachable_without(a) for a in stores)
  R['q_cfg']={'instructions':len(rows),'jump_tables':jump_tables,'route_call':hex(route),'own_safety_call':hex(safety),'route_dominates_own_safety':dominates,'four_projected_stores_dominate_own_safety':[hex(a) for a in stores],'limitations':'Whole-function static CFG with all legal switch targets and fallthrough after calls (including panic calls); no runtime path frequencies. Dominance alone does not prove per-iteration freshness; source single-owner ordering and actual stack pointer operands supply that proof.'}
  # Keep whole relevant blocks in one reviewable capture without dependence on symbol spelling.
  windows=[]
  for target in [0x38c0f,0x39906,0x39ca3]:
   idx=next(i for i,(a,_) in enumerate(rows) if a==target);windows.extend([f'{a:x}: {t}' for a,t in rows[max(0,idx-17):idx+18]]);windows.append('')
  (C/'phase2-q-focused-windows.txt').write_text('\n'.join(windows)+'\n')
assert R['artifacts']['phase1']['tables']['rook2::attacks::MASKS']['sha256']==R['artifacts']['phase2']['tables']['rook2::attacks::MASKS']['sha256']
assert R['artifacts']['phase1']['tables']['rook2::geometry::KNIGHT_SOURCES']['sha256']==R['artifacts']['phase2']['tables']['rook2::geometry::KNIGHT_SOURCES']['sha256']
assert R['artifacts']['phase1']['full_impl_panic_locations']==R['artifacts']['phase2']['full_impl_panic_locations']
# Replace only anonymous source-location names after decoding their content above.
a=(C/'phase1-full_impl-0-normalized.txt').read_text();b=(C/'phase2-full_impl-0-normalized.txt').read_text();norm=lambda x:re.sub(r'anon\.[0-9a-f]+\.\d+','SAME_DECODED_PANIC_LOCATION',x)
assert norm(a)==norm(b);R['full_impl_normalized_equal_after_verified_location_roles']=True
# New outlined attacked occurrence differs only panic source location, decoded and retained.
a=(C/'phase2-attacked-0-normalized.txt').read_text();b=(C/'phase2-attacked-1-normalized.txt').read_text();normclone=lambda x:re.sub(r'RIP<anon\.[^>]+>','RIP<DECODED_PANIC_LOCATION>',x)
assert normclone(a)==normclone(b);R['attacked_clone_equal_except_decoded_panic_location']=True
(C/'focused-analysis.json').write_text(json.dumps(R,indent=2)+'\n');print(json.dumps({'pass':True,'q_cfg':R['q_cfg'],'full_impl_panic_locations':R['artifacts']['phase2']['full_impl_panic_locations'],'attacked_panic_locations':R['artifacts']['phase2']['attacked_panic_locations']}))
