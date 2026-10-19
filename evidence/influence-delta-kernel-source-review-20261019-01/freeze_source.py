#!/usr/bin/env python3
"""Source-text/hash closure only; never parses Rust or runs native code."""
from pathlib import Path
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
BASE = Path('/home/legolas/rook2/evidence/ordinary-projected-bits-generic-build-20261018-01')
TRIAL = Path('/home/legolas/rook2-work/imp2-influence-delta-20261019-01')
ADDED = 'src/influence_delta_tests.rs'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_map(root, paths):
    return {p: digest((root / p).read_bytes()) for p in sorted(paths)}

def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

receipt = json.loads((BASE / 'receipt.json').read_text())
before = {**receipt['source_sha256_before'], **receipt['tool_sha256_before']}
assert len(before) == 69
assert read_map(BASE / 'source-before', before) == before
assert set(p.relative_to(TRIAL).as_posix() for p in TRIAL.rglob('*') if p.is_file()) == set(before) | {ADDED}
after = read_map(TRIAL, set(before) | {ADDED})
changed = sorted(p for p in before if after[p] != before[p])
assert changed == ['src/attacks.rs', 'src/influence.rs']
assert all(after[p] == h for p, h in receipt['tool_sha256_before'].items())
proof = json.loads((HERE / 'kernel-source-proof.json').read_text())
assert proof['proposed_kernel_files'] == {p: after[p] for p in changed}
paths = changed + [ADDED]
forward, inverse = [], []
for p in paths:
    a = (BASE / 'source-before' / p).read_text() if p in before else ''
    b = (TRIAL / p).read_text()
    # Independent ndiff endpoint reconstruction, without Rust parsing.
    delta = list(difflib.ndiff(a.splitlines(True), b.splitlines(True)))
    assert ''.join(difflib.restore(delta, 1)) == a
    assert ''.join(difflib.restore(delta, 2)) == b
    forward.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
        fromfile='a/' + p if p in before else '/dev/null', tofile='b/' + p))
    inverse.extend(difflib.unified_diff(b.splitlines(True), a.splitlines(True),
        fromfile='a/' + p, tofile='b/' + p if p in before else '/dev/null'))
(HERE / 'proposal.patch').write_text(''.join(forward))
(HERE / 'inverse.patch').write_text(''.join(inverse))
count = lambda text: len(re.findall(r'^\s*#\[test\]\s*$', text, re.M))
old_tests = sum(count((BASE / 'source-before' / p).read_text()) for p in before if p.endswith('.rs'))
new_tests = count((TRIAL / ADDED).read_text())
assert old_tests == 178
assert sum(count((TRIAL / p).read_text()) for p in after if p.endswith('.rs')) == old_tests + new_tests
write_json('source-before-manifest.json', {'schema': 'relative-path-sha256-v1', 'files': before,
    'graph_sha256': digest(json.dumps(before, sort_keys=True, separators=(',', ':')).encode())})
write_json('source-manifest.json', {'schema': 'relative-path-sha256-v1', 'files': after,
    'graph_sha256': digest(json.dumps(after, sort_keys=True, separators=(',', ':')).encode())})
write_json('test-declarations.json', {'existing': old_tests, 'new': new_tests, 'total': old_tests + new_tests,
    'executed': False, 'count_method': 'textual #[test] declarations; not Rust parse'})
write_json('prepared.json', {'source': str(TRIAL), 'source_files': len(after),
    'native_files': len(receipt['source_sha256_before']) + 1, 'tools_files': len(receipt['tool_sha256_before']),
    'changed_existing': changed, 'added': [ADDED], 'source_graph_sha256': digest(json.dumps(after, sort_keys=True, separators=(',', ':')).encode()),
    'patch_sha256': digest((HERE / 'proposal.patch').read_bytes()),
    'inverse_sha256': digest((HERE / 'inverse.patch').read_bytes()),
    'endpoint_reconstruction': True, 'native_tests': old_tests + new_tests,
    'native_execution': False, 'rust_parse': False, 'authority': 'source-only kernel prototype; no integration/build/test/measurement'})
assert read_map(TRIAL, after) == after
print(json.dumps(json.loads((HERE / 'prepared.json').read_text()), indent=2))
