#!/usr/bin/env python3
"""Close saved qualification records, preserving the compile-only setup failure."""
import argparse
import json
from pathlib import Path
import re

from run import HERE, ROOT, IMAGE, SHA, sha, read, write


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('raw',type=Path)
    parser.add_argument('--output',type=Path,default=HERE)
    args=parser.parse_args();raw=args.raw.resolve();out=args.output.resolve()
    initial=read(raw/'pipeline.json');continuation=read(raw/'continuation.json')
    repair=read(raw/'observer-setup-repair/repair.json')
    assert not initial['complete'] and initial['failure']=="AssertionError(('observer-build', 1))"
    assert [x['stage'] for x in initial['stages']]==['exact-configuration','mandatory','observer-build']
    assert [x['exit'] for x in initial['stages']]==[0,0,1]
    assert continuation['complete'] and continuation['failure'] is None and continuation['active'] is None
    assert continuation['initialPipelineSha256']==sha(raw/'pipeline.json')==repair['initialPipelineSha256']
    assert continuation['repairSha256']==sha(raw/'observer-setup-repair/repair.json')
    assert continuation['resourceElapsedNs']<continuation['originalResourceSeconds']*10**9
    assert [x['stage'] for x in continuation['stages']]==['observer-build-corrected','threaded-observer','ordinary-mode2','ordinary-mode1']
    bindings={}
    for row in initial['stages']+continuation['stages']:
        assert not Path(f'/proc/{row["pid"]}').exists()
        assert row['cleanup'] is False
        for stream in ['stdout','stderr']:
            p=raw/(row['stage']+'.'+stream)
            assert sha(p)==row[stream+'Sha256'];bindings[str(p)]=sha(p)
    assert all(x['exit']==0 for x in continuation['stages'])
    assert repair['engineRunsInFailedObserverAttempt']==0 and not repair['productionSourceOrImageChanged']
    assert sha(HERE/'threaded_observer.rs')==repair['afterSha256']
    assert sha(raw/'observer-setup-repair/threaded_observer-before.rs')==repair['beforeSha256']
    assert all(sha(ROOT/n)==h for n,h in initial['source'].items()) and sha(IMAGE)==SHA
    for p,h in initial['pins'].items():
        assert sha(raw/'observer-setup-repair/threaded_observer-before.rs' if p==str(HERE/'threaded_observer.rs') else p)==h
    config=read(raw/'ordinary/configuration/result.json')
    assert config['complete'] and config['engineSha256']==SHA and len(config['cli'])==13
    assert [x['requestedThreads'] for x in config['oneCpu']]==[1,2]
    for row in config['oneCpu']:
        assert row['configuredThreads']==1 and row['exit']==0 and row['orderedPosts']==10
        assert row['taskObservations']['minimumTasks']==row['taskObservations']['maximumTasks']==1
        d=raw/'ordinary/configuration'/f'request{row["requestedThreads"]}'
        for name,h in row['sha256'].items():assert sha(d/name)==h
    mandatory=read(raw/'mandatory/independent-reconciliation.json');selection=read(raw/'mandatory/selection.json')
    assert mandatory['pass'] and mandatory['mandatory']['cases']==selection['mandatoryCases']
    assert mandatory['mandatory']['files']==len(selection['files'])
    assert mandatory['mandatory']['singleRunAllFixtures'] and mandatory['tests']['failures']==0
    diag=mandatory['diagnostic'];assert sha(diag['path'])==diag['sha256'] and diag['sameEngineSourceAsOrdinary']
    assert diag['configuration']=='default1; no adapter helper configuration'
    assert mandatory['tests']['freshLibraryPassed']+mandatory['tests']['reusedLibraryPassed']+len(mandatory['tests']['ignoredLibrary'])==mandatory['tests']['libraryInventory']
    observer=continuation['observer'];binding=read(observer['binding'])
    assert observer['bindingSha256']==sha(observer['binding']) and observer['sha256']==sha(observer['executable'])
    assert binding['testSourceSha256']==sha(HERE/'threaded_observer.rs')
    assert sha(binding['library'])==binding['librarySha256']
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',
        (raw/'threaded-observer.stdout').read_text())==[('1','0')]
    ordinary={}
    for mode,count,gated in [('mode2',33,22),('mode1',21,10)]:
        d=raw/'ordinary'/mode;result=read(d/'independent-reconciliation.json');lane=read(d/'lane-outcome.json')
        assert result['verified'] and result['nativeImageSha256']==SHA
        assert lane['complete'] and lane['failure'] is None and lane['allOwnedGroupsTerminal'] and lane['deadlineSatisfied']
        assert result['nativeLifetimes']==count and result['fullyGatedSearchLifetimes']==gated
        assert result['noSearchSynchronousLifetimes']==11 and result['nativeExpectedExit1']==8
        assert result['completeFocusedReplay']==(mode=='mode2') and not result['completeGameplayQualification']
        if mode=='mode2':
            assert result['games']['games']==12 and result['games']['searches']==632
            assert result['games']['posts']==5801
            combined=d/'combine/report.json';target=out/'mode2-combined-focused-report.json'
            assert not target.exists();target.write_bytes(combined.read_bytes());assert sha(target)==sha(combined)
        else:assert result['games'] is None and result['originalCombinedFocusedReport'] is None
        for n in result['nativeReceipts']:
            assert not Path(f'/proc/{n["nativePid"]}').exists() and not Path(f'/proc/{n["supervisorPid"]}').exists()
        ordinary[mode]={k:v for k,v in result.items() if k!='nativeReceipts'}
        bindings[str(d/'independent-reconciliation.json')]=sha(d/'independent-reconciliation.json')
        bindings[str(d/'lane-outcome.json')]=sha(d/'lane-outcome.json')
    for name in ['pipeline.json','continuation.json','observer-setup-repair/repair.json','observer/binding.json',
                 'observer/repaired-binding.json','ordinary/configuration/result.json','mandatory/plan.json',
                 'mandatory/selection.json','mandatory/lane-outcome.json','mandatory/independent-reconciliation.json']:
        bindings[str(raw/name)]=sha(raw/name)
    result=dict(complete=True,sourceCommit=initial['sourceCommit'],ordinaryImage=dict(path=str(IMAGE),sha256=SHA),
        diagnosticImage=diag,configurationControls=dict(nativeCli=13,oneCpu=config['oneCpu'],
            priorQueryFailureInjection='Reused exact-source unit seam, not an OS fault probe'),
        mandatory={k:mandatory[k] for k in ['tests','mandatory','rawBytes','postExecObservations','missingPostExecObservations']},
        observer={'pass':True,'comparisons':12,'actualConfiguredModes':[1,2],'binding':observer},ordinary=ordinary,
        compileOnlyRepair=repair,resource=dict(conservativeElapsedNs=continuation['resourceElapsedNs'],limitSeconds=4200),
        recommendation='Ready for a local adoption decision within recorded finite/source/configuration scope; no adoption performed',
        limits='Mandatory diagnostic is default1, not mode2 mandatory; mode1 short only; synchronous seed observations may be unavailable and are not pre-input placement; no external full3288 or final performance/specification-owner qualification')
    proof=dict(complete=True,raw=str(raw),bindings=bindings,sourceReviewSha256=sha(HERE/'source-review.md'),
        closerSha256=sha(Path(__file__)),noProductionSourceOrOrdinaryImageChange=True,noNativeRetry=True,
        compileOnlyFailurePreserved=True,observerGapReceiptBound=True)
    for p,value in [(out/'result.json',result),(out/'proof.json',proof)]:assert not p.exists();write(p,value)
    print('Closed exact PGO configuration, default1 mandatory, threaded observer and separate ordinary modes; no engine rerun')


if __name__=='__main__':main()
