#!/usr/bin/env python3
"""Independent bounded pure-result census ledger/cost audit; no native execution."""
import argparse
import collections
import json
import math
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from build import HERE, HELPERS, admit, baseline, snapshot, sha, read
CASES = ['profile-35', 'profile-08', 'profile-43']
KINDS = ['influence', 'chain']
SCOPES = ['coordinator', *['queued-'+str(i) for i in range(7)], 'suffix']
PAYLOAD = dict(influence=128, chain=48)
CATEGORIES = ['total', 'pooled', 'same_intended_child', 'matched_prior_prefix',
    'matched_prefix_absent', 'producer_first', 'canonical_earlier', 'serial_cache_prior']
COST_FIELDS = ['capture_dedup_observer_ns', 'key_construction_ns', 'lookup_full_equality_ns',
    'materialization_ns', 'materialized_bytes', 'epoch_check_ns']
CAPS = dict(producer_nodes=262144, producer_keys=262144, producer_calls=4194304,
    producer_bytes=67108864, pool_keys=1835008, pool_calls=29360128,
    pool_bytes=536870912, demand_keys=262144, demand_calls=4194304,
    demand_bytes=134217728, prefix_calls=4194304, prefix_bytes=134217728,
    json_output_bytes=268435456, mechanism_bytes=2147483648,
    process_bytes=8589934592, lifetime_seconds=180)

def count(value):
    assert type(value) is int and value >= 0, ('nonnegative integer', value)
    return value

def checked_preparation(path):
    prep = read(path); directory = path.parent
    assert prep['schema'] in ['rook2-internal-split-preparation-run-v1', 'rook2-wide-preparation-run-v1', 'rook2-coarse-pure-preparation-run-v1']
    assert prep['complete'] is True and prep['failure'] is None
    assert prep['sourceBefore'] == prep['sourceAfter']
    assert prep['baselineBefore'] == prep['baselineAfter']
    for name, digest in prep['sourceBefore'].items():
        assert sha(directory/'source-before'/name) == digest
    for name, digest in prep['tools'].items():
        assert sha(name) == digest
    selectors = prep['selectors']
    assert selectors and len(selectors) == len(set(selectors))
    stages = prep['stages']; assert len(stages) == len(selectors)+1
    tests = []
    for i, stage in enumerate(stages):
        expected = f'tests-{i:02d}' if i < len(selectors) else 'build'
        assert stage['stage'] == expected and stage['exit'] == 0 and count(stage['wallNs']) > 0
        assert sha(directory/(expected+'.stdout')) == stage['stdoutSha256']
        assert sha(directory/(expected+'.stderr')) == stage['stderrSha256']
        if i < len(selectors):
            assert stage['argv'][-3:] == [selectors[i], '--', '--test-threads=1']
            names = stage['passedTests']; assert names
            assert all(name.startswith(selectors[i]) for name in names)
            text = (directory/(expected+'.stdout')).read_text()
            assert all(f'test {name} ... ok\n' in text for name in names)
            assert f'test result: ok. {len(names)} passed; 0 failed; 0 ignored;' in text
            tests.extend(names)
    assert len(tests) == len(set(tests)) == prep['focusedTests'] > 0
    return prep

def audit_inputs():
    spec_path = Path('/home/legolas/king-spec/conformance/profiling/workloads.json')
    cases = read(spec_path)['cases']
    for name in ['profile-35']:
        case, = [c for c in cases if c['id'] == name]
        assert case['position']['initial'] == 'standard-start'
        parameters = case['personality']['parameters']
        expected = dict(case=name, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            moves=' '.join(case['position']['moves']), randomness='0')
        fields = dict(own=['myp', 'myn', 'myb', 'myr', 'myq', 'myk', 'mycc', 'mymob', 'myks', 'mypp', 'mypw'],
            opponent=['opp', 'opn', 'opb', 'opr', 'opq', 'opk', 'opcc', 'opmob', 'opks', 'oppp', 'oppw'],
            evaluation=['avd', 'cfd', 'sop'], search=['sel', 'md', 'tts', 'ana'])
        for field, keys in fields.items():
            expected[field] = ','.join(str(parameters[k]) for k in keys)
        assert parameters['rnd'] == 0
        lines = (HERE/'inputs'/(name+'.txt')).read_text().splitlines()
        entries = [line.split('=', 1) for line in lines if line and not line.startswith('#')]
        assert len(entries) == len(dict(entries)) and dict(entries) == expected

def pid_and_group_gone(pids, groups):
    for pid in pids:
        assert not Path(f'/proc/{pid}').exists(), ('recorded PID is live; inspect reuse', pid)
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            stat = (proc/'stat').read_text()
        except (FileNotFoundError, ProcessLookupError):
            continue
        group = int(stat[stat.rfind(')')+2:].split()[2])
        assert group not in groups, ('recorded process group is live; inspect reuse', group)

