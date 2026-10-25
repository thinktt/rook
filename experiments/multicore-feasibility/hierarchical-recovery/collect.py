#!/usr/bin/env python3
"""Two preselected serial recovery simulations, profile08 then35; no wire replay."""
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
from build import HERE, ROOT, HELPERS, BASE_HELPER, admit, baseline, read, write, sha

ACCOUNT = ROOT/'tools/account_native.py'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
INPUTS = HERE.parent/'branch-transactions/inputs'
CASES = ['profile-08', 'profile-35']
CAPS = dict(queue_depth=2, max_depth=6, max_tail_candidates=8, log_events=524288,
            max_segments=131072, max_recorded_nodes=262144, max_forest_bytes=536870912,
            max_touched_groups=131072, oracle_trace_cap=131072)
OPTIONS = {'--queue-depth': 'queue_depth', '--max-depth': 'max_depth', '--max-tail': 'max_tail_candidates',
           '--log-events': 'log_events', '--max-segments': 'max_segments',
           '--max-recorded-nodes': 'max_recorded_nodes', '--max-forest-bytes': 'max_forest_bytes',
           '--max-touched-groups': 'max_touched_groups'}
AS_BYTES, OUTPUT_BYTES = 8*1024**3, 16*1024**2


def policy(path):
    data = read(path)
    assert data['schema'] == 'rook2-hierarchical-policy-v1'
    assert data['reportSchema'] == 'rook2-hierarchical-recovery-v1'
    assert data['caps'] == CAPS
    assert all(type(value) is int for value in data['caps'].values())
    args = data['driverOptions']; assert type(args) is list and len(args) == 2*len(OPTIONS)
    assert all(type(arg) is str for arg in args)
    seen = set()
    for flag, value in zip(args[::2], args[1::2]):
        assert flag in OPTIONS and flag not in seen; seen.add(flag)
        assert value == str(CAPS[OPTIONS[flag]])
    assert seen == set(OPTIONS)
    return data


