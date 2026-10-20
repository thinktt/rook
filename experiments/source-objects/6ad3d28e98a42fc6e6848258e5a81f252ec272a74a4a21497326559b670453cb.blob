//! Ordinary legal inventory in KingRE generation order.
//!
//! Legality projects only the mailbox. Chronology, fingerprints and evaluation
//! state are updated only when a caller actually plays an admitted move.

use crate::position::Position;
use crate::types::{Color, Move, MoveKind, Piece, PieceKind, Square};

pub const MOVE_CAPACITY: usize = 512;

#[derive(Clone)]
pub struct MoveList {
    pub moves: [Move; MOVE_CAPACITY],
    pub len: usize,
}

impl MoveList {
    pub const fn new() -> Self {
        Self {
            moves: [Move::NONE; MOVE_CAPACITY],
            len: 0,
        }
    }

    #[inline]
    pub fn as_slice(&self) -> &[Move] {
        &self.moves[..self.len]
    }

    #[inline]
    pub fn clear(&mut self) {
        self.len = 0;
    }

    #[inline]
    pub fn push(&mut self, mv: Move) {
        assert!(
            self.len < MOVE_CAPACITY,
            "ordinary candidate capacity exceeded"
        );
        self.moves[self.len] = mv;
        self.len += 1;
    }
}

impl Default for MoveList {
    fn default() -> Self {
        Self::new()
    }
}

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
const DIRECTIONS: [(i8, i8); 8] = [
    (1, 1),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (0, 1),
    (0, -1),
    (1, 0),
    (-1, 0),
];
const PROMOTIONS: [PieceKind; 4] = [
    PieceKind::Queen,
    PieceKind::Rook,
    PieceKind::Bishop,
    PieceKind::Knight,
];

#[derive(Clone, Copy)]
struct Checkers {
    squares: [Square; 2],
    len: usize,
}

impl Checkers {
    #[inline]
    fn add<const LIMIT: usize>(&mut self, square: Square) -> bool {
        self.squares[self.len] = square;
        self.len += 1;
        self.len == LIMIT
    }
}

#[inline]
fn has_piece(board: &[Piece; 64], square: Square, color: Color, kind: PieceKind) -> bool {
    board[square.0 as usize] == Piece::new(color, kind)
}

/// Pinned pieces still attack their geometric destinations.
#[inline]
fn find_attackers<const LIMIT: usize>(board: &[Piece; 64], square: Square, by: Color) -> Checkers {
    let mut result = Checkers {
        squares: [Square(0); 2],
        len: 0,
    };
    let pawn_back = if by == Color::White { -1 } else { 1 };
    for df in [-1, 1] {
        if let Some(from) = square.offset(df, pawn_back) {
            if has_piece(board, from, by, PieceKind::Pawn) && result.add::<LIMIT>(from) {
                return result;
            }
        }
    }
    for (df, dr) in KNIGHT {
        if let Some(from) = square.offset(df, dr) {
            if has_piece(board, from, by, PieceKind::Knight) && result.add::<LIMIT>(from) {
                return result;
            }
        }
    }
    for (direction, &(df, dr)) in DIRECTIONS.iter().enumerate() {
        let mut next = square.offset(df, dr);
        let mut adjacent = true;
        while let Some(from) = next {
            let piece = board[from.0 as usize];
            if !piece.is_empty() {
                if piece.color() == by {
                    let kind = piece.kind();
                    let slider = kind == PieceKind::Queen
                        || (direction < 4 && kind == PieceKind::Bishop)
                        || (direction >= 4 && kind == PieceKind::Rook);
                    if (slider || (adjacent && kind == PieceKind::King))
                        && result.add::<LIMIT>(from)
                    {
                        return result;
                    }
                }
                break;
            }
            adjacent = false;
            next = from.offset(df, dr);
        }
    }
    result
}

#[inline]
pub fn attacked(board: &[Piece; 64], square: Square, by: Color) -> bool {
    find_attackers::<1>(board, square, by).len != 0
}