def audit_native(directory, image, options, row, chosen):
    native, terminal = read(directory/'native.json'), read(directory/'terminal.json')
    assert native['schema'] == 'rook2-internal-native-wait4-v1'
    assert native['failure'] is None and native['native_exit_code'] == native['native_wait_status'] == 0
    assert native['engine'] == str(image) and native['argv'] == [str(image), *options]
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
    assert native['supervisor_affinity'] == [chosen['supervisorCpu']]
    assert native['native_pid'] == row['nativePid'] and native['supervisor_pid'] == row['supervisorPid']
    assert native['native_pid'] != native['supervisor_pid']
    assert native['native_pre_exec'] == [dict(pid=native['native_pid'], pgid=native['supervisor_pid'], affinity=[14])]
    observed = native['native_post_exec']
    # /proc observation can race a very short process; these lives enclose two
    # fixed searches, so require the actual native image to have been observed.
    assert observed is not None and observed['exe'] == str(image)
    assert observed['tasks'] == [str(native['native_pid'])]
    status = dict(line.split(':', 1) for line in observed['status'].splitlines() if ':' in line)
    assert int(status['Pid']) == int(status['Tgid']) == native['native_pid']
    assert int(status['PPid']) == native['supervisor_pid'] and status['Cpus_allowed_list'].strip() == '14'
    assert terminal['pid'] == native['supervisor_pid'] and terminal['exit'] == 0 and terminal['cleanup'] is None
    start, end = count(terminal['startMonotonicNs']), count(terminal['endMonotonicNs'])
    assert 0 < count(native['wall_ns']) <= end-start <= chosen['limits']['perLifeSeconds']*10**9
    for k in ['total_cpu_s', 'user_cpu_s', 'system_cpu_s']:
        assert type(native[k]) in [float, int] and math.isfinite(native[k]) and native[k] >= 0
    assert native['total_cpu_s'] == native['user_cpu_s']+native['system_cpu_s'] > 0
    assert row['wholeCpuSeconds'] == native['total_cpu_s']
    assert row['nativeWallNs'] == native['wall_ns']
    assert row['rssKiB'] == count(native['maxrss_linux_kib']) > 0
    assert native['maxrss_linux_kib']*1024 <= chosen['limits']['addressSpaceBytes']
    for k in ['voluntary_context_switches', 'involuntary_context_switches']:
        count(native[k])
    return native, terminal

def audit_housekeeping(record, chosen, threads, originals):
    assert threads == 1
    cpus = chosen['housekeepingCpus']; assert cpus == list(range(8, 14))
    assert record['cpus'] == record['selfAffinity'] == cpus
    keys = set()
    for task in record['selectedTasks']:
        key = tuple(count(task[k]) for k in ['pid', 'tid', 'starttime'])
        assert key not in keys; keys.add(key)
        assert task['after'] == cpus and task['before'] == sorted(set(task['before']))
        assert task['before'] and all(type(c) is int and 0 <= c < 16 for c in task['before'])
        originals.setdefault(key, task['before'])


def vector(value, length):
    assert type(value) is list and len(value) == length
    for n in value: count(n)
    return value


def audit_policy(chosen):
    assert chosen['schema'] == 'rook2-coarse-pure-policy-v1'
    assert chosen['reportSchema'] == 'rook2-coarse-pure-salvage-v1'
    assert chosen['case'] == 'profile-35' and chosen['horizon'] == 8 and chosen['threads'] == 1
    assert chosen['producerTasks'] == 7
    assert chosen['producerPasses'] == ['plain-private-native', 'pure-observed-private-native']
    assert chosen['canonicalPasses'] == ['actual-target-demand', 'bounded-prefix-membership']
    assert chosen['numericalReuse'] is False and chosen['replayJournals'] is False
    assert chosen['allReadyCoverageCeiling'] is True and chosen['readinessMeasured'] is False
    assert chosen['limits'] == dict(nativeLives=1, perLifeSeconds=180, pipelineSeconds=1800,
        addressSpaceBytes=8589934592, reportBytes=268435456)
    assert chosen['taskCaps'] == dict(executedNodes=262144, overlayGroups=131072, mechanismEstimatedBytes=2147483648)
    observer = chosen['observerCaps']
    for name, stem in [('producer', 'producer'), ('pooled', 'pool'), ('canonicalDemand', 'demand')]:
        assert observer[name] == dict(uniqueKeys=CAPS[stem+'_keys'], actualCalls=CAPS[stem+'_calls'], retainedBytes=CAPS[stem+'_bytes'])
    assert observer['prefix'] == dict(actualCalls=CAPS['prefix_calls'], retainedBytes=CAPS['prefix_bytes'])
    assert observer['globalReportBytes'] == CAPS['json_output_bytes']
    assert chosen['nativeCpu'] == 14 and chosen['supervisorCpu'] == 13
    assert chosen['housekeepingCpus'] == list(range(8, 14)) and chosen['buildHelperCpus'] == sorted(HELPERS)
    wide = Path('/home/legolas/rook2-experiments/wide-internal-20261026-01')
    assert chosen['fixture'] == str(wide/'fixture.txt')
    assert chosen['fixtureSelection'] == str(wide/'fixture-selection.json')
    assert chosen['fixtureFreeze'] == str(wide/'fixture-freeze.json')
    return chosen


