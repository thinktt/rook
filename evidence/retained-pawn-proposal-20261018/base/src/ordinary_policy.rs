//! Native ordinary-search decisions. Callers own search/relation charges.
use crate::evaluation::RootContext;
use crate::influence::{
    adjusted_relation, profile_sum, relation, Contribution, Influence, Relation,
};
use crate::position::Position;
use crate::quiescence_policy;
use crate::types::{Color, Move, MoveKind, PieceKind, Square};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SelectiveDepth {
    pub adjustment: i32,
    pub margin: i32,
    pub adjusted_target: i32,
}

pub fn selective_depth(
    iteration: i32,
    selectivity: i32,
    endgame: u16,
    target: i32,
) -> SelectiveDepth {
    let crossed = [0, 60, 104, 144, 180, 212, 230, 254]
        .iter()
        .filter(|&&t| endgame > t)
        .count() as i32;
    let adjusted = selectivity.wrapping_sub(crossed);
    let remainder = iteration.wrapping_sub(adjusted);
    let margin = iteration.min(1.max(remainder).max(remainder.wrapping_add(8) / 3));
    let adjustment = iteration - margin;
    SelectiveDepth {
        adjustment,
        margin,
        adjusted_target: target - adjustment,
    }
}

fn nonpawn_measure(counts: &[u8; 6]) -> u16 {
    (counts[1] as u16
        + counts[2] as u16
        + counts[3] as u16
        + counts[4] as u16
        + (counts[1] as u16 + counts[3] as u16) / 16)
        % 16
}

pub fn fast_admitted(
    position: &Position,
    previous: &Position,
    movement: Option<Move>,
    depth: i32,
    adjustment: i32,
) -> bool {
    let Some(movement) = movement else {
        return false;
    };
    movement.kind() == MoveKind::Ordinary
        && previous.board[movement.to().0 as usize].is_empty()
        && position.counts.iter().any(|c| nonpawn_measure(c) >= 2)
        && depth <= adjustment
}

pub fn king_pressure(position: &Position, previous: &Influence, current: &Influence) -> bool {
    let king = position.piece_squares(position.side, PieceKind::King)[0];
    let enemy = position.side.opponent();
    let (mut before, mut after) = (0u16, 0u16);
    for dr in -1..=1 {
        for df in -1..=1 {
            if df == 0 && dr == 0 {
                continue;
            }
            if let Some(square) = king.offset(df, dr) {
                let b = profile_sum(previous.code(enemy, square));
                let c = profile_sum(current.code(enemy, square));
                if c > b && c > 1 {
                    return true;
                }
                before += b as u16;
                after += c as u16;
            }
        }
    }
    after > before && after > 1
}

