//! Central influence and literal bishop/opening patterns, with no relation charge.
use crate::influence::Influence;
use crate::position::{Phase, Position};
use crate::types::{Color, Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Central {
    pub colors: [i32; 2],
    pub weighted: i32,
}

pub fn central(map: &Influence, phase: Phase, weights: [i32; 2]) -> Central {
    let factor = phase.opening as i64 + 2 * phase.middlegame as i64;
    if factor <= 16 {
        return Central::default();
    }
    const SQUARES: [[i32; 4]; 6] = [
        [8, 12, 12, 8],
        [12, 16, 16, 12],
        [20, 34, 34, 20],
        [20, 34, 34, 20],
        [12, 16, 16, 12],
        [8, 12, 12, 8],
    ];
    let mut sums = [0; 2];
    for rank in 1..=6 {
        for file in 2..=5 {
            let square = Square(rank * 8 + file);
            let a = map.code(Color::White, square) as i32;
            let b = map.code(Color::Black, square) as i32;
            let difference = (a - b).abs();
            let magnitude = match difference {
                0 => 0,
                1 => 90,
                2 => 115,
                3 => 130,
                4 => 141,
                5 => 148,
                6 => 154,
                7..=15 => 160,
                16 => 179,
                17 => 183,
                18 => 185,
                19 => 186,
                20 => 192,
                21 => 195,
                22 => 197,
                23 => 199,
                24..=63 => 203,
                _ => 225,
            };
            let color = usize::from(a < b);
            sums[color] += magnitude * SQUARES[rank as usize - 1][file as usize - 2];
        }
    }
    let colors = [sums[0] / 1024, sums[1] / 1024];
    let first = (colors[0] as i64 * weights[0] as i64 - colors[1] as i64 * weights[1] as i64 + 512)
        .div_euclid(1024);
    Central {
        colors,
        weighted: (first * factor + 256).div_euclid(512) as i32,
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Patterns {
    pub bishop_coordination: i32,
    pub raw: i32,
    pub opening: i32,
}

pub fn patterns(position: &Position) -> Patterns {
    patterns_with_phase(position, position.phase())
}

/// Full evaluation may supply its already-produced current-position phase.
pub(crate) fn patterns_with_phase(position: &Position, phase: Phase) -> Patterns {
    const PAWN: [[i32; 8]; 6] = [
        [4, 4, 6, 8, 8, 6, 4, 4],
        [6, 8, 10, 10, 10, 10, 8, 6],
        [6, 8, 10, 14, 14, 10, 8, 6],
        [6, 6, 8, 12, 12, 8, 6, 6],
        [2, 4, 4, 6, 6, 4, 4, 2],
        [0; 8],
    ];
    let wb = position.counts[0][2];
    let bb = position.counts[1][2];
    let central_pawns = (2..=5)
        .flat_map(|rank| [Square(rank * 8 + 3), Square(rank * 8 + 4)])
        .filter(|s| {
            let p = position.board[s.0 as usize];
            !p.is_empty() && p.kind() == PieceKind::Pawn
        })
        .count();
    let value = [44, 44, 36, 28, 20, 20, 20, 20, 20][central_pawns];
    let mut bishop_coordination = if wb == bb || (wb <= 1 && bb <= 1) {
        0
    } else if bb >= 2 {
        -value
    } else {
        value
    };
    let mut raw = 0;
    for side in [Color::White, Color::Black] {
        let sign = if side == Color::White { 1 } else { -1 };
        if position.counts[side.index()][2] == 1 {
            let bishop = position.piece_squares(side, PieceKind::Bishop)[0];
            let shade = (bishop.file() + bishop.rank()) & 1;
            let mut sum = 0;
            for &square in position.piece_squares(side, PieceKind::Pawn) {
                if (square.file() + square.rank()) & 1 != shade {
                    continue;
                }
                let rank = if side == Color::White {
                    square.rank()
                } else {
                    7 - square.rank()
                };
                let forward = square
                    .offset(0, if side == Color::White { 1 } else { -1 })
                    .unwrap();
                let blocked = position.board[forward.0 as usize]
                    == Piece::new(side.opponent(), PieceKind::Pawn);
                sum +=
                    PAWN[rank as usize - 1][square.file() as usize] * if blocked { 2 } else { 1 };
            }
            let rank = if side == Color::White {
                bishop.rank()
            } else {
                7 - bishop.rank()
            };
            let multiplier = match rank {
                0 | 1 => 8,
                2 => 7,
                3 => 6,
                _ => 5,
            };
            bishop_coordination -= sign * ((multiplier * sum - 80).div_euclid(16)).max(0);
        }
        let at = |file: u8, rank: u8| {
            position.board[Square(if side == Color::White {
                rank * 8 + file
            } else {
                (7 - rank) * 8 + file
            })
            .0 as usize]
        };
        let own = |kind, file, rank| at(file, rank) == Piece::new(side, kind);
        let own_pawn = |file, rank| own(PieceKind::Pawn, file, rank);
        let enemy_pawn =
            |file, rank| at(file, rank) == Piece::new(side.opponent(), PieceKind::Pawn);
        let pawn = |file, rank| {
            let p = at(file, rank);
            !p.is_empty() && p.kind() == PieceKind::Pawn
        };
        let mut term = 0;
        if own(PieceKind::Knight, 2, 2) && (own_pawn(3, 3) || pawn(3, 4)) {
            if own_pawn(2, 3) {
                term += 7;
            }
            if own_pawn(2, 1) {
                term -= 12;
            }
        }
        if own(PieceKind::Knight, 5, 2) && own_pawn(5, 3) && (own_pawn(4, 3) || own_pawn(4, 4)) {
            term += 7;
        }
        if own_pawn(2, 4) && own_pawn(3, 3) {
            if (4..=6).any(|r| enemy_pawn(4, r)) {
                term -= 18;
            } else if enemy_pawn(4, 3) {
                term -= 12;
            }
        }
        raw += sign * term;
    }
    let opening = phase.opening as i32;
    Patterns {
        bishop_coordination,
        raw,
        opening: if opening == 0 {
            0
        } else if opening >= 128 {
            raw
        } else {
            (opening * raw + 64).div_euclid(128)
        },
    }
}