#[inline]
pub fn in_check(position: &Position, side: Color) -> bool {
    let king = position.piece_squares(side, PieceKind::King)[0];
    attacked(&position.board, king, side.opponent())
}

/// Project just the fields needed for geometric king safety, not a semantic
/// Position transition. The caller has checked destination and special geometry.
#[inline]
fn legal_after(position: &Position, mv: Move, king: Square) -> bool {
    let mut board = position.board;
    let from = mv.from();
    let to = mv.to();
    let mover = board[from.0 as usize];
    board[from.0 as usize] = Piece::EMPTY;
    board[to.0 as usize] = mover;
    match mv.kind() {
        MoveKind::Ordinary => {}
        MoveKind::Promotion(kind) => {
            board[to.0 as usize] = Piece::new(position.side, kind);
        }
        MoveKind::EnPassant => {
            let behind = if position.side == Color::White {
                to.0 - 8
            } else {
                to.0 + 8
            };
            board[behind as usize] = Piece::EMPTY;
        }
        MoveKind::Castle => {
            let rank = from.rank() * 8;
            let (rook_from, rook_to) = if to.file() == 2 {
                (rank, rank + 3)
            } else {
                (rank + 7, rank + 5)
            };
            board[rook_to as usize] = board[rook_from as usize];
            board[rook_from as usize] = Piece::EMPTY;
        }
    }
    let king = if mover.kind() == PieceKind::King {
        to
    } else {
        king
    };
    !attacked(&board, king, position.side.opponent())
}

#[inline]
fn add_if_legal(position: &Position, list: &mut MoveList, king: Square, mv: Move) {
    if legal_after(position, mv, king) {
        list.push(mv);
    }
}

fn en_passant_prefix(position: &Position, list: &mut MoveList, king: Square) {
    if position.ep >= 64 {
        return;
    }
    let target = Square(position.ep);
    if !position.board[target.0 as usize].is_empty() {
        return;
    }
    let step = if position.side == Color::White { 1 } else { -1 };
    let Some(behind) = target.offset(0, -step) else {
        return;
    };
    let victim = position.board[behind.0 as usize];
    // Joined ingress accepts any opposing non-king piece behind the target.
    // Its exceptional king-victim command is an ingress outcome, not search.
    if victim.is_empty() || victim.color() == position.side || victim.kind() == PieceKind::King {
        return;
    }
    for df in [-1, 1] {
        if let Some(from) = target.offset(df, -step) {
            if has_piece(&position.board, from, position.side, PieceKind::Pawn) {
                add_if_legal(
                    position,
                    list,
                    king,
                    Move::new(from, target, MoveKind::EnPassant),
                );
            }
        }
    }
}

fn castles(position: &Position, list: &mut MoveList, king: Square, checked: bool) {
    if checked {
        return;
    }
    let (rank, long_right, short_right) = if position.side == Color::White {
        (0, 1, 2)
    } else {
        (56, 4, 8)
    };
    let home = Square(rank + 4);
    if king != home || !has_piece(&position.board, home, position.side, PieceKind::King) {
        return;
    }
    for (right, rook, transit, target, empty) in [
        (
            long_right,
            rank,
            rank + 3,
            rank + 2,
            [rank + 1, rank + 2, rank + 3],
        ),
        (
            short_right,
            rank + 7,
            rank + 5,
            rank + 6,
            [rank + 5, rank + 6, rank + 6],
        ),
    ] {
        if position.rights & right == 0
            || !has_piece(
                &position.board,
                Square(rook),
                position.side,
                PieceKind::Rook,
            )
            || empty
                .into_iter()
                .any(|s| !position.board[s as usize].is_empty())
        {
            continue;
        }
        if !legal_after(
            position,
            Move::new(home, Square(transit), MoveKind::Ordinary),
            king,
        ) {
            continue;
        }
        add_if_legal(
            position,
            list,
            king,
            Move::new(home, Square(target), MoveKind::Castle),
        );
    }
}

