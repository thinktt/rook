"""Bound the metadata-only completion to immutable evidence and original caps.

No process starts on import. Historical auditor bytes execute with their original
__file__ so their path-derived constants stay original; their launcher expectation
comes from the old plan, never the repaired file's current hash.
"""
import hashlib
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
from common import (HERE, ROOT, HELPERS, ACCOUNT, SPEC, baseline, code_paths, module,
                    read, sha, snapshot, variants, schedule)

ORIGINAL = Path('/home/legolas/rook2-experiments/colors-three-20261026-01')
REPAIR_FILES = [HERE/'account_threads.py', HERE/'common.py']


def archived_module(name, path, archived):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__package__ = None
    exec(compile(archived.read_bytes(), str(archived), 'exec'), value.__dict__)
    return value


def archive(original):
    root = original/'frozen-tools'
    manifest = read(root/'manifest.json')
    assert manifest['schema'] == 'rook2-colors-three-frozen-tools-v1' and manifest['copiedBeforeRepair'] is True
    assert sha(root/'manifest.json') == 'd6d07eac600f6740034f432c4abb8531b4b572812d2d9acd820bab561d08944d'
    by = {}
    for row in manifest['files']:
        path = Path(row['original'])
        assert path not in by
        archived = root/row['archive']
        assert archived.is_relative_to(root) and sha(archived) == row['sha256']
        assert archived.stat().st_size == row['bytes']
        by[path] = (archived, row['sha256'])
    return root, by


def inspect(original):
    original = original.resolve()
    assert original == ORIGINAL
    frozen, files = archive(original)
    pipeline_path, plan_path, result_path = original/'pipeline.json', original/'pilot/plan.json', original/'pilot/result.json'
    for path in [pipeline_path, plan_path, result_path, HERE/'preparation.json']:
        assert sha(path) == files[path][1]
    pipeline, plan, result = read(pipeline_path), read(plan_path), read(result_path)
    prep_path = Path(pipeline['preparation'])
    prepared = read(prep_path)
    assert sha(prep_path) == pipeline['preparationSha256'] == files[prep_path][1]
    assert prepared == pipeline['sourcePreparation']
    assert prepared['schema'] == 'rook2-colors-three-source-preparation-v1'
    assert prepared['baseCommit'].startswith('9b58c225')
    for path, expected in prepared['inputSha256'].items():
        source = Path(path)
        assert files[source][1] == expected
        if source not in REPAIR_FILES:
            assert sha(source) == expected
    repairs = []
    for path in REPAIR_FILES:
        old = files[path][0].read_bytes()
        assert old.count(b'rook2-eval-white') == old.count(b'rook2-eval-black') == 1
        expected = old.replace(b'rook2-eval-white', b'rook2-eval-whit').replace(b'rook2-eval-black', b'rook2-eval-blac')
        assert path.read_bytes() == expected, 'only the two comm literals may change: '+str(path)
        repairs.append(dict(path=str(path), originalSha256=files[path][1], repairedSha256=sha(path)))
    assert prepared['candidateSource'] == snapshot(Path(prepared['candidateCrate']))
    assert prepared['controlSource'] == snapshot(Path(prepared['controlCrate']))
    assert pipeline['prepared'] and not pipeline['collected'] and not pipeline['complete']
    assert pipeline['failure'] == "AssertionError(('collection', 1))"
    assert pipeline['pipelineSeconds'] == 3600
    tests = [row for row in pipeline['stages'] if row['stage'].startswith('tests-')]
    assert len(tests) == 7 and all(row['exit'] == 0 for row in tests)
    assert sum(len(row['passedTests']) for row in tests) == 38
    assert len({name for row in tests for name in row['passedTests']}) == 38
    for stage in pipeline['stages']:
        for suffix in ['stdout', 'stderr']:
            assert sha(original/(stage['stage']+'.'+suffix)) == stage[suffix+'Sha256']
    assert [(row['stage'], row['exit']) for row in pipeline['stages'][-3:]] == [
        ('candidate-build', 0), ('cli-affinity', 0), ('collection', 1)]
    focused = read(original/'focused/result.json')
    assert focused['complete'] and len(focused['cli']) == 13 and len(focused['affinityReplays']) == 2
    assert focused['engineSha256'] == sha(pipeline['candidate']['path'])
    assert plan['schema'] == 'rook2-colors-three-generic-v1' and plan['schedule'] == schedule()
    assert plan['variants'] == variants(Path(pipeline['control']['path']), Path(pipeline['candidate']['path']))
    assert plan['limits'] == dict(perLifeSeconds=180, totalSeconds=1800,
                                 supervisorPlacementSeconds=10, inputGateSeconds=12)
    assert not result['complete'] and result['failure'] == 'AssertionError()'
    assert len(result['runs']) == 3 and result['idle'] == []
    for step, row in zip(plan['schedule'], result['runs']):
        assert step['warmup'] and all(row[key] == value for key, value in step.items())
    assert all(not step['warmup'] or step['repeat'] == 0 for step in plan['schedule'])
    for path, expected in plan['inputSha256'].items():
        if Path(path) not in REPAIR_FILES:
            assert sha(path) == expected, path
        else:
            assert files[Path(path)][1] == expected
    assert pipeline['protectedArtifacts'] == plan['protectedArtifacts'] == baseline()
    old = archived_module('colors_three_frozen_original_common', HERE/'common.py', files[HERE/'common.py'][0])
    old.admission(Path(plan['controlBuild']), Path(plan['candidateBuild']),
                  Path(pipeline['control']['path']), Path(pipeline['candidate']['path']), prepared)
    return dict(original=original, frozen=frozen, files=files, pipeline=pipeline,
                plan=plan, result=result, prepared=prepared, repairs=repairs, old=old)


