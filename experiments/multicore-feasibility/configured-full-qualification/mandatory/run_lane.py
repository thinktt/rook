#!/usr/bin/env python3
"""One finite build/test/mandatory lane; no native retries or ordinary rebuild."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
from common import HELPERS, read, put, sha, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    args = parser.parse_args()
    base = args.raw.resolve(); plan = read(base/'plan.json')
    assert plan['schema'] == 'rook2-configured-full-mandatory-v1'
    assert sorted(os.sched_getaffinity(0)) == plan['helperCpus'] == HELPERS
    verify(plan)
    assert not (base/'lane-clock.json').exists()
    assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
    started = time.monotonic_ns(); deadline = started+plan['aggregateSeconds']*10**9
    put(base/'lane-clock.json', dict(startMonotonicNs=started, driverPid=os.getpid(),
        seconds=plan['aggregateSeconds'], basis='before first native test-list launch; build/test/fixtures/gaps/offline audit included'))
    state = dict(complete=False, failure=None, stages=[], ownedGroups=[], performanceMeasurement=False)
    artifacts = dict(libraryTests=plan['libraryExecutable'])

    def reap():
        rows = []
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if not pid:
                    break
                rows.append(dict(pid=pid, waitStatus=status))
            except ChildProcessError:
                break
        return rows

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (plan['limits']['addressSpaceBytes'],)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (plan['limits']['stageOutputBytes'],)*2)

    def stage(name):
        verify(plan)
        cfg, directory = plan['stages'][name], base/name
        env = {**os.environ, **plan['environment']}
        env.pop('LLVM_PROFILE_FILE', None)
        if name == 'fixtures':
            env.update(ROOK2_FOCUSED_TAP_CONFIG=str(directory/'tap-config.json'),
                       ROOK2_FOCUSED_NATIVE_DIR=str(directory/'native'))
        stage_deadline = min(deadline, time.monotonic_ns()+cfg['maximumSeconds']*10**9)
        assert time.monotonic_ns() < stage_deadline
        cleanup, code, pid = None, None, None
        with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
            child = subprocess.Popen(cfg['argv'], cwd=cfg['cwd'], stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, env=env, start_new_session=True, preexec_fn=limits)
            pid = child.pid; state['ownedGroups'].append(pid)
            put(directory/'launch.json', dict(pid=pid, pgid=pid, argv=cfg['argv'], cwd=cfg['cwd'],
                expectedExit=cfg['expectedExit'], affinity=sorted(os.sched_getaffinity(pid))))
            try:
                while child.poll() is None:
                    if time.monotonic_ns() >= stage_deadline:
                        raise TimeoutError('per-stage or aggregate deadline')
                    if stdout.tell()+stderr.tell() > plan['limits']['stageOutputBytes']:
                        raise RuntimeError('stage output storage cap')
                    time.sleep(.05)
                code = child.wait()
            except BaseException:
                cleanup = dict(term=True, kill=False)
                try:
                    os.killpg(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    code = child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    cleanup['kill'] = True
                    try:
                        os.killpg(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    code = child.wait(timeout=5)
                cleanup['orphanWaits'] = reap()
                raise
            finally:
                terminal = dict(pid=pid, returncode=code, expectedExit=cfg['expectedExit'],
                                cleanup=cleanup, argv=cfg['argv'])
                put(directory/'terminal.json', terminal)
                state['stages'].append(dict(name=name, **terminal))
        assert code == cfg['expectedExit'], (name, code)
        try:
            os.killpg(pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise RuntimeError('owned group survives stage exit')
        verify(plan)
        assert time.monotonic_ns() < deadline
        print(json.dumps(dict(stage=name, returncode=code)), flush=True)

    def artifact(name, key, target_name):
        found = []
        for line in (base/name/'stdout').read_text().splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get('reason') == 'compiler-artifact' and row.get('executable') and row['target']['name'] == target_name:
                found.append(row)
        assert len(found) == 1, (name, len(found))
        row = found[0]; path = Path(row['executable'])
        assert path.is_file() and base in path.parents
        value = dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size,
                     target=row['target'], profile=row['profile'])
        artifacts[key] = value; put(base/name/'artifact.json', value)

    try:
        stage('library_list')
        stage('library_complement')
        stage('diagnostic_build'); artifact('diagnostic_build', 'diagnostic', 'rook2-diag')
        assert artifacts['diagnostic']['path'] == plan['diagnosticImage']
        stage('diagnostic_tests'); artifact('diagnostic_tests', 'diagnosticTests', 'rook2-diag')
        stage('development_tests'); artifact('development_tests', 'developmentTests', 'rook2-dev')
        put(base/'artifacts.json', artifacts)
        stage('fixtures')
        stage('independent')
        assert read(base/'independent-reconciliation.json')['pass']
        assert time.monotonic_ns() < deadline
        state['complete'] = True
    except BaseException as error:
        state['failure'] = repr(error)
        with (base/'lane-error.txt').open('x') as stream:
            stream.write(traceback.format_exc())
    finally:
        survivors = []
        for pgid in state['ownedGroups']:
            try:
                os.killpg(pgid, 0); survivors.append(pgid)
            except ProcessLookupError:
                pass
        state['forcedCleanupGroups'] = list(survivors)
        for pgid in survivors:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        state['orphanWaits'] = reap(); until = time.monotonic()+5
        while survivors and time.monotonic() < until:
            state['orphanWaits'] += reap(); remaining = []
            for pgid in survivors:
                try:
                    os.killpg(pgid, 0); remaining.append(pgid)
                except ProcessLookupError:
                    pass
            survivors = remaining
            if survivors:
                time.sleep(.05)
        state.update(allOwnedGroupsTerminal=not survivors,
                     elapsedResourceLimitNs=time.monotonic_ns()-started)
        state['deadlineSatisfied'] = state['elapsedResourceLimitNs'] < plan['aggregateSeconds']*10**9
        put(base/'lane-outcome.json', state); print(json.dumps(state), flush=True)
    return 0 if state['complete'] and state['allOwnedGroupsTerminal'] and state['deadlineSatisfied'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
