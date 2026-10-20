//! Shared cold evaluation admission and native-value record formatting.
use super::{integer, object, pawn_progress, scores, Result};
use rook2::{
    endgame::Finished,
    evaluator::{Evaluator, Parameters, Retained},
    position::Position,
    types::{Color, PieceKind},
};
use serde_json::{json, Value};

pub(super) fn apply_pawn_order(position: &mut Position, value: &Value) -> Result<()> {
    let order = pawn_progress::candidates(position, value)?;
    for side in [Color::White, Color::Black] {
        let index = side.index();
        if order[index].len() != position.counts[index][PieceKind::Pawn.index()] as usize {
            return Err("pawn order must contain every current pawn exactly once".into());
        }
    }
    // Native Position groups P,N,B,R,Q,K. Only the validated current pawn
    // chronology changes: board, counts, attack planes and identities do not.
    for side in [Color::White, Color::Black] {
        let index = side.index();
        position.squares[index][..order[index].len()].copy_from_slice(&order[index]);
    }
    position.validate()
}

pub(super) fn parameters(value: &Value, final_score: bool) -> Result<Parameters> {
    let mut parameters = Parameters::default();
    parameters.average_depth = integer(&value["averageDepth"], -100, 100)?;
    let percentages = &value["percentages"];
    object(percentages, &["own", "opponent"])?;
    for (owner, target) in [
        ("own", &mut parameters.own),
        ("opponent", &mut parameters.opponent),
    ] {
        object(&percentages[owner], &scores::NAMES)?;
        for (index, name) in scores::NAMES.iter().enumerate() {
            target[index] = integer(&percentages[owner][*name], 0, 1000)?;
        }
    }
    if final_score {
        parameters.draw = integer(&value["cfd"], -10_000, 10_000)?;
        parameters.opponent_selectivity = integer(&value["sop"], 0, 100)?;
    }
    Ok(parameters)
}

pub(super) fn retained_output(retained: Retained) -> Value {
    json!({"positionalSubtotal":retained.positional,"pawnProgress":retained.pawn_progress,
        "evaluationAge":retained.age})
}

/// Serialize actual native finishing values; no diagnostic admission is added.
pub(super) fn finishing_output<const DIAGNOSTICS: bool>(
    position: &Position,
    evaluator: &Evaluator<DIAGNOSTICS>,
    finished: Finished,
) -> Value {
    json!({"identity":{"primary":position.primary,"secondary":position.secondary,
            "pawn":position.pawn,"pawnGroup":position.pawn % 128},
        "variationIdentity":position.primary ^ position.secondary,
        "drawPreference":evaluator.draw_preference,"variationRange":evaluator.variation_range,
        "adjustedBase":finished.adjusted_base,"lateEndgame":finished.late_score,
        "scaledScore":finished.scaled_score,"score":finished.score,
        "lowerBound":finished.lower,"upperBound":finished.upper})
}
