"""Finite own37 read-only windows; four/0x400/16KiB strict cap."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
P=Path(__file__).resolve().parent
E=P.parent
IMAGE=E/'coherent-influence-masks-pgo-use-build-20261019-01/rook2-exact'
SOURCE=IMAGE.parent/'source-before'
OLD=E/'coherent-influence-masks-pgo-backend-review-20261019-01'
EXPECTED='54be65520cbe5e3324e94021ff49eed096027fd871f17150c97bdfb21a3c023f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
a=argparse.ArgumentParser();a.add_argument('start');a.add_argument('length');args=a.parse_args()
start,length=int(args.start,16),int(args.length,16)
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
assert 0<length<=0x400
# Only actual saved own37 activity::compute or default full_impl extents.
assert any(lo<=start and start+length<=hi for lo,hi in [(0x121d0,0x14535),(0x38030,0x39378)])
assert not (P/'failure.json').exists()
previous=json.loads((P/'state.json').read_text()) if (P/'state.json').exists() else {'windows':[],'disassembly_bytes':0}
assert len(previous['windows'])<4
old=json.loads((OLD/'discovery.json').read_text())
paths=[IMAGE,SOURCE/'src/activity.rs',SOURCE/'src/evaluator.rs',SOURCE/'src/ordinary.rs',SOURCE/'src/timed.rs',SOURCE/'src/session.rs',SOURCE/'src/bin/rook2.rs',IMAGE.parent/'receipt.json',OLD/'discovery.json',OLD/'candidate-nm.stdout',OLD/'objdump-version.stdout',Path('/usr/bin/objdump'),Path(__file__)]
pins={str(p):sha(p) for p in paths}
assert pins[str(IMAGE)]==EXPECTED
assert pins['/usr/bin/objdump']==old['input_pins']['/usr/bin/objdump']
if previous['windows']:assert previous['input_pins']==pins
stem='window-'+hex(start)[2:]+'-'+hex(length)[2:]
argv=['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(start),'--stop-address='+hex(start+length),str(IMAGE)]
remaining=16384-previous['disassembly_bytes'];written=0;capped=False
with (P/(stem+'.stdout')).open('xb') as out,(P/(stem+'.stderr')).open('xb') as err:
 child=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=err)
 try:
  while True:
   chunk=child.stdout.read(min(65536,max(1,remaining-written+1)))
   if not chunk:break
   if written+len(chunk)>remaining:
    out.write(chunk[:max(0,remaining-written)]);written=remaining;capped=True;child.terminate();break
   out.write(chunk);written+=len(chunk)
 finally:child.stdout.close();code=child.wait()
row={'start':hex(start),'length':length,'argv':argv,'pid':child.pid,'exit_code':code,'stdout':str(P/(stem+'.stdout')),'stderr':str(P/(stem+'.stderr')),'stdout_bytes':written,'cap_hit':capped}
put(stem+'-command.json',row)
if code!=0 or capped:
 put('failure.json',row);raise RuntimeError(row)
assert pins=={str(p):sha(p) for p in paths}
state={'windows':previous['windows']+[row],'disassembly_bytes':previous['disassembly_bytes']+written,'input_pins':pins,'all_inputs_unchanged':True}
put('state-'+str(len(state['windows']))+'.json',state)
(P/'state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({'complete':True,'window':row,'total_windows':len(state['windows']),'total_disassembly_bytes':state['disassembly_bytes']}))
