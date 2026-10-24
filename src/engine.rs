//! Search-wide ownership shared by ordinary and tactical recursion.
use crate::evaluator::Evaluator;
use crate::history::SearchHistory;
use crate::host::{Host, NoHost};
use crate::movegen::{MoveList, MOVE_CAPACITY};
use crate::ordinary_policy::Learning;
use crate::position::Position;
use crate::quiescence::{Limits, Outcome, Stats, Stopped, Work};
use crate::remembered::RememberedTable;
use crate::tactical::OrderingScratch;
use crate::types::Move;

pub(crate) const PLIES: usize = 64;

#[derive(Clone, Copy, Debug)]
pub struct Config {
    pub selectivity: i32,
    pub maximum_depth: usize,
    pub analysis: i32,
    pub tts_bytes: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            selectivity: 14,
            maximum_depth: 99,
            analysis: 0,
            tts_bytes: 67_108_864,
        }
    }
}

pub struct Search<const DIAGNOSTICS: bool = true, H: Host = NoHost> {
    pub evaluator: Evaluator<DIAGNOSTICS>,
    pub config: Config,
    pub(crate) candidates: Box<[MoveList]>,
    pub(crate) extension_flags: Box<[[u8; MOVE_CAPACITY]]>,
    pub(crate) ordering: OrderingScratch,
    pub(crate) learning: Learning,
    pub(crate) remembered: Option<RememberedTable>,
    table_bytes: usize,
    // Valid only inside a guarded owned-root call; never a Node certificate.
    coherent_geometry: bool,
    pub(crate) pv: [[Move; PLIES]; PLIES],
    pub(crate) pv_len: [usize; PLIES],
    pub(crate) stats: Stats,
    pub(crate) limits: Limits,
    pub(crate) timing: Option<crate::timed::Clock>,
    pub(crate) host: H,
    pub(crate) control: Option<crate::host::Control>,
}

impl<const DIAGNOSTICS: bool> Search<DIAGNOSTICS, NoHost> {
    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_clone(&self) -> Self {
        assert!(self.timing.is_none() && self.limits.nodes.is_none() && self.control.is_none());
        Self {
            evaluator: self.evaluator.research_clone(),
            config: self.config,
            candidates: self.candidates.clone(),
            extension_flags: self.extension_flags.clone(),
            // Sorting writes its scratch before reading it. It is not shared
            // search state and need not preserve unused bytes from an earlier call.
            ordering: OrderingScratch::new(),
            learning: self.learning.research_clone(),
            remembered: self
                .remembered
                .as_ref()
                .map(RememberedTable::research_clone),
            table_bytes: self.table_bytes,
            coherent_geometry: self.coherent_geometry,
            pv: self.pv,
            pv_len: self.pv_len,
            stats: self.stats,
            limits: self.limits,
            timing: None,
            host: NoHost,
            control: None,
        }
    }

    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_attach_sink(&mut self, sink: Option<crate::branch_journal::Sink>) {
        assert!(sink.is_none() || self.evaluator.research_journal_compatible(),
            "cannot attach a serial journal while the pawn helper owns its cache");
        self.learning.attach_sink(sink.clone());
        self.evaluator.research_attach_sink(sink.clone());
        if let Some(table) = &mut self.remembered {
            table.attach_sink(sink);
        }
    }

    /// Relevant persistent state and the selected root child's output PV.
    /// Deeper PV rows, generated lists and extension/ordering arrays are private
    /// recursive scratch: a fresh entry initializes them before consumption.
    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_eq(&self, other: &Self) -> bool {
        self.stats == other.stats
            && self.evaluator.research_eq(&other.evaluator)
            && self.learning.research_eq(&other.learning)
            && (match (&self.remembered, &other.remembered) {
                (Some(a), Some(b)) => a.research_eq(b),
                (None, None) => true,
                _ => false,
            })
            && self.pv[1][..self.pv_len[1]] == other.pv[1][..other.pv_len[1]]
    }

