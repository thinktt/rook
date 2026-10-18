from pathlib import Path
import json,struct,re,hashlib,difflib
C=Path(__file__).parent
I=json.loads((C/'inputs.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
images={}
for label in ['retained82','default']:
 images[label]={'bytes':Path(I['artifacts'][label]['binary']).read_bytes(),'sections':json.loads((C/f'{label}-section-hashes.json').read_text()),'crate':json.loads((Path(I['artifacts'][label]['build'])/'receipt.json').read_text())['crate']}
def mem(label,addr,n):
 for s in images[label]['sections'].values():
  if s['kind']!='NOBITS' and s['address']!=0 and s['address']<=addr and addr+n<=s['address']+s['size']:
   off=s['offset']+addr-s['address'];return images[label]['bytes'][off:off+n]
 return b''
def location(label,addr):
 raw=mem(label,addr,24)
 if len(raw)!=24:return None
 ptr,n,line,col=struct.unpack('<QQII',raw)
 if not (0<n<=512 and 0<line<100000 and 0<col<100000):return None
 text=mem(label,ptr,n)
 try:text=text.decode('utf-8')
 except UnicodeError:return None
 if not text.endswith('.rs'):return None
 return {'file':text,'normalized_file':text.replace(images[label]['crate'],'<crate>'),'line':line,'column':col,'descriptor24_hex':raw.hex()}
summary={'focused_functions':{},'location_differences':[],'jump_table_differences':[],'unclassified_changed_data':[]}
for fn in ['full_impl','visit_ordinary','visit_q']:
 refs={label:json.loads((C/f'{label}-{fn}-0-references.json').read_text()) for label in images}
 assert len(refs['retained82'])==len(refs['default'])
 changed=[]
 for index,(a,b) in enumerate(zip(refs['retained82'],refs['default'])):
  if a.get('window32_sha256')==b.get('window32_sha256') and a.get('resolved')==b.get('resolved') and a.get('relocation')==b.get('relocation') and a.get('file_pointer')==b.get('file_pointer'):continue
  record={'function':fn,'reference_index':index,'old_instruction':hex(a['instruction']),'new_instruction':hex(b['instruction']),'displayed_target':a['displayed_target']};changed.append(record)
  x=location('retained82',a['target_address']);y=location('default',b['target_address'])
  if x and y:
   record.update({'old':x,'new':y,'same_source_file_after_crate_prefix_mapping':x['normalized_file']==y['normalized_file'],'same_line_column':(x['line'],x['column'])==(y['line'],y['column'])});summary['location_differences'].append(record)
   assert record['same_source_file_after_crate_prefix_mapping']
   if fn=='visit_ordinary':assert record['same_line_column']
  elif fn=='visit_q' and index==18:
   # The preceding native bound is cmp $0x5 / ja; table uses signed 32-bit offsets.
   x=mem('retained82',a['target_address'],24);y=mem('default',b['target_address'],24)
   assert x==y
   record.update({'referenced_entries':6,'entry_bytes':4,'first24_bytes_equal':True,'old_and_new_24_hex':x.hex(),'classification':'32-byte window overlaps following relocated jump table; six referenced entries are unchanged'})
   summary['jump_table_differences'].append(record)
  else:summary['unclassified_changed_data'].append(record)
 summary['focused_functions'][fn]={'references':len(refs['retained82']),'changed_data_reference_count':len(changed),'changed_data_references':changed}
assert not summary['unclassified_changed_data']
# A limited extraction of the inline fast path plus native refresh/output handling.
# Remove only within-visit_q destination offsets; data/GOT annotations stay intact.
fast={}
for label in images:
 text=(C/f'{label}-visit_q-0-normalized.txt').read_text()
 start=text.index('movq 0x84(%rsp),%xmm0\nmovzbl 0x79(%r13),%ecx')
 end=text.index('mov 0x94(%rsp),',start)
 block=text[start:end]
 canon=re.sub(r'(TARGET<rook2::quiescence::<impl rook2::engine::Search<_,H>>::visit_q)\+0x[0-9a-f]+>',r'\1+LOCAL>',block)
 fast[label]={'raw_block':block,'normalized_block':canon,'raw_sha256':sha(block.encode()),'normalized_sha256':sha(canon.encode()),'instruction_count':len(block.splitlines())}
 (C/f'{label}-inline-fast-and-refresh.txt').write_text(block)
assert fast['retained82']['normalized_block']==fast['default']['normalized_block']
# Follow full_impl's two non-GOT Location descriptors to their filename bytes,
# rather than relying only on the containing 32-byte window.
full_locations=[]
a=json.loads((C/'retained82-full_impl-0-references.json').read_text())
b=json.loads((C/'default-full_impl-0-references.json').read_text())
for index,(x,y) in enumerate(zip(a,b)):
 if x['got']:continue
 old_location=location('retained82',x['target_address']);new_location=location('default',y['target_address'])
 assert old_location and old_location==new_location
 full_locations.append({'reference_index':index,'old':old_location,'new':new_location,'descriptor_and_dereferenced_filename_equal':True})
summary['full_impl_non_got_referent_descriptors']=full_locations
summary['inline_fast_and_refresh']={'equal_except_local_branch_offsets':True,'instruction_count':fast['default']['instruction_count'],'normalized_sha256':fast['default']['normalized_sha256'],'scope':'From native base/finishing inputs through strict refresh, full fallback call and Evaluation output assembly, immediately before disposition lower-bound comparison; direct intra-function branch destination offsets removed only. Full function equivalence is not claimed.'}
summary['gate']={'default_full_impl_raw_bytes_equal':True,'full_impl_all_14_data_got_references_equal':summary['focused_functions']['full_impl']['changed_data_reference_count']==0,'default_inline_fast_and_refresh_old_instruction_sequence_restored':True,'no_extra_observer_construction_or_copy_in_compared_evaluation_scopes':True,'whole_visit_q_raw_or_normalized_equal':False,'strict54_and_wire_authorized_gate_met':True,'performance_claim':False}
(C/'focused-referents-deep.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'gate':summary['gate'],'location_differences':len(summary['location_differences']),'jump_table_window_differences':len(summary['jump_table_differences']),'unclassified_changed_data':len(summary['unclassified_changed_data']),'fast_instructions':fast['default']['instruction_count']},indent=2))
