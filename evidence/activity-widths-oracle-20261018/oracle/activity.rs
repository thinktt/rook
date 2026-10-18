//! EVAL-ACTIVITY: mobility, fresh pressure marks and semantic relation work.
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

const DIAGONAL: [(i8, i8); 4] = [(1, 1), (-1, -1), (-1, 1), (1, -1)];
const ORTHOGONAL: [(i8, i8); 4] = [(0, 1), (0, -1), (1, 0), (-1, 0)];
const KNIGHT: [(i8, i8); 8] = [
    (1, 2),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (2, 1),
    (-2, -1),
    (-2, 1),
    (2, -1),
];
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
        for kind in [
            PieceKind::Knight,
            PieceKind::Bishop,
            PieceKind::Rook,
            PieceKind::Queen,
        ] {
            for &source in position.piece_squares(color, kind) {
                let mobility = destinations(position, influence, color, kind, source, &mut marks);
                let (score, queries) =
                    piece_score(influence, color, kind, source, mobility, phase.endgame);
                raw_scores[color.index()] += score;
                relation_queries += queries;
            }
        }
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

fn destinations(
    position: &Position,
    influence: &Influence,
    color: Color,
    kind: PieceKind,
    source: Square,
    marks: &mut Marks,
) -> Mobility {
    let mut result = Mobility::default();
    if kind == PieceKind::Knight {
        for step in KNIGHT {
            let Some(target) = source.offset(step.0, step.1) else {
                continue;
            };
            let victim = position.board[target.0 as usize];
            if !victim.is_empty() && victim.color() == color {
                continue;
            }
            let category = direct_category(influence, color, kind, target, victim);
            result.categories += category;
            result.total += category
                * DESTINATION_VALUE[relative_rank(color, target)][target.file() as usize] as i64;
            mark(marks, color, kind, target, category);
        }
        return result;
    }
    let enemy_king = position.piece_squares(color.opponent(), PieceKind::King)[0];
    let king_rank = relative_rank(color, enemy_king);
    let rook_seventh =
        kind == PieceKind::Rook && (king_rank == 7 || (king_rank == 6 && enemy_king.file() >= 6));
    let directions: &[(i8, i8)] = match kind {
        PieceKind::Bishop => &DIAGONAL,
        PieceKind::Rook => &ORTHOGONAL,
        PieceKind::Queen => &[
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
        ],
        _ => unreachable!("non-activity piece"),
    };
    for &step in directions {
        let mut cursor = source;
        let mut additional = false;
        while let Some(target) = cursor.offset(step.0, step.1) {
            cursor = target;
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
                let rank = relative_rank(color, target);
                let value = if rook_seventh && rank == 6 {
                    ROOK_SEVENTH[target.file() as usize]
                } else {
                    DESTINATION_VALUE[rank][target.file() as usize]
                };
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

fn piece_score(
    influence: &Influence,
    color: Color,
    kind: PieceKind,
    source: Square,
    mobility: Mobility,
    endgame: u16,
) -> (i64, u64) {
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

#[inline]
fn pressure_value(mark: u8) -> i32 {
    i32::from(mark & 1 != 0) * 16
        + i32::from(mark & 2 != 0) * 24
        + (mark & 0x54).count_ones() as i32 * 8
        + (mark & 0xa8).count_ones() as i32 * 16
}

fn king_pressure(position: &Position, defender: Color, marks: &Marks) -> i32 {
    let source = position.piece_squares(defender, PieceKind::King)[0];
    let attacker = defender.opponent();
    let counts = position.counts[attacker.index()];
    let mut pressure = 0;
    for (directions, mask, admitted) in [
        (
            &ORTHOGONAL,
            0xf0u8,
            counts[PieceKind::Rook.index()] != 0 || counts[PieceKind::Queen.index()] != 0,
        ),
        (
            &DIAGONAL,
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
