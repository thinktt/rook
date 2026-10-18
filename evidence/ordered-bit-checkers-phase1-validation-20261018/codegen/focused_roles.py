from pathlib import Path
import json,hashlib,struct,re,difflib
C=Path(__file__).parent;I=json.loads((C/'inputs.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();images={}
for label,a in I['artifacts'].items():images[label]={'bytes':Path(a['binary']).read_bytes(),'sections':json.loads((C/f'{label}-section-hashes.json').read_text()),'crate':json.loads((Path(a['build'])/'receipt.json').read_text())['crate']}
def read(label,addr,n):
 for section in images[label]['sections'].values():
  if section['kind']!='NOBITS' and section['address']!=0 and section['address']<=addr and addr+n<=section['address']+section['size']:
   off=section['offset']+addr-section['address'];return images[label]['bytes'][off:off+n]
 return b''
def location(label,addr):
 raw=read(label,addr,24)
 if len(raw)!=24:return None
 ptr,n,line,col=struct.unpack('<QQII',raw)
 if not (0<n<512 and 0<line<100000 and 0<col<100000):return None
 try:text=read(label,ptr,n).decode('utf8')
 except UnicodeError:return None
 if not text.endswith('.rs'):return None
 return {'file':text,'normalized_file':text.replace(images[label]['crate'],'<crate>'),'line':line,'column':col}
tables={}
for name in ['rook2::attacks::MASKS','rook2::geometry::KNIGHT_SOURCES','rook2::geometry::ATTACK_RAYS']:
 pair={}
 for label in images:
  matches=[]
  for line in (C/f'{label}-nm-demangled.txt').read_text().splitlines():
   m=re.match(r'([0-9a-f]+) ([0-9a-f]+) [A-Za-z] (.*)',line)
   if m and m[3]==name:matches.append(m)
  assert len(matches)==1,(name,label,len(matches));m=matches[0];addr,n=int(m[1],16),int(m[2],16);pair[label]={'address':addr,'bytes':n,'sha256':sha(read(label,addr,n))}
 pair['equal_bytes']=pair['control']['sha256']==pair['phase1']['sha256'];assert pair['equal_bytes'];tables[name]=pair
summary={'exact_shared_tables':tables,'default_function_comparison':{},'role_map':{'control_mailbox_cap2':{'address':'0x1f7f0','size':3800,'production_callers':['generate_legal','legal_replies_up_to_two','visit_q/check_routes inline']},'control_mailbox_cap1':{'address':'0x3b6b0','size':3781,'production_callers':['public attacked inlined callers including visit_q safety']},'phase1_mailbox_cap1':{'address':'0x3bc30','size':3781},'phase1_mailbox_cap2_with_route_output':{'symbol':'check_routes','address':'0x20130','size':3824},'phase1_ordered_cap2':{'symbol':'AttackBits::ordered_attackers','address':'0x19ae0','size':1554},'warning':'Generated occurrence-order function-comparison paired old cap2 with new cap1 because both demangle identically. That pair is invalid for semantic comparison; this caller-based role map supersedes it.'}}
for fn,old_occ in [('full_impl',0),('visit_ordinary',0),('attacked',0),('find_attackers',1)]:
 old=(C/f'control-{fn}-{old_occ}-normalized.txt').read_text();new=(C/f'phase1-{fn}-0-normalized.txt').read_text();anon=lambda s:re.sub(r'anon\.[0-9a-f]+\.\d+','ANON',s)
 eq=anon(old)==anon(new)
 a=json.loads((C/f'control-{fn}-{old_occ}-references.json').read_text());b=json.loads((C/f'phase1-{fn}-0-references.json').read_text());details=[]
 assert len(a)==len(b),(fn,len(a),len(b))
 for index,(x,y) in enumerate(zip(a,b)):
  if x['got'] and y['got']:
   details.append({'index':index,'kind':'GOT','old_referent':x['resolved'],'new_referent':y['resolved'],'same_resolved_name':x['resolved']==y['resolved'],'dynamic_binding':str(x['resolved']).startswith('unresolved')});continue
  loc1=location('control',x['target_address']);loc2=location('phase1',y['target_address'])
  details.append({'index':index,'kind':'data','old_displayed':x['displayed_target'],'new_displayed':y['displayed_target'],'window32_equal':x.get('window32_sha256')==y.get('window32_sha256'),'old_location':loc1,'new_location':loc2,'same_location_after_crate_prefix':bool(loc1 and loc2 and {k:loc1[k] for k in ['normalized_file','line','column']}=={k:loc2[k] for k in ['normalized_file','line','column']})})
 summary['default_function_comparison'][fn]={'instruction_sequence_equal_after_link_and_anonymous_label_mapping':eq,'reference_count':len(a),'references':details,'normalization_limit':'Anonymous IDs are renamed, not semantically erased. Data payload/window/decoded location records remain available; opaque allocation/panic aggregates and dynamic bindings are not exhaustively pointer-resolved.'}
 (C/f'role-matched-{fn}.diff').write_text(''.join(difflib.unified_diff(anon(old).splitlines(True),anon(new).splitlines(True),fromfile='control-role',tofile='phase1-role')))
assert summary['default_function_comparison']['full_impl']['instruction_sequence_equal_after_link_and_anonymous_label_mapping']
assert summary['default_function_comparison']['visit_ordinary']['instruction_sequence_equal_after_link_and_anonymous_label_mapping']
assert summary['default_function_comparison']['attacked']['instruction_sequence_equal_after_link_and_anonymous_label_mapping']
assert summary['default_function_comparison']['find_attackers']['instruction_sequence_equal_after_link_and_anonymous_label_mapping']
(C/'focused-role-and-data-review.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'shared_tables_exact':{k:v['control']['bytes'] for k,v in tables.items()},'role_corrected_normalized_matches':{k:v['instruction_sequence_equal_after_link_and_anonymous_label_mapping'] for k,v in summary['default_function_comparison'].items()},'full_impl_data_locations':[x for x in summary['default_function_comparison']['full_impl']['references'] if x['kind']=='data']},indent=2))
