#!/usr/bin/env python3
"""Read-only bounded union of60 saved replay lives and5 completed idle probes."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from common import (ACCOUNT,HELPERS,LIMITS,METRICS,CASES,NAMES,admission,audit,audit_placement,
    baseline,code_paths,dist,image_layout,native_receipt,preparation,
    prepared_run,read,readiness,readiness_summary,sha,variants)


def housekeeping_audit(path,expected_applies):
    record = read(path)
    assert record['schema'] == 'rook2-whole-full-epoch-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus'] == sorted(HELPERS)
    assert len(record['applies']) == expected_applies and record['restored'] is not None
    originals, leaders, observed = {}, {}, {}
    for row in record['originals']:
        key = (row['pid'], row['tid'], row['starttime'])
        assert key not in originals and row['affinity']
        originals[key] = row['affinity']
    for row in record['leaders']:
        key = (row['pid'], row['starttime'])
        assert key not in leaders and row['affinity']
        leaders[key] = row['affinity']
    for event in record['applies']:
        assert event['cpus'] == event['selfAffinity'] == sorted(HELPERS)
        for row in event['selectedTasks']:
            key = (row['pid'], row['tid'], row['starttime'])
            assert row['after'] == sorted(HELPERS)
            if key in observed:
                assert row['before'] == sorted(HELPERS)
            else:
                assert originals[key] == row['before']
                observed[key] = row['before']
    assert observed == originals
    for row in record['restored']:
        key = (row['pid'], row['tid'], row['starttime'])
        if key in originals:
            assert not row['inheritedNewThread'] and row['restored'] == originals[key]
        else:
            masks = [mask for (pid, _), mask in leaders.items() if pid == row['pid']]
            assert len(masks) == 1 and row['inheritedNewThread'] and row['restored'] == masks[0]
    assert record['postRestoreSelfAffinity'] == sorted(HELPERS)
    return dict(selectedOriginalTasks=len(originals), restoredTasks=len(record['restored']),
                applyCount=len(record['applies']), receiptSha256=sha(path))


def completion_binding(original,completion,plan,oldresult,repair,newresult):
    pipeline=read(original/'pipeline.json')
    assert repair['schema']=='rook2-whole-full-epoch-idle-completion-v1'
    assert repair['original']==str(original)
    assert repair['oldPlanSha256']==sha(original/'pilot/plan.json')
    assert repair['oldResultSha256']==sha(original/'pilot/result.json')
    assert repair['oldPipelineSha256']==sha(original/'pipeline.json')
    assert not oldresult['complete'] and oldresult['idle']==[] and len(oldresult['runs'])==60
    assert 'check_task_masks' in oldresult['failure'] and 'ImportError' in oldresult['failure']
    assert not pipeline['complete'] and pipeline['prepared'] and not pipeline['collected']
    assert pipeline['failure']=="AssertionError(('collection', 1))"
    assert pipeline['stages'][-1]['stage']=='collection' and pipeline['stages'][-1]['exit']==1
    for suffix in ['stdout','stderr']:
        assert sha(original/('collection.'+suffix))==pipeline['stages'][-1][suffix+'Sha256']
    assert repair['pipelineStartMonotonicNs']==pipeline['pipelineStartMonotonicNs']==plan['pipelineStartMonotonicNs']
    assert repair['pipelineDeadlineMonotonicNs']==pipeline['pipelineDeadlineMonotonicNs']==plan['pipelineDeadlineMonotonicNs']
    assert repair['pipelineDeadlineMonotonicNs']==repair['pipelineStartMonotonicNs']+3600*10**9
    assert repair['collectionStartMonotonicNs']==plan['streamStartMonotonicNs']==oldresult['streamStartMonotonicNs']
    assert repair['collectionDeadlineMonotonicNs']==min(repair['pipelineDeadlineMonotonicNs'],repair['collectionStartMonotonicNs']+1800*10**9)
    assert repair['idleNames']==NAMES and repair['variants']==plan['variants']
    assert repair['originalPins']==plan['inputSha256']
    assert repair['adapter']=='common.check_task_masks = common.epoch.check_task_masks; original files unchanged'
    adapter=Path(__file__).with_name('finish_idle.py')
    assert repair['inputSha256'][str(adapter)]==sha(adapter)
    required=[original/'pipeline.json',original/'pilot/plan.json',original/'pilot/result.json',
        original/'collection.stderr',original/'prepared-run.json']
    for path in required: assert repair['inputSha256'][str(path)]==sha(path)
    for path,digest in repair['inputSha256'].items(): assert sha(path)==digest,path
    failed=original/'pilot/idle-preserved2'
    for path in failed.iterdir():
        if path.is_file(): assert repair['inputSha256'][str(path)]==sha(path)
    ready,error=read(failed/'native.json.ready'),read(failed/'failure.json')
    assert ready['schema']=='rook2-external-placement-ready-v1' and ready['expected_threads']==2
    assert ready['engine']==plan['variants']['preserved2']['path']
    assert ready['engine_sha256']==sha(ready['engine'])
    assert ready['launcher_sha256']==plan['inputSha256'][str(ACCOUNT)]
    assert ready['native_pre_exec']==dict(pid=ready['native_pid'],pgid=ready['supervisor_pid'],affinity=[6,14])
    observed=ready['native_post_exec']
    assert observed['path']==ready['engine'] and observed['pgid']==ready['supervisor_pid'] and observed['affinity']==[14]
    assert len(observed['task_affinities'])==2 and observed['task_affinities'][str(ready['native_pid'])]==[14]
    assert [mask for tid,mask in observed['task_affinities'].items() if tid!=str(ready['native_pid'])]==[[6]]
    assert error['supervisorPid']==ready['supervisor_pid'] and error['exit']==-9
    assert error['error']==oldresult['failure']
    assert not (failed/'native.json').exists() and not (failed/'native.json.input-gate.json').exists()
    assert not (failed/'colors.json').exists()
    assert (failed/'stdin.raw').read_bytes()==(failed/'stdout.raw').read_bytes()==(failed/'stderr').read_bytes()==b''
    for pid in [ready['native_pid'],ready['supervisor_pid']]: assert not Path('/proc',str(pid)).exists(),'recorded failed-start PID live; possible reuse'
    expected=dict(directory=str(failed),nativePid=ready['native_pid'],supervisorPid=ready['supervisor_pid'],
        supervisorExit=-9,nativeExitReceiptAvailable=False,inputBytes=0,outputBytes=0)
    assert repair['failedPreinput']==expected
    assert newresult['complete'] and newresult['failure'] is None and len(newresult['idle'])==5
    assert newresult['streamStartMonotonicNs']==repair['completionStartMonotonicNs']
    assert oldresult['runs'][-1]['controllerEndMonotonicNs']<=int(ready['ready_monotonic_ns'])<=newresult['streamStartMonotonicNs']<newresult['streamEndMonotonicNs']<repair['collectionDeadlineMonotonicNs']
    successful_ids={row['nativePid'] for row in oldresult['runs']} | {row['nativePid'] for row in newresult['idle']}
    assert len(successful_ids)==65 and ready['native_pid'] not in successful_ids
    return dict(**expected,readySha256=sha(failed/'native.json.ready'),failureSha256=sha(failed/'failure.json'),
        explanation='Lazy helper import failed before first input; missing native exit receipt is disclosed. No completed idle request or benchmark life was repeated.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original',type=Path)
    parser.add_argument('completion',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    original,completion=args.original.resolve(),args.completion.resolve()
    base=original/'pilot'
    plan,oldresult=read(base/'plan.json'),read(base/'result.json')
    repair,newresult=read(completion/'plan.json'),read(completion/'result.json')
    failed=completion_binding(original,completion,plan,oldresult,repair,newresult)
    result=dict(runs=oldresult['runs'],idle=newresult['idle'],
        streamStartMonotonicNs=oldresult['streamStartMonotonicNs'],
        streamEndMonotonicNs=newresult['streamEndMonotonicNs'])
    assert plan['schema']=='rook2-whole-full-epoch-generic-v1'
    expected=[]
    for case in CASES:
        expected += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            expected += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(expected)==len(result['runs'])==60 and plan['schedule']==expected
    assert plan['coordinatorCpu']==14 and plan['helperCpus']==[6,4]
    assert plan['idleOwnedSiblings']==[5,7,15] and plan['helperAffinity']==sorted(HELPERS)
    assert plan['nativePreExecAffinities']=={'1':[6,14],'2':[6,14],'3':[4,6,14]}
    assert plan['limits']==LIMITS and plan['protectedArtifacts']==baseline()
    hashes=plan['inputSha256']
    assert all(str(path) in hashes for path in code_paths())
    for path,digest in hashes.items(): assert sha(path)==digest,path
    prepared_path,record_path=Path(plan['sourcePreparation']),Path(plan['preparedRun'])
    prepared=preparation(prepared_path);record=prepared_run(record_path,prepared_path,prepared)
    assert hashes[str(prepared_path)]==sha(prepared_path) and hashes[str(record_path)]==sha(record_path)
    for key in ['sourceChanges','controlSource','candidateSource','evidenceReuse','readinessSemantics']:
        assert plan[key]==prepared[key]
    modes=plan['variants'];assert list(modes)==NAMES and modes==variants(Path(record['candidate']['path']))
    assert plan['images']=={name:image_layout(Path(value['path'])) for name,value in modes.items()}
    assert plan['candidateBuild']==str(record_path.parent/'candidate-build')
    admission(record_path.parent/'candidate-build',Path(record['candidate']['path']),prepared)
    assert plan['pipelineStartMonotonicNs']==record['pipelineStartMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==record['pipelineDeadlineMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==plan['pipelineStartMonotonicNs']+3600*10**9
    start,end=result['streamStartMonotonicNs'],result['streamEndMonotonicNs']
    assert plan['streamStartMonotonicNs']==start and record['preparedMonotonicNs']<=start
    assert 0<end-start<=1800*10**9 and end<plan['pipelineDeadlineMonotonicNs']
    previous_end,pids,posts=start,set(),0
    for index,(step,row) in enumerate(zip(expected,result['runs'])):
        value=modes[step['variant']]
        directory=base/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        native,count=audit.lifetime(directory,row,step,Path(value['path']),value['budget'],value['options'],hashes)
        assert row['orderedPosts']==count and row['placement']==audit_placement(directory,native,hashes)
        assert previous_end<=row['controllerStartMonotonicNs']<=native['start_monotonic_ns']
        assert native['reaped_monotonic_ns']<=row['controllerEndMonotonicNs']<=end and native['wall_ns']<=180*10**9
        readiness(directory,row['colors'],value['budget'],True)
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']);posts+=count;previous_end=row['controllerEndMonotonicNs']
    assert len(result['idle'])==5
    for name,row in zip(NAMES,result['idle']):
        value,directory=modes[name],completion/('idle-'+name)
        assert row['variant']==name and read(directory/'probe.json')==row
        native=native_receipt(directory/'native.json',Path(value['path']),value['budget'],value['options'],hashes)
        assert read(directory/'launch.json')==dict(argv=[native['python_executable'],str(ACCOUNT),
            '--engine',value['path'],'--record',str(directory/'native.json'),'--known-single-process',
            '--thread-budget',str(value['budget']),*value['options']],variant=name,kind='startup-idle-shutdown')
        assert row['nativePid']==native['native_pid'] and row['supervisorPid']==native['supervisor_pid']
        assert row['wholeCpuSeconds']==native['total_cpu_s'] and row['wholeWallNs']==native['wall_ns']
        assert row['rssKiB']==native['maxrss_linux_kib'] and row['placement']==audit_placement(directory,native,hashes)
        assert row['idleCpuTicks']==row['shutdownStartCpuTicks']-row['startupCpuTicks']>=0
        assert row['tickHz']==read(next(base.glob('*-r0'))/'tap-config.json')['tickHz']
        assert row['idleCpuSeconds']==row['idleCpuTicks']/row['tickHz']
        assert row['idleNs']==row['idleEndMonotonicNs']-row['idleStartMonotonicNs']>=250_000_000
        assert previous_end<=native['start_monotonic_ns']<row['idleStartMonotonicNs']<row['idleEndMonotonicNs']<native['reaped_monotonic_ns']<=end
        assert row['startupReplyNs']>0 and row['shutdownSupervisorNs']>0
        assert (directory/'stdin.raw').read_bytes()==b'cm_parm\nquit\n' and (directory/'stdout.raw').read_bytes()==b'cm_parm\n'
        assert (directory/'stderr').read_bytes()==b''
        for file,digest in row['sha256'].items(): assert sha(directory/file)==digest
        readiness(directory,row['colors'],value['budget'],True,idle=True)
        assert native['native_pid'] not in pids;pids.add(native['native_pid']);previous_end=native['reaped_monotonic_ns']
    assert len(pids)==65
    summaries=[dict(case=case,variant=name,**{key:dist([row[key] for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
    by={(row['case'],row['variant']):row for row in summaries}
    pairs=[('wholeepoch2','preserved2'),('wholeepoch2','preserved3'),('wholeepoch2','colorepoch3'),
        ('wholeepoch2','inline1'),('colorepoch3','preserved3'),('inline1','preserved2')]
    comparisons=[dict(case=case,**{a+'Vs'+b:{key:by[case,a][key]['median']/by[case,b][key]['median']
        for key in METRICS[:3]} for a,b in pairs}) for case in CASES]
    sums={name:{key:sum(by[case,name][key]['median'] for case in CASES) for key in METRICS[:3]} for name in NAMES}
    color_readiness=[dict(case=case,variant=name,**readiness_summary([row for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]))
        for case in CASES for name in ['preserved3','colorepoch3']]
    colors=[]
    for case in CASES:
        reports=[row['colors']['report'] for row in result['runs'] if row['case']==case and row['variant'] in ['preserved3','colorepoch3']]
        assert len(reports)==8 and len({value['dispatches'] for value in reports})==1
        colors.append(dict(case=case,dispatches=reports[0]['dispatches']))
    cpus={'cpu4','cpu5','cpu6','cpu7','cpu14','cpu15'}
    def ticks(path):
        return {parts[0]:[int(item) for item in parts[1:]] for line in path.read_text().splitlines()
            if (parts:=line.split()) and parts[0] in cpus}
    before,after=ticks(base/'proc-stat-before'),ticks(base/'proc-stat-after')
    assert set(before)==set(after)==cpus
    old_deltas={cpu:[y-x for x,y in zip(before[cpu],after[cpu])] for cpu in cpus}
    assert all(len(before[cpu])==len(after[cpu]) and all(item>=0 for item in old_deltas[cpu]) for cpu in cpus)
    before,after=ticks(completion/'proc-stat-before'),ticks(completion/'proc-stat-after')
    assert set(before)==set(after)==cpus
    new_deltas={cpu:[y-x for x,y in zip(before[cpu],after[cpu])] for cpu in cpus}
    assert all(len(before[cpu])==len(after[cpu]) and all(item>=0 for item in new_deltas[cpu]) for cpu in cpus)
    deltas=dict(original=old_deltas,idleCompletion=new_deltas)
    output=dict(schema='rook2-whole-full-epoch-idle-completion-audit-v1',complete=True,replayLives=60,measured=45,warmups=15,idleProcesses=5,
        orderedPosts=posts,summaries=summaries,comparisons=comparisons,summedMedians=sums,
        colorDispatches=colors,readiness=color_readiness,idle=result['idle'],failedPreinput=failed,successfulNativeProcesses=65,physicalNativeProcesses=66,
        housekeeping=dict(original=housekeeping_audit(base/'housekeeping.json',61),
            idleCompletion=housekeeping_audit(completion/'housekeeping.json',5)),
        readinessSemantics=plan['readinessSemantics'],evidenceReuse=plan['evidenceReuse'],images=plan['images'],
        sourceChanges=plan['sourceChanges'],
        guestCpuTickDeltas=deltas,raw=str(base),idleCompletion=str(completion),
        originalRawSha256={name:sha(base/name) for name in ['plan.json','result.json','housekeeping.json','proc-stat-before','proc-stat-after']},
        completionRawSha256={name:sha(completion/name) for name in ['plan.json','result.json','housekeeping.json','proc-stat-before','proc-stat-after']},
        pipelineStartMonotonicNs=repair['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=repair['pipelineDeadlineMonotonicNs'],
        collectionStartMonotonicNs=start,collectionDeadlineMonotonicNs=repair['collectionDeadlineMonotonicNs'],
        streamEndMonotonicNs=end,adapter=repair['adapter'],adapterInputSha256=repair['inputSha256'],
        reconcilerSha256=sha(Path(__file__)),
        scope='Original60 benchmark lives unchanged; five previously unstarted idle probes completed with one in-memory lazy-import alias. One pre-input setup failure has no native exit receipt; supervisor-9 is recorded, not classified as an engine failure. Both original clocks retained; no benchmark repeated or source/image rebuilt.')
    with (args.output or completion/'reconciled.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','replayLives','orderedPosts','summedMedians','comparisons']},indent=2))


if __name__=='__main__': main()
