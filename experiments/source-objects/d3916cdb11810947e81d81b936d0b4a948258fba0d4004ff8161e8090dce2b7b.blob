//! Current consumers of retained pawn structure, before progress and weighting.

use crate::influence::{profile_sum, relation, Influence, Relation};
use crate::pawn_structure::{PawnStructure, Weakness};
use crate::position::Position;
use crate::types::{Color, Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct PawnTerms {
    pub structure: [i32; 2],
    pub raw_piece: [i32; 2],
    pub piece: [i32; 2],
    pub relation_queries: u64,
}

const ADVANCE: [[i32; 8]; 6] = [
    [5, 10, 20, 25, 25, 20, 10, 5],
    [6, 12, 20, 25, 25, 20, 12, 6],
    [4, 8, 14, 16, 16, 14, 8, 4],
    [3, 4, 5, 6, 6, 5, 4, 3],
    [0; 8],
    [0; 8],
];
const ISOLATED: [[i32; 8]; 6] = [
    [5, 10, 10, 4, 4, 7, 7, 3],
    [5, 10, 10, 4, 4, 7, 7, 3],
    [5, 10, 10, 4, 4, 7, 7, 3],
    [5, 10, 10, 4, 4, 7, 7, 3],
    [2, 5, 5, 2, 2, 3, 3, 1],
    [0; 8],
];
const EXPOSED: [[i32; 8]; 6] = [
    [3, 3, 4, 6, 6, 4, 3, 3],
    [3, 3, 4, 6, 6, 4, 3, 3],
    [2, 2, 3, 4, 4, 3, 2, 2],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [0; 8],
    [0; 8],
];
const KNIGHT: [[i32; 8]; 8] = [
    [0; 8],
    [0; 8],
    [0, 0, 2, 4, 4, 2, 0, 0],
    [0, 0, 6, 10, 10, 6, 0, 0],
    [0, 0, 10, 16, 16, 10, 0, 0],
    [0, 0, 12, 20, 20, 12, 0, 0],
    [0, 0, 0, 12, 12, 0, 0, 0],
    [0; 8],
];
const SLIDER: [[i32; 8]; 8] = [
    [0; 8],
    [0; 8],
    [0; 8],
    [0, 0, 5, 9, 9, 5, 0, 0],
    [0, 7, 10, 15, 15, 10, 7, 0],
    [0, 9, 13, 15, 15, 13, 9, 0],
    [0, 4, 6, 9, 9, 6, 4, 0],
    [0; 8],
];
const OCCUPIED: [[i32; 4]; 4] = [[5, 10, 5, 5], [1, 5, 5, 5], [1, 2, 3, 2], [1, 5, 5, 5]];

#[inline]
fn normalized_rank(square: Square, side: Color) -> usize {
    if side == Color::White {
        square.rank() as usize + 1
    } else {
        8 - square.rank() as usize
    }
}

#[inline]
fn advance(square: Square, side: Color) -> Square {
    square
        .offset(0, if side == Color::White { 1 } else { -1 })
        .expect("pawn on a promotion rank")
}

#[inline]
fn influence_class(code: u8) -> usize {
    if code >= 16 {
        0
    } else if code & 12 != 0 {
        1
    } else if code & 2 != 0 {
        2
    } else {
        3
    }
}

fn advance_pressure(
    position: &Position,
    influence: &Influence,
    side: Color,
    square: Square,
) -> i32 {
    let target = advance(square, side);
    let own = influence.code(side, target);
    let opponent = influence.code(side.opponent(), target);
    let occupant = position.board[target.0 as usize];
    let pressure = (profile_sum(opponent) as i32 - profile_sum(own) as i32
        + i32::from(opponent >> 6 != 0)
        + i32::from(!occupant.is_empty() && occupant.color() != side))
    .clamp(0, 4);
    ADVANCE[normalized_rank(square, side) - 2][square.file() as usize] * pressure / 4
}

fn rook_line(position: &Position, influence: &Influence, side: Color, square: Square) -> i32 {
    let mut best = 0;
    for (df, dr) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
        let mut empty = 0;
        let mut found = false;
        let mut next = square.offset(df, dr);
        while let Some(target) = next {
            let piece = position.board[target.0 as usize];
            if piece == Piece::new(side, PieceKind::Rook) {
                found = true;
            } else if piece.is_empty() {
                if influence.code(side.opponent(), target) >> 6 == 0 {
                    empty += 1;
                }
            } else {
                break;
            }
            next = target.offset(df, dr);
        }
        if found {
            let value = match empty {
                0 => 20,
                1 => 10,
                _ => 5,
            };
            best = best.max(if df == 0 { value * 2 } else { value });
        }
    }
    best
}