    #[cfg(feature = "branch-transactions")]
    pub(crate) fn research_bytes(&self) -> usize {
        // Embedded evaluator, pawn and learning storage are already in Self.
        std::mem::size_of::<Self>()
            + self.candidates.len() * std::mem::size_of::<MoveList>()
            + self.extension_flags.len() * std::mem::size_of::<[u8; MOVE_CAPACITY]>()
            + self
                .remembered
                .as_ref()
                .map_or(0, |table| table.research_bytes() - std::mem::size_of::<RememberedTable>())
    }

    pub fn new(root: &Position) -> Self {
        Self {
            evaluator: Evaluator::new(root),
            config: Config::default(),
            candidates: (0..PLIES).map(|_| MoveList::new()).collect(),
            extension_flags: vec![[0; MOVE_CAPACITY]; PLIES].into_boxed_slice(),
            ordering: OrderingScratch::new(),
            learning: Learning::default(),
            remembered: None,
            table_bytes: 0,
            coherent_geometry: false,
            pv: [[Move::NONE; PLIES]; PLIES],
            pv_len: [0; PLIES],
            stats: Stats::default(),
            limits: Limits::default(),
            timing: None,
            host: NoHost,
            control: None,
        }
    }
}

impl<const DIAGNOSTICS: bool, H: Host> Search<DIAGNOSTICS, H> {
    /// Transfer reusable storage; changing a host neither clones nor allocates search buffers.
    pub fn map_host<N: Host>(self, host: N) -> (Search<DIAGNOSTICS, N>, H) {
        let Self {
            evaluator,
            config,
            candidates,
            extension_flags,
            ordering,
            learning,
            remembered,
            table_bytes,
            coherent_geometry: _,
            pv,
            pv_len,
            stats,
            limits,
            timing,
            host: previous,
            control,
        } = self;
        (
            Search {
                evaluator,
                config,
                candidates,
                extension_flags,
                ordering,
                learning,
                remembered,
                table_bytes,
                coherent_geometry: false,
                pv,
                pv_len,
                stats,
                limits,
                timing,
                host,
                control,
            },
            previous,
        )
    }

    pub(crate) fn clear_geometry_permission(&mut self) {
        self.coherent_geometry = false;
    }

    pub(crate) fn bind_geometry_permission(&mut self, position: &Position) {
        self.coherent_geometry = position.validate().is_ok();
    }

    #[inline]
    pub(crate) fn geometry_permission(&self) -> bool {
        self.coherent_geometry
    }

    pub(crate) fn ensure_table(&mut self) -> Result<(), String> {
        if self.remembered.is_none() || self.table_bytes != self.config.tts_bytes {
            self.remembered = Some(RememberedTable::from_tts(self.config.tts_bytes)?);
            self.table_bytes = self.config.tts_bytes;
        }
        Ok(())
    }

    pub fn work(&self) -> Work {
        Work {
            charged_search_units: self.stats.nodes,
            charged_relation_queries: self.evaluator.stats.relation_queries,
        }
    }

    pub(crate) fn charge_node(&mut self, history: &SearchHistory) -> Result<(), Stopped> {
        if crate::work_clock::charge_search_unit(&mut self.stats.nodes,self.limits.nodes)? {
            let work = self.work();
            self.work_poll(history, work)?;
        }
        Ok(())
    }

    pub(crate) fn outcome(&self, ply: usize, score: i32) -> Outcome {
        Outcome {
            score,
            pv: self.pv[ply][..self.pv_len[ply]].to_vec(),
            work: self.work(),
            stats: self.stats,
            evaluations: self.evaluator.stats,
        }
    }

    pub(crate) fn replace_pv(&mut self, ply: usize, movement: Move) {
        let child_len = self.pv_len[ply + 1];
        let (parents, children) = self.pv.split_at_mut(ply + 1);
        parents[ply][0] = movement;
        parents[ply][1..1 + child_len].copy_from_slice(&children[0][..child_len]);
        self.pv_len[ply] = child_len + 1;
    }
}

#[cfg(test)]
#[path = "engine/geometry_tests.rs"]
mod geometry_tests;