fn pawn_destination(
    position: &Position,
    list: &mut MoveList,
    king: Square,
    from: Square,
    to: Square,
) {
    if to.rank() == 0 || to.rank() == 7 {
        // Promotion type cannot alter whether an opposing piece attacks our
        // king: each choice has identical occupancy and color at the target.
        if legal_after(
            position,
            Move::new(from, to, MoveKind::Promotion(PieceKind::Queen)),
            king,
        ) {
            for kind in PROMOTIONS {
                list.push(Move::new(from, to, MoveKind::Promotion(kind)));
            }
        }
    } else {
        add_if_legal(
            position,
            list,
            king,
            Move::new(from, to, MoveKind::Ordinary),
        );
    }
}

fn pawns(position: &Position, list: &mut MoveList, king: Square) {
    let step = if position.side == Color::White { 1 } else { -1 };
    let files = if position.side == Color::White {
        [1, -1]
    } else {
        [-1, 1]
    };
    let initial_rank = if position.side == Color::White { 1 } else { 6 };
    for &from in position.piece_squares(position.side, PieceKind::Pawn) {
        for df in files {
            if let Some(to) = from.offset(df, step) {
                let victim = position.board[to.0 as usize];
                if !victim.is_empty()
                    && victim.color() != position.side
                    && victim.kind() != PieceKind::King
                {
                    pawn_destination(position, list, king, from, to);
                }
            }
        }
        if let Some(to) = from.offset(0, step) {
            if position.board[to.0 as usize].is_empty() {
                pawn_destination(position, list, king, from, to);
                if from.rank() == initial_rank {
                    let twice = from.offset(0, 2 * step).unwrap();
                    if position.board[twice.0 as usize].is_empty() {
                        add_if_legal(
                            position,
                            list,
                            king,
                            Move::new(from, twice, MoveKind::Ordinary),
                        );
                    }
                }
            }
        }
    }
}

fn pieces(position: &Position, list: &mut MoveList, king: Square, kind: PieceKind) {
    let directions: &[(i8, i8)] = match kind {
        PieceKind::Knight => &KNIGHT,
        PieceKind::Bishop => &DIRECTIONS[..4],
        PieceKind::Rook => &DIRECTIONS[4..],
        PieceKind::Queen | PieceKind::King => &DIRECTIONS,
        PieceKind::Pawn => unreachable!(),
    };
    let sliding = matches!(kind, PieceKind::Bishop | PieceKind::Rook | PieceKind::Queen);
    for &from in position.piece_squares(position.side, kind) {
        for &(df, dr) in directions {
            let mut next = from.offset(df, dr);
            while let Some(to) = next {
                let victim = position.board[to.0 as usize];
                if !victim.is_empty()
                    && (victim.color() == position.side || victim.kind() == PieceKind::King)
                {
                    break;
                }
                add_if_legal(
                    position,
                    list,
                    king,
                    Move::new(from, to, MoveKind::Ordinary),
                );
                if !sliding || !victim.is_empty() {
                    break;
                }
                next = to.offset(df, dr);
            }
        }
    }
}

fn prefix_matching(
    list: &mut MoveList,
    next: &mut usize,
    end: usize,
    predicate: impl Fn(Move) -> bool,
) {
    let mut cursor = *next;
    while cursor < end {
        let mv = list.moves[cursor];
        if predicate(mv) {
            list.moves.copy_within(*next..cursor, *next + 1);
            list.moves[*next] = mv;
            *next += 1;
        }
        cursor += 1;
    }
}

fn single_check_pawn_prefix(
    list: &mut MoveList,
    start: usize,
    end: usize,
    king: Square,
    checker: Square,
    side: Color,
) {
    let mut next = start;
    let df = checker.file() as i8 - king.file() as i8;
    let dr = checker.rank() as i8 - king.rank() as i8;
    if df == 0 || dr == 0 || df.abs() == dr.abs() {
        let mut between = king.offset(df.signum(), dr.signum());
        while let Some(square) = between {
            if square == checker {
                break;
            }
            prefix_matching(list, &mut next, end, |mv| mv.to() == square);
            between = square.offset(df.signum(), dr.signum());
        }
    }
    for index in 0..8 {
        let file = if side == Color::White {
            index
        } else {
            7 - index
        };
        prefix_matching(list, &mut next, end, |mv| {
            mv.to() == checker && mv.from().file() == file
        });
    }
}

