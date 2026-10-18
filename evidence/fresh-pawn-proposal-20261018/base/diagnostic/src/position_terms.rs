//! Fresh diagnostic schemas for native placement-derived evaluation components.
use super::{array, integer, object, phase, positions, relations, Result};
use rook2::{activity, influence::Influence, positional_terms, shelter};
use serde_json::{json, Value};

fn weights(value: &Value, minimum: i32, maximum: i32) -> Result<[i32; 2]> {
    object(value, &["white", "black"])?;
    Ok([
        integer(&value["white"], minimum, maximum)?,
        integer(&value["black"], minimum, maximum)?,
    ])
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let mut results = Vec::new();
    for query in array(&input["queries"], 1, 4096)? {
        let result = match operation {
            "evaluation.boardPatterns" => {
                object(query, &["placement"])?;
                let position = positions::placement(&query["placement"], true)?;
                let patterns = positional_terms::patterns(&position);
                json!({"phase":positions::phase_value(position.phase()),
                    "bishopCoordination":patterns.bishop_coordination,
                    "rawPatterns":patterns.raw,"openingPatterns":patterns.opening})
            }
            "evaluation.activity" => {
                object(
                    query,
                    &[
                        "placement",
                        "activityWeights",
                        "positionWeights",
                        "materialScore",
                    ],
                )?;
                let position = positions::placement(&query["placement"], true)?;
                let activity_weights = weights(&query["activityWeights"], 0, 4096)?;
                let position_weights = weights(&query["positionWeights"], 0, 4096)?;
                let material = integer(&query["materialScore"], -100000, 100000)?;
                let influence = Influence::build(&position);
                let activity = activity::compute(&position, &influence, material, activity_weights);
                let position_terms = shelter::compute(
                    &position,
                    &influence,
                    activity.pressure,
                    material,
                    position_weights,
                );
                json!({"phase":positions::phase_value(position.phase()),
                    "pieces":{"white":activity.pieces[0],"black":activity.pieces[1]},
                    "activityPressure":{"white":activity.pressure[0],"black":activity.pressure[1]},
                    "weightedActivity":activity.weighted,
                    "positionTerms":{"white":position_terms.terms[0],"black":position_terms.terms[1],"weighted":position_terms.weighted},
                    "relationQueries":activity.relation_queries})
            }
            "evaluation.centralInfluenceBalance" | "evaluation.positionCentralBalance" => {
                let controlled = operation == "evaluation.centralInfluenceBalance";
                let influence = if controlled {
                    object(query, &["phase", "weights", "samples"])?;
                    let mut influence = Influence {
                        profiles: [[0; 64]; 2],
                    };
                    let mut seen = 0u64;
                    for sample in array(&query["samples"], 0, 64)? {
                        object(sample, &["square", "white", "black"])?;
                        let square = positions::square(&sample["square"])?;
                        if seen & (1u64 << square.0) != 0 {
                            return Err("central samples must name distinct squares".into());
                        }
                        seen |= 1u64 << square.0;
                        influence.profiles[0][square.0 as usize] =
                            relations::profile(&sample["white"])?;
                        influence.profiles[1][square.0 as usize] =
                            relations::profile(&sample["black"])?;
                    }
                    influence
                } else {
                    object(query, &["phase", "weights", "placement"])?;
                    Influence::build(&positions::placement(&query["placement"], true)?)
                };
                let result = positional_terms::central(
                    &influence,
                    phase(&query["phase"])?,
                    weights(&query["weights"], -10000, 10000)?,
                );
                json!({"white":result.colors[0],"black":result.colors[1],"weighted":result.weighted,"relationQueries":0})
            }
            _ => return Err(format!("unsupported position contribution: {operation}")),
        };
        results.push(result);
    }
    Ok(json!({"results":results}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn central_schema_validates_ignored_squares_and_closed_phase_gate() {
        let empty = json!({"weak":0,"queen":0,"rook":0,"minor":0,"pawn":0});
        let sample = json!({"square":"a1","white":empty.clone(),"black":empty});
        let query = json!({"phase":{"opening":0,"middlegame":0,"endgame":256},
            "weights":{"white":-10000,"black":10000},"samples":[sample.clone()]});
        assert!(dispatch(
            "evaluation.centralInfluenceBalance",
            &json!({"queries":[query.clone()]})
        )
        .is_ok());
        let mut duplicate = query.clone();
        duplicate["samples"] = json!([sample.clone(), sample]);
        assert!(dispatch(
            "evaluation.centralInfluenceBalance",
            &json!({"queries":[duplicate]})
        )
        .is_err());
        let mut bad = query;
        bad["samples"][0]["white"]["extra"] = json!(0);
        assert!(dispatch(
            "evaluation.centralInfluenceBalance",
            &json!({"queries":[bad]})
        )
        .is_err());
    }

    #[test]
    fn activity_rejects_supplied_dependencies_and_invalid_weight_domains() {
        let query = json!({"placement":"4k3/8/8/8/8/8/8/4K3",
            "activityWeights":{"white":0,"black":4096},"positionWeights":{"white":4096,"black":0},"materialScore":-100000});
        assert!(dispatch(
            "evaluation.activity",
            &json!({"queries":[query.clone(),query.clone()]})
        )
        .is_ok());
        let mut extra = query.clone();
        extra["phase"] = json!({"opening":0,"middlegame":0,"endgame":256});
        assert!(dispatch("evaluation.activity", &json!({"queries":[extra]})).is_err());
        let mut negative = query;
        negative["activityWeights"]["white"] = json!(-1);
        assert!(dispatch("evaluation.activity", &json!({"queries":[negative]})).is_err());
    }

    #[test]
    fn component_placements_allow_attacked_kings_but_keep_type_bounds() {
        assert!(dispatch(
            "evaluation.boardPatterns",
            &json!({"queries":[{"placement":"8/8/8/8/8/8/k7/K7"}]})
        )
        .is_ok());
        assert!(dispatch(
            "evaluation.boardPatterns",
            &json!({"queries":[{"placement":"7k/8/8/8/8/NNNNNNNN/NNN5/K7"}]})
        )
        .is_err());
        assert!(dispatch(
            "evaluation.boardPatterns",
            &json!({"queries":[{"placement":"7k/8/8/8/8/8/8/K7","phase":0}]})
        )
        .is_err());
    }
}
