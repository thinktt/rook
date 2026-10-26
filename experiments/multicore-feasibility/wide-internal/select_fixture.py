#!/usr/bin/env python3
"""Independently select one external wide-parent fixture from three bound captures."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from build import HERE, admit, baseline, snapshot, sha, read

CASES = ['profile-35', 'profile-08', 'profile-43']
FIXTURE_KEYS = ['schema', 'case', 'horizon', 'parent_ordinal', 'binding_hex']


def count(value):
    assert type(value) is int and value >= 0
    return value


def binding(value):
    assert type(value) is str and value and len(value) % 2 == 0
    assert all(c in '0123456789abcdef' for c in value)
    bytes.fromhex(value).decode('utf-8')
    return value


def descriptor(case, parent):
    assert case in CASES and count(parent['entry_ordinal']) > 0
    return dict(schema='rook2-wide-fixture-v1', case=case, horizon=8,
        parent_ordinal=parent['entry_ordinal'], binding_hex=binding(parent['binding_hex']))


def read_fixture(path):
    assert Path(path).stat().st_size <= 4*1024*1024
    lines = Path(path).read_text().splitlines()
    pairs = [line.split('=', 1) for line in lines]
    assert len(pairs) == 5 and all(len(pair) == 2 for pair in pairs)
    value = dict(pairs); assert len(value) == 5 and set(value) == set(FIXTURE_KEYS)
    assert value['schema'] == 'rook2-wide-fixture-v1' and value['case'] in CASES and value['horizon'] == '8'
    assert value['parent_ordinal'].isdigit() and not value['parent_ordinal'].startswith('0')
    value['horizon'], value['parent_ordinal'] = 8, int(value['parent_ordinal'])
    binding(value['binding_hex'])
    return value


def audit_parent(parent, canonical_nodes):
    ordinal = count(parent['entry_ordinal']); assert ordinal > 0
    assert type(parent['depth']) is int and parent['depth'] >= 3
    assert 1 <= count(parent['ply']) < 64 and 1 <= count(parent['iteration']) <= 8
    window = parent['window']; assert type(window) is list and len(window) == 2
    assert all(type(v) is int for v in window)
    assert -10000 < window[0] < window[1] < 10000
    assert count(parent['remaining']) >= 8
    assert type(parent['best']) is int
    assert count(parent['child0_nodes']) <= canonical_nodes
    children = parent['children']; assert type(children) is list and len(children) <= 8
    assert [row['index'] for row in children] == list(range(1, len(children)+1))
    previous_best = parent['best']
    for child in children:
        assert type(child['complete']) is bool and type(child['best_changed']) is bool
        assert count(child['movement']) <= 65535
        for key in ['nodes', 'relations', 'full', 'fast', 'maps', 'retries']:
            count(child[key])
        assert child['nodes'] <= canonical_nodes
        for key in ['best_before', 'best_after', 'score']:
            assert type(child[key]) is int
        assert child['best_before'] == previous_best
        assert child['best_after'] >= child['best_before']
        assert child['best_changed'] == (child['best_after'] != child['best_before'])
        previous_best = child['best_after']
        requests = child['requests']; assert type(requests) is list and requests
        assert child['retries'] == len(requests)-1
        first = requests[0]
        assert first['ply'] == parent['ply']+1 and first['iteration'] == parent['iteration']
        assert first['lower'] == -window[1] and first['upper'] == -max(window[0], child['best_before'])
        for request in requests:
            assert set(request) == {'ply', 'depth', 'lower', 'upper', 'previous_extension', 'iteration', 'checked'}
            assert all(type(request[key]) is int for key in request if key != 'checked')
            assert 1 <= request['ply'] < 64 and 1 <= request['iteration'] <= 8
            assert request['lower'] < request['upper']
            assert request['checked'] is None or type(request['checked']) is bool
    qualifies = (len(children) == 8 and all(c['complete'] and c['nodes'] >= 512 for c in children)
                 and sum(c['nodes'] for c in children) >= 8192)
    assert type(parent['qualifies']) is bool and parent['qualifies'] == qualifies
    if qualifies:
        binding(parent['binding_hex'])
    else:
        assert parent['binding_hex'] is None
    return qualifies


def audit_report(report):
    assert report['schema'] == 'rook2-wide-capture-v1' and report['horizon'] == 8
    assert type(report['complete']) is bool and type(report['censored']) is bool
    assert report['censored'] == (report['censor_reason'] is not None)
    assert count(report['canonical_nodes']) > 0
    count(report['canonical_relations']); count(report['ordinary_entries'])
    for key in ['fixed_completion', 'no_host', 'zero_randomness']:
        assert report[key] is True
    limits = read(HERE/'policy.json')['captureLimits']
    assert report['caps'] == dict(candidate_parents=limits['parentRecords'], retained_bytes=limits['retainedBytes'],
        output_bytes=limits['reportBytes'], lifetime_seconds=limits['perLifeSeconds'])
    assert count(report['retained_bytes']) <= count(report['peak_retained_bytes']) <= 67108864
    assert count(report['wall_ns']) > 0 and count(report['process_cpu_ns']) > 0
    if report['complete']:
        assert not report['censored'] and report['error'] is None and report['completed_depth'] == 8
    count(report['root_passes'])
    parents = report['parents']; assert type(parents) is list and len(parents) <= 131072
    ordinals = [parent['entry_ordinal'] for parent in parents]
    assert ordinals == sorted(set(ordinals))
    assert all(ordinal <= report['ordinary_entries'] for ordinal in ordinals)
    qualifiers = [p for p in parents if audit_parent(p, report['canonical_nodes'])]
    audit_coverage(report, qualifiers)
    return qualifiers


def work_bin(n):
    for i, upper in enumerate([0, 127, 511, 1023, 2047, 4095, 8191]):
        if n <= upper:
            return i
    return 7


def audit_coverage(report, qualifiers):
    value = report['coverage']; parents = report['parents']
    for key, item in value.items():
        if key == 'work_bins':
            continue
        if type(item) is list:
            for number in item:
                count(number)
        else:
            count(item)
    fields = ['post_child0', 'finite_window', 'depth_ge3', 'width_ge8']
    counts = [count(value[key]) for key in fields]
    assert all(a >= b for a, b in zip(counts, counts[1:]))
    if report['complete'] and not report['censored']:
        assert counts[-1] == len(parents)
    else:
        assert counts[-1] >= len(parents)
    completed, minima, sums = [0]*9, [0]*8, [0]*8
    for parent in parents:
        children = parent['children']; n = sum(child['complete'] for child in children)
        completed[n] += 1
        if n == 8:
            minima[work_bin(min(c['nodes'] for c in children))] += 1
            sums[work_bin(sum(c['nodes'] for c in children))] += 1
    assert value['completed_hist'] == completed and value['minimum_child_nodes_hist'] == minima and value['sum8_hist'] == sums
    assert value['completed8'] == completed[8] and value['qualified'] == len(qualifiers)
    assert count(value['max_remaining']) >= max([p['remaining'] for p in parents]+[0])
    assert value['max_completed'] == max([sum(c['complete'] for c in p['children']) for p in parents]+[0])
    assert value['max_child_nodes'] == max([c['nodes'] for p in parents for c in p['children']]+[0])
    assert value['max_sum8'] == max([sum(c['nodes'] for c in p['children']) for p in parents
        if len(p['children']) == 8 and all(c['complete'] for c in p['children'])]+[0])
    assert value['work_bins'] == ['0', '1..127', '128..511', '512..1023', '1024..2047', '2048..4095', '4096..8191', '8192+']


def admit_captures(base):
    # Import the shared read-only receipt checker after module initialization;
    # select_fixture owns all capture eligibility/selection logic independently
    # from the native capture's advertised qualifies flag.
    from reconcile import admit_raw
    plan, result, chosen, build, lives = admit_raw(base, 'capture')
    reports = {}
    for row in lives:
        report, native = row['report'], row['native']
        audit_report(report)
        assert report['wall_ns'] <= native['wall_ns']
        assert report['process_cpu_ns'] <= native['total_cpu_s']*10**9+2_000_000
        reports[row['step']['case']] = report
    provenance = dict(binarySha256=plan['binarySha256'], sourcePins=plan['sourcePins'],
        rawSha256={name: sha(base/name) for name in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after', 'housekeeping-restore.json']},
        reportSha256={row['case']: row['sha256']['stdout'] for row in result['runs']})
    return reports, provenance


def select(reports):
    assert set(reports) == set(CASES)
    qualifiers, summary = {}, {}
    for case in CASES:
        report = reports[case]; qualifiers[case] = audit_report(report)
        summary[case] = dict(complete=report['complete'], censored=report['censored'],
            censorReason=report['censor_reason'], ordinaryEntries=report['ordinary_entries'],
            recordedParents=len(report['parents']), qualifyingParents=len(qualifiers[case]),
            completedEightParents=sum(len(p['children']) == 8 and all(c['complete'] for c in p['children']) for p in report['parents']),
            maximumMinimumChildNodes=max([min(c['nodes'] for c in p['children'])
                for p in report['parents'] if len(p['children']) == 8 and all(c['complete'] for c in p['children'])]+[0]),
            maximumCompletedEightNodes=max([sum(c['nodes'] for c in p['children'])
                for p in report['parents'] if len(p['children']) == 8 and all(c['complete'] for c in p['children'])]+[0]))
    if not all(reports[case]['complete'] and not reports[case]['censored'] for case in CASES):
        return None, None, summary, 'capture-incomplete-or-censored'
    for case in CASES:
        if qualifiers[case]:
            parent = min(qualifiers[case], key=lambda p: p['entry_ordinal'])
            return descriptor(case, parent), parent, summary, None
    return None, None, summary, 'no-qualifying-parent'


def admit_selection(path, fixture_path=None):
    receipt = read(path)
    assert receipt['schema'] == 'rook2-wide-fixture-selection-v1' and receipt['complete'] is True
    assert receipt['selectorSha256'] == sha(Path(__file__))
    reports, provenance = admit_captures(Path(receipt['capture']))
    selected, parent, summary, stop = select(reports)
    assert receipt['captureProvenance'] == provenance
    assert receipt['selected'] == selected and receipt['selectedParent'] == parent
    assert receipt['summaries'] == summary and receipt['stopReason'] == stop
    recorded = Path(receipt['fixturePath'])
    if fixture_path is not None:
        assert recorded == fixture_path
    if selected is None:
        assert not recorded.exists() and receipt['fixtureSha256'] is None
    else:
        assert sha(recorded) == receipt['fixtureSha256'] and read_fixture(recorded) == selected
    return receipt, reports


def write_exclusive(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); base = args.capture.resolve(); output = args.output.resolve()
    receipt_path = output.with_name('fixture-selection.json')
    assert not output.exists() and not receipt_path.exists()
    reports, provenance = admit_captures(base)
    selected, parent, summary, stop = select(reports)
    if selected is not None:
        with output.open('x') as stream:
            stream.write(''.join(f'{key}={selected[key]}\n' for key in FIXTURE_KEYS))
        assert read_fixture(output) == selected
    receipt = dict(schema='rook2-wide-fixture-selection-v1', complete=True,
        capture=str(base), captureProvenance=provenance, selected=selected,
        selectedParent=parent, summaries=summary, stopReason=stop,
        fixturePath=str(output), fixtureSha256=sha(output) if selected is not None else None,
        selectorSha256=sha(Path(__file__)),
        scope='Future-informed external benchmark fixture only; fixed case35/08/43 then smallest canonical ordinary-entry ordinal. Eight siblings are disjoint within one parent; overlapping parent opportunities are never summed as available parallel work. Descriptor carries known-input identity only and no expected work/output/effects. No runtime prediction or engine-gain claim.')
    write_exclusive(receipt_path, receipt)
    print('selected '+selected['case']+' parent '+str(selected['parent_ordinal']) if selected else 'no fixture: '+stop, flush=True)


if __name__ == '__main__':
    main()
