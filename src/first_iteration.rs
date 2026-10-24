//! First unrestricted root pass with actual tactical children.
//! The composed evaluator and ordinary state owner are shared with later iterations.

use crate::evaluator::EvalStats;
use crate::history::SearchHistory;
use crate::movegen::{generate_legal, MoveList};
use crate::position::Position;
use crate::quiescence::{Entry, Limits, Quiescence, Stats, Stopped, Work};
use crate::quiescence_policy;
use crate::types::Move;

pub const FIDELITY: &str = "neutral-evaluation-first-root-iteration-v2";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    NoLegalRoots,
    Stopped(Stopped),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Step {
    pub movement: Move,
    pub lower: i32,
    pub score: i32,
    pub best: i32,
    pub second: i32,
    pub child_pv: Vec<Move>,
    pub root_pv: Vec<Move>,
    pub work: Work,
}

pub struct Outcome {
    pub candidates: Vec<Move>,
    pub steps: Vec<Step>,
    pub score: i32,
    pub pv: Vec<Move>,
    pub work: Work,
    pub stats: Stats,
    pub evaluations: EvalStats,
}

/// Visits the unchanged natural root sequence once. Ranking completed results
/// updates only the next window, never the order of unvisited candidates.
pub fn run<const DIAGNOSTICS: bool>(
    search: &mut Quiescence<DIAGNOSTICS>,
    position: Position,
    history: &mut SearchHistory,
    limits: Limits,
) -> Result<Outcome, Error> {
    let worker_scope = search.evaluator.full_worker_scope();
    let result = run_inner(search, position, history, limits);
    crate::evaluator::Evaluator::<DIAGNOSTICS>::finish_full_worker_scope(worker_scope);
    result
}

