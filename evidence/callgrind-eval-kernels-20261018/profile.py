#!/usr/bin/env python3
"""Refresh one exact ordinary replay under the previously verified Ir simulator."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BUILD = ROOT/'evidence/production-eval-kernels-use-build-20261018'
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
PREFIX = Path('/home/legolas/.local/imp2-tools/valgrind/usr')
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def run(command, stem, env):
    stdout, stderr = OUT/(stem+'.stdout'), OUT/(stem+'.stderr')
    with stdout.open('xb') as out, stderr.open('xb') as err:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=err)
    return dict(command=command, exit_code=result.returncode, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))


def main():
    prior = load(ROOT/'evidence/callgrind-pgo-20261018/provenance.json')
    assert all(sha(Path(p)) == item['sha256'] for p, item in prior['files'].items())
    cpu_terminal = ROOT/'evidence/production54-eval-kernels-preparation-20261018/driver-terminal.json'
    cpu_verification = ROOT/'evidence/production54-cpu-eval-kernels-20261018/verification.json'
    assert load(cpu_terminal)['collector_returncode'] == 0
    assert load(cpu_verification)['complete'] and load(cpu_verification)['lifetimes_independently_reconciled'] == 216
    engine = BUILD/'rook2-exact'
    build = load(BUILD/'receipt.json')
    identity = sha(engine)
    assert identity == build['binary_output']['sha256'] == '8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953'
    before = source_snapshot(ROOT)
    assert before == build['source_sha256_before']
    dependencies = [Path(__file__), BUILD/'receipt.json', cpu_terminal, cpu_verification,
                    SPEC/'replay-check.mjs', SPEC/'workloads.json', SPEC/'replay-oracle.json',
                    PREFIX/'bin/valgrind', PREFIX/'bin/callgrind_annotate', PREFIX/'libexec/valgrind/callgrind-amd64-linux']
    dependencies += sorted((PREFIX/'libexec/valgrind').glob('vgpreload*callgrind*'))
    dependencies += sorted((PREFIX/'libexec/valgrind').glob('vgpreload_core*'))
    hashes = {str(p):sha(p) for p in dependencies}
    env = dict(os.environ, VALGRIND_LIB=str(PREFIX/'libexec/valgrind'))
    command = ['/usr/bin/node', str(SPEC/'replay-check.mjs'), '--case', 'profile-01', '--',
               '/usr/bin/taskset', '-c', '14', '/usr/bin/env', 'VALGRIND_LIB='+env['VALGRIND_LIB'],
               str(PREFIX/'bin/valgrind'), '--tool=callgrind', '--cache-sim=no', '--branch-sim=no',
               '--callgrind-out-file='+str(OUT/'profile-01.callgrind'), '--log-file='+str(OUT/'profile-01.log'), str(engine)]
    write('plan.json', dict(command=command, artifact_sha256=identity, input_sha256=hashes, source_sha256=before,
          helper_affinity=sorted(os.sched_getaffinity(0)), environment={'VALGRIND_LIB':env['VALGRIND_LIB']},
          native_modes='Appended unchanged by released replay checker from replay-oracle.json',
          bounds='One fixed case; unmodified checker owns30s setup/900s search/5s cleanup and4MiB original streams. Profile/log retained whole; final local64MiB profile cap.',
          event='Ir simulated user instructions for whole guest lifetime; no PMU retired I/cycles or native CPU-time interpretation',
          ownership='Only this owned simulator/engine run; no concurrent owned build, tests, other engine collection or profiler'))
    stage = run(command, 'profile-01-oracle', env)
    report = load(OUT/'profile-01-oracle.stdout')
    assert stage['exit_code'] == 0 and report['status'] == 'pass' and report['selectedCases'] == ['profile-01']
    assert len(report['results']) == 1 and report['results'][0]['exit'] == dict(code=0, signal=None)
    assert not (OUT/'profile-01-oracle.stderr').stat().st_size
    data = OUT/'profile-01.callgrind'
    assert data.stat().st_size <= 67108864
    lines = data.read_text().splitlines()
    assert [line for line in lines if line.startswith('events:')] == ['events: Ir']
    totals = [int(line.split(':', 1)[1]) for line in lines if line.startswith('summary:')]
    assert len(totals) == 1 and totals[0] > 0
    annotations = {}
    for stem, args in [('functions', ['--threshold=99']), ('activity-lines', ['--context=0', 'src/activity.rs']),
                       ('influence-lines', ['--context=0', 'src/influence.rs']), ('movegen-lines', ['--context=0', 'src/movegen.rs'])]:
        extra = args[:1] + [str(data)] + args[1:]
        result = run([str(PREFIX/'bin/callgrind_annotate'), '--auto=no', *extra], stem, env)
        assert result['exit_code'] == 0
        annotations[stem] = result
    assert source_snapshot(ROOT) == before and sha(engine) == identity
    assert hashes == {str(p):sha(p) for p in dependencies}
    write('provenance.json', dict(complete=True, native_artifact_sha256=identity, total_simulated_ir=totals[0],
          source_sha256=before, input_sha256=hashes, oracle=stage, profile_sha256=sha(data),
          log_sha256=sha(OUT/'profile-01.log'), annotations=annotations, driver_sha256=sha(Path(__file__)),
          prior_3660_simulated_ir=prior['total_simulated_ir'],
          historical_ir_ratio=totals[0]/prior['total_simulated_ir'],
          historical_scope='Multiple implementation/profile changes and changed inlining attribution; not isolated kernel attribution or PMU comparison',
          event='Whole-lifetime Ir simulation only; not retired instructions, cycles, CPI/IPC or native timing'))
    print(json.dumps(dict(complete=True, artifact_sha256=identity, total_simulated_ir=totals[0], strict_replay='pass')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
