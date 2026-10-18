#!/usr/bin/env python3
"""Verify all original combined training/profile/source inputs without engine runs."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    training = load(OUT/'training.json')
    replay = load(OUT/'replay.json')
    build_path = ROOT/'evidence/production-activity-specialization-instrumented-build-20261018/receipt.json'
    build = load(build_path)
    assert training['complete'] and training['schema'] == 'rook2-pgo-training-v1'
    assert len(training['raw_profiles_sha256']) == 54
    assert set(training['raw_profiles_sha256']) == {str(p) for p in (OUT/'raw').glob('*.profraw')}
    assert all(sha(Path(p)) == h for p, h in training['raw_profiles_sha256'].items())
    workloads = load(Path('/home/legolas/king-spec/conformance/profiling/workloads.json'))
    assert replay['status'] == 'pass' and len(replay['results']) == 54
    assert replay['selectedCases'] == [c['id'] for c in workloads['cases']]
    assert not (OUT/'replay.stderr').stat().st_size
    for filename, key in [('replay.json', 'replay_sha256'), ('launch.json', 'launch_sha256'), ('train.py', 'driver_sha256'),
                          ('merged.profdata', 'profile_sha256'), ('merged.profdata.gz', 'profile_archive_sha256')]:
        assert sha(OUT/filename) == training[key]
    assert gzip.decompress((OUT/'merged.profdata.gz').read_bytes()) == (OUT/'merged.profdata').read_bytes()
    assert all(sha(Path(p)) == h for p, h in training['input_sha256'].items())
    assert sha(build_path) == training['instrumented_build_receipt']['sha256']
    assert sha(build_path.parent/'rook2-exact') == training['instrumented_engine_sha256'] == build['binary_output']['sha256']
    assert training['engine_source_sha256'] == build['source_sha256_before'] == source_snapshot(ROOT)
    assert sha(Path('/usr/bin/llvm-profdata-19').resolve()) == training['merge_tool_sha256']
    terminal = load(OUT/'tool-terminal.json')
    assert terminal['exit_code'] == 0
    verification = dict(complete=True, strict_replays=54, raw_profiles_independently_hashed=54,
          merged_profile_sha256=training['profile_sha256'], training_record_sha256=sha(OUT/'training.json'),
          driver_terminal_sha256=sha(OUT/'tool-terminal.json'), verifier_sha256=sha(Path(__file__)),
          scope='Own static-kind activity compiler training only; no production timing interpretation')
    write('verification.json', verification)
    print(json.dumps(verification))


if __name__ == '__main__':
    main()
