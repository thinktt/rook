#!/usr/bin/env python3
"""Read-only audit: adopt the retained08 and bind exactly one new35 continuation."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from build import HERE, ROOT, HELPERS, BASE_HELPER, FROZEN_TOOLS, read, write, sha, snapshot, baseline, admit, resolve_pinned
from collect import ACCOUNT, SPEC, CAPS, AS_BYTES, OUTPUT_BYTES, policy, materialization
from reconcile import audit_report, native_receipt

ORIGINAL = Path('/home/legolas/rook2-experiments/consumed-prefix-20261025-02')
IMAGE_SHA = '9cd791b4051632213edecbf71c519087b8b2a7f049254df050f0cf5557e91788'
NAMES = ['launch.json', 'terminal.json', 'native.json', 'stdout', 'stderr']


def audit_life(directory, step, image, chosen, hashes, policy_sha):
    options = ['--input', str(materialization(step['case'])), *chosen['driverOptions']]
    native = native_receipt(directory, image, options, hashes)
    command = [native['python_executable'], str(ACCOUNT), '--engine', str(image),
               '--record', str(directory/'native.json'), '--known-single-process', *options]
    assert read(directory/'launch.json') == dict(argv=command, nativeArgv=[str(image), *options], step=step,
        policySha256=policy_sha, addressSpaceBytes=AS_BYTES, stdoutBytes=OUTPUT_BYTES)
    terminal = read(directory/'terminal.json')
    assert terminal['pid'] == native['supervisor_pid'] and terminal['exit'] == 0 and terminal['cleanup'] is None
    assert terminal['startMonotonicNs'] <= native['start_monotonic_ns'] < native['reaped_monotonic_ns'] <= terminal['endMonotonicNs']
    assert native['wall_ns'] <= 180*10**9
    assert (directory/'stderr').read_bytes() == b'' and 0 < (directory/'stdout').stat().st_size <= OUTPUT_BYTES
    report = read(directory/'stdout'); assert report['processId'] == native['native_pid']
    summary = audit_report(report, chosen)
    row = dict(**step, directory=str(directory), nativePid=native['native_pid'], supervisorPid=native['supervisor_pid'],
        wholeCpuSeconds=native['total_cpu_s'], rssKiB=native['maxrss_linux_kib'], nativeWallNs=native['wall_ns'],
        controllerWallNs=terminal['endMonotonicNs']-terminal['startMonotonicNs'],
        sha256={n: sha(directory/n) for n in NAMES})
    return row, summary, terminal


def original_evidence(original, chosen):
    assert original == ORIGINAL
    archive, pilot = original/'frozen-tools', original/'pilot'
    plan, result, pipeline = read(pilot/'plan.json'), read(pilot/'result.json'), read(original/'pipeline.json')
    assert plan['schema'] == 'rook2-consumed-prefix-collection-v1'
    assert plan['schedule'] == [dict(case=c, queue_depth=2, repeat=1) for c in ['profile-08', 'profile-35']]
    assert not result['complete'] and result['failure'] == 'AssertionError()' and result['runs'] == []
    assert read(pilot/'failure.json') == dict(failure='AssertionError()', completed=0)
    assert not (pilot/'01-profile-35-q2').exists(), '35 already started in original raw'
    assert plan['nativeCpu'] == 14 and plan['helperAffinity'] == sorted(HELPERS) and plan['quietSiblings'] == [7, 15]
    assert plan['limits'] == dict(perLifeSeconds=180, streamSeconds=900, addressSpaceBytes=AS_BYTES, stdoutBytesPerCase=OUTPUT_BYTES)
    old_policy = read(archive/'policy.json')
    assert old_policy == plan['policy'] == read(pilot/'policy.json') == read(original/'policy.json')
    assert old_policy['reportSchema'] == 'rook2-consumed-prefix-recovery-v1'
    repaired = dict(old_policy, reportSchema='rook2-consumed-prefix-v1')
    assert repaired == chosen, 'policy changed beyond the schema label'
    assert sha(archive/'policy.json') == plan['policySha256'] == sha(pilot/'policy.json')
    resolved = {}
    for path, digest in plan['inputSha256'].items():
        actual = resolve_pinned(path, digest, archive)
        resolved[path] = dict(path=str(actual), sha256=digest)
    receipt = admit(Path(plan['build']), tool_archive=archive); image = Path(receipt['binary'])
    assert image == original/'build/rook2-consumed-prefix' and sha(image) == receipt['binarySha256'] == plan['binarySha256'] == IMAGE_SHA
    assert receipt['sourceBefore'] == plan['sourcePins'] == snapshot(Path(receipt['crate']))
    assert receipt['baselineBefore'] == plan['baseline'] == baseline()
    assert pipeline['sourceBefore'] == receipt['sourceBefore'] and pipeline['baselineBefore'] == receipt['baselineBefore']
    assert pipeline['policy'] == old_policy and pipeline['policySha256'] == plan['policySha256']
    assert not pipeline['complete'] and pipeline['failure'] == "AssertionError(('collect', 1))"
    expected_selectors = ['hierarchical_recovery::prefix_tests::', 'branch_journal::prefix_tests::',
        'hierarchical_recovery::tests::', 'remembered::sparse_tests::', 'branch_journal::range_tests::',
        'remembered::tests::', 'branch_transactions::focused_tests::']
    assert pipeline['selectors'] == expected_selectors
    tests = [row for row in pipeline['stages'] if row['stage'].startswith('tests-')]
    assert len(tests) == 7
    names = []
    for i, (row, selector, expected) in enumerate(zip(tests, expected_selectors, [6,5,4,3,5,10,1])):
        assert row['stage'] == f'tests-{i:02d}' and row['exit'] == 0
        assert row['argv'][row['argv'].index('--')-1] == selector
        assert len(row['passedTests']) == expected and all(n.startswith(selector) for n in row['passedTests'])
        assert row['testSummaries'] == [['ok', str(expected), '0', '0']]
        names += row['passedTests']
    assert len(names) == len(set(names)) == 34
    assert [r['exit'] for r in pipeline['stages'] if r['stage'] == 'build'] == [0]
    assert [r['exit'] for r in pipeline['stages'] if r['stage'] == 'collect'] == [1]
    for path, digest in pipeline['driverInputs'].items():
        resolve_pinned(path, digest, archive)
    for row in pipeline['stages']:
        for stream in ['stdout', 'stderr']:
            assert sha(original/(row['stage']+'.'+stream)) == row[stream+'Sha256']
    row, summary, terminal = audit_life(pilot/'00-profile-08-q2', plan['schedule'][0], image,
        chosen, plan['inputSha256'], plan['policySha256'])
    assert result['startMonotonicNs'] <= terminal['startMonotonicNs'] < terminal['endMonotonicNs'] <= result['endMonotonicNs']
    assert 0 < result['endMonotonicNs']-result['startMonotonicNs'] <= 900*10**9
    paths = [original/'pipeline.json', original/'policy.json', *archive.iterdir()]
    paths += [pilot/n for n in ['plan.json', 'result.json', 'failure.json', 'policy.json', 'proc-stat-before', 'proc-stat-after']]
    paths += [pilot/'00-profile-08-q2'/n for n in NAMES]
    paths += [original/'build'/n for n in ['receipt.json', 'stdout', 'stderr', 'rook2-consumed-prefix']]
    for stage in pipeline['stages']:
        paths += [original/(stage['stage']+'.'+stream) for stream in ['stdout', 'stderr']]
    bindings = {str(p): sha(p) for p in paths if p.is_file()}
    return dict(original=str(original), image=str(image), imageSha256=IMAGE_SHA, sourcePins=receipt['sourceBefore'],
        baseline=receipt['baselineBefore'], originalBindings=bindings, originalResolvedPins=resolved,
        policyRepair=dict(field='reportSchema', old=old_policy['reportSchema'], new=chosen['reportSchema'], semanticFieldsUnchanged=True),
        focusedTests=34, adopted08=row, adopted08Summary=summary,
        adoptionReason='Original collector exited after successful08 because its expected report schema label was wrong. Native stdout/wait4/terminal are adopted unchanged;08 is never rerun.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', nargs='?', type=Path)
    parser.add_argument('--adopt-only', type=Path)
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.adopt_only:
        assert args.raw is None and args.policy and args.output
        chosen = policy(args.policy.resolve())
        result = dict(complete=True, schema='rook2-consumed-prefix-adopted08-v1', **original_evidence(args.adopt_only.resolve(), chosen))
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
        print('adopted and independently audited original08; no native execution', flush=True)
        return
    base = args.raw.resolve(); plan, result = read(base/'continuation-plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-consumed-prefix-continuation-v1'
    assert result['complete'] and result['failure'] is None and len(result['newRuns']) == 1 and result['nativeLaunches'] == 1
    assert result['adopted08Sha256'] == sha(base/'adopted-08.json')
    chosen = policy(base/'policy.json')
    assert chosen == plan['policy'] == policy(Path(plan['policyPath']))
    assert sha(base/'policy.json') == plan['policySha256'] == sha(plan['policyPath'])
    original = original_evidence(Path(plan['original']), chosen)
    assert original == plan['adoptedEvidence']
    assert read(base/'adopted-08.json') == dict(complete=True, schema='rook2-consumed-prefix-adopted08-v1', **original)
    for path, digest in plan['currentInputs'].items():
        resolve_pinned(path, digest, base/'repaired-tools')
    assert plan['schedule'] == [dict(case='profile-08', action='adopt-existing'), dict(case='profile-35', action='one-new-life')]
    assert plan['nativeCpu'] == 14 and plan['helperAffinity'] == sorted(HELPERS) and plan['quietSiblings'] == [7,15]
    assert plan['limits'] == dict(perLifeSeconds=180, streamSeconds=900, addressSpaceBytes=AS_BYTES, stdoutBytesPerCase=OUTPUT_BYTES)
    assert plan['imageSha256'] == original['imageSha256'] == IMAGE_SHA and plan['image'] == original['image']
    image = Path(plan['image']); step = dict(case='profile-35', queue_depth=2, repeat=1)
    row, summary, terminal = audit_life(base/'01-profile-35-q2', step, image, chosen, plan['currentInputs'], plan['policySha256'])
    assert result['newRuns'] == [row]
    assert result['startMonotonicNs'] <= terminal['startMonotonicNs'] < terminal['endMonotonicNs'] <= result['endMonotonicNs']
    assert 0 < result['endMonotonicNs']-result['startMonotonicNs'] <= 900*10**9
    assert original['adopted08']['nativePid'] != row['nativePid']
    assert read(Path(original['adopted08']['directory'])/'terminal.json')['endMonotonicNs'] < terminal['startMonotonicNs']
    output = dict(complete=True, schema='rook2-consumed-prefix-combined-audit-v1', nativeLives=2, adoptedLives=1, newLives=1,
        original=str(ORIGINAL), continuation=str(base), noRerun08=True, noNewBuildOrTests=True, focusedTests=34,
        rows=[dict(case='profile-08', provenance='adopted-original02', native=original['adopted08'], counts=original['adopted08Summary']),
              dict(case='profile-35', provenance='one-new-continuation-life', native=row, counts=summary)],
        sourcePins=original['sourcePins'], imageSha256=IMAGE_SHA, originalBindings=original['originalBindings'],
        currentInputSha256=plan['currentInputs'], reconcilerSha256=sha(Path(__file__)),
        continuationBindings={str(base/n): sha(base/n) for n in ['continuation-plan.json', 'result.json', 'adopted-08.json', 'policy.json', 'proc-stat-before', 'proc-stat-after']},
        policyRepair=original['policyRepair'],
        scope='Same binary/source/caps and fixed-completion NoHost serial paired modes. Schema-label/admission repair only; no08 rerun,35 retry, parallel speedup, wire qualification or per-rejection full-state audit.')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print('reconciled adopted08 plus exactly one continuation35', flush=True)

if __name__ == '__main__':
    main()
