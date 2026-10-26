#!/usr/bin/env python3
"""Frozen five-mode60 depth8 actual-search lives; no wire replay or idle series."""
import argparse
import os
from pathlib import Path
import signal
import sys
import time

sys.dont_write_bytecode=True
from common import (HERE,HELPERS,CASES,NAMES,LIMITS,METRICS,baseline,code_paths,
    preparation,prepared_run,read,write,sha,variants,schedule,run_lifetime,housekeeping,dist)


def main():
    def interrupted(signum,_frame):raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]:signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['preparation','prepared-run','output']:parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();prepared_path=args.preparation.resolve();record_path=args.prepared_run.resolve()
    prepared=preparation(prepared_path);record=prepared_run(record_path,prepared_path,prepared)
    assert set(os.sched_getaffinity(0))==HELPERS
    modes=variants(Path(record['images']['preserved']['path']),Path(record['images']['new']['path']))
    out=args.output.resolve();out.mkdir();start=time.monotonic_ns()
    inputs=code_paths()+[prepared_path,record_path]+[Path(path) for path in record['inputSha256']]
    for row in record['audits']:
        inputs += [Path(row['directory'])/name for name in row['sha256']]
    plan=dict(schema='rook2-replicated-control-timing-v1',sourcePreparation=str(prepared_path),preparedRun=str(record_path),
        variants=modes,schedule=schedule(),depth=8,audit=False,seed=0,inputs=record['inputs'],limits=LIMITS,
        inputSha256={str(path):sha(path) for path in sorted(set(inputs))},protectedArtifacts=baseline(),
        helperAffinity=sorted(HELPERS),coordinatorCpu=14,peerCpus=[6,4],unassignedOwnedSiblings=[5,7,15],
        pipelineStartMonotonicNs=record['pipelineStartMonotonicNs'],pipelineDeadlineMonotonicNs=record['pipelineDeadlineMonotonicNs'],
        streamStartMonotonicNs=start,
        boundaries=dict(search='driver gated actual fixed-depth Search calls through joined peer/helper shutdown',
            cpu='direct native wait4 all joined threads plus Python pre-exec prefix',rss='whole native lifetime peak RSS',
            placement='actual native tasks pinned before saved GO; READY plus supervisor identity gate'),
        scope='NoHost/unrestricted fixed-completion depth8; original input/config/history, seed0/rnd0; matched unwind study builds, not original production timed protocol or original7ac executable performance')
    write(out/'plan.json',plan)
    state=dict(complete=False,failure=None,runs=[],outcomes={},streamStartMonotonicNs=start)
    deadline=min(record['pipelineDeadlineMonotonicNs'],start+1800*10**9)/1e9
    place=housekeeping.Placement();house=dict(helperCpus=sorted(HELPERS),applies=[],originals=[],leaders=[],restored=None,failure=None)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for index,step in enumerate(plan['schedule']):
            assert time.monotonic()<deadline,'collection/pipeline deadline'
            house['applies'].append(place.apply(HELPERS))
            house['originals']=[dict(pid=p,tid=t,starttime=s,affinity=mask) for (p,t,s),mask in sorted(place.original.items())]
            house['leaders']=[dict(pid=p,starttime=s,affinity=mask) for (p,s),mask in sorted(place.leaders.items())]
            write(out/'housekeeping.json',house);variant=modes[step['variant']]
            row=run_lifetime(out/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}',step,
                Path(variant['path']),variant,deadline,plan['inputSha256'],Path(record['inputs'][step['case']]['path']))
            state['runs'].append(row);write(out/'progress.json',state)
            outcome=row['report']['outcome'];canonical=state['outcomes'].setdefault(step['case'],outcome)
            assert outcome==canonical,'whole structured outcome differs: '+step['case']+' '+step['variant']
            write(out/'progress.json',state)
        assert all(sha(path)==digest for path,digest in plan['inputSha256'].items())
        state['summaries']=[dict(case=case,variant=name,**{key:dist([row[key] for row in state['runs']
            if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
        state['complete']=True
    except BaseException as error:
        state['failure']=repr(error);write(out/'failure.json',dict(error=repr(error),completedLives=len(state['runs'])));raise
    finally:
        try:house['restored']=place.restore();house['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
        except BaseException as error:house['failure']=repr(error);state.update(complete=False,failure=repr(error));raise
        finally:
            write(out/'housekeeping.json',house);(out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
            state['streamEndMonotonicNs']=time.monotonic_ns()
            if state['streamEndMonotonicNs']>=deadline*1e9:state.update(complete=False,failure='collection/pipeline deadline during cleanup')
            write(out/'result.json',state)
    assert state['complete'] and state['failure'] is None
    print('completed60 matched fixed-depth actual-search lives; no production replay posts',flush=True)


if __name__=='__main__':main()
