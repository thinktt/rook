//! Bounded semantic operation journal for serial branch-transaction research.
//!
//! The enclosing driver owns request/demand validation and the canonical state.
//! Replay uses a detached staging copy and the original native operations. Its
//! writes are publishable only after every observation and the independent
//! canonical branch comparison succeed. Speculative final bytes are never used.

use std::cell::RefCell;
use std::rc::Rc;
use std::time::Instant;

use crate::evaluation::RootContext;
use crate::influence::Influence;
use crate::movegen::{MoveList, MOVE_CAPACITY};
use crate::ordinary_policy::{self, Learning};
use crate::pawn_structure::{PawnCache, Selection};
use crate::position::Position;
use crate::remembered::{ProbeResult, Query, RememberedTable, Store};
use crate::tactical::{self, OrderingScratch};
use crate::types::Move;

#[derive(Clone, Debug)]
pub(crate) enum Event {
    TTProbe { query: Query, expected: ProbeResult },
    TTStore { store: Store },
    PawnSelect { identity: u32, expected: Selection },
    LearningClearNext { ply: usize },
    LearningRecord { position: Position, ply: usize, depth: i32, movement: Option<Move> },
    OrderMain {
        position: Position,
        influence: Influence,
        ply: usize,
        preferred: Option<Move>,
        input: Vec<Move>,
        expected: Vec<Move>,
    },
    OrderQ { position: Position, input: Vec<Move>, expected: Vec<Move> },
}

impl Event {
    fn allocation_bytes(&self) -> usize {
        match self {
            Self::OrderMain { input, expected, .. } | Self::OrderQ { input, expected, .. } => {
                (input.capacity() + expected.capacity()) * std::mem::size_of::<Move>()
            }
            _ => 0,
        }
    }
}

#[derive(Clone, Debug)]
pub(crate) struct Log {
    pub events: Vec<Event>,
    pub overflowed: bool,
    pub attempted: usize,
    /// Time inside Sink::record, including append/growth and capped attempts;
    /// event construction and cloning at the native call sites are excluded.
    pub recording_ns: u128,
    cap: usize,
}

impl Log {
    pub(crate) fn new(cap: usize) -> Self {
        Self { events: Vec::new(), overflowed: false, attempted: 0, recording_ns: 0, cap }
    }

    pub(crate) fn estimated_bytes(&self) -> usize {
        std::mem::size_of::<Self>()
            + self.events.capacity() * std::mem::size_of::<Event>()
            + self.events.iter().map(Event::allocation_bytes).sum::<usize>()
    }

    /// Replays into staging only. Sinks are detached before native calls so
    /// recording cannot recursively append or borrow this journal.
    pub(crate) fn replay(
        &self,
        root: &RootContext,
        table: &mut RememberedTable,
        learning: &mut Learning,
        pawns: &mut PawnCache,
    ) -> ReplayResult {
        table.attach_sink(None);
        learning.attach_sink(None);
        pawns.attach_sink(None);
        let mut result = ReplayResult::default();
        if self.overflowed {
            result.rejection = Some(Rejection {
                event_index: self.events.len(), kind: RejectionKind::Overflow,
            });
            return result;
        }
        let mut scratch = OrderingScratch::new();
        for (event_index, event) in self.events.iter().enumerate() {
            let rejection = match event {
                Event::TTProbe { query, expected } => {
                    result.counts.tt_probes += 1;
                    (table.probe(*query) != *expected).then_some(RejectionKind::TTProbe)
                }
                Event::TTStore { store } => {
                    result.counts.tt_stores += 1;
                    table.store(*store);
                    None
                }
                Event::PawnSelect { identity, expected } => {
                    result.counts.pawn_selects += 1;
                    (pawns.research_replay_select(*identity, *expected) != *expected)
                        .then_some(RejectionKind::PawnSelect)
                }
                Event::LearningClearNext { ply } => {
                    result.counts.learning_clears += 1;
                    learning.clear_next(*ply);
                    None
                }
                Event::LearningRecord { position, ply, depth, movement } => {
                    result.counts.learning_records += 1;
                    learning.record(position, *ply, *depth, *movement);
                    None
                }
                Event::OrderMain { position, influence, ply, preferred, input, expected } => {
                    result.counts.order_main += 1;
                    if let Some(mut list) = inventory(input, expected) {
                        tactical::order_by(&mut list, &mut scratch, |movement| {
                            ordinary_policy::priority(
                                position, root, influence, learning, *ply, *preferred, movement,
                            )
                        });
                        (list.as_slice() != expected.as_slice()).then_some(RejectionKind::OrderMain)
                    } else {
                        Some(RejectionKind::InvalidInventory)
                    }
                }
                Event::OrderQ { position, input, expected } => {
                    result.counts.order_q += 1;
                    if let Some(mut list) = inventory(input, expected) {
                        tactical::order_with_scratch(
                            position, root, &learning.history, &mut list, &mut scratch,
                        );
                        (list.as_slice() != expected.as_slice()).then_some(RejectionKind::OrderQ)
                    } else {
                        Some(RejectionKind::InvalidInventory)
                    }
                }
            };
            if let Some(kind) = rejection {
                result.rejection = Some(Rejection { event_index, kind });
                break;
            }
        }
        result
    }
}

