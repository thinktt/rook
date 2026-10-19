#!/usr/bin/env python3
"""Verify all original combined training/profile/source inputs without engine runs."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import subprocess

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "weighted-bound-cache-pgo-training-20261019-01"
ROOT = HERE.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/legolas/rook2/evidence/weighted-bound-cache-pgo-preparation-20261019-01')
from guard import require_clearance,terminal,check_inputs,check_merge_tool,run
sys.path.insert(0,'/home/legolas/rook2-work/imp2-weighted-bound-cache-20261019-01/tools')
from build import source_snapshot,tool_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    require_clearance()
    check_inputs()
    check_merge_tool()
    terminal(OUT/'tool-terminal.json')
    training = load(OUT/'training.json')
    replay = load(OUT/'replay.json')
    build_path = ROOT/'evidence/weighted-bound-cache-pgo-instrumented-build-20261019-01/receipt.json'
    build = load(build_path)
    assert training['complete'] and training['schema'] == 'rook2-pgo-training-v1'
    assert len(training['raw_profiles_sha256']) == 54
    assert set(training['raw_profiles_sha256']) == {str(p) for p in (OUT/'raw').glob('*.profraw')}
    assert all(sha(Path(p)) == h for p, h in training['raw_profiles_sha256'].items())
    workloads = load(Path('/home/legolas/king-spec/conformance/profiling/workloads.json'))
    assert replay['status'] == 'pass' and len(replay['results']) == 54
    assert replay['selectedCases'] == [c['id'] for c in workloads['cases']]
    assert len({row['pid'] for row in replay['results']})==54
    assert {int(Path(path).stem.rsplit('-',1)[1]) for path in training['raw_profiles_sha256']}=={row['pid'] for row in replay['results']}
    for row in replay['results']:
        assert row['command']==['/usr/bin/taskset','-c','14',str(build_path.parent/'rook2-exact'),'--work-clock=kingwcr','--work-clock-post=work']
        assert row['status']=='pass' and row['complete'] and not row['truncated']
        assert row['exit']=={'code':0,'signal':None} and row['error'] is None and row['stderr']==''
        assert row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
    assert not (OUT/'replay.stderr').stat().st_size
    for filename, key in [('replay.json', 'replay_sha256'), ('launch.json', 'launch_sha256'), ('../weighted-bound-cache-pgo-preparation-20261019-01/train.py', 'driver_sha256'),
                          ('merged.profdata', 'profile_sha256'), ('merged.profdata.gz', 'profile_archive_sha256')]:
        assert sha(OUT/filename) == training[key]
    assert gzip.decompress((OUT/'merged.profdata.gz').read_bytes()) == (OUT/'merged.profdata').read_bytes()
    assert all(sha(Path(p)) == h for p, h in training['input_sha256'].items())
    assert sha(build_path) == training['instrumented_build_receipt']['sha256']
    assert sha(build_path.parent/'rook2-exact') == training['instrumented_engine_sha256'] == build['binary_output']['sha256']
    assert training['engine_source_sha256'] == build['source_sha256_before'] == source_snapshot(Path('/home/legolas/rook2-work/imp2-weighted-bound-cache-20261019-01'))
    assert sha(Path('/usr/bin/llvm-profdata-19').resolve()) == training['merge_tool_sha256']
    terminal_receipt = load(OUT/'tool-terminal.json')
    assert terminal_receipt['exit_code'] == 0
    assert all(sha(Path(path))==h for path,h in load(OUT/'input-closure.json').items())
    assert tool_snapshot(Path('/home/legolas/rook2-work/imp2-weighted-bound-cache-20261019-01'))==load(HERE/'plan.json')['tool_source_sha256']==build['tool_sha256_before']==build['tool_sha256_after']
    # Reuse the accepted raw protocol model and released original checker on
    # training only; post-use54/wire is deliberately gated after the CPU pilot.
    from raw_model import replay as verify_raw_replay
    verify_raw_replay(OUT/'replay.json',build_path.parent/'rook2-exact',True,OUT/'raw-original54')
    run(['/usr/bin/node',str(HERE/'recheck.mjs'),str(OUT/'replay.json')],OUT/'original-checkReplay')
    original=load(OUT/'original-checkReplay.stdout')
    assert original==dict(offlineOnly=True,originalCheckReplayCount=54)
    merged=OUT/'independently-merged.profdata';assert not merged.exists()
    command=['/usr/bin/llvm-profdata-19','merge','-o',str(merged),*sorted(training['raw_profiles_sha256'])]
    with (OUT/'independent-merge.stdout').open('xb') as a,(OUT/'independent-merge.stderr').open('xb') as b:
        result=subprocess.run(command,stdout=a,stderr=b)
    write('independent-merge-child-terminal.json',dict(actual_child_return_observed=True,exit_code=result.returncode,command=command))
    assert result.returncode==0 and not (OUT/'independent-merge.stderr').stat().st_size
    assert merged.read_bytes()==(OUT/'merged.profdata').read_bytes(),'independent remerge differs'
    verification = dict(complete=True, independent_remerge_byte_identical=True, independent_remerge_exit_code=result.returncode, independent_remerge_command=command, independent_profile_sha256=sha(merged), strict_replays=54, original_checkReplay_count=54, raw_training_protocol_cases=54, raw_profiles_independently_hashed=54,
          merged_profile_sha256=training['profile_sha256'], training_record_sha256=sha(OUT/'training.json'),
          driver_terminal_sha256=sha(OUT/'tool-terminal.json'), verifier_sha256=sha(Path(__file__)),
          scope='Own exact weighted-bound-cache candidate compiler training and independent raw/PID/profile remerge only; no production timing interpretation')
    check_inputs()
    write('verification.json', verification)
    print(json.dumps(verification))


if __name__ == '__main__':
    main()
