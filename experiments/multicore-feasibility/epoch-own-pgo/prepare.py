#!/usr/bin/env python3
"""One joint1/2/3 own-PGO preparation, then a separate fixed full54 collection.

Both invocations share the original3600-second ceiling, including the gap. The
parent announces quiet windows before training and before comparison collection.
"""
import argparse
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import (HERE, ROOT, DEFAULT_CRATE, BUILD_ADAPTER, FOCUSED, HELPERS,
    PIPELINE_SECONDS, TRAIN_SECONDS, admit_build, baseline, generic_evidence,
    housekeeping, image_layout, preparation, read, sha, write)


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=['prepare', 'collect'], default='prepare')
    args = parser.parse_args()
    prepared_path, out = args.preparation.resolve(), args.output.resolve()
    prepared = preparation(prepared_path)
    assert set(os.sched_getaffinity(0)) == HELPERS
    if args.stage == 'prepare':
        out.mkdir()
        start = time.monotonic_ns()
        state = dict(schema='rook2-epoch-own-pgo-pipeline-v1', complete=False,
            prepared=False, collected=False, failure=None, active=None, stages=[],
            pipelineStartMonotonicNs=start, pipelineDeadlineMonotonicNs=start+PIPELINE_SECONDS*10**9,
            pipelineSeconds=PIPELINE_SECONDS, preparation=str(prepared_path),
            preparationSha256=sha(prepared_path), sourcePreparation=prepared,
            protectedArtifacts=baseline(), evidenceReuse=generic_evidence(prepared),
            parentQuietAnnouncementsRequired=['training', 'comparison'],
            scope='one fresh joint162 profile, one use build, fresh13CLI+2affinity, fixed270+5; no small screen or adoption')
    else:
        state = read(out/'pipeline.json')
        assert state['schema'] == 'rook2-epoch-own-pgo-pipeline-v1'
        assert state['prepared'] and not state['collected'] and state['failure'] is None
        assert state['preparation'] == str(prepared_path) and state['preparationSha256'] == sha(prepared_path)
        assert state['sourcePreparation'] == prepared
        assert state['stages'][-1]['stage'] == 'cli-affinity'
        assert read(out/'prepared-run.json')['complete']
        assert read(out/'housekeeping-prepare.json')['restored'] is not None
        state['complete'] = False
    assert state['pipelineDeadlineMonotonicNs'] == state['pipelineStartMonotonicNs']+PIPELINE_SECONDS*10**9
    deadline = state['pipelineDeadlineMonotonicNs']/1e9
    assert time.monotonic() < deadline, 'original pipeline deadline exhausted'
    write(out/'pipeline.json', state)
    env = dict(os.environ, PATH='/usr/bin:/bin', RUSTC='/usr/bin/rustc', CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTFLAGS','RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or key.startswith(('CARGO_PROFILE_', 'ROOK2_')):
            env.pop(key, None)
    placement = housekeeping.Placement()
    housekeeping_record = dict(schema='rook2-epoch-own-pgo-housekeeping-v1', helperCpus=sorted(HELPERS),
        applies=[], originals=[], leaders=[], restored=None, failure=None)

    def check():
        assert preparation(prepared_path) == prepared
        assert sha(prepared_path) == state['preparationSha256']
        assert baseline() == state['protectedArtifacts']
        assert time.monotonic() < deadline, 'persisted pipeline deadline'

    def stage(name, command, cap):
        check()
        housekeeping_record['applies'].append(placement.apply(HELPERS))
        housekeeping_record['originals'] = [dict(pid=p,tid=t,starttime=s,affinity=mask)
            for (p,t,s),mask in sorted(placement.original.items())]
        housekeeping_record['leaders'] = [dict(pid=p,starttime=s,affinity=mask)
            for (p,s),mask in sorted(placement.leaders.items())]
        state['active'] = name
        write(out/'pipeline.json', state)
        write(out/('housekeeping-'+args.stage+'.json'), housekeeping_record)
        started = time.monotonic_ns()
        stage_deadline_ns = min(state['pipelineDeadlineMonotonicNs'], started+cap*10**9)
        stage_deadline = stage_deadline_ns/1e9
        assert time.monotonic_ns() < stage_deadline_ns
        with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen([str(value) for value in command], cwd=ROOT, env=env,
                stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                remaining = stage_deadline-time.monotonic(); assert remaining > 0
                code = child.wait(timeout=remaining)
                assert time.monotonic_ns() < stage_deadline_ns, 'stage deadline'
            except BaseException:
                try: os.killpg(child.pid, signal.SIGINT)
                except ProcessLookupError: pass
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    try: os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    child.wait()
                raise
        ended = time.monotonic_ns()
        state['stages'].append(dict(stage=name, argv=[str(value) for value in command],
            cwd=str(ROOT), pid=child.pid, exit=code, startedMonotonicNs=started, endedMonotonicNs=ended,
            deadlineMonotonicNs=stage_deadline_ns, elapsedNs=ended-started,
            stdoutSha256=sha(out/(name+'.stdout')), stderrSha256=sha(out/(name+'.stderr'))))
        write(out/'pipeline.json', state)
        assert code == 0, (name,code)
        print(name+' exit '+str(code), flush=True)
        check()

    def freeze(directory, name, mode):
        receipt = read(directory/'receipt.json')
        target = out/name
        assert not target.exists()
        shutil.copy2(Path(receipt['binary_output']['path']), target)
        admit_build(directory, target, mode, prepared)
        return target

    try:
        if args.stage == 'prepare':
            stage('instrumented-build', ['/usr/bin/python3', BUILD_ADAPTER,
                '--crate', DEFAULT_CRATE, '--mode', 'generic', '--bin', 'rook2', '--jobs', '4',
                '--pgo-generate', out/'profile-raw', '--output', out/'instrumented-build'], 300)
            instrumented = freeze(out/'instrumented-build', 'rook2-instrumented', 'instrumented')
            clock = ['--pipeline-start-ns', str(state['pipelineStartMonotonicNs']),
                     '--pipeline-deadline-ns', str(state['pipelineDeadlineMonotonicNs'])]
            stage('training', ['/usr/bin/python3', HERE/'train.py', '--build', out/'instrumented-build',
                '--engine', instrumented, '--preparation', prepared_path, *clock,
                '--output', out/'training'], 2500)
            stage('training-audit', ['/usr/bin/python3', HERE/'training_reconcile.py', out/'training',
                '--pipeline-deadline-ns', str(state['pipelineDeadlineMonotonicNs'])], 120)
            training_audit = read(out/'training/reconciled.json')
            assert training_audit['complete'] and training_audit['nativeProcesses'] == 162
            assert training_audit['remerge']['byteIdentical'] is True
            stage('use-build', ['/usr/bin/python3', BUILD_ADAPTER, '--crate', DEFAULT_CRATE,
                '--mode', 'generic', '--bin', 'rook2', '--jobs', '4',
                '--pgo-use', out/'training/merged.profdata', '--training-record', out/'training/training.json',
                '--ext-tsp-profiled', '--output', out/'use-build'], 300)
            candidate = freeze(out/'use-build', 'rook2-pgo', 'profile-use')
            stage('cli-affinity', ['/usr/bin/python3', FOCUSED, '--engine', candidate,
                '--output', out/'focused'], 420)
            cli = read(out/'focused/result.json')
            assert cli['complete'] and len(cli['cli']) == 13 and len(cli['affinityReplays']) == 2
            assert cli['engineSha256'] == sha(candidate)
            files = [out/(row['stage']+'.'+suffix) for row in state['stages'] for suffix in ['stdout','stderr']]
            files += [path for path in (out/'focused').rglob('*') if path.is_file()]
            files += [out/'training'/name for name in ['plan.json','training.json','reconciled.json','merged.profdata']]
            files += [out/'instrumented-build'/name for name in ['receipt.json','build.stderr']]
            files += [out/'use-build'/name for name in ['receipt.json','build.stderr']]
            record = dict(schema='rook2-epoch-own-pgo-prepared-run-v1', complete=True,
                sourcePreparation=str(prepared_path), sourcePreparationSha256=sha(prepared_path),
                source=prepared['candidateSource'], evidenceReuse=state['evidenceReuse'],
                stages=list(state['stages']), candidate=image_layout(candidate), instrumented=image_layout(instrumented),
                pipelineStartMonotonicNs=state['pipelineStartMonotonicNs'],
                pipelineDeadlineMonotonicNs=state['pipelineDeadlineMonotonicNs'],
                preparedMonotonicNs=time.monotonic_ns(),
                profileSha256=sha(out/'training/merged.profdata'), trainingAudit=training_audit,
                inputSha256={str(path):sha(path) for path in sorted(set(files))})
            write(out/'prepared-run.json', record)
            state.update(prepared=True, complete=True, candidate=str(candidate), candidateSha256=sha(candidate), active=None)
        else:
            candidate = Path(state['candidate'])
            assert sha(candidate) == state['candidateSha256']
            stage('comparison', ['/usr/bin/python3', HERE/'collect.py', '--preparation', prepared_path,
                '--prepared-run', out/'prepared-run.json', '--output', out/'full54'], 1900)
            stage('comparison-audit', ['/usr/bin/python3', HERE/'reconcile.py', out/'full54'], 120)
            assert read(out/'full54/reconciled.json')['complete']
            state.update(collected=True, complete=True, active=None)
        check()
    except BaseException as error:
        state.update(complete=False, failure=repr(error))
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
            state['lastInvocationEndMonotonicNs'] = time.monotonic_ns()
            if state['lastInvocationEndMonotonicNs'] >= state['pipelineDeadlineMonotonicNs']:
                state.update(complete=False, failure=state['failure'] or 'persisted pipeline deadline during cleanup')
            write(out/('housekeeping-'+args.stage+'.json'), housekeeping_record)
            write(out/'pipeline.json', state)
    assert state['complete'] and state['failure'] is None, state['failure']
    print('prepared joint-PGO image; stopped before comparison' if args.stage == 'prepare'
          else 'completed descriptive270+5 and raw audit', flush=True)


if __name__ == '__main__':
    main()
