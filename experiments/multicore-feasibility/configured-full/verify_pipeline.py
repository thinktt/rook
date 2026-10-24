#!/usr/bin/env python3
"""Focused configuration lane; no PGO or performance study is launched here."""
import argparse
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

from common import HERE, ROOT, HELPERS, read, sha, write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True)
    assert set(os.sched_getaffinity(0))==HELPERS
    env=dict(os.environ,PATH='/usr/bin:/bin',CARGO_TARGET_DIR=str(out/'test-target'))
    env.pop('LLVM_PROFILE_FILE',None)
    source={str(p):sha(p) for p in [ROOT/'Cargo.toml',ROOT/'Cargo.lock',*sorted((ROOT/'src').rglob('*.rs'))]}
    state=dict(complete=False,source=source,stages=[])
    write(out/'pipeline.json',state)

    def stage(name,argv,limit,tests=None):
        state['active']=name;write(out/'pipeline.json',state)
        started=time.monotonic_ns()
        with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try: code=child.wait(timeout=limit)
            except BaseException:
                os.killpg(child.pid,signal.SIGINT)
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL);child.wait()
                raise
        row=dict(stage=name,argv=argv,pid=child.pid,exit=code,elapsedNs=time.monotonic_ns()-started,
                 stdoutSha256=sha(out/(name+'.stdout')),stderrSha256=sha(out/(name+'.stderr')))
        state['stages'].append(row);write(out/'pipeline.json',state)
        print(name,code,flush=True);assert code==0,(name,code)
        if tests is not None:
            assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',
                (out/(name+'.stdout')).read_text())==[(str(tests),'0')]
            row['passedTests']=tests

    try:
        for name,selector,count in [('budgets','evaluator::parallel_tests',8),
                                    ('lifecycle','evaluator::lifecycle_tests',3)]:
            stage(name,['/usr/bin/cargo','test','--lib',selector,'--','--test-threads=1'],300,count)
        stage('parser',['/usr/bin/cargo','test','--bin','rook2',
              'tests::thread_argument_requires_a_positive_representable_integer','--','--exact'],300,1)
        stage('build',['/usr/bin/python3',str(ROOT/'tools/build.py'),'--mode','generic',
              '--bin','rook2','--jobs','4','--output',str(out/'build')],300)
        receipt=read(out/'build/receipt.json');built=Path(receipt['binary_output']['path'])
        image=out/'rook2-generic';shutil.copy2(built,image)
        assert sha(image)==receipt['binary_output']['sha256']
        stage('verify',['/usr/bin/python3',str(HERE/'verify.py'),'--engine',str(image),
                       '--output',str(out/'verification')],450)
        assert all(sha(Path(p))==h for p,h in source.items())
        state.update(complete=True,active=None,binary=dict(path=str(image),sha256=sha(image),bytes=image.stat().st_size))
        write(out/'pipeline.json',state)
        print('configuration verification complete; source freeze/PGO are separate',flush=True)
    except BaseException as error:
        state['failure']=repr(error);write(out/'pipeline.json',state);raise


if __name__=='__main__':main()
