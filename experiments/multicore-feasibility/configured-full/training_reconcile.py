#!/usr/bin/env python3
"""Independent read-only training audit; no native process, compiler or remerge."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from common import HERE, ROOT, USABLE, ORIGINAL, ACCOUNT, SPEC, HELPERS, audit, audit_placement, read, sha


def audit_training(base):
    plan, training = read(base/'plan.json'), read(base/'training.json')
    assert plan['schema'] == 'rook2-configured-full-training-plan-v1'
    assert training['schema'] == 'rook2-pgo-training-v1' and training['complete']
    assert plan['coordinatorCpu'] == 14 and plan['workerCpu'] == 6
    assert plan['nativePreExecAffinity'] == [6, 14] and plan['quietSiblings'] == [7, 15]
    assert plan['helperAffinity'] == sorted(HELPERS)
    assert plan['limits'] == dict(perLifetimeSeconds=180, aggregateSeconds=2400,
        rawProfileBytes=256*1024*1024, nativeRawBytesPerLifetime=8*1024*1024, ownedCleanupSeconds=10)
    hashes = plan['inputs']
    required = [HERE/n for n in ['train.py', 'pipeline.py', 'training_reconcile.py', 'common.py']]
    required += [USABLE/n for n in ['common.py', 'collect.py', 'reconcile.py', 'account_threads.py',
                                   'placement_gate.mjs', 'tools/tap_wire.mjs']]
    required += [ORIGINAL/n for n in ['train.py', 'reconcile.py']]
    required += [ROOT/'tools/build.py', ROOT/'tools/tap_wire.mjs', ROOT/'tools/compare_ordinary.py',
                 SPEC/'workloads.json', SPEC/'replay-oracle.json', SPEC/'replay-check.mjs', SPEC/'benchmark.mjs']
    assert all(str(path.resolve()) in hashes for path in required)
    assert all(sha(Path(path)) == digest for path, digest in hashes.items())
    build_directory = Path(plan['buildDirectory'])
    build, effective = audit.check_build(build_directory, 'instrumented')
    assert training['effective_rustc_options'] == plan['effectiveRustcOptions'] == effective
    assert training['engine_source_sha256'] == plan['source'] == build['source_sha256_before']
    assert training['input_sha256'] == hashes
    assert training['target_triple'] == build['target_triple']
    assert training['base_rust_flags'] == ['-C', 'target-cpu=x86-64']
    assert training['instrumented_build_receipt'] == dict(path=str(build_directory/'receipt.json'), sha256=sha(build_directory/'receipt.json'))
    image = Path(plan['image'])
    assert training['instrumented_engine_sha256'] == plan['imageSha256'] == sha(image)
    cases = [row['id'] for row in read(SPEC/'workloads.json')['cases']]
    assert len(cases) == len(set(cases)) == 54
    schedule = [dict(case=case, budget=budget, variant=f'budget{budget}') for budget in [1, 2] for case in cases]
    assert plan['schedule'] == schedule and len(training['runs']) == training['original_lifetimes'] == 108
    assert training['modes'] == [dict(budget=budget, originalCases=54) for budget in [1, 2]]
    start, end = training['streamStartMonotonicNs'], training['streamEndMonotonicNs']
    assert plan['streamStartMonotonicNs'] == start and 0 < end-start <= 2400*10**9
    root = Path(plan['profileRoot'])
    profiles, pids, posts, previous_end = {}, set(), 0, start
    for index, (step, row) in enumerate(zip(schedule, training['runs'])):
        name = f'{index:03d}-{step["case"]}-b{step["budget"]}'
        directory, profile_directory = base/name, root/name
        native, count = audit.lifetime(directory, row, step, image, step['budget'],
            [f'--threads={step["budget"]}'], hashes, profile_directory/'native-%p.profraw')
        assert row['placement'] == audit_placement(directory, native, hashes)
        assert previous_end <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= end
        assert native['wall_ns'] <= 180*10**9
        previous_end = row['controllerEndMonotonicNs']
        profile = profile_directory/f'native-{native["native_pid"]}.profraw'
        assert list(profile_directory.iterdir()) == [profile] and profile.stat().st_size > 0
        assert row['profile'] == str(profile) and row['profileSha256'] == sha(profile)
        profiles[str(profile)] = sha(profile)
        pids.add(native['native_pid']); posts += count
    assert len(profiles) == len(pids) == 108
    assert {str(path) for path in root.rglob('*.profraw')} == set(profiles)
    assert {path.name for path in root.iterdir()} == {f'{i:03d}-{s["case"]}-b{s["budget"]}' for i, s in enumerate(schedule)}
    assert sum(Path(path).stat().st_size for path in profiles) <= plan['limits']['rawProfileBytes']
    assert profiles == training['raw_profiles_sha256']
    merge, version = read(base/'merge.json'), read(base/'merge-tool.json')
    expected_merge = ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(base/'merged.profdata'), *sorted(profiles)]
    assert merge['argv'] == expected_merge == training['merge_command']
    assert merge['exit'] == 0 and merge['elapsedNs'] > 0 and (base/'merge.stderr').read_bytes() == b''
    assert sha(base/'merge.json') == training['merge_record_sha256']
    assert version['argv'] == ['/usr/bin/llvm-profdata-19', '--version'] and version['exit'] == 0
    assert version['stdout'] == training['merge_tool_version'] and '19.1.7' in version['stdout']
    assert version['sha256'] == plan['mergeToolSha256'] == training['merge_tool_sha256']
    assert sha(Path(plan['mergeTool']).resolve()) == plan['mergeToolSha256']
    assert sha(base/'merged.profdata') == training['profile_sha256'] and (base/'merged.profdata').stat().st_size > 0
    assert training['plan_sha256'] == sha(base/'plan.json')
    assert training['driver_sha256'] == sha(HERE/'train.py')
    assert training['adaptation'] == plan['adaptation']
    return dict(schema='rook2-configured-full-training-audit-v1', complete=True,
        nativeProcesses=108, strictReplayLifetimes=108, orderedPosts=posts,
        originalCasesPerMode=54, rawProfiles=108, mergeCount=1,
        profileSha256=training['profile_sha256'], rawDirectory=str(base),
        inputSha256=hashes, reconcilerSha256=sha(Path(__file__).resolve()),
        rawSha256={name: sha(base/name) for name in ['plan.json', 'training.json', 'merge.json',
            'merge-tool.json', 'merged.profdata', 'proc-stat-before', 'proc-stat-after']},
        limits='Recorded single merge and all raw hashes audited; LLVM is not independently rerun. Native wait4/ready/input-gate/original streams audited through frozen independent readers; captured stdin excludes end(data) cleanup. Instrumented costs are not production performance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.directory.resolve()
    result = audit_training(base)
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({key: result[key] for key in ['complete', 'nativeProcesses', 'orderedPosts', 'profileSha256', 'mergeCount']}))


if __name__ == '__main__':
    main()
