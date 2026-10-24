#!/usr/bin/env python3
"""Bind saved focused and measurement receipts; no engine/compiler execution."""
import argparse
import json
from pathlib import Path
import re

from common import HERE, ROOT, SPEC, audit, read, sha, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--output', type=Path, default=HERE)
    args = parser.parse_args()
    raw, out = args.raw.resolve(), args.output.resolve()
    pipeline = read(raw/'pipeline.json')
    assert pipeline['complete'] and pipeline['active'] is None and 'failure' not in pipeline
    for name, digest in pipeline['inputs'].items(): assert sha(Path(name)) == digest
    expected = ['worker','numerical','scope','delayed','cli-parser','generic-build',
                'cli-affinity','collection','reconcile']
    assert [r['stage'] for r in pipeline['stages']] == expected
    tests = []
    bindings = {str(raw/'pipeline.json'): sha(raw/'pipeline.json')}
    for row in pipeline['stages']:
        assert row['exit'] == 0 and not Path(f'/proc/{row["pid"]}').exists()
        for stream in ['stdout','stderr']:
            path=raw/(row['stage']+'.'+stream)
            assert sha(path) == row[stream+'Sha256']
            bindings[str(path)]=sha(path)
        if 'passedTests' in row:
            names=re.findall(r'^test ([^\n]+) \.\.\. ok$',(raw/(row['stage']+'.stdout')).read_text(),re.M)
            assert len(names)==row['passedTests']
            tests.extend(names)
    assert len(tests)==len(set(tests))==20
    delayed=next(row for row in pipeline['stages'] if row['stage']=='delayed')
    assert delayed['elapsedNs'] >= 10*10**9
    receipt=read(raw/'build/receipt.json')
    assert receipt['source_sha256_before']==receipt['source_sha256_after']
    for name,digest in receipt['source_sha256_before'].items():
        assert sha(ROOT/name)==sha(raw/'build/source-before'/name)==digest
    image=Path(pipeline['binary']['path'])
    assert sha(image)==receipt['binary_output']['sha256']==pipeline['binary']['sha256']
    assert image.stat().st_size==pipeline['binary']['bytes']
    focused=read(raw/'focused/result.json')
    assert focused['complete'] and focused['engineSha256']==sha(image) and len(focused['cli'])==9
    for row, requested in zip(focused['cli'][:4],[1,1,2,8]):
        assert row['exit']==0 and row['stderr']==''
        assert json.loads(row['stdout'])==dict(requested_threads=requested,configured_threads=min(requested,2))
    assert all(row['exit']!=0 and row['stdout']=='' and row['stderr'] for row in focused['cli'][4:])
    one=focused['oneCpu']
    assert one['exit']==0 and one['orderedPosts']==10 and len(one['allowedTaskMasks'])==2
    assert all(mask==[14] for mask in one['allowedTaskMasks'].values())
    assert not Path(f'/proc/{one["nativePid"]}').exists()
    assert sha(raw/'focused/one-cpu-stdout.raw')==one['stdoutSha256']
    stdout=(raw/'focused/one-cpu-stdout.raw').read_bytes()
    assert stdout.startswith(b'cm_parm\n')
    workload=next(c for c in read(SPEC/'workloads.json')['cases'] if c['id']=='profile-08')
    oracle=next(c for c in read(SPEC/'replay-oracle.json')['cases'] if c['id']=='profile-08')
    projected=stdout[len(b'cm_parm\n'):]
    stdin=('\n'.join([*workload['protocol']['recordsBeforeSearch'],'cm_parm rnd','go'])+'\n').encode()
    assert audit.original_streams(dict(stdout=projected.decode(),stderr='',exit=dict(code=0,signal=None)),
        workload,oracle,dict(stdin=stdin,stdout=projected,stderr=b''))==10
    results=read(raw/'pilot/reconciled.json')
    assert results['complete'] and results['replayLives']==48 and results['orderedPosts']==648
    assert results['idleProcesses']==3 and results['measured']==36 and results['warmups']==12
    for name,digest in results['rawSha256'].items(): assert sha(raw/'pilot'/name)==digest
    for name in ['build/receipt.json','build/build.stdout','build/build.stderr',
                 'focused/result.json','focused/cli-progress.json','focused/one-cpu-stdout.raw',
                 'pilot/plan.json','pilot/result.json','pilot/reconciled.json']:
        bindings[str(raw/name)]=sha(raw/name)
    proof=dict(sourceCommit='e44b7c3b4d12a0d4c975a16763bc7c830f354dcf',
               complete=True,focusedUnitTests=tests,cliControls=9,oneCpu=one,
               binary=pipeline['binary'],raw=str(raw),rawBindings=bindings,
               preserved={name:digest for name,digest in pipeline['inputs'].items()
                          if 'full-split-production-20261024-01/rook2-pgo' in name
                          or name.endswith('training/merged.profdata')},
               closerSha256=sha(Path(__file__)),
               scope='20 unit checks,9 CLI controls,one single-CPU projected08 replay,48 original replay lives+3 idle; no PGO/adoption/qualification')
    assert len(proof['preserved'])==2
    for p in [out/'results.json',out/'proof.json']: assert not p.exists()
    write(out/'results.json',results)
    write(out/'proof.json',proof)
    print(json.dumps(dict(complete=True,focusedTests=20,replayLives=48,
                         binarySha256=sha(image),summedMedians=results['summedMedians']),indent=2))


if __name__=='__main__': main()
