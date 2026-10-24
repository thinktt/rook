#!/usr/bin/env python3
"""Unattended local static-profile preparation and finite release qualification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def write(p, value):
    temporary = p.with_name(p.name+'.pending')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(p)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--docker', default='docker')
    p.add_argument('--builder-image', required=True)
    p.add_argument('--alpine-image', required=True)
    p.add_argument('--spec', required=True, type=Path)
    p.add_argument('--notify-pane')
    p.add_argument('--notify-prefix', default='Local release supervisor')
    a = p.parse_args()
    b = a.output.resolve()
    b.mkdir()
    state = dict(complete=False, failed=False, supervisorPid=os.getpid(), stages=[])

    def notify(message):
        if a.notify_pane:
            try:
                r = subprocess.run(['herdr', 'agent', 'prompt', a.notify_pane,
                    a.notify_prefix+': '+message+'; receipts '+str(b)], capture_output=True, text=True, timeout=20)
                write(b/'notification.json', dict(exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
            except Exception:
                write(b/'notification.json', dict(error=traceback.format_exc()))

    def stage(name, command, limit, cid=None):
        row = dict(name=name, argv=command, secondsLimit=limit, exit=None)
        state['stages'].append(row)
        write(b/'status.json', state)
        start = time.monotonic()
        with (b/(name+'.stdout')).open('xb') as so, (b/(name+'.stderr')).open('xb') as se:
            child = subprocess.Popen(command, stdout=so, stderr=se, start_new_session=True)
            row['pid'] = child.pid
            try:
                while child.poll() is None:
                    if time.monotonic()-start > limit:
                        raise TimeoutError(name+' deadline')
                    if sum(f.stat().st_size for f in b.rglob('*') if f.is_file()) > 4*1024**3:
                        raise RuntimeError('local study exceeds 4GiB retained-data limit')
                    time.sleep(1)
            except BaseException:
                if cid and cid.exists():
                    removed = subprocess.run([a.docker, 'rm', '-f', cid.read_text().strip()], capture_output=True, text=True, timeout=30)
                    row['containerCleanup'] = dict(exit=removed.returncode, stdout=removed.stdout, stderr=removed.stderr)
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
                raise
            finally:
                row.update(exit=child.poll(), elapsedSeconds=time.monotonic()-start)
                write(b/'status.json', state)
        assert row['exit'] == 0, name+' failed; see its stderr'
        print(json.dumps(dict(stage=name, exit=row['exit'])), flush=True)
        return row

    def build(name, mode, variant='all'):
        cid = b/(name+'.cid')
        command = [sys.executable, str(ROOT/'release/build.py'), '--docker', a.docker,
            '--skip-image-build', '--image', a.builder_image, '--mode', mode, '--variant', variant,
            '--output', str(b/name), '--cidfile', str(cid)]
        if mode == 'generate':
            command += ['--profiles-out', str(b/'profiles-raw')]
        return stage(name, command, 900, cid)

    def alpine(name, options, seconds):
        cid = b/(name+'.cid')
        command = [a.docker, 'run', '--rm', '--network', 'none', '--read-only',
            '--cpuset-cpus', '14', '--user', f'{os.getuid()}:{os.getgid()}',
            '--tmpfs', '/tmp:exec,mode=1777', '--cidfile', str(cid),
            '--mount', f'type=bind,src={ROOT},dst=/source,readonly',
            '--mount', f'type=bind,src={a.spec.resolve()},dst=/spec,readonly',
            '--mount', f'type=bind,src={b},dst=/work',
            '--mount', f'type=bind,src={b}/helpers,dst=/helpers,readonly',
            '--entrypoint', '/usr/bin/python3', a.alpine_image,
            '/source/release/qualify.py', *options]
        return stage(name, command, seconds, cid)

    try:
        helpers = b/'helpers'
        helpers.mkdir()
        shutil.copyfile(ROOT/'release/record_native.py', helpers/'account_native.py')
        text = (ROOT/'tools/check_live.py').read_text()
        old = 'HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}'
        assert text.count(old) == 1
        (helpers/'check_live.py').write_text(text.replace(old, 'HELPERS = {14}').replace('/home/legolas/king-spec', '/spec'))
        images = {}
        for name in [a.builder_image, a.alpine_image]:
            images[name] = json.loads(subprocess.check_output([a.docker, 'image', 'inspect', name], text=True))[0]
        write(b/'images.json', images)
        recipe = read(ROOT/'build/release.json')
        source_graph = recipe['sourceGraphSha256']
        write(b/'plan.json', dict(builderImage=a.builder_image, alpineImage=a.alpine_image,
            sourceGraphSha256=source_graph, driverSha256=sha(Path(__file__)),
            nativeRecorderSha256=sha(ROOT/'release/record_native.py'),
            inputs={str(p):sha(p) for p in [ROOT/'release/qualify.py', ROOT/'release/native.py',
                ROOT/'release/capture.mjs', ROOT/'release/build.py', helpers/'check_live.py']},
            qualification='mandatory fixtures + standard54 + 12-game/continuity/seed/wire pre-gate; no full3288 gate',
            containerCpus=[14], cpu15WorkAssigned=False, retries=0))
        build('generate', 'generate', 'glibc-static')
        alpine('training', ['--train', '--engine', '/work/generate/glibc-static/rook',
            '--output', '/work/training-results', '--profiles', '/work/profiles-raw/glibc-static'], 1800)
        trained = read(b/'training-results/summary.json')
        assert trained['complete'] and len(trained['profiles']) == 54
        raw = sorted((b/'profiles-raw/glibc-static').glob('*.profraw'))
        for f in raw:
            assert sha(f) == trained['profiles']['/work/profiles-raw/glibc-static/'+f.name]
        merged = b/'glibc-static.profdata'
        stage('merge', ['llvm-profdata-19', 'merge', '-o', str(merged), *map(str, raw)], 60)
        text = ROOT/'build/profiles/glibc-static.proftext'
        stage('profile-text', ['llvm-profdata-19', 'merge', '--text', str(merged), '-o', str(text)], 60)
        recipe['variants']['glibc-static']['profileTextSha256'] = sha(text)
        write(ROOT/'build/release.json', recipe)
        build('first', 'release')
        build('repeat', 'release')
        artifacts = {}
        expected = {item['path']:item['sha256'] for item in read(ROOT/'release/qualification.json')['artifacts'] if item['path'].startswith('glibc/')}
        for variant in recipe['variants']:
            record = read(b/'first'/variant/'build.json')
            assert record['sourceGraphSha256'] == source_graph
            for program, data in record['artifacts'].items():
                first, second = b/'first'/variant/program, b/'repeat'/variant/program
                assert sha(first) == sha(second) == data['sha256']
                relative = variant+'/'+program
                if relative in expected:
                    assert data['sha256'] == expected[relative], 'original qualified bytes changed'
                artifacts[relative] = dict(sha256=data['sha256'], bytes=data['bytes'])
        write(b/'reproduced.json', artifacts)
        alpine('qualification', ['--engine', '/work/first/glibc-static/rook',
            '--diagnostic', '/work/first/glibc-static/rook-diag', '--output', '/work/qualification-results'], 5400)
        report = read(b/'qualification-results/summary.json')
        assert report['complete'] and report['focusedReplayComplete']
        assert report['mandatory'] == dict(files=115, cases=7673)
        assert report['games'] == dict(games=12, searches=632)
        assert read(ROOT/'build/release.json')['sourceGraphSha256'] == source_graph
        for file, h in read(b/'plan.json')['inputs'].items():
            assert sha(Path(file)) == h
        write(b/'complete.json', dict(artifacts=artifacts, qualification=report,
            qualifiedReportSha256=sha(b/'qualification-results/summary.json'),
            rawProfileSha256=sha(merged), profileTextSha256=sha(text),
            reproducibleFourArtifacts=True, sourceGraphSha256=source_graph))
        state['complete'] = True
        write(b/'status.json', state)
        notify('Static release preparation COMPLETE; all four reproduce and the new static pair passes the local pre-gate. Review/commit the qualification manifest and finish local workflow checks; no extra engine runs')
    except BaseException:
        state.update(failed=True, error=traceback.format_exc())
        write(b/'status.json', state)
        notify('Static release preparation FAILED and stopped; inspect status.json; no automatic retry')
        raise


if __name__ == '__main__':
    main()
