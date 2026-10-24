//! Differential FULL composition and actual-cache ownership controls.
use super::*;
use crate::engine::Search;
use crate::history::SearchHistory;
use crate::pawn_structure::PawnCacheCore;
use crate::quiescence::{Limits, Stopped};
use std::panic::{catch_unwind, AssertUnwindSafe};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const MIDDLE: &str = "r3k2r/ppp2ppp/2npbn2/3qp3/3PP3/2N1BN2/PPP2PPP/R2Q1RK1 b kq - 0 10";
const ENDING: &str = "6k1/5pp1/6p1/3P4/8/2N5/5P2/6K1 w - - 0 40";
const FIRST: &str = "7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7 w - - 0 1";
const COLLISION: &str = "7k/8/2p4P/2p5/7P/1p6/p5PP/K7 w - - 0 1";

fn cache<const D: bool>(evaluator: &mut Evaluator<D>) -> PawnCacheCore {
    if let Some(worker) = &mut evaluator.pawn_worker {
        worker.snapshot_core().unwrap()
    } else {
        // Cold test observation only. Production FULL never copies the core.
        let core = evaluator.pawns.take_core();
        let observed = core.clone();
        evaluator.pawns.install_core(core);
        observed
    }
}

fn parked<const D: bool>(evaluator: &Evaluator<D>) {
    if let Some(worker) = &evaluator.research_worker { assert!(worker.is_parked()); }
    if let Some(worker) = &evaluator.pawn_worker { assert!(worker.is_parked()); }
}

#[derive(Debug, PartialEq, Eq)]
struct Observed { evaluation: Evaluation, details: FullDetails, node: Node }

fn observe<const D: bool>(evaluator: &mut Evaluator<D>, mut node: Node,
    map: &Influence, checked: bool, fresh: bool) -> Observed {
    let before = node.retained;
    let stats = evaluator.stats;
    let mut details = None;
    let evaluation = if fresh {
        evaluator.fresh_detailed_observed(&mut node, map, checked, |value| details = Some(value))
    } else {
        evaluator.full_detailed_observed(&mut node, map, checked, |value| details = Some(value))
    };
    let details = details.unwrap();
    assert_eq!(details.base, details.components.base());
    assert_eq!(node.retained.nonking_squares, before.nonking_squares);
    assert_eq!(node.retained.age, 0);
    assert_eq!(node.retained.positional, details.components.positional());
    assert_eq!(node.retained.pawn_progress, details.components.pawn_progress);
    assert_eq!(evaluator.stats.relation_queries-stats.relation_queries, evaluation.relation_queries);
    assert_eq!(evaluator.stats.full-stats.full, u64::from(D));
    assert_eq!(evaluator.stats.pawn_reuses-stats.pawn_reuses, u64::from(D && details.pawn_entry_reused));
    assert_eq!(evaluator.stats.pawn_replacements-stats.pawn_replacements, u64::from(D && !details.pawn_entry_reused));
    if fresh { assert!(!details.pawn_entry_reused); }
    parked(evaluator);
    Observed { evaluation, details, node }
}

#[test]
fn all_placements_match_components_retained_relations_supplied_maps_and_rebinding() {
    fn verify<const D: bool>() {
        let initial = Position::from_fen(START).unwrap();
        let mut evaluators = [Evaluator::<D>::new(&initial), Evaluator::new(&initial), Evaluator::new(&initial)];
        for (evaluator, mode) in evaluators.iter_mut().zip([
            ResearchFullMode::Inline, ResearchFullMode::Current, ResearchFullMode::Reversed]) {
            evaluator.set_research_full_mode(mode).unwrap();
        }
        let mut asymmetric = Parameters::default();
        asymmetric.own = [133,73,151,87,200,121,19,313,207,251,49];
        asymmetric.opponent = [91,128,67,142,80,57,183,47,333,107,229];
        asymmetric.average_depth = 13; asymmetric.draw = -173; asymmetric.opponent_selectivity = 31;
        let mut zero = Parameters::default(); zero.own[6..].fill(0); zero.opponent[6..].fill(0);
        for fen in [START, MIDDLE, ENDING, START] {
            let position = Position::from_fen(fen).unwrap();
            for parameters in [Parameters::default(), asymmetric.clone(), zero.clone()] {
                for evaluator in &mut evaluators {
                    evaluator.parameters = parameters.clone();
                    evaluator.begin_search(&position);
                    assert_eq!(evaluator.stats, EvalStats::default());
                    parked(evaluator);
                }
                let natural = Influence::build(&position);
                let contrary = Influence { profiles: [[255;64], [0;64]] };
                for map in [&natural, &contrary] {
                    for checked in [false, true] {
                        let mut node = Node::root(position, &evaluators[0].root);
                        node.retained.positional = 731; node.retained.pawn_progress = -193; node.retained.age = 17;
                        for fresh in [false, false, true, false] {
                            let before = cache(&mut evaluators[0]);
                            let expected = observe(&mut evaluators[0], node, map, checked, fresh);
                            let expected_cache = cache(&mut evaluators[0]);
                            if fresh { assert_eq!(expected_cache, before); }
                            let expected_stats = evaluators[0].stats;
                            for evaluator in &mut evaluators[1..] {
                                assert_eq!(observe(evaluator, node, map, checked, fresh), expected);
                                assert_eq!(evaluator.stats, expected_stats);
                                assert_eq!(cache(evaluator), expected_cache);
                            }
                        }
                    }
                }
            }
        }
    }
    verify::<true>(); verify::<false>();
}

