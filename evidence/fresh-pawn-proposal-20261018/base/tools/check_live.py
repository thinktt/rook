#!/usr/bin/env python3
"""Replay released interruption fixtures through literal ordinary process I/O.

This is a focused wire check, not the mandatory diagnostic JSON interface.
One process per fixture retains its three ordered searches. Queued records are
written with go, then no later setup is sent until move/abort publication.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import time

HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Process:
    def __init__(self, engine, directory):
        self.child = subprocess.Popen([str(engine)], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.child.stdout, selectors.EVENT_READ, 'stdout')
        self.selector.register(self.child.stderr, selectors.EVENT_READ, 'stderr')
        self.raw = {'stdout': bytearray(), 'stderr': bytearray(), 'stdin': bytearray()}
        self.buffer = bytearray()
        self.directory = directory
        self.deadline = time.monotonic() + 120

    def send(self, records):
        data = ('\n'.join(records) + '\n').encode('ascii')
        self.raw['stdin'].extend(data)
        self.child.stdin.write(data)
        self.child.stdin.flush()

    def receive(self, deadline):
        assert time.monotonic() < min(deadline, self.deadline), 'host deadline'
        events = self.selector.select(max(0, min(deadline, self.deadline) - time.monotonic()))
        assert events, 'host deadline'
        for key, _ in events:
            data = os.read(key.fileobj.fileno(), 65536)
            if not data:
                self.selector.unregister(key.fileobj)
                continue
            self.raw[key.data].extend(data)
            assert len(self.raw[key.data]) <= 4194304, 'stream cap'
            if key.data == 'stdout':
                self.buffer.extend(data)

    def line(self):
        deadline = time.monotonic() + 30
        while b'\n' not in self.buffer:
            assert self.selector.get_map(), 'missing output record'
            self.receive(deadline)
        line, _, tail = self.buffer.partition(b'\n')
        self.buffer = bytearray(tail)
        assert b'\r' not in line and line.isascii(), 'invalid output framing'
        return line.decode('ascii')

    def finish(self):
        self.send(['quit'])
        self.child.stdin.close()
        deadline = time.monotonic() + 5
        while self.selector.get_map():
            self.receive(deadline)
        assert self.child.wait(timeout=5) == 0, 'unclean process exit'
        assert not self.buffer, 'extra/partial shutdown output'
        assert not self.raw['stderr'], 'unexpected stderr'

    def retain(self):
        if self.child.poll() is None:
            self.child.kill()
            self.child.wait(timeout=5)
        for name, data in self.raw.items():
            (self.directory / (name + '.raw')).write_bytes(data)
        self.selector.close()
        for stream in (self.child.stdin, self.child.stdout, self.child.stderr):
            stream.close()


def semantic(line):
    if line.startswith('move '):
        return {'type': 'move', 'move': line[5:]}
    if line.startswith('stat01: '):
        match = re.fullmatch(r'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?', line)
        assert match, 'invalid status record: ' + line
        cs, sid, depth, remaining, total = map(int, match.groups()[:5])
        return dict(type='status', engineCentiseconds=cs, searchId=sid,
                    depthToken=depth, remaining=remaining, total=total,
                    pv=(match[6] or '').replace('0', 'O'))
    match = re.fullmatch(r' *(-?\d+) +([+-]?\d+) +(\d+) +(\d+)(?: (.*))?', line)
    assert match, 'unexpected record: ' + line
    depth, score, cs, sid = map(int, match.groups()[:4])
    return dict(type='post', depthToken=depth, evaluation=score,
                engineCentiseconds=cs, searchId=sid,
                pv=(match[5] or '').replace('0', 'O'))


def run_case(engine, case, directory):
    directory.mkdir()
    process = Process(engine, directory)
    row = dict(id=case['id'], status='running', searches=[])
    try:
        requests = case['request']['input']['searches']
        expected = case['expected']['results']
        assert len(requests) == len(expected)
        for request, answer in zip(requests, expected):
            commands = request['commands']
            # An ordinary empty parameter query observes setup order. It changes
            # no setting and is not a new protocol handshake or engine clock.
            process.send(commands + [f"time {request['allowanceCs']}", 'cm_parm'])
            for command in commands:
                if command.startswith('cm_parm '):
                    # Released inputs use canonical decimal assignments/default.
                    assert process.line() == ' '.join(command.split()), 'setup acknowledgment'
            assert process.line() == 'cm_parm', 'setup ordering query'
            process.send(['go'] + request['queued'])
            events = []
            abort = bool(request['queued'] and request['queued'][-1] == 'force')
            for _ in range(len(answer['events'])):
                events.append(semantic(process.line()))
            if abort:
                assert process.line() == 'aborting search ...', 'missing abort record'
            assert events == answer['events'], f"semantic event mismatch: {events!r}"
            row['searches'].append(dict(status='pass', events=events, abort=abort))
        process.finish()
        row.update(status='pass', exit_code=0, complete_streams=True)
    except Exception as error:
        row.update(status='fail', failure=str(error), complete_streams=False)
    finally:
        process.retain()
        row['observed_exit_code'] = process.child.returncode
        row['raw'] = {name: dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
                      for name, data in process.raw.items()}
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.engine = args.engine.resolve()
    args.output.mkdir()
    original_affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, HELPERS & original_affinity)
    fixture = Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json')
    digest = sha(args.engine)
    report = dict(schema='rook2-live-interruption-check-v1', engine=str(args.engine),
                  engine_sha256_before=digest, fixture=str(fixture), fixture_sha256=sha(fixture),
                  checker_sha256=sha(Path(__file__)), original_affinity=sorted(original_affinity),
                  effective_affinity=sorted(os.sched_getaffinity(0)),
                  limits=dict(seconds_per_record=30, seconds_per_case=120, bytes_per_stream=4194304),
                  diagnostic_transport=False, performance_sample=False, results=[])
    try:
        for case in json.loads(fixture.read_text())['cases']:
            row = run_case(args.engine, case, args.output / case['id'])
            report['results'].append(row)
            if row['status'] != 'pass':
                break
        report['engine_sha256_after'] = sha(args.engine)
        report['pass'] = (len(report['results']) == 8 and
                          all(row['status'] == 'pass' for row in report['results']) and
                          report['engine_sha256_after'] == digest)
        (args.output / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    finally:
        os.sched_setaffinity(0, original_affinity)
    print(json.dumps(dict(output=str(args.output), passed=report['pass'], cases=len(report['results']))))
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
