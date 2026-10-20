#!/usr/bin/env python3
"""Offline recheck of the one closed calibration/collection; never launch native."""
import argparse
import json
from pathlib import Path
import collect


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, required=True)
    a = ap.parse_args()
    b = a.evidence.resolve(strict=True)
    authority = collect.load(b / 'execution-clearance.closed.json')
    calibration = collect.load(b / 'calibration/calibration.json')
    result = collect.load(b / 'collection/result.json')
    closure = collect.bindings(Path(result['input_closure']['engine']), authority)
    assert calibration['complete'] and result['complete']
    assert calibration['input_closure'] == result['input_closure'] == closure
    units = {u['id']: u for u in collect.load(collect.PUBLIC / 'functional-workloads.json')['units']}
    pids, projections, measurements = [], 0, 0
    for stage, count in [('calibration', 4), ('collection', 48)]:
        terminal = collect.load(b / stage / 'tool-terminal.json')
        assert terminal['actual_tool_terminal_observed'] and terminal['exit_code'] == 0
        records = sorted((b / stage).rglob('native.json'))
        assert len(records) == count
        for p in records:
            n = collect.load(p)
            child = collect.load(p.parent / 'child-terminal.json')
            assert child['returncode'] == 0 and child['failure'] is None
            assert child['raw_capture_complete'] and child['cleanup_confirmed']
            assert n['failure'] is None and n['native_wait_status'] == 0 and n['known_single_process']
            assert n['engine_sha256_before'] == n['engine_sha256_after'] == closure['engine_sha256']
            assert n['native_post_exec']['affinity'] == [14]
            assert n['native_post_exec']['tasks'] == [str(n['native_pid'])]
            assert n['supervisor_affinity'] == sorted(collect.H)
            assert (p.parent / 'stderr').stat().st_size == 0
            row = n['argv'][n['argv'].index('--row') + 1]
            mode = n['argv'][n['argv'].index('--mode') + 1]
            iterations = int(n['argv'][n['argv'].index('--iterations') + 1])
            input_path = Path(n['argv'][n['argv'].index('--input') + 1])
            unit_id = next(u for r, u, _, _ in collect.ROWS if r == row)
            unit = units[unit_id]
            collect.exact(collect.load(input_path), unit['workload']['request']['input'], 'native input')
            obs = collect.load(p.parent / 'stdout')
            expected = unit['expectedProjection']
            nn, rr = ((54, 234) if row == 'search' else
                      (0, sum(x['relationQueries'] for x in expected['results']))
                      if row.startswith('eval-') else (0, 0))
            collect.checked_observation(obs, row, iterations,
                                        {'chargedSearchUnits': nn, 'chargedRelationQueries': rr},
                                        expected if mode == 'verify' else None)
            if mode == 'verify':
                projections += 1
            else:
                measurements += 1
                assert obs['local_cpu_ns'] <= n['total_cpu_s'] * 1e9
            pids.append(n['native_pid'])
    assert len(set(pids)) == 52 and projections == 32 and measurements == 20
    # Recompute per-sequence statistics directly from the saved measured observations.
    summaries = []
    for row in result['rows']:
        samples = [collect.load(b / 'collection' / row['row'] / ('measured-' + str(i)) / 'stdout')
                   for i in (1, 2, 3)]
        ns = sorted(x['local_cpu_ns'] / x['completed'] for x in samples)
        assert ns == [row['local_cpu_ns_per_sequence'][k] for k in ('min', 'median', 'max')]
        summaries.append({'row': row['row'], 'local_cpu_ns_min_median_max': ns})
    def cpu15(p):
        text = collect.load(p)['proc_stat']
        return [int(x) for line in text.splitlines() if line.startswith('cpu15 ') for x in line.split()[1:]]
    before = cpu15(b / 'collection/context-before.json')
    after = cpu15(b / 'collection/context-after.json')
    output = {'complete': True, 'offline_only': True, 'unique_native_pids': 52,
              'exact_original_projections': 32, 'measurement_outputs_including_probes': 20,
              'source_and_provenance_closure_still_exact': True,
              'cpu15_proc_stat_tick_deltas': [y - x for x, y in zip(before, after)],
              'cpu15_scope': 'Guest point snapshots only; no continuous host exclusion claim',
              'rows': summaries}
    collect.save(b / 'offline-verification.json', output)
    print(json.dumps(output))


if __name__ == '__main__':
    main()
