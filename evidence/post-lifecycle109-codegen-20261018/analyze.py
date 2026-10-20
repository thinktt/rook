from pathlib import Path
import json,re,struct,hashlib,collections,difflib,os
C=Path(__file__).parent;CAP=json.loads((C/'capture.json').read_text());E=C.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class ELF:
 def __init__(self,path,nm):
  self.path=Path(path);self.data=self.path.read_bytes();assert self.data[:6]==b'\x7fELF\x02\x01'
  off=struct.unpack_from('<Q',self.data,40)[0];num,strings=struct.unpack_from('<HH',self.data,60);heads=[struct.unpack_from('<IIQQQQIIQQ',self.data,off+i*64) for i in range(num)];names=self.data[heads[strings][4]:heads[strings][4]+heads[strings][5]]
  self.sections={names[h[0]:].split(b'\0',1)[0].decode():{'type':h[1],'addr':h[3],'offset':h[4],'size':h[5],'link':h[6],'entry':h[9]} for h in heads}
  self.symbols=[]
  for l in Path(nm).read_text().splitlines():
   m=re.match(r'([0-9a-f]+) ([0-9a-f]+) (\S) (.*)',l)
   if m:self.symbols.append({'address':int(m[1],16),'size':int(m[2],16),'type':m[3],'name':m[4]})
  self.relas={};dyn=[]
  if '.dynsym' in self.sections:
   ds=self.sections['.dynsym'];ss=self.sections['.dynstr'];st=self.data[ss['offset']:ss['offset']+ss['size']]
   for off in range(ds['offset'],ds['offset']+ds['size'],24):
    name,_,_,_,_,_=struct.unpack_from('<IBBHQQ',self.data,off);dyn.append(st[name:].split(b'\0',1)[0].decode())
  for k,s in self.sections.items():
   if s['type']==4:
    for off in range(s['offset'],s['offset']+s['size'],24):
     addr,info,addend=struct.unpack_from('<QQq',self.data,off);self.relas[addr]={'type':info&0xffffffff,'symbol':dyn[info>>32] if (info>>32)<len(dyn) else None,'addend':addend}
 def read(self,addr,n):
  for s in self.sections.values():
   if s['type']!=8 and s['addr']>0 and s['addr']<=addr and addr+n<=s['addr']+s['size']:
    off=s['offset']+addr-s['addr'];return self.data[off:off+n]
  return b''
 def symbol(self,addr):
  a=[s for s in self.symbols if s['address']==addr]
  if a:return sorted(a,key=lambda s:('anon.' in s['name'],s['name']))[0]
  return None
 def resolve(self,addr):
  r=self.relas.get(addr)
  if r:
   if r['type']==8:
    s=self.symbol(r['addend']);return {'role':s['name'] if s else 'internal-address:'+hex(r['addend']),'pointer':r['addend'],'relocation':r}
   if r['symbol']:return {'role':r['symbol'],'relocation':r}
  s=self.symbol(addr)
  if s:return {'role':s['name'],'address':addr}
  return {'role':'unresolved:'+hex(addr)}
 def location(self,addr):
  b=self.read(addr,24)
  if len(b)!=24:return None
  p,n,line,col=struct.unpack('<QQII',b)
  if not(1<=n<=4096 and 1<=line<1000000 and 1<=col<10000):return None
  name=self.read(p,n)
  try:name=name.decode()
  except UnicodeDecodeError:return None
  if not name.endswith('.rs'):return None
  return {'filename':name,'suffix':name[name.rfind('/src/')+1:] if '/src/' in name else name,'line':line,'column':col}
