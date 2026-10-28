#!/usr/bin/env python3
"""Close the selected PGO lane from existing terminal raw records; run no engine."""
import argparse
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from common import HERE,PIPELINE_SECONDS,generic_evidence,preparation,prepared_run,read,sha,write


def close(raw):
    p=read(raw/'pipeline.json');prep_path=HERE/'preparation.json';prep=preparation(prep_path)
    assert p['schema']=='rook2-single-owner-own-pgo-pipeline-v1'
    assert p['complete'] and p['prepared'] and p['collected'] and p['failure'] is None and p['active'] is None
    assert p['preparationSha256']==sha(prep_path) and p['sourcePreparation']==prep
    projected=prepared_run(raw/'prepared-run.json',prep_path,prep)
    assert isinstance(projected,tuple) and len(projected)==3
    pr=projected[0]
    assert isinstance(pr,dict) and pr==read(raw/'prepared-run.json')
    assert prep['sourceCheckpoint']=='19a1c1b83f6875064afc0b1677cb0c3e6d5bf303'
    assert len(prep['candidateSource'])==69
    assert p['stages'][:6]==pr['stages']
    assert [s['stage']for s in p['stages']]==['instrumented-build','training','training-audit','use-build','cli-affinity','layout','comparison','comparison-audit']
    assert p['pipelineStartMonotonicNs']==pr['pipelineStartMonotonicNs']
    assert p['pipelineDeadlineMonotonicNs']==pr['pipelineDeadlineMonotonicNs']==p['pipelineStartMonotonicNs']+PIPELINE_SECONDS*10**9
    assert p['lastInvocationEndMonotonicNs']<p['pipelineDeadlineMonotonicNs']
    a=read(raw/'full54/reconciled.json');run=read(raw/'full54/result.json')
    t=read(raw/'training/reconciled.json');tr=read(raw/'training/training.json')
    assert a['complete'] and a['replayLives']==270 and a['idleProcesses']==5 and a['orderedPosts']==3120
    assert a['schema']=='rook2-single-owner-own-pgo-full54-audit-v1'
    assert a['terminalNativeReceipts']==a['rowBindingsVerified']==275
    assert t['complete'] and t['strictReplayLifetimes']==216 and t['orderedPosts']==2496
    assert t['rowBindingsVerified']==216
    assert t['remerge']['exit']==0 and t['remerge']['byteIdentical'] and t['profileSha256']==a['profileSha256']
    canonical=raw/'training/merged.profdata';remade=Path(t['remerge']['profile'])
    assert canonical.read_bytes()==remade.read_bytes()
    pins={}
    for m in [prep['protectedArtifacts'],prep['inputSha256'],prep['reusedEvidenceSha256'],pr['inputSha256']]:
        for f,h in m.items():
            assert f not in pins or pins[f]==h
            pins[f]=h
    for base,data in [(raw/'training',t),(raw/'full54',a)]:
        for f,h in data['rawSha256'].items():assert sha(base/f)==h; pins[str(base/f)]=h
    for f,h in tr['raw_profiles_sha256'].items():assert sha(f)==h; pins[f]=h
    assert p['stages'][6]['argv']==['/usr/bin/python3',str(HERE/'collect.py'),'--preparation',str(prep_path),'--prepared-run',str(raw/'prepared-run.json'),'--output',str(raw/'full54')]
    assert p['stages'][7]['argv']==['/usr/bin/python3',str(HERE/'reconcile.py'),str(raw/'full54')]
    previous=p['pipelineStartMonotonicNs']
    for s,cap in zip(p['stages'],[300,2500,120,300,420,120,1900,120]):
        assert s['exit']==0 and previous<=s['startedMonotonicNs']<s['endedMonotonicNs']<s['deadlineMonotonicNs']<=p['pipelineDeadlineMonotonicNs']
        assert s['elapsedNs']==s['endedMonotonicNs']-s['startedMonotonicNs']
        assert s['deadlineMonotonicNs']==min(p['pipelineDeadlineMonotonicNs'],s['startedMonotonicNs']+cap*10**9)
        assert s['cwd']==str(HERE.parents[2])
        assert not Path('/proc',str(s['pid'])).exists()
        previous=s['endedMonotonicNs']
        for suffix in ['stdout','stderr']:
            file=raw/(s['stage']+'.'+suffix);assert sha(file)==s[suffix+'Sha256'];pins[str(file)]=sha(file)
    terminal=0;rowpins=0;bindings=[];pids=set()
    rows=[('training',row)for row in tr['runs']]+[('replay',row)for row in run['runs']]+[('idle',row)for row in run['idle']]
    for kind,row in rows:
        d=Path(row['directory']) if kind!='idle' else raw/'full54'/('idle-'+row['variant'])
        for f,h in row['sha256'].items():assert sha(d/f)==h;rowpins+=1
        n=read(d/'native.json');assert n['native_exit_code']==0 and n['failure'] is None and n['exec_error'] is None
        assert row['nativePid']==n['native_pid'] and n['native_pid'] not in pids
        pids.add(n['native_pid'])
        assert n['engine_sha256_before']==n['engine_sha256_after']==sha(n['engine'])
        assert n['reaped_monotonic_ns']>=n['start_monotonic_ns']>0
        binding=dict(kind=kind,engine=n['engine'],engineSha256=n['engine_sha256_before'],
            argv=n['argv'],threadBudget=n['expected_threads'],nativePid=n['native_pid'],
            nativeReceiptSha256=sha(d/'native.json'))
        for key in ['case','variant','warmup','repeat']:
            if key in row:binding[key]=row[key]
        if kind=='training':
            assert row['profileSha256']==tr['raw_profiles_sha256'][row['profile']]==sha(row['profile'])
            binding.update(profile=row['profile'],profileSha256=row['profileSha256'])
        bindings.append(binding)
        pins[str(d/'native.json')]=sha(d/'native.json')
        assert not Path('/proc',str(n['native_pid'])).exists();terminal+=1
    assert terminal==len(pids)==len(bindings)==491
    assert bindings[216:]==a['rowBindings']==run['rowBindings']
    assert run['terminalNativeReceipts']==275
    layout=read(raw/'layout/result.json');assert layout['complete'] and layout['joined']
    assert not Path('/proc',str(layout['nativePid'])).exists()
    assert layout['nativePid'] not in pids
    assert pr['layout']['report']==layout
    for f in (raw/'layout').iterdir():
        if f.is_file():pins[str(f)]=sha(f)
    for key in ['controlSource','candidateSource']:
        if key in prep:
            crate=Path(prep['candidateCrate'])
            for n,h in prep[key].items():assert sha(crate/n)==h
    files=[prep_path,raw/'pipeline.json',raw/'prepared-run.json',raw/'housekeeping-prepare.json',raw/'housekeeping-collect.json',raw/'rook2-instrumented',raw/'rook2-pgo',raw/'training/reconciled.json',raw/'training/independent-remerge/receipt.json',remade,raw/'full54/plan.json',raw/'full54/result.json',raw/'full54/reconciled.json',raw/'full54/housekeeping.json']
    for f in files:pins[str(f)]=sha(f)
    for f,h in pins.items():assert sha(f)==h,f
    return dict(schema='rook2-single-owner-own-pgo-closure-v1',complete=True,raw=str(raw),
        sourceCheckpoint=prep['sourceCheckpoint'],candidateSource=prep['candidateSource'],sourceFiles=69,
        sourceChangesAgainstGeneric=[],reusedGenericControls=70,freshControlsThisLane=0,
        evidenceReuse=generic_evidence(prep),trainingLives=216,comparisonLives=270,idleProbes=5,
        orderedTrainingPosts=2496,orderedComparisonPosts=3120,cliControls=14,fallbackSearches=2,
        observationsPerCell=1,warmups=0,terminalNativeReceipts=terminal,rowBindingsVerified=len(bindings),
        rowBindings=bindings,rowFileBindingsVerified=rowpins,canonicalMergeCount=1,independentAuditMergeCount=1,
        byteIdenticalRemerge=True,coldLayoutProcesses=1,terminalColdLayoutProcesses=1,
        productionLayout=layout['projection'],layoutAdmissionSha256=sha(raw/'layout/result.json'),
        profileSha256=a['profileSha256'],profileBytes=canonical.stat().st_size,images=a['images'],
        protectedArtifacts=prep['protectedArtifacts'],stageExits={s['stage']:s['exit']for s in p['stages']},
        pipelineElapsedNs=p['lastInvocationEndMonotonicNs']-p['pipelineStartMonotonicNs'],
        pipelineStartMonotonicNs=p['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=p['pipelineDeadlineMonotonicNs'],
        clockReset=False,failuresThisLane=0,retriesThisLane=0,pins=pins,table=a['table'],totals=a['totals'],
        ratios=a['ratios'],caseRatios=a['caseRatios'],gainsLosses=a['gainsLosses'],memory=a['memory'],idle=a['idle'],
        rotationSlotCounts=a['rotationSlotCounts'],closerSha256=sha(Path(__file__)),
        scope='single-observation descriptive original54 unchanged-source own-PGO; no significance, qualification, adoption, isolated causal explanation, matched Bee comparison or automatic follow-on')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path)
    args=parser.parse_args();value=close(args.root.resolve());out=args.output or args.root/'closure-audit.json';assert not out.exists();write(out,value)
    print({k:value[k]for k in ['complete','trainingLives','comparisonLives','idleProbes','terminalNativeReceipts','pipelineElapsedNs']})


if __name__=='__main__':main()