#[test]
fn actual_identity_and_group_cache_entries_survive_every_mode_transfer_and_fresh() {
    let first = Position::from_fen(FIRST).unwrap();
    let collision = Position::from_fen(COLLISION).unwrap();
    assert_eq!(first.pawn, collision.pawn);
    let group_a = Position::from_fen("7k/8/8/8/6P1/3P4/8/K7 w - - 0 1").unwrap();
    let group_b = Position::from_fen("7k/8/6P1/8/8/3P4/8/K7 w - - 0 1").unwrap();
    assert_eq!(group_a.pawn%128, group_b.pawn%128); assert_ne!(group_a.pawn, group_b.pawn);
    let mut serial = Evaluator::<true>::new(&first);
    let mut switched = Evaluator::<true>::new(&first);
    for (step, (mode, position, fresh)) in [
        (ResearchFullMode::Inline, first, false),
        (ResearchFullMode::Reversed, collision, false),
        (ResearchFullMode::Current, collision, true),
        (ResearchFullMode::Reversed, collision, false),
        (ResearchFullMode::Inline, group_a, false),
        (ResearchFullMode::Reversed, group_b, false),
        (ResearchFullMode::Current, group_a, false),
        (ResearchFullMode::Inline, collision, false),
    ].into_iter().enumerate() {
        let before = cache(&mut switched);
        switched.set_research_full_mode(mode).unwrap();
        assert_eq!(cache(&mut switched), before, "mode change cleared actual cache");
        let node = Node::root(position, &serial.root);
        let map = Influence::build(&position);
        let expected = observe(&mut serial, node, &map, false, fresh);
        let actual = observe(&mut switched, node, &map, false, fresh);
        assert_eq!(actual, expected);
        assert_eq!(switched.stats, serial.stats);
        assert_eq!(cache(&mut switched), cache(&mut serial));
        if step == 1 || step == 3 { assert!(actual.details.pawn_entry_reused); }
    }
    for evaluator in [&mut serial, &mut switched] { evaluator.begin_search(&collision); }
    let node = Node::root(collision, &serial.root); let map = Influence::build(&collision);
    assert!(!observe(&mut serial, node, &map, false, false).details.pawn_entry_reused);
    assert!(!observe(&mut switched, node, &map, false, false).details.pawn_entry_reused);
    assert_eq!(cache(&mut switched), cache(&mut serial));
}

#[test]
fn fast_remains_local_and_lazy_full_keeps_authoritative_supplied_map() {
    let position = Position::from_fen(MIDDLE).unwrap();
    let mut serial = Evaluator::<true>::new(&position);
    let mut reversed = Evaluator::<true>::new(&position);
    reversed.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
    let contrary = Influence { profiles: [[255;64], [0;64]] };
    let node = Node::root(position, &serial.root);
    let before = cache(&mut reversed);
    for checked in [false, true] {
        assert_eq!(reversed.fast(&node, checked), serial.fast(&node, checked));
        assert_eq!(reversed.stats, serial.stats); parked(&reversed);
    }
    assert_eq!(cache(&mut reversed), before);
    let score = serial.fast(&node, false).score;
    reversed.fast(&node, false);
    for (lower, upper, exception) in [(score+500, score+501, false), (-10000,10000,true)] {
        let (mut a, mut b) = (node, node);
        let (mut am, mut bm) = (Some(contrary), Some(contrary));
        let expected = serial.select_noncheck_for_search(&mut a, lower, upper, exception, &mut am, false);
        let actual = reversed.select_noncheck_for_search(&mut b, lower, upper, exception, &mut bm, false);
        assert_eq!((actual,b,bm), (expected,a,am));
        assert_eq!(reversed.stats, serial.stats); assert_eq!(cache(&mut reversed), cache(&mut serial));
        parked(&reversed);
    }
}

