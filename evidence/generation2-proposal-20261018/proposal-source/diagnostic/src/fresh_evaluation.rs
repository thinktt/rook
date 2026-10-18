//! Forced-fresh evaluation transport. Numerical composition stays native.
use super::{array, color, evaluation_common as common, integer, object, positions, Result};
use rook2::{
    evaluator::{Components, Evaluator, FullDetails, Node, Parameters},
    influence::Influence,
    movegen,
    position::Position,
};
use serde_json::{json, Value};

struct Query {
    root: Position,
    current: Position,
    parameters: Parameters,
}

impl Query {
    fn parse(query: &Value, final_score: bool) -> Result<Self> {
        let mut fields = vec![
            "rootPlacement", "placement", "rootSide", "sideToMove",
            "percentages", "averageDepth", "pawnOrder",
        ];
        if final_score {
            fields.extend(["cfd", "sop", "reversiblePlies"]);
        }
        object(query, &fields)?;
        let mut root = positions::placement(&query["rootPlacement"], true)?;
        let mut current = positions::placement(&query["placement"], true)?;
        root.side = color(&query["rootSide"])?;
        current.side = color(&query["sideToMove"])?;
        let parameters = common::parameters(query, final_score)?;
        if final_score {
            current.halfmove = integer(&query["reversiblePlies"], 0, 255)? as u8;
        }
        common::apply_pawn_order(&mut current, &query["pawnOrder"])?;
        Ok(Self { root, current, parameters })
    }

    fn observe(self, final_score: bool) -> Value {
        let mut evaluator = Evaluator::<true>::new(&self.root);
        evaluator.parameters = self.parameters;
        evaluator.begin_search(&self.root);
        let mut node = Node::root(self.current, &evaluator.root);
        let checked = movegen::in_check(&self.current, self.current.side);
        let influence = Influence::build(&self.current);
        let mut details = None;
        let evaluation = evaluator.fresh_detailed_observed(
            &mut node, &influence, checked, |value| details = Some(value),
        );
        let FullDetails { components, base, finished, .. } = details.expect("fresh evaluation observes its result once");
        let subtotal = json!({
            "rootPhase":positions::phase_value(evaluator.root.phase),
            "currentPhase":positions::phase_value(self.current.phase()),
            "inCheck":checked,"components":components_output(components),
            "positionalSubtotal":node.retained.positional,"baseScore":base,
            "retained":common::retained_output(node.retained),
            "relationQueries":evaluation.relation_queries,
        });
        if !final_score {
            return subtotal;
        }
        // These values are produced by the actual native finishing call. The
        // standalone supplied finalScore late-input restriction does not apply.
        let mut output = common::finishing_output(&self.current, &evaluator, finished);
        output["subtotal"] = subtotal;
        output
    }
}

