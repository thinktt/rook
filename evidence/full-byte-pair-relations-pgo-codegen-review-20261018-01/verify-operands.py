"""Verify actual typed table, scoped call transfers and selected data referents."""
from pathlib import Path
import collections
import hashlib
import json
import re
import runpy
import struct

HERE=Path(__file__).resolve().parent
IDENTITY=json.loads((HERE/'identity.json').read_text())
CAPTURE=json.loads((HERE/'function-capture.json').read_text())
ANALYSIS=json.loads((HERE/'bounded-analysis.json').read_text())
PROPOSAL=HERE.parent/'full-byte-pair-relations-proposal-20261018-01'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    binaries={};sections={};symbols={}
    for side,item in IDENTITY['images'].items():
        assert sha(item['image'])==item['image_sha256']
        binaries[side]=Path(item['image']).read_bytes()
        sections[side]=[];symbols[side]={}
        for line in (HERE/side/'sections.stdout').read_text().splitlines():
            m=re.match(r'^\s*\[\s*\d+\]\s+(\S+)\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)',line)
            if m:sections[side].append((m[1],*(int(x,16) for x in m.groups()[1:])))
        for line in (HERE/side/'nm-demangled.stdout').read_text().splitlines():
            m=re.match(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+\S\s+(.+)$',line)
            if m:symbols[side][m[3]]=(int(m[1],16),int(m[2],16))
    def read(side,address,size):
        for name,start,offset,length in sections[side]:
            if start<=address and address+size<=start+length:
                return binaries[side][offset+address-start:offset+address-start+size]
        raise AssertionError((side,hex(address),size))
    prepared=json.loads((PROPOSAL/'prepared.json').read_text())
    generator=PROPOSAL/'generate_full_relations.py'
    assert sha(generator)==prepared['generator_sha256']
    namespace=runpy.run_path(str(generator))
    source=Path(IDENTITY['images']['candidate']['receipt']).parent/'source-before/src/relation_table.rs'
    assert source.read_text()==namespace['source']()
    # Explicit enum variant encoding is independently visible in unchanged repr(u8).
    influence=(source.parent/'influence.rs').read_text()
    assert '#[repr(u8)]\npub enum Relation {\n    Unfavorable = 0,\n    Contested = 1,\n    Favorable = 2,\n}' in influence
    encoded={'U':0,'C':1,'F':2}
    expected=bytes(encoded[namespace['outcome'](namespace['features'](own),namespace['features'](opponent),tested)]
                   for tested in [1,3,5,9] for own in range(256) for opponent in range(256))
    address,size=symbols['candidate']['rook2::relation_table::RELATIONS']
    assert size==262144 and read('candidate',address,size)==expected
    assert 'rook2::relation_table::CLASS' not in symbols['candidate']
    assert binaries['candidate'].count(expected)==1
    assert symbols['control']['rook2::relation_table::CLASS'][1]==256
    assert symbols['control']['rook2::relation_table::RELATIONS'][1]==1024
    table=dict(address=hex(address),bytes=size,sha256=hashlib.sha256(expected).hexdigest(),
               general_formula_all_emitted_bytes_equal=True,full_payload_occurrences=1,
               no_named_CLASS=True,control_CLASS_bytes=256,control_RELATIONS_bytes=1024)
    checks={}
    candidate_receipt=json.loads(Path(IDENTITY['images']['candidate']['receipt']).read_text())
    proposal_manifest=json.loads((PROPOSAL/'source-manifest.json').read_text())
    assert (candidate_receipt['source_sha256_before']|candidate_receipt['tool_sha256_before'])==proposal_manifest['source69']
    checks['candidate_source69_equals_frozen_6aa']=True
    calls={};comparisons={}
    for side in IDENTITY['images']:
        calls[side]={}
        for name,metrics in ANALYSIS['metrics'][side].items():
            start=int(CAPTURE['functions'][side][name]['address'],16);decoded=[]
            for call in metrics['calls']:
                if call['resolved_got']:
                    role=call['resolved_got']['symbol']
                    mode='resolved-GOT' if role else 'unresolved-GOT'
                else:
                    found=re.search(r'<(.+)>',call['operands'])
                    role=found[1] if found else call['operands']
                    mode='direct-symbol' if found else 'unresolved-register'
                decoded.append(dict(offset=int(call['address'],16)-start,mode=mode,role=role,
                                    address=call['address'],operands=call['operands']))
            calls[side][name]=decoded
    for name in CAPTURE['functions']['control']:
        left=calls['control'][name];right=calls['candidate'][name]
        same_roles=[(x['mode'],x['role']) for x in left]==[(x['mode'],x['role']) for x in right]
        same_offsets=[x['offset'] for x in left]==[x['offset'] for x in right]
        same_role_counts=collections.Counter((x['mode'],x['role']) for x in left)==collections.Counter((x['mode'],x['role']) for x in right)
        assert same_role_counts,(name,'changed call-role counts')
        if name in ['evaluation','q']:assert same_roles and same_offsets,(name,'changed call boundaries')
        comparisons[name]=dict(ordered_static_call_roles_equal=same_roles,
            static_call_role_counts_equal=same_role_counts,
            ordered_static_call_offsets_equal=same_offsets,
            unresolved_register_sites=sum(x['mode']=='unresolved-register' for x in left),
            not_a_runtime_count_or_unresolved_target_equivalence=True)
    refs={};lookup_windows=[]
    for side in IDENTITY['images']:
        refs[side]={}
        for function in ['activity','ordinary','evaluation','q']:
            assembly=(HERE/side/(function+'.asm')).read_text().splitlines()
            refs[side][function]=dict(CLASS=sum('::CLASS>' in x for x in assembly),
                                    RELATIONS=sum('::RELATIONS>' in x for x in assembly))
            if function in ['activity','ordinary']:
                first=next(i for i,x in enumerate(assembly) if 'relation_table::' in x)
                lookup_windows.extend([side+' '+function,*assembly[max(0,first-12):first+12],''])
    assert refs['control']['activity']==dict(CLASS=11,RELATIONS=11)
    assert refs['candidate']['activity']==dict(CLASS=0,RELATIONS=11)
    assert refs['control']['ordinary']==dict(CLASS=2,RELATIONS=1)
    assert refs['candidate']['ordinary']==dict(CLASS=0,RELATIONS=1)
    (HERE/'representative-lookups.txt').write_text('\n'.join(lookup_windows)+'\n')
    inputs=IDENTITY['source_input_sha256']|{str(generator):sha(generator),str(PROPOSAL/'prepared.json'):sha(PROPOSAL/'prepared.json')}
    assert all(sha(path)==digest for path,digest in inputs.items())
    result=dict(complete=True,table=table,selected_payload_checks=checks,
         decoded_static_calls=calls,call_comparisons=comparisons,scoped_named_table_references=refs,
         section_sizes={side:{name:length for name,start,offset,length in sections[side] if name in ['.text','.rodata']}
                        for side in sections},all_inputs_unchanged=True,
         additional_inputs_sha256={str(generator):sha(generator),str(PROPOSAL/'prepared.json'):sha(PROPOSAL/'prepared.json')},
         native_engine_runs=0,build_runs=0,no_dynamic_or_whole_function_equivalence_claim=True)
    with (HERE/'operand-verification.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(dict(complete=True,table=table,calls=comparisons,refs=refs,sections=result['section_sizes'])))

if __name__=='__main__':main()
