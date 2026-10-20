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
    table_values={}
    for side in IDENTITY['images']:
        address,size=symbols[side]['rook2::relation_table::RELATIONS']
        assert size==262144
        table_values[side]=read(side,address,size)
    assert table_values['control']==table_values['candidate']
    table=dict(bytes=262144,unchanged_payload=True,
               sha256=hashlib.sha256(table_values['control']).hexdigest())
    assert table['sha256']=='09eb9f279a6111078f8600b9ebffff5b3c7eb35a8bf5298e7ef7691d162284ee'
    checks={}
    for name,mnemonic,size in [('ordinary-window','movq',8),('ordinary-piece-count','punpcklbw',16)]:
        values={}
        for side in IDENTITY['images']:
            line=next(x for x in (HERE/side/'ordinary.asm').read_text().splitlines()
                      if '\t'+mnemonic in x and '[rip' in x)
            pointer=int(re.search(r'#\s*([0-9a-f]+)',line)[1],16)
            values[side]=read(side,pointer,size).hex()
        assert values['control']==values['candidate'];checks[name]=values
    for function,ordinal,count in [('q',0,8),('q',1,7),('q',2,6),('charge',0,7)]:
        values={}
        for side in IDENTITY['images']:
            lines=(HERE/side/(function+'.asm')).read_text().splitlines()
            bases=[]
            for i,line in enumerate(lines):
                if '\tjmp ' in line and not re.search(r'jmp\s+[0-9a-f]+ ',line):
                    lea=next(x for x in reversed(lines[max(0,i-6):i]) if '[rip' in x)
                    bases.append(int(re.search(r'#\s*([0-9a-f]+)',lea)[1],16))
            base=bases[ordinal];start=int(CAPTURE['functions'][side][function]['address'],16)
            values[side]=[base+entry-start for entry in struct.unpack('<'+'i'*count,read(side,base,count*4))]
            assert all(0<=value<CAPTURE['functions'][side][function]['bytes'] for value in values[side])
        assert values['control']==values['candidate'];checks[f'{function}-dispatch-{ordinal}']=values
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
        counts_left=collections.Counter((x['mode'],x['role']) for x in left)
        counts_right=collections.Counter((x['mode'],x['role']) for x in right)
        removed=[dict(mode=k[0],role=k[1],sites=v) for k,v in (counts_left-counts_right).items()]
        added=[dict(mode=k[0],role=k[1],sites=v) for k,v in (counts_right-counts_left).items()]
        if name=='ordinary':
            assert removed==[dict(mode='resolved-GOT',role='core::panicking::panic_const::panic_const_rem_by_zero',sites=1)] and not added
        else:assert not removed and not added,(name,removed,added)
        comparisons[name]=dict(ordered_static_call_roles_equal=same_roles,removed_static_call_roles=removed,added_static_call_roles=added,
            ordered_static_call_offsets_equal=same_offsets,
            unresolved_register_sites=sum(x['mode']=='unresolved-register' for x in left),
            not_a_runtime_count_or_unresolved_target_equivalence=True)
    arithmetic={}
    for side in IDENTITY['images']:
        arithmetic[side]={}
        for function in ['ordinary','constructor','store','probe','store-ordinary']:
            instructions=[]
            for line in (HERE/side/(function+'.asm')).read_text().splitlines():
                m=re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
                if m and m[2] in ['div','idiv']:
                    instructions.append(dict(address=m[1],mnemonic=m[2],operands=m[3]))
            arithmetic[side][function]=instructions
    assert len(arithmetic['control']['ordinary'])==2 and len(arithmetic['candidate']['ordinary'])==1
    assert len(arithmetic['candidate']['constructor'])==len(arithmetic['control']['constructor'])+1
    assert not any(arithmetic[side][f] for side in arithmetic for f in ['store','probe','store-ordinary'])
    PROPOSAL=HERE.parent/'fullbyte-remembered-reciprocal-proposal-20261018-01'
    functional=HERE.parent/'fullbyte-remembered-reciprocal-validation-preparation-20261018-01'
    additional=[PROPOSAL/'source-manifest.json',PROPOSAL/'source-proof.json',functional/'functional-result.json',functional/'all-owned-process-closure.json']
    candidate_receipt=json.loads(Path(IDENTITY['images']['candidate']['receipt']).read_text())
    assert (candidate_receipt['source_sha256_before']|candidate_receipt['tool_sha256_before'])==json.loads((PROPOSAL/'source-manifest.json').read_text())['source69']
    inputs=IDENTITY['source_input_sha256']|{str(path):sha(path) for path in additional}
    assert all(sha(path)==digest for path,digest in inputs.items())
    result=dict(complete=True,table=table,selected_payload_checks=checks,
         decoded_static_calls=calls,call_comparisons=comparisons,arithmetic_divide_sites=arithmetic,
         section_sizes={side:{name:length for name,start,offset,length in sections[side] if name in ['.text','.rodata']}
                        for side in sections},all_inputs_unchanged=True,
         additional_inputs_sha256={str(path):sha(path) for path in additional},
         native_engine_runs=0,build_runs=0,no_dynamic_or_whole_function_equivalence_claim=True)
    with (HERE/'operand-verification.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(dict(complete=True,table=table,calls=comparisons,arithmetic=arithmetic,sections=result['section_sizes'])))

if __name__=='__main__':main()
