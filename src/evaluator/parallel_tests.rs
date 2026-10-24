//! Focused budget1/budget2 checks of the actual composed evaluator and search.

use super::*;
use crate::engine::Search;
use crate::history::SearchHistory;
use crate::movegen::{generate_legal, MoveList};
use crate::ordinary;
use crate::quiescence::{Limits, Stopped};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const MIDDLE: &str = "r3k2r/ppp2ppp/2npbn2/3qp3/3PP3/2N1BN2/PPP2PPP/R2Q1RK1 b kq - 0 10";
const ENDING: &str = "6k1/5pp1/6p1/3P4/8/2N5/5P2/6K1 w - - 0 40";

fn evaluators<const D: bool>(position: &Position) -> (Evaluator<D>, Evaluator<D>) {
    let mut serial = Evaluator::new(position);
    let mut worker = Evaluator::new(position);
    serial.set_threads(1).unwrap();
    worker.set_threads(2).unwrap();
    (serial, worker)
}

#[derive(Debug, PartialEq, Eq)]
struct Observed {
    evaluation: Evaluation,
    node: Node,
    details: FullDetails,
}

fn observe<const D: bool>(
    evaluator: &mut Evaluator<D>,
    mut node: Node,
    map: &Influence,
    checked: bool,
    fresh: bool,
) -> Observed {
    let before = node.retained;
    let stats_before = evaluator.stats;
    let mut details = None;
    let evaluation = if fresh {
        evaluator.fresh_detailed_observed(&mut node, map, checked, |value| details = Some(value))
    } else {
        evaluator.full_detailed_observed(&mut node, map, checked, |value| details = Some(value))
    };
    let details = details.unwrap();
    assert_eq!(details.base, details.components.base());
    assert_eq!((evaluation.score, evaluation.lower, evaluation.upper),
        (details.finished.score, details.finished.lower, details.finished.upper));
    assert_eq!(node.retained.positional, details.components.positional());
    assert_eq!(node.retained.pawn_progress, details.components.pawn_progress);
    assert_eq!(node.retained.nonking_squares, before.nonking_squares);
    assert_eq!(node.retained.age, 0);
    assert_eq!(evaluator.stats.relation_queries - stats_before.relation_queries,
        evaluation.relation_queries);
    assert_eq!(evaluator.stats.full - stats_before.full, u64::from(D));
    assert_eq!(evaluator.stats.influence_builds, stats_before.influence_builds);
    assert_eq!(evaluator.stats.pawn_reuses - stats_before.pawn_reuses,
        u64::from(D && details.pawn_entry_reused));
    assert_eq!(evaluator.stats.pawn_replacements - stats_before.pawn_replacements,
        u64::from(D && !details.pawn_entry_reused));
    if fresh {
        assert!(!details.pawn_entry_reused);
    }
    Observed { evaluation, node, details }
}

fn compare<const D: bool>(
    serial: &mut Evaluator<D>,
    worker: &mut Evaluator<D>,
    node: Node,
    map: &Influence,
    checked: bool,
    fresh: bool,
) -> Observed {
    let expected = observe(serial, node, map, checked, fresh);
    let actual = observe(worker, node, map, checked, fresh);
    assert_eq!(actual, expected);
    assert_eq!(worker.stats, serial.stats);
    expected
}

