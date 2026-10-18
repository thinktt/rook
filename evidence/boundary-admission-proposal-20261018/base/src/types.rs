//! Compact native values. Their encodings do not define move ordering.

use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum Color {
    White = 0,
    Black = 1,
}

impl Color {
    pub const fn index(self) -> usize {
        self as usize
    }
    pub const fn opponent(self) -> Self {
        match self {
            Self::White => Self::Black,
            Self::Black => Self::White,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum PieceKind {
    Pawn = 0,
    Knight = 1,
    Bishop = 2,
    Rook = 3,
    Queen = 4,
    King = 5,
}

impl PieceKind {
    pub const ALL: [Self; 6] = [
        Self::Pawn,
        Self::Knight,
        Self::Bishop,
        Self::Rook,
        Self::Queen,
        Self::King,
    ];
    pub const fn index(self) -> usize {
        self as usize
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(transparent)]
pub struct Square(pub u8);

impl Square {
    pub const fn file(self) -> u8 {
        self.0 & 7
    }
    pub const fn rank(self) -> u8 {
        self.0 >> 3
    }
    pub fn parse(text: &str) -> Option<Self> {
        let b = text.as_bytes();
        if b.len() == 2 && (b'a'..=b'h').contains(&b[0]) && (b'1'..=b'8').contains(&b[1]) {
            Some(Self((b[1] - b'1') * 8 + b[0] - b'a'))
        } else {
            None
        }
    }
    pub const fn offset(self, file: i8, rank: i8) -> Option<Self> {
        let f = self.file() as i8 + file;
        let r = self.rank() as i8 + rank;
        if f >= 0 && f < 8 && r >= 0 && r < 8 {
            Some(Self(r as u8 * 8 + f as u8))
        } else {
            None
        }
    }
}

impl fmt::Display for Square {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{}{}",
            (b'a' + self.file()) as char,
            (b'1' + self.rank()) as char
        )
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(transparent)]
pub struct Piece(pub u8);

impl Piece {
    pub const EMPTY: Self = Self(0);
    pub const fn new(color: Color, kind: PieceKind) -> Self {
        Self((kind as u8 + 1) | ((color as u8) << 3))
    }
    pub const fn is_empty(self) -> bool {
        self.0 == 0
    }
    /// Only call on a nonempty, validated piece code.
    pub const fn color(self) -> Color {
        debug_assert!(!self.is_empty());
        if self.0 & 8 == 0 {
            Color::White
        } else {
            Color::Black
        }
    }
    /// Only call on a nonempty, validated piece code.
    pub const fn kind(self) -> PieceKind {
        match self.0 & 7 {
            1 => PieceKind::Pawn,
            2 => PieceKind::Knight,
            3 => PieceKind::Bishop,
            4 => PieceKind::Rook,
            5 => PieceKind::Queen,
            6 => PieceKind::King,
            _ => panic!("invalid piece code"),
        }
    }
    pub fn from_fen(c: char) -> Option<Self> {
        let kind = match c.to_ascii_lowercase() {
            'p' => PieceKind::Pawn,
            'n' => PieceKind::Knight,
            'b' => PieceKind::Bishop,
            'r' => PieceKind::Rook,
            'q' => PieceKind::Queen,
            'k' => PieceKind::King,
            _ => return None,
        };
        Some(Self::new(
            if c.is_ascii_uppercase() {
                Color::White
            } else {
                Color::Black
            },
            kind,
        ))
    }
    pub fn fen_char(self) -> char {
        let c = match self.kind() {
            PieceKind::Pawn => 'p',
            PieceKind::Knight => 'n',
            PieceKind::Bishop => 'b',
            PieceKind::Rook => 'r',
            PieceKind::Queen => 'q',
            PieceKind::King => 'k',
        };
        if self.color() == Color::White {
            c.to_ascii_uppercase()
        } else {
            c
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MoveKind {
    Ordinary,
    Promotion(PieceKind),
    EnPassant,
    Castle,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(transparent)]
pub struct Move(pub u16);

impl Move {
    pub const NONE: Self = Self(0);
    pub const fn new(from: Square, to: Square, kind: MoveKind) -> Self {
        debug_assert!(from.0 < 64 && to.0 < 64 && from.0 != to.0);
        let tag = match kind {
            MoveKind::Ordinary => 0,
            MoveKind::Promotion(PieceKind::Knight) => 1,
            MoveKind::Promotion(PieceKind::Bishop) => 2,
            MoveKind::Promotion(PieceKind::Rook) => 3,
            MoveKind::Promotion(PieceKind::Queen) => 4,
            MoveKind::EnPassant => 5,
            MoveKind::Castle => 6,
            MoveKind::Promotion(_) => panic!("invalid promotion kind"),
        };
        Self(from.0 as u16 | ((to.0 as u16) << 6) | (tag << 12))
    }
    pub const fn from(self) -> Square {
        Square((self.0 & 63) as u8)
    }
    pub const fn to(self) -> Square {
        Square(((self.0 >> 6) & 63) as u8)
    }
    pub const fn kind(self) -> MoveKind {
        match (self.0 >> 12) & 7 {
            0 => MoveKind::Ordinary,
            1 => MoveKind::Promotion(PieceKind::Knight),
            2 => MoveKind::Promotion(PieceKind::Bishop),
            3 => MoveKind::Promotion(PieceKind::Rook),
            4 => MoveKind::Promotion(PieceKind::Queen),
            5 => MoveKind::EnPassant,
            6 => MoveKind::Castle,
            _ => panic!("invalid move tag"),
        }
    }
    pub const fn same_endpoints(self, other: Self) -> bool {
        (self.0 & 4095) == (other.0 & 4095)
    }
}

impl fmt::Display for Move {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if *self == Self::NONE {
            return f.write_str("0000");
        }
        write!(f, "{}{}", self.from(), self.to())?;
        if let MoveKind::Promotion(kind) = self.kind() {
            f.write_str(match kind {
                PieceKind::Knight => "n",
                PieceKind::Bishop => "b",
                PieceKind::Rook => "r",
                PieceKind::Queen => "q",
                _ => unreachable!(),
            })?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compact_moves_preserve_full_identity_and_endpoint_comparison() {
        let kinds = [
            MoveKind::Ordinary,
            MoveKind::Promotion(PieceKind::Knight),
            MoveKind::Promotion(PieceKind::Bishop),
            MoveKind::Promotion(PieceKind::Rook),
            MoveKind::Promotion(PieceKind::Queen),
            MoveKind::EnPassant,
            MoveKind::Castle,
        ];
        for from in 0..64 {
            for to in 0..64 {
                if from == to {
                    continue;
                }
                for kind in kinds {
                    let mv = Move::new(Square(from), Square(to), kind);
                    assert_ne!(mv, Move::NONE);
                    assert_eq!(
                        (mv.from(), mv.to(), mv.kind()),
                        (Square(from), Square(to), kind)
                    );
                    assert!(mv.same_endpoints(Move::new(
                        Square(from),
                        Square(to),
                        MoveKind::Ordinary
                    )));
                }
            }
        }
        assert_eq!(std::mem::size_of::<Move>(), 2);
    }

    #[test]
    fn square_notation_and_piece_codes_round_trip() {
        for square in 0..64 {
            let sq = Square(square);
            assert_eq!(Square::parse(&sq.to_string()), Some(sq));
        }
        for color in [Color::White, Color::Black] {
            for kind in PieceKind::ALL {
                let piece = Piece::new(color, kind);
                assert_eq!(piece.color(), color);
                assert_eq!(piece.kind(), kind);
                assert_eq!(Piece::from_fen(piece.fen_char()), Some(piece));
            }
        }
        assert_eq!(Square::parse("a9"), None);
        assert_eq!(Square::parse("é"), None);
        assert_eq!(Square(7).offset(1, 0), None);
    }
}
