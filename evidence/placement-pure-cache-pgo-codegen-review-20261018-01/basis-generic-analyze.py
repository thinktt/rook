"""Offline static metrics, preserving actual operands; these are not runtime counts or an ABI proof."""
from pathlib import Path
import difflib,json,re
from capture import HERE,guard,write,sha

def rows(path):
 result=[]
 for line in path.read_text().splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
  if m:result.append((int(m[1],16),m[2],m[3]))
 return result

def main():
 guard();cap=json.loads((HERE/'function-capture.json').read_text());result={};signatures={}
 identity=json.loads((HERE/'identity.json').read_text());assert all(sha(p)==h for p,h in identity['source_input_sha256'].items())
 for side,funcs in cap['functions'].items():
  result[side]={};signatures[side]={};reloc={};symbols={}
  for line in (HERE/side/'relocations.stdout').read_text().splitlines():
   m=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)$',line)
   if m:reloc[int(m[1],16)]=int(m[2],16)
  for line in (HERE/side/'nm-demangled.stdout').read_text().splitlines():
   m=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+\S\s+(.+)$',line)
   if m:symbols.setdefault(int(m[1],16),[]).append(m[2])
  for name,meta in funcs.items():
   path=HERE/side/(name+'.asm');assert sha(path)==meta['saved_asm_sha256'];ins=rows(path);start=int(meta['address'],16);end=start+meta['bytes'];calls=[];tails=[];sig=[]
   for address,mn,op in ins:
    body,_,comment=op.partition('#');normalized=body.strip()
    if '[rip' in body:normalized=re.sub(r'\[rip[^]]*\]','[PCREL '+comment.strip()+']',normalized)
    direct=re.match(r'^([0-9a-f]+)\s+<(.+)>$',body.strip());got=re.search(r'#\s*([0-9a-f]+)',op);target=None
    if direct:
     target=int(direct[1],16);normalized='LOCAL+'+hex(target-start) if start<=target<end else direct[2]
    elif got:target=reloc.get(int(got[1],16))
    transfer={'address':hex(address),'operands':op,'target_address':hex(target) if target is not None else None,'target_symbols':symbols.get(target),'self_body_target':target is not None and start<=target<end}
    if mn=='call':calls.append(transfer)
    if mn=='jmp' and not transfer['self_body_target']:tails.append(transfer)
    sig.append(mn+' '+normalized)
   canonical=re.sub(r'::h[0-9a-f]+$','',meta['symbol']);signatures[side].setdefault(canonical,[]).append({'body':name,'signature':sig})
   with (HERE/side/(name+'.signature.txt')).open('x') as f:f.write('\n'.join(sig)+'\n')
   result[side][name]={'symbol':meta['symbol'],'aliases':meta['aliases'],'groups':meta['groups'],'bytes':meta['bytes'],'instructions':len(ins),'rsp_subtractions':[op for _,mn,op in ins if mn=='sub' and op.startswith('rsp,')],'rsp_additions':[op for _,mn,op in ins if mn=='add' and op.startswith('rsp,')],'stack_references':[{'address':hex(a),'instruction':mn+' '+op} for a,mn,op in ins if '[rsp' in op or '[rbp' in op],'static_calls':calls,'static_tail_transfers':tails,'all_memory_operands':[{'address':hex(a),'instruction':mn+' '+op} for a,mn,op in ins if '[' in op],'first_instructions':[mn+' '+op for _,mn,op in ins[:12]]}
 comparisons={}
 for index,key in enumerate(sorted(set(signatures['control'])|set(signatures['candidate']))):
  left=signatures['control'].get(key,[]);right=signatures['candidate'].get(key,[])
  entry={'control_bodies':[x['body'] for x in left],'candidate_bodies':[x['body'] for x in right]}
  if len(left)==len(right)==1:
   diff='\n'.join(difflib.unified_diff(left[0]['signature'],right[0]['signature'],fromfile='control/'+left[0]['body'],tofile='candidate/'+right[0]['body'],lineterm=''))+'\n'
   name='comparison-'+str(index)+'.diff'
   with (HERE/name).open('x') as f:f.write(diff)
   entry.update(signature_equal=left[0]['signature']==right[0]['signature'],diff=name)
  else:entry['comparison']='No arbitrary pairing: monomorph identity/source/callers require manual review.'
  comparisons[key]=entry
 write(HERE/'bounded-analysis.json',{'complete':True,'metrics':result,'comparisons':comparisons,'limitations':['Static calls/transfers are not dynamic counts.','RSP adjustment is not total stack highwater; pushes, alignment, nested calls and spills require review.','Signatures preserve memory displacements and referents but do not prove runtime equality.','No symbol absence, allocation neutrality, layout neutrality or cache correctness conclusion.']})
 print(json.dumps({'complete':True,'sides':{k:len(v) for k,v in result.items()},'manual_review_required':True}))
if __name__=='__main__':main()
