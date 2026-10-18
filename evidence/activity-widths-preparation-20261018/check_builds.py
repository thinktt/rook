#!/usr/bin/env python3
"""Freeze/archive both generic artifacts and regress every public54 case."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]
OUT = ROOT / 'evidence/activity-widths-check-20261018'
sys.path.insert(0, str(ROOT / 'tools'))
from build import source_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def run(command, stem):
    stdout, stderr = OUT / (stem + '.stdout'), OUT / (stem + '.stderr')
    with stdout.open('xb') as out, stderr.open('xb') as err:
        process = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err, start_new_session=True)
        try:
            process.wait(timeout=900)
        except BaseException:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            raise
    return dict(command=command, exit_code=process.returncode, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))


def main():
    OUT.mkdir()
    native = json.loads((PREP / 'native-verification.json').read_text())
    assert native['complete'] and native['inputs_stable'] and native['units']['rook2']['passed'] == 132
    oracle_path = ROOT / 'evidence/activity-widths-oracle-20261018/receipt.json'
    oracle = json.loads(oracle_path.read_text())
    assert oracle['pass'] and oracle['cases'] == 10000 and oracle['test_exit'] == 0
    assert oracle['native_source_before'] == oracle['native_source_after'] == native['source_after']
    roots = {'baseline': ROOT, 'widths': Path('/tmp/imp2-activity-widths-20261018')}
    builds = {'baseline': ROOT / 'evidence/activity-baseline-build-20261018',
              'widths': ROOT / 'evidence/activity-widths-build-20261018'}
    before = {name: source_snapshot(root) for name, root in roots.items()}
    prepared = json.loads((PREP / 'prepared.json').read_text())
    assert before['baseline'] == prepared['baseline_source_sha256']
    assert before['widths'] == prepared['variant_source_sha256'] == native['source_after']
    results = {}
    for name, directory in builds.items():
        build = json.loads((directory / 'receipt.json').read_text())
        assert build['outcome'] == 'build-succeeded-with-stable-input-snapshot'
        assert build['source_sha256_before'] == build['source_sha256_after'] == before[name]
        frozen = directory / 'rook2-exact'
        if not frozen.exists():
            with frozen.open('xb') as stream:
                stream.write(Path(build['binary_output']['path']).read_bytes())
            frozen.chmod(0o755)
        identity = sha(frozen)
        assert identity == build['binary_output']['sha256']
        archive = run([sys.executable, str(ROOT / 'tools/archive_build.py'), str(directory)], name + '-archive')
        assert archive['exit_code'] == 0
        replay = run(['/usr/bin/node', '/home/legolas/king-spec/conformance/profiling/replay-check.mjs', '--', str(frozen)], name + '-replay')
        report = json.loads((OUT / (name + '-replay.stdout')).read_text())
        assert replay['exit_code'] == 0 and report['status'] == 'pass' and len(report['results']) == 54
        assert not (OUT / (name + '-replay.stderr')).stat().st_size
        assert sha(frozen) == identity
        results[name] = dict(artifact_sha256=identity, archive=archive, replay=replay, cases=54,
                             build_receipt_sha256=sha(directory / 'receipt.json'))
        print(json.dumps(dict(variant=name, artifact_sha256=identity, strict_replays=54)), flush=True)
    after = {name: source_snapshot(root) for name, root in roots.items()}
    assert before == after
    write(OUT / 'verification.json', dict(complete=True, variants=results, source_before=before, source_after=after,
          oracle_verification_sha256=sha(oracle_path), units_verification_sha256=sha(PREP / 'native-verification.json'), driver_sha256=sha(Path(__file__)),
          scope='Generic artifact correctness regression only; no CPU or PGO benefit claim'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
