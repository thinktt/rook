//! Root-fixed material/square context consumed by composed evaluation.

use crate::eval_basis::SQUARE_BASIS;
use crate::position::{Phase, Position};
use crate::types::{Color, PieceKind, Square};

const MATERIAL_BASE: [[i32; 5]; 3] = [
    [66, 295, 310, 470, 880],
    [80, 295, 310, 485, 900],
    [100, 300, 300, 500, 890],
];

pub fn draw_preference(phase: Phase, cfd: i32) -> i32 {
    (((4 * phase.opening as i64 + 2 * phase.middlegame as i64 + phase.endgame as i64) * cfd as i64
        + 512)
        .div_euclid(1024)) as i32
}

/// Mathematical floor division, including negative values.
#[inline]
pub fn floor_div(value: i64, divisor: i64) -> i64 {
    debug_assert!(divisor > 0);
    value.div_euclid(divisor)
}

/// Root-phase material values. Percentages are bound to White/Black ownership.
/// Phase components must be in 0..256 and sum to 256.
pub fn material_values(phase: Phase, percentages: [[u16; 5]; 2]) -> [[i32; 5]; 2] {
    assert!(
        percentages.iter().flatten().all(|&value| value <= 1000),
        "material percentages must be in 0..1000"
    );
    let mut values = [[0; 5]; 2];
    for kind in 0..5 {
        let base = blend(
            phase,
            [
                MATERIAL_BASE[0][kind],
                MATERIAL_BASE[1][kind],
                MATERIAL_BASE[2][kind],
            ],
        );
        for color in [Color::White, Color::Black] {
            let c = color.index();
            let weight = (1024 * percentages[c][kind] as i32 + 50) / 100;
            values[c][kind] = (weight * base + 512) / 1024;
        }
    }
    values
}

/// One oriented square adjustment, including king and empty/promotion-rank queries.
/// Phase components must be in 0..256 and sum to 256; square must be in 0..=63.
pub fn square_adjustment(phase: Phase, color: Color, kind: PieceKind, square: Square) -> i32 {
    let oriented = if color == Color::White {
        square.0 as usize
    } else {
        (square.0 ^ 56) as usize
    };
    blend(
        phase,
        [
            SQUARE_BASIS[0][kind.index()][oriented] as i32,
            SQUARE_BASIS[1][kind.index()][oriented] as i32,
            SQUARE_BASIS[2][kind.index()][oriented] as i32,
        ],
    )
}

#[derive(Clone)]
pub struct RootContext {
    pub side: Color,
    pub phase: Phase,
    pub counts: [[u8; 6]; 2],
    pub values: [[i32; 5]; 2],
    pub squares: [[[i16; 64]; 5]; 2],
    pub average_depth: i32,
}

impl RootContext {
    /// Percentages are already bound to White/Black ownership, not moving side.
    pub fn new(root: &Position, percentages: [[u16; 5]; 2], average_depth: i32) -> Self {
        let phase = root.phase();
        let values = material_values(phase, percentages);
        assert!(
            (-100..=100).contains(&average_depth),
            "average depth must be in -100..100"
        );
        let mut squares = [[[0; 64]; 5]; 2];
        for kind in &PieceKind::ALL[..5] {
            for color in [Color::White, Color::Black] {
                for square in 0..64 {
                    squares[color.index()][kind.index()][square] =
                        square_adjustment(phase, color, *kind, Square(square as u8)) as i16;
                }
            }
        }
        Self {
            side: root.side,
            phase,
            counts: root.counts,
            values,
            squares,
            average_depth,
        }
    }

    pub fn neutral(root: &Position) -> Self {
        Self::new(root, [[100; 5]; 2], 0)
    }