#[test]
fn budgets_match_detailed_full_and_fresh_across_weights_and_root_rebinding() {
    fn verify<const D: bool>() {
        let position = Position::from_fen(START).unwrap();
        let (mut serial, mut worker) = evaluators::<D>(&position);
        let mut asymmetric = Parameters::default();
        asymmetric.own = [133, 73, 151, 87, 200, 121, 19, 313, 207, 251, 49];
        asymmetric.opponent = [91, 128, 67, 142, 80, 57, 183, 47, 333, 107, 229];
        asymmetric.average_depth = 13;
        asymmetric.draw = -173;
        asymmetric.opponent_selectivity = 31;
        let mut zero = Parameters::default();
        zero.own[6..].fill(0);
        zero.opponent[6..].fill(0);
        // One persistent worker crosses changes in root side, phase, material,
        // current weight pairs and finishing parameters.
        for fen in [START, MIDDLE, ENDING, START] {
            let position = Position::from_fen(fen).unwrap();
            let map = Influence::build(&position);
            for (index, parameters) in [Parameters::default(), asymmetric.clone(), zero.clone()]
                .into_iter().enumerate()
            {
                serial.parameters = parameters.clone();
                worker.parameters = parameters;
                serial.begin_search(&position);
                worker.begin_search(&position);
                assert_eq!(serial.stats, EvalStats::default());
                assert_eq!(worker.stats, EvalStats::default());
                for checked in [false, true] {
                    let mut node = Node::root(position, &serial.root);
                    node.retained.positional = 731;
                    node.retained.pawn_progress = -193;
                    node.retained.age = 17;
                    for fresh in [false, false, true, false] {
                        let value = compare(&mut serial, &mut worker, node, &map, checked, fresh);
                        if checked {
                            assert_eq!(value.details.components.tempo, 0);
                        }
                        if index == 2 {
                            assert_eq!(value.details.components.activity, 0);
                            assert_eq!(value.details.components.shelter, 0);
                        }
                        if !D {
                            assert_eq!(worker.stats.full, 0);
                            assert_eq!(worker.stats.pawn_reuses, 0);
                            assert_eq!(worker.stats.pawn_replacements, 0);
                        }
                    }
                }
                assert_eq!(worker.stats.influence_builds, 0);
            }
        }
    }
    verify::<true>();
    verify::<false>();
}

#[test]
fn budgets_preserve_supplied_contrary_influence_and_lazy_selection() {
    let position = Position::from_fen(START).unwrap();
    let natural = Influence::build(&position);
    let contrary = Influence { profiles: [[255; 64], [0; 64]] };
    let (mut serial, mut worker) = evaluators::<true>(&position);
    let node = Node::root(position, &serial.root);
    let normal = compare(&mut serial, &mut worker, node, &natural, false, true);
    let custom = compare(&mut serial, &mut worker, node, &contrary, false, true);
    assert_ne!((custom.details.components.activity, custom.details.components.shelter),
        (normal.details.components.activity, normal.details.components.shelter));
    assert_eq!(compare(&mut serial, &mut worker, node, &natural, false, true), normal);

    serial.begin_search(&position);
    worker.begin_search(&position);
    let (mut a, mut b) = (node, node);
    let (mut am, mut bm) = (Some(contrary), Some(contrary));
    let (mut af, mut bf, mut aq, mut bq) = (None, None, None, None);
    let expected = serial.select_noncheck_detailed_observed(&mut a, -10000, 10000,
        true, &mut am, |value| af = Some(value), |value| aq = Some(value));
    let actual = worker.select_noncheck_detailed_observed(&mut b, -10000, 10000,
        true, &mut bm, |value| bf = Some(value), |value| bq = Some(value));
    assert_eq!((actual, b, bm, bf, bq), (expected, a, am, af, aq));
    assert!(expected.refreshed && !expected.initially_full);
    assert_eq!(af.unwrap().components, custom.details.components);
    assert_eq!(am, Some(contrary));
    assert_eq!(worker.stats, serial.stats);
    assert_eq!(worker.stats.influence_builds, 0);

    // A strict-endpoint FAST return must leave the supplied worker idle and
    // must not construct a map or modify inherited retained values.
    let (mut a, mut b) = (a.null_child(), b.null_child());
    let before = a;
    let score = serial.fast(&a, false).score;
    assert_eq!(worker.fast(&b, false).score, score);
    let (mut am, mut bm) = (None, None);
    let expected = serial.select_noncheck(&mut a, score + 250, score + 251, false, &mut am);
    let actual = worker.select_noncheck(&mut b, score + 250, score + 251, false, &mut bm);
    assert_eq!((actual, b, bm), (expected, a, am));
    assert!(!actual.refreshed && !actual.initially_full);
    assert_eq!(a, before);
    assert!(am.is_none());
    assert_eq!(worker.stats, serial.stats);
}

