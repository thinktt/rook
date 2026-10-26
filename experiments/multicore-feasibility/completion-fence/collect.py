#!/usr/bin/env python3
"""Fixed48 generic replay lives and4 idle probes using the frozen epoch collector."""
import argparse
import os
from pathlib import Path
import signal
import sys
import time
sys.dont_write_bytecode=True
from common import (HERE,HELPERS,CASES,NAMES,METRICS,LIMITS,admission,baseline,code_paths,
    dist,housekeeping,idle_probe,image_layout,preparation,prepared_run,read,run_lifetime,schedule,sha,variants,write)

def main():
    def interrupted(signum,_frame): raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]: signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['preparation','prepared-run','output']: parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    prepared_path,record_path=args.preparation.resolve(),args.prepared_run.resolve()
    prepared=preparation(prepared_path)
    record=prepared_run(record_path,prepared_path,prepared)
    assert isinstance(record,dict)
    assert set(os.sched_getaffinity(0))==HELPERS
    assert CASES==['profile-35','profile-08','profile-43']
    assert NAMES==['preserved1','preserved3','inline1','fence3']
    candidate=Path(record['candidate']['path'])
    receipts=admission(record_path.parent/'candidate-build',candidate,prepared)
    out=args.output.resolve();out.mkdir()
    modes=variants(candidate)
    assert list(modes)==NAMES
    assert len(prepared['controlSource'])==len(prepared['candidateSource'])==68
    assert prepared['sourceChanges']==['src/colors_worker.rs']
    assert prepared['sourceAdded']==prepared['sourceRemoved']==[]
    for name,budget in zip(NAMES,[1,3,1,3]):
        assert modes[name]['budget']==budget and modes[name]['report'] is True
        assert modes[name]['options']==['--threads='+str(budget),'--owner-local-inventory','--q-owner-local-inventory']
    assert modes['preserved1']['path']==modes['preserved3']['path']==record['control']['path']
    assert modes['inline1']['path']==modes['fence3']['path']==record['candidate']['path']
    inputs=code_paths()+[prepared_path,record_path]+[Path(row['path']) for row in modes.values()]
    for field in ['inputSha256','reusedEvidenceSha256']: inputs += [Path(path) for path in prepared[field]]
    inputs += [Path(path) for path in record['inputSha256']]+[Path(path) for path in baseline()]
    from common import CONTROL_BUILD
    for directory,receipt in zip([CONTROL_BUILD,record_path.parent/'candidate-build'],receipts):
        inputs += [directory/'receipt.json',directory/'build.stderr']
        inputs += [directory/'source-before'/name for name in (receipt['source_sha256_before']|receipt['tool_sha256_before'])]
    start=time.monotonic_ns()
    plan=dict(schema='rook2-completion-fence-generic-v1',variants=modes,schedule=schedule(),
        sourcePreparation=str(prepared_path),preparedRun=str(record_path),
        candidateBuild=str(record_path.parent/'candidate-build'),
        sourceChanges=prepared['sourceChanges'],sourceAdded=prepared['sourceAdded'],sourceRemoved=prepared['sourceRemoved'],
        sourceChallenge=prepared['sourceChallenge'],
        controlSource=prepared['controlSource'],candidateSource=prepared['candidateSource'],
        evidenceReuse=prepared['evidenceReuse'],readinessSemantics=prepared['readinessSemantics'],
        images={name:image_layout(Path(value['path'])) for name,value in modes.items()},
        coordinatorCpu=14,helperCpus=[6,4],idleOwnedSiblings=[5,7,15],helperAffinity=sorted(HELPERS),
        nativePreExecAffinities={'1':[6,14],'2':[6,14],'3':[4,6,14]},
        inputSha256={str(path):sha(path) for path in sorted(set(inputs))},protectedArtifacts=baseline(),limits=LIMITS,
        pipelineStartMonotonicNs=record['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=record['pipelineDeadlineMonotonicNs'],
        streamStartMonotonicNs=start,
        boundaries=dict(search='unchanged raw tap go-write through move-data callback',
            cpu='direct native wait4 including joined threads/Python pre-exec prefix',rss='whole native lifetime peak RSS',
            placement='main14/helper6, color second helper4; verified before first setup input',
            observations='unchanged mode3 colors512 observations; owner-ready precedes ordinary/Q hooks; sampled residual join excludes eager generation and cannot measure saved work; no added report fields or hot census'),
        scope='one completion notification discriminator, fixed48+4; no observer additions/PGO/qualification/adoption')
    write(out/'plan.json',plan)
    state=dict(complete=False,failure=None,runs=[],idle=[],streamStartMonotonicNs=start)
    write(out/'progress.json',state)
    deadline_ns=min(record['pipelineDeadlineMonotonicNs'],start+LIMITS['totalSeconds']*10**9)
    deadline=deadline_ns/1e9
    placement=housekeeping.Placement()
    house=dict(schema='rook2-completion-fence-housekeeping-v1',helperCpus=sorted(HELPERS),
        applies=[],originals=[],leaders=[],restored=None,failure=None)
    def place():
        house['applies'].append(placement.apply(HELPERS))
        house['originals']=[dict(pid=p,tid=t,starttime=s,affinity=mask) for (p,t,s),mask in sorted(placement.original.items())]
        house['leaders']=[dict(pid=p,starttime=s,affinity=mask) for (p,s),mask in sorted(placement.leaders.items())]
        write(out/'housekeeping.json',house)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for index,step in enumerate(plan['schedule']):
            assert time.monotonic_ns()<deadline_ns
            place();value=modes[step['variant']]
            directory=out/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
            state['runs'].append(run_lifetime(directory,step,Path(value['path']),value,deadline,plan['inputSha256']))
            write(out/'progress.json',state)
        for name,value in modes.items():
            assert time.monotonic()+35<deadline
            place()
            state['idle'].append(idle_probe(out/('idle-'+name),name,Path(value['path']),value,deadline,plan['inputSha256']))
            write(out/'progress.json',state)
        state['summaries']=[dict(case=case,variant=name,**{key:dist([row[key] for row in state['runs']
            if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
        assert all(sha(path)==digest for path,digest in plan['inputSha256'].items())
        admission(record_path.parent/'candidate-build',candidate,prepared)
        state['complete']=True
    except BaseException as error:
        state['failure']=repr(error)
        write(out/'failure.json',dict(error=repr(error),completedReplayLives=len(state['runs']),completedIdleLives=len(state['idle'])))
        raise
    finally:
        try:
            house['restored']=placement.restore();house['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
        except BaseException as error:
            house['failure']=repr(error);state.update(complete=False,failure=repr(error));raise
        finally:
            write(out/'housekeeping.json',house)
            (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
            if state['complete']:
                state['streamEndMonotonicNs']=time.monotonic_ns()
                if state['streamEndMonotonicNs']>=deadline_ns: state.update(complete=False,failure='deadline during cleanup')
            write(out/'result.json',state)
    assert state['complete'] and state['failure'] is None
    print('complete48 replay lives +4 idle probes',flush=True)


if __name__=='__main__': main()