    pub fn material(&self, position: &Position) -> i32 {
        let mut pawns = [0i32; 2];
        let mut heavy = [0i32; 2];
        let mut remaining = 0i32;
        let mut root_count = 0i32;
        let mut any_heavy = false;
        for c in 0..2 {
            pawns[c] = position.counts[c][0] as i32 * self.values[c][0];
            for kind in 0..5 {
                remaining += position.counts[c][kind] as i32;
                root_count += self.counts[c][kind] as i32;
                if kind != 0 {
                    heavy[c] += position.counts[c][kind] as i32 * self.values[c][kind];
                    any_heavy |= position.counts[c][kind] != 0;
                }
            }
        }
        let d = floor_div(
            (root_count - remaining) as i64 * self.average_depth as i64 + 1,
            2,
        ) as i32;
        let mut balance = heavy[0] + pawns[0]
            - heavy[1]
            - pawns[1]
            - if self.side == Color::White { d } else { -d };
        if any_heavy && balance.abs() > 50 {
            let winning = usize::from(balance < 0);
            let losing = winning ^ 1;
            let losing_heavy = floor_div((2400 - heavy[losing]) as i64, 16).max(0);
            let winning_pawns = floor_div((3 * pawns[winning]) as i64, 16).min(100);
            let extra = (balance.abs() - 50).min(512) as i64 * (losing_heavy + winning_pawns) / 512;
            balance += if balance > 0 {
                extra as i32
            } else {
                -(extra as i32)
            };
        }
        balance.clamp(-7000, 7000)
    }

    pub fn square_balance(&self, position: &Position) -> i32 {
        self.square_balance_from(position, self.nonking_square_balance(position))
    }

    /// Root-valued non-king sum, maintained incrementally by searched children.
    pub fn nonking_square_balance(&self, position: &Position) -> i32 {
        let mut result = 0;
        for color in [Color::White, Color::Black] {
            let sign = if color == Color::White { 1 } else { -1 };
            for kind in &PieceKind::ALL[..5] {
                for square in position.piece_squares(color, *kind) {
                    result +=
                        sign * self.squares[color.index()][kind.index()][square.0 as usize] as i32;
                }
            }
        }
        result
    }

    /// Current-phase kings round once; a pawn-only position doubles both terms.
    pub fn square_balance_from(&self, position: &Position, nonking_sum: i32) -> i32 {
        self.square_balance_from_phase(position, nonking_sum, position.phase())
    }

    /// Explicit current-phase variant; nonking_sum still belongs to this root.
    /// Phase components must be in 0..256 and sum to 256.
    pub fn square_balance_from_phase(
        &self,
        position: &Position,
        nonking_sum: i32,
        phase: Phase,
    ) -> i32 {
        let mut king_differences = [0i32; 3];
        for color in [Color::White, Color::Black] {
            let sign = if color == Color::White { 1 } else { -1 };
            let square = position.piece_squares(color, PieceKind::King)[0].0 as usize;
            let oriented = if color == Color::White {
                square
            } else {
                square ^ 56
            };
            for phase in 0..3 {
                king_differences[phase] += sign * SQUARE_BASIS[phase][5][oriented] as i32;
            }
        }
        let mut result = nonking_sum + blend(phase, king_differences);
        if position
            .counts
            .iter()
            .all(|counts| counts[1..5].iter().all(|&n| n == 0))
        {
            result *= 2;
        }
        result
    }

    /// Partial score, oriented to moving side. No complete-score parity claim.
    pub fn development_score(&self, position: &Position) -> i32 {
        let white = self.material(position) + self.square_balance(position);
        if position.side == Color::White {
            white
        } else {
            -white
        }
    }
}

#[inline]
fn blend(phase: Phase, values: [i32; 3]) -> i32 {
    floor_div(
        phase.opening as i64 * values[0] as i64
            + phase.middlegame as i64 * values[1] as i64
            + phase.endgame as i64 * values[2] as i64
            + 128,
        256,
    ) as i32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signed_floor_and_phase_blends_keep_negative_half_rounding() {
        assert_eq!(floor_div(-1, 256), -1);
        assert_eq!(floor_div(-256, 256), -1);
        let half = Phase {
            opening: 128,
            middlegame: 128,
            endgame: 0,
        };
        assert_eq!(blend(half, [-1, 0, 0]), 0);
        assert_eq!(blend(half, [-2, -1, 0]), -1);
    }

    #[test]
    fn root_context_remains_fixed_and_symmetry_has_zero_partial_score() {
        let start =
            Position::from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
        let context = RootContext::neutral(&start);
        assert_eq!(context.material(&start), 0);
        assert_eq!(context.square_balance(&start), 0);
        assert_eq!(context.development_score(&start), 0);
        assert_eq!(context.values[0], [66, 295, 310, 470, 880]);
        let ending = Position::from_fen("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1").unwrap();
        let separate = RootContext::neutral(&ending);
        assert_ne!(context.values, separate.values);
        assert_eq!(context.values[0][0], 66);
        assert_eq!(separate.values[0][0], 100);
    }
}
