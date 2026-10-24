//! Composed root-bound evaluation with retained full/fast state.
//! Component correctness and complete engine qualification remain separate.

use crate::evaluation::RootContext;
use crate::evaluator_worker::{self, ActivityShelterWorker};
use crate::influence::Influence;
use crate::pawn_structure::{self, PawnCache};
use crate::position::Position;
use crate::types::{Color, Move, MoveKind, Piece, PieceKind, Square};
use crate::{endgame, pawn_progress, pawn_terms, positional_terms};

#[cfg(test)]
std::thread_local! {
    static COHERENT_BUILDS: std::cell::Cell<u64> = const { std::cell::Cell::new(0) };
}

#[cfg(test)]
pub(crate) fn coherent_build_count() -> u64 {
    COHERENT_BUILDS.with(|count| count.get())
}

pub const OMITTED_TERMS: &str = "production personality/session/protocol binding";

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Retained {
    pub positional: i32,
    pub pawn_progress: i32,
    pub nonking_squares: i32,
    pub age: u8,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Node {
    pub position: Position,
    pub retained: Retained,
}

impl Node {
    pub fn root(position: Position, root: &RootContext) -> Self {
        Self {
            position,
            retained: Retained {
                nonking_squares: root.nonking_square_balance(&position),
                ..Retained::default()
            },
        }
    }

    pub fn child(&self, root: &RootContext, movement: Move) -> Self {
        let moving = self.position.board[movement.from().0 as usize];
        let victim_square = if movement.kind() == MoveKind::EnPassant {
            Square(if moving.color() == Color::White {
                movement.to().0 - 8
            } else {
                movement.to().0 + 8
            })
        } else {
            movement.to()
        };
        let victim = self.position.board[victim_square.0 as usize];
        let promoted = match movement.kind() {
            MoveKind::Promotion(kind) => Piece::new(moving.color(), kind),
            _ => moving,
        };
        let mut nonking = self.retained.nonking_squares
            - square_value(root, moving, movement.from())
            - square_value(root, victim, victim_square)
            + square_value(root, promoted, movement.to());
        if movement.kind() == MoveKind::Castle {
            let home = if moving.color() == Color::White {
                0
            } else {
                56
            };
            let (from, to) = if movement.to().0 > movement.from().0 {
                (home + 7, home + 5)
            } else {
                (home, home + 3)
            };
            let rook = Piece::new(moving.color(), PieceKind::Rook);
            nonking +=
                square_value(root, rook, Square(to)) - square_value(root, rook, Square(from));
        }
        Self {
            position: self.position.played_unchecked(movement),
            retained: Retained {
                nonking_squares: nonking,
                age: self.retained.age.wrapping_add(1),
                ..self.retained
            },
        }
    }

    pub fn null_child(&self) -> Self {
        Self {
            position: self.position.null_child(),
            retained: Retained {
                age: self.retained.age.wrapping_add(1),
                ..self.retained
            },
        }
    }
}

#[inline]
fn square_value(root: &RootContext, piece: Piece, square: Square) -> i32 {
    if piece.is_empty() || piece.kind() == PieceKind::King {
        return 0;
    }
    let value = root.squares[piece.color().index()][piece.kind().index()][square.0 as usize] as i32;
    if piece.color() == Color::White {
        value
    } else {
        -value
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Evaluation {
    pub score: i32,
    pub lower: i32,
    pub upper: i32,
    pub relation_queries: u64,
    /// True when the specialized late-endgame stage was selected.
    pub late_endgame_applied: bool,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct EvalStats {
    pub full: u64,
    pub fast: u64,
    pub influence_builds: u64,
    pub pawn_reuses: u64,
    pub pawn_replacements: u64,
    pub relation_queries: u64,
}

/// An actual evaluator call, with retained state sampled around that call.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StageKind { Full, Fast }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct EvaluationStage {
    pub kind: StageKind,
    pub before: Retained,
    pub after: Retained,
    pub evaluation: Evaluation,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Selection {
    pub evaluation: Evaluation,
    pub initially_full: bool,
    pub fast_score: Option<i32>,
    pub refreshed: bool,
}

#[derive(Clone, Debug)]
pub struct Parameters {
    /// Pawn, knight, bishop, rook, queen, king, center, mobility, shelter,
    /// pawn progress, pawn structure; ownership follows the root side.
    pub own: [i32; 11],
    pub opponent: [i32; 11],
    pub average_depth: i32,
    pub draw: i32,
    pub opponent_selectivity: i32,
}
impl Default for Parameters {
    fn default() -> Self {
        Self {
            own: [100; 11],
            opponent: [100; 11],
            average_depth: 0,
            draw: 0,
            opponent_selectivity: 100,
        }
    }
}
pub fn coefficient(percentage: i32) -> i32 {
    percentage.wrapping_mul(1024).wrapping_add(50) / 100
}

#[derive(Clone, Copy)]
struct Weights {
    structure: [i32; 2],
    progress: [i32; 2],
    central: [i32; 2],
    mobility: [i32; 2],
    shelter: [i32; 2],
}
impl Parameters {
    fn bind(&self, position: &Position) -> (RootContext, Weights, i32, u32) {
        assert!(self.own.iter().all(|v| (0..=1000).contains(v)));
        assert!(self
            .opponent
            .iter()
            .enumerate()
            .filter(|&(i, _)| i != 5)
            .all(|(_, v)| (0..=1000).contains(v)));
        assert!((-10000..=10000).contains(&self.draw));
        assert!((0..=100).contains(&self.opponent_selectivity));
        let percentages = if position.side == Color::White {
            [self.own, self.opponent]
        } else {
            [self.opponent, self.own]
        };
        let material = std::array::from_fn(|c| std::array::from_fn(|k| percentages[c][k] as u16));
        let root = RootContext::new(position, material, self.average_depth);
        let pair = |index| {
            [
                coefficient(percentages[0][index]),
                coefficient(percentages[1][index]),
            ]
        };
        let weights = Weights {
            central: pair(6),
            mobility: pair(7),
            shelter: pair(8),
            progress: pair(9),
            structure: pair(10),
        };
        let draw = crate::evaluation::draw_preference(root.phase, self.draw);
        let range = crate::evaluation::variation_range(self.opponent_selectivity);
        (root, weights, draw, range)
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Components {
    pub material: i32,
    pub squares: i32,
    pub pawn_structure: i32,
    pub pawn_progress: i32,
    pub activity: i32,
    pub central: i32,
    pub shelter: i32,
    pub bishops: i32,
    pub patterns: i32,
    pub tempo: i32,
}
impl Components {
    pub fn positional(self) -> i32 {
        self.pawn_structure
            + self.activity
            + self.central
            + self.shelter
            + self.bishops
            + self.patterns
    }
    pub fn base(self) -> i32 {
        self.positional() + self.material + self.squares + self.pawn_progress + self.tempo
    }
}

/// Cold full-evaluation details observed from the actual component/finish path.
/// This record is not stored in nodes or returned by ordinary evaluation.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct FullDetails {
    pub components: Components,
    pub base: i32,
    pub finished: endgame::Finished,
    pub pawn_entry_reused: bool,
}

/// Cold fast-path details from its actual base and single native finishing call.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct FastDetails {
    pub base: i32,
    pub finished: endgame::Finished,
}

pub struct Evaluator<const DIAGNOSTICS: bool = true> {
    pub root: RootContext,
    pub parameters: Parameters,
    pub draw_preference: i32,
    pub variation_range: u32,
    weights: Weights,
    pawns: PawnCache,
    requested_threads: usize,
    full_worker: Option<ActivityShelterWorker>,
    #[cfg(feature = "child-preparation")]
    child_preparation: Option<crate::child_preparation::ChildPreparation>,
    pub stats: EvalStats,
}

impl<const DIAGNOSTICS: bool> Evaluator<DIAGNOSTICS> {
    /// Detached copies are deliberately expensive in the bounded transaction
    /// pilot. They never start or share the separate evaluator worker.
    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_clone(&self) -> Self {
        assert!(
            self.full_worker.is_none(),
            "branch pilot requires inline evaluation"
        );
        Self {
            root: self.root.clone(),
            parameters: self.parameters.clone(),
            draw_preference: self.draw_preference,
            variation_range: self.variation_range,
            weights: self.weights,
            pawns: self.pawns.research_clone(),
            requested_threads: self.requested_threads,
            full_worker: None,
            #[cfg(feature = "child-preparation")]
            child_preparation: None,
            stats: self.stats,
        }
    }

    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_pawns(&mut self) -> &mut PawnCache {
        &mut self.pawns
    }

    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_eq(&self, other: &Self) -> bool {
        self.stats == other.stats && self.pawns.research_eq(&other.pawns)
    }

    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_attach_sink(&mut self, sink: Option<crate::branch_journal::Sink>) {
        self.pawns.attach_sink(sink);
    }

    pub fn new(position: &Position) -> Self {
        let parameters = Parameters::default();
        let (root, weights, draw_preference, variation_range) = parameters.bind(position);
        Self {
            root,
            parameters,
            weights,
            draw_preference,
            variation_range,
            pawns: PawnCache::new(),
            requested_threads: 1,
            full_worker: None,
            #[cfg(feature = "child-preparation")]
            child_preparation: None,
            stats: EvalStats::default(),
        }
    }

    /// Request a positive total thread budget. Requests above one query the
    /// configuring thread's permitted affinity before changing configuration.
    /// Exactly one permitted CPU caps execution at one; otherwise the capacity
    /// is min(requested, 2). Later external placement does not change this cap.
    /// The helper inherits allowed affinity and parks outside owned scopes.
    pub fn set_threads(&mut self, requested: usize) -> Result<(), String> {
        self.set_threads_with_affinity(requested, crate::thread_budget::permitted_cpus)
    }

    fn set_threads_with_affinity(
        &mut self,
        requested: usize,
        permitted_cpus: impl FnOnce() -> Result<usize, String>,
    ) -> Result<(), String> {
        if requested == 0 {
            return Err("thread request must be positive".into());
        }
        let configured = if requested == 1 {
            1
        } else {
            match permitted_cpus()? {
                0 => return Err("permitted CPU affinity is empty".into()),
                1 => 1,
                _ => requested.min(2),
            }
        };
        #[cfg(feature = "child-preparation")]
        if configured != 1 && self.child_preparation.is_some() {
            return Err("child preparation and FULL worker cannot be nested".into());
        }
        match configured {
            1 => {
                if let Some(worker) = self.full_worker.as_mut() {
                    worker.shutdown()?;
                }
                self.full_worker = None;
            }
            2 => {
                if let Some(worker) = self.full_worker.as_ref() {
                    worker.check_running()?;
                } else {
                    self.full_worker = Some(ActivityShelterWorker::start()?);
                }
            }
            _ => unreachable!(),
        }
        self.requested_threads = requested;
        Ok(())
    }

    pub fn requested_threads(&self) -> usize { self.requested_threads }

    /// Configured capacity, rather than a claim that both threads run at once.
    pub fn configured_threads(&self) -> usize {
        if self.full_worker.is_some() { 2 } else { 1 }
    }

    // The archived transaction prototype still calls its original strict API.
    // Keep that spelling out of the normal public interface and CLI.
    #[cfg(feature = "branch-transactions")]
    pub(crate) fn set_research_thread_budget(&mut self, budget: usize) -> Result<(), String> {
        if ![1, 2].contains(&budget) {
            return Err("transaction evaluator budget must be 1 or 2".into());
        }
        self.set_threads(budget)
    }

    #[cfg(feature = "child-preparation")]
    pub fn set_child_preparation_budget(&mut self, budget: usize) -> Result<(), String> {
        if ![1,2,4].contains(&budget) {return Err("child preparation budget must be1,2,4".into());}
        if self.full_worker.is_some() {return Err("child preparation requires inline FULL mode".into());}
        if let Some(mut old)=self.child_preparation.take() {old.shutdown()?;}
        if budget>1 {self.child_preparation=Some(crate::child_preparation::ChildPreparation::start(budget-1)?);}
        Ok(())
    }

    #[cfg(feature = "child-preparation")]
    pub fn finish_child_preparation(&mut self) -> Result<String,String> {
        if let Some(mut pool)=self.child_preparation.take() {
            let reserved=pool.estimated_bytes();
            pool.shutdown()?;
            let mut json=pool.stats().json();json.pop();
            Ok(format!("{json},\"pool_reserved_bytes\":{reserved}}}"))
        } else {Ok(crate::child_preparation::Stats::default().json())}
    }

    #[cfg(feature = "child-preparation")]
    pub(crate) fn prepare_children(&mut self, position: &Position, moves: &[Move])
        -> Option<crate::child_preparation::ScopeGuard> {
        let pool=self.child_preparation.as_mut()?;
        // Native legal inventory plus guarded descendant ancestry supplies coherent geometry.
        // Restrict this initial domain to ordinary moves; no exceptional projections.
        let jobs=moves.iter().filter(|m|m.kind()==MoveKind::Ordinary && {
            let victim=position.board[m.to().0 as usize];
            victim.is_empty() || victim.kind()!=PieceKind::King
        }).take(6).map(|m| {
            let child=position.played_unchecked(*m);
            crate::child_preparation::Job {position:child,material:self.root.material(&child),
                mobility_weights:self.weights.mobility,shelter_weights:self.weights.shelter,coherent:true}
        }).collect();
        pool.begin(jobs)
    }

    /// Owns one lexical search activation; the guard parks the helper on every exit.
    pub(crate) fn full_worker_scope(&self) -> Option<crate::evaluator_worker::ActiveScope> {
        self.full_worker.as_ref().map(|worker| worker.start_active_scope()
            .unwrap_or_else(|error|panic!("FULL worker activation failed: {error}")))
    }

    /// Normal returns check closure; Drop is only abandoned-path cleanup.
    pub(crate) fn finish_full_worker_scope(scope: Option<crate::evaluator_worker::ActiveScope>) {
        if let Some(scope) = scope {
            scope.finish().unwrap_or_else(|error|panic!("FULL worker scope closure failed: {error}"));
        }
    }

    pub fn begin_search(&mut self, position: &Position) {
        #[cfg(feature = "child-preparation")]
        if let Some(pool)=self.child_preparation.as_mut() {pool.reset();}
        (
            self.root,
            self.weights,
            self.draw_preference,
            self.variation_range,
        ) = self.parameters.bind(position);
        self.pawns.clear();
        self.stats = EvalStats::default();
    }

    pub fn ensure_influence<'a>(
        &mut self,
        position: &Position,
        scratch: &'a mut Option<Influence>,
    ) -> &'a Influence {
        self.ensure_influence_for_search(position, scratch, false)
    }

    /// Only a guarded Search-owned descendant chain may pass true. Supplied
    /// maps remain authoritative, including on the trusted route.
    pub(crate) fn ensure_influence_for_search<'a>(
        &mut self,
        position: &Position,
        scratch: &'a mut Option<Influence>,
        coherent_geometry: bool,
    ) -> &'a Influence {
        if scratch.is_none() {
            #[cfg(feature = "child-preparation")]
            let prepared = if coherent_geometry {
                self.child_preparation.as_mut().and_then(|pool|pool.take_map(position))
            } else {None};
            #[cfg(not(feature = "child-preparation"))]
            let prepared: Option<Influence> = None;
            *scratch = Some(if let Some(map)=prepared {map} else if coherent_geometry {
                let map = Influence::build_coherent(position);
                #[cfg(test)]
                COHERENT_BUILDS.with(|count| count.set(count.get() + 1));
                map
            } else {
                Influence::build(position)
            });
            if DIAGNOSTICS {
                self.stats.influence_builds += 1;
            }
        }
        scratch.as_ref().unwrap()
    }

    pub fn full(&mut self, node: &mut Node, influence: &Influence, in_check: bool) -> Evaluation {
        self.full_impl::<false, _, _>(node, influence, in_check, |_| {}, |_| {})
    }
    /// Cold component observation; the default monomorph has a zero-sized no-op observer.
    pub fn full_observed<F: FnOnce(Components)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.full_impl::<false, _, _>(node, influence, in_check, observer, |_| {})
    }
    pub fn fresh_observed<F: FnOnce(Components)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.full_impl::<true, _, _>(node, influence, in_check, observer, |_| {})
    }
    /// Forced-fresh observation includes the single native finishing result.
    /// Ordinary calls retain statically dispatched, zero-sized no-op observers.
    pub fn fresh_detailed_observed<F: FnOnce(FullDetails)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.full_impl::<true, _, _>(node, influence, in_check, |_| {}, observer)
    }
    /// Ordinary full selection, including the actual cache identity-match flag.
    pub fn full_detailed_observed<F: FnOnce(FullDetails)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.full_impl::<false, _, _>(node, influence, in_check, |_| {}, observer)
    }
    fn full_impl<const FRESH: bool, F: FnOnce(Components), D: FnOnce(FullDetails)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
        details: D,
    ) -> Evaluation {
        let position = &node.position;
        let phase = position.phase();
        let material = self.root.material(position);
        // Standalone public evaluator calls get a one-call lifetime. Search
        // owners already hold an outer scope, so their handoff stays active.
        let call_scope = self.full_worker.as_ref().and_then(|worker|worker.start_call_scope()
            .unwrap_or_else(|error|panic!("FULL worker call activation failed: {error}")));
        // Snapshot every worker input on every FULL, including authoritative
        // supplied maps and the current root-bound weights after begin_search.
        if let Some(worker) = self.full_worker.as_mut() {
            worker
                .dispatch(
                    position,
                    influence,
                    material,
                    self.weights.mobility,
                    self.weights.shelter,
                )
                .unwrap_or_else(|error| panic!("FULL evaluator dispatch failed: {error}"));
        }
        let selected = if FRESH {
            pawn_structure::Selection {
                structure: pawn_structure::fresh(position, influence, [1024; 2]),
                reused: false,
            }
        } else {
            self.pawns.select(position, influence)
        };
        let pawn = pawn_terms::compute(position, influence, &selected.structure);
        // Keep inline execution at the original chain position. Both routes
        // invoke the same numerical kernels and share the composition below.
        #[cfg(feature = "child-preparation")]
        let prepared_chain=self.child_preparation.as_mut().and_then(|pool|pool.take_chain(
            position,influence,material,self.weights.mobility,self.weights.shelter));
        #[cfg(not(feature = "child-preparation"))]
        let prepared_chain: Option<evaluator_worker::ActivityShelter> = None;
        let inline_chain = if self.full_worker.is_none() {
            Some(prepared_chain.unwrap_or_else(||evaluator_worker::compute(
                position,
                influence,
                material,
                self.weights.mobility,
                self.weights.shelter,
            )))
        } else {
            None
        };
        let structure = pawn_progress::structure_weighted(
            phase,
            pawn.structure,
            pawn.piece,
            self.weights.structure,
        );
        // This producer has no state or charged relation work. At a zero final
        // phase factor, its weighted result is identically zero.
        let progress = if phase.middlegame == 0 && phase.endgame == 0 {
            0
        } else {
            pawn_progress::selected(
                position,
                influence,
                &selected.structure,
                phase,
                material,
                self.weights.progress,
            )
            .weighted
        };
        let central = positional_terms::central(influence, phase, self.weights.central);
        let patterns = positional_terms::patterns(position);
        let squares = self.root.square_balance_from(position, node.retained.nonking_squares);
        // No retained changes, tempo, relation-ledger publication or finishing
        // occurs until the actual worker output has joined the owner branch.
        let chain = if let Some(worker) = self.full_worker.as_mut() {
            worker
                .complete()
                .unwrap_or_else(|error| panic!("FULL evaluator completion failed: {error}"))
        } else {
            inline_chain.unwrap()
        };
        Self::finish_full_worker_scope(call_scope);
        let activity = chain.activity;
        let shelter = chain.shelter;
        let tempo = if in_check {
            0
        } else {
            let magnitude = ((activity.pieces[position.side.index()] as i64 + 140)
                * (5 * phase.opening as i64
                    + 4 * phase.middlegame as i64
                    + 2 * phase.endgame as i64)
                + 16384)
                .div_euclid(32768) as i32;
            if position.side == Color::White {
                magnitude
            } else {
                -magnitude
            }
        };
        let components = Components {
            material,
            squares,
            pawn_structure: structure,
            pawn_progress: progress,
            activity: activity.weighted,
            central: central.weighted,
            shelter: shelter.weighted,
            bishops: patterns.bishop_coordination,
            patterns: patterns.opening,
            tempo,
        };
        node.retained.positional = components.positional();
        node.retained.pawn_progress = progress;
        node.retained.age = 0;
        let queries = pawn.relation_queries + activity.relation_queries;
        if DIAGNOSTICS {
            self.stats.full += 1;
            if selected.reused {
                self.stats.pawn_reuses += 1;
            } else {
                self.stats.pawn_replacements += 1;
            }
        }
        self.stats.relation_queries += queries;
        observer(components);
        let base = components.base();
        self.finish_observed(position, base, in_check, progress, queries, |finished| {
            details(FullDetails {
                components,
                base,
                finished,
                pawn_entry_reused: selected.reused,
            });
        })
    }
    fn finish_observed<F: FnOnce(endgame::Finished)>(
        &self,
        position: &Position,
        base: i32,
        checked: bool,
        progress: i32,
        queries: u64,
        observer: F,
    ) -> Evaluation {
        let value = endgame::finish(
            position,
            base,
            self.draw_preference,
            self.root.side,
            self.variation_range,
            position.primary ^ position.secondary,
            position.phase().endgame,
            checked,
            progress,
        );
        observer(value);
        Evaluation {
            score: value.score,
            lower: value.lower,
            upper: value.upper,
            relation_queries: queries,
            late_endgame_applied: position.phase().endgame >= 192,
        }
    }
    pub fn fast(&mut self, node: &Node, in_check: bool) -> Evaluation {
        self.fast_impl(node, in_check, |_| {})
    }
    /// Observe fast evaluation without influence construction or pawn selection.
    pub fn fast_detailed_observed<F: FnOnce(FastDetails)>(
        &mut self,
        node: &Node,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.fast_impl(node, in_check, observer)
    }
    fn fast_impl<F: FnOnce(FastDetails)>(
        &mut self,
        node: &Node,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        if DIAGNOSTICS {
            self.stats.fast += 1;
        }
        let position = &node.position;
        let tempo = if in_check {
            0
        } else if position.side == Color::White {
            6
        } else {
            -6
        };
        let base = self.root.material(position)
            + self
                .root
                .square_balance_from(position, node.retained.nonking_squares)
            + node.retained.positional
            + node.retained.pawn_progress
            + tempo;
        self.finish_observed(position, base, in_check, node.retained.pawn_progress, 0, |finished| {
            observer(FastDetails { base, finished });
        })
    }

    /// Select and refresh from the finished current-side score.
    pub fn select_noncheck(
        &mut self,
        node: &mut Node,
        lower: i32,
        upper: i32,
        capture_exception: bool,
        scratch: &mut Option<Influence>,
    ) -> Selection {
        self.select_noncheck_for_search(
            node, lower, upper, capture_exception, scratch, false,
        )
    }

    pub(crate) fn select_noncheck_for_search(
        &mut self,
        node: &mut Node,
        lower: i32,
        upper: i32,
        capture_exception: bool,
        scratch: &mut Option<Influence>,
        coherent_geometry: bool,
    ) -> Selection {
        self.select_noncheck_impl::<false, false, _, _, _>(
            node, lower, upper, capture_exception, scratch, coherent_geometry,
            |_| {}, |_| {}, |_| {},
        )
    }

    /// Observe actual selected stages without changing sparse admission, strict
    /// refresh ordering, lazy influence, or the ordinary result/state layouts.
    /// A refresh emits fast details first and full details second.
    pub fn select_noncheck_detailed_observed<F, G>(
        &mut self,
        node: &mut Node,
        lower: i32,
        upper: i32,
        capture_exception: bool,
        scratch: &mut Option<Influence>,
        full_observer: F,
        fast_observer: G,
    ) -> Selection
    where
        F: FnMut(FullDetails),
        G: FnMut(FastDetails),
    {
        self.select_noncheck_impl::<true, false, _, _, _>(
            node, lower, upper, capture_exception, scratch, false, full_observer, fast_observer, |_| {},
        )
    }

    /// Observe actual selected calls, including the fast stage before a refresh.
    pub fn select_noncheck_stages_observed<F: FnMut(EvaluationStage)>(
        &mut self,
        node: &mut Node,
        lower: i32,
        upper: i32,
        capture_exception: bool,
        scratch: &mut Option<Influence>,
        observer: F,
    ) -> Selection {
        self.select_noncheck_impl::<false, true, _, _, _>(
            node, lower, upper, capture_exception, scratch, false, |_| {}, |_| {}, observer,
        )
    }

    /// Terminal Q leaves also observe one actual fast call without a refresh.
    pub fn fast_stage_observed<F: FnOnce(EvaluationStage)>(
        &mut self, node: &Node, checked: bool, observer: F,
    ) -> Evaluation {
        let before = node.retained;
        let evaluation = self.fast(node, checked);
        observer(EvaluationStage { kind: StageKind::Fast, before,
            after: node.retained, evaluation });
        evaluation
    }

    fn full_stage_observed<F: FnOnce(EvaluationStage)>(
        &mut self, node: &mut Node, influence: &Influence, observer: F,
    ) -> Evaluation {
        let before = node.retained;
        let evaluation = self.full(node, influence, false);
        observer(EvaluationStage { kind: StageKind::Full, before,
            after: node.retained, evaluation });
        evaluation
    }

    // Only stage call wrappers differ. The ordinary instantiation retains its
    // original full/fast call sites; every selection condition stays shared.
    fn select_noncheck_impl<const OBSERVE: bool, const STAGES: bool, F, G, S>(
        &mut self,
        node: &mut Node,
        lower: i32,
        upper: i32,
        capture_exception: bool,
        scratch: &mut Option<Influence>,
        coherent_geometry: bool,
        mut full_observer: F,
        mut fast_observer: G,
        mut stage_observer: S,
    ) -> Selection
    where
        F: FnMut(FullDetails),
        G: FnMut(FastDetails),
        S: FnMut(EvaluationStage),
    {
        let sparse = node.position.counts.iter().all(|c| {
            (c[1] as u16
                + c[2] as u16
                + c[3] as u16
                + c[4] as u16
                + (c[1] as u16 + c[3] as u16) / 16)
                % 16
                <= 1
        });
        if sparse {
            let influence = self.ensure_influence_for_search(&node.position, scratch, coherent_geometry);
            return Selection {
                evaluation: if STAGES {
                    self.full_stage_observed(node, influence, |stage| stage_observer(stage))
                } else if OBSERVE {
                    self.full_detailed_observed(node, influence, false, |details| full_observer(details))
                } else {
                    self.full(node, influence, false)
                },
                initially_full: true,
                fast_score: None,
                refreshed: false,
            };
        }
        let fast = if STAGES {
            self.fast_stage_observed(node, false, |stage| stage_observer(stage))
        } else if OBSERVE {
            self.fast_detailed_observed(node, false, |details| fast_observer(details))
        } else {
            self.fast(node, false)
        };
        let refresh = capture_exception || (lower - 250 < fast.score && fast.score < upper + 250);
        let evaluation = if refresh {
            let influence = self.ensure_influence_for_search(&node.position, scratch, coherent_geometry);
            if STAGES {
                self.full_stage_observed(node, influence, |stage| stage_observer(stage))
            } else if OBSERVE {
                self.full_detailed_observed(node, influence, false, |details| full_observer(details))
            } else {
                self.full(node, influence, false)
            }
        } else {
            fast
        };
        Selection {
            evaluation,
            initially_full: false,
            fast_score: Some(fast.score),
            refreshed: refresh,
        }
    }
}

