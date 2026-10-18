#!/usr/bin/env python3
"""Reconcile original diagnostic counts and strict outcomes without engine runs."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    manifest, summary = load(OUT/'manifest.json'), load(OUT/'summary.json')
    terminal = load(OUT/'tool-terminal.json')
    assert terminal['exit_code'] == 0 and terminal['summary_sha256'] == sha(OUT/'summary.json')
    assert summary['complete'] and len(summary['rows']) == len(manifest['case_order']) == 54
    assert manifest['input_sha256'] == summary['input_sha256_after']
    assert all(sha(Path(p)) == h for p, h in manifest['input_sha256'].items())
    assert manifest['helper_affinity'] == [0,1,2,3,4,5,8,9,10,11,12,13]
    keys = {'null_trials','null_positive_map','null_to_quiescence','influence_builds','full','fast'}
    totals = dict.fromkeys(sorted(keys), 0)
    inputs = {}
    for case, row in zip(manifest['case_order'], summary['rows']):
        assert row['case'] == case and row['comparator_exit'] == 0
        directory = OUT/case
        counts = load(directory/'counts.json')
        report = load(directory/'comparator.stdout')
        assert counts == row['counts'] and set(counts) == keys
        assert all(type(v) is int and v >= 0 for v in counts.values())
        assert counts['null_positive_map'] + counts['null_to_quiescence'] <= counts['null_trials']
        assert counts['null_positive_map'] <= counts['influence_builds']
        assert sha(directory/'counts.json') == row['counts_sha256']
        assert sha(directory/'comparator.stdout') == row['oracle_sha256']
        assert report['status'] == 'pass' and report['selectedCases'] == [case]
        assert len(report['results']) == 1 and not (directory/'comparator.stderr').stat().st_size
        for name in ['counts.json','comparator.stdout','comparator.stderr']:
            inputs[str(directory/name)] = sha(directory/name)
        for key in keys:
            totals[key] += counts[key]
    assert totals == summary['totals']
    fraction = totals['null_positive_map']/totals['influence_builds']
    assert fraction == summary['positive_null_build_fraction']
    result = dict(complete=True, strict_cases_independently_reconciled=54,
                  totals=totals, positive_null_build_fraction=fraction,
                  terminal_sha256=sha(OUT/'tool-terminal.json'),
                  input_receipts_sha256=inputs, reconciler_sha256=sha(Path(__file__)),
                  decision='Park positive ordinary null-only reuse; 0.768% of map builds is a small opportunity before added admission/copy cost.',
                  boundary_scope='Null-to-Q entries are not direct map-build counts. No reuse benefit established there.',
                  scope='Frozen8c D=true diagnostic derivative; no native CPU/PMU savings or current artifact timing interpretation.')
    with (OUT/'verification.json').open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({k:result[k] for k in ['complete','totals','positive_null_build_fraction']}))


if __name__ == '__main__':
    main()
