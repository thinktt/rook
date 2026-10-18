#!/usr/bin/env python3
"""Regress the isolated forced-fresh observer generic artifact, without timing claims."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BUILD = ROOT/'evidence/full-fresh-build-20261018'
SOURCE = Path('/tmp/imp2-full-fresh-proposal-20261018-92x348cj')
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def run(command, stem):
    out, err = OUT/(stem+'.stdout'), OUT/(stem+'.stderr')
    with out.open('xb') as stdout, err.open('xb') as stderr:
        result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
    return dict(command=command, exit_code=result.returncode, stdout_sha256=sha(out), stderr_sha256=sha(err))


def main():
    build = json.loads((BUILD/'receipt.json').read_text())
    native = json.loads((ROOT/'evidence/full-fresh-preparation-20261018/native-verification.json').read_text())
    assert native['complete'] and native['inputs_stable'] and native['units']['rook2']['passed'] == 135
    diagnostic = ROOT/'evidence/diagnostic-full-fresh-20261018'
    assert json.loads((diagnostic/'tool-terminal.json').read_text())['exit_code'] == 0
    component = json.loads((diagnostic/'identity.json').read_text())
    assert component['cases'] == 4637 and component['units'] == 92
    assert component['native_build_reference_sha256'] == sha(BUILD/'receipt.json')
    before = source_snapshot(SOURCE)
    assert before == build['source_sha256_before'] == build['source_sha256_after']
    engine = BUILD/'rook2-exact'
    assert engine.is_file(), 'Exact image was frozen at actual build terminal'
    identity = sha(engine)
    assert identity == build['binary_output']['sha256']
    warnings = (BUILD/'build.stderr').read_text()
    assert 'no profile data available for function' not in warnings and 'profile data may be out of date' not in warnings
    archive = run([sys.executable,str(ROOT/'tools/archive_build.py'),str(BUILD)], 'archive')
    assert archive['exit_code'] == 0
    replay = run(['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--',str(engine)], 'profile-all')
    report = json.loads((OUT/'profile-all.stdout').read_text())
    assert replay['exit_code'] == 0 and report['status'] == 'pass' and len(report['results']) == 54
    assert not (OUT/'profile-all.stderr').stat().st_size
    wire_out = ROOT/'evidence/full-fresh-interruption-wire-20261018'
    wire = run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(engine),'--output',str(wire_out)], 'wire')
    receipt = json.loads((wire_out/'receipt.json').read_text())
    assert wire['exit_code'] == 0 and receipt['pass'] and len(receipt['results']) == 8
    assert receipt['engine_sha256_before'] == receipt['engine_sha256_after'] == identity
    assert before == source_snapshot(SOURCE) and sha(engine) == identity
    write('identity.json', dict(status='all54-strict-replays-and-eight-interruption-fixtures-pass',
          native_artifact_sha256=identity, build_receipt_sha256=sha(BUILD/'receipt.json'),
          replay_sha256=sha(OUT/'profile-all.stdout'), missing_function_warnings=0,
          wire_receipt_sha256=sha(wire_out/'receipt.json'), source_before=before, source_after=source_snapshot(SOURCE),
          stages=dict(archive=archive, replay=replay, wire=wire), driver_sha256=sha(Path(__file__)),
          scope='Isolated81-operation forced-fresh observer generic regression; no own-PGO, timing, gameplay or final qualification claim'))
    print(json.dumps(dict(complete=True, native_artifact_sha256=identity, strict_replays=54, interruption_fixtures=8)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
