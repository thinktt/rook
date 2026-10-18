#!/usr/bin/env python3
"""Package a development build's verified pre-build bytes; never execute it."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    args = parser.parse_args()
    record = json.loads((args.build / 'receipt.json').read_text())
    if record['outcome'] != 'build-succeeded-with-stable-input-snapshot':
        parser.error('only a stable successful build may be packaged')
    expected = record['source_sha256_before'] | record['tool_sha256_before']
    archive = args.build / 'verified-source-before.tar.gz'
    receipt = args.build / 'archive-receipt.json'
    if archive.exists() or receipt.exists():
        parser.error('archive and receipt must be absent')
    with archive.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as output:
                for name, sha256 in sorted(expected.items()):
                    path = Path(name)
                    if path.is_absolute() or '..' in path.parts:
                        raise ValueError('pre-build snapshot must contain relative contained paths')
                    data = (args.build / 'source-before' / path).read_bytes()
                    if digest(data) != sha256:
                        raise ValueError(f'pre-build archive bytes changed: {name}')
                    member = tarfile.TarInfo(name)
                    member.size, member.mode = len(data), 0o644
                    output.addfile(member, io.BytesIO(data))
    with tarfile.open(archive, 'r:gz') as check:
        actual = {member.name: digest(check.extractfile(member).read()) for member in check}
    if actual != expected:
        raise ValueError('archive verification failed')
    frozen = args.build / 'rook2-exact'
    if not frozen.exists():
        frozen = args.build / 'rook2-diag-exact'
    binary_hash = digest(frozen.read_bytes())
    if binary_hash != record['binary_output']['sha256']:
        raise ValueError('frozen binary differs from the build identity')
    result = dict(archive=archive.name, sha256=digest(archive.read_bytes()),
                  files=len(expected), verified_against_build_before_hashes=True,
                  binary_sha256=binary_hash, helper_sha256=digest(Path(__file__).read_bytes()))
    with receipt.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(build=str(args.build), **result)))


if __name__ == '__main__':
    main()
