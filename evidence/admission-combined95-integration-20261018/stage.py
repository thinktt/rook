"""Stage only closed95 and phase1-PGO evidence plus the exact promoted source."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
integration = json.loads((OUT / 'integration.json').read_text())
for relative, digest in integration['source_map'].items():
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest

paths = ['src', 'diagnostic/src', 'diagnostic/README.md', 'STATUS.md',
         'docs/decisions/0009-shared-search-boundaries.md', 'docs/qualification-gaps.md',
         'docs/research/remaining-performance.md', 'docs/research/production-score-capacity.md']
for prefix in ['admission-combined95-', 'diagnostic-admission-combined95-', 'pgo-ordered-bit-checkers-phase1-']:
    paths.extend(str(p.relative_to(ROOT)) for p in (ROOT / 'evidence').iterdir() if p.is_dir() and p.name.startswith(prefix))
paths.append('evidence/generation2-proposal-review-20261018')
paths = sorted(set(paths))
assert all((ROOT / p).exists() for p in paths)
assert all('ordered-q-bitview-phase2-' not in p and 'generation2-validation-' not in p for p in paths)
with (OUT / 'staging-whitelist.json').open('x') as stream:
    json.dump(paths, stream, indent=2); stream.write('\n')
subprocess.run(['git', '-C', str(ROOT), 'diff', '--check', '--', 'src', 'diagnostic/src', 'docs', 'STATUS.md'], check=True)
subprocess.run(['git', '-C', str(ROOT), 'add', '--', *paths], check=True)
subprocess.run(['git', '-C', str(ROOT), 'diff', '--cached', '--check', '--', 'src', 'diagnostic/src', 'diagnostic/README.md', 'docs', 'STATUS.md'], check=True)
names = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--cached', '--name-only', '-z']).decode().split('\0')
assert not any('ordered-q-bitview-phase2-' in p or 'generation2-validation-' in p for p in names)
print(json.dumps(dict(staged_files=len([p for p in names if p]), source99_matches=True,
                      active_phase2_and_generation2_excluded=True)))
