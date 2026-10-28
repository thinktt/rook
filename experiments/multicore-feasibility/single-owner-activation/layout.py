#!/usr/bin/env python3
"""One opt-in cold projection from the actual production colors3 allocation.

Importing and audit_result start no process. main executes one configured3
candidate with both hooks requested and exits after its parked-instance JSON.
No search/protocol input, binutils, allocator projection or per-life query.
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
from common import CONTROL_RAW, DEFAULT_CRATE, HELPERS, image_layout, read, sha, snapshot, write

SCHEMA = 'rook2-single-owner-activation-layout-admission-v1'
OPTIONS = ['--threads=3', '--owner-local-inventory', '--q-owner-local-inventory',
    '--inspect-color-layout']
REGIONS = ['request', 'packet', 'white', 'black', 'lifecycle', 'latch', 'wait', 'control']
CAP_SECONDS = 120
RAW_CAP = 1024*1024


def integer(value, minimum=0):
    assert type(value) is int and value >= minimum, value
    return value


def admit_projection(value):
    assert value['schema'] == 'rook2-single-owner-activation-layout-v1'
    assert value['layoutDesign'] == 'single-owner'
    assert value['testBuild'] is False and value['parked'] is True
    shared = value['shared']
    size = integer(shared['size'], 1)
    assert size % 64 == 0 and shared['align'] == 64 and shared['addressMod64'] == 0
    rows = value['regions']
    assert [row['name'] for row in rows] == REGIONS
    previous_end = 0
    by = {}
    for row in rows:
        offset, span = integer(row['offset']), integer(row['size'], 1)
        assert row['align'] == 64 and offset % 64 == span % 64 == 0
        assert previous_end <= offset and offset+span <= size
        previous_end = offset+span
        by[row['name']] = row
    for name in ['request', 'white', 'black', 'lifecycle', 'latch', 'wait']:
        assert by[name]['size'] == 64
    types = value['types']
    for name in ['packetBytes', 'sideOutputBytes', 'controlMutexBytes',
                 'lifecycleBytes', 'waitBytes', 'cellsBytes', 'ownerStateBytes', 'ownerFlightBytes']:
        integer(types[name], 1)
    assert by['packet']['size'] == (types['packetBytes']+63)//64*64
    assert by['control']['size'] == (types['controlMutexBytes']+63)//64*64
    assert types['lifecycleBytes'] == types['waitBytes'] == 64
    assert types['sideOutputBytes'] == 56
    assert len(value['slots']) == 2
    for slot, name in zip(value['slots'], ['white', 'black']):
        assert slot['name'] == name
        offset = integer(slot['offset'])
        assert offset == by[name]['offset'] and offset % 64 == 0
        assert slot['size'] == slot['align'] == 64
        assert slot['outputBytes'] == 56 and slot['doneBytes'] == 8
        output, done = integer(slot['outputOffset']), integer(slot['doneOffset'])
        # All offsets are relative to actual Shared, including member offsets.
        assert offset <= output and output+56 <= offset+64
        assert offset <= done and done+8 <= offset+64
        assert output+56 <= done or done+8 <= output
        assert output//64 == (output+55)//64 == done//64 == (done+7)//64
    owner = value['ownerState']
    assert integer(owner['size'], 1) == types['ownerStateBytes']
    alignment = integer(owner['align'], 1)
    assert alignment & (alignment-1) == 0 and owner['size'] % alignment == 0
    assert types['ownerFlightBytes'] <= owner['size']
    # Compare the actual selected transport to the preserved writer production
    # projection. Owner-local storage and cold Control may change size; retained
    # request/packet/output regions and output/done member offsets may not drift.
    old = read(CONTROL_RAW/'layout/stdout.raw')
    assert old['schema'] == 'rook2-writer-regions-layout-v1' and old['layoutDesign'] == 'eight64'
    prior = {row['name']: row for row in old['regions']}
    for name in ['request', 'packet', 'white', 'black']:
        assert by[name] == prior[name], name
    assert value['slots'] == old['slots']
    for name in ['packetBytes', 'sideOutputBytes', 'cellsBytes']:
        assert types[name] == old['types'][name], name
    return value


def input_paths(image, crate, source):
    paths = [Path(__file__).resolve(), Path(__file__).with_name('common.py').resolve(), image,
        CONTROL_RAW/'layout/stdout.raw', CONTROL_RAW/'layout/result.json']
    paths += [Path(function.__code__.co_filename).resolve()
              for function in [image_layout, read, sha, snapshot, write]]
    paths += [crate/name for name in source]
    return sorted(set(paths))


def cold_process(image, out, deadline_ns):
    started = time.monotonic_ns()
    status = dict(argv=[str(image), *OPTIONS], nativePid=None, exit=None, signal=None,
        joined=False, pidAbsentAfterReap=False, failure=None, cleanupSignals=[],
        inheritedMask=sorted(os.sched_getaffinity(0)), startedMonotonicNs=started,
        deadlineMonotonicNs=deadline_ns)
    child = None
    env = {key: value for key, value in os.environ.items()
           if not key.startswith('ROOK2_') and key != 'LLVM_PROFILE_FILE'}
    try:
        assert time.monotonic_ns() < deadline_ns, 'layout deadline before process launch'
        with (out/'stdout.raw').open('xb') as stdout, (out/'stderr.raw').open('xb') as stderr:
            child = subprocess.Popen(status['argv'], stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, env=env, start_new_session=True)
            status['nativePid'] = child.pid
            while child.poll() is None:
                assert time.monotonic_ns() < deadline_ns, 'layout process deadline'
                assert (out/'stdout.raw').stat().st_size <= RAW_CAP
                assert (out/'stderr.raw').stat().st_size <= RAW_CAP
                time.sleep(.02)
            status.update(exit=child.returncode,
                signal=-child.returncode if child.returncode < 0 else None, joined=True)
            assert child.returncode == 0
            assert (out/'stderr.raw').stat().st_size == 0
            assert 0 < (out/'stdout.raw').stat().st_size <= RAW_CAP
            assert not Path(f'/proc/{child.pid}').exists()
            status['pidAbsentAfterReap'] = True
    except BaseException as error:
        status['failure'] = repr(error)
        if child is not None and child.poll() is None:
            for signum in [signal.SIGTERM, signal.SIGKILL]:
                try:
                    os.killpg(child.pid, signum)
                    status['cleanupSignals'].append(int(signum))
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=5)
                    break
                except subprocess.TimeoutExpired:
                    if signum == signal.SIGKILL:
                        raise
        if child is not None:
            status.update(exit=child.returncode,
                signal=-child.returncode if child.returncode is not None and child.returncode < 0 else None,
                joined=child.returncode is not None)
        raise
    finally:
        status['endedMonotonicNs'] = time.monotonic_ns()
        status['elapsedNs'] = status['endedMonotonicNs']-started
        for name in ['stdout.raw', 'stderr.raw']:
            path = out/name
            if path.exists():
                status[name] = dict(sha256=sha(path), bytes=path.stat().st_size)
        write(out/'status.json', status)
    return status


def audit_result(path, engine, crate):
    """Read-only admission: saved source/image, real geometry, raw and reap."""
    path, engine, crate = Path(path).resolve(), Path(engine).resolve(), Path(crate).resolve()
    value = read(path)
    assert value['schema'] == SCHEMA and value['complete'] is True
    assert value['image'] == image_layout(engine) and value['crate'] == str(crate)
    source = snapshot(crate)
    assert len(source) >= 68 and value['sourceSha256'] == source
    assert value['requestedThreads'] == value['configuredThreads'] == 3
    assert value['argv'] == [str(engine), *OPTIONS]
    assert value['joined'] is True
    assert value['projection'] == admit_projection(read(path.parent/'stdout.raw'))
    assert set(value['inputSha256']) == {str(item) for item in input_paths(engine, crate, source)}
    for name, digest in value['inputSha256'].items():
        assert sha(name) == digest, name
    assert set(value['rawSha256']) == {'stdout.raw', 'stderr.raw', 'status.json'}
    for name, digest in value['rawSha256'].items():
        raw = path.parent/name
        assert raw.is_file() and not raw.is_symlink() and sha(raw) == digest, name
    assert (path.parent/'stderr.raw').stat().st_size == 0
    status = read(path.parent/'status.json')
    assert value['status'] == status and status['argv'] == value['argv']
    assert status['exit'] == 0 and status['signal'] is None and status['failure'] is None
    assert status['cleanupSignals'] == [] and status['joined'] is status['pidAbsentAfterReap'] is True
    assert status['inheritedMask'] == sorted(HELPERS)
    assert value['nativePid'] == integer(status['nativePid'], 1)
    for name in ['stdout.raw', 'stderr.raw']:
        assert status[name] == dict(sha256=sha(path.parent/name), bytes=(path.parent/name).stat().st_size)
        assert status[name]['bytes'] <= RAW_CAP
    start, end = value['startedMonotonicNs'], value['endedMonotonicNs']
    assert value['elapsedNs'] == end-start > 0
    assert end < value['deadlineMonotonicNs'] == start+CAP_SECONDS*10**9
    assert start <= status['startedMonotonicNs'] < status['endedMonotonicNs'] <= end
    assert status['endedMonotonicNs'] < status['deadlineMonotonicNs'] <= value['deadlineMonotonicNs']
    assert status['elapsedNs'] == status['endedMonotonicNs']-status['startedMonotonicNs'] > 0
    return value


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image, out = args.engine.resolve(), args.output.resolve()
    out.mkdir()
    started = time.monotonic_ns()
    deadline = started+CAP_SECONDS*10**9
    result = dict(schema=SCHEMA, complete=False, startedMonotonicNs=started,
        deadlineMonotonicNs=deadline)
    try:
        assert set(os.sched_getaffinity(0)) == HELPERS
        crate = DEFAULT_CRATE.resolve()
        source = snapshot(crate)
        assert len(source) >= 68
        inputs = input_paths(image, crate, source)
        result.update(image=image_layout(image), crate=str(crate), sourceSha256=source,
            inputSha256={str(path): sha(path) for path in inputs})
        status = cold_process(image, out, deadline-10*10**9)
        projection = admit_projection(read(out/'stdout.raw'))
        # Only an actual configured3 worker can emit the parked production
        # projection: mode1/2 return an error in evaluator's cold forwarding API.
        result.update(projection=projection, status=status, nativePid=status['nativePid'],
            argv=status['argv'], requestedThreads=3, configuredThreads=3, joined=True,
            configurationBasis='Exact --threads=3 plus both requested hook flags; successful parked production colors-worker projection, unavailable in configured1/2. One cold invocation, no protocol input.')
        assert all(sha(path) == digest for path, digest in result['inputSha256'].items())
        result.update(complete=True, endedMonotonicNs=time.monotonic_ns(),
            rawSha256={name: sha(out/name) for name in ['stdout.raw', 'stderr.raw', 'status.json']})
        result['elapsedNs'] = result['endedMonotonicNs']-started
        assert result['endedMonotonicNs'] < deadline
        write(out/'result.json', result)
        audit_result(out/'result.json', image, crate)
        assert time.monotonic_ns() < deadline, 'layout final audit deadline'
    except BaseException as error:
        result.update(complete=False, failure=repr(error), endedMonotonicNs=time.monotonic_ns())
        result['elapsedNs'] = result['endedMonotonicNs']-started
        write(out/'failure.json', result)
        raise
    print(json.dumps(dict(complete=True, result=str(out/'result.json'),
        sharedBytes=projection['shared']['size'], sharedAlign=projection['shared']['align'],
        ownerStateBytes=projection['ownerState']['size'], ownerStateAlign=projection['ownerState']['align'])))


if __name__ == '__main__':
    main()
