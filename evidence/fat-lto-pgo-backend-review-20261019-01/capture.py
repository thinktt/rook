"""Inert until parent release; bounded own-image static tools, no engine runs."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess
P=Path(__file__).resolve().parent
E=P.parent
H={0,1,2,3,4,5,8,9,10,11,12,13}
CAP=128*1024
BODY_CAP=12
D={'control':E/'ordinary-projected-bits-pgo-use-build-20261018-01',
   'candidate':E/'fat-lto-pgo-use-build-20261019-01'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x') as f: json.dump(value,f,indent=2);f.write('\n')
def load(path): return json.loads(path.read_text())
def terminal(row):
    assert row['actual_tool_terminal_observed'] is True and row['exit_code']==0
    assert (row.get('terminal_chunk_id') or row.get('chunk_id') or '').strip()
def normalized_environment(receipt):
    env=dict(receipt['build_effective_environment'])
    profile=receipt['pgo']['profile']
    for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS']:
        assert isinstance(env[key],str) and env[key].count(profile)==1
        env[key]=env[key].replace(profile,'<OWN_PROFILE>')
    return env

def preflight():
    assert not (P/'capture-failure.json').exists(), 'Preserved failure requires parent review'
    plan=load(P/'plan.json')
    assert plan['execution_authorized'] is True and plan['candidate_sha256']
    assert os.sched_getaffinity(0)<=H
    assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
    assert plan['required_input_pins'] and plan['actual_terminals']
    pins={str(P/'plan.json'):sha(P/'plan.json'),str(P/'capture.py'):sha(P/'capture.py'),str(P/'analyze.py'):sha(P/'analyze.py')}
    for path,h in plan['required_input_pins'].items():
        assert sha(Path(path))==h; pins[path]=h
    for row in plan['actual_terminals']: terminal(row)
    receipts={}
    for side,base in D.items():
        receipt=load(base/'receipt.json');receipts[side]=receipt
        assert receipt['cargo_exit_code']==0 and receipt['mode']=='generic'
        pgo=receipt['pgo'];assert pgo['mode']=='profile-use'
        profile=Path(pgo['profile']);training_path=Path(pgo['training_record'])
        assert receipt['rust_flags']==['-C','target-cpu=x86-64','-C','profile-use='+str(profile),'-C','llvm-args=-pgo-warn-missing-function']
        assert pgo['input_sha256_before']==pgo['input_sha256_after'] and pgo['inputs_unchanged']
        assert set(pgo['input_sha256_before'])=={str(profile),str(training_path)}
        for path,h in pgo['input_sha256_before'].items():
            assert sha(Path(path))==h;pins[path]=h
        assert sha(profile)==plan['profile_sha256'][side]
        training=load(training_path)
        assert training['schema']=='rook2-pgo-training-v1' and training['complete'] is True
        assert training['engine_source_sha256']==receipt['source_sha256_before']
        assert training['target_triple']==receipt['target_triple']
        assert training['base_rust_flags']==['-C','target-cpu=x86-64']
        assert training['profile_sha256']==sha(profile) and len(training['raw_profiles_sha256'])==54
        inst_path=Path(training['instrumented_build_receipt']['path'])
        assert sha(inst_path)==training['instrumented_build_receipt']['sha256'];pins[str(inst_path)]=sha(inst_path)
        inst=load(inst_path)
        assert inst['cargo_exit_code']==0 and inst['pgo']['mode']=='instrumented'
        assert inst['source_sha256_before']==inst['source_sha256_after']==receipt['source_sha256_before']
        assert inst['tool_sha256_before']==receipt['tool_sha256_before']
        assert inst['toolchain']==receipt['toolchain']
        assert receipt['source_sha256_before']==receipt['source_sha256_after']
        assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
        assert len(receipt['source_sha256_before'])==46
        assert len(receipt['tool_sha256_before'])==23
        image=base/'rook2-exact'; expected=plan[side+'_sha256']
        assert sha(image)==expected==receipt['binary_output']['sha256']
        for path in [base/'receipt.json',image,base/'tool-terminal.json']:
            pins[str(path)]=sha(path)
        terminal(load(base/'tool-terminal.json'))
        for name,h in {**receipt['source_sha256_before'],**receipt['tool_sha256_before']}.items():
            path=base/'source-before'/name;assert sha(path)==h;pins[str(path)]=h
    a,b=receipts['control'],receipts['candidate']
    assert a['tool_sha256_before']==b['tool_sha256_before']
    for key in ['mode','target_triple','target_cpu','jobs','toolchain']:
        assert a[key]==b[key],key
    assert normalized_environment(a)==normalized_environment(b)
    assert a['pgo']['profile']!=b['pgo']['profile']
    assert plan['profile_sha256']['control']!=plan['profile_sha256']['candidate']
    old,new=a['source_sha256_before'],b['source_sha256_before']
    assert set(new)==set(old)
    assert [k for k in old if old[k]!=new[k]]==['Cargo.toml']
    old_manifest=(D['control']/'source-before/Cargo.toml').read_text()
    new_manifest=(D['candidate']/'source-before/Cargo.toml').read_text()
    assert old_manifest.count('lto = "thin"')==1
    assert new_manifest==old_manifest.replace('lto = "thin"','lto = "fat"')
    for side,setting in [('control','thin'),('candidate','fat')]:
        log=D[side]/'build.stderr';pins[str(log)]=sha(log)
        binary_lines=[line for line in log.read_text().splitlines() if '--crate-type bin' in line and 'src/bin/rook2.rs' in line and 'Running ' in line]
        assert len(binary_lines)==1
        assert '-C lto='+setting+' ' in binary_lines[0]
        assert '-C codegen-units=1 ' in binary_lines[0]
        assert '-C profile-use='+receipts[side]['pgo']['profile']+' ' in binary_lines[0]
        assert not re.search(r'no profile data available|profile data.*out of date|function control flow change detected|hash mismatch',log.read_text(),re.I)
    for tool in ['nm','objdump','readelf','size']:
        path=Path('/usr/bin')/tool;pins[str(path)]=sha(path)
    return pins

def symbols(text):
    return [{'address':int(m[1],16),'bytes':int(m[2],16),'name':m[3]}
        for line in text.splitlines()
        if (m:=re.match(r'^([0-9a-f]+) ([0-9a-f]+) [tT] (.*)$',line))]

def run(argv,stem,remaining=None):
    stdout=P/(stem+'.stdout');stderr=P/(stem+'.stderr')
    with stdout.open('xb') as out,stderr.open('xb') as err:
        process=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=err)
        written=0; capped=False
        try:
            while True:
                limit=65536 if remaining is None else min(65536,max(1,remaining-written+1))
                data=process.stdout.read(limit)
                if not data: break
                if remaining is not None and written+len(data)>remaining:
                    out.write(data[:max(0,remaining-written)]);written=remaining
                    capped=True;process.terminate();break
                out.write(data);written+=len(data)
        finally:
            process.stdout.close();code=process.wait()
    record={'argv':argv,'pid':process.pid,'exit_code':code,'stdout':str(stdout),
            'stderr':str(stderr),'stdout_bytes':written,'disassembly_cap_exhausted':capped}
    put(P/(stem+'-command.json'),record)
    if code!=0 or capped:
        put(P/'capture-failure.json',record)
        raise RuntimeError(record)
    return record

parser=argparse.ArgumentParser()
parser.add_argument('stage',choices=['discover','windows'])
parser.add_argument('--window',action='append',default=[],
    help='side:hex_start:hex_length; explicit bounded range in one named function')
args=parser.parse_args()
pins=preflight()
if args.stage=='discover':
    assert not args.window
    commands=[];all_symbols={}
    for tool in ['nm','objdump','readelf','size']:
        commands.append(run(['/usr/bin/'+tool,'--version'],tool+'-version'))
    for side,base in D.items():
        image=str(base/'rook2-exact')
        commands.append(run(['/usr/bin/nm','--numeric-sort','--print-size',image],side+'-nm-mangled'))
        commands.append(run(['/usr/bin/nm','--numeric-sort','--print-size','--demangle',image],side+'-nm'))
        commands.append(run(['/usr/bin/size','-A',image],side+'-size'))
        commands.append(run(['/usr/bin/readelf','-rW',image],side+'-relocations'))
        commands.append(run(['/usr/bin/readelf','-SW',image],side+'-sections'))
        all_symbols[side]=symbols((P/(side+'-nm.stdout')).read_text())
    assert all(sha(Path(path))==h for path,h in pins.items())
    put(P/'discovery.json',{'complete':True,'commands':commands,'symbols':all_symbols,'input_pins':pins})
else:
    assert args.window
    discovery=load(P/'discovery.json');assert discovery['complete']
    # Discovery plan is immutable while subsequent windows are selected.
    assert discovery['input_pins']==pins
    previous=load(P/'window-state.json') if (P/'window-state.json').exists() else {'windows':[],'disassembly_bytes':0}
    requests=[]
    for spec in args.window:
        side,start,length=spec.split(':');assert side in D
        start,length=int(start,16),int(length,16);assert 0<length<=0x800
        found=[r for r in discovery['symbols'][side] if r['address']<=start<r['address']+r['bytes']]
        assert len(found)==1;row=found[0];assert start+length<=row['address']+row['bytes']
        hot=('rook2::activity::' in row['name'] or row['name']=='rook2::run' or any(x in row['name'] for x in ['rook2::evaluator::','::full_impl','::visit_ordinary','::visit_q_impl','::visit_quiescence','::main']))
        assert hot,'No allocator or unrelated body capture'
        requests.append({'side':side,'start':start,'length':length,'symbol':row,
            'starts_at_entry':start==row['address'],'whole_body':start==row['address'] and length==row['bytes']})
    selected={(r['side'],r['symbol']['address']) for r in previous['windows']+requests}
    assert len(selected)<=BODY_CAP
    total=previous['disassembly_bytes'];results=[]
    for row in requests:
        stem=row['side']+'-window-'+format(row['start'],'x')+'-'+format(row['length'],'x')
        command=run(['/usr/bin/objdump','-d','-w','-C','-Mintel','--no-show-raw-insn',
            '--start-address='+hex(row['start']),'--stop-address='+hex(row['start']+row['length']),str(D[row['side']]/'rook2-exact')],stem,CAP-total)
        total+=command['stdout_bytes'];results.append({**row,'command':command})
    assert total<=CAP and all(sha(Path(path))==h for path,h in pins.items())
    state={'windows':previous['windows']+results,'disassembly_bytes':total,'named_bodies':len(selected),'caps':{'named_bodies':BODY_CAP,'disassembly_bytes':CAP},'all_inputs_unchanged':True}
    # Retain each state, then update only this review-owned selection index.
    put(P/('window-state-'+str(len(state['windows']))+'.json'),state)
    (P/'window-state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({'complete':True,'stage':args.stage,'engine_runs':0}))
