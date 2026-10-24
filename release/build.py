#!/usr/bin/env python3
"""Run the same pinned builder locally and in GitHub Actions."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--docker', default='docker')
    p.add_argument('--image', default='rook-release-builder:local')
    p.add_argument('--skip-image-build', action='store_true')
    p.add_argument('--variant', choices=['all', 'glibc', 'glibc-static'], default='all')
    p.add_argument('--mode', choices=['release', 'generate', 'plain'], default='release')
    p.add_argument('--profiles-out', type=Path)
    p.add_argument('--cidfile', type=Path, help='optional container ID file for external supervision')
    a = p.parse_args()
    out = a.output.resolve()
    if out.exists():
        p.error('output must be a fresh external directory')
    if not a.skip_image_build:
        subprocess.run([a.docker, 'build', '--platform', 'linux/amd64', '-t', a.image,
                        str(ROOT/'build/linux-builder')], check=True)
    out.mkdir(parents=True)
    command = [a.docker, 'run', '--rm', '--platform', 'linux/amd64', '--network', 'none',
               '--read-only', '--user', f'{os.getuid()}:{os.getgid()}',
               '--tmpfs', '/home:exec,mode=1777', '--tmpfs', '/build:exec,mode=1777',
               '--tmpfs', '/tmp:exec,mode=1777',
               '--mount', f'type=bind,src={ROOT},dst=/source,readonly',
               '--mount', f'type=bind,src={out},dst=/out']
    if a.cidfile:
        command += ['--cidfile', str(a.cidfile.resolve())]
    if a.mode == 'generate':
        if not a.profiles_out or a.profiles_out.exists():
            p.error('generate requires a fresh --profiles-out directory')
        raw = a.profiles_out.resolve()
        raw.mkdir(parents=True)
        command += ['--mount', f'type=bind,src={raw},dst=/profiles-out']
    command += [a.image, '--variant', a.variant, '--mode', a.mode]
    subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
