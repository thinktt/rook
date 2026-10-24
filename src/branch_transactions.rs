//! Bounded serial simulation of queued restricted-root branch transactions.
//!
//! This is fixed completion with NoHost, no timing controller or node limit,
//! and inline evaluation. It measures feasibility and copy/log/replay costs;
//! executing the proposed tasks serially cannot demonstrate a speedup.
use std::collections::VecDeque;
use std::fmt::Write;
use std::time::Instant;

use crate::branch_journal::{Event, Log, Sink};
use crate::engine::{Config, Search};
use crate::evaluator::{EvalStats, Node, Parameters};
use crate::history::SearchHistory;
use crate::influence::Influence;
use crate::movegen::{self, MoveList};
use crate::ordinary::{Predecessor, Request};
use crate::position::Position;
use crate::quiescence::{Limits, Stats};
use crate::remembered::{Query, Store};
use crate::root_schedule::{Attempt, Completed, Iteration, Policy, Returned, Row};
use crate::types::Move;

#[derive(Clone, Copy, Debug)]
pub struct Caps {
    pub max_depth: u8,
    pub max_tail_candidates: usize,
    pub queue_depth: usize,
    pub log_events: usize,
}
impl Default for Caps {
    fn default() -> Self {
        Self {
            max_depth: 6,
            max_tail_candidates: 8,
            queue_depth: 2,
            log_events: 16_384,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct Timings {
    pub prefix_ns: u128,
    pub snapshot_ns: u128,
    pub speculation_ns: u128,
    /// Sink insertion/allocation only; event construction is in speculation_ns.
    pub recording_ns: u128,
    pub request_validation_ns: u128,
    pub staging_ns: u128,
    pub replay_ns: u128,
    pub commit_ns: u128,
    pub comparison_ns: u128,
    /// Independent canonical execution. For rejected tasks this is also the
    /// measured native fallback cost, and must not be counted twice.
    pub oracle_ns: u128,
    pub oracle_snapshot_ns: u128,
    pub fallback_ns: u128,
}

#[derive(Clone, Debug)]
pub struct CandidateReport {
    pub depth: u8,
    pub index: usize,
    pub id: u16,
    pub movement: String,
    /// Number of preceding still-unconsumed tasks when this task was enqueued.
    pub ahead_distance: usize,
    pub enqueued_at_turn: usize,
    pub consumed_at_turn: usize,
    pub speculative_nodes: u64,
    pub canonical_nodes: u64,
    pub accepted: bool,
    pub semantic_accepted: bool,
    pub audit_failed: bool,
    pub rejection: Option<&'static str>,
    pub rejection_event: Option<usize>,
    pub oracle_match: bool,
    pub rollback_unchanged: bool,
    pub passes: usize,
    pub log_events: usize,
    pub log_attempted: usize,
    pub log_bytes: usize,
    pub log_overflowed: bool,
    pub snapshot_bytes: usize,
    pub timings: Timings,
}

#[derive(Clone, Debug)]
pub struct ControlReport {
    pub name: &'static str,
    pub accepted: bool,
    pub passed: bool,
    pub rejection: Option<&'static str>,
    pub rejection_event: Option<usize>,
    pub events: usize,
    pub nodes: u64,
    pub staged_writes_before_rejection: usize,
    pub canonical_unchanged: bool,
    pub matches_fresh_canonical: bool,
    pub differs_from_speculative_final: bool,
    pub replay_ns: u128,
    pub oracle_ns: u128,
    pub comparison_ns: u128,
}

#[derive(Clone, Debug)]
pub struct Report {
    pub caps: Caps,
    pub zero_randomness: bool,
    pub restricted_depth: Option<u8>,
    pub restricted_entry_nodes: Option<u64>,
    pub completed_depth: u8,
    pub incomplete_iteration: bool,
    pub stopped_reason: &'static str,
    pub prefix_nodes: u64,
    pub canonical_nodes: u64,
    pub candidate_nodes: u64,
    pub accepted_nodes: u64,
    pub rejected_nodes: u64,
    pub incomplete_nodes: u64,
    pub abandoned_nodes: u64,
    pub abandoned_candidates: usize,
    pub unsafe_nodes: u64,
    pub unsafe_validation: bool,
    pub event_size_bytes: usize,
    pub oracle_nodes: u64,
    pub max_queue_len: usize,
    pub peak_queue_snapshot_bytes: usize,
    pub peak_queue_log_bytes: usize,
    pub elapsed_ns: u128,
    pub timings: Timings,
    pub candidates: Vec<CandidateReport>,
    pub controls: Vec<ControlReport>,
}

struct Environment {
    root: Node,
    influence: Influence,
    checked: bool,
    movements: Vec<Move>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct Pass {
    attempt: Attempt,
    score: i32,
    nodes: u64,
    relations: u64,
    child: Node,
    pv: Vec<Move>,
}

struct Branch {
    child: Node,
    passes: Vec<Pass>,
    completed: Completed,
    base_stats: Stats,
    base_evaluations: EvalStats,
}

struct Task {
    depth: u8,
    attempt: Attempt,
    history: SearchHistory,
    final_state: Search<true>,
    branch: Branch,
    log: Log,
    ahead: usize,
    turn: usize,
    snapshot_bytes: usize,
    snapshot_ns: u128,
    speculation_ns: u128,
}

fn error(error: impl std::fmt::Debug) -> String {
    format!("{error:?}")
}

/// Execute the native branch, preserving one actual child across native retries.
/// The scheduler is private here; its completed ranking is installed by the
/// canonical owner only after validation or native fallback.
fn execute(
    search: &mut Search<true>,
    history: &mut SearchHistory,
    env: &Environment,
    depth: u8,
    mut schedule: Iteration,
    mut attempt: Attempt,
) -> Result<Branch, String> {
    assert!(search.timing.is_none() && search.limits.nodes.is_none());
    let movement = env.movements[usize::from(attempt.id)];
    let mut child = env.root.child(&search.evaluator.root, movement);
    let base_stats = search.stats;
    let base_evaluations = search.evaluator.stats;
    let mut passes = Vec::with_capacity(2);
    loop {
        history.push(&child.position, Some(movement));
        let value = search.visit_ordinary(
            &mut child,
            history,
            Request {
                ply: 1,
                depth: i32::from(depth) - 1,
                lower: -attempt.window[1],
                upper: -attempt.window[0],
                previous_extension: 0,
                iteration: i32::from(depth),
                checked: None,
            },
            Predecessor {
                position: &env.root.position,
                influence: &env.influence,
                checked: env.checked,
                movement: Some(movement),
            },
        );
        history.pop();
        let score = -value.map_err(error)?;
        passes.push(Pass {
            attempt,
            score,
            nodes: search.stats.nodes - base_stats.nodes,
            relations: search.evaluator.stats.relation_queries - base_evaluations.relation_queries,
            child,
            pv: search.pv[1][..search.pv_len[1]].to_vec(),
        });
        match schedule.returned(score, search.stats.nodes) {
            Returned::Retry(next) => attempt = next,
            Returned::Completed(completed) => {
                return Ok(Branch {
                    child,
                    passes,
                    completed,
                    base_stats,
                    base_evaluations,
                });
            }
        }
    }
}

fn advance(schedule: &mut Iteration, branch: &Branch, start_nodes: u64) -> Completed {
    let mut completed = None;
    for (index, pass) in branch.passes.iter().enumerate() {
        match schedule.returned(pass.score, start_nodes + pass.nodes) {
            Returned::Retry(next) => {
                assert_eq!(branch.passes.get(index + 1).map(|p| p.attempt), Some(next));
            }
            Returned::Completed(value) => {
                assert_eq!(index + 1, branch.passes.len());
                completed = Some(value);
            }
        }
    }
    completed.expect("native branch must complete")
}

fn same_passes(a: &Branch, b: &Branch) -> bool {
    a.child == b.child && a.passes == b.passes
}

fn request_matches(task: &Task, depth: u8, actual: Attempt, history: &SearchHistory) -> bool {
    task.depth == depth && task.attempt == actual && task.history == *history
}

// All counters are additive under the explicitly fixed-completion environment.
// Their absolute origins may differ between enqueue and ordered consumption.
macro_rules! rebase {
    ($entry:expr, $final:expr, $base:expr; $($field:ident),+ $(,)?) => {{
        let mut value = $entry;
        $(value.$field += $final.$field - $base.$field;)+
        value
    }};
}
fn install_outputs(stage: &mut Search<true>, task: &Task) {
    stage.stats = rebase!(stage.stats, task.final_state.stats, task.branch.base_stats;
        nodes, generated, examined, children, projections, reply_probes, reused_reply_lists,
        optimistic_updates, unsafe_rejections, cutoffs, late_endgame_evaluations,
        ordinary_nodes, table_probes, table_hits, table_stores, fast_cutoffs, shallow_cutoffs,
        null_trials, mate_probes, iio_passes, iio_children, iio_nonzero_fresh_extensions,
        iio_initial_phases, iio_tail_phases, accumulated_extension_uses, scout_retries,
        refreshed_scout_retries, frontier_skips, material_threats);
    stage.evaluator.stats = rebase!(stage.evaluator.stats, task.final_state.evaluator.stats,
        task.branch.base_evaluations;
        full, fast, influence_builds, pawn_reuses, pawn_replacements, relation_queries);
    stage.pv_len[1] = task.final_state.pv_len[1];
    stage.pv[1] = task.final_state.pv[1];
}

fn replay(log: &Log, stage: &mut Search<true>) -> crate::branch_journal::ReplayResult {
    let root = stage.evaluator.root.clone();
    log.replay(
        &root,
        stage.remembered.as_mut().unwrap(),
        &mut stage.learning,
        stage.evaluator.research_pawns(),
    )
}

fn enqueue(
    canonical: &Search<true>,
    history: &SearchHistory,
    env: &Environment,
    depth: u8,
    schedule: &Iteration,
    ahead: usize,
    turn: usize,
    cap: usize,
) -> Result<Option<Task>, String> {
    let snapshot_start = Instant::now();
    let Some((projected, attempt)) = schedule.research_proposal(ahead, canonical.stats.nodes)
    else {
        return Ok(None);
    };
    let mut state = canonical.research_clone();
    let saved_history = history.clone();
    let mut task_history = saved_history.clone();
    let snapshot_bytes = state.research_bytes()
        + saved_history.research_bytes()
        + task_history.research_bytes()
        + projected.research_bytes();
    let snapshot_ns = snapshot_start.elapsed().as_nanos();
    let sink = Sink::new(cap);
    state.research_attach_sink(Some(sink.clone()));
    let start = Instant::now();
    let branch = execute(
        &mut state,
        &mut task_history,
        env,
        depth,
        projected,
        attempt,
    )?;
    let speculation_ns = start.elapsed().as_nanos();
    state.research_attach_sink(None);
    let log = sink.take();
    assert_eq!(task_history, saved_history);
    Ok(Some(Task {
        depth,
        attempt,
        history: saved_history,
        final_state: state,
        branch,
        log,
        ahead,
        turn,
        snapshot_bytes,
        snapshot_ns,
        speculation_ns,
    }))
}

/// Run one queue-depth case from a fresh search lifetime. Root scheduling and
/// every recursive branch use their native implementations. This adapter uses
/// zero root randomness; seed-dependent root adjustments are outside its API.
/// Restriction begins only after the actual serial prefix reaches 25,000 nodes.
pub fn run(
    position: Position,
    mut history: SearchHistory,
    parameters: Parameters,
    config: Config,
    caps: Caps,
) -> Result<Report, String> {
    if !(1..=8).contains(&caps.max_depth)
        || !(1..=8).contains(&caps.max_tail_candidates)
        || ![2, 4].contains(&caps.queue_depth)
        || caps.log_events == 0
        || caps.log_events > 16_384
    {
        return Err(
            "branch pilot caps require depth1..8, tail1..8, queue2/4, events1..16384".into(),
        );
    }
    if history.search_ply() != 0 {
        return Err("branch pilot requires root history boundary".into());
    }
    let started = Instant::now();
    let mut canonical = Search::<true>::new(&position);
    canonical.config = config;
    canonical.evaluator.parameters = parameters;
    canonical.evaluator.set_research_thread_budget(1)?;
    canonical.ensure_table()?;
    canonical.bind_geometry_permission(&position);
    let (root, influence) = canonical.prepare_root_with_influence(position);
    let mut legal = MoveList::new();
    movegen::generate_legal(&position, &mut legal);
    if legal.len < 2 {
        return Err("branch pilot needs at least two legal root candidates".into());
    }
    let env = Environment {
        root,
        influence,
        checked: movegen::in_check(&position, position.side),
        movements: legal.as_slice().to_vec(),
    };
    canonical.begin_owned_sequence(Limits { nodes: None });
    let mut report = Report {
        caps,
        zero_randomness: true,
        restricted_depth: None,
        restricted_entry_nodes: None,
        completed_depth: 0,
        incomplete_iteration: false,
        stopped_reason: "depth-cap-before-restricted",
        prefix_nodes: 0,
        canonical_nodes: 0,
        candidate_nodes: 0,
        accepted_nodes: 0,
        rejected_nodes: 0,
        incomplete_nodes: 0,
        abandoned_nodes: 0,
        abandoned_candidates: 0,
        unsafe_nodes: 0,
        unsafe_validation: false,
        event_size_bytes: std::mem::size_of::<Event>(),
        oracle_nodes: 0,
        max_queue_len: 0,
        peak_queue_snapshot_bytes: 0,
        peak_queue_log_bytes: 0,
        elapsed_ns: 0,
        timings: Timings::default(),
        candidates: Vec::new(),
        controls: Vec::new(),
    };
    let mut rows = env
        .movements
        .iter()
        .enumerate()
        .map(|(id, _)| Row {
            id: id as u16,
            score: 0,
            work: 0,
        })
        .collect();
    let mut previous = 0;
    for depth in 1..=caps.max_depth {
        let mut schedule = Iteration::new(rows, canonical.stats.nodes, previous);
        let restricted = schedule.policy() == Policy::Restricted;
        if restricted {
            report.restricted_depth = Some(depth);
            report.restricted_entry_nodes = Some(canonical.stats.nodes);
        }
        // The whole unrestricted prefix and restricted child0 execute normally.
        while let Some(attempt) = schedule.next(canonical.stats.nodes) {
            let start_nodes = canonical.stats.nodes;
            let start = Instant::now();
            let branch = execute(
                &mut canonical,
                &mut history,
                &env,
                depth,
                schedule.clone(),
                attempt,
            )?;
            report.timings.prefix_ns += start.elapsed().as_nanos();
            let completed = advance(&mut schedule, &branch, start_nodes);
            assert_eq!(completed, branch.completed);
            if restricted {
                break;
            }
        }
        if !restricted {
            report.completed_depth = depth;
            previous = schedule.best();
            rows = schedule.into_ranked();
            continue;
        }
        report.prefix_nodes = canonical.stats.nodes;
        let sample = caps.max_tail_candidates.min(env.movements.len() - 1);
        let mut queue = VecDeque::<Task>::new();
        for turn in 0..sample {
            while queue.len() < caps.queue_depth && turn + queue.len() < sample {
                if let Some(task) = enqueue(
                    &canonical,
                    &history,
                    &env,
                    depth,
                    &schedule,
                    queue.len(),
                    turn,
                    caps.log_events,
                )? {
                    report.candidate_nodes +=
                        task.final_state.stats.nodes - task.branch.base_stats.nodes;
                    queue.push_back(task);
                } else {
                    break;
                }
            }
            report.max_queue_len = report.max_queue_len.max(queue.len());
            report.peak_queue_snapshot_bytes = report.peak_queue_snapshot_bytes.max(
                queue
                    .iter()
                    .map(|task| task.final_state.research_bytes() + task.history.research_bytes())
                    .sum(),
            );
            report.peak_queue_log_bytes = report
                .peak_queue_log_bytes
                .max(queue.iter().map(|task| task.log.estimated_bytes()).sum());
            let task = queue.pop_front().expect("bounded tail task exists");
            let attempt = schedule
                .next(canonical.stats.nodes)
                .expect("native tail demand exists");
            let start_nodes = canonical.stats.nodes;
            let mut timing = Timings {
                snapshot_ns: task.snapshot_ns,
                speculation_ns: task.speculation_ns,
                recording_ns: task.log.recording_ns,
                ..Timings::default()
            };
            let oracle_snapshot_start = Instant::now();
            let entry_witness = canonical.research_clone();
            let mut oracle = canonical.research_clone();
            let mut oracle_history = history.clone();
            timing.oracle_snapshot_ns = oracle_snapshot_start.elapsed().as_nanos();
            let oracle_start = Instant::now();
            let reference = execute(
                &mut oracle,
                &mut oracle_history,
                &env,
                depth,
                schedule.clone(),
                attempt,
            )?;
            timing.oracle_ns = oracle_start.elapsed().as_nanos();
            report.oracle_nodes += oracle.stats.nodes - start_nodes;

            let validation_start = Instant::now();
            let request_matches = request_matches(&task, depth, attempt, &history);
            timing.request_validation_ns = validation_start.elapsed().as_nanos();
            let mut rejection = (!request_matches).then_some("request-window");
            let mut rejection_event = None;
            let mut oracle_match = false;
            let mut staged = None;
            let mut audit_failed = false;
            if rejection.is_none() {
                let staging_start = Instant::now();
                let mut stage = canonical.research_clone();
                timing.staging_ns = staging_start.elapsed().as_nanos();
                let replay_start = Instant::now();
                let replayed = replay(&task.log, &mut stage);
                timing.replay_ns = replay_start.elapsed().as_nanos();
                if let Some(reason) = replayed.rejection {
                    rejection = Some(reason.kind.name());
                    rejection_event = Some(reason.event_index);
                } else {
                    let output_staging_start = Instant::now();
                    install_outputs(&mut stage, &task);
                    timing.staging_ns += output_staging_start.elapsed().as_nanos();
                    let compare_start = Instant::now();
                    oracle_match =
                        same_passes(&task.branch, &reference) && stage.research_eq(&oracle);
                    timing.comparison_ns = compare_start.elapsed().as_nanos();
                    if oracle_match {
                        staged = Some(stage);
                    } else {
                        audit_failed = true;
                    }
                }
            }
            let semantic_accepted = rejection.is_none();
            let accepted = semantic_accepted && !audit_failed;
            // Validation has only mutated detached staging. Compare against an
            // independent untouched entry clone before publishing fallback.
            let rollback_unchanged = if accepted {
                true
            } else {
                let compare_start = Instant::now();
                let unchanged = canonical.research_eq(&entry_witness) && history == oracle_history;
                timing.comparison_ns += compare_start.elapsed().as_nanos();
                unchanged
            };
            if !rollback_unchanged {
                audit_failed = true;
            }
            let commit_start = Instant::now();
            if let Some(stage) = staged {
                canonical = stage;
            } else if !audit_failed {
                canonical = oracle;
                timing.fallback_ns = timing.oracle_ns;
            }
            timing.commit_ns = commit_start.elapsed().as_nanos();
            if !audit_failed {
                let completed = advance(&mut schedule, &reference, start_nodes);
                assert_eq!(completed, reference.completed);
            }
            let speculative_nodes = task.final_state.stats.nodes - task.branch.base_stats.nodes;
            let canonical_nodes = canonical.stats.nodes - start_nodes;
            if task.log.overflowed {
                report.incomplete_nodes += speculative_nodes;
            }
            if accepted {
                report.accepted_nodes += speculative_nodes;
            } else if audit_failed {
                report.unsafe_nodes += speculative_nodes;
            } else {
                report.rejected_nodes += speculative_nodes;
            }
            add_timings(&mut report.timings, &timing);
            report.candidates.push(CandidateReport {
                depth,
                index: attempt.index,
                id: attempt.id,
                movement: env.movements[usize::from(attempt.id)].to_string(),
                ahead_distance: task.ahead,
                enqueued_at_turn: task.turn,
                consumed_at_turn: turn,
                speculative_nodes,
                canonical_nodes,
                accepted,
                semantic_accepted,
                audit_failed,
                rejection,
                rejection_event,
                oracle_match,
                rollback_unchanged,
                passes: reference.passes.len(),
                log_events: task.log.events.len(),
                log_attempted: task.log.attempted,
                log_bytes: task.log.estimated_bytes(),
                log_overflowed: task.log.overflowed,
                snapshot_bytes: task.snapshot_bytes,
                timings: timing,
            });
            if audit_failed {
                report.unsafe_validation = true;
                report.stopped_reason = "unsafe-validation";
                report.incomplete_iteration = true;
                // These queued branches executed but were never demanded after
                // the fatal audit. Keep their work/copy/log costs visible.
                for abandoned in queue.drain(..) {
                    let nodes =
                        abandoned.final_state.stats.nodes - abandoned.branch.base_stats.nodes;
                    report.incomplete_nodes += nodes;
                    report.abandoned_nodes += nodes;
                    report.abandoned_candidates += 1;
                    report.timings.snapshot_ns += abandoned.snapshot_ns;
                    report.timings.speculation_ns += abandoned.speculation_ns;
                    report.timings.recording_ns += abandoned.log.recording_ns;
                }
                break;
            }
        }
        assert!(queue.is_empty());
        if report.unsafe_validation {
            break;
        }
        report.incomplete_iteration = sample < env.movements.len() - 1;
        if !report.incomplete_iteration {
            report.completed_depth = depth;
        }
        report.stopped_reason = if report.incomplete_iteration {
            "tail-candidate-cap"
        } else {
            "first-restricted-iteration-complete"
        };
        break;
    }
    if report.restricted_depth.is_none() {
        report.prefix_nodes = canonical.stats.nodes;
    }
    report.canonical_nodes = canonical.stats.nodes;
    report.controls = controls()?;
    report.elapsed_ns = started.elapsed().as_nanos();
    Ok(report)
}

fn add_timings(a: &mut Timings, b: &Timings) {
    a.prefix_ns += b.prefix_ns;
    a.snapshot_ns += b.snapshot_ns;
    a.speculation_ns += b.speculation_ns;
    a.recording_ns += b.recording_ns;
    a.request_validation_ns += b.request_validation_ns;
    a.staging_ns += b.staging_ns;
    a.replay_ns += b.replay_ns;
    a.commit_ns += b.commit_ns;
    a.comparison_ns += b.comparison_ns;
    a.oracle_ns += b.oracle_ns;
    a.oracle_snapshot_ns += b.oracle_snapshot_ns;
    a.fallback_ns += b.fallback_ns;
}

fn writes(event: &Event) -> bool {
    matches!(
        event,
        Event::TTStore { .. }
            | Event::LearningClearNext { .. }
            | Event::LearningRecord { .. }
            | Event::PawnSelect {
                expected: crate::pawn_structure::Selection { reused: false, .. },
                ..
            }
    )
}

/// Small machinery controls use a real ordinary branch (and its recursive Q
/// calls). The extra suffix probe deliberately supplies a dependency after the
/// branch's staged writes so rollback is exercised late in chronological replay.
pub fn controls() -> Result<Vec<ControlReport>, String> {
    let position = Position::from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")?;
    let mut entry = Search::<true>::new(&position);
    entry.config.tts_bytes = 65_536;
    entry.ensure_table()?;
    entry.bind_geometry_permission(&position);
    let (root, influence) = entry.prepare_root_with_influence(position);
    entry.begin_owned_sequence(Limits { nodes: None });
    let mut legal = MoveList::new();
    movegen::generate_legal(&position, &mut legal);
    let env = Environment {
        root,
        influence,
        checked: false,
        movements: legal.as_slice().to_vec(),
    };
    let pawn_id = env
        .movements
        .iter()
        .position(|movement| {
            position.board[movement.from().0 as usize].kind() == crate::types::PieceKind::Pawn
        })
        .ok_or("control fixture needs a pawn root")? as u16;
    let mut schedule = Iteration::new(
        vec![Row {
            id: pawn_id,
            score: 0,
            work: 0,
        }],
        0,
        0,
    );
    let attempt = schedule.next(0).unwrap();
    let history = SearchHistory::new(&position);
    let mut speculative = entry.research_clone();
    let sink = Sink::new(16_384);
    speculative.research_attach_sink(Some(sink.clone()));
    let mut task_history = history.clone();
    let branch = execute(
        &mut speculative,
        &mut task_history,
        &env,
        2,
        schedule.clone(),
        attempt,
    )?;
    let mut log = sink.take();
    if log.overflowed {
        return Err("control fixture exceeded event cap".into());
    }
    let mut touched = vec![false; entry.remembered.as_ref().unwrap().group_count()];
    for event in &log.events {
        match event {
            Event::TTProbe { query, .. } => touched[query.group] = true,
            Event::TTStore { store } => touched[store.query.group] = true,
            _ => (),
        }
    }
    let mut untouched = touched
        .iter()
        .enumerate()
        .filter_map(|(group, used)| (!used).then_some(group));
    let suffix_group = untouched
        .next()
        .ok_or("control fixture has no untouched TT group")?;
    let irrelevant_group = untouched
        .next()
        .ok_or("control fixture needs two untouched TT groups")?;
    let suffix = Query {
        group: suffix_group,
        identity: 0xc011_ab1e,
        ply: 1,
        target: 3,
        lower: -10_000,
        upper: 10_000,
    };
    // This is an actual native probe, recorded after all real branch writes.
    speculative.remembered.as_mut().unwrap().probe(suffix);
    let suffix_log = sink.take();
    log.recording_ns += suffix_log.recording_ns;
    log.attempted += suffix_log.attempted;
    log.events.extend(suffix_log.events);
    speculative.research_attach_sink(None);
    let nodes = speculative.stats.nodes;
    let task = Task {
        depth: 2,
        attempt,
        history: history.clone(),
        final_state: speculative,
        branch,
        log,
        ahead: 0,
        turn: 0,
        snapshot_bytes: 0,
        snapshot_ns: 0,
        speculation_ns: 0,
    };

    // Only change a pawn slot whose first recorded access is a miss. No earlier
    // operation is allowed to observe the deliberately changed victim payload.
    let mut seen_pawn = [false; 128];
    let pawn_miss = task
        .log
        .events
        .iter()
        .find_map(|event| {
            if let Event::PawnSelect { identity, expected } = event {
                let group = (*identity % 128) as usize;
                let first = !seen_pawn[group];
                seen_pawn[group] = true;
                if first && !expected.reused {
                    return Some((*identity, expected.structure));
                }
            }
            None
        })
        .ok_or("control fixture has no first-access pawn miss")?;
    let mut perturbed = entry.research_clone();
    perturbed.remembered.as_mut().unwrap().store(Store {
        query: Query {
            group: irrelevant_group,
            identity: 0xa11d_a11d,
            ..suffix
        },
        score: 317,
        move_hint: None,
        quiet_mate_checked: false,
        mark_depth: false,
    });
    let mut changed_payload = pawn_miss.1;
    changed_payload.base_score[0] ^= 0x55aa;
    perturbed
        .evaluator
        .research_pawns()
        .research_overwrite_slot(pawn_miss.0.wrapping_add(128), changed_payload);
    let mut stage = perturbed.research_clone();
    let replay_start = Instant::now();
    let result = replay(&task.log, &mut stage);
    let replay_ns = replay_start.elapsed().as_nanos();
    if result.accepted() {
        install_outputs(&mut stage, &task);
    }
    let mut fresh = perturbed.research_clone();
    let oracle_start = Instant::now();
    let fresh_branch = execute(
        &mut fresh,
        &mut history.clone(),
        &env,
        2,
        schedule.clone(),
        attempt,
    )?;
    fresh.remembered.as_mut().unwrap().probe(suffix);
    let oracle_ns = oracle_start.elapsed().as_nanos();
    let compare_start = Instant::now();
    let matches_fresh =
        result.accepted() && same_passes(&task.branch, &fresh_branch) && stage.research_eq(&fresh);
    let differs_speculative = !stage.research_eq(&task.final_state);
    let comparison_ns = compare_start.elapsed().as_nanos();
    let relaxed = ControlReport {
        name: "untouched-tt-and-pawn-miss-victim",
        accepted: result.accepted(),
        passed: matches_fresh && differs_speculative,
        rejection: result.rejection.map(|r| r.kind.name()),
        rejection_event: result.rejection.map(|r| r.event_index),
        events: task.log.events.len(),
        nodes,
        staged_writes_before_rejection: 0,
        canonical_unchanged: true,
        matches_fresh_canonical: matches_fresh,
        differs_from_speculative_final: differs_speculative,
        replay_ns,
        oracle_ns,
        comparison_ns,
    };

    // Change precisely the suffix observation's input. Replay must execute its
    // preceding writes privately, then reject without touching authoritative state.
    let mut late_entry = entry.research_clone();
    late_entry.remembered.as_mut().unwrap().store(Store {
        query: suffix,
        score: 777,
        move_hint: None,
        quiet_mate_checked: false,
        mark_depth: false,
    });
    let witness = late_entry.research_clone();
    let mut late_stage = late_entry.research_clone();
    let replay_start = Instant::now();
    let late_result = replay(&task.log, &mut late_stage);
    let late_replay_ns = replay_start.elapsed().as_nanos();
    let rejection_index = late_result.rejection.map(|reason| reason.event_index);
    let writes_before = rejection_index.map_or(0, |index| {
        task.log.events[..index]
            .iter()
            .filter(|event| writes(event))
            .count()
    });
    let compare_start = Instant::now();
    let unchanged = late_entry.research_eq(&witness);
    let private_writes = !late_stage.research_eq(&witness);
    let late_comparison_ns = compare_start.elapsed().as_nanos();
    let late = ControlReport {
        name: "late-probe-mismatch-rolls-back",
        accepted: late_result.accepted(),
        passed: !late_result.accepted()
            && rejection_index == Some(task.log.events.len() - 1)
            && writes_before > 0
            && private_writes
            && unchanged,
        rejection: late_result.rejection.map(|r| r.kind.name()),
        rejection_event: rejection_index,
        events: task.log.events.len(),
        nodes,
        staged_writes_before_rejection: writes_before,
        canonical_unchanged: unchanged,
        matches_fresh_canonical: false,
        differs_from_speculative_final: false,
        replay_ns: late_replay_ns,
        oracle_ns: 0,
        comparison_ns: late_comparison_ns,
    };
    let mut changed_request = attempt;
    changed_request.window[0] += 1;
    let request_witness = entry.research_clone();
    let request_accepted = request_matches(&task, 2, changed_request, &history);
    let request_unchanged = entry.research_eq(&request_witness);
    let mismatch = ControlReport {
        name: "changed-request-window",
        accepted: request_accepted,
        passed: !request_accepted && request_unchanged,
        rejection: Some("request-window"),
        rejection_event: None,
        events: 0,
        nodes,
        staged_writes_before_rejection: 0,
        canonical_unchanged: request_unchanged,
        matches_fresh_canonical: false,
        differs_from_speculative_final: false,
        replay_ns: 0,
        oracle_ns: 0,
        comparison_ns: 0,
    };
    Ok(vec![relaxed, late, mismatch])
}

fn option_str(value: Option<&str>) -> String {
    value.map_or_else(|| "null".into(), |value| format!("\"{value}\""))
}
fn option_number<T: std::fmt::Display>(value: Option<T>) -> String {
    value.map_or_else(|| "null".into(), |value| value.to_string())
}
fn timings_json(t: &Timings) -> String {
    format!(
        concat!(
            "{{\"prefix_ns\":{},\"snapshot_ns\":{},\"speculation_ns\":{},",
            "\"recording_ns\":{},\"request_validation_ns\":{},\"staging_ns\":{},",
            "\"replay_ns\":{},\"commit_ns\":{},\"comparison_ns\":{},\"oracle_ns\":{},",
            "\"oracle_snapshot_ns\":{},\"fallback_ns\":{}}}"
        ),
        t.prefix_ns,
        t.snapshot_ns,
        t.speculation_ns,
        t.recording_ns,
        t.request_validation_ns,
        t.staging_ns,
        t.replay_ns,
        t.commit_ns,
        t.comparison_ns,
        t.oracle_ns,
        t.oracle_snapshot_ns,
        t.fallback_ns
    )
}
impl Report {
    /// Numeric costs and static reason strings; this encoder adds no dependency
    /// or protocol recording to the production search.
    pub fn json(&self) -> String {
        let mut out = format!(concat!("{{\"caps\":{{\"max_depth\":{},\"max_tail_candidates\":{},",
            "\"queue_depth\":{},\"log_events\":{}}},\"zero_randomness\":{},\"restricted_depth\":{},",
            "\"restricted_entry_nodes\":{},\"completed_depth\":{},\"incomplete_iteration\":{},",
            "\"stopped_reason\":\"{}\",\"prefix_nodes\":{},\"canonical_nodes\":{},",
            "\"candidate_nodes\":{},\"accepted_nodes\":{},\"rejected_nodes\":{},",
            "\"incomplete_nodes\":{},\"unsafe_nodes\":{},\"unsafe_validation\":{},",
            "\"abandoned_nodes\":{},\"abandoned_candidates\":{},",
            "\"event_size_bytes\":{},\"oracle_nodes\":{},\"max_queue_len\":{},",
            "\"peak_queue_snapshot_bytes\":{},\"peak_queue_log_bytes\":{},\"elapsed_ns\":{},",
            "\"timings\":{},\"candidates\":["),
            self.caps.max_depth,self.caps.max_tail_candidates,self.caps.queue_depth,self.caps.log_events,
            self.zero_randomness,option_number(self.restricted_depth),option_number(self.restricted_entry_nodes),
            self.completed_depth,self.incomplete_iteration,self.stopped_reason,self.prefix_nodes,
            self.canonical_nodes,self.candidate_nodes,self.accepted_nodes,self.rejected_nodes,
            self.incomplete_nodes,self.unsafe_nodes,self.unsafe_validation,
            self.abandoned_nodes,self.abandoned_candidates,self.event_size_bytes,
            self.oracle_nodes,self.max_queue_len,self.peak_queue_snapshot_bytes,self.peak_queue_log_bytes,
            self.elapsed_ns,timings_json(&self.timings));
        for (index, c) in self.candidates.iter().enumerate() {
            if index != 0 {
                out.push(',');
            }
            write!(
                out,
                concat!(
                    "{{\"depth\":{},\"index\":{},\"id\":{},\"movement\":\"{}\",",
                    "\"ahead_distance\":{},\"enqueued_at_turn\":{},\"consumed_at_turn\":{},",
                    "\"speculative_nodes\":{},\"canonical_nodes\":{},\"accepted\":{},",
                    "\"semantic_accepted\":{},\"audit_failed\":{},\"rejection\":{},",
                    "\"rejection_event\":{},\"oracle_match\":{},\"rollback_unchanged\":{},",
                    "\"passes\":{},\"log_events\":{},\"log_attempted\":{},\"log_bytes\":{},",
                    "\"log_overflowed\":{},\"snapshot_bytes\":{},\"timings\":{}}}"
                ),
                c.depth,
                c.index,
                c.id,
                c.movement,
                c.ahead_distance,
                c.enqueued_at_turn,
                c.consumed_at_turn,
                c.speculative_nodes,
                c.canonical_nodes,
                c.accepted,
                c.semantic_accepted,
                c.audit_failed,
                option_str(c.rejection),
                option_number(c.rejection_event),
                c.oracle_match,
                c.rollback_unchanged,
                c.passes,
                c.log_events,
                c.log_attempted,
                c.log_bytes,
                c.log_overflowed,
                c.snapshot_bytes,
                timings_json(&c.timings)
            )
            .unwrap();
        }
        out.push_str("],\"controls\":[");
        for (index, c) in self.controls.iter().enumerate() {
            if index != 0 {
                out.push(',');
            }
            write!(out, concat!("{{\"name\":\"{}\",\"accepted\":{},\"passed\":{},\"rejection\":{},",
                "\"rejection_event\":{},\"events\":{},\"nodes\":{},\"staged_writes_before_rejection\":{},",
                "\"canonical_unchanged\":{},\"matches_fresh_canonical\":{},",
                "\"differs_from_speculative_final\":{},\"replay_ns\":{},\"oracle_ns\":{},",
                "\"comparison_ns\":{}}}"),c.name,c.accepted,c.passed,option_str(c.rejection),
                option_number(c.rejection_event),c.events,c.nodes,c.staged_writes_before_rejection,
                c.canonical_unchanged,c.matches_fresh_canonical,c.differs_from_speculative_final,
                c.replay_ns,c.oracle_ns,c.comparison_ns).unwrap();
        }
        out.push_str("]}");
        out
    }
}

#[cfg(test)]
mod focused_tests {
    #[test]
    fn semantic_replay_and_late_rollback_controls() {
        let rows=super::controls().expect("controls execute");
        assert!(rows.iter().all(|row| row.passed), "{rows:#?}");
        assert!(rows.iter().any(|row| row.accepted && row.nodes>1 && row.differs_from_speculative_final));
        assert!(rows.iter().any(|row| !row.accepted && row.staged_writes_before_rejection>0 && row.canonical_unchanged));
    }
}