DATA={};details={};jumpdata={};metrics={}
oldq=json.loads((E/'controlled-root108-codegen-02-20261018/q-jump-table-referents.json').read_text())['captures'][1]['tables']
for tag,cap in CAP['tags'].items():
 for image in ['engine','probe']:
  path=Path('/home/legolas/rook2/evidence/'+('controlled-root108-generic-build-20261018' if tag=='control' else 'post-lifecycle109-generic-build-20261018')+'/rook2-exact') if image=='engine' else C/(tag+'-probe')
  elf=ELF(path,C/(tag+'-'+image+'-symbols.stdout'));assert sha(elf.data)==(cap['engine_sha256'] if image=='engine' else cap['probe_sha256'])
  rowsbyname={};
  for f in cap['functions'][image]:
   addr=int(f['address'],16);sy=next(s for s in elf.symbols if s['address']==addr and s['name']==f['symbol']);end=addr+sy['size'];rows=[];refs=[];calls=[];normalized=[];qtablemap={}
   body=(C/f['file']).read_text()
   for l in body.splitlines():
    m=re.match(r'\s*([0-9a-f]+):\s*(.*)',l)
    if not m or not(addr<=int(m[1],16)<end):continue
    ip=int(m[1],16);ins=m[2];ref=None
    mm=re.search(r'# ([0-9a-f]+) <.*>',ins)
    if mm and '(%rip)' in ins:
     target=int(mm[1],16);ref={'instruction':hex(ip),'target':hex(target),**elf.resolve(target)};loc=elf.location(target)
     if loc:ref['location']=loc;token='LOCATION:'+loc['suffix']+':'+str(loc['line'])+':'+str(loc['column'])
     elif 'visit_q_impl' in f['symbol']:
      token=None
      for table in oldq:
       count=table['entries'];b=elf.read(target,count*4)
       if len(b)!=count*4:continue
       targets=[hex(target+x-addr) for x in struct.unpack('<'+'i'*count,b)]
       if targets==table['relative_targets_in_actual_q']:
        ref['q_jump_table']={'entries':count,'relative_targets':targets};qtablemap[hex(target)]=ref['q_jump_table'];token='QTABLE:'+str(count)+':'+','.join(targets);break
      if token is None:
       if ref['role'].startswith('unresolved:') or 'anon.' in ref['role']:
        token='DATA32:'+sha(elf.read(target,32));ref['raw_window32_hex']=elf.read(target,32).hex()
       else:token='ROLE:'+re.sub(r'\.llvm\.\d+','',ref['role'])
     else:
      token='ROLE:'+re.sub(r'\.llvm\.\d+','',ref['role']) if not(ref['role'].startswith('unresolved:') or 'anon.' in ref['role']) else 'DATA32:'+sha(elf.read(target,32))
     ins=ins.split('#',1)[0];ins=re.sub(r'-?0x[0-9a-f]+\(%rip\)',lambda _:'RIP<'+token+'>',ins);refs.append(ref)
    else:ins=ins.split('#',1)[0]
    def targetnorm(m):
     a=int(m[1],16)
     if addr<=a<end:return 'LOCAL+'+hex(a-addr)
     return 'TARGET<'+re.sub(r'\.llvm\.\d+','',m[2])+'>'
    ins=re.sub(r'\b([0-9a-f]+) <([^>]*(?:>[^>]*<[^>]*)?)>',targetnorm,ins) if False else re.sub(r'\b([0-9a-f]+) <(.*)>',targetnorm,ins)
    ins=' '.join(ins.split());rows.append({'address':hex(ip),'offset':hex(ip-addr),'text':l.strip(),'normalized':ins});normalized.append(ins)
    if re.match(r'callq?\b',m[2]):
     call={'instruction':hex(ip),'text':l.strip()}
     if ref:call['referent']=ref
     else:
      direct=re.search(r'([0-9a-f]+) <(.*)>',m[2]);call['role']=re.sub(r'\.llvm\.\d+','',direct[2]) if direct else 'unresolved-register-indirect:'+m[2]
     calls.append(call)
   stem=tag+'-'+image+'-'+str(len(rowsbyname));(C/(stem+'-normalized.txt')).write_text('\n'.join(normalized)+'\n');write(C/(stem+'-references.json'),refs)
   item={'symbol':f['symbol'],'address':hex(addr),'bytes':sy['size'],'instructions':len(rows),'static_calls':len(calls),'call_roles':dict(collections.Counter(re.sub(r'\.llvm\.\d+','',(x.get('referent',{}).get('role') or x.get('role'))) for x in calls)),'calls':calls,'stack_operand_instructions':sum('%rsp' in r['normalized'] or '%rbp' in r['normalized'] for r in rows),'first_instructions':[r['text'] for r in rows[:12]],'normalized_file':stem+'-normalized.txt','references_file':stem+'-references.json','raw_bytes_sha256':sha(elf.read(addr,sy['size'])),'normalized_sha256':sha('\n'.join(normalized).encode())}
   rowsbyname[f['symbol']]={'item':item,'rows':rows,'refs':refs}
   if qtablemap:jumpdata[tag+'-'+image]=qtablemap
  DATA[tag+'-'+image]=rowsbyname;metrics[tag+'-'+image]=[x['item'] for x in rowsbyname.values()]
  # Whole lookup objects and decoded panic metadata anchor normalized comparisons.
  for nm in ['rook2::attacks::MASKS','rook2::geometry::KNIGHT_SOURCES']:
   sym=next(s for s in elf.symbols if s['name']==nm);details[tag+'-'+image+':'+nm]={'address':hex(sym['address']),'size':sym['size'],'sha256':sha(elf.read(sym['address'],sym['size']))}
