//! One pawn FULL numerical branch, shared by inline and helper ownership.

use crate::influence::Influence;
use crate::pawn_structure::{self, PawnCache, PawnCacheCore, Selection};
use crate::position::{Phase, Position};
use crate::{pawn_progress, pawn_terms};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct PawnBranchResult {
    pub structure: i32,
    pub progress: i32,
    pub relation_queries: u64,
    pub reused: bool,
}

pub(crate) fn compute<const FRESH: bool>(
    cache: &mut PawnCache, position: &Position, influence: &Influence,
    phase: Phase, material: i32, structure_weights: [i32; 2], progress_weights: [i32; 2],
) -> PawnBranchResult {
    let selected = if FRESH {
        Selection { structure: pawn_structure::fresh(position, influence, [1024; 2]), reused: false }
    } else {
        cache.select(position, influence)
    };
    finish(position, influence, selected, phase, material, structure_weights, progress_weights)
}

pub(crate) fn compute_core<const FRESH: bool>(
    cache: &mut PawnCacheCore, position: &Position, influence: &Influence,
    phase: Phase, material: i32, structure_weights: [i32; 2], progress_weights: [i32; 2],
) -> PawnBranchResult {
    let selected = if FRESH {
        Selection { structure: pawn_structure::fresh(position, influence, [1024; 2]), reused: false }
    } else {
        cache.select(position, influence)
    };
    finish(position, influence, selected, phase, material, structure_weights, progress_weights)
}

#[inline]
fn finish(
    position: &Position, influence: &Influence, selected: Selection,
    phase: Phase, material: i32, structure_weights: [i32; 2], progress_weights: [i32; 2],
) -> PawnBranchResult {
    let pawn = pawn_terms::compute(position, influence, &selected.structure);
    let structure = pawn_progress::structure_weighted(
        phase, pawn.structure, pawn.piece, structure_weights,
    );
    let progress = if phase.middlegame == 0 && phase.endgame == 0 {
        0
    } else {
        pawn_progress::selected(
            position, influence, &selected.structure, phase, material, progress_weights,
        ).weighted
    };
    PawnBranchResult { structure, progress, relation_queries: pawn.relation_queries, reused: selected.reused }
}
