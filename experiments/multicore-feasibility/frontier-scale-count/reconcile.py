#!/usr/bin/env python3
"""Saved-raw one-search qualification and bounded counter-report consistency.

No counter is independently recounted from wire events: six focused controls and
source review own that assurance. This parser rechecks exact posts/move/work,
placement, joined exits, pair shape and carried original stopping metadata.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import time
sys.dont_write_bytecode=True
from common import (HERE,ROOT,CRATE,HELPERS,SPEC,BUILD_ADAPTER,OPTIONS,STEP,TESTS,REPORT,REPORT_ENV,
    admit_build,audit,audit_placement,baseline,image_layout,preparation,read,sha)


def integer(value,maximum=2**64-1):
    assert type(value) is int and 0<=value<=maximum,value
    return value


def report_audit(report,oracle,search_ns):
    assert set(report)=={'schema','E6','S6','M7','F7','searchStarts','error','pairComplete','clockBasis','boundaries','outcome','stateBytes'}
    assert report['schema']=='rook2-frontier-scale-v1' and integer(report['searchStarts'])==1
    for name in ['E6','S6','M7','F7']:integer(report[name])
    assert report['error'] is None or isinstance(report['error'],str)
    assert type(report['pairComplete']) is bool and report['clockBasis']=='relative-to-iteration6-entry'
    assert 0<integer(report['stateBytes'])<=512
    pair=report['boundaries'];assert len(pair)==2
    for row,iteration in zip(pair,[6,7]):
        assert set(row)=={'iteration','entered','complete','startNs','endNs'} and row['iteration']==iteration
        assert type(row['entered']) is type(row['complete']) is bool
        for name in ['startNs','endNs']:
            if row[name] is not None:integer(row[name],2**128-1)
    outcome=report['outcome']
    assert set(outcome)=={'stopPoint','stopDepth','stopRootIndex','stopReason','N','R','completedIterationsMask','lastIterationDepth','selectedDepth','selectedSearchUnits'}
    assert outcome['stopPoint'] in ['root','poll','iteration'] and isinstance(outcome['stopReason'],str) and outcome['stopReason']
    for name in ['N','R','completedIterationsMask']:integer(outcome[name])
    for name in ['stopDepth','lastIterationDepth']:assert 0<integer(outcome[name])<=62
    if outcome['stopRootIndex'] is not None:integer(outcome['stopRootIndex'])
    last=oracle['posts'][-1]
    assert integer(outcome['selectedSearchUnits'])==last['searchId']
    assert integer(outcome['selectedDepth'])==last['depth']//1000==8
    assert outcome['N']>=outcome['selectedSearchUnits'] and outcome['lastIterationDepth']>=8 and outcome['stopDepth']>=8
    complete=report['pairComplete'] and report['error'] is None
    if complete:
        assert report['E6']<=report['S6']
        assert all(row['entered'] and row['complete'] for row in pair)
        assert pair[0]['startNs']==0 and 0<=pair[0]['endNs']<=pair[1]['startNs']<=pair[1]['endNs']<=search_ns
        assert outcome['completedIterationsMask']&192==192
    return dict(complete=complete,censored=not complete,counts={name:report[name] for name in ['E6','S6','M7','F7']},
        boundaries=pair,outcome=outcome,stateBytes=report['stateBytes'],error=report['error'],
        assurance='Counts and domains: frozen source plus six controls; raw wire does not recount E6/S6/M7/F7 or stop R. Relative6/7 span fits go-to-move; no absolute alignment or speed comparison is claimed.')


def audit_run(root,during=False):
    root=Path(root).resolve();state=read(root/'pipeline.json');prepared_path=Path(state['preparation']);prepared=preparation(prepared_path)
    assert state['schema']=='rook2-frontier-scale-count-pipeline-v1' and state['sourcePreparation']==prepared
    assert state['preparationSha256']==sha(prepared_path) and state['protectedArtifacts']==baseline()
    start,deadline=state['pipelineStartMonotonicNs'],state['pipelineDeadlineMonotonicNs'];assert deadline==start+900*10**9
    names=['unit-tests','candidate-build','observe']+([] if during else ['audit'])
    assert [row['stage'] for row in state['stages']]==names
    assert (state['active']=='audit' and not state['complete']) if during else (state['complete'] and state['active'] is None)
    assert state['failure'] is None
    expected=[['/usr/bin/cargo','test','--offline','--locked','--lib','--target','x86_64-unknown-linux-gnu','--jobs','4',
        '--target-dir',str(root/'test-target'),'--manifest-path',str(CRATE/'Cargo.toml'),'frontier_scale::tests','--','--test-threads=1'],
        ['/usr/bin/python3',str(BUILD_ADAPTER),'--crate',str(CRATE),'--mode','generic','--bin','rook2','--jobs','4','--output',str(root/'candidate-build')],
        ['/usr/bin/python3',str(HERE/'pipeline.py'),'--preparation',str(prepared_path),'--output',str(root),'--observe-only'],
        ['/usr/bin/python3',str(HERE/'reconcile.py'),str(root),'--during-pipeline']]
    previous=start
    for row,argv,cap in zip(state['stages'],expected,[300,300,200,60]):
        assert row['argv']==argv and row['cwd']==str(ROOT) and row['exit']==0
        assert previous<=row['startedMonotonicNs']<row['endedMonotonicNs']<row['deadlineMonotonicNs']==min(deadline,row['startedMonotonicNs']+cap*10**9)
        previous=row['endedMonotonicNs'];assert not Path(f'/proc/{row["pid"]}').exists()
        for suffix in ['stdout','stderr']:assert sha(root/(row['stage']+'.'+suffix))==row[suffix+'Sha256']
    text=(root/'unit-tests.stdout').read_text();passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
    assert sorted(passed)==TESTS and state['stages'][0]['passedTests']==passed
    assert re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)==[('6','0','0')]
    image=root/'rook2-candidate';admit_build(root/'candidate-build',image,CRATE,prepared['candidateSource'])
    plan=read(root/'observation-plan.json');assert plan['schema']=='rook2-frontier-scale-count-observation-v1'
    assert plan['step']==STEP and plan['case']=='profile-35' and plan['options']==OPTIONS and plan['budget']==3
    assert plan['source']==prepared['candidateSource'] and plan['engine']==image_layout(image)
    assert plan['pipelineStartMonotonicNs']==start and plan['pipelineDeadlineMonotonicNs']==deadline
    assert plan['sourcePreparation']==str(prepared_path) and plan['preparationSha256']==sha(prepared_path)
    for name,digest in plan['inputSha256'].items():assert sha(name)==digest,name
    directory=root/'replay';row=read(directory/'result.json')
    native,count=audit.lifetime(directory,row,STEP,image,3,OPTIONS,plan['inputSha256'])
    assert count==row['orderedPosts']==13 and native['wall_ns']<=180*10**9
    assert row['placement']==audit_placement(directory,native,plan['inputSha256'])
    assert row['replayRunnerExit']==0 and not Path(f'/proc/{row["replayRunnerPid"]}').exists()
    assert state['stages'][2]['startedMonotonicNs']<=row['controllerStartMonotonicNs']<row['controllerEndMonotonicNs']<=state['stages'][2]['endedMonotonicNs']
    env=read(directory/'frontier-env.json')
    assert env==dict(schema='rook2-frontier-scale-environment-v1',variable=REPORT_ENV,path=str(directory/REPORT))
    report=read(directory/REPORT);assert row['frontierReport']==dict(path=str(directory/REPORT),sha256=sha(directory/REPORT))
    oracle=next(case for case in read(SPEC/'replay-oracle.json')['cases'] if case['id']=='profile-35')
    summary=report_audit(report,oracle,row['searchWallNs'])
    if not during:
        house=read(root/'housekeeping.json')
        assert house['failure'] is None and house['helperCpus']==house['postRestoreSelfAffinity']==sorted(HELPERS)
        assert len(house['applies'])==4 and house['restored'] is not None
        assert all(event['cpus']==event['selfAffinity']==sorted(HELPERS) for event in house['applies'])
        assert state['endedMonotonicNs']<deadline
    mutable={'pipeline.json','audit.stdout','audit.stderr','housekeeping.json'} if during else set()
    pins={str(path):sha(path) for path in root.rglob('*') if path.is_file() and path.name not in mutable and 'test-target' not in path.parts and 'candidate-build' not in path.parts}
    assert time.monotonic_ns()<deadline
    return dict(schema='rook2-frontier-scale-count-audit-v1',**summary,raw=str(root),duringPipeline=during,
        focusedPassed=6,replayLives=1,orderedPosts=13,move=oracle['move'],finalPost=oracle['posts'][-1],
        nativePid=native['native_pid'],supervisorPid=native['supervisor_pid'],replayRunnerPid=row['replayRunnerPid'],
        observedTaskAffinities=native['native_post_exec']['task_affinities'],terminalNativeReceipts=1,
        wholeCpuSeconds=row['wholeCpuSeconds'],wholeWallNs=row['wholeWallNs'],rssKiB=row['rssKiB'],searchWallNs=row['searchWallNs'],
        source=prepared['candidateSource'],image=plan['engine'],protectedArtifacts=state['protectedArtifacts'],
        stageExits={item['stage']:item['exit'] for item in state['stages']},pipelineStartMonotonicNs=start,pipelineDeadlineMonotonicNs=deadline,
        terminalAuditMonotonicNs=time.monotonic_ns(),rawSha256=pins,
        scope='One aggregate original35 mode3 observation; instrumented timing is not a speed comparison; S6 includes duplicates, not distinct/new/useful/ready work; no consumer, service, keys, cohort executor or automatic follow-on')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('--during-pipeline',action='store_true')
    args=parser.parse_args();root=args.root.resolve();output=root/('audit-before-restore.json' if args.during_pipeline else 'reconciled.json')
    assert not output.exists()
    try:
        value=audit_run(root,args.during_pipeline)
        with output.open('x') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
    except BaseException as error:
        with (root/'audit-failure.json').open('x') as stream:json.dump(dict(complete=False,failure=repr(error)),stream);stream.write('\n')
        raise
    print(json.dumps({name:value[name] for name in ['complete','censored','counts','boundaries','outcome']},indent=2))
    if not value['complete']:raise SystemExit(2)


if __name__=='__main__':main()
