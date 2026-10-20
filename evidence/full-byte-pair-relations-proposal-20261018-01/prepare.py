#!/usr/bin/env python3
"""Freeze this one source-only full-byte-pair proposal; no Rust/native jobs."""
from pathlib import Path
import collections
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path('/home/legolas/rook2')
HERE = Path(__file__).resolve().parent
REFERENCE = ROOT / 'evidence/activity-value-inputs-generic-build-20261018-01/receipt.json'
AUTHORITY = Path('/home/legolas/king-spec/spec/evaluation-relations.md')
CHANGED = ['src/influence.rs', 'src/relation_table.rs']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def hashes(base, names):
    return {name: digest((base / name).read_bytes()) for name in sorted(names)}


def emit(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    reference = json.loads(REFERENCE.read_text())
    native = reference['source_sha256_before']
    tools = reference['tool_sha256_before']
    assert native == reference['source_sha256_after']
    assert tools == reference['tool_sha256_after']
    expected = native | tools
    assert len(native) == 46 and len(tools) == 23
    before = hashes(ROOT, expected)
    assert before == expected, 'current source differs from accepted activity-only basis'
    # Check table ownership across this entire bounded native closure.
    references = []
    for name in native:
        if name.endswith('.rs') and 'relation_table::' in (ROOT / name).read_text():
            references.append(name)
    assert references == ['src/influence.rs'], references
    target = Path(tempfile.mkdtemp(prefix='imp2-full-byte-pair-relations-20261018-',
                                   dir='/home/legolas/rook2-work'))
    for name in expected:
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
    for tree in ['basis', 'proposed']:
        for name in CHANGED:
            dest = HERE / tree / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
    old = (target / 'src/influence.rs').read_text()
    old_comment = '/// Classify the same four tested-piece tiers using capped count/tier states.'
    new_comment = '/// Classify the same four tested-piece tiers directly from normalized bytes.'
    old_lookup = '    let own = (crate::relation_table::CLASS[own as usize] & 15) as usize;\n    let opponent = (crate::relation_table::CLASS[opponent as usize] & 15) as usize;\n    crate::relation_table::RELATIONS[tested][(own << 4) | opponent]'
    new_lookup = '    crate::relation_table::RELATIONS[tested][((own as usize) << 8) | opponent as usize]'
    assert old.count(old_comment) == old.count(old_lookup) == 1
    new = old.replace(old_comment, new_comment).replace(old_lookup, new_lookup)
    assert new.replace(new_comment, old_comment).replace(new_lookup, old_lookup) == old
    (target / 'src/influence.rs').write_text(new)
    generated = HERE / 'generated-relation-table.rs'
    argv = ['taskset', '-c', '0-5,8-13', 'python3',
            str(HERE / 'generate_full_relations.py'), '--output', str(generated)]
    child = subprocess.run(argv, capture_output=True, check=False)
    (HERE / 'generator.stdout').write_bytes(child.stdout)
    (HERE / 'generator.stderr').write_bytes(child.stderr)
    emit('generator-command.json', dict(argv=argv, cwd=str(Path.cwd()),
         exit_code=child.returncode, kind='Python source generation only; not a native test'))
    assert child.returncode == 0
    shutil.copy2(generated, target / 'src/relation_table.rs')
    for name in CHANGED:
        shutil.copy2(target / name, HERE / 'proposed' / name)
    after = hashes(target, expected)
    assert [name for name in before if before[name] != after[name]] == CHANGED
    assert hashes(ROOT, expected) == before, 'root changed during source preparation'
    marker = '#[cfg(test)]\nmod tests'
    assert old[old.index(marker):] == new[new.index(marker):]
    assert old[:old.index(old_comment)] == new[:new.index(new_comment)]
    # Everything after relation(), including adjusted_relation and all tests,
    # is byte-identical; selection/panic/shortcut prefix is unchanged too.
    tail = '/// Exclude from normalized own support'
    assert old[old.index(tail):] == new[new.index(tail):]
    head = 'pub fn relation(own: u8, opponent: u8, kind: PieceKind) -> Relation {'
    assert old[old.index(head):old.index(old_lookup)] == new[new.index(head):new.index(new_lookup)]
    table = generated.read_text()
    payload = table.split('pub(crate) static RELATIONS:', 1)[1].split('= [', 1)[1]
    tokens = re.findall(r'\b[UCF]\b', payload)
    assert len(tokens) == 4 * 65536
    assert len(re.findall(r'^    \[$', payload, re.M)) == 4
    assert 'CLASS' not in table and 'unsafe' not in table
    assert '[[Relation; 65_536]; 4]' in table
    # Read-back structure only. No second formula/test is introduced.
    for direction, left, right in [('proposal.patch', ROOT, target),
                                    ('inverse.patch', target, ROOT)]:
        chunks = []
        for name in CHANGED:
            chunks.extend(difflib.unified_diff((left/name).read_text().splitlines(True),
                          (right/name).read_text().splitlines(True),
                          fromfile='a/' + name, tofile='b/' + name))
        (HERE / direction).write_text(''.join(chunks))
    shutil.copy2(AUTHORITY, HERE / 'evaluation-relations.md')
    emit('basis-source-manifest.json', dict(parent_assigned_revision='ed85b6dd',
         native46=native, tools23=tools, source69=before,
         accepted_activity_build_receipt=str(REFERENCE),
         accepted_activity_build_receipt_sha256=digest(REFERENCE.read_bytes()),
         root_native46_tools23_equal_accepted_activity_basis=True,
         activity_included=True, pawn_fusion_included=False))
    emit('source-manifest.json', dict(path=str(target), source69=after,
         native46={k:after[k] for k in native}, tools23={k:after[k] for k in tools},
         source_graph_sha256=digest(json.dumps(after,sort_keys=True,separators=(',', ':')).encode())))
    emit('source-proof.json', dict(modified_files=CHANGED,
         unchanged_native_files=44, unchanged_tools=23,
         relation_prefix_kind_dispatch_and_zero_shortcut_identical=True,
         adjusted_relation_and_all_later_source_identical=True,
         independent_exhaustive_test_module_identical=True,
         influence_builder_and_all_prior_source_identical=True,
         inverse_lookup_and_comment_reconstruct_entire_old_influence=True,
         relation_table_consumers=references,
         typed_payload_elements=len(tokens), per_tier_elements=65536,
         symbolic_outcomes=dict(collections.Counter(tokens)),
         declared_payload_bytes=262144, previous_declared_payload_bytes=1280,
         payload_increase_bytes=260864, payload_ratio=204.8,
         generated_source_bytes=generated.stat().st_size,
         expected_native_declarations_unchanged=178,
         expected_diagnostic_declarations_unchanged=209,
         no_build_test_rust_parse_engine_profile_timing_git=True,
         root_before=before, root_after=hashes(ROOT,expected)))
    emit('prepared.json', dict(status='SOURCE_ONLY_UNCOMPILED_UNTESTED_UNMEASURED',
         source=str(target), parent_basis='ed85b6dd/activity7cf-source46+tools23',
         modified_files=CHANGED,
         generator_sha256=digest((HERE/'generate_full_relations.py').read_bytes()),
         authority_path=str(AUTHORITY), authority_sha256=digest(AUTHORITY.read_bytes()),
         proposed_files=hashes(target,CHANGED), basis_files=hashes(ROOT,CHANGED),
         forward_patch_sha256=digest((HERE/'proposal.patch').read_bytes()),
         inverse_patch_sha256=digest((HERE/'inverse.patch').read_bytes()),
         source_manifest_sha256=digest((HERE/'source-manifest.json').read_bytes()),
         source_proof_sha256=digest((HERE/'source-proof.json').read_bytes()),
         execution_clearance=False))
    print(json.dumps(dict(source=str(target), source_files=len(after), changed=CHANGED,
          proposed_files=hashes(target,CHANGED), data_bytes=262144)))


if __name__ == '__main__':
    main()