#[test]
fn budgets_preserve_zero_group_replacement_order_and_reset() {
    let empty = Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 0 1").unwrap();
    let first = Position::from_fen("7k/8/8/8/6P1/3P4/8/K7 w - - 0 1").unwrap();
    let second = Position::from_fen("7k/8/6P1/8/8/3P4/8/K7 w - - 0 1").unwrap();
    assert_eq!(empty.pawn, 0);
    assert_eq!(first.pawn % 128, 0);
    assert_eq!(second.pawn % 128, 0);
    assert_ne!(first.pawn, second.pawn);
    let (mut serial, mut worker) = evaluators::<true>(&empty);
    for (position, reused) in [(empty, true), (first, false), (first, true),
        (second, false), (first, false), (empty, false), (empty, true)]
    {
        let node = Node::root(position, &serial.root);
        let value = compare(&mut serial, &mut worker, node, &Influence::build(&position), false, false);
        assert_eq!(value.details.pawn_entry_reused, reused);
    }
    serial.begin_search(&empty);
    worker.begin_search(&empty);
    let node = Node::root(empty, &serial.root);
    let map = Influence::build(&empty);
    compare(&mut serial, &mut worker, node, &map, false, true);
    assert_eq!((worker.stats.pawn_reuses, worker.stats.pawn_replacements), (0, 1));
    assert!(compare(&mut serial, &mut worker, node, &map, false, false).details.pawn_entry_reused);
    serial.begin_search(&first);
    worker.begin_search(&first);
    let node = Node::root(first, &serial.root);
    let value = compare(&mut serial, &mut worker, node, &Influence::build(&first), false, false);
    assert!(!value.details.pawn_entry_reused);
    assert_eq!((worker.stats.full, worker.stats.pawn_replacements), (1, 1));
}

#[test]
fn budgets_preserve_full_identity_collision_and_fresh_cache_bypass() {
    let first = Position::from_fen("7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7 w - - 0 1").unwrap();
    let collision = Position::from_fen("7k/8/2p4P/2p5/7P/1p6/p5PP/K7 w - - 0 1").unwrap();
    assert_eq!(first.pawn, collision.pawn);
    assert_ne!(first.pawn, 0);
    let (first_map, collision_map) = (Influence::build(&first), Influence::build(&collision));
    let (mut serial, mut worker) = evaluators::<true>(&first);
    let node = Node::root(first, &serial.root);
    assert!(!compare(&mut serial, &mut worker, node, &first_map, false, false).details.pawn_entry_reused);
    let retained = serial.pawns.select(&first, &first_map).structure;
    assert_eq!(worker.pawns.select(&first, &first_map).structure, retained);
    assert_ne!(retained, pawn_structure::fresh(&collision, &collision_map, [1024; 2]));
    let node = Node::root(collision, &serial.root);
    assert!(compare(&mut serial, &mut worker, node, &collision_map, false, false).details.pawn_entry_reused);
    compare(&mut serial, &mut worker, node, &collision_map, false, true);
    assert!(compare(&mut serial, &mut worker, node, &collision_map, false, false).details.pawn_entry_reused);
    assert_eq!(serial.pawns.select(&collision, &collision_map).structure, retained);
    assert_eq!(worker.pawns.select(&collision, &collision_map).structure, retained);
    serial.begin_search(&collision);
    worker.begin_search(&collision);
    let node = Node::root(collision, &serial.root);
    assert!(!compare(&mut serial, &mut worker, node, &collision_map, false, false).details.pawn_entry_reused);
    assert_eq!(worker.pawns.select(&collision, &collision_map).structure,
        pawn_structure::fresh(&collision, &collision_map, [1024; 2]));
}

fn assert_search_equal(actual: &ordinary::Outcome, expected: &ordinary::Outcome) {
    assert_eq!((&actual.initial_candidates, actual.score, &actual.pv, actual.work,
        actual.stats, actual.evaluations), (&expected.initial_candidates, expected.score,
        &expected.pv, expected.work, expected.stats, expected.evaluations));
    assert_eq!(actual.iterations.len(), expected.iterations.len());
    for (a, b) in actual.iterations.iter().zip(&expected.iterations) {
        assert_eq!((a.depth, &a.candidates, &a.steps, a.score, &a.pv, a.work),
            (b.depth, &b.candidates, &b.steps, b.score, &b.pv, b.work));
    }
}

fn replay_pv(mut position: Position, pv: &[Move]) {
    for &movement in pv {
        let mut legal = MoveList::new();
        generate_legal(&position, &mut legal);
        assert!(legal.as_slice().contains(&movement), "illegal PV move {movement}");
        position = position.played_unchecked(movement);
    }
}

