#!/usr/bin/env python3
"""Fresh original54 training once per configured FULL mode, followed by one merge.

Importing launches no process. The existing frozen external-placement supervisor
and input gate place/verify native TIDs before any original protocol input.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, ROOT, USABLE, ORIGINAL, ACCOUNT, SPEC, HELPERS,
                    train, native_receipt, audit_placement, read, write, sha)

MERGE_TOOL = Path('/usr/bin/llvm-profdata-19')
RAW_PROFILE_CAP = 256 * 1024 * 1024


def input_paths(build, image):
    paths = list(HERE.glob('*.py'))
    paths += [USABLE/n for n in ['common.py', 'collect.py', 'reconcile.py',
                                  'account_threads.py', 'placement_gate.mjs', 'tools/tap_wire.mjs']]
    paths += [ORIGINAL/n for n in ['train.py', 'collect.py', 'reconcile.py']]
    paths += [HERE.parent/'reversed-full/collect.py', ROOT/'tools/tap_wire.mjs',
              ROOT/'tools/compare_ordinary.py', ROOT/'tools/build.py',
              SPEC/'workloads.json', SPEC/'replay-oracle.json', SPEC/'replay-check.mjs',
              SPEC/'benchmark.mjs', build/'receipt.json', build/'build.stderr', image,
              MERGE_TOOL.resolve()]
    receipt = read(build/'receipt.json')
    paths += [build/'source-before'/name for name in receipt['source_sha256_before']]
    for tool in ['rustc', 'cargo']:
        paths.append(Path(receipt['toolchain'][tool]['argv'][0]).resolve())
    return sorted(set(path.resolve() for path in paths))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build_directory = args.build.resolve()
    build, image, effective = train.admit_build(build_directory, 'instrumented')
    profile_root = Path(build['pgo']['profile_directory']).resolve()
    assert profile_root.is_dir() and not list(profile_root.iterdir()), 'profile root must be fresh and empty'
    out = args.output.resolve()
    assert out != profile_root and profile_root not in out.parents
    out.mkdir()
    cases = [row['id'] for row in read(SPEC/'workloads.json')['cases']]
    assert len(cases) == len(set(cases)) == 54
    schedule = [dict(case=case, budget=budget, variant=f'budget{budget}')
                for budget in [1, 2] for case in cases]
    start = time.monotonic_ns()
    plan = dict(schema='rook2-configured-full-training-plan-v1', schedule=schedule,
        buildDirectory=str(build_directory), image=str(image), imageSha256=sha(image),
        profileRoot=str(profile_root), source=build['source_sha256_before'],
        effectiveRustcOptions=effective, inputs={str(path): sha(path) for path in input_paths(build_directory, image)},
        coordinatorCpu=14, workerCpu=6, nativePreExecAffinity=[6, 14],
        helperAffinity=sorted(HELPERS), quietSiblings=[7, 15],
        limits=dict(perLifetimeSeconds=180, aggregateSeconds=2400,
                    rawProfileBytes=RAW_PROFILE_CAP, nativeRawBytesPerLifetime=8*1024*1024,
                    ownedCleanupSeconds=10),
        mergeTool=str(MERGE_TOOL), mergeToolSha256=sha(MERGE_TOOL.resolve()),
        streamStartMonotonicNs=start,
        adaptation='One instrumented own-source image; original54 once with --threads=1 and once with --threads=2; external allowed6/14 before configuration, TIDs pinned/verified before first input; equal raw-profile merge weights; one merge, no retry',
        performance='Instrumented training only, never production performance')
    write(out/'plan.json', plan)
    original_affinity = os.sched_getaffinity(0)
    assert HELPERS <= original_affinity
    os.sched_setaffinity(0, HELPERS)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    rows, raw_hashes = [], {}
    deadline = time.monotonic()+2400
    try:
        for index, step in enumerate(schedule):
            assert time.monotonic() < deadline, 'aggregate training deadline'
            name = f'{index:03d}-{step["case"]}-b{step["budget"]}'
            profile_directory = profile_root/name
            profile_directory.mkdir()
            pattern = profile_directory/'native-%p.profraw'
            directory = out/name
            options = [f'--threads={step["budget"]}']
            began = time.monotonic_ns()
            row = train.run_lifetime(directory, step, image, step['budget'], options, deadline, pattern)
            native = native_receipt(directory/'native.json', image, step['budget'],
                [*options, *read(SPEC/'replay-oracle.json')['mode']], plan['inputs'])
            row['placement'] = audit_placement(directory, native, plan['inputs'])
            row['controllerStartMonotonicNs'] = began
            row['controllerEndMonotonicNs'] = time.monotonic_ns()
            profile = profile_directory/f'native-{row["nativePid"]}.profraw'
            assert list(profile_directory.iterdir()) == [profile] and profile.stat().st_size > 0
            raw_hashes[str(profile)] = sha(profile)
            assert sum(Path(path).stat().st_size for path in raw_hashes) <= RAW_PROFILE_CAP
            row.update(profile=str(profile), profileSha256=sha(profile))
            rows.append(row)
            write(out/'progress.json', dict(complete=False, runs=rows))
        assert len(rows) == len(raw_hashes) == len({row['nativePid'] for row in rows}) == 108
        assert {str(path) for path in profile_root.rglob('*.profraw')} == set(raw_hashes)
        assert all(sha(Path(path)) == digest for path, digest in plan['inputs'].items())
        assert train.source_snapshot(Path(build['crate'])) == plan['source']
        assert time.monotonic() < deadline, 'aggregate training deadline before merge'
        version = subprocess.run([str(MERGE_TOOL), '--version'], capture_output=True,
            text=True, check=True, timeout=max(.01, min(10, deadline-time.monotonic())))
        assert '19.1.7' in version.stdout
        write(out/'merge-tool.json', dict(argv=[str(MERGE_TOOL), '--version'], exit=version.returncode,
            stdout=version.stdout, stderr=version.stderr, sha256=plan['mergeToolSha256']))
        merge = [str(MERGE_TOOL), 'merge', '-o', str(out/'merged.profdata'), *sorted(raw_hashes)]
        merge_start = time.monotonic_ns()
        with (out/'merge.stdout').open('xb') as stdout, (out/'merge.stderr').open('xb') as stderr:
            child = subprocess.Popen(merge, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=max(.01, min(60, deadline-time.monotonic())))
            except BaseException:
                child.kill(); child.wait(); raise
        write(out/'merge.json', dict(argv=merge, pid=child.pid, exit=code,
            elapsedNs=time.monotonic_ns()-merge_start))
        assert code == 0 and (out/'merge.stderr').stat().st_size == 0
        assert all(sha(Path(path)) == digest for path, digest in raw_hashes.items())
        assert all(sha(Path(path)) == digest for path, digest in plan['inputs'].items())
        assert train.source_snapshot(Path(build['crate'])) == plan['source']
        assert time.monotonic() < deadline, 'aggregate training deadline after merge'
        training = dict(schema='rook2-pgo-training-v1', complete=True,
            engine_source_sha256=plan['source'], target_triple=build['target_triple'],
            base_rust_flags=['-C', 'target-cpu=x86-64'], effective_rustc_options=effective,
            instrumented_build_receipt=dict(path=str(build_directory/'receipt.json'), sha256=sha(build_directory/'receipt.json')),
            instrumented_engine_sha256=sha(image), input_sha256=plan['inputs'],
            raw_profiles_sha256=raw_hashes, merge_command=merge,
            merge_tool_sha256=plan['mergeToolSha256'], merge_tool_version=version.stdout,
            profile_sha256=sha(out/'merged.profdata'), driver_sha256=sha(Path(__file__).resolve()),
            modes=[dict(budget=budget, originalCases=54) for budget in [1, 2]],
            original_lifetimes=108, runs=rows, adaptation=plan['adaptation'],
            plan_sha256=sha(out/'plan.json'), merge_record_sha256=sha(out/'merge.json'),
            streamStartMonotonicNs=start, streamEndMonotonicNs=time.monotonic_ns(),
            performance='Training only; original strict replay, externally gated placement and joined native exit precede PID-bound profile admission; no production timing interpretation')
        write(out/'training.json', training)
    except BaseException as error:
        write(out/'failure.json', dict(complete=False, failure=repr(error), completedLifetimes=len(rows)))
        raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
        os.sched_setaffinity(0, original_affinity)
    print(__import__('json').dumps(dict(complete=True, lifetimes=108,
        profile_sha256=training['profile_sha256'], profile=str(out/'merged.profdata'),
        training=str(out/'training.json'))))


if __name__ == '__main__':
    main()
