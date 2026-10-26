#!/usr/bin/env python3
"""Original54 in four Q owner-local tactical modes; one canonical PGO merge.

Importing starts no process. The shared frozen native supervisor and input gate
verify actual TIDs on14/6/4 before protocol input. Training is instrumentation
work, never a production performance observation.
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
from common import (ROOT, HELPERS, SPEC, DEFAULT_CRATE,
    admit_build, baseline, code_paths, housekeeping, preparation, read, run_lifetime,
    sha, snapshot, write, TRAINING_MODES, SOURCE_CHECKPOINT)

MERGE_TOOL = Path('/usr/bin/llvm-profdata-19')
PIPELINE_SECONDS = 3600
TRAIN_SECONDS = 2400
RAW_PROFILE_CAP = 256 * 1024 * 1024
LIMITS = dict(perLifetimeSeconds=180, aggregateSeconds=TRAIN_SECONDS,
    rawProfileBytes=RAW_PROFILE_CAP, nativeRawBytesPerLifetime=8*1024*1024,
    ownedCleanupSeconds=10, canonicalMergeSeconds=60, mergeVersionSeconds=10)


def input_paths(build_directory, build, image, prepared_path, prepared):
    paths = code_paths()+[prepared_path, image, build_directory/'receipt.json',
        build_directory/'build.stderr', MERGE_TOOL.resolve()]
    paths += [Path(path) for path in prepared['inputSha256']]
    paths += [Path(path) for path in prepared['reusedEvidenceSha256']]
    paths += [Path(path) for path in baseline()]
    paths += [build_directory/'source-before'/name for name in
              (build['source_sha256_before'] | build['tool_sha256_before'])]
    for tool in ['rustc', 'cargo']:
        paths.append(Path(build['toolchain'][tool]['argv'][0]).resolve())
    return sorted(set(path.resolve() for path in paths))


def terminate_tool(child, events):
    """Only this newly created tool session; preserve attempted group signals."""
    if child.poll() is None:
        for signum, seconds in [(signal.SIGTERM, 5), (signal.SIGKILL, 5)]:
            try:
                os.killpg(child.pid, signum)
                events.append(dict(signal=int(signum), monotonicNs=time.monotonic_ns()))
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=seconds)
                break
            except subprocess.TimeoutExpired:
                if signum == signal.SIGKILL:
                    raise


def tool(directory, name, argv, deadline_ns, cap, received_signals):
    """Finite owned-session tool invocation, including interrupted receipts."""
    started = time.monotonic_ns()
    limit_ns = min(deadline_ns, started+cap*10**9)
    assert time.monotonic_ns() < limit_ns, 'training tool deadline before launch'
    record = dict(argv=argv, cwd=str(ROOT), startedMonotonicNs=started,
        deadlineMonotonicNs=limit_ns, pid=None, exit=None, signal=None,
        failure=None, cleanupFailure=None, cleanupSignals=[], receivedSignals=[])
    child = None
    env = {key: value for key, value in os.environ.items()
           if key != 'LLVM_PROFILE_FILE' and not key.startswith('ROOK2_')}
    try:
        with (directory/(name+'.stdout')).open('xb') as stdout, (directory/(name+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stdout,
                stderr=stderr, start_new_session=True)
            record['pid'] = child.pid
            while child.poll() is None:
                assert time.monotonic_ns() < limit_ns, 'training tool deadline'
                assert (directory/(name+'.stdout')).stat().st_size <= 8*1024*1024
                assert (directory/(name+'.stderr')).stat().st_size <= 1024*1024
                time.sleep(.05)
            record['exit'] = child.returncode
            record['signal'] = -child.returncode if child.returncode < 0 else None
            assert child.returncode == 0, (name, child.returncode)
            assert (directory/(name+'.stdout')).stat().st_size <= 8*1024*1024
            assert (directory/(name+'.stderr')).stat().st_size <= 1024*1024
            assert time.monotonic_ns() < limit_ns, 'training tool completion deadline'
    except BaseException as error:
        record['failure'] = repr(error)
        if child is not None:
            # Native lives use common.stop_owned; these LLVM tools own only
            # their explicitly created session and no native engine subgroup.
            try:
                terminate_tool(child, record['cleanupSignals'])
            except BaseException as cleanup_error:
                record['cleanupFailure'] = repr(cleanup_error)
                raise
            record['exit'] = child.returncode
            record['signal'] = -child.returncode if child.returncode is not None and child.returncode < 0 else None
        raise
    finally:
        record['endedMonotonicNs'] = time.monotonic_ns()
        record['elapsedNs'] = record['endedMonotonicNs']-started
        record['receivedSignals'] = list(received_signals)
        for suffix in ['stdout', 'stderr']:
            path = directory/(name+'.'+suffix)
            if path.exists():
                record[suffix+'Sha256'] = sha(path)
                record[suffix+'Bytes'] = path.stat().st_size
        write(directory/(name+'.json'), record)
    return record


def main():
    received_signals = []

    def interrupted(signum, _frame):
        received_signals.append(dict(signal=signum, monotonicNs=time.monotonic_ns()))
        raise InterruptedError('external signal '+str(signum))

    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['build', 'engine', 'preparation', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--pipeline-start-ns', type=int, required=True)
    parser.add_argument('--pipeline-deadline-ns', type=int, required=True)
    args = parser.parse_args()
    assert TRAINING_MODES == [
        dict(variant='inline1', budget=1, options=['--threads=1', '--owner-local-inventory', '--q-owner-local-inventory']),
        dict(variant='current2', budget=2, options=['--threads=2', '--owner-local-inventory', '--q-owner-local-inventory']),
        dict(variant='q-off3', budget=3, options=['--threads=3', '--owner-local-inventory']),
        dict(variant='q-on3', budget=3, options=['--threads=3', '--owner-local-inventory', '--q-owner-local-inventory']),
    ]
    start = time.monotonic_ns()
    assert 0 < args.pipeline_start_ns <= start < args.pipeline_deadline_ns
    assert args.pipeline_deadline_ns == args.pipeline_start_ns+PIPELINE_SECONDS*10**9
    stage_deadline_ns = min(start+TRAIN_SECONDS*10**9, args.pipeline_deadline_ns)
    deadline = stage_deadline_ns/1e9
    assert set(os.sched_getaffinity(0)) == HELPERS
    prepared_path = args.preparation.resolve()
    prepared = preparation(prepared_path)
    assert prepared['sourceCheckpoint'] == SOURCE_CHECKPOINT == '61f827b3790f5cbcbe9fc7885de0c300f060aaa8'
    build_directory, image = args.build.resolve(), args.engine.resolve()
    build, effective = admit_build(build_directory, image, 'instrumented', prepared)
    for name in ['rustc', 'cargo']:
        executable = Path(build['toolchain'][name]['argv'][0]).resolve()
        assert sha(executable) == build['toolchain'][name+'_executable_sha256']
    assert len(build['source_sha256_before']) == 68
    assert build['source_sha256_before'] == prepared['candidateSource'] == snapshot(DEFAULT_CRATE)
    profile_root = Path(build['pgo']['profile_directory']).resolve()
    assert profile_root.is_dir() and not list(profile_root.iterdir()), 'profile root must be fresh and empty'
    out = args.output.resolve()
    assert out != profile_root and profile_root not in out.parents and out not in profile_root.parents
    out.mkdir()
    cases = [row['id'] for row in read(SPEC/'workloads.json')['cases']]
    assert len(cases) == len(set(cases)) == 54
    schedule = [dict(case=case, variant=mode['variant'], budget=mode['budget'],
                     options=list(mode['options']))
                for mode in TRAINING_MODES for case in cases]
    assert len(schedule) == len({(step['variant'], step['case']) for step in schedule}) == 216
    plan = dict(schema='rook2-q-owner-local-own-pgo-training-plan-v1', schedule=schedule, trainingModes=TRAINING_MODES,
        buildDirectory=str(build_directory), image=str(image), imageSha256=sha(image),
        profileRoot=str(profile_root), source=build['source_sha256_before'],
        effectiveRustcOptions=effective, sourcePreparation=str(prepared_path),
        sourcePreparationSha256=sha(prepared_path), sourceCheckpoint=prepared['sourceCheckpoint'],
        inputs={str(path): sha(path) for path in input_paths(build_directory, build, image, prepared_path, prepared)},
        protectedArtifacts=baseline(), coordinatorCpu=14, helperCpus=[6, 4],
        nativePreExecAffinities={'1': [6, 14], '2': [6, 14], '3': [4, 6, 14]},
        helperAffinity=sorted(HELPERS), quietSiblings=[5, 7, 15], limits=LIMITS,
        mergeTool=str(MERGE_TOOL), mergeToolSha256=sha(MERGE_TOOL.resolve()),
        streamStartMonotonicNs=start, stageDeadlineMonotonicNs=stage_deadline_ns,
        pipelineStartMonotonicNs=args.pipeline_start_ns,
        pipelineDeadlineMonotonicNs=args.pipeline_deadline_ns, pipelineSeconds=PIPELINE_SECONDS,
        readinessSemantics=prepared['readinessSemantics'],
        adaptation='One unchanged Q owner-local tactical source68 instrumented image; original54 once each in inline1/current2/q-off3/q-on3 mode-major order with exact recorded options (both requested hooks dormant in budgets1/2); actual external14/6/4 placement gated before input; equal raw-profile merge weights; one canonical merge; no retry, weighting variant or profile reuse',
        performance='Instrumented training only, never production performance')
    write(out/'plan.json', plan)
    rows, raw_hashes = [], {}
    progress = dict(complete=False, runs=rows, failure=None, signals=received_signals)
    write(out/'progress.json', progress)
    placement = housekeeping.Placement()
    housekeeping_record = dict(schema='rook2-q-owner-local-own-pgo-training-housekeeping-v1',
        helperCpus=sorted(HELPERS), applies=[], originals=[], leaders=[], restored=None, failure=None)
    original_affinity = set(os.sched_getaffinity(0))
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())

    def place():
        housekeeping_record['applies'].append(placement.apply(HELPERS))
        housekeeping_record['originals'] = [dict(pid=p, tid=t, starttime=s, affinity=mask)
            for (p, t, s), mask in sorted(placement.original.items())]
        housekeeping_record['leaders'] = [dict(pid=p, starttime=s, affinity=mask)
            for (p, s), mask in sorted(placement.leaders.items())]
        write(out/'housekeeping.json', housekeeping_record)

    try:
        try:
            for index, step in enumerate(schedule):
                assert time.monotonic() < deadline, 'persisted training stage/pipeline deadline'
                place()
                name = f'{index:03d}-{step["case"]}-b{step["budget"]}'
                profile_directory = profile_root/name
                profile_directory.mkdir()
                pattern = profile_directory/'native-%p.profraw'
                variant = dict(budget=step['budget'], options=list(step['options']), report=True)
                row = run_lifetime(out/name, step, image, variant, deadline, plan['inputs'], pattern)
                assert row['requestedThreads'] == row['configuredThreads'] == step['budget']
                assert row['nativeOptions'] == step['options']
                profile = profile_directory/f'native-{row["nativePid"]}.profraw'
                assert list(profile_directory.iterdir()) == [profile]
                assert profile.is_file() and not profile.is_symlink() and profile.stat().st_size > 0
                raw_hashes[str(profile)] = sha(profile)
                assert sum(Path(path).stat().st_size for path in raw_hashes) <= RAW_PROFILE_CAP
                row.update(profile=str(profile), profileSha256=raw_hashes[str(profile)])
                rows.append(row)
                write(out/'progress.json', progress)
            assert len(rows) == len(raw_hashes) == len({row['nativePid'] for row in rows}) == 216
            assert {str(path) for path in profile_root.rglob('*.profraw')} == set(raw_hashes)
            assert {path.name for path in profile_root.iterdir()} == {
                f'{i:03d}-{step["case"]}-b{step["budget"]}' for i, step in enumerate(schedule)}
            assert all(sha(Path(path)) == digest for path, digest in plan['inputs'].items())
            assert snapshot(DEFAULT_CRATE) == plan['source']
            version_record = tool(out, 'merge-tool', [str(MERGE_TOOL), '--version'], stage_deadline_ns, 10, received_signals)
            version = (out/'merge-tool.stdout').read_text()
            assert '19.1.7' in version and (out/'merge-tool.stderr').read_bytes() == b''
            assert version_record['exit'] == 0 and version_record['failure'] is None
            merge = [str(MERGE_TOOL), 'merge', '-o', str(out/'merged.profdata'), *sorted(raw_hashes)]
            merge_record = tool(out, 'merge', merge, stage_deadline_ns, 60, received_signals)
            assert merge_record['exit'] == 0 and (out/'merge.stderr').read_bytes() == b''
            assert (out/'merged.profdata').is_file() and 0 < (out/'merged.profdata').stat().st_size <= RAW_PROFILE_CAP
            assert all(sha(Path(path)) == digest for path, digest in raw_hashes.items())
            training = dict(schema='rook2-pgo-training-v1', complete=False,
                engine_source_sha256=plan['source'], target_triple=build['target_triple'],
                base_rust_flags=['-C', 'target-cpu=x86-64'], effective_rustc_options=effective,
                instrumented_build_receipt=dict(path=str(build_directory/'receipt.json'), sha256=sha(build_directory/'receipt.json')),
                instrumented_engine_sha256=sha(image), input_sha256=plan['inputs'],
                raw_profiles_sha256=raw_hashes, merge_command=merge,
                merge_tool_sha256=plan['mergeToolSha256'], merge_tool_version=version,
                profile_sha256=sha(out/'merged.profdata'), driver_sha256=sha(Path(__file__).resolve()),
                modes=[dict(**mode, originalCases=54) for mode in TRAINING_MODES],
                original_lifetimes=216, canonical_merge_count=1, runs=rows, adaptation=plan['adaptation'],
                plan_sha256=sha(out/'plan.json'), merge_record_sha256=sha(out/'merge.json'),
                pipelineStartMonotonicNs=args.pipeline_start_ns,
                pipelineDeadlineMonotonicNs=args.pipeline_deadline_ns,
                stageDeadlineMonotonicNs=stage_deadline_ns, streamStartMonotonicNs=start,
                performance='Training only; original strict replay, actual externally gated TIDs and joined native exit precede admission of the sole PID-bound profile file; no production timing interpretation')
        finally:
            try:
                housekeeping_record['restored'] = placement.restore()
                os.sched_setaffinity(0, original_affinity)
                housekeeping_record['postRestoreSelfAffinity'] = sorted(os.sched_getaffinity(0))
            except BaseException as error:
                housekeeping_record['failure'] = repr(error)
                raise
            finally:
                write(out/'housekeeping.json', housekeeping_record)
                (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
        assert not received_signals
        assert baseline() == plan['protectedArtifacts']
        assert preparation(prepared_path) == prepared and sha(prepared_path) == plan['sourcePreparationSha256']
        assert all(sha(Path(path)) == digest for path, digest in plan['inputs'].items())
        assert all(sha(Path(path)) == digest for path, digest in raw_hashes.items())
        assert snapshot(DEFAULT_CRATE) == plan['source']
        assert time.monotonic_ns() < stage_deadline_ns, 'persisted deadline after training cleanup/audits'
        training.update(complete=True, streamEndMonotonicNs=time.monotonic_ns(),
            housekeeping_sha256=sha(out/'housekeeping.json'))
        write(out/'training.json', training)
        progress.update(complete=True, streamEndMonotonicNs=training['streamEndMonotonicNs'])
        write(out/'progress.json', progress)
    except BaseException as error:
        progress.update(complete=False, failure=repr(error))
        write(out/'progress.json', progress)
        write(out/'failure.json', dict(complete=False, failure=repr(error), completedLifetimes=len(rows),
            signals=received_signals, pipelineDeadlineMonotonicNs=args.pipeline_deadline_ns,
            failureMonotonicNs=time.monotonic_ns()))
        raise
    print(json.dumps(dict(complete=True, lifetimes=216,
        profile_sha256=training['profile_sha256'], profile=str(out/'merged.profdata'),
        training=str(out/'training.json'), canonicalMergeCount=1)))


if __name__ == '__main__':
    main()
