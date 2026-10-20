//! Fixed-root controlled full/fast sequence over one native evaluator lifetime.
use super::{array, color, evaluation_common as common, integer, object, positions, text, Result};
use rook2::{
    evaluator::{Evaluator, FastDetails, FullDetails, Node, Parameters},
    influence::Influence,
    movegen,
    position::Position,
};
use serde_json::{json, Value};

#[derive(Clone, Copy, PartialEq, Eq)]
enum Kind {
    Full,
    Fast,
}

impl Kind {
    fn parse(value: &Value) -> Result<Self> {
        match text(value)? {
            "full" => Ok(Self::Full),
            "fast" => Ok(Self::Fast),
            _ => Err("evaluation kind must be full or fast".into()),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Full => "full",
            Self::Fast => "fast",
        }
    }
}

struct Step {
    kind: Kind,
    position: Position,
}

struct Request {
    parameters: Parameters,
    steps: Vec<Step>,
}

impl Request {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["rootSide", "averageDepth", "percentages", "cfd", "sop", "positions"])?;
        let root_side = color(&input["rootSide"])?;
        let parameters = common::parameters(input, true)?;
        // Validate every position and order before considering first-position
        // gates or creating the evaluator and its retained pawn cache.
        let steps = array(&input["positions"], 1, 512)?.iter().map(|value| {
            object(value, &["kind", "placement", "sideToMove", "pawnOrder", "reversiblePlies"])?;
            let kind = Kind::parse(&value["kind"])?;
            let mut position = positions::placement(&value["placement"], true)?;
            position.side = color(&value["sideToMove"])?;
            position.halfmove = integer(&value["reversiblePlies"], 0, 255)? as u8;
            common::apply_pawn_order(&mut position, &value["pawnOrder"])?;
            Ok(Step { kind, position })
        }).collect::<Result<Vec<_>>>()?;
        if steps[0].kind != Kind::Full {
            return Err("first evaluation must be full".into());
        }
        if steps[0].position.side != root_side {
            return Err("first position side must equal rootSide".into());
        }
        Ok(Self { parameters, steps })
    }

    fn observe(self) -> Value {
        let root = self.steps[0].position;
        let mut evaluator = Evaluator::<true>::new(&root);
        evaluator.parameters = self.parameters;
        evaluator.begin_search(&root);
        let mut pair = (0, 0);
        let mut results = Vec::with_capacity(self.steps.len());
        for step in self.steps {
            // Controlled placements are not moves: recompute only the current
            // root-valued nonking square state and carry the last produced pair.
            // Node::root establishes age zero; fast preserves it and full resets it.
            let mut node = Node::root(step.position, &evaluator.root);
            node.retained.positional = pair.0;
            node.retained.pawn_progress = pair.1;
            let checked = movegen::in_check(&step.position, step.position.side);
            let (evaluation, base, finished, reused) = match step.kind {
                Kind::Full => {
                    let influence = Influence::build(&step.position);
                    let mut details = None;
                    let evaluation = evaluator.full_detailed_observed(
                        &mut node, &influence, checked, |value| details = Some(value),
                    );
                    let FullDetails { base, finished, pawn_entry_reused, .. } =
                        details.expect("full evaluation observes one result");
                    (evaluation, base, finished, Some(pawn_entry_reused))
                }
                Kind::Fast => {
                    // No influence is constructed, and the native fast owner
                    // performs no pawn selection or mutation of this node.
                    let mut details = None;
                    let evaluation = evaluator.fast_detailed_observed(
                        &node, checked, |value| details = Some(value),
                    );
                    let FastDetails { base, finished } =
                        details.expect("fast evaluation observes one result");
                    (evaluation, base, finished, None)
                }
            };
            pair = (node.retained.positional, node.retained.pawn_progress);
            let mut output = common::finishing_output(&step.position, &evaluator, finished);
            output["kind"] = json!(step.kind.name());
            output["rootPhase"] = positions::phase_value(evaluator.root.phase);
            output["currentPhase"] = positions::phase_value(step.position.phase());
            output["inCheck"] = json!(checked);
            output["baseScore"] = json!(base);
            output["retained"] = common::retained_output(node.retained);
            output["relationQueries"] = json!(evaluation.relation_queries);
            output["pawnEntryReused"] = json!(reused);
            results.push(output);
        }
        json!({"results":results})
    }
}

