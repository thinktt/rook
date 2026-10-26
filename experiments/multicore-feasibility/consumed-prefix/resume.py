#!/usr/bin/env python3
"""Adopt audited08; launch only35 once with the unchanged02 image and fixed limits."""
import argparse
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time
sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, BASE_HELPER, FROZEN_TOOLS, read, write, sha, baseline, snapshot, admit
from collect import ACCOUNT, SPEC, AS_BYTES, OUTPUT_BYTES, policy, materialization
from reconcile_continuation import ORIGINAL, IMAGE_SHA, NAMES, original_evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, default=ORIGINAL)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); original, chosen_path, out = args.original.resolve(), args.policy.resolve(), args.output.resolve()
    assert sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    assert original == ORIGINAL and out.is_dir() and (out/'adopted-08.json').is_file()
    assert not (out/'continuation-plan.json').exists() and not (out/'01-profile-35-q2').exists() and not (out/'result.json').exists()
    chosen = policy(chosen_path); evidence = original_evidence(original, chosen)
    assert read(out/'adopted-08.json') == dict(complete=True, schema='rook2-consumed-prefix-adopted08-v1', **evidence)
    image = Path(evidence['image']); assert sha(image) == IMAGE_SHA
    frozen = out/'repaired-tools'; frozen.mkdir()
    scripts = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py', 'resume.py', 'reconcile_continuation.py']]
    for path in [*scripts, chosen_path]:
        shutil.copy2(path, frozen/path.name)
    shutil.copy2(chosen_path, out/'policy.json'); assert sha(out/'policy.json') == sha(chosen_path)
    paths = [*scripts, chosen_path, BASE_HELPER, *FROZEN_TOOLS, ACCOUNT, SPEC/'workloads.json',
             materialization('profile-08'), materialization('profile-35'), out/'adopted-08.json', *frozen.iterdir()]
    paths += [Path(p) for p in evidence['originalBindings']]
    pins = {str(path): sha(path) for path in paths}
    plan = dict(schema='rook2-consumed-prefix-continuation-v1', original=str(original), image=str(image), imageSha256=IMAGE_SHA,
        policy=chosen, policyPath=str(chosen_path), policySha256=sha(chosen_path), adoptedEvidence=evidence,
        currentInputs=pins, schedule=[dict(case='profile-08', action='adopt-existing'), dict(case='profile-35', action='one-new-life')],
        nativeCpu=14, helperAffinity=sorted(HELPERS), quietSiblings=[7,15],
        limits=dict(perLifeSeconds=180, streamSeconds=900, addressSpaceBytes=AS_BYTES, stdoutBytesPerCase=OUTPUT_BYTES),
        scope='Schema-label/admission repair only. Original08 adopted unchanged. Exactly one35 process; no tests/builds/retries/Rust or binary changes. Physical paired-mode costs are reported-only.')
    write(out/'continuation-plan.json', plan)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    state = dict(schema='rook2-consumed-prefix-continuation-result-v1', complete=False, failure=None, newRuns=[], nativeLaunches=0,
                 startMonotonicNs=time.monotonic_ns(), adopted08Sha256=sha(out/'adopted-08.json'))
    deadline = time.monotonic()+900
    env = dict(os.environ, PATH='/usr/bin:/bin')
    for key in list(env):
        if key.startswith('ROOK2_') or key == 'LLVM_PROFILE_FILE':
            env.pop(key, None)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (AS_BYTES, AS_BYTES))
        resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_BYTES, OUTPUT_BYTES))

    try:
        step = dict(case='profile-35', queue_depth=2, repeat=1)
        directory = out/'01-profile-35-q2'; directory.mkdir()
        options = ['--input', str(materialization('profile-35')), *chosen['driverOptions']]
        command = ['/usr/bin/python3', str(ACCOUNT), '--engine', str(image), '--record', str(directory/'native.json'),
                   '--known-single-process', *options]
        write(directory/'launch.json', dict(argv=command, nativeArgv=[str(image), *options], step=step,
            policySha256=plan['policySha256'], addressSpaceBytes=AS_BYTES, stdoutBytes=OUTPUT_BYTES))
        start = time.monotonic_ns(); code, cleanup = None, None
        with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
            child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                     env=env, start_new_session=True, preexec_fn=limits)
            state['nativeLaunches'] = 1; write(out/'progress.json', state)
            try:
                code = child.wait(timeout=max(.001, min(180, deadline-time.monotonic())))
            except BaseException:
                cleanup = 'external deadline/interruption'
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    code = child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); code = child.wait()
                raise
            finally:
                terminal = dict(pid=child.pid, exit=code, cleanup=cleanup, startMonotonicNs=start, endMonotonicNs=time.monotonic_ns())
                write(directory/'terminal.json', terminal)
        assert code == 0 and cleanup is None and (directory/'stderr').stat().st_size == 0
        assert 0 < (directory/'stdout').stat().st_size <= OUTPUT_BYTES
        native, report = read(directory/'native.json'), read(directory/'stdout')
        assert native['failure'] is None and native['native_exit_code'] == 0
        assert native['engine_sha256_before'] == native['engine_sha256_after'] == IMAGE_SHA
        assert report['schema'] == chosen['reportSchema'] and report['caps'] == chosen['caps']
        assert report['unsafe_validation'] is False and report['fatal_reason'] is None
        row = dict(**step, directory=str(directory), nativePid=native['native_pid'], supervisorPid=child.pid,
            wholeCpuSeconds=native['total_cpu_s'], rssKiB=native['maxrss_linux_kib'], nativeWallNs=native['wall_ns'],
            controllerWallNs=terminal['endMonotonicNs']-start, sha256={n: sha(directory/n) for n in NAMES})
        state['newRuns'].append(row); write(out/'progress.json', state)
        assert all(sha(path) == digest for path, digest in pins.items())
        assert original_evidence(original, chosen) == evidence
        assert baseline() == evidence['baseline'] and time.monotonic() < deadline
        state.update(complete=True, endMonotonicNs=time.monotonic_ns()); write(out/'result.json', state)
        print('completed only35 once using original02 image;08 adopted, no rerun', flush=True)
    except BaseException as error:
        state.update(failure=repr(error), endMonotonicNs=time.monotonic_ns()); write(out/'result.json', state)
        write(out/'failure.json', dict(failure=repr(error), newNativeLaunches=state['nativeLaunches'])); raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())

if __name__ == '__main__':
    main()
