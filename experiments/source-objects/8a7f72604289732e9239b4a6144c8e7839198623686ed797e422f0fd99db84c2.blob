"""Offline bounded emitted-owner analysis; no native image execution."""
from pathlib import Path
import re,json,hashlib
E=Path(__file__).resolve().parent
load=lambda n:json.loads((E/n).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=load('discovery.json');assert all(sha(p)==h for p,h in d['input_pins'].items())
all_symbols={};all_relocs={};names={}
for side in ('control','candidate'):
    rows={}
    for line in (E/(side+'-nm.stdout')).read_text().splitlines():
        match=re.match(r'^([0-9a-f]+) ([0-9a-f]+) (\w) (.*)$',line)
        if match:
            addr=int(match[1],16);rows.setdefault(addr,[]).append({'address':addr,'bytes':int(match[2],16),'type':match[3],'symbol':match[4]})
    all_symbols[side]=rows
    mangled={}
    for line in (E/(side+'-nm-mangled.stdout')).read_text().splitlines():
        match=re.match(r'^([0-9a-f]+) ([0-9a-f]+) (\w) (.*)$',line)
        if match:mangled.setdefault(int(match[1],16),[]).append(match[4])
    names[side]=mangled
    all_relocs[side]={int(m[1],16):int(m[2],16) for line in (E/(side+'-relocations.stdout')).read_text().splitlines() if (m:=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)\s*$',line))}
results=[]
for body in load('bodies.json')['bodies']:
    side=body['side'];text=(E/body['stdout']).read_text();instructions=[];calls=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(.+)',line)
        if not m:continue
        addr=int(m[1],16);asm=m[2];instructions.append((addr,asm))
        if not asm.startswith('call '):continue
        target=None;slot=None
        if asm.startswith('call   QWORD PTR'):
            slot_match=re.search(r'# ([0-9a-f]+)',asm)
            if slot_match:slot=int(slot_match[1],16);target=all_relocs[side].get(slot)
        else:
            direct=re.match(r'call\s+([0-9a-f]+)',asm)
            if direct:target=int(direct[1],16)
        symbols=all_symbols[side].get(target,[]) if target is not None else []
        calls.append({'address':addr,'assembly':asm,'got_slot':slot,'target':target,'resolved_symbols':symbols})
    frame=next((int(m[1],16) for _,asm in instructions[:12] if (m:=re.match(r'sub\s+rsp,0x([0-9a-f]+)',asm))),None)
    results.append(body|{'mangled_symbols':names[side].get(body['address'],[]),'local_stack_reservation':frame,'static_instruction_rows':len(instructions),'calls':calls,'raw_sha256':sha(E/body['stdout'])})
selected=load('caller-selection.json');caller_capture=load('caller-capture.json')
for command in caller_capture['commands']:
    assert command['exit_code']==0 and sha(E/command['stdout'])==command['stdout_sha256']
    if '-entry.' not in command['stdout']:
        # Recorded target must appear as an actual decoded direct call in the bounded window.
        side=command['stdout'].split('-')[0]
        owner=next(o for s in selected if s['side']==side for o in s['owners'] if o['address']==command['owner_address'])
        target=owner['target'];text=(E/command['stdout']).read_text()
        assert re.search(r'call\s+'+format(target,'x')+r'\s+<rook2::evaluator::Evaluator<_>::full_impl>',text)
activity=[r for r in results if 'rook2::activity::' in r['symbol']]
for body in activity:
    assert all(call['resolved_symbols'] for call in body['calls'])
    assert all(any('king_pressure' in s['symbol'] or 'panicking' in s['symbol'] or 'slice_end_index_len_fail' in s['symbol'] for s in call['resolved_symbols']) for call in body['calls'])
# Function identity is actual entry + mangled linkage + relocation target, not demangled-name pairing alone.
full_handoffs=[]
for r in results:
    if 'full_impl' not in r['symbol']:continue
    matching=[c for c in r['calls'] if c['target']==0x18850]
    assert len(matching)==1
    full_handoffs.append({'side':r['side'],'full_symbol_address':r['address'],'full_mangled':r['mangled_symbols'],'activity_call':matching[0]})
sections={}
for side in ('control','candidate'):
    sections[side]={m[1]:int(m[2]) for line in (E/(side+'-size.stdout')).read_text().splitlines() if (m:=re.match(r'^(\.\S+)\s+(\d+)\s+\d+\s*$',line))}
summary={'complete':True,'all_inputs_unchanged':True,'bodies':results,'actual_full_to_activity_handoffs':full_handoffs,'caller_scope':selected,'sections':sections,'capture_accounting':{'complete_symbols':4,'additional_partial_caller_symbols':6,'unique_symbols':10,'raw_disassembly_bytes':caller_capture['total_raw_disassembly_bytes'],'cap_bytes':1048576},'binutils_exit_codes':[c['exit_code'] for c in d['commands']+load('bodies.json')['commands']+caller_capture['commands']],'no_new_activity_hot_calls_or_memcpy_in_captured_complete_body':True,'limits':['Whole Q/ordinary/run instruction bodies uninspected except entries and actual full call points.','Callsite window starts/ends can intersect instructions; only complete decoded argument setup and verified call instructions are interpreted.','No type-layout probe, dynamic copy count, PMU or speed conclusion.','cfg(test) logical group counter cannot establish emitted zero setup; LLVM hoists true-path common plane decode before group branches.']}
assert len(summary['binutils_exit_codes'])==32 and set(summary['binutils_exit_codes'])=={0}
(E/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'complete':True,'binutils_commands':32,'all_exit0':True,'body_bytes':[(r['side'],r['symbol'],r['bytes'],r['local_stack_reservation']) for r in results],'raw_disassembly_bytes':caller_capture['total_raw_disassembly_bytes'],'all_inputs_unchanged':True}))
