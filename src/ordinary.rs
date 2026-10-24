//! Ordinary recursive policy with shared tactical, retained and learned state.
//! Fixed-iteration and work-timed callers share this native recursive kernel.
use crate::engine::Search;
use crate::evaluator::{EvalStats, Node};
use crate::first_iteration::Step;
use crate::history::SearchHistory;
use crate::influence::Influence;
use crate::movegen::{self, MoveList};
use crate::ordinary_policy::{self as policy, Extensions};
use crate::position::Position;
use crate::quiescence::{Entry as TacticalEntry, Limits, Stats, Stopped, Work};
use crate::quiescence_policy;
use crate::remembered::{Bound, Query, Store};
use crate::tactical;
use crate::types::{Move, MoveKind, PieceKind};

pub const FIDELITY: &str = "neutral-evaluation-ordinary-iterations-v2";

#[derive(Debug)]
pub enum Error {
    NoLegalRoots,
    InvalidDepth,
    Table(String),
    Stopped(Stopped),
    IterationCapacity,
    Host(std::io::Error),
}

#[cfg(test)]
mod tests {
    use super::*;
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn engine<const D: bool>(position: &Position) -> Search<D> {
        let mut search = Search::new(position);
        search.config.tts_bytes = 65536;
        search
    }

    #[test]
    fn zero_randomness_keeps_fixed_wrapper_records_and_work_exact() {
        for fen in [START, "r3k3/8/8/8/2n5/8/8/RN2K3 w - - 0 1",
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"] {
            let position = Position::from_fen(fen).unwrap();
            let mut ordinary = engine::<true>(&position);
            let mut seeded = engine::<true>(&position);
            let mut history = SearchHistory::new(&position);
            let expected = ordinary.run_iterations(position, &mut history, 2, Limits::default()).unwrap();
            let mut raw = Vec::new();
            let actual = seeded.run_seeded_iterations(position, &mut history, 2,
                Limits::default(), u32::MAX, 0, |score| raw.push(score)).unwrap();
            assert_eq!(history.search_ply(), 0);
            assert_eq!((&actual.initial_candidates, actual.score, &actual.pv, actual.work),
                (&expected.initial_candidates, expected.score, &expected.pv, expected.work));
            for (a,b) in actual.iterations.iter().zip(&expected.iterations) {
                assert_eq!((&a.candidates, &a.steps, a.score, &a.pv, a.work),
                    (&b.candidates, &b.steps, b.score, &b.pv, b.work));
            }
            assert_eq!(raw, actual.iterations.iter().flat_map(|i| i.steps.iter().map(|s| s.score)).collect::<Vec<_>>());
        }
    }

    #[test]
    fn explicit_zero_seed_observes_actual_child_and_preserves_root_return_order() {
        let position = Position::from_fen(START).unwrap();
        let mut direct = engine::<true>(&position);
        let (root, influence) = direct.prepare_root_with_influence(position);
        let checked = movegen::in_check(&position, position.side);
        let mut legal = MoveList::new(); movegen::generate_legal(&position, &mut legal);
        let movement = legal.moves[0];
        let mut child = root.child(&direct.evaluator.root, movement);
        let mut history = SearchHistory::new(&position);
        direct.begin_sequence(Limits::default());
        history.push(&child.position, Some(movement));
        let raw_first = -direct.visit_ordinary(&mut child, &mut history,
            Request { ply:1, depth:0, lower:-10000, upper:10000,
                previous_extension:0, iteration:1, checked:None },
            Predecessor { position:&position, influence:&influence, checked,
                movement:Some(movement) }).unwrap();
        history.pop();
        let child_pv = direct.pv[1][..direct.pv_len[1]].to_vec();
        let first_work = direct.work();
        let mut seeded = engine::<true>(&position);
        let mut raw = Vec::new();
        let actual = seeded.run_seeded_iterations(position, &mut history, 2,
            Limits::default(), 0, 50, |score| raw.push(score)).unwrap();
        assert_eq!(raw[0], raw_first);
        let first = &actual.iterations[0].steps[0];
        assert_eq!((&first.child_pv, first.work), (&child_pv, first_work));
        let mut observed = raw.into_iter();
        let mut nonzero = false;
        for iteration in &actual.iterations {
            for step in &iteration.steps {
                let adjustment = crate::timed::random_adjustment(0, 50, step.movement);
                nonzero |= adjustment != 0;
                assert_eq!(step.score, crate::timed::score_add(observed.next().unwrap(), adjustment));
            }
            validate_pv(position, &iteration.pv);
        }
        assert!(nonzero && observed.next().is_none());
        assert_eq!(history.search_ply(),0);
        let mut stopped = engine::<true>(&position);
        let mut interrupted_raw = Vec::new();
        assert!(matches!(stopped.run_seeded_iterations(position, &mut history, 2,
            Limits { nodes:Some(0) }, 0, 50, |score| interrupted_raw.push(score)),
            Err(Error::Stopped(Stopped::NodeLimit(0)))));
        assert!(interrupted_raw.is_empty());
        assert_eq!(history.search_ply(),0);
    }

    fn validate_pv(mut position: Position, pv: &[Move]) {
        for &movement in pv {
            let mut legal = MoveList::new();
            movegen::generate_legal(&position, &mut legal);
            assert!(
                legal.as_slice().contains(&movement),
                "illegal PV move {movement}"
            );
            position = position.played_unchecked(movement);
        }
    }

