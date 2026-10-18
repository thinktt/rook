#!/usr/bin/env python3
"""Promote the exact native145/DIAG133 combined88 closure."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('/tmp/imp2-qtree-pawn-combined-20261018-73lk5tii')
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
    previous = ROOT/'evidence/retained-search-pawn-integration-20261018/integration.json'
    old = load(previous)
    native_dir = ROOT/'evidence/quiescence-tree-native-validation-02-20261018'
    native_id = load(native_dir/'final-identity.json')
    native_build = ROOT/'evidence/quiescence-tree-native-build-02-20261018/receipt.json'
    out = ROOT/'evidence/diagnostic-qtree-pawn-20261018'
    cold_build = ROOT/'evidence/diagnostic-qtree-pawn-build-20261018/receipt.json'
    identity, terminal = load(out/'identity.json'), load(out/'tool-terminal.json')
    assert identity['cases'] == identity['independent_raw_response_equal'] == 6161
    assert identity['units'] == 133 and len(identity['operations']) == 88
    assert identity['whole_fixture_files'] == 83 and identity['partial_files'] == identity['duplicate_case_ids'] == 0
    assert identity['source_identity_stable'] and terminal['complete'] and terminal['exit_code'] == 0
    assert terminal['all_owned_jobs_terminal'] and terminal['owned_live_processes'] == 0
    assert terminal['pipeline_actual_terminal']['actual_exit_code'] == 0
    assert terminal['identity_sha256'] == sha(out/'identity.json')
    assert native_id['native_tests'] == 145 and native_id['strict_replays'] == 54
    assert native_id['interruption_fixtures'] == 8 and native_id['interruption_searches'] == 24
    assert native_id['all_owned_processes_terminal'] and native_id['source_stable_at_handoff']
    assert native_id['local_q_rsp_delta_bytes'] == 32 and native_id['performance_claim'] is False
    before = dict(native=source_snapshot(ROOT), adapter=source_snapshot(ROOT/'diagnostic'), tools=tool_snapshot(ROOT))
    assert before['native'] == old['native_source_sha256'] and before['adapter'] == old['adapter_source_sha256']
    native, adapter, tools = source_snapshot(SOURCE), source_snapshot(SOURCE/'diagnostic'), tool_snapshot(SOURCE)
    assert native == native_id['native_source_manifest'] == load(native_build)['source_sha256_before']
    assert tools == before['tools'] == native_id['tools_manifest'] == load(native_build)['tool_sha256_before']
    assert adapter == load(cold_build)['source_sha256_before'] == load(cold_build)['source_sha256_after']
    assert identity['build_receipt_sha256'] == sha(cold_build)
    assert native_id['build_receipt_sha256'] == identity['native_build_reference_sha256'] == sha(native_build)
    native_image, cold_image = native_build.parent/'rook2-exact', cold_build.parent/'rook2-diag-exact'
    assert sha(native_image) == native_id['native_binary_sha256'] == identity['native_binary_sha256']
    assert sha(cold_image) == identity['adapter_sha256'] == load(cold_build)['binary_output']['sha256']
    assert all(sha(Path(p)) == digest for p,digest in identity['native_reuse_evidence_sha256'].items())
    changed_native = [p for p,h in native.items() if before['native'].get(p) != h]
    changed_adapter = [p for p,h in adapter.items() if before['adapter'].get(p) != h]
    assert changed_native == ['src/evaluator.rs','src/quiescence.rs']
    assert changed_adapter == ['src/main.rs','src/positions.rs','src/quiescence_tree.rs']
    dependencies = [previous, native_build, cold_build, native_dir/'final-identity.json', native_dir/'handoff.md',
        ROOT/'evidence/quiescence-tree-codegen-review-02-20261018/bounded-gate.json',
        ROOT/'evidence/quiescence-tree-codegen-review-02-20261018/bounded-review.md',
        ROOT/'evidence/combined-qtree-pawn-proposal-20261018/source-graph.json',
        out/'identity.json',out/'tool-terminal.json',out/'case-reconciliation.json']
    frozen_dependencies = {str(p):sha(p) for p in dependencies}
    write(HERE/'before.json', before)
    for p in changed_native:
        shutil.copyfile(SOURCE/p, ROOT/p)
    for p in changed_adapter:
        shutil.copyfile(SOURCE/'diagnostic'/p, ROOT/'diagnostic'/p)
    assert source_snapshot(ROOT) == native and source_snapshot(ROOT/'diagnostic') == adapter
    assert tool_snapshot(ROOT) == tools and all(sha(Path(p)) == h for p,h in frozen_dependencies.items())
    write(HERE/'integration.json',dict(status='Exact tested88-operation combined source closure promoted',
        native_source_sha256=native,adapter_source_sha256=adapter,tool_source_sha256=tools,
        changed_native=changed_native,changed_adapter=changed_adapter,dependency_sha256=frozen_dependencies,
        native_binary_sha256=sha(native_image),adapter_sha256=sha(cold_image),native_tests=145,adapter_units=133,
        mandatory_operations=88,unique_cases=6161,whole_files=83,strict_replays=54,interruption_fixtures=8,
        interruption_searches=24,remaining_mandatory_operations=29,remaining_cases=1512,
        ordinary_q_local_stack_delta_bytes=32,ordinary_q_text_delta_bytes=-116,
        bounded_codegen_claim='No surviving observer argument/record/dispatch/allocation, extra evaluator work or wrapper detour found in reviewed NoTrace path; same55calls/direct recursive ABI. Full/fast scope retained.',
        limits='Finite source/codegen/behavior evidence; no CPU neutrality, new own-PGO/cost/gameplay or prior-artifact timing transfer.',
        preserved_failure='First native test setup incorrectly reached draw admission; corrected onlyH0toH193 in new copy, then native145 passed. Original failure retained.',
        no_canonical_path_rebuild=True,script_sha256=sha(Path(__file__))))
    prior = ROOT/'evidence/retained-search-pawn-integration-20261018/numeric-proof-delta-binding.json'
    write(HERE/'numeric-proof-delta-binding.json',dict(preceding_binding=str(prior),preceding_binding_sha256=sha(prior),
        native_delta='One shared Q recursion with static outside observation, actual evaluation stage hooks, unchanged selection predicates/default wrappers, inherited transition/math/charge owners.',
        preserved_premises='Ordinary position/evaluation state and numeric inputs/algorithms remain unchanged. Recorded work and retained snapshots do not feed production calculations.',
        limitations='Prior bounded numerical prerequisites and unresolved hint-composition domain remain; no new global arithmetic or whole-behavior/performance proof.'))
    print(json.dumps(dict(operations=88,cases=6161,native_tests=145,adapter_units=133,native=sha(native_image),adapter=sha(cold_image))))


if __name__ == '__main__':
    main()
