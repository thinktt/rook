#!/usr/bin/env python3
"""Mechanical complete-fragment facts only; never a native/timing admission."""
from pathlib import Path
import json,re,hashlib
from capture import setup,read,sha,save,captured_text_bytes
P=Path(__file__).resolve().parent
plan=setup('analyze');d=json.loads(read(P/'discovery.json'));b=json.loads(read(P/'bodies.json'))
assert b['complete'] and b['all_discovery_inputs_unchanged']
request=json.loads(read(P/'body-request.json'));assert sha(P/'body-request.json')==b['body_request_sha256']
raw={};sections={};all_symbols={};relocations={}
for side in ['control','candidate']:
 image=Path(plan[side+'_build'])/'rook2-exact';raw[side]=read(image);assert hashlib.sha256(raw[side]).hexdigest()==plan[side+'_image_sha256']
 sections[side]=[]
 for line in read(P/(side+'-sections.stdout')).decode().splitlines():
  m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+(\S+)',line)
  if m:
   name,kind,address,offset,size,entsize,flags=m.groups()
   sections[side].append(dict(name=name,kind=kind,address=int(address,16),offset=int(offset,16),bytes=int(size,16),flags=flags))
 all_symbols[side]={}
 for line in read(P/(side+'-nm.stdout')).decode().splitlines():
  f=line.split(maxsplit=3)
  if len(f)==4 and f[2] in ['t','T']:all_symbols[side].setdefault(int(f[0],16),[]).append(dict(bytes=int(f[1],16),name=f[3]))
 relocations[side]=read(P/(side+'-relocations.stdout')).decode().splitlines()
def owning(side,address):
 return [dict(role=r['role'],label=r['label']) for r in request if r['side']==side and int(r['start'],16)<=address<int(r['start'],16)+r['bytes']]
def resolve(side,operand):
 m=re.search(r'# ([0-9a-f]+)',operand)
 if not m:return None
 slot=int(m[1],16);lines=[x for x in relocations[side] if re.match(r'^0*'+format(slot,'x')+r'\s',x)]
 if len(lines)!=1:return dict(slot=hex(slot),resolved=False)
 line=lines[0];result=dict(slot=hex(slot),raw_relocation=line)
 if 'R_X86_64_JUMP_SLOT' in line or 'R_X86_64_GLOB_DAT' in line:
  result['dynamic_symbol']=line.split()[4]
 if 'R_X86_64_RELATIVE' in line:
  address=int(line.split()[-1],16);result.update(address=hex(address),symbols=all_symbols[side].get(address,[]),captured_owner=owning(side,address))
 return result