    #[test]
    fn first_iteration_matches_the_independent_root_consumer_exactly() {
        for fen in [
            START,
            "1r5k/6pp/6Q1/8/8/3B4/8/K7 b - - 0 1",
            "r3k3/1Pr5/8/8/8/8/8/4K3 b - - 0 1",
        ] {
            let position = Position::from_fen(fen).unwrap();
            let mut a = engine::<true>(&position);
            let mut b = engine::<true>(&position);
            let mut history = SearchHistory::new(&position);
            let expected =
                crate::first_iteration::run(&mut a, position, &mut history, Limits::default())
                    .unwrap();
            let actual = b
                .run_iterations(position, &mut history, 1, Limits::default())
                .unwrap();
            assert_eq!(
                (actual.score, &actual.pv, actual.work),
                (expected.score, &expected.pv, expected.work)
            );
            assert_eq!(actual.iterations[0].steps, expected.steps);
            assert_eq!(actual.iterations[0].candidates, expected.candidates);
        }
    }

    #[test]
    fn iterative_carryover_is_stable_and_real_pvs_remain_legal() {
        let position = Position::from_fen(START).unwrap();
        let mut search = engine::<true>(&position);
        let mut history = SearchHistory::new(&position);
        let out = search
            .run_iterations(
                position,
                &mut history,
                4,
                Limits {
                    nodes: Some(100000),
                },
            )
            .unwrap();
        assert_eq!(history.search_ply(), 0);
        assert!(
            out.stats.ordinary_nodes > 0 && out.stats.table_stores > 0 && out.stats.table_hits > 0
        );
        assert!(out.evaluations.full > 0 && out.evaluations.fast > 0);
        assert!(out.evaluations.pawn_reuses > 0 && out.evaluations.pawn_replacements > 0);
        for (index, iteration) in out.iterations.iter().enumerate() {
            validate_pv(position, &iteration.pv);
            if index > 0 {
                let mut previous: Vec<&Step> = out.iterations[index - 1].steps.iter().collect();
                previous.sort_by_key(|s| std::cmp::Reverse(s.score));
                assert_eq!(
                    iteration.candidates,
                    previous.iter().map(|s| s.movement).collect::<Vec<_>>()
                );
                assert!(
                    iteration.work.charged_search_units
                        > out.iterations[index - 1].work.charged_search_units
                );
            }
        }
    }

    #[test]
    fn interruption_unwinds_real_ordinary_frames_and_fresh_retry_clears_shared_effects() {
        let position = Position::from_fen(START).unwrap();
        let mut search = engine::<true>(&position);
        let mut history = SearchHistory::new(&position);
        assert!(matches!(
            search.run_iterations(position, &mut history, 3, Limits { nodes: Some(25) }),
            Err(Error::Stopped(Stopped::NodeLimit(25)))
        ));
        assert_eq!(history.search_ply(), 0);
        assert!(search.stats.ordinary_nodes > 0);
        let retry = search
            .run_iterations(position, &mut history, 3, Limits::default())
            .unwrap();
        let mut fresh = engine::<true>(&position);
        let expected = fresh
            .run_iterations(position, &mut history, 3, Limits::default())
            .unwrap();
        assert_eq!(
            (retry.score, retry.pv, retry.work),
            (expected.score, expected.pv, expected.work)
        );
        for (a, b) in retry.iterations.iter().zip(&expected.iterations) {
            assert_eq!(a.steps, b.steps);
        }
    }

    #[test]
    fn diagnostics_preserve_results_work_and_public_history_with_nonempty_game_prefix() {
        let mut position = Position::from_fen(START).unwrap();
        let mut history = SearchHistory::new(&position);
        for token in ["e2e4", "e7e5", "g1f3", "b8c6"] {
            let mut list = MoveList::new();
            movegen::generate_legal(&position, &mut list);
            let movement = *list
                .as_slice()
                .iter()
                .find(|m| m.to_string() == token)
                .unwrap();
            position = position.played_unchecked(movement);
            history.push(&position, Some(movement));
        }
        history.mark_root();
        let mut a = engine::<true>(&position);
        let mut b = engine::<false>(&position);
        let x = a
            .run_iterations(position, &mut history, 3, Limits::default())
            .unwrap();
        let y = b
            .run_iterations(position, &mut history, 3, Limits::default())
            .unwrap();
        assert_eq!((history.search_ply(), history.pre_root_len()), (0, 4));
        assert_eq!((x.score, x.pv, x.work), (y.score, y.pv, y.work));
        assert!(y.iterations.iter().all(|i| i.steps.is_empty()));
    }

    #[test]
    fn real_ordering_passes_with_collisions_preserve_diagnostic_parity_and_legal_pv() {
        let position = Position::from_fen("6k1/8/8/8/8/8/P7/K6R w - - 0 1").unwrap();
        let mut a = engine::<true>(&position);
        let mut b = engine::<false>(&position);
        a.config.tts_bytes = 96;
        b.config.tts_bytes = 96;
        let mut history = SearchHistory::new(&position);
        let x = a
            .run_iterations(
                position,
                &mut history,
                6,
                Limits {
                    nodes: Some(100000),
                },
            )
            .unwrap();
        let y = b
            .run_iterations(
                position,
                &mut history,
                6,
                Limits {
                    nodes: Some(100000),
                },
            )
            .unwrap();
        validate_pv(position, &x.pv);
        assert!(
            x.stats.iio_initial_phases > 0 && x.stats.iio_passes > 0 && x.stats.iio_children > 0
        );
        assert!(
            x.stats.null_trials > 0
                && x.stats.scout_retries > 0
                && x.stats.refreshed_scout_retries > 0
        );
        assert_eq!((x.score, x.pv, x.work), (y.score, y.pv, y.work));
        assert_eq!(history.search_ply(), 0);
    }

