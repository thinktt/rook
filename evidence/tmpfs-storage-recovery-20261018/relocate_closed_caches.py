"""Move only named closed, rebuildable caches off tmpfs; retain source paths."""
from pathlib import Path
import hashlib
import json
import os
import shutil

OUT = Path(__file__).resolve().parent
DEST = Path('/home/legolas/rook2-build-cache/closed-20261018')
NAMES = ['imp2-eval-observers-20261018', 'imp2-eval-pawn-context-20261018',
         'imp2-eval-pawn-observers-20261018', 'imp2-full-fresh-proposal-20261018-92x348cj',
         'imp2-retained-evaluation-proposal-20261018-uz57d6p0',
         'imp2-generation-safety-20261018', 'imp2-generation-evasion-20261018',
         'imp2-evaluation-inputs-20261018']


def source_map(root):
    paths = []
    for crate in [root, root/'diagnostic']:
        paths += [p for p in [crate/'Cargo.toml', crate/'Cargo.lock'] if p.is_file()]
        if (crate/'src').exists():
            paths += [p for p in (crate/'src').rglob('*') if p.is_file()]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


roots = [Path('/tmp')/name for name in NAMES]
assert all(root.is_dir() and not root.is_symlink() for root in roots)
active = []
for process in Path('/proc').iterdir():
    if not process.name.isdigit():
        continue
    try:
        exe = os.readlink(process/'exe')
        if any(exe.startswith(str(root)+'/') for root in roots):
            active.append(int(process.name))
    except OSError:
        pass
assert not active, active
before = {str(root): source_map(root) for root in roots}
record = dict(complete=False, failure=None, moves=[], source_before=before,
              tmpfs_available_before=shutil.disk_usage('/tmp').free,
              home_available_before=shutil.disk_usage('/home/legolas').free,
              active_images_under_selected_roots=active,
              scope='Named historical closed compiler caches only; active phase1/95 source, caches, profiles and all frozen artifacts untouched')
try:
    for root in roots:
        for relative in ['target', 'diagnostic/target']:
            old = root/relative
            if not old.is_dir() or old.is_symlink():
                continue
            new = DEST/root.name/relative
            assert not new.exists() and not new.is_symlink()
            new.parent.mkdir(parents=True, exist_ok=True)
            sizes = [p.stat().st_size for p in old.rglob('*') if p.is_file()]
            shutil.move(str(old), str(new))
            old.symlink_to(new, target_is_directory=True)
            assert old.resolve() == new and new.is_dir()
            after_sizes = [p.stat().st_size for p in new.rglob('*') if p.is_file()]
            assert sorted(sizes) == sorted(after_sizes)
            record['moves'].append(dict(original=str(old), destination=str(new),
                                        regular_files=len(sizes), logical_bytes=sum(sizes)))
    record['source_after'] = {str(root): source_map(root) for root in roots}
    assert record['source_after'] == before
    record['complete'] = True
except BaseException as error:
    record['failure'] = f'{type(error).__name__}: {error}'
record.update(tmpfs_available_after=shutil.disk_usage('/tmp').free,
              home_available_after=shutil.disk_usage('/home/legolas').free)
with (OUT/'result.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({k: record[k] for k in ['complete', 'failure', 'tmpfs_available_before', 'tmpfs_available_after']}))
raise SystemExit(0 if record['complete'] else 1)
