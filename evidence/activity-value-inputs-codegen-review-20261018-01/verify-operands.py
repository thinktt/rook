"""Bounded operand/payload checks of saved own ELF images; no native execution."""
from pathlib import Path
import ast
import hashlib
import json
import re
import struct

HERE=Path(__file__).resolve().parent
IDENTITY=json.loads((HERE/'identity.json').read_text())
CAPTURE=json.loads((HERE/'function-capture.json').read_text())
ANALYSIS=json.loads((HERE/'bounded-analysis.json').read_text())

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    binaries={}
    sections={}
    def read(side,address,size):
        for section in sections[side]:
            start,offset,length=section
            if start<=address and address+size<=start+length:
                return binaries[side][offset+address-start:offset+address-start+size]
        raise AssertionError((side,hex(address),size))
    for side,item in IDENTITY['images'].items():
        assert sha(item['image'])==item['image_sha256']
        binaries[side]=Path(item['image']).read_bytes()
        sections[side]=[]
        for line in (HERE/side/'sections.stdout').read_text().splitlines():
            m=re.match(r'^\s*\[\s*\d+\]\s+\S+\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)',line)
            if m:sections[side].append(tuple(int(x,16) for x in m.groups()))
    source=Path(IDENTITY['images']['control']['receipt']).parent/'source-before/src/activity.rs'
    text=source.read_text()
    ordinary=ast.literal_eval(re.search(r'const DESTINATION_VALUE:.*?= (\[.*?\n\]);',text,re.S)[1])
    rook=ast.literal_eval(re.search(r'const ROOK_SEVENTH:.*?= (\[.*?\]);',text)[1])
    expected=bytes(rook[square%8] if variant and rank==6 else ordinary[rank][square%8]
        for color in range(2) for variant in range(2) for square in range(64)
        for rank in [square//8 if color==0 else 7-square//8])
    assert len(expected)==256
    symbol=next(row.split() for row in (HERE/'candidate/nm-demangled.stdout').read_text().splitlines()
                if row.endswith('rook2::activity::DESTINATION_VALUES'))
    table_address,table_size=int(symbol[0],16),int(symbol[1],16)
    assert table_size==256 and read('candidate',table_address,256)==expected
    assert binaries['candidate'].count(expected)==1
    checks={}
    # Actual RIP-loaded ordinary SIMD constants, not merely their linker names.
    for name,needle,size in [('ordinary-window','movq xmm1,QWORD PTR [PCREL',8),
                              ('ordinary-piece-count','punpcklbw xmm0,XMMWORD PTR [PCREL',16)]:
        values={}
        for side in IDENTITY['images']:
            assembly=(HERE/side/'ordinary.asm').read_text().splitlines()
            mnemonic='movq' if size==8 else 'punpcklbw'
            line=next(x for x in assembly if '\t'+mnemonic in x and '[rip' in x)
            address=int(re.search(r'#\s*([0-9a-f]+)',line)[1],16)
            values[side]=read(side,address,size).hex()
        assert values['control']==values['candidate']
        checks[name]=values
    # Dispatch-table spans are bounded by consecutive emitted table offsets and
    # source domains: Q move kinds8 / victim tags7 / nonzero kinds6, Host commands7.
    for function,offset,count in [('q','0x43d',8),('q','0x475',7),('q','0x45d',6),('charge','0x491',7)]:
        values={}
        for side in IDENTITY['images']:
            lines=(HERE/side/(function+'.asm')).read_text().splitlines()
            line=next(x for x in lines if '[rip' in x and '+'+offset+'>' in x)
            base=int(re.search(r'#\s*([0-9a-f]+)',line)[1],16)
            start=int(CAPTURE['functions'][side][function]['address'],16)
            entries=struct.unpack('<'+'i'*count,read(side,base,count*4))
            targets=[base+entry-start for entry in entries]
            assert all(0<=value<CAPTURE['functions'][side][function]['bytes'] for value in targets)
            values[side]=targets
        assert values['control']==values['candidate']
        checks[function+'-'+offset]=values
    # Resolve actual evaluator -> activity GOT transfer in both exact images.
    transfers={}
    for side in IDENTITY['images']:
        calls=ANALYSIS['metrics'][side]['evaluation']['calls']
        found=[call for call in calls if call['resolved_got'] and
               call['resolved_got']['symbol']=='rook2::activity::compute']
        assert len(found)==1
        transfers[side]=found[0]
    assert all(sha(path)==digest for path,digest in IDENTITY['source_input_sha256'].items())
    with (HERE/'operand-verification.json').open('x') as out:
        json.dump(dict(complete=True,table=dict(address=hex(table_address),bytes=table_size,
            full_payload_occurrences=1,full_domain_payload_matches_source=True),
            selected_propagated_payload_checks=checks,evaluator_activity_calls=transfers,
            all_bound_inputs_unchanged=True,no_whole_function_equality_claim=True),out,indent=2)
        out.write('\n')
    print(json.dumps(dict(complete=True,table_bytes=table_size,checks=len(checks),
        evaluator_activity_calls=transfers,native_engine_runs=0)))

if __name__=='__main__':main()
