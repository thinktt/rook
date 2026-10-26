#!/usr/bin/env python3
"""Frozen48 original replay lives and4 idle probes; no retries or extensions."""
import argparse
import hashlib
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, ACCOUNT, TAP, CONTROL_BUILD, CONTROL_IMAGE, SPEC, HELPERS, CASES, NAMES, METRICS, LIMITS, EVIDENCE_REUSE,
    admission, audit, audit_placement, baseline, code_paths, colors_report, dist,
    housekeeping, image_layout, native_receipt, preparation, prepared_run, read, schedule, sha, stop_owned,
    supervisor, variants, write)


def environment(directory, report):
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('ROOK2_') or key == 'LLVM_PROFILE_FILE':
            env.pop(key, None)
    if report:
        env['ROOK2_COLORS_REPORT'] = str(directory/'colors.json')
    return env


def ready_record(directory, supervisor_pid, image, budget, deadline):
    from common import check_task_masks
    path = directory/'native.json.ready'
    while not path.exists():
        assert time.monotonic() < deadline, 'external placement ready deadline'
        time.sleep(.001)
    ready = read(path)
    assert ready['schema'] == 'rook2-external-placement-ready-v1'
    assert ready['supervisor_pid'] == supervisor_pid and ready['engine'] == str(image)
    assert ready['engine_sha256'] == sha(image) and ready['launcher_sha256'] == sha(ACCOUNT)
    assert ready['expected_threads'] == budget
    check_task_masks(ready['native_post_exec']['task_affinities'], ready['native_pid'], budget)
    return ready


def run_lifetime(directory, step, image, variant, deadline, hashes):
    directory.mkdir()
    started = time.monotonic_ns()
    budget, options = variant['budget'], variant['options']
    native = supervisor(image, budget, directory, options)
    mode = read(SPEC/'replay-oracle.json')['mode']
    config = dict(version=1, expectedArgv=native+mode, directory=str(directory/'wire'),
        nativeExecutable=str(image), maxRawBytes=8*1024*1024, tickHz=os.sysconf('SC_CLK_TCK'))
    write(directory/'tap-config.json', config)
    env = environment(directory, variant['report'])
    env['ROOK2_WIRE_TAP_CONFIG'] = str(directory/'tap-config.json')
    command = ['/usr/bin/node', '--import', str(TAP),
        str(SPEC/'replay-check.mjs'), '--case', step['case'], '--', *native]
    write(directory/'launch.json', dict(argv=command, step=step, profileEnvironment={}))
    run_deadline = min(deadline, time.monotonic()+LIMITS['perLifeSeconds'])
    with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        try:
            while child.poll() is None:
                assert time.monotonic() < run_deadline, 'per-life or aggregate deadline'
                assert (directory/'stdout').stat().st_size <= 8*1024*1024, 'comparator stdout cap'
                assert (directory/'stderr').stat().st_size <= 1024*1024, 'comparator stderr cap'
                assert not (directory/'wire/failure.json').exists(), 'raw tap failure'
                time.sleep(.05)
        except BaseException as error:
            stop_owned(child)
            write(directory/'failure.json', dict(exit=child.poll(), step=step, error=repr(error)))
            raise
    assert child.returncode == 0 and (directory/'stderr').stat().st_size == 0
    receipt = native_receipt(directory/'native.json', image, budget, options+mode, hashes)
    tap = read(directory/'wire/receipt.json')
    assert tap['failure'] is None and len(tap['searches']) == 1
    row = dict(**step, directory=str(directory), nativePid=receipt['native_pid'],
        searchWallNs=tap['searches'][0]['wallNs'], wholeCpuSeconds=receipt['total_cpu_s'],
        wholeWallNs=receipt['wall_ns'], nonSearchWallNs=receipt['wall_ns']-tap['searches'][0]['wallNs'],
        rssKiB=receipt['maxrss_linux_kib'], taskAffinities=receipt['native_post_exec']['task_affinities'],
        sha256={name: sha(directory/name) for name in ['native.json', 'stdout', 'stderr',
            'wire/receipt.json', 'tap-config.json', 'launch.json']},
        placement=audit_placement(directory, receipt, hashes), controllerStartMonotonicNs=started)
    if variant['report']:
        row['colors'] = dict(path=str(directory/'colors.json'), sha256=sha(directory/'colors.json'),
            report=colors_report(directory/'colors.json', budget))
    else:
        assert receipt['colors_report_path'] is None
        row['colors'] = None
    # Raw replay is independently reparsed rather than trusting comparator pass.
    _, row['orderedPosts'] = audit.lifetime(directory, row, step, image, budget, options, hashes)
    row['controllerEndMonotonicNs'] = time.monotonic_ns()
    return row


def proc_ticks(pid):
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    return int(fields[11])+int(fields[12])


