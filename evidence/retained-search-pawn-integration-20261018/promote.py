#!/usr/bin/env python3
"""Promote the exact tested cold-only87-operation source closure."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('/tmp/imp2-retained-search-pawn-20261018-5hjoji3q')
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot, tool_snapshot


def load(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    old = ROOT/'evidence/move-q-evaluation-integration-20261018/integration.json'
    old_identity = load(old)
    result = ROOT/'evidence/diagnostic-retained-search-pawn-20261018'
    build_path = ROOT/'evidence/diagnostic-retained-search-pawn-build-20261018/receipt.json'
    identity, terminal, build = load(result/'identity.json'), load(result/'tool-terminal.json'), load(build_path)
    assert identity['cases'] == 6151 and identity['units'] == 126 and len(identity['operations']) == 87
    assert identity['whole_fixture_files'] == 82 and identity['independent_raw_response_equal'] == 6151
    assert identity['partial_files'] == identity['duplicate_case_ids'] == 0
    assert identity['source_identity_stable'] and terminal['complete'] and terminal['exit_code'] == 0
    assert terminal['all_owned_jobs_terminal'] and terminal['owned_live_processes'] == 0
    assert terminal['pipeline_actual_terminal']['actual_exit_code'] == 0
    assert terminal['identity_sha256'] == sha(result/'identity.json')
    assert identity['build_receipt_sha256'] == sha(build_path)
    native, adapter, tools = source_snapshot(ROOT), source_snapshot(ROOT/'diagnostic'), tool_snapshot(ROOT)
    assert native == source_snapshot(SOURCE) == old_identity['native_source_sha256']
    assert adapter == old_identity['adapter_source_sha256']
    assert tools == tool_snapshot(SOURCE) == old_identity['tool_source_sha256']
    expected = source_snapshot(SOURCE/'diagnostic')
    assert expected == build['source_sha256_before'] == build['source_sha256_after']
    assert identity['native_binary_sha256'] == old_identity['native_binary_sha256']
    frozen = build_path.parent/'rook2-diag-exact'
    assert sha(frozen) == identity['adapter_sha256'] == build['binary_output']['sha256']
    assert all(sha(Path(path)) == digest for path,digest in identity['native_reuse_evidence_sha256'].items())
    changed = [path for path,digest in expected.items() if adapter.get(path) != digest]
    assert changed == ['src/main.rs','src/pawn_subtotals.rs']
    dependencies = {str(p):sha(p) for p in [old,build_path,result/'identity.json',result/'tool-terminal.json',
        result/'report.md',result/'case-reconciliation.json']}
    write(HERE/'before.json', dict(native=native,adapter=adapter,tools=tools))
    for path in changed:
        shutil.copyfile(SOURCE/'diagnostic'/path, ROOT/'diagnostic'/path)
    assert source_snapshot(ROOT) == native and tool_snapshot(ROOT) == tools
    assert source_snapshot(ROOT/'diagnostic') == expected
    assert all(sha(Path(path)) == digest for path,digest in dependencies.items())
    write(HERE/'integration.json', dict(status='Exact tested87-operation cold-only closure promoted',
        native_source_sha256=native,adapter_source_sha256=expected,tool_source_sha256=tools,
        changed_native=[],changed_adapter=changed,dependency_sha256=dependencies,
        native_binary_sha256=identity['native_binary_sha256'],adapter_sha256=identity['adapter_sha256'],
        native_tests_reused=142,strict_replays_reused=54,interruption_fixtures_reused=8,
        adapter_units=126,mandatory_operations=87,unique_cases=6151,whole_files=82,
        remaining_mandatory_operations=30,remaining_cases=1522,
        no_canonical_path_rebuild=True,no_ordinary_native_rebuild=True,
        performance_claim='No new native source or timing claim; frozen artifacts retain their own evidence',
        script_sha256=sha(Path(__file__))))
    previous = ROOT/'evidence/move-q-evaluation-integration-20261018/numeric-proof-delta-binding.json'
    write(HERE/'numeric-proof-delta-binding.json',dict(
        preceding_binding=str(previous),preceding_binding_sha256=sha(previous),
        native_source_exactly_unchanged=True,
        conclusion='Preceding bounded production numerical premises are unchanged; cold supplied and produced-context admissions remain distinct.',
        limitation='No broader arithmetic, complete behavior or performance qualification follows.'))
    print(json.dumps(dict(operations=87,cases=6151,units=126,changed_native=0,changed_adapter=changed)))


if __name__ == '__main__':
    main()
