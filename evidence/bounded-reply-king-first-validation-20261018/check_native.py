#!/usr/bin/env python3
"""Freeze and run Q-only endpoint reuse tests; untimed housekeeping validation."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = Path('/tmp/imp2-bounded-reply-king-first85-20261018-zup28rca')
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command,stem,env):
    stdout,stderr = OUT/(stem+'.stdout'),OUT/(stem+'.stderr')
    with stdout.open('xb') as out,stderr.open('xb') as err:
        result = subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=err)
    return dict(command=command,exit_code=result.returncode,stdout_sha256=sha(stdout),stderr_sha256=sha(stderr))


def main():
    before = source_snapshot(ROOT)
    expected = json.loads((Path('/home/legolas/rook2/evidence/bounded-reply-king-first-preparation-20261018/prepared.json')).read_text())['variant_source_sha256']
    assert before == expected
    env = dict(os.environ,RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',
               RUSTC_WRAPPER='',RUSTC_WORKSPACE_WRAPPER='',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4')
    receipt = dict(complete=False,failure=None,source_before=before,stages=[],units={},
                   helper_affinity=sorted(os.sched_getaffinity(0)),driver_sha256=sha(Path(__file__)),
                   scope='Checked-only capped reply king-first on correctedQ85; untimed housekeeping native regression, not performance qualification')
    try:
        command = ['cargo','test','--offline','--locked','--release','--no-run','--message-format=json',
                   '--lib','--bin','rook2-dev','--target','x86_64-unknown-linux-gnu',
                   '--target-dir',str(ROOT/'target/bounded-reply-king-first-tests-20261018'),
                   '--manifest-path',str(ROOT/'Cargo.toml')]
        stage = run(command,'unit-build',env);receipt['stages'].append(stage)
        assert stage['exit_code'] == 0,'integration unit compilation failed'
        artifacts = {}
        for line in (OUT/'unit-build.stdout').read_text().splitlines():
            item = json.loads(line)
            if item.get('reason') == 'compiler-artifact' and item['profile']['test'] and item.get('executable'):
                artifacts[item['target']['name']] = Path(item['executable'])
        assert set(artifacts) == {'rook2','rook2-dev'},'compiled unit inventory'
        for target,count in [('rook2',142),('rook2-dev',2)]:
            frozen = OUT/'unit-bin'/target/'rook2-exact';frozen.parent.mkdir(parents=True)
            shutil.copy2(artifacts[target],frozen);identity=sha(frozen)
            stage=run([str(frozen),'--test-threads=1'],target+'-tests',env);receipt['stages'].append(stage)
            assert stage['exit_code'] == 0,f'{target} integration tests failed'
            match=re.search(r'test result: ok\. (\d+) passed; 0 failed;', (OUT/(target+'-tests.stdout')).read_text())
            assert match and int(match[1]) == count,'unit count'
            assert sha(frozen)==identity,'unit image changed'
            receipt['units'][target]=dict(passed=count,binary_sha256=identity)
        receipt['complete']=True
    except BaseException as error:
        receipt['failure']=f'{type(error).__name__}: {error}'
    finally:
        receipt['source_after']=source_snapshot(ROOT)
        receipt['inputs_stable']=before==receipt['source_after']
        if not receipt['inputs_stable']:receipt.update(complete=False,failure='source changed')
        with (OUT/'native-verification.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(complete=receipt['complete'],failure=receipt['failure'],units=receipt['units'])))
    return 0 if receipt['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
