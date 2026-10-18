#!/usr/bin/env python3
"""Reconcile the finished run from original bytes; do not execute an engine."""
import hashlib
import json
from pathlib import Path
import re
import tarfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BUILD = ROOT / 'evidence/production-activity-specialization-use-build-20261018'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    provenance = load(OUT / 'provenance.json')
    plan = load(OUT / 'plan.json')
    terminal = load(OUT / 'tool-terminal.json')
    build = load(BUILD / 'receipt.json')
    assert terminal['exit_code'] == 0
    assert terminal['provenance_sha256'] == sha(OUT / 'provenance.json')
    assert provenance['complete'] and provenance['oracle']['exit_code'] == 0
    assert provenance['source_sha256'] == plan['source_sha256']
    assert provenance['source_sha256'] == build['source_sha256_before'] == build['source_sha256_after']
    identity = sha(BUILD / 'rook2-exact')
    assert identity == build['binary_output']['sha256'] == provenance['native_artifact_sha256'] == plan['artifact_sha256']
    assert plan['command'] == provenance['oracle']['command']
    assert plan['input_sha256'] == provenance['input_sha256']
    for path, digest in provenance['input_sha256'].items():
        assert sha(Path(path)) == digest, path
    archive = load(BUILD / 'archive-receipt.json')
    assert sha(BUILD / archive['archive']) == archive['sha256']
    assert archive['verified_against_build_before_hashes']
    archived = {}
    with tarfile.open(BUILD / archive['archive'], 'r:gz') as stream:
        for member in stream.getmembers():
            if member.isfile():
                data = stream.extractfile(member).read()
                archived[member.name] = hashlib.sha256(data).hexdigest()
    # Retained sources, rather than the later working tree, bind line attribution.
    for path, digest in provenance['source_sha256'].items():
        assert archived[path] == digest, path
    assert sha(OUT / 'profile-01.callgrind') == provenance['profile_sha256']
    assert sha(OUT / 'profile-01.log') == provenance['log_sha256']
    raw = (OUT / 'profile-01.callgrind').read_text()
    total = provenance['total_simulated_ir']
    assert re.findall(r'^events: (.+)$', raw, re.M) == ['Ir']
    assert re.findall(r'^summary: (\d+)$', raw, re.M) == [str(total)]
    assert re.findall(r'^totals: (\d+)$', raw, re.M) == [str(total)]
    log = (OUT / 'profile-01.log').read_text()
    assert re.search(r'Collected\s*:\s*' + str(total) + r'\b', log)
    oracle = provenance['oracle']
    assert sha(OUT / 'profile-01-oracle.stdout') == oracle['stdout_sha256']
    assert sha(OUT / 'profile-01-oracle.stderr') == oracle['stderr_sha256']
    assert not (OUT / 'profile-01-oracle.stderr').stat().st_size
    report = load(OUT / 'profile-01-oracle.stdout')
    assert report['status'] == 'pass' and report['selectedCases'] == ['profile-01']
    assert report['completeEngineQualification'] is False and len(report['results']) == 1
    result = report['results'][0]
    assert result['status'] == 'pass' and result['complete'] and not result['truncated']
    assert result['exit'] == {'code': 0, 'signal': None} and result['error'] is None
    assert result['stderr'] == ''
    for name, record in provenance['annotations'].items():
        assert record['exit_code'] == 0
        assert sha(OUT / (name + '.stdout')) == record['stdout_sha256']
        assert sha(OUT / (name + '.stderr')) == record['stderr_sha256']
        assert not (OUT / (name + '.stderr')).stat().st_size
    prior = load(ROOT / 'evidence/callgrind-eval-kernels-20261018/provenance.json')
    assert prior['total_simulated_ir'] == provenance['prior_8c_simulated_ir']
    ratio = total / prior['total_simulated_ir']
    assert ratio == provenance['ratio_to_previous_8c']
    answer = dict(complete=True, native_artifact_sha256=identity,
                  native_source_files=len(provenance['source_sha256']),
                  total_simulated_ir=total, prior_8c_simulated_ir=prior['total_simulated_ir'],
                  ratio_to_prior=ratio, percent_fewer=100 * (1 - ratio),
                  provenance_sha256=sha(OUT / 'provenance.json'),
                  actual_terminal_sha256=sha(OUT / 'tool-terminal.json'),
                  reconciler_sha256=sha(Path(__file__)),
                  scope='Independent retained-byte reconciliation; simulated Ir only, no engine execution or PMU/native timing claim')
    with (OUT / 'verification.json').open('x') as stream:
        json.dump(answer, stream, indent=2)
        stream.write('\n')
    print(json.dumps(answer))


if __name__ == '__main__':
    main()
