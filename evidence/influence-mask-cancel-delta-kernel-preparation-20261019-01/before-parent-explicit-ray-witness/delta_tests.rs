//! Source-independent full-map controls: the expected child is always the
//! unchanged coordinate/mailbox Influence::build, never the shared mask owner.
use super::*;
use crate::evaluation::RootContext;
use crate::evaluator::Node;
use crate::types::{Move, MoveKind};

fn sq(text: &str) -> Square { Square::parse(text).unwrap() }
fn movement(from: &str, to: &str, kind: MoveKind) -> Move {
    Move::new(sq(from), sq(to), kind)
}
fn placement(pieces: &[(&str, char)], side: Color) -> Position {
    let mut board = [Piece::EMPTY; 64];
    for &(name, piece) in pieces {
        let index = sq(name).0 as usize;
        assert!(board[index].is_empty());
        board[index] = Piece::from_fen(piece).unwrap();
    }
    from_board(board, side)
}
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
fn mirror(parent: &Position, movement: Move) -> (Position, Move) {
    let mut board = [Piece::EMPTY; 64];
    for (index, piece) in parent.board.into_iter().enumerate() {
        if !piece.is_empty() {
            board[index ^ 56] = Piece::new(piece.color().opponent(), piece.kind());
        }
    }
    (from_board(board, parent.side.opponent()),
        Move::new(Square(movement.from().0 ^ 56), Square(movement.to().0 ^ 56), movement.kind()))
}
fn compare(parent: &Position, movement: Move) -> Position {
    parent.validate().unwrap();
    assert!(matches!(movement.kind(), MoveKind::Ordinary | MoveKind::Promotion(_)));
    let saved_parent = *parent;
    let parent_map = Influence::build_coherent(parent);
    assert_eq!(parent_map, Influence::build(parent), "independent parent full map");
    let child = parent.played_unchecked(movement);
    child.validate().unwrap();
    let changed: Vec<_> = (0..64).filter(|&i| parent.board[i] != child.board[i]).collect();
    assert_eq!(changed.len(), 2, "kernel admission: {movement}");
    assert!(changed.contains(&(movement.from().0 as usize)) && changed.contains(&(movement.to().0 as usize)));
    let saved_child = child;
    let mut actual = parent_map; // Caller-owned initialization, outside the kernel.
    Influence::update_two_square(parent, &child, movement, &mut actual);
    let expected = Influence::build(&child);
    assert_eq!(actual, expected, "all128 bytes after {movement}");
    assert_eq!(Influence::build_coherent(&child), expected, "shared fresh producer after extraction");
    assert_eq!(*parent, saved_parent);
    assert_eq!(child, saved_child);
    assert_eq!(parent_map, Influence::build(parent), "immutable parent map");
    child
}