fn occupied_pressure(
    position: &Position,
    influence: &Influence,
    side: Color,
    square: Square,
) -> i32 {
    let own = influence.code(side, square);
    let opponent = influence.code(side.opponent(), square);
    if profile_sum(opponent) == 0 || profile_sum(own) > profile_sum(opponent) {
        return 0;
    }
    let own_class = influence_class(own);
    let base = OCCUPIED[influence_class(opponent)][own_class];
    base + if own_class == 1 {
        rook_line(position, influence, side, square)
    } else {
        0
    }
}

fn structural_penalty(
    position: &Position,
    influence: &Influence,
    side: Color,
    square: Square,
    weakness: Weakness,
) -> (i32, u64) {
    match weakness {
        Weakness::None => (0, 0),
        Weakness::Isolated => {
            let mut penalty = ISOLATED[normalized_rank(square, side) - 2][square.file() as usize]
                + occupied_pressure(position, influence, side, square);
            if position.board[advance(square, side).0 as usize]
                != Piece::new(side.opponent(), PieceKind::Pawn)
            {
                penalty += 5 * advance_pressure(position, influence, side, square) / 8;
            }
            (penalty, 0)
        }
        Weakness::BlockedBackward => (occupied_pressure(position, influence, side, square), 0),
        Weakness::ExposedBackward => (
            occupied_pressure(position, influence, side, square)
                + advance_pressure(position, influence, side, square)
                + EXPOSED[normalized_rank(square, side) - 2][square.file() as usize],
            0,
        ),
        Weakness::ExposedLevel => {
            let target = advance(square, side);
            if !position.board[target.0 as usize].is_empty() {
                return (occupied_pressure(position, influence, side, square) + 4, 0);
            }
            let outcome = relation(
                influence.code(side, target),
                influence.code(side.opponent(), target),
                PieceKind::Pawn,
            );
            if outcome == Relation::Unfavorable {
                (occupied_pressure(position, influence, side, square) + 4, 1)
            } else {
                (0, 1)
            }
        }
    }
}

#[inline]
fn ahead_behind(square: Square, side: Color) -> (u8, u8) {
    let above = (0xffu16 << (square.rank() + 1)) as u8;
    let below = ((1u16 << square.rank()) - 1) as u8;
    if side == Color::White {
        (above, below)
    } else {
        (below, above)
    }
}

