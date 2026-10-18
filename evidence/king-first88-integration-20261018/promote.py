"""Promote the exact tested king-first88 source; no engine/build execution."""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('/tmp/imp2-king-first88-20261018-daksyrcp')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def write(path, record):
    with path.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')


old_path = ROOT/'evidence/quiescence-tree-integration-20261018/integration.json'
old = load(old_path)
old_map = {**old['native_source_sha256'], **old['tool_source_sha256'],
           **{'diagnostic/'+p: h for p, h in old['adapter_source_sha256'].items()}}
assert len(old_map) == 97
assert all(sha(ROOT/p) == h for p, h in old_map.items())
summary_path = ROOT/'evidence/king-first88-validation-20261018/validation-summary.json'
summary = load(summary_path)
new_map = summary['source_map']
assert new_map.keys() == old_map.keys()
assert all(sha(SOURCE/p) == h for p, h in new_map.items())
assert [p for p in old_map if old_map[p] != new_map[p]] == ['src/movegen.rs']
assert summary['all_owned_processes_terminal'] and summary['no_native_source_fixes']
assert summary['native_tests'] == 147 and summary['diagnostic_unit_tests'] == 133
assert summary['strict_replays'] == 54 and summary['interruption_fixtures'] == 8
assert summary['interruption_searches'] == 24 and summary['diagnostic_cases'] == 6161
assert summary['diagnostic_operations'] == 88 and summary['whole_fixture_files'] == 83
assert summary['all_raw_cases_independently_reconciled']
deps = [old_path, summary_path]
for name, terminal in summary['terminal_records'].items():
    path = ROOT/name
    assert load(path) == terminal and terminal['exit_code'] == 0
    deps.append(path)
native = ROOT/'evidence/king-first88-build-20261018'
diag = ROOT/'evidence/king-first88-diagnostic-build-20261018'
for directory, prefix, artifact_key in [(native, '', 'native_artifact_sha256'),
                                      (diag, 'diagnostic/', 'diagnostic_artifact_sha256')]:
    receipt_path = directory/'receipt.json'
    receipt = load(receipt_path)
    assert receipt['source_identity_unchanged']
    assert receipt['source_sha256_before'] == receipt['source_sha256_after']
    assert all(new_map[prefix+p] == h for p, h in receipt['source_sha256_before'].items())
    image = directory/('rook2-exact' if not prefix else 'rook2-diag-exact')
    assert sha(image) == receipt['binary_output']['sha256'] == summary[artifact_key]
    deps.append(receipt_path)
strict_path = ROOT/'evidence/king-first88-check-02-20261018/identity.json'
diag_path = ROOT/'evidence/king-first88-diagnostic-20261018/identity.json'
assert sha(strict_path) == summary['strict_identity_sha256']
assert sha(diag_path) == summary['diagnostic_identity_sha256']
assert load(diag_path)['independent_raw_response_equal'] == 6161
deps += [strict_path, diag_path]
for directory, expected in [('bounded-reply-king-first-cpu-pilot-20261018', 1.2474175839),
                            ('pgo-bounded-reply-cpu-pilot-20261018', 1.5126094717)]:
    pilot = ROOT/'evidence'/directory
    analysis = load(pilot/'analysis.json')
    assert analysis['complete'] and analysis['lifetimes_independently_reconciled'] == 60
    assert abs(analysis['percent_lower']-expected) < 0.000001
    assert load(pilot/'tool-terminal.json')['exit_code'] == 0
    deps += [pilot/'analysis.json', pilot/'tool-terminal.json']
dependency_hashes = {str(path): sha(path) for path in deps}
write(OUT/'before.json', dict(source_sha256=old_map, dependencies=dependency_hashes))
shutil.copy2(SOURCE/'src/movegen.rs', ROOT/'src/movegen.rs')
assert all(sha(ROOT/p) == h for p, h in new_map.items())
write(OUT/'integration.json', dict(
    status='Exact tested king-first88 source promoted', source_map=new_map,
    dependencies_sha256=dependency_hashes, changed=['src/movegen.rs'],
    native_artifact_sha256=summary['native_artifact_sha256'],
    diagnostic_artifact_sha256=summary['diagnostic_artifact_sha256'],
    native_tests=147, diagnostic_unit_tests=133, mandatory_operations=88,
    cases=6161, whole_fixture_files=83, strict_replays=54,
    interruption_fixtures=8, interruption_searches=24,
    no_canonical_path_rebuild=True,
    decision='Adopt saturated checked reply predicate after separate generic/own-PGO trials and fresh composed regression.',
    limits='Trial CPU results stay with frozen85 artifacts. Current88 composition has no own-PGO/cost/gameplay result.',
    script_sha256=sha(Path(__file__))))
preceding = ROOT/'evidence/quiescence-tree-integration-20261018/numeric-proof-delta-binding.json'
write(OUT/'numeric-proof-delta-binding.json', dict(
    preceding_binding=str(preceding), preceding_binding_sha256=sha(preceding),
    native_delta='Only saturated checked LIMIT2 witness order; EP prefix, legality and complete full order unchanged.',
    preserved_premises='Q discards result2 before recursion; session uses zero only. Exact0/1 lists remain complete. No arithmetic/state/domain changes.',
    limitations='Prior numerical/ownership premises and unresolved hint-composition domain remain. No global behavior or timing transfer.'))
print(json.dumps(dict(promoted=True, native_tests=147, mandatory_operations=88,
                      cases=6161, native_artifact_sha256=summary['native_artifact_sha256'])))
