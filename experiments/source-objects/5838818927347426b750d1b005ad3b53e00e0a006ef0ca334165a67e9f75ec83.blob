//! Concrete tactical recursion over the produced position/evaluation lifetimes.
//!
//! Search policy follows SEARCH-QUIESCENCE-TREE, but the current composed
//! evaluator is partial. Results are development evidence, not KingRE parity.
//! Host polling and timed interruption are not connected yet; the explicit
//! node budget returns an error and never publishes an incomplete score.

pub use crate::engine::Search as Quiescence;
use crate::evaluator::{EvalStats, Node};
use crate::history::{repetition_draw, SearchHistory};
use crate::movegen;
#[cfg(test)]
use crate::movegen::MoveList;
use crate::position::Position;
use crate::quiescence_policy::{self as policy, CaptureContext};
use crate::tactical;
use crate::types::{Move, MoveKind, PieceKind};

const PLIES: usize = 64;
pub const FIDELITY: &str = "retained-neutral-evaluation-quiescence-v2";

#[derive(Clone, Copy, Debug)]
pub struct Entry {
    pub ply: usize,
    pub target: i32,
    pub iteration_depth: i32,
    pub lower: i32,
    pub upper: i32,
    pub analysis: i32,
    /// Classified against the incoming move's parent, before that move.
    pub capture_exception: bool,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Limits {
    pub nodes: Option<u64>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stopped {
    NodeLimit(u64),
    WorkPoll,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Stats {
    pub nodes: u64,
    pub generated: u64,
    pub examined: u64,
    pub children: u64,
    pub projections: u64,
    pub reply_probes: u64,
    pub reused_reply_lists: u64,
    pub optimistic_updates: u64,
    pub unsafe_rejections: u64,
    pub cutoffs: u64,
    pub late_endgame_evaluations: u64,
    pub ordinary_nodes: u64,
    pub table_probes: u64,
    pub table_hits: u64,
    pub table_stores: u64,
    pub fast_cutoffs: u64,
    pub shallow_cutoffs: u64,
    pub null_trials: u64,
    pub mate_probes: u64,
    pub iio_passes: u64,
    pub iio_children: u64,
    pub iio_initial_phases: u64,
    pub iio_tail_phases: u64,
    pub accumulated_extension_uses: u64,
    pub scout_retries: u64,
    pub refreshed_scout_retries: u64,
    pub frontier_skips: u64,
    pub material_threats: u64,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Work {
    pub charged_search_units: u64,
    pub charged_relation_queries: u64,
}

impl Work {
    pub fn effective_search_count(self) -> u64 {
        self.charged_search_units.min(2_147_483_648)
    }
}

pub struct Outcome {
    pub score: i32,
    pub pv: Vec<Move>,
    pub work: Work,
    pub stats: Stats,
    pub evaluations: EvalStats,
}

impl<const DIAGNOSTICS: bool> Quiescence<DIAGNOSTICS> {
    /// Begin one fresh ordinary-search lifetime and fully evaluate its root.
    /// This preparation's relation work is excluded by `search_subtree`.
    pub fn prepare_root(&mut self, position: Position) -> Node {
        self.prepare_root_with_influence(position).0
    }

    pub(crate) fn prepare_root_with_influence(
        &mut self,
        position: Position,
    ) -> (Node, crate::influence::Influence) {
        self.evaluator.begin_search(&position);
        self.learning.clear();
        if let Some(table) = &mut self.remembered {
            table.clear();
        }
        let mut root = Node::root(position, &self.evaluator.root);
        let mut scratch = None;
        let influence = self.evaluator.ensure_influence(&position, &mut scratch);
        self.evaluator.full(
            &mut root,
            influence,
            movegen::in_check(&position, position.side),
        );
        (root, scratch.unwrap())
    }

    /// Search one selected node, preserving shared pawn effects and the caller's
    /// history boundary even if a descendant exhausts the explicit budget.
    pub fn search_subtree(
        &mut self,
        node: &mut Node,
        history: &mut SearchHistory,
        entry: Entry,
        limits: Limits,
    ) -> Result<Outcome, Stopped> {
        self.begin_sequence(limits);
        self.continue_subtree(node, history, entry)
    }

    /// Start the measured/search-work segment without clearing shared pawns.
    /// Root candidates then use `continue_subtree` in actual visit order.
    pub fn begin_sequence(&mut self, limits: Limits) {
        self.timing = None;
        self.stats = Stats::default();
        self.evaluator.stats = EvalStats::default();
        self.pv_len.fill(0);
        self.limits = limits;
    }

    pub fn continue_subtree(
        &mut self,
        node: &mut Node,
        history: &mut SearchHistory,
        entry: Entry,
    ) -> Result<Outcome, Stopped> {
        assert!((1..PLIES).contains(&entry.ply));
        assert_eq!(entry.ply, history.search_ply());
        assert!(entry.iteration_depth >= 1 && entry.target >= 0);
        assert!(-10000 <= entry.lower && entry.lower < entry.upper && entry.upper <= 10000);
        let score = self.visit_q(node, history, entry, None, false)?;
        Ok(self.outcome(entry.ply, score))
    }

    pub(crate) fn visit_q(
        &mut self,
        node: &mut Node,
        history: &mut SearchHistory,
        entry: Entry,
        checked: Option<bool>,
        replies_available: bool,
    ) -> Result<i32, Stopped> {
        self.charge_node()?;
        let ply = entry.ply;
        self.pv_len[ply] = 0;
        let position = node.position;
        let checked = checked.unwrap_or_else(|| movegen::in_check(&position, position.side));
        if repetition_draw(history.repetition_count(checked), ply, entry.analysis) {
            return Ok(0);
        }
        self.learning.clear_next(ply);
        if entry.upper <= 0 && history.short_reversal() {
            return Ok(0);
        }
        if ply == PLIES - 1 {
            let value = self.evaluator.fast(node, checked);
            if DIAGNOSTICS {
                self.stats.late_endgame_evaluations += u64::from(value.late_endgame_applied);
            }
            return Ok(value.score);
        }

        let mut influence = None;
        let mut lower = entry.lower;
        let (mut best, standing, evaluation_upper) = if checked {
            (-10000, -10000, 10000)
        } else {
            let value = self
                .evaluator
                .select_noncheck(
                    node,
                    lower,
                    entry.upper,
                    entry.capture_exception,
                    &mut influence,
                )
                .evaluation;
            if DIAGNOSTICS {
                self.stats.late_endgame_evaluations += u64::from(value.late_endgame_applied);
            }
            if value.lower >= entry.upper {
                return Ok(value.lower);
            }
            if value.upper <= lower {
                return Ok(value.upper);
            }
            if value.score >= entry.upper {
                return Ok(value.score);
            }
            lower = lower.max(value.score);
            (value.score, value.score, value.upper)
        };

        if checked {
            if replies_available {
                if DIAGNOSTICS {
                    self.stats.reused_reply_lists += 1;
                }
            } else {
                movegen::generate_legal(&position, &mut self.candidates[ply]);
            }
        } else {
            tactical::generate(&position, &mut self.candidates[ply]);
        }
        let count = self.candidates[ply].len;
        if DIAGNOSTICS {
            self.stats.generated += count as u64;
        }
        if count == 0 {
            return Ok(if checked { ply as i32 - 10000 } else { best });
        }
        if checked && ply as i32 - 9998 >= entry.upper {
            return Ok(ply as i32 - 9998);
        }
        tactical::order_with_scratch(
            &position,
            &self.evaluator.root,
            &self.learning.history,
            &mut self.candidates[ply],
            &mut self.ordering,
        );

        let previous = history.previous_move();
        let king = position.piece_squares(position.side, PieceKind::King)[0];
        let enemy_king = position.piece_squares(position.side.opponent(), PieceKind::King)[0];
        for index in 0..count {
            let movement = self.candidates[ply].moves[index];
            if DIAGNOSTICS {
                self.stats.examined += 1;
            }
            let mut prepared_child = None;
            let mut child_checked = None;
            let mut complete_replies = false;
            if !checked {
                let recapture = policy::is_recapture(&movement, previous);
                if ply as i32 > entry.target + entry.iteration_depth && !recapture {
                    continue;
                }
                let victim = position.board[movement.to().0 as usize];
                let special = matches!(
                    movement.kind(),
                    MoveKind::Promotion(_) | MoveKind::EnPassant
                );
                let mut forced = special;
                if !special && !victim.is_empty() {
                    let estimate = standing
                        + policy::allowance(
                            &self.evaluator.root,
                            &position,
                            &movement,
                            node.retained.positional,
                            node.retained.pawn_progress,
                        );
                    let moving_value =
                        policy::moving_value(&self.evaluator.root, &position, &movement);
                    let decision = policy::capture_policy(
                        estimate,
                        moving_value,
                        CaptureContext {
                            ply: ply as i32,
                            target: entry.target,
                            iteration_depth: entry.iteration_depth,
                            best,
                            alpha: lower,
                        },
                        || {
                            let map = self.evaluator.ensure_influence(&position, &mut influence);
                            policy::destination_support(&position, map, movement.to())
                        },
                    );
                    if DIAGNOSTICS && decision.best > best {
                        self.stats.optimistic_updates += 1;
                    }
                    best = decision.best;
                    forced = decision.force_search;
                }

                let board = movegen::projected_board(&position, movement);
                if DIAGNOSTICS {
                    self.stats.projections += 1;
                }
                let (checking, double_check) =
                    movegen::check_routes(&board, enemy_king, position.side, movement.to());
                child_checked = Some(checking);
                // Every quiet item from the non-check producer checks directly;
                // retain this screen explicitly for the composed policy.
                if !policy::initial_eligibility(
                    &position,
                    &movement,
                    previous,
                    checking,
                    ply as i32,
                    entry.target,
                    entry.iteration_depth,
                ) {
                    continue;
                }
                if !forced {
                    if !checking {
                        continue;
                    }
                    if !double_check && !recapture {
                        let child = node.child(&self.evaluator.root, movement);
                        history.push(&child.position, Some(movement));
                        let repeats = history.repetition_count(true) > 0;
                        if !repeats {
                            if DIAGNOSTICS {
                                self.stats.reply_probes += 1;
                            }
                            let replies = movegen::legal_replies_up_to_two(
                                &child.position,
                                &mut self.candidates[ply + 1],
                            );
                            if replies > 1 {
                                history.pop();
                                continue;
                            }
                            complete_replies = true;
                        }
                        history.pop();
                        prepared_child = Some(child);
                    }
                }
                let moving = position.board[movement.from().0 as usize];
                let king_after = if moving.kind() == PieceKind::King {
                    movement.to()
                } else {
                    king
                };
                if movegen::attacked(&board, king_after, position.side.opponent()) {
                    if DIAGNOSTICS {
                        self.stats.unsafe_rejections += 1;
                    }
                    continue;
                }
            }
            let mut child =
                prepared_child.unwrap_or_else(|| node.child(&self.evaluator.root, movement));
            let capture_exception = policy::capture_exception(&position, &movement);
            history.push(&child.position, Some(movement));
            if DIAGNOSTICS {
                self.stats.children += 1;
            }
            let returned = self.visit_q(
                &mut child,
                history,
                Entry {
                    ply: ply + 1,
                    target: entry.target + i32::from(checked),
                    lower: -entry.upper,
                    upper: -lower,
                    capture_exception,
                    ..entry
                },
                child_checked,
                complete_replies,
            );
            history.pop();
            let score = -returned?;
            if score > best {
                best = score;
                if score > lower && score < entry.upper {
                    self.pv[ply][0] = movement;
                    let child_len = self.pv_len[ply + 1];
                    let (parents, children) = self.pv.split_at_mut(ply + 1);
                    parents[ply][1..1 + child_len].copy_from_slice(&children[0][..child_len]);
                    self.pv_len[ply] = child_len + 1;
                }
            }
            if score > lower {
                lower = score;
                if lower >= entry.upper {
                    if DIAGNOSTICS {
                        self.stats.cutoffs += 1;
                    }
                    break;
                }
            }
        }
        Ok(best.min(evaluation_upper))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{MoveKind, Square};

    fn movement(from: &str, to: &str) -> Move {
        Move::new(
            Square::parse(from).unwrap(),
            Square::parse(to).unwrap(),
            MoveKind::Ordinary,
        )
    }

    fn selected<const D: bool>(
        fen: &str,
        token: &str,
    ) -> (Quiescence<D>, Node, SearchHistory, Entry) {
        let position = Position::from_fen(fen).unwrap();
        let mut search = Quiescence::new(&position);
        let root = search.prepare_root(position);
        let mut history = SearchHistory::new(&position);
        let mut legal = MoveList::new();
        movegen::generate_legal(&position, &mut legal);
        let movement = *legal
            .as_slice()
            .iter()
            .find(|m| m.to_string() == token)
            .unwrap();
        let child = root.child(&search.evaluator.root, movement);
        history.push(&child.position, Some(movement));
        let entry = Entry {
            ply: 1,
            target: 1,
            iteration_depth: 1,
            lower: -10000,
            upper: 10000,
            analysis: 0,
            capture_exception: policy::capture_exception(&position, &movement),
        };
        (search, child, history, entry)
    }

    #[test]
    fn mate_returns_before_static_and_evasion_boundary_precedes_ordering() {
        let (mut search, mut node, mut history, entry) =
            selected::<true>("7k/8/5KQ1/8/8/8/8/8 w - - 0 1", "g6g7");
        assert!(movegen::in_check(&node.position, node.position.side));
        let out = search
            .search_subtree(&mut node, &mut history, entry, Limits::default())
            .unwrap();
        assert_eq!(
            (out.score, out.work.charged_search_units, out.pv.len()),
            (-9999, 1, 0)
        );
        assert_eq!(out.evaluations, EvalStats::default());

        let (mut search, mut node, mut history, mut entry) =
            selected::<true>("7k/8/8/8/8/8/8/K6R w - - 0 1", "h1h7");
        entry.lower = -10000;
        entry.upper = -9997;
        let out = search
            .search_subtree(&mut node, &mut history, entry, Limits::default())
            .unwrap();
        assert_eq!(
            (out.score, out.stats.nodes, out.stats.examined),
            (-9997, 1, 0)
        );
        assert!(out.stats.generated > 0 && out.pv.is_empty());
    }

    #[test]
    fn explicit_stop_restores_history_and_a_fresh_search_repeats() {
        let fen = "r3k3/1Pr5/8/8/8/8/8/4K3 b - - 0 1";
        let (mut search, mut node, mut history, entry) = selected::<true>(fen, "c7c8");
        assert_eq!(
            search
                .search_subtree(&mut node, &mut history, entry, Limits { nodes: Some(1) })
                .err(),
            Some(Stopped::NodeLimit(1))
        );
        assert_eq!(history.search_ply(), 1);
        let out = search
            .search_subtree(&mut node, &mut history, entry, Limits::default())
            .unwrap();
        assert_eq!(history.search_ply(), 1);
        let (mut fresh, mut fresh_node, mut fresh_history, entry) = selected::<true>(fen, "c7c8");
        let repeated = fresh
            .search_subtree(
                &mut fresh_node,
                &mut fresh_history,
                entry,
                Limits::default(),
            )
            .unwrap();
        assert_eq!(
            (out.score, out.pv, out.work),
            (repeated.score, repeated.pv, repeated.work)
        );
        assert!(out.stats.nodes > 1 && out.evaluations.full > 0);
    }

    #[test]
    fn diagnostic_specialization_preserves_score_pv_and_semantic_work() {
        let fen = "r3k3/1Pr5/8/8/8/8/8/4K3 b - - 0 1";
        let (mut a, mut an, mut ah, entry) = selected::<true>(fen, "c7c8");
        let (mut b, mut bn, mut bh, _) = selected::<false>(fen, "c7c8");
        let x = a
            .search_subtree(&mut an, &mut ah, entry, Limits::default())
            .unwrap();
        let y = b
            .search_subtree(&mut bn, &mut bh, entry, Limits::default())
            .unwrap();
        assert_eq!(
            (x.score, x.pv, x.work, an.retained),
            (y.score, y.pv, y.work, bn.retained)
        );
        assert_eq!(y.stats.examined, 0);
        assert_eq!(y.evaluations.full, 0);
    }

    #[test]
    fn released_mate_summaries_preserve_first_equal_score_pv_and_relation_work() {
        // Summary projections from the released tree cases. These do not claim
        // trace parity, or qualify this partial evaluator on the other cases.
        for (fen, token, nodes, queries) in [
            ("1r5k/7p/6Q1/8/8/3B4/8/K7 b - - 0 1", "b8b6", 6, 1),
            ("1r5k/6pp/6Q1/8/8/3B4/8/K7 b - - 0 1", "b8b7", 5, 0),
        ] {
            let (mut search, mut node, mut history, entry) = selected::<true>(fen, token);
            let out = search
                .search_subtree(&mut node, &mut history, entry, Limits::default())
                .unwrap();
            assert_eq!(out.score, 9998);
            assert_eq!(out.pv, [movement("g6", "h7")]);
            assert_eq!(
                out.work,
                Work {
                    charged_search_units: nodes,
                    charged_relation_queries: queries
                }
            );
        }
    }

    #[test]
    fn terminal_ply_uses_fast_retained_state_after_admission_and_clears_ply64() {
        // Controlled history isolates the terminal boundary; this is not a
        // claim that these repeated zero-halfmove boundaries are a legal game.
        let position = Position::from_fen("7k/8/8/8/8/8/8/K6R b - - 0 1").unwrap();
        let mut search = Quiescence::<true>::new(&position);
        let mut node = search.prepare_root(position);
        node.retained.positional = 123;
        node.retained.pawn_progress = 17;
        node.retained.age = 19;
        let saved = node.retained;
        let expected = search.evaluator.fast(&node, true).score;
        let mut history = SearchHistory::new(&position);
        for _ in 0..63 {
            history.push(&position, None);
        }
        search.learning.killers[64] = [movement("a1", "a2"), Move::NONE];
        let out = search
            .search_subtree(
                &mut node,
                &mut history,
                Entry {
                    ply: 63,
                    target: 63,
                    iteration_depth: 1,
                    lower: -10000,
                    upper: 10000,
                    analysis: 0,
                    capture_exception: false,
                },
                Limits::default(),
            )
            .unwrap();
        assert_eq!(out.score, expected);
        assert_eq!(
            out.work,
            Work {
                charged_search_units: 1,
                charged_relation_queries: 0
            }
        );
        assert_eq!(
            (
                out.evaluations.fast,
                out.evaluations.full,
                out.evaluations.influence_builds
            ),
            (1, 0, 0)
        );
        assert_eq!(node.retained, saved);
        assert_eq!(search.learning.killers[64], [Move::NONE; 2]);
    }

    #[test]
    fn repetition_admission_preserves_killers_before_terminal_fast() {
        let position = Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 101 1").unwrap();
        let mut search = Quiescence::<true>::new(&position);
        let mut node = search.prepare_root(position);
        let mut history = SearchHistory::new(&position);
        history.push(&position, None);
        search.learning.killers[2] = [movement("a1", "a2"), Move::NONE];
        let entry = Entry {
            ply: 1,
            target: 1,
            iteration_depth: 1,
            lower: -1,
            upper: 1,
            analysis: 0,
            capture_exception: false,
        };
        let out = search
            .search_subtree(&mut node, &mut history, entry, Limits::default())
            .unwrap();
        assert_eq!(
            (
                out.score,
                out.stats.nodes,
                out.evaluations.full,
                out.evaluations.fast
            ),
            (0, 1, 0, 0)
        );
        assert_eq!(search.learning.killers[2][0], movement("a1", "a2"));
    }
}