def read_fixture(path):
    text = path.read_text(); assert len(text.encode()) <= 4*1024*1024
    rows = [line.split('=', 1) for line in text.splitlines()]
    assert len(rows) == 5 and all(len(row) == 2 for row in rows)
    value = dict(rows)
    assert set(value) == {'schema', 'case', 'horizon', 'parent_ordinal', 'binding_hex'}
    assert value['schema'] == 'rook2-wide-fixture-v1' and value['case'] == 'profile-35' and value['horizon'] == '8'
    assert value['parent_ordinal'].isdigit() and int(value['parent_ordinal']) > 0
    binding = value['binding_hex']; assert binding and len(binding) % 2 == 0 and all(c in '0123456789abcdef' for c in binding)
    bytes.fromhex(binding).decode('utf-8')
    value['horizon'], value['parent_ordinal'] = 8, int(value['parent_ordinal'])
    return value


def admit_original_fixture(chosen):
    path = Path(chosen['fixture']); fixture = read_fixture(path)
    selection = read(chosen['fixtureSelection']); freeze = read(chosen['fixtureFreeze'])
    assert selection['schema'] == 'rook2-wide-fixture-selection-v1' and selection['complete'] is True
    assert selection['fixturePath'] == str(path) and selection['selected'] == fixture
    assert selection['fixtureSha256'] == freeze['fixtureSha256'] == sha(path)
    assert freeze['schema'] == 'rook2-wide-fixture-freeze-v1' and freeze['fixture'] == str(path)
    assert freeze['selectionSha256'] == sha(chosen['fixtureSelection'])
    assert selection['selectorSha256'] == sha(HERE.parent/'wide-internal/select_fixture.py')
    provenance = selection['captureProvenance']
    assert provenance['binarySha256'] == freeze['binarySha256'] and provenance['sourcePins'] == freeze['source']
    capture = Path(selection['capture'])
    for name, digest in provenance['rawSha256'].items(): assert sha(capture/name) == digest
    capture_result = read(capture/'result.json')
    assert capture_result['complete'] is True and capture_result['failure'] is None
    assert capture_result['endMonotonicNs'] <= freeze['frozenMonotonicNs']
    rows = capture_result['runs']; assert len(rows) == 3 and [row['case'] for row in rows] == CASES
    selected_report = None
    for row in rows:
        stdout = Path(row['directory'])/'stdout'
        assert sha(stdout) == row['sha256']['stdout'] == provenance['reportSha256'][row['case']]
        if row['case'] == fixture['case']: selected_report = read(stdout)
    parent = selection['selectedParent']; assert parent['entry_ordinal'] == fixture['parent_ordinal']
    assert parent['binding_hex'] == fixture['binding_hex'] and parent['qualifies'] is True
    assert len(parent['children']) == 8 and all(c['complete'] and c['nodes'] >= 512 for c in parent['children'])
    assert sum(c['nodes'] for c in parent['children']) >= 8192
    return fixture, parent, selected_report


def audit_preparation(path, receipt):
    prep = checked_preparation(path)
    assert prep['schema'] == 'rook2-coarse-pure-preparation-run-v1'
    assert prep['crate'] == receipt['crate'] and prep['sourceBefore'] == receipt['sourceBefore']
    assert prep['baselineBefore'] == receipt['baselineBefore']
    assert prep['selectors'] == ['pure_observer::tests::', 'coarse_pure_salvage::tests::']
    paths = [Path('/home/legolas/rook2-experiments')/name/'prepare/preparation-run.json'
        for name in ['internal-split-20261026-01', 'internal-horizon-20261026-01', 'wide-internal-20261026-01']]
    inherited = prep['inheritedControls']; assert len(inherited) == 3
    old = []
    for row, source, total in zip(inherited, paths, [36, 3, 11]):
        assert row == dict(path=str(source), sha256=sha(source), focusedTests=total)
        prior = checked_preparation(source); assert prior['focusedTests'] == total
        assert prior['baselineBefore'] == prep['baselineBefore']; old.append(prior)
    delta = sorted(key for key in set(old[-1]['sourceBefore']) | set(prep['sourceBefore'])
        if old[-1]['sourceBefore'].get(key) != prep['sourceBefore'].get(key))
    assert delta == prep['reusedSourceDelta'] == ['Cargo.toml', 'src/bin/rook2-coarse-pure-census.rs',
        'src/coarse_pure_salvage.rs', 'src/engine.rs', 'src/evaluator.rs', 'src/internal_split.rs',
        'src/lib.rs', 'src/ordinary.rs', 'src/pure_observer.rs']


def costs(value, materialized_bytes, calls):
    assert set(value) == set(COST_FIELDS)
    for n in value.values(): count(n)
    assert value['materialized_bytes'] == materialized_bytes
    assert sum(value[k] for k in ['key_construction_ns', 'lookup_full_equality_ns', 'materialization_ns']) <= value['capture_dedup_observer_ns']
    if materialized_bytes == 0: assert value['materialization_ns'] == 0
    if calls == 0:
        assert all(value[k] == 0 for k in COST_FIELDS if k != 'epoch_check_ns')


