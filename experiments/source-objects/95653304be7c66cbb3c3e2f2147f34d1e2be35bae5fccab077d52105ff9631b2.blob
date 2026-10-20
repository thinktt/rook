//! Association/permission falsifiers; numerical mask cancellation has a separate oracle.
use super::*;
use crate::types::{Color, Piece, Square};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
fn legal(position: &Position, token: &str) -> Move {
    let mut moves = MoveList::new();
    movegen::generate_legal(position, &mut moves);
    *moves.as_slice().iter().find(|m| m.to_string() == token).unwrap()
}

#[test]
fn experiment50_native_raw_and_public_some_do_not_authenticate() {
    let p = Position::from_fen(START).unwrap();
    let mut evaluator = Evaluator::<true>::new(&p);
    let parent = Node::root(p, &evaluator.root);
    let movement = legal(&p, "e2e4");
    let child = parent.child(&evaluator.root, movement);
    let custom = Influence { profiles: [[255; 64]; 2] };
    assert_ne!(custom, Influence::build(&p));
    let raw = Predecessor::unlinked(&p, &custom, false, Some(movement));
    assert!(!raw.native_main_child);
    let mut current = CurrentInfluence::new(&child.position);
    current.fill(&mut evaluator, raw, true);
    assert_eq!(*current.trusted().influence, Influence::build(&child.position));
    assert!(std::ptr::eq(raw.influence, &custom));
    assert_eq!(evaluator.stats.influence_builds, 1);

    // A correct raw map does not authenticate an unrelated child either.
    let correct = Influence::build(&p);
    let raw = Predecessor::unlinked(&p, &correct, false, Some(movement));
    let unrelated = parent.child(&evaluator.root, legal(&p, "d2d4"));
    let mut other = CurrentInfluence::new(&unrelated.position);
    other.fill(&mut evaluator, raw, true);
    assert_eq!(*other.trusted().influence, Influence::build(&unrelated.position));
    assert_eq!(evaluator.stats.influence_builds, 2);

    // Public and search supply APIs keep arbitrary Some authoritative and do
    // not construct or import it into CurrentInfluence.
    let mut supplied = Some(custom);
    assert_eq!(*evaluator.ensure_influence(&p, &mut supplied), custom);
    assert_eq!(*evaluator.ensure_influence_for_search(&p, &mut supplied, true), custom);
    assert_eq!(supplied, Some(custom));
    assert_eq!(evaluator.stats.influence_builds, 2);
}

#[test]
fn experiment50_native_fresh_entry_seeds_main_retry_and_checked_parent() {
    let p = Position::from_fen(START).unwrap();
    let mut evaluator = Evaluator::<true>::new(&p);
    let parent = Node::root(p, &evaluator.root);
    let first = legal(&p, "e2e4");
    let child = parent.child(&evaluator.root, first);
    let supplied = Influence { profiles: [[0; 64]; 2] };
    let incoming = Predecessor::unlinked(&p, &supplied, false, Some(first));
    let mut current = CurrentInfluence::new(&child.position);
    assert_eq!(evaluator.stats.influence_builds, 0); // No eager fill.
    current.fill(&mut evaluator, incoming, true);
    let first_address = current.trusted().influence as *const Influence;
    current.fill(&mut evaluator, incoming, true);
    assert_eq!(first_address, current.trusted().influence as *const Influence);
    assert_eq!(evaluator.stats.influence_builds, 1);

    let movement = legal(&child.position, "e7e5");
    let mut grandchild = child.child(&evaluator.root, movement);
    let linked = Predecessor::main_child(current.trusted(), false, movement);
    assert!(linked.native_main_child && linked.coherent_geometry);
    let placement = grandchild.position;
    let mut descendant = CurrentInfluence::new(&placement);
    descendant.fill(&mut evaluator, linked, true);
    let map = *descendant.trusted().influence;
    assert_eq!(map, Influence::build(&placement));
    assert_eq!(evaluator.stats.influence_builds, 2);
    evaluator.full(&mut grandchild, &map, false);
    assert_eq!(grandchild.position, placement);
    assert_eq!(grandchild.retained.age, 0);
    let refreshed = grandchild.retained;
    let mut retry = CurrentInfluence::new(&placement);
    retry.fill(&mut evaluator, linked, true);
    assert_eq!(*retry.trusted().influence, map);
    assert_eq!(grandchild.retained, refreshed);
    assert_eq!(evaluator.stats.influence_builds, 3);

    // Genuine checked parent: blocking a rook check remains an ordinary
    // authenticated child. Checked is not a map-eligibility disqualifier.
    let p = Position::from_fen("4r2k/8/8/8/8/8/3R4/4K3 w - - 0 1").unwrap();
    assert!(movegen::in_check(&p, p.side));
    let mut evaluator = Evaluator::<true>::new(&p);
    let parent = Node::root(p, &evaluator.root);
    let baseline = Influence::build(&p);
    let mut current = CurrentInfluence::new(&parent.position);
    current.fill(&mut evaluator, Predecessor::unlinked(&p, &baseline, true, None), true);
    let movement = legal(&p, "d2e2");
    let child = parent.child(&evaluator.root, movement);
    let linked = Predecessor::main_child(current.trusted(), true, movement);
    assert!(linked.native_main_child && linked.checked);
    let mut next = CurrentInfluence::new(&child.position);
    next.fill(&mut evaluator, linked, true);
    assert_eq!(*next.trusted().influence, Influence::build(&child.position));
}

