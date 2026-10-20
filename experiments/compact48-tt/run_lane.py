#!/usr/bin/env python3
"""One finite native lane. First tests start its immutable1800s monotonic clock."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

B = Path('/home/legolas/rook2-experiments/compact48-tt-20261020-01')
W = B / 'worktree'
R = Path('/home/legolas/rook2')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
STAGE_SECONDS = dict(tests=240, instrumented=240, train=600, verify=120,
                     use=240, capture=90, screen=600, reconcile=120)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def stat(pid):
    try:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        return fields[0], fields[19]
    except (FileNotFoundError, ProcessLookupError):
        return None


def discover(pid, owned):
    state = stat(pid)
    if state is None:
        return
    owned.setdefault(pid, state[1])
    try:
        children = Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
    except (FileNotFoundError, ProcessLookupError):
        children = []
    for child in children:
        discover(int(child), owned)


def live(owned):
    return [pid for pid, start in owned.items()
            if (s := stat(pid)) is not None and s[1] == start and s[0] != 'Z']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=STAGE_SECONDS)
    stage = parser.parse_args().stage
    assert os.sched_getaffinity(0) == H
    assert os.environ.get('TMPDIR') == '/home/legolas/rook2-build-tmp'
    for k in ['LLVM_PROFILE_FILE', 'LD_PRELOAD', 'LD_LIBRARY_PATH', 'NODE_OPTIONS']:
        assert not os.environ.get(k), k
    resources = json.loads((B / 'resources.json').read_text())
    assert resources['stage_seconds'] == STAGE_SECONDS
    assert resources['lane_seconds'] == 1800
    clock = B / 'lane-clock.json'
    if stage == 'tests':
        assert not clock.exists()
        save(clock, dict(start_monotonic=time.monotonic(), start_epoch=time.time(),
                         seconds=1800, boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                         basis='Immediately before first native Cargo test stage; no resets, gaps included'))
    c = json.loads(clock.read_text())
    assert c['boot_id'] == Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    deadline = min(c['start_monotonic'] + 1800, time.monotonic() + STAGE_SECONDS[stage])
    assert deadline > time.monotonic(), 'Elapsed native lane ceiling exhausted'
    pgo = B / 'pgo'
    if stage == 'tests':
        argv = ['/usr/bin/cargo', 'test', '--offline', '--locked', '--lib',
                '--target-dir', str(B / 'test-target'), '--', '--test-threads=4']
        cwd = W
    elif stage in ('instrumented', 'use'):
        argv = ['/usr/bin/python3', str(pgo / 'build_stage.py'), stage]
        cwd = R
    elif stage in ('train', 'verify'):
        argv = ['/usr/bin/python3', str(pgo / (stage + '.py'))]
        cwd = R
    elif stage == 'capture':
        argv = ['/usr/bin/python3', str(R / 'experiments/compact48-tt/capture.py')]
        cwd = R
    else:
        helper = 'pilot.py' if stage == 'screen' else 'reconcile_pilot.py'
        argv = ['/usr/bin/python3', str(B / 'screen' / helper), '--plan', str(B / 'screen-plan.json')]
        cwd = R
    out = B / 'stages' / stage
    out.mkdir(parents=True)
    save(out / 'command.json', dict(argv=argv, cwd=str(cwd), helper_affinity=sorted(H),
                                   stage_limit_s=STAGE_SECONDS[stage], remaining_lane_s=deadline-time.monotonic(),
                                   resources_sha256=sha(B/'resources.json'), clock_sha256=sha(clock)))

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))
        resource.setrlimit(resource.RLIMIT_FSIZE, (256 * 1024**2, 256 * 1024**2))

    owned = {}
    failure = None
    with (out / 'stdout').open('xb') as stdout, (out / 'stderr').open('xb') as stderr:
        child = subprocess.Popen(argv, cwd=cwd, stdout=stdout, stderr=stderr,
                                 start_new_session=True, preexec_fn=limits)
        try:
            while child.poll() is None:
                discover(child.pid, owned)
                if time.monotonic() >= deadline:
                    failure = 'stage-or-whole-lane-deadline'
                if max((out/'stdout').stat().st_size, (out/'stderr').stat().st_size) > 8*1024**2:
                    failure = 'outer-stream-cap'
                if failure:
                    break
                time.sleep(.05)
        except BaseException as error:
            failure = repr(error)
        if failure:
            discover(child.pid, owned)
            for sig in (signal.SIGTERM, signal.SIGKILL):
                for pid in reversed(live(owned)):
                    try:
                        os.kill(pid, sig)
                    except ProcessLookupError:
                        pass
                try:
                    child.wait(timeout=1 if sig == signal.SIGTERM else 4)
                except subprocess.TimeoutExpired:
                    pass
            child.wait(timeout=1)
        else:
            child.wait(timeout=1)
    remaining = live(owned)
    if remaining:
        failure = failure or 'observed-owned-process-still-live'
    if time.monotonic() > c['start_monotonic']+1800:
        failure = failure or 'whole-lane-ceiling-exceeded'
    result = dict(stage=stage, actual_child_return_observed=True, exit_code=child.returncode,
                  failure=failure, owned_remaining=remaining, observed_owned_pids=sorted(owned),
                  elapsed_lane_s=time.monotonic()-c['start_monotonic'],
                  scope='Known observed child tree, PID-start checked; original API/comparator owns detached native cleanup')
    save(out / 'child-terminal.json', result)
    print(json.dumps(result), flush=True)
    print((out/'stdout').read_text()[-2200:], flush=True)
    print((out/'stderr').read_text()[-1000:], flush=True)
    if child.returncode or failure:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
