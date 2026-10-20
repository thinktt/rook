//! Complete ordered-vector controls against frozen43 coordinate generation.
//! Legacy code below is cfg(test)-only; expected vectors do not use new masks.
use crate::movegen::{MoveList, MOVE_CAPACITY};
use crate::position::Position;
use crate::types::{Color, Move, MoveKind, Piece, PieceKind, Square};

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

fn legacy_generate(position: &Position, out: &mut MoveList) {
    out.clear();
    let side = position.side;
    let enemy_king = position.piece_squares(side.opponent(), PieceKind::King)[0];
    let forward = if side == Color::White { 1 } else { -1 };
    let source_rank = -forward;
    let prefix_files = if side == Color::White {
        [-1, 1]
    } else {
        [1, -1]
    };
    if position.ep < 64 {
        let target = Square(position.ep);
        if position.board[target.0 as usize].is_empty() {
            if let Some(victim_square) = target.offset(0, source_rank) {
                let victim = position.board[victim_square.0 as usize];
                // Joined setups can retain a non-pawn victim; king removal is a cold path.
                if !victim.is_empty() && victim.color() != side && victim.kind() != PieceKind::King
                {
                    for file in prefix_files {
                        if let Some(source) = target.offset(file, source_rank) {
                            let piece = position.board[source.0 as usize];
                            if !piece.is_empty()
                                && piece.color() == side
                                && piece.kind() == PieceKind::Pawn
                            {
                                out.push(Move::new(source, target, MoveKind::EnPassant));
                            }
                        }
                    }
                }
            }
        }
    }
    // Quiet pawn checks precede other pawn moves in fixed target geometry.
    for file in prefix_files {
        if let Some(target) = enemy_king.offset(file, source_rank) {
            if !position.board[target.0 as usize].is_empty() {
                continue;
            }
            if let Some(source) = target.offset(0, source_rank) {
                let piece = position.board[source.0 as usize];
                if !piece.is_empty() && piece.color() == side && piece.kind() == PieceKind::Pawn {
                    out.push(Move::new(source, target, MoveKind::Ordinary));
                }
            }
        }
    }
    let prefix_len = out.len;
    let capture_files = if side == Color::White {
        [1, -1]
    } else {
        [-1, 1]
    };
    for &source in position.piece_squares(side, PieceKind::Pawn) {
        let quiet = source
            .offset(0, forward)
            .filter(|to| position.board[to.0 as usize].is_empty());
        let promotes = quiet.is_some_and(|to| to.rank() == 0 || to.rank() == 7);
        // For one pawn, quiet queen promotion precedes its capture promotions.
        if promotes {
            out.push(Move::new(
                source,
                quiet.unwrap(),
                MoveKind::Promotion(PieceKind::Queen),
            ));
        }
        for file in capture_files {
            let Some(target) = source.offset(file, forward) else {
                continue;
            };
            let victim = position.board[target.0 as usize];
            if victim.is_empty() || victim.color() == side || victim.kind() == PieceKind::King {
                continue;
            }
            let kind = if target.rank() == 0 || target.rank() == 7 {
                MoveKind::Promotion(PieceKind::Queen)
            } else {
                MoveKind::Ordinary
            };
            out.push(Move::new(source, target, kind));
        }
        if !promotes {
            if let Some(target) = quiet {
                let movement = Move::new(source, target, MoveKind::Ordinary);
                if !out.moves[..prefix_len].contains(&movement)
                    && direct_check(position, source, target, PieceKind::Pawn, enemy_king)
                {
                    out.push(movement);
                }
            }
        }
    }
    for kind in [
        PieceKind::Knight,
        PieceKind::Bishop,
        PieceKind::Rook,
        PieceKind::Queen,
        PieceKind::King,
    ] {
        let directions: &[(i8, i8)] = match kind {
            PieceKind::Knight => &KNIGHT,
            PieceKind::Bishop => &DIRECTIONS[..4],
            PieceKind::Rook => &DIRECTIONS[4..],
            _ => &DIRECTIONS,
        };
        let sliding = matches!(kind, PieceKind::Bishop | PieceKind::Rook | PieceKind::Queen);
        for &source in position.piece_squares(side, kind) {
            for &(df, dr) in directions {
                let mut cursor = source;
                while let Some(target) = cursor.offset(df, dr) {
                    let victim = position.board[target.0 as usize];
                    if !victim.is_empty() {
                        if victim.color() != side && victim.kind() != PieceKind::King {
                            out.push(Move::new(source, target, MoveKind::Ordinary));
                        }
                        break;
                    }
                    if kind != PieceKind::King
                        && direct_check(position, source, target, kind, enemy_king)
                    {
                        out.push(Move::new(source, target, MoveKind::Ordinary));
                    }
                    if !sliding {
                        break;
                    }
                    cursor = target;
                }
            }
        }
    }
}

