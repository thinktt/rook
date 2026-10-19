#!/usr/bin/env python3
"""Source bytes/text-only freeze; does not parse or execute Rust or build tools."""
import difflib
import hashlib
import json
import re
from pathlib import Path

E = Path('/home/legolas/rook2/evidence/weighted-bound-cache-preparation-20261019-01')
S = Path('/home/legolas/rook2-work/imp2-weighted-bound-cache-20261019-01')
B = Path('/home/legolas/rook2/evidence/ordinary-projected-bits-pgo-use-build-20261018-01/source-before')
ALLOWED = ['src/evaluator.rs', 'src/ordinary.rs', 'src/quiescence.rs', 'src/session.rs', 'src/timed.rs']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(name, value):
    path = E / name
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def between(text, start, end):
    assert text.count(start) == 1, start
    rest = text.split(start, 1)[1]
    assert end in rest, end
    return start + rest.split(end, 1)[0]

def body(text):
    start = text.index('    fn full_impl<')
    start = text.index('        let position = &node.position;', start)
    return text[start:text.index('    pub fn fast(', start)]

basis = json.loads((E / 'basis-source-manifest.json').read_text())
old = basis['source69']
assert len(old) == 69
assert len(basis['native46']) == 46 and len(basis['tools23']) == 23
assert all(sha((B / name).read_bytes()) == digest for name, digest in old.items())
current = {name: sha((S / name).read_bytes()) for name in old}
changed = sorted(name for name in old if current[name] != old[name])
assert changed == ALLOWED, changed
assert all(current[name] == digest for name, digest in basis['tools23'].items())

test_blocks = {}
for name in ALLOWED:
    before = (B / name).read_text()
    after = (S / name).read_text()
    assert (E / 'basis' / Path(name).name).read_text() == before
    if name.endswith(('evaluator.rs', 'quiescence.rs', 'session.rs')):
        block = before[before.index('#[cfg(test)]\nmod tests {'):]
    elif name.endswith('timed.rs'):
        block = between(before, '#[cfg(test)]\nmod tests {', '\nimpl<const D: bool, H: crate::host::Host> Search<D, H>')
    else:
        block = between(before, '#[cfg(test)]\nmod tests {', '\npub struct Iteration {')
    assert after.count(block) == 1, ('old test module changed', name)
    test_blocks[name] = {'bytes': len(block.encode()), 'sha256': sha(block.encode()), 'unchanged': True}

before = (B / 'src/evaluator.rs').read_text()
after = (S / 'src/evaluator.rs').read_text()
old_full = body(before)
new_full = body(after)
old_producers = between(old_full,
    '        let activity = activity::compute(position, influence, material, self.weights.mobility);\n',
    '        let structure = pawn_progress::structure_weighted(')
new_producers = between(new_full,
    '        let cached = if ROOT_CACHE { self.bound_get(position) } else { None };\n',
    '        let structure = pawn_progress::structure_weighted(')
normalized = new_full.replace(new_producers, old_producers, 1)
for a, b in [('pure.pieces', 'activity.pieces'), ('pure.activity', 'activity.weighted'),
             ('pure.shelter', 'shelter.weighted'), ('pure.relation_queries', 'activity.relation_queries')]:
    normalized = normalized.replace(a, b)
assert normalized == old_full, 'numerical full suffix/prefix changed'

# Every old test function remains in the unchanged files or exact old modules.
def declarations(base):
    rows = []
    for name in sorted(basis['native46']):
        if not name.endswith('.rs'):
            continue
        text = (base / name).read_text()
        for match in re.finditer(r'#\[test\]\s*fn\s+([A-Za-z0-9_]+)', text):
            rows.append({'file': name, 'name': match.group(1)})
    return rows

old_tests = declarations(B)
new_tests = declarations(S)
assert len(old_tests) == 178, len(old_tests)
old_pairs = {(r['file'], r['name']) for r in old_tests}
new_pairs = {(r['file'], r['name']) for r in new_tests}
assert old_pairs <= new_pairs and len(new_pairs) == len(new_tests)
added = [r for r in new_tests if (r['file'], r['name']) not in old_pairs]
assert len(added) == 8 and len(new_tests) == 186, (len(added), len(new_tests))
assert all(r['name'].startswith('bound_') for r in added)
assert sum(r['file'] == 'src/development.rs' for r in new_tests) == 2

patches = []
inverse = []
for name in changed:
    a = (B / name).read_text().splitlines(keepends=True)
    b = (S / name).read_text().splitlines(keepends=True)
    patches.extend(difflib.unified_diff(a, b, fromfile='a/' + name, tofile='b/' + name))
    inverse.extend(difflib.unified_diff(b, a, fromfile='a/' + name, tofile='b/' + name))
    target = E / 'proposed' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists()
    target.write_bytes((S / name).read_bytes())
for name, content in [('trial.patch', patches), ('inverse.patch', inverse)]:
    path = E / name
    assert not path.exists()
    path.write_text(''.join(content))

graph = sha(json.dumps(current, sort_keys=True, separators=(',', ':')).encode())
write('source-manifest.json', {'source': str(S), 'source_graph': graph,
    'native46': {n: current[n] for n in basis['native46']},
    'tools23': {n: current[n] for n in basis['tools23']}, 'source69': current,
    'changed': changed, 'basis_source': str(B), 'basis_graph': basis.get('source_graph')})
write('test-declarations.json', {'unrun': True, 'old_tests': 178,
    'expected_native_tests': 186, 'expected_library_tests': 184,
    'expected_development_tests': 2, 'added': added, 'all': new_tests,
    'unchanged_old_test_modules': test_blocks})
write('source-proof.json', {'source_only': True, 'source_graph': graph,
    'source_files': 69, 'native_files': 46, 'tools': 23, 'changed_files': changed,
    'all_other_64_files_byte_equal': True, 'all_tools_byte_equal': True,
    'old_178_test_bodies_unchanged': True, 'old_test_modules': test_blocks,
    'full_body_inverse': {'equal': True, 'basis_sha256': sha(old_full.encode()),
        'normalized_trial_sha256': sha(normalized.encode()),
        'normalization': ['replace only cache-or-payload producer block with exact two old producers',
            'pure.pieces -> activity.pieces', 'pure.activity -> activity.weighted',
            'pure.shelter -> shelter.weighted', 'pure.relation_queries -> activity.relation_queries']},
    'no_rust_parse_compile_build_test_or_engine_execution': True})
write('prepared.json', {'experiment': 33, 'source_only': True, 'execution_authorized': False,
    'source': str(S), 'source_graph': graph, 'basis_source': str(B), 'source_files': 69,
    'native_files': 46, 'tools': 23, 'changed_files': changed,
    'expected_native_tests': 186, 'expected_library_tests': 184, 'expected_development_tests': 2,
    'new_tests': added, 'slot_count': 1024, 'entry_expected_bytes': 64,
    'payload_expected_bytes': 24, 'layout_assertions_unrun': True,
    'production_retained': 25, 'root_design': '/home/legolas/rook2/evidence/weighted-bound-cache-proposal-20261019-01/design.md',
    'trial_patch_sha256': sha((E / 'trial.patch').read_bytes()),
    'inverse_patch_sha256': sha((E / 'inverse.patch').read_bytes())})
print(json.dumps({'complete': True, 'source_only': True, 'source_graph': graph,
    'changed_files': changed, 'native_declarations': len(new_tests),
    'new_declarations': len(added), 'source_files': len(current)}, sort_keys=True))