facts=[]
for r in request:
 side=r['side'];start=int(r['start'],16);end=start+r['bytes']
 matches=[s for s in sections[side] if s['kind']=='PROGBITS' and 'A' in s['flags'] and 'X' in s['flags'] and 'W' not in s['flags'] and s['address']<=start and end<=s['address']+s['bytes']]
 assert len(matches)==1,'fragment not wholly contained in unique allocated readonly executable PROGBITS'
 section=matches[0];offset=section['offset']+start-section['address'];code=raw[side][offset:offset+r['bytes']];assert len(code)==r['bytes']
 text=read(P/(side+'-'+r['label']+'.stdout')).decode();ins=re.findall(r'^\s*([0-9a-f]+):\s+(.+)$',text,re.M)
 assert ins and int(ins[0][0],16)==start and all(start<=int(a,16)<end for a,op in ins),'instruction range mismatch'
 calls=[];edges=[];mnemonics=set()
 for index,(address,operand) in enumerate(ins):
  op=operand.split()[0];mnemonics.add(op)
  if op=='call':calls.append(dict(address=address,operand=operand,RIP_resolution=resolve(side,operand)))
  if op.startswith('j') or op=='call':
   m=re.match(r'(?:j[a-z]+|call)\s+([0-9a-f]+)(?:\s|$)',operand);target=int(m[1],16) if m else None
   owners=[] if target is None else owning(side,target)
   fallthrough=(int(ins[index+1][0],16) if index+1<len(ins) else end) if op!='jmp' else None
   edges.append(dict(address=address,operand=operand,target=None if target is None else hex(target),captured_target=owners,cross_fragment=bool(owners and any(x['label']!=r['label'] for x in owners)),unresolved_indirect=target is None,fallthrough=None if fallthrough is None else hex(fallthrough)))
 facts.append(dict(side=side,role=r['role'],label=r['label'],fragment_kind=r['fragment_kind'],actual_symbol=r['display_name'],actual_mangled_symbol=r['actual_mangled_symbol'],address=hex(start),end_exclusive=hex(end),bytes=r['bytes'],machine_sha256=hashlib.sha256(code).hexdigest(),output_section=section['name'],instructions=len(ins),stack_reservations=re.findall(r'\bsub\s+rsp,(0x[0-9a-f]+)',text),pushes=sum(bool(re.match(r'push\s',op)) for a,op in ins),stack_reference_instruction_count=sum(bool(re.search(r'\[(?:rsp|rbp)',op)) for a,op in ins),mnemonics=sorted(mnemonics),calls=calls,register_mediated_call_rows=[dict(address=a,operand=op) for a,op in ins if re.fullmatch(r'call\s+(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[89]|1[0-5]))',op)],source_paths=sorted(set(re.findall(r'^(/[^:\n]+):\d+',text,re.M)))))
owners={}
for role in sorted({x['role'] for x in request}):
 owners[role]={}
 for side in ['control','candidate']:
  fs=[x for x in facts if x['side']==side and x['role']==role]
  if not fs:owners[role][side]=None;continue
  owners[role][side]=dict(combined_machine_bytes=sum(x['bytes'] for x in fs),fragment_labels=[x['label'] for x in fs],cold_fragment_count=sum(x['fragment_kind']=='cold' for x in fs),hot_stack_reservations=[x['stack_reservations'] for x in fs if x['fragment_kind']=='hot'],combined_calls=sum(len(x['calls']) for x in fs),combined_instruction_rows=sum(x['instructions'] for x in fs))
 owners[role]['combined_size_delta']=owners[role]['candidate']['combined_machine_bytes']-owners[role]['control']['combined_machine_bytes'] if owners[role]['candidate'] and owners[role]['control'] else None
assert all(sha(path)==value for path,value in d['pins'].items())
result=dict(complete=True,owners=owners,fragments=facts,sections=sections,all_inputs_unchanged=True,all_actual_child_codes_zero=all(x['exit_code']==0 for x in d['commands']) and all(x['command']['exit_code']==0 for x in b['bodies']),complete_fragments=len(request),total_captured_text_bytes=captured_text_bytes(),manual_mechanism_review_required=True,execution_authorized=False,limits=['NAME suffixes are profile attribution, not physical clones; exact symbol/source/call-role confirmation remains manual.','Complete hot and all recognized .cold suffix fragments required; unsupported/unsized/unmapped fragments stop instead of broader capture.','A final merged .text is allowed; actual linked fragment addresses and cross-fragment transfers matter.','Fragment stack/code/call/opcode facts are static; no summed frame or CPU claim. Register-mediated calls are unresolved here: manual actual definition/use proof is required, never label them callbacks or memcpy from totals alone.'])
result['all_discovery_and_body_codes_zero']=result['all_actual_child_codes_zero']
result['all_actual_child_codes_zero']=False
result['original_analysis_exit_code']=1
result['original_analysis_json_complete']=False
result['offline_postmortem']='Compact independent facts from unchanged complete raw bodies; original gate failed metadata file-size cap. Full static edges remain in raw bodies; no captures or clocks retried/reset.'
save(P/'analysis-compact.json',result)
print(json.dumps(dict(complete=True,owners=owners,fragments=len(request),all_inputs_unchanged=True)))
