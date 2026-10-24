#!/usr/bin/env python3
"""Independent read-only audit of FULL split training or production collection.

No native executable or compiler/tool is launched. A fresh reconciled JSON file
is the only output; raw evidence and failed earlier receipts are never replaced.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shlex
import statistics
import tomllib

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ACCOUNT = HERE.parent/'integration/account_threads.py'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
CONTROL_SHA = '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a'
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
SMALL_CASES = ['profile-35', 'profile-08', 'profile-04']
VARIANTS = ['control', 'budget1', 'budget2']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def bad(value):
        raise ValueError('nonfinite JSON: '+value)
    return json.loads(path.read_text(), parse_constant=bad)


def distribution(samples):
    assert samples and all(type(value) in [int, float] and math.isfinite(value) for value in samples)
    return dict(samples=samples, median=statistics.median(samples), min=min(samples), max=max(samples))


def check_build(directory, mode):
    receipt = read(directory/'receipt.json')
    assert receipt['schema'] == 'rook2-development-build-v1'
    assert receipt['outcome'] == 'build-succeeded-with-stable-input-snapshot' and receipt['cargo_exit_code'] == 0
    assert receipt['target_triple'] == 'x86_64-unknown-linux-gnu' and receipt['target_cpu'] == 'x86-64'
    assert receipt['binary_name'] == 'rook2' and receipt['pgo']['mode'] == mode
    assert receipt['source_sha256_before'] == receipt['source_sha256_after']
    assert receipt['tool_sha256_before'] == receipt['tool_sha256_after']
    assert receipt['cargo_config_sha256_before'] == receipt['cargo_config_sha256_after']
    assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged'] and receipt['cargo_config_unchanged']
    assert 'release: 1.85.1\n' in receipt['toolchain']['rustc']['stdout']
    assert 'LLVM version: 19.1.7\n' in receipt['toolchain']['rustc']['stdout']
    for tool in ['rustc', 'cargo']:
        assert receipt['toolchain'][tool]['exit_code'] == 0
    source = Path(receipt['crate'])
    source_paths = [source/'Cargo.toml', source/'Cargo.lock']
    source_paths += sorted(path for path in (source/'src').rglob('*') if path.is_file())
    source_paths += [source/name for name in ['build.rs', 'rust-toolchain', 'rust-toolchain.toml'] if (source/name).is_file()]
    assert {str(path.relative_to(source)): sha(path) for path in source_paths} == receipt['source_sha256_before']
    for name, digest in receipt['source_sha256_before'].items():
        assert sha(directory/'source-before'/name) == digest
    assert tomllib.loads((directory/'source-before/Cargo.toml').read_text())['profile']['release'] == {
        'opt-level': 3, 'lto': 'thin', 'codegen-units': 1, 'panic': 'abort', 'debug': 1}
    assert sha(Path(receipt['binary_output']['path'])) == receipt['binary_output']['sha256']
    commands = [shlex.split(line.split('Running `', 1)[1].rsplit('`', 1)[0])
                for line in (directory/'build.stderr').read_text().splitlines()
                if 'Running `' in line and '--crate-name rook2 ' in line]
    effective = {}
    for source_name, kind in [('src/lib.rs', 'lib'), ('src/bin/rook2.rs', 'bin')]:
        matching = [command for command in commands if source_name in command]
        assert len(matching) == 1
        command, options = matching[0], {}
        assert command[command.index('--crate-type')+1] == kind
        for index, token in enumerate(command):
            if token == '-C':
                value = command[index+1]
            elif token.startswith('-C') and len(token) > 2:
                value = token[2:]
            else:
                continue
            key, separator, value = value.partition('=')
            assert key not in options
            options[key] = value if separator else True
        assert all(options.get(key) == value for key, value in [
            ('opt-level', '3'), ('panic', 'abort'), ('codegen-units', '1'), ('debuginfo', '1'), ('target-cpu', 'x86-64')])
        if kind == 'bin':
            assert options.get('lto') == 'thin' and 'linker-plugin-lto' not in options
        else:
            assert options.get('linker-plugin-lto') is True and 'lto' not in options
        if mode == 'instrumented':
            assert options.get('profile-generate') == receipt['pgo']['profile_directory']
            assert 'profile-use' not in options and 'llvm-args' not in options
        else:
            assert options.get('profile-use') == receipt['pgo']['profile'] and 'profile-generate' not in options
            assert options.get('llvm-args') == ('-pgo-warn-missing-function '
                '-enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false')
        effective[source_name] = options
    if mode == 'profile-use':
        assert receipt['pgo']['inputs_unchanged'] and receipt['pgo']['code_layout']['profiled_functions_only']
        assert receipt['pgo']['input_sha256_before'] == receipt['pgo']['input_sha256_after']
        for path, digest in receipt['pgo']['input_sha256_before'].items():
            assert sha(Path(path)) == digest
        training = read(Path(receipt['pgo']['training_record']))
        assert training['schema'] == 'rook2-pgo-training-v1' and training['complete']
        assert training['engine_source_sha256'] == receipt['source_sha256_before']
        assert training['target_triple'] == receipt['target_triple']
        assert training['base_rust_flags'] == ['-C', 'target-cpu=x86-64']
        assert training['profile_sha256'] == sha(Path(receipt['pgo']['profile']))
        lower = (directory/'build.stderr').read_text().lower()
        assert not any(value in lower for value in ['no profile data available for function',
            'profile data may be out of date', 'profile data mismatch', 'malformed instrumentation profile',
            'hash mismatch', 'unprofiled function'])
    return receipt, effective


def native_receipt(path, image, budget, options, input_hashes):
    native = read(path)
    assert native['schema'] == 'rook2-native-wait4-v1' and native['known_single_process']
    assert native['failure'] is None and native['native_exit_code'] == native['native_wait_status'] == 0
    assert native['exec_error'] is None and native['supervisor_signals'] == []
    assert native['engine'] == str(image)
    assert native['engine_sha256_before'] == native['engine_sha256_after'] == sha(image)
    assert native['launcher_sha256'] == input_hashes[str(ACCOUNT)]
    assert sha(Path(native['python_executable'])) == native['python_executable_sha256']
    assert native['argv'] == [str(image), *options] and native['expected_threads'] == budget
    assert set(native['supervisor_affinity']) and set(native['supervisor_affinity']) <= HELPERS
    assert native['native_pre_exec'] == dict(pid=native['native_pid'], pgid=native['supervisor_pid'], affinity=[14])
    observed = native['native_post_exec']
    assert observed['path'] == str(image) and observed['pgid'] == native['supervisor_pid'] and observed['affinity'] == [14]
    affinities = observed['task_affinities']
    assert sorted(observed['tasks']) == sorted(affinities)
    assert len(affinities) == budget and affinities[str(native['native_pid'])] == [14]
    assert all(cpus == [6] for tid, cpus in affinities.items() if tid != str(native['native_pid']))
    assert native['wall_ns'] == native['reaped_monotonic_ns'] - native['start_monotonic_ns'] > 0
    assert native['total_cpu_s'] == native['user_cpu_s'] + native['system_cpu_s'] > 0
    for pid in [native['native_pid'], native['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists(), 'recorded PID currently live; inspect possible PID reuse'
    return native


def original_streams(actual, workload, expected, raw):
    assert actual['stdout'].encode() == raw['stdout'] and actual['stderr'].encode() == raw['stderr']
    assert actual['stderr'] == expected['stderr'] and actual['exit'] == expected['exit'] == dict(code=0, signal=None)
    protocol = workload['protocol']
    # This pinned tap wraps write(), not end(data); cleanup is verified through
    # the pinned released runner and complete output/exit, not claimed captured.
    assert raw['stdin'] == ('\n'.join([*protocol['recordsBeforeSearch'], 'cm_parm rnd', protocol['searchRecord']])+'\n').encode()
    text = raw['stdout'].decode(); assert text.endswith('\n')
    lines = text.split('\n')[:-1]
    replies = [line for line in protocol['recordsBeforeSearch'] if line.startswith('cm_parm ')]+['cm_parm rnd=0']
    assert lines[:len(replies)] == replies
    lines = lines[len(replies):]
    expression = re.compile(r'^\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?$')
    for post in expected['posts']:
        match = expression.fullmatch(lines.pop(0)); assert match
        assert dict(depth=int(match[1]), score=int(match[2]), workThousands=int(match[3]),
                    searchId=int(match[4]), pv=(match[5] or '').strip().replace('0', 'O')) == post
    assert lines.pop(0) == 'move '+expected['move'] and lines == expected['resultRecords']
    return len(expected['posts'])


def lifetime(directory, row, step, image, budget, options, hashes, profile_pattern=None):
    assert all(row[key] == value for key, value in step.items()) and Path(row['directory']).resolve() == directory
    mode = read(SPEC/'replay-oracle.json')['mode']
    native = native_receipt(directory/'native.json', image, budget, [*options, *mode], hashes)
    assert row['nativePid'] == native['native_pid'] and row['taskAffinities'] == native['native_post_exec']['task_affinities']
    supervisor = [native['python_executable'], str(ACCOUNT), '--engine', str(image), '--record', str(directory/'native.json'),
                  '--known-single-process', '--thread-budget', str(budget), *options]
    config, tap, launch, replay = [read(directory/name) for name in ['tap-config.json', 'wire/receipt.json', 'launch.json', 'stdout']]
    assert config['expectedArgv'] == [*supervisor, *mode] == tap['argv']
    assert config['nativeExecutable'] == str(image) and config['directory'] == str(directory/'wire')
    assert config['maxRawBytes'] == 8*1024*1024
    assert tap['configSha256'] == sha(directory/'tap-config.json')
    assert launch == dict(argv=['/usr/bin/node', '--import', str(ROOT/'tools/tap_wire.mjs'), str(SPEC/'replay-check.mjs'),
                                '--case', step['case'], '--', *supervisor], step=step,
                         profileEnvironment={'LLVM_PROFILE_FILE': str(profile_pattern)} if profile_pattern else {})
    assert (directory/'stderr').read_bytes() == b'' and (directory/'stdout').stat().st_size <= 8*1024*1024
    assert replay['status'] == 'pass' and replay['selectedCases'] == [step['case']] and len(replay['results']) == 1
    assert replay['workloadSha256'] == sha(SPEC/'workloads.json') and replay['oracleSha256'] == sha(SPEC/'replay-oracle.json')
    actual = replay['results'][0]
    assert actual['command'] == [*supervisor, *mode] and actual['case'] == step['case']
    assert actual['status'] == 'pass' and actual['complete'] and not actual['truncated']
    assert actual['error'] is None and actual['discardedObservedBytes'] == 0
    assert tap['failure'] is None and tap['pending'] is None and len(tap['searches']) == 1
    assert tap['launcherPid'] == native['supervisor_pid'] and tap['launcherExit'] == dict(code=0, signal=None)
    assert tap['native']['pid'] == native['native_pid'] and tap['native']['image'] == str(image)
    search = tap['searches'][0]
    assert search['wallNs'] == int(search['endMonotonicNs']) - int(search['startMonotonicNs']) > 0
    assert row['searchWallNs'] == search['wallNs'] and row['wholeWallNs'] == native['wall_ns']
    assert row['wholeCpuSeconds'] == native['total_cpu_s'] and row['rssKiB'] == native['maxrss_linux_kib']
    assert row['nonSearchWallNs'] == native['wall_ns']-search['wallNs'] >= 0
    for boundary in ['beforeWrite', 'afterData']:
        observed = search[boundary]
        assert observed['available'] and observed['pid'] == native['native_pid'] and observed['image'] == str(image)
        assert observed['lastProcessor'] == 14 and observed['startTicks'] == tap['native']['startTicks']
    assert set(tap['raw']) == {'stdin', 'stdout', 'stderr'}
    raw = {}
    for name, item in tap['raw'].items():
        path = directory/'wire'/f'{name}.raw'
        assert item['path'] == str(path) and sha(path) == item['sha256']
        assert path.stat().st_size == item['bytes'] == item['observedBytes'] and item['discardedObservedBytes'] == 0
        raw[name] = path.read_bytes()
    assert sum(len(value) for value in raw.values()) <= config['maxRawBytes']
    workloads, oracle = read(SPEC/'workloads.json'), read(SPEC/'replay-oracle.json')
    workload = next(case for case in workloads['cases'] if case['id'] == step['case'])
    expected = next(case for case in oracle['cases'] if case['id'] == step['case'])
    posts = original_streams(actual, workload, expected, raw)
    assert search['move'] == expected['move']
    assert set(row['sha256']) == {'native.json', 'stdout', 'stderr', 'wire/receipt.json', 'tap-config.json', 'launch.json'}
    for path, digest in row['sha256'].items():
        assert sha(directory/path) == digest
    return native, posts


def training_audit(base, plan):
    training = read(base/'training.json')
    assert training['schema'] == 'rook2-pgo-training-v1' and training['complete']
    build, effective = check_build(Path(plan['buildDirectory']), 'instrumented')
    assert training['effective_rustc_options'] == plan['effectiveRustcOptions'] == effective
    assert training['engine_source_sha256'] == plan['source'] == build['source_sha256_before']
    assert training['target_triple'] == build['target_triple'] and training['base_rust_flags'] == ['-C', 'target-cpu=x86-64']
    assert training['input_sha256'] == plan['inputs']
    assert training['instrumented_build_receipt'] == dict(path=str(Path(plan['buildDirectory'])/'receipt.json'),
                                                         sha256=sha(Path(plan['buildDirectory'])/'receipt.json'))
    assert training['instrumented_engine_sha256'] == plan['imageSha256'] == sha(Path(plan['image']))
    cases = [case['id'] for case in read(SPEC/'workloads.json')['cases']]
    assert len(cases) == len(set(cases)) == 54
    schedule = [dict(case=case, budget=budget, variant=f'budget{budget}') for budget in [1, 2] for case in cases]
    assert plan['schedule'] == schedule and len(training['runs']) == training['original_lifetimes'] == 108
    assert training['modes'] == [dict(budget=budget, originalCases=54) for budget in [1, 2]]
    assert plan['limits']['aggregateSeconds'] == 2400 and plan['limits']['perLifetimeSeconds'] == 180
    profiles, pids, posts = {}, set(), 0
    profile_root = Path(plan['profileRoot'])
    for index, (step, row) in enumerate(zip(schedule, training['runs'])):
        directory = base/f'{index:03d}-{step["case"]}-b{step["budget"]}'
        raw_directory = profile_root/directory.name
        native, count = lifetime(directory, row, step, Path(plan['image']), step['budget'],
                                 [f'--research-threads={step["budget"]}'], plan['inputs'], raw_directory/'native-%p.profraw')
        profile = raw_directory/f'native-{native["native_pid"]}.profraw'
        assert list(raw_directory.iterdir()) == [profile] and profile.stat().st_size > 0
        assert row['profile'] == str(profile) and row['profileSha256'] == sha(profile)
        profiles[str(profile)] = sha(profile); pids.add(native['native_pid']); posts += count
    assert len(pids) == len(profiles) == 108
    assert {str(path) for path in profile_root.rglob('*.profraw')} == set(profiles)
    assert sum(Path(path).stat().st_size for path in profiles) <= plan['limits']['rawProfileBytes']
    assert profiles == training['raw_profiles_sha256']
    merge = read(base/'merge.json')
    expected_merge = ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(base/'merged.profdata'), *sorted(profiles)]
    assert merge['exit'] == 0 and merge['elapsedNs'] > 0 and merge['argv'] == expected_merge == training['merge_command']
    assert (base/'merge.stderr').read_bytes() == b''
    assert sha(base/'merge.json') == training['merge_record_sha256']
    version = read(base/'merge-tool.json')
    assert version['argv'] == ['/usr/bin/llvm-profdata-19', '--version'] and version['exit'] == 0
    assert version['stdout'] == training['merge_tool_version'] and '19.1.7' in version['stdout']
    assert version['sha256'] == plan['mergeToolSha256'] == training['merge_tool_sha256']
    assert sha(Path(plan['mergeTool']).resolve()) == plan['mergeToolSha256']
    assert (base/'merged.profdata').stat().st_size > 0 and sha(base/'merged.profdata') == training['profile_sha256']
    assert training['plan_sha256'] == sha(base/'plan.json') and training['driver_sha256'] == sha(HERE/'train.py')
    return dict(kind='training', complete=True, nativeProcesses=108, strictReplayLifetimes=108,
                originalCasesPerMode=54, orderedPosts=posts, profileSha256=training['profile_sha256'],
                rawProfiles=108, mergeCount=1,
                notes='Original54 once per mode, equal merge weights, PID-bound unique raw files; verifier checks recorded merge and hashes without rerunning LLVM. Instrumented costs are not production performance.',
                rawSha256={name: sha(base/name) for name in ['plan.json', 'training.json', 'merge.json', 'merge-tool.json', 'merged.profdata', 'proc-stat-before', 'proc-stat-after']})


def gate(summaries):
    by = {(row['case'], row['variant']): row for row in summaries}
    lower, separated = {}, {}
    sums = {name: sum(by[case, name]['searchWallNs']['median'] for case in SMALL_CASES) for name in VARIANTS}
    for case in SMALL_CASES:
        worker = by[case, 'budget2']['searchWallNs']
        others = [by[case, name]['searchWallNs'] for name in ['control', 'budget1']]
        lower[case] = all(worker['median'] < value['median'] for value in others)
        separated[case] = all(worker['max'] < value['min'] for value in others)
    ratios = {name: sums['budget2']/sums[name] for name in ['control', 'budget1']}
    return dict(passed=all(lower.values()) and all(sums['budget2']*100 <= sums[name]*98 for name in ['control', 'budget1']) and sum(separated.values()) >= 2,
                workerMedianLowerBothByCase=lower, workerRangeBelowBothByCase=separated,
                workerSelectedSumRatios=ratios,
                rule='budget2 medians lower than control and budget1 in all3; selected summed medians gain>=2% versus both; >=2 cases max budget2<min both controls',
                automaticExtension=False)


def collection_audit(base, plan):
    result = read(base/'result.json')
    assert result['complete'] and result['failure'] is None
    full = plan['study'] == 'original54'
    assert plan['study'] in ['three-case', 'original54']
    build, effective = check_build(Path(plan['candidateBuildDirectory']), 'profile-use')
    assert effective == plan['effectiveRustcOptions']
    assert plan['variants']['control']['sha256'] == CONTROL_SHA
    assert plan['variants']['control']['args'] == [] and plan['variants']['control']['threads'] == 1
    assert set(plan['variants']) == set(VARIANTS)
    for name, budget in [('budget1', 1), ('budget2', 2)]:
        value = plan['variants'][name]
        assert value['sha256'] == build['binary_output']['sha256'] and value['threads'] == budget
        assert value['args'] == [f'--research-threads={budget}']
    compatibility = plan['controlCompatibility']
    old = read(Path(compatibility['receipt']))
    assert old['binary_output']['sha256'] == compatibility['acceptedArtifactSha256'] == CONTROL_SHA
    assert old['target_triple'] == build['target_triple'] and old['target_cpu'] == build['target_cpu']
    assert all(old['toolchain'][tool]['stdout'] == build['toolchain'][tool]['stdout'] for tool in ['rustc', 'cargo'])
    assert all(old['toolchain'][tool+'_executable_sha256'] == build['toolchain'][tool+'_executable_sha256']
               for tool in ['rustc', 'cargo'])
    assert any(value['sha256'] == CONTROL_SHA for value in read(ROOT/'release/qualification.json')['artifacts'])
    cases = [case['id'] for case in read(SPEC/'workloads.json')['cases']] if full else SMALL_CASES
    assert plan['cases'] == cases
    schedule = []
    for index, case in enumerate(cases):
        if full:
            order = VARIANTS[index % 3:]+VARIANTS[:index % 3]
            schedule += [dict(case=case, variant=name, warmup=False, repeat=1) for name in order]
        else:
            schedule += [dict(case=case, variant=name, warmup=True, repeat=0) for name in VARIANTS]
            for repeat in range(3):
                order = VARIANTS[repeat:]+VARIANTS[:repeat]
                schedule += [dict(case=case, variant=name, warmup=False, repeat=repeat+1) for name in order]
    assert schedule == plan['schedule'] and len(result['runs']) == len(schedule) == (162 if full else 36)
    posts = 0
    for index, (step, row) in enumerate(zip(schedule, result['runs'])):
        variant = plan['variants'][step['variant']]
        directory = base/f'{index:03d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        _, count = lifetime(directory, row, step, Path(variant['path']), variant['threads'], variant['args'], plan['inputs'])
        posts += count
    assert plan['idleVariants'] == ([] if full else VARIANTS) and len(result['idle']) == (0 if full else 3)
    for row, name in zip(result['idle'], VARIANTS):
        assert row['variant'] == name
        directory, variant = base/('idle-'+name), plan['variants'][name]
        assert read(directory/'probe.json') == row
        native = native_receipt(directory/'native.json', Path(variant['path']), variant['threads'], variant['args'], plan['inputs'])
        assert row['nativePid'] == native['native_pid'] and row['supervisorPid'] == native['supervisor_pid']
        expected_command = [native['python_executable'], str(ACCOUNT), '--engine', variant['path'],
                            '--record', str(directory/'native.json'), '--known-single-process',
                            '--thread-budget', str(variant['threads']), *variant['args']]
        assert read(directory/'launch.json') == dict(argv=expected_command, variant=name, kind='startup-idle-shutdown')
        assert (directory/'stdin.raw').read_bytes() == b'cm_parm\nquit\n'
        assert (directory/'stdout.raw').read_bytes() == b'cm_parm\n' and (directory/'stderr').read_bytes() == b''
        assert row['idleNs'] >= 250_000_000 and row['idleCpuTicks'] >= 0 and row['tickHz'] > 0
        assert row['shutdownStartCpuTicks'] - row['startupCpuTicks'] == row['idleCpuTicks']
        assert row['idleCpuSeconds'] == row['idleCpuTicks']/row['tickHz']
        assert row['wholeCpuSeconds'] == native['total_cpu_s'] and row['wholeWallNs'] == native['wall_ns']
        assert row['rssKiB'] == native['maxrss_linux_kib'] and row['startupReplyNs'] > 0 and row['shutdownSupervisorNs'] > 0
        assert set(row['sha256']) == {'launch.json', 'native.json', 'stdin.raw', 'stdout.raw', 'stderr'}
        for path, digest in row['sha256'].items():
            assert sha(directory/path) == digest
    summaries = []
    for case in cases:
        for name in VARIANTS:
            rows = [row for row in result['runs'] if (row['case'], row['variant'], row['warmup']) == (case, name, False)]
            assert len(rows) == (1 if full else 3)
            original = next(value for value in result['summaries'] if (value['case'], value['variant']) == (case, name))
            summary = dict(case=case, variant=name)
            for metric in METRICS:
                values = [row[metric] for row in rows]
                regenerated = distribution(values)
                assert regenerated == original[metric]
                summary[metric] = dict(**regenerated, mean=statistics.mean(values))
            summaries.append(summary)
    assert len(result['summaries']) == len(summaries) == len(cases)*3
    assert result['extensionGate'] == (None if full else gate(summaries))
    by = {(row['case'], row['variant']): row for row in summaries}
    comparisons = []
    for case in cases:
        control, one, two = [by[case, name] for name in VARIANTS]
        comparisons.append(dict(case=case,
            serialWallRatioVsControl=one['searchWallNs']['median']/control['searchWallNs']['median'],
            workerWallRatioVsBudget1=two['searchWallNs']['median']/one['searchWallNs']['median'],
            workerWallRatioVsControl=two['searchWallNs']['median']/control['searchWallNs']['median'],
            workerWholeCpuRatioVsBudget1=two['wholeCpuSeconds']['median']/one['wholeCpuSeconds']['median']))
    sums = {name: {metric: sum(by[case, name][metric]['median'] for case in cases)
                   for metric in ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs']} for name in VARIANTS}
    return dict(kind='production-collection', study=plan['study'], complete=True,
                nativeProcesses=len(schedule)+len(result['idle']), strictReplayLifetimes=len(schedule),
                measuredReplayObservations=162 if full else 27, excludedWarmups=0 if full else 9,
                idleProcesses=len(result['idle']), orderedPosts=posts, comparisons=comparisons,
                summedMedians=sums, summaries=summaries, idle=result['idle'], extensionGate=result['extensionGate'],
                notes='Case medians and ranges only; full54 has one observation per configuration/case. Whole CPU includes all native threads/lifecycle; idle ticks are quantized. No current KingWCR or performance-qualification claim.',
                rawSha256={name: sha(base/name) for name in ['plan.json', 'result.json', 'proc-stat-before', 'proc-stat-after']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = args.directory.resolve()
    plan = read(base/'plan.json')
    assert plan['coordinatorCpu'] == 14 and plan['workerCpu'] == 6
    assert plan['helperAffinity'] == sorted(HELPERS)
    for path, digest in plan['inputs'].items():
        assert sha(Path(path)) == digest, 'pinned input changed: '+path
    if plan['schema'] == 'rook2-full-split-training-plan-v1':
        result = training_audit(base, plan)
    else:
        assert plan['schema'] == 'rook2-full-split-production-plan-v1'
        assert plan['helperAffinity'] == sorted(HELPERS) and plan['idleOwnedSiblings'] == [7, 15]
        result = collection_audit(base, plan)
    result.update(rawDirectory=str(base), reconcilerSha256=sha(Path(__file__)),
                  stdinCapture='Exact captured write() setup/query/search bytes; end(data) cleanup is outside this pinned tap. Pinned runner source and complete raw stdout/stderr/exit retain shutdown checks.')
    destination = args.output.resolve() if args.output else base/'reconciled.json'
    with destination.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    printed = {key: value for key, value in result.items() if key not in ['summaries', 'idle', 'rawSha256']}
    print(json.dumps(printed, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
