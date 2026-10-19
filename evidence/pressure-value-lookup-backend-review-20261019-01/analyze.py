"""Offline window metrics only; no executable or subprocess access."""
from pathlib import Path
import json,re
P=Path(__file__).resolve().parent
state=json.loads((P/'window-state.json').read_text())
result=[]
for row in state['windows']:
    code=Path(row['command']['stdout']).read_text()
    ins=[{'address':m[1],'instruction':m[2]} for line in code.splitlines()
         if (m:=re.match(r'^\s*([0-9a-f]+):\s+(.*)',line))]
    result.append({'side':row['side'],'symbol':row['symbol'],'window_start':hex(row['start']),
        'window_bytes':row['length'],'whole_body':row['whole_body'],'starts_at_entry':row['starts_at_entry'],
        'static_instructions_in_window':len(ins),
        'stack_reference_rows':[r for r in ins if '[rsp' in r['instruction'] and not r['instruction'].startswith(('lea','nop'))],
        'stack_adjustments':[r for r in ins if re.match(r'(sub|add)\s+rsp,',r['instruction'])],
        'calls':[r for r in ins if r['instruction'].startswith('call')],
        'transpose_ops':[r for r in ins if r['instruction'].startswith(('pmovmskb','paddb','movdqu'))]})
with (P/'window-analysis.json').open('x') as f:json.dump({'windows':result,'disassembly_bytes':state['disassembly_bytes'],'named_bodies':state['named_bodies'],'partial_windows_are_not_whole_body_metrics':True},f,indent=2);f.write('\n')
print(json.dumps({'complete':True,'windows':len(result)}))
