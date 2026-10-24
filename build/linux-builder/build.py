#!/usr/bin/env python3
"""Build unstripped dynamic/static glibc companions from explicit release inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=Path('/source'))
    p.add_argument('--output', type=Path, default=Path('/out'))
    p.add_argument('--variant', choices=['all', 'glibc', 'glibc-static'], default='all')
    p.add_argument('--mode', choices=['release', 'generate', 'plain'], default='release')
    p.add_argument('--jobs', type=int, default=4)
    a = p.parse_args()
    if not 1 <= a.jobs <= 64 or not a.output.is_dir() or any(a.output.iterdir()):
        p.error('jobs must be 1..64; output must be an existing empty directory')
    recipe_path = a.source/'build/release.json'
    recipe = json.loads(recipe_path.read_text())
    if recipe['schema'] != 'rook-release-build-v1':
        p.error('unsupported build recipe')
    if sha(a.source/'diagnostic/Cargo.lock') != sha(HERE/'diagnostic-Cargo.lock'):
        p.error('diagnostic lock changed; refresh the builder lock and rebuild the image')
    source, home = Path(recipe['sourceRoot']), Path(recipe['cargoHome'])
    if any(not path.is_absolute() or '..' in path.parts or path.parts[1] not in ('home', 'build') for path in [source, home]):
        p.error('build paths must be absolute paths below /home or /build')
    if source.exists() or home.exists():
        p.error('fresh /home and /build mounts required')
    names = ['Cargo.toml', 'Cargo.lock', 'diagnostic/Cargo.toml', 'diagnostic/Cargo.lock']
    names += [str(f.relative_to(a.source)) for prefix in ['src', 'diagnostic/src']
              for f in sorted((a.source/prefix).rglob('*')) if f.is_file()]
    if any((a.source/n).exists() for n in ['build.rs', 'diagnostic/build.rs']):
        p.error('project build.rs needs explicit review before adding it to this recipe')
    snapshot = {n:sha(a.source/n) for n in names}
    graph = hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if graph != recipe['sourceGraphSha256']:
        p.error('source graph differs from the profile-bound release recipe')
    for n in names:
        dest = source/n
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(a.source/n, dest)
    vendor = home/'registry/src'/recipe['registryDirectory']
    shutil.copytree(HERE/'vendor', vendor)
    (home/'config.toml').write_text(
        '[source.crates-io]\nreplace-with="locked-vendor"\n'
        '[source.locked-vendor]\ndirectory='+json.dumps(str(vendor))+'\n[net]\noffline=true\n')
    env = dict(PATH='/usr/bin:/bin', HOME=str(home.parent), CARGO_HOME=str(home),
               RUSTC='/usr/bin/rustc', RUSTC_WRAPPER='', RUSTC_WORKSPACE_WRAPPER='',
               CARGO_NET_OFFLINE='true', CARGO_INCREMENTAL='0', CARGO_BUILD_JOBS=str(a.jobs),
               LANG='C', LC_ALL='C', TZ='UTC', TMPDIR='/tmp')
    version = subprocess.check_output(['/usr/bin/rustc', '-vV'], env=env, text=True)
    variants = list(recipe['variants']) if a.variant == 'all' else [a.variant]
    for variant in variants:
        settings = recipe['variants'][variant]
        out = a.output/variant
        out.mkdir()
        base = ['-C', 'target-cpu='+recipe['cpu']]
        if settings['static']:
            base += ['-C', 'target-feature=+crt-static']
        flags = list(base)
        profile_hash = None
        if a.mode == 'generate':
            raw = Path('/profiles-out')/variant
            raw.mkdir()
            flags += ['-C', 'profile-generate='+str(raw)]
        elif a.mode == 'release':
            text = a.source/settings['profileText']
            if sha(text) != settings['profileTextSha256']:
                raise ValueError('profile text checksum mismatch: '+variant)
            profile = Path(settings['profilePath'])
            profile.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['llvm-profdata-19', 'merge', str(text), '-o', str(profile)], check=True)
            profile_hash = sha(profile)
            flags += ['-C', 'profile-use='+str(profile), '-C',
                      'llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false']
        artifacts = {}
        for name, binary, manifest, program_flags in [
            ('rook', 'rook2', source/'Cargo.toml', flags),
            ('rook-diag', 'rook2-diag', source/'diagnostic/Cargo.toml', base),
        ]:
            command = ['/usr/bin/cargo', 'build', '--offline', '--locked', '--release', '--verbose',
                       '--target', recipe['target'], '--jobs', str(a.jobs), '--target-dir',
                       '/build/target/'+variant+'/'+name, '--manifest-path', str(manifest), '--bin', binary]
            child_env = dict(env, RUSTFLAGS=' '.join(program_flags), CARGO_ENCODED_RUSTFLAGS='\x1f'.join(program_flags))
            with (out/(name+'.stdout')).open('xb') as so, (out/(name+'.stderr')).open('xb') as se:
                subprocess.run(command, cwd=source, env=child_env, stdout=so, stderr=se, check=True)
            log = (out/(name+'.stderr')).read_text().lower()
            if name == 'rook' and a.mode == 'release' and any(s in log for s in [
                'no profile data available for function', 'profile data may be out of date',
                'profile data mismatch', 'malformed instrumentation profile', 'hash mismatch', 'unprofiled function']):
                raise ValueError('stale or missing PGO data: '+variant)
            image = out/name
            shutil.copyfile(Path('/build/target')/variant/name/recipe['target']/'release'/binary, image)
            image.chmod(0o755)
            programs = subprocess.check_output(['readelf', '-lW', str(image)], text=True)
            dynamic = subprocess.check_output(['readelf', '-dW', str(image)], text=True)
            sections = subprocess.check_output(['readelf', '-SW', str(image)], text=True)
            if '.debug_info' not in sections or '.symtab' not in sections:
                raise ValueError('debug information or symbols missing: '+name)
            if settings['static']:
                if ' INTERP ' in programs or '(NEEDED)' in dynamic:
                    raise ValueError('static artifact requires a dynamic runtime')
            elif '/lib64/ld-linux-x86-64.so.2' not in programs or 'libc.so.6' not in dynamic:
                raise ValueError('unexpected dynamic runtime')
            artifacts[name] = dict(sha256=sha(image), bytes=image.stat().st_size,
                                   flags=program_flags, argv=command, debugInformationRetained=True)
        if any(sha(source/n) != h or sha(a.source/n) != h for n, h in snapshot.items()):
            raise ValueError('source changed during compilation')
        if a.mode == 'release' and sha(profile) != profile_hash:
            raise ValueError('profile changed during compilation')
        write(out/'build.json', dict(schema='rook-linux-build-v1', variant=variant, mode=a.mode,
            recipeSha256=sha(recipe_path), sourceGraphSha256=graph, sourceSha256=snapshot,
            rustc=version, profileSha256=profile_hash, artifacts=artifacts))
        (out/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+k+'\n' for k, v in artifacts.items()))
        print(json.dumps(dict(variant=variant, artifacts={k:v['sha256'] for k,v in artifacts.items()})), flush=True)


if __name__ == '__main__':
    main()
