#!/usr/bin/env python3
"""Close the selected PGO lane from existing terminal raw records; run no engine."""
import argparse
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from common import HERE,preparation,prepared_run,read,sha,write


def close(raw):
    p=read(raw/'pipeline.json');prep_path=HERE/'preparation.json';prep=preparation(prep_path)
    assert p['schema']=='rook2-owner-local-own-pgo-pipeline-v1'
    assert p['complete'] and p['prepared'] and p['collected'] and p['failure'] is None and p['active'] is None
    assert p['preparationSha256']==sha(prep_path) and p['sourcePreparation']==prep
    pr=prepared_run(raw/'prepared-run.json',prep_path,prep)
    assert p['stages'][:5]==pr['stages']
    assert [s['stage']for s in p['stages']]==['instrumented-build','training','training-audit','use-build','cli-affinity','comparison','comparison-audit']
    assert p['pipelineStartMonotonicNs']==pr['pipelineStartMonotonicNs']
    assert p['pipelineDeadlineMonotonicNs']==pr['pipelineDeadlineMonotonicNs']==p['pipelineStartMonotonicNs']+3600*10**9
    assert p['lastInvocationEndMonotonicNs']<p['pipelineDeadlineMonotonicNs']
    a=read(raw/'full54/reconciled.json');run=read(raw/'full54/result.json')
    t=read(raw/'training/reconciled.json');tr=read(raw/'training/training.json')
    assert a['complete'] and a['replayLives']==270 and a['idleProcesses']==5 and a['orderedPosts']==3120
    assert t['complete'] and t['strictReplayLifetimes']==216 and t['orderedPosts']==2496
    assert t['remerge']['exit']==0 and t['remerge']['byteIdentical'] and t['profileSha256']==a['profileSha256']
    canonical=raw/'training/merged.profdata';remade=Path(t['remerge']['profile'])
    assert canonical.read_bytes()==remade.read_bytes()
    pins={}
    for m in [prep['protectedArtifacts'],prep['inputSha256'],prep['reusedEvidenceSha256'],pr['inputSha256']]:pins.update(m)
    for base,data in [(raw/'training',t),(raw/'full54',a)]:
        for f,h in data['rawSha256'].items():assert sha(base/f)==h; pins[str(base/f)]=h
    for f,h in tr['raw_profiles_sha256'].items():assert sha(f)==h; pins[f]=h
    assert p['stages'][5]['argv']==['/usr/bin/python3',str(HERE/'collect.py'),'--preparation',str(prep_path),'--prepared-run',str(raw/'prepared-run.json'),'--output',str(raw/'full54')]
    assert p['stages'][6]['argv']==['/usr/bin/python3',str(HERE/'reconcile.py'),str(raw/'full54')]
    previous=p['pipelineStartMonotonicNs']
    for s,cap in zip(p['stages'],[300,2500,120,300,420,1900,120]):
        assert s['exit']==0 and previous<=s['startedMonotonicNs']<s['endedMonotonicNs']<s['deadlineMonotonicNs']<=p['pipelineDeadlineMonotonicNs']
        assert s['elapsedNs']==s['endedMonotonicNs']-s['startedMonotonicNs']
        assert s['deadlineMonotonicNs']==min(p['pipelineDeadlineMonotonicNs'],s['startedMonotonicNs']+cap*10**9)
        assert s['cwd']==str(HERE.parents[2])
        assert not Path('/proc',str(s['pid'])).exists()
        previous=s['endedMonotonicNs']
        for suffix in ['stdout','stderr']:
            file=raw/(s['stage']+'.'+suffix);assert sha(file)==s[suffix+'Sha256'];pins[str(file)]=sha(file)
    terminal=0;rowpins=0
    for row in tr['runs']+run['runs']+run['idle']:
        d=Path(row.get('directory',raw/'full54'/('idle-'+row.get('variant',''))))
        for f,h in row['sha256'].items():assert sha(d/f)==h;rowpins+=1
        n=read(d/'native.json');assert n['native_exit_code']==0 and n['failure'] is None and n['exec_error'] is None
        assert not Path('/proc',str(n['native_pid'])).exists();terminal+=1
    assert terminal==491
    for key in ['controlSource','candidateSource']:
        if key in prep:
            crate=Path(prep['candidateCrate'])
            for n,h in prep[key].items():assert sha(crate/n)==h
    files=[prep_path,raw/'pipeline.json',raw/'prepared-run.json',raw/'housekeeping-prepare.json',raw/'housekeeping-collect.json',raw/'rook2-instrumented',raw/'rook2-pgo',raw/'training/reconciled.json',raw/'training/independent-remerge/receipt.json',remade,raw/'full54/plan.json',raw/'full54/result.json',raw/'full54/reconciled.json',raw/'full54/housekeeping.json']
    for f in files:pins[str(f)]=sha(f)
    for f,h in pins.items():assert sha(f)==h,f
    return dict(schema='rook2-owner-local-own-pgo-closure-v1',complete=True,raw=str(raw),sourceCheckpoint=prep['sourceCheckpoint'],candidateSource=prep['candidateSource'],sourceFiles=66,sourceChangesAgainstGeneric=[],reusedGenericControls=47,trainingLives=216,comparisonLives=270,idleProbes=5,orderedTrainingPosts=2496,orderedComparisonPosts=3120,cliControls=14,fallbackSearches=2,observationsPerCell=1,warmups=0,terminalNativeReceipts=terminal,rowBindingsVerified=rowpins,canonicalMergeCount=1,independentAuditMergeCount=1,byteIdenticalRemerge=True,profileSha256=a['profileSha256'],profileBytes=canonical.stat().st_size,images=a['images'],protectedArtifacts=prep['protectedArtifacts'],stageExits={s['stage']:s['exit']for s in p['stages']},pipelineElapsedNs=p['lastInvocationEndMonotonicNs']-p['pipelineStartMonotonicNs'],pipelineStartMonotonicNs=p['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=p['pipelineDeadlineMonotonicNs'],clockReset=False,failuresThisLane=0,retriesThisLane=0,pins=pins,totals=a['totals'],ratios=a['ratios'],rotationSlotCounts=a['rotationSlotCounts'],closerSha256=sha(Path(__file__)),scope='single-observation descriptive original54 unchanged-source own-PGO; no qualification, adoption, isolated causal explanation or automatic follow-on')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path)
    args=parser.parse_args();value=close(args.root.resolve());out=args.output or args.root/'closure-audit.json';assert not out.exists();write(out,value)
    print({k:value[k]for k in ['complete','trainingLives','comparisonLives','idleProbes','terminalNativeReceipts','pipelineElapsedNs']})


if __name__=='__main__':main()