def idle_probe(directory, name, image, variant, deadline, hashes):
    directory.mkdir()
    budget, options = variant['budget'], variant['options']
    command = supervisor(image, budget, directory, options)
    write(directory/'launch.json', dict(argv=command, variant=name, kind='startup-idle-shutdown'))
    started = time.monotonic_ns()
    (directory/'stdin.raw').touch(exist_ok=False)
    (directory/'stdout.raw').touch(exist_ok=False)
    with (directory/'stderr').open('xb') as stderr:
        child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=stderr, env=environment(directory, variant['report']), start_new_session=True)
        selector = selectors.DefaultSelector()
        try:
            ready = ready_record(directory, child.pid, image, budget, min(deadline, time.monotonic()+12))
            release = time.monotonic_ns()
            write(directory/'native.json.input-gate.json', dict(
                schema='rook2-placement-input-gate-v1', implementation='python-idle',
                gate_sha256=sha(Path(__file__)), ready_path=str(directory/'native.json.ready'),
                ready_sha256=sha(directory/'native.json.ready'), native_pid=ready['native_pid'],
                supervisor_pid=child.pid, release_monotonic_ns=str(release), first_write_bytes=8,
                first_write_sha256=hashlib.sha256(b'cm_parm\n').hexdigest()))
            (directory/'stdin.raw').write_bytes(b'cm_parm\n')
            child.stdin.write(b'cm_parm\n'); child.stdin.flush()
            selector.register(child.stdout, selectors.EVENT_READ)
            reply, reply_deadline = b'', min(deadline, time.monotonic()+10)
            while not reply.endswith(b'\n'):
                remaining = reply_deadline-time.monotonic()
                assert remaining > 0 and selector.select(remaining), 'idle startup deadline'
                chunk = os.read(child.stdout.fileno(), 64)
                assert chunk, 'idle native exited before startup reply'
                reply += chunk
                (directory/'stdout.raw').write_bytes(reply)
                assert len(reply) <= 64, 'idle reply cap'
            assert reply == b'cm_parm\n'
            startup = time.monotonic_ns()-started
            pid = ready['native_pid']
            assert Path(f'/proc/{child.pid}/task/{child.pid}/children').read_text().split() == [str(pid)]
            before = proc_ticks(pid)
            begin = time.monotonic_ns()
            assert time.monotonic()+.25 < deadline
            time.sleep(.25)
            after, end = proc_ticks(pid), time.monotonic_ns()
            with (directory/'stdin.raw').open('ab') as sent:
                sent.write(b'quit\n')
            child.stdin.write(b'quit\n'); child.stdin.close()
            shutdown = time.monotonic_ns()
            assert child.wait(timeout=max(.001, min(10, deadline-time.monotonic()))) == 0
            shutdown = time.monotonic_ns()-shutdown
            assert child.stdout.read() == b''
        except BaseException as error:
            stop_owned(child)
            write(directory/'failure.json', dict(error=repr(error), supervisorPid=child.pid, exit=child.returncode))
            raise
        finally:
            selector.close()
            child.stdout.close()
            if child.stdin is not None and not child.stdin.closed:
                child.stdin.close()
    native = native_receipt(directory/'native.json', image, budget, options, hashes)
    assert (directory/'stderr').stat().st_size == 0
    hz = os.sysconf('SC_CLK_TCK')
    report = (dict(path=str(directory/'colors.json'), sha256=sha(directory/'colors.json'),
        report=colors_report(directory/'colors.json', budget, idle=True)) if variant['report'] else None)
    row = dict(variant=name, nativePid=pid, supervisorPid=child.pid,
        idleNs=end-begin, idleCpuTicks=after-before, tickHz=hz, idleCpuSeconds=(after-before)/hz,
        startupReplyNs=startup, startupCpuTicks=before, shutdownStartCpuTicks=after,
        idleStartMonotonicNs=begin, idleEndMonotonicNs=end, shutdownSupervisorNs=shutdown,
        wholeCpuSeconds=native['total_cpu_s'], wholeWallNs=native['wall_ns'], rssKiB=native['maxrss_linux_kib'],
        placement=audit_placement(directory, native, hashes), colors=report,
        boundaries='startup through cm_parm reply; whole-process ticks for250ms; quit through joined supervisor exit; tick resolution',
        sha256={name: sha(directory/name) for name in ['launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr']})
    write(directory/'probe.json', row)
    return row


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['control', 'candidate', 'control-build', 'candidate-build', 'preparation', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    control, candidate = args.control.resolve(), args.candidate.resolve()
    assert control == CONTROL_IMAGE and args.control_build.resolve() == CONTROL_BUILD
    control_build, candidate_build = args.control_build.resolve(), args.candidate_build.resolve()
    prepared = preparation(args.preparation.resolve())
    receipts = admission(control_build, candidate_build, control, candidate, prepared)
    assert set(os.sched_getaffinity(0)) == HELPERS
    prepared_path = args.preparation.resolve()
    prepared_run_path = candidate_build.parent/'prepared-run.json'
    prepared_record = prepared_run(prepared_run_path, prepared_path, prepared, candidate)
    out = args.output.resolve(); out.mkdir()
    modes = variants(control, candidate)
    inputs = code_paths()+[prepared_path, prepared_run_path, control, candidate]
    inputs += [Path(path) for path in prepared_record['inputSha256']]
    inputs += [Path(path) for path in prepared['oldEvidenceSha256']]
    inputs += [Path(p) for p in prepared['inputSha256']]
    inputs += [Path(p) for p in baseline()]
    for directory, receipt in zip([control_build, candidate_build], receipts):
        inputs += [directory/'receipt.json', directory/'build.stderr']
        inputs += [directory/'source-before'/name for name in
                   (receipt['source_sha256_before'] | receipt['tool_sha256_before'])]
    plan = dict(schema='rook2-epoch-colors-generic-v1', variants=modes, schedule=schedule(),
        controlBuild=str(control_build), candidateBuild=str(candidate_build),
        sourcePreparation=str(prepared_path), preparedRun=str(prepared_run_path),
        pipelineStartMonotonicNs=prepared_record['pipelineStartMonotonicNs'], pipelineSeconds=3600,
        coordinatorCpu=14, helperCpus=[6, 4],
        nativePreExecAffinities={'1': [6, 14], '2': [6, 14], '3': [4, 6, 14]},
        idleOwnedSiblings=[5, 7, 15], helperAffinity=sorted(HELPERS),
        inputSha256={str(path): sha(path) for path in sorted(set(inputs))}, protectedArtifacts=baseline(),
        limits=LIMITS, sourceChanges=prepared['sourceChanges'],
        evidenceReuse=EVIDENCE_REUSE, readinessSemantics=prepared['readinessSemantics'],
        images={name: image_layout(Path(value['path'])) for name, value in modes.items()},
        controlSource=prepared['controlSource'], candidateSource=prepared['candidateSource'],
        boundaries=dict(search='unchanged tap: go write through move data callback',
            cpu='direct native wait4: all joined threads and Python pre-exec prefix', rss='whole lifetime peak RSS',
            placement='external supervisor places main14/helpers6/4 before first setup input',
            counters='all four configurations report after joined shutdown; sparse every512 FULL dispatches in oldcolors3/epoch3',
            lifecycle='four separate startup/250ms process-tick idle/quit probes'),
        assumptions='original raw auditor adapted only ACCOUNT/ROOT/native_receipt; no native execution in reconciler',
        scope='three-case generic bounded discriminator; no PGO/full qualification/adoption')
    write(out/'plan.json', plan)
    state = dict(complete=False, failure=None, runs=[], idle=[], streamStartMonotonicNs=time.monotonic_ns())
    write(out/'progress.json', state)
    placement = housekeeping.Placement()
    housekeeping_record = dict(schema='rook2-epoch-colors-housekeeping-v1',
        helperCpus=sorted(HELPERS), applies=[], originals=[], leaders=[], restored=None, failure=None)
    deadline = min(time.monotonic()+LIMITS['totalSeconds'],
        prepared_record['pipelineStartMonotonicNs']/1e9+3600)

    def place():
        housekeeping_record['applies'].append(placement.apply(HELPERS))
        housekeeping_record['originals'] = [dict(pid=p, tid=t, starttime=s, affinity=mask)
            for (p, t, s), mask in sorted(placement.original.items())]
        housekeeping_record['leaders'] = [dict(pid=p, starttime=s, affinity=mask)
            for (p, s), mask in sorted(placement.leaders.items())]
        write(out/'housekeeping.json', housekeeping_record)

    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    try:
        for index, step in enumerate(plan['schedule']):
            assert time.monotonic() < deadline, 'aggregate collection deadline'
            place()
            value = modes[step['variant']]
            directory = out/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
            state['runs'].append(run_lifetime(directory, step, Path(value['path']), value, deadline, plan['inputSha256']))
            write(out/'progress.json', state)
        for name, value in modes.items():
            assert time.monotonic()+35 < deadline, 'insufficient aggregate idle allowance'
            place()
            state['idle'].append(idle_probe(out/('idle-'+name), name, Path(value['path']), value,
                                           deadline, plan['inputSha256']))
        state['summaries'] = []
        for case in CASES:
            for name in NAMES:
                rows = [r for r in state['runs'] if r['case'] == case and r['variant'] == name and not r['warmup']]
                assert len(rows) == 3
                state['summaries'].append(dict(case=case, variant=name,
                    **{key: dist([r[key] for r in rows]) for key in METRICS}))
        assert all(sha(path) == digest for path, digest in plan['inputSha256'].items())
        admission(control_build, candidate_build, control, candidate, prepared)
        assert time.monotonic() < deadline
        state.update(complete=True, streamEndMonotonicNs=time.monotonic_ns())
    except BaseException as error:
        state['failure'] = repr(error)
        write(out/'failure.json', dict(error=repr(error), completedReplayLives=len(state['runs'])))
        raise
    finally:
        try:
            housekeeping_record['restored'] = placement.restore()
            housekeeping_record['postRestoreSelfAffinity'] = sorted(os.sched_getaffinity(0))
        except BaseException as error:
            housekeeping_record['failure'] = repr(error)
            state.update(complete=False, failure='housekeeping restoration failed: '+repr(error))
            raise
        finally:
            write(out/'housekeeping.json', housekeeping_record)
            (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
            write(out/'result.json', state)
    print('complete48 replay lives +4 separate idle processes', flush=True)


if __name__ == '__main__':
    main()
