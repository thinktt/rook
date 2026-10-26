#!/usr/bin/env python3
"""Complete the unchanged schedule after the retained pre-input comm failure.

Reuse3 excluded historical warmups; execute only remaining45 lives and4 idle
probes. No build/test/native-control repetition and no deadline extension.
"""
import argparse
import os
from pathlib import Path
import signal
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, HELPERS, CASES, NAMES, METRICS, baseline, dist,
                    housekeeping, module, sha, write)
from completion_common import (ORIGINAL, completion_paths, epoch_binding,
                               failed_startup, inspect)


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, default=ORIGINAL)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    context = inspect(args.original)
    failed = failed_startup(context)
    original, old_plan, pipeline = context['original'], context['plan'], context['pipeline']
    assert set(os.sched_getaffinity(0)) == HELPERS
    collection_start = context['result']['streamStartMonotonicNs']
    pipeline_start = pipeline['pipelineStartMonotonicNs']
    deadline = min(collection_start/1e9+1800, pipeline_start/1e9+3600)
    assert time.monotonic()+35 < deadline, 'original collection/pipeline allowance exhausted'
    out = args.output.resolve(); out.mkdir()
    old_hashes = old_plan['inputSha256']
    inputs = completion_paths()+[context['frozen']/'manifest.json', original/'pipeline.json',
        original/'pilot/plan.json', original/'pilot/result.json', original/'pilot/housekeeping.json',
        HERE/'preparation.json']
    inputs += [Path(path) for path in old_hashes if Path(path) not in [HERE/'common.py', HERE/'account_threads.py']]
    hashes = {str(path): sha(path) for path in sorted(set(inputs))}
    plan = dict(schema='rook2-colors-three-completion-v1', original=str(original),
        originalPlanSha256=sha(original/'pilot/plan.json'), originalPipelineSha256=sha(original/'pipeline.json'),
        originalResultSha256=sha(original/'pilot/result.json'),
        frozenManifest=str(context['frozen']/'manifest.json'),
        frozenManifestSha256=sha(context['frozen']/'manifest.json'),
        schedule=old_plan['schedule'], variants=old_plan['variants'],
        originalInputSha256=old_hashes, inputSha256=hashes, repairs=context['repairs'],
        historicalReplayLives=3, remainingReplayLives=45, remainingIdleLives=4,
        failedStartup=failed, pipelineStartMonotonicNs=pipeline_start,
        collectionStartMonotonicNs=collection_start, pipelineSeconds=3600, collectionSeconds=1800,
        perLifeSeconds=180, protectedArtifacts=baseline(),
        controlBuild=old_plan['controlBuild'], candidateBuild=old_plan['candidateBuild'],
        sourcePreparation=str(HERE/'preparation.json'),
        scope='metadata-only comm-field repair; no completed life repeated, no engine/source rebuild,38 focused controls and2 affinity lives reused')
    write(out/'plan.json', plan)
    state = dict(complete=False, failure=None, runs=list(context['result']['runs']), idle=[],
        bindings=[epoch_binding(index, row, 'original', old_hashes)
                  for index, row in enumerate(context['result']['runs'])],
        streamStartMonotonicNs=collection_start, pipelineStartMonotonicNs=pipeline_start,
        resumeStartMonotonicNs=time.monotonic_ns())
    write(out/'progress.json', state)
    collector = module('colors_three_unchanged_collector_for_completion', HERE/'collect.py')
    place = housekeeping.Placement()
    housekeeping_record = dict(schema='rook2-colors-three-housekeeping-v1', helperCpus=sorted(HELPERS),
        applies=[], originals=[], leaders=[], restored=None, failure=None)

    def apply():
        housekeeping_record['applies'].append(place.apply(HELPERS))
        housekeeping_record['originals'] = [dict(pid=p, tid=t, starttime=s, affinity=mask)
            for (p, t, s), mask in sorted(place.original.items())]
        housekeeping_record['leaders'] = [dict(pid=p, starttime=s, affinity=mask)
            for (p, s), mask in sorted(place.leaders.items())]
        write(out/'housekeeping.json', housekeeping_record)

    def immutable():
        assert all(sha(path) == digest for path, digest in hashes.items())
        assert inspect(original)['repairs'] == plan['repairs']

    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for index in range(3, 48):
            assert time.monotonic() < deadline, 'unchanged original aggregate allowance'
            apply()
            step = plan['schedule'][index]
            value = plan['variants'][step['variant']]
            directory = out/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
            row = collector.run_lifetime(directory, step, Path(value['path']), value, deadline, hashes)
            state['runs'].append(row)
            state['bindings'].append(epoch_binding(index, row, 'repaired', hashes))
            write(out/'progress.json', state)
        for name, value in plan['variants'].items():
            assert time.monotonic()+35 < deadline, 'unchanged original idle allowance'
            apply()
            state['idle'].append(collector.idle_probe(out/('idle-'+name), name, Path(value['path']), value, deadline, hashes))
        state['idleBindings'] = [dict(variant=name, epoch='repaired',
            **{key: value for key, value in epoch_binding(-1, dict(directory=str(out/('idle-'+name))),
                'repaired', hashes).items() if key not in ['scheduleIndex', 'epoch']}) for name in NAMES]
        state['summaries'] = []
        for case in CASES:
            for name in NAMES:
                rows = [r for r in state['runs'] if r['case'] == case and r['variant'] == name and not r['warmup']]
                assert len(rows) == 3
                state['summaries'].append(dict(case=case, variant=name,
                    **{key: dist([row[key] for row in rows]) for key in METRICS}))
        immutable()
        assert time.monotonic() < deadline
        state.update(complete=True, streamEndMonotonicNs=time.monotonic_ns(), reusedReplayLives=3,
            executedReplayLives=45, executedIdleLives=4)
    except BaseException as error:
        state['failure'] = repr(error)
        write(out/'failure.json', dict(error=repr(error), totalCompletedReplayLives=len(state['runs']),
                                      newCompletedReplayLives=len(state['runs'])-3))
        raise
    finally:
        try:
            housekeeping_record['restored'] = place.restore()
            housekeeping_record['postRestoreSelfAffinity'] = sorted(os.sched_getaffinity(0))
        except BaseException as error:
            housekeeping_record['failure'] = repr(error)
            state.update(complete=False, failure='housekeeping restoration failed: '+repr(error))
            raise
        finally:
            write(out/'housekeeping.json', housekeeping_record)
            (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
            write(out/'result.json', state)
    print('completed original48 using3 historical warmups+45 new lives;4 idle; no caps extended', flush=True)


if __name__ == '__main__':
    main()