def produced_summary(value, calls, unique, kernel, first, payload):
    expected = dict(calls=calls, unique_keys=unique, repeated_calls=calls-unique,
        payload_bytes=unique*payload, kernel_ns=kernel, first_unique_kernel_ns=first)
    for key, number in expected.items():
        assert count(value[key]) == number, ('production summary', key)
    assert count(value['retained_bytes']) >= unique*payload
    return expected


def coverage(records, prefix, category, scope=None):
    """Recompute actual query subsets, retaining key uniqueness across scopes."""
    result = dict(calls=0, unique_keys=0, repeated_calls=0, kernel_ns=0, first_target_kernel_ns=0)
    for row in records:
        pooled = row['pool_id'] is not None
        prior = pooled and row['pool_id'] in prefix
        absent = pooled and not prior
        any_event = False
        for tally in row['scopes']:
            i = tally['index']
            if scope is not None and i != scope: continue
            same = pooled and 1 <= i <= 7 and row['producer_mask'] & (1 << (i-1)) != 0
            accept = dict(total=True, pooled=pooled, same_intended_child=same,
                matched_prior_prefix=prior, matched_prefix_absent=absent,
                producer_first=absent, canonical_earlier=pooled, serial_cache_prior=pooled)[category]
            if not accept: continue
            is_first = row['first_scope'] == i
            n, kernel = tally['calls'], tally['kernel_ns']
            first_cost = row['first_kernel_ns'] if is_first else 0
            include_first = is_first
            if category == 'producer_first':
                n = int(is_first); kernel = first_cost
            elif category == 'canonical_earlier' or (category == 'serial_cache_prior' and absent):
                n -= int(is_first); kernel -= first_cost; include_first = False
            assert n >= 0 and kernel >= 0
            if n:
                any_event = True; result['calls'] += n; result['kernel_ns'] += kernel
                if include_first: result['first_target_kernel_ns'] += first_cost
        result['unique_keys'] += int(any_event)
    result['repeated_calls'] = result['calls']-result['unique_keys']
    return result


def audit_kind(report, kind):
    pool, demand, prefix = report['pool'][kind], report['demand'][kind], report['prefix'][kind]
    rows = pool['records']; assert type(rows) is list and len(rows) <= CAPS['pool_keys']
    assert [r['pool_id'] for r in rows] == list(range(len(rows)))
    per_child = [dict(calls=0, unique=0, kernel=0, first=0) for _ in range(7)]
    pooled_calls = pooled_kernel = pooled_first = 0
    for row in rows:
        count(row['pool_id']); count(row['producer_mask']); count(row['first_unique_kernel_ns'])
        calls = vector(row['producer_calls'], 7); kernels = vector(row['producer_kernel_ns'], 7)
        firsts = vector(row['producer_first_unique_kernel_ns'], 7)
        mask = sum(1 << i for i, n in enumerate(calls) if n)
        assert mask == row['producer_mask'] and 0 < mask < 128
        for i, (n, kernel, first) in enumerate(zip(calls, kernels, firsts)):
            if not n: assert kernel == first == 0
            else:
                assert first <= kernel
                if n == 1: assert first == kernel
                per_child[i]['calls'] += n; per_child[i]['unique'] += 1
                per_child[i]['kernel'] += kernel; per_child[i]['first'] += first
        first_producer = next(i for i, n in enumerate(calls) if n)
        assert row['first_unique_kernel_ns'] == firsts[first_producer]
        pooled_calls += sum(calls); pooled_kernel += sum(kernels); pooled_first += row['first_unique_kernel_ns']
    produced_summary(pool, pooled_calls, len(rows), pooled_kernel, pooled_first, PAYLOAD[kind])
    for i, metrics in enumerate(per_child):
        value = report['producers'][i]['production'][kind]
        produced_summary(value, metrics['calls'], metrics['unique'], metrics['kernel'], metrics['first'], PAYLOAD[kind])
    prior = prefix['matched_records']; assert type(prior) is list
    ids = [row['pool_id'] for row in prior]
    assert ids == sorted(set(ids)) and all(type(i) is int and 0 <= i < len(rows) for i in ids)
    for row in prior:
        assert count(row['calls']) > 0; count(row['kernel_ns'])
    assert prefix['pool_matched_unique_keys'] == len(ids)
    assert prefix['pool_matched_calls'] == sum(row['calls'] for row in prior) <= count(prefix['calls'])
    assert prefix['pool_matched_kernel_ns'] == sum(row['kernel_ns'] for row in prior) <= count(prefix['kernel_ns'])
    records = demand['records']; assert type(records) is list and len(records) <= CAPS['demand_keys']
    assert [row['demand_id'] for row in records] == list(range(len(records)))
    supplied = set()
    for row in records:
        count(row['demand_id']); count(row['producer_mask'])
        pool_id = row['pool_id']
        if pool_id is None: assert row['producer_mask'] == 0
        else:
            assert type(pool_id) is int and 0 <= pool_id < len(rows) and pool_id not in supplied
            supplied.add(pool_id); assert row['producer_mask'] == rows[pool_id]['producer_mask']
        first_scope = count(row['first_scope']); assert first_scope < 9
        first = count(row['first_kernel_ns'])
        scopes = row['scopes']; assert type(scopes) is list and scopes
        indices = [t['index'] for t in scopes]; assert indices == sorted(set(indices))
        for tally in scopes:
            i = count(tally['index']); assert i < 9 and tally['scope'] == SCOPES[i]
            assert count(tally['calls']) > 0; count(tally['kernel_ns'])
        assert first_scope in indices
        first_tally = next(t for t in scopes if t['index'] == first_scope)
        assert first <= first_tally['kernel_ns']
        if first_tally['calls'] == 1: assert first == first_tally['kernel_ns']
    derived = {}
    prior_set = set(ids)
    for category in CATEGORIES:
        expected = coverage(records, prior_set, category)
        assert demand[category] == expected, ('coverage aggregate', kind, category)
        derived[category] = expected
    assert derived['same_intended_child']['calls'] <= derived['pooled']['calls'] <= derived['total']['calls']
    assert derived['pooled']['calls'] == derived['producer_first']['calls']+derived['serial_cache_prior']['calls']
    assert derived['pooled']['kernel_ns'] == derived['producer_first']['kernel_ns']+derived['serial_cache_prior']['kernel_ns']
    scopes = demand['scopes']; assert [r['scope'] for r in scopes] == SCOPES
    for i, row in enumerate(scopes):
        for category in CATEGORIES:
            assert row[category] == coverage(records, prior_set, category, i), ('coverage scope', kind, i, category)
    assert sum(row['total']['calls'] for row in scopes) == derived['total']['calls']
    assert sum(row['total']['kernel_ns'] for row in scopes) == derived['total']['kernel_ns']
    return derived