def materialization(case):
    path = INPUTS/(case+'.txt')
    assignments = {}
    for line in path.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        key, value = line.split('=', 1); assert key not in assignments; assignments[key] = value
    workload = next(c for c in read(SPEC/'workloads.json')['cases'] if c['id'] == case)
    assert workload['position']['initial'] == 'standard-start'
    p = workload['personality']['parameters']
    own = ['myp', 'myn', 'myb', 'myr', 'myq', 'myk', 'mycc', 'mymob', 'myks', 'mypp', 'mypw']
    opponent = ['opp', 'opn', 'opb', 'opr', 'opq', 'opk', 'opcc', 'opmob', 'opks', 'oppp', 'oppw']
    assert assignments == dict(case=case, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        moves=' '.join(workload['position']['moves']), own=','.join(str(p[k]) for k in own),
        opponent=','.join(str(p[k]) for k in opponent), evaluation=','.join(str(p[k]) for k in ['avd', 'cfd', 'sop']),
        search=','.join(str(p[k]) for k in ['sel', 'md', 'tts', 'ana']), randomness='0')
    assert p['rnd'] == 0
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); build, policy_path, out = args.build.resolve(), args.policy.resolve(), args.output.resolve()
    receipt, chosen = admit(build), policy(policy_path); image = Path(receipt['binary'])
    assert sorted(os.sched_getaffinity(0)) == sorted(HELPERS)
    inputs = {case: materialization(case) for case in CASES}
    out.mkdir(); shutil.copy2(policy_path, out/'policy.json'); assert sha(out/'policy.json') == sha(policy_path)
    paths = [HERE/n for n in ['build.py', 'collect.py', 'reconcile.py', 'pipeline.py']]
    paths += [BASE_HELPER, ACCOUNT, policy_path, build/'receipt.json', build/'stdout', build/'stderr',
              image, SPEC/'workloads.json', *inputs.values()]
    paths += [Path(p) for p in receipt['toolsBefore']]
    paths += [Path(p) for p in receipt['baselineBefore']['protectedArtifacts']]
    paths.append(Path(receipt['baselineBefore']['receipt']['path']))
    schedule = [dict(case=case, queue_depth=2, repeat=1) for case in CASES]
    plan = dict(schema='rook2-hierarchical-collection-v1', build=str(build), binary=str(image),
                binarySha256=sha(image), policy=chosen, policyPath=str(policy_path),
                policySha256=sha(policy_path), sourcePins=receipt['sourceBefore'], baseline=receipt['baselineBefore'],
                schedule=schedule, nativeCpu=14, helperAffinity=sorted(HELPERS), quietSiblings=[7, 15],
                inputSha256={str(path): sha(path) for path in paths},
                limits=dict(perLifeSeconds=180, streamSeconds=900, addressSpaceBytes=AS_BYTES, stdoutBytesPerCase=OUTPUT_BYTES),
                scope='serial fixed-completion NoHost/timingNone/rnd0/inline FULL; queue2 is simulated, no branch worker; original histories/personality materialized, not standard wire replay')
    write(out/'plan.json', plan)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    state = dict(complete=False, failure=None, runs=[], startMonotonicNs=time.monotonic_ns())
    deadline = time.monotonic()+900
    env = dict(os.environ, PATH='/usr/bin:/bin')
    for key in list(env):
        if key.startswith('ROOK2_') or key == 'LLVM_PROFILE_FILE':
            env.pop(key, None)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (AS_BYTES, AS_BYTES))
        resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_BYTES, OUTPUT_BYTES))

    try:
        for index, step in enumerate(schedule):
            assert time.monotonic() < deadline
            directory = out/f'{index:02d}-{step["case"]}-q2'; directory.mkdir()
            native_args = ['--input', str(inputs[step['case']]), *chosen['driverOptions']]
            command = ['/usr/bin/python3', str(ACCOUNT), '--engine', str(image),
                       '--record', str(directory/'native.json'), '--known-single-process', *native_args]
            write(directory/'launch.json', dict(argv=command, nativeArgv=[str(image), *native_args], step=step,
                policySha256=plan['policySha256'], addressSpaceBytes=AS_BYTES, stdoutBytes=OUTPUT_BYTES))
            start = time.monotonic_ns(); code, cleanup = None, None
            with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
                child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                         env=env, start_new_session=True, preexec_fn=limits)
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
                    terminal = dict(pid=child.pid, exit=code, cleanup=cleanup,
                                    startMonotonicNs=start, endMonotonicNs=time.monotonic_ns())
                    write(directory/'terminal.json', terminal)
            assert code == 0 and cleanup is None
            assert (directory/'stderr').stat().st_size == 0
            assert 0 < (directory/'stdout').stat().st_size <= OUTPUT_BYTES
            native, report = read(directory/'native.json'), read(directory/'stdout')
            assert native['failure'] is None and native['native_exit_code'] == 0
            assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
            assert report['schema'] == chosen['reportSchema'] and report['caps'] == chosen['caps']
            assert report['unsafe_validation'] is False and report['fatal_reason'] is None
            row = dict(**step, directory=str(directory), nativePid=native['native_pid'], supervisorPid=child.pid,
                wholeCpuSeconds=native['total_cpu_s'], rssKiB=native['maxrss_linux_kib'],
                nativeWallNs=native['wall_ns'], controllerWallNs=terminal['endMonotonicNs']-start,
                sha256={name: sha(directory/name) for name in ['launch.json', 'terminal.json', 'native.json', 'stdout', 'stderr']})
            state['runs'].append(row); write(out/'progress.json', state)
            print('completed '+step['case']+' serial recovery simulation', flush=True)
        assert all(sha(path) == digest for path, digest in plan['inputSha256'].items())
        assert baseline() == plan['baseline']; admit(build); assert time.monotonic() < deadline
        state.update(complete=True, endMonotonicNs=time.monotonic_ns()); write(out/'result.json', state)
    except BaseException as error:
        state['failure'] = repr(error); state['endMonotonicNs'] = time.monotonic_ns(); write(out/'result.json', state)
        write(out/'failure.json', dict(failure=repr(error), completed=len(state['runs']))); raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())


if __name__ == '__main__':
    main()
