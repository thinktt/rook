"""Authorized candidate43 static capture; baseline files read-only."""
from pathlib import Path
import hashlib,json,os,re,subprocess
E=Path(__file__).resolve().parent
B=E.parent/'influence-bitsliced-sum-generic-build-20261019-01'
EXPECTED='ea057f6a4a0c57ddc3ed35667d01363c7f2fc68d2de1d2fa745d2ba16f6e4a23'
FN='rook2::influence::Influence::build_coherent'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def save(name,obj):
    with (E/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
r=load(B/'receipt.json');t=load(B/'tool-terminal.json')
assert t['actual_tool_terminal_observed'] and t['exit_code']==0 and t['terminal_chunk_id']=='8c4328' and t['session_id']==45113
assert r['mode']=='generic' and r['pgo']['mode']=='none' and r['cargo_exit_code']==0
assert r['source_sha256_before']==r['source_sha256_after'] and len(r['source_sha256_before'])==49
assert r['tool_sha256_before']==r['tool_sha256_after'] and len(r['tool_sha256_before'])==23
assert sha(B/'rook2-exact')==r['binary_output']['sha256']==EXPECTED
assert r['rust_flags']==['-C','target-cpu=x86-64']
pins={str(E/'capture-candidate.py'):sha(E/'capture-candidate.py')}
freeze=E.parent/'influence-bitsliced-sum-parent-review-20261019-01/source-freeze.json'
q=load(freeze);pins[str(freeze)]=sha(freeze)
assert q['source_graph']=='e89dcb3315e4d8aaa5089ec445d0a7d0bda7f0928001c502c6343899a5195aa5'
assert q['files_sha256']==r['source_sha256_before']|r['tool_sha256_before']
assert t['source_freeze_sha256']==sha(freeze)
control=load(E.parent/'pressure-value-static-generic-build-20261019-01/receipt.json')
for key in ['mode','target_triple','target_cpu','jobs','toolchain','build_effective_environment']:
    assert r[key]==control[key],key
assert r['tool_sha256_before']==control['tool_sha256_before']
assert sorted(f for f,h in r['source_sha256_before'].items() if h!=control['source_sha256_before'][f])==['src/attacks.rs','src/influence/coherent.rs','src/influence/coherent_tests.rs']
for p,h in load(E/'baseline-capture.json')['input_pins'].items():
    assert sha(p)==h;pins[p]=h
for name in ['baseline-closure.json','baseline-capture.json','baseline-analysis.json','baseline-source-map.json','baseline-review.md','baseline-complete-build-coherent.stdout']:
    pins[str(E/name)]=sha(E/name)
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
for tool in ['nm','objdump','readelf','size']:run(['/usr/bin/'+tool,'--version'],'candidate-'+tool+'-version')
for tool,args,stem in [('nm',['--numeric-sort','--print-size','--demangle'],'candidate-nm'),('nm',['--numeric-sort','--print-size'],'candidate-nm-mangled'),('size',['-A'],'candidate-size'),('readelf',['-SW'],'candidate-sections'),('readelf',['-rW'],'candidate-relocations')]:
    run(['/usr/bin/'+tool,*args,str(B/'rook2-exact')],stem)
symbols=[]
for line in (E/'candidate-nm.stdout').read_text().splitlines():
    match=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',line)
    if match and (match[3]==FN or 'BitSums' in match[3]):symbols.append((int(match[1],16),int(match[2],16),match[3]))
assert 1<=len(symbols)<=4 and sum(name==FN for _,_,name in symbols)==1
bodies=[]
for address,size,name in symbols:
    stem='candidate-complete-'+format(address,'x')
    run(['/usr/bin/objdump','-d','-l','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(address),'--stop-address='+hex(address+size),str(B/'rook2-exact')],stem)
    bodies.append({'address':address,'bytes':size,'symbol':name,'raw_body':stem+'.stdout'})
rawbytes=sum((E/b['raw_body']).stat().st_size for b in bodies)
assert rawbytes<=1048576
assert all(sha(p)==digest for p,digest in pins.items())
save('candidate-capture.json',{'complete':True,'candidate_only':True,'image_sha256':EXPECTED,'source_graph':q['source_graph'],'bodies':bodies,'commands':commands,'raw_disassembly_bytes':rawbytes,'input_pins':pins,'all_inputs_unchanged':True,'baseline_namespace_unchanged':True,'generic_settings_match':True,'engine_build_test_profile_runs':0})
print(json.dumps({'complete':True,'candidate_only':True,'commands':len(commands),'bodies':bodies,'raw_disassembly_bytes':rawbytes,'all_inputs_unchanged':True}))
