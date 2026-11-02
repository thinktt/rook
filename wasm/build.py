#!/usr/bin/env python3
"""Build the ordinary and diagnostic WASM modules with locked dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, default=ROOT/'wasm/dist')
p.add_argument('--sysroot', type=Path, help='optional alternate Rust sysroot containing the WASM standard library')
p.add_argument('--linker', help='optional wasm-ld path')
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
flags = ['-C', 'link-arg=-zstack-size=8388608']
if a.sysroot: flags += ['--sysroot='+str(a.sysroot.resolve())]
if a.linker: flags += ['-C', 'linker='+a.linker]
env = dict(os.environ, CARGO_ENCODED_RUSTFLAGS='\x1f'.join(flags))
env.pop('RUSTFLAGS', None)
if hasattr(os, 'sched_setaffinity'):
    housekeeping = set(range(6)) | set(range(8, 14))
    os.sched_setaffinity(0, os.sched_getaffinity(0) & housekeeping)
records = []
for crate, name in [('engine', 'rook_wasm'), ('diagnostic', 'rook_diag_wasm')]:
    manifest = ROOT/f'wasm/{crate}/Cargo.toml'
    command = ['cargo', 'build', '--offline', '--locked', '--release', '--manifest-path', str(manifest), '--target', 'wasm32-unknown-unknown']
    subprocess.run(command, env=env, check=True)
    source = manifest.parent/f'target/wasm32-unknown-unknown/release/{name}.wasm'
    target = a.output/('rook.wasm' if crate == 'engine' else 'rook-diag.wasm')
    shutil.copyfile(source, target)
    records.append(dict(file=target.name, bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
(a.output/'build.json').write_text(json.dumps(dict(rustc=subprocess.check_output(['rustc', '-vV'], text=True), flags=flags, artifacts=records), indent=2)+'\n')
