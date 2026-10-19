"""Authorized BASELINE40 only; no candidate or engine execution."""
from pathlib import Path
import hashlib,json,os,re,subprocess
E=Path(__file__).resolve().parent
B=E.parent/'pressure-value-static-generic-build-20261019-01'
EXPECTED='adbf66a39b710bc0f44db2ceb99cac7b823fc02962e4c23a2d6ec12dfa92d664'
FN='rook2::influence::Influence::build_coherent'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def save(name,obj):
    with (E/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
r=load(B/'receipt.json');t=load(B/'tool-terminal.json')
assert t['actual_tool_terminal_observed'] and t['exit_code']==0 and t['terminal_chunk_id']=='151f6b'
assert r['mode']=='generic' and r['pgo']['mode']=='none' and r['cargo_exit_code']==0
assert r['source_sha256_before']==r['source_sha256_after'] and len(r['source_sha256_before'])==49
assert r['tool_sha256_before']==r['tool_sha256_after'] and len(r['tool_sha256_before'])==23
assert sha(B/'rook2-exact')==r['binary_output']['sha256']==EXPECTED
assert r['rust_flags']==['-C','target-cpu=x86-64']
pins={str(E/'capture-baseline.py'):sha(E/'capture-baseline.py')}
for name in ['rook2-exact','receipt.json','tool-terminal.json','frozen-image.json','archive-receipt.json','build.stderr']:
    pins[str(B/name)]=sha(B/name)
for name,digest in (r['source_sha256_before']|r['tool_sha256_before']).items():
    p=B/'source-before'/name;assert sha(p)==digest;pins[str(p)]=digest
for name in ['rustc','cargo']:
    p=Path('/usr/bin')/name;digest=sha(p);assert digest==r['toolchain'][name+'_executable_sha256'];pins[str(p)]=digest
for name in ['nm','objdump','readelf','size']:pins['/usr/bin/'+name]=sha('/usr/bin/'+name)
verbose=(B/'build.stderr').read_text();line=[l for l in verbose.splitlines() if 'Running ' in l and '--crate-type bin' in l and 'src/bin/rook2.rs' in l]
assert len(line)==1 and '-C lto=thin ' in line[0] and '-C codegen-units=1 ' in line[0]
commands=[]
def run(argv,stem):
    with (E/(stem+'.stdout')).open('xb') as out,(E/(stem+'.stderr')).open('xb') as err:
        child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
    row={'argv':argv,'pid':child.pid,'actual_child_return_observed':True,'exit_code':code,'stdout':stem+'.stdout','stdout_sha256':sha(E/(stem+'.stdout')),'stderr_sha256':sha(E/(stem+'.stderr'))}
    save(stem+'-command.json',row);assert code==0,row;commands.append(row)
for tool in ['nm','objdump','readelf','size']:run(['/usr/bin/'+tool,'--version'],tool+'-version')
for tool,args,stem in [('nm',['--numeric-sort','--print-size','--demangle'],'baseline-nm'),('nm',['--numeric-sort','--print-size'],'baseline-nm-mangled'),('size',['-A'],'baseline-size'),('readelf',['-SW'],'baseline-sections'),('readelf',['-rW'],'baseline-relocations')]:
    run(['/usr/bin/'+tool,*args,str(B/'rook2-exact')],stem)
symbols=[]
for line in (E/'baseline-nm.stdout').read_text().splitlines():
    match=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',line)
    if match and match[3]==FN:symbols.append((int(match[1],16),int(match[2],16),match[3]))
assert len(symbols)==1
address,size,name=symbols[0]
run(['/usr/bin/objdump','-d','-l','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(address),'--stop-address='+hex(address+size),str(B/'rook2-exact')],'baseline-complete-build-coherent')
assert (E/'baseline-complete-build-coherent.stdout').stat().st_size<=1048576
assert all(sha(p)==digest for p,digest in pins.items())
save('baseline-capture.json',{'complete':True,'baseline_only':True,'candidate_unbound':True,'image_sha256':EXPECTED,'source_graph':hashlib.sha256(json.dumps(r['source_sha256_before']|r['tool_sha256_before'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'producer':{'address':address,'bytes':size,'symbol':name,'raw_body':'baseline-complete-build-coherent.stdout'},'commands':commands,'raw_disassembly_bytes':(E/'baseline-complete-build-coherent.stdout').stat().st_size,'input_pins':pins,'all_inputs_unchanged':True,'engine_build_test_profile_runs':0})
print(json.dumps({'complete':True,'baseline_only':True,'commands':len(commands),'function_address':hex(address),'function_bytes':size,'raw_disassembly_bytes':(E/'baseline-complete-build-coherent.stdout').stat().st_size,'all_inputs_unchanged':True}))
