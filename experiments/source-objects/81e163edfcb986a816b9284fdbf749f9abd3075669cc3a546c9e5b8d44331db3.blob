"""Offline own-PGO paired mechanism analysis; no subprocesses."""
from pathlib import Path
from collections import Counter
import json,re,hashlib
E=Path(__file__).resolve().parent
load=lambda n:json.loads((E/n).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=load('capture.json');assert all(sha(p)==h for p,h in c['input_pins'].items())
results={}
for body in c['bodies']:
    side=body['side'];symbols={};mangled={}
    for name,dest in [(side+'-nm.stdout',symbols),(side+'-nm-mangled.stdout',mangled)]:
        for line in (E/name).read_text().splitlines():
            m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) (\w) (.*)$',line)
            if m:dest.setdefault(int(m[1],16),[]).append({'bytes':int(m[2],16),'type':m[3],'symbol':m[4]})
    relocs={int(m[1],16):int(m[2],16) for line in (E/(side+'-relocations.stdout')).read_text().splitlines() if (m:=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)\s*$',line))}
    source=None;instructions=[];calls=[]
    for line in (E/body['stdout']).read_text().splitlines():
        m=re.match(r'^(/.+\.rs):(\d+)(?:\s.*)?$',line)
        if m:source={'path':m[1],'line':int(m[2])};continue
        m=re.match(r'^\s*([0-9a-f]+):\s+(.*)$',line)
        if not m:continue
        row={'address':int(m[1],16),'asm':m[2],'source':source};instructions.append(row)
        if row['asm'].startswith('call '):
            slot=int(re.search(r'# ([0-9a-f]+)',row['asm'])[1],16);target=relocs[slot]
            calls.append(row|{'got_slot':slot,'target':target,'symbols':symbols[target]})
    assert all(any('slice_end_index_len_fail' in s['symbol'] or 'panic_bounds_check' in s['symbol'] for s in call['symbols']) for call in calls)
    frame=next(int(re.match(r'sub\s+rsp,0x([0-9a-f]+)',row['asm'])[1],16) for row in instructions[:12] if re.match(r'sub\s+rsp,0x',row['asm']))
    opcodes=Counter(row['asm'].split()[0] for row in instructions)
    sections={m[1]:int(m[2]) for line in (E/(side+'-size.stdout')).read_text().splitlines() if (m:=re.match(r'^(\.\S+)\s+(\d+)\s+\d+\s*$',line))}
    counter=[row for row in instructions if row['source'] and row['source']['path'].endswith('/influence/coherent.rs') and 136<=row['source']['line']<=159 and '[rsp' in row['asm']]
    results[side]=body|{'mangled_symbols':mangled[body['address']],'local_frame':frame,'static_calls':calls,'opcodes_static':dict(opcodes),'sections':sections,'counter_memory_debug_context':counter if side=='candidate' else [],'instructions':instructions,'raw_sha256':sha(E/body['stdout'])}
a,b=results['control'],results['candidate']
assert a['local_frame']==0x188 and b['local_frame']==0x1c8
assert len(a['static_calls'])==len(b['static_calls'])==7
assert any(row['address']==0x15de3 and row['asm'].startswith('je     16c59') for row in b['instructions'])
assert not any('EXPANSION' in line for line in (E/'candidate-nm.stdout').read_text().splitlines())
assert b['opcodes_static'].get('paddb',0)==0
summary={'complete':True,'own_PGO_only':True,'no_generic_cost_transfer':True,'all_inputs_unchanged':True,'source_profile_recipe_bindings':c['bindings'],'producer_local_frames':{'control':a['local_frame'],'candidate':b['local_frame'],'delta':b['local_frame']-a['local_frame']},'producer_bytes':{'control':a['bytes'],'candidate':b['bytes'],'delta':b['bytes']-a['bytes']},'whole_section_deltas':{key:b['sections'][key]-a['sections'][key] for key in ['.text','.rodata','.data.rel.ro']},'new_mnemonics':sorted(set(b['opcodes_static'])-set(a['opcodes_static'])),'candidate_per_source_EXPANSION_and_paddb_absent':True,'all_outgoing_calls_resolved_cold':True,'actual_candidate_zero_slider_branch':{'address':0x15de3,'target':0x16c59,'bypasses_counter_and_transpose':True,'scalar_PNK_retained':True,'frame_and_result_zero_and_common_plane_decode_still_paid':True},'candidate_transpose_region':[0x16a4d,0x16c10],'candidate_final_result_transfer_region':[0x16e2b,0x16e97],'candidate_counter_memory_anchors':b['counter_memory_debug_context'],'raw_disassembly_bytes':c['raw_disassembly_bytes'],'binutils_children':len(c['commands']),'all_binutils_exit0':True,'bodies':{side:{k:v for k,v in result.items() if k not in ['instructions','counter_memory_debug_context']} for side,result in results.items()},'limits':['No native workloads/tests or CPU/profiler measurements.','Generic native11focus is prior evidence; own-use broad189/54/wire/full117/games are not claimed.','Static memory operands are not dynamic spill/traffic counts.','All other caller bodies and other monomorphs uninspected.']}
assert all(command['exit_code']==0 for command in c['commands']) and len(c['commands'])==16
(E/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({key:summary[key] for key in ['producer_local_frames','producer_bytes','whole_section_deltas','new_mnemonics','binutils_children','raw_disassembly_bytes','all_inputs_unchanged']}))
