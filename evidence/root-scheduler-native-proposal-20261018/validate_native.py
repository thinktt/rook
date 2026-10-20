"""Fresh generic/type/native-test check of the isolated root owner prototype."""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'evidence/root-scheduler-native-validation-20261018'
BUILD = ROOT / 'evidence/root-scheduler-native-build-20261018'
SOURCE = Path('/home/legolas/rook2-work/imp2-root-scheduler-native-validation-20261018')
HELPERS = [0,1,2,3,4,5,8,9,10,11,12,13]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())

def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2); f.write('\n')

def main():
    assert sorted(os.sched_getaffinity(0)) == HELPERS
    assert os.environ['TMPDIR'] == '/home/legolas/rook2-build-tmp'
    assert not OUT.exists() and not BUILD.exists() and not SOURCE.exists()
    prepared = load(HERE/'prepared.json')
    files = load(HERE/'source-manifest.json')['files']
    frozen = Path(prepared['source'])
    assert len(files) == 103 and all(sha(frozen/n) == h for n,h in files.items())
    OUT.mkdir(); SOURCE.mkdir()
    for name, identity in files.items():
        destination = SOURCE/name; destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(frozen/name,destination); assert sha(destination) == identity
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', RUSTC='/usr/bin/rustc',
               RUSTFLAGS='-C target-cpu=x86-64', CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',
               RUSTC_WRAPPER='', RUSTC_WORKSPACE_WRAPPER='', CARGO_NET_OFFLINE='true', CARGO_BUILD_JOBS='4')
    env.pop('LLVM_PROFILE_FILE',None)
    result = dict(complete=False,failure=None,source=str(SOURCE),frozen_source=str(frozen),
                  source_sha256=files,stages=[],affinity=HELPERS,
                  scope='Untimed generic image plus exact native units only; no strict/DIAG/codegen/timing/adoption claim')
    def run(argv,stem):
        with (OUT/(stem+'.stdout')).open('xb') as a,(OUT/(stem+'.stderr')).open('xb') as b:
            child = subprocess.run(argv,cwd=SOURCE,env=env,stdout=a,stderr=b)
        result['stages'].append(dict(command=argv,exit_code=child.returncode,
                                     actual_child_return_observed=True,
                                     stdout_sha256=sha(OUT/(stem+'.stdout')),
                                     stderr_sha256=sha(OUT/(stem+'.stderr'))))
        assert child.returncode == 0, stem+' failed'
    try:
        run([sys.executable,str(SOURCE/'tools/build.py'),'--crate',str(SOURCE),
             '--mode','generic','--bin','rook2','--jobs','4','--output',str(BUILD)],'generic-build')
        receipt = load(BUILD/'receipt.json')
        native = {n:h for n,h in files.items() if n in ['Cargo.toml','Cargo.lock'] or n.startswith('src/')}
        assert len(native)==44 and receipt['source_sha256_before']==receipt['source_sha256_after']==native
        assert receipt['mode']=='generic' and receipt['pgo']['mode']=='none'
        binary = BUILD/'rook2-exact'; shutil.copy2(receipt['binary_output']['path'],binary)
        assert sha(binary)==receipt['binary_output']['sha256']
        result['artifact_sha256']=sha(binary)
        run([sys.executable,str(SOURCE/'tools/archive_build.py'),str(BUILD)],'archive-build')
        run(['/usr/bin/cargo','test','--offline','--locked','--release','--no-run','--message-format=json',
             '--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(SOURCE/'target/root-owner-units'),
             '--manifest-path',str(SOURCE/'Cargo.toml'),'--lib','--bin','rook2-dev'],'unit-build')
        artifacts={}
        for line in (OUT/'unit-build.stdout').read_text().splitlines():
            item=json.loads(line)
            if item.get('reason')=='compiler-artifact' and item['profile']['test'] and item.get('executable'):
                artifacts[item['target']['name']]=Path(item['executable'])
        assert set(artifacts)=={'rook2','rook2-dev'}
        result['units']={}
        for name,count in [('rook2',156),('rook2-dev',2)]:
            target=OUT/'unit-bin'/name/'unit-exact';target.parent.mkdir(parents=True)
            shutil.copy2(artifacts[name],target);identity=sha(target)
            run([str(target),'--test-threads=1'],name+'-tests')
            output=(OUT/(name+'-tests.stdout')).read_text()
            assert re.search(r'test result: ok\. '+str(count)+r' passed; 0 failed;',output)
            assert len(re.findall(r'^test .* \.\.\. ok$',output,re.M))==count and sha(target)==identity
            result['units'][name]=dict(passed=count,binary_sha256=identity)
        assert all(sha(SOURCE/n)==sha(frozen/n)==h for n,h in files.items())
        assert sha(binary)==result['artifact_sha256']
        result['complete']=True
    except BaseException as error:
        result['failure']=f'{type(error).__name__}: {error}'
    finally:
        write(OUT/'verification.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','stages']}),flush=True)
    return 0 if result['complete'] else 1

if __name__=='__main__': sys.exit(main())