/// Only the moved piece is considered; other pieces' discovered checks do not qualify.
fn direct_check(
    position: &Position,
    source: Square,
    target: Square,
    kind: PieceKind,
    enemy_king: Square,
) -> bool {
    let df = enemy_king.file() as i8 - target.file() as i8;
    let dr = enemy_king.rank() as i8 - target.rank() as i8;
    match kind {
        PieceKind::Pawn => {
            return df.abs() == 1 && dr == if position.side == Color::White { 1 } else { -1 }
        }
        PieceKind::Knight => return df.abs() * dr.abs() == 2,
        PieceKind::Bishop if df.abs() != dr.abs() => return false,
        PieceKind::Rook if df != 0 && dr != 0 => return false,
        PieceKind::Queen if df != 0 && dr != 0 && df.abs() != dr.abs() => return false,
        PieceKind::King => return false,
        _ => {}
    }
    if df == 0 && dr == 0 {
        return false;
    }
    let step = (df.signum(), dr.signum());
    let mut cursor = target;
    while let Some(square) = cursor.offset(step.0, step.1) {
        if square == enemy_king {
            return true;
        }
        if square != source && !position.board[square.0 as usize].is_empty() {
            return false;
        }
        cursor = square;
    }
    false
}


fn sq(text: &str) -> Square { Square::parse(text).unwrap() }
fn ordinary(from: &str, to: &str) -> Move { Move::new(sq(from), sq(to), MoveKind::Ordinary) }
fn from_board(board: [Piece; 64], side: Color) -> Position {
    let mut fen = String::new();
    for rank in (0..8).rev() {
        if rank != 7 { fen.push('/'); }
        let mut empty = 0u8;
        for file in 0..8 {
            let piece = board[rank * 8 + file];
            if piece.is_empty() { empty += 1; }
            else {
                if empty != 0 { fen.push(char::from(b'0' + empty)); empty = 0; }
                fen.push(piece.fen_char());
            }
        }
        if empty != 0 { fen.push(char::from(b'0' + empty)); }
    }
    Position::from_fen(&format!("{fen} {} - - 0 1", if side == Color::White { "w" } else { "b" })).unwrap()
}
fn mirror(position: &Position) -> Position {
    let mut board = [Piece::EMPTY; 64];
    for (index, piece) in position.board.into_iter().enumerate() {
        if !piece.is_empty() {
            board[index ^ 56] = Piece::new(piece.color().opponent(), piece.kind());
        }
    }
    let mut result = from_board(board, position.side.opponent());
    result.ep = if position.ep < 64 { position.ep ^ 56 } else { position.ep };
    result.recompute_derived();
    result
}
fn seeded_list() -> MoveList {
    let mut result = MoveList::new();
    result.len = MOVE_CAPACITY; // Each route must clear an already-populated output.
    result
}
fn legacy(position: &Position) -> Vec<Move> {
    let mut list = seeded_list();
    legacy_generate(position, &mut list);
    list.as_slice().to_vec()
}
fn compare_coherent(position: &Position) -> Vec<Move> {
    position.validate().unwrap();
    let saved = *position;
    let expected = legacy(position);
    let mut public = seeded_list();
    super::generate(position, &mut public);
    assert_eq!(public.as_slice(), expected.as_slice(), "public scalar versus frozen43");
    for geometry in [false, true] {
        let mut actual = seeded_list();
        super::generate_for_search(position, &mut actual, geometry);
        assert_eq!(actual.as_slice(), expected.as_slice(), "complete ordered vector; geometry={geometry}");
    }
    assert_eq!(*position, saved, "generation cannot mutate chronology/placement");
    expected
}
fn reversed_chronology(mut position: Position) -> Position {
    for side in 0..2 {
        let mut start = 0;
        for count in position.counts[side] {
            let end = start + usize::from(count);
            position.squares[side][start..end].reverse();
            start = end;
        }
    }
    position
}
fn place(board: &mut [Piece; 64], preferred: usize, side: Color, kind: PieceKind) {
    for step in 0..64 {
        let index = (preferred + 17 * step) & 63;
        if board[index].is_empty() && (kind != PieceKind::Pawn || (1..7).contains(&(index / 8))) {
            board[index] = Piece::new(side, kind);
            return;
        }
    }
    panic!("bounded test placement capacity");
}

