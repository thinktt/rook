//! Partial composed evaluator with the production state lifetimes.
//!
//! Implemented components are real spec formulas. Progress/races, central and
//! board patterns, personality configuration and late-endgame adjustment remain
//! absent; this module must not be presented as complete KingRE evaluation.

use crate::evaluation::RootContext;
use crate::influence::Influence;
use crate::pawn_structure::PawnCache;
use crate::position::Position;
use crate::types::{Color, Move, MoveKind, Piece, PieceKind, Square};
use crate::{activity, pawn_terms, shelter};

pub const OMITTED_TERMS: &str = "pawn progress/races/endings; central influence; bishop coordination/opening patterns; nonneutral personality; late-endgame adjustment/bounds";

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
    /// Bounds below the late threshold are specified. Later geometry is pending.
    pub late_endgame_pending: bool,
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

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Selection {
    pub evaluation: Evaluation,
    pub initially_full: bool,
    pub fast_score: Option<i32>,
    pub refreshed: bool,
}

pub struct Evaluator<const DIAGNOSTICS: bool = true> {
    pub root: RootContext,
    pawns: PawnCache,
    pub stats: EvalStats,
}

impl<const DIAGNOSTICS: bool> Evaluator<DIAGNOSTICS> {
    pub fn new(position: &Position) -> Self {
        Self {
            root: RootContext::neutral(position),
            pawns: PawnCache::new(),
            stats: EvalStats::default(),
        }
    }

    pub fn begin_search(&mut self, position: &Position) {
        self.root = RootContext::neutral(position);
        self.pawns.clear();
        self.stats = EvalStats::default();
    }

    pub fn ensure_influence<'a>(
        &mut self,
        position: &Position,
        scratch: &'a mut Option<Influence>,
    ) -> &'a Influence {
        if scratch.is_none() {
            *scratch = Some(Influence::build(position));
            if DIAGNOSTICS {
                self.stats.influence_builds += 1;
            }
        }
        scratch.as_ref().unwrap()
    }

    pub fn full(&mut self, node: &mut Node, influence: &Influence, in_check: bool) -> Evaluation {
        let position = &node.position;
        let phase = position.phase();
        let material = self.root.material(position);
        let selected = self.pawns.select(position, influence);
        let pawn = pawn_terms::compute(position, influence, &selected.structure);
        let activity = activity::compute(position, influence, material, [1024; 2]);
        let shelter = shelter::compute(position, influence, activity.pressure, material, [1024; 2]);
        // Neutral structure weights are both1024; keep the two separate rounds.
        let structural = ((pawn.structure[0] - pawn.piece[1]) as i64 * 1024
            - (pawn.structure[1] - pawn.piece[0]) as i64 * 1024
            + 512)
            .div_euclid(1024);
        let structure = (structural
            * (13 * phase.opening as i64
                + 14 * phase.middlegame as i64
                + 19 * phase.endgame as i64)
            + 2048)
            .div_euclid(4096) as i32;
        let positional = structure + activity.weighted + shelter.weighted;
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
        node.retained.positional = positional;
        node.retained.pawn_progress = 0; // Explicit missing progress producer.
        node.retained.age = 0;
        let base = material
            + self
                .root
                .square_balance_from(position, node.retained.nonking_squares)
            + positional
            + tempo;
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
        finish_partial(position, base, queries)
    }

    pub fn fast(&mut self, node: &Node, in_check: bool) -> Evaluation {
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
        finish_partial(position, base, 0)
    }

    /// The specified selection predicates applied to this explicitly partial
    /// score producer. Missing terms can change F and therefore the chosen tree.
    pub fn select_noncheck(
        &mut self,
        node: &mut Node,
        lower: i32,
        upper: i32,
        capture_exception: bool,
        scratch: &mut Option<Influence>,
    ) -> Selection {
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
            let influence = self.ensure_influence(&node.position, scratch);
            return Selection {
                evaluation: self.full(node, influence, false),
                initially_full: true,
                fast_score: None,
                refreshed: false,
            };
        }
        let fast = self.fast(node, false);
        let refresh = capture_exception || (lower - 250 < fast.score && fast.score < upper + 250);
        let evaluation = if refresh {
            let influence = self.ensure_influence(&node.position, scratch);
            self.full(node, influence, false)
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

/// Ordinary finishing is real; late endgame geometry is explicitly pending.
fn finish_partial(position: &Position, base: i32, queries: u64) -> Evaluation {
    let clipped = base.clamp(-7900, 7900);
    let h = position.halfmove as i64;
    let white = if h <= 11 {
        clipped
    } else {
        ((23 * (100 - h)).max(0) * clipped as i64 + 1024).div_euclid(2048) as i32
    };
    Evaluation {
        score: if position.side == Color::White {
            white
        } else {
            -white
        },
        lower: -10000,
        upper: 10000,
        relation_queries: queries,
        late_endgame_pending: position.phase().endgame >= 192,
    }
}

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
        assert_eq!(std::mem::size_of::<Node>(), 144);
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
        assert!(selected.evaluation.late_endgame_pending);
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
}
