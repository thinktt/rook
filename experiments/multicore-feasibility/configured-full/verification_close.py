#!/usr/bin/env python3
"""Read-only closure of the saved generic configuration controls."""
import argparse
from pathlib import Path
import re

from common import HERE, ROOT, SPEC, audit, train, read, sha, write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path)
    parser.add_argument('--output',type=Path,default=HERE/'verification-proof.json')
    args=parser.parse_args();raw=args.raw.resolve()
    pipeline=read(raw/'pipeline.json');build=read(raw/'build/receipt.json')
    proof=read(raw/'verification/result.json')
    assert pipeline['complete'] and pipeline['active'] is None and 'failure' not in pipeline
    assert [s['stage'] for s in pipeline['stages']]==['budgets','lifecycle','parser','build','verify']
    assert build['outcome']=='build-succeeded-with-stable-input-snapshot' and build['pgo']['mode']=='none'
    assert build['source_sha256_before']==build['source_sha256_after']==train.source_snapshot(ROOT)
    for name,h in build['source_sha256_before'].items():assert sha(raw/'build/source-before'/name)==h
    assert all(sha(Path(p))==h for p,h in pipeline['source'].items())
    assert proof['complete'] and proof['engineSha256']==build['binary_output']['sha256']==sha(Path(proof['engine']))
    assert len(proof['cli'])==13 and len(proof['oneCpu'])==2
    bindings={}
    tests=[]
    for stage in pipeline['stages']:
        assert stage['exit']==0 and not Path(f'/proc/{stage["pid"]}').exists()
        for stream in ['stdout','stderr']:
            p=raw/(stage['stage']+'.'+stream)
            assert sha(p)==stage[stream+'Sha256'];bindings[str(p)]=sha(p)
        if 'passedTests' in stage:
            names=re.findall(r'^test ([^\n]+) \.\.\. ok$',(raw/(stage['stage']+'.stdout')).read_text(),re.M)
            assert len(names)==stage['passedTests'];tests.extend(names)
    assert len(tests)==len(set(tests))==12
    for p,h in proof['inputSha256'].items():assert sha(Path(p))==h
    for row in proof['cli']:
        if row['exit']==0:
            import json
            wanted=min(row['requestedThreads'],2,len(row['permittedCpus']))
            assert row['configuredThreads']==wanted
            assert json.loads(row['stdout'])==dict(requested_threads=row['requestedThreads'],configured_threads=wanted)
            assert row['stderr']==''
        else:assert row['exit']==1 and row['stdout']=='' and row['stderr']
    workload=next(c for c in read(SPEC/'workloads.json')['cases'] if c['id']=='profile-08')
    oracle=next(c for c in read(SPEC/'replay-oracle.json')['cases'] if c['id']=='profile-08')
    assert [row['requestedThreads'] for row in proof['oneCpu']]==[1,2]
    for row in proof['oneCpu']:
        assert row['configuredThreads']==1 and row['exit']==0 and row['orderedPosts']==10
        assert not Path(f'/proc/{row["nativePid"]}').exists()
        observations=row['taskObservations']
        assert observations['minimumTasks']==observations['maximumTasks']==1
        assert observations['taskIds']==[str(row['nativePid'])]
        for bound in ['first','last']:assert observations[bound]['taskAffinities']=={str(row['nativePid']):[14]}
        d=raw/'verification'/f'request{row["requestedThreads"]}'
        assert read(d/'result.json')==row
        for name,h in row['sha256'].items():assert sha(d/name)==h;bindings[str(d/name)]=h
        streams={n:(d/(n+'.raw')).read_bytes() for n in ['stdin','stdout','stderr']}
        actual=dict(stdout=streams['stdout'].decode(),stderr=streams['stderr'].decode(),exit=dict(code=0,signal=None))
        assert audit.original_streams(actual,workload,oracle,streams)==10
    for name in ['pipeline.json','build/receipt.json','verification/result.json']:
        bindings[str(raw/name)]=sha(raw/name)
    result=dict(complete=True,unitTests=tests,cliControls=13,oneCpu=proof['oneCpu'],
        genericBinary=dict(path=proof['engine'],sha256=proof['engineSha256'],bytes=Path(proof['engine']).stat().st_size),
        raw=str(raw),bindings=bindings,closerSha256=sha(Path(__file__)),
        scope='12 focused unit checks,13 CLI controls,two exact one-CPU08 projections; injected query error is not an OS fault probe; no timing qualification')
    assert not args.output.exists();write(args.output,result)
    print('closed12 unit checks/13 CLI controls/two one-task original08 replays')


if __name__=='__main__':main()
