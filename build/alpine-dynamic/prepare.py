#!/usr/bin/env python3
"""Prepare a hash-locked candidate68 dynamic-musl Docker context; no build/run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--profile', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path, help='fresh absent context directory')
    parser.add_argument('--apk-cache', type=Path, help='optional directory containing the exact APKs; otherwise download pinned files')
    args = parser.parse_args()
    lock = json.loads((HERE / 'inputs.lock.json').read_text())
    if args.output.exists():
        parser.error('output must be absent')
    if digest(args.profile) != lock['profileSha256']:
        parser.error('profile does not match the locked musl training artifact')
    for name, expected in lock['sourceSha256'].items():
        if digest(args.source / name) != expected:
            parser.error('source mismatch: ' + name)
    args.output.mkdir()
    source = args.output / 'source'
    for name in lock['sourceSha256']:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((args.source / name).read_bytes())
    (args.output / 'merged.profdata').write_bytes(args.profile.read_bytes())
    if digest(args.output / 'merged.profdata') != lock['profileSha256']:
        raise ValueError('profile changed during capture')
    for name, expected in lock['sourceSha256'].items():
        if digest(source / name) != expected:
            raise ValueError('source changed during capture: ' + name)
    for name in ('Dockerfile', 'build.sh'):
        (args.output / name).write_bytes((HERE / name).read_bytes())
    apk_dir = args.output / 'apks'
    apk_dir.mkdir()
    for name, entry in lock['apks'].items():
        target = apk_dir / name
        if args.apk_cache:
            target.write_bytes((args.apk_cache / name).read_bytes())
        else:
            with urllib.request.urlopen(entry['url'], timeout=60) as response:
                target.write_bytes(response.read())
        if digest(target) != entry['sha256']:
            raise ValueError('APK checksum mismatch: ' + name)
    (apk_dir / 'SHA256SUMS').write_text(''.join(entry['sha256'] + '  ' + name + '\n' for name, entry in sorted(lock['apks'].items())))
    checks = ['build.sh', 'merged.profdata'] + ['source/' + name for name in sorted(lock['sourceSha256'])]
    (args.output / 'input.SHA256SUMS').write_text(''.join(digest(args.output / name) + '  ' + name + '\n' for name in checks))
    for path in args.output.rglob('*'):
        if path.is_file():
            path.chmod(0o644)
            os.utime(path, (lock['sourceDateEpoch'], lock['sourceDateEpoch']))
    print(json.dumps({'context': str(args.output.absolute()), 'sourceFiles': len(lock['sourceSha256']), 'profileSha256': lock['profileSha256'], 'expectedBinarySha256': lock['binarySha256']}))

if __name__ == '__main__':
    main()
