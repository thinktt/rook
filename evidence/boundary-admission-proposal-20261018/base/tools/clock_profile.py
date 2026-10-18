#!/usr/bin/env python3
"""Transparent ordinary-stream launcher for local gprofng clock diagnosis.

This is not an acceptance CPU/PMU collector. It routes collector messages to
separate files, preserves engine stdin/stdout/stderr and execs without a relay
process. The standard profiler may still impose its own runtime overhead.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--experiment', type=Path, required=True)
    args, engine_args = parser.parse_known_args()
    engine = args.engine.resolve()
    experiment = args.experiment.resolve()
    if experiment.exists():
        parser.error('experiment must be fresh')
    experiment.parent.mkdir(exist_ok=True)
    stdout_path = Path(str(experiment) + '.collector.stdout')
    stderr_path = Path(str(experiment) + '.collector.stderr')
    metadata_path = Path(str(experiment) + '.launcher.json')
    for path in (stdout_path, stderr_path, metadata_path):
        if path.exists():
            parser.error(f'output already exists: {path}')
    command = ['/usr/bin/taskset', '-c', '14', '/usr/bin/gprofng', 'collect', 'app',
               '-p', '1', '-F', 'on', '-a', 'off', '-o', str(experiment),
               '/bin/sh', '-c',
               'exec "$0" "$@" >&"$ROOK2_CLOCK_STDOUT" 2>&"$ROOK2_CLOCK_STDERR"',
               str(engine), *engine_args]
    metadata = dict(schema='rook2-clock-profile-launch-v1', engine=str(engine),
                    engine_sha256=sha(engine), launcher_sha256=sha(Path(__file__)),
                    command=command, inherited_affinity=sorted(os.sched_getaffinity(0)),
                    engine_cpu=14, sampling_interval_ms=1, follows_exec=True, hardware_counters=False,
                    acceptance_measurement=False,
                    tools={p: sha(Path(p)) for p in ('/usr/bin/gprofng', '/usr/bin/taskset', '/bin/sh')})
    with metadata_path.open('x') as stream:
        json.dump(metadata, stream, indent=2)
        stream.write('\n')
    # The same open pipe descriptions remain live under their new descriptor
    # numbers. The shell redirects only the native child's standard streams.
    output_fd, error_fd = os.dup(1), os.dup(2)
    os.set_inheritable(output_fd, True)
    os.set_inheritable(error_fd, True)
    with stdout_path.open('xb') as stream:
        os.dup2(stream.fileno(), 1)
    with stderr_path.open('xb') as stream:
        os.dup2(stream.fileno(), 2)
    # A declared minimal environment keeps unrelated credentials out of
    # profiler metadata and does not change any engine behavioral input.
    environment = {'PATH': '/usr/bin:/bin', 'HOME': '/home/legolas',
                   'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
                   'ROOK2_CLOCK_STDOUT': str(output_fd), 'ROOK2_CLOCK_STDERR': str(error_fd)}
    os.execve(command[0], command, environment)


if __name__ == '__main__':
    main()