write(C/'resolved-functions.json',metrics);write(C/'resolved-data-objects.json',details);write(C/'q-jump-table-referents.json',jumpdata)
comparisons=[]
for image in ['engine','probe']:
 a=DATA['control-'+image];b=DATA['candidate-'+image]
 for name in sorted(set(a)&set(b)):
  x,y=a[name],b[name];equal=x['item']['normalized_sha256']==y['item']['normalized_sha256'];comparisons.append({'image':image,'symbol':name,'control_bytes':x['item']['bytes'],'candidate_bytes':y['item']['bytes'],'control_instructions':x['item']['instructions'],'candidate_instructions':y['item']['instructions'],'control_calls':x['item']['static_calls'],'candidate_calls':y['item']['static_calls'],'normalized_equal':equal})
  if not equal:
   stem=image+'-'+name.split('::')[-1];(C/(stem+'-normalized.diff')).write_text(''.join(difflib.unified_diff([r['normalized']+'\n' for r in x['rows']],[r['normalized']+'\n' for r in y['rows']],fromfile='control',tofile='candidate')))
write(C/'resolved-owner-comparison.json',comparisons)
# Complete resolved call argument windows, not symbol absence, for root capture and recursive boundaries.
windows={}
for label,funcs in DATA.items():
 selected={}
 for name,x in funcs.items():
  if not(name=='rook2::run' or name=='default_root' or 'CaptureSlot' in name or 'publish_capture' in name):continue
  allwindows=[]
  for i,row in enumerate(x['rows']):
   call=next((c for c in x['item']['calls'] if c['instruction']==row['address']),None)
   if call:
    role=call.get('referent',{}).get('role',call.get('role',''))
    if any(n in role for n in ['capture','publish','visit_ordinary','render','malloc','free','memcpy','root_schedule','Clock','format']):allwindows.append({'resolved_call':call,'operand_window':[r['text'] for r in x['rows'][max(0,i-14):i+9]]})
  selected[name]={'body':x['item'],'call_windows':allwindows}
 windows[label]=selected
write(C/'root-clone-callback-abi-windows.json',windows)
# Save actual type-layout blocks, with field order, independently of nominal sizeof.
layouts={}
for tag in ['control','candidate']:
 text=(C/(tag+'-probe-compile.stdout')).read_text();blocks=re.split(r'(?=print-type-size type: )',text);wanted={}
 for block in blocks:
  if any('type: `'+n+'`:' in block for n in ['rook2::timed::Capture','rook2::timed::Outcome','rook2::post_lifecycle::CaptureSlot<rook2::timed::Capture>','rook2::engine::Search<false>','core::option::Option<core::result::Result<rook2::output::Post, rook2::output::InvalidPv>>']):wanted[block.splitlines()[0]]=block
 layouts[tag]=wanted
write(C/'selected-type-layout-blocks.json',layouts)
write(C/'analysis-summary.json',{'complete':True,'scope':'Bounded actual activeHost main+capture helper, forced NoHost public root, capture fields and recursive scopes; no CPU/neutrality claim','comparison':comparisons,'all_roles_not_dynamic_counts':True,'unknown_register_calls_remain_explicit':True,'q_tables_decoded_against_exact_source_unchanged108_admitted8_7_6_targets':jumpdata,'affinity':sorted(os.sched_getaffinity(0))})
print(json.dumps({'complete':True,'comparison':comparisons},indent=2))
