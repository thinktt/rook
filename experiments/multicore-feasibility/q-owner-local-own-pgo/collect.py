#!/usr/bin/env python3
"""Frozen270 descriptive original54 lives and5 idle probes; no repeat or screen."""
import argparse
import os
from pathlib import Path
import signal
import sys
import time

sys.dont_write_bytecode = True
from common import (HELPERS, LIMITS, METRICS, NAMES, SERIAL_BUILD, RETAINED_BUILD,
    admit_build, baseline, cases, code_paths, drift, generic_evidence, housekeeping,
    idle_probe, image_layout, preparation, prepared_run, read, run_lifetime,
    schedule, sha, variants, write)


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation', type=Path, required=True)
    parser.add_argument('--prepared-run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepared_path, record_path = args.preparation.resolve(), args.prepared_run.resolve()
    prepared = preparation(prepared_path)
    record, receipt, effective = prepared_run(record_path, prepared_path, prepared)
    assert set(os.sched_getaffinity(0)) == HELPERS
    assert NAMES == ['serial1','retained3','inline1','q-off3','q-on3']
    candidate = Path(record['candidate']['path'])
    modes, steps = variants(candidate), schedule()
    assert list(modes) == NAMES and len(steps) == 270
    slots = {name:[0]*5 for name in NAMES}
    for index, step in enumerate(steps):
        slots[step['variant']][index%5] += 1
    assert all(sum(counts)==54 and sorted(counts)==[10,11,11,11,11] for counts in slots.values())
    out = args.output.resolve(); out.mkdir()
    inputs = code_paths()+[prepared_path,record_path,record_path.parent/'housekeeping-prepare.json']
    inputs += [Path(path) for path in record['inputSha256']]
    inputs += [Path(path) for path in prepared['inputSha256']]
    inputs += [Path(path) for path in prepared['reusedEvidenceSha256']]
    inputs += [Path(path) for path in baseline()]
    inputs += [Path(value['path']) for value in modes.values()]
    inputs += [directory/'receipt.json' for directory in [SERIAL_BUILD,RETAINED_BUILD]]
    for directory in [record_path.parent/'instrumented-build',record_path.parent/'use-build']:
        saved = read(directory/'receipt.json')
        inputs += [directory/'source-before'/name for name in
            (saved['source_sha256_before'] | saved['tool_sha256_before'])]
    training = read(record_path.parent/'training/training.json')
    inputs += [Path(path) for path in training['raw_profiles_sha256']]
    inputs += [Path(path) for path in training['input_sha256']]
    start = time.monotonic_ns()
    plan = dict(schema='rook2-q-owner-local-own-pgo-full54-v1', study='descriptive-original54',
        cases=cases(), variants=modes, schedule=steps, rotationSlotCounts=slots,
        rotationSemantics='54 cases/five configurations: exact10/11 placements per slot, not perfectly balanced',
        sourcePreparation=str(prepared_path), preparedRun=str(record_path),
        candidateBuild=str(record_path.parent/'use-build'), source=prepared['candidateSource'],
        effectiveRustcOptions=effective, profileSha256=record['profileSha256'],
        drift=drift(prepared,record_path.parent/'training/merged.profdata'),
        images={name:image_layout(Path(value['path'])) for name,value in modes.items()},
        readinessSemantics=prepared['readinessSemantics'], evidenceReuse=generic_evidence(prepared),
        inputSha256={str(path):sha(path) for path in sorted(set(inputs))}, protectedArtifacts=baseline(),
        coordinatorCpu=14, helperCpus=[6,4], idleOwnedSiblings=[5,7,15], helperAffinity=sorted(HELPERS),
        nativePreExecAffinities={'1':[6,14],'2':[6,14],'3':[4,6,14]}, limits=LIMITS,
        pipelineStartMonotonicNs=record['pipelineStartMonotonicNs'],
        pipelineDeadlineMonotonicNs=record['pipelineDeadlineMonotonicNs'],
        streamStartMonotonicNs=start,
        boundaries=dict(search='frozen original tap go-write through move-data callback',
            cpu='direct native wait4: all joined threads and Python pre-exec prefix', rss='whole native lifetime peak RSS',
            placement='external main14/helpers6/4, verified before first input; siblings15/7/5 unassigned by us',
            counters='unchanged sparse512 phase; owner_ready before eager generation, residual join starts after hook and excludes generation',
            lifecycle='five separate startup/250ms process-tick idle/quit probes'),
        scope='single observations/configuration/case; complete sums, no per-case medians/confidence, no qualification/adoption; training is not timing evidence')
    write(out/'plan.json', plan)
    state = dict(complete=False,failure=None,runs=[],idle=[],streamStartMonotonicNs=start)
    write(out/'progress.json', state)
    deadline_ns = min(record['pipelineDeadlineMonotonicNs'], start+LIMITS['totalSeconds']*10**9)
    deadline = deadline_ns/1e9
    place = housekeeping.Placement()
    house = dict(schema='rook2-q-owner-local-own-pgo-housekeeping-v1',helperCpus=sorted(HELPERS),
        applies=[],originals=[],leaders=[],restored=None,failure=None)

    def apply():
        house['applies'].append(place.apply(HELPERS))
        house['originals'] = [dict(pid=p,tid=t,starttime=s,affinity=mask)
            for (p,t,s),mask in sorted(place.original.items())]
        house['leaders'] = [dict(pid=p,starttime=s,affinity=mask) for (p,s),mask in sorted(place.leaders.items())]
        write(out/'housekeeping.json', house)

    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for index, step in enumerate(steps):
            assert time.monotonic() < deadline, 'comparison/pipeline deadline'
            apply()
            value = modes[step['variant']]
            directory = out/f'{index:03d}-{step["case"]}-{step["variant"]}-r1'
            state['runs'].append(run_lifetime(directory,step,Path(value['path']),value,deadline,plan['inputSha256']))
            write(out/'progress.json',state)
        for name,value in modes.items():
            assert time.monotonic()+35 < deadline, 'insufficient idle allowance'
            apply()
            state['idle'].append(idle_probe(out/('idle-'+name),name,Path(value['path']),value,deadline,plan['inputSha256']))
            write(out/'progress.json',state)
        state['table'] = [dict(case=case, **{name:{key:next(row[key] for row in state['runs']
            if row['case']==case and row['variant']==name) for key in METRICS} for name in NAMES}) for case in cases()]
        state['totals'] = {name:{key:sum(row[key] for row in state['runs'] if row['variant']==name)
            for key in METRICS[:-1]} for name in NAMES}
        assert all(sha(path)==digest for path,digest in plan['inputSha256'].items())
        admit_build(record_path.parent/'use-build',candidate,'profile-use',prepared)
        assert time.monotonic() < deadline
        state.update(complete=True,streamEndMonotonicNs=time.monotonic_ns())
    except BaseException as error:
        state['failure']=repr(error)
        write(out/'failure.json',dict(error=repr(error),completedReplayLives=len(state['runs']),completedIdleLives=len(state['idle'])))
        raise
    finally:
        try:
            house['restored']=place.restore()
            house['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
        except BaseException as error:
            house['failure']=repr(error)
            state.update(complete=False,failure='housekeeping restoration failed: '+repr(error))
            raise
        finally:
            write(out/'housekeeping.json',house)
            (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
            if state['complete']:
                state['streamEndMonotonicNs'] = time.monotonic_ns()
                if state['streamEndMonotonicNs'] >= deadline_ns:
                    state.update(complete=False,failure='comparison/pipeline deadline during cleanup')
            write(out/'result.json',state)
    assert state['complete'] and state['failure'] is None, state['failure']
    print('complete270 original54 replay lives +5 idle probes',flush=True)


if __name__=='__main__':
    main()