fn run_inner<const DIAGNOSTICS: bool>(
    search: &mut Quiescence<DIAGNOSTICS>,
    position: Position,
    history: &mut SearchHistory,
    limits: Limits,
) -> Result<Outcome, Error> {
    assert_eq!(history.search_ply(), 0);
    let root = search.prepare_root(position);
    let mut candidates = MoveList::new();
    generate_legal(&position, &mut candidates);
    if candidates.len == 0 {
        return Err(Error::NoLegalRoots);
    }
    search.begin_sequence(limits);
    let mut best = -10000;
    let mut second = -10000;
    let mut pv = Vec::with_capacity(63);
    let mut steps = Vec::with_capacity(if DIAGNOSTICS { candidates.len } else { 0 });
    let mut last = None;
    for (index, &movement) in candidates.as_slice().iter().enumerate() {
        let lower = if index < 2 { -10000 } else { second };
        let mut child = root.child(&search.evaluator.root, movement);
        history.push(&child.position, Some(movement));
        let returned = search.continue_subtree(
            &mut child,
            history,
            Entry {
                ply: 1,
                target: 1,
                iteration_depth: 1,
                lower: -10000,
                upper: -lower,
                analysis: 0,
                capture_exception: quiescence_policy::capture_exception(&position, &movement),
            },
        );
        history.pop();
        let returned = returned.map_err(Error::Stopped)?;
        let score = -returned.score;
        if score > best {
            second = best;
            best = score;
            pv.clear();
            pv.push(movement);
            pv.extend_from_slice(&returned.pv);
        } else if score > second {
            // Equal best results still occupy the second ranked position.
            second = score;
        }
        if DIAGNOSTICS {
            steps.push(Step {
                movement,
                lower,
                score,
                best,
                second,
                child_pv: returned.pv.clone(),
                root_pv: pv.clone(),
                work: returned.work,
            });
        }
        last = Some(returned);
    }
    let last = last.unwrap();
    Ok(Outcome {
        candidates: candidates.as_slice().to_vec(),
        steps,
        score: best,
        pv,
        work: last.work,
        stats: last.stats,
        evaluations: last.evaluations,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{MoveKind, Square};
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    #[test]
    fn all_start_roots_share_one_work_segment_and_repeat_from_fresh_state() {
        let position = Position::from_fen(START).unwrap();
        let mut history = SearchHistory::new(&position);
        let mut search = Quiescence::<true>::new(&position);
        let a = run(&mut search, position, &mut history, Limits::default()).unwrap();
        assert_eq!(history.search_ply(), 0);
        assert_eq!(a.candidates.len(), 20);
        // Released first-iteration work projection: evaluation omissions do not
        // change these particular entry/relation charges.
        assert_eq!(
            a.work,
            Work {
                charged_search_units: 20,
                charged_relation_queries: 178
            }
        );
        let b = run(&mut search, position, &mut history, Limits::default()).unwrap();
        assert_eq!(
            (a.score, &a.pv, &a.steps, a.work),
            (b.score, &b.pv, &b.steps, b.work)
        );
        let mut ranked = Vec::new();
        for (index, step) in a.steps.iter().enumerate() {
            assert_eq!(step.movement, a.candidates[index]);
            assert_eq!(step.lower, if index < 2 { -10000 } else { ranked[1] });
            ranked.push(step.score);
            ranked.sort_by(|a, b| b.cmp(a));
            assert_eq!(step.best, ranked[0]);
            assert_eq!(step.second, *ranked.get(1).unwrap_or(&-10000));
            assert_eq!(step.work.charged_search_units, index as u64 + 1);
        }
        assert_eq!(a.steps.last().unwrap().work, a.work);
        assert!(a.evaluations.pawn_reuses > 0 && a.evaluations.pawn_replacements > 0);
    }

    #[test]
    fn equal_best_mates_preserve_the_earlier_root_pv_and_fill_second_place() {
        let position = Position::from_fen("7k/6pp/6Q1/8/8/3B4/8/K7 w - - 0 1").unwrap();
        let mut search = Quiescence::<true>::new(&position);
        let mut history = SearchHistory::new(&position);
        let out = run(&mut search, position, &mut history, Limits::default()).unwrap();
        let first = Move::new(
            Square::parse("g6").unwrap(),
            Square::parse("h7").unwrap(),
            MoveKind::Ordinary,
        );
        assert_eq!((out.score, out.pv.as_slice()), (9999, [first].as_slice()));
        assert!(out.steps.iter().filter(|s| s.score == 9999).count() >= 2);
        assert_eq!(out.steps.last().unwrap().second, 9999);
        for step in out.steps.iter().filter(|s| s.best == 9999) {
            assert_eq!(step.root_pv, [first]);
        }
    }

    #[test]
    fn explicit_budget_spans_roots_and_stopped_search_restores_the_public_boundary() {
        let position = Position::from_fen(START).unwrap();
        let mut search = Quiescence::<true>::new(&position);
        let mut history = SearchHistory::new(&position);
        assert_eq!(
            run(
                &mut search,
                position,
                &mut history,
                Limits { nodes: Some(1) }
            )
            .err(),
            Some(Error::Stopped(Stopped::NodeLimit(1)))
        );
        assert_eq!(history.search_ply(), 0);
        let complete = run(&mut search, position, &mut history, Limits::default()).unwrap();
        assert_eq!(complete.work.charged_search_units, 20);
    }

    #[test]
    fn diagnostic_root_steps_do_not_change_semantic_results_or_work() {
        let position = Position::from_fen("1r5k/6pp/6Q1/8/8/3B4/8/K7 b - - 0 1").unwrap();
        let mut a = Quiescence::<true>::new(&position);
        let mut b = Quiescence::<false>::new(&position);
        let mut history = SearchHistory::new(&position);
        let x = run(&mut a, position, &mut history, Limits::default()).unwrap();
        let y = run(&mut b, position, &mut history, Limits::default()).unwrap();
        assert_eq!((x.score, x.pv, x.work), (y.score, y.pv, y.work));
        assert!(y.steps.is_empty());
    }
}
