#!/usr/bin/env python3
"""Freeze the centrally merged Move83/default-Q85 source and verification plan."""
import collections
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot, tool_snapshot

MOVE = Path('/tmp/imp2-move-evaluation-proposal-20261018-kx5a4x1v')
Q = Path('/tmp/imp2-quiescence-evaluation-default-20261018-native-child')
COMBINED = Path('/tmp/imp2-move-q-evaluation-combined-20261018')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def archive(path, files):
    with tarfile.open(path, 'x:gz') as bundle:
        for name, data in files.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            entry.mode = 0o644
            bundle.addfile(entry, io.BytesIO(data))


def main():
    move_prep = ROOT/'evidence/diagnostic-move-evaluation-preparation-20261018'
    move_manifest = json.loads((move_prep/'source-preparation.json').read_text())
    reference_path = ROOT/'evidence/quiescence-evaluation-default-build-20261018/receipt.json'
    reference = json.loads(reference_path.read_text())
    native = source_snapshot(Q)
    assert native == reference['source_sha256_before'] == reference['source_sha256_after']
    assert source_snapshot(MOVE/'diagnostic') == move_manifest['adapter_source_sha256']
    assert source_snapshot(COMBINED) == source_snapshot(MOVE)
    assert source_snapshot(COMBINED/'diagnostic') == source_snapshot(MOVE/'diagnostic')
    tools = tool_snapshot(Q)
    assert tools == tool_snapshot(MOVE) == tool_snapshot(COMBINED) == tool_snapshot(ROOT)
    assert tools == reference['tool_sha256_before'] == reference['tool_sha256_after']
    native_changes = [name for name in native if native[name] != source_snapshot(MOVE)[name]]
    assert native_changes == ['src/evaluator.rs', 'src/quiescence.rs', 'src/quiescence_policy.rs']
    for name in native_changes:
        shutil.copyfile(Q/name, COMBINED/name)
    shutil.copyfile(Q/'diagnostic/src/quiescence_evaluation.rs', COMBINED/'diagnostic/src/quiescence_evaluation.rs')
    move_main = (MOVE/'diagnostic/src/main.rs').read_text()
    assert 'mod quiescence_evaluation;' not in move_main
    combined_main = move_main.replace('mod positions;\n', 'mod positions;\nmod quiescence_evaluation;\n', 1)
    anchor = '        "evaluation.retainedSequence" => retained_evaluation::dispatch(input),\n'
    assert move_main.count(anchor) == 1
    combined_main = combined_main.replace(anchor, anchor +
        '        "evaluation.quiescenceEntry" | "evaluation.quiescenceDisposition" => {\n'
        '            quiescence_evaluation::dispatch(operation, input)\n'
        '        }\n', 1)
    q_main = (Q/'diagnostic/src/main.rs').read_text()
    expected_from_q = q_main.replace('mod ledger;\n', 'mod ledger;\nmod move_evaluation;\n', 1)
    expected_from_q = expected_from_q.replace(anchor,
        '        "evaluation.moveSequence" => move_evaluation::dispatch(input),\n'+anchor, 1)
    assert combined_main == expected_from_q, 'independent adjacent-dispatch merge derivations disagree'
    (COMBINED/'diagnostic/src/main.rs').write_text(combined_main)
    assert source_snapshot(COMBINED) == native
    adapter = source_snapshot(COMBINED/'diagnostic')
    assert len(native) == 43 and len(adapter) == 30 and len(tools) == 23
    changed_cold = [name for name in adapter if adapter[name] != move_manifest['adapter_source_sha256'].get(name)]
    assert changed_cold == ['src/main.rs', 'src/quiescence_evaluation.rs']
    move_plan = json.loads((move_prep/'plan.json').read_text())
    q_plan = json.loads((ROOT/'evidence/diagnostic-quiescence-evaluation-preparation-20261018/plan.json').read_text())
    fixtures = move_plan['fixtures'] | q_plan['fixtures']
    operations, ids, inventory = collections.Counter(), [], []
    for path, digest in fixtures.items():
        fixture = json.loads(Path(path).read_text())
        assert sha(Path(path)) == digest
        ids.extend(case['id'] for case in fixture['cases'])
        counts = collections.Counter(case['request']['operation'] for case in fixture['cases'])
        operations.update(counts)
        inventory.append(dict(path=path, sha256=digest, count=len(fixture['cases']), operations=dict(counts)))
    assert len(fixtures) == 79 and len(ids) == len(set(ids)) == 5289 and len(operations) == 85
    archive(HERE/'prepared-adapter.tar.gz', {name:(COMBINED/'diagnostic'/name).read_bytes() for name in adapter})
    archive(HERE/'exact-inputs.tar.gz', {Path(path).name:Path(path).read_bytes() for path in fixtures})
    plan = dict(status='Frozen85-operation central merge; untimed adapter validation pending',
        source_root=str(COMBINED), native_build_reference=str(reference_path),
        inherited_native_binary_sha256=reference['binary_output']['sha256'],
        expected_unit_tests=117, expected_native_unit_tests=142,
        expected_case_count=5289, expected_operation_count=85, fixture_file_count=79,
        operations=sorted(operations), operation_case_counts=dict(sorted(operations.items())), fixtures=fixtures,
        fixture_selection='Every case from79 whole official files, original fixture metadata preserved; no partial files',
        adapter_preparation='source-preparation.json',
        native_reuse_evidence=[str(ROOT/'evidence'/p) for p in [
            'quiescence-evaluation-default-validation-20261018/native-verification.json',
            'quiescence-evaluation-default-validation-20261018/native-tool-terminal.json',
            'quiescence-evaluation-default-validation-20261018/native-actual-terminal.json',
            'quiescence-evaluation-default-build-20261018/tool-terminal.json',
            'diagnostic-move-evaluation-20261018/identity.json',
            'diagnostic-move-evaluation-20261018/tool-terminal.json']],
        merge_note='Earlier git apply --check failed main.rs adjacent dispatch context (parent terminal9c9f11 exit1); no patches applied. This merge copies exact3 corrected native files and one exact Q cold module, and derives main.rs identically from both parents.',
        authorization='Parent untimed housekeeping adapter validation; default-Q strict54+wire may run concurrently on housekeeping. No CPU timing, PGO training or profiling.',
        promotion_gate='Require corrected-Q native142, strict54+8 interruption fixtures, default codegen review and combined117 units/5289 cases before central source promotion.')
    write(HERE/'plan.json', plan)
    write(HERE/'fixture-inventory.json', inventory)
    write(HERE/'source-preparation.json', dict(adapter_source_sha256=adapter,
        native_source_sha256=native, tool_source_sha256=tools,
        archive='prepared-adapter.tar.gz', archive_sha256=sha(HERE/'prepared-adapter.tar.gz'),
        planned_verifier_sha256=sha(HERE/'run.py'), native_reference=str(reference_path),
        native_reference_sha256=sha(reference_path),
        changed_native_from_move83=native_changes, changed_cold_from_move83=changed_cold,
        independent_main_merge_equal=True))
    print(json.dumps(dict(native=len(native), frontend=len(adapter), tools=len(tools), cases=len(ids), operations=len(operations))))


if __name__ == '__main__':
    main()