/// Complete legal root/non-root base order, including search-specific prefixes.
/// This does not apply ordinary learned/hash/capture ranking.
pub fn generate_legal(position: &Position, list: &mut MoveList) {
    list.clear();
    let king = position.piece_squares(position.side, PieceKind::King)[0];
    let checkers = find_attackers::<2>(&position.board, king, position.side.opponent());
    en_passant_prefix(position, list, king);
    castles(position, list, king, checkers.len != 0);
    let pawn_start = list.len;
    pawns(position, list, king);
    if checkers.len == 1 {
        let pawn_end = list.len;
        single_check_pawn_prefix(
            list,
            pawn_start,
            pawn_end,
            king,
            checkers.squares[0],
            position.side,
        );
    }
    // Do not shortcut double check to king-only here: the broader joined EP
    // transition can remove a non-pawn checker and simultaneously block a ray.
    for kind in [
        PieceKind::Knight,
        PieceKind::Bishop,
        PieceKind::Rook,
        PieceKind::Queen,
        PieceKind::King,
    ] {
        pieces(position, list, king, kind);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn inventory(fen: &str) -> Vec<String> {
        let position = Position::from_fen(fen).unwrap();
        let mut moves = MoveList::new();
        generate_legal(&position, &mut moves);
        moves.as_slice().iter().map(ToString::to_string).collect()
    }

    fn perft(position: &Position, depth: u8) -> u64 {
        if depth == 0 {
            return 1;
        }
        let mut moves = MoveList::new();
        generate_legal(position, &mut moves);
        if depth == 1 {
            return moves.len as u64;
        }
        moves
            .as_slice()
            .iter()
            .map(|&mv| perft(&position.played_unchecked(mv), depth - 1))
            .sum()
    }

    #[test]
    fn initial_order_and_legal_tree() {
        let mut expected = Vec::new();
        for file in b'a'..=b'h' {
            expected.push(format!("{}2{}3", file as char, file as char));
            expected.push(format!("{}2{}4", file as char, file as char));
        }
        expected.extend(["b1c3", "b1a3", "g1h3", "g1f3"].map(str::to_owned));
        assert_eq!(inventory(START), expected);
        let position = Position::from_fen(START).unwrap();
        for (depth, count) in [(1, 20), (2, 400), (3, 8902), (4, 197281)] {
            assert_eq!(perft(&position, depth), count, "depth {depth}");
        }
    }

    #[test]
    fn castling_and_promotion_order() {
        let castles = inventory("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
        assert_eq!(&castles[..2], ["e1c1", "e1g1"]);
        let promotions = inventory("1r2k3/P7/8/8/8/8/8/4K3 w - - 0 1");
        assert_eq!(
            &promotions[..8],
            ["a7b8q", "a7b8r", "a7b8b", "a7b8n", "a7a8q", "a7a8r", "a7a8b", "a7a8n"]
        );
        let checked = inventory("4k3/8/8/8/8/8/8/r3K2R w K - 0 1");
        assert!(!checked.iter().any(|mv| mv == "e1g1"));
    }

    #[test]
    fn single_check_prefixes_match_released_examples() {
        // Generated inventories from the corresponding released candidate
        // production examples, before ordinary preference ordering.
        assert_eq!(
            inventory("4k3/8/8/1b6/P7/8/2PPK3/8 w - - 0 1"),
            ["d2d3", "c2c4", "a4b5", "e2f3", "e2d1", "e2e3", "e2e1", "e2f2"]
        );
        assert_eq!(
            inventory("k7/8/8/8/3n4/2P1PK2/8/8 w - - 0 1"),
            ["c3d4", "e3d4", "f3g4", "f3e4", "f3g2", "f3f4", "f3f2", "f3g3"]
        );
        assert_eq!(
            inventory("8/8/2p1pk2/3N4/8/8/8/K7 b - - 0 1"),
            ["e6d5", "c6d5", "f6g7", "f6e5", "f6g5", "f6f7", "f6f5", "f6g6"]
        );
        assert_eq!(
            inventory("4r1k1/8/8/8/1b6/8/8/4K3 w - - 0 1"),
            ["e1f2", "e1f1", "e1d1"]
        );
    }

    #[test]
    fn joined_en_passant_geometry_and_self_check() {
        let mut position = Position::from_fen("4k3/8/8/2PnP3/8/8/8/4K3 w - d6 0 1").unwrap();
        position.squares[Color::White.index()].swap(0, 1);
        let mut moves = MoveList::new();
        generate_legal(&position, &mut moves);
        assert_eq!(moves.moves[0].to_string(), "c5d6");
        assert_eq!(moves.moves[1].to_string(), "e5d6");
        assert_eq!(moves.moves[0].kind(), MoveKind::EnPassant);
        assert!(!inventory("k7/8/8/4KPpr/8/8/8/8 w - g6 0 1")
            .iter()
            .any(|mv| mv == "f5g6"));

        // The joined non-pawn victim rule makes a non-king evasion possible
        // here even though a knight and bishop both check the king.
        let double = Position::from_fen("1b5k/8/8/2Pn4/5K2/8/8/8 w - d6 0 1").unwrap();
        let king = double.piece_squares(Color::White, PieceKind::King)[0];
        assert_eq!(
            find_attackers::<2>(&double.board, king, Color::Black).len,
            2
        );
        generate_legal(&double, &mut moves);
        assert_eq!(moves.moves[0].to_string(), "c5d6");
        let child = double.played_unchecked(moves.moves[0]);
        assert!(!in_check(&child, Color::White));
    }

    #[test]
    fn pinned_attackers_remain_geometric_and_projected_moves_restore_parent() {
        let pinned = Position::from_fen("4k3/4n3/8/8/6K1/8/8/4Q3 w - - 0 1").unwrap();
        assert!(attacked(
            &pinned.board,
            Square::parse("f5").unwrap(),
            Color::Black
        ));
        assert!(!inventory("4k3/4n3/8/8/6K1/8/8/4Q3 w - - 0 1")
            .iter()
            .any(|mv| mv == "g4f5"));

        for fen in [
            START,
            "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
            "1r2k3/P7/8/8/8/8/8/4K3 w - - 0 1",
            "4k3/8/8/2PnP3/8/8/8/4K3 w - d6 0 1",
        ] {
            let position = Position::from_fen(fen).unwrap();
            let original = position.board;
            let king = position.piece_squares(position.side, PieceKind::King)[0];
            let mut moves = MoveList::new();
            generate_legal(&position, &mut moves);
            for &mv in moves.as_slice() {
                let child = position.played_unchecked(mv);
                assert_eq!(
                    legal_after(&position, mv, king),
                    !in_check(&child, position.side),
                    "{fen}: {mv}"
                );
                assert_eq!(position.board, original);
            }
        }

        for (fen, from, to, kind) in [
            (
                "k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1",
                "e2",
                "f2",
                MoveKind::Ordinary,
            ),
            (
                "k7/8/8/4KPpr/8/8/8/8 w - g6 0 1",
                "f5",
                "g6",
                MoveKind::EnPassant,
            ),
        ] {
            let position = Position::from_fen(fen).unwrap();
            let king = position.piece_squares(position.side, PieceKind::King)[0];
            let mv = Move::new(
                Square::parse(from).unwrap(),
                Square::parse(to).unwrap(),
                kind,
            );
            let child = position.played_unchecked(mv);
            assert!(!legal_after(&position, mv, king), "{fen}: {mv}");
            assert!(in_check(&child, position.side), "{fen}: {mv}");
        }
    }
}
