//! Search-wide ownership shared by ordinary and tactical recursion.
use crate::evaluator::Evaluator;
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

pub struct Search<const DIAGNOSTICS: bool = true> {
    pub evaluator: Evaluator<DIAGNOSTICS>,
    pub config: Config,
    pub(crate) candidates: Box<[MoveList]>,
    pub(crate) extension_flags: Box<[[u8; MOVE_CAPACITY]]>,
    pub(crate) ordering: OrderingScratch,
    pub(crate) learning: Learning,
    pub(crate) remembered: Option<RememberedTable>,
    table_bytes: usize,
    pub(crate) pv: [[Move; PLIES]; PLIES],
    pub(crate) pv_len: [usize; PLIES],
    pub(crate) stats: Stats,
    pub(crate) limits: Limits,
}

impl<const DIAGNOSTICS: bool> Search<DIAGNOSTICS> {
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
            pv: [[Move::NONE; PLIES]; PLIES],
            pv_len: [0; PLIES],
            stats: Stats::default(),
            limits: Limits::default(),
        }
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

    pub(crate) fn charge_node(&mut self) -> Result<(), Stopped> {
        if let Some(limit) = self.limits.nodes {
            if self.stats.nodes >= limit {
                return Err(Stopped::NodeLimit(limit));
            }
        }
        self.stats.nodes += 1;
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
