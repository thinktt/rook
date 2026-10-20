#!/usr/bin/env python3
"""Summarize complete captured owners; lexical stack sites are not spill/traffic counts."""
import json,re
from pathlib import Path
B=Path('/home/legolas/rook2-experiments/checked-enumeration-compiler-20261020-01')
r=json.loads((B/'capture/receipt.json').read_text())
out={}
for label,im in r['images'].items():
    rows=[]
    for s in im['generation_caller_symbols']:
        body=Path(s['capture']).read_text()
        ins=[m.groups() for m in re.finditer(r'^\s+([0-9a-f]+):\s+(\S+)\s*(.*)$',body,re.M) if s['address'] <= int(m[1],16) < s['address']+s['size']]
        rows.append(dict(name=s['name'],address=hex(s['address']),bytes=s['size'],capture=s['capture'],
            first_instructions=[' '.join(x) for x in ins[:12]],
            rsp_memory_sites=sum('[' in x[2] and bool(re.search(r'\[[^\]]*\brsp\b',x[2])) and x[1] not in ('lea','nop') and not(x[1] in ('cs','data16') and 'nop' in x[2]) for x in ins),
            calls=[' '.join(x) for x in ins if x[1] in ('call','jmp') and ('<' in x[2])],
            masks_references=[' '.join(x) for x in ins if 'attacks::MASKS' in x[2]]))
    sections=(B/'capture'/label/'sections.txt').read_text()
    text=re.search(r'\]\s+\.text\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)',sections)
    out[label]=dict(text_section_bytes=int(text[3],16),owners=rows)
(B/'capture/inventory.json').write_text(json.dumps(out,indent=2)+'\n')
for label,v in out.items():
 print(label,'text',v['text_section_bytes'])
 for x in v['owners']:
  print(x['address'],x['bytes'],'rsp sites',x['rsp_memory_sites'],x['name'])
  print(' PROLOGUE',x['first_instructions'][:9])
  if 'pieces' in x['name'] or 'generate_legal' in x['name'] or 'legal_replies' in x['name']:print(' CALLS',x['calls'],'MASKS',x['masks_references'])
