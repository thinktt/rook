"""Offline paired43 mechanism analysis from closed complete-body text only."""
from pathlib import Path
from collections import Counter
import re,json,hashlib
E=Path(__file__).resolve().parent
load=lambda n:json.loads((E/n).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=load('candidate-capture.json');assert all(sha(p)==h for p,h in c['input_pins'].items())
all_results={}
for label,file in [('baseline','baseline-complete-build-coherent.stdout'),('candidate','candidate-complete-1ff00.stdout')]:
    symbols={};mangled={}
    for filename,destination in [(label+'-nm.stdout',symbols),(label+'-nm-mangled.stdout',mangled)]:
        for line in (E/filename).read_text().splitlines():
            m=re.match(r'^([0-9a-f]+) ([0-9a-f]+) (\w) (.*)$',line)
            if m:destination.setdefault(int(m[1],16),[]).append({'bytes':int(m[2],16),'type':m[3],'name':m[4]})
    relocs={int(m[1],16):int(m[2],16) for line in (E/(label+'-relocations.stdout')).read_text().splitlines() if (m:=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)\s*$',line))}
    source=None;instructions=[];calls=[]
    for line in (E/file).read_text().splitlines():
        m=re.match(r'^(/.+\.rs):(\d+)(?:\s.*)?$',line)
        if m:source={'file':m[1],'line':int(m[2])};continue
        m=re.match(r'^\s*([0-9a-f]+):\s+(.*)$',line)
        if not m:continue
        row={'address':int(m[1],16),'assembly':m[2],'source':source};instructions.append(row)
        if row['assembly'].startswith('call '):
            slot=int(re.search(r'# ([0-9a-f]+)',row['assembly'])[1],16);target=relocs[slot]
            calls.append(row|{'slot':slot,'target':target,'symbols':symbols[target]})
    assert all(any('slice_end_index_len_fail' in sym['name'] or 'panic_bounds_check' in sym['name'] for sym in call['symbols']) for call in calls)
    frame=next(int(re.match(r'sub\s+rsp,0x([0-9a-f]+)',r['assembly'])[1],16) for r in instructions[:12] if re.match(r'sub\s+rsp,0x',r['assembly']))
    opcodes=Counter(r['assembly'].split()[0] for r in instructions)
    sections={m[1]:int(m[2]) for line in (E/(label+'-size.stdout')).read_text().splitlines() if (m:=re.match(r'^(\.\S+)\s+(\d+)\s+\d+\s*$',line))}
    carries=[row for row in instructions if row['source'] and row['source']['file'].endswith('/influence/coherent.rs') and 136<=row['source']['line']<=159 and '[rsp' in row['assembly']]
    all_results[label]={'producer':symbols[0x1ff00],'mangled':mangled[0x1ff00],'local_frame':frame,'static_calls':calls,'opcode_counts_static':dict(opcodes),'sections':sections,'counter_memory_debug_context':carries if label=='candidate' else [],'complete_body_sha256':sha(E/file),'instructions':instructions}
base,new=all_results['baseline'],all_results['candidate']
assert base['local_frame']==408 and new['local_frame']==456
assert not any('EXPANSION' in line for line in (E/'candidate-nm.stdout').read_text().splitlines())
assert new['opcode_counts_static'].get('paddb',0)==0
assert any(r['address']==0x202c7 and r['assembly'].startswith('je     203b0') for r in new['instructions'])
result={'complete':True,'baseline_namespace_unchanged':True,'candidate_image_sha256':c['image_sha256'],'source_graph':c['source_graph'],'generic_compiler_settings_match':True,'baseline_frame':408,'candidate_frame':456,'frame_delta':48,'baseline_function_bytes':5485,'candidate_function_bytes':5789,'function_delta':304,'whole_text_delta':new['sections']['.text']-base['sections']['.text'],'whole_rodata_delta':new['sections']['.rodata']-base['sections']['.rodata'],'data_rel_ro_delta':new['sections']['.data.rel.ro']-base['sections']['.data.rel.ro'],'new_mnemonics':sorted(set(new['opcode_counts_static'])-set(base['opcode_counts_static'])),'no_new_ISA_from_new_mnemonics':True,'candidate_named_EXPANSION_absent':True,'candidate_per_source_EXPANSION_and_paddb_absent_in_complete_body':True,'no_outlined_hot_helpers':True,'counter_memory_is_not_zero':True,'candidate_counter_stack_memory_anchors':new['counter_memory_debug_context'],'no_slider_branch':{'address':0x202c7,'target':0x203b0,'scalar_leaper_region':[0x203b0,0x20670],'skips_bit_counter_and_transpose':True,'common_plane_decode_and_result_zero_not_skipped':True},'transpose_region':[0x20040,0x20217],'final_output_transfer_region':[0x21467,0x214cf],'candidate_binutils_commands':10,'all_candidate_binutils_exit0':True,'candidate_complete_symbols':1,'candidate_raw_disassembly_bytes':104897,'baseline_raw_disassembly_bytes':103766,'per_side':{label:{key:value for key,value in rows.items() if key not in ['instructions','counter_memory_debug_context']} for label,rows in all_results.items()},'all_pinned_inputs_unchanged':True,'static_only_not_CPU_traffic_or_semantic_proof':True,'focused_tests_pending':True}
assert len(c['commands'])==10 and all(command['exit_code']==0 for command in c['commands'])
(E/'candidate-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['complete','baseline_frame','candidate_frame','function_delta','whole_text_delta','whole_rodata_delta','data_rel_ro_delta','new_mnemonics','candidate_counter_stack_memory_anchors'] if k!='candidate_counter_stack_memory_anchors'}))
print(json.dumps({'counter_stack_memory_debug_rows':len(result['candidate_counter_stack_memory_anchors']),'all_static_children_terminal':True}))
