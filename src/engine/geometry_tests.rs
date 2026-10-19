//! Permission falsifiers; kernel arithmetic has a separate independent oracle.
use super::*;
use crate::evaluator::{coherent_build_count, EvaluationStage, Node, Retained};
use crate::influence::Influence;
use crate::ordinary;
use crate::quiescence::{Entry, Observer};
use crate::timed::Controls;
use crate::types::{Color, Piece, PieceKind, Square};
use std::panic::{catch_unwind, AssertUnwindSafe};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
fn position() -> Position { Position::from_fen(START).unwrap() }
fn control() -> Controls {
    Controls { average_cs: 0, maximum_cs: 0, origin: 0, seed: 0,
        randomness: 0, maximum_entered_iterations: 2 }
}
struct Off;
impl Observer for Off {
    const ENABLED: bool = false;
    type Parent = ();
    type Frame = ();
    fn parent(_: &Retained) {}
    fn enter(&mut self, _: &Position, _: Entry, _: Option<Move>, _: (),
        _: Retained, _: bool, _: Work) {}
    fn stage(&mut self, _: EvaluationStage) {}
    fn ordered(&mut self) {}
    fn leave(&mut self, _: (), _: Retained, _: i32, _: &[Move], _: Work) {}
}

#[test]
fn experiment37_private_supply_selection_and_public_custom_bypass() {
    let p = position();
    let mut trusted = Search::<true>::new(&p);
    trusted.bind_geometry_permission(&p);
    assert!(trusted.geometry_permission());
    let before = coherent_build_count();
    let mut scratch = None;
    let map = *trusted.evaluator.ensure_influence_for_search(&p, &mut scratch, true);
    assert_eq!(map, Influence::build(&p));
    assert_eq!(coherent_build_count() - before, 1);
    assert_eq!(trusted.evaluator.stats.influence_builds, 1);
    assert_eq!(*trusted.evaluator.ensure_influence_for_search(&p, &mut scratch, true), map);
    assert_eq!(coherent_build_count() - before, 1);

    // Force refresh and compare the actual selected evaluation, retained state,
    // maps and shared pawn/stat effects, not merely map geometry.
    let mut a = crate::evaluator::Evaluator::<true>::new(&p);
    let mut b = crate::evaluator::Evaluator::<true>::new(&p);
    let mut an = Node::root(p, &a.root);
    let mut bn = Node::root(p, &b.root);
    let mut am = None;
    let mut bm = None;
    let before = coherent_build_count();
    let av = a.select_noncheck_for_search(&mut an, -10000, 10000, true, &mut am, true);
    let bv = b.select_noncheck(&mut bn, -10000, 10000, true, &mut bm);
    assert_eq!(coherent_build_count() - before, 1);
    assert_eq!((av, an.retained, am, a.stats), (bv, bn.retained, bm, b.stats));

    let mut custom = Influence { profiles: [[0; 64]; 2] };
    custom.profiles[0][7] = 255;
    custom.profiles[1][12] = 4;
    let mut a = crate::evaluator::Evaluator::<true>::new(&p);
    let mut b = crate::evaluator::Evaluator::<true>::new(&p);
    let mut an = Node::root(p, &a.root);
    let mut bn = Node::root(p, &b.root);
    let mut am = Some(custom);
    let mut bm = Some(custom);
    let before = coherent_build_count();
    let av = a.select_noncheck_for_search(&mut an, -10000, 10000, true, &mut am, true);
    let bv = b.select_noncheck(&mut bn, -10000, 10000, true, &mut bm);
    assert_eq!(coherent_build_count(), before);
    assert_eq!((av, an.retained, am, a.stats), (bv, bn.retained, bm, b.stats));
    assert_eq!(am, Some(custom));
    assert_eq!(a.stats.influence_builds, 0);

    // Public methods ignore even an artificially stale owning Search flag.
    // The mailbox mutation intentionally leaves private planes/lists stale.
    let mut stale = p;
    stale.board[Square::parse("e4").unwrap().0 as usize] = Piece::new(Color::Black, PieceKind::Pawn);
    assert!(stale.validate().is_err());
    let expected = Influence::build(&stale);
    let before = coherent_build_count();
    let mut none = None;
    assert_eq!(*trusted.evaluator.ensure_influence(&stale, &mut none), expected);
    let mut node = Node::root(stale, &trusted.evaluator.root);
    let mut none = None;
    trusted.evaluator.select_noncheck_detailed_observed(&mut node,
        -10000, 10000, true, &mut none, |_| {}, |_| {});
    assert_eq!(none, Some(expected));
    assert_eq!(coherent_build_count(), before);
}

