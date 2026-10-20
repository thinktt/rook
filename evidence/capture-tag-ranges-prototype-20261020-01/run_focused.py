from pathlib import Path
import os,json,hashlib,subprocess,time,signal,re
E=Path(__file__).resolve().parent
W=Path('/home/legolas/rook2-work/imp2-capture-tag-ranges-20261020-01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected=json.loads((E/'source-after.json').read_text())
assert all(sha(W/n)==h for n,h in expected.items())
receipt=json.loads((E/'generic-build/receipt.json').read_text());assert receipt['rust_flags']==['-C','target-cpu=x86-64'] and receipt['pgo']['mode']=='none'
env=dict(os.environ,RUSTC='/usr/bin/rustc',RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',RUSTFLAGS=' '.join(receipt['rust_flags']),CARGO_ENCODED_RUSTFLAGS=chr(31).join(receipt['rust_flags']),CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4')
assert not any(env.get(k) for k in ['LLVM_PROFILE_FILE','LD_PRELOAD','LD_LIBRARY_PATH'])
argv=['/usr/bin/cargo','test','--offline','--locked','--release','--target','x86_64-unknown-linux-gnu','--jobs','4','--target-dir',str(W/'target/dev-generic'),'--manifest-path',str(W/'Cargo.toml'),'--lib','activity::','--','--test-threads=1']
start=time.monotonic();failure=None
with (E/'focused.stdout').open('xb') as out,(E/'focused.stderr').open('xb') as err:
 q=subprocess.Popen(argv,cwd=W,env=env,stdout=out,stderr=err,start_new_session=True)
 try:code=q.wait(timeout=180)
 except BaseException as exc:
  os.killpg(q.pid,signal.SIGKILL);code=q.wait(timeout=5);failure=type(exc).__name__+': '+str(exc)
row=dict(argv=argv,pid=q.pid,exit_code=code,actual_child_return_observed=True,child_reaped=True,failure=failure,elapsed_wall_s=time.monotonic()-start,environment_overrides={k:env[k] for k in ['RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']},stdout_sha256=sha(E/'focused.stdout'),stderr_sha256=sha(E/'focused.stderr'),source_before_sha256=expected,source_after_sha256={n:sha(W/n) for n in expected})
with (E/'focused-command.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
assert code==0 and failure is None,row
assert row['source_before_sha256']==row['source_after_sha256']
text=(E/'focused.stdout').read_text();passed=re.findall(r'^test (activity::\S+) \.\.\. ok$',text,re.M)
assert len(passed)==10 and len(set(passed))==10,passed
assert sum('::experiment64_' in x for x in passed)==2
assert 'test result: ok. 10 passed; 0 failed;' in text
with (E/'focused-result.json').open('x') as f:json.dump(dict(complete=True,passed_tests=passed,total_executed=10,new_executed=2,inherited_executed=8,full197_not_run=True,source_unchanged=True,actual_cargo_command='focused-command.json'),f,indent=2);f.write('\n')
print(json.dumps(dict(complete=True,total_executed=10,new_executed=2,inherited_executed=8,source_unchanged=True,cargo_pid=q.pid,exit_code=code)))