/// First gate only; pressure and threat are deliberately not evaluated here.
pub fn fast_cutoff_gate(
    score: i32,
    depth: i32,
    upper: i32,
    checked: bool,
    previous_checked: bool,
    capture_exception: bool,
) -> Option<i32> {
    if depth > 2 {
        return None;
    }
    let adjusted = score - if depth == 1 { 100 } else { 150 };
    if adjusted < upper || checked || previous_checked || capture_exception {
        None
    } else {
        Some(adjusted)
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Threat {
    pub value: i32,
    pub queries: u64,
}

pub fn material_threat(
    position: &Position,
    root: &RootContext,
    map: &Influence,
    progress: i32,
) -> Threat {
    let side = position.side;
    let enemy = side.opponent();
    let counts = position.counts[side.index()];
    let sparse = counts[0] <= 2;
    let few_pieces = counts[1..5].iter().map(|&n| n as u16).sum::<u16>() <= 2;
    let mut result = Threat::default();
    for kind in &PieceKind::ALL[..5] {
        for &square in position.piece_squares(side, *kind) {
            let opposing = map.code(enemy, square);
            if opposing == 0 {
                continue;
            }
            result.queries += 1;
            let category = relation(map.code(side, square), opposing, *kind);
            if category == Relation::Favorable {
                continue;
            }
            let mut value = root.squares[side.index()][kind.index()][square.0 as usize] as i32
                + if category == Relation::Contested {
                    20
                } else {
                    root.values[side.index()][kind.index()]
                };
            if sparse && (*kind == PieceKind::Pawn || few_pieces) {
                value += 600;
            }
            result.value = result.value.max(value);
        }
    }
    let (rank, forward) = if enemy == Color::White {
        (6, 1)
    } else {
        (1, -1)
    };
    for &square in position.piece_squares(enemy, PieceKind::Pawn) {
        if square.rank() != rank {
            continue;
        }
        let straight = square.offset(0, forward).unwrap();
        let can_promote = position.board[straight.0 as usize].is_empty()
            || [-1, 1].iter().any(|&df| {
                square.offset(df, forward).is_some_and(|to| {
                    let piece = position.board[to.0 as usize];
                    !piece.is_empty() && piece.color() == side
                })
            });
        if can_promote {
            result.value = result.value.max(
                750 + if enemy == Color::White {
                    (-progress).max(0)
                } else {
                    progress.max(0)
                },
            );
        }
    }
    result
}

pub fn frontier_estimate(
    position: &Position,
    root: &RootContext,
    movement: Move,
    checking: bool,
    score: i32,
    positional: i32,
    progress: i32,
) -> i32 {
    if movement.kind() != MoveKind::Ordinary || checking {
        return 10000;
    }
    if !position.board[movement.to().0 as usize].is_empty() {
        return score
            + quiescence_policy::allowance(root, position, &movement, positional, progress);
    }
    score
        + 30
        + if position.side == Color::White && positional < -1 {
            -positional.div_euclid(2)
        } else if position.side == Color::Black && positional > 1 {
            positional.div_euclid(2)
        } else {
            0
        }
}

pub struct Extensions {
    allowance: i32,
    checked: bool,
    sole: bool,
    unique_recapture: Option<Square>,
    sparse_class: bool,
    sparse_additions: i32,
}

impl Extensions {
    pub fn new(
        position: &Position,
        candidates: &[Move],
        previous: &Position,
        movement: Option<Move>,
        previous_extension: u8,
        checked: bool,
    ) -> Self {
        let mut combined = [0u32; 5];
        for counts in position.counts {
            for kind in 0..5 {
                combined[kind] += counts[kind] as u32;
            }
        }
        let encoded = combined[0]
            + 16 * combined[1]
            + 256 * combined[2]
            + 4096 * combined[3]
            + 65536 * combined[4];
        let sparse_class = matches!((encoded / 16) % 65536, 1 | 16 | 256 | 4096);
        let low_pawns = position.counts.iter().all(|c| c[0] <= 2)
            && position
                .piece_squares(Color::White, PieceKind::Pawn)
                .iter()
                .all(|s| s.rank() <= 4)
            && position
                .piece_squares(Color::Black, PieceKind::Pawn)
                .iter()
                .all(|s| s.rank() >= 3);
        let sparse_additions = if low_pawns {
            1 + i32::from(position.counts.iter().all(|c| c[0] <= 1))
        } else {
            0
        };
        let unique_recapture = movement
            .filter(|m| {
                !previous.board[m.to().0 as usize].is_empty()
                    && candidates.iter().filter(|c| c.to() == m.to()).count() == 1
            })
            .map(|m| m.to());
        Self {
            allowance: (2 - previous_extension as i32).max(0),
            checked,
            sole: candidates.len() == 1,
            unique_recapture,
            sparse_class,
            sparse_additions,
        }
    }

    pub fn for_move(&self, position: &Position, movement: Move) -> u8 {
        let victim = position.board[movement.to().0 as usize];
        if self.sparse_class && movement.kind() == MoveKind::Ordinary && !victim.is_empty() {
            let value = match victim.kind() {
                PieceKind::Knight | PieceKind::Bishop => 2,
                PieceKind::Rook => 3,
                PieceKind::Queen => 4,
                _ => 0,
            };
            if value != 0 {
                return (value + self.sparse_additions + self.allowance - 2) as u8;
            }
        }
        if self.allowance == 0 {
            return 0;
        }
        if self.checked {
            return if self.allowance > 1 && self.sole {
                2
            } else {
                1
            };
        }
        if self.sole || self.unique_recapture == Some(movement.to()) {
            return 1;
        }
        let moving = position.board[movement.from().0 as usize];
        if moving.kind() != PieceKind::Pawn {
            return 0;
        }
        let (rank, forward) = if moving.color() == Color::White {
            (6, 1)
        } else {
            (1, -1)
        };
        if movement.to().rank() != rank {
            return 0;
        }
        let to = movement.to();
        let front_empty = to
            .offset(0, forward)
            .is_some_and(|s| position.board[s.0 as usize].is_empty());
        let mut opponent = false;
        for df in [-1, 1] {
            if let Some(square) = to.offset(df, forward) {
                let piece = position.board[square.0 as usize];
                if !piece.is_empty() && piece.color() != moving.color() {
                    if piece.kind() == PieceKind::King {
                        return 0;
                    }
                    opponent = true;
                }
            }
        }
        u8::from(front_empty || opponent)
    }
}

pub struct Learning {
    pub history: [[[u32; 64]; 6]; 2],
    pub killers: [[Move; 2]; 65],
    pub total: u32,
}

impl Default for Learning {
    fn default() -> Self {
        Self {
            history: [[[0; 64]; 6]; 2],
            killers: [[Move::NONE; 2]; 65],
            total: 0,
        }
    }
}

impl Learning {
    pub fn clear(&mut self) {
        self.history.fill([[0; 64]; 6]);
        self.killers.fill([Move::NONE; 2]);
        self.total = 0;
    }
    pub fn clear_next(&mut self, ply: usize) {
        self.killers[ply + 1] = [Move::NONE; 2];
    }
    pub fn record(&mut self, position: &Position, ply: usize, depth: i32, movement: Option<Move>) {
        let Some(movement) = movement.filter(|m| *m != Move::NONE) else {
            return;
        };
        if !position.board[movement.to().0 as usize].is_empty() {
            return;
        }
        let piece = position.board[movement.from().0 as usize];
        // A cache hint is not certified legal. Never index an empty piece code.
        if piece.is_empty() {
            return;
        }
        let pair = &mut self.killers[ply];
        if movement == pair[1] {
            pair.swap(0, 1);
        } else if movement != pair[0] {
            if pair[0] == Move::NONE {
                pair[0] = movement;
            } else {
                pair[1] = movement;
            }
        }
        let increment = 8 * (depth as u32 + 1);
        self.history[piece.color().index()][piece.kind().index()][movement.to().0 as usize] +=
            increment;
        self.total += increment;
        if self.total > 10000 {
            self.total = 0;
            for value in self.history.iter_mut().flatten().flatten() {
                *value = (*value + 1) / 2;
                self.total += *value;
            }
        }
    }
}

fn promotion_bonus(movement: Move) -> u32 {
    match movement.kind() {
        MoveKind::Promotion(PieceKind::Knight) => 256,
        MoveKind::Promotion(PieceKind::Bishop) => 512,
        MoveKind::Promotion(PieceKind::Rook) => 768,
        MoveKind::Promotion(PieceKind::Queen) => 1024,
        _ => 0,
    }
}

fn contribution(kind: PieceKind) -> Contribution {
    match kind {
        PieceKind::Pawn => Contribution::Pawn,
        PieceKind::Knight | PieceKind::Bishop => Contribution::Minor,
        PieceKind::Rook => Contribution::Rook,
        PieceKind::Queen => Contribution::Queen,
        PieceKind::King => Contribution::Weak,
    }
}

pub fn capture_magnitude(
    kind: PieceKind,
    attacker: i32,
    victim: i32,
    own: u8,
    enemy: u8,
    promotion: u32,
) -> u32 {
    if kind == PieceKind::King {
        return (4096i64 * victim as i64 - 160) as u32;
    }
    let category = adjusted_relation(own, enemy, contribution(kind), kind);
    let gain = if victim > 600 || category != Relation::Unfavorable {
        victim
    } else {
        victim - attacker
    };
    let penalty = match kind {
        PieceKind::Pawn => 99,
        PieceKind::Knight => 24,
        PieceKind::Bishop => 25,
        PieceKind::Rook => 40,
        PieceKind::Queen => 72,
        PieceKind::King => unreachable!(),
    };
    let magnitude = if (victim >= 200 || gain <= 0) && gain >= 50 {
        65536i64 * gain as i64 - penalty + promotion as i64
    } else if (victim >= 200 || gain <= 0) && gain < -50 {
        0
    } else {
        4096i64 * victim as i64 - penalty + promotion as i64
    };
    magnitude as u32
}

pub fn priority(
    position: &Position,
    root: &RootContext,
    map: &Influence,
    learned: &Learning,
    ply: usize,
    hint: Option<Move>,
    movement: Move,
) -> u32 {
    let bonus = promotion_bonus(movement);
    if hint.is_some_and(|h| h.same_endpoints(movement)) {
        return 0xffff0000u32.wrapping_add(bonus);
    }
    let mover = position.board[movement.from().0 as usize];
    let victim = position.board[movement.to().0 as usize];
    let own = map.code(position.side, movement.to());
    let enemy = map.code(position.side.opponent(), movement.to());
    if mover.kind() == PieceKind::Queen {
        let king = position.piece_squares(position.side.opponent(), PieceKind::King)[0];
        let to = movement.to();
        if (king.file() as i8 - to.file() as i8).abs() <= 1
            && (king.rank() as i8 - to.rank() as i8).abs() <= 1
            && own & 2 != 0
            && own > 2
            && adjusted_relation(own, enemy, Contribution::Queen, PieceKind::Queen)
                == Relation::Favorable
        {
            let value = if victim.is_empty() {
                1
            } else {
                root.values[victim.color().index()][victim.kind().index()]
            };
            if value != 0 {
                return 0xf0000000u32.wrapping_add((value as u32).wrapping_mul(65536));
            }
        }
    }
    if !victim.is_empty() {
        let value = root.values[victim.color().index()][victim.kind().index()]
            + root.squares[victim.color().index()][victim.kind().index()][movement.to().0 as usize]
                as i32;
        let attacker = if mover.kind() == PieceKind::King {
            0
        } else {
            root.values[mover.color().index()][mover.kind().index()]
        };
        let magnitude = capture_magnitude(mover.kind(), attacker, value, own, enemy, bonus);
        if magnitude != 0 {
            return 0xe0000000u32.wrapping_add(magnitude);
        }
    }
    if matches!(
        movement.kind(),
        MoveKind::Promotion(_) | MoveKind::EnPassant
    ) {
        return 0xe0000000
            + bonus
            + if movement.kind() == MoveKind::EnPassant {
                2048
            } else {
                0
            };
    }
    let current = learned.killers[ply];
    let earlier = if ply >= 3 {
        learned.killers[ply - 2]
    } else {
        [Move::NONE; 2]
    };
    if let Some(index) = [current[0], current[1], earlier[0], earlier[1]]
        .iter()
        .position(|&k| k == movement)
    {
        return 0xd0000005 - index as u32;
    }
    if !victim.is_empty() {
        return victim.kind().index() as u32 + 2;
    }
    learned.history[mover.color().index()][mover.kind().index()][movement.to().0 as usize]
}

#[cfg(test)]
mod tests {
    use super::*;
    fn movement(from: &str, to: &str) -> Move {
        Move::new(
            Square::parse(from).unwrap(),
            Square::parse(to).unwrap(),
            MoveKind::Ordinary,
        )
    }

    #[test]
    fn selective_wrapping_thresholds_and_frontier_negative_floor_are_exact() {
        assert_eq!(selective_depth(10, i32::MIN, 0, 20).margin, 1);
        assert_eq!(selective_depth(10, -2147483630, 0, 20).margin, 10);
        assert_eq!(selective_depth(0, 14, 256, 0).adjustment, 0);
        for e in [0, 60, 104, 144, 180, 212, 230, 254] {
            let a = selective_depth(30, 30, e, 40);
            let b = selective_depth(30, 30, e + 1, 40);
            assert!(b.margin >= a.margin);
        }
        let white = Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 0 1").unwrap();
        let mut black = white;
        black.side = Color::Black;
        let root = RootContext::neutral(&white);
        assert_eq!(
            frontier_estimate(&white, &root, movement("a1", "a2"), false, 10, -3, 0),
            42
        );
        assert_eq!(
            frontier_estimate(&black, &root, movement("h8", "h7"), false, 10, 3, 0),
            41
        );
    }

    #[test]
    fn sparse_exception_precedes_exhausted_extension_and_pawn_king_guard() {
        let position = Position::from_fen("7k/8/8/8/2q5/1P6/8/K7 w - - 0 1").unwrap();
        let capture = movement("b3", "c4");
        let ext = Extensions::new(&position, &[capture], &position, None, 7, false);
        assert_eq!(ext.for_move(&position, capture), 4); // Queen4 + low-pawn2 -2.
        let position = Position::from_fen("7k/8/6P1/8/8/8/8/K7 w - - 0 1").unwrap();
        let pawn = movement("g6", "g7");
        let other = movement("a1", "a2");
        let ext = Extensions::new(&position, &[pawn, other], &position, None, 0, false);
        assert_eq!(ext.for_move(&position, pawn), 0); // King h8 blocks this rule even with g8 empty.
    }

    #[test]
    fn learned_reduction_rounds_each_entry_and_special_empty_destinations_are_eligible() {
        let position = Position::from_fen("7k/8/8/8/8/8/P7/K7 w - - 0 1").unwrap();
        let mut learned = Learning::default();
        learned.history[1][1][0] = 4999;
        learned.history[1][2][0] = 5001;
        learned.total = 10000;
        learned.record(&position, 3, 0, Some(movement("a2", "a3")));
        assert_eq!(
            (
                learned.history[1][1][0],
                learned.history[1][2][0],
                learned.total
            ),
            (2500, 2501, 5005)
        );
        learned.record(&position, 3, 0, Some(movement("a1", "b1")));
        assert_eq!(
            learned.killers[3],
            [movement("a2", "a3"), movement("a1", "b1")]
        );
        learned.record(&position, 3, 0, Some(movement("a1", "b1")));
        assert_eq!(learned.killers[3][0], movement("a1", "b1"));
    }

    #[test]
    fn threat_queries_favorable_and_nonmaximum_pieces_but_not_zero_opposing_codes() {
        let position = Position::from_fen("7k/8/8/8/8/8/PP6/K7 w - - 0 1").unwrap();
        let mut map = Influence {
            profiles: [[0; 64]; 2],
        };
        let root = RootContext::neutral(&position);
        map.profiles[1][Square::parse("a2").unwrap().0 as usize] = 2;
        map.profiles[0][Square::parse("a2").unwrap().0 as usize] = 64;
        assert_eq!(
            material_threat(&position, &root, &map, 0),
            Threat {
                value: 0,
                queries: 1
            }
        );
        map.profiles[1][Square::parse("b2").unwrap().0 as usize] = 64;
        let result = material_threat(&position, &root, &map, 0);
        assert_eq!(result.queries, 2);
        assert!(result.value >= 600);
    }
}