    #[test]
    fn qualified_initial_single_passes_have_zero_fresh_ordering_flags_and_diagnostic_parity() {
        for fen in [
            "1r5k/7p/6Q1/8/8/3B4/8/K7 b - - 0 1",
            "1r5k/6pp/6Q1/8/8/3B4/8/K7 b - - 0 1",
        ] {
            let position = Position::from_fen(fen).unwrap();
            let mut a = Search::<true>::new(&position);
            let mut b = Search::<false>::new(&position);
            let mut parameters = crate::parameters::Parameters::default();
            parameters.values[27] = 99;
            parameters.values[29] = 67_108_864;
            parameters.bind(&mut a).unwrap();
            parameters.bind(&mut b).unwrap();
            let mut history = SearchHistory::new(&position);
            let x = a.run_iterations(position, &mut history, 5, Limits { nodes: Some(4095) }).unwrap();
            let y = b.run_iterations(position, &mut history, 5, Limits { nodes: Some(4095) }).unwrap();
            assert!(x.stats.iio_initial_phases > 0);
            assert_eq!(x.stats.iio_passes, x.stats.iio_initial_phases);
            assert_eq!(x.stats.iio_tail_phases, 0);
            assert_eq!(x.stats.iio_nonzero_fresh_extensions, 0);
            assert_eq!(x.stats.accumulated_extension_uses, 0);
            assert_eq!(y.stats.iio_nonzero_fresh_extensions, 0);
            assert_eq!((x.score, x.pv, x.work), (y.score, y.pv, y.work));
            assert_eq!(history.search_ply(), 0);
        }
    }

    #[test]
    fn entry_lower_metadata_selects_tail_and_retains_its_extension_flags() {
        // Isolate a controlled remembered-entry state, rather than claim this
        // metadata necessarily arises in a fresh search of this exact root.
        let position = Position::from_fen("7k/R7/8/8/8/8/8/K7 w - - 0 1").unwrap();
        let mut search = engine::<true>(&position);
        search.ensure_table().unwrap();
        let (root, influence) = search.prepare_root_with_influence(position);
        let mut legal = MoveList::new();
        movegen::generate_legal(&position, &mut legal);
        let movement = *legal
            .as_slice()
            .iter()
            .find(|m| m.to_string() == "a7a8")
            .unwrap();
        let mut child = root.child(&search.evaluator.root, movement);
        let mut history = SearchHistory::new(&position);
        history.push(&child.position, Some(movement));
        search.begin_sequence(Limits {
            nodes: Some(200000),
        });
        let table = search.remembered.as_mut().unwrap();
        table.store(Store {
            query: Query {
                group: table.group_for(&child.position),
                identity: child.position.secondary,
                ply: 1,
                target: 6,
                lower: -10000,
                upper: 100,
            },
            score: 100,
            move_hint: None,
            quiet_mate_checked: true,
            mark_depth: true,
        });
        let score = search
            .visit_ordinary(
                &mut child,
                &mut history,
                Request {
                    ply: 1,
                    depth: 5,
                    lower: -10000,
                    upper: 10000,
                    previous_extension: 0,
                    iteration: 6,
                    checked: Some(true),
                },
                Predecessor {
                    position: &position,
                    influence: &influence,
                    checked: false,
                    movement: Some(movement),
                },
            )
            .unwrap();
        assert!((-10000..10000).contains(&score));
        assert!(search.stats.iio_tail_phases > 0);
        // Two evasions become a one-item tail: its fresh flag2 combines with
        // the main move's flag1; it must not be overwritten by that later1.
        assert!(search.stats.accumulated_extension_uses > 0);
        assert!(search.stats.iio_nonzero_fresh_extensions > 0);
        validate_pv(child.position, &search.pv[1][..search.pv_len[1]]);
        assert_eq!(history.search_ply(), 1);
    }
    #[test]
    fn disabled_iio_counts_actual_initial_and_tail_entry_before_any_phase_work() {
        let position=Position::from_fen(START).unwrap();
        for start in [0,1] {
            let mut search=engine::<true>(&position);
            let (node,map)=search.prepare_root_with_influence(position);
            let mut history=SearchHistory::new(&position);
            movegen::generate_legal(&position,&mut search.candidates[0]);
            let before=search.candidates[0].as_slice().to_vec();
            search.extension_flags[0].fill(7);
            search.begin_sequence(Limits::default());
            let result=search.ordering_phase::<false>(&node,&mut history,
                Request{ply:0,depth:6,lower:-10000,upper:10000,
                    previous_extension:0,iteration:6,checked:Some(false)},
                Predecessor{position:&position,influence:&map,checked:false,movement:None},
                &map,false,start);
            assert_eq!(result,Err(Stopped::InternalIterativeOrdering));
            assert_eq!((search.stats.iio_initial_phases,search.stats.iio_tail_phases),
                if start==0 {(1,0)} else {(0,1)});
            assert_eq!((search.stats.iio_passes,search.stats.iio_children,
                search.stats.iio_nonzero_fresh_extensions),(0,0,0));
            assert_eq!(search.work(),Work::default());
            assert_eq!(search.candidates[0].as_slice(),before);
            assert!(search.extension_flags[0].iter().all(|&flag|flag==7));
            assert_eq!(history.search_ply(),0);
            assert_eq!(node.position,position);
        }
    }