#[test]
fn experiment50_native_promotions_specials_and_independent_geometry_gates() {
    for (fen, token) in [
        ("4k3/P7/8/8/8/8/8/4K3 w - - 0 1", "a7a8q"),
        ("4k3/P7/8/8/8/8/8/4K3 w - - 0 1", "a7a8r"),
        ("4k3/P7/8/8/8/8/8/4K3 w - - 0 1", "a7a8b"),
        ("4k3/P7/8/8/8/8/8/4K3 w - - 0 1", "a7a8n"),
        ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", "e1g1"),
        ("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1", "e5d6"),
    ] {
        let p = Position::from_fen(fen).unwrap();
        let mut evaluator = Evaluator::<true>::new(&p);
        let parent = Node::root(p, &evaluator.root);
        let baseline = Influence::build(&p);
        let raw = Predecessor::unlinked(&p, &baseline, false, None);
        let mut current = CurrentInfluence::new(&parent.position);
        current.fill(&mut evaluator, raw, true);
        let movement = legal(&p, token);
        let child = parent.child(&evaluator.root, movement);
        let linked = Predecessor::main_child(current.trusted(), false, movement);
        assert_eq!(linked.native_main_child,
            matches!(movement.kind(), MoveKind::Ordinary | MoveKind::Promotion(_)));
        let mut next = CurrentInfluence::new(&child.position);
        next.fill(&mut evaluator, linked, true);
        assert_eq!(*next.trusted().influence, Influence::build(&child.position));
        // Root/IIO raw contexts remain unlinked even with a genuine supplied
        // parent map and movement. Null carries no main-child authentication.
        let incoming = Predecessor::unlinked(&p, &baseline, false, Some(movement));
        assert!(!incoming.native_main_child);
        let mut raw_next = CurrentInfluence::new(&child.position);
        raw_next.fill(&mut evaluator, incoming, true);
        assert_eq!(*raw_next.trusted().influence, Influence::build(&child.position));
        let null = parent.null_child();
        let mut null_map = CurrentInfluence::new(&null.position);
        null_map.fill(&mut evaluator, raw, true);
        assert_eq!(*null_map.trusted().influence, Influence::build(&null.position));
        assert_eq!(evaluator.stats.influence_builds, 4);
    }

    // Copy every public state field while retaining the target's private
    // planes. These are explicit permission falsifiers, not eligible kernels.
    fn public_state_on_planes(state: Position, mut target: Position) -> Position {
        target.board = state.board;
        target.squares = state.squares;
        target.counts = state.counts;
        target.primary = state.primary;
        target.secondary = state.secondary;
        target.pawn = state.pawn;
        target.side = state.side;
        target.rights = state.rights;
        target.ep = state.ep;
        target.halfmove = state.halfmove;
        target.starting_units = state.starting_units;
        target
    }
    let p = Position::from_fen("7k/8/8/8/8/8/P7/R6K w - - 0 1").unwrap();
    let no_rook = Position::from_fen("7k/8/8/8/8/8/P7/7K w - - 0 1").unwrap();
    let movement = legal(&p, "a2a3");
    let a3 = Square::parse("a3").unwrap();
    let mut evaluator = Evaluator::<true>::new(&p);
    let baseline = Influence::build(&p);
    assert_eq!(baseline.code(Color::White, a3), 0);

    // False parent, true child: the parent's scalar map includes Ra1, but its
    // stale origin planes omit it. Repair the actual child's derived metadata
    // before granting child permission. A forbidden update would miss Ra1's
    // newly reached a3; the pawn/king sources cannot contribute there.
    let stale_parent = public_state_on_planes(p, no_rook);
    assert!(stale_parent.validate().is_err());
    let parent = Node::root(stale_parent, &evaluator.root);
    let mut current = CurrentInfluence::new(&parent.position);
    current.fill(&mut evaluator, Predecessor::unlinked(&stale_parent, &baseline, false, None), false);
    assert_eq!(*current.trusted().influence, baseline);
    let mut child = parent.child(&evaluator.root, movement);
    child.position.recompute_derived();
    assert!(child.position.validate().is_ok());
    let linked = Predecessor::main_child(current.trusted(), false, movement);
    assert!(linked.native_main_child && !linked.coherent_geometry);
    let expected = Influence::build(&child.position);
    assert_eq!(expected.code(Color::White, a3), 4);
    let mut next = CurrentInfluence::new(&child.position);
    next.fill(&mut evaluator, linked, true);
    assert_eq!(*next.trusted().influence, expected);

    // True parent, false child: preserve the genuine child public state on the
    // old parent planes, which still block Ra1 at a2. A forbidden update would
    // cancel the identical stale ray and leave a3 at0 rather than4.
    let parent = Node::root(p, &evaluator.root);
    let mut current = CurrentInfluence::new(&parent.position);
    current.fill(&mut evaluator, Predecessor::unlinked(&p, &baseline, false, None), true);
    let child = parent.child(&evaluator.root, movement);
    let stale_child = public_state_on_planes(child.position, p);
    assert!(stale_child.validate().is_err());
    let linked = Predecessor::main_child(current.trusted(), false, movement);
    assert!(linked.native_main_child && linked.coherent_geometry);
    let expected = Influence::build(&stale_child);
    assert_eq!(expected.code(Color::White, a3), 4);
    let mut next = CurrentInfluence::new(&stale_child);
    next.fill(&mut evaluator, linked, false);
    assert!(!next.trusted().coherent_geometry);
    assert_eq!(*next.trusted().influence, expected);

    let p = Position::from_fen(START).unwrap();
    let movement = legal(&p, "e2e3");
    let child = Node::root(p, &evaluator.root).child(&evaluator.root, movement);
    let baseline = Influence::build(&p);
    // Public stale-plane input stays on the scalar authority, without a link.
    let mut stale = p;
    stale.board[Square::parse("e4").unwrap().0 as usize] = Piece::new(Color::Black, PieceKind::Pawn);
    assert!(stale.validate().is_err());
    let mut scratch = None;
    assert_eq!(*evaluator.ensure_influence(&stale, &mut scratch), Influence::build(&stale));
    let mut quiet = Evaluator::<false>::new(&p);
    let mut current = CurrentInfluence::new(&child.position);
    current.fill(&mut quiet, Predecessor::unlinked(&p, &baseline, false, Some(movement)), true);
    assert_eq!(quiet.stats.influence_builds, 0);
}
