"""Bounded actual-symbol capture; missing private symbols are review gaps, not guessed failures."""
from pathlib import Path
import json,re,subprocess
from capture import HERE,PLAN,guard,sha,write
GROUPS={
 'ordinary-Q-order':r'rook2::(?:ordinary::|quiescence::).*::(?:visit_ordinary|ordering_phase|visit_q)',
 'charge-poll':r'rook2::(?:engine::Search.*::charge_node|timed::.*::work_poll|work_clock::charge_search_unit)',
 'root-run':r'^rook2::run$',
 'public-boundary':r'rook2::(?:timed::|quiescence::|ordinary::|first_iteration::).*::(?:run_work_timed|run_iterations|run_seeded_iterations|continue_subtree|search_subtree|run_session_timed)',
 'full-fast':r'rook2::evaluator::Evaluator.*::(?:full|fast)',
 'node-transitions':r'rook2::evaluator::Node::(?:child|root|null_child)',
}
SUPPORT=re.compile(r'__rust_(?:alloc|dealloc|realloc)|alloc::alloc::|alloc::raw_vec::|drop_in_place<.*(?:Evaluator|Search|PureCache)')
def symbols(path):
 result={}
 for line in path.read_text().splitlines():
  m=re.match(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+([tT])\s+(.+)$',line)
  if m:result.setdefault(int(m[1],16),[]).append({'address':int(m[1],16),'bytes':int(m[2],16),'symbol':m[4]})
 return result

def main():
 guard();identity=json.loads((HERE/'identity.json').read_text());captured={};commands=[];gaps={}
 for side,inp in identity['images'].items():
  image=Path(inp['image']);assert sha(image)==inp['image_sha256'];dest=HERE/side
  table=symbols(dest/'nm-demangled.stdout');selected={};gaps[side]={}
  for group,pattern in GROUPS.items():
   found=[]
   for address,aliases in table.items():
    if any(re.search(pattern,x['symbol']) for x in aliases):
     selected.setdefault(address,dict(aliases[0],aliases=[x['symbol'] for x in aliases],groups=[]))['groups'].append(group);found.append(hex(address))
   gaps[side][group]={'selected_addresses':found,'missing_disposition':'standalone body not emitted: inlining/not-linked remains unresolved' if not found else None}
  reloc={}
  for line in (dest/'relocations.stdout').read_text().splitlines():
   m=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)$',line)
   if m:reloc[int(m[1],16)]=int(m[2],16)
  captured[side]={};support=set();consumed=0
  def capture(address,row):
   nonlocal consumed
   assert 0<row['bytes'];consumed+=row['bytes']
   assert len(captured[side])<PLAN['limits']['maximum_named_bodies_per_image']
   assert consumed<=PLAN['limits']['maximum_selected_text_bytes_per_image']
   name='body-'+hex(address)[2:];outpath=dest/(name+'.asm');errpath=dest/(name+'.stderr')
   cmd=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/objdump','-d','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(address),'--stop-address='+hex(address+row['bytes']),str(image)]
   with outpath.open('xb') as out,errpath.open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
   commands.append({'side':side,'body':name,'argv':cmd,'exit_code':r.returncode,'actual_child_return_observed':True});assert r.returncode==0 and errpath.stat().st_size==0
   captured[side][name]=dict(row,address=hex(address),saved_asm_sha256=sha(outpath))
   return outpath.read_text()
  for address,row in sorted(selected.items()):
   text=capture(address,row)
   for line in text.splitlines():
    m=re.match(r'^\s*[0-9a-f]+:\s+(?:call|jmp)\s+(.*)$',line)
    if not m:continue
    direct=re.match(r'^([0-9a-f]+)\s+<',m[1]);got=re.search(r'#\s*([0-9a-f]+)',m[1])
    target=int(direct[1],16) if direct else reloc.get(int(got[1],16)) if got else None
    if target in table and target not in selected and any(SUPPORT.search(x['symbol']) for x in table[target]):support.add(target)
  assert len(support)<=PLAN['limits']['maximum_one_hop_support_bodies']
  for address in sorted(support):capture(address,dict(table[address][0],aliases=[x['symbol'] for x in table[address]],groups=['one-hop allocator/drop support']))
  assert sha(image)==inp['image_sha256']
 assert all(sha(p)==h for p,h in identity['source_input_sha256'].items())
 write(HERE/'function-capture.json',{'complete':True,'functions':captured,'standalone_scope_resolution':gaps,'commands':commands,'no_absence_or_neutrality_claim':True,'engine_runs':0,'build_runs':0})
 print(json.dumps({'complete':True,'selected_body_counts':{s:len(x) for s,x in captured.items()},'unresolved_source_inlining_requires_review':True}))
if __name__=='__main__':main()
