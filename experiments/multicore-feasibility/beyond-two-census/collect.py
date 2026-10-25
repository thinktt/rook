#!/usr/bin/env python3
"""Exactly three count-only original replay lives; no repeats or speed claims."""
import argparse
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, FEATURE, admit, baseline, load_usable, read, write, sha

CASES = ['profile-35', 'profile-08', 'profile-43']
ENV = 'ROOK2_BRANCH_WORK_CENSUS_REPORT'
MAX_REPORT = 4*1024*1024


def dependencies(build, receipt):
    usable = HERE.parent/'usable-full'; original = HERE.parent/'full-split-production'
    paths = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']]
    paths += [usable/n for n in ['common.py', 'account_threads.py', 'placement_gate.mjs', 'tools/tap_wire.mjs']]
    paths += [original/n for n in ['train.py', 'reconcile.py']]
    paths += [ROOT/'tools/tap_wire.mjs', ROOT/'tools/compare_ordinary.py',
              build/'receipt.json', build/'stdout', build/'stderr', Path(receipt['binary'])]
    spec = Path('/home/legolas/king-spec/conformance/profiling')
    paths += [spec/n for n in ['replay-check.mjs', 'benchmark.mjs', 'workloads.json', 'replay-oracle.json']]
    paths += [Path(p) for p in receipt['toolsBefore']]
    paths += [Path(p) for p in receipt['baselineBefore']['protectedArtifacts']]
    paths.append(Path(receipt['baselineBefore']['receipt']['path']))
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); build, out = args.build.resolve(), args.output.resolve()
    receipt = admit(build); usable = load_usable(); image = Path(receipt['binary'])
    assert sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    assert ENV not in os.environ, 'census report path must be explicitly scoped by this collector'
    out.mkdir()
    steps = [dict(case=case, variant='count-census', warmup=False, repeat=1) for case in CASES]
    plan = dict(schema='rook2-beyond-two-count-plan-v1', build=str(build), crate=receipt['crate'],
                binary=str(image), binarySha256=sha(image), feature=FEATURE, schedule=steps,
                budget=2, options=['--threads=2'], coordinatorCpu=14, workerCpu=6,
                nativePreExecAffinity=[6, 14], helperAffinity=sorted(HELPERS), quietSiblings=[7, 15],
                reportEnvironment=ENV, reportSchema='rook2-branch-work-census-v1',
                baseline=receipt['baselineBefore'], sourcePins=receipt['sourceBefore'],
                inputSha256={str(path): sha(path) for path in dependencies(build, receipt)},
                limits=dict(perLifeSeconds=180, totalSeconds=900, censusBytesPerCase=MAX_REPORT),
                scope='one original35/08/43 each; no warmups/repeats/per-node timers/trace; all CPU/RSS/wall are instrumented reported-only costs, not speed evidence')
    write(out/'plan.json', plan)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    state = dict(complete=False, failure=None, runs=[], streamStartMonotonicNs=time.monotonic_ns())
    deadline = time.monotonic()+900
    try:
        for i, step in enumerate(steps):
            assert time.monotonic() < deadline
            directory = out/f'{i:02d}-{step["case"]}'
            report_path = directory/'census.json'
            assert not report_path.exists()
            os.environ[ENV] = str(report_path)
            try:
                row = usable.run_lifetime(directory, step, image, 2, ['--threads=2'], deadline, plan['inputSha256'])
            finally:
                os.environ.pop(ENV, None)
            assert 0 < report_path.stat().st_size <= MAX_REPORT
            census = read(report_path)
            assert census['schema'] == plan['reportSchema'] and census['processId'] == row['nativePid']
            assert census['overflow'] is False and census['accountingFailures'] == 0
            row['censusReport'] = dict(path=str(report_path), bytes=report_path.stat().st_size,
                                       sha256=sha(report_path), environment={ENV: str(report_path)})
            state['runs'].append(row); write(out/'progress.json', state)
            print('completed '+step['case'], flush=True)
        assert all(sha(Path(path)) == digest for path, digest in plan['inputSha256'].items())
        assert baseline() == plan['baseline']; admit(build)
        assert time.monotonic() < deadline
        state.update(complete=True, streamEndMonotonicNs=time.monotonic_ns(),
                     interpretation='Count-only opportunity/dependency discriminator; inclusive populations overlap; no measured speedup or qualification')
        write(out/'result.json', state)
    except BaseException as error:
        state['failure'] = repr(error); write(out/'result.json', state)
        write(out/'failure.json', dict(failure=repr(error), completed=len(state['runs'])))
        raise
    finally:
        os.environ.pop(ENV, None)
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())


if __name__ == '__main__':
    main()
