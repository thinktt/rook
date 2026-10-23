#!/usr/bin/env python3
"""Measure an existing plain static-glibc build in Alpine, all descendants on CPU14."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--alpine-root', type=Path, required=True)
    a = p.parse_args()
    b, build, alpine = a.output.resolve(), a.build.resolve(), a.alpine_root.resolve()
    receipt = build/'plain-output/glibc-static/build.json'
    image = build/'plain-output/glibc-static/rook'
    info = json.loads(receipt.read_text())
    assert info['mode'] == 'plain' and info['artifacts']['rook']['sha256'] == sha(image)
    assert info['artifacts']['rook']['needed'] == []
    assert all(sha(ROOT/n) == h for n, h in info['source_sha256'].items())
    assert json.loads((build/'plain-validation.json').read_text())['exit'] == 0
    b.mkdir()
    (b/'build').mkdir()
    # Keep canonical helpers untouched. Overlay only the CPU-policy constants;
    # comparator, accounting boundaries and engine execution remain unchanged.
    shutil.copytree(ROOT/'tools', b/'tools', ignore=shutil.ignore_patterns('__pycache__'))
    changes = {}
    for name, old, new in [
        ('collect_ordinary.py', 'HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}', 'HELPERS = {14}'),
        ('collect_games.py', 'HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}', 'HELPERS = {14}'),
        ('account_native.py', 'helpers = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}', 'helpers = {14}'),
    ]:
        path = b/'tools'/name
        text = path.read_text()
        assert text.count(old) == 1
        path.write_text(text.replace(old, new))
        changes[name] = dict(original=sha(ROOT/'tools'/name), overlay=sha(path), old=old, new=new)
    # Explicit adapter from the real builder receipt to the old collector API.
    # This is not a new compiler invocation or an assertion of PGO qualification.
    write(b/'collector-build.json', dict(
        schema='rook-builder-collector-adapter-v1',
        outcome='build-succeeded-with-stable-input-snapshot',
        binary_output=dict(sha256=sha(image)), mode='plain',
        actualBuilderReceipt='/work/build/plain-output/glibc-static/build.json',
        actualBuilderReceiptSha256=sha(receipt),
        sourceMapCheckedAtPreparation=True))
    old = Path('/home/legolas/rook2-experiments/alpine-dynamic-musl-20261021-01/run_games_once.py')
    text = old.read_text()
    text = text.replace("engine=B/'artifacts/rook2-musl';build=B/'build-use/receipt.json'",
                        "engine=B/'build/plain-output/glibc-static/rook';build=B/'collector-build.json'")
    text = text.replace(" and r['dynamicMuslVerified']", '')
    text = text.replace('dynamic musl own-PGO variant', 'static glibc plain non-PGO variant; entire container CPU14')
    (b/'run_games_once.py').write_text(text)
    prefix = ['taskset', '-c', '14', 'bwrap', '--ro-bind', str(alpine), '/',
              '--unshare-user', '--uid', '0', '--gid', '0', '--unshare-net',
              '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
              '--ro-bind', str(ROOT), str(ROOT),
              '--ro-bind', '/home/legolas/king-spec', '/home/legolas/king-spec',
              '--bind', str(b), '/work', '--ro-bind', str(build), '/work/build',
              '--ro-bind', str(b/'tools'), str(ROOT/'tools'), '--chdir', '/work',
              '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin',
              '--setenv', 'LANG', 'C', '--setenv', 'LC_ALL', 'C',
              '--setenv', 'TZ', 'UTC', '--setenv', 'PYTHONDONTWRITEBYTECODE', '1', '--']
    inputs = {str(x): sha(x) for x in [image, receipt, Path(__file__), old,
              b/'run_games_once.py', b/'collector-build.json']}
    inputs.update({str(x): sha(x) for x in (b/'tools').iterdir() if x.is_file()})
    write(b/'plan.json', dict(engineSha256=sha(image), builderReceiptSha256=sha(receipt),
        inputSha256=inputs, helperChanges=changes, containerCpu=14, cpu15WorkAssigned=False,
        alpineRelease=(alpine/'etc/alpine-release').read_text().strip(),
        standard54='one excluded warmup plus three measured fresh processes per case',
        games12='one complete pass; not medians or final qualification',
        accounting='native wait4 whole lifetime; collectors also share CPU14',
        buildMode='plain non-PGO', prefix=prefix))
    stages = [
        ('standard54', ['/usr/bin/python3', str(ROOT/'tools/collect_ordinary.py'),
                        '--engine', '/work/build/plain-output/glibc-static/rook',
                        '--build-record', '/work/collector-build.json', '--output', '/work/standard54']),
        ('games12', ['/usr/bin/python3', '/work/run_games_once.py']),
    ]
    status = dict(complete=False, stages=[])
    for name, command in stages:
        row = dict(name=name, argv=prefix+command, exit=None)
        status['stages'].append(row)
        write(b/'status.json', status)
        t = time.monotonic()
        with (b/(name+'.stdout')).open('xb') as so, (b/(name+'.stderr')).open('xb') as se:
            result = subprocess.run(row['argv'], stdout=so, stderr=se, timeout=15000)
        row.update(exit=result.returncode, elapsedSeconds=time.monotonic()-t)
        write(b/'status.json', status)
        print(json.dumps(row), flush=True)
        assert result.returncode == 0, name
    assert all(sha(Path(x)) == h for x, h in inputs.items())
    status['complete'] = True
    write(b/'status.json', status)


if __name__ == '__main__':
    main()
