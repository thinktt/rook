"""Own-PGO admissions and scoped reuse of frozen external-placement machinery.

No process starts on import. Frozen modules and their source bytes are unchanged.
"""
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
USABLE = HERE.parent/'usable-full'
ORIGINAL = HERE.parent/'full-split-production'
SERIAL_BUILD = Path('/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build')
PREVIOUS_BUILD = Path('/home/legolas/rook2-experiments/full-split-production-20261024-01/use-build')
SERIAL_SHA = '5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a'
PREVIOUS_SHA = 'a977bb0031b1beeb6fb50f8c391968f6e2d959ae86d648727442bdf027c88763'
CASES = ['profile-35', 'profile-08', 'profile-04', 'profile-43']
NAMES = ['serial1', 'previous2', 'cleaned1', 'cleaned2']
METRICS = ['searchWallNs', 'wholeCpuSeconds', 'wholeWallNs', 'nonSearchWallNs', 'rssKiB']


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


usable = module('configured_full_frozen_usable_common', USABLE/'common.py')
ACCOUNT, SPEC, HELPERS = usable.ACCOUNT, usable.SPEC, usable.HELPERS
sha, read, write = usable.sha, usable.read, usable.write
train, audit = usable.train, usable.audit
run_lifetime = usable.run_lifetime
native_receipt, audit_placement = usable.native_receipt, usable.audit_placement


def frozen_module(name, path):
    # The frozen collectors import a module literally named common. Bind only
    # during their import; their functions retain the frozen objects afterwards.
    previous = sys.modules.get('common')
    try:
        sys.modules['common'] = usable
        return module(name, path)
    finally:
        if previous is None:
            del sys.modules['common']
        else:
            sys.modules['common'] = previous


idle_probe = frozen_module('configured_full_frozen_usable_collect', USABLE/'collect.py').idle_probe
guest_ticks = frozen_module('configured_full_frozen_usable_reconcile', USABLE/'reconcile.py').guest_ticks


def variants(serial, previous, candidate):
    return dict(serial1=dict(path=str(serial), budget=1, options=[]),
                previous2=dict(path=str(previous), budget=2, options=['--research-threads=2']),
                cleaned1=dict(path=str(candidate), budget=1, options=['--threads=1']),
                cleaned2=dict(path=str(candidate), budget=2, options=['--threads=2']))


def schedule(full54=False):
    cases = [row['id'] for row in read(SPEC/'workloads.json')['cases']] if full54 else CASES
    assert not full54 or len(cases) == len(set(cases)) == 54
    steps = []
    for i, case in enumerate(cases):
        if full54:
            order = NAMES[i % 4:]+NAMES[:i % 4]
            steps += [dict(case=case, variant=name, warmup=False, repeat=1) for name in order]
        else:
            steps += [dict(case=case, variant=name, warmup=True, repeat=0) for name in NAMES]
            for repeat in range(3):
                order = NAMES[repeat:]+NAMES[:repeat]
                steps += [dict(case=case, variant=name, warmup=False, repeat=repeat+1) for name in order]
    assert len(steps) == (216 if full54 else 64)
    return cases, steps


def admission(build, serial, previous, candidate):
    receipt, image, effective = train.admit_build(build, 'profile-use')
    assert sha(candidate) == sha(image) == receipt['binary_output']['sha256']
    assert sha(serial) == SERIAL_SHA and sha(previous) == PREVIOUS_SHA
    compatibility = {}
    for name, directory, expected in [('serial1', SERIAL_BUILD, SERIAL_SHA),
                                      ('previous2', PREVIOUS_BUILD, PREVIOUS_SHA)]:
        old = read(directory/'receipt.json')
        assert old['outcome'] == 'build-succeeded-with-stable-input-snapshot' and old['cargo_exit_code'] == 0
        assert old['binary_output']['sha256'] == expected and old['pgo']['mode'] == 'profile-use'
        assert old['target_cpu'] == receipt['target_cpu'] == 'x86-64'
        assert old['target_triple'] == receipt['target_triple'] == 'x86_64-unknown-linux-gnu'
        for tool in ['rustc', 'cargo']:
            assert old['toolchain'][tool] == receipt['toolchain'][tool]
            assert old['toolchain'][tool+'_executable_sha256'] == receipt['toolchain'][tool+'_executable_sha256']
        compatibility[name] = dict(receipt=str(directory/'receipt.json'),
                                    sha256=sha(directory/'receipt.json'), imageSha256=expected)
    return receipt, effective, compatibility


def input_paths(build, receipt, serial, previous, candidate):
    # A fixed code closure avoids accidentally binding later reports/raw outputs.
    paths = [HERE/n for n in ['common.py', 'collect.py', 'reconcile.py']]
    paths += [USABLE/n for n in ['common.py', 'collect.py', 'reconcile.py',
                                 'account_threads.py', 'placement_gate.mjs', 'tools/tap_wire.mjs']]
    paths += [ORIGINAL/n for n in ['train.py', 'reconcile.py']]
    paths += [ROOT/'tools/tap_wire.mjs', ROOT/'tools/compare_ordinary.py',
              SPEC/'replay-check.mjs', SPEC/'benchmark.mjs', SPEC/'workloads.json', SPEC/'replay-oracle.json',
              serial, previous, candidate, build/'receipt.json', build/'build.stderr',
              SERIAL_BUILD/'receipt.json', PREVIOUS_BUILD/'receipt.json',
              Path(receipt['pgo']['profile']), Path(receipt['pgo']['training_record'])]
    paths += [build/'source-before'/name for name in receipt['source_sha256_before']]
    return paths
