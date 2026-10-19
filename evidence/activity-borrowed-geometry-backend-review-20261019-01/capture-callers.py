from pathlib import Path
import hashlib,json,os,subprocess
E=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
d=load(E/'discovery.json');assert all(sha(p)==h for p,h in d['input_pins'].items())
selected=load(E/'caller-selection.json');commands=[]
for side in selected:
 label=side['side'];dirname='activity-borrowed-geometry' if label=='candidate' else 'pressure-value-static'
 image=E.parent/(dirname+'-generic-build-20261019-01/rook2-exact')
 for owner in side['owners']:
  a=owner['address'];end=a+owner['size'];ranges=[('entry',a,min(a+64,end))]
  ranges += [(format(c,'x'),max(a,c-64),min(end,c+16)) for c in owner['direct_full_calls']]
  for tag,start,stop in ranges:
   stem=label+'-caller-'+format(a,'x')+'-'+tag
   argv=['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(start),'--stop-address='+hex(stop),str(image)]
   with (E/(stem+'.stdout')).open('xb') as out,(E/(stem+'.stderr')).open('xb') as err:
    child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
   row={'argv':argv,'pid':child.pid,'actual_child_return_observed':True,'exit_code':code,'owner':owner['symbol'],'owner_address':a,'stdout':stem+'.stdout','stdout_sha256':sha(E/(stem+'.stdout')),'stderr_sha256':sha(E/(stem+'.stderr')),'scope':'Bounded prologue or actual full callsite; whole recursive/run body is uninspected.'}
   (E/(stem+'-command.json')).write_text(json.dumps(row,indent=2)+'\n');assert code==0,row
   commands.append(row)
bodies=load(E/'bodies.json')['bodies'];raw=sum((E/x['stdout']).stat().st_size for x in bodies)+sum((E/x['stdout']).stat().st_size for x in commands)
assert len(bodies)+sum(len(s['owners']) for s in selected)<=12 and raw<=1048576
assert all(sha(p)==h for p,h in d['input_pins'].items())
result={'complete':True,'commands':commands,'unique_symbols_total':len(bodies)+sum(len(s['owners']) for s in selected),'total_raw_disassembly_bytes':raw,'all_inputs_unchanged':True}
(E/'caller-capture.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'complete':True,'commands':len(commands),'unique_symbols_total':result['unique_symbols_total'],'total_raw_disassembly_bytes':raw}))
