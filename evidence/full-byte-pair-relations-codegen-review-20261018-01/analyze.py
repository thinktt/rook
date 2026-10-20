"""Offline inspection of captured own-image assembly and relocation text."""
from pathlib import Path
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
CAPTURE = json.loads((HERE/'function-capture.json').read_text())

def rows(path):
    result=[]
    for line in path.read_text().splitlines():
        match=re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
        if match:
            result.append((int(match[1],16),match[2],match[3]))
    return result

def signatures(instructions,start,size):
    result=[]
    for address, mnemonic, operands in instructions:
        body,_,comment=operands.partition('#')
        # Retain named RIP referents, rather than silently deleting the operand.
        if '[rip' in body:
            name=re.search(r'<(.+)>',comment)
            target=name.group(1) if name else comment.strip()
            body=re.sub(r'\[rip[^]]*\]','[PCREL '+target+']',body)
        # Local branch offsets distinguish control-flow targets after rebasing.
        match=re.match(r'^([0-9a-f]+) <(.+)>$',body.strip())
        if match:
            target=int(match[1],16)
            body=('LOCAL+'+hex(target-start) if start<=target<start+size else match[2])
        result.append(mnemonic+' '+body.strip())
    return result

def main():
    summary={}
    for side,functions in CAPTURE['functions'].items():
        summary[side]={}
        relocations={}
        for line in (HERE/side/'relocations.stdout').read_text().splitlines():
            m=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)$',line)
            if m:relocations[int(m[1],16)]=int(m[2],16)
        symbols={}
        for line in (HERE/side/'nm-demangled.stdout').read_text().splitlines():
            m=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+\S\s+(.+)$',line)
            if m:symbols.setdefault(int(m[1],16),m[2])
        for name,metadata in functions.items():
            instructions=rows(HERE/side/(name+'.asm'))
            sig=signatures(instructions,int(metadata['address'],16),metadata['bytes'])
            (HERE/side/(name+'.signature.txt')).write_text('\n'.join(sig)+'\n')
            calls=[]
            for address,mnemonic,operands in instructions:
                if mnemonic!='call':continue
                got=re.search(r'#\s*([0-9a-f]+)',operands)
                resolved=None
                if got:
                    slot=int(got[1],16)
                    if slot in relocations:
                        target=relocations[slot]
                        resolved=dict(slot=hex(slot),target=hex(target),symbol=symbols.get(target))
                calls.append(dict(address=hex(address),operands=operands,resolved_got=resolved))
            summary[side][name]=dict(bytes=metadata['bytes'],instructions=len(instructions),
                static_calls=len(calls),static_conditional_jumps=sum(m.startswith('j') and m!='jmp' for _,m,_ in instructions),
                static_rsp_reference_instructions=sum('[rsp' in o for _,_,o in instructions),
                rsp_subtractions=[o for _,m,o in instructions if m=='sub' and o.startswith('rsp,')],
                first_instructions=[m+' '+o for _,m,o in instructions[:8]],calls=calls)
    comparisons={}
    for name in CAPTURE['functions']['control']:
        left=(HERE/'control'/(name+'.signature.txt')).read_text().splitlines()
        right=(HERE/'candidate'/(name+'.signature.txt')).read_text().splitlines()
        diff=list(difflib.unified_diff(left,right,fromfile='control/'+name,tofile='candidate/'+name,lineterm=''))
        (HERE/(name+'.signature.diff')).write_text('\n'.join(diff)+'\n')
        comparisons[name]=dict(same_instruction_register_stack_branch_signature=left==right,
            signature_does_not_prove_referent_payload_or_runtime_equality=True)
    with (HERE/'bounded-analysis.json').open('x') as out:
        json.dump(dict(complete=True,metrics=summary,comparisons=comparisons,
            caveat='Static counts and bounded structural signatures only; no dynamic cost/equality claim'),out,indent=2)
        out.write('\n')
    print(json.dumps(dict(comparisons=comparisons,metrics={side:{key:{k:v for k,v in value.items() if k!='calls'}
        for key,value in functions.items()} for side,functions in summary.items()})))

if __name__=='__main__':main()
