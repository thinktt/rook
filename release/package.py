#!/usr/bin/env python3
"""Verify locally qualified bytes, then prepare assets for a version tag."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare(build, manifest_path, version, output):
    if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?', version):
        raise ValueError('release tag must be vMAJOR.MINOR.PATCH with optional prerelease')
    manifest = json.loads(manifest_path.read_text())
    if manifest['schema'] != 'rook-artifact-qualification-v1' or manifest['status'] != 'qualified-locally':
        raise ValueError('manifest is not locally qualified')
    recipe = json.loads((ROOT/'build/release.json').read_text())
    expected = {v+'/'+p for v in recipe['variants'] for p in ['rook', 'rook-diag']}
    declared = [item['path'] for item in manifest['artifacts']]
    if set(declared) != expected or len(declared) != len(expected):
        raise ValueError('qualification manifest does not cover the complete build')
    checked, receipts = [], {}
    for item in manifest['artifacts']:
        relative = Path(item['path'])
        if relative.is_absolute() or '..' in relative.parts or len(relative.parts) != 2:
            raise ValueError('invalid artifact path')
        path = build/relative
        variant, program = relative.parts
        if variant not in receipts:
            receipts[variant] = json.loads((build/variant/'build.json').read_text())
        record = receipts[variant]
        if record['mode'] != 'release' or record['sourceGraphSha256'] != manifest['sourceGraphSha256']:
            raise ValueError('build provenance does not match qualification')
        if sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('qualified artifact mismatch: '+str(relative))
        if record['artifacts'][program]['sha256'] != item['sha256']:
            raise ValueError('build receipt mismatch: '+str(relative))
        if record['artifacts'][program]['debugInformationRetained'] is not True:
            raise ValueError('debug information was not retained')
        name = item['releaseName'].format(version=version[1:])
        if Path(name).name != name or not name or name.startswith('.'):
            raise ValueError('invalid release asset name')
        checked.append((path, name))
    if not checked or len({n for _, n in checked}) != len(checked):
        raise ValueError('empty or duplicate release assets')
    if output.exists():
        raise ValueError('asset output must be fresh')
    output.mkdir(parents=True)
    for source, name in checked:
        shutil.copyfile(source, output/name)
        (output/name).chmod(0o755)
    source_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (output/'release.json').write_text(json.dumps(dict(version=version, sourceCommit=source_commit,
        qualificationManifest=manifest, buildReceipts=receipts), indent=2, sort_keys=True)+'\n')
    paths = sorted(p for p in output.iterdir() if p.is_file())
    (output/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in paths))
    return [p.name for p in paths]+['SHA256SUMS']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-output', required=True, type=Path)
    p.add_argument('--manifest', type=Path, default=ROOT/'release/qualification.json')
    p.add_argument('--version', required=True)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prepare(a.build_output, a.manifest, a.version, a.output)))


if __name__ == '__main__':
    main()