    fn actual_iio_probe(mode:u8,tail:bool)->(Result<i32,Stopped>,Search<true>,SearchHistory,Node) {
        let position=Position::from_fen("7k/R7/8/8/8/8/8/K7 w - - 0 1").unwrap();
        let mut search=engine::<true>(&position);
        // Tail-only controlled native gate witness: the parent at ply1
        // remains ordinary, while its first ply2 child enters actual Q.
        // This is not a claim about genericTimedSearch's md>=6 admission.
        if tail {search.config.maximum_depth=2;}
        search.ensure_table().unwrap();
        let (root,influence)=search.prepare_root_with_influence(position);
        let mut legal=MoveList::new();movegen::generate_legal(&position,&mut legal);
        let movement=*legal.as_slice().iter().find(|m|m.to_string()=="a7a8").unwrap();
        let mut child=root.child(&search.evaluator.root,movement);
        search.begin_sequence(Limits{nodes:Some(200000)});
        if tail {
            // Lower metadata skips parent initial IIO without returning a
            // score; real Q terminates its first ordinary main-child call.
            let table=search.remembered.as_mut().unwrap();
            table.store(Store{query:Query{group:table.group_for(&child.position),
                identity:child.position.secondary,ply:1,target:6,lower:-10000,upper:100},
                score:100,move_hint:None,quiet_mate_checked:true,mark_depth:true});
            let observed=table.probe(Query{group:table.group_for(&child.position),
                identity:child.position.secondary,ply:1,target:6,
                lower:-10000,upper:10000});
            assert_eq!((observed.bound,observed.marked_depth,observed.score),
                (Bound::Lower,Some(5),None));
        }
        let mut history=SearchHistory::new(&position);
        history.push(&child.position,Some(movement));
        let request=Request{ply:1,depth:5,lower:-10000,upper:10000,
            previous_extension:0,iteration:6,checked:Some(true)};
        let previous=Predecessor{position:&position,influence:&influence,checked:false,
            movement:Some(movement)};
        let result=match mode {
            0=>search.visit_ordinary(&mut child,&mut history,request,previous),
            1=>search.visit_ordinary_impl::<true>(&mut child,&mut history,request,previous),
            2=>search.visit_ordinary_impl::<false>(&mut child,&mut history,request,previous),
            _=>unreachable!(),
        };
        assert_eq!(history.search_ply(),1);
        history.pop();
        (result,search,history,child)
    }

    #[test]
    fn recursive_iio_defaults_true_and_false_initial_tail_errors_unwind_without_phase_subtrees() {
        for tail in [false,true] {
            let (default,a,history_a,node_a)=actual_iio_probe(0,tail);
            let (enabled,b,history_b,node_b)=actual_iio_probe(1,tail);
            assert!(default.is_ok());assert_eq!(default,enabled);
            assert_eq!(a.stats,b.stats);assert_eq!(a.evaluator.stats,b.evaluator.stats);
            assert_eq!(a.work(),b.work());assert_eq!(node_a,node_b);
            assert_eq!(&a.pv[1][..a.pv_len[1]],&b.pv[1][..b.pv_len[1]]);
            assert_eq!((history_a.search_ply(),history_b.search_ply()),(0,0));
            assert!(if tail {a.stats.iio_tail_phases>0} else {a.stats.iio_initial_phases>0});
            let (disabled,c,history_c,_)=actual_iio_probe(2,tail);
            assert_eq!(disabled,Err(Stopped::InternalIterativeOrdering));
            assert_eq!((c.stats.iio_initial_phases,c.stats.iio_tail_phases),
                if tail {(0,1)} else {(1,0)});
            assert_eq!((c.stats.iio_passes,c.stats.iio_children,
                c.stats.iio_nonzero_fresh_extensions),(0,0,0));
            assert_eq!(history_c.search_ply(),0);
            // False reaches the parent's tail only after index1: one
            // ordinary main-child call handed to actual charged Q, with no
            // recursive ordinary entry. Global children includes Q children.
            if tail {
                assert_eq!((c.stats.ordinary_nodes,c.stats.table_probes),(1,1));
                assert!(c.stats.children>=1);
                assert!(c.work().charged_search_units>1);
            } else {assert_eq!(c.stats.children,0);}
        }
    }

}

pub struct Iteration {
    pub depth: u8,
    pub candidates: Vec<Move>,
    pub steps: Vec<Step>,
    pub score: i32,
    pub pv: Vec<Move>,
    pub work: Work,
}

pub struct Outcome {
    pub initial_candidates: Vec<Move>,
    pub iterations: Vec<Iteration>,
    pub score: i32,
    pub pv: Vec<Move>,
    pub work: Work,
    pub stats: Stats,
    pub evaluations: EvalStats,
}

#[derive(Clone, Copy)]
pub(crate) struct Request {
    pub(crate) ply: usize,
    pub(crate) depth: i32,
    pub(crate) lower: i32,
    pub(crate) upper: i32,
    pub(crate) previous_extension: u8,
    pub(crate) iteration: i32,
    pub(crate) checked: Option<bool>,
}

#[derive(Clone, Copy)]
pub(crate) struct Predecessor<'a> {
    pub(crate) position: &'a Position,
    pub(crate) influence: &'a Influence,
    pub(crate) checked: bool,
    pub(crate) movement: Option<Move>,
}

