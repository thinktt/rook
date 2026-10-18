#!/usr/bin/env python3
"""Promote exact tested85-operation closures after all explicit correctness gates."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('/tmp/imp2-move-q-evaluation-combined-20261018')
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot, tool_snapshot


def load(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, v):
    with p.open('x') as stream:
        json.dump(v, stream, indent=2); stream.write('\n')


def main():
    prep = ROOT/'evidence/diagnostic-move-q-evaluation-preparation-20261018'
    out = ROOT/'evidence/diagnostic-move-q-evaluation-20261018'
    native_dir = ROOT/'evidence/quiescence-evaluation-default-validation-20261018'
    prepared = load(prep/'source-preparation.json')
    baseline_native = load(ROOT/'evidence/retained-evaluation-build-20261018/receipt.json')
    baseline_cold = load(ROOT/'evidence/diagnostic-retained-evaluation-build-20261018/receipt.json')
    native_build = ROOT/'evidence/quiescence-evaluation-default-build-20261018/receipt.json'
    cold_build = ROOT/'evidence/diagnostic-move-q-evaluation-build-20261018/receipt.json'
    expected_native = prepared['native_source_sha256']
    expected_cold = prepared['adapter_source_sha256']
    expected_tools = prepared['tool_source_sha256']
    before = dict(native=source_snapshot(ROOT), adapter=source_snapshot(ROOT/'diagnostic'), tools=tool_snapshot(ROOT))
    assert before['native'] == baseline_native['source_sha256_before']
    assert before['adapter'] == baseline_cold['source_sha256_before']
    assert source_snapshot(SOURCE) == expected_native == load(native_build)['source_sha256_before']
    assert source_snapshot(SOURCE/'diagnostic') == expected_cold == load(cold_build)['source_sha256_before']
    assert before['tools'] == expected_tools == tool_snapshot(SOURCE)
    native = load(native_dir/'identity.json')
    terminal = load(native_dir/'tool-terminal.json')
    diag = load(out/'identity.json')
    assert native['native_total_units'] == 142 and native['strict_replays'] == 54
    assert native['interruption_fixtures'] == 8 and native['interruption_searches'] == 24
    assert native['retry_all_stage_inputs_stable'] and native['retry_actual_exit'] == 0
    assert native['owned_live_processes'] == terminal['owned_live_processes'] == 0
    assert terminal['complete'] and terminal['exit_code'] == 0
    assert native['default_full_impl_raw_bytes_restored'] and native['default_inline_fast_scope_restored']
    assert len(diag['operations']) == 85 and diag['cases'] == 5289 and diag['units'] == 117
    assert load(out/'tool-terminal.json')['exit_code'] == load(out/'reconcile-terminal.json')['exit_code'] == 0
    frozen_native = native_build.parent/'rook2-exact'
    frozen_cold = cold_build.parent/'rook2-diag-exact'
    assert sha(frozen_native) == native['native_sha256'] == diag['native_binary_sha256']
    assert sha(frozen_cold) == diag['adapter_sha256']
    dependencies = [prep/'plan.json', prep/'source-preparation.json', prep/'prepared-adapter.tar.gz',
        prep/'run.py', prep/'reconcile.py', native_build, cold_build,
        native_dir/'identity.json', native_dir/'tool-terminal.json', native_dir/'report.md',
        native_dir/'codegen/report.md', native_dir/'codegen/focused-referents-and-default-gate.json',
        native_dir/'final-process-check.json', out/'identity.json', out/'tool-terminal.json',
        out/'reconcile-terminal.json', out/'verification.json', out/'conformance.json']
    inputs = {str(p):sha(p) for p in dependencies}
    write(HERE/'before.json', before)
    changed_native = [p for p,h in expected_native.items() if before['native'].get(p) != h]
    changed_cold = [p for p,h in expected_cold.items() if before['adapter'].get(p) != h]
    assert changed_native == ['src/evaluator.rs','src/quiescence.rs','src/quiescence_policy.rs']
    assert changed_cold == ['src/evaluation_common.rs','src/main.rs','src/move_evaluation.rs',
        'src/positions.rs','src/quiescence_evaluation.rs','src/retained_evaluation.rs']
    for p in changed_native:
        shutil.copyfile(SOURCE/p, ROOT/p)
    for p in changed_cold:
        shutil.copyfile(SOURCE/'diagnostic'/p, ROOT/'diagnostic'/p)
    assert source_snapshot(ROOT) == expected_native
    assert source_snapshot(ROOT/'diagnostic') == expected_cold
    assert tool_snapshot(ROOT) == expected_tools
    assert {str(p):sha(p) for p in dependencies} == inputs
    record = dict(status='Promoted exact validated85-operation source closures',
        native_source_sha256=expected_native, adapter_source_sha256=expected_cold,
        tool_source_sha256=expected_tools, changed_native=changed_native, changed_adapter=changed_cold,
        native_binary_sha256=sha(frozen_native), diagnostic_binary_sha256=sha(frozen_cold),
        native_artifact=str(frozen_native), diagnostic_artifact=str(frozen_cold),
        native_tests=142, adapter_units=117, official_cases=5289, mandatory_operations=85,
        full_official_files=79, strict_replays=54, interruption_fixtures=8, interruption_searches=24,
        dependency_sha256=inputs, no_canonical_path_rebuild=True,
        performance_claim='None for this new closure; prior8d PGO/cost/gameplay remains artifact-specific',
        preserved_failure='First default strict/wire wrapper metadata instability, despite passing raw behavior; stable retry used for promotion',
        integration_script_sha256=sha(Path(__file__)))
    write(HERE/'integration.json', record)
    prior = ROOT/'evidence/retained-evaluation-integration-20261018/numeric-proof-delta-binding.json'
    write(HERE/'numeric-proof-delta-binding.json', dict(
        status='Bounded source delta retains preceding numerical premises; not a new global proof',
        preceding_binding=str(prior), preceding_binding_sha256=sha(prior),
        integration_sha256=sha(HERE/'integration.json'), changed_native=changed_native,
        premises=[
            'Same ordinary input domains, Position/Node/Retained fields and transition/inheritance owners.',
            'Shared selector retains exact sparse/strict refresh predicates, bounds and arithmetic; const false calls original full/fast wrappers.',
            'Noncheck disposition extraction preserves lower-bound, upper-bound, stand-pat priority and returned values.',
            'Detailed callbacks consume actual produced values only; ordinary finishing and work charges retain their owners.',
            'Cold move transport uses actual Node child/null transitions and fixed-root evaluator; no production domain or formula change.'],
        limitations='Existing proofs retain their bounded invariants and unresolved composed-hint admission gap. Finite conformance, codegen scope and source equality do not prove full behavior, global arithmetic or CPU neutrality.'))
    print(json.dumps({k:record[k] for k in ['native_tests','adapter_units','official_cases','mandatory_operations','native_binary_sha256','diagnostic_binary_sha256']}))


if __name__ == '__main__':
    main()
