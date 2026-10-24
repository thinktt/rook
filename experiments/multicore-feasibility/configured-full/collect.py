#!/usr/bin/env python3
"""Four-configuration own-PGO comparison; no automatic extension or retry."""
import argparse
import os
from pathlib import Path
import statistics
import sys
import time

sys.dont_write_bytecode = True
from common import (HELPERS, NAMES, METRICS, admission, idle_probe, input_paths,
                    read, write, sha, run_lifetime, schedule, variants)


def distribution(samples):
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['serial', 'previous', 'candidate', 'build', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--full54', action='store_true', help='separately selected216-life descriptive run; never automatic')
    args = parser.parse_args()
    serial, previous, candidate, build = (getattr(args, n).resolve()
                                          for n in ['serial', 'previous', 'candidate', 'build'])
    receipt, effective, compatibility = admission(build, serial, previous, candidate)
    cases, steps = schedule(args.full54)
    modes = variants(serial, previous, candidate)
    out = args.output.resolve(); out.mkdir()
    plan = dict(schema='rook2-configured-full-pgo-v1',
                study='original54' if args.full54 else 'four-case',
                variants=modes, cases=cases, schedule=steps, build=str(build),
                effectiveRustcOptions=effective, preservedArtifacts=compatibility,
                coordinatorCpu=14, workerCpu=6, nativePreExecAffinity=[6, 14],
                idleOwnedSiblings=[7, 15], helperAffinity=sorted(os.sched_getaffinity(0)),
                inputSha256={str(path): sha(path) for path in input_paths(build, receipt, serial, previous, candidate)},
                limits=dict(perLifeSeconds=180, totalSeconds=1800,
                            supervisorPlacementSeconds=10, inputGateSeconds=12),
                idleVariants=[] if args.full54 else NAMES,
                boundaries=dict(search='frozen original tap go-write through move-data callback',
                    cpu='direct native wait4 all threads plus Python pre-exec prefix', rss='whole native lifetime peak RSS',
                    placement='start allowed6/14; configure before external main14/helper6 pin/verification; gate first setup input',
                    lifecycle='four separate startup/250ms process-tick idle/quit probes in small study'),
                limitations='no automatic numerical gate/extension; descriptive original54 single observations only when separately selected; no performance qualification/adoption')
    assert plan['helperAffinity'] == sorted(HELPERS)
    write(out/'plan.json', plan)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    state = dict(complete=False, failure=None, runs=[], idle=[], streamStartMonotonicNs=time.monotonic_ns())
    deadline = time.monotonic()+1800
    try:
        for i, step in enumerate(steps):
            assert time.monotonic() < deadline, 'aggregate study deadline'
            v = modes[step['variant']]
            directory = out/f'{i:03d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
            state['runs'].append(run_lifetime(directory, step, Path(v['path']),
                                              v['budget'], v['options'], deadline, plan['inputSha256']))
            write(out/'progress.json', state)
        if not args.full54:
            for name, v in modes.items():
                assert time.monotonic()+35 < deadline, 'insufficient aggregate idle allowance'
                state['idle'].append(idle_probe(out/('idle-'+name), name, Path(v['path']),
                                                 v['budget'], v['options'], deadline, plan['inputSha256']))
        summaries = []
        for case in cases:
            for name in NAMES:
                rows = [r for r in state['runs'] if r['case'] == case and r['variant'] == name and not r['warmup']]
                assert len(rows) == (1 if args.full54 else 3)
                summaries.append(dict(case=case, variant=name,
                    **{k: distribution([r[k] for r in rows]) for k in METRICS}))
        assert all(sha(Path(path)) == digest for path, digest in plan['inputSha256'].items())
        admission(build, serial, previous, candidate)
        assert time.monotonic() < deadline
        state.update(complete=True, summaries=summaries, streamEndMonotonicNs=time.monotonic_ns(),
                     qualification='descriptive216 original54 observations, no warmups/idle probes' if args.full54 else
                         'four-case own-PGO research:48 retained replay lives,16 excluded warmups,4 separate idle probes',
                     automaticExtension=False)
        write(out/'result.json', state)
    except BaseException as error:
        state['failure'] = repr(error)
        write(out/'result.json', state)
        write(out/'failure.json', dict(error=repr(error), completed=len(state['runs'])))
        raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
    print(f'complete {len(steps)} replay lives + {len(state["idle"])} idle processes', flush=True)


if __name__ == '__main__':
    main()
