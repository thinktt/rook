"""Promote reviewed exact95 source only after completed functional and CPU gates."""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('/tmp/imp2-admission-combined95-20261018-n0_cyxa7')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    decision_path = OUT / 'decision.json'
    decision = load(decision_path)
    assert decision['promote_exact95'] is True and decision['cpu_pilot_actual_terminal_observed']
    old_path = ROOT / 'evidence/king-first88-integration-20261018/integration.json'
    old = load(old_path); old_map = old['source_map']
    assert len(old_map) == 97 and all(sha(ROOT / p) == h for p, h in old_map.items())
    manifest_path = ROOT / 'evidence/admission-combined95-proposal-20261018/source-manifest.json'
    new_map = load(manifest_path)
    assert len(new_map) == 99 and set(old_map).issubset(new_map)
    assert all(sha(SOURCE / p) == h for p, h in new_map.items())
    pilot = ROOT / 'evidence/admission-combined95-cpu-pilot-20261018'
    gate_path = pilot / 'regression-gate.json'; gate = load(gate_path)
    assert gate['complete'] and all(sha(Path(p)) == h for p, h in gate['dependencies'].items())
    analysis = load(pilot / 'analysis.json')
    assert analysis['complete'] and analysis['lifetimes_independently_reconciled'] == 60
    for p in [pilot / 'tool-terminal.json', pilot / 'reconcile-tool-terminal.json']:
        record = load(p)
        assert record['exit_code'] == 0 and record['actual_tool_terminal_observed']
    final_path = ROOT / 'evidence/diagnostic-admission-combined95-02-20261018/final-identity.json'
    final = load(final_path)
    assert final['source_manifest_sha256'] == sha(manifest_path)
    assert final['native_units'] == 151 and final['diagnostic_units'] == 149 and final['cases'] == 7393
    assert final['operations'] == 95 and final['whole_fixture_files'] == 89
    assert final['raw_original_expected_and_actual_exit_reconciled'] == 7393
    changed = [p for p in new_map if old_map.get(p) != new_map[p]]
    assert changed == ['diagnostic/src/admission.rs', 'diagnostic/src/boundary_admission.rs',
                       'diagnostic/src/cached_entry.rs', 'diagnostic/src/learned.rs',
                       'diagnostic/src/main.rs', 'diagnostic/src/supplied.rs',
                       'src/ordinary.rs', 'src/ordinary_policy.rs', 'src/quiescence.rs'], changed
    write('before.json', dict(source_map=old_map, changed=changed, previous_integration_sha256=sha(old_path)))
    for p in changed:
        (ROOT / p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / p, ROOT / p)
    assert all(sha(ROOT / p) == h for p, h in new_map.items())
    dependencies = {str(p): sha(p) for p in [old_path, decision_path, manifest_path, gate_path,
                    final_path, pilot / 'analysis.json', pilot / 'tool-terminal.json', pilot / 'reconcile-tool-terminal.json']}
    write('integration.json', dict(status='Reviewed exact tested95 source promoted', source_map=new_map,
          changed=changed, dependencies_sha256=dependencies,
          native_artifact_sha256=final['native_binary_sha256'], diagnostic_artifact_sha256=final['adapter_binary_sha256'],
          native_tests=151, diagnostic_unit_tests=149, strict_replays=54,
          interruption_fixtures=8, interruption_searches=24, mandatory_operations=95,
          cases=7393, whole_fixture_files=89, no_canonical_path_rebuild=True,
          material_codegen_risk=final['material_codegen_risk'],
          limits='Generic pilot is finite and reported-only. No canonical-path build, exact95 own-PGO, full54/12 cost, gameplay or reference qualification.',
          script_sha256=sha(Path(__file__))))
    previous = ROOT / 'evidence/king-first88-integration-20261018/numeric-proof-delta-binding.json'
    write('numeric-proof-delta-binding.json', dict(previous=str(previous), previous_sha256=sha(previous),
          native_delta='Share ordered repetition/clear/reversal, remaining-depth handoff, terminal mate scalar and effective evaluation endpoints/cutoff.',
          preserved='Explicit caller ply; repetition before clear_next before lazy reversal. Same absolute threshold and lower-before-upper comparison; effective pair reused later. No state/layout/charge/query chronology change.',
          bounded_leaf='New component only: reached-target caller supplies admission and S1 charge; lazy legal count only after draw/ceiling/check gates. Score ply-10000 retains bounded i32 range.',
          limits='Prior numerical/ownership premises and unresolved uncertified-hint composition domain remain. Cold controlled FastCutoff arithmetic is not a production fast-entry final kernel. No global proof or timing transfer.'))
    print(json.dumps(dict(promoted=True, changed=changed, operations=95, cases=7393)))


if __name__ == '__main__':
    main()
