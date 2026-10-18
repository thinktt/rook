#!/usr/bin/env python3
"""One unchanged public54 replay, followed by a fully bound LLVM profile merge."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BUILD = ROOT / 'evidence/pgo-eval-geometry-instrumented-build-20261018'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
sys.path.insert(0, str(ROOT / 'tools'))
from build import source_snapshot, cargo_configs


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    build = json.loads((BUILD / 'receipt.json').read_text())
    assert build['outcome'] == 'build-succeeded-with-stable-input-snapshot'
    assert build['pgo']['mode'] == 'instrumented'
    assert build['source_sha256_before'] == source_snapshot(ROOT)
    assert build['cargo_config_sha256_before'] == cargo_configs(ROOT)
    engine = BUILD / 'rook2-exact'
    assert sha(engine) == build['binary_output']['sha256']
    assert not list((OUT / 'raw').iterdir())
    inputs = [SPEC / name for name in ['workloads.json', 'replay-oracle.json', 'replay-check.mjs']]
    before = {str(p):sha(p) for p in inputs}
    plan = json.loads((OUT / 'plan.json').read_text())
    assert before == plan['input_sha256']
    command = ['/usr/bin/node', str(SPEC / 'replay-check.mjs'), '--',
               '/usr/bin/taskset', '-c', '14', str(engine)]
    env = dict(os.environ, LLVM_PROFILE_FILE=str(OUT / 'raw/native-%m-%p.profraw'))
    write('launch.json', dict(command=command, cwd=str(ROOT),
                             driver_sha256=sha(Path(__file__)),
                             profile_environment={'LLVM_PROFILE_FILE':env['LLVM_PROFILE_FILE']},
                             input_sha256=before, engine_sha256=sha(engine),
                             helper_affinity=sorted(os.sched_getaffinity(0)),
                             limits='Unmodified released checker owns case/time/stream/cleanup limits',
                             purpose='Compiler training only; timings are not production measurements'))
    with (OUT / 'replay.json').open('xb') as stdout, (OUT / 'replay.stderr').open('xb') as stderr:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    report = json.loads((OUT / 'replay.json').read_text())
    assert result.returncode == 0 and report['status'] == 'pass'
    assert len(report['results']) == 54 and not (OUT / 'replay.stderr').stat().st_size
    workloads = json.loads((SPEC / 'workloads.json').read_text())
    assert report['selectedCases'] == [c['id'] for c in workloads['cases']]
    assert sha(engine) == build['binary_output']['sha256']
    assert build['source_sha256_before'] == source_snapshot(ROOT)
    assert before == {str(p):sha(p) for p in inputs}
    raw = sorted((OUT / 'raw').glob('*.profraw'))
    assert len(raw) == 54, ('expected one unique raw image per native process', len(raw))
    raw_hashes = {str(p):sha(p) for p in raw}
    merge = ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(OUT / 'merged.profdata'), *map(str, raw)]
    with (OUT / 'merge.stdout').open('xb') as stdout, (OUT / 'merge.stderr').open('xb') as stderr:
        result = subprocess.run(merge, stdout=stdout, stderr=stderr)
    assert result.returncode == 0
    assert raw_hashes == {str(p):sha(p) for p in raw}
    profile = OUT / 'merged.profdata'
    with (OUT / 'profile-summary.stdout').open('xb') as stdout, (OUT / 'profile-summary.stderr').open('xb') as stderr:
        result = subprocess.run(['/usr/bin/llvm-profdata-19', 'show', str(profile)], stdout=stdout, stderr=stderr)
    assert result.returncode == 0
    with profile.open('rb') as source, (OUT / 'merged.profdata.gz').open('xb') as target:
        with gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0) as compressed:
            compressed.write(source.read())
    version = subprocess.run(['/usr/bin/llvm-profdata-19', '--version'], capture_output=True, text=True, check=True)
    write('training.json', dict(schema='rook2-pgo-training-v1', complete=True,
                               engine_source_sha256=source_snapshot(ROOT),
                               target_triple=build['target_triple'],
                               base_rust_flags=build['rust_flags'][:2],
                               instrumented_build_receipt=dict(path=str(BUILD/'receipt.json'),sha256=sha(BUILD/'receipt.json')),
                               instrumented_engine_sha256=sha(engine),
                               input_sha256=before, raw_profiles_sha256=raw_hashes,
                               replay_sha256=sha(OUT/'replay.json'),
                               launch_sha256=sha(OUT/'launch.json'),
                               merge_command=merge, merge_tool_sha256=sha(Path('/usr/bin/llvm-profdata-19').resolve()),
                               merge_tool_version=version.stdout,
                               profile_sha256=sha(profile), profile_archive_sha256=sha(OUT/'merged.profdata.gz'),
                               driver_sha256=sha(Path(__file__)),
                               performance='Training instrumentation only; no production CPU/PMU interpretation'))
    print(json.dumps(dict(complete=True, training='training.json', raw_profiles=len(raw), merged_profile_sha256=sha(profile))))


if __name__ == '__main__':
    main()
