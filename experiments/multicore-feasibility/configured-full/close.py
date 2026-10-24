#!/usr/bin/env python3
"""Bind completed profile/measurement records and emit concise reports, no engines."""
import argparse
import csv
from pathlib import Path

from common import HERE, ROOT, NAMES, admission, read, sha, write
from pipeline import check_inputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path)
    parser.add_argument('--output',type=Path,default=HERE)
    args=parser.parse_args();raw=args.raw.resolve();out=args.output.resolve()
    state=read(raw/'pipeline.json')
    assert state['complete'] and state['failure'] is None and state['active'] is None
    check_inputs(state)
    expected=['instrumented-build','training','training-audit','use-build','small','small-audit']
    has_full='full54Extension' in state
    if has_full:
        assert state['full54Extension']['complete'] and state['full54Extension']['failure'] is None
        expected+=['full54','full54-audit']
    assert [r['stage'] for r in state['stages']]==expected
    bindings={str(raw/'pipeline.json'):sha(raw/'pipeline.json')}
    for row in state['stages']:
        assert row['exit']==0
        for stream in ['stdout','stderr']:
            p=raw/(row['stage']+'.'+stream)
            assert sha(p)==row[stream+'Sha256'];bindings[str(p)]=sha(p)
    receipt,_,_=admission(raw/'use-build',Path(state['serial']),Path(state['previous']),Path(state['candidate']))
    assert receipt['source_sha256_before']==state['sourceInputs']
    image=Path(state['candidate']);assert sha(image)==state['candidateSha256']
    profile=raw/'training/merged.profdata';assert sha(profile)==state['profileSha256']
    training=read(raw/'training/reconciled.json')
    assert training['complete'] and training['nativeProcesses']==108 and training['rawProfiles']==108
    assert training['mergeCount']==1 and training['orderedPosts']==1248
    assert training['profileSha256']==sha(profile)
    for name,h in training['rawSha256'].items():assert sha(raw/'training'/name)==h
    verification=read(HERE/'verification-proof.json')
    assert verification['complete'] and len(verification['unitTests'])==12 and verification['cliControls']==13
    assert sha(Path(verification['genericBinary']['path']))==verification['genericBinary']['sha256']
    assert all(sha(Path(p))==h for p,h in verification['bindings'].items())
    summaries={};total_posts=training['orderedPosts'];total_lives=108
    for label,count,posts in [('small',64,864)]+([('full54',216,2496)] if has_full else []):
        result=read(raw/label/'reconciled.json')
        assert result['complete'] and result['replayLives']==count and result['orderedPosts']==posts
        for name,h in result['rawSha256'].items():assert sha(raw/label/name)==h
        total_lives+=count;total_posts+=posts
        summaries[label]={k:result[k] for k in ['replayLives','measured','warmups','idleProcesses','orderedPosts',
                             'summedMedians','comparisons','guestCpuTickDeltas','rawSha256']}
        summaries[label]['maxObservedRssKiB']={n:max(x['rssKiB']['max'] for x in result['summaries']
                                                  if x['variant']==n) for n in NAMES}
        if label=='small':
            summaries[label]['summaries']=result['summaries']
            summaries[label]['idle']=result['idle']
        else:
            table=out/'full54-timings.csv';assert not table.exists()
            by={(x['case'],x['variant']):x for x in result['summaries']}
            cases=list(dict.fromkeys(x['case'] for x in result['summaries']))
            with table.open('x',newline='') as f:
                writer=csv.writer(f,lineterminator='\n')
                writer.writerow(['case',*[f'{n}_{m}' for n in NAMES for m in
                    ['searchWallNs','wholeCpuSeconds','wholeWallNs','rssKiB']]])
                for case in cases:
                    writer.writerow([case,*[by[case,n][m]['median'] for n in NAMES for m in
                        ['searchWallNs','wholeCpuSeconds','wholeWallNs','rssKiB']]])
            summaries[label]['timingsCsvSha256']=sha(table)
        for filename in ['plan.json','result.json','reconciled.json']:
            p=raw/label/filename;bindings[str(p)]=sha(p)
    for name in ['instrumented-build/receipt.json','use-build/receipt.json','training/reconciled.json',
                 'training/training.json','training/merge.json','training/merge-tool.json','extension-decision.json']:
        p=raw/name
        if p.exists():bindings[str(p)]=sha(p)
    old=Path('/home/legolas/rook2-experiments/usable-full-20261024-01/build/source-before/src/evaluator_worker.rs')
    worker=ROOT/'src/evaluator_worker.rs';assert sha(old)==sha(worker)
    output=dict(complete=True,sourceCommit=state['sourceRevision'],image=dict(path=str(image),sha256=sha(image),bytes=image.stat().st_size),
        profile=dict(path=str(profile),sha256=sha(profile)),training=dict(nativeLives=108,orderedPosts=1248,rawProfiles=108,mergeCount=1),
        summaries=summaries,totalReplayLives=total_lives,totalOrderedPosts=total_posts,
        qualification='Finite source-bound own-PGO study; no full mandatory/gameplay/adoption/performance qualification')
    proof=dict(complete=True,sourceCommit=state['sourceRevision'],raw=str(raw),bindings=bindings,
        reusedWorkerSourceSha256=sha(worker),verificationProofSha256=sha(HERE/'verification-proof.json'),
        profileUseReceiptSha256=sha(raw/'use-build/receipt.json'),closerSha256=sha(Path(__file__)),
        preservedControls={n:dict(path=state[k],sha256=sha(Path(state[k]))) for n,k in [('serial1','serial'),('previous2','previous')]},
        limitations='One recorded merge/hash audit, not independent remerge; exact generic verification image differs from PGO image; original finite projections and point affinity are not final qualification')
    for p,value in [(out/'results.json',output),(out/'proof.json',proof)]:
        assert not p.exists();write(p,value)
    print('Closed',total_lives,'source-bound training/comparison lives and',total_posts,'posts; no engine rerun')


if __name__=='__main__':main()
