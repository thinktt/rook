#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,struct
P=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
d=load(P/'discovery.json');requests=load(P/'body-request.json');bodyproof=load(P/'bodies.json')
assert bodyproof['complete'] and bodyproof['all_discovery_inputs_unchanged']
images={side:Path(next(p for p in d['pins'] if p.endswith('/rook2-exact') and name in p)) for side,name in [('control','influence-bitsliced-sum-generic-build'),('candidate','influence-direct-fill-generic-build')]}
sections={};raw={};symbols={}
for side,image in images.items():
 raw[side]=image.read_bytes();assert sha(raw[side])==d['pins'][str(image)]
 sections[side]={}
 for line in (P/(side+'-sections.stdout')).read_text().splitlines():
  match=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+',line)
  if match:
   name,kind,addr,offset,size=match.groups();sections[side][name]=dict(kind=kind,address=int(addr,16),offset=int(offset,16),bytes=int(size,16))
 symbols[side]={}
 for line in (P/(side+'-nm.stdout')).read_text().splitlines():
  match=re.match(r'([0-9a-f]+) ([0-9a-f]+) ([tT]) (.+)$',line)
  if match:symbols[side][int(match[1],16)]=dict(bytes=int(match[2],16),name=match[4])
def get(side,address,size):
 s=next(s for s in sections[side].values() if s['kind']=='PROGBITS' and s['address']<=address and address+size<=s['address']+s['bytes'])
 offset=s['offset']+address-s['address'];return raw[side][offset:offset+size]
functionproof={}
for label in ['producer','ensure','ordinary']:
 pair={}
 for side in ['control','candidate']:
  r=next(r for r in requests if r['side']==side and r['label']==label);address=int(r['start'],16);code=get(side,address,r['bytes'])
  text=(P/(side+'-'+label+'.stdout')).read_text();instructions=re.findall(r'^\s*([0-9a-f]+):\s+(.+)$',text,re.M)
  pair[side]=dict(address=hex(address),bytes=r['bytes'],machine_sha256=sha(code),stack_reservations=re.findall(r'\bsub\s+rsp,(0x[0-9a-f]+)',text),pushes=sum(bool(re.match(r'push\s',i)) for _,i in instructions),call_sites=[dict(address=a,operand=i) for a,i in instructions if re.match(r'call\s',i)],instructions=len(instructions))
 assert pair['control']['machine_sha256']==pair['candidate']['machine_sha256']
 functionproof[label]=dict(**pair,complete_machine_bytes_identical=True)