impl<const DIAGNOSTICS: bool, H: crate::host::Host> Search<DIAGNOSTICS, H> {
    pub fn run_iterations(
        &mut self,
        position: Position,
        history: &mut SearchHistory,
        completed: u8,
        limits: Limits,
    ) -> Result<Outcome, Error> {
        self.run_iterations_inner::<false, _>(position, history, completed, limits, 0, 0, |_| {})
    }

    /// Fixed completion with one immutable explicit root seed. The observer
    /// receives each normally completed root's actual unadjusted return once,
    /// before ordinary score addition; no Step or recursive state is enlarged.
    /// `randomness` has the same domain as timed::random_adjustment.
    pub fn run_seeded_iterations<F: FnMut(i32)>(
        &mut self,
        position: Position,
        history: &mut SearchHistory,
        completed: u8,
        limits: Limits,
        seed: u32,
        randomness: u32,
        observe_raw: F,
    ) -> Result<Outcome, Error> {
        self.clear_geometry_permission();
        assert!(randomness <= i32::MAX as u32);
        self.run_iterations_inner::<true, F>(position, history, completed, limits,
            seed, randomness, observe_raw)
    }

    fn run_iterations_inner<const SEEDED: bool, F: FnMut(i32)>(
        &mut self, position: Position, history: &mut SearchHistory,
        completed: u8, limits: Limits, seed: u32, randomness: u32,
        observe_raw: F,
    ) -> Result<Outcome, Error> {
        let _worker_scope = self.evaluator.full_worker_scope();
        self.clear_geometry_permission();
        let result = self.run_iterations_body::<SEEDED, F>(
            position, history, completed, limits, seed, randomness, observe_raw,
        );
        self.clear_geometry_permission();
        result
    }

    fn run_iterations_body<const SEEDED: bool, F: FnMut(i32)>(
        &mut self, position: Position, history: &mut SearchHistory,
        completed: u8, limits: Limits, seed: u32, randomness: u32,
        mut observe_raw: F,
    ) -> Result<Outcome, Error> {
        if !(1..=8).contains(&completed) {
            return Err(Error::InvalidDepth);
        }
        assert_eq!(history.search_ply(), 0);
        self.ensure_table().map_err(Error::Table)?;
        self.bind_geometry_permission(&position);
        let (root, root_influence) = self.prepare_root_with_influence(position);
        let root_checked = movegen::in_check(&position, position.side);
        let mut roots = MoveList::new();
        movegen::generate_legal(&position, &mut roots);
        if roots.len == 0 {
            return Err(Error::NoLegalRoots);
        }
        let initial_candidates = roots.as_slice().to_vec();
        self.begin_owned_sequence(limits);
        let mut iterations = Vec::with_capacity(completed as usize);
        for depth in 1..=completed {
            let mut ranked = Vec::<(Move, i32)>::with_capacity(roots.len);
            let mut best = -10000;
            let mut pv = Vec::with_capacity(63);
            let candidates = roots.as_slice().to_vec();
            let mut steps = Vec::with_capacity(if DIAGNOSTICS { roots.len } else { 0 });
            for &movement in roots.as_slice() {
                let lower = ranked.get(1).map_or(-10000, |entry| entry.1);
                let adjustment = if SEEDED {
                    crate::timed::random_adjustment(seed, randomness, movement)
                } else { 0 };
                let mut child = root.child(&self.evaluator.root, movement);
                history.push(&child.position, Some(movement));
                let returned = self.visit_ordinary(
                    &mut child,
                    history,
                    Request {
                        ply: 1,
                        depth: depth as i32 - 1,
                        lower: if SEEDED { -crate::timed::score_add(10000, -adjustment) } else { -10000 },
                        upper: if SEEDED { -crate::timed::score_add(lower, -adjustment) } else { -lower },
                        previous_extension: 0,
                        iteration: depth as i32,
                        checked: None,
                    },
                    Predecessor {
                        position: &position,
                        influence: &root_influence,
                        checked: root_checked,
                        movement: Some(movement),
                    },
                );
                history.pop();
                let raw_score = -returned.map_err(Error::Stopped)?;
                if SEEDED { observe_raw(raw_score); }
                let score = if SEEDED { crate::timed::score_add(raw_score, adjustment) } else { raw_score };
                if score > best {
                    best = score;
                    pv.clear();
                    pv.push(movement);
                    pv.extend_from_slice(&self.pv[1][..self.pv_len[1]]);
                }
                let place = ranked.partition_point(|entry| entry.1 >= score);
                ranked.insert(place, (movement, score));
                if DIAGNOSTICS {
                    steps.push(Step {
                        movement,
                        lower,
                        score,
                        best,
                        second: ranked.get(1).map_or(-10000, |e| e.1),
                        child_pv: self.pv[1][..self.pv_len[1]].to_vec(),
                        root_pv: pv.clone(),
                        work: self.work(),
                    });
                }
            }
            for (index, (movement, _)) in ranked.into_iter().enumerate() {
                roots.moves[index] = movement;
            }
            iterations.push(Iteration {
                depth,
                candidates,
                steps,
                score: best,
                pv,
                work: self.work(),
            });
        }
        let last = iterations.last().unwrap();
        Ok(Outcome {
            initial_candidates,
            score: last.score,
            pv: last.pv.clone(),
            work: self.work(),
            iterations,
            stats: self.stats,
            evaluations: self.evaluator.stats,
        })
    }

    fn store_ordinary(
        &mut self,
        query: Query,
        score: i32,
        movement: Option<Move>,
        quiet_mate_checked: bool,
        mark_depth: bool,
    ) {
        self.remembered.as_mut().unwrap().store(Store {
            query,
            score,
            move_hint: movement,
            quiet_mate_checked,
            mark_depth,
        });
        if DIAGNOSTICS {
            self.stats.table_stores += 1;
        }
    }

