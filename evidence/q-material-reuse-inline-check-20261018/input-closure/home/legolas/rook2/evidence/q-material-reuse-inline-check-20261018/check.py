#!/usr/bin/env python3
"""Regress frozen Q-only material endpoint reuse; UNTIMED housekeeping only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BUILD = ROOT/'evidence/q-material-reuse-inline-build-20261018'
SOURCE = Path('/tmp/imp2-q-material-reuse-inline79-20261018-kj58btzg')
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
    native = json.loads((ROOT/'evidence/q-material-reuse-inline-validation-20261018/native-verification.json').read_text())
    assert native['complete'] and native['inputs_stable'] and native['units']['rook2']['passed'] == 136
    assert native['units']['rook2-dev']['passed'] == 2
    for path in (BUILD/'tool-terminal.json', ROOT/'evidence/q-material-reuse-inline-validation-20261018/native-tool-terminal.json'):
        terminal=json.loads(path.read_text()); assert terminal['actual_tool_terminal_observed'] and terminal['exit_code'] == 0
    proposal=ROOT/'evidence/q-material-reuse-inline-proposal-20261018/prepared.json'
    expected=json.loads(proposal.read_text())['variant_source_sha256']
    assert source_snapshot(SOURCE)==expected
    closure_paths=[proposal, BUILD/'receipt.json', BUILD/'tool-terminal.json',
        ROOT/'evidence/q-material-reuse-inline-validation-20261018/native-verification.json',
        ROOT/'evidence/q-material-reuse-inline-validation-20261018/native-tool-terminal.json',
        ROOT/'tools/build.py',ROOT/'tools/archive_build.py',ROOT/'tools/check_live.py',Path(__file__)]
    spec=Path('/home/legolas/king-spec/conformance')
    closure_paths += [spec/'profiling'/name for name in ('replay-check.mjs','benchmark.mjs','workloads.json','replay-oracle.json')]
    closure_paths += [spec/'fixtures/interrupted-sessions-v1.json']
    closure={str(p):sha(p) for p in closure_paths}
    copy=OUT/'input-closure';copy.mkdir()
    for p in closure_paths:
        dest=copy/str(p).lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    write('input-closure.json',closure)
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
    assert len(set(row['case'] for row in report['results']))==54
    for row in report['results']:
        assert row['status']=='pass' and row['complete'] and not row['truncated']
        assert row['exit']=={'code':0,'signal':None} and row['error'] is None
        assert row['stderr']=='' and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
    wire_out = ROOT/'evidence/q-material-reuse-inline-interruption-wire-20261018'
    wire = run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(engine),'--output',str(wire_out)], 'wire')
    receipt = json.loads((wire_out/'receipt.json').read_text())
    assert wire['exit_code'] == 0 and receipt['pass'] and len(receipt['results']) == 8
    assert sum(len(r['searches']) for r in receipt['results'])==24
    assert all(r['observed_exit_code']==0 and r['complete_streams'] for r in receipt['results'])
    assert all(sha(Path(p))==h for p,h in closure.items()), 'input closure changed'
    assert receipt['engine_sha256_before'] == receipt['engine_sha256_after'] == identity
    assert before == source_snapshot(SOURCE) and sha(engine) == identity
    write('identity.json', dict(status='all54-strict-replays-and-eight-interruption-fixtures-pass',
          native_artifact_sha256=identity, build_receipt_sha256=sha(BUILD/'receipt.json'),
          replay_sha256=sha(OUT/'profile-all.stdout'), missing_function_warnings=0,
          wire_receipt_sha256=sha(wire_out/'receipt.json'), source_before=before, source_after=source_snapshot(SOURCE),
          stages=dict(archive=archive, replay=replay, wire=wire), driver_sha256=sha(Path(__file__)),
          scope='Q-only endpoint reuse exact79+three differential tests; UNTIMED housekeeping CPUs0-5,8-13; no CPU pilot/PGO/profiling/gameplay/final qualification claim'))
    print(json.dumps(dict(complete=True, native_artifact_sha256=identity, strict_replays=54, interruption_fixtures=8)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