pub(super) fn dispatch(input: &Value) -> Result<Value> {
    Ok(Request::parse(input)?.observe())
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::scores;
    use rook2::types::{Color, PieceKind};

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    const TIED: &str = "8/P1P5/8/8/3K3k/8/p7/8";
    const COLLISION_A: &str = "7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7";
    const COLLISION_B: &str = "7k/8/2p4P/2p5/7P/1p6/p5PP/K7";
    const GROUP_A: &str = "7k/8/8/8/6P1/3P4/8/K7";
    const GROUP_C: &str = "7k/8/6P1/8/8/3P4/8/K7";
    const EMPTY: &str = "7k/8/8/8/8/8/8/K7";

    fn step(kind: &str, placement: &str, white: &[&str], black: &[&str]) -> Value {
        json!({"kind":kind,"placement":placement,"sideToMove":"white","reversiblePlies":0,
            "pawnOrder":{"white":white,"black":black}})
    }

    fn automatic(kind: &str, placement: &str) -> Value {
        let position = positions::placement(&json!(placement), true).unwrap();
        let names = |side| position.piece_squares(side, PieceKind::Pawn).iter()
            .map(|square| square.to_string()).collect::<Vec<_>>();
        json!({"kind":kind,"placement":placement,"sideToMove":"white","reversiblePlies":0,
            "pawnOrder":{"white":names(Color::White),"black":names(Color::Black)}})
    }

    fn request(steps: Vec<Value>) -> Value {
        let percentages: serde_json::Map<String, Value> = scores::NAMES.iter()
            .map(|name| (name.to_string(), json!(100))).collect();
        json!({"rootSide":"white","averageDepth":0,"cfd":0,"sop":100,
            "percentages":{"own":percentages.clone(),"opponent":percentages},"positions":steps})
    }

    #[test]
    fn full_collision_reuses_actual_descriptors_while_fast_preserves_the_produced_pair() {
        let a = step("full", COLLISION_A, &["g7","e6","f5","e2"], &["b6","d6","e5","c3"]);
        let b_fast = step("fast", COLLISION_B, &["h6","h4","g2","h2"], &["c6","c5","b3","a2"]);
        let mut b_full = b_fast.clone();
        b_full["kind"] = json!("full");
        let reversed_a = step("full", COLLISION_A, &["e2","f5","e6","g7"], &["c3","e5","d6","b6"]);
        let mut input = request(vec![a,b_fast,b_full,reversed_a]);
        input["averageDepth"] = json!(-100);
        input["cfd"] = json!(-10000);
        input["sop"] = json!(0);
        let out = dispatch(&input).unwrap();
        let r = &out["results"];
        assert_eq!(r[0]["identity"]["pawn"], r[1]["identity"]["pawn"]);
        assert_eq!(r[0]["baseScore"], 592);
        assert_eq!(r[1]["baseScore"], 554);
        assert_eq!(r[2]["baseScore"], -32);
        assert_eq!(r[3]["baseScore"], 592);
        assert_eq!(r[0]["pawnEntryReused"], false);
        assert!(r[1]["pawnEntryReused"].is_null());
        assert_eq!(r[2]["pawnEntryReused"], true);
        assert_eq!(r[3]["pawnEntryReused"], true);
        assert_eq!(r[0]["retained"], json!({"positionalSubtotal":-17,"pawnProgress":583,"evaluationAge":0}));
        assert_eq!(r[1]["retained"], r[0]["retained"]);
        assert_eq!(r[2]["retained"], json!({"positionalSubtotal":-16,"pawnProgress":0,"evaluationAge":0}));
        assert_eq!(r[1]["relationQueries"], 0);
        assert_eq!(dispatch(&input).unwrap(), out);
    }

    #[test]
    fn fast_positions_cannot_evict_a_same_group_pawn_entry() {
        let input = request(vec![automatic("full",GROUP_A),automatic("fast",GROUP_C),
            automatic("full",GROUP_A),automatic("full",GROUP_C),automatic("full",GROUP_A)]);
        let out = dispatch(&input).unwrap();
        let r = &out["results"];
        assert_eq!(r[0]["identity"]["pawnGroup"], r[1]["identity"]["pawnGroup"]);
        assert_ne!(r[0]["identity"]["pawn"], r[1]["identity"]["pawn"]);
        assert_eq!(r[1]["retained"], r[0]["retained"]);
        assert!(r[1]["pawnEntryReused"].is_null());
        assert_eq!(r[2]["pawnEntryReused"], true);
        assert_eq!(r[3]["pawnEntryReused"], false);
        assert_eq!(r[4]["pawnEntryReused"], false);
    }

    #[test]
    fn cleared_zero_identity_and_group_zero_replacement_are_not_forced_fresh() {
        let input = request(vec![automatic("full",EMPTY),automatic("fast",EMPTY),
            automatic("full",GROUP_A),automatic("fast",EMPTY),automatic("full",GROUP_A),
            automatic("full",EMPTY),automatic("full",EMPTY)]);
        let out = dispatch(&input).unwrap();
        let reused: Vec<_> = out["results"].as_array().unwrap().iter()
            .map(|result| result["pawnEntryReused"].clone()).collect();
        assert_eq!(reused, vec![json!(true),Value::Null,json!(false),Value::Null,json!(true),json!(false),json!(true)]);
        for result in out["results"].as_array().unwrap() {
            assert_eq!(result["retained"]["evaluationAge"], 0);
        }
    }

    #[test]
    fn supplied_order_changes_only_the_first_miss_and_remains_validated_on_hits() {
        let first = step("full",TIED,&["a7","c7"],&["a2"]);
        let reversed = step("full",TIED,&["c7","a7"],&["a2"]);
        let out = dispatch(&request(vec![first.clone(),reversed.clone()])).unwrap();
        assert_eq!(out["results"][1]["pawnEntryReused"], true);
        assert_eq!(out["results"][0]["retained"], out["results"][1]["retained"]);
        assert_eq!(out["results"][0]["baseScore"], out["results"][1]["baseScore"]);
        let second_request = dispatch(&request(vec![reversed.clone()])).unwrap();
        assert_eq!(out["results"][0]["retained"]["pawnProgress"].as_i64().unwrap()
            - second_request["results"][0]["retained"]["pawnProgress"].as_i64().unwrap(), 300);
        let mut invalid = reversed;
        invalid["pawnOrder"]["white"] = json!(["a7","a7"]);
        assert!(Request::parse(&request(vec![first,invalid])).is_err());
    }

    #[test]
    fn fast_rebuilds_current_squares_without_rebinding_the_root_or_adding_relation_work() {
        let middle = step("full","r3k2r/pp1n1ppp/2pbpn2/q7/2BP4/2N1PN2/PPQ2PPP/R3K2R",
            &["d4","e3","a2","b2","f2","g2","h2"],&["a7","b7","f7","g7","h7","c6","e6"]);
        let mut fast = step("fast","7k/8/2N5/3P4/8/8/8/K7",&["d5"],&[]);
        fast["sideToMove"] = json!("black");
        fast["reversiblePlies"] = json!(11);
        let mut input = request(vec![automatic("full",START),middle,fast]);
        input["averageDepth"] = json!(-100);
        input["cfd"] = json!(-10000);
        input["sop"] = json!(0);
        let out = dispatch(&input).unwrap();
        let r = &out["results"];
        assert_eq!(r[2]["rootPhase"], json!({"opening":256,"middlegame":0,"endgame":0}));
        assert_eq!(r[2]["currentPhase"], json!({"opening":0,"middlegame":0,"endgame":256}));
        assert_eq!(r[2]["drawPreference"], -10000);
        assert_eq!(r[2]["baseScore"], 1888);
        assert_eq!(r[2]["retained"], r[1]["retained"]);
        assert_eq!(r[1]["relationQueries"], 2);
        assert_eq!(r[2]["relationQueries"], 0);
        assert_eq!(r[2]["upperBound"], 0);
    }

    #[test]
    fn fast_finishing_uses_current_counter_and_does_not_store_the_finished_score() {
        let first = step("full",TIED,&["a7","c7"],&["a2"]);
        let mut fast = first.clone();
        fast["kind"] = json!("fast");
        fast["reversiblePlies"] = json!(100);
        let out = dispatch(&request(vec![first,fast.clone(),fast])).unwrap();
        assert_ne!(out["results"][0]["score"], 0);
        assert_eq!(out["results"][1]["score"], 0);
        assert_eq!(out["results"][2]["score"], 0);
        assert_eq!(out["results"][1]["retained"], out["results"][0]["retained"]);
        assert_eq!(out["results"][2]["retained"], out["results"][0]["retained"]);
        assert_eq!(out["results"][1]["retained"]["evaluationAge"], 0);
    }

    #[test]
    fn all_schemas_orders_and_initial_requirements_validate_before_native_work() {
        let good = automatic("full",START);
        let mut bad_kind = good.clone();
        bad_kind["kind"] = json!("fast");
        assert!(Request::parse(&request(vec![bad_kind])).is_err());
        let mut mismatch = request(vec![good.clone()]);
        mismatch["rootSide"] = json!("black");
        assert!(Request::parse(&mismatch).is_err());
        let mut invalid_fast = automatic("fast",START);
        invalid_fast["pawnOrder"]["white"] = json!([]);
        assert!(Request::parse(&request(vec![good.clone(),invalid_fast])).is_err());
        for field in ["phase","identity","retained","clear","percentages","baseScore"] {
            let mut extra = good.clone();
            extra[field] = json!(0);
            assert!(Request::parse(&request(vec![good.clone(),extra])).is_err());
        }
        let mut ignored = request(vec![good.clone()]);
        ignored["percentages"]["opponent"]["king"] = json!(1001);
        assert!(Request::parse(&ignored).is_err());
        ignored["percentages"]["opponent"]["king"] = json!(1000);
        assert!(Request::parse(&ignored).is_ok());
        assert!(Request::parse(&request(vec![])).is_err());
        assert!(Request::parse(&request(vec![good;513])).is_err());
        let broad = step("full","8/8/8/8/8/8/k7/K7",&[],&[]);
        assert_eq!(dispatch(&request(vec![broad])).unwrap()["results"][0]["inCheck"], true);
    }
}
