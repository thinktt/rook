#!/usr/bin/env python3
"""Bounded literal ordinary controls derived from KING-XBOARD-ORDINARY.

This checks additional transport edges; it is not a complete wire qualification.
"""
import hashlib
import json
from pathlib import Path
import subprocess

engine = Path('/home/legolas/rook2/evidence/live-wire-build-20261018-frozen/rook2-exact')
out = Path(__file__).parent
book = ' This engine does not have a book.\n \n Okay?\n\n'
cases = [
    ('silent-eof', '', '', 0),
    ('silent-crlf-quit', '\t xboard \t\r\n \t\r\nquit\r\n', '', 0),
    ('book-illegal-unknown-result', 'new\nforce\nresult 1-0 {ASCII comment}\n\tbk\r\ne2e5\nprotover 2\nping 12\npong 12\nquit\n',
     book + 'Illegal move: e2e5\nError (unknown command): protover\nError (unknown command): ping\nError (unknown command): pong\n', 0),
    ('parameter-storage-order', 'cm_parm opk=+0007 opk default opk md=+0001 md tts=00065536 tts xyz\nquit\n',
     'cm_parm opk=7 opk=7 default opk=7 md=1 md=1 tts=65536 tts=65536 xyz=?\n', 0),
    ('forty-tokens', 'cm_parm' + ' xyz' * 39 + '\nquit\n', 'cm_parm' + ' xyz=?' * 39 + '\n', 0),
    ('maximum-lf-record', 'z' * 1022 + '\n', 'Error (unknown command): ' + 'z' * 1022 + '\n', 0),
    ('maximum-crlf-record', 'z' * 1021 + '\r\n', 'Error (unknown command): ' + 'z' * 1021 + '\n', 0),
    ('mate-fatal-go', 'post\nsetboard 7k/6Q1/5K2/8/8/8/8/8 b - - 0 1\ngo\nping 1\n', '', 1),
    ('stalemate-fatal-go', 'post\nsetboard 7k/5Q2/5K2/8/8/8/8/8 b - - 0 1\ngo\nping 1\n', '', 1),
    ('king-victim-fatal-go', 'force\npost\nsetboard 8/8/8/3Pk3/8/8/8/K7 w - e6 0 1\nd5e6\ngo\nping 1\n', '', 1),
]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
report = dict(schema='rook2-literal-wire-controls-v1', engine=str(engine),
              engine_sha256_before=sha(engine), checker_sha256=sha(Path(__file__)),
              timeout_seconds_per_process=5, results=[])
for name, input_text, expected, code in cases:
    args = ['--diagnostic-seed-command'] if 'fatal' in name else []
    row = dict(name=name, args=args, input=input_text, expected_stdout=expected,
               expected_stderr='', expected_exit_code=code)
    try:
        process = subprocess.run([str(engine), *args], input=input_text.encode('ascii'),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        row.update(stdout=process.stdout.decode('ascii'), stderr=process.stderr.decode('ascii'),
                   exit_code=process.returncode)
        row['pass'] = (row['stdout'] == expected and row['stderr'] == '' and process.returncode == code)
    except Exception as error:
        row.update(failure=str(error), pass_=False)
        row['pass'] = False
    report['results'].append(row)
    if not row['pass']:
        break
report['engine_sha256_after'] = sha(engine)
report['pass'] = (len(report['results']) == len(cases) and all(r['pass'] for r in report['results'])
                  and report['engine_sha256_before'] == report['engine_sha256_after'])
(out / 'wire-controls.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(passed=report['pass'], cases=len(report['results']))))
raise SystemExit(0 if report['pass'] else 1)
