//! Placement-owned exact Piece-tag planes for geometric queries.
//! Capped ordered checker identities and evaluation influence keep separate owners.
use crate::geometry::{DIRECTIONS, KNIGHT, KNIGHT_SOURCES};
use crate::position::Position;
use crate::types::{Color, Move, MoveKind, Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct AttackBits {
    planes: [u64; 4],
}

#[repr(align(64))]
struct Masks {
    knight: [u64; 64],
    king: [u64; 64],
    pawn_sources: [[u64; 64]; 2],
    rays: [[u64; 8]; 64],
    increasing: [bool; 8],
}

const fn masks() -> Masks {
    let mut result = Masks {
        knight: [0; 64],
        king: [0; 64],
        pawn_sources: [[0; 64]; 2],
        rays: [[0; 8]; 64],
        increasing: [false; 8],
    };
    let mut index = 0;
    while index < 64 {
        let square = Square(index as u8);
        let mut direction = 0;
        while direction < 8 {
            let (df, dr) = DIRECTIONS[direction];
            result.increasing[direction] = df as i16 + 8 * dr as i16 > 0;
            if let Some(target) = square.offset(df, dr) {
                result.king[index] |= 1u64 << target.0;
            }
            let mut cursor = square;
            while let Some(target) = cursor.offset(df, dr) {
                result.rays[index][direction] |= 1u64 << target.0;
                cursor = target;
            }
            let (df, dr) = KNIGHT[direction];
            if let Some(target) = square.offset(df, dr) {
                result.knight[index] |= 1u64 << target.0;
            }
            direction += 1;
        }
        let mut side = 0;
        while side < 2 {
            let back = if side == 0 { -1 } else { 1 };
            if let Some(target) = square.offset(-1, back) {
                result.pawn_sources[side][index] |= 1u64 << target.0;
            }
            if let Some(target) = square.offset(1, back) {
                result.pawn_sources[side][index] |= 1u64 << target.0;
            }
            side += 1;
        }
        index += 1;
    }
    result
}

static MASKS: Masks = masks();

/// Existing immutable geometry for the private coherent evaluation producer.
/// Return references, not a copied per-source ray row or a rebuilt table.
#[inline]
pub(crate) fn influence_rays(square: Square) -> (&'static [u64; 8], &'static [bool; 8]) {
    (&MASKS.rays[square.0 as usize], &MASKS.increasing)
}

impl AttackBits {
    #[inline]
    pub(crate) fn planes(&self) -> &[u64; 4] {
        &self.planes
    }

    pub(crate) const fn empty() -> Self {
        Self { planes: [0; 4] }
    }

    /// Reconstruction uses OR from actual tags, independently of replacement.
    pub(crate) fn from_board(board: &[Piece; 64]) -> Self {
        let mut result = Self::empty();
        for (index, piece) in board.iter().enumerate() {
            if piece.is_empty() {
                continue;
            }
            let square = 1u64 << index;
            for bit in 0..4 {
                if piece.0 & (1 << bit) != 0 {
                    result.planes[bit] |= square;
                }
            }
        }
        result
    }

    /// Local supply can gather ordered lists; the Boolean kernel is identical.
    pub(crate) fn from_position(position: &Position) -> Self {
        let mut result = Self::empty();
        for side in [Color::White, Color::Black] {
            for kind in PieceKind::ALL {
                let mut squares = 0;
                for square in position.piece_squares(side, kind) {
                    squares |= 1u64 << square.0;
                }
                let piece = Piece::new(side, kind);
                for bit in 0..4 {
                    if piece.0 & (1 << bit) != 0 {
                        result.planes[bit] |= squares;
                    }
                }
            }
        }
        result
    }

    #[inline]
    pub(crate) fn replace(&mut self, square: Square, old: Piece, next: Piece) {
        let changed = old.0 ^ next.0;
        let mask = 1u64 << square.0;
        for bit in 0..4 {
            self.planes[bit] ^= mask & 0u64.wrapping_sub(((changed >> bit) & 1) as u64);
        }
    }

    /// Decode each tag and compare with the mailbox; do not call the updater.
    pub(crate) fn matches_board(&self, board: &[Piece; 64]) -> bool {
        board.iter().enumerate().all(|(square, piece)| {
            let mut tag = 0u8;
            for bit in 0..4 {
                tag |= (((self.planes[bit] >> square) & 1) as u8) << bit;
            }
            tag == piece.0
        })
    }

    #[inline]
    pub(crate) fn attacked(&self, square: Square, by: Color) -> bool {
        let [a, b, c, black] = self.planes;
        let color = if by == Color::Black { black } else { !black };
        let pawns = a & !b & !c & color;
        let knights = !a & b & !c & color;
        let kings = !a & b & c & color;
        let index = square.0 as usize;
        if (pawns & MASKS.pawn_sources[by.index()][index])
            | (knights & MASKS.knight[index])
            | (kings & MASKS.king[index])
            != 0
        {
            return true;
        }
        let diagonal = a & (b ^ c) & color; // Bishop3 or Queen5.
        let orthogonal = c & !b & color; // Rook4 or Queen5.
        if diagonal | orthogonal == 0 {
            return false;
        }
        let occupied = a | b | c;
        for direction in 0..8 {
            let matching = if direction < 4 { diagonal } else { orthogonal };
            let ray_mask = MASKS.rays[index][direction];
            if matching & ray_mask == 0 {
                continue;
            }
            let on_ray = occupied & ray_mask;
            debug_assert_ne!(on_ray, 0);
            let first = if MASKS.increasing[direction] {
                on_ray & on_ray.wrapping_neg()
            } else {
                1u64 << (63 - on_ray.leading_zeros())
            };
            if matching & first != 0 {
                return true;
            }
        }
        false
    }

    /// Capped geometric identities in the mailbox checker's exact order.
    /// This reads the existing placement planes; it does not rebuild a view.
    #[inline]
    pub(crate) fn ordered_attackers<const LIMIT: usize>(
        &self,
        square: Square,
        by: Color,
    ) -> ([Square; 2], usize) {
        debug_assert!((1..=2).contains(&LIMIT));
        let [a, b, c, black] = self.planes;
        let color = if by == Color::Black { black } else { !black };
        let index = square.0 as usize;
        let pawns = a & !b & !c & color;
        let knights = !a & b & !c & color;
        let adjacent_kings = !a & b & c & color & MASKS.king[index];
        let diagonal = a & (b ^ c) & color;
        let orthogonal = c & !b & color;
        let occupied = a | b | c;
        let mut result = ([Square(0); 2], 0usize);
        let mut emit = |source| {
            result.0[result.1] = source;
            result.1 += 1;
            result.1 == LIMIT
        };

        // The two pawn sources share a rank. Numeric order is exactly the
        // mailbox's source-file offsets [-1,+1] for either attacking color.
        let mut pawn_hits = pawns & MASKS.pawn_sources[by.index()][index];
        while pawn_hits != 0 {
            let source = Square(pawn_hits.trailing_zeros() as u8);
            if emit(source) {
                return result;
            }
            pawn_hits &= pawn_hits - 1;
        }
        let knight_hits = knights & MASKS.knight[index];
        if knight_hits != 0 {
            let leaps = &KNIGHT_SOURCES[index];
            for &source in &leaps.squares[..leaps.len as usize] {
                if knight_hits & (1u64 << source) != 0 && emit(Square(source)) {
                    return result;
                }
            }
        }
        // An adjacent king participates at its ray's original position, after
        // pawns/knights, rather than ahead of earlier-direction sliders.
        for direction in 0..8 {
            let matching = adjacent_kings | if direction < 4 { diagonal } else { orthogonal };
            let ray = MASKS.rays[index][direction];
            if matching & ray == 0 {
                continue;
            }
            let blockers = occupied & ray;
            debug_assert_ne!(blockers, 0);
            let first = if MASKS.increasing[direction] {
                blockers & blockers.wrapping_neg()
            } else {
                1u64 << (63 - blockers.leading_zeros())
            };
            if matching & first != 0 && emit(Square(first.trailing_zeros() as u8)) {
                return result;
            }
        }
        result
    }

    #[inline]
    pub(crate) fn projected(mut self, position: &Position, movement: Move) -> Self {
        let from = movement.from();
        let to = movement.to();
        let mover = position.board[from.0 as usize];
        self.replace(from, mover, Piece::EMPTY);
        let next = match movement.kind() {
            MoveKind::Promotion(kind) => Piece::new(position.side, kind),
            _ => mover,
        };
        self.replace(to, position.board[to.0 as usize], next);
        match movement.kind() {
            MoveKind::EnPassant => {
                let victim = Square(if position.side == Color::White {
                    to.0 - 8
                } else {
                    to.0 + 8
                });
                self.replace(victim, position.board[victim.0 as usize], Piece::EMPTY);
            }
            MoveKind::Castle => {
                let base = from.rank() * 8;
                let (rook_from, rook_to) = if to.file() == 2 {
                    (base, base + 3)
                } else {
                    (base + 7, base + 5)
                };
                let rook = position.board[rook_from as usize];
                self.replace(Square(rook_from), rook, Piece::EMPTY);
                self.replace(Square(rook_to), position.board[rook_to as usize], rook);
            }
            _ => {}
        }
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::movegen::{self, MoveList};

    #[test]
    fn every_tag_replacement_matches_independent_mailbox_decode() {
        let pieces: Vec<_> = std::iter::once(Piece::EMPTY)
            .chain([Color::White, Color::Black].into_iter().flat_map(|side| {
                PieceKind::ALL
                    .into_iter()
                    .map(move |kind| Piece::new(side, kind))
            }))
            .collect();
        for square in 0..64 {
            for old in &pieces {
                let mut board = [Piece::EMPTY; 64];
                board[square] = *old;
                let before = AttackBits::from_board(&board);
                for next in &pieces {
                    let mut changed = before;
                    changed.replace(Square(square as u8), *old, *next);
                    board[square] = *next;
                    assert!(changed.matches_board(&board));
                    assert!(before.matches_board(&{
                        let mut b = board;
                        b[square] = *old;
                        b
                    }));
                }
            }
        }
    }

    fn random(state: &mut u64) -> u64 {
        *state ^= *state << 13;
        *state ^= *state >> 7;
        *state ^= *state << 17;
        *state
    }
    fn empty_square(board: &[Piece; 64], state: &mut u64, pawn: bool) -> usize {
        loop {
            let square = random(state) as usize % 64;
            if board[square].is_empty() && (!pawn || (8..56).contains(&square)) {
                return square;
            }
        }
    }
    fn constructed(state: &mut u64) -> Position {
        let mut board = [Piece::EMPTY; 64];
        for side in [Color::White, Color::Black] {
            let square = empty_square(&board, state, false);
            board[square] = Piece::new(side, PieceKind::King);
            let mut pawns = 0;
            for _ in 0..(random(state) % 16) {
                let mut kind = PieceKind::ALL[random(state) as usize % 5];
                if kind == PieceKind::Pawn && pawns == 8 {
                    kind = PieceKind::Knight;
                }
                if kind == PieceKind::Pawn {
                    pawns += 1;
                }
                let square = empty_square(&board, state, kind == PieceKind::Pawn);
                board[square] = Piece::new(side, kind);
            }
        }
        let mut placement = String::new();
        for rank in (0..8).rev() {
            if rank != 7 {
                placement.push('/');
            }
            let mut empty = 0u8;
            for file in 0..8 {
                let piece = board[rank * 8 + file];
                if piece.is_empty() {
                    empty += 1;
                    continue;
                }
                if empty != 0 {
                    placement.push((b'0' + empty) as char);
                    empty = 0;
                }
                placement.push(piece.fen_char());
            }
            if empty != 0 {
                placement.push((b'0' + empty) as char);
            }
        }
        Position::from_fen(&format!(
            "{placement} {} KQkq - 0 1",
            if random(state) & 1 == 0 { "w" } else { "b" }
        ))
        .unwrap()
    }

    #[test]
    fn boolean_queries_and_projections_match_mailbox_on_broad_setups() {
        let mut state = 0x9e3779b97f4a7c15;
        for iteration in 0..10000 {
            let position = constructed(&mut state);
            let bits = position.attack_view();
            assert!(bits.matches_board(&position.board));
            assert_eq!(bits, AttackBits::from_position(&position));
            assert_eq!(bits, AttackBits::from_board(&position.board));
            for side in [Color::White, Color::Black] {
                for square in 0..64 {
                    assert_eq!(
                        bits.attacked(Square(square), side),
                        movegen::attacked(&position.board, Square(square), side)
                    );
                }
            }
            if iteration < 500 {
                let mut moves = MoveList::new();
                movegen::generate_legal(&position, &mut moves);
                for &movement in moves.as_slice() {
                    let projected = bits.projected(&position, movement);
                    let board = movegen::projected_board(&position, movement);
                    assert!(projected.matches_board(&board));
                    let child = position.played_unchecked(movement);
                    child.validate().unwrap();
                    assert_eq!(child.attack_view(), projected);
                    assert!(child.null_child().attack_view().matches_board(&board));
                }
            }
        }
    }

    #[test]
    fn special_and_joined_projections_keep_actual_tags() {
        for (fen, spelling, kind) in [
            (
                "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
                "e1c1",
                MoveKind::Castle,
            ),
            (
                "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1",
                "e8g8",
                MoveKind::Castle,
            ),
            (
                "1r2k3/P7/8/8/8/8/8/4K3 w - - 0 1",
                "a7b8",
                MoveKind::Promotion(PieceKind::Knight),
            ),
            (
                "4k3/8/8/8/8/8/p7/4K3 b - - 0 1",
                "a2a1",
                MoveKind::Promotion(PieceKind::Queen),
            ),
            (
                "k7/8/8/4KPnr/8/8/8/8 w - g6 0 1",
                "f5g6",
                MoveKind::EnPassant,
            ),
            (
                "7k/8/8/8/8/8/3rP3/K7 w - d3 0 1",
                "e2d3",
                MoveKind::EnPassant,
            ),
            (
                "8/8/8/3kP3/8/8/8/K7 w - d6 0 1",
                "e5d6",
                MoveKind::EnPassant,
            ),
        ] {
            let position = Position::from_fen(fen).unwrap();
            let movement = Move::new(
                Square::parse(&spelling[..2]).unwrap(),
                Square::parse(&spelling[2..]).unwrap(),
                kind,
            );
            let projected = position.attack_view().projected(&position, movement);
            let board = movegen::projected_board(&position, movement);
            assert!(projected.matches_board(&board));
            for side in [Color::White, Color::Black] {
                for square in 0..64 {
                    assert_eq!(
                        projected.attacked(Square(square), side),
                        movegen::attacked(&board, Square(square), side)
                    );
                }
            }
            let child = if fen.starts_with("8/8/8/3kP3") {
                position.exceptional_en_passant(movement)
            } else {
                position.played_unchecked(movement)
            };
            assert!(child.attack_view().matches_board(&board));
            assert_eq!(child.attack_view(), projected);
        }
    }
    /// Compare before own-king legality: rejecting a pseudo-candidate first
    /// would miss the Q path's optimistic-update/unsafe-capture obligation.
    fn compare_pseudo_projection(position: &Position, movement: Move, exhaustive: bool) -> bool {
        let parent = position.attack_view();
        let projected = parent.projected(position, movement);
        let board = movegen::projected_board(position, movement);
        assert!(parent.matches_board(&position.board));
        assert!(projected.matches_board(&board));
        assert_eq!(position.attack_view(), parent);
        let enemy_king = position.piece_squares(position.side.opponent(), PieceKind::King)[0];
        let old = movegen::mailbox_ordered_attackers_for_test::<2>(&board, enemy_king, position.side);
        assert_eq!(projected.ordered_attackers::<2>(enemy_king, position.side), old,
            "Q identities {movement} in {}", position.placement());
        assert_eq!(movegen::check_routes_bits(&projected, enemy_king, position.side, movement.to()),
            movegen::check_routes(&board, enemy_king, position.side, movement.to()),
            "Q routes {movement} in {}", position.placement());
        let own_king = if position.board[movement.from().0 as usize].kind() == PieceKind::King {
            movement.to()
        } else { position.piece_squares(position.side, PieceKind::King)[0] };
        let unsafe_move = movegen::attacked(&board, own_king, position.side.opponent());
        assert_eq!(projected.attacked(own_king, position.side.opponent()), unsafe_move,
            "Q safety {movement} in {}", position.placement());
        if exhaustive {
            for side in [Color::White, Color::Black] {
                for square in 0..64 {
                    let target = Square(square);
                    assert_eq!(projected.ordered_attackers::<1>(target, side),
                        movegen::mailbox_ordered_attackers_for_test::<1>(&board, target, side));
                    assert_eq!(projected.ordered_attackers::<2>(target, side),
                        movegen::mailbox_ordered_attackers_for_test::<2>(&board, target, side));
                    assert_eq!(projected.attacked(target, side), movegen::attacked(&board, target, side));
                    assert_eq!(movegen::check_routes_bits(&projected, target, side, movement.to()),
                        movegen::check_routes(&board, target, side, movement.to()));
                }
            }
        }
        unsafe_move
    }

    #[test]
    fn every_pseudo_tactical_projection_matches_mailbox_before_legality_on_broad_setups() {
        let mut state = 0x63de_492b_18a7_f50d;
        let mut candidates = 0usize;
        let mut unsafe_candidates = 0usize;
        for iteration in 0..10000 {
            let position = constructed(&mut state);
            let mut moves = MoveList::new();
            crate::tactical::generate(&position, &mut moves);
            for &movement in moves.as_slice() {
                candidates += 1;
                unsafe_candidates += usize::from(compare_pseudo_projection(&position, movement, iteration < 500));
            }
        }
        assert!(candidates > 0);
        assert!(unsafe_candidates > 0, "broad pseudo coverage must not silently become legal-only");
    }

    #[test]
    fn fixed_pseudo_projection_keeps_unsafe_special_tags_and_exact_capped_routes() {
        for (fen, spelling, unsafe_move) in [
            ("k3r3/8/8/8/8/8/4R2p/4K3 w - - 0 1", "e2h2", true),
            // c7/f2 block bishop rays to their own kings before promotion.
            ("1b5k/2P5/8/8/8/8/7K/8 w - - 0 1", "c7c8q", true),
            ("1b5k/2P5/8/8/8/8/7K/8 w - - 0 1", "c7b8q", false),
            ("8/k7/8/8/8/8/5p2/K5B1 b - - 0 1", "f2f1q", true),
            ("8/k7/8/8/8/8/5p2/K5B1 b - - 0 1", "f2g1q", false),
            // Joined EP removes an actual non-pawn blocker, for both colors.
            ("k7/8/8/4KPnr/8/8/8/8 w - g6 0 1", "f5g6", true),
            ("8/8/8/8/RNpk4/8/8/7K b - b3 0 1", "c4b3", true),
            ("7k/8/8/8/8/8/3rP3/K7 w - d3 0 1", "e2d3", false),
            ("7k/3pR3/8/8/8/8/8/K7 b - e6 0 1", "d7e6", false),
        ] {
            let position = Position::from_fen(fen).unwrap();
            let mut moves = MoveList::new();crate::tactical::generate(&position, &mut moves);
            let movement = *moves.as_slice().iter().find(|m| m.to_string() == spelling)
                .unwrap_or_else(|| panic!("missing pseudo-candidate {spelling} in {fen}"));
            assert_eq!(compare_pseudo_projection(&position, movement, true), unsafe_move, "{fen}/{spelling}");
        }
        for (fen, spelling, expected, flags, unsafe_move) in [
            // The moved rook is a third route: first pawn, then knight stop
            // discovery. All-attackers membership would wrongly return true.
            ("4k3/3P4/5N2/8/8/8/R7/K7 w - - 0 1", "a2e2", ["d7", "f6"], (true, false), false),
            // KNIGHT_SOURCES, not numeric square order, emits f6 before d2.
            ("8/8/5N2/8/4k3/8/8/K4N2 w - - 0 1", "f1d2", ["f6", "d2"], (true, true), false),
            // An unsafe king capture still participates at its ray's position,
            // after the earlier diagonal bishop, rather than before sliders.
            ("8/8/6B1/8/4k3/2Kp4/8/8 w - - 0 1", "c3d3", ["g6", "d3"], (true, true), true),
        ] {
            let position = Position::from_fen(fen).unwrap();
            let mut moves = MoveList::new();crate::tactical::generate(&position, &mut moves);
            let movement = *moves.as_slice().iter().find(|m| m.to_string() == spelling)
                .unwrap_or_else(|| panic!("missing capped-route pseudo-candidate {spelling} in {fen}"));
            assert_eq!(compare_pseudo_projection(&position, movement, true), unsafe_move);
            let projected = position.attack_view().projected(&position, movement);
            let king = position.piece_squares(position.side.opponent(), PieceKind::King)[0];
            let old_board = movegen::projected_board(&position, movement);
            let old = movegen::mailbox_ordered_attackers_for_test::<2>(&old_board, king, position.side);
            assert_eq!(old.1, 2);
            assert_eq!(old.0, expected.map(|name| Square::parse(name).unwrap()));
            assert_eq!(projected.ordered_attackers::<2>(king, position.side), old);
            assert_eq!(movegen::check_routes_bits(&projected, king, position.side, movement.to()), flags);
        }
    }

}
