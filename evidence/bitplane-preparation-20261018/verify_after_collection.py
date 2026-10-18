#!/usr/bin/env python3
"""Deferred matched bitplane validation and generic CPU pilot; no adoption."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIVE = ROOT/'evidence/production12-cpu-20261018-pgo'
PROFILE = Path('/home/legolas/king-spec/conformance/profiling')
BASE = ROOT/'evidence/eval-geometry-build-20261018-02'
BASE_CHECK = ROOT/'evidence/eval-geometry-check-20261018-02'
CASES = ['profile-01','profile-02','profile-04','profile-05','profile-35','profile-29']
sys.path.insert(0,str(ROOT/'tools'))
from build import source_snapshot
from measure import cgroup_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2); stream.write('\n')


def context():
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                helper_affinity=sorted(os.sched_getaffinity(0)),uname=list(os.uname()),
                cgroups=cgroup_snapshot(),proc_stat=Path('/proc/stat').read_text(),
                loadavg=Path('/proc/loadavg').read_text(),
                scope='Local point observations; no claim of exclusive host ownership or final qualification')


def run(argv, directory, stem, env):
    stdout,stderr = directory/(stem+'.stdout'),directory/(stem+'.stderr')
    with stdout.open('xb') as out,stderr.open('xb') as err:
        result = subprocess.run(argv,cwd=ROOT,env=env,stdout=out,stderr=err)
    return dict(command=argv,exit_code=result.returncode,
                stdout_sha256=sha(stdout),stderr_sha256=sha(stderr))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',default='20261018',help='Fresh absent attempt label; failures are never overwritten')
    parser.add_argument('--checks-only',action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.label): parser.error('invalid label')
    terminal = LIVE/'terminal.json'
    if not terminal.exists(): parser.error('poll existing collector handle37105 to actual termination first')
    manifest = json.loads((LIVE/'collection/manifest.json').read_text())
    active = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            argv = (proc/'cmdline').read_bytes().decode().split('\0')
            image = os.readlink(proc/'exe')
            if (str(LIVE/'driver.py') in argv or image == manifest['engine']
                    or (str(ROOT/'tools/collect_games.py') in argv and str(LIVE/'collection') in argv)):
                active.append(int(proc.name))
        except (OSError,UnicodeDecodeError): pass
    if active: parser.error(f'prior collector/native still live: {active}')
    prepared = json.loads((HERE/'prepared.json').read_text())
    archived = json.loads((HERE/'archive.json').read_text())
    if sha(HERE/archived['archive']) != archived['archive_sha256']: parser.error('preparation archive changed')
    if source_snapshot(ROOT) != prepared['base_native_source_sha256']: parser.error('root native source changed')
    variants = {name:Path(item['path']) for name,item in prepared['variants'].items()}
    for name,path in variants.items():
        if source_snapshot(path) != prepared['variants'][name]['source_sha256']: parser.error(f'{name} source changed')
    for name,digest in archived['files'].items():
        variant,relative = name.split('/',1)
        if sha(variants[variant]/relative) != digest: parser.error(f'prepared dependency changed: {name}')
    if len({sha(p/'src/attacks.rs') for p in variants.values()}) != 1: parser.error('query kernels differ')
    base_identity = json.loads((BASE_CHECK/'profile-identity.json').read_text())
    base_report = json.loads((BASE_CHECK/'profile-all.json').read_text())
    base_build = json.loads((BASE/'receipt.json').read_text())
    baseline = BASE/'rook2-exact'
    if (sha(baseline) != base_identity['native_artifact_sha256']
            or sha(BASE_CHECK/'profile-all.json') != base_identity['replay_sha256']
            or sha(BASE/'receipt.json') != base_identity['build_receipt_sha256']
            or base_build['source_sha256_before'] != prepared['base_native_source_sha256']
            or base_report['status'] != 'pass' or len(base_report['results']) != 54):
        parser.error('baseline replay/build/artifact binding failed')
    output = ROOT/'evidence'/('bitplanes-'+args.label)
    if output.exists(): parser.error('attempt output must be absent')
    helpers = {0,1,2,3,4,5,8,9,10,11,12,13}
    if not helpers <= os.sched_getaffinity(0): parser.error('all housekeeping CPUs must be available')
    os.sched_setaffinity(0,helpers)
    output.mkdir()
    env = dict(os.environ,RUSTFLAGS='-C target-cpu=x86-64',CARGO_ENCODED_RUSTFLAGS='-C\x1ftarget-cpu=x86-64',
               CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='4')
    dependencies = [Path(__file__),HERE/'prepared.json',HERE/'archive.json',HERE/archived['archive'],terminal,
                    ROOT/'tools/build.py',ROOT/'tools/archive_build.py',ROOT/'tools/compare_ordinary.py',
                    ROOT/'tools/account_native.py',ROOT/'tools/measure.py',PROFILE/'replay-check.mjs',
                    PROFILE/'workloads.json',PROFILE/'replay-oracle.json',baseline,BASE/'receipt.json',
                    BASE_CHECK/'profile-all.json',BASE_CHECK/'profile-identity.json']
    before = {str(p):sha(p) for p in dependencies}
    write(output/'plan.json',dict(status='planned validation and reported-only generic pilot',
        preparation_sha256=sha(HERE/'prepared.json'),dependency_sha256=before,
        cases=CASES,baseline=str(baseline),variants=prepared['variants'],checks_only=args.checks_only,
        expected_tests=dict(library=131,development_cli=2),expected_replays_per_variant=54,
        scope='Same Boolean attack kernel and consumer scope; local versus persistent supply. No production adoption, PGO inference or reference qualification.',
        cpu_order='Each case: excluded warmup per variant, then four alternating forward/reverse rounds with baseline/persistent/local',
        environment={k:env[k] for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']}))
    write(output/'context-before.json',context())
    receipt = dict(complete=False,failure=None,stages=[],variants={},cpu_pilot={})
    engines = {'baseline':baseline}
    try:
        for name,path in variants.items():
            directory = output/name; directory.mkdir()
            command = ['cargo','test','--offline','--locked','--release','--no-run','--message-format=json',
                       '--lib','--bin','rook2-dev','--manifest-path',str(path/'Cargo.toml')]
            stage = run(command,directory,'unit-build',env); receipt['stages'].append(stage)
            assert stage['exit_code'] == 0,f'{name} unit compilation failed'
            artifacts = {}
            for line in (directory/'unit-build.stdout').read_text().splitlines():
                item = json.loads(line)
                if item.get('reason') == 'compiler-artifact' and item['profile']['test'] and item.get('executable'):
                    artifacts[item['target']['name']] = Path(item['executable'])
            assert set(artifacts) == {'rook2','rook2-dev'},'unit executable inventory'
            units = {}
            for target,expected in [('rook2',131),('rook2-dev',2)]:
                frozen = directory/'unit-bin'/target/'rook2-exact'; frozen.parent.mkdir(parents=True)
                shutil.copy2(artifacts[target],frozen); identity = sha(frozen)
                stage = run([str(frozen),'--test-threads=1'],directory,target+'-tests',env)
                receipt['stages'].append(stage)
                assert stage['exit_code'] == 0,f'{name} {target} unit tests failed'
                count = re.search(r'test result: ok\. (\d+) passed; 0 failed;', (directory/(target+'-tests.stdout')).read_text())
                assert count and int(count[1]) == expected,'unit test count'
                assert sha(frozen) == identity,'unit image changed'
                units[target] = dict(binary_sha256=identity,passed=expected)
            build = directory/'build'
            command = [sys.executable,str(ROOT/'tools/build.py'),'--crate',str(path),'--bin','rook2',
                       '--mode','generic','--output',str(build)]
            stage = run(command,directory,'build',env); receipt['stages'].append(stage)
            assert stage['exit_code'] == 0,f'{name} native build failed'
            built = json.loads((build/'receipt.json').read_text())
            frozen = build/'rook2-exact'; shutil.copy2(built['binary_output']['path'],frozen)
            identity = sha(frozen); assert identity == built['binary_output']['sha256'],'frozen native image'
            stage = run([sys.executable,str(ROOT/'tools/archive_build.py'),str(build)],directory,'archive',env)
            receipt['stages'].append(stage); assert stage['exit_code'] == 0,'native archive failed'
            stage = run(['/usr/bin/node',str(PROFILE/'replay-check.mjs'),'--',str(frozen)],directory,'profile-all',env)
            receipt['stages'].append(stage); assert stage['exit_code'] == 0,f'{name} strict replay failed'
            report = json.loads((directory/'profile-all.stdout').read_text())
            assert report['status'] == 'pass' and len(report['results']) == 54,'strict replay count'
            assert not (directory/'profile-all.stderr').stat().st_size,'unexpected replay stderr'
            assert sha(frozen) == identity and source_snapshot(path) == prepared['variants'][name]['source_sha256'],'native artifact/source changed'
            receipt['variants'][name] = dict(units=units,artifact=str(frozen),artifact_sha256=identity,replays=54)
            engines[name] = frozen
            print(json.dumps(dict(variant=name,tests=133,replays=54,sha256=identity)),flush=True)
        if not args.checks_only:
            write(output/'cpu-context-before.json',context())
            for case in CASES:
                command = [sys.executable,str(ROOT/'tools/compare_ordinary.py'),'--case',case,'--output',str(output/case)]
                for name,path in engines.items(): command += ['--variant',name+'='+str(path)]
                stage = run(command,output,case,env); receipt['stages'].append(stage)
                assert stage['exit_code'] == 0,f'{case} CPU pilot failed'
                report = json.loads((output/case/'summary.json').read_text())
                assert report['complete'] and len(report['runs']) == 15,'CPU lifetime count'
                receipt['cpu_pilot'][case] = report['summaries']
                print(json.dumps(dict(case=case,summaries=report['summaries'])),flush=True)
            write(output/'cpu-context-after.json',context())
        receipt['complete'] = True
    except BaseException as error:
        receipt['failure'] = f'{type(error).__name__}: {error}'
    finally:
        after = {str(p):sha(p) for p in dependencies}
        stable = (before == after and source_snapshot(ROOT) == prepared['base_native_source_sha256']
                  and all(source_snapshot(path) == prepared['variants'][name]['source_sha256'] for name,path in variants.items()))
        receipt['inputs_stable'] = stable
        if not stable: receipt.update(complete=False,failure='source/dependency changed')
        write(output/'inputs-after.json',after)
        write(output/'context-after.json',context())
        write(output/'verification.json',receipt)
    print(json.dumps(dict(output=str(output),complete=receipt['complete'],failure=receipt['failure'])))
    return 0 if receipt['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
