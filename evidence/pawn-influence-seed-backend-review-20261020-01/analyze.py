from pathlib import Path
import json,re,hashlib
P=Path(__file__).resolve().parent
request=json.loads((P/'body-request.json').read_text());results=[]
for row in request:
 label=row['side']+'-'+row['role'];lines=(P/(label+'.stdout')).read_text().splitlines();raw={};ins=[]
 for l in lines:
  fields=l.split('\t')
  if len(fields)<2 or not re.fullmatch(r'\s*[0-9a-f]+:',fields[0]):continue
  addr=int(fields[0].strip()[:-1],16);bs=bytes.fromhex(fields[1])
  for offset,b in enumerate(bs):assert addr+offset not in raw;raw[addr+offset]=b
  if len(fields)>2 and fields[2].strip():ins.append({'address':hex(addr),'instruction':fields[2].strip()})
 start=int(row['start'],16);assert set(raw)==set(range(start,start+row['bytes'])),label
 calls=[i for i in ins if i['instruction'].startswith('call')]
 frame=[i for i in ins[:12] if re.search(r'sub\s+\$0x[0-9a-f]+,%rsp',i['instruction'])]
 results.append(dict(**row,instruction_rows=len(ins),code_sha256=hashlib.sha256(bytes(raw[a] for a in range(start,start+row['bytes']))).hexdigest(),frame_subtractions=frame,static_rsp_memory_reference_rows=sum('(%rsp' in i['instruction'] for i in ins),calls=calls,mnemonics=sorted(set(i['instruction'].split()[0] for i in ins))))
sections={}
for side in ['control','candidate']:
 sections[side]={}
 for l in (P/(side+'-size.stdout')).read_text().splitlines():
  s=l.split()
  if len(s)==3 and s[0].startswith('.') and s[1].isdigit():sections[side][s[0]]=int(s[1])
 commands=[json.loads(x.read_text()) for x in P.glob('*-command.json')]
 assert all(x['exit_code']==0 for x in commands)
 pins=json.loads((P/'runtime-input-pins.json').read_text())
 for name,h in pins.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
out={'complete':True,'bodies':results,'section_sizes':sections,'binutils_commands':len(commands),'all_binutils_exit_zero':True,'all_input_pins_unchanged':True,'input_pins':len(pins),'captures':json.loads((P/'capture.json').read_text()),'whole_binary_code_or_rodata_equivalence_claimed':False}
(P/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'metrics':[{k:r[k] for k in ['side','role','bytes','instruction_rows','frame_subtractions','static_rsp_memory_reference_rows']} for r in results],'binutils_commands':len(commands),'pins':len(pins),'section_delta':{x:sections['candidate'][x]-sections['control'][x] for x in ['.text','.rodata','.data.rel.ro']},'all_input_pins_unchanged':True}))
