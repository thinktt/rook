from pathlib import Path
import re,json,hashlib,struct,shutil,difflib,collections,sys
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/"plan.json").read_text())
OUT=Path(PLAN["codegen"])
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
  stack_rows=[r for r in rows if re.search(r'\b(?:push|pop|sub|add|lea)\w*\b',r['instruction']) and ('%rsp' in r['instruction'] or re.match(r'push|pop',r['instruction']))]
  offsets=[int(m[1],16) for r in rows for m in re.finditer(r'(-?0x[0-9a-f]+)\(%r(?:sp|bp)\)',r['instruction'])]
  subtractions=[int(m[1],16) for r in rows if (m:=re.match(r'sub\w* \$0x([0-9a-f]+),%rsp',r['instruction']))]
  stack_evidence=dict(adjustments=stack_rows,max_immediate_rsp_sub=max(subtractions,default=0),min_stack_displacement=min(offsets,default=0),max_stack_displacement=max(offsets,default=0),note='Static instruction evidence; not a computed recursive peak or exact frame size')
  item=dict(item,bytes_sha256=sha(read(addr,size)),normalized_sha256=sha('\n'.join(x['instruction'] for x in rows).encode()),instruction_count=len(rows),prologue=[x['raw_display'] for x in rows[:10]])
  key=(item['name'],item['occurrence']);functions[key]=item
  if any(s in item['name'] for s in ['rook2::evaluator::','rook2::ordinary::','rook2::quiescence::','rook2::endgame::finish','rook2::pawn_structure::PawnCache::select','rook2::pawn_progress::structure_weighted','rook2::evaluation::RootContext::square_balance_from']):
   stem=item['name'].split('::')[-1]+'-'+str(item['occurrence']);(OUT/(label+'-'+stem+'-normalized.txt')).write_text('\n'.join(x['instruction'] for x in rows)+'\n');(OUT/(label+'-'+stem+'-references.json')).write_text(json.dumps(refs,indent=2)+'\n');(OUT/(label+'-'+stem+'-calls.json')).write_text(json.dumps(calls,indent=2)+'\n')
  item['calls']=calls
  item['stack_evidence']=stack_evidence
  item['noncall_references']=[r for r in refs if not any(c['address']==r['instruction'] for c in calls)]
 DATA[label]={'functions':functions,'sections':sections}
 focus_records=[]
 for key,fn in functions.items():
  if any(token in fn['name'] for token in ['rook2::evaluator::','rook2::quiescence::','rook2::ordinary::']):
   record=dict(fn)
   record['q_transfers']=[c for c in fn['calls'] if 'visit_q' in c['instruction'] or (c.get('reference') and 'visit_q' in c['reference'].get('resolved',''))]
   record['allocation_transfers']=[c for c in fn['calls'] if re.search(r'__rust_(?:alloc|realloc)|RawVec|raw_vec|malloc|realloc|Vec.*(?:grow|reserve)',c['instruction'])]
   focus_records.append(record)
 (OUT/(label+'-focused-transfers-frames.json')).write_text(json.dumps(focus_records,indent=2)+'\n')
A=DATA['control731']['functions'];B=DATA['combined95']['functions'];pairs=[]
for key in sorted(set(A)&set(B)):
 x,y=A[key],B[key];pairs.append({'name':key[0],'occurrence':key[1],'control731':x,'combined95':y,'bytes_equal':x['bytes_sha256']==y['bytes_sha256'],'normalized_equal':x['normalized_sha256']==y['normalized_sha256'],'address_equal':x['address']==y['address'],'size_equal':x['size']==y['size']})