def failed_startup(context):
    directory = context['original']/'pilot/03-profile-35-colors3-r0'
    native = read(directory/'native.json')
    assert native['expected_threads'] == 3 and native['native_exit_code'] == -9
    assert native['native_wait_status'] == 9 and native['failure'] == 'external-placement-unverified'
    assert native['placement_error'] == 'AssertionError()'
    assert native['launcher_sha256'] == context['plan']['inputSha256'][str(ACCOUNT)]
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(native['engine'])
    assert native['ready_sha256'] is None and native['colors_report_sha256'] is None
    assert not (directory/'native.json.ready').exists() and not (directory/'native.json.input-gate.json').exists()
    assert not (directory/'wire/receipt.json').exists() and not (directory/'colors.json').exists()
    # The tap records an attempted write before the placement gate forwards it.
    # Bind those bytes rather than mistaking the tap file for delivered input.
    workload = next(row for row in read(SPEC/'workloads.json')['cases'] if row['id'] == 'profile-35')
    setup = ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
    assert (directory/'wire/stdin.raw').read_bytes() == setup and len(setup) == 421
    for stream in ['stdout', 'stderr']:
        assert (directory/'wire'/f'{stream}.raw').stat().st_size == 0
    observed = native['native_post_exec']
    tasks = sorted((tid for tid in observed['tasks'] if tid != str(native['native_pid'])), key=int)
    assert observed['task_affinities'][str(native['native_pid'])] == [14]
    assert [observed['task_affinities'][tid] for tid in tasks] == [[6], [4]]
    assert [observed['task_names'][tid] for tid in tasks] == ['rook2-eval-whit', 'rook2-eval-blac']
    for pid in [native['native_pid'], native['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists()
    return dict(directory=str(directory), nativePid=native['native_pid'],
                nativeSha256=sha(directory/'native.json'), attemptedSetupBytes=len(setup),
                attemptedSetupSha256=sha(directory/'wire/stdin.raw'), gatedReleaseObserved=False,
                deliveredProtocolBytes=0, searchCalls=0,
                deliveryAssurance='pinned gate forwards original write only after ready and input-gate artifacts; both absent',
                reason='full Rust thread names compared with Linux15-byte comm; attempted setup stopped before gated release')


def completion_paths():
    return code_paths()+[HERE/'completion_common.py', HERE/'complete.py', HERE/'completion_reconcile.py']


def epoch_binding(index, row, epoch, hashes):
    return dict(scheduleIndex=index, epoch=epoch, directory=row['directory'],
        launcherSha256=hashes[str(ACCOUNT)], commonSha256=hashes[str(HERE/'common.py')],
        collectorSha256=hashes[str(HERE/'collect.py')], gateSha256=hashes[str(HERE/'placement_gate.mjs')],
        tapSha256=hashes[str(HERE/'tools/tap_wire.mjs')])
