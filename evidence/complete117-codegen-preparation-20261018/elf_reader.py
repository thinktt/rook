# Inert ELF reader reused verbatim from closed109 analyze.py class; no binary read on import.
from pathlib import Path
import struct,re
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
