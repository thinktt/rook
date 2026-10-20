"""Own-image GOT target resolution; saved instruction metrics are static, not dynamic."""
from pathlib import Path
import json,re,subprocess,hashlib
P=Path(__file__).resolve().parent;E=P.parent
c=json.loads((P/'capture.json').read_text());results={};commands=[]
for side,dirname in [('control','ordinary-projected-bits-generic-build-20261018-01'),('candidate','full-evaluation-phase-sharing-generic-build-20261018-01')]:
 image=str(E/dirname/'rook2-exact');argv=['/usr/bin/objdump','-R',image]
 with (P/side/'relocations.stdout').open('xb') as o,(P/side/'relocations.stderr').open('xb') as e:r=subprocess.run(argv,stdout=o,stderr=e)
 assert r.returncode==0
 commands.append({'argv':argv,'exit_code':r.returncode})
 rel={}
 for line in (P/side/'relocations.stdout').read_text().splitlines():
  m=re.match(r'^([0-9a-f]+)\s+R_X86_64_RELATIVE\s+\*ABS\*\+0x([0-9a-f]+)',line)
  if m:rel[int(m[1],16)]=int(m[2],16)
 names={}
 for line in (P/side/'nm.stdout').read_text().splitlines():
  m=re.match(r'^([0-9a-f]+) (?:[0-9a-f]+ )?[A-Za-z] (.*)$',line)
  if m:names.setdefault(int(m[1],16),[]).append(m[2])
 funcs=[]
 for row in c['functions'][side]:
  if not row['captured']:continue
  a=[]
  for line in (P/row['assembly']).read_text().splitlines():
   m=re.match(r'^\s*([0-9a-f]+):\s+(.*)',line)
   if m:a.append((int(m[1],16),m[2]))
  calls=[]
  for addr,inst in a:
   if inst.startswith('call'):
    m=re.search(r'# ([0-9a-f]+) ',inst);slot=int(m[1],16) if m else None
    direct=re.match(r'call\s+([0-9a-f]+) ',inst)
    target=rel.get(slot) if slot is not None else int(direct[1],16) if direct else None
    calls.append({'site':hex(addr),'instruction':inst,'slot':hex(slot) if slot else None,'target':hex(target) if target else None,'symbols':names.get(target,[])})
  stack=[{'address':hex(addr),'instruction':inst} for addr,inst in a if '[rsp' in inst and not inst.startswith(('lea','nop'))]
  funcs.append({**row,'static_instructions':len(a),'rsp_adjustments':[{'address':hex(x),'instruction':y} for x,y in a if re.match(r'(sub|add)\s+rsp,',y)],'push_instructions':[{'address':hex(x),'instruction':y} for x,y in a if y.startswith('push')],'stack_memory_reference_instruction_count':len(stack),'stack_reference_instructions':stack,'calls':calls,'phase_like_0x140_markers':[hex(x) for x,y in a if re.search(r'[, ]0x140(?:$|\s)',y)],'phase_like_0x180_markers':[hex(x) for x,y in a if re.search(r'[, ]0x180(?:$|\s)',y)]})
 results[side]=funcs
for path,h in json.loads((P/'input-pins.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
with (P/'lowering.json').open('x') as f:json.dump({'functions':results,'commands':commands,'all_inputs_unchanged':True},f,indent=2);f.write('\n')
print(json.dumps({s:[{k:v for k,v in r.items() if k not in ['stack_reference_instructions','push_instructions']} for r in rows] for s,rows in results.items()},indent=2))
