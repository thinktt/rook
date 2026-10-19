#!/usr/bin/env python3
"""Independently recompute experiment42 native CPU samples and fixed decision."""
from pathlib import Path
import argparse
import hashlib
import json
import statistics
import subprocess


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True, type=Path)
    args = parser.parse_args()
    plan = read(args.plan)
    output = Path(plan['output'])
    terminal = read(output / 'tool-terminal.json')
    assert terminal['actual_tool_terminal_observed'] and terminal['exit_code'] == 0
    aggregate = read(output / 'result.json')
    assert aggregate['complete'] and aggregate['failure'] is None and aggregate['lifetimes'] == 70
    assert read(output / 'plan.json') == plan
    all_rows = []
    cases = []
    for case in plan['cases']:
        directory = output / case
        report = read(directory / 'summary.json')
        manifest = read(directory / 'manifest.json')
        assert report['complete'] and report['failure'] is None and len(report['runs']) == 10
        assert read(output / (case + '-terminal.json'))['exit_code'] == 0
        assert manifest['case'] == case
        assert manifest['variants'] == plan['variants']
        for path, digest in manifest['files'].items():
            assert sha(path) == digest
        for index, (schedule, row) in enumerate(zip(manifest['schedule'], report['runs'])):
            assert all(row[k] == v for k, v in schedule.items())
            run = directory / f'{index:02d}-{row["variant"]}'
            native = read(run / 'native.json')
            comparator = read(run / 'comparator.stdout')
            identity = plan['variants'][row['variant']]['sha256']
            assert row['failure'] is None and row['comparator_exit'] == 0
            assert native['failure'] is None and native['native_exit_code'] == 0 and native['native_wait_status'] == 0
            assert native['engine_sha256_before'] == native['engine_sha256_after'] == identity
            assert native['native_pre_exec']['affinity'] == native['native_post_exec']['affinity'] == [14]
            assert native['native_post_exec']['tasks'] == [str(native['native_pid'])]
            assert native['supervisor_affinity'] == [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
            assert native['total_cpu_s'] == native['user_cpu_s'] + native['system_cpu_s'] == row['native_cpu_s']
            assert native['wall_ns'] == row['native_wall_ns']
            assert native['argv'] == [plan['variants'][row['variant']]['path'], '--work-clock=kingwcr', '--work-clock-post=work']
            assert sha(run / 'native.json') == row['native_receipt_sha256']
            assert sha(run / 'comparator.stdout') == row['comparator_sha256']
            assert not (run / 'comparator.stderr').stat().st_size
            assert comparator['status'] == 'pass' and comparator['selectedCases'] == [case]
            assert len(comparator['results']) == 1
            all_rows.append(dict(case=case, repeat=row['repeat'], variant=row['variant'], warmup=row['warmup'],
                                 cpu_s=native['total_cpu_s'], native_pid=native['native_pid']))
        medians = {}
        statistics_by_variant = {}
        for name in plan['variants']:
            values = [r['cpu_s'] for r in all_rows if r['case'] == case and r['variant'] == name and not r['warmup']]
            assert len(values) == 4
            medians[name] = statistics.median(values)
            statistics_by_variant[name] = dict(samples=values, median=medians[name], minimum=min(values), maximum=max(values))
            assert statistics_by_variant[name] == report['summaries'][name]
        cases.append(dict(case=case, statistics=statistics_by_variant,
                          ratio=medians['candidate'] / medians['baseline']))
    assert len(all_rows) == 70 and len({r['native_pid'] for r in all_rows}) == 70
    assert sum(r['warmup'] for r in all_rows) == 14
    totals = {name: sum(c['statistics'][name]['median'] for c in cases) for name in plan['variants']}
    ratio = totals['candidate'] / totals['baseline']
    lower = sum(c['ratio'] < 1 for c in cases)
    worst = max(c['ratio'] for c in cases)
    advance = ratio <= .995 and lower >= 5 and worst <= 1.02
    for path, digest in plan['immutable_inputs'].items():
        assert sha(path) == digest
    for variant in plan['variants'].values():
        assert sha(variant['path']) == variant['sha256']
    command = ['/usr/bin/node', str(Path(__file__).resolve().parent / 'check_pilot.mjs'), str(args.plan)]
    oracle = subprocess.run(command, capture_output=True, text=True)
    with (output / 'independent-checkReplay.stdout').open('x') as stream:
        stream.write(oracle.stdout)
    with (output / 'independent-checkReplay.stderr').open('x') as stream:
        stream.write(oracle.stderr)
    assert oracle.returncode == 0 and not oracle.stderr
    assert json.loads(oracle.stdout) == dict(complete=True, originalCheckReplayCount=70, engineRuns=0)
    for path, digest in plan['immutable_inputs'].items():
        assert sha(path) == digest
    result = dict(complete=True, lifetimes=70, excluded_warmups=14, measured=56,
                  sum_case_medians_s=totals, candidate_div_baseline=ratio,
                  percent_lower=(1 - ratio) * 100, lower_cases=lower, worst_case_ratio=worst,
                  advance_under_declared_rule=advance, cases=cases, native_rows=all_rows,
                  no_outlier_deletion=True, original_checkReplay_count=70,
                  scope='Fixed seven-case informational native wait4 pilot; no PMU or full-corpus qualification.')
    with (output / 'independent-reconciliation.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['cases', 'native_rows']}))


if __name__ == '__main__':
    main()
