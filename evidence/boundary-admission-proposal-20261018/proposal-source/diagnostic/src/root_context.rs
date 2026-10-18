//! Cold root material/square schemas; arithmetic remains in native evaluation.
use super::{array, color, integer, moves, object, phase, positions, supplied, Result};
use rook2::{
    evaluation::{self, RootContext},
    types::{Color, PieceKind, Square},
};
use serde_json::{json, Map, Value};

fn percentages(value: &Value, root_side: Color) -> Result<[[u16; 5]; 2]> {
    object(value, &["own", "opponent"])?;
    let mut result = [[0; 5]; 2];
    for (name, side) in [("own", root_side), ("opponent", root_side.opponent())] {
        object(&value[name], &moves::PIECES[..5])?;
        for (kind, piece) in moves::PIECES[..5].iter().enumerate() {
            result[side.index()][kind] = integer(&value[name][*piece], 0, 1000)? as u16;
        }
    }
    Ok(result)
}

fn values(value: [[i32; 5]; 2]) -> Value {
    let mut colors = Map::new();
    for (side, name) in moves::COLORS.iter().enumerate() {
        let mut pieces = Map::new();
        for (kind, piece) in moves::PIECES[..5].iter().enumerate() {
            pieces.insert((*piece).into(), json!(value[side][kind]));
        }
        colors.insert((*name).into(), Value::Object(pieces));
    }
    Value::Object(colors)
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "evaluation.materialValues" => {
            object(input, &["phase", "rootSide", "materialPercent"])?;
            let phase = phase(&input["phase"])?;
            let side = color(&input["rootSide"])?;
            let percentages = percentages(&input["materialPercent"], side)?;
            Ok(json!({"values":values(evaluation::material_values(phase, percentages))}))
        }
        "evaluation.rootMaterial" => {
            object(
                input,
                &[
                    "placement",
                    "rootSide",
                    "materialPercent",
                    "currentCounts",
                    "averageDepth",
                ],
            )?;
            // This domain admits promotion-heavy placements and adjacent kings.
            let mut position = positions::placement(&input["placement"], false)?;
            position.side = color(&input["rootSide"])?;
            let percentages = percentages(&input["materialPercent"], position.side)?;
            let depth = integer(&input["averageDepth"], -100, 100)?;
            let root = RootContext::new(&position, percentages, depth);
            // Counts are an independent material hypothetical, never a board for
            // move generation. Keep the placement's root phase/counts fixed.
            position.counts = supplied::counts(&input["currentCounts"])?;
            Ok(json!({"phase":positions::phase_value(root.phase),
                      "values":values(root.values), "score":root.material(&position)}))
        }
        "evaluation.squareValues" => {
            object(input, &["phase", "queries"])?;
            let phase = phase(&input["phase"])?;
            let mut adjustments = Vec::new();
            for query in array(&input["queries"], 0, 768)? {
                object(query, &["side", "piece", "square"])?;
                adjustments.push(evaluation::square_adjustment(
                    phase,
                    color(&query["side"])?,
                    moves::piece(&query["piece"])?,
                    positions::square(&query["square"])?,
                ));
            }
            Ok(json!({"adjustments":adjustments, "chargedRelationQueries":0}))
        }
        "evaluation.squareBalance" => {
            object(input, &["rootPhase", "phase", "placement"])?;
            let root_phase = phase(&input["rootPhase"])?;
            let phase = phase(&input["phase"])?;
            let position = positions::placement(&input["placement"], false)?;
            let mut root = RootContext::neutral(&position);
            root.phase = root_phase;
            for color in [Color::White, Color::Black] {
                for kind in &PieceKind::ALL[..5] {
                    for square in 0..64 {
                        root.squares[color.index()][kind.index()][square] =
                            evaluation::square_adjustment(
                                root_phase,
                                color,
                                *kind,
                                Square(square as u8),
                            ) as i16;
                    }
                }
            }
            let nonking_sum = root.nonking_square_balance(&position);
            Ok(
                json!({"balance":root.square_balance_from_phase(&position, nonking_sum, phase),
                      "chargedRelationQueries":0}),
            )
        }
        _ => Err(format!("unsupported root-context operation: {operation}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn neutral_percentages() -> Value {
        let pieces = json!({"pawn":100,"knight":100,"bishop":100,"rook":100,"queen":100});
        json!({"own":pieces,"opponent":pieces})
    }

    fn empty_counts() -> Value {
        let pieces = json!({"pawn":0,"knight":0,"bishop":0,"rook":0,"queen":0});
        json!({"white":pieces,"black":pieces})
    }

    #[test]
    fn material_values_keep_separate_rounding_and_black_root_ownership() {
        // Released root-material-values-3-black, including base then weight rounding.
        let q = json!({"phase":{"opening":1,"middlegame":127,"endgame":128},
            "rootSide":"black","materialPercent":{
                "own":{"pawn":0,"knight":1,"bishop":49,"rook":99,"queen":101},
                "opponent":{"pawn":92,"knight":100,"bishop":133,"rook":200,"queen":1000}}});
        assert_eq!(
            dispatch("evaluation.materialValues", &q).unwrap(),
            json!({"values":{
            "white":{"pawn":83,"knight":298,"bishop":406,"rook":984,"queen":8950},
            "black":{"pawn":0,"knight":3,"bishop":150,"rook":487,"queen":904}}})
        );
    }

    #[test]
    fn root_material_keeps_root_values_through_independent_descendant_counts() {
        let mut counts = empty_counts();
        counts["white"]["pawn"] = json!(1);
        let mut q = json!({"placement":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            "rootSide":"black","materialPercent":neutral_percentages(),
            "currentCounts":counts,"averageDepth":-5});
        let out = dispatch("evaluation.rootMaterial", &q).unwrap();
        assert_eq!(
            out["phase"],
            json!({"opening":256,"middlegame":0,"endgame":0})
        );
        assert_eq!(out["values"]["white"]["pawn"], 66);
        // 30 root pieces minus one current piece, signed odd floor, black root.
        assert_eq!(out["score"], -6);
        q["rootSide"] = json!("white");
        assert_eq!(
            dispatch("evaluation.rootMaterial", &q).unwrap()["score"],
            138
        );
    }

    #[test]
    fn square_values_preserve_duplicates_orientation_and_promotion_rank_queries() {
        let query = json!({"side":"black","piece":"knight","square":"a8"});
        let reflected = json!({"side":"white","piece":"knight","square":"a1"});
        let pawn = json!({"side":"white","piece":"pawn","square":"a8"});
        let mut q = json!({"phase":{"opening":17,"middlegame":81,"endgame":158},
            "queries":[query.clone(),reflected,query,pawn]});
        assert_eq!(
            dispatch("evaluation.squareValues", &q).unwrap(),
            json!({"adjustments":[-16,-16,-16,0],"chargedRelationQueries":0})
        );
        q["queries"] = json!([]);
        assert_eq!(
            dispatch("evaluation.squareValues", &q).unwrap(),
            json!({"adjustments":[],"chargedRelationQueries":0})
        );
    }

    #[test]
    fn square_balance_uses_independent_root_and_current_phases() {
        // Released square-balance-1-1 and square-balance-1-0.
        let mut q = json!({"rootPhase":{"opening":0,"middlegame":0,"endgame":256},
            "phase":{"opening":256,"middlegame":0,"endgame":0},
            "placement":"7k/8/8/3P4/8/2N5/8/K7"});
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap(),
            json!({"balance":2,"chargedRelationQueries":0})
        );
        q["rootPhase"] = json!({"opening":256,"middlegame":0,"endgame":0});
        q["phase"] = json!({"opening":0,"middlegame":0,"endgame":256});
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap()["balance"],
            15
        );
    }

    #[test]
    fn king_difference_rounds_once_and_nonpawn_presence_disables_doubling() {
        // Released single-round-128 cases isolate the one-round king difference.
        let mut q = json!({"rootPhase":{"opening":0,"middlegame":256,"endgame":0},
            "phase":{"opening":128,"middlegame":128,"endgame":0},
            "placement":"k7/8/8/8/8/K7/8/8"});
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap()["balance"],
            -110
        );
        q["placement"] = json!("k7/8/8/8/8/K7/3P4/8");
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap()["balance"],
            -130
        );
        q["placement"] = json!("k7/8/8/8/8/K7/8/7N");
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap()["balance"],
            -71
        );
        q["placement"] = json!("8/8/k7/8/8/8/8/K7");
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap()["balance"],
            112
        );
    }

    #[test]
    fn square_balance_keeps_negative_half_rounding_per_nonking_before_summing() {
        // Each a3/a4 knight has O=-12, M=-9: -10.5 rounds to -10.
        // Separately rounded terms sum to -20; rounding their sum gives -21.
        let q = json!({"rootPhase":{"opening":128,"middlegame":128,"endgame":0},
            "phase":{"opening":0,"middlegame":0,"endgame":256},
            "placement":"k7/8/8/8/N7/N7/8/7K"});
        assert_eq!(
            dispatch("evaluation.squareBalance", &q).unwrap()["balance"],
            -20
        );
    }

    #[test]
    fn schemas_reject_extra_fields_bad_phases_percentages_and_counts() {
        let q = json!({"phase":{"opening":256,"middlegame":0,"endgame":0},
            "rootSide":"white","materialPercent":neutral_percentages()});
        for bad in [
            {
                let mut v = q.clone();
                v["extra"] = json!(0);
                v
            },
            {
                let mut v = q.clone();
                v["phase"]["opening"] = json!(255);
                v
            },
            {
                let mut v = q.clone();
                v["phase"]["endgame"] = json!(-1);
                v
            },
            {
                let mut v = q.clone();
                v["phase"]["extra"] = json!(0);
                v
            },
            {
                let mut v = q.clone();
                v["materialPercent"]["own"]["pawn"] = json!(1001);
                v
            },
            {
                let mut v = q.clone();
                v["materialPercent"]["opponent"]["king"] = json!(100);
                v
            },
        ] {
            assert!(dispatch("evaluation.materialValues", &bad).is_err());
        }
        let mut q = json!({"placement":"7k/8/8/8/8/8/8/K7", "rootSide":"white",
            "materialPercent":neutral_percentages(),"currentCounts":empty_counts(),"averageDepth":0});
        q["currentCounts"]["white"]["pawn"] = json!(15);
        q["currentCounts"]["black"]["queen"] = json!(15);
        assert!(dispatch("evaluation.rootMaterial", &q).is_ok());
        q["currentCounts"]["black"]["rook"] = json!(1);
        assert!(dispatch("evaluation.rootMaterial", &q).is_err());
        q["currentCounts"] = empty_counts();
        q["averageDepth"] = json!(101);
        assert!(dispatch("evaluation.rootMaterial", &q).is_err());
        let mut q = json!({"phase":{"opening":256.0,"middlegame":0,"endgame":0},
            "queries":vec![json!({"side":"white","piece":"pawn","square":"a8"});768]});
        assert!(dispatch("evaluation.squareValues", &q).is_ok());
        q["queries"]
            .as_array_mut()
            .unwrap()
            .push(json!({"side":"white","piece":"pawn","square":"a8"}));
        assert!(dispatch("evaluation.squareValues", &q).is_err());
        q["queries"] = json!([{"side":"white","piece":"pawn","square":"a8","extra":0}]);
        assert!(dispatch("evaluation.squareValues", &q).is_err());
    }

    #[test]
    fn placements_admit_promotion_heavy_counts_and_adjacent_kings_without_legality() {
        let mut q = json!({"rootPhase":{"opening":256,"middlegame":0,"endgame":0},
            "phase":{"opening":0,"middlegame":0,"endgame":256},
            "placement":"8/8/8/8/8/8/8/Kk6"});
        assert!(dispatch("evaluation.squareBalance", &q).is_ok());
        q["placement"] = json!("7k/8/8/8/8/QQQQQQQQ/QQQQQQQ1/K7");
        assert!(dispatch("evaluation.squareBalance", &q).is_ok());
        q["placement"] = json!("P6k/8/8/8/8/8/8/K7");
        assert!(dispatch("evaluation.squareBalance", &q).is_err());
    }
}
