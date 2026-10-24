#!/usr/bin/env python3
"""One source-bound original54 training pass per FULL split mode, one profile merge.

Importing supplies shared collection helpers but starts no process. Native jobs
are launched only by main(), under the explicit parent's announced native window.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
import tomllib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ACCOUNT = HERE.parent/'integration/account_threads.py'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
CONTROL_SHA = '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a'
sys.path.insert(0, str(ROOT/'tools'))
from compare_ordinary import stop_owned


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temporary.replace(path)


def source_snapshot(root):
    paths = [root/'Cargo.toml', root/'Cargo.lock']
    paths += sorted(path for path in (root/'src').rglob('*') if path.is_file())
    paths += [root/name for name in ['build.rs', 'rust-toolchain', 'rust-toolchain.toml'] if (root/name).is_file()]
    return {str(path.relative_to(root)): sha(path) for path in paths}


def effective_options(directory, mode, profile):
    commands = [shlex.split(line.split('Running `', 1)[1].rsplit('`', 1)[0])
                for line in (directory/'build.stderr').read_text().splitlines()
                if 'Running `' in line and '--crate-name rook2 ' in line]
    observed = {}
    for source, kind in [('src/lib.rs', 'lib'), ('src/bin/rook2.rs', 'bin')]:
        matches = [argv for argv in commands if source in argv]
        assert len(matches) == 1, (source, len(matches))
        argv = matches[0]
        assert argv[argv.index('--crate-type')+1] == kind
        options = {}
        for index, token in enumerate(argv):
            if token == '-C':
                item = argv[index+1]
            elif token.startswith('-C') and len(token) > 2:
                item = token[2:]
            else:
                continue
            key, separator, value = item.partition('=')
            assert key not in options, (source, key)
            options[key] = value if separator else True
        for key, value in [('opt-level', '3'), ('panic', 'abort'), ('codegen-units', '1'),
                           ('debuginfo', '1'), ('target-cpu', 'x86-64')]:
            assert options.get(key) == value, (source, key, options)
        if kind == 'bin':
            assert options.get('lto') == 'thin' and 'linker-plugin-lto' not in options
        else:
            assert options.get('linker-plugin-lto') is True and 'lto' not in options
        key = 'profile-generate' if mode == 'instrumented' else 'profile-use'
        assert options.get(key) == str(profile)
        assert ('profile-use' if mode == 'instrumented' else 'profile-generate') not in options
        if mode == 'instrumented':
            assert 'llvm-args' not in options
        else:
            assert options.get('llvm-args') == ('-pgo-warn-missing-function '
                '-enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false')
        observed[source] = options
    return observed


def admit_build(directory, mode):
    build = read(directory/'receipt.json')
    assert build['schema'] == 'rook2-development-build-v1'
    assert build['outcome'] == 'build-succeeded-with-stable-input-snapshot' and build['cargo_exit_code'] == 0
    assert build['mode'] == 'generic' and build['target_triple'] == 'x86_64-unknown-linux-gnu'
    assert build['target_cpu'] == 'x86-64' and build['binary_name'] == 'rook2'
    assert build['pgo']['mode'] == mode
    assert build['source_sha256_before'] == build['source_sha256_after']
    assert build['tool_sha256_before'] == build['tool_sha256_after']
    assert build['cargo_config_sha256_before'] == build['cargo_config_sha256_after']
    rustc = build['toolchain']['rustc']
    assert rustc['exit_code'] == 0 and 'release: 1.85.1\n' in rustc['stdout']
    assert 'LLVM version: 19.1.7\n' in rustc['stdout']
    assert build['toolchain']['cargo']['exit_code'] == 0
    image = Path(build['binary_output']['path']).resolve()
    assert sha(image) == build['binary_output']['sha256']
    source = Path(build['crate'])
    assert source_snapshot(source) == build['source_sha256_before']
    for name, digest in build['source_sha256_before'].items():
        assert sha(directory/'source-before'/name) == digest
    manifest = tomllib.loads((source/'Cargo.toml').read_text())
    release = manifest['profile']['release']
    assert release == {'opt-level': 3, 'lto': 'thin', 'codegen-units': 1, 'panic': 'abort', 'debug': 1}
    profile = Path(build['pgo']['profile_directory'] if mode == 'instrumented' else build['pgo']['profile'])
    effective = effective_options(directory, mode, profile)
    if mode == 'profile-use':
        assert build['pgo']['code_layout']['profiled_functions_only'] is True
        assert build['pgo']['inputs_unchanged'] is True
        for path, digest in build['pgo']['input_sha256_before'].items():
            assert sha(Path(path)) == digest
        training = read(Path(build['pgo']['training_record']))
        assert training['schema'] == 'rook2-pgo-training-v1' and training['complete']
        assert training['engine_source_sha256'] == build['source_sha256_before']
        assert training['target_triple'] == build['target_triple']
        assert training['base_rust_flags'] == ['-C', 'target-cpu=x86-64']
        assert training['profile_sha256'] == sha(profile)
        log = (directory/'build.stderr').read_text().lower()
        assert not any(text in log for text in ['no profile data available for function',
            'profile data may be out of date', 'profile data mismatch', 'malformed instrumentation profile',
            'hash mismatch', 'unprofiled function'])
    return build, image, effective


def supervisor(image, budget, directory, options):
    return [sys.executable, str(ACCOUNT), '--engine', str(image), '--record', str(directory/'native.json'),
            '--known-single-process', '--thread-budget', str(budget), *options]


def run_lifetime(directory, step, image, budget, options, deadline, profile_pattern=None):
    directory.mkdir()
    native = supervisor(image, budget, directory, options)
    modes = read(SPEC/'replay-oracle.json')['mode']
    config = dict(version=1, expectedArgv=native+modes, directory=str(directory/'wire'),
                  nativeExecutable=str(image), maxRawBytes=8*1024*1024, tickHz=os.sysconf('SC_CLK_TCK'))
    write(directory/'tap-config.json', config)
    env = dict(os.environ, ROOK2_WIRE_TAP_CONFIG=str(directory/'tap-config.json'))
    env.pop('LLVM_PROFILE_FILE', None)
    if profile_pattern:
        env['LLVM_PROFILE_FILE'] = str(profile_pattern)
    command = ['/usr/bin/node', '--import', str(ROOT/'tools/tap_wire.mjs'),
               str(SPEC/'replay-check.mjs'), '--case', step['case'], '--', *native]
    write(directory/'launch.json', dict(argv=command, step=step,
          profileEnvironment={'LLVM_PROFILE_FILE': str(profile_pattern)} if profile_pattern else {}))
    run_deadline = min(deadline, time.monotonic()+180)
    with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        try:
            while child.poll() is None:
                if time.monotonic() >= run_deadline:
                    raise RuntimeError('per-lifetime or aggregate deadline')
                if ((directory/'stdout').stat().st_size > 8*1024*1024
                        or (directory/'stderr').stat().st_size > 1024*1024):
                    raise RuntimeError('comparator stream cap')
                if (directory/'wire/failure.json').exists():
                    raise RuntimeError('raw tap failed')
                time.sleep(.05)
        except BaseException:
            stop_owned(child)
            write(directory/'failure.json', dict(exit=child.poll(), step=step))
            raise
    assert child.returncode == 0 and (directory/'stderr').stat().st_size == 0
    assert (directory/'stdout').stat().st_size <= 8*1024*1024
    replay, receipt, tap = (read(directory/path) for path in ['stdout', 'native.json', 'wire/receipt.json'])
    assert replay['status'] == 'pass' and replay['selectedCases'] == [step['case']]
    assert len(replay['results']) == 1
    actual = replay['results'][0]
    assert actual['status'] == 'pass' and actual['complete'] and not actual['truncated']
    assert actual['error'] is None and actual['discardedObservedBytes'] == 0
    assert actual['exit'] == dict(code=0, signal=None) and actual['command'] == native+modes
    assert receipt['failure'] is None and receipt['native_exit_code'] == 0 and receipt['supervisor_signals'] == []
    assert receipt['engine_sha256_before'] == receipt['engine_sha256_after'] == sha(image)
    assert receipt['launcher_sha256'] == sha(ACCOUNT)
    assert receipt['argv'] == [str(image), *options, *modes] and receipt['expected_threads'] == budget
    affinities = receipt['native_post_exec']['task_affinities']
    assert len(affinities) == budget and affinities[str(receipt['native_pid'])] == [14]
    assert all(cpus == [6] for tid, cpus in affinities.items() if tid != str(receipt['native_pid']))
    assert tap['failure'] is None and tap['pending'] is None and len(tap['searches']) == 1
    search = tap['searches'][0]
    for boundary in ['beforeWrite', 'afterData']:
        assert search[boundary]['available'] and search[boundary]['pid'] == receipt['native_pid']
        assert search[boundary]['lastProcessor'] == 14
    for stream, item in tap['raw'].items():
        path = directory/'wire'/f'{stream}.raw'
        assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'] == item['observedBytes']
        assert item['discardedObservedBytes'] == 0
    assert (directory/'wire/stdout.raw').read_bytes() == actual['stdout'].encode()
    assert (directory/'wire/stderr.raw').read_bytes() == actual['stderr'].encode()
    assert (directory/'wire/stdin.raw').read_bytes().splitlines().count(b'go') == 1
    for pid in [receipt['native_pid'], receipt['supervisor_pid']]:
        assert not Path(f'/proc/{pid}').exists()
    row = dict(**step, directory=str(directory), nativePid=receipt['native_pid'],
               searchWallNs=search['wallNs'], wholeCpuSeconds=receipt['total_cpu_s'],
               wholeWallNs=receipt['wall_ns'], nonSearchWallNs=receipt['wall_ns']-search['wallNs'],
               rssKiB=receipt['maxrss_linux_kib'], taskAffinities=affinities,
               sha256={name: sha(directory/name) for name in ['native.json', 'stdout', 'stderr', 'wire/receipt.json',
                                                           'tap-config.json', 'launch.json']})
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile-root', type=Path)
    args = parser.parse_args()
    build_directory = args.build.resolve()
    build, image, effective = admit_build(build_directory, 'instrumented')
    profile_root = (args.profile_root or Path(build['pgo']['profile_directory'])).resolve()
    assert profile_root == Path(build['pgo']['profile_directory']).resolve()
    assert profile_root.is_dir() and not list(profile_root.iterdir()), 'generated profile root must be empty'
    out = args.output.resolve()
    assert out != profile_root and profile_root not in out.parents
    out.mkdir()
    workloads = read(SPEC/'workloads.json')['cases']
    assert len(workloads) == 54 and len({case['id'] for case in workloads}) == 54
    schedule = [dict(case=case['id'], budget=budget, variant=f'budget{budget}')
                for budget in [1, 2] for case in workloads]
    inputs = [Path(__file__), HERE/'collect.py', HERE/'reconcile.py', ACCOUNT, ROOT/'tools/tap_wire.mjs',
              ROOT/'tools/compare_ordinary.py', ROOT/'tools/build.py', build_directory/'receipt.json',
              build_directory/'build.stderr', SPEC/'workloads.json', SPEC/'replay-oracle.json',
              SPEC/'replay-check.mjs', SPEC/'benchmark.mjs', image]
    manifest = dict(schema='rook2-full-split-training-plan-v1', schedule=schedule,
                    buildDirectory=str(build_directory), image=str(image), imageSha256=sha(image),
                    profileRoot=str(profile_root), source=build['source_sha256_before'],
                    effectiveRustcOptions=effective, inputs={str(path): sha(path) for path in inputs},
                    coordinatorCpu=14, workerCpu=6, helperAffinity=sorted(HELPERS), quietSiblings=[7, 15],
                    limits=dict(perLifetimeSeconds=180, aggregateSeconds=2400, rawProfileBytes=256*1024*1024,
                                nativeRawBytesPerLifetime=8*1024*1024, ownedCleanupSeconds=10),
                    mergeTool='/usr/bin/llvm-profdata-19', mergeToolSha256=sha(Path('/usr/bin/llvm-profdata-19').resolve()),
                    adaptation='One image, original54 once with --research-threads=1 and once with2; equal raw merge weights; no repeated training',
                    performance='instrumented training only; not production timings')
    write(out/'plan.json', manifest)
    original_affinity = os.sched_getaffinity(0)
    assert HELPERS <= original_affinity
    os.sched_setaffinity(0, HELPERS)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    rows, raw_hashes = [], {}
    deadline = time.monotonic()+2400
    try:
        for index, step in enumerate(schedule):
            assert time.monotonic() < deadline, 'aggregate training deadline'
            profile_directory = profile_root/f'{index:03d}-{step["case"]}-b{step["budget"]}'
            profile_directory.mkdir()
            pattern = profile_directory/'native-%p.profraw'
            row = run_lifetime(out/f'{index:03d}-{step["case"]}-b{step["budget"]}', step, image,
                               step['budget'], [f'--research-threads={step["budget"]}'], deadline, pattern)
            profile = profile_directory/f'native-{row["nativePid"]}.profraw'
            assert list(profile_directory.iterdir()) == [profile] and profile.stat().st_size > 0
            raw_hashes[str(profile)] = sha(profile)
            assert sum(Path(path).stat().st_size for path in raw_hashes) <= manifest['limits']['rawProfileBytes']
            row.update(profile=str(profile), profileSha256=sha(profile))
            rows.append(row)
            write(out/'progress.json', dict(complete=False, runs=rows))
        assert len(rows) == len(raw_hashes) == 108
        assert len({row['nativePid'] for row in rows}) == 108
        assert {str(path) for path in profile_root.rglob('*.profraw')} == set(raw_hashes)
        assert all(sha(Path(path)) == digest for path, digest in manifest['inputs'].items())
        assert source_snapshot(Path(build['crate'])) == build['source_sha256_before']
        assert time.monotonic() < deadline, 'aggregate training deadline before merge'
        version = subprocess.run(['/usr/bin/llvm-profdata-19', '--version'], capture_output=True,
                                 text=True, check=True, timeout=min(10, deadline-time.monotonic()))
        write(out/'merge-tool.json', dict(argv=['/usr/bin/llvm-profdata-19', '--version'],
              exit=version.returncode, stdout=version.stdout, stderr=version.stderr,
              sha256=manifest['mergeToolSha256']))
        merge = ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(out/'merged.profdata'), *sorted(raw_hashes)]
        assert time.monotonic() < deadline, 'aggregate training deadline before merge'
        started = time.monotonic_ns()
        with (out/'merge.stdout').open('xb') as stdout, (out/'merge.stderr').open('xb') as stderr:
            child = subprocess.Popen(merge, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=max(.01, min(60, deadline-time.monotonic())))
            except BaseException:
                child.kill(); child.wait(); raise
        write(out/'merge.json', dict(argv=merge, pid=child.pid, exit=code, elapsedNs=time.monotonic_ns()-started))
        assert code == 0 and (out/'merge.stderr').stat().st_size == 0
        assert all(sha(Path(path)) == digest for path, digest in raw_hashes.items())
        assert all(sha(Path(path)) == digest for path, digest in manifest['inputs'].items())
        training = dict(schema='rook2-pgo-training-v1', complete=True,
                        engine_source_sha256=build['source_sha256_before'],
                        target_triple=build['target_triple'], base_rust_flags=['-C', 'target-cpu=x86-64'],
                        effective_rustc_options=effective,
                        instrumented_build_receipt=dict(path=str(build_directory/'receipt.json'),
                                                        sha256=sha(build_directory/'receipt.json')),
                        instrumented_engine_sha256=sha(image), input_sha256=manifest['inputs'],
                        raw_profiles_sha256=raw_hashes, merge_command=merge,
                        merge_tool_sha256=manifest['mergeToolSha256'], merge_tool_version=version.stdout,
                        profile_sha256=sha(out/'merged.profdata'), driver_sha256=sha(Path(__file__)),
                        modes=[dict(budget=budget, originalCases=54) for budget in [1, 2]],
                        original_lifetimes=108, runs=rows,
                        adaptation=manifest['adaptation'], plan_sha256=sha(out/'plan.json'),
                        merge_record_sha256=sha(out/'merge.json'),
                        performance='Training only; original replay/normal exit and worker Drop join precede profile flush; no production timing interpretation')
        write(out/'training.json', training)
    except BaseException as error:
        write(out/'failure.json', dict(complete=False, failure=repr(error), completedLifetimes=len(rows)))
        raise
    finally:
        (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
        os.sched_setaffinity(0, original_affinity)
    print(json.dumps(dict(complete=True, lifetimes=108, profile_sha256=training['profile_sha256'],
                         profile=str(out/'merged.profdata'), training=str(out/'training.json'))))


if __name__ == '__main__':
    main()
