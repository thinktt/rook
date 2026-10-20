//! EVAL-ACTIVITY: mobility, fresh pressure marks and semantic relation work.
use crate::geometry::{ATTACK_RAYS, DIRECTIONS, KNIGHT, KNIGHT_SOURCES};
use crate::influence::{
    adjusted_relation, profile_sum, relation, Contribution, Influence, Relation,
};
use crate::position::{Phase, Position};
use crate::types::{Color, Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Activity {
    pub pieces: [i32; 2],
    pub pressure: [i32; 2],
    pub weighted: i32,
    pub relation_queries: u64,
}

const DESTINATION_VALUE: [[u8; 8]; 8] = [
    [6, 7, 8, 8, 8, 8, 7, 6],
    [6, 7, 8, 8, 8, 8, 7, 6],
    [7, 10, 12, 13, 13, 12, 10, 7],
    [8, 12, 17, 20, 20, 17, 12, 8],
    [8, 13, 20, 23, 23, 20, 13, 8],
    [8, 13, 20, 23, 23, 20, 13, 8],
    [8, 12, 17, 20, 20, 17, 12, 8],
    [7, 10, 12, 13, 13, 12, 10, 7],
];
const ROOK_SEVENTH: [u8; 8] = [40, 43, 45, 47, 47, 45, 43, 40];

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
const LOW_MOBILITY: [[u8; 8]; 8] = [
    [2, 1, 0, 0, 0, 0, 1, 2],
    [3, 2, 1, 1, 1, 1, 2, 3],
    [4, 4, 3, 3, 3, 3, 4, 4],
    [7, 6, 5, 5, 5, 5, 6, 7],
    [9, 8, 7, 7, 7, 7, 8, 9],
    [9, 9, 8, 8, 8, 8, 9, 9],
    [11, 10, 10, 9, 9, 10, 10, 11],
    [12, 12, 11, 11, 11, 11, 12, 12],
];
const CURVE: [u8; 120] = [
    0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14,
    14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20, 21, 21, 21, 22, 22,
    22, 22, 23, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 25, 26, 26, 26, 26, 27, 27, 27, 27, 28, 28,
    28, 28, 29, 29, 29, 29, 30, 30, 30, 30, 31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 33, 33, 33, 33,
    33, 34, 34, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36,
];
type Marks = [[u8; 64]; 2];

#[derive(Clone, Copy, Debug, Default)]
struct Mobility {
    categories: i64,
    total: i64,
    queries: u64,
}

/// Weights are already owned by color; shelter remains the caller's composition.
pub fn compute(
    position: &Position,
    influence: &Influence,
    material_score: i32,
    weights: [i32; 2],
) -> Activity {
    debug_assert!(weights.iter().all(|w| (0..=10_240).contains(w)));
    let phase = position.phase();
    let mut marks = [[0u8; 64]; 2];
    let mut raw_scores = [0i64; 2];
    let mut relation_queries = 0;
    for color in [Color::White, Color::Black] {
        let values = &DESTINATION_VALUES[color.index()];
        accumulate_kind::<1>(
            position,
            influence,
            color,
            values,
            &mut marks,
            phase.endgame,
            &mut raw_scores[color.index()],
            &mut relation_queries,
        );
        accumulate_kind::<2>(
            position,
            influence,
            color,
            values,
            &mut marks,
            phase.endgame,
            &mut raw_scores[color.index()],
            &mut relation_queries,
        );
        accumulate_kind::<3>(
            position,
            influence,
            color,
            values,
            &mut marks,
            phase.endgame,
            &mut raw_scores[color.index()],
            &mut relation_queries,
        );
        accumulate_kind::<4>(
            position,
            influence,
            color,
            values,
            &mut marks,
            phase.endgame,
            &mut raw_scores[color.index()],
            &mut relation_queries,
        );
    }
    let pieces = raw_scores.map(|score| (276 * score + 128).div_euclid(256) as i32);
    Activity {
        pieces,
        pressure: [
            king_pressure(position, Color::White, &marks),
            king_pressure(position, Color::Black, &marks),
        ],
        weighted: weighted(pieces, material_score, weights, phase),
        relation_queries,
    }
}

#[inline]
fn accumulate_kind<const KIND: usize>(
    position: &Position,
    influence: &Influence,
    color: Color,
    values: &'static DestinationValues,
    marks: &mut Marks,
    endgame: u16,
    score: &mut i64,
    queries: &mut u64,
) {
    let kind = PieceKind::ALL[KIND];
    for &source in position.piece_squares(color, kind) {
        let values = piece_destination_values::<KIND>(position, color, values);
        let mobility = destinations_kind::<KIND>(position, influence, color, source, values, marks);
        let (piece, work) = piece_score_kind::<KIND>(influence, color, source, mobility, endgame);
        *score += piece;
        *queries += work;
    }
}

#[inline]
fn relative_rank(color: Color, square: Square) -> usize {
    if color == Color::White {
        square.rank() as usize
    } else {
        7 - square.rank() as usize
    }
}

#[inline]
fn removal(kind: PieceKind) -> Contribution {
    match kind {
        PieceKind::Knight | PieceKind::Bishop => Contribution::Minor,
        PieceKind::Rook => Contribution::Rook,
        PieceKind::Queen => Contribution::Queen,
        _ => unreachable!("non-activity piece"),
    }
}

#[inline]
fn capture_priority(kind: PieceKind, victim: Piece, category: i64) -> i64 {
    if victim.is_empty() {
        return category;
    }
    match (kind, victim.kind()) {
        (PieceKind::Knight | PieceKind::Bishop, PieceKind::Knight | PieceKind::Bishop) => 2,
        (
            PieceKind::Knight | PieceKind::Bishop,
            PieceKind::Rook | PieceKind::Queen | PieceKind::King,
        ) => 3,
        (PieceKind::Rook, PieceKind::Rook) => 2,
        (PieceKind::Rook, PieceKind::Queen | PieceKind::King) => 3,
        _ => category,
    }
}

fn direct_category(
    influence: &Influence,
    color: Color,
    kind: PieceKind,
    target: Square,
    victim: Piece,
) -> i64 {
    let own = influence.code(color, target);
    let opponent = influence.code(color.opponent(), target);
    let shortcut = if kind == PieceKind::Queen {
        opponent == 0 || (!victim.is_empty() && victim.kind() == PieceKind::Queen)
    } else {
        opponent == 0 && (kind == PieceKind::Knight || victim.is_empty())
    };
    let category = if shortcut {
        2
    } else {
        adjusted_relation(own, opponent, removal(kind), kind) as i64
    };
    capture_priority(kind, victim, category)
}

#[inline]
fn mark(marks: &mut Marks, color: Color, kind: PieceKind, target: Square, category: i64) {
    let bit = 2 * (kind.index() - 1) + usize::from(category >= 2);
    marks[color.index()][target.0 as usize] |= 1 << bit;
}

fn transparent(color: Color, kind: PieceKind, step: (i8, i8), occupant: Piece) -> bool {
    debug_assert!(!occupant.is_empty());
    let friendly = occupant.color() == color;
    match kind {
        PieceKind::Bishop => {
            !friendly || matches!(occupant.kind(), PieceKind::Knight | PieceKind::Rook)
        }
        PieceKind::Rook => {
            if !friendly {
                return occupant.kind() != PieceKind::Pawn;
            }
            let forward = if color == Color::White { 1 } else { -1 };
            occupant.kind() == PieceKind::Rook
                || (step.0 == 0
                    && step.1 == forward
                    && matches!(
                        occupant.kind(),
                        PieceKind::Knight | PieceKind::Bishop | PieceKind::Queen
                    ))
        }
        _ => false,
    }
}

fn destinations_kind<const KIND: usize>(
    position: &Position,
    influence: &Influence,
    color: Color,
    source: Square,
    values: &[u8; 64],
    marks: &mut Marks,
) -> Mobility {
    let kind = PieceKind::ALL[KIND];
    let mut result = Mobility::default();
    if kind == PieceKind::Knight {
        let targets = &KNIGHT_SOURCES[source.0 as usize];
        for &target in &targets.squares[..targets.len as usize] {
            debug_assert!(target < 64);
            let target = Square(target & 63);
            let victim = position.board[target.0 as usize];
            if !victim.is_empty() && victim.color() == color {
                continue;
            }
            let category = direct_category(influence, color, kind, target, victim);
            result.categories += category;
            result.total += category * values[target.0 as usize] as i64;
            mark(marks, color, kind, target, category);
        }
        return result;
    }
    let directions = match kind {
        PieceKind::Bishop => 0..4,
        PieceKind::Rook => 4..8,
        PieceKind::Queen => 0..8,
        _ => unreachable!("non-activity piece"),
    };
    for direction in directions {
        let step = DIRECTIONS[direction];
        let mut additional = false;
        let ray = &ATTACK_RAYS.0[source.0 as usize][direction];
        for &target in &ray.squares[..ray.len as usize] {
            debug_assert!(target < 64);
            let target = Square(target & 63);
            let victim = position.board[target.0 as usize];
            let friendly = !victim.is_empty() && victim.color() == color;
            if !friendly {
                let category = if additional {
                    result.queries += 1;
                    capture_priority(
                        kind,
                        victim,
                        relation(
                            influence.code(color, target),
                            influence.code(color.opponent(), target),
                            kind,
                        ) as i64,
                    )
                } else {
                    let category = direct_category(influence, color, kind, target, victim);
                    result.categories += category;
                    mark(marks, color, kind, target, category);
                    category
                };
                let value = values[target.0 as usize];
                let vertical = if kind == PieceKind::Rook && step.0 == 0 {
                    2
                } else {
                    1
                };
                result.total += category * value as i64 * vertical;
            }
            if !victim.is_empty() {
                if !transparent(color, kind, step, victim) {
                    break;
                }
                additional = true;
            }
        }
    }
    result
}

fn piece_score_kind<const KIND: usize>(
    influence: &Influence,
    color: Color,
    source: Square,
    mobility: Mobility,
    endgame: u16,
) -> (i64, u64) {
    let kind = PieceKind::ALL[KIND];
    let raw_mobility = match kind {
        PieceKind::Knight => (3 * mobility.total) / 4,
        PieceKind::Bishop => mobility.total / 2,
        PieceKind::Rook | PieceKind::Queen => (5 * mobility.total) / 16,
        _ => unreachable!("non-activity piece"),
    };
    let index = ((((512 - endgame as i64) / 2) * raw_mobility + 128) / 256).min(119) as usize;
    let mut score = CURVE[index] as i64;
    let own = influence.code(color, source);
    let opponent = influence.code(color.opponent(), source);
    let attack_count = profile_sum(opponent);
    if profile_sum(own) <= attack_count {
        score -= 5 * attack_count as i64 + 2;
    }
    let rank = relative_rank(color, source);
    let file = source.file() as usize;
    let knight_exempt = kind == PieceKind::Knight
        && own >> 6 != 0
        && (((2..=5).contains(&file) && (2..=5).contains(&rank))
            || ((file == 3 || file == 4) && rank == 6));
    let mut queries = mobility.queries;
    if mobility.categories < 3 && !knight_exempt {
        let mut penalty = LOW_MOBILITY[rank][file] as i64 * (3 - mobility.categories);
        if mobility.categories < 2 {
            queries += 1;
            if relation(own, opponent, kind) == Relation::Unfavorable {
                penalty += 6 + if mobility.categories == 0 { 15 } else { 0 };
            }
        }
        score -= penalty;
    }
    (score, queries)
}

#[cfg(test)]
fn destinations(
    position: &Position,
    influence: &Influence,
    color: Color,
    kind: PieceKind,
    source: Square,
    marks: &mut Marks,
) -> Mobility {
    match kind {
        PieceKind::Knight => destinations_kind::<1>(position, influence, color, source,
            piece_destination_values::<1>(position, color, &DESTINATION_VALUES[color.index()]), marks),
        PieceKind::Bishop => destinations_kind::<2>(position, influence, color, source,
            piece_destination_values::<2>(position, color, &DESTINATION_VALUES[color.index()]), marks),
        PieceKind::Rook => destinations_kind::<3>(position, influence, color, source,
            piece_destination_values::<3>(position, color, &DESTINATION_VALUES[color.index()]), marks),
        PieceKind::Queen => destinations_kind::<4>(position, influence, color, source,
            piece_destination_values::<4>(position, color, &DESTINATION_VALUES[color.index()]), marks),
        _ => unreachable!("non-activity piece"),
    }
}
#[cfg(test)]
fn piece_score(
    influence: &Influence,
    color: Color,
    kind: PieceKind,
    source: Square,
    mobility: Mobility,
    endgame: u16,
) -> (i64, u64) {
    match kind {
        PieceKind::Knight => piece_score_kind::<1>(influence, color, source, mobility, endgame),
        PieceKind::Bishop => piece_score_kind::<2>(influence, color, source, mobility, endgame),
        PieceKind::Rook => piece_score_kind::<3>(influence, color, source, mobility, endgame),
        PieceKind::Queen => piece_score_kind::<4>(influence, color, source, mobility, endgame),
        _ => unreachable!("non-activity piece"),
    }
}

#[inline]
fn pressure_value(mark: u8) -> i32 {
    // Each nibble sums two base-4 digits (at most 6), with no cross-nibble carry.
    let pairs = (mark & 0x33) + ((mark >> 2) & 0x33);
    // The base weights are 8/16; the knight bits need an extra 8 each.
    // The complete sum is at most 14, so every intermediate fits u8.
    let units = (pairs & 15) + (pairs >> 4) + (mark & 1) + ((mark >> 1) & 1);
    i32::from(units) * 8
}

fn king_pressure(position: &Position, defender: Color, marks: &Marks) -> i32 {
    let source = position.piece_squares(defender, PieceKind::King)[0];
    let attacker = defender.opponent();
    let counts = position.counts[attacker.index()];
    let mut pressure = 0;
    for (directions, mask, admitted) in [
        (
            &DIRECTIONS[4..],
            0xf0u8,
            counts[PieceKind::Rook.index()] != 0 || counts[PieceKind::Queen.index()] != 0,
        ),
        (
            &DIRECTIONS[..4],
            0xccu8,
            counts[PieceKind::Bishop.index()] != 0 || counts[PieceKind::Queen.index()] != 0,
        ),
    ] {
        if !admitted {
            continue;
        }
        for &step in directions {
            let mut cursor = source;
            while let Some(target) = cursor.offset(step.0, step.1) {
                let piece = position.board[target.0 as usize];
                if !piece.is_empty() && piece.color() == attacker {
                    break;
                }
                pressure += pressure_value(marks[attacker.index()][target.0 as usize] & mask);
                if !piece.is_empty() {
                    break;
                }
                cursor = target;
            }
        }
    }
    if counts[PieceKind::Knight.index()] != 0 {
        for step in KNIGHT {
            if let Some(target) = source.offset(step.0, step.1) {
                let piece = position.board[target.0 as usize];
                if piece.is_empty() || piece.color() == defender {
                    pressure += pressure_value(marks[attacker.index()][target.0 as usize] & 3);
                }
            }
        }
    }
    (pressure - 12).max(0)
}

fn weighted(pieces: [i32; 2], material_score: i32, weights: [i32; 2], phase: Phase) -> i32 {
    let material = material_score.clamp(-256, 256) as i64;
    let white = ((1024 - material) * weights[0] as i64 + 512).div_euclid(1024);
    let black = ((1024 + material) * weights[1] as i64 + 512).div_euclid(1024);
    let difference = (white * pieces[0] as i64 - black * pieces[1] as i64 + 512).div_euclid(1024);
    ((9 * difference * (phase.opening as i64 + 2 * phase.middlegame as i64 + phase.endgame as i64)
        + 2048)
        .div_euclid(4096)) as i32
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sq(text: &str) -> Square {
        Square::parse(text).unwrap()
    }
    fn position(placement: &str) -> Position {
        Position::from_fen(&format!("{placement} w - - 0 1")).unwrap()
    }
    fn empty_influence() -> Influence {
        Influence {
            profiles: [[0; 64]; 2],
        }
    }

    #[test]
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
    fn direct_capture_categories_and_queen_exception_use_final_category() {
        let mut influence = empty_influence();
        let target = sq("d4");
        influence.profiles[1][target.0 as usize] = Contribution::Pawn as u8;
        for kind in [PieceKind::Knight, PieceKind::Bishop] {
            assert_eq!(
                direct_category(
                    &influence,
                    Color::White,
                    kind,
                    target,
                    Piece::new(Color::Black, PieceKind::Pawn)
                ),
                0
            );
            assert_eq!(
                direct_category(
                    &influence,
                    Color::White,
                    kind,
                    target,
                    Piece::new(Color::Black, PieceKind::Bishop)
                ),
                2
            );
            assert_eq!(
                direct_category(
                    &influence,
                    Color::White,
                    kind,
                    target,
                    Piece::new(Color::Black, PieceKind::King)
                ),
                3
            );
        }
        assert_eq!(
            direct_category(
                &influence,
                Color::White,
                PieceKind::Rook,
                target,
                Piece::new(Color::Black, PieceKind::Rook)
            ),
            2
        );
        assert_eq!(
            direct_category(
                &influence,
                Color::White,
                PieceKind::Rook,
                target,
                Piece::new(Color::Black, PieceKind::Queen)
            ),
            3
        );
        assert_eq!(
            direct_category(
                &influence,
                Color::White,
                PieceKind::Queen,
                target,
                Piece::new(Color::Black, PieceKind::Queen)
            ),
            2
        );
        assert_eq!(
            direct_category(
                &influence,
                Color::White,
                PieceKind::Queen,
                target,
                Piece::new(Color::Black, PieceKind::Rook)
            ),
            0
        );
    }

    #[test]
    fn bishop_additional_rays_charge_without_direct_categories_or_marks() {
        let influence = empty_influence();
        for (blocker, expected_direct, expected_queries, marked) in
            [('N', 4, 4, false), ('p', 6, 4, true), ('B', 4, 0, false)]
        {
            let pos = position(&format!("7k/8/8/8/8/8/3{blocker}4/K1B5"));
            let mut marks = [[0; 64]; 2];
            let mobility = destinations(
                &pos,
                &influence,
                Color::White,
                PieceKind::Bishop,
                sq("c1"),
                &mut marks,
            );
            assert_eq!(mobility.categories, expected_direct);
            assert_eq!(mobility.queries, expected_queries);
            assert_eq!(marks[0][sq("d2").0 as usize] != 0, marked);
            assert_eq!(marks[0][sq("e3").0 as usize], 0);
        }
    }

    #[test]
    fn rook_forward_transparency_seventh_bonus_and_vertical_value_do_not_double_work() {
        let pos = position("7k/8/8/3B4/2RRQ3/3B4/8/K7");
        let influence = empty_influence();
        let mut marks = [[0; 64]; 2];
        let mobility = destinations(
            &pos,
            &influence,
            Color::White,
            PieceKind::Rook,
            sq("d4"),
            &mut marks,
        );
        assert_eq!(mobility.categories, 0);
        assert_eq!(mobility.queries, 5); // d6,d7,d8 and b4,a4, exactly once each.
        assert_eq!(mobility.total, 372); // Vertical values doubled; d7 uses the seventh-rank row.
        assert!(marks[0].iter().all(|&mark| mark == 0));
        let (_, queries) = piece_score(
            &influence,
            Color::White,
            PieceKind::Rook,
            sq("d4"),
            mobility,
            pos.phase().endgame,
        );
        assert_eq!(queries, 6); // The additional low-mobility source query is separate.
        let blocked = position("7k/8/8/3p4/3R4/8/8/K7");
        let mut marks = [[0; 64]; 2];
        let mobility = destinations(
            &blocked,
            &influence,
            Color::White,
            PieceKind::Rook,
            sq("d4"),
            &mut marks,
        );
        assert_eq!(mobility.queries, 0); // Opposing pawn ends its ray.
        assert_ne!(marks[0][sq("d5").0 as usize], 0);
        assert_eq!(marks[0][sq("d6").0 as usize], 0);
    }

    #[test]
    fn low_mobility_exemption_uses_normalized_pawn_and_source_sums_are_uncapped() {
        let mut influence = empty_influence();
        let source = sq("c4");
        influence.profiles[0][source.0 as usize] = 64;
        influence.profiles[1][source.0 as usize] = 64;
        let (exempt, queries) = piece_score(
            &influence,
            Color::White,
            PieceKind::Knight,
            source,
            Mobility::default(),
            0,
        );
        assert_eq!((exempt, queries), (-7, 0));
        influence.profiles[0][source.0 as usize] = 16;
        let (ordinary, queries) = piece_score(
            &influence,
            Color::White,
            PieceKind::Knight,
            source,
            Mobility::default(),
            0,
        );
        assert_eq!((ordinary, queries), (-43, 1));
        influence.profiles[0][source.0 as usize] = 120; // Six normalized contributions.
        influence.profiles[1][source.0 as usize] = 104; // Five, though both multiplicities cap at four.
        let mobility = Mobility {
            categories: 3,
            total: 0,
            queries: 0,
        };
        assert_eq!(
            piece_score(
                &influence,
                Color::White,
                PieceKind::Bishop,
                source,
                mobility,
                0
            ),
            (0, 0)
        );
    }

    #[test]
    fn paired_pressure_digits_match_independent_bit_weights_for_all_marks() {
        for mark in 0..=u8::MAX {
            let expected = i32::from(mark & 1 != 0) * 16
                + i32::from(mark & 2 != 0) * 24
                + (mark & 0x54).count_ones() as i32 * 8
                + (mark & 0xa8).count_ones() as i32 * 16;
            assert_eq!(pressure_value(mark), expected, "mark {mark:#04x}");
        }
    }

    #[test]
    fn pressure_marks_are_presence_bits_and_own_blockers_are_included() {
        let mut marks = [[0; 64]; 2];
        let target = sq("d5");
        mark(&mut marks, Color::Black, PieceKind::Knight, target, 0);
        mark(&mut marks, Color::Black, PieceKind::Knight, target, 2);
        mark(&mut marks, Color::Black, PieceKind::Knight, target, 3);
        assert_eq!(marks[1][target.0 as usize], 3);
        assert_eq!(pressure_value(marks[1][target.0 as usize]), 40);
        let pos = position("7r/8/3P4/8/3Kp3/8/8/k7");
        marks = [[0; 64]; 2];
        mark(&mut marks, Color::Black, PieceKind::Rook, sq("d5"), 0);
        mark(&mut marks, Color::Black, PieceKind::Rook, sq("d6"), 2);
        mark(&mut marks, Color::Black, PieceKind::Rook, sq("d7"), 2);
        mark(&mut marks, Color::Black, PieceKind::Rook, sq("e4"), 2);
        assert_eq!(king_pressure(&pos, Color::White, &marks), 12); // 8+16-12; d7 and e4 excluded.
    }

    #[test]
    fn signed_rounds_material_clamp_and_large_owned_weights() {
        assert_eq!((276i64 * -1 + 128).div_euclid(256), -1);
        let phase = Phase {
            opening: 0,
            middlegame: 256,
            endgame: 0,
        };
        assert_eq!(weighted([-1, 0], 0, [1024, 1024], phase), -1);
        assert_eq!(
            weighted([17, -39], 100_000, [10_240, 9173], phase),
            weighted([17, -39], 256, [10_240, 9173], phase)
        );
        assert_eq!(
            weighted([17, -39], -100_000, [10_240, 9173], phase),
            weighted([17, -39], -256, [10_240, 9173], phase)
        );
    }

    #[test]
    fn complete_activity_is_fresh_and_color_reflects_components() {
        for placement in [
            "r3k2r/pp1n1p2/2b1q1p1/3pP3/2BN1P2/1Q3N2/PP4PP/R3K2R",
            "7k/8/3n4/2B5/3R4/8/8/K7",
            "7k/8/8/8/8/8/8/K7",
        ] {
            let pos = position(placement);
            let influence = Influence::build(&pos);
            let first = compute(&pos, &influence, 217, [10_240, 8192]);
            assert_eq!(first, compute(&pos, &influence, 217, [10_240, 8192]));
            let mut mirror = pos;
            mirror.board = [Piece::EMPTY; 64];
            for (index, &piece) in pos.board.iter().enumerate() {
                if !piece.is_empty() {
                    mirror.board[index ^ 56] = Piece::new(piece.color().opponent(), piece.kind());
                }
            }
            mirror.counts.swap(0, 1);
            mirror.squares.swap(0, 1);
            for side in 0..2 {
                for square in &mut mirror.squares[side] {
                    if square.0 < 64 {
                        square.0 ^= 56;
                    }
                }
            }
            mirror.side = pos.side.opponent();
            mirror.rights = (pos.rights >> 2) | ((pos.rights & 3) << 2);
            mirror.ep = if pos.ep < 64 { pos.ep ^ 56 } else { pos.ep };
            mirror.recompute_derived();
            mirror.validate().unwrap();
            let reflected = compute(&mirror, &Influence::build(&mirror), -217, [8192, 10_240]);
            assert_eq!(first.pieces, [reflected.pieces[1], reflected.pieces[0]]);
            assert_eq!(
                first.pressure,
                [reflected.pressure[1], reflected.pressure[0]]
            );
            assert_eq!(first.relation_queries, reflected.relation_queries);
        }
    }
}
