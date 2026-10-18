//! Integrated development traversal. This is not the KingRE search policy.

use crate::activity;
use crate::evaluation::RootContext;
use crate::influence::Influence;
use crate::movegen::{generate_legal, in_check, MoveList};
use crate::position::Position;
use crate::types::{Color, Move};

pub const SEARCH_FIDELITY: &str = "material-square-activity-alpha-beta-v1";
pub const SEARCH_OMISSIONS: &str = "pawn/shelter/central/pattern/endgame/final-score terms; full-fast selection and pawn retention; quiescence; KingRE ranking/windows/extensions/pruning/IIO/TT/repetition; personality/timed stopping and semantic work clock";
const PLIES: usize = 64;

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct SearchStats {
    pub nodes: u64,
    pub leaf_evaluations: u64,
    pub generated_legal_moves: u64,
    pub searched_children: u64,
    pub cutoffs: u64,
    pub influence_builds: u64,
    pub activity_evaluations: u64,
    pub activity_relation_queries: u64,
}

pub struct SearchResult {
    pub score: i32,
    pub pv: Vec<Move>,
    pub stats: SearchStats,
}

pub struct Search {
    context: RootContext,
    candidates: Box<[MoveList]>,
    pv: [[Move; PLIES]; PLIES],
    pv_len: [usize; PLIES],
    stats: SearchStats,
}

impl Search {
    pub fn new(root: &Position) -> Self {
        Self {
            context: RootContext::neutral(root),
            candidates: (0..PLIES).map(|_| MoveList::new()).collect(),
            pv: [[Move::NONE; PLIES]; PLIES],
            pv_len: [0; PLIES],
            stats: SearchStats::default(),
        }
    }

    pub fn run(&mut self, position: &Position, depth: u8) -> SearchResult {
        assert!(
            (1..=8).contains(&depth),
            "development search depth must be 1..8"
        );
        self.stats = SearchStats::default();
        self.pv_len.fill(0);
        let score = self.visit(position, depth, 0, -30000, 30000);
        SearchResult {
            score,
            pv: self.pv[0][..self.pv_len[0]].to_vec(),
            stats: self.stats,
        }
    }

    fn visit(
        &mut self,
        position: &Position,
        depth: u8,
        ply: usize,
        mut lower: i32,
        upper: i32,
    ) -> i32 {
        self.stats.nodes += 1;
        self.pv_len[ply] = 0;
        if depth == 0 {
            self.stats.leaf_evaluations += 1;
            let material = self.context.material(position);
            let influence = Influence::build(position);
            self.stats.influence_builds += 1;
            let activity = activity::compute(position, &influence, material, [1024; 2]);
            self.stats.activity_evaluations += 1;
            self.stats.activity_relation_queries += activity.relation_queries;
            let phase = position.phase();
            let tempo = if in_check(position, position.side) {
                0
            } else {
                let moving_activity = activity.pieces[position.side.index()] as i64;
                let magnitude = ((moving_activity + 140)
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
            let white =
                material + self.context.square_balance(position) + activity.weighted + tempo;
            return if position.side == Color::White {
                white
            } else {
                -white
            };
        }
        generate_legal(position, &mut self.candidates[ply]);
        let count = self.candidates[ply].len;
        self.stats.generated_legal_moves += count as u64;
        if count == 0 {
            return if in_check(position, position.side) {
                ply as i32 - 10000
            } else {
                0
            };
        }
        let mut best = -30000;
        for index in 0..count {
            let movement = self.candidates[ply].moves[index];
            let child = position.played_unchecked(movement);
            self.stats.searched_children += 1;
            let score = -self.visit(&child, depth - 1, ply + 1, -upper, -lower);
            if score > best {
                best = score;
                self.pv[ply][0] = movement;
                let child_len = self.pv_len[ply + 1];
                let (parents, children) = self.pv.split_at_mut(ply + 1);
                parents[ply][1..1 + child_len].copy_from_slice(&children[0][..child_len]);
                self.pv_len[ply] = child_len + 1;
            }
            lower = lower.max(score);
            if lower >= upper {
                self.stats.cutoffs += 1;
                break;
            }
        }
        best
    }
}

pub fn perft(position: &Position, depth: u8) -> u64 {
    assert!(depth <= 8, "development perft depth must be at most eight");
    let mut candidates: Vec<MoveList> = (0..=depth).map(|_| MoveList::new()).collect();
    fn walk(position: &Position, depth: u8, ply: usize, lists: &mut [MoveList]) -> u64 {
        if depth == 0 {
            return 1;
        }
        generate_legal(position, &mut lists[ply]);
        let count = lists[ply].len;
        if depth == 1 {
            return count as u64;
        }
        let mut total = 0;
        for index in 0..count {
            let child = position.played_unchecked(lists[ply].moves[index]);
            total += walk(&child, depth - 1, ply + 1, lists);
        }
        total
    }
    walk(position, depth, 0, &mut candidates)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn repeated_search_restores_root_and_recomputes_invocation_state() {
        let position =
            Position::from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
        let saved = position;
        let mut search = Search::new(&position);
        let a = search.run(&position, 3);
        let b = search.run(&position, 3);
        assert_eq!((a.score, &a.pv, a.stats), (b.score, &b.pv, b.stats));
        assert_eq!(position, saved);
        let mut current = position;
        for movement in a.pv {
            let mut legal = MoveList::new();
            generate_legal(&current, &mut legal);
            assert!(legal.as_slice().contains(&movement));
            current = current.played_unchecked(movement);
            current.validate().unwrap();
        }
        assert_eq!(a.stats.nodes, a.stats.searched_children + 1);
        assert!(a.stats.leaf_evaluations > 0);
    }
}