#[test]
fn experiment51_ordered_vectors_all_king_squares_colors_and_chronology() {
    let mut saw_chronology_difference = false;
    for side in [Color::White, Color::Black] {
        for enemy_king in 0..64 {
            for mode in 0..3 {
                // Joined geometry, not a historical/own-king-safety admission.
                let mut board = [Piece::EMPTY; 64];
                board[enemy_king] = Piece::new(side.opponent(), PieceKind::King);
                let own_king = if enemy_king == 0 { 63 } else { 0 };
                board[own_king] = Piece::new(side, PieceKind::King);
                for (i, kind) in [PieceKind::Knight, PieceKind::Bishop, PieceKind::Rook, PieceKind::Queen,
                    PieceKind::Knight, PieceKind::Bishop, PieceKind::Rook, PieceKind::Queen,
                    PieceKind::Pawn, PieceKind::Pawn].into_iter().enumerate() {
                    place(&mut board, (enemy_king + 7 * i + 11 * mode + 9) & 63, side, kind);
                }
                if mode != 0 {
                    let blockers = if mode == 1 { side } else { side.opponent() };
                    for (i, kind) in [PieceKind::Pawn, PieceKind::Rook, PieceKind::Bishop, PieceKind::Queen].into_iter().enumerate() {
                        place(&mut board, (enemy_king + 13 * i + 3) & 63, blockers, kind);
                    }
                }
                let position = from_board(board, side);
                let expected = compare_coherent(&position);
                let reordered = reversed_chronology(position);
                let alternate = compare_coherent(&reordered);
                saw_chronology_difference |= expected != alternate;
            }
        }
    }
    assert!(saw_chronology_difference, "the corpus must exercise observable source order");
}

