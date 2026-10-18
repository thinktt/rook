"""Bind completed generic88king/95 regressions before a CPU-only experiment."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def main():
    dependencies = {}

    def bind(path, expected=None):
        digest = sha(path)
        if expected is not None:
            assert digest == expected, str(path)
        dependencies[str(path)] = digest
        return load(path)

    final_path = ROOT / 'evidence/diagnostic-admission-combined95-02-20261018/final-identity.json'
    final = bind(final_path, '3d65acef5699df28f1ccdef5ea4b3b81a8568abc050c745b3a54c83d14d9eceb')
    assert [final[k] for k in ['native_units', 'strict_replays', 'interruption_fixtures', 'interruption_searches',
                               'diagnostic_units', 'cases', 'operations', 'whole_fixture_files']] == [151, 54, 8, 24, 149, 7393, 95, 89]
    assert final['owned_live_processes'] == final['partial_files'] == final['duplicate_ids'] == 0
    assert final['source_fixes_after_frozen95'] == 0 and final['same_source_bytes_after_home_relocation']
    closure = bind(final_path.with_name('final-closure.json'), '1755fdfbedde41db21d53611a04d542eec20c54d71455065c2067c4bc7b6cfcb')
    assert closure['no_owned_native_jobs'] and closure['final_identity_sha256'] == sha(final_path)
    # Verify every retained dependency, including the independent raw/expected/exit result.
    for filename, expected in final['evidence_sha256'].items():
        assert sha(Path(filename)) == expected, filename
        dependencies[filename] = expected
    old_path = ROOT / 'evidence/king-first88-validation-20261018/validation-summary.json'
    old = bind(old_path)
    assert old['all_owned_processes_terminal'] and old['all_raw_cases_independently_reconciled']
    assert old['native_tests'] == 147 and old['strict_replays'] == 54 and old['interruption_searches'] == 24
    for filename, record in old['terminal_records'].items():
        assert bind(ROOT / filename) == record and record['exit_code'] == 0
    manifest_path = ROOT / 'evidence/admission-combined95-proposal-20261018/source-manifest.json'
    candidate = bind(manifest_path, final['source_manifest_sha256'])
    assert len(candidate) == 99
    source_roots = {
        'baseline': Path(old['source_root']),
        'admission95': Path('/tmp/imp2-admission-combined95-20261018-n0_cyxa7'),
    }
    source_maps = {'baseline': old['source_map'], 'admission95': candidate}
    variants, builds = {}, {}
    for name, stem, digest, check_stem, wire_stem in [
        ('baseline', 'king-first88-build-20261018', old['native_artifact_sha256'],
         'king-first88-check-02-20261018', 'king-first88-interruption-wire-02-20261018'),
        ('admission95', 'admission-combined95-native-build-20261018', final['native_binary_sha256'],
         'admission-combined95-check-20261018', 'admission-combined95-wire-20261018'),
    ]:
        directory = ROOT / 'evidence' / stem
        build = bind(directory / 'receipt.json'); builds[name] = build
        assert build['mode'] == 'generic' and build['pgo']['mode'] == 'none'
        assert build['rust_flags'] == ['-C', 'target-cpu=x86-64'] and build['cargo_exit_code'] == 0
        assert build['source_identity_unchanged'] and build['tool_identity_unchanged']
        assert build['source_sha256_before'] == build['source_sha256_after']
        assert build['tool_sha256_before'] == build['tool_sha256_after']
        for p, h in source_maps[name].items():
            assert sha(source_roots[name] / p) == h, (name, p)
        assert all(source_maps[name][p] == h for p, h in build['source_sha256_before'].items())
        image = directory / 'rook2-exact'
        assert sha(image) == digest == build['binary_output']['sha256']
        check = bind(ROOT / 'evidence' / check_stem / 'identity.json')
        assert check['native_artifact_sha256'] == digest and check['build_receipt_sha256'] == sha(directory / 'receipt.json')
        # The strict wire receipt is found by its retained identity hash, not assumed basename.
        matching_wire = [p for p in (ROOT / 'evidence').glob('*wire*/receipt.json')
                         if p.parent.name.startswith(('king-first88-', 'admission-combined95-'))
                         and sha(p) == check['wire_receipt_sha256']]
        assert len(matching_wire) == 1, name
        wire = bind(matching_wire[0])
        assert wire['pass'] and len(wire['results']) == 8 and sum(len(r['searches']) for r in wire['results']) == 24
        assert wire['engine_sha256_before'] == wire['engine_sha256_after'] == digest
        variants[name] = dict(path=str(image), sha256=digest)
    for key in ['toolchain', 'target_triple', 'target_cpu', 'rust_flags', 'tool_sha256_before', 'cargo_config_sha256_before']:
        assert builds['baseline'][key] == builds['admission95'][key], key
    native_changes = [p for p, h in builds['baseline']['source_sha256_before'].items()
                      if h != builds['admission95']['source_sha256_before'][p]]
    assert native_changes == ['src/ordinary.rs', 'src/ordinary_policy.rs', 'src/quiescence.rs'], native_changes
    dependencies[str(Path(__file__))] = sha(Path(__file__))
    result = dict(complete=True, variants=variants, dependencies=dependencies,
                  native_source_changes=native_changes, source_roots={n: str(p) for n, p in source_roots.items()},
                  material_codegen_risk=final['material_codegen_risk'],
                  scope='Generic own-source88king versus95 scalar extraction trial. No PGO or final qualification transfer.')
    with (OUT / 'regression-gate.json').open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(complete=True, native_source_changes=native_changes, variants=variants)))


if __name__ == '__main__':
    main()