/// Raw, ungated piece activity and its own selected rook-relation queries.
/// Ordinary composition must apply the phase gate before invoking this seam.
pub fn raw_piece_terms(
    position: &Position,
    influence: &Influence,
    retained: &PawnStructure,
) -> ([i32; 2], u64) {
    let mut files = [[0u8; 8]; 2];
    // Intentionally do not filter membership here: piece activity consumes the
    // retained pawn arrangement even after a full-identity collision.
    for side in [Color::White, Color::Black] {
        for pawn in retained.pawn_slice(side) {
            files[side.index()][pawn.square.file() as usize] |= 1 << pawn.square.rank();
        }
    }
    let mut scores = [0; 2];
    let mut queries = 0;
    for side in [Color::White, Color::Black] {
        let opponent = side.opponent();
        let own_files = &files[side.index()];
        let opponent_files = &files[opponent.index()];
        for kind in [PieceKind::Knight, PieceKind::Bishop, PieceKind::Rook] {
            for &square in position.piece_squares(side, kind) {
                let value = if kind == PieceKind::Knight {
                    KNIGHT[normalized_rank(square, side) - 1][square.file() as usize]
                } else {
                    SLIDER[normalized_rank(square, side) - 1][square.file() as usize]
                };
                if value == 0 {
                    continue;
                }
                let (ahead, behind) = ahead_behind(square, side);
                let mut eligible = true;
                let mut pawn_behind = false;
                let file = square.file() as usize;
                for adjacent in [file.checked_sub(1), (file + 1 < 8).then_some(file + 1)]
                    .into_iter()
                    .flatten()
                {
                    let enemy_ahead = opponent_files[adjacent] & ahead != 0;
                    if enemy_ahead
                        && (kind != PieceKind::Knight || own_files[adjacent] & ahead == 0)
                    {
                        eligible = false;
                        break;
                    }
                    pawn_behind |= own_files[adjacent] & behind != 0;
                }
                if !eligible {
                    continue;
                }
                let own = influence.code(side, square);
                if kind == PieceKind::Knight {
                    let mut factor = if pawn_behind { 4 } else { 2 };
                    factor += profile_sum(own) as i32;
                    factor += i32::from(own & 14 != 0);
                    if square
                        .offset(0, if side == Color::White { 1 } else { -1 })
                        .is_some_and(|target| {
                            position.board[target.0 as usize]
                                == Piece::new(opponent, PieceKind::Pawn)
                        })
                    {
                        factor += 3;
                    }
                    let counts = &position.counts[opponent.index()];
                    if own >> 6 != 0 && counts[PieceKind::Knight.index()] == 0 {
                        let bishops = position.piece_squares(opponent, PieceKind::Bishop);
                        if bishops.is_empty()
                            || (bishops.len() == 1
                                && (bishops[0].file() + bishops[0].rank()) % 2
                                    != (square.file() + square.rank()) % 2)
                        {
                            factor += 2;
                        }
                    }
                    scores[side.index()] += factor * value / 4;
                } else if kind == PieceKind::Bishop {
                    scores[side.index()] += value;
                } else {
                    queries += 1;
                    let outcome = relation(own, influence.code(opponent, square), PieceKind::Rook);
                    if outcome == Relation::Favorable
                        || (outcome == Relation::Contested && own & 12 != 0)
                    {
                        scores[side.index()] += value;
                    }
                }
            }
        }
    }
    (scores, queries)
}

/// Current selected penalties, retaining cached base scores even when some
/// descriptors no longer name a same-color pawn. Includes only this work's R.
pub fn structure_terms(
    position: &Position,
    influence: &Influence,
    retained: &PawnStructure,
) -> ([i32; 2], u64) {
    let mut scores = retained.base_score;
    let mut relation_queries = 0;
    for side in [Color::White, Color::Black] {
        for descriptor in retained.pawn_slice(side) {
            if position.board[descriptor.square.0 as usize] != Piece::new(side, PieceKind::Pawn) {
                continue;
            }
            let (penalty, queries) = structural_penalty(
                position,
                influence,
                side,
                descriptor.square,
                descriptor.weakness,
            );
            scores[side.index()] -= penalty;
            relation_queries += queries;
        }
    }
    (scores, relation_queries)
}