#[test]
fn experiment50_joined_rays_weights_transparency_and_wrap() {
    // These are coherent joined placements and actual ordinary transitions;
    // king safety is intentionally not an additional kernel precondition.
    let cases: &[(&[(&str, char)], &str, &str)] = &[
        // Several collinear sources beyond F/T; same source/ray selected twice.
        (&[("a1",'K'),("h8",'k'),("a4",'R'),("b4",'R'),("c4",'Q'),("d4",'R'),("e4",'n'),("g4",'r')], "d4", "e4"),
        // An own queen moves OFF a continuing rook ray: weak->normal targets.
        (&[("a1",'K'),("h8",'k'),("a4",'R'),("c4",'Q'),("g4",'r')], "c4", "c5"),
        // An own queen moves ONTO the ray: normal->weak, plus opposing king transparency.
        (&[("a1",'K'),("g4",'k'),("a4",'R'),("c5",'Q')], "c5", "c4"),
        // Forward pawn extension: add one square after a stopping pawn, including an occupied extra square.
        (&[("a1",'K'),("h8",'k'),("b2",'B'),("d4",'P'),("e5",'n')], "d4", "d5"),
        // Diagonal own bishop/queen chains and a moved blocker with two affected directions.
        (&[("a1",'K'),("h8",'k'),("a2",'B'),("b3",'B'),("c4",'Q'),("d5",'B'),("e6",'p'),("d3",'b')], "c4", "d4"),
        // F/T select two DIFFERENT rays of the same unchanged origin.
        (&[("a1",'K'),("h8",'k'),("d4",'R'),("c4",'Q'),("d1",'r'),("h4",'r')], "c4", "d3"),
        // Capture a slider: remove its COMPLETE old source, not only affected rays.
        (&[("a1",'K'),("h8",'k'),("c3",'N'),("d5",'q'),("a5",'r'),("g2",'b')], "c3", "d5"),
        // King changes leaper ownership and is transparent only to the opposing color.
        (&[("d4",'K'),("h8",'k'),("a4",'r'),("a1",'b'),("h4",'R')], "d4", "e4"),
        // Pawn capture, leaper removal/addition, and both-color slider changes.
        (&[("a1",'K'),("h8",'k'),("d4",'P'),("e5",'n'),("a5",'r'),("b2",'B')], "d4", "e5"),
        // Ordinary slider mover must remove/add all four/eight rays.
        (&[("a1",'K'),("h8",'k'),("d4",'Q'),("c5",'r'),("a4",'R'),("f6",'b')], "d4", "c5"),
    ];
    for &(pieces, from, to) in cases {
        let parent = placement(pieces, Color::White);
        let mv = movement(from, to, MoveKind::Ordinary);
        compare(&parent, mv);
        let (other, mirrored) = mirror(&parent, mv);
        compare(&other, mirrored);
    }
    let overflow = placement(&[("a1",'K'),("h8",'k'),("b3",'N'),("b5",'N'),("c2",'N'),("c6",'N'),
        ("e2",'N'),("e6",'N'),("f3",'N'),("f5",'N'),("c3",'P'),("e3",'P')], Color::White);
    assert_eq!(Influence::build(&overflow).code(Color::White, sq("d4")), 0);
    let child = compare(&overflow, movement("b3", "a5", MoveKind::Ordinary));
    assert_eq!(Influence::build(&child).code(Color::White, sq("d4")), 240);
    let (other, mirrored) = mirror(&overflow, movement("b3", "a5", MoveKind::Ordinary));
    compare(&other, mirrored);
}

#[test]
fn experiment50_all_promotions_quiet_capture_and_both_colors() {
    for fen in ["1r5k/P7/8/8/8/8/8/K7 w - - 0 1", "7k/P7/8/8/8/8/8/K7 w - - 0 1"] {
        let parent = Position::from_fen(fen).unwrap();
        for kind in [PieceKind::Knight, PieceKind::Bishop, PieceKind::Rook, PieceKind::Queen] {
            for to in ["a8", "b8"] {
                if to == "b8" && parent.board[sq(to).0 as usize].is_empty() { continue; }
                let mv = movement("a7", to, MoveKind::Promotion(kind));
                compare(&parent, mv);
                let (other, mirrored) = mirror(&parent, mv);
                compare(&other, mirrored);
            }
        }
    }
}

#[test]
fn experiment50_native_legal_pairs_and_owned_node_children() {
    let roots = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r3k2r/ppp2ppp/2n1bn2/3qp3/3PP3/2N1BN2/PPP2PPP/R2Q1RK1 w kq - 0 1",
        "4k3/8/2b5/3p4/3P4/2B5/8/4K3 w - - 0 1",
        "1r5k/P7/8/8/8/8/8/K7 w - - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
    ];
    let mut samples = 0usize;
    let mut state = 0x5a17_83c9u32;
    for fen in roots {
        let start = Position::from_fen(fen).unwrap();
        let root = RootContext::new(&start, [[100; 5]; 2], 0);
        let mut node = Node::root(start, &root);
        for _ in 0..24 {
            let mut legal = crate::movegen::MoveList::new();
            crate::movegen::generate_legal(&node.position, &mut legal);
            if legal.as_slice().is_empty() { break; }
            // Sample a bounded prefix of actual generator order at every legal parent.
            for &mv in legal.as_slice().iter().filter(|mv| matches!(mv.kind(), MoveKind::Ordinary | MoveKind::Promotion(_))).take(8) {
                let saved = node;
                let expected_position = compare(&node.position, mv);
                let child = node.child(&root, mv);
                assert_eq!(child.position, expected_position);
                assert_eq!(node, saved, "owned parent and retained state stay unchanged");
                samples += 1;
            }
            state = state.wrapping_mul(1664525).wrapping_add(1013904223);
            node = node.child(&root, legal.as_slice()[state as usize % legal.as_slice().len()]);
        }
    }
    assert!(samples >= 100, "meaningful bounded legal-pair population");
}