fn components_output(components: Components) -> Value {
    json!({"material":components.material,"squareBalance":components.squares,
        "pawnStructure":components.pawn_structure,"pawnProgress":components.pawn_progress,
        "activity":components.activity,"centralInfluence":components.central,
        "kingShelter":components.shelter,"bishopCoordination":components.bishops,
        "openingPatterns":components.patterns,"tempo":components.tempo})
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    let final_score = match operation {
        "evaluation.freshSubtotal" => false,
        "evaluation.freshScore" => true,
        _ => return Err(format!("unsupported fresh-evaluation operation: {operation}")),
    };
    object(input, &["queries"])?;
    // No evaluator/cache/influence work starts until every supplied query has
    // passed its complete schema, percentage and semantic order validation.
    let queries = array(&input["queries"], 1, 512)?.iter()
        .map(|query| Query::parse(query, final_score)).collect::<Result<Vec<_>>>()?;
    let results: Vec<_> = queries.into_iter().map(|query| query.observe(final_score)).collect();
    Ok(json!({"results":results}))
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::scores;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    const TIED: &str = "8/P1P5/8/8/3K3k/8/p7/8";

    fn query(final_score: bool) -> Value {
        let percentages: serde_json::Map<String, Value> = scores::NAMES.iter()
            .map(|name| (name.to_string(), json!(100))).collect();
        let mut query = json!({"rootPlacement":START,"placement":START,
            "rootSide":"white","sideToMove":"white","averageDepth":0,
            "percentages":{"own":percentages.clone(),"opponent":percentages},
            "pawnOrder":{"white":["a2","b2","c2","d2","e2","f2","g2","h2"],
                "black":["a7","b7","c7","d7","e7","f7","g7","h7"]}});
        if final_score {
            query["cfd"] = json!(0);
            query["sop"] = json!(100);
            query["reversiblePlies"] = json!(0);
        }
        query
    }

    fn current(query: &mut Value, placement: &str, white: &[&str], black: &[&str]) {
        query["placement"] = json!(placement);
        query["pawnOrder"] = json!({"white":white,"black":black});
    }

    fn result(operation: &str, query: Value) -> Value {
        dispatch(operation, &json!({"queries":[query]})).unwrap()["results"][0].clone()
    }

    #[test]
    fn fresh_subtotal_exposes_all_native_terms_retained_state_and_current_tempo() {
        let q = query(false);
        let white = result("evaluation.freshSubtotal", q.clone());
        assert_eq!(white["components"], json!({"material":0,"squareBalance":0,
            "pawnStructure":0,"pawnProgress":0,"activity":0,"centralInfluence":0,
            "kingShelter":0,"bishopCoordination":0,"openingPatterns":0,"tempo":6}));
        assert_eq!(white["baseScore"], 6);
        assert_eq!(white["positionalSubtotal"], 0);
        assert_eq!(white["retained"], json!({"positionalSubtotal":0,"pawnProgress":0,"evaluationAge":0}));
        assert_eq!(white["relationQueries"], 10);
        let mut black = q;
        black["sideToMove"] = json!("black");
        let black = result("evaluation.freshSubtotal", black);
        assert_eq!(black["components"]["tempo"], -6);
        assert_eq!(black["baseScore"], -6);
        assert_eq!(black["retained"], white["retained"]);
        assert_eq!(black["relationQueries"], 10);
    }

    #[test]
    fn explicit_pawn_order_changes_actual_progress_without_changing_identity_or_root() {
        let mut q = query(true);
        current(&mut q, TIED, &["a7","c7"], &["a2"]);
        let mut reversed = q.clone();
        reversed["pawnOrder"]["white"] = json!(["c7","a7"]);
        let out = dispatch("evaluation.freshScore", &json!({"queries":[q.clone(),reversed,q]})).unwrap();
        let results = &out["results"];
        assert_eq!(results[0]["identity"], results[1]["identity"]);
        assert_eq!(results[0]["variationIdentity"], results[1]["variationIdentity"]);
        assert_eq!(results[0]["subtotal"]["rootPhase"], json!({"opening":256,"middlegame":0,"endgame":0}));
        assert_eq!(results[0]["subtotal"]["currentPhase"], json!({"opening":0,"middlegame":0,"endgame":256}));
        assert_eq!(results[0]["subtotal"]["components"]["pawnProgress"].as_i64().unwrap()
            - results[1]["subtotal"]["components"]["pawnProgress"].as_i64().unwrap(), 300);
        assert_eq!(results[0]["subtotal"]["positionalSubtotal"], results[1]["subtotal"]["positionalSubtotal"]);
        assert_eq!(results[0], results[2]);
    }

    #[test]
    fn produced_late_base_is_not_rejected_by_the_supplied_final_score_domain() {
        // Released fresh-score-001: produced late-phase adjusted base is 11742.
        let mut q = query(true);
        current(&mut q, TIED, &["a7","c7"], &["a2"]);
        q["averageDepth"] = json!(-100);
        q["cfd"] = json!(10000);
        q["sop"] = json!(49);
        q["reversiblePlies"] = json!(12);
        let out = result("evaluation.freshScore", q);
        assert_eq!(out["subtotal"]["baseScore"], 1914);
        assert_eq!(out["drawPreference"], 10000);
        assert_eq!(out["variationRange"], 816);
        assert_eq!(out["adjustedBase"], 11742);
        assert_eq!(out["lateEndgame"], 9907);
        assert_eq!(out["scaledScore"], 7807);
        assert_eq!(out["score"], 7807);
        assert_eq!(out["subtotal"]["relationQueries"], 0);
    }

    #[test]
    fn geometric_check_and_reversible_zero_keep_produced_retained_pair_and_bounds() {
        let mut q = query(true);
        current(&mut q, "7k/8/8/8/8/8/1p6/K7", &[], &["b2"]);
        q["averageDepth"] = json!(-100);
        q["cfd"] = json!(101);
        q["sop"] = json!(99);
        q["reversiblePlies"] = json!(100);
        let out = result("evaluation.freshScore", q);
        assert_eq!(out["subtotal"]["inCheck"], true);
        assert_eq!(out["subtotal"]["components"]["tempo"], 0);
        assert_eq!(out["score"], 0);
        assert_eq!(out["lowerBound"], -10000);
        assert_eq!(out["upperBound"], 0);
        assert_eq!(out["subtotal"]["retained"], json!({"positionalSubtotal":10,"pawnProgress":-204,"evaluationAge":0}));
    }

    #[test]
    fn schema_validates_ignored_percentages_complete_orders_and_query_limits() {
        for field in ["phase","rootPhase","inCheck","baseScore","drawPreference","variationIdentity"] {
            let mut q = query(true);
            q[field] = json!(0);
            assert!(dispatch("evaluation.freshScore", &json!({"queries":[q]})).is_err());
        }
        for owner in ["own","opponent"] {
            let mut q = query(false);
            q["percentages"][owner]["king"] = json!(1001);
            assert!(dispatch("evaluation.freshSubtotal", &json!({"queries":[q.clone()]})).is_err());
            q["percentages"][owner]["king"] = json!(1000);
            assert!(Query::parse(&q, false).is_ok());
        }
        let mut invalid = query(true);
        invalid["pawnOrder"]["white"] = json!(["a2","a2","c2","d2","e2","f2","g2","h2"]);
        assert!(dispatch("evaluation.freshScore", &json!({"queries":[query(true),invalid]})).is_err());
        let mut missing = query(false);
        missing["pawnOrder"]["black"] = json!([]);
        assert!(dispatch("evaluation.freshSubtotal", &json!({"queries":[missing]})).is_err());
        assert!(dispatch("evaluation.freshScore", &json!({"queries":[]})).is_err());
        assert!(dispatch("evaluation.freshScore", &json!({"queries":vec![query(true);513]})).is_err());
        let mut broad = query(false);
        current(&mut broad, "8/8/8/8/8/8/k7/K7", &[], &[]);
        let out = result("evaluation.freshSubtotal", broad);
        assert_eq!(out["inCheck"], true);
        assert_eq!(out["components"]["tempo"], 0);
    }

    #[test]
    fn identities_come_only_from_current_placement_across_independent_contexts() {
        let q = query(true);
        let mut altered = q.clone();
        altered["rootPlacement"] = json!("7k/8/8/8/8/8/8/K7");
        altered["rootSide"] = json!("black");
        altered["sideToMove"] = json!("black");
        altered["reversiblePlies"] = json!(255);
        let out = dispatch("evaluation.freshScore", &json!({"queries":[q.clone(),altered,q]})).unwrap();
        assert_eq!(out["results"][0]["identity"], out["results"][1]["identity"]);
        assert_eq!(out["results"][0]["variationIdentity"], out["results"][1]["variationIdentity"]);
        assert_eq!(out["results"][1]["subtotal"]["rootPhase"], json!({"opening":0,"middlegame":0,"endgame":256}));
        assert_eq!(out["results"][1]["subtotal"]["currentPhase"], out["results"][0]["subtotal"]["currentPhase"]);
        assert_eq!(out["results"][0], out["results"][2]);
    }
}
