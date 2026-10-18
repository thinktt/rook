#!/usr/bin/env python3
"""Recompute local54 measurements from native/wire receipts; no engine launch."""
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

OUT = Path(__file__).resolve().parent
COLLECTION = OUT / 'collection'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpu_ticks(context, name):
    return [int(x) for x in next(line for line in context['proc_stat'].splitlines()
                                if line.startswith(name + ' ')).split()[1:]]


def main():
    plan = read(OUT / 'plan.json')
    manifest = read(COLLECTION / 'manifest.json')
    summary = read(COLLECTION / 'summary.json')
    terminal = read(OUT / 'collector-terminal.json')
    workloads = read(SPEC / 'workloads.json')
    oracle = read(SPEC / 'replay-oracle.json')
    assert terminal['exit_code'] == 0
    assert summary['complete'] is True and summary['failure'] is None
    assert sha(Path(plan['engine'])) == plan['engine_sha256'] == manifest['engine_sha256']
    assert sha(OUT / 'collect54.py') == plan['collector_sha256']
    assert summary['artifact_sha256_after'] == plan['engine_sha256']
    for path, digest in manifest['input_sha256'].items():
        assert sha(Path(path)) == digest == summary['input_sha256_after'][path], path
    schedule = [dict(case=c['id'], repeat=i, warmup=i == 0)
                for c in workloads['cases'] for i in range(4)]
    assert manifest['schedule'] == schedule
    assert len(schedule) == len(summary['runs']) == 216
    assert len(summary['case_summaries']) == 54
    all_rows = []
    posts = 0
    for index, (step, reported) in enumerate(zip(schedule, summary['runs'])):
        directory = COLLECTION / f"{index:03d}-{step['case']}-r{step['repeat']}"
        native = read(directory / 'native.json')
        wire = read(directory / 'wire/receipt.json')
        config = read(directory / 'wire-config.json')
        comparator = read(directory / 'comparator.stdout')
        workload = next(c for c in workloads['cases'] if c['id'] == step['case'])
        expected = next(c for c in oracle['cases'] if c['id'] == step['case'])
        assert all(reported[k] == v for k, v in step.items())
        assert reported['failure'] is None and reported['comparator_exit'] == 0
        assert comparator['status'] == 'pass' and comparator['selectedCases'] == [step['case']]
        assert len(comparator['results']) == 1
        assert (directory / 'comparator.stderr').stat().st_size == 0
        assert native['failure'] is None and native['native_exit_code'] == 0
        assert native['engine_sha256_before'] == native['engine_sha256_after'] == plan['engine_sha256']
        assert native['native_pre_exec']['affinity'] == native['native_post_exec']['affinity'] == [14]
        assert native['native_post_exec']['tasks'] == [str(native['native_pid'])]
        assert native['supervisor_affinity'] == [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
        assert native['argv'] == [plan['engine'], *oracle['mode']]
        assert native['supervisor_pid'] == wire['launcherPid']
        assert wire['launcherExit'] == dict(code=0, signal=None)
        assert wire['failure'] is None and wire['pending'] is None
        assert wire['configSha256'] == sha(directory / 'wire-config.json')
        assert config['expectedArgv'] == wire['argv']
        assert len(wire['searches']) == 1
        search = wire['searches'][0]
        before, after = search['beforeWrite'], search['afterData']
        assert before['available'] and after['available']
        assert before['pid'] == after['pid'] == native['native_pid']
        assert before['startTicks'] == after['startTicks'] == wire['native']['startTicks']
        assert before['image'] == after['image'] == plan['engine']
        assert before['lastProcessor'] == after['lastProcessor'] == 14
        ticks = after['userTicks'] + after['systemTicks'] - before['userTicks'] - before['systemTicks']
        assert ticks > 0 and ticks == search['cpuTicks']
        assert search['cpuSeconds'] == ticks / wire['tickHz'] == reported['search_cpu_s']
        assert search['cpuUnavailableReason'] is None and wire['tickHz'] == 100
        assert search['wallNs'] == int(search['endMonotonicNs']) - int(search['startMonotonicNs'])
        assert search['wallNs'] == reported['search_wall_ns']
        assert search['move'] == expected['move']
        assert native['total_cpu_s'] == native['user_cpu_s'] + native['system_cpu_s'] == reported['cpu_s']
        assert native['wall_ns'] == native['reaped_monotonic_ns'] - native['start_monotonic_ns'] == reported['wall_ns']
        for name, receipt in wire['raw'].items():
            path = directory / 'wire' / (name + '.raw')
            assert sha(path) == receipt['sha256'] and path.stat().st_size == receipt['bytes']
            assert receipt['observedBytes'] == receipt['bytes'] and receipt['discardedObservedBytes'] == 0
        # Existing tap observes stdin.write; stdin.end('quit\n') is not captured.
        expected_stdin = '\n'.join(workload['protocol']['recordsBeforeSearch'] + ['cm_parm rnd', workload['protocol']['searchRecord']]) + '\n'
        assert (directory / 'wire/stdin.raw').read_text() == expected_stdin
        assert (directory / 'wire/stdout.raw').read_text() == comparator['results'][0]['stdout']
        assert (directory / 'wire/stderr.raw').stat().st_size == 0
        for relative, key in [('native.json', 'native_receipt_sha256'),
                              ('comparator.stdout', 'comparator_sha256'),
                              ('wire/receipt.json', 'wire_receipt_sha256')]:
            assert sha(directory / relative) == reported[key]
        posts += len(expected['posts'])
        all_rows.append(dict(**step, native_cpu_s=native['total_cpu_s'],
                             search_cpu_s=ticks / wire['tickHz'],
                             search_wall_s=search['wallNs'] / 1e9,
                             native_wall_s=native['wall_ns'] / 1e9))
    cases = []
    with Path('/home/legolas/spec-issues/v2.5.0/2026-10-18-imp2-candidate25-benchmark-results/comparison.csv').open() as stream:
        bee = {row['id']: row for row in csv.DictReader(stream)}
    for case in [c['id'] for c in workloads['cases']]:
        measured = [r for r in all_rows if r['case'] == case and not r['warmup']]
        assert len(measured) == 3
        row = dict(case=case)
        for metric in ['native_cpu_s', 'search_cpu_s', 'search_wall_s', 'native_wall_s']:
            values = [r[metric] for r in measured]
            row[metric] = dict(samples=values, median=statistics.median(values),
                               minimum=min(values), maximum=max(values))
        assert row['native_cpu_s']['median'] == summary['case_summaries'][case]['median']
        assert row['search_cpu_s']['median'] == summary['case_summaries'][case]['search_cpu_s']['median']
        row['bee_search_cpu_median_s'] = float(bee[case]['Rook_cpuMedianMs']) / 1000
        row['bee_div_vic_search_cpu'] = row['bee_search_cpu_median_s'] / row['search_cpu_s']['median']
        cases.append(row)
    totals = {metric: sum(c[metric]['median'] for c in cases)
              for metric in ['native_cpu_s', 'search_cpu_s', 'search_wall_s', 'native_wall_s']}
    assert totals['native_cpu_s'] == summary['sum_case_medians_s']
    assert totals['search_cpu_s'] == summary['sum_case_search_cpu_medians_s']
    bee_total = sum(c['bee_search_cpu_median_s'] for c in cases)
    assert math.isclose(bee_total, 75.77, abs_tol=1e-10)
    before = read(COLLECTION / 'context-before.json')
    after = read(COLLECTION / 'context-after.json')
    sibling_delta = [a - b for a, b in zip(cpu_ticks(after, 'cpu15'), cpu_ticks(before, 'cpu15'))]
    proof = dict(verified=True, engine_sha256=plan['engine_sha256'], cases=54,
                 lifetimes=216, excluded_warmups=54, measured=162, semantic_posts=posts,
                 medians_total_s=totals, bee_search_cpu_medians_total_s=bee_total,
                 bee_div_vic_search_cpu=bee_total / totals['search_cpu_s'],
                 bee_div_vic_per_case_range=[min(c['bee_div_vic_search_cpu'] for c in cases),
                                            max(c['bee_div_vic_search_cpu'] for c in cases)],
                 cpu15_guest_tick_delta=sibling_delta,
                 cpu15_nonidle_ticks=sum(sibling_delta[:3]) + sum(sibling_delta[4:8]),
                 context_before=before['utc'], context_after=after['utc'], case_results=cases,
                 scope='Informational local measurement; CPU14 pinning and finite observations do not prove exclusive ownership. No PMU or performance/gameplay qualification.',
                 input_tap_limit='stdin.write captured; cleanup sent through stdin.end is not captured. Released strict comparator and clean exits validate completed lifecycle.')
    (OUT / 'independent-reconciliation.json').write_text(json.dumps(proof, indent=2, allow_nan=False) + '\n')
    with (OUT / 'timings.csv').open('w') as stream:
        writer = csv.writer(stream)
        writer.writerow(['case', 'vic_search_cpu_median_s', 'vic_native_cpu_median_s',
                         'bee_search_cpu_median_s', 'bee_div_vic_search_cpu'])
        for row in cases:
            writer.writerow([row['case'], row['search_cpu_s']['median'], row['native_cpu_s']['median'],
                             row['bee_search_cpu_median_s'], row['bee_div_vic_search_cpu']])
    print(json.dumps({k: v for k, v in proof.items() if k != 'case_results'}))


if __name__ == '__main__':
    main()
