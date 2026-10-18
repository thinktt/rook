"""Independent unified-text patch application and source-scope restoration only."""
from pathlib import Path
import json,re
p=Path(__file__).parent
base=(p/'base-src/pawn_progress.rs').read_text();proposed=(p/'proposed-src/pawn_progress.rs').read_text()
def apply(source,patch):
 lines=source.splitlines(keepends=True);out=[];cursor=0
 hunks=patch.splitlines(keepends=True);i=2
 while i<len(hunks):
  m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',hunks[i]);assert m,hunks[i]
  start=int(m[1])-1;old_count=int(m[2] or '1');new_count=int(m[4] or '1')
  assert start>=cursor
  out+=lines[cursor:start];cursor=start;i+=1;removed=added=0
  while i<len(hunks) and not hunks[i].startswith('@@ '):
   line=hunks[i];prefix=line[0];value=line[1:]
   if prefix in ' -': assert lines[cursor]==value;cursor+=1;removed+=1
   if prefix in ' +':out.append(value);added+=1
   assert prefix in ' +-';i+=1
  assert (removed,added)==(old_count,new_count)
 out+=lines[cursor:]
 return ''.join(out)
assert apply(base,(p/'proposal.patch').read_text())==proposed
assert apply(proposed,(p/'inverse.patch').read_text())==base
# Restore the old raw body by removing only the path collector/tuple projection.
start='    const COEFFICIENT:';end='\n#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub struct Paths'
old=base[base.index(start):base.index(end)]
new=proposed[proposed.index(start):proposed.index(end)]
new=new.replace('    let mut path = 0;\n    let mut protected = true;\n','',1)
new=new.replace('''        if WITH_PATH {
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || own != 0;
        }
''','',1)
new=new.replace('    let raw = if map.code(side, pawn) >> 6 != 0 {','    if map.code(side, pawn) >> 6 != 0 {',1)
assert new.endswith('    };\n    (raw, path, protected)\n}\n')
new=new[:-len('    };\n    (raw, path, protected)\n}\n')]+'    }\n}\n'
assert old==new
# The retained test reference is the prior body, not a new-helper comparison.
ref=proposed[proposed.index('    fn separate_raw_reference('):proposed.index('    // Coordinate-indexed path oracle:')]
ref='\n'.join(line[4:] if line.startswith('    ') else line for line in ref.splitlines())+'\n'
ref=ref.replace('fn separate_raw_reference(', 'pub fn raw(',1)
original=base[base.index('pub fn raw('):base.index(end)]
assert ref==original
result={'kind':'independent text patch application and raw-body restoration; no Rust parse or execution','forward_patch_exact':True,'inverse_patch_exact':True,'raw_arithmetic_body_exact_after_removing_path_collection_and_tuple_projection':True,'prior_raw_test_reference_exact':True,'base_test_declarations':base.count('#[test]'),'proposed_test_declarations':proposed.count('#[test]'),'all_tests_unrun':True}
(p/'derivation-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('Forward/inverse exact; full original raw arithmetic restored exactly; test reference is exact prior raw; all unrun.')
