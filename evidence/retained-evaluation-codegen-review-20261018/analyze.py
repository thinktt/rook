"""Static focused comparison; normalized operands do not prove referent equality."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import struct

OUT = Path(__file__).resolve().parent
INPUT = json.loads((OUT/'inputs.json').read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(name):
    return re.sub(r'\.llvm\.\d+', '', name)


def sections(data):
    assert data[:6] == b'\x7fELF\x02\x01'
    offset = struct.unpack_from('<Q', data, 40)[0]
    size, count, strings = struct.unpack_from('<HHH', data, 58)
    rows = [struct.unpack_from('<IIQQQQIIQQ', data, offset+i*size) for i in range(count)]
    names = data[rows[strings][4]:rows[strings][4]+rows[strings][5]]
    return {names[row[0]:].split(b'\0',1)[0].decode():
            dict(address=row[3], offset=row[4], size=row[5], type=row[1]) for row in rows}


def image(label, info):
    data = Path(info['binary']).read_bytes()
    assert sha(data) == info['binary_sha256']
    sec = sections(data)
    text = sec['.text']
    chunks = re.split(r'(?m)^([0-9a-f]+) <(.+)>:\n', (OUT/(label+'-disassembly.txt')).read_text())
    bodies = {int(chunks[i],16):chunks[i+2] for i in range(1,len(chunks),3)}
    answer, occurrences = {}, {}
    for line in (OUT/(label+'-nm-demangled.txt')).read_text().splitlines():
        match = re.match(r'([0-9a-f]+) ([0-9a-f]+) ([tT]) (.*)', line)
        if not match:
            continue
        address, size, name = int(match[1],16), int(match[2],16), canonical(match[4])
        n = occurrences.get(name,0)
        occurrences[name] = n+1
        start = text['offset']+address-text['address']
        body = []
        instructions = []
        for line in bodies.get(address,'').splitlines():
            match = re.match(r'\s*([0-9a-f]+):\s*(.*)',line)
            if not match or int(match[1],16) >= address+size:
                continue
            body.append(line)
            instruction = canonical(match[2])
            parts = instruction.split('#',1)
            instruction = parts[0]
            if len(parts)==2 and '(%rip)' in instruction:
                target = re.search(r'[0-9a-f]+ <(.*)>',parts[1])
                if target:
                    instruction = re.sub(r'-?0x[0-9a-f]+\(%rip\)', 'RIP<'+target[1]+'>', instruction)
            instruction = re.sub(r'\b[0-9a-f]+ <(.*)>',r'TARGET<\1>',instruction)
            instructions.append(' '.join(instruction.split()))
        answer[(name,n)] = dict(name=name, occurrence=n, address=address, size=size,
            bytes_sha256=sha(data[start:start+size]),
            normalized_sha256=sha('\n'.join(instructions).encode()),
            instruction_count=len(instructions), body=body)
    section_data = {name:{**row, 'sha256':sha(data[row['offset']:row['offset']+row['size']])}
                    for name,row in sec.items() if row['type']!=8}
    (OUT/(label+'-sections.json')).write_text(json.dumps(section_data,indent=2)+'\n')
    return answer


def main():
    images = {label:image(label,info) for label,info in INPUT['artifacts'].items()}
    before,after = images['root79'],images['retained82']
    focused = []
    for key in sorted(set(before)&set(after)):
        if not any(part in key[0] for part in ('rook2::evaluator::','rook2::ordinary::','rook2::quiescence::')):
            continue
        a,b = before[key],after[key]
        index = len(focused)
        diff = '\n'.join(difflib.unified_diff(a['body'],b['body'],fromfile='root79',tofile='retained82'))+'\n'
        (OUT/f'function-{index:02d}.diff').write_text(diff)
        focused.append(dict(name=key[0], occurrence=key[1],
            root79={k:v for k,v in a.items() if k!='body'},
            retained82={k:v for k,v in b.items() if k!='body'},
            bytes_equal=a['bytes_sha256']==b['bytes_sha256'],
            normalized_equal=a['normalized_sha256']==b['normalized_sha256'],
            diff=f'function-{index:02d}.diff'))
    qkey = next(key for key in before if '::visit_q' in key[0])
    a,b = before[qkey],after[qkey]
    assert a['address']==b['address'] and a['size']==b['size']
    assert len(a['body'])==len(b['body'])
    operand_changes = []
    for old,new in zip(a['body'],b['body']):
        if old.split('#',1)[0].strip()==new.split('#',1)[0].strip():
            continue
        assert 'lea ' in old and '(%rip)' in old and 'lea ' in new and '(%rip)' in new
        targets=[]
        for label,line in [('root79',old),('retained82',new)]:
            address = int(re.search(r'#\s*([0-9a-f]+) <',line)[1],16)
            sec = json.loads((OUT/(label+'-sections.json')).read_text())['.rodata']
            assert sec['address']<=address and address+32<=sec['address']+sec['size']
            data = Path(INPUT['artifacts'][label]['binary']).read_bytes()
            offset = sec['offset']+address-sec['address']
            words = struct.unpack_from('<8i',data,offset)
            targets.append(dict(base=address, decoded_window_targets=[address+word for word in words]))
        assert targets[0]['decoded_window_targets']==targets[1]['decoded_window_targets']
        operand_changes.append(dict(old_instruction=old,new_instruction=new,
            root79=targets[0],retained82=targets[1],window_bytes=32,
            scope='Window around table base; not a claim that every window word is an admitted table entry'))
    assert len(operand_changes)==3
    result = dict(focused=focused,quiescence_operand_changes=operand_changes,
        normalization='Remove displayed instruction addresses/comments and numeric LLVM suffixes; canonicalize annotated direct targets and RIP symbolic operands. Preserve registers, other offsets, immediates and ordering. No data-referent equality follows.',
        scope='Frozen generic artifacts only. No CPU, PMU, whole-image semantic identity or PGO claim.',
        analyzer_sha256=sha(Path(__file__).read_bytes()))
    (OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:row[k] for k in ('name','bytes_equal','normalized_equal','diff')} for row in focused]))


if __name__ == '__main__':
    main()
