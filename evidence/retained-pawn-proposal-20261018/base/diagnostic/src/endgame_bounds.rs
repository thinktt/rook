//! Selected material domains and supplied endpoints; native endgame routines own geometry.
use super::{array, boolean, color, integer, object, positions, text, Result};
use rook2::{
    endgame::{self, Bounded},
    position::Position,
};
use serde_json::{json, Value};

fn exact(counts: &[u8; 6], expected: [u8; 5]) -> bool {
    counts[..5] == expected
}

fn bounded(query: &Value) -> Result<Bounded> {
    Ok(Bounded {
        score: integer(&query["score"], -10_000, 10_000)?,
        lower: integer(&query["lowerBound"], -10_000, 10_000)?,
        upper: integer(&query["upperBound"], -10_000, 10_000)?,
    })
}

fn position(query: &Value) -> Result<Position> {
    let mut position = positions::placement(&query["placement"], true)?;
    position.side = color(&query["sideToMove"])?;
    Ok(position)
}

fn value(result: Bounded, include_score: bool) -> Value {
    let mut output = json!({"lowerBound":result.lower,"upperBound":result.upper});
    if include_score {
        output["score"] = json!(result.score);
    }
    output
}

fn race(query: &Value) -> Result<Value> {
    object(
        query,
        &[
            "placement",
            "pawnSide",
            "sideToMove",
            "score",
            "lowerBound",
            "upperBound",
        ],
    )?;
    let position = position(query)?;
    let side = color(&query["pawnSide"])?;
    let own = position.counts[side.index()];
    let other = position.counts[side.opponent().index()];
    if own[0] == 0 || own[1..5].iter().any(|&n| n != 0) || !exact(&other, [0; 5]) {
        return Err("pawn-race bound requires selected pawns against a bare king".into());
    }
    Ok(value(
        endgame::race_bounds(&position, side, bounded(query)?),
        true,
    ))
}

fn adjust(query: &Value) -> Result<Value> {
    object(
        query,
        &[
            "placement",
            "sideToMove",
            "inCheck",
            "score",
            "endgameWeight",
            "passedPawnBalance",
            "lowerBound",
            "upperBound",
        ],
    )?;
    let position = position(query)?;
    let initial = bounded(query)?;
    let result = endgame::adjust(
        &position,
        initial.score,
        integer(&query["endgameWeight"], 192, 256)? as u16,
        integer(&query["passedPawnBalance"], -10_000, 10_000)?,
        boolean(&query["inCheck"])?,
        initial.lower,
        initial.upper,
    );
    Ok(value(result, true))
}

fn fortress(query: &Value) -> Result<Value> {
    object(
        query,
        &[
            "mode",
            "placement",
            "affectedSide",
            "sideToMove",
            "score",
            "lowerBound",
            "upperBound",
        ],
    )?;
    let position = position(query)?;
    let side = color(&query["affectedSide"])?;
    let own = position.counts[side.index()];
    let other = position.counts[side.opponent().index()];
    let initial = bounded(query)?;
    let result = match text(&query["mode"])? {
        "bishopPawns" => {
            if own[0] == 0 || own[2] != 1 || own[1] != 0 || own[3] != 0 || own[4] != 0 {
                return Err(
                    "bishop-pawn bound requires exactly one bishop and selected pawns".into(),
                );
            }
            endgame::bishop_pawns(&position, side, initial)
        }
        "queenPawn" => {
            if !exact(&own, [0, 0, 0, 0, 1]) || !exact(&other, [1, 0, 0, 0, 0]) {
                return Err("queen-pawn bound requires queen against exactly one pawn".into());
            }
            endgame::queen_pawn(&position, side, initial)
        }
        _ => return Err("unknown fortress bound mode".into()),
    };
    Ok(value(result, false))
}