    fn threat(&mut self, node: &Node, influence: &Influence) -> i32 {
        let threat = policy::material_threat(
            &node.position,
            &self.evaluator.root,
            influence,
            node.retained.pawn_progress,
        );
        self.evaluator.stats.relation_queries += threat.queries;
        if DIAGNOSTICS {
            self.stats.material_threats += 1;
        }
        threat.value
    }

    /// Ordinary production and fixed-iteration callers retain full IIO.
    pub(crate) fn visit_ordinary(
        &mut self,
        node: &mut Node,
        history: &mut SearchHistory,
        request: Request,
        previous: Predecessor<'_>,
    ) -> Result<i32, Stopped> {
        self.visit_ordinary_impl::<true>(node, history, request, previous)
    }

    pub(crate) fn visit_ordinary_impl<const ALLOW_IIO: bool>(
        &mut self,
        node: &mut Node,
        history: &mut SearchHistory,
        request: Request,
        previous: Predecessor<'_>,
    ) -> Result<i32, Stopped> {
        let p = request.ply;
        let target = p as i32 + request.depth;
        if policy::quiescence_handoff(request.depth, p, self.config.maximum_depth) {
            return self.visit_q(
                node,
                history,
                TacticalEntry {
                    ply: p,
                    target: target.max(0),
                    iteration_depth: request.iteration,
                    lower: request.lower,
                    upper: request.upper,
                    analysis: self.config.analysis,
                    capture_exception: previous.movement.is_some_and(|m| {
                        quiescence_policy::capture_exception(previous.position, &m)
                    }),
                },
                request.checked,
                false,
            );
        }
        self.charge_node(history)?;
        if DIAGNOSTICS {
            self.stats.ordinary_nodes += 1;
        }
        self.pv_len[p] = 0;
        let position = node.position;
        let checked = request
            .checked
            .unwrap_or_else(|| movegen::in_check(&position, position.side));
        if policy::early_draw(history,p,checked,self.config.analysis,request.upper,&mut self.learning) {
            return Ok(0);
        }
        let table = self.remembered.as_mut().unwrap();
        let query = Query {
            group: table.group_for(&position),
            identity: position.secondary,
            ply: p as i32,
            target,
            lower: request.lower,
            upper: request.upper,
        };
        let remembered = table.probe(query);
        if DIAGNOSTICS {
            self.stats.table_probes += 1;
        }
        if let Some(score) = remembered.score {
            if DIAGNOSTICS {
                self.stats.table_hits += 1;
            }
            return Ok(score);
        }
        let mut preferred = remembered.move_hint;
        let mut quiet_checked = remembered.quiet_mate_checked;
        let adjustment = policy::selective_depth(
            request.iteration,
            self.config.selectivity,
            position.phase().endgame,
            target,
        )
        .adjustment;
        let mut scratch = None;
        let coherent_geometry = self.geometry_permission();
        if policy::fast_admitted(
            &position,
            previous.position,
            previous.movement,
            request.depth,
            adjustment,
        ) {
            let fast = self.evaluator.fast(node, checked);
            if let Some(adjusted) = policy::fast_cutoff_gate(
                fast.score,
                request.depth,
                request.upper,
                checked,
                previous.checked,
                previous
                    .movement
                    .is_some_and(|m| quiescence_policy::capture_exception(previous.position, &m)),
            ) {
                let map = self.evaluator.ensure_influence_for_search(&position, &mut scratch, coherent_geometry);
                if !policy::king_pressure(&position, previous.influence, map) {
                    let trial = adjusted - self.threat(node, map);
                    if trial >= request.upper {
                        if DIAGNOSTICS {
                            self.stats.fast_cutoffs += 1;
                        }
                        self.store_ordinary(query, trial, preferred, quiet_checked, false);
                        return Ok(trial);
                    }
                }
            }
        }
        let map = self.evaluator.ensure_influence_for_search(&position, &mut scratch, coherent_geometry);
        let evaluation = self.evaluator.full(node, map, checked);
        if DIAGNOSTICS {
            self.stats.late_endgame_evaluations += u64::from(evaluation.late_endgame_applied);
        }
        let bounds = policy::evaluation_bounds(p as i32,target,evaluation.lower,evaluation.upper);
        let (effective_lower,effective_upper) = (bounds.lower,bounds.upper);
        if let Some(bound) = bounds.cutoff(request.lower,request.upper) {
            return Ok(bound.score());
        }
        let current = Predecessor {
            position: &position,
            influence: map,
            checked,
            movement: None,
        };
        if request.depth <= adjustment && evaluation.score >= request.upper && !checked {
            let trial = if request.depth <= 2
                && !previous.checked
                && !policy::king_pressure(&position, previous.influence, map)
            {
                evaluation.score - self.threat(node, map) - if request.depth <= 1 { 25 } else { 40 }
            } else {
                if DIAGNOSTICS {
                    self.stats.null_trials += 1;
                }
                let mut child = node.null_child();
                history.push(&child.position, None);
                let returned = self.visit_ordinary_impl::<ALLOW_IIO>(
                    &mut child,
                    history,
                    Request {
                        ply: p + 1,
                        depth: request.depth - if request.depth < 6 { 3 } else { 4 },
                        lower: -request.upper,
                        upper: 1 - request.upper,
                        previous_extension: 0,
                        checked: None,
                        ..request
                    },
                    current,
                );
                history.pop();
                -returned?
            };
            if trial >= request.upper {
                if DIAGNOSTICS {
                    self.stats.shallow_cutoffs += 1;
                }
                self.store_ordinary(query, trial, preferred, quiet_checked, false);
                return Ok(trial);
            }
        }

        movegen::generate_legal(&position, &mut self.candidates[p]);
        let count = self.candidates[p].len;
        if DIAGNOSTICS {
            self.stats.generated += count as u64;
        }
        if count == 0 {
            return Ok(if checked { policy::mate_score(p) } else { 0 });
        }
        if p as i32 - 9998 >= request.upper {
            return Ok(p as i32 - 9998);
        }
        #[cfg(feature = "branch-transactions")]
        let order_journal = self.learning.research_sink();
        #[cfg(feature = "branch-transactions")]
        let order_input = order_journal.as_ref().map(|_| self.candidates[p].as_slice().to_vec());
        tactical::order_by(&mut self.candidates[p], &mut self.ordering, |movement| {
            policy::priority(
                &position,
                &self.evaluator.root,
                map,
                &self.learning,
                p,
                remembered.move_hint,
                movement,
            )
        });
        #[cfg(feature = "branch-transactions")]
        if let (Some(sink), Some(input)) = (order_journal, order_input) {
            sink.record(crate::branch_journal::Event::OrderMain {
                position,
                influence: *map,
                ply: p,
                preferred: remembered.move_hint,
                input,
                expected: self.candidates[p].as_slice().to_vec(),
            });
        }
        self.extension_flags[p][..count].fill(0);
        let encoded = position.counts[position.side.index()][..5]
            .iter()
            .enumerate()
            .map(|(kind, &n)| (n as u32) << (4 * kind))
            .sum::<u32>();
        if !quiet_checked
            && !checked
            && p as i32 <= target / 2
            && p as i32 <= target - 3
            && encoded >= 4112
        {
            for index in 0..count {
                let movement = self.candidates[p].moves[index];
                if movement.kind() != MoveKind::Ordinary {
                    continue;
                }
                let projected = position.attack_view().projected(&position, movement);
                let king = position.piece_squares(position.side.opponent(), PieceKind::King)[0];
                if !projected.attacked(king, position.side) {
                    continue;
                }
                if DIAGNOSTICS {
                    self.stats.mate_probes += 1;
                }
                let mut child = node.child(&self.evaluator.root, movement);
                history.push(&child.position, Some(movement));
                let returned = self.visit_q(
                    &mut child,
                    history,
                    TacticalEntry {
                        ply: p + 1,
                        target: p as i32 + 1,
                        iteration_depth: request.iteration,
                        lower: -9000,
                        upper: -8999,
                        analysis: self.config.analysis,
                        capture_exception: quiescence_policy::capture_exception(
                            &position, &movement,
                        ),
                    },
                    Some(true),
                    false,
                );
                history.pop();
                let score = -returned?;
                if score >= 9000 {
                    preferred = Some(movement);
                    if score >= request.upper {
                        self.learning.record(&position, p, request.depth, preferred);
                        self.store_ordinary(query, score, preferred, true, true);
                    }
                    break;
                }
            }
            quiet_checked = true;
        }

        if request.depth >= 4
            && remembered
                .marked_depth
                .is_none_or(|d| d < request.depth - 2)
        {
            self.ordering_phase::<ALLOW_IIO>(node, history, request, previous, map, checked, 0)?;
        }
        #[cfg(feature = "child-preparation")]
        let _preparation_scope = if request.depth == 2 && coherent_geometry {
            self.evaluator.prepare_children(&position, self.candidates[p].as_slice())
        } else {None};
        let mut best = effective_lower;
        let mut lower = request.lower;
        // Main extensions depend on the complete inventory, whose contents do
        // not change when an ordering phase permutes its unconsumed suffix.
        let main_extensions = Extensions::new(
            &position,
            self.candidates[p].as_slice(),
            previous.position,
            previous.movement,
            request.previous_extension,
            checked,
        );
        let mut index = 0;
        while index < count {
            let movement = self.candidates[p].moves[index];
            if DIAGNOSTICS {
                self.stats.examined += 1;
            }
            let fresh = main_extensions.for_move(&position, movement);
            let accumulated = self.extension_flags[p][index] | fresh;
            if DIAGNOSTICS && accumulated != fresh {
                self.stats.accumulated_extension_uses += 1;
            }
            self.extension_flags[p][index] = accumulated;
            let depth = request.depth - 1 + fresh as i32;
            let mut child_checked = None;
            let estimate = if depth <= 0 {
                let checking = if movement.kind() == MoveKind::Ordinary {
                    let projected = position.attack_view().projected(&position, movement);
                    let king = position.piece_squares(position.side.opponent(), PieceKind::King)[0];
                    let checking = projected.attacked(king, position.side);
                    child_checked = Some(checking);
                    checking
                } else {
                    false
                };
                Some(policy::frontier_estimate(
                    &position,
                    &self.evaluator.root,
                    movement,
                    checking,
                    evaluation.score,
                    node.retained.positional,
                    node.retained.pawn_progress,
                ))
            } else {
                None
            };
            let score = if estimate.is_some_and(|e| e <= best.max(lower)) {
                if DIAGNOSTICS {
                    self.stats.frontier_skips += 1;
                }
                estimate.unwrap()
            } else {
                let mut child = node.child(&self.evaluator.root, movement);
                let inherited = child.retained;
                let predecessor = Predecessor {
                    movement: Some(movement),
                    ..current
                };
                history.push(&child.position, Some(movement));
                let full_window = index == 0
                    || best <= request.lower
                    || (request.lower > -10000 && request.upper < 10000);
                let child_request = Request {
                    ply: p + 1,
                    depth,
                    previous_extension: accumulated,
                    lower: if full_window {
                        -request.upper
                    } else {
                        -(best + 1).min(request.upper)
                    },
                    upper: if full_window {
                        -best.max(request.lower)
                    } else {
                        -best
                    },
                    checked: child_checked,
                    ..request
                };
                if DIAGNOSTICS {
                    self.stats.children += 1;
                }
                let returned = self.visit_ordinary_impl::<ALLOW_IIO>(&mut child, history, child_request, predecessor);
                let returned = match returned {
                    Ok(value) => Ok(-value),
                    Err(stop) => Err(stop),
                };
                let returned = if let Ok(score) = returned {
                    if !full_window && score >= best + 1 && score < request.upper {
                        if DIAGNOSTICS {
                            self.stats.scout_retries += 1;
                            if child.retained != inherited {
                                self.stats.refreshed_scout_retries += 1;
                            }
                        }
                        self.visit_ordinary_impl::<ALLOW_IIO>(
                            &mut child,
                            history,
                            Request {
                                lower: -request.upper,
                                upper: -best,
                                ..child_request
                            },
                            predecessor,
                        )
                        .map(|s| -s)
                    } else {
                        Ok(score)
                    }
                } else {
                    returned
                };
                history.pop();
                returned?
            };
            if score > best {
                best = score;
                if score > lower {
                    preferred = Some(movement);
                    if score < request.upper {
                        self.replace_pv(p, movement);
                    }
                    lower = score;
                    if lower >= request.upper {
                        if DIAGNOSTICS {
                            self.stats.cutoffs += 1;
                        }
                        break;
                    }
                }
            }
            // The released first-main rule ends processing even without a strict lower raise.
            if index == 0 && score >= request.upper {
                if DIAGNOSTICS {
                    self.stats.cutoffs += 1;
                }
                break;
            }
            index += 1;
            if index == 1 && index < count && request.depth >= 5 && remembered.bound == Bound::Lower
            {
                self.ordering_phase::<ALLOW_IIO>(node, history, request, previous, map, checked, 1)?;
            }
        }
        best = best.min(effective_upper);
        if best > request.lower {
            self.learning.record(&position, p, request.depth, preferred);
        }
        self.store_ordinary(query, best, preferred, quiet_checked, true);
        Ok(best)
    }