fn completed_pair(serial: &mut Search, worker: &mut Search, position: Position) -> ordinary::Outcome {
    let (mut ah, mut bh) = (SearchHistory::new(&position), SearchHistory::new(&position));
    let (mut ar, mut br) = (Vec::new(), Vec::new());
    let expected = serial.run_seeded_iterations(position, &mut ah, 2, Limits::default(),
        0x1020_3040, 7, |score| ar.push(score)).unwrap();
    let actual = worker.run_seeded_iterations(position, &mut bh, 2, Limits::default(),
        0x1020_3040, 7, |score| br.push(score)).unwrap();
    assert_eq!((ah.search_ply(), bh.search_ply()), (0, 0));
    assert_eq!(ar, br);
    assert_search_equal(&actual, &expected);
    assert!(actual.evaluations.full > 0);
    for iteration in &actual.iterations {
        replay_pv(position, &iteration.pv);
        for step in &iteration.steps {
            replay_pv(position, &step.root_pv);
            replay_pv(position.played_unchecked(step.movement), &step.child_pv);
        }
    }
    expected
}

#[test]
fn persistent_worker_crosses_repeated_search_stop_retry_and_budget_changes() {
    let position = Position::from_fen(START).unwrap();
    let mut serial = Search::<true>::new(&position);
    let mut worker = Search::<true>::new(&position);
    serial.config.tts_bytes = 65536;
    worker.config.tts_bytes = 65536;
    serial.evaluator.set_threads(1).unwrap();
    worker.evaluator.set_threads(2).unwrap();
    let baseline = completed_pair(&mut serial, &mut worker, position);
    let repeated = completed_pair(&mut serial, &mut worker, position);
    assert_search_equal(&repeated, &baseline);
    let other = Position::from_fen("r3k3/8/8/8/2n5/8/8/RN2K3 w - - 0 1").unwrap();
    completed_pair(&mut serial, &mut worker, other);
    assert_search_equal(&completed_pair(&mut serial, &mut worker, position), &baseline);

    for limit in [0, 25] {
        let (mut ah, mut bh) = (SearchHistory::new(&position), SearchHistory::new(&position));
        let (mut ar, mut br) = (Vec::new(), Vec::new());
        let expected = serial.run_seeded_iterations(position, &mut ah, 3,
            Limits { nodes: Some(limit) }, 0x1020_3040, 7, |score| ar.push(score));
        let actual = worker.run_seeded_iterations(position, &mut bh, 3,
            Limits { nodes: Some(limit) }, 0x1020_3040, 7, |score| br.push(score));
        assert!(matches!(expected, Err(ordinary::Error::Stopped(Stopped::NodeLimit(n))) if n == limit));
        assert!(matches!(actual, Err(ordinary::Error::Stopped(Stopped::NodeLimit(n))) if n == limit));
        assert_eq!((ah.search_ply(), bh.search_ply()), (0, 0));
        assert_eq!(ar, br);
        assert_eq!(worker.work(), serial.work());
        assert_eq!(worker.stats, serial.stats);
        assert_eq!(worker.evaluator.stats, serial.evaluator.stats);
        assert_search_equal(&completed_pair(&mut serial, &mut worker, position), &baseline);
    }
    assert!(worker.evaluator.set_threads(0).is_err());
    worker.evaluator.set_threads(3).unwrap();
    assert_eq!((worker.requested_threads(),worker.configured_threads()),(3,2));
    assert_search_equal(&completed_pair(&mut serial, &mut worker, position), &baseline);
    worker.evaluator.set_threads(1).unwrap();
    assert_search_equal(&completed_pair(&mut serial, &mut worker, position), &baseline);
    worker.evaluator.set_threads(2).unwrap();
    assert_search_equal(&completed_pair(&mut serial, &mut worker, position), &baseline);
    // Drop joins an active persistent worker after its last completed FULL.
}

#[test]
fn positive_total_requests_saturate_without_changing_cache_or_evaluation() {
    let first = Position::from_fen("7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7 w - - 0 1").unwrap();
    let collision = Position::from_fen("7k/8/2p4P/2p5/7P/1p6/p5PP/K7 w - - 0 1").unwrap();
    assert_eq!(first.pawn,collision.pawn);
    let (mut serial,mut worker)=(Evaluator::<true>::new(&first),Evaluator::<true>::new(&first));
    assert_eq!((worker.requested_threads(),worker.configured_threads()),(1,1));
    let first_map=Influence::build(&first);
    let node=Node::root(first,&serial.root);
    compare(&mut serial,&mut worker,node,&first_map,false,false);
    let collision_map=Influence::build(&collision);
    for requested in [2,3,usize::MAX,1,2,1] {
        let before=worker.stats;
        worker.set_threads_with_affinity(requested,||Ok(2)).unwrap();
        assert_eq!((worker.requested_threads(),worker.configured_threads()),(requested,requested.min(2)));
        assert_eq!(worker.stats,before);
        assert!(worker.set_threads(0).is_err());
        assert_eq!((worker.requested_threads(),worker.configured_threads()),(requested,requested.min(2)));
        assert_eq!(worker.stats,before);
        let node=Node::root(collision,&serial.root);
        assert!(compare(&mut serial,&mut worker,node,&collision_map,false,false).details.pawn_entry_reused);
        if let Some(helper)=&worker.full_worker {assert!(helper.is_parked());}
    }
}

