//! Cold endgame component domains, with native numerical/geometry ownership.
use super::{array, color, integer, moves, object, positions, text, Result};
use rook2::{endgame, types::Square};
use serde_json::{json, Value};

fn files(value: &Value) -> Result<Vec<u8>> {
    array(value, 0, 8)?
        .iter()
        .map(|v| {
            let bytes = text(v)?.as_bytes();
            if bytes.len() != 1 || !(b'a'..=b'h').contains(&bytes[0]) {
                return Err("pawn file must be one lowercase letter a..h".into());
            }
            Ok(bytes[0] - b'a')
        })
        .collect()
}

fn material(value: &Value) -> Result<[u8; 6]> {
    object(value, &moves::PIECES[..5])?;
    let mut counts = [0u8; 6];
    for (index, name) in moves::PIECES[..5].iter().enumerate() {
        counts[index] = integer(&value[*name], 0, if index == 0 { 8 } else { 15 })? as u8;
    }
    if counts[..5].iter().map(|&n| n as u32).sum::<u32>() > 15 {
        return Err("each material side has at most15 non-king pieces".into());
    }
    counts[5] = 1;
    Ok(counts)
}

fn distinct(a: Square, b: Square, c: Square) -> Result<()> {
    if a == b || a == c || b == c {
        Err("three supplied squares must be distinct".into())
    } else {
        Ok(())
    }
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let mut scores = Vec::new();
    for query in array(&input["queries"], 1, 4096)? {
        scores.push(match operation {
            "evaluation.endgamePawnSpread" => {
                object(
                    query,
                    &["score", "endgameWeight", "whitePawnFiles", "blackPawnFiles"],
                )?;
                let white = files(&query["whitePawnFiles"])?;
                let black = files(&query["blackPawnFiles"])?;
                endgame::pawn_spread_files(
                    integer(&query["score"], -100000, 100000)?,
                    integer(&query["endgameWeight"], 192, 256)? as u16,
                    &white,
                    &black,
                )
            }
            "evaluation.pawnlessPotential" => {
                object(query, &["score", "favoredMaterial", "otherMaterial"])?;
                let favored = material(&query["favoredMaterial"])?;
                let other = material(&query["otherMaterial"])?;
                if favored[0] != 0 {
                    return Err("favored pawnless side must have zero pawns".into());
                }
                endgame::pawnless_potential(integer(&query["score"], 0, 100000)?, &favored, &other)
            }
            "evaluation.minorMateGeometry" => {
                object(
                    query,
                    &["strongerSide", "strongerKing", "weakerKing", "bishop"],
                )?;
                color(&query["strongerSide"])?;
                let stronger = positions::square(&query["strongerKing"])?;
                let weaker = positions::square(&query["weakerKing"])?;
                let bishop = positions::square(&query["bishop"])?;
                distinct(stronger, weaker, bishop)?;
                endgame::minor_mate(stronger, weaker, bishop)
            }
            "evaluation.endgameMaterialBlend" => {
                object(
                    query,
                    &["placement", "score", "endgameWeight", "passedPawnBalance"],
                )?;
                let position = positions::placement(&query["placement"], true)?;
                endgame::material_blend(
                    &position,
                    integer(&query["score"], -10000, 10000)?,
                    integer(&query["endgameWeight"], 192, 256)? as u16,
                    integer(&query["passedPawnBalance"], -10000, 10000)?,
                )
            }
            "evaluation.pawnRace" => {
                object(
                    query,
                    &["pawnSide", "pawnKing", "pawn", "otherKing", "sideToMove"],
                )?;
                let side = color(&query["pawnSide"])?;
                let king = positions::square(&query["pawnKing"])?;
                let pawn = positions::square(&query["pawn"])?;
                let other = positions::square(&query["otherKing"])?;
                let turn = color(&query["sideToMove"])?;
                distinct(king, pawn, other)?;
                if !(1..=6).contains(&pawn.rank()) {
                    return Err("classifier pawn must be on ranks2..7".into());
                }
                endgame::pawn_race(side, king, pawn, other, turn)
            }
            _ => return Err(format!("unsupported endgame operation: {operation}")),
        });
    }
    Ok(if operation == "evaluation.pawnRace" {
        json!({"classifications":scores})
    } else {
        json!({"scores":scores})
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn classifier_keeps_adjacent_kings_admitted_and_requires_distinct_squares() {
        let mut query = json!({"pawnSide":"white","pawnKing":"a1","pawn":"a2","otherKing":"b1","sideToMove":"black"});
        assert!(dispatch("evaluation.pawnRace", &json!({"queries":[query.clone()]})).is_ok());
        query["pawn"] = json!("a1");
        assert!(dispatch("evaluation.pawnRace", &json!({"queries":[query.clone()]})).is_err());
        query["pawn"] = json!("a8");
        assert!(dispatch("evaluation.pawnRace", &json!({"queries":[query]})).is_err());
    }

    #[test]
    fn component_counts_and_files_have_their_own_population_domains() {
        assert_eq!(files(&json!(["h", "h", "a"])).unwrap(), vec![7, 7, 0]);
        assert!(files(&json!(["A"])).is_err());
        let mut counts = json!({"pawn":8,"knight":0,"bishop":0,"rook":0,"queen":7});
        assert!(material(&counts).is_ok());
        counts["queen"] = json!(8);
        assert!(material(&counts).is_err());
        counts["queen"] = json!(0);
        let empty = json!({"pawn":0,"knight":0,"bishop":0,"rook":0,"queen":0});
        assert!(dispatch(
            "evaluation.pawnlessPotential",
            &json!({"queries":[{"score":0,"favoredMaterial":counts,"otherMaterial":empty}]})
        )
        .is_err());
    }
}
