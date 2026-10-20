#!/usr/bin/env python3
"""Freeze this isolated source-only remembered reciprocal proposal."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import tempfile

ROOT=Path('/home/legolas/rook2')
HERE=Path(__file__).resolve().parent
REFERENCE=ROOT/'evidence/activity-value-inputs-generic-build-20261018-01/receipt.json'
AUTHORITY=ROOT/'evidence/remembered-modulus-review-20261018-01/review.md'


def sha(data):return hashlib.sha256(data).hexdigest()


def hashes(base,names):return {name:sha((base/name).read_bytes()) for name in sorted(names)}


def emit(name,value):
    with (HERE/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def main():
    reference=json.loads(REFERENCE.read_text())
    native=reference['source_sha256_before'];tools=reference['tool_sha256_before']
    assert native==reference['source_sha256_after'] and tools==reference['tool_sha256_after']
    assert len(native)==46 and len(tools)==23
    names=native|tools;before=hashes(ROOT,names)
    assert before==names,'root differs from accepted activity7cf native46/tools23'
    target=Path(tempfile.mkdtemp(prefix='imp2-remembered-reciprocal-20261018-',dir='/home/legolas/rook2-work'))
    for name in names:
        dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
    old=(ROOT/'src/remembered.rs').read_text()
    helpers=(HERE/'reciprocal-helpers.rs').read_text()
    test=(HERE/'reciprocal-oracle-test.rs').read_text()
    replacements=[
        ('pub struct RememberedTable {\n    groups: Vec<Group>,',
         'pub struct RememberedTable {\n    groups: Vec<Group>,\n    // Immutable floor(2^32 / group_count); group length never changes in place.\n    reciprocal: u64,'),
        ('impl RememberedTable {',helpers+'impl RememberedTable {'),
        ('Self { groups: vec![Group::default(); count], generation: 1 }',
         'Self { groups: vec![Group::default(); count], generation: 1,\n               reciprocal: group_reciprocal(count) }'),
        ('Ok(Self { groups, generation: 1 })',
         'Ok(Self { groups, generation: 1, reciprocal: group_reciprocal(count) })'),
        ('        key as usize % self.groups.len()',
         '        group_remainder(key, self.groups.len(), self.reciprocal)'),
        ('    #[test]\n    fn exact_interior_is_metadata_only_and_permissions_use_strict_store_bounds() {',
         test+'    #[test]\n    fn exact_interior_is_metadata_only_and_permissions_use_strict_store_bounds() {'),
    ]
    new=old
    for left,right in replacements:
        assert new.count(left)==1,left
        new=new.replace(left,right)
    inverse=new
    for left,right in reversed(replacements):
        assert inverse.count(right)==1,right
        inverse=inverse.replace(right,left)
    assert inverse==old
    marker='#[cfg(test)]\nmod tests'
    assert new[new.index(marker):].replace(test,'')==old[old.index(marker):]
    store='    pub fn store(&mut self, store: Store) {'
    assert new[new.index(store):].replace(test,'')==old[old.index(store):]
    clear='    pub fn clear(&mut self) {'
    group_for='    #[inline]\n    pub fn group_for'
    assert old[old.index(clear):old.index(group_for)]==new[new.index(clear):new.index(group_for)]
    key_start='        let ep = if position.ep < 64 {'
    old_return='        key as usize % self.groups.len()'
    new_return='        group_remainder(key, self.groups.len(), self.reciprocal)'
    assert old[old.index(key_start):old.index(old_return)]==new[new.index(key_start):new.index(new_return)]
    (target/'src/remembered.rs').write_text(new)
    for tree,content in [('basis',old),('proposed',new)]:
        dest=HERE/tree/'src/remembered.rs';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)
    for name,left,right in [('proposal.patch',old,new),('inverse.patch',new,old)]:
        (HERE/name).write_text(''.join(difflib.unified_diff(left.splitlines(True),right.splitlines(True),
                                                        fromfile='a/src/remembered.rs',tofile='b/src/remembered.rs')))
    after=hashes(target,names)
    changes=[name for name in before if before[name]!=after[name]]
    assert changes==['src/remembered.rs'],changes
    assert hashes(ROOT,names)==before
    # Text inventory only; no Rust parsing or unit execution.
    owner_rows=[]
    for name in native:
        if not name.endswith('.rs'):continue
        for line,text in enumerate((ROOT/name).read_text().splitlines(),1):
            if 'RememberedTable {' in text or ('RememberedTable::' in text and name!='src/remembered.rs'):
                owner_rows.append(dict(file=name,line=line,text=text))
    assert old.count('Self { groups')==2
    assert new.count('reciprocal: group_reciprocal(count)')==2
    assert new.count('#[test]')==old.count('#[test]')+1
    emit('basis-source-manifest.json',dict(native46=native,tools23=tools,source69=before,
         reference=str(REFERENCE),reference_sha256=sha(REFERENCE.read_bytes()),
         activity_included=True,pawn_fusion_included=False,full_pair_relation_included=False))
    graph=sha(json.dumps(after,sort_keys=True,separators=(',',':')).encode())
    emit('source-manifest.json',dict(path=str(target),source69=after,source_graph_sha256=graph,
         native46={n:after[n] for n in native},tools23={n:after[n] for n in tools}))
    emit('source-proof.json',dict(changed=changes,unchanged_native_files=45,unchanged_tool_files=23,
         existing_tests_byte_identical_after_removing_single_new_test=True,
         production_store_probe_prime_selection_record_group_bodies_identical=True,
         key_composition_and_clear_body_identical=True,inverse_reconstructs_entire_basis=True,
         literal_table_constructors=2,reciprocal_constructor_initializations=2,
         constructor_and_owner_text_inventory=owner_rows,
         field_owner='RememberedTable private immutable u64 reciprocal',
         per_query_large_divisor_branch=False,first_reducer_branch='key as usize < count',
         expected_native_tests=179,expected_library_tests=177,expected_dev_tests=2,
         expected_diagnostic_units_unchanged=209,new_test_declarations=1,
         new_test_name='reciprocal_group_remainders_match_builtin_modulo_and_survive_clear',
         bounded_test_usize_modulo_comparisons_upper_bound=23480,
         no_rust_parse_build_test_engine_profile_timing_git=True,root_before=before,root_after=hashes(ROOT,names)))
    emit('prepared.json',dict(status='SOURCE_ONLY_UNCOMPILED_UNTESTED_UNMEASURED',source=str(target),
         source_graph_sha256=graph,modified_files=changes,proposed_sha256=after['src/remembered.rs'],
         basis_sha256=before['src/remembered.rs'],reference_review=str(AUTHORITY),
         reference_review_sha256=sha(AUTHORITY.read_bytes()),
         forward_patch_sha256=sha((HERE/'proposal.patch').read_bytes()),
         inverse_patch_sha256=sha((HERE/'inverse.patch').read_bytes()),
         source_proof_sha256=sha((HERE/'source-proof.json').read_bytes()),
         execution_clearance=False))
    print(json.dumps(dict(source=str(target),source_graph_sha256=graph,changed=changes,
          proposed_sha256=after['src/remembered.rs'],expected_native_tests=179,execution_clearance=False)))

if __name__=='__main__':main()