#[test]
fn search_and_session_expose_requested_and_configured_budgets() {
    let position=Position::from_fen(START).unwrap();
    let mut search=Search::<false>::new(&position);
    assert_eq!((search.requested_threads(),search.configured_threads()),(1,1));
    search.set_threads(3).unwrap();
    let (mut search,_)=search.map_host(crate::host::NoHost);
    assert_eq!((search.requested_threads(),search.configured_threads()),(3,2));
    assert!(search.set_threads(0).is_err());
    assert_eq!((search.requested_threads(),search.configured_threads()),(3,2));
    search.set_threads(1).unwrap();
    assert_eq!((search.requested_threads(),search.configured_threads()),(1,1));
    let mut session=crate::session::Session::<false>::default();
    assert_eq!((session.requested_threads().unwrap(),session.configured_threads().unwrap()),(1,1));
    session.set_threads(usize::MAX).unwrap();
    assert_eq!((session.requested_threads().unwrap(),session.configured_threads().unwrap()),(usize::MAX,2));
    assert!(session.set_threads(0).is_err());
    assert_eq!((session.requested_threads().unwrap(),session.configured_threads().unwrap()),(usize::MAX,2));
    session.set_threads(1).unwrap();
    assert_eq!((session.requested_threads().unwrap(),session.configured_threads().unwrap()),(1,1));
}

#[test]
fn affinity_cap_queries_before_mutation_and_preserves_active_cache_on_failure() {
    let first=Position::from_fen("7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7 w - - 0 1").unwrap();
    let collision=Position::from_fen("7k/8/2p4P/2p5/7P/1p6/p5PP/K7 w - - 0 1").unwrap();
    assert_eq!(first.pawn,collision.pawn);
    let (mut serial,mut worker)=(Evaluator::<true>::new(&first),Evaluator::<true>::new(&first));
    assert!(worker.set_threads_with_affinity(0,||panic!("invalid request queried affinity")).is_err());
    worker.set_threads_with_affinity(1,||panic!("one thread queried affinity")).unwrap();
    worker.set_threads_with_affinity(2,||Ok(2)).unwrap();
    let node=Node::root(first,&serial.root);
    compare(&mut serial,&mut worker,node,&Influence::build(&first),false,false);
    let before=worker.stats;
    assert_eq!(worker.set_threads_with_affinity(8,||Err("affinity query failed".into())),
        Err("affinity query failed".into()));
    assert_eq!((worker.requested_threads(),worker.configured_threads()),(2,2));
    assert_eq!(worker.stats,before);
    assert!(worker.full_worker.as_ref().unwrap().is_parked());
    assert!(worker.set_threads_with_affinity(0,||panic!("invalid request queried affinity")).is_err());
    assert!(worker.set_threads_with_affinity(8,||Ok(0)).is_err());
    assert_eq!((worker.requested_threads(),worker.configured_threads()),(2,2));
    assert_eq!(worker.stats,before);
    let map=Influence::build(&collision);
    let node=Node::root(collision,&serial.root);
    assert!(compare(&mut serial,&mut worker,node,&map,false,false).details.pawn_entry_reused);
    for (requested,allowed,configured) in [(8,1,1),(usize::MAX,2,2),(2,1,1),(3,4,2)] {
        let before=worker.stats;
        worker.set_threads_with_affinity(requested,||Ok(allowed)).unwrap();
        assert_eq!((worker.requested_threads(),worker.configured_threads()),(requested,configured));
        assert_eq!(worker.stats,before);
        assert_eq!(worker.full_worker.is_some(),configured==2);
        assert!(compare(&mut serial,&mut worker,node,&map,false,false).details.pawn_entry_reused);
    }
    worker.set_threads_with_affinity(1,||panic!("one thread queried affinity")).unwrap();
    assert_eq!((worker.requested_threads(),worker.configured_threads()),(1,1));
}
