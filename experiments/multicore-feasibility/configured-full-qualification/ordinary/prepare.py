#!/usr/bin/python3
"""Freeze separate mode2/full and mode1/short ordinary lanes; no native runs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
KIT = Path('/home/legolas/king-spec/conformance/gate-replay')
PRODUCTION = Path('/home/legolas/rook2-experiments/configured-full-20261024-01/production')
IMAGE_SHA = '8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b'
SOURCE_COMMIT = '66f35e44'
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--image', type=Path, default=PRODUCTION/'rook2-pgo')
    parser.add_argument('--build', type=Path, default=PRODUCTION/'use-build')
    args = parser.parse_args()
    base, image, build = args.output.resolve(), args.image.resolve(), args.build.resolve()
    base.mkdir()
    receipt = load(build/'receipt.json')
    assert sha(image) == receipt['binary_output']['sha256'] == IMAGE_SHA
    assert receipt['source_sha256_before'] == receipt['source_sha256_after']
    for name, digest in receipt['source_sha256_before'].items():
        assert sha(ROOT/name) == sha(build/'source-before'/name) == digest, name
    fixture = load(KIT/'accepted-games-v1.json')
    assert len(fixture['games']) == 12 and sum(len(row['plies']) for row in fixture['games']) == 632
    paths = [path for path in HERE.iterdir() if path.is_file()]
    paths += [KIT/name for name in ['run.mjs', 'continuous.mjs', 'combine.mjs',
        'seed-command-controls.mjs', 'seed-persistence-controls.mjs', 'accepted-games-v1.json',
        'continuous-switching-v1.json', 'README.md']]
    paths += [ROOT/'tools/check_live.py', HERE.parents[1]/'usable-full/account_threads.py',
        HERE.parents[1]/'configured-full/verify.py', build/'receipt.json', image,
        Path('/usr/bin/python3'), Path('/usr/bin/node'),
        Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json')]
    pins = {str(path): sha(path) for path in paths}
    pins.update({str(ROOT/name): digest for name, digest in receipt['source_sha256_before'].items()})
    plans = []
    for budget in [2, 1]:
        directory = base/f'mode{budget}'
        directory.mkdir()
        launcher = ['/usr/bin/python3', str(HERE/'native_launch.py'), str(image), f'--threads={budget}', '--']
        counts = ({'games': 12} if budget == 2 else {})
        counts.update({'continuous': 1, 'seed-command-controls': 11, 'seed-persistence-controls': 1})
        stages = {}
        for name, script in [('games', 'run.mjs'), ('continuous', 'continuous.mjs'),
                ('seed-command-controls', 'seed-command-controls.mjs'),
                ('seed-persistence-controls', 'seed-persistence-controls.mjs')]:
            if name not in counts:
                continue
            local = directory/name
            local.mkdir()
            (local/'native').mkdir()
            (local/'wire').mkdir()
            command = ['/usr/bin/node', '--import', str(HERE/'capture.mjs'), str(KIT/script)]
            if name in ['games', 'continuous']:
                command += ['--report', str(local/'report.json')]
            stages[name] = [*command, '--', *launcher]
            calls = [launcher+([] if name == 'seed-command-controls' and index == 10
                               else ['--diagnostic-seed-command']) for index in range(counts[name])]
            config = local/'tap-config.json'
            put(config, dict(rawRoot=str(local/'wire'), image=str(image), expectedCalls=calls,
                maxBytes=(40 if name == 'games' else 9)*1024**2, threadBudget=budget))
        (directory/'wire').mkdir()
        (directory/'wire/native').mkdir()
        stages['wire'] = ['/usr/bin/python3', str(HERE/'run_wire.py'), str(directory)]
        if budget == 2:
            (directory/'combine').mkdir()
            stages['combine'] = ['/usr/bin/node', str(KIT/'combine.mjs'), '--report',
                str(directory/'combine/report.json'), '--continuous', str(directory/'continuous/report.json'),
                str(directory/'games/report.json')]
        (directory/'independent').mkdir()
        local_pins = {**pins, **{str(directory/name/'tap-config.json'): sha(directory/name/'tap-config.json') for name in counts}}
        plan = dict(schema='rook2-configured-full-ordinary-qualification-v1', repo=str(ROOT), kit=str(KIT),
            rawRoot=str(directory), sourceCommit=SOURCE_COMMIT, buildReceipt=str(build/'receipt.json'),
            image=str(image), imageSha256=IMAGE_SHA, threads=budget, launcherCommand=launcher,
            placementSupervisor=str(HERE.parents[1]/'usable-full/account_threads.py'),
            wireChecker=str(ROOT/'tools/check_live.py'), wireLauncher=str(HERE/'wire_engine.py'),
            wireFixture='/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json',
            tapCounts=counts, nativeStageOrder=[*counts, 'wire'], selectedNativeLifetimes=sum(counts.values())+8,
            gatedSearchLifetimes=(22 if budget == 2 else 10), noSearchSynchronousLifetimes=11,
            aggregateSeconds=(1200 if budget == 2 else 300), memoryPerProcessBytes=8*1024**3,
            perFileBytes=256*1024**2, retainedStreamBytes=512*1024**2, helperCpus=HELPERS,
            startupPermittedCpus=[6, 14], actualSearchCoordinatorCpus=[14], actualSearchHelperCpus=([6] if budget == 2 else []),
            originalLimitsPreserved=True, performanceMeasurement=False, retries=0,
            optionalSequenceConflict=False, reportCommandsIdentical=True, nativeDirsPassedOutsideArgv=True,
            completeFocusedReplaySelected=(budget == 2), pins=local_pins, stages=stages,
            scope=('Regular12 plus continuity8/seed11/persistence3/wire8-24 and literal original focused combine.'
                   if budget == 2 else 'Short continuity8/seed11/persistence3/wire8-24 only; no full12 or complete focused claim.'),
            adapterLimits='Synchronous no-search seed input is unchanged and eager; optional actual/null task observations do not prove pre-input placement. All search owners are gated after configuration and before their first protocol byte.',
            runtime=dict(python=sys.version, uname=list(os.uname()),
                environment={key: os.environ.get(key) for key in ['PATH','TMPDIR','LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS']}))
        put(directory/'plan.json', plan)
        plans.append(dict(threads=budget, plan=str(directory/'plan.json'), sha256=sha(directory/'plan.json'),
            run=['/usr/bin/python3', str(HERE/'run.py'), str(directory)]))
    manifest = dict(schema='rook2-configured-full-ordinary-setup-v1', image=str(image), imageSha256=IMAGE_SHA,
        sourceCommit=SOURCE_COMMIT, configurationVerification=['/usr/bin/python3',
            str(HERE.parents[1]/'configured-full/verify.py'), '--engine', str(image), '--output', str(base/'configuration')],
        lanes=plans, nativeLifetimes=54, nativeRunsByPreparation=0, noBuild=True,
        scope='Separate ordinary PGO qualification configurations; configuration verification is extra and separately recorded.')
    put(base/'setup.json', manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