pub fn compute(position: &Position, influence: &Influence, retained: &PawnStructure) -> PawnTerms {
    let (structure, relation_queries) = structure_terms(position, influence, retained);
    let mut result = PawnTerms {
        structure,
        relation_queries,
        ..PawnTerms::default()
    };
    let phase = position.phase();
    let weight = (phase.opening + phase.middlegame) as i32;
    if weight > 16 {
        let (raw, queries) = raw_piece_terms(position, influence, retained);
        result.raw_piece = raw;
        result.relation_queries += queries;
        for side in [Color::White, Color::Black] {
            result.piece[side.index()] = (raw[side.index()] * weight + 128) / 256;
        }
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::pawn_structure::{fresh, PawnCache};

    fn position(placement: &str) -> Position {
        Position::from_fen(&format!("{placement} w - - 0 1")).unwrap()
    }

    fn fresh_terms(placement: &str) -> PawnTerms {
        let p = position(placement);
        let influence = Influence::build(&p);
        compute(&p, &influence, &fresh(&p, &influence, [1024; 2]))
    }

    #[test]
    fn isolated_advance_rounding_is_staged_and_backward_rows_do_not_stack() {
        let p = position("2r4k/8/8/8/2P5/8/8/K7");
        let influence = Influence::build(&p);
        let square = Square::parse("c4").unwrap();
        assert_eq!(advance_pressure(&p, &influence, Color::White, square), 3);
        assert_eq!(occupied_pressure(&p, &influence, Color::White, square), 5);
        assert_eq!(fresh_terms("2r4k/8/8/8/2P5/8/8/K7").structure[0], -19);
        assert_eq!(fresh_terms("7k/8/8/5p2/3P4/4P3/8/K7").structure[0], -18);
        assert_eq!(fresh_terms("7k/8/8/3p4/3Pp3/4P3/8/K7").structure[0], 0);
    }

    #[test]
    fn isolated_files_are_asymmetric_and_black_structure_is_not_negated() {
        for (placement, side, expected) in [
            ("7k/8/8/8/8/8/P7/K7", Color::White, -8),
            ("7k/8/8/8/8/8/7P/K7", Color::White, -6),
            ("7k/p7/8/8/8/8/8/K7", Color::Black, -8),
            ("7k/7p/8/8/8/8/8/K7", Color::Black, -6),
        ] {
            assert_eq!(
                fresh_terms(placement).structure[side.index()],
                expected,
                "{placement}"
            );
        }
    }

    #[test]
    fn exposed_level_queries_count_even_when_the_relation_suppresses_penalty() {
        let original = position("7k/8/8/5p2/8/3PP3/8/K7");
        let influence = Influence::build(&original);
        let retained = fresh(&original, &influence, [1024; 2]);
        let contested = compute(&original, &influence, &retained);
        assert_eq!((contested.structure[0], contested.relation_queries), (4, 1));
        let missing_support = position("7k/8/8/5p2/8/4P3/8/K7");
        let unfavorable = compute(
            &missing_support,
            &Influence::build(&missing_support),
            &retained,
        );
        assert_eq!(
            (unfavorable.structure[0], unfavorable.relation_queries),
            (0, 1)
        );
        let occupied = position("7k/8/8/5p2/4N3/3PP3/8/K7");
        let blocked = compute(&occupied, &Influence::build(&occupied), &retained);
        assert_eq!((blocked.structure[0], blocked.relation_queries), (0, 0));
        let missing_enemy = position("7k/8/8/8/8/3PP3/8/K7");
        let favorable = compute(&missing_enemy, &Influence::build(&missing_enemy), &retained);
        assert_eq!((favorable.structure[0], favorable.relation_queries), (4, 1));
    }

    #[test]
    fn rook_lines_use_maximum_and_only_augment_rook_class_pressure() {
        let p = position("7k/8/8/8/3P3r/3R4/3N4/K7");
        let influence = Influence::build(&p);
        let pawn = Square::parse("d4").unwrap();
        assert_eq!(rook_line(&p, &influence, Color::White, pawn), 40);
        assert_eq!(occupied_pressure(&p, &influence, Color::White, pawn), 45);
        let priority = position("3r3k/8/8/8/3P3r/2PR4/3N4/K7");
        let ip = Influence::build(&priority);
        assert_eq!(rook_line(&priority, &ip, Color::White, pawn), 40);
        assert_eq!(occupied_pressure(&priority, &ip, Color::White, pawn), 1);
        // Empty squares before the first rook count; a queen terminates the ray.
        let long = position("7k/8/8/8/3P4/7r/8/K2R4");
        assert_eq!(
            rook_line(&long, &Influence::build(&long), Color::White, pawn),
            10
        );
        let queen = position("7k/8/8/8/3P4/3Q4/8/K2R4");
        assert_eq!(
            rook_line(&queen, &Influence::build(&queen), Color::White, pawn),
            0
        );
    }

    #[test]
    fn retained_collision_keeps_base_and_skips_missing_current_descriptors() {
        let a = position("7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7");
        let b = position("7k/8/2p4P/2p5/7P/1p6/p5PP/K7");
        let mut cache = PawnCache::new();
        let retained = cache.select(&a, &Influence::build(&a));
        let selected = cache.select(&b, &Influence::build(&b));
        assert!(selected.reused);
        assert_eq!(a.pawn, b.pawn);
        let terms = compute(&b, &Influence::build(&b), &selected.structure);
        assert_eq!(terms.structure, retained.structure.base_score);
        assert_eq!(
            (terms.raw_piece, terms.piece, terms.relation_queries),
            ([0; 2], [0; 2], 0)
        );
    }

    #[test]
    fn piece_eligibility_uses_retained_geometry_not_current_pawn_membership() {
        let old = position("7k/8/p7/8/8/8/8/K7");
        let retained = fresh(&old, &Influence::build(&old), [1024; 2]);
        let current = position("1r5q/8/3p4/4B3/8/8/8/NK4k1");
        let influence = Influence::build(&current);
        let fresh_current = fresh(&current, &influence, [1024; 2]);
        assert_eq!(raw_piece_terms(&current, &influence, &retained).0[0], 15);
        assert_eq!(
            raw_piece_terms(&current, &influence, &fresh_current).0[0],
            0
        );
        let terms = compute(&current, &influence, &retained);
        assert_eq!(terms.structure[1], retained.base_score[1]);
        assert_eq!(terms.raw_piece[0], 15);
    }

    #[test]
    fn knight_file_guards_factors_and_current_opposing_minor_material() {
        let p = position("7k/8/3p1P2/4N3/8/8/8/K7");
        let i = Influence::build(&p);
        assert_eq!(raw_piece_terms(&p, &i, &fresh(&p, &i, [1024; 2])).0[0], 0);
        for (back_rank, expected) in [
            ("7k", 48),
            ("6bk", 48),
            ("5b1k", 40),
            ("2b3bk", 40),
            ("n6k", 40),
        ] {
            let p = position(&format!("{back_rank}/8/4p3/4N3/3P4/8/8/K3R3"));
            let i = Influence::build(&p);
            assert_eq!(
                raw_piece_terms(&p, &i, &fresh(&p, &i, [1024; 2])).0[0],
                expected,
                "{back_rank}"
            );
        }
        let before = position("7k/8/4p3/4N3/3P4/8/8/K3R3");
        let retained = fresh(&before, &Influence::build(&before), [1024; 2]);
        let after = position("7k/8/8/4N3/3P4/8/8/K3R3");
        assert_eq!(
            raw_piece_terms(&after, &Influence::build(&after), &retained).0[0],
            36
        );
        let rounded = position("7k/8/8/8/8/2N2N2/1P4P1/K7");
        let i = Influence::build(&rounded);
        assert_eq!(
            raw_piece_terms(&rounded, &i, &fresh(&rounded, &i, [1024; 2])).0[0],
            6
        );
    }

    #[test]
    fn rook_contested_support_requires_normalized_rook_category_and_counts_queries() {
        for (support, expected) in [("3R4", 15), ("3Q4", 0)] {
            let p = position(&format!("7k/8/8/3R3r/8/8/{support}/K7"));
            let i = Influence::build(&p);
            let retained = fresh(&p, &i, [1024; 2]);
            assert_eq!(raw_piece_terms(&p, &i, &retained), ([expected, 0], 1));
        }
    }

    #[test]
    fn current_phase_gate_suppresses_raw_work_and_rounds_after_color_sum() {
        let gated = position("1r5q/8/8/3R4/8/8/P6P/K6k");
        let pg = gated.phase();
        assert_eq!(pg.opening + pg.middlegame, 16);
        let i = Influence::build(&gated);
        let retained = fresh(&gated, &i, [1024; 2]);
        assert_eq!(raw_piece_terms(&gated, &i, &retained), ([15, 0], 1));
        let skipped = compute(&gated, &i, &retained);
        assert_eq!(
            (skipped.raw_piece, skipped.piece, skipped.relation_queries),
            ([0; 2], [0; 2], 0)
        );
        let active = position("1r5q/8/8/3R4/8/8/P3P2P/K6k");
        let phase = active.phase();
        assert_eq!(phase.opening + phase.middlegame, 24);
        let terms = fresh_terms("1r5q/8/8/3R4/8/8/P3P2P/K6k");
        assert_eq!(
            (terms.raw_piece, terms.piece, terms.relation_queries),
            ([15, 0], [1, 0], 1)
        );
        let summed = fresh_terms("1r5q/8/8/8/2B2B2/8/P7/K6k");
        assert_eq!((summed.raw_piece[0], summed.piece[0]), (10, 1));
    }
}
