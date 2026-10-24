#!/usr/bin/env python3
"""Run released local checks against exact artifacts; never publish or rebuild."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=Path('/source'))
    p.add_argument('--spec', type=Path, default=Path('/spec'))
    p.add_argument('--helpers', type=Path, default=Path('/helpers'))
    p.add_argument('--engine', required=True, type=Path)
    p.add_argument('--diagnostic', type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--train', action='store_true')
    p.add_argument('--profiles', type=Path)
    a = p.parse_args()
    assert os.sched_getaffinity(0) == {14}, 'the complete check container must use CPU14'
    a.output.mkdir()
    launcher = ['/usr/bin/python3', str(a.source/'release/native.py')]
    account = a.helpers/'account_native.py'
    env = dict(os.environ, ROOK_RELEASE_ENGINE=str(a.engine), ROOK_RELEASE_ACCOUNT=str(account))
    initial = dict(engine=sha(a.engine), diagnostic=sha(a.diagnostic) if a.diagnostic else None)
    summary = dict(complete=False, training=a.train, artifactSha256=initial, stages=[],
                   containerCpus=[14], fullGameGate=False, finalPerformanceQualification=False)
    spec_files = [p for p in (a.spec/'conformance').rglob('*') if p.is_file() and p.suffix in ('.json', '.mjs')]
    pins = {str(p):sha(p) for p in spec_files}
    pins.update({str(p):sha(p) for p in [account, a.source/'release/native.py', a.source/'release/capture.mjs']})
    write(a.output/'inputs.json', pins)

    def run(name, args, image, calls=None, signals=False, timeout=1800):
        out = a.output/name
        out.mkdir()
        native = out/'native'
        native.mkdir()
        child_env = dict(env, ROOK_RELEASE_ENGINE=str(image), ROOK_RELEASE_NATIVE_DIR=str(native))
        command = ['/usr/bin/node']
        if calls is not None:
            raw = out/'raw'
            raw.mkdir()
            config = out/'capture.json'
            write(config, dict(image=str(image), rawRoot=str(raw), expectedCalls=calls, maxBytes=32*1024**2))
            child_env['ROOK_RELEASE_TAP_CONFIG'] = str(config)
            command += ['--import', str(a.source/'release/capture.mjs')]
        command += args
        with (out/'stdout').open('xb') as so, (out/'stderr').open('xb') as se:
            result = subprocess.run(command, env=child_env, stdout=so, stderr=se, timeout=timeout)
        assert result.returncode == 0, name+' comparator failed'
        assert (out/'stderr').stat().st_size == 0, name+' unexpected stderr'
        receipts = []
        for file in sorted(native.glob('*.json')):
            n = json.loads(file.read_text())
            assert n['failure'] is None and n['exec_error'] is None
            assert n['engine_sha256_before'] == n['engine_sha256_after'] == sha(image)
            assert n['supervisor_affinity'] == [14] and n['native_pre_exec']['affinity'] == [14]
            assert n['native_exit_code'] in ([0, 1] if name == 'seed-command' else [0])
            assert n['supervisor_signals'] == [] or signals
            assert not Path('/proc/'+str(n['native_pid'])).exists()
            receipts.append(n)
        if calls is not None:
            count = json.loads((out/'raw/launch-count.json').read_text())
            assert count['observed'] == count['expected'] == len(calls) == len(receipts)
            for f in (out/'raw').glob('*/receipt.json'):
                r = json.loads(f.read_text())
                assert r['error'] is None and r['signal'] is None
                assert r['imageBefore'] == r['imageAfter'] == sha(image)
                for item in r['raw'].values():
                    path = Path(item['path'])
                    assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
        row = dict(name=name, nativeRequests=len(receipts), exit=0,
                   cpuSeconds=sum(n['total_cpu_s'] for n in receipts),
                   unavailablePostExecObservations=sum('native_post_exec' not in n or n['native_post_exec'] is None for n in receipts))
        summary['stages'].append(row)
        write(a.output/'summary.json', summary)
        return out, receipts

    if a.train:
        assert a.profiles is not None
        os.environ['LLVM_PROFILE_FILE'] = str(a.profiles/'native-%m-%p.profraw')
        env['LLVM_PROFILE_FILE'] = os.environ['LLVM_PROFILE_FILE']
        out, natives = run('training', [str(a.spec/'conformance/profiling/replay-check.mjs'), '--', *launcher], a.engine)
        report = json.loads((out/'stdout').read_text())
        expected = json.loads((a.spec/'conformance/profiling/workloads.json').read_text())['cases']
        assert report['status'] == 'pass' and report['selectedCases'] == [x['id'] for x in expected]
        assert len(natives) == len(expected)
        profiles = sorted(a.profiles.glob('*.profraw'))
        assert len(profiles) == len(expected)
        assert {int(p.stem.rsplit('-', 1)[1]) for p in profiles} == {n['native_pid'] for n in natives}
        summary['profiles'] = {str(p):sha(p) for p in profiles}
    else:
        assert a.diagnostic
        files = []
        for file in sorted((a.spec/'conformance/fixtures').glob('*.json')):
            cases = json.loads(file.read_text())['cases']
            optional = {'output.analysisCandidateReport', 'search.analysisRootSequence'}
            if any(c['request']['operation'] in optional for c in cases):
                assert all(c['request']['operation'] in optional for c in cases)
            else:
                files.append(file)
        args = [str(a.spec/'conformance/run.mjs'), '--timeout', '60000']
        for file in files:
            args += ['--fixtures', str(file)]
        out, natives = run('mandatory', args+['--', *launcher], a.diagnostic, timeout=2400)
        report = json.loads((out/'stdout').read_text())
        cases = sum(len(json.loads(p.read_text())['cases']) for p in files)
        assert report['pass'] and len(report['results']) == len(natives) == cases
        summary['mandatory'] = dict(files=len(files), cases=cases)
        out, natives = run('standard54', [str(a.spec/'conformance/profiling/replay-check.mjs'), '--', *launcher], a.engine)
        report = json.loads((out/'stdout').read_text())
        assert report['status'] == 'pass' and len(report['results']) == len(natives) == 54
        gate = a.spec/'conformance/gate-replay'
        games = json.loads((gate/'accepted-games-v1.json').read_text())['games']
        seed = launcher+['--diagnostic-seed-command']
        run('games', [str(gate/'run.mjs'), '--report', str(a.output/'games/report.json'), '--', *launcher],
            a.engine, calls=[seed]*len(games), timeout=2400)
        report = json.loads((a.output/'games/report.json').read_text())
        assert report['pass'] and len(report['games']) == len(games)
        summary['games'] = dict(games=len(games), searches=sum(g['searches'] for g in report['games']))
        run('continuous', [str(gate/'continuous.mjs'), '--report', str(a.output/'continuous/report.json'), '--', *launcher],
            a.engine, calls=[seed], timeout=600)
        run('seed-command', [str(gate/'seed-command-controls.mjs'), '--', *launcher], a.engine,
            calls=[seed]*10+[launcher], timeout=120)
        run('seed-persistence', [str(gate/'seed-persistence-controls.mjs'), '--', *launcher],
            a.engine, calls=[seed], timeout=180)
        # The unchanged wire checker takes one executable rather than an argv list.
        out = a.output/'wire'
        out.mkdir()
        (out/'native').mkdir()
        with (out/'stdout').open('xb') as so, (out/'stderr').open('xb') as se:
            result = subprocess.run(['/usr/bin/python3', str(a.helpers/'check_live.py'), '--engine',
                str(a.source/'release/native.py'), '--output', str(out/'output')],
                env=dict(env, ROOK_RELEASE_NATIVE_DIR=str(out/'native')), stdout=so, stderr=se, timeout=180)
        assert result.returncode == 0
        wire = json.loads((out/'output/receipt.json').read_text())
        assert wire['pass'] and len(wire['results']) == 8 and sum(len(r['searches']) for r in wire['results']) == 24
        write(out/'summary.json', dict(pass_=True, sessions=8, searches=24))
        command = ['/usr/bin/node', str(gate/'combine.mjs'), '--report', str(a.output/'combined.json'),
            '--continuous', str(a.output/'continuous/report.json'), str(a.output/'games/report.json')]
        with (a.output/'combine.stdout').open('xb') as so, (a.output/'combine.stderr').open('xb') as se:
            subprocess.run(command, stdout=so, stderr=se, check=True, timeout=30)
        assert json.loads((a.output/'combined.json').read_text())['completeFocusedReplay']
        summary['wire'] = dict(sessions=8, searches=24)
        summary['focusedReplayComplete'] = True
    assert sha(a.engine) == initial['engine']
    if a.diagnostic:
        assert sha(a.diagnostic) == initial['diagnostic']
    assert all(sha(Path(p)) == h for p, h in pins.items())
    summary['complete'] = True
    write(a.output/'summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