(OUT/'function-comparison.json').write_text(json.dumps(pairs,indent=2)+'\n')
focus=[x for x in pairs if any(s in x['name'] for s in ['rook2::evaluator::','rook2::ordinary::','rook2::quiescence::'])]
summary={'matched_functions':len(pairs),'control731_functions':len(A),'combined95_functions':len(B),'exact_byte_matches':sum(x['bytes_equal'] for x in pairs),'normalized_matches':sum(x['normalized_equal'] for x in pairs),'same_size':sum(x['size_equal'] for x in pairs),'same_address':sum(x['address_equal'] for x in pairs),'new_functions':[B[k] for k in sorted(set(B)-set(A))],'removed_functions':[A[k] for k in sorted(set(A)-set(B))],'focused_functions':focus,'tool_executable_sha256':{t:{'path':str(Path(shutil.which(t)).resolve()),'sha256':sha(Path(shutil.which(t)).read_bytes())} for t in ['nm','size','objdump','readelf','python3']},'normalization':'Strip displayed instruction addresses/comments and numeric LLVM module suffixes. Replace annotated RIP displacement by symbolic referent; GOT references resolve file pointers through RELATIVE relocation addends to native function symbols. Replace direct branch absolute addresses by symbolic targets, retaining within-function offsets. Non-RIP operands/registers/immediates/order remain. Equal normalized operands do not prove equal non-code data referents; focused refs are retained for separate inspection.'}
(OUT/'analysis-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for name in ['full_impl','visit_ordinary','visit_q','ordering_phase','store_ordinary']:
 a=OUT/('control731-'+name+'-0-normalized.txt');b=OUT/('combined95-'+name+'-0-normalized.txt')
 if a.exists() and b.exists():(OUT/(name+'-normalized.diff')).write_text(''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),fromfile=a.name,tofile=b.name)))
print(json.dumps({k:v for k,v in summary.items() if k not in ['focused_functions','tool_executable_sha256','normalization','new_functions','removed_functions']},indent=2))
print('new',[(x['name'],x['size'],hex(x['address'])) for x in summary['new_functions']])
print('focus',[(x['name'],x['control731']['size'],x['combined95']['size'],x['normalized_equal']) for x in focus])

focus_tokens=['rook2::evaluator::','rook2::quiescence::','rook2::ordinary::']
focused=lambda fs:{key:fn for key,fn in fs.items() if any(t in fn['name'] for t in focus_tokens)}
left,right=focused(A),focused(B)
changes=[]
for key in sorted(set(left)|set(right)):
 x,y=left.get(key),right.get(key)
 flags=[]
 if x is None:flags.append('new-focused-function-or-monomorph')
 elif y is None:flags.append('removed-or-inlined-focused-function')
 else:
  if y['size']>x['size']:flags.append('code-size-expansion')
  if y['stack_evidence']['max_immediate_rsp_sub']>x['stack_evidence']['max_immediate_rsp_sub']:flags.append('larger-rsp-adjustment')
  if y['stack_evidence']['max_stack_displacement']>x['stack_evidence']['max_stack_displacement']:flags.append('larger-stack-reference')
  if len(y['calls'])>len(x['calls']):flags.append('more-call-or-tail-transfer-sites')
  if y['normalized_sha256']!=x['normalized_sha256']:flags.append('instruction-or-operand-shape-changed')
 if flags:changes.append(dict(name=key[0],occurrence=key[1],flags=flags,control731=x,combined95=y))
review=dict(status='pending-parent-manual-codegen-review',automatic_acceptance=False,focused_changes=changes,
 relevant_recursive_symbols={label:[dict(name=f['name'],occurrence=f['occurrence'],address=f['address'],size=f['size'],calls=f['calls'],stack_evidence=f['stack_evidence']) for f in data['functions'].values() if 'visit_q' in f['name']] for label,data in DATA.items()},
 scope='Actual production NoTrace transfers, instruction operands, prologue/stack evidence, full/fast and inline selection scope; absent observer symbols alone is insufficient',
 limits='Occurrence matching can shift for monomorphs; inspect all listed recursive bodies, actual transfers and full/fast operands manually. RSP evidence is not recursive peak. Normalized equality needs referenced-data review.',
 next_action='Report any material expansion/frame/call/observer issue before source fixes or strict replay/wire; no automatic strict run')
(OUT/'manual-gate.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(dict(manual_gate=review['status'],focused_change_count=len(changes))))