#[test]
fn experiment37_external_entries_clear_even_before_assertion_failure() {
    let p = position();
    let mut search = Search::<true>::new(&p);
    search.config.tts_bytes = 96;
    search.coherent_geometry = true;
    let before = coherent_build_count();
    let mut node = search.prepare_root(p);
    assert!(!search.geometry_permission());
    assert_eq!(coherent_build_count(), before);
    search.coherent_geometry = true;
    search.begin_sequence(Limits::default());
    assert!(!search.geometry_permission());

    let mut history = SearchHistory::new(&p);
    history.push(&node.position, None);
    let entry = Entry { ply: 1, target: 1, iteration_depth: 1,
        lower: -10000, upper: 10000, analysis: 0, capture_exception: false };
    search.limits = Limits { nodes: Some(0) };
    search.coherent_geometry = true;
    assert!(matches!(search.continue_subtree(&mut node, &mut history, entry),
        Err(Stopped::NodeLimit(0))));
    assert!(!search.geometry_permission());
    assert_eq!(coherent_build_count(), before);
    history.pop();

    search.coherent_geometry = true;
    assert!(catch_unwind(AssertUnwindSafe(|| {
        let mut off = Off;
        let _ = search.search_subtree_observed(&mut node, &mut history,
            Entry { ply: 0, ..entry }, Limits::default(), &Retained::default(), &mut off);
    })).is_err());
    assert!(!search.geometry_permission());
    search.coherent_geometry = true;
    assert!(catch_unwind(AssertUnwindSafe(|| {
        let _ = search.run_seeded_iterations(p, &mut history, 1,
            Limits::default(), 0, u32::MAX, |_| {});
    })).is_err());
    assert!(!search.geometry_permission());
    assert_eq!(coherent_build_count(), before);

    // Validation rejects invalid raw kinds before any kind-dependent producer.
    let mut malformed = p;
    malformed.board[Square::parse("e4").unwrap().0 as usize] = Piece(7);
    search.bind_geometry_permission(&malformed);
    assert!(!search.geometry_permission());
    assert_eq!(coherent_build_count(), before);

    // A safe but incoherent root chooses scalar, not an admission error.
    let mut invalid = p;
    invalid.starting_units ^= 1;
    assert!(invalid.validate().is_err());
    search.coherent_geometry = true;
    let mut history = SearchHistory::new(&invalid);
    assert!(matches!(search.run_iterations(invalid, &mut history, 1,
        Limits { nodes: Some(0) }), Err(ordinary::Error::Stopped(Stopped::NodeLimit(0)))));
    assert!(!search.geometry_permission());
    assert_eq!(coherent_build_count(), before);
    assert_eq!(history.search_ply(), 0);
}

#[test]
fn experiment37_native_root_lifetime_stops_errors_and_host_transfer() {
    let p = position();
    let mut search = Search::<true>::new(&p);
    search.config.tts_bytes = 96;
    let mut history = SearchHistory::new(&p);
    let before = coherent_build_count();
    let outcome = search.run_iterations(p, &mut history, 1,
        Limits { nodes: Some(100000) }).unwrap();
    assert!(!search.geometry_permission());
    assert!(outcome.evaluations.influence_builds > 0);
    // Root construction is before segment-stat reset; every later actual build
    // must retain permission through private Q selection and recursion.
    assert_eq!(coherent_build_count() - before, outcome.evaluations.influence_builds + 1);
    assert_eq!(history.search_ply(), 0);

    let before = coherent_build_count();
    assert!(matches!(search.run_work_timed(p, &mut history, control(),
        Limits { nodes: Some(0) }), Err(ordinary::Error::Stopped(Stopped::NodeLimit(0)))));
    assert_eq!(coherent_build_count() - before, 1);
    assert!(!search.geometry_permission());
    assert!(search.timing.is_none());
    assert_eq!(history.search_ply(), 0);
    let before = coherent_build_count();
    assert!(matches!(search.run_work_timed_without_iio(p, &mut history, control(),
        Limits { nodes: Some(0) }), Err(ordinary::Error::Stopped(Stopped::NodeLimit(0)))));
    assert_eq!(coherent_build_count() - before, 1);
    assert!(!search.geometry_permission());

    struct FailSeed;
    impl Host for FailSeed {
        fn acquire_seed(&mut self, _: u32, _: u32) -> std::io::Result<u32> {
            Err(std::io::Error::new(std::io::ErrorKind::Other, "controlled seed failure"))
        }
    }
    search.coherent_geometry = true;
    let (mut active, _) = search.map_host(FailSeed);
    assert!(!active.geometry_permission());
    let before = coherent_build_count();
    assert!(matches!(active.run_work_timed(p, &mut history, control(), Limits::default()),
        Err(ordinary::Error::Host(_))));
    assert_eq!(coherent_build_count() - before, 1);
    assert!(!active.geometry_permission());
    assert!(active.timing.is_none());
    assert_eq!(history.search_ply(), 0);
    active.coherent_geometry = true;
    let (saved, _) = active.map_host(NoHost);
    assert!(!saved.geometry_permission());
}