sectionproof={}
for name in ['.text','.rodata','.data.rel.ro','.rela.dyn']:
 pair={};data={}
 for side in ['control','candidate']:
  s=sections[side][name];data[side]=raw[side][s['offset']:s['offset']+s['bytes']];pair[side]=dict(**s,sha256=sha(data[side]))
 different=[i for i,(x,y) in enumerate(zip(data['control'],data['candidate'])) if x!=y]
 sectionproof[name]=dict(**pair,identical=data['control']==data['candidate'],positional_different_bytes=len(different),size_delta=len(data['candidate'])-len(data['control']))
 if name=='.rodata':
  old_prefix=b'/home/legolas/rook2-work/imp2-influence-bitsliced-sum-20261019-01'
  new_prefix=b'/home/legolas/rook2-work/imp2-influence-direct-fill-20261019-01'
  old_norm=data['control'].replace(old_prefix,b'<SOURCE>');new_norm=data['candidate'].replace(new_prefix,b'<SOURCE>')
  sectionproof[name]['source_root_prefix_occurrences']={'control':data['control'].count(old_prefix),'candidate':data['candidate'].count(new_prefix)}
  sectionproof[name]['identical_after_only_exact_source_root_prefix_normalization']=old_norm==new_norm
 if name=='.data.rel.ro':
  words=sorted(set(i//4*4 for i in different));rows=[];unclassified=[]
  prefixes={'control':'/home/legolas/rook2-work/imp2-influence-bitsliced-sum-20261019-01','candidate':'/home/legolas/rook2-work/imp2-influence-direct-fill-20261019-01'}
  def location(side,address):
   pointer,length,line,column=struct.unpack('<QQII',get(side,address,24))
   if not 0<length<256:return None
   filename=get(side,pointer,length).decode('ascii')
   if not filename.endswith('.rs') or any(ord(c)<32 for c in filename):return None
   return dict(pointer=hex(pointer),length=length,line=line,column=column,filename=filename,normalized_filename=filename.replace(prefixes[side],'<SOURCE>'))
  for off in words:
   address=pair['control']['address']+off;classified=False
   for start in [address,address-8,address-16,address-20]:
    try:
     old=location('control',start);new=location('candidate',start)
     if not old or not new or old['normalized_filename']!=new['normalized_filename'] or old['column']!=new['column']:continue
     line_delta=new['line']-old['line']
     if line_delta and not (old['filename'].endswith('src/influence/coherent.rs') and line_delta in [-1,-2] or old['filename'].endswith('src/influence.rs') and line_delta==2):continue
     rows.append(dict(changed_word_address=hex(address),record_start=hex(start),control=old,candidate=new));classified=True;break
    except (AssertionError,StopIteration,UnicodeDecodeError,struct.error):continue
   if not classified:unclassified.append(hex(address))
  sectionproof[name]['changed_words']=len(words);sectionproof[name]['source_location_classified_words']=rows;sectionproof[name]['unclassified_word_addresses']=unclassified
 # Whole-section identity is measured, not required by the scoped mechanism gate.
resolved={}
for side in ['control','candidate']:
 relocs=(P/(side+'-relocations.stdout')).read_text().splitlines()
 def resolve(slot):
  matches=[line for line in relocs if re.match(r'^0*'+format(slot,'x')+r'\s',line)]
  assert len(matches)==1,(side,hex(slot),matches)
  line=matches[0];parts=line.split()
  if 'R_X86_64_RELATIVE' in line:
   address=int(parts[-1],16);return dict(slot=hex(slot),relocation=line,target_address=hex(address),symbol=symbols[side].get(address))
  return dict(slot=hex(slot),relocation=line)
 calls=[]
 for row in functionproof['producer'][side]['call_sites']:
  slot=int(re.search(r'# ([0-9a-f]+)',row['operand'])[1],16);calls.append(dict(**row,resolved=resolve(slot)))
 assert calls  # Count and roles are actual generic facts, not inherited own-PGO values.
 resolved[side]=dict(producer_calls=calls,coherent_true_GOT=resolve(0xe3900),scalar_false_GOT=resolve(0xe3d00))
 assert resolved[side]['coherent_true_GOT']['target_address']=='0x1ff00'
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in d['pins'].items())
result=dict(complete=True,verdict='NO-GO: equivalent generic lowering; park before focused tests/timing',functions=functionproof,sections=sectionproof,calls_resolved=resolved,no_separate_fill_symbol=not any('coherent::fill' in s['name'] for ss in symbols.values() for s in ss.values()),all_inputs_unchanged=True,binutils_children=20,all_binutils_exit0=True,complete_function_count=6,raw_complete_function_bytes=bodyproof['total_raw_bytes'],limits=['No CPU or correctness execution; no own-PGO transfer.','Complete producer/ensure/ordinary only; Q and full run instruction bodies uninspected.','Selected complete function bytes match; whole text/data may differ, so no whole-binary identity or invalid-input panic-output equivalence claim.'])
with (P/'analysis.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(complete=True,verdict=result['verdict'],function_machine_hashes={k:v['candidate']['machine_sha256'] for k,v in functionproof.items()},section_differences={k:dict(size_delta=v['size_delta'],positional_different_bytes=v['positional_different_bytes']) for k,v in sectionproof.items()},data_changed_words=sectionproof['.data.rel.ro']['changed_words'],data_unclassified_words=len(sectionproof['.data.rel.ro']['unclassified_word_addresses']),source_root_only_rodata=sectionproof['.rodata']['identical_after_only_exact_source_root_prefix_normalization'],all_inputs_unchanged=True)))