#[test]
fn abandoned_result_keeps_native_cache_mutation_until_mode_transfer() {
    let first = Position::from_fen(FIRST).unwrap();
    let next = Position::from_fen(START).unwrap();
    let mut reference = Evaluator::<true>::new(&first);
    let mut reversed = Evaluator::<true>::new(&first);
    reversed.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
    for evaluator in [&mut reference, &mut reversed] {
        let node = Node::root(first, &evaluator.root);
        observe(evaluator, node, &Influence::build(&first), false, false);
    }
    let map = Influence::build(&next);
    reference.pawns.select(&next, &map);
    let expected = cache(&mut reference);
    let stats = reversed.stats;
    let worker = reversed.pawn_worker.as_mut().unwrap();
    let scope = worker.start_active_scope().unwrap();
    worker.dispatch::<false>(&next, &map, next.phase(), reversed.root.material(&next),
        reversed.weights.structure, reversed.weights.progress).unwrap();
    drop(scope); // Drain authoritative selection; discard only the result packet.
    parked(&reversed);
    assert_eq!(cache(&mut reversed), expected);
    assert_eq!(reversed.stats, stats, "abandoned output published evaluation counters");
    reversed.set_research_full_mode(ResearchFullMode::Inline).unwrap();
    assert_eq!(cache(&mut reversed), expected);
}

#[test]
fn worker_failure_after_selection_restores_mutated_cache_before_returning_error() {
    let position = Position::from_fen(START).unwrap();
    let map = Influence::build(&position);
    let mut reference = Evaluator::<true>::new(&position);
    reference.pawns.select(&position, &map);
    let expected = cache(&mut reference);
    assert_ne!(expected, PawnCacheCore::new(), "failure fixture must mutate authoritative entries");
    let mut reversed = Evaluator::<true>::new(&position);
    reversed.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
    reversed.pawn_worker.as_ref().unwrap().fail_after_selection_next();
    let mut node = Node::root(position, &reversed.root);
    let saved_node = node;
    let stats = reversed.stats;
    assert!(catch_unwind(AssertUnwindSafe(|| reversed.full(&mut node, &map, false))).is_err());
    assert_eq!(node, saved_node); assert_eq!(reversed.stats, stats);
    assert!(reversed.set_research_full_mode(ResearchFullMode::Inline).is_err());
    assert!(reversed.pawn_worker.is_none());
    assert_eq!(cache(&mut reversed), expected, "failed transfer resumed with a fresh placeholder");
    assert!(observe(&mut reversed, saved_node, &map, false, false).details.pawn_entry_reused);
    reversed.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
    assert_eq!(cache(&mut reversed), expected);
}

