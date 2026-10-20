#!/usr/bin/env python3
"""Restore a preserved source snapshot; never build or run it."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--prefix')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    records = json.loads((ROOT / 'experiments/source-snapshots.json').read_text())
    if args.list:
        prefixes = set()
        for key in records:
            for marker in ('/source-before/', '/source-after/', '/frozen-source/'):
                if marker in key:
                    prefixes.add(key.split(marker, 1)[0] + marker)
        print('\n'.join(sorted(prefixes)))
        return
    if not args.prefix or not args.prefix.endswith('/') or not args.output:
        parser.error('--prefix must end in / and requires --output')
    chosen = [(key[len(args.prefix):], rec) for key, rec in records.items()
              if key.startswith(args.prefix)]
    if not chosen:
        parser.error('no snapshot files match that prefix')
    if args.output.exists():
        parser.error('output must not exist')
    validated = []
    for relative, rec in chosen:
        path = PurePosixPath(relative)
        obj = PurePosixPath(rec['object'])
        if path.is_absolute() or '..' in path.parts or obj.is_absolute() or '..' in obj.parts:
            raise ValueError('unsafe snapshot path')
        data = (ROOT / obj).read_bytes()
        if len(data) != rec['bytes'] or hashlib.sha256(data).hexdigest() != rec['sha256']:
            raise ValueError('source object identity mismatch: ' + relative)
        validated.append((path, rec, data))
    args.output.mkdir(parents=True)
    for relative, rec, data in validated:
        target = args.output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(int(rec['mode'], 8))
    print(f'Restored {len(validated)} source files to {args.output}')

if __name__ == '__main__':
    main()
