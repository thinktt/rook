#!/usr/bin/env python3
"""Complete only five unstarted idle probes after the preserved lazy-import failure."""
import argparse
import os
from pathlib import Path
import time
import common as c


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();original=args.original.resolve();out=args.output.resolve()
    assert set(os.sched_getaffinity(0))==c.HELPERS
    pipeline=c.read(original/'pipeline.json');oldplan=c.read(original/'pilot/plan.json');oldresult=c.read(original/'pilot/result.json')
    assert len(oldresult['runs'])==60 and oldresult['idle']==[] and not oldresult['complete']
    assert 'check_task_masks' in oldresult['failure'] and 'ImportError' in oldresult['failure']
    assert pipeline['failure'] and pipeline['stages'][-1]['stage']=='collection' and pipeline['stages'][-1]['exit']==1
    failed=original/'pilot/idle-preserved2';ready=c.read(failed/'native.json.ready')
    assert (failed/'stdin.raw').read_bytes()==(failed/'stdout.raw').read_bytes()==b''
    assert not (failed/'native.json.input-gate.json').exists() and not (failed/'native.json').exists()
    assert c.read(failed/'failure.json')['exit']==-9
    for pid in [ready['native_pid'],ready['supervisor_pid']]:assert not Path('/proc',str(pid)).exists()
    for file,digest in oldplan['inputSha256'].items():assert c.sha(file)==digest,file
    preparedpath=Path(oldplan['sourcePreparation']);prepared=c.preparation(preparedpath)
    c.prepared_run(original/'prepared-run.json',preparedpath,prepared)
    assert pipeline['pipelineStartMonotonicNs']==oldplan['pipelineStartMonotonicNs']
    assert pipeline['pipelineDeadlineMonotonicNs']==oldplan['pipelineDeadlineMonotonicNs']==pipeline['pipelineStartMonotonicNs']+3600*10**9
    collection_deadline=min(pipeline['pipelineDeadlineMonotonicNs'],oldplan['streamStartMonotonicNs']+1800*10**9)
    assert time.monotonic_ns()<collection_deadline
    out.mkdir();start=time.monotonic_ns()
    # The reused idle ready_record's sole lazy import. Export the exact frozen
    # function in memory; do not edit any original code/source/input binding.
    assert not hasattr(c,'check_task_masks')
    c.check_task_masks=c.epoch.check_task_masks
    inputs=[Path(__file__),original/'pipeline.json',original/'pilot/plan.json',original/'pilot/result.json',original/'collection.stderr',original/'prepared-run.json']
    inputs += [file for file in failed.iterdir() if file.is_file()]
    reconcile=Path(__file__).with_name('repair_reconcile.py')
    if reconcile.exists():inputs.append(reconcile)
    plan=dict(schema='rook2-whole-full-epoch-idle-completion-v1',original=str(original),
        oldPlanSha256=c.sha(original/'pilot/plan.json'),oldResultSha256=c.sha(original/'pilot/result.json'),oldPipelineSha256=c.sha(original/'pipeline.json'),
        pipelineStartMonotonicNs=pipeline['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=pipeline['pipelineDeadlineMonotonicNs'],
        collectionStartMonotonicNs=oldplan['streamStartMonotonicNs'],collectionDeadlineMonotonicNs=collection_deadline,
        completionStartMonotonicNs=start,idleNames=c.NAMES,variants=oldplan['variants'],
        originalPins=oldplan['inputSha256'],inputSha256={str(file):c.sha(file) for file in sorted(set(inputs))},
        adapter='common.check_task_masks = common.epoch.check_task_masks; original files unchanged',
        failedPreinput=dict(directory=str(failed),nativePid=ready['native_pid'],supervisorPid=ready['supervisor_pid'],supervisorExit=-9,nativeExitReceiptAvailable=False,inputBytes=0,outputBytes=0),
        scope='only five previously unstarted idle probes; preserve all60 completed benchmark lives, original failed records, source and images; inherit both original clocks')
    c.write(out/'plan.json',plan)
    state=dict(complete=False,failure=None,idle=[],streamStartMonotonicNs=start)
    c.write(out/'progress.json',state)
    placement=c.housekeeping.Placement()
    house=dict(schema='rook2-whole-full-epoch-housekeeping-v1',helperCpus=sorted(c.HELPERS),applies=[],originals=[],leaders=[],restored=None,failure=None)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for name,value in oldplan['variants'].items():
            assert time.monotonic_ns()<collection_deadline
            house['applies'].append(placement.apply(c.HELPERS))
            house['originals']=[dict(pid=p,tid=t,starttime=s,affinity=mask) for (p,t,s),mask in sorted(placement.original.items())]
            house['leaders']=[dict(pid=p,starttime=s,affinity=mask) for (p,s),mask in sorted(placement.leaders.items())]
            c.write(out/'housekeeping.json',house)
            deadline=min(collection_deadline/1e9,time.monotonic()+180)
            row=c.idle_probe(out/('idle-'+name),name,Path(value['path']),value,deadline,oldplan['inputSha256'])
            state['idle'].append(row);c.write(out/'progress.json',state)
        assert len(state['idle'])==5
        for file,digest in plan['originalPins'].items():assert c.sha(file)==digest,file
        for file,digest in plan['inputSha256'].items():assert c.sha(file)==digest,file
        state['complete']=True
    except BaseException as error:
        state['failure']=repr(error);raise
    finally:
        try:
            house['restored']=placement.restore();house['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
        except BaseException as error:
            house['failure']=repr(error);state.update(complete=False,failure=repr(error));raise
        finally:
            c.write(out/'housekeeping.json',house);(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
            state['streamEndMonotonicNs']=time.monotonic_ns()
            if state['streamEndMonotonicNs']>=collection_deadline:state.update(complete=False,failure='inherited deadline during cleanup')
            c.write(out/'result.json',state)
    assert state['complete'] and state['failure'] is None
    print('completed five idle probes; original60 unchanged',flush=True)


if __name__=='__main__':main()
