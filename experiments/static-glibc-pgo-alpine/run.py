#!/usr/bin/env python3
"""Unattended own-PGO static-glibc build/training/Alpine measurement pipeline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
OLD = Path('/home/legolas/rook2-experiments/alpine-dynamic-musl-20261021-01')
PLAIN = Path('/home/legolas/rook2-experiments/debian-static-glibc-builder-20261023-01')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def write(p, x):
    temporary = p.with_name(p.name+'.pending')
    temporary.write_text(json.dumps(x, indent=2)+'\n')
    temporary.replace(p)


def descendants(root):
    parents = {}
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            parents[int(p.parent.name)] = int(p.read_text().rsplit(')', 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            pass
    found = {root}
    while True:
        new = {pid for pid, parent in parents.items() if parent in found}
        if new <= found:
            return found
        found |= new


def stop(process):
    # Inner collectors create their own process groups. Reconcile the live
    # descendant tree, rather than killing only the outer namespace's group.
    owned = descendants(process.pid)
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid in sorted(owned, reverse=True):
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        if sig == signal.SIGTERM:
            owned |= descendants(process.pid)
    return sorted(owned)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--notify-pane', required=True)
    a = p.parse_args()
    b = a.output.resolve()
    b.mkdir()
    status = dict(complete=False, failed=False, stages=[], supervisorPid=os.getpid())

    def notify(message):
        try:
            result = subprocess.run(['herdr', 'agent', 'prompt', a.notify_pane,
                'Sender centrally unnamed; unattended static-glibc PGO supervisor: '+message],
                capture_output=True, text=True, timeout=20)
            write(b/'notification.json', dict(exit=result.returncode, stdout=result.stdout,
                                             stderr=result.stderr))
        except Exception:
            write(b/'notification.json', dict(error=traceback.format_exc()))

    def stage(name, argv, seconds):
        row = dict(name=name, argv=argv, exit=None, deadlineSeconds=seconds)
        status['stages'].append(row)
        write(b/'status.json', status)
        start = time.monotonic()
        with (b/(name+'.stdout')).open('xb') as so, (b/(name+'.stderr')).open('xb') as se:
            process = subprocess.Popen(argv, stdout=so, stderr=se, start_new_session=True)
            row['pid'] = process.pid
            write(b/'status.json', status)
            try:
                while process.poll() is None:
                    if time.monotonic()-start > seconds:
                        raise TimeoutError(name+' deadline')
                    # Covers profiles and captured streams as well as outputs.
                    if sum(x.stat().st_size for x in b.rglob('*') if x.is_file()) > 4*1024**3:
                        raise RuntimeError('4GiB pipeline artifact budget')
                    time.sleep(1)
            except BaseException:
                row['cleanupPids'] = stop(process)
                raise
            finally:
                row.update(exit=process.poll(), elapsedSeconds=time.monotonic()-start)
                write(b/'status.json', status)
        assert row['exit'] == 0, f'{name} exit {row["exit"]}; see {b}/{name}.stderr'
        print(json.dumps(dict(stage=name, exit=row['exit'])), flush=True)

    try:
        original = read(PLAIN/'plain-output/glibc-static/build.json')
        (b/'source').mkdir()
        for name, expected in original['source_sha256'].items():
            assert sha(ROOT/name) == expected, name
            target = b/'source'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)
        (b/'builder').mkdir()
        for name in ['Dockerfile', 'build.py', 'musl-linker.sh', 'vendor.py', 'diagnostic-Cargo.lock']:
            shutil.copy2(ROOT/'build/linux-builder'/name, b/'builder'/name)
        vendor = Path('/home/legolas/rook2-experiments/debian-four-builder-20261022-01/vendor')
        shutil.copytree(vendor, b/'builder/vendor')
        shutil.copytree(ROOT/'tools', b/'tools', ignore=shutil.ignore_patterns('__pycache__'))
        path = b/'tools/account_native.py'
        text = path.read_text()
        old = 'helpers = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}'
        assert text.count(old) == 1
        path.write_text(text.replace(old, 'helpers = {14}'))
        write(b/'source-map.json', original['source_sha256'])
        (b/'profile-raw').mkdir()
        (b/'profiles').mkdir()
        base = read(PLAIN/'plain-validation.json')['argv']
        def build_command(mode):
            out = b/(mode+'-output')
            out.mkdir()
            argv = [str(b/'builder') if x == str(PLAIN/'builder') else
                    str(out) if x == str(PLAIN/'plain-output') else
                    str(b/'source') if x == str(ROOT) else x for x in base]
            i = argv.index('--clearenv')
            argv[i:i] = ['--bind' if mode == 'generate' else '--ro-bind',
                         str(b/'profile-raw' if mode == 'generate' else b/'profiles'),
                         '/profiles-out' if mode == 'generate' else '/profiles']
            return argv+['--mode', mode]
        stage('generate', build_command('generate'), 900)
        # The training profile belongs to this exact instrumented source/runtime.
        worker = (OLD/'train.py').read_text()
        worker = worker.replace("B/'profile-raw'", "B/'profile-raw/glibc-static'")
        worker = worker.replace('/work/profile-raw/native-', '/work/profile-raw/glibc-static/native-')
        worker = worker.replace("B/'artifacts/rook2-instrumented'", "B/'generate-output/glibc-static/rook'")
        worker = worker.replace('x86_64-unknown-linux-musl', 'x86_64-unknown-linux-gnu')
        (b/'train.py').write_text(worker)
        launch = (OLD/'training-launch.py').read_text().replace(
            '/work/artifacts/rook2-instrumented', '/work/generate-output/glibc-static/rook')
        (b/'training-launch.py').write_text(launch)
        alpine = OLD/'rootfs'
        container = ['taskset', '-c', '14', 'bwrap', '--ro-bind', str(alpine), '/',
            '--unshare-user', '--uid', '0', '--gid', '0', '--unshare-net',
            '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
            '--ro-bind', str(ROOT), str(ROOT), '--ro-bind',
            '/home/legolas/king-spec', '/home/legolas/king-spec',
            '--bind', str(b), '/work', '--ro-bind', str(b/'tools'), str(ROOT/'tools'),
            '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin', '--setenv', 'LANG', 'C',
            '--setenv', 'LC_ALL', 'C', '--setenv', 'TZ', 'UTC',
            '--setenv', 'PYTHONDONTWRITEBYTECODE', '1', '--']
        stage('training', container+['/usr/bin/python3', '/work/train.py'], 1800)
        trained = read(b/'training/result.json')
        assert trained['complete'] and trained['strictCases'] == 54
        raw = sorted((b/'profile-raw/glibc-static').glob('*.profraw'))
        assert len(raw) == 54
        for path in raw:
            assert sha(path) == trained['rawProfileSha256']['/work/profile-raw/glibc-static/'+path.name]
        profile = b/'profiles/glibc-static.profdata'
        stage('merge', ['/usr/bin/llvm-profdata-19', 'merge', '-o', str(profile), *map(str, raw)], 60)
        template = read(b/'generate-output/glibc-static/profile-template.json')
        template['profile_sha256'] = sha(profile)
        write(b/'profiles/glibc-static.json', template)
        stage('use', build_command('use'), 900)
        use = read(b/'use-output/glibc-static/build.json')
        assert use['mode'] == 'use' and use['artifacts']['rook']['needed'] == []
        assert use['artifacts']['rook-diag']['mode'] == 'plain'
        assert use['artifacts']['rook-diag']['sha256'] == original['artifacts']['rook-diag']['sha256']
        use_stage = next(x for x in status['stages'] if x['name'] == 'use')
        write(b/'use-validation.json', use_stage)
        # Reuse the previous identical-work measurement setup, changing only its
        # admitted build mode/output paths and labels. Canonical scripts stay frozen.
        previous = ROOT/'experiments/static-glibc-alpine-performance'
        text = (previous/'run.py').read_text()
        text = text.replace('ROOT = Path(__file__).resolve().parents[2]', 'ROOT = Path('+repr(str(ROOT))+')')
        text = text.replace('plain-output', 'use-output').replace('plain-validation.json', 'use-validation.json')
        text = text.replace("info['mode'] == 'plain'", "info['mode'] == 'use'")
        text = text.replace("mode='plain'", "mode='use'").replace('plain non-PGO', 'own-PGO')
        (b/'benchmark-run.py').write_text(text)
        text = (previous/'reconcile.py').read_text().replace('plain-output', 'use-output').replace('plain non-PGO', 'own-PGO')
        (b/'reconcile.py').write_text(text)
        write(b/'bindings.json', dict(driverSha256=sha(Path(__file__)),
            instrumentedSha256=sha(b/'generate-output/glibc-static/rook'),
            optimizedSha256=sha(b/'use-output/glibc-static/rook'),
            profileSha256=sha(profile), profileTemplate=template,
            generatedScripts={n:sha(b/n) for n in ['train.py', 'training-launch.py', 'benchmark-run.py', 'reconcile.py']},
            baseMeasurementScripts={n:sha(previous/n) for n in ['run.py', 'reconcile.py']},
            compilerReceiptSha256=sha(b/'use-output/glibc-static/build.json'),
            entireAlpineContainerCpu=14, cpu15WorkAssigned=False))
        stage('measure', [sys.executable, str(b/'benchmark-run.py'), '--output', str(b/'measurement'),
                         '--build', str(b), '--alpine-root', str(alpine)], 10800)
        stage('reconcile', [sys.executable, str(b/'reconcile.py'), str(b/'measurement')], 60)
        assert sha(profile) == template['profile_sha256']
        assert all(sha(ROOT/n) == h and sha(b/'source'/n) == h for n, h in original['source_sha256'].items())
        status['complete'] = True
        write(b/'status.json', status)
        report = read(b/'measurement/reconciled.json')
        notify('COMPLETE; no jobs left. Results '+str(b)+'/measurement/reconciled.json; '
               '54-case CPU '+str(report['standard54']['sumCaseMedianCpuSeconds'])+'s; '
               '12-game CPU '+str(report['games12']['sumNativeCpuSeconds'])+'s. '
               'Reconcile/commit concise records and report to Toby; no extra native runs.')
    except BaseException:
        status.update(failed=True, error=traceback.format_exc())
        write(b/'status.json', status)
        notify('FAILED and stopped; inspect '+str(b)+'/status.json. No automatic retry.')
        raise


if __name__ == '__main__':
    main()
