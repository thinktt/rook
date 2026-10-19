import hashlib,json,subprocess,re
from pathlib import Path
P=Path(__file__).resolve().parent
R=Path('/home/legolas/rook2')
B=R/'evidence/influence-bitsliced-sum-pgo-use-build-20261019-01'
OLD=R/'evidence/influence-bitsliced-sum-pgo-backend-review-20261019-01'
IMAGE=B/'rook2-exact'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 q=P/n;assert not q.exists();q.write_text(json.dumps(d,indent=2)+'\n')
assert sha(IMAGE)=='36251ecf12cfdc9437c9bfc5b7a571c1992471bee611cab024fc692ac79e91b2'
inputs=[IMAGE,B/'receipt.json',B/'frozen-image.json',B/'tool-terminal.json',OLD/'candidate-nm.stdout',OLD/'candidate-nm-mangled.stdout',OLD/'candidate-nm-command.json',OLD/'candidate-nm-mangled-command.json',OLD/'objdump-version.stdout',OLD/'objdump-version-command.json',Path('/usr/bin/objdump'),Path(__file__)]
inputs+=sorted(q for q in (B/'source-before').rglob('*') if q.is_file())
pins={str(q):sha(q) for q in inputs}
nm=(OLD/'candidate-nm.stdout').read_text(); mangled=(OLD/'candidate-nm-mangled.stdout').read_text()
rows=[]
for line in nm.splitlines():
 m=re.match(r'([0-9a-f]+) ([0-9a-f]+) [tT] (.*visit_ordinary_impl.*)$',line)
 if m:rows.append(m)
assert len(rows)==1
m=rows[0];start=int(m[1],16);size=int(m[2],16)
assert start==0x31370 and size==0x6d39
assert any('hae010e8d5293be7cE' in x and x.startswith(m[1]) for x in mangled.splitlines())
assert len([(x) for x in (B/'source-before').rglob('*') if x.is_file()])==72
write('input-pins.json',pins)
argv=['/usr/bin/objdump','-d','-l','--demangle','-Mintel',f'--start-address={start}',f'--stop-address={start+size}',str(IMAGE)]
with (P/'ordinary.stdout').open('xb') as out,(P/'ordinary.stderr').open('xb') as err:
 child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
record={'argv':argv,'pid':child.pid,'actual_child_return_observed':True,'exit_code':code,'stdout_sha256':sha(P/'ordinary.stdout'),'stderr_sha256':sha(P/'ordinary.stderr')}
write('ordinary-command.json',record)
assert code==0
assert (P/'ordinary.stdout').stat().st_size<=1048576
assert all(sha(Path(q))==h for q,h in pins.items())
write('capture.json',{'complete':True,'body_count':1,'complete_body':True,'symbol':m[3],'mangled_suffix':'hae010e8d5293be7cE','address':hex(start),'bytes':size,'raw_disassembly_bytes':(P/'ordinary.stdout').stat().st_size,'command':record,'all_inputs_unchanged':True,'pins':len(pins),'clone_scope':'Only one linked sized visit_ordinary_impl symbol in actual own43 PGO image. Normal WireHost image, not diagnostic/NoHost probe. Callgrind suffix2 identity is not inferred from a demangled name.','limits':['No native/search/test/profile execution','One complete body; no timed/Q/ordering_phase body captured','No dynamic cost or removable-copy frequency estimate']})
print(json.dumps({'complete':True,'raw_bytes':(P/'ordinary.stdout').stat().st_size,'size':size,'all_inputs_unchanged':True}))
