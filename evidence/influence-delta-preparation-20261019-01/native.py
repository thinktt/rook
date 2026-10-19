#!/usr/bin/env python3
"""Frozen first-run kernel tests; no default engine build or CPU benchmark."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
HERE=Path(__file__).resolve().parent
H=[0,1,2,3,4,5,8,9,10,11,12,13]
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,value):
    with Path(p).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    plan=read(HERE/'native-binding.json')
    assert plan['parent_source_review_complete'] and sha(__file__)==plan['driver_sha256']
    assert sorted(os.sched_getaffinity(0))==H
    assert os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS'])
    trial=Path(plan['trial']);output=Path(plan['output'])
    pins={trial/rel:h for rel,h in plan['source_map'].items()}
    pins.update({Path(p):h for p,h in plan['immutable_inputs'].items()})
    assert all(sha(p)==h for p,h in pins.items())
    output.mkdir()
    save(output/'plan.json',plan)
    rows=[]
    def run(argv,label,env):
        with (output/(label+'.stdout')).open('xb') as stdout,(output/(label+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen(argv,cwd=trial,env=env,stdout=stdout,stderr=stderr)
            save(output/(label+'-launch.json'),dict(argv=argv,pid=child.pid,affinity=H))
            code=child.wait()
        row=dict(argv=argv,pid=child.pid,exit_code=code,stdout_sha256=sha(output/(label+'.stdout')),stderr_sha256=sha(output/(label+'.stderr')))
        save(output/(label+'-terminal.json'),row);rows.append(row)
        assert code==0,(label,code)
    try:
        env=dict(os.environ,RUSTC='/usr/bin/rustc',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',CARGO_NET_OFFLINE='true')
        run(['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--manifest-path',str(trial/'Cargo.toml'),'--target-dir',str(trial/'target/kernel-tests-generic-01'),'--jobs','4','--lib','--bin','rook2-dev','--no-run','--message-format=json'],'native-build',env)
        artifacts=[json.loads(x) for x in (output/'native-build.stdout').read_text().splitlines()]
        artifacts=[a for a in artifacts if a.get('reason')=='compiler-artifact' and a.get('executable') and a.get('profile',{}).get('test')]
        assert len(artifacts)==2
        identities={}
        for artifact in artifacts:
            kind=artifact['target']['kind'];assert kind in [['lib'],['bin']]
            name='lib' if kind==['lib'] else 'dev';assert name not in identities
            expected=plan['expected_passed'][name]
            frozen=output/('rook2-'+name+'-tests-exact')
            shutil.copyfile(artifact['executable'],frozen);frozen.chmod(0o555)
            identity=dict(path=str(frozen),sha256=sha(frozen),cargo_artifact=artifact,expected_passed=expected)
            save(output/(name+'-identity-before.json'),identity)
            run([str(frozen),'--test-threads=1','--nocapture'],name+'-tests',env)
            assert sha(frozen)==identity['sha256']
            assert f'test result: ok. {expected} passed; 0 failed;' in (output/(name+'-tests.stdout')).read_text()
            identities[name]=identity
        assert set(identities)=={'lib','dev'}
        assert all(sha(p)==h for p,h in pins.items())
        save(output/'result.json',dict(complete=True,failure=None,total_tests=sum(plan['expected_passed'].values()),identities=identities,records=rows,source_and_inputs_stable=True,frozen_before_first_test_execution=True,default_engine_runs=0,search_integration=False,cpu_benchmark=False))
        print(json.dumps(dict(complete=True,total_tests=sum(plan['expected_passed'].values()),default_engine_runs=0,cpu_benchmark=False)),flush=True)
    except BaseException as error:
        save(output/'failure.json',dict(error=repr(error),records=rows))
        raise
if __name__=='__main__':main()
