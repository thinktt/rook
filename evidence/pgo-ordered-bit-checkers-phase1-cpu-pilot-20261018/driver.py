"""Matched own-PGO ordered-bit checker pilot; whole native wait4 + strict replay."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from measure import cgroup_snapshot

CASES = ['profile-01', 'profile-02', 'profile-04', 'profile-05', 'profile-35', 'profile-29']
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
VARIANTS = {
    'baseline': ('pgo-bounded-reply-baseline', 'e49219753e437e072bb7a3ddd53fc270419ee3a84464428f5b676b55ec51ab4f',
                 '2e6ba24a4b4e240fad3601de17569a128ce9b12f5019cabe7cae8d5a259a1170'),
    'ordered_bits': ('pgo-ordered-bit-checkers-phase1', '7b17c00030363da52ce797e41cbbc29de4433ede4491c80d3799c7d08383d200',
                     'e55270f63f4683752f4f4255cd192d2b280cdff22deb44ee41a4d29bc90a06fa'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def native_processes():
    found = []
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():
            continue
        try:
            executable = os.readlink(process / 'exe')
            if Path(executable).name.startswith(('rook2', 'cargo', 'rustc', 'callgrind', 'valgrind', 'git',
                                                  'objdump', 'readelf', 'nm', 'llvm-profdata', 'c++filt')):
                found.append(dict(pid=int(process.name), executable=executable))
        except OSError:
            pass
    return found


def context():
    return dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                uname=list(os.uname()), helper_affinity=sorted(os.sched_getaffinity(0)),
                cgroups=cgroup_snapshot(), proc_stat=Path('/proc/stat').read_text(),
                loadavg=Path('/proc/loadavg').read_text(), native_processes=native_processes(),
                owned_background_work='All owned native jobs terminal; children restricted to small source/text work',
                isolation='Own-pane client109 threads corrected to housekeeping previously; other panes/system untouched. '
                          'Guest point-in-time snapshots do not establish sibling15 idle or exclusive host ownership.',
                pmu='No PMU data; self-open EACCES limitation remains')


def main():
    assert sorted(os.sched_getaffinity(0)) == HELPERS
    assert not native_processes(), 'Native build/test/engine/profiler remains live'
    prep = ROOT / 'evidence/pgo-ordered-bit-checkers-phase1-preparation-20261018'
    summary_path = prep / 'validation-summary.json'
    assert sha(summary_path) == 'f2e2a709db7574a7f64085ceb0518917337cf7b3f8f172a3f9004cbdb5c341b2'
    summary = load(summary_path)
    assert summary['all_owned_processes_terminal'] and summary['control_same_artifact_reuse']
    for key in ['new_training_replays', 'new_raw_pid_linked_profiles', 'new_post_use_strict_replays']:
        assert summary[key] == 54
    assert summary['new_interruption_fixtures'] == 8 and summary['new_interruption_searches'] == 24
    assert summary['independent_remerge_byte_identical'] and summary['native143_evidence_reused_exact_source']
    assert summary['missing_or_stale_function_warnings'] == 0
    independent = ROOT / 'evidence/pgo-ordered-bit-checkers-phase1-reconciliation-20261018/independent-verification.json'
    assert sha(independent) == summary['independent_verification_sha256']
    terminals = []
    for filename, record in summary['terminal_records'].items():
        assert record['exit_code'] == 0 and record['actual_tool_terminal_observed']
        assert load(Path(filename)) == record
        terminals.append(Path(filename))
    final_terminal = prep / 'finalize-tool-terminal.json'
    assert load(final_terminal)['exit_code'] == 0 and load(final_terminal)['all_owned_processes_terminal']
    reuse_path = prep / 'control-reuse.json'; reuse = load(reuse_path)
    assert sha(reuse_path) == summary['control_reuse_sha256']
    assert reuse['eligible_exact_same_control'] and not reuse['profile_transfer']
    generic = ROOT / 'evidence/ordered-bit-checkers-phase1-cpu-pilot-20261018'
    assert load(generic / 'tool-terminal.json')['exit_code'] == 0 and load(generic / 'analysis.json')['complete']
    common = [summary_path, independent, final_terminal, reuse_path, prep / 'validation-file-manifest.json',
              generic / 'analysis.json', generic / 'tool-terminal.json', *terminals]
    paths, validation, builds = {}, {}, {}
    for name, (stem, artifact_hash, profile_hash) in VARIANTS.items():
        build_path = ROOT / f'evidence/{stem}-use-build-20261018/receipt.json'
        build = load(build_path); builds[name] = build
        artifact = build_path.parent / 'rook2-exact'; paths[name] = artifact
        identity_path = ROOT / f'evidence/{stem}-use-check-20261018/identity.json'
        identity = load(identity_path)
        training_path = ROOT / f'evidence/{stem}-training-20261018/training.json'
        verification_path = training_path.parent / 'verification.json'
        training, verification = load(training_path), load(verification_path)
        profile = training_path.parent / 'merged.profdata'
        assert sha(artifact) == artifact_hash == identity['native_artifact_sha256'] == build['binary_output']['sha256']
        assert sha(build_path) == identity['build_receipt_sha256']
        assert sha(training_path) == identity['training_record_sha256']
        assert sha(verification_path) == identity['training_verification_sha256']
        assert sha(profile) == profile_hash == identity['profile_sha256'] == training['profile_sha256']
        assert training['complete'] and verification['complete'] and verification['strict_replays'] == 54
        assert identity['status'] == 'pass' and identity['strict_replays'] == 54
        assert identity['interruption_fixtures'] == 8 and identity['interruption_searches'] == 24
        assert identity['missing_function_warnings'] == 0
        assert build['pgo']['mode'] == 'profile-use' and build['cargo_exit_code'] == 0
        assert build['source_identity_unchanged'] and build['tool_identity_unchanged'] and build['cargo_config_unchanged']
        assert build['rust_flags'] == ['-C', 'target-cpu=x86-64', '-C', f'profile-use={profile}',
                                       '-C', 'llvm-args=-pgo-warn-missing-function']
        assert training['engine_source_sha256'] == build['source_sha256_before'] == build['source_sha256_after']
        expected_source = reuse['baseline_source_sha256'] if name == 'baseline' else summary['candidate_source_sha256']
        assert expected_source == build['source_sha256_before']
        assert build['tool_sha256_before'] == build['tool_sha256_after'] == summary['tool_source_sha256']
        for relative, digest in expected_source.items():
            assert sha(Path(build['crate']) / relative) == digest
        for relative, digest in summary['tool_source_sha256'].items():
            assert sha(ROOT / relative) == digest
        replay = identity_path.parent / 'profile-all.stdout'
        report = load(replay)
        assert sha(replay) == identity['replay_sha256'] and report['status'] == 'pass' and len(report['results']) == 54
        assert all(row['status'] == 'pass' and row['complete'] and not row['truncated']
                   and row['exit'] == {'code': 0, 'signal': None} and row['error'] is None
                   and row['stderr'] == '' and row['discardedObservedBytes'] == 0 for row in report['results'])
        wire = ROOT / f'evidence/{stem}-interruption-wire-20261018/receipt.json'; w = load(wire)
        assert sha(wire) == identity['wire_receipt_sha256'] and w['pass']
        assert len(w['results']) == 8 and sum(len(row['searches']) for row in w['results']) == 24
        assert w['engine_sha256_before'] == w['engine_sha256_after'] == artifact_hash
        validation[name] = {str(p): sha(p) for p in [*common, build_path, artifact, identity_path, training_path,
                                                   verification_path, profile, replay, wire]}
    for key in ['toolchain', 'target_triple', 'mode', 'target_cpu', 'cargo_config_sha256_before']:
        assert builds['baseline'][key] == builds['ordered_bits'][key]
    a, b = (builds[n]['source_sha256_before'] for n in VARIANTS)
    assert list(a) == list(b) and [p for p in a if a[p] != b[p]] == ['src/attacks.rs', 'src/movegen.rs']
    for filename, digest in reuse['corpus_current_sha256'].items():
        assert sha(Path(filename)) == digest
    write('validation-before.json', validation)
    write('suite.json', dict(cases=CASES, variants={n: dict(path=str(p), sha256=sha(p)) for n, p in paths.items()},
                            order='One warmup/variant then four alternating forward/reverse rounds per case',
                            driver_sha256=sha(Path(__file__)),
                            scope='Matched own-source PGO85 ordered-bit first-two checker trial only. '
                                  'No king-first, Q-bitview, known-check, observer88/95, old8d profile, '
                                  'final54/12 cost, gameplay or reference qualification transfer.'))
    before = context(); assert not before['native_processes']; write('context-before.json', before)
    results = {}
    for case in CASES:
        command = [sys.executable, str(ROOT / 'tools/compare_ordinary.py'), '--case', case, '--output', str(OUT / case)]
        for name, path in paths.items():
            command += ['--variant', name + '=' + str(path)]
        with (OUT / (case + '.stdout')).open('x') as out, (OUT / (case + '.stderr')).open('x') as err:
            child = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
        report = load(OUT / case / 'summary.json')
        assert child.returncode == 0 and report['complete'], (case, report['failure'])
        results[case] = report['summaries']
        print(json.dumps(dict(case=case, summaries=report['summaries'])), flush=True)
    after = context(); assert not after['native_processes']; write('context-after.json', after)
    assert all(sha(Path(p)) == h for files in validation.values() for p, h in files.items())
    write('suite-summary.json', dict(complete=True, summaries=results,
                                   artifact_hashes_after={n: sha(p) for n, p in paths.items()}))


if __name__ == '__main__':
    main()
