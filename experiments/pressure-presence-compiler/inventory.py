#!/usr/bin/env python3
"""Static, address-bounded instruction inventory; never dynamic traffic counts."""
import collections
import json
from pathlib import Path
import re

B = Path('/home/legolas/rook2-experiments/pressure-presence-compiler-20261020-01')


def main():
    receipt = json.loads((B / 'capture/receipt.json').read_text())
    result = {'scope': 'Complete nm-bounded Activity owners. Lexical RSP operand sites exclude '
                       'LEA/NOP and omit aliased stack operands. RBP is not a frame pointer here. '
                       'Neither instruction/site counts nor frame size establish dynamic spills/traffic.',
              'images': {}}
    for label, image in receipt['images'].items():
        owners = []
        for symbol in image['activity_symbols']:
            if symbol['type'] not in ('t', 'T'):
                continue
            rows = []
            for line in Path(symbol['capture']).read_text().splitlines():
                m = re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$', line)
                if m and symbol['address'] <= int(m[1], 16) < symbol['address'] + symbol['size']:
                    rows.append((m[1], m[2], m[3]))
            counts = collections.Counter(m for _, m, _ in rows)
            owners.append({'name': symbol['name'], 'address': hex(symbol['address']),
                           'bytes': symbol['size'], 'lexical_instructions': len(rows),
                           'mnemonics': dict(counts),
                           'pushes': [r for r in rows if r[1] == 'push'],
                           'local_reservations': [r for r in rows if r[1] == 'sub' and r[2].startswith('rsp,')],
                           'direct_rsp_operand_sites': sum(bool(re.search(r'\[rsp(?:\+|\-|\])', a))
                                                           and m not in ('lea', 'nop') for _, m, a in rows),
                           'memory_or_sites': [r for r in rows if r[1] == 'or' and ' PTR [' in r[2]],
                           'constant_vector_loads': [r for r in rows if r[1] in ('movdqa', 'movaps', 'movups', 'movdqu')
                                                     and '[rip' in r[2]],
                           'calls': [r for r in rows if r[1].startswith('call')]})
        section = next(line for line in (B / 'capture' / label / 'sections.txt').read_text().splitlines()
                       if re.search(r'\]\s+\.text\s', line))
        text_bytes = int(section.split('.text')[1].split()[3], 16)
        result['images'][label] = {'elf_bytes': image['bytes'], 'text_section_bytes': text_bytes,
                                   'activity_text_bytes': sum(x['bytes'] for x in owners), 'owners': owners}
    p = B / 'backend-inventory.json'
    with p.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({'scope': result['scope'], 'images': {
        label: {**{k: image[k] for k in ('elf_bytes', 'text_section_bytes', 'activity_text_bytes')},
                'owners': [{k: owner[k] for k in ('name', 'bytes', 'lexical_instructions', 'direct_rsp_operand_sites')}
                           for owner in image['owners']]}
        for label, image in result['images'].items()}}))


if __name__ == '__main__':
    main()
