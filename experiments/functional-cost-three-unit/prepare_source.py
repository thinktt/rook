#!/usr/bin/env python3
"""Reconstruct only this study's derivative from a byte-pinned retained62 tree."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline', type=Path, required=True)
    ap.add_argument('--destination', type=Path, required=True)
    a = ap.parse_args()
    baseline = a.baseline.resolve(strict=True)
    destination = a.destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination must be absent')
    pins = json.loads((here / 'derivative-source.json').read_text())
    original = pins['baseline_files_sha256']
    for name, expected in original.items():
        if digest(baseline / name) != expected:
            raise ValueError('baseline mismatch: ' + name)
    patch = here / 'study.patch'
    if digest(patch) != pins['patch_sha256']:
        raise ValueError('patch mismatch')
    destination.mkdir()
    for name in original:
        p = destination / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((baseline / name).read_bytes())
    subprocess.run(['/usr/bin/patch', '--batch', '--forward', '-p1', '-i', str(patch)],
                   cwd=destination, check=True)
    final = original | pins['derivative_changed_files_sha256']
    for name, expected in final.items():
        if digest(destination / name) != expected:
            raise ValueError('derivative mismatch: ' + name)
    print(json.dumps({'verified_files': len(final), 'destination': str(destination)}))


if __name__ == '__main__':
    main()