    fn ordering_phase<const ALLOW_IIO: bool>(
        &mut self,
        node: &Node,
        history: &mut SearchHistory,
        request: Request,
        previous: Predecessor<'_>,
        map: &Influence,
        checked: bool,
        start: usize,
    ) -> Result<(), Stopped> {
        if DIAGNOSTICS || !ALLOW_IIO {
            if start == 0 {
                self.stats.iio_initial_phases += 1;
            } else {
                self.stats.iio_tail_phases += 1;
            }
        }
        if !ALLOW_IIO {
            return Err(Stopped::InternalIterativeOrdering);
        }
        let p = request.ply;
        let target = p as i32 + request.depth;
        let position = &node.position;
        let count = self.candidates[p].len;
        for offset in (2..=20).rev().step_by(2) {
            let shallow_target = target - offset;
            if shallow_target < p as i32 + 2 {
                continue;
            }
            if DIAGNOSTICS {
                self.stats.iio_passes += 1;
            }
            let extensions = Extensions::new(
                position,
                &self.candidates[p].moves[start..count],
                previous.position,
                previous.movement,
                request.previous_extension,
                checked,
            );
            let mut best = -10000;
            for index in start..count {
                let movement = self.candidates[p].moves[index];
                let fresh = extensions.for_move(position, movement);
                if DIAGNOSTICS && fresh != 0 {
                    self.stats.iio_nonzero_fresh_extensions += 1;
                }
                let accumulated = self.extension_flags[p][index] | fresh;
                if DIAGNOSTICS && accumulated != fresh {
                    self.stats.accumulated_extension_uses += 1;
                }
                self.extension_flags[p][index] = accumulated;
                let mut child = node.child(&self.evaluator.root, movement);
                history.push(&child.position, Some(movement));
                if DIAGNOSTICS {
                    self.stats.iio_children += 1;
                }
                let returned = self.visit_ordinary_impl::<ALLOW_IIO>(
                    &mut child,
                    history,
                    Request {
                        ply: p + 1,
                        depth: shallow_target + fresh as i32 - p as i32 - 1,
                        lower: -request.upper,
                        upper: -best.max(request.lower),
                        previous_extension: accumulated,
                        checked: None,
                        ..request
                    },
                    Predecessor {
                        position,
                        influence: map,
                        checked,
                        movement: Some(movement),
                    },
                );
                history.pop();
                let score = -returned?;
                if score > best {
                    let promote = score > request.lower;
                    best = score;
                    if promote {
                        self.candidates[p]
                            .moves
                            .copy_within(start..index, start + 1);
                        self.candidates[p].moves[start] = movement;
                        self.extension_flags[p].copy_within(start..index, start + 1);
                        self.extension_flags[p][start] = accumulated;
                        if score >= request.upper {
                            break;
                        }
                    }
                }
            }
        }
        Ok(())
    }
}

#[cfg(test)]
#[path = "ordinary/first_main_tests.rs"]
mod first_main_tests;