#[test]
fn native_search_repeated_roots_stops_and_scope_unwind_preserve_reversed_state() {
    let initial = Position::from_fen(START).unwrap();
    let mut serial = Search::<true>::new(&initial);
    let mut reversed = Search::<true>::new(&initial);
    serial.config.tts_bytes = 65536; reversed.config.tts_bytes = 65536;
    for fen in [START, ENDING, START] {
        let position = Position::from_fen(fen).unwrap();
        reversed.evaluator.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
        let (mut a, mut b) = (SearchHistory::new(&position), SearchHistory::new(&position));
        let expected = serial.run_iterations(position, &mut a, 2, Limits::default()).unwrap();
        let actual = reversed.run_iterations(position, &mut b, 2, Limits::default()).unwrap();
        assert_eq!((actual.score,actual.pv,actual.work,actual.stats,actual.evaluations),
                   (expected.score,expected.pv,expected.work,expected.stats,expected.evaluations));
        assert_eq!(a.search_ply(), 0); assert_eq!(b.search_ply(), 0); parked(&reversed.evaluator);
        assert_eq!(cache(&mut reversed.evaluator), cache(&mut serial.evaluator));
        for limit in [0,25] {
            assert!(matches!(serial.run_iterations(position,&mut a,3,Limits{nodes:Some(limit)}),
                Err(crate::ordinary::Error::Stopped(Stopped::NodeLimit(n))) if n==limit));
            assert!(matches!(reversed.run_iterations(position,&mut b,3,Limits{nodes:Some(limit)}),
                Err(crate::ordinary::Error::Stopped(Stopped::NodeLimit(n))) if n==limit));
            assert_eq!(reversed.stats,serial.stats); assert_eq!(reversed.evaluator.stats,serial.evaluator.stats);
            assert_eq!(cache(&mut reversed.evaluator),cache(&mut serial.evaluator)); parked(&reversed.evaluator);
        }
        reversed.evaluator.set_research_full_mode(ResearchFullMode::Inline).unwrap();
        #[cfg(feature="branch-transactions")]
        assert!(reversed.research_eq(&serial));
    }
    reversed.evaluator.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
    let mut history = SearchHistory::new(&initial);
    assert!(catch_unwind(AssertUnwindSafe(|| reversed.run_seeded_iterations(initial,&mut history,1,
        Limits::default(),0,0,|_|panic!("reversed root callback unwind")))).is_err());
    parked(&reversed.evaluator);
}

#[test]
fn reversed_scope_parks_after_live_finish_abort_and_host_error() {
    use crate::host::{Command, Control, Host};
    struct Events { command: Option<Command>, fail: bool }
    impl Host for Events {
        fn command(&mut self) -> std::io::Result<Option<Command>> {
            if self.fail { Err(std::io::Error::other("reversed host control failure")) }
            else { Ok(self.command.take()) }
        }
    }
    for (command, fail) in [(Some(Command::Finish),false), (Some(Command::Abort),false), (None,true)] {
        let position = Position::from_fen(START).unwrap();
        let mut search = Search::<true>::new(&position); search.config.tts_bytes = 65536;
        search.evaluator.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
        let (mut search, _) = search.map_host(Events { command, fail });
        search.control = Some(Control { clock: crate::clock::GameClock::default(), post:false,
            force:false, pondering:false, published:false, fine_work:false, game_ply:0,
            initial_side:position.side, clock_color:position.side });
        let controls = crate::timed::Controls { average_cs:1000, maximum_cs:10000, origin:0,
            seed:0, randomness:0, maximum_entered_iterations:8 };
        let mut history = SearchHistory::new(&position);
        let result = search.run_work_timed(position,&mut history,controls,Limits { nodes:Some(10000) });
        if fail {
            assert!(matches!(result,Err(crate::ordinary::Error::Stopped(Stopped::HostIo(_)))));
        } else {
            assert_eq!(result.unwrap().stop.reason,if command==Some(Command::Abort) {"abort"} else {"host"});
        }
        parked(&search.evaluator); assert_eq!(history.search_ply(),0);
        let before = cache(&mut search.evaluator);
        search.evaluator.set_research_full_mode(ResearchFullMode::Inline).unwrap();
        assert_eq!(cache(&mut search.evaluator),before);
    }
}

#[cfg(feature="branch-transactions")]
#[test]
fn serial_journal_and_snapshot_admission_never_touch_worker_placeholder() {
    let position = Position::from_fen(START).unwrap();
    let mut evaluator = Evaluator::<true>::new(&position);
    let initial = cache(&mut evaluator);
    evaluator.research_attach_sink(Some(crate::branch_journal::Sink::new(8)));
    assert!(evaluator.set_research_full_mode(ResearchFullMode::Reversed).is_err());
    evaluator.research_attach_sink(None);
    assert_eq!(cache(&mut evaluator),initial);
    evaluator.set_research_full_mode(ResearchFullMode::Reversed).unwrap();
    assert!(catch_unwind(AssertUnwindSafe(|| evaluator.research_attach_sink(
        Some(crate::branch_journal::Sink::new(8))))).is_err());
    assert!(catch_unwind(AssertUnwindSafe(|| evaluator.research_clone())).is_err());
    evaluator.set_research_full_mode(ResearchFullMode::Inline).unwrap();
    assert_eq!(cache(&mut evaluator),initial);
}