fn inventory(input: &[Move], expected: &[Move]) -> Option<MoveList> {
    if input.len() > MOVE_CAPACITY || input.len() != expected.len() {
        return None;
    }
    let mut list = MoveList::new();
    list.moves[..input.len()].copy_from_slice(input);
    list.len = input.len();
    Some(list)
}

/// Shared only inside the serial simulation. This deliberately is not Send:
/// an actual multiworker executor is outside the experiment's scope.
#[derive(Clone, Debug)]
pub(crate) struct Sink(Rc<RefCell<Log>>);

impl Sink {
    pub(crate) fn new(cap: usize) -> Self {
        Self(Rc::new(RefCell::new(Log::new(cap))))
    }

    pub(crate) fn record(&self, event: Event) {
        let started = Instant::now();
        let mut log = self.0.borrow_mut();
        log.attempted = log.attempted.saturating_add(1);
        if log.events.len() == log.cap {
            log.overflowed = true;
        } else {
            // Vec's geometric reserve may exceed a small explicit cap. Grow
            // by an exact bounded request instead of the default growth rule.
            if log.events.len() == log.events.capacity() {
                let capacity = log.events.capacity().max(4).saturating_mul(2).min(log.cap);
                let additional = capacity - log.events.len();
                log.events.reserve_exact(additional);
            }
            log.events.push(event);
        }
        log.recording_ns = log.recording_ns.saturating_add(started.elapsed().as_nanos());
    }

    /// Moves the allocation out even while storage objects retain Sink clones.
    /// Subsequent operations start an empty journal with the same explicit cap.
    pub(crate) fn take(&self) -> Log {
        let mut log = self.0.borrow_mut();
        let cap = log.cap;
        std::mem::replace(&mut *log, Log::new(cap))
    }

    pub(crate) fn finish(&self) -> Log {
        self.take()
    }

    pub(crate) fn estimated_bytes(&self) -> usize {
        self.0.borrow().estimated_bytes()
            + 2 * std::mem::size_of::<usize>() // Rc strong/weak counters.
            + std::mem::size_of::<isize>() // RefCell borrow flag.
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub(crate) struct OperationCounts {
    pub tt_probes: usize,
    pub tt_stores: usize,
    pub pawn_selects: usize,
    pub learning_clears: usize,
    pub learning_records: usize,
    pub order_main: usize,
    pub order_q: usize,
}

impl OperationCounts {
    pub(crate) fn total(self) -> usize {
        self.tt_probes + self.tt_stores + self.pawn_selects + self.learning_clears
            + self.learning_records + self.order_main + self.order_q
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum RejectionKind {
    Overflow,
    TTProbe,
    PawnSelect,
    OrderMain,
    OrderQ,
    InvalidInventory,
}

impl RejectionKind {
    pub(crate) fn name(self) -> &'static str {
        match self {
            Self::Overflow => "log-overflow",
            Self::TTProbe => "tt-probe",
            Self::PawnSelect => "pawn-selection",
            Self::OrderMain => "ordinary-order",
            Self::OrderQ => "quiescence-order",
            Self::InvalidInventory => "invalid-inventory",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct Rejection {
    pub event_index: usize,
    pub kind: RejectionKind,
}

#[derive(Clone, Debug, Default)]
pub(crate) struct ReplayResult {
    pub rejection: Option<Rejection>,
    pub counts: OperationCounts,
}

impl ReplayResult {
    pub(crate) fn accepted(&self) -> bool {
        self.rejection.is_none()
    }
}
