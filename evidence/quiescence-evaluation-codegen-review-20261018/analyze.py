from pathlib import Path
import re,json,hashlib,struct,shutil,difflib,collections
OUT=Path(__file__).parent
INPUT=json.loads((OUT/'inputs.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda s:re.sub(r'\.llvm\.\d+','',s)
DATA={}
for label,artifact in INPUT['artifacts'].items():
 binary=Path(artifact['binary']).read_bytes();sections={}
 for line in (OUT/(label+'-sections.txt')).read_text().splitlines():
  m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)',line)
  if m:
   name,kind,addr,off,n=m.groups();addr,off,n=map(lambda x:int(x,16),(addr,off,n));sections[name]={'kind':kind,'address':addr,'offset':off,'size':n,'sha256':sha(binary[off:off+n]) if kind!='NOBITS' else None}
 (OUT/(label+'-section-hashes.json')).write_text(json.dumps(sections,indent=2)+'\n')
 relas={};s=sections['.rela.dyn']
 for off in range(s['offset'],s['offset']+s['size'],24):
  addr,info,addend=struct.unpack_from('<QQq',binary,off);relas[addr]={'type':info&0xffffffff,'symbol':info>>32,'addend':addend}
 syms=[];counts={}
 for line in (OUT/(label+'-nm-demangled.txt')).read_text().splitlines():
  m=re.match(r'([0-9a-f]+) ([0-9a-f]+) ([tT]) (.*)',line)
  if m:
   addr,size=int(m[1],16),int(m[2],16);name=canon(m[4]);occ=counts.get(name,0);counts[name]=occ+1
   syms.append({'address':addr,'size':size,'name':name,'occurrence':occ})
 def read(addr,n):
  for s in sections.values():
   if s['kind']!='NOBITS' and s['address']<=addr and addr+n<=s['address']+s['size'] and s['address']!=0:
    off=s['offset']+addr-s['address'];return binary[off:off+n]
  return b''
 def resolve(addr):
  found=[x['name'] for x in syms if x['address']==addr]
  if found:return sorted(found)[0]
  found=[x['name']+'+'+hex(addr-x['address']) for x in syms if x['address']<addr<x['address']+x['size']]
  return sorted(found)[0] if found else None
 chunks=re.split(r'(?m)^([0-9a-f]+) <(.+)>:\n',(OUT/(label+'-disassembly.txt')).read_text());bodies={int(chunks[i],16):chunks[i+2] for i in range(1,len(chunks),3)}
 functions={}
 for item in syms:
  addr,size=item['address'],item['size'];body=bodies.get(addr,'');rows=[];calls=[];refs=[]
  for line in body.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s*(.*)',line)
   if not m or int(m[1],16)>=addr+size:continue
   ip=int(m[1],16);ins=canon(m[2]);parts=ins.split('#',1);operand=parts[0];ref=None
   if len(parts)==2 and '(%rip)' in operand:
    target=re.search(r'([0-9a-f]+) <(.*)>',parts[1])
    if target:
     target_addr=int(target[1],16);name=target[2];s=sections['.got'];in_got=s['address']<=target_addr<s['address']+s['size'];ref={'instruction':ip,'target_address':target_addr,'displayed_target':name,'got':in_got}
     if in_got:
      raw=read(target_addr,8);value=struct.unpack('<Q',raw)[0] if raw else 0;rela=relas.get(target_addr)
      if rela and rela['type']==8:value=rela['addend']
      name=resolve(value) or ('unresolved-GOT:'+name);ref.update({'resolved':name,'relocation':rela,'file_pointer':struct.unpack('<Q',raw)[0] if raw else None,'code_target':value})
     else:
      window=read(target_addr,32);ref.update({'resolved':name,'window32_hex':window.hex(),'window32_sha256':sha(window)})
     operand=re.sub(r'-?0x[0-9a-f]+\(%rip\)',lambda _: 'RIP<'+name+'>',operand)
   operand=re.sub(r'\b[0-9a-f]+ <(.*)>',r'TARGET<\1>',operand);operand=' '.join(operand.split());rows.append({'address':ip,'offset':ip-addr,'instruction':operand,'raw_display':line.strip()})
   if ref:refs.append(ref)
   if re.match(r'call|jmp',operand):calls.append({'address':ip,'offset':ip-addr,'instruction':operand,'reference':ref})
  item=dict(item,bytes_sha256=sha(read(addr,size)),normalized_sha256=sha('\n'.join(x['instruction'] for x in rows).encode()),instruction_count=len(rows),prologue=[x['raw_display'] for x in rows[:10]])
  key=(item['name'],item['occurrence']);functions[key]=item
  if any(s in item['name'] for s in ['rook2::evaluator::','rook2::ordinary::','rook2::quiescence::','rook2::endgame::finish','rook2::pawn_structure::PawnCache::select','rook2::pawn_progress::structure_weighted','rook2::evaluation::RootContext::square_balance_from']):
   stem=item['name'].split('::')[-1]+'-'+str(item['occurrence']);(OUT/(label+'-'+stem+'-normalized.txt')).write_text('\n'.join(x['instruction'] for x in rows)+'\n');(OUT/(label+'-'+stem+'-references.json')).write_text(json.dumps(refs,indent=2)+'\n');(OUT/(label+'-'+stem+'-calls.json')).write_text(json.dumps(calls,indent=2)+'\n')
  item['noncall_references']=[r for r in refs if not any(c['address']==r['instruction'] for c in calls)]
 DATA[label]={'functions':functions,'sections':sections}
A=DATA['retained82']['functions'];B=DATA['qnative']['functions'];pairs=[]
for key in sorted(set(A)&set(B)):
 x,y=A[key],B[key];pairs.append({'name':key[0],'occurrence':key[1],'retained82':x,'qnative':y,'bytes_equal':x['bytes_sha256']==y['bytes_sha256'],'normalized_equal':x['normalized_sha256']==y['normalized_sha256'],'address_equal':x['address']==y['address'],'size_equal':x['size']==y['size']})
(OUT/'function-comparison.json').write_text(json.dumps(pairs,indent=2)+'\n')
focus=[x for x in pairs if any(s in x['name'] for s in ['rook2::evaluator::','rook2::ordinary::','rook2::quiescence::'])]
summary={'matched_functions':len(pairs),'retained82_functions':len(A),'qnative_functions':len(B),'exact_byte_matches':sum(x['bytes_equal'] for x in pairs),'normalized_matches':sum(x['normalized_equal'] for x in pairs),'same_size':sum(x['size_equal'] for x in pairs),'same_address':sum(x['address_equal'] for x in pairs),'new_functions':[B[k] for k in sorted(set(B)-set(A))],'removed_functions':[A[k] for k in sorted(set(A)-set(B))],'focused_functions':focus,'tool_executable_sha256':{t:{'path':str(Path(shutil.which(t)).resolve()),'sha256':sha(Path(shutil.which(t)).read_bytes())} for t in ['nm','size','objdump','readelf','python3']},'normalization':'Strip displayed instruction addresses/comments and numeric LLVM module suffixes. Replace annotated RIP displacement by symbolic referent; GOT references resolve file pointers through RELATIVE relocation addends to native function symbols. Replace direct branch absolute addresses by symbolic targets, retaining within-function offsets. Non-RIP operands/registers/immediates/order remain. Equal normalized operands do not prove equal non-code data referents; focused refs are retained for separate inspection.'}
(OUT/'analysis-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for name in ['full_impl','visit_ordinary','visit_q','ordering_phase','store_ordinary']:
 a=OUT/('retained82-'+name+'-0-normalized.txt');b=OUT/('qnative-'+name+'-0-normalized.txt')
 if a.exists() and b.exists():(OUT/(name+'-normalized.diff')).write_text(''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),fromfile=a.name,tofile=b.name)))
print(json.dumps({k:v for k,v in summary.items() if k not in ['focused_functions','tool_executable_sha256','normalization','new_functions','removed_functions']},indent=2))
print('new',[(x['name'],x['size'],hex(x['address'])) for x in summary['new_functions']])
print('focus',[(x['name'],x['retained82']['size'],x['qnative']['size'],x['normalized_equal']) for x in focus])