def audit_report(report, chosen):
    assert report['schema'] == 'rook2-coarse-pure-salvage-v1'
    assert report['serial_threads'] == 1 and report['horizon'] == report['completed_depth'] == 8
    for key in ['fixture_bound', 'all_results_ready_coverage_ceiling', 'canonical_fidelity', 'producer_native_fidelity']:
        assert report[key] is True
    for key in ['readiness_measured', 'numerical_reuse', 'journals_constructed']:
        assert report[key] is False
    assert report['caps'] == CAPS
    assert report['physical_producer_executions'] == 14 and report['physical_canonical_passes'] == 2
    for key in ['processId', 'root_passes', 'canonical_nodes', 'canonical_relations',
        'second_canonical_nodes', 'second_canonical_relations', 'producer_nodes_per_set',
        'producer_relations_per_set', 'physical_total_nodes', 'physical_total_relations',
        'parent_nodes', 'parent_relations', 'tt_base_copy_bytes', 'tt_base_bytes', 'snapshot_bytes',
        'estimated_mechanism_bytes', 'peak_rss_kib']:
        count(report[key])
    assert report['root_passes'] > 0 and report['canonical_nodes'] > 0
    assert report['canonical_nodes'] == report['second_canonical_nodes']
    assert report['canonical_relations'] == report['second_canonical_relations']
    assert report['parent_nodes'] <= report['canonical_nodes'] and report['parent_relations'] <= report['canonical_relations']
    assert report['tt_base_copy_bytes'] > 0 and report['tt_base_bytes'] == report['tt_base_copy_bytes']+40
    assert report['snapshot_bytes'] > 0 and report['peak_rss_kib']*1024 <= CAPS['process_bytes']
    estimate = (7*CAPS['producer_bytes']+2*CAPS['pool_bytes']+CAPS['demand_bytes']+CAPS['prefix_bytes']
        +2*24*1024*1024+report['tt_base_bytes']+2*report['snapshot_bytes']+16*1024*1024)
    assert report['estimated_mechanism_bytes'] == estimate <= CAPS['mechanism_bytes']
    digest = report['binding_tt_digest']
    assert type(digest) is str and len(digest) == 16 and all(c in '0123456789abcdef' for c in digest)
    assert digest == report['prefix_binding_tt_digest']
    timings = report['timings']
    expected_times = ['first_canonical_wall_ns', 'first_canonical_process_cpu_ns',
        'second_canonical_wall_ns', 'second_canonical_process_cpu_ns', 'parent_wall_ns',
        'parent_process_cpu_ns', 'binding_wall_ns', 'binding_process_cpu_ns',
        'prefix_binding_wall_ns', 'prefix_binding_process_cpu_ns', 'snapshot_ns',
        'pool_wall_ns', 'pool_process_cpu_ns', 'pool_render_ns', 'pool_render_process_cpu_ns',
        'prefix_prebind_ns', 'root_compare_ns']
    assert set(timings) == set(expected_times)
    for n in timings.values(): count(n)
    assert 0 < timings['parent_wall_ns']+timings['binding_wall_ns'] <= timings['first_canonical_wall_ns']
    assert 0 < timings['parent_process_cpu_ns']+timings['binding_process_cpu_ns'] <= timings['first_canonical_process_cpu_ns']
    assert timings['prefix_binding_wall_ns'] <= timings['second_canonical_wall_ns']
    assert timings['prefix_binding_process_cpu_ns'] <= timings['second_canonical_process_cpu_ns']
    producers = report['producers']; assert [p['id'] for p in producers] == list(range(7))
    for producer in producers:
        assert producer['native_equal'] is True and producer['physical_executions'] == 2
        for key, value in producer.items():
            if key.endswith(('_ns', '_bytes', '_groups', '_per_execution')): count(value)
        assert producer['nodes_per_execution'] <= CAPS['producer_nodes']
        request = producer['request']; window = request['window']
        assert len(window) == 2 and all(type(n) is int for n in window) and window[0] < window[1]
        assert 1 <= request['ply'] < 64 and request['iteration'] <= 8 and request['depth'] >= 2
        assert producer['plain_setup_ns'] <= producer['plain_wall_ns']
        assert producer['captured_setup_ns'] <= producer['captured_wall_ns']
        for arm in ['plain', 'captured']:
            assert producer[arm+'_overlay_groups'] <= 131072+64
            assert producer[arm+'_overlay_bytes'] == 48*producer[arm+'_overlay_groups']
            assert producer[arm+'_private_bytes'] <= CAPS['mechanism_bytes']
        assert producer['plain_overlay_groups'] == producer['captured_overlay_groups']
        value = producer['production']; assert value['producer'] == producer['id'] and value['failed'] is False
        assert value['influence']['calls'] == producer['maps_per_execution']
        assert value['chain']['calls'] == producer['full_per_execution']
        assert sum(value[kind]['calls'] for kind in KINDS) <= CAPS['producer_calls']
        assert sum(value[kind]['unique_keys'] for kind in KINDS) <= CAPS['producer_keys']
        assert sum(value[kind]['retained_bytes'] for kind in KINDS) <= CAPS['producer_bytes']
        costs(value['timings'], sum(PAYLOAD[k]*value[k]['repeated_calls'] for k in KINDS), sum(value[k]['calls'] for k in KINDS))
        kernel = sum(value[k]['kernel_ns'] for k in KINDS)
        assert kernel+value['timings']['capture_dedup_observer_ns'] <= producer['captured_wall_ns']
    for metric in ['nodes', 'relations']:
        per_set = sum(p[metric+'_per_execution'] for p in producers)
        assert report['producer_'+metric+'_per_set'] == per_set
        assert report['physical_total_'+metric] == report['canonical_'+metric]+report['second_canonical_'+metric]+2*per_set
    for key in ['pool', 'demand', 'prefix']: assert report[key]['failed'] is False
    assert report['pool']['retained_bytes'] <= CAPS['pool_bytes']
    assert report['demand']['peak_retained_bytes'] <= CAPS['demand_bytes']
    assert report['demand']['payload_sizes'] == PAYLOAD
    assert report['demand']['json_budget'] == dict(report_bytes=268435456,
        pool_prefix_ledger_bytes=134217728, demand_ledger_bytes=100663296, fixed_reserved_bytes=33554432)
    assert report['prefix']['membership_bytes'] <= CAPS['prefix_bytes']
    assert report['pool']['combine_ns'] <= timings['pool_wall_ns']
    derived = {kind: audit_kind(report, kind) for kind in KINDS}
    assert sum(report['pool'][kind]['unique_keys'] for kind in KINDS) <= CAPS['pool_keys']
    assert sum(report['pool'][kind]['unique_keys'] for kind in KINDS)*(1024+160) <= 134217728
    assert sum(report['pool'][kind]['calls'] for kind in KINDS) <= CAPS['pool_calls']
    assert sum(derived[kind]['total']['unique_keys'] for kind in KINDS) <= CAPS['demand_keys']
    assert sum(derived[kind]['total']['unique_keys'] for kind in KINDS)*1536 <= 100663296
    assert sum(derived[kind]['total']['calls'] for kind in KINDS) <= CAPS['demand_calls']
    assert sum(report['prefix'][kind]['calls'] for kind in KINDS) <= CAPS['prefix_calls']
    costs(report['demand']['timings'], sum(PAYLOAD[k]*(derived[k]['pooled']['calls']+derived[k]['total']['repeated_calls']) for k in KINDS), sum(derived[k]['total']['calls'] for k in KINDS))
    costs(report['prefix']['timings'], sum(PAYLOAD[k]*report['prefix'][k]['pool_matched_calls'] for k in KINDS), sum(report['prefix'][k]['calls'] for k in KINDS))
    demand_kernel = sum(derived[k]['total']['kernel_ns'] for k in KINDS)
    prefix_kernel = sum(report['prefix'][k]['kernel_ns'] for k in KINDS)
    assert prefix_kernel+report['prefix']['timings']['capture_dedup_observer_ns'] <= timings['second_canonical_wall_ns']
    producer_wall = sum(sum(p[k] for k in ['plain_wall_ns', 'captured_wall_ns', 'capture_finish_ns',
        'capture_summary_render_ns', 'private_state_compare_ns', 'plain_private_drop_ns', 'captured_private_drop_ns']) for p in producers)
    assert (producer_wall+timings['snapshot_ns']+timings['pool_wall_ns']+timings['pool_render_ns']+demand_kernel
        +report['demand']['timings']['capture_dedup_observer_ns']) <= timings['parent_wall_ns']
    producer_cpu = sum(sum(p[k] for k in ['plain_process_cpu_ns', 'captured_process_cpu_ns',
        'capture_finish_process_cpu_ns', 'capture_summary_render_process_cpu_ns',
        'plain_private_drop_process_cpu_ns', 'captured_private_drop_process_cpu_ns']) for p in producers)
    assert producer_cpu+timings['pool_process_cpu_ns']+timings['pool_render_process_cpu_ns'] <= timings['parent_process_cpu_ns']
    return derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); base = args.raw.resolve()
    plan, result = read(base/'plan.json'), read(base/'result.json')
    assert plan['schema'] == 'rook2-coarse-pure-collection-v1'
    assert result['schema'] == 'rook2-coarse-pure-collection-result-v1'
    assert result['complete'] is True and result['failure'] is None
    chosen = audit_policy(plan['policy'])
    assert read(plan['policyPath']) == chosen and sha(plan['policyPath']) == plan['policySha256']
    assert plan['scope'] == chosen['scope']
    assert plan['limits'] == chosen['limits']
    step = dict(case='profile-35', threads=1, repeat=1, warmup=False)
    assert plan['schedule'] == [step]
    pins = plan['inputSha256']
    required = [*HERE.glob('*.py'), HERE/'policy.json', Path('/usr/bin/python3'),
        Path('/home/legolas/king-spec/conformance/profiling/workloads.json'),
        Path(plan['build'])/'receipt.json', Path(plan['binary']), Path(plan['preparation']),
        Path(chosen['fixture']), Path(chosen['fixtureSelection']), Path(chosen['fixtureFreeze'])]
    required += [HERE/'inputs/profile-35.txt']
    assert all(str(p.resolve()) in pins for p in required)
    for path, digest in pins.items(): assert sha(path) == digest, ('input changed', path)
    receipt = admit(Path(plan['build'])); image = Path(plan['binary'])
    assert receipt['binary'] == str(image) and receipt['binarySha256'] == plan['binarySha256'] == sha(image)
    assert receipt['sourceBefore'] == plan['sourcePins'] == snapshot(Path(receipt['crate']))
    assert receipt['baselineBefore'] == plan['baseline'] == baseline()
    assert all(path in pins and pins[path] == digest for path, digest in plan['baseline']['protectedArtifacts'].items())
    audit_preparation(Path(plan['preparation']), receipt); audit_inputs()
    fixture, parent, original = admit_original_fixture(chosen)
    assert plan['fixture'] == fixture and plan['fixturePath'] == chosen['fixture']
    assert plan['fixtureSelectionPath'] == chosen['fixtureSelection'] and plan['fixtureFreezePath'] == chosen['fixtureFreeze']
    assert read(chosen['fixtureFreeze'])['frozenMonotonicNs'] < result['startMonotonicNs']
    assert 0 < result['endMonotonicNs']-result['startMonotonicNs'] <= chosen['limits']['pipelineSeconds']*10**9
    assert len(result['runs']) == 1
    row = result['runs'][0]
    assert all(row[key] == value and type(row[key]) is type(value) for key, value in step.items())
    directory = base/'00-profile-35-t1-r1'
    assert row['directory'] == str(directory) and directory.is_dir() and not directory.is_symlink()
    assert set(row['sha256']) == {'launch.json', 'terminal.json', 'native.json', 'stdout', 'stderr', 'housekeeping.json'}
    for name, digest in row['sha256'].items():
        assert not (directory/name).is_symlink() and sha(directory/name) == digest
    assert (directory/'stderr').read_bytes() == b''
    assert 0 < (directory/'stdout').stat().st_size <= chosen['limits']['reportBytes']
    options = ['--input', str(HERE/'inputs/profile-35.txt'), '--fixture', chosen['fixture']]
    native, terminal = audit_native(directory, image, options, row, chosen)
    launch = read(directory/'launch.json')
    command = ['/usr/bin/python3', str(HERE/'account.py'), '--engine', str(image), '--record', str(directory/'native.json'), *options]
    assert launch == dict(argv=command, nativeArgv=[str(image), *options],
        step=plan['schedule'][0], policySha256=plan['policySha256'])
    assert result['startMonotonicNs'] <= terminal['startMonotonicNs'] < terminal['endMonotonicNs'] <= result['endMonotonicNs']
    originals = {}; audit_housekeeping(read(directory/'housekeeping.json'), chosen, 1, originals)
    restored = set()
    for record in read(base/'housekeeping-restore.json'):
        key = tuple(count(record[k]) for k in ['pid', 'tid', 'starttime'])
        assert key not in restored; restored.add(key)
        assert type(record['inheritedNewThread']) is bool
        if not record['inheritedNewThread']: assert record['restored'] == originals[key]
    pid_and_group_gone({native['native_pid'], native['supervisor_pid']}, {native['supervisor_pid']})
    report = read(directory/'stdout')
    assert report['processId'] == native['native_pid'] and report['fixture'] == fixture
    assert report['canonical_nodes'] == original['canonical_nodes'] and report['canonical_relations'] == original['canonical_relations']
    derived = audit_report(report, chosen)
    forecast = [-parent['window'][1], -max(parent['window'][0], parent['best'])]
    for producer in report['producers']:
        request = producer['request']
        assert request['window'] == forecast and request['ply'] == parent['ply']+1 and request['iteration'] == parent['iteration']
    timings = report['timings']
    assert timings['first_canonical_wall_ns']+timings['second_canonical_wall_ns'] <= native['wall_ns']
    assert timings['first_canonical_process_cpu_ns']+timings['second_canonical_process_cpu_ns'] <= native['total_cpu_s']*10**9+2_000_000
    producer_costs = {key: sum(p[key] for p in report['producers']) for key in report['producers'][0]
        if key.endswith('_ns') and type(report['producers'][0][key]) is int}
    summaries = {kind: dict(aggregate=derived[kind], scopes=report['demand'][kind]['scopes'],
        production={key: report['pool'][kind][key] for key in ['calls', 'unique_keys', 'repeated_calls', 'payload_bytes', 'retained_bytes', 'kernel_ns', 'first_unique_kernel_ns']},
        prefix={key: report['prefix'][kind][key] for key in ['calls', 'kernel_ns', 'pool_matched_calls', 'pool_matched_kernel_ns', 'pool_matched_unique_keys']}) for kind in KINDS}
    output = dict(schema='rook2-coarse-pure-reconciled-v1', complete=True, raw=str(base), nativeLives=1,
        rawSha256={name: sha(base/name) for name in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after', 'housekeeping-restore.json']},
        reportSha256=sha(directory/'stdout'), reconcilerSha256=sha(Path(__file__)),
        fixture=dict(case=fixture['case'], parentOrdinal=fixture['parent_ordinal'], sha256=sha(chosen['fixture'])),
        physicalWork={key: report[key] for key in ['canonical_nodes', 'canonical_relations', 'producer_nodes_per_set', 'producer_relations_per_set',
            'physical_producer_executions', 'physical_canonical_passes', 'physical_total_nodes', 'physical_total_relations', 'parent_nodes', 'parent_relations']},
        summaries=summaries, dispatcherTimingsNs=timings, producerTimingTotalsNs=producer_costs,
        observerTimings=dict(producers=[p['production']['timings'] for p in report['producers']], demand=report['demand']['timings'], prefix=report['prefix']['timings']),
        retainedBytes=dict(pool=report['pool']['retained_bytes'], demandPeak=report['demand']['peak_retained_bytes'], prefixMembership=report['prefix']['membership_bytes'],
            ttBaseCopy=report['tt_base_copy_bytes'], ttBase=report['tt_base_bytes'], snapshot=report['snapshot_bytes'], mechanismEstimate=report['estimated_mechanism_bytes']),
        wholeNativeWait4=dict(cpuSeconds=native['total_cpu_s'], wallNs=native['wall_ns'], peakRssKiB=native['maxrss_linux_kib']),
        coverageScope='All results ready ceiling only; no readiness, delivery, cache consumer or speed forecast. Same-child is a subset of pooled-seven. Global unique counts deduplicate across scopes; scope unique counts are not additive. Producer-first is one prefix-absent first actual target query per matched key; later target repetitions are canonical-earlier opportunities, not multiple newly unavailable values. Prefix membership retains only bounded producer keys and does not imply an existing canonical cache.',
        costScope='Influence and actual FULL inline Activity/Shelter native-kernel timers are disjoint observational proxies with clock/observer perturbation, never CPU saved. Observer/key/lookup/full-equality/materialization timers nest; setup nests in each producer execution. materialization_ns includes native payload copy plus equality audit and is not a tuned delivery path. Private Search destruction, finish and summary/pool rendering are explicit. Whole wait4 includes fourteen producer executions, two full canonical passes, prebind/setup, final demand/prefix report serialization and teardown outside the pass intervals. No wall timer is subtracted from process CPU.',
        assurance='Offline incidence/count/cost joins use native exact-key IDs. Native hashes index full equality; duplicate-key/different-payload failures abort. Key completeness and exact equality are source/control assurances; full private keys are not dumped for independent offline replay. Paired plain/captured producer output/work/private-state audits and two-pass whole-root output/work/final-state equality are mandatory; transient incorrect shared writes later overwritten may escape final-state checks.',
        scope=chosen['scope'])
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False); stream.write('\n')
    print('reconciled one serial pure-result census;14 producer executions and2 canonical passes accounted', flush=True)


if __name__ == '__main__': main()
