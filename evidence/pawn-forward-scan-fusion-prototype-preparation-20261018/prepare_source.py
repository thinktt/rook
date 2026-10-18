"""Literal source derivation only: no Rust parser/compiler or runtime evaluation."""
from pathlib import Path
import difflib,json
p=Path(__file__).parent
base=(p/'base-src/pawn_progress.rs').read_text()
text=base
raw_start=base.index('pub fn raw(')
raw_end=base.index('\n#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub struct Paths',raw_start)
raw_reference=base[raw_start:raw_end].replace('pub fn raw(', 'fn separate_raw_reference(',1)
# Keep this prior independent two-pass raw algorithm test-only, with no new helper calls.
raw_reference='\n'.join('    '+line if line else '' for line in raw_reference.splitlines())+'\n'
def replace(old,new,n=1):
 global text
 assert text.count(old)==n,(old[:90],text.count(old),n)
 text=text.replace(old,new)
replace('pub fn raw(position: &Position, map: &Influence, pawn: Square) -> i32 {','''pub fn raw(position: &Position, map: &Influence, pawn: Square) -> i32 {
    raw_and_path::<false>(position, map, pawn).0
}

// Raw-only callers retain their scalar API; path collection is statically absent.
// Current selected candidates have the pawn's own color, so their two forward
// traversals can share each square's occupancy and normalized influence reads.
#[inline]
fn raw_and_path<const WITH_PATH: bool>(
    position: &Position,
    map: &Influence,
    pawn: Square,
) -> (i32, i32, bool) {''')
replace('''    let mut next = pawn.offset(0, forward);
    while let Some(square) = next {''','''    let mut path = 0;
    let mut protected = true;
    let mut next = pawn.offset(0, forward);
    while let Some(square) = next {''')
replace('''        let own = map.code(side, square);
        let other = map.code(side.opponent(), square);
        if own > other {''','''        let own = map.code(side, square);
        let other = map.code(side.opponent(), square);
        if WITH_PATH {
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || own != 0;
        }
        if own > other {''')
