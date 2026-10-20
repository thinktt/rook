"""Bounded actual own40/own43 PGO static comparison. No engine/build/merge."""
from pathlib import Path
import hashlib,json,re,os,subprocess
E=Path(__file__).resolve().parent;ROOT=E.parent
SIDES={'control':('pressure-value-static','c3166899f9380812b0fcb114d613021ba308699e46b0f7de48ffafaf4ff0e5a7','7f79529773da099060bb1b73a1d92a7d03b52b228bc3d754607b76980981c75a'),
'candidate':('influence-bitsliced-sum','36251ecf12cfdc9437c9bfc5b7a571c1992471bee611cab024fc692ac79e91b2','132fc1fd85d81592173cdc97a22cfb223616b97e33a4a270c968331f8558a93f')}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
def save(n,x):
    with (E/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
assert os.sched_getaffinity(0)<={0,1,2,3,4,5,8,9,10,11,12,13}
assert os.environ['PATH']=='/usr/bin:/bin' and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
pins={str(E/'capture.py'):sha(E/'capture.py')};receipts={};bindings={};normalized_env={}
for side,(name,image,profile) in SIDES.items():
    B=ROOT/(name+'-pgo-use-build-20261019-01');I=ROOT/(name+'-pgo-instrumented-build-20261019-01');T=ROOT/(name+'-pgo-training-20261019-01');P=ROOT/(name+'-pgo-preparation-20261019-01')
    r=load(B/'receipt.json');ir=load(I/'receipt.json');tr=load(T/'training.json');v=load(T/'verification.json');receipts[side]=r
    assert r['mode']=='generic' and r['pgo']['mode']=='profile-use' and r['cargo_exit_code']==0
    assert r['source_sha256_before']==r['source_sha256_after']==ir['source_sha256_before']==ir['source_sha256_after']==tr['engine_source_sha256']
    assert r['tool_sha256_before']==r['tool_sha256_after']==ir['tool_sha256_before']==ir['tool_sha256_after']
    assert len(r['source_sha256_before'])==49 and len(r['tool_sha256_before'])==23
    assert sha(B/'rook2-exact')==image==r['binary_output']['sha256']
    assert sha(I/'receipt.json')==tr['instrumented_build_receipt']['sha256']
    assert ir['binary_output']['sha256']==tr['instrumented_engine_sha256']
    assert r['pgo']['input_sha256_before']==r['pgo']['input_sha256_after']
    assert sha(Path(r['pgo']['profile']))==profile==tr['profile_sha256']==v['merged_profile_sha256']==v['independent_profile_sha256']
    assert v['complete'] and v['independent_remerge_byte_identical'] and v['independent_remerge_exit_code']==0
    assert all(v[k]==54 for k in ['strict_replays','original_checkReplay_count','raw_training_protocol_cases','raw_profiles_independently_hashed'])
    assert len(tr['raw_profiles_sha256'])==54 and tr['complete']
    assert sha(T/'training.json')==v['training_record_sha256']==r['pgo']['input_sha256_before'][str(T/'training.json')]
    stages={}
    for stage,path in [('instrumented',I/'tool-terminal.json'),('training',T/'tool-terminal.json'),('verification',T/'verify-tool-terminal.json'),('use',B/'tool-terminal.json')]:
        term=load(path);assert term['exit_code']==0 and term.get('terminal_chunk_id');pins[str(path)]=sha(path);stages[stage]=term
    for stage in ['instrumented','use']:
        path=P/(stage+'-stage.json');meta=load(path);assert meta['complete'] and meta['missing_or_stale_profile_warnings']==0;pins[str(path)]=sha(path)
        for unit,options in meta['effective_rustc_options'].items():
            assert options['opt-level']=='3' and options['panic']=='abort' and options['codegen-units']=='1' and options['debuginfo']=='1' and options['target-cpu']=='x86-64'
            if unit=='src/bin/rook2.rs':assert options['lto']=='thin'
    for path in [B/'receipt.json',B/'rook2-exact',B/'frozen-image.json',B/'archive-receipt.json',B/'build.stderr',I/'receipt.json',I/'frozen-image.json',T/'training.json',T/'verification.json',Path(r['pgo']['profile'])]:pins[str(path)]=sha(path)
    for f,h in (r['source_sha256_before']|r['tool_sha256_before']).items():
        path=B/'source-before'/f;assert sha(path)==h;pins[str(path)]=h
    log=(B/'build.stderr').read_text();binary=[l for l in log.splitlines() if 'Running ' in l and '--crate-type bin' in l and 'src/bin/rook2.rs' in l]
    assert len(binary)==1 and '-C lto=thin ' in binary[0] and '-C codegen-units=1 ' in binary[0] and ('profile-use='+r['pgo']['profile']) in binary[0]
    assert not re.search(r'(no profile data|mismatched.*profile|out[- ]of[- ]date.*profile)',log,re.I)
    normalized_env[side]={k:(value.replace(r['pgo']['profile'],'<OWN_PROFILE>') if isinstance(value,str) and k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS'] else value) for k,value in r['build_effective_environment'].items()}
    bindings[side]={'image':image,'profile':profile,'source_graph':hashlib.sha256(json.dumps(r['source_sha256_before']|r['tool_sha256_before'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'actual_stages':stages,'verified_original_training':54,'independent_remerge_byte_identical':True,'missing_stale_profile_warnings':0}
a,b=receipts['control'],receipts['candidate']
for k in ['mode','target_triple','target_cpu','jobs','toolchain']:assert a[k]==b[k],k
assert normalized_env['control']==normalized_env['candidate']
assert a['tool_sha256_before']==b['tool_sha256_before']
assert sorted(f for f,h in a['source_sha256_before'].items() if h!=b['source_sha256_before'][f])==['src/attacks.rs','src/influence/coherent.rs','src/influence/coherent_tests.rs']
freeze=ROOT/'influence-bitsliced-sum-parent-review-20261019-01/source-freeze.json';q=load(freeze);pins[str(freeze)]=sha(freeze)
assert q['files_sha256']==b['source_sha256_before']|b['tool_sha256_before'] and q['source_graph']==bindings['candidate']['source_graph']
for name in ['rustc','cargo']:
    p=Path('/usr/bin')/name;digest=sha(p);assert digest==b['toolchain'][name+'_executable_sha256'];pins[str(p)]=digest
for name in ['nm','objdump','readelf','size']:pins['/usr/bin/'+name]=sha('/usr/bin/'+name)
commands=[]
def run(argv,stem):
    with (E/(stem+'.stdout')).open('xb') as out,(E/(stem+'.stderr')).open('xb') as err:
        child=subprocess.Popen(argv,stdout=out,stderr=err);code=child.wait()
    row={'argv':argv,'pid':child.pid,'actual_child_return_observed':True,'exit_code':code,'stdout':stem+'.stdout','stdout_sha256':sha(E/(stem+'.stdout')),'stderr_sha256':sha(E/(stem+'.stderr'))}
    save(stem+'-command.json',row);assert code==0,row;commands.append(row)
for tool in ['nm','objdump','readelf','size']:run(['/usr/bin/'+tool,'--version'],tool+'-version')
bodies=[]
for side,(name,_,_) in SIDES.items():
    image=ROOT/(name+'-pgo-use-build-20261019-01/rook2-exact')
    for tool,args,stem in [('nm',['--numeric-sort','--print-size','--demangle'],'nm'),('nm',['--numeric-sort','--print-size'],'nm-mangled'),('size',['-A'],'size'),('readelf',['-SW'],'sections'),('readelf',['-rW'],'relocations')]:run(['/usr/bin/'+tool,*args,str(image)],side+'-'+stem)
    selected=[]
    for line in (E/(side+'-nm.stdout')).read_text().splitlines():
        match=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',line)
        if match and ('rook2::influence::Influence::build_coherent' in match[3] or 'BitSums' in match[3] or 'rook2::influence::coherent::build' in match[3]):selected.append((int(match[1],16),int(match[2],16),match[3]))
    assert 1<=len(selected)<=4
    for address,size,name in selected:
        stem=side+'-complete-'+format(address,'x')
        run(['/usr/bin/objdump','-d','-l','-w','-C','-Mintel','--no-show-raw-insn','--start-address='+hex(address),'--stop-address='+hex(address+size),str(image)],stem)
        bodies.append({'side':side,'address':address,'bytes':size,'symbol':name,'stdout':stem+'.stdout'})
rawbytes=sum((E/body['stdout']).stat().st_size for body in bodies);assert rawbytes<=1048576
assert all(sha(p)==h for p,h in pins.items())
save('capture.json',{'complete':True,'bindings':bindings,'bodies':bodies,'commands':commands,'raw_disassembly_bytes':rawbytes,'effective_environment_only_profile_paths_normalized':True,'all_other_compiler_settings_equal':True,'source_delta_exact_three_files':True,'input_pins':pins,'all_inputs_unchanged':True,'no_native_compiler_test_profile_merge_runs':True})
print(json.dumps({'complete':True,'commands':len(commands),'bodies':bodies,'raw_disassembly_bytes':rawbytes,'all_inputs_unchanged':True}))
