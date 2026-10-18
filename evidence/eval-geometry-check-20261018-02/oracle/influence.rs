//! Pure evaluation influence. This is deliberately not a legal attack map.
//!
//! The five mixed-radix digits fit exactly in one byte. Contributions accumulate
//! with wrapping addition; adjusted relation exclusion instead saturates.
//! Consumers own semantic relation charges, including any cache-hit charges.

use crate::position::Position;
use crate::types::{Color, Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum Contribution {
    Weak = 1,
    Queen = 2,
    Rook = 4,
    Minor = 16,
    Pawn = 64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum Relation {
    Unfavorable = 0,
    Contested = 1,
    Favorable = 2,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Influence {
    pub profiles: [[u8; 64]; 2],
}

const ORTHOGONAL: [(i8, i8); 4] = [(1, 0), (-1, 0), (0, 1), (0, -1)];
const DIAGONAL: [(i8, i8); 4] = [(1, 1), (1, -1), (-1, 1), (-1, -1)];
const KNIGHT: [(i8, i8); 8] = [
    (1, 2),
    (2, 1),
    (2, -1),
    (1, -2),
    (-1, -2),
    (-2, -1),
    (-2, 1),
    (-1, 2),
];

impl Influence {
    pub fn build(position: &Position) -> Self {
        Self::build_board(&position.board)
    }

    #[inline]
    pub fn code(&self, side: Color, square: Square) -> u8 {
        self.profiles[side.index()][square.0 as usize]
    }

    fn build_board(board: &[Piece; 64]) -> Self {
        let mut influence = Self {
            profiles: [[0; 64]; 2],
        };
        // Chronology is immaterial to these commutative placement-only sums.
        for (index, &piece) in board.iter().enumerate() {
            if piece.is_empty() {
                continue;
            }
            let side = piece.color();
            let square = Square(index as u8);
            match piece.kind() {
                PieceKind::Pawn => {
                    let forward = if side == Color::White { 1 } else { -1 };
                    for file in [-1, 1] {
                        if let Some(target) = square.offset(file, forward) {
                            influence.add(side, target, Contribution::Pawn as u8);
                        }
                    }
                }
                PieceKind::Knight => {
                    for (file, rank) in KNIGHT {
                        if let Some(target) = square.offset(file, rank) {
                            influence.add(side, target, Contribution::Minor as u8);
                        }
                    }
                }
                PieceKind::King => {
                    for (file, rank) in ORTHOGONAL.into_iter().chain(DIAGONAL) {
                        if let Some(target) = square.offset(file, rank) {
                            influence.add(side, target, Contribution::Weak as u8);
                        }
                    }
                }
                PieceKind::Rook => {
                    for step in ORTHOGONAL {
                        influence.ray(board, side, square, step, Contribution::Rook);
                    }
                }
                PieceKind::Bishop => {
                    for step in DIAGONAL {
                        influence.ray(board, side, square, step, Contribution::Minor);
                    }
                }
                PieceKind::Queen => {
                    for step in ORTHOGONAL.into_iter().chain(DIAGONAL) {
                        influence.ray(board, side, square, step, Contribution::Queen);
                    }
                }
            }
        }
        influence
    }

    #[inline]
    fn add(&mut self, side: Color, target: Square, weight: u8) {
        let code = &mut self.profiles[side.index()][target.0 as usize];
        *code = code.wrapping_add(weight);
    }

    fn ray(
        &mut self,
        board: &[Piece; 64],
        side: Color,
        source: Square,
        step: (i8, i8),
        contribution: Contribution,
    ) {
        let diagonal = step.0 != 0 && step.1 != 0;
        let forward = if side == Color::White { 1 } else { -1 };
        let mut weight = contribution as u8;
        let mut cursor = source;
        while let Some(target) = cursor.offset(step.0, step.1) {
            // The occupied square gets the old contribution before transparency
            // or weakening is considered.
            self.add(side, target, weight);
            cursor = target;
            let piece = board[target.0 as usize];
            if piece.is_empty() {
                continue;
            }
            if piece.color() != side {
                if piece.kind() == PieceKind::King {
                    continue;
                }
                break;
            }
            match piece.kind() {
                PieceKind::Queen => weight = Contribution::Weak as u8,
                PieceKind::Rook if !diagonal => {}
                PieceKind::Bishop if diagonal => {}
                PieceKind::Pawn if diagonal && step.1 == forward => {
                    if let Some(extra) = target.offset(step.0, step.1) {
                        self.add(side, extra, weight);
                    }
                    break;
                }
                _ => break,
            }
        }
    }
}

/// Sum normalized digit counts without the relation multiplicity cap of four.
#[inline]
pub const fn profile_sum(code: u8) -> u8 {
    (code & 1) + ((code >> 1) & 1) + ((code >> 2) & 3) + ((code >> 4) & 3) + (code >> 6)
}

#[inline]
fn least_tier(code: u8) -> u8 {
    if code >= 64 {
        1
    } else if code >= 16 {
        3
    } else if code >= 4 {
        5
    } else if code >= 2 {
        9
    } else {
        99
    } // Empty profiles are handled before a tier is used.
}

/// Classify a pawn, minor (knight/bishop), rook or queen; kings have no query tier.
/// This function does not charge a relation unit.
#[inline]
pub fn relation(own: u8, opponent: u8, kind: PieceKind) -> Relation {
    let tested = match kind {
        PieceKind::Pawn => 1,
        PieceKind::Knight | PieceKind::Bishop => 3,
        PieceKind::Rook => 5,
        PieceKind::Queen => 9,
        PieceKind::King => panic!("king has no tested-piece relation tier"),
    };
    if opponent == 0 {
        return Relation::Favorable;
    }
    let attack_tier = least_tier(opponent);
    if own == 0 || attack_tier < tested {
        return Relation::Unfavorable;
    }
    let attacks = profile_sum(opponent).min(4);
    let defenses = profile_sum(own).min(4);
    if attack_tier == tested {
        if attacks <= defenses {
            Relation::Contested
        } else {
            Relation::Unfavorable
        }
    } else if attacks <= defenses || attack_tier > tested + least_tier(own) {
        Relation::Favorable
    } else {
        Relation::Unfavorable
    }
}

/// Exclude from normalized own support, preserving the base map and opponent.
/// Borrowing is intentional; underflow empties support rather than wrapping.
#[inline]
pub fn adjusted_relation(own: u8, opponent: u8, remove: Contribution, kind: PieceKind) -> Relation {
    relation(own.saturating_sub(remove as u8), opponent, kind)
}
