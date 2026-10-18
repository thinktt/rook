//! Cold policy schemas over the native root, tactical and PV-formatting seams.
use super::{array, boolean, integer, moves, object, positions, text, unsigned32, Result};
use rook2::{
    output,
    quiescence_policy::{capture_policy, CaptureContext},
    timed,
    types::{Move, MoveKind, PieceKind},
};
use serde_json::{json, Value};

fn random_move(value: &Value) -> Result<Move> {
    object(value, &["from", "to", "kind", "promotion"])?;
    let from = positions::square(&value["from"])?;
    let to = positions::square(&value["to"])?;
    if from == to {
        return Err("move endpoints must differ".into());
    }
    let promotion = if value["promotion"].is_null() {
        None
    } else {
        let piece = moves::piece(&value["promotion"])?;
        if !matches!(
            piece,
            PieceKind::Knight | PieceKind::Bishop | PieceKind::Rook | PieceKind::Queen
        ) {
            return Err("invalid promotion choice".into());
        }
        Some(piece)
    };
    let displacement = (from.file() as i32 - to.file() as i32).abs();
    let kind = match (text(&value["kind"])?, promotion) {
        ("ordinary", None) => MoveKind::Ordinary,
        ("ordinary", Some(piece))
            if matches!((from.rank(), to.rank()), (6, 7) | (1, 0)) && displacement <= 1 =>
        {
            MoveKind::Promotion(piece)
        }
        ("enPassant", None)
            if matches!((from.rank(), to.rank()), (4, 5) | (3, 2)) && displacement == 1 =>
        {
            MoveKind::EnPassant
        }
        ("castle", None)
            if from.file() == 4
                && matches!(from.rank(), 0 | 7)
                && to.rank() == from.rank()
                && matches!(to.file(), 2 | 6) =>
        {
            MoveKind::Castle
        }
        _ => return Err("move kind/promotion geometry outside root-randomization domain".into()),
    };
    Ok(Move::new(from, to, kind))
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let maximum = match operation {
        "output.pvLine" => 128,
        "search.quiescenceCapturePolicy" => 1024,
        _ => 4096,
    };
    let mut results = Vec::new();
    for query in array(&input["queries"], 1, maximum)? {
        results.push(match operation {
            "search.rootRandomization" => {
                object(query, &["seed", "randomness", "move", "lowerBound", "upperBound", "rawScore"])?;
                let lower = integer(&query["lowerBound"], -10000, 10000)?;
                let upper = integer(&query["upperBound"], -10000, 10000)?;
                if lower > upper {
                    return Err("lower bound exceeds upper bound".into());
                }
                let adjustment = timed::random_adjustment(
                    unsigned32(&query["seed"])?,
                    integer(&query["randomness"], 0, i32::MAX)? as u32,
                    random_move(&query["move"])?,
                );
                json!({"adjustment":adjustment,
                       "searchLowerBound":timed::score_add(lower, -adjustment),
                       "searchUpperBound":timed::score_add(upper, -adjustment),
                       "rankingScore":timed::score_add(integer(&query["rawScore"], -10000, 10000)?, adjustment)})
            }
            "search.rootAspiration" => {
                object(query, &["currentBest", "previousBest", "firstScore", "retryScore"])?;
                let window = timed::aspiration(
                    integer(&query["currentBest"], -10000, 10000)?,
                    integer(&query["previousBest"], -10000, 10000)?,
                );
                let first = integer(&query["firstScore"], -10000, 10000)?;
                let retry = integer(&query["retryScore"], -10000, 10000)?;
                let mut passes = vec![json!({"lowerBound":window[0], "upperBound":window[1], "score":first})];
                let returned = if first >= window[1] {
                    passes.push(json!({"lowerBound":window[0], "upperBound":10000, "score":retry}));
                    retry
                } else {
                    first
                };
                json!({"passes":passes, "returnedScore":returned,
                       "rankingScore":timed::ranking_score(returned, window, true)})
            }
            "search.quiescenceCapturePolicy" => {
                object(query, &["initialEstimate", "searchPly", "targetPly", "iterationDepth", "best", "alpha", "movingPieceValue", "defended"])?;
                let defended = boolean(&query["defended"])?;
                let decision = capture_policy(
                    integer(&query["initialEstimate"], -30000, 30000)?,
                    integer(&query["movingPieceValue"], 0, 10000)?,
                    CaptureContext {
                        ply: integer(&query["searchPly"], 1, 62)?,
                        target: integer(&query["targetPly"], 0, 62)?,
                        iteration_depth: integer(&query["iterationDepth"], 1, 62)?,
                        best: integer(&query["best"], -10000, 10000)?,
                        alpha: integer(&query["alpha"], -10000, 10000)?,
                    },
                    || defended,
                );
                json!({"estimate":decision.estimate, "best":decision.best,
                       "forceSearch":decision.force_search, "defenseQueried":decision.defense_queried})
            }
            "output.pvLine" => {
                object(query, &["prefixLength", "tokens"])?;
                let prefix = integer(&query["prefixLength"], 0, 80)? as usize;
                let mut tokens = Vec::new();
                for token in array(&query["tokens"], 0, 63)? {
                    let token = text(token)?;
                    if !(1..=12).contains(&token.len())
                        || !token.bytes().all(|b| b.is_ascii_alphanumeric() || matches!(b, b'+' | b'=' | b'-'))
                        || matches!(token, "O-O" | "O-O-O")
                    {
                        return Err("invalid controlled PV token".into());
                    }
                    tokens.push(token.to_owned());
                }
                let (tokens, length) = output::displayed_tokens(prefix, &tokens);
                json!({"tokens":tokens, "byteLength":length})
            }
            _ => return Err(format!("unsupported policy operation: {operation}")),
        });
    }
    Ok(if operation == "output.pvLine" {
        json!({"lines":results})
    } else {
        json!({"results":results})
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn root_move_domain_differs_from_uncertified_hint_syntax() {
        for descriptor in [
            json!({"from":"a2","to":"h7","kind":"ordinary","promotion":null}),
            json!({"from":"e8","to":"c8","kind":"castle","promotion":null}),
            json!({"from":"b2","to":"a1","kind":"ordinary","promotion":"knight"}),
            json!({"from":"e5","to":"d6","kind":"enPassant","promotion":null}),
        ] {
            assert!(random_move(&descriptor).is_ok());
        }
        for descriptor in [
            json!({"from":"a2","to":"a3","kind":"ordinary","promotion":"queen"}),
            json!({"from":"a1","to":"h1","kind":"castle","promotion":null}),
            json!({"from":"e5","to":"e6","kind":"enPassant","promotion":null}),
        ] {
            assert!(random_move(&descriptor).is_err());
        }
        let q = json!({"seed":4294967295u64,"randomness":i32::MAX,"move":{"from":"a2","to":"h7","kind":"ordinary","promotion":null},"lowerBound":-9000,"upperBound":9000,"rawScore":10000});
        let out = dispatch(
            "search.rootRandomization",
            &json!({"queries":[q.clone(),q]}),
        )
        .unwrap();
        assert_eq!(out["results"][0], out["results"][1]);
        assert_eq!(out["results"][0]["rankingScore"], 10000);
    }

    #[test]
    fn aspiration_retains_retry_lower_and_validates_unused_input() {
        let q = json!({"currentBest":0,"previousBest":0,"firstScore":3,"retryScore":2});
        let out = dispatch("search.rootAspiration", &json!({"queries":[q.clone()]})).unwrap();
        assert_eq!(
            out["results"][0],
            json!({"passes":[{"lowerBound":2,"upperBound":3,"score":3},{"lowerBound":2,"upperBound":10000,"score":2}],"returnedScore":2,"rankingScore":0})
        );
        let mut invalid = q;
        invalid["firstScore"] = json!(0);
        invalid["retryScore"] = json!(10001);
        assert!(dispatch("search.rootAspiration", &json!({"queries":[invalid]})).is_err());
    }

    #[test]
    fn capture_policy_preserves_independence_and_checks_required_boolean() {
        let mut q = json!({"initialEstimate":11,"searchPly":1,"targetPly":0,"iterationDepth":1,"best":0,"alpha":10,"movingPieceValue":1,"defended":true});
        let out = dispatch(
            "search.quiescenceCapturePolicy",
            &json!({"queries":[q.clone(),q.clone()]}),
        )
        .unwrap();
        assert_eq!(
            out["results"][0],
            json!({"estimate":10,"best":10,"forceSearch":false,"defenseQueried":true})
        );
        assert_eq!(out["results"][0], out["results"][1]);
        q["defended"] = json!(0);
        assert!(dispatch("search.quiescenceCapturePolicy", &json!({"queries":[q]})).is_err());
    }

    #[test]
    fn pv_schema_keeps_crossing_token_and_rejects_other_alphabets() {
        let q = json!({"prefixLength":80,"tokens":vec!["abcdefghi"; 32]});
        let out = dispatch("output.pvLine", &json!({"queries":[q]})).unwrap();
        assert_eq!(out["lines"][0]["byteLength"], 390);
        assert_eq!(out["lines"][0]["tokens"].as_array().unwrap().len(), 31);
        for invalid in ["O-O", "O-O-O", "a#", "é", "", "abcdefghijklm"] {
            assert!(dispatch(
                "output.pvLine",
                &json!({"queries":[{"prefixLength":0,"tokens":[invalid]}]})
            )
            .is_err());
        }
    }
}
