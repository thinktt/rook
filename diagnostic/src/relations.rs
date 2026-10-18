//! Cold profile encodings and schemas; all classification is native computation.
use super::{array, color, integer, object, positions, text, Result};
use rook2::{
    influence::{adjusted_relation, relation, Contribution, Influence, Relation},
    types::PieceKind,
};
use serde_json::{json, Value};

pub(super) fn profile(value: &Value) -> Result<u8> {
    object(value, &["weak", "queen", "rook", "minor", "pawn"])?;
    let mut code = 0u32;
    for (name, weight) in [
        ("weak", 1),
        ("queen", 2),
        ("rook", 4),
        ("minor", 16),
        ("pawn", 64),
    ] {
        code += integer(&value[name], 0, 31)? as u32 * weight;
    }
    // The native byte is the normalized mixed-radix magnitude. Conversion
    // retains all specified carries and discards only the final pawn quotient.
    Ok(code as u8)
}

fn contribution(value: &Value) -> Result<Contribution> {
    match text(value)? {
        "weak" => Ok(Contribution::Weak),
        "queen" => Ok(Contribution::Queen),
        "rook" => Ok(Contribution::Rook),
        "minor" => Ok(Contribution::Minor),
        "pawn" => Ok(Contribution::Pawn),
        _ => Err("invalid excluded contribution".into()),
    }
}

fn name(relation: Relation) -> &'static str {
    match relation {
        Relation::Unfavorable => "unfavorable",
        Relation::Contested => "contested",
        Relation::Favorable => "favorable",
    }
}

fn outcomes(own: u8, opponent: u8, remove: Option<Contribution>) -> Value {
    let classify = |kind| {
        name(match remove {
            Some(remove) => adjusted_relation(own, opponent, remove, kind),
            None => relation(own, opponent, kind),
        })
    };
    json!({"pawn":classify(PieceKind::Pawn), "minor":classify(PieceKind::Knight),
           "rook":classify(PieceKind::Rook), "queen":classify(PieceKind::Queen)})
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "evaluation.relations" | "evaluation.adjustedRelations" => {
            object(input, &["pairs"])?;
            let adjusted = operation == "evaluation.adjustedRelations";
            let pairs = array(&input["pairs"], 1, 1024)?;
            let mut relations = Vec::with_capacity(pairs.len());
            for pair in pairs {
                let remove = if adjusted {
                    object(pair, &["own", "opponent", "remove", "side"])?;
                    color(&pair["side"])?;
                    Some(contribution(&pair["remove"])?)
                } else {
                    object(pair, &["own", "opponent"])?;
                    None
                };
                relations.push(outcomes(
                    profile(&pair["own"])?,
                    profile(&pair["opponent"])?,
                    remove,
                ));
            }
            Ok(
                json!({"relations":relations, "chargedRelationQueries":if adjusted { 0 } else { pairs.len() }}),
            )
        }
        "evaluation.influence" | "evaluation.squareRelations" => {
            object(input, &["placement", "queries"])?;
            let position = positions::placement(&input["placement"], true)?;
            let influence = Influence::build(&position);
            let queries = array(&input["queries"], 1, 1024)?;
            let mut results = Vec::with_capacity(queries.len());
            let profiles = operation == "evaluation.influence";
            for query in queries {
                object(query, &["square", "side"])?;
                let square = positions::square(&query["square"])?;
                let side = color(&query["side"])?;
                let own = influence.code(side, square);
                results.push(if profiles {
                    json!({"weak":own & 1, "queen":(own >> 1) & 1,
                           "rook":(own >> 2) & 3, "minor":(own >> 4) & 3, "pawn":own >> 6})
                } else {
                    outcomes(own, influence.code(side.opponent(), square), None)
                });
            }
            if profiles {
                Ok(json!({"profiles":results,"chargedRelationQueries":0}))
            } else {
                Ok(json!({"relations":results,"chargedRelationQueries":queries.len()}))
            }
        }
        _ => Err(format!("unsupported relation operation: {operation}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn admission_bounds_and_normalized_borrow_are_distinct() {
        let empty = json!({"weak":0,"queen":0,"rook":0,"minor":8,"pawn":2});
        let pair = json!({"own":empty,"opponent":{"weak":0,"queen":0,"rook":0,"minor":0,"pawn":1},"remove":"pawn","side":"black"});
        let output = dispatch(
            "evaluation.adjustedRelations",
            &json!({"pairs":[pair.clone(),pair.clone()]}),
        )
        .unwrap();
        assert_eq!(output["chargedRelationQueries"], 0);
        assert_eq!(
            output["relations"][0],
            json!({"pawn":"unfavorable","minor":"unfavorable","rook":"unfavorable","queen":"unfavorable"})
        );
        assert_eq!(output["relations"][0], output["relations"][1]);
        let mut invalid = pair;
        invalid["own"]["weak"] = json!(32);
        assert!(dispatch("evaluation.adjustedRelations", &json!({"pairs":[invalid]})).is_err());
        assert!(dispatch("evaluation.relations", &json!({"pairs":[]})).is_err());
    }

    #[test]
    fn placement_schema_preserves_duplicate_queries_and_component_domain() {
        let query = json!({"square":"e2","side":"white"});
        let mut input = json!({"placement":"4k3/8/8/8/8/8/8/4K3","queries":[query.clone(),query]});
        let output = dispatch("evaluation.influence", &input).unwrap();
        assert_eq!(
            output["profiles"],
            json!([{"weak":1,"queen":0,"rook":0,"minor":0,"pawn":0},{"weak":1,"queen":0,"rook":0,"minor":0,"pawn":0}])
        );
        assert_eq!(
            dispatch("evaluation.squareRelations", &input).unwrap()["chargedRelationQueries"],
            2
        );
        input["queries"][0]["extra"] = json!(0);
        assert!(dispatch("evaluation.influence", &input).is_err());
        assert!(dispatch("evaluation.influence", &json!({"placement":"7k/8/8/8/8/NNNNNNNN/NNN5/K7","queries":[{"square":"a1","side":"white"}]})).is_err());
    }
}
