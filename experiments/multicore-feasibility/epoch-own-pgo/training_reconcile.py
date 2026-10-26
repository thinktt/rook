#!/usr/bin/env python3
"""Independent saved training audit and one fresh byte-identical LLVM remerge.

No engine, compiler, replay or training process is run. Raw evidence and the
canonical profile remain unchanged. The sole process is the fixed profdata
remerge, supervised within the original persisted pipeline ceiling.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, ROOT, SPEC, HELPERS, DEFAULT_CRATE, ACCOUNT, GATE, TAP,
    BUILD_ADAPTER, SERIAL_BUILD, PRACTICAL_BUILD,
    audit, audit_placement, baseline, code_paths, preparation, read, readiness,
    sha, snapshot, write)

MERGE_TOOL = Path('/usr/bin/llvm-profdata-19')
RAW_PROFILE_CAP = 256 * 1024 * 1024
LIMITS = dict(perLifetimeSeconds=180, aggregateSeconds=2400,
    rawProfileBytes=RAW_PROFILE_CAP, nativeRawBytesPerLifetime=8*1024*1024,
    ownedCleanupSeconds=10, canonicalMergeSeconds=60, mergeVersionSeconds=10)


def unchanged(hashes):
    for name, digest in hashes.items():
        assert sha(Path(name)) == digest, name


def audit_tool(base, name, argv, cap, plan, end):
    record = read(base/(name+'.json'))
    assert record['argv'] == argv and record['cwd'] == str(ROOT)
    assert record['exit'] == 0 and record['signal'] is None and record['failure'] is None
    assert record['cleanupFailure'] is None
    assert record['cleanupSignals'] == record['receivedSignals'] == []
    began, ended = record['startedMonotonicNs'], record['endedMonotonicNs']
    assert plan['streamStartMonotonicNs'] <= began < ended <= end
    assert record['elapsedNs'] == ended-began > 0
    assert ended <= record['deadlineMonotonicNs'] <= plan['stageDeadlineMonotonicNs']
    assert record['deadlineMonotonicNs']-began <= cap*10**9
    assert type(record['pid']) is int and record['pid'] > 0
    assert not Path(f'/proc/{record["pid"]}').exists(), 'recorded tool PID currently live; possible reuse'
    for suffix, maximum in [('stdout', 8*1024*1024), ('stderr', 1024*1024)]:
        path = base/(name+'.'+suffix)
        assert path.stat().st_size == record[suffix+'Bytes'] <= maximum
        assert sha(path) == record[suffix+'Sha256']
    return record


def audit_housekeeping(path):
    record = read(path)
    assert record['schema'] == 'rook2-epoch-own-pgo-training-housekeeping-v1'
    assert record['failure'] is None and record['helperCpus'] == sorted(HELPERS)
    assert len(record['applies']) == 162 and record['restored'] is not None
    originals, leaders, seen = {}, {}, {}
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
            if key in seen:
                assert row['before'] == sorted(HELPERS)
            else:
                assert row['before'] == originals[key]
                seen[key] = row['before']
    assert seen == originals
    for row in record['restored']:
        key = (row['pid'], row['tid'], row['starttime'])
        if key in originals:
            assert row['inheritedNewThread'] is False and row['restored'] == originals[key]
        else:
            masks = [mask for (pid, _), mask in leaders.items() if pid == row['pid']]
            assert len(masks) == 1 and row['inheritedNewThread'] is True and row['restored'] == masks[0]
    assert record['postRestoreSelfAffinity'] == sorted(HELPERS)
    return dict(applyCount=162, selectedOriginalTasks=len(originals),
        restoredTasks=len(record['restored']), receiptSha256=sha(path))


def equal_bytes(first, second):
    with first.open('rb') as left, second.open('rb') as right:
        while True:
            a, b = left.read(1024*1024), right.read(1024*1024)
            if a != b:
                return False
            if not a:
                return True


def independent_remerge(base, profiles, deadline_ns, received_signals):
    """Fresh output and equal input weights; canonical is never a merge input."""
    directory = base/'independent-remerge'
    directory.mkdir()
    output = directory/'merged.profdata'
    command = [str(MERGE_TOOL), 'merge', '-o', str(output), *sorted(profiles)]
    began = time.monotonic_ns()
    limit_ns = min(deadline_ns, began+60*10**9)
    assert began < limit_ns, 'independent remerge deadline before launch'
    record = dict(argv=command, cwd=str(ROOT), pid=None, exit=None, signal=None,
        failure=None, cleanupFailure=None, startedMonotonicNs=began, deadlineMonotonicNs=limit_ns,
        cleanupSignals=[], receivedSignals=[])
    child = None
    env = {key: value for key, value in os.environ.items()
           if key != 'LLVM_PROFILE_FILE' and not key.startswith('ROOK2_')}
    try:
        with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
            child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout,
                stderr=stderr, start_new_session=True)
            record['pid'] = child.pid
            while child.poll() is None:
                assert time.monotonic_ns() < limit_ns, 'independent remerge deadline'
                assert (directory/'stdout').stat().st_size <= 8*1024*1024
                assert (directory/'stderr').stat().st_size <= 1024*1024
                time.sleep(.05)
            record['exit'] = child.returncode
            record['signal'] = -child.returncode if child.returncode < 0 else None
            assert child.returncode == 0 and (directory/'stderr').read_bytes() == b''
            assert (directory/'stdout').stat().st_size <= 8*1024*1024
        assert output.is_file() and not output.is_symlink()
        assert 0 < output.stat().st_size <= RAW_PROFILE_CAP
        assert time.monotonic_ns() < limit_ns, 'independent remerge completion deadline'
        record.update(profile=str(output), profileSha256=sha(output), profileBytes=output.stat().st_size)
    except BaseException as error:
        record['failure'] = repr(error)
        if child is not None and child.poll() is None:
            for signum, seconds in [(signal.SIGTERM, 5), (signal.SIGKILL, 5)]:
                try:
                    os.killpg(child.pid, signum)
                    record['cleanupSignals'].append(dict(signal=int(signum), monotonicNs=time.monotonic_ns()))
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=seconds)
                    break
                except subprocess.TimeoutExpired:
                    if signum == signal.SIGKILL:
                        record['cleanupFailure'] = 'tool did not reap within the owned cleanup cap'
                        raise
        if child is not None:
            record['exit'] = child.returncode
            record['signal'] = -child.returncode if child.returncode is not None and child.returncode < 0 else None
        raise
    finally:
        record['endedMonotonicNs'] = time.monotonic_ns()
        record['elapsedNs'] = record['endedMonotonicNs']-began
        record['receivedSignals'] = list(received_signals)
        for suffix in ['stdout', 'stderr']:
            path = directory/suffix
            if path.exists():
                record[suffix+'Sha256'] = sha(path)
                record[suffix+'Bytes'] = path.stat().st_size
        write(directory/'receipt.json', record)
    return record


def audit_training(base, pipeline_deadline_ns, received_signals):
    audit_started = time.monotonic_ns()
    assert audit_started < pipeline_deadline_ns, 'original pipeline deadline before training audit'
    audit_deadline_ns = min(pipeline_deadline_ns, audit_started+120*10**9)
    assert set(os.sched_getaffinity(0)) == HELPERS
    plan, training = read(base/'plan.json'), read(base/'training.json')
    assert plan['schema'] == 'rook2-epoch-own-pgo-training-plan-v1'
    assert training['schema'] == 'rook2-pgo-training-v1' and training['complete'] is True
    assert plan['pipelineSeconds'] == 3600
    assert pipeline_deadline_ns == plan['pipelineDeadlineMonotonicNs'] == training['pipelineDeadlineMonotonicNs']
    pipeline_start = plan['pipelineStartMonotonicNs']
    assert pipeline_deadline_ns == pipeline_start+3600*10**9
    assert training['pipelineStartMonotonicNs'] == pipeline_start
    start, end = training['streamStartMonotonicNs'], training['streamEndMonotonicNs']
    assert pipeline_start <= start == plan['streamStartMonotonicNs'] < end <= audit_started
    assert plan['stageDeadlineMonotonicNs'] == training['stageDeadlineMonotonicNs'] == min(start+2400*10**9, pipeline_deadline_ns)
    assert end < plan['stageDeadlineMonotonicNs']
    assert plan['limits'] == LIMITS
    assert plan['coordinatorCpu'] == 14 and plan['helperCpus'] == [6, 4]
    assert plan['nativePreExecAffinities'] == {'1': [6, 14], '2': [6, 14], '3': [4, 6, 14]}
    assert plan['quietSiblings'] == [5, 7, 15] and plan['helperAffinity'] == sorted(HELPERS)
    prepared_path = Path(plan['sourcePreparation'])
    prepared = preparation(prepared_path)
    assert sha(prepared_path) == plan['sourcePreparationSha256']
    assert prepared['sourceCheckpoint'] == plan['sourceCheckpoint']
    assert prepared['readinessSemantics'] == plan['readinessSemantics']
    hashes = plan['inputs']
    required = code_paths()+[prepared_path, MERGE_TOOL.resolve(), ACCOUNT, GATE, TAP]
    required += [Path(path) for key in ['inputSha256', 'reusedEvidenceSha256'] for path in prepared[key]]
    required += [Path(path) for path in baseline()]
    assert all(str(path.resolve()) in hashes for path in required)
    unchanged(hashes)
    assert plan['protectedArtifacts'] == baseline()
    build_directory = Path(plan['buildDirectory'])
    # Independently parse receipt/source/compiler command instead of importing
    # the training driver or trusting its build admission result.
    build, effective = audit.check_build(build_directory, 'instrumented')
    assert build['mode'] == 'generic' and Path(build['crate']).resolve() == DEFAULT_CRATE
    assert build['helper_sha256'] == sha(ROOT/'tools/build.py')
    assert len(build['source_sha256_before']) == 64
    assert training['effective_rustc_options'] == plan['effectiveRustcOptions'] == effective
    assert training['engine_source_sha256'] == plan['source'] == build['source_sha256_before'] == prepared['candidateSource'] == snapshot(DEFAULT_CRATE)
    assert training['input_sha256'] == hashes
    assert training['target_triple'] == build['target_triple'] == 'x86_64-unknown-linux-gnu'
    assert training['base_rust_flags'] == ['-C', 'target-cpu=x86-64']
    assert training['instrumented_build_receipt'] == dict(path=str(build_directory/'receipt.json'), sha256=sha(build_directory/'receipt.json'))
    assert build['initial_affinity'] == build['build_affinity'] == build['restored_affinity'] == sorted(HELPERS)
    assert build['affinity_adapter'] == dict(path=str(BUILD_ADAPTER), sha256=sha(BUILD_ADAPTER),
        original_tool=str(ROOT/'tools/build.py'), original_tool_sha256=sha(ROOT/'tools/build.py'),
        only_override='HELPERS', original_helpers=[0,1,2,3,4,5,8,9,10,11,12,13], helpers=sorted(HELPERS))
    for name in ['rustc', 'cargo']:
        executable = Path(build['toolchain'][name]['argv'][0]).resolve()
        assert str(executable) in hashes
        assert sha(executable) == build['toolchain'][name+'_executable_sha256'] == hashes[str(executable)]
        for control_directory in [SERIAL_BUILD, PRACTICAL_BUILD]:
            control = read(control_directory/'receipt.json')
            assert control['toolchain'][name] == build['toolchain'][name]
            assert control['toolchain'][name+'_executable_sha256'] == build['toolchain'][name+'_executable_sha256']
    source_copies = [build_directory/'source-before'/name for name in
                     (build['source_sha256_before'] | build['tool_sha256_before'])]
    for path in source_copies+[build_directory/'receipt.json', build_directory/'build.stderr']:
        assert str(path.resolve()) in hashes
    for name, digest in build['tool_sha256_before'].items():
        assert sha(build_directory/'source-before'/name) == digest
    image = Path(plan['image'])
    assert str(image.resolve()) in hashes
    assert training['instrumented_engine_sha256'] == plan['imageSha256'] == sha(image) == build['binary_output']['sha256']
    cases = [row['id'] for row in read(SPEC/'workloads.json')['cases']]
    assert len(cases) == len(set(cases)) == 54
    schedule = [dict(case=case, budget=budget, variant=f'budget{budget}')
                for budget in [1, 2, 3] for case in cases]
    assert plan['schedule'] == schedule
    assert len(training['runs']) == training['original_lifetimes'] == 162
    assert training['modes'] == [dict(budget=budget, originalCases=54) for budget in [1, 2, 3]]
    root = Path(plan['profileRoot'])
    assert root == Path(build['pgo']['profile_directory']).resolve()
    assert root != base and root not in base.parents and base not in root.parents
    profiles, pids, posts, previous_end = {}, set(), 0, start
    for index, (step, row) in enumerate(zip(schedule, training['runs'])):
        assert time.monotonic_ns() < audit_deadline_ns, 'training raw audit deadline'
        name = f'{index:03d}-{step["case"]}-b{step["budget"]}'
        directory, profile_directory = base/name, root/name
        pattern = profile_directory/'native-%p.profraw'
        options = [f'--threads={step["budget"]}']
        native, count = audit.lifetime(directory, row, step, image, step['budget'], options, hashes, pattern)
        assert row['placement'] == audit_placement(directory, native, hashes)
        assert row['orderedPosts'] == count
        assert row['colors'] == dict(path=str(directory/'colors.json'), sha256=sha(directory/'colors.json'),
            report=readiness(directory, row['colors'], step['budget'], True))
        assert previous_end <= row['controllerStartMonotonicNs'] <= native['start_monotonic_ns']
        assert native['reaped_monotonic_ns'] <= row['controllerEndMonotonicNs'] <= end
        assert 0 < native['wall_ns'] <= 180*10**9
        previous_end = row['controllerEndMonotonicNs']
        profile = profile_directory/f'native-{native["native_pid"]}.profraw'
        assert list(profile_directory.iterdir()) == [profile]
        assert profile.is_file() and not profile.is_symlink() and profile.stat().st_size > 0
        assert row['profile'] == str(profile) and row['profileSha256'] == sha(profile)
        profiles[str(profile)] = sha(profile)
        pids.add(native['native_pid']); posts += count
    assert len(profiles) == len(pids) == 162
    assert {str(path) for path in root.rglob('*.profraw')} == set(profiles)
    assert {path.name for path in root.iterdir()} == {
        f'{index:03d}-{step["case"]}-b{step["budget"]}' for index, step in enumerate(schedule)}
    assert sum(Path(path).stat().st_size for path in profiles) <= RAW_PROFILE_CAP
    assert profiles == training['raw_profiles_sha256']
    expected_merge = [str(MERGE_TOOL), 'merge', '-o', str(base/'merged.profdata'), *sorted(profiles)]
    assert training['canonical_merge_count'] == 1 and training['merge_command'] == expected_merge
    version = audit_tool(base, 'merge-tool', [str(MERGE_TOOL), '--version'], 10, plan, end)
    merge = audit_tool(base, 'merge', expected_merge, 60, plan, end)
    assert previous_end <= version['startedMonotonicNs'] < version['endedMonotonicNs'] <= merge['startedMonotonicNs']
    assert (base/'merge-tool.stderr').read_bytes() == (base/'merge.stderr').read_bytes() == b''
    version_text = (base/'merge-tool.stdout').read_text()
    assert version_text == training['merge_tool_version'] and '19.1.7' in version_text
    assert plan['mergeTool'] == str(MERGE_TOOL)
    assert sha(MERGE_TOOL.resolve()) == plan['mergeToolSha256'] == training['merge_tool_sha256']
    assert sha(base/'merge.json') == training['merge_record_sha256']
    canonical = base/'merged.profdata'
    assert canonical.is_file() and not canonical.is_symlink()
    assert 0 < canonical.stat().st_size <= RAW_PROFILE_CAP
    assert sha(canonical) == training['profile_sha256']
    assert sha(base/'plan.json') == training['plan_sha256']
    assert sha(HERE/'train.py') == training['driver_sha256']
    assert training['adaptation'] == plan['adaptation']
    assert training['housekeeping_sha256'] == sha(base/'housekeeping.json')
    housekeeping_result = audit_housekeeping(base/'housekeeping.json')
    progress = read(base/'progress.json')
    assert progress == dict(complete=True, runs=training['runs'], failure=None,
        signals=[], streamEndMonotonicNs=end)
    assert not (base/'failure.json').exists()
    raw_names = ['plan.json', 'training.json', 'merge.json', 'merge-tool.json',
        'merge.stdout', 'merge.stderr', 'merge-tool.stdout', 'merge-tool.stderr',
        'merged.profdata', 'proc-stat-before', 'proc-stat-after', 'housekeeping.json', 'progress.json']
    raw_hashes = {name: sha(base/name) for name in raw_names}
    unchanged(hashes); unchanged(profiles)
    assert time.monotonic_ns() < audit_deadline_ns, 'training audit deadline before actual remerge'
    remerge = independent_remerge(base, profiles, audit_deadline_ns, received_signals)
    remade = Path(remerge['profile'])
    assert remerge['exit'] == 0 and remerge['failure'] is None and remerge['cleanupSignals'] == []
    assert remerge['cleanupFailure'] is None
    assert remerge['startedMonotonicNs'] < remerge['endedMonotonicNs'] <= remerge['deadlineMonotonicNs'] <= audit_deadline_ns
    assert remerge['elapsedNs'] == remerge['endedMonotonicNs']-remerge['startedMonotonicNs'] <= 60*10**9
    assert not received_signals and remerge['receivedSignals'] == []
    assert remerge['profileSha256'] == training['profile_sha256']
    assert remerge['profileBytes'] == canonical.stat().st_size
    assert equal_bytes(canonical, remade), 'independent merge differs byte-for-byte'
    remerge.update(byteIdentical=True, independentAuditMergeCount=1,
        canonicalProfile=str(canonical), canonicalProfileSha256=training['profile_sha256'],
        receipt=str(base/'independent-remerge/receipt.json'),
        receiptSha256=sha(base/'independent-remerge/receipt.json'))
    unchanged(hashes); unchanged(profiles)
    assert all(sha(base/name) == digest for name, digest in raw_hashes.items())
    assert baseline() == plan['protectedArtifacts']
    assert preparation(prepared_path) == prepared and snapshot(DEFAULT_CRATE) == plan['source']
    assert time.monotonic_ns() < audit_deadline_ns, 'original pipeline/audit deadline after remerge and audits'
    return dict(schema='rook2-epoch-own-pgo-training-audit-v1', complete=True,
        nativeProcesses=162, strictReplayLifetimes=162, orderedPosts=posts,
        originalCasesPerMode=54, modes=[1, 2, 3], rawProfiles=162,
        mergeCount=1, canonicalMergeCount=1, independentAuditMergeCount=1,
        profileSha256=training['profile_sha256'], rawDirectory=str(base),
        inputSha256=hashes, reconcilerSha256=sha(Path(__file__).resolve()),
        rawSha256=raw_hashes, housekeeping=housekeeping_result, remerge=remerge,
        pipelineStartMonotonicNs=pipeline_start, pipelineDeadlineMonotonicNs=pipeline_deadline_ns,
        auditStartMonotonicNs=audit_started, auditEndMonotonicNs=time.monotonic_ns(),
        auditDeadlineMonotonicNs=audit_deadline_ns,
        limits='162 PID/profile-bound native lives audited from saved original raw replay, source64/build/image and actual pre-input TID placement; exactly one unweighted canonical merge plus one separately recorded byte-identical independent merge; only canonical profile may feed the use build; no native rerun or compiler')


def main():
    received_signals = []

    def interrupted(signum, _frame):
        received_signals.append(dict(signal=signum, monotonicNs=time.monotonic_ns()))
        raise InterruptedError('external signal '+str(signum))

    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--pipeline-deadline-ns', type=int, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.directory.resolve()
    output = (args.output or base/'reconciled.json').resolve()
    assert not output.exists() and not output.is_symlink(), 'audit output must be fresh'
    failure_path = output.with_suffix(output.suffix+'.failure.json')
    assert not failure_path.exists(), 'preserve an earlier failed audit'
    try:
        result = audit_training(base, args.pipeline_deadline_ns, received_signals)
        with output.open('x') as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write('\n')
    except BaseException as error:
        with failure_path.open('x') as stream:
            json.dump(dict(complete=False, failure=repr(error), signals=received_signals,
                pipelineDeadlineMonotonicNs=args.pipeline_deadline_ns,
                failureMonotonicNs=time.monotonic_ns()), stream, indent=2, allow_nan=False)
            stream.write('\n')
        raise
    print(json.dumps({key: result[key] for key in ['complete', 'nativeProcesses',
        'orderedPosts', 'profileSha256', 'mergeCount', 'independentAuditMergeCount']}))


if __name__ == '__main__':
    main()
