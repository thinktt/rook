import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/home/legolas/rook2')
OUT = Path(__file__).resolve().parent
PROTO = Path('/tmp/imp2-activity-widths-20261018')
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    env = dict(os.environ, CARGO_BUILD_JOBS='4', RUSTC_WRAPPER='', RUSTC_WORKSPACE_WRAPPER='', RUSTFLAGS='-C target-cpu=x86-64', CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64')
    subprocess.run(['cargo','generate-lockfile','--offline','--manifest-path',str(OUT/'Cargo.toml')],env=env,check=True)
    files = [OUT/'Cargo.toml',OUT/'Cargo.lock',OUT/'src/lib.rs',OUT/'freeze_run.py',*sorted((OUT/'oracle').glob('*.rs'))]
    before = {str(p):sha(p) for p in files}
    native = source_snapshot(PROTO)
    command = ['cargo','test','--offline','--locked','--release','--no-run','--message-format=json',
               '--target','x86_64-unknown-linux-gnu','--manifest-path',str(OUT/'Cargo.toml')]
    with (OUT/'compile.stdout').open('xb') as stdout,(OUT/'compile.stderr').open('xb') as stderr:
        r = subprocess.run(command,env=env,stdout=stdout,stderr=stderr)
    assert r.returncode == 0
    messages = [json.loads(line) for line in (OUT/'compile.stdout').read_text().splitlines()]
    binaries = [Path(x['executable']) for x in messages if x.get('reason')=='compiler-artifact' and x.get('executable')]
    assert len(binaries) == 1
    original = binaries[0]
    binary = OUT/'rook2-exact'
    with binary.open('xb') as stream: stream.write(original.read_bytes())
    binary.chmod(0o755)
    identity = sha(binary)
    with (OUT/'test.stdout').open('xb') as stdout,(OUT/'test.stderr').open('xb') as stderr:
        r = subprocess.run([str(binary),'--test-threads=1'],stdout=stdout,stderr=stderr,env=env)
    after = {str(p):sha(p) for p in files}
    record=dict(schema='rook2-activity-widths-differential-v1',compile_command=command,
                environment_overrides={k:env[k] for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS']},
                input_sha256_before=before,input_sha256_after=after,
                native_source_before=native,native_source_after=source_snapshot(PROTO),
                test_executable=str(binary),test_sha256_before=identity,test_sha256_after=sha(binary),
                test_exit=r.returncode,helper_affinity=sorted(os.sched_getaffinity(0)),
                old_oracle_origin='Prefix of our own prior coordinate-based activity/influence modules before cfg(test); not fixtures or other-engine code',
                current_root_source_sha256={name:sha(ROOT/'src'/name) for name in ['activity.rs','influence.rs']},
                cases=10000,scope='Constructed admitted placements including broad promotion/check domains; full normalized influence bytes, activity fields and relation counts',
                profile='Release-optimized test harness with panic unwinding; not production timing')
    record['pass']=(r.returncode == 0 and before==after and record['native_source_before']==record['native_source_after'] and identity==sha(binary))
    (OUT/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(output=str(OUT),passed=record['pass'])))
    return 0 if record['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
