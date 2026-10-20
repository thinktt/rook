from pathlib import Path
import hashlib,json,os,sys,subprocess
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def load(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):
    with Path(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def terminal(p):
    t=load(p);assert t['actual_tool_terminal_observed'] is True and t['exit_code']==0
    assert (t.get('terminal_chunk_id') or t.get('chunk_id'))
    return t

def guard(stage):
    plan=load(P/'plan.json');c=load(P/'execution-clearance.json')
    assert sorted(os.sched_getaffinity(0))==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
    assert c['authorized'] is True and c['scope']=='placement-census-no-cpu' and stage in c['authorized_stages']
    assert c['plan_sha256']==sha(P/'plan.json') and c['all_conflicting_jobs_reviewed'] is True
    assert c['helper_sha256']==load(P/'helper-pins.json')
    for p,h in c['dependencies'].items():assert sha(p)==h,p
    for p,h in plan['input_sha256'].items():assert sha(p)==h,p
    for n,h in c['helper_sha256'].items():assert sha(P/n)==h,n
    source=Path(plan['source'])
    for n,h in plan['source71'].items():assert sha(source/n)==h,n
    actual={'Cargo.toml','Cargo.lock'}|{str(p.relative_to(source)) for d in ['src','tools'] for p in (source/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert actual==set(plan['source71'])
    configs=set()
    for parent in [source,*source.parents,Path.home()]:
        for name in ['config','config.toml']:
            q=parent/'.cargo'/name
            if q.is_file():configs.add(q)
    assert {str(q):sha(q) for q in configs}==plan['cargo_configs']
    for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTUP_TOOLCHAIN','LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH','CARGO_HOME','NODE_OPTIONS','PYTHONPATH','PYTHONHOME','CC','CFLAGS','CXX','CXXFLAGS','AR','LDFLAGS']:
        assert not os.environ.get(key),key
    assert not any(k.startswith(('CARGO_PROFILE_','CARGO_TARGET_','CARGO_BUILD_')) for k in os.environ)
    return plan

def child(argv,stem,env=None,cwd=ROOT):
    with Path(str(stem)+'.stdout').open('xb') as a,Path(str(stem)+'.stderr').open('xb') as b:
        p=subprocess.Popen(list(map(str,argv)),cwd=cwd,env=env,stdout=a,stderr=b);code=p.wait()
    record={'argv':list(map(str,argv)),'pid':p.pid,'exit_code':code,'actual_child_return_observed':True}
    write(Path(str(stem)+'.child-terminal.json'),record)
    assert code==0,record
    return record
