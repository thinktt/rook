from pathlib import Path
import json,re,difflib
p=Path('/home/legolas/rook2/evidence/placement-pure-cache-codegen-review-20261018-01');a=json.loads((p/'bounded-analysis.json').read_text())
def ins(side,name):
 out=[]
 for line in (p/side/(name+'.asm')).read_text().splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
  if m:out.append((int(m[1],16),m[2],m[3]))
 return out
def canonical_calls(x):
 out=[]
 for c in x['static_calls']:
  if c['target_symbols']:out.append(c['target_symbols'])
  else:
   op=c['operands'];comment=re.search(r'<([^<>]+)>',op)
   out.append(comment[1] if comment and not comment[1].startswith('_GLOBAL_OFFSET_TABLE_') else op.split('#')[0].strip())
 return out
names=['visit_q_impl','visit_ordinary_impl','ordering_phase','charge_node','activity::compute','king_pressure','shelter::compute','pawn_terms::compute','pawn_structure::fresh_with_order','pawn_progress::selected']
report={}
for key in names:
 pair={}
 for side in ['control','candidate']:
  matches=[(name,x) for name,x in a['metrics'][side].items() if key in x['symbol']];assert len(matches)==1
  name,x=matches[0];pair[side]={'body':name,'metadata':x,'instructions':ins(side,name)}
 l,r=pair['control'],pair['candidate'];li,ri=l['instructions'],r['instructions'];assert len(li)==len(ri)
 differences=[];pcrel=[];branches=[]
 for index,((la,lm,lo),(ra,rm,ro)) in enumerate(zip(li,ri))):
  lb=lo.split('#')[0].strip();rb=ro.split('#')[0].strip()
  if lm!=rm:differences.append({'index':index,'control':lm+' '+lo,'candidate':rm+' '+ro});continue
  if '[rip' in lb or '[rip' in rb:
   if lo!=ro:pcrel.append({'index':index,'control':lo,'candidate':ro})
   continue
  if re.match(r'^[0-9a-f]+ <',lb):
   ltarget=int(lb.split()[0],16);rtarget=int(rb.split()[0],16)
   lc=ltarget-int(l['metadata'].get('address','0'),16) if False else None
   if lm.startswith('j'):
    startl=li[0][0];startr=ri[0][0]
    if ltarget-startl!=rtarget-startr or lb[lb.find('<'):]!=rb[rb.find('<'):]:branches.append({'index':index,'control':lo,'candidate':ro})
   elif lb[lb.find('<'):]!=rb[rb.find('<'):]:differences.append({'index':index,'control':lo,'candidate':ro})
   continue
  if lb!=rb:differences.append({'index':index,'control':lm+' '+lo,'candidate':rm+' '+ro})
 report[key]={'control_body':l['body'],'candidate_body':r['body'],'same_named_static_call_sequence':canonical_calls(l['metadata'])==canonical_calls(r['metadata']),'control_static_call_sequence':canonical_calls(l['metadata']),'candidate_static_call_sequence':canonical_calls(r['metadata']),'non_PCREL_nonlocal_operand_changes':differences,'PCREL_sites_needing_referent_interpretation':pcrel,'branch_name_or_relative_target_changes':branches,'bytes':{'control':l['metadata']['bytes'],'candidate':r['metadata']['bytes']},'rsp_subtractions':{'control':l['metadata']['rsp_subtractions'],'candidate':r['metadata']['rsp_subtractions']}}
with (p/'referent-review.json').open('x') as f:json.dump({'complete':True,'scope':'Offline interpretation of existing bounded captures only; all PC-relative sites retained explicitly, no payload equality assumed','regions':report},f,indent=2);f.write('\n')
for k,v in report.items():print(k,'same static calls',v['same_named_static_call_sequence'],'operand deltas',len(v['non_PCREL_nonlocal_operand_changes']),'PCREL',len(v['PCREL_sites_needing_referent_interpretation']),'branch',len(v['branch_name_or_relative_target_changes']))
print('root total reservation',hex(0x13000+0x498),hex(0x13000+0x4b8),0x13000+0x498,0x13000+0x4b8)