replace('''    if map.code(side, pawn) >> 6 != 0 {
        preliminary * 11 / 8
    } else if map.code(side, pawn.offset(0, forward).unwrap()) >> 6 != 0 {
        preliminary * 10 / 8
    } else {
        preliminary
    }
}''','''    let raw = if map.code(side, pawn) >> 6 != 0 {
        preliminary * 11 / 8
    } else if map.code(side, pawn.offset(0, forward).unwrap()) >> 6 != 0 {
        preliminary * 10 / 8
    } else {
        preliminary
    };
    (raw, path, protected)
}''')
replace('''        let mut path = 0;
        let mut protected = true;
        let mut next = pawn.offset(0, forward);
        while let Some(square) = next {
            let piece = position.board[square.0 as usize];
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || map.code(side, square) != 0;
            next = square.offset(0, forward);
        }
''','''        let (raw, path, protected) = raw_and_path::<true>(position, map, pawn);
''')
replace('        let intermediate = (raw(position, map, pawn) * multiplier + offset) / 64;', '        let intermediate = (raw * multiplier + offset) / 64;')
tests='''
#[cfg(test)]
mod tests {
    use super::*;

REFERENCE
    // Coordinate-indexed path oracle: independent of the fused offset loop.
    fn separate_path_reference(position: &Position, map: &Influence, pawn: Square) -> (i32, bool) {
        let side = position.board[pawn.0 as usize].color();
        let mut path = 0;
        let mut protected = true;
        for rank in 0..8 {
            let ahead = if side == Color::White { rank > pawn.rank() }
                        else { rank < pawn.rank() };
            if !ahead { continue; }
            let square = Square(8 * rank + pawn.file());
            let piece = position.board[square.0 as usize];
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || map.code(side, square) != 0;
        }
        (path, protected)
    }

    #[test]
    fn shared_scan_matches_separate_raw_and_coordinate_path_across_both_colors() {
        // Occupied forward squares never stop either scan, own kings protect
        // without influence, and the nearer knight hides the backward rook.
        // Relative ranks2,4,7 cover the long path and immediate promotion edge.
        for (placement, pawn) in [
            ("3K3k/3r4/3R4/3p4/3P4/8/3R4/8", "d4"),
            ("3K3k/3r4/3R4/3p4/3P4/3N4/3R4/8", "d4"),
            ("8/3r4/8/3p4/3P4/3r4/3R4/3k3K", "d5"),
            ("8/3r4/3n4/3p4/3P4/3r4/3R4/3k3K", "d5"),
            ("K6k/r7/8/R7/8/p7/P7/R7", "a2"),
            ("5r1k/5P2/8/8/8/8/8/5K2", "f7"),
            ("5k2/8/8/8/8/8/5p2/5R1K", "f2"),
        ] {
            let position = Position::from_fen(&format!("{placement} w - - 0 1")).unwrap();
            let pawn = Square::parse(pawn).unwrap();
            let check = |map: &Influence| {
                let raw = separate_raw_reference(&position, map, pawn);
                let (path, protected) = separate_path_reference(&position, map, pawn);
                assert_eq!(raw_and_path::<true>(&position, map, pawn), (raw, path, protected));
                assert_eq!(super::raw(&position, map, pawn), raw);
            };
            check(&Influence::build(&position));
            // Exercise all normalized profile byte values, including carries,
            // equality, both ordinal comparisons and current/front pawn bits.
            // These are internal pure-producer witnesses, not admission claims
            // that every constructed map is placement-derived.
            for value in 0..=255u16 {
                let mut map = Influence { profiles: [[0; 64]; 2] };
                for square in 0..64 {
                    map.profiles[0][square] = (value as u8).wrapping_add((37 * square) as u8);
                    map.profiles[1][square] = (value as u8).wrapping_mul(73)
                        .wrapping_add((13 * square) as u8);
                }
                check(&map);
            }
        }
    }
}
'''.replace('REFERENCE',raw_reference.rstrip())
text+=tests
(p/'proposed-src/pawn_progress.rs').write_text(text)
(p/'proposal.patch').write_text(''.join(difflib.unified_diff(base.splitlines(keepends=True),text.splitlines(keepends=True),fromfile='a/src/pawn_progress.rs',tofile='b/src/pawn_progress.rs')))
(p/'inverse.patch').write_text(''.join(difflib.unified_diff(text.splitlines(keepends=True),base.splitlines(keepends=True),fromfile='a/src/pawn_progress.rs',tofile='b/src/pawn_progress.rs')))
# Literal scope proof, not a Rust parse or semantic execution.
start='fn aligned('
assert base[base.index(start):] == text[text.index(start):text.index('\n#[cfg(test)]\nmod tests {')]
backward_start='    let mut measure = rank as i32 - 4;'
backward_end='    let mut next = pawn.offset(0, forward);'
old=base[base.index(backward_start):base.index(backward_end)]
new=text[text.index(backward_start):text.index('    let mut path = 0;')]
assert old==new
old_candidates=base[base.index('pub fn candidates('):base.index('\nfn aligned(')]
new_candidates=text[text.index('pub fn candidates('):text.index('\nfn aligned(')]
old_loop='''        let mut path = 0;
        let mut protected = true;
        let mut next = pawn.offset(0, forward);
        while let Some(square) = next {
            let piece = position.board[square.0 as usize];
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || map.code(side, square) != 0;
            next = square.offset(0, forward);
        }
'''
assert old_candidates.replace(old_loop,'        let (raw, path, protected) = raw_and_path::<true>(position, map, pawn);\n').replace('raw(position, map, pawn) * multiplier','raw * multiplier')==new_candidates
(p/'scope-proof.json').write_text(json.dumps({'kind':'literal source-scope comparisons; no Rust parsing/compilation/execution','unchanged':['nearest-backward-blocker scan','candidate composition except scan acquisition and raw operand binding','all original source from aligned through weighted, including selector/order/ending/rounding'],'test_reference':'entire prior raw body copied only under cfg(test), with no calls to new producer','test_declarations':{'base':base.count('#[test]'),'proposed':text.count('#[test]'),'all_unrun':True},'public_raw_api':'unchanged scalar signature','private_helper':'const WITH_PATH false/true; tuple(raw,path,protected)','persistent_state_or_relation_charge_added':False},indent=2)+'\n')
print('Source-only fusion, patch/inverse/scope proof written; pawn_progress test declarations0->1; no Rust parser or execution.')