#[test]
fn experiment51_vacancy_axes_opaque_blockers_and_pseudo_legal_boundaries() {
    let cases = [
        ("2k5/8/8/8/2R5/8/8/7K w - - 0 1", "c4", "c1", true),
        ("2k5/8/2R5/8/2R5/8/8/7K w - - 0 1", "c4", "c1", false),
        ("7K/8/8/8/8/2B5/8/k7 w - - 0 1", "c3", "f6", true),
        ("3k4/8/8/8/2Q5/8/8/7K w - - 0 1", "c4", "d5", true),
        ("3k4/8/8/8/R7/8/8/7K w - - 0 1", "a4", "d4", true),
        ("8/8/8/8/1B3k2/8/8/7K w - - 0 1", "b4", "d6", true),
        ("1k6/8/1Q6/8/R7/8/8/7K w - - 0 1", "a4", "b4", false),
        ("1k6/8/1B6/8/R7/8/8/7K w - - 0 1", "a4", "b4", false),
        ("1k6/8/1R6/8/R7/8/8/7K w - - 0 1", "a4", "b4", false),
        ("1k6/8/1K6/8/R7/8/8/8 w - - 0 1", "a4", "b4", false),
        ("1k6/8/1n6/8/R7/8/8/7K w - - 0 1", "a4", "b4", false),
        ("k7/8/8/8/8/8/N7/R6K w - - 0 1", "a2", "b4", false),
        ("k3r3/8/8/8/8/8/4Rn2/4K3 w - - 0 1", "e2", "f2", true),
        ("7k/8/8/8/8/8/5r2/4K3 w - - 0 1", "e1", "f2", true),
        ("4k3/8/8/8/8/8/4R3/K7 w - - 0 1", "e2", "e8", false),
    ];
    for (fen, from, to, included) in cases {
        let position = Position::from_fen(fen).unwrap();
        let expected = compare_coherent(&position);
        assert_eq!(expected.contains(&ordinary(from, to)), included, "{fen}: {from}{to}");
        let other = mirror(&position);
        let expected_other = compare_coherent(&other);
        let mirrored_move = Move::new(Square(sq(from).0 ^ 56), Square(sq(to).0 ^ 56), MoveKind::Ordinary);
        assert_eq!(expected_other.contains(&mirrored_move), included);
    }
}

#[test]
fn experiment51_native_legal_walks_specials_and_exact_prefixes() {
    let roots = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r3k2r/ppp2ppp/2n1bn2/3qp3/3PP3/2N1BN2/PPP2PPP/R2Q1RK1 w kq - 0 1",
        "7k/8/8/3pP3/8/8/8/K7 w - d6 0 1",
        "1r5k/P7/8/8/8/8/8/K7 w - - 0 1",
        "7k/8/8/8/8/8/4P3/K7 w - - 0 1",
    ];
    let mut state = 0x51a9_32d7u32;
    let mut compared = 0;
    for fen in roots {
        let mut position = Position::from_fen(fen).unwrap();
        for _ in 0..24 {
            if !crate::movegen::in_check(&position, position.side) {
                compare_coherent(&position);
                compared += 1;
            }
            let mut legal = MoveList::new();
            crate::movegen::generate_legal(&position, &mut legal);
            if legal.as_slice().is_empty() { break; }
            state = state.wrapping_mul(1664525).wrapping_add(1013904223);
            position = position.played_unchecked(legal.as_slice()[state as usize % legal.as_slice().len()]);
        }
    }
    assert!(compared >= 20, "actual nonchecked legal-parent population");
    let start = Position::from_fen(roots[0]).unwrap();
    assert!(compare_coherent(&start).is_empty());
    for fen in ["7k/8/8/8/8/8/8/K7 w - - 0 1", "8/8/8/8/3k4/8/4P3/7K w - - 0 1"] {
        let position = Position::from_fen(fen).unwrap();
        let expected = compare_coherent(&position);
        assert!(expected.iter().all(|mv| position.board[mv.from().0 as usize].kind() != PieceKind::King));
        if position.counts[Color::White.index()][PieceKind::Pawn.index()] != 0 {
            assert_eq!(expected.iter().filter(|&&mv| mv == ordinary("e2", "e3")).count(), 1, "pawn prefix must not duplicate in suffix");
        }
        compare_coherent(&mirror(&position));
    }
    let black = Position::from_fen("7k/8/8/8/2pPp3/1p6/8/K7 b - d3 0 1").unwrap();
    let prefix = compare_coherent(&black);
    assert_eq!(&prefix[..3], &[
        Move::new(sq("e4"), sq("d3"), MoveKind::EnPassant),
        Move::new(sq("c4"), sq("d3"), MoveKind::EnPassant), ordinary("b3", "b2")]);
    compare_coherent(&mirror(&black));
    let promotion = Position::from_fen("1r2k3/P7/8/8/8/8/4P3/4K3 w - - 0 1").unwrap();
    let promoted = compare_coherent(&promotion);
    assert_eq!(&promoted[..2], &[Move::new(sq("a7"), sq("a8"), MoveKind::Promotion(PieceKind::Queen)),
        Move::new(sq("a7"), sq("b8"), MoveKind::Promotion(PieceKind::Queen))]);
    assert!(promoted.iter().all(|mv| !matches!(mv.kind(), MoveKind::Promotion(kind) if kind != PieceKind::Queen)));
    compare_coherent(&mirror(&promotion));
    let mut joined_ep = Position::from_fen("k7/8/8/4KPnr/8/8/8/8 w - - 0 1").unwrap();
    joined_ep.ep = sq("g6").0; // Genuine broad joined non-pawn victim, not historical reachability.
    joined_ep.recompute_derived();
    let ep = Move::new(sq("f5"), sq("g6"), MoveKind::EnPassant);
    let generated = compare_coherent(&joined_ep);
    assert_eq!(generated.first(), Some(&ep));
    assert!(crate::movegen::in_check(&joined_ep.played_unchecked(ep), Color::White), "unsafe EP must remain generated");
    compare_coherent(&mirror(&joined_ep));
}

