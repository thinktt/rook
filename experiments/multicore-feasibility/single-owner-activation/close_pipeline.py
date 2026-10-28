#!/usr/bin/env python3
"""Reparse the completed original-clock pipeline and bind its terminal evidence."""
import argparse
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
from common import HERE,ROOT,baseline,preparation,prepared_run,read,sha
from reconcile import audit_run


def close(root):
    root=Path(root).resolve()
    pipeline=read(root/'pipeline.json')
    assert pipeline['schema']=='rook2-single-owner-activation-pipeline-v1'
    assert pipeline['complete'] and pipeline['prepared'] and pipeline['collected']
    assert pipeline['failure'] is None and pipeline['active'] is None
    prepared_path=Path(pipeline['preparation'])
    prepared=preparation(prepared_path)
    assert pipeline['preparationSha256']==sha(prepared_path)
    assert pipeline['sourcePreparation']==prepared
    assert pipeline['protectedArtifacts']==baseline()
    record=prepared_run(root/'prepared-run.json',prepared_path,prepared)
    start,deadline=pipeline['pipelineStartMonotonicNs'],pipeline['pipelineDeadlineMonotonicNs']
    assert start==record['pipelineStartMonotonicNs'] and deadline==record['pipelineDeadlineMonotonicNs']==start+3600*10**9
    stages=pipeline['stages'];prefix=record['stages']
    assert stages[:-2]==prefix and [row['stage'] for row in stages[-2:]]==['collection','reconcile']
    commands=[['/usr/bin/python3',str(HERE/'collect.py'),'--preparation',str(prepared_path),
        '--prepared-run',str(root/'prepared-run.json'),'--output',str(root/'pilot')],
        ['/usr/bin/python3',str(HERE/'reconcile.py'),str(root/'pilot')]]
    previous=record['preparedMonotonicNs']
    for row,command,cap in zip(stages[-2:],commands,[1900,120]):
        assert row['argv']==command and row['cwd']==str(ROOT)
        assert previous<=row['startedMonotonicNs']<row['endedMonotonicNs']<row['deadlineMonotonicNs']
        assert row['deadlineMonotonicNs']==min(deadline,row['startedMonotonicNs']+cap*10**9)
        assert row['elapsedNs']==row['endedMonotonicNs']-row['startedMonotonicNs'] and row['exit']==0
        previous=row['endedMonotonicNs']
    assert previous<=pipeline['pipelineEndedMonotonicNs']<deadline
    for row in stages:
        assert not Path(f'/proc/{row["pid"]}').exists(),'stage PID currently live; inspect possible reuse'
        for suffix in ['stdout','stderr']:
            assert sha(root/(row['stage']+'.'+suffix))==row[suffix+'Sha256']
    # The same independent parser recomputes original protocol semantics, wait4,
    # pre-input placement, observations, idle shutdown and all52 terminal exits.
    reconciled=audit_run(root/'pilot')
    assert read(root/'pilot/reconciled.json')==reconciled
    plan,result=read(root/'pilot/plan.json'),read(root/'pilot/result.json')
    assert stages[-2]['startedMonotonicNs']<=result['streamStartMonotonicNs']<result['streamEndMonotonicNs']<=stages[-2]['endedMonotonicNs']
    assert reconciled['reconcilerSha256']==sha(HERE/'reconcile.py')
    layout=read(root/'layout/result.json');assert layout['complete']
    focused=read(root/'focused/result.json')
    for row in focused['affinityReplays']:
        assert not Path(f'/proc/{row["nativePid"]}').exists(),'fallback PID currently live; inspect possible reuse'
    files=set(map(Path,plan['inputSha256']))|set(map(Path,record['inputSha256']))
    files.update(root/name for name in ['pipeline.json','prepared-run.json','focused/result.json','housekeeping-prepare.json','housekeeping-collect.json'])
    for name in ['prepare','collect']:
        outer=read(root/('housekeeping-'+name+'.json'))
        assert outer['failure'] is None and outer['restored'] is not None
        assert outer['helperCpus']==outer['postRestoreSelfAffinity']==[0,1,2,3,8,9,10,11,12,13]
        assert len(outer['applies'])==1
    files.update(root/(row['stage']+'.'+suffix) for row in stages for suffix in ['stdout','stderr'])
    files.update(path for path in (root/'pilot').rglob('*') if path.is_file())
    files.update(path for path in (root/'layout').rglob('*') if path.is_file())
    values={str(path):sha(path) for path in sorted(files)}
    # Freeze checks are repeated after the full raw parse and hashing pass.
    assert preparation(prepared_path)==prepared and baseline()==pipeline['protectedArtifacts']
    assert read(root/'pipeline.json')==pipeline
    terminal=time.monotonic_ns()
    assert terminal<deadline,'original pipeline deadline during terminal raw audit'
    return dict(schema='rook2-single-owner-activation-closure-v1',complete=True,raw=str(root),
        sourcePreparation=str(prepared_path),sourcePreparationSha256=sha(prepared_path),
        controlSource=prepared['controlSource'],candidateSource=prepared['candidateSource'],
        sourceChanges=prepared['sourceChanges'],sourceAdded=prepared['sourceAdded'],sourceRemoved=prepared['sourceRemoved'],
        sourceChallenge=prepared['sourceChallenge'],protectedArtifacts=pipeline['protectedArtifacts'],
        images=plan['images'],pipelineStartMonotonicNs=start,pipelineDeadlineMonotonicNs=deadline,
        pipelineEndedMonotonicNs=pipeline['pipelineEndedMonotonicNs'],pipelineElapsedNs=pipeline['pipelineEndedMonotonicNs']-start,
        terminalAuditMonotonicNs=terminal,terminalAuditElapsedNs=terminal-start,
        focusedPassed=sum(len(row['passedTests']) for row in prefix if row['stage'].startswith('tests-')),
        stageExits={row['stage']:row['exit'] for row in stages},stagesRun=len(stages),
        terminalNativeReceipts=reconciled['terminalNativeReceipts'],rowBindingsVerified=reconciled['rowBindingsVerified'],
        layout=str(root/'layout/result.json'),layoutSha256=sha(root/'layout/result.json'),
        cliControls=len(focused['cli']),fallbackLives=len(focused['affinityReplays']),
        replayLives=48,measured=36,warmups=12,idleProcesses=4,orderedPosts=reconciled['orderedPosts'],
        reconciled=str(root/'pilot/reconciled.json'),reconciledSha256=sha(root/'pilot/reconciled.json'),
        inputSha256=values,closerSha256=sha(Path(__file__)),
        scope='finite original-protocol fixed single-owner activation comparison; preserved/new inline and mode3 controls; no isolated synchronization/cache cause, PGO, qualification or adoption claim')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();output=close(args.root)
    with (args.output or args.root/'closure-audit.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','replayLives','idleProcesses','orderedPosts','pipelineElapsedNs']}))


if __name__=='__main__': main()
