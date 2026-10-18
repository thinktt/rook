//! Composed root-bound evaluation with retained full/fast state.
//! Component correctness and complete engine qualification remain separate.

use crate::evaluation::RootContext;
use crate::influence::Influence;
use crate::pawn_structure::{self, PawnCache};
use crate::position::Position;
use crate::types::{Color, Move, MoveKind, Piece, PieceKind, Square};
use crate::{activity, endgame, pawn_progress, pawn_terms, positional_terms, shelter};

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
        let d = 100 - self.opponent_selectivity;
        let range = d * d * d / 200 + 3 * d;
        (root, weights, draw, range as u32)
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

pub struct Evaluator<const DIAGNOSTICS: bool = true> {
    pub root: RootContext,
    pub parameters: Parameters,
    pub draw_preference: i32,
    pub variation_range: u32,
    weights: Weights,
    pawns: PawnCache,
    pub stats: EvalStats,
}

impl<const DIAGNOSTICS: bool> Evaluator<DIAGNOSTICS> {
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
            stats: EvalStats::default(),
        }
    }
    pub fn begin_search(&mut self, position: &Position) {
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
        if scratch.is_none() {
            *scratch = Some(Influence::build(position));
            if DIAGNOSTICS {
                self.stats.influence_builds += 1;
            }
        }
        scratch.as_ref().unwrap()
    }

    pub fn full(&mut self, node: &mut Node, influence: &Influence, in_check: bool) -> Evaluation {
        self.full_impl::<false, _>(node, influence, in_check, |_| {})
    }
    /// Cold component observation; the default monomorph has a zero-sized no-op observer.
    pub fn full_observed<F: FnOnce(Components)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.full_impl::<false, _>(node, influence, in_check, observer)
    }
    pub fn fresh_observed<F: FnOnce(Components)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        self.full_impl::<true, _>(node, influence, in_check, observer)
    }
    fn full_impl<const FRESH: bool, F: FnOnce(Components)>(
        &mut self,
        node: &mut Node,
        influence: &Influence,
        in_check: bool,
        observer: F,
    ) -> Evaluation {
        let position = &node.position;
        let phase = position.phase();
        let material = self.root.material(position);
        let selected = if FRESH {
            pawn_structure::Selection {
                structure: pawn_structure::fresh(position, influence, [1024; 2]),
                reused: false,
            }
        } else {
            self.pawns.select(position, influence)
        };
        let pawn = pawn_terms::compute(position, influence, &selected.structure);
        let activity = activity::compute(position, influence, material, self.weights.mobility);
        let shelter = shelter::compute(
            position,
            influence,
            activity.pressure,
            material,
            self.weights.shelter,
        );
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
            squares: self
                .root
                .square_balance_from(position, node.retained.nonking_squares),
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
        self.finish(position, components.base(), in_check, progress, queries)
    }
    fn finish(
        &self,
        position: &Position,
        base: i32,
        checked: bool,
        progress: i32,
        queries: u64,
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
        Evaluation {
            score: value.score,
            lower: value.lower,
            upper: value.upper,
            relation_queries: queries,
            late_endgame_applied: position.phase().endgame >= 192,
        }
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
        self.finish(position, base, in_check, node.retained.pawn_progress, 0)
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
}