#[cfg(test)]
#[path = "evaluator/parallel_tests.rs"]
mod parallel_tests;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::movegen::{generate_legal, in_check, MoveList};
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn initialized() -> (Evaluator, Node) {
        let position = Position::from_fen(START).unwrap();
        let mut evaluator = Evaluator::new(&position);
        let mut root = Node::root(position, &evaluator.root);
        let influence = Influence::build(&position);
        evaluator.full(&mut root, &influence, false);
        (evaluator, root)
    }

    #[test]
    fn incremental_squares_match_recomputation_through_special_children() {
        for fen in [
            START,
            "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
            "7k/P7/8/8/8/8/7p/K7 w - - 0 1",
            "7k/8/8/3pP3/8/8/8/K7 w - d6 0 1",
            "7k/8/8/3rP3/8/8/8/K7 w - d6 0 1",
        ] {
            let position = Position::from_fen(fen).unwrap();
            let context = RootContext::neutral(&position);
            let node = Node::root(position, &context);
            let mut moves = MoveList::new();
            generate_legal(&position, &mut moves);
            for &movement in moves.as_slice() {
                let child = node.child(&context, movement);
                assert_eq!(
                    child.retained.nonking_squares,
                    context.nonking_square_balance(&child.position)
                );
                assert_eq!(
                    context.square_balance_from(&child.position, child.retained.nonking_squares),
                    context.square_balance(&child.position)
                );
                child.position.validate().unwrap();
            }
        }
        assert_eq!(std::mem::size_of::<Node>(), 176);
    }

    #[test]
    fn retry_preserves_child_refresh_and_sibling_inherits_unchanged_parent() {
        let (mut evaluator, parent) = initialized();
        let saved = parent;
        let mut legal = MoveList::new();
        generate_legal(&parent.position, &mut legal);
        let mut child = parent.child(&evaluator.root, legal.moves[0]);
        assert_eq!(child.retained.age, 1);
        let influence = Influence::build(&child.position);
        let checked = in_check(&child.position, child.position.side);
        evaluator.full(&mut child, &influence, checked);
        let refreshed = child.retained;
        let reuses_before = evaluator.stats.pawn_reuses;
        evaluator.fast(&child, false);
        assert_eq!(child.retained, refreshed);
        assert_eq!(evaluator.stats.pawn_reuses, reuses_before);
        let sibling = parent.child(&evaluator.root, legal.moves[1]);
        assert_eq!(sibling.retained.positional, parent.retained.positional);
        assert_eq!(sibling.retained.age, 1);
        assert_eq!(parent, saved);
    }

    #[test]
    fn detailed_noncheck_observes_real_stages_and_preserves_default_state_and_charges() {
        use std::cell::{Cell, RefCell};
        for (offset_alpha, offset_beta, exception, refreshed) in [
            (250, 251, false, false),
            (-251, -250, false, false),
            (-1, 1, false, true),
            (250, 251, true, true),
        ] {
            let (mut ordinary, parent) = initialized();
            let (mut observed, same_parent) = initialized();
            let mut a = parent.null_child();
            let mut b = same_parent.null_child();
            let score = ordinary.fast(&a, false).score;
            assert_eq!(observed.fast(&b, false).score, score);
            let before = b.retained;
            let (mut scratch_a, mut scratch_b) = (None, None);
            let expected = ordinary.select_noncheck(&mut a, score + offset_alpha,
                score + offset_beta, exception, &mut scratch_a);
            let stages = RefCell::new(Vec::new());
            let full = Cell::new(None);
            let fast = Cell::new(None);
            let selected = observed.select_noncheck_detailed_observed(&mut b,
                score + offset_alpha, score + offset_beta, exception, &mut scratch_b,
                |details| { stages.borrow_mut().push("full"); full.set(Some(details)); },
                |details| { stages.borrow_mut().push("fast"); fast.set(Some(details)); });
            assert_eq!(selected, expected);
            assert_eq!(a, b);
            assert_eq!(ordinary.stats, observed.stats);
            assert_eq!(scratch_a.is_some(), scratch_b.is_some());
            assert_eq!(selected.refreshed, refreshed);
            assert_eq!(selected.fast_score, Some(fast.get().unwrap().finished.score));
            if refreshed {
                assert_eq!(*stages.borrow(), vec!["fast", "full"]);
                let details = full.get().unwrap();
                assert!(details.pawn_entry_reused);
                assert_eq!(details.finished.score, selected.evaluation.score);
                assert_eq!(b.retained.age, 0);
            } else {
                assert_eq!(*stages.borrow(), vec!["fast"]);
                assert!(full.get().is_none());
                assert_eq!(selected.evaluation.relation_queries, 0);
                assert_eq!(b.retained, before);
                assert!(scratch_b.is_none());
            }
        }
    }

    #[test]
    fn detailed_sparse_selection_has_no_fast_stage_even_with_capture_exception() {
        let position = Position::from_fen("7k/8/8/8/8/8/P7/K7 w - - 0 1").unwrap();
        let mut evaluator = Evaluator::<true>::new(&position);
        let mut node = Node::root(position, &evaluator.root);
        let mut scratch = None;
        let mut details = None;
        let selected = evaluator.select_noncheck_detailed_observed(&mut node,
            9000, 9001, true, &mut scratch, |value| details = Some(value),
            |_| panic!("sparse admission must not produce a preliminary fast result"));
        assert!(selected.initially_full && !selected.refreshed);
        assert_eq!(selected.fast_score, None);
        assert_eq!(details.unwrap().finished.score, selected.evaluation.score);
        assert_eq!(evaluator.stats.fast, 0);
        assert!(scratch.is_some());
    }

    #[test]
    fn noncheck_selection_preserves_strict_window_endpoints_and_lazy_influence() {
        let (mut evaluator, parent) = initialized();
        let mut node = parent.null_child();
        let fast = evaluator.fast(&node, false).score;
        let mut scratch = None;
        let before = node.retained;
        let selected =
            evaluator.select_noncheck(&mut node, fast + 250, fast + 251, false, &mut scratch);
        assert!(!selected.initially_full && !selected.refreshed);
        assert!(scratch.is_none());
        assert_eq!(node.retained, before);
        let selected =
            evaluator.select_noncheck(&mut node, fast + 250, fast + 251, true, &mut scratch);
        assert!(selected.refreshed && scratch.is_some());
        assert_eq!(node.retained.age, 0);
        let sparse = Position::from_fen("7k/8/8/8/8/8/P7/K7 w - - 0 1").unwrap();
        evaluator.begin_search(&sparse);
        let mut node = Node::root(sparse, &evaluator.root);
        let selected = evaluator.select_noncheck(&mut node, -1, 1, false, &mut None);
        assert!(selected.initially_full && selected.fast_score.is_none());
        assert!(selected.evaluation.late_endgame_applied);
    }

    #[test]
    fn fresh_search_clears_shared_pawns_and_diagnostic_specialization_preserves_results() {
        let (mut evaluator, mut root) = initialized();
        let influence = Influence::build(&root.position);
        evaluator.full(&mut root, &influence, false);
        assert_eq!(evaluator.stats.pawn_reuses, 1);
        evaluator.begin_search(&root.position);
        let a = evaluator.full(&mut root, &influence, false);
        assert_eq!(evaluator.stats.pawn_replacements, 1);
        let mut quiet = Evaluator::<false>::new(&root.position);
        let mut second = Node::root(root.position, &quiet.root);
        let b = quiet.full(&mut second, &influence, false);
        assert_eq!((a, root.retained), (b, second.retained));
        assert_eq!(quiet.stats.full, 0);
        assert_eq!(quiet.stats.relation_queries, a.relation_queries);
    }

    #[test]
    fn fresh_details_observe_one_native_result_and_preserve_components_apis() {
        let position = Position::from_fen(START).unwrap();
        let influence = Influence::build(&position);
        let mut evaluator = Evaluator::<false>::new(&position);
        evaluator.parameters.draw = 10000;
        evaluator.parameters.opponent_selectivity = 49;
        evaluator.begin_search(&position);
        let mut node = Node::root(position, &evaluator.root);
        let mut calls = 0;
        let mut observed = None;
        let result = evaluator.fresh_detailed_observed(&mut node, &influence, false, |details| {
            calls += 1;
            observed = Some(details);
        });
        let details = observed.unwrap();
        assert_eq!(calls, 1);
        assert_eq!(details.base, 6);
        assert_eq!(details.base, details.components.base());
        assert_eq!((result.score, result.lower, result.upper),
            (details.finished.score, details.finished.lower, details.finished.upper));
        assert_eq!(node.retained.positional, details.components.positional());
        assert_eq!(node.retained.pawn_progress, details.components.pawn_progress);
        assert_eq!(result.relation_queries, 10);
        let mut old_node = Node::root(position, &evaluator.root);
        let mut old_components = None;
        let old_result = evaluator.fresh_observed(&mut old_node, &influence, false,
            |components| old_components = Some(components));
        assert_eq!(old_components, Some(details.components));
        assert_eq!((old_result, old_node.retained), (result, node.retained));
        let full_result = evaluator.full_observed(&mut old_node, &influence, false,
            |components| assert_eq!(components, details.components));
        assert_eq!(full_result, result);
    }

    #[test]
    fn detailed_fresh_bypasses_zero_and_full_identity_matches_without_populating_cache() {
        let first = Position::from_fen("7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7 w - - 0 1").unwrap();
        let collision = Position::from_fen("7k/8/2p4P/2p5/7P/1p6/p5PP/K7 w - - 0 1").unwrap();
        assert_eq!(first.pawn, collision.pawn);
        let first_map = Influence::build(&first);
        let collision_map = Influence::build(&collision);
        let mut evaluator = Evaluator::<true>::new(&first);
        let mut first_node = Node::root(first, &evaluator.root);
        evaluator.full(&mut first_node, &first_map, false);
        let retained = evaluator.pawns.select(&first, &first_map).structure;
        let before = evaluator.stats;
        let mut node = Node::root(collision, &evaluator.root);
        evaluator.fresh_detailed_observed(&mut node, &collision_map, false, |_| {});
        assert_eq!(evaluator.stats.pawn_reuses, before.pawn_reuses);
        assert_eq!(evaluator.stats.pawn_replacements, before.pawn_replacements + 1);
        let after = evaluator.pawns.select(&collision, &collision_map);
        assert!(after.reused);
        assert_eq!(after.structure, retained);
        assert_ne!(after.structure, pawn_structure::fresh(&collision, &collision_map, [1024; 2]));

        let empty = Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 0 1").unwrap();
        assert_eq!(empty.pawn, 0);
        let map = Influence::build(&empty);
        let mut evaluator = Evaluator::<true>::new(&empty);
        let mut node = Node::root(empty, &evaluator.root);
        evaluator.fresh_detailed_observed(&mut node, &map, false, |_| {});
        assert_eq!((evaluator.stats.pawn_reuses, evaluator.stats.pawn_replacements), (0, 1));
        evaluator.full(&mut node, &map, false);
        assert_eq!(evaluator.stats.pawn_reuses, 1);
    }

    #[test]
    fn detailed_full_reports_actual_zero_group_replacement_and_identity_hits() {
        fn observe(evaluator: &mut Evaluator, position: Position) -> bool {
            let influence = Influence::build(&position);
            let mut node = Node::root(position, &evaluator.root);
            let mut observed = None;
            evaluator.full_detailed_observed(&mut node, &influence, false,
                |details| observed = Some(details));
            observed.unwrap().pawn_entry_reused
        }
        let empty = Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 0 1").unwrap();
        let group_zero = Position::from_fen("7k/8/8/8/6P1/3P4/8/K7 w - - 0 1").unwrap();
        assert_eq!(group_zero.pawn % 128, 0);
        let mut evaluator = Evaluator::<true>::new(&empty);
        assert!(observe(&mut evaluator, empty));
        assert!(!observe(&mut evaluator, group_zero));
        assert!(observe(&mut evaluator, group_zero));
        assert!(!observe(&mut evaluator, empty));
        assert!(observe(&mut evaluator, empty));
    }

    #[test]
    fn detailed_fast_preserves_node_cache_and_nonfast_work_in_both_monomorphs() {
        fn verify<const D: bool>() {
            let first = Position::from_fen("7k/8/8/8/6P1/3P4/8/K7 w - - 0 1").unwrap();
            let current = Position::from_fen("7k/8/6P1/8/8/3P4/8/K7 w - - 0 1").unwrap();
            assert_eq!(first.pawn % 128, current.pawn % 128);
            assert_ne!(first.pawn, current.pawn);
            let mut evaluator = Evaluator::<D>::new(&first);
            let first_map = Influence::build(&first);
            let mut root = Node::root(first, &evaluator.root);
            evaluator.full(&mut root, &first_map, false);
            let mut node = Node::root(current, &evaluator.root);
            node.retained.positional = root.retained.positional;
            node.retained.pawn_progress = root.retained.pawn_progress;
            node.retained.age = 19;
            let saved = node;
            let before = evaluator.stats;
            let mut calls = 0;
            let mut observed = None;
            let evaluation = evaluator.fast_detailed_observed(&node, false, |details| {
                calls += 1;
                observed = Some(details);
            });
            let details = observed.unwrap();
            assert_eq!(calls, 1);
            assert_eq!(node, saved);
            assert_eq!(evaluation.relation_queries, 0);
            assert_eq!((evaluation.score, evaluation.lower, evaluation.upper),
                (details.finished.score, details.finished.lower, details.finished.upper));
            assert_eq!(evaluator.stats.full, before.full);
            assert_eq!(evaluator.stats.influence_builds, before.influence_builds);
            assert_eq!(evaluator.stats.pawn_reuses, before.pawn_reuses);
            assert_eq!(evaluator.stats.pawn_replacements, before.pawn_replacements);
            assert_eq!(evaluator.stats.relation_queries, before.relation_queries);
            assert_eq!(evaluator.stats.fast, before.fast + u64::from(D));
            // A fast probe/populate on the different current identity would have
            // evicted this same-group first entry. It must still be an exact hit.
            assert!(evaluator.pawns.select(&first, &first_map).reused);
            assert_eq!(evaluator.fast(&node, false), evaluation);
            let mut repeated = None;
            evaluator.fast_detailed_observed(&node, false, |details| repeated = Some(details));
            assert_eq!(observed, repeated);
            assert_eq!(node, saved);
        }
        verify::<false>();
        verify::<true>();
    }
}

#[cfg(all(test, feature = "child-preparation"))]
#[path = "evaluator/child_preparation_tests.rs"]
mod child_preparation_tests;

#[cfg(test)]
#[path = "evaluator/lifecycle_tests.rs"]
mod lifecycle_tests;
