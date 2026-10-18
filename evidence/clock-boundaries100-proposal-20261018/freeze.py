"""Freeze source-only three-route cold clock proposal and exact public inventory."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import tarfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = Path('/tmp/imp2-generation2-proposal-20261018-9roinj7p')
SOURCE = Path('/home/legolas/rook2-work/imp2-clock-boundaries100-proposal-20261018-4d9e7a1f')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    old = json.loads((OUT / 'base-source-manifest.json').read_text())
    assert len(old) == 100 and all(sha(BASE / p) == h for p, h in old.items())
    paths = sorted([*old, 'diagnostic/src/clock_boundaries.rs'])
    new = {p: sha(SOURCE / p) for p in paths}
    changed = [p for p in new if old.get(p) != new[p]]
    assert changed == ['diagnostic/src/clock_boundaries.rs', 'diagnostic/src/main.rs']
    native = {p: h for p, h in new.items() if p in ('Cargo.toml', 'Cargo.lock') or p.startswith('src/')}
    assert len(native) == 43 and all(old[p] == h for p, h in native.items())
    tools = {p: h for p, h in new.items() if p.startswith('tools/')}
    assert len(tools) == 23
    tests = {p: len(re.findall(r'#\[test\]', (SOURCE / p).read_text())) for p in paths if p.endswith('.rs')}
    native_units = sum(n for p, n in tests.items() if p.startswith('src/'))
    adapter_units = sum(n for p, n in tests.items() if p.startswith('diagnostic/src/'))
    assert native_units == 152 and adapter_units == 164, (native_units, adapter_units)
    operations = json.loads((ROOT / 'evidence/generation2-proposal-20261018/plan.json').read_text())['operations']
    operations = {**operations, 'time.adaptiveSequence': 12, 'search.iterationTerminalStop': 3, 'session.timeSetup': 28}
    assert len(operations) == 100 and sum(operations.values()) == 7490
    files, ids, actual = [], set(), {}
    for path in sorted(Path('/home/legolas/king-spec/conformance/fixtures').glob('*.json')):
        data = json.loads(path.read_text())
        cases = data.get('cases', []) if isinstance(data, dict) else []
        selected = [c for c in cases if c.get('request', {}).get('operation') in operations]
        if not selected:
            continue
        assert len(selected) == len(cases), str(path)
        case_ids = []
        for case in selected:
            key = case['id']; assert key not in ids, key
            ids.add(key); case_ids.append(key)
            name = case['request']['operation']; actual[name] = actual.get(name, 0) + 1
        files.append(dict(path=str(path), sha256=sha(path), cases=len(selected), case_ids=case_ids))
    assert actual == operations and len(ids) == 7490 and len(files) == 95, (len(actual), len(ids), len(files))
    patch = ''
    for p in changed:
        before = (BASE / p).read_text().splitlines(keepends=True) if p in old else []
        after = (SOURCE / p).read_text().splitlines(keepends=True)
        patch += ''.join(difflib.unified_diff(before, after, fromfile='a/' + p, tofile='b/' + p))
    with (OUT / 'proposal.patch').open('x') as stream:
        stream.write(patch)
    with tarfile.open(OUT / 'source-101.tar.gz', 'x:gz') as archive:
        for p in paths:
            archive.add(SOURCE / p, arcname=p, recursive=False)
    write('source-manifest.json', new)
    write('whole-fixture-inventory.json', files)
    write('test-source-inventory.json', tests)
    write('plan.json', dict(status='SOURCE_ONLY; uncompiled/unexecuted; parent independent review pending',
          source=str(SOURCE), base=str(BASE), source_files=101, native_source_files=43, tools_files=23,
          adapter_source_files=35, native_units_expected=152, diagnostic_units_expected=164,
          operation_count=100, operations=operations, unique_cases=7490, whole_files=95,
          partial_files=0, duplicate_ids=0, new_cases=43, new_whole_files=3,
          native_unchanged=True, source_manifest_sha256=sha(OUT / 'source-manifest.json'),
          source_archive_sha256=sha(OUT / 'source-101.tar.gz'), patch_sha256=sha(OUT / 'proposal.patch')))
    assert all(sha(SOURCE / p) == h for p, h in new.items())
    print(json.dumps(dict(source_only=True, native_units_unrun=152, adapter_units_unrun=164,
                          operations=100, cases=7490, whole_files=95, changed=changed)))


if __name__ == '__main__':
    main()
