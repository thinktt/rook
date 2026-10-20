from pathlib import Path
import json,hashlib,struct,re,difflib,collections,os
C=Path(__file__).parent;cap=json.loads((C/'capture.json').read_text());metrics=json.loads((C/'resolved-functions.json').read_text())
ns={'__file__':str(C/'analyze.py')};source=(C/'analyze.py').read_text();exec(source[:source.index('\nDATA={};')],ns);ELF=ns['ELF']
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
proof={};fixed={};byname={}
for tag,c in cap['tags'].items():
 for image in ['engine','probe']:
  path=C/(tag+'-probe') if image=='probe' else C.parent/('controlled-root108-generic-build-20261018' if tag=='control' else 'post-lifecycle109-generic-build-20261018')/'rook2-exact'
  elf=ELF(path,C/(tag+'-'+image+'-symbols.stdout'));items={x['symbol']:x for x in metrics[tag+'-'+image]};rowsout={}
  for f in c['functions'][image]:
   item=items[f['symbol']];addr=int(item['address'],16);end=addr+item['bytes'];rows=[]
   for l in (C/f['file']).read_text().splitlines():
    m=re.match(r'\s*([0-9a-f]+):\s*(.*)',l)
    if m and addr<=int(m[1],16)<end:rows.append({'ip':int(m[1],16),'ins':m[2],'text':l.strip()})
   norms=(C/item['normalized_file']).read_text().splitlines();assert len(norms)==len(rows);refs=json.loads((C/item['references_file']).read_text());verified=[]
   for ref in refs:
    if not any(n in f['symbol'] for n in ['::visit_q_impl','::visit_ordinary','::ordering_phase','::full_impl','::Iteration::next','::Clock::adjustment','::Clock::check']):continue
    i=next(j for j,r in enumerate(rows) if r['ip']==int(ref['instruction'],16));ins=rows[i]['ins'];target=int(ref['target'],16)
    if 'RIP<DATA32:' not in norms[i] and 'RIP<ROLE:internal-address:' not in norms[i]:continue
    if re.match(r'(?:movsd|mulsd|ucomisd|addsd|subsd|divsd)\b',ins):
     raw=elf.read(target,8);assert len(raw)==8;token='FLOAT64_BITS:'+raw.hex();verified.append({'instruction':hex(rows[i]['ip']),'method':'Actual scalar-double operand reads8bytes, not the arbitrary32byte display window','width':8,'raw_hex':raw.hex(),'float':struct.unpack('<d',raw)[0]})
    else:
     m=re.match(r'lea\s+[^,]+,(%\w+)',ins)
     if not m:continue
     reg=m[1]
     a=re.match(r'mov\s+'+re.escape(reg)+r',(?:(0x[0-9a-f]+))?\(%rsp\)',rows[i+1]['ins']);b=re.match(r'movq\s+\$0x1,(0x[0-9a-f]+)\(%rsp\)',rows[i+2]['ins'])
     if not(a and b and int(b[1],16)==(int(a[1],16) if a[1] else 0)+8):continue
     raw=elf.read(target,16);assert len(raw)==16;ptr,n=struct.unpack('<QQ',raw);rel=elf.relas.get(target)
     if rel and rel['type']==8:ptr=rel['addend']
     assert 1<=n<=4096;payload=elf.read(ptr,n);assert len(payload)==n
     text=payload.decode();token='ONE_FORMAT_PIECE:'+payload.hex();verified.append({'instruction':hex(rows[i]['ip']),'method':'Actual format pieces pointer followed by length1 stores; decode the sole16byte pointer/length descriptor and exact payload, not adjacent unused metadata','descriptor':hex(target),'string_address':hex(ptr),'string_bytes':n,'text':text,'pointer_relocation':rel,'argument_window':[r['text'] for r in rows[i:i+5]]})
    norms[i]=re.sub(r'RIP<(?:DATA32:[^>]+|ROLE:internal-address:[^>]+)>',lambda _:'RIP<'+token+'>',norms[i])
   stem=tag+'-'+image+'-'+f['symbol'].split('::')[-1];(C/(stem+'-verified-normalized.txt')).write_text('\n'.join(norms)+'\n');rowsout[f['symbol']]={'normalized':norms,'proof':verified,'metrics':item,'rows':rows}
  byname[tag+'-'+image]=rowsout;proof[tag+'-'+image]={n:x['proof'] for n,x in rowsout.items() if x['proof']}
comparisons=[]
for image in ['engine','probe']:
 a=byname['control-'+image];b=byname['candidate-'+image]
 for name in sorted(set(a)&set(b)):
  x,y=a[name],b[name];equal=x['normalized']==y['normalized'];comparisons.append({'image':image,'symbol':name,'normalized_after_actual_referent_decoding_equal':equal,'control_bytes':x['metrics']['bytes'],'candidate_bytes':y['metrics']['bytes']})
  if not equal:(C/(image+'-'+name.split('::')[-1]+'-verified.diff')).write_text(''.join(difflib.unified_diff([n+'\n' for n in x['normalized']],[n+'\n' for n in y['normalized']],fromfile='control',tofile='candidate')))
write(C/'operand-referent-proof.json',proof);write(C/'verified-owner-comparison.json',comparisons)
q=json.loads((C/'q-jump-table-referents.json').read_text());assert len(q['control-engine'])==len(q['candidate-engine'])==3
assert sorted(q['control-engine'].values(),key=lambda x:x['entries'])==sorted(q['candidate-engine'].values(),key=lambda x:x['entries'])
# Keep every register-indirect NoHost root call explicit with prior operand windows.
regcalls={}
for tag in ['control','candidate']:
 x=byname[tag+'-probe']['default_root'];rows=x['rows'];result=[]
 for i,r in enumerate(rows):
  if re.match(r'call\s+\*%\w+',r['ins']):result.append({'instruction':hex(r['ip']),'call':r['ins'],'prior_operand_window':[n['text'] for n in rows[max(0,i-20):i+1]]})
 regcalls[tag]=result
write(C/'nohost-register-indirect-windows.json',regcalls)
# Same actually linked recursive bodies after resolved operands, without hash-size inference.
for image in ['engine','probe']:
 for suffix in ['visit_q_impl','visit_ordinary','ordering_phase','full_impl']:
  selected=[x for x in comparisons if x['image']==image and x['symbol'].endswith('::'+suffix)];assert len(selected)==1 and selected[0]['normalized_after_actual_referent_decoding_equal']
write(C/'focused-summary.json',{'complete':True,'actual_recursive_normalized_operands_match':True,'comparison':comparisons,'q_engine_all3_admitted8_7_6_tables_match':True,'nohost_indirect_sites_left_explicit_not_counted_as_unknown_callbacks':{k:len(v) for k,v in regcalls.items()},'scope':'Decoded actual operand widths and format payloads supplement unmodified initial32byte display-window analysis. Static body equivalence only, no CPU/retired work/dynamic cost claim.','affinity':sorted(os.sched_getaffinity(0))})
print(json.dumps({'complete':True,'comparison':comparisons,'register_indirect_sites':{k:len(v) for k,v in regcalls.items()}},indent=2))
