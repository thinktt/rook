//! Exact placement fingerprints from POSITION-IDENTITY; rule state is separate.
use crate::types::{Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Fingerprints {
    pub primary: u32,
    pub secondary: u32,
    pub pawn: u32,
}

const fn make_keys() -> [[[u32; 2]; 64]; 12] {
    let mut coefficients = [0u32; 1920];
    let mut state = 0x0123_4567u32;
    let mut i = 0;
    while i < coefficients.len() {
        state = state.wrapping_mul(0xbb40_e62d).wrapping_add(1);
        // An arithmetic signed shift is floor(signed(state) / 65536).
        let high = ((state as i32) >> 16) as u32;
        state = state.wrapping_mul(0xbb40_e62d).wrapping_add(1);
        coefficients[i] = high ^ state;
        i += 1;
    }
    let mut keys = [[[0u32; 2]; 64]; 12];
    let mut piece = 0;
    while piece < 12 {
        let mut square = 0;
        while square < 64 {
            let index = 80 * piece + 10 * (square / 8) + square % 8 + 1;
            keys[piece][square] = [coefficients[index], coefficients[960 + index]];
            square += 1;
        }
        piece += 1;
    }
    keys
}

/// Type/color rows are white pawn, black pawn, white knight, black knight, ...
pub const KEYS: [[[u32; 2]; 64]; 12] = make_keys();

#[inline]
pub fn piece_keys(piece: Piece, square: Square) -> [u32; 2] {
    debug_assert!(!piece.is_empty());
    KEYS[2 * piece.kind().index() + piece.color().index()][square.0 as usize]
}

pub fn fingerprints(board: &[Piece; 64]) -> Fingerprints {
    let mut result = Fingerprints::default();
    for (index, &piece) in board.iter().enumerate() {
        if piece.is_empty() {
            continue;
        }
        let keys = piece_keys(piece, Square(index as u8));
        result.primary ^= keys[0];
        result.secondary ^= keys[1];
        if piece.kind() == PieceKind::Pawn {
            result.pawn ^= keys[0];
        }
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::Color;

    #[test]
    fn keys_match_independent_signed_floor_definition() {
        let mut state = 0x0123_4567u64;
        let mut coefficients = [0u32; 1920];
        for coefficient in &mut coefficients {
            state = (0xbb40_e62du64 * state + 1) % (1u64 << 32);
            let signed = if state >= (1u64 << 31) {
                state as i64 - (1i64 << 32)
            } else {
                state as i64
            };
            let high = signed.div_euclid(65_536) as u32;
            state = (0xbb40_e62du64 * state + 1) % (1u64 << 32);
            *coefficient = high ^ state as u32;
        }
        for (piece, row) in KEYS.iter().enumerate() {
            for (square, pair) in row.iter().enumerate() {
                let index = 80 * piece + 10 * (square / 8) + square % 8 + 1;
                assert_eq!(*pair, [coefficients[index], coefficients[960 + index]]);
            }
        }
    }

    #[test]
    fn nonpawn_move_keeps_pawn_identity() {
        let mut board = [Piece::EMPTY; 64];
        board[12] = Piece::new(Color::White, PieceKind::Pawn);
        board[50] = Piece::new(Color::Black, PieceKind::Pawn);
        board[1] = Piece::new(Color::White, PieceKind::Knight);
        let before = fingerprints(&board);
        board[18] = board[1];
        board[1] = Piece::EMPTY;
        let after = fingerprints(&board);
        assert_eq!(before.pawn, after.pawn);
        assert_ne!(before.primary, after.primary);
        assert_ne!(before.secondary, after.secondary);
    }
}