fn scalar_outcome(position: &Position, route: u8) -> (bool, Vec<Move>) {
    let mut output = seeded_list();
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| match route {
        0 => legacy_generate(position, &mut output),
        1 => super::generate(position, &mut output),
        2 => super::generate_for_search(position, &mut output, false),
        _ => unreachable!(),
    }));
    (result.is_err(), output.as_slice().to_vec())
}
#[test]
fn experiment51_public_and_false_stale_lazy_domains_remain_scalar() {
    let base = Position::from_fen("1k6/8/8/8/R7/8/8/7K w - - 0 1").unwrap();
    let clean = compare_coherent(&base);
    assert!(clean.contains(&ordinary("a4", "b4")));
    for raw in [Piece::new(Color::White, PieceKind::Queen), Piece(193), Piece(7)] {
        let mut stale = base;
        stale.board[sq("b6").0 as usize] = raw;
        assert_eq!(stale.attack_view(), base.attack_view());
        assert!(stale.validate().is_err());
        let expected = scalar_outcome(&stale, 0);
        assert!(!expected.0, "unvisited/opaque reserved tags must not be eagerly inspected");
        assert!(!expected.1.contains(&ordinary("a4", "b4")));
        assert_eq!(scalar_outcome(&stale, 1), expected);
        assert_eq!(scalar_outcome(&stale, 2), expected);
    }
    let mut bad_victim = base;
    bad_victim.board[sq("a6").0 as usize] = Piece::new(Color::Black, PieceKind::Pawn);
    bad_victim.board[sq("b4").0 as usize] = Piece(15); // Opposing invalid kind is visited after a valid capture.
    let expected = scalar_outcome(&bad_victim, 0);
    assert!(expected.0);
    assert_eq!(expected.1, vec![ordinary("a4", "a6")]);
    assert_eq!(scalar_outcome(&bad_victim, 1), expected, "same lazy panic/partial output");
    assert_eq!(scalar_outcome(&bad_victim, 2), expected, "false route must not prevalidate/drop effects");
    let mut occupied_ep = Position::from_fen("k7/8/6n1/5Pr1/8/8/8/7K w - - 0 1").unwrap();
    occupied_ep.ep = sq("g6").0;
    let expected = scalar_outcome(&occupied_ep, 0);
    assert!(!expected.0);
    assert!(!expected.1.iter().any(|mv| mv.kind() == MoveKind::EnPassant));
    assert_eq!(scalar_outcome(&occupied_ep, 1), expected);
    assert_eq!(scalar_outcome(&occupied_ep, 2), expected);
}
