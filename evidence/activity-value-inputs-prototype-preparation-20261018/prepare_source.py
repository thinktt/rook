"""Bounded literal text transformation only; never parses or executes Rust."""
from pathlib import Path
p=Path(__file__).parent
text=(p/'base-src/activity.rs').read_text()
def replace(old,new,n=1):
 global text
 assert text.count(old)==n,(old[:90],text.count(old),n)
 text=text.replace(old,new)
replace('const ROOK_SEVENTH: [u8; 8] = [40, 43, 45, 47, 47, 45, 43, 40];\n', '''const ROOK_SEVENTH: [u8; 8] = [40, 43, 45, 47, 47, 45, 43, 40];

// Physical-square indexed views: ordinary destinations, then the eligible
// rook's seventh-rank row. Construction is compile-time only.
type DestinationValues = [[u8; 64]; 2];
static DESTINATION_VALUES: [DestinationValues; 2] = oriented_destination_values();

const fn oriented_destination_values() -> [DestinationValues; 2] {
    let mut values = [[[0; 64]; 2]; 2];
    let mut color = 0;
    while color < 2 {
        let mut square = 0;
        while square < 64 {
            let rank = if color == 0 { square / 8 } else { 7 - square / 8 };
            let file = square % 8;
            let ordinary = DESTINATION_VALUE[rank][file];
            values[color][0][square] = ordinary;
            values[color][1][square] = if rank == 6 { ROOK_SEVENTH[file] } else { ordinary };
            square += 1;
        }
        color += 1;
    }
    values
}

#[inline]
fn piece_destination_values<const KIND: usize>(
    position: &Position,
    color: Color,
    values: &'static DestinationValues,
) -> &'static [u8; 64] {
    let seventh = if KIND == PieceKind::Rook.index() {
        let king = position.piece_squares(color.opponent(), PieceKind::King)[0];
        let rank = relative_rank(color, king);
        rank == 7 || (rank == 6 && king.file() >= 6)
    } else {
        false
    };
    &values[usize::from(seventh)]
}
''')
replace('    for color in [Color::White, Color::Black] {\n        accumulate_kind::<1>(', '    for color in [Color::White, Color::Black] {\n        let values = &DESTINATION_VALUES[color.index()];\n        accumulate_kind::<1>(')
replace('            color,\n            &mut marks,', '            color,\n            values,\n            &mut marks,',4)
replace('    color: Color,\n    marks: &mut Marks,\n    endgame: u16,', '    color: Color,\n    values: &\'static DestinationValues,\n    marks: &mut Marks,\n    endgame: u16,')
replace('        let mobility = destinations_kind::<KIND>(position, influence, color, source, marks);', '''        let values = piece_destination_values::<KIND>(position, color, values);
        let mobility = destinations_kind::<KIND>(position, influence, color, source, values, marks);''')
replace('fn destinations_kind<const KIND: usize>(\n    position: &Position,\n    influence: &Influence,\n    color: Color,\n    source: Square,\n    marks: &mut Marks,', 'fn destinations_kind<const KIND: usize>(\n    position: &Position,\n    influence: &Influence,\n    color: Color,\n    source: Square,\n    values: &[u8; 64],\n    marks: &mut Marks,')
replace('            result.total += category\n                * DESTINATION_VALUE[relative_rank(color, target)][target.file() as usize] as i64;', '            result.total += category * values[target.0 as usize] as i64;')
replace('''    let enemy_king = position.piece_squares(color.opponent(), PieceKind::King)[0];
    let king_rank = relative_rank(color, enemy_king);
    let rook_seventh =
        kind == PieceKind::Rook && (king_rank == 7 || (king_rank == 6 && enemy_king.file() >= 6));
''','')
replace('''                let rank = relative_rank(color, target);
                let value = if rook_seventh && rank == 6 {
                    ROOK_SEVENTH[target.file() as usize]
                } else {
                    DESTINATION_VALUE[rank][target.file() as usize]
                };
''','''                let value = values[target.0 as usize];
''')
for kind in range(1,5):
 replace(f'destinations_kind::<{kind}>(position, influence, color, source, marks)', f'destinations_kind::<{kind}>(position, influence, color, source,\n            piece_destination_values::<{kind}>(position, color, &DESTINATION_VALUES[color.index()]), marks)')
replace('''    #[test]
    fn direct_capture_categories_and_queen_exception_use_final_category() {''','''    #[test]
    fn destination_views_preserve_coordinates_and_both_rook_gate_boundaries() {
        for color in [Color::White, Color::Black] {
            let views = &DESTINATION_VALUES[color.index()];
            for rank in 0..8 {
                for file in 0..8 {
                    let physical_rank = if color == Color::White { rank } else { 7 - rank };
                    let square = 8 * physical_rank + file;
                    assert_eq!(views[0][square], DESTINATION_VALUE[rank][file]);
                    let expected = if rank == 6 { ROOK_SEVENTH[file] }
                                   else { DESTINATION_VALUE[rank][file] };
                    assert_eq!(views[1][square], expected);
                }
            }
        }
        // Relative f7/g7 is the file boundary; h8/h6 brackets the rank gate.
        // The second four positions reflect rank and color, retaining files.
        for (placement, color, seventh) in [
            ("8/5k2/8/8/3R4/8/8/K7", Color::White, false),
            ("8/6k1/8/8/3R4/8/8/K7", Color::White, true),
            ("7k/8/8/8/3R4/8/8/K7", Color::White, true),
            ("8/8/7k/8/3R4/8/8/K7", Color::White, false),
            ("k7/8/8/3r4/8/8/5K2/8", Color::Black, false),
            ("k7/8/8/3r4/8/8/6K1/8", Color::Black, true),
            ("k7/8/8/3r4/8/8/8/7K", Color::Black, true),
            ("k7/8/8/3r4/8/7K/8/8", Color::Black, false),
        ] {
            let pos = position(placement);
            let views = &DESTINATION_VALUES[color.index()];
            assert_eq!(piece_destination_values::<3>(&pos, color, views),
                       &views[usize::from(seventh)]);
            assert_eq!(piece_destination_values::<1>(&pos, color, views), &views[0]);
            assert_eq!(piece_destination_values::<2>(&pos, color, views), &views[0]);
            assert_eq!(piece_destination_values::<4>(&pos, color, views), &views[0]);
        }
    }

    #[test]
    fn direct_capture_categories_and_queen_exception_use_final_category() {''')
(p/'proposed-src/activity.rs').write_text(text)
print('Wrote only proposed activity.rs from exact base text; one test declaration added; no Rust parser invoked.')