fn rook(query: &Value) -> Result<Value> {
    object(
        query,
        &[
            "mode",
            "placement",
            "affectedSide",
            "sideToMove",
            "inCheck",
            "score",
        ],
    )?;
    let position = position(query)?;
    let side = color(&query["affectedSide"])?;
    let own = position.counts[side.index()];
    let other = position.counts[side.opponent().index()];
    let score = integer(&query["score"], -10_000, 10_000)?;
    let checked = boolean(&query["inCheck"])?;
    let result = match text(&query["mode"])? {
        "rookPawn" => {
            if !exact(&own, [1, 0, 0, 1, 0]) || !exact(&other, [0, 0, 0, 1, 0]) {
                return Err("rook-pawn component requires rook and pawn against rook".into());
            }
            endgame::rook_pawn(&position, side, score)
        }
        "rookAgainstPawns" => {
            if !exact(&own, [0, 0, 0, 1, 0]) || other[0] == 0 {
                return Err("rook-against-pawns requires a lone rook and opposing pawns".into());
            }
            endgame::rook_against_pawns(&position, side, score, checked)
        }
        _ => return Err("unknown rook fortress mode".into()),
    };
    Ok(json!(result))
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let mut results = Vec::new();
    for query in array(&input["queries"], 1, 4096)? {
        results.push(match operation {
            "evaluation.pawnRaceBounds" => race(query)?,
            "evaluation.endgameAdjust" => adjust(query)?,
            "evaluation.fortressBounds" => fortress(query)?,
            "evaluation.rookFortress" => rook(query)?,
            _ => return Err(format!("unsupported endgame bound operation: {operation}")),
        });
    }
    Ok(if operation == "evaluation.rookFortress" {
        json!({"scores":results})
    } else {
        json!({"results":results})
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn selected_race_keeps_score_sign_and_contradictory_endpoints() {
        let mut q = json!({"placement":"8/8/kK6/8/8/8/1P6/8","pawnSide":"white","sideToMove":"black","score":-10000,"lowerBound":10000,"upperBound":-10000});
        assert_eq!(race(&q).unwrap()["score"], -10000);
        q["pawnSide"] = json!("black");
        assert!(race(&q).is_err());
        q["pawnSide"] = json!("white");
        q["placement"] = json!("8/8/kK6/8/8/8/1PN5/8");
        assert!(race(&q).is_err());
    }

    #[test]
    fn selected_material_is_validated_even_when_other_inputs_disable_geometry() {
        let mut q = json!({"mode":"rookAgainstPawns","placement":"8/8/8/8/8/8/p7/KR5k","affectedSide":"white","sideToMove":"black","inCheck":true,"score":-513});
        assert_eq!(rook(&q).unwrap(), -513);
        q["placement"] = json!("8/8/8/8/8/8/p7/KRN4k");
        assert!(rook(&q).is_err());
        q["placement"] = json!("8/8/8/8/8/8/p7/KR5k");
        q["mode"] = json!("rookPawn");
        assert!(rook(&q).is_err());
        q["mode"] = json!("rookAgainstPawns");
        q["inCheck"] = json!(0);
        assert!(rook(&q).is_err());
    }

    #[test]
    fn full_stage_admits_broad_placement_and_bounds_but_rejects_earlier_phase() {
        let mut q = json!({"placement":"8/8/8/8/8/8/k7/K7","sideToMove":"white","inCheck":false,"score":513,"endgameWeight":192,"passedPawnBalance":0,"lowerBound":10000,"upperBound":-10000});
        assert!(adjust(&q).is_ok());
        q["endgameWeight"] = json!(191);
        assert!(adjust(&q).is_err());
        q["endgameWeight"] = json!(256);
        q["inCheck"] = json!("false");
        assert!(adjust(&q).is_err());
        let f = json!({"mode":"bishopPawns","placement":"8/8/8/8/8/8/kP6/KB6","affectedSide":"white","sideToMove":"black","score":-10000,"lowerBound":7,"upperBound":-7});
        assert!(fortress(&f).is_ok());
    }
}
