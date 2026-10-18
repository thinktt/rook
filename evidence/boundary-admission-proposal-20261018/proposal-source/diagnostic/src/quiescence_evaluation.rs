//! Admitted non-check evaluation and immediate disposition, without a Q search.
use super::{array, evaluation_common as common, integer, object, positions, text, Result};
use rook2::{
    evaluator::{Evaluation, Evaluator, FastDetails, FullDetails, Node, Parameters, Retained},
    influence::Influence,
    movegen,
    position::Position,
    quiescence_policy::{self as policy, EvaluationReturn},
    types::Move,
};
use serde_json::{json, Value};
use std::cell::Cell;

#[derive(Clone, Copy)]
enum Kind { Full, Fast }

impl Kind {
    fn parse(value: &Value) -> Result<Self> {
        match text(value)? {
            "full" => Ok(Self::Full),
            "fast" => Ok(Self::Fast),
            _ => Err("evaluation kind must be full or fast".into()),
        }
    }
}

#[derive(Clone, Copy)]
enum Details { Full(FullDetails), Fast(FastDetails) }

struct Transition { movement: Option<Move>, kind: Kind }

struct Request {
    root: Position,
    initial_placement: String,
    parameters: Parameters,
    history: Vec<Transition>,
    final_move: Move,
    alpha: i32,
    beta: i32,
}

impl Request {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["fen", "percentages", "averageDepth", "cfd", "sop",
            "history", "move", "alpha", "beta"])?;
        let parameters = common::parameters(input, true)?;
        let fen = text(&input["fen"])?;
        let root = positions::sequence_position(fen, true)?;
        let alpha = integer(&input["alpha"], -10000, 10000)?;
        let beta = integer(&input["beta"], -10000, 10000)?;
        if alpha >= beta { return Err("alpha must be strictly below beta".into()); }
        let supplied = array(&input["history"], 0, 255)?.iter().map(|step| {
            object(step, &["move", "kind"])?;
            let kind = Kind::parse(&step["kind"])?;
            let movement = if step["move"].is_null() { None } else { Some(text(&step["move"])?) };
            Ok((movement, kind))
        }).collect::<Result<Vec<_>>>()?;
        let final_spelling = text(&input["move"])?;
        // Validate the complete legal path on cold Position copies before any
        // evaluator, pawn cache, retained pair, or evaluation stage is created.
        let mut current = root;
        let mut history = Vec::with_capacity(supplied.len());
        for (spelling, kind) in supplied {
            let movement = if let Some(spelling) = spelling {
                let (child, movement) = positions::advance_with_move(&current, spelling)?;
                current = child;
                Some(movement)
            } else {
                if movegen::in_check(&current, current.side)
                    || movegen::in_check(&current, current.side.opponent())
                {
                    return Err("null history transition requires neither king checked".into());
                }
                current = current.null_child();
                None
            };
            history.push(Transition { movement, kind });
        }
        let (final_position, final_move) = positions::advance_with_move(&current, final_spelling)?;
        if movegen::in_check(&final_position, final_position.side) {
            return Err("final side to move must not be in check".into());
        }
        Ok(Self { root, initial_placement:fen.split(' ').next().unwrap().into(),
            parameters, history, final_move, alpha, beta })
    }

    fn observe(self, disposition: bool) -> Value {
        let mut evaluator = Evaluator::<true>::new(&self.root);
        evaluator.parameters = self.parameters;
        evaluator.begin_search(&self.root);
        let mut node = Node::root(self.root, &evaluator.root);
        let mut results = Vec::with_capacity(self.history.len() + 2);
        let (evaluation, details) = evaluate(&mut evaluator, &mut node, Kind::Full);
        let mut initial = record(&evaluator, &node, evaluation, details, None);
        initial["state"]["placement"] = json!(self.initial_placement);
        results.push(initial);
        for step in self.history {
            node = if let Some(movement) = step.movement {
                node.child(&evaluator.root, movement)
            } else {
                node.null_child()
            };
            let inherited = node.retained;
            let (evaluation, details) = evaluate(&mut evaluator, &mut node, step.kind);
            results.push(record(&evaluator, &node, evaluation, details, Some(inherited)));
        }
        // Classify exactly the pre-transition parent/victim, including promotion
        // and the empty-destination exclusion for ordinary en passant.
        let capture_exception = policy::capture_exception(&node.position, &self.final_move);
        node = node.child(&evaluator.root, self.final_move);
        let inherited = node.retained;
        let observed = Cell::new(None);
        let mut scratch = None;
        let selected = evaluator.select_noncheck_detailed_observed(
            &mut node, self.alpha, self.beta, capture_exception, &mut scratch,
            |details| observed.set(Some(Details::Full(details))),
            |details| observed.set(Some(Details::Fast(details))),
        );
        let details = observed.get().expect("native selection observes its actual stages");
        let mut final_record = record(&evaluator, &node, selected.evaluation, details, Some(inherited));
        final_record["selection"] = json!({
            "initialKind":if selected.initially_full { "full" } else { "fast" },
            "fastScore":selected.fast_score,"refreshed":selected.refreshed});
        if disposition {
            final_record["disposition"] = disposition_output(policy::evaluation_return(
                selected.evaluation.lower, selected.evaluation.upper, selected.evaluation.score,
                self.alpha, self.beta));
        }
        results.push(final_record);
        json!({"results":results})
    }
}

fn evaluate(evaluator: &mut Evaluator<true>, node: &mut Node, kind: Kind) -> (Evaluation, Details) {
    let checked = movegen::in_check(&node.position, node.position.side);
    let mut details = None;
    let evaluation = match kind {
        Kind::Full => {
            let influence = Influence::build(&node.position);
            evaluator.full_detailed_observed(node, &influence, checked,
                |value| details = Some(Details::Full(value)))
        }
        Kind::Fast => evaluator.fast_detailed_observed(node, checked,
            |value| details = Some(Details::Fast(value))),
    };
    (evaluation, details.expect("native full/fast evaluation observes one result"))
}

fn record(evaluator: &Evaluator<true>, node: &Node, evaluation: Evaluation,
    details: Details, inherited: Option<Retained>) -> Value
{
    let (kind, base, finished, reused) = match details {
        Details::Full(value) => ("full", value.base, value.finished, Some(value.pawn_entry_reused)),
        Details::Fast(value) => ("fast", value.base, value.finished, None),
    };
    let position = &node.position;
    let mut output = common::finishing_output(position, evaluator, finished);
    output["kind"] = json!(kind);
    output["rootPhase"] = positions::phase_value(evaluator.root.phase);
    output["currentPhase"] = positions::phase_value(position.phase());
    output["inCheck"] = json!(movegen::in_check(position, position.side));
    output["baseScore"] = json!(base);
    output["retained"] = common::retained_output(node.retained);
    output["relationQueries"] = json!(evaluation.relation_queries);
    output["pawnEntryReused"] = json!(reused);
    output["state"] = positions::state(position);
    output["inherited"] = inherited.map(common::retained_output).unwrap_or(Value::Null);
    output
}

fn disposition_output(returned: Option<EvaluationReturn>) -> Value {
    match returned {
        Some(value) => {
            let reason = match value {
                EvaluationReturn::LowerBound(_) => "lower-bound",
                EvaluationReturn::UpperBound(_) => "upper-bound",
                EvaluationReturn::StandPat(_) => "stand-pat",
            };
            json!({"action":"return","reason":reason,"score":value.score()})
        }
        None => json!({"action":"tactical","reason":null,"score":null}),
    }
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    let disposition = match operation {
        "evaluation.quiescenceEntry" => false,
        "evaluation.quiescenceDisposition" => true,
        _ => return Err("unsupported quiescence evaluation operation".into()),
    };
    Ok(Request::parse(input)?.observe(disposition))
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::scores;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn request(fen: &str, movement: &str) -> Value {
        let percentages: serde_json::Map<String, Value> = scores::NAMES.iter()
            .map(|name| (name.to_string(), json!(100))).collect();
        json!({"fen":fen,"move":movement,"history":[],"alpha":-10000,"beta":10000,
            "averageDepth":0,"cfd":0,"sop":100,
            "percentages":{"own":percentages.clone(),"opponent":percentages}})
    }

    fn entry(input: &Value) -> Value {
        dispatch("evaluation.quiescenceEntry", input).unwrap()
    }

    fn last(output: &Value) -> &Value {
        output["results"].as_array().unwrap().last().unwrap()
    }

    fn outside_fast_window(mut input: Value, above: bool) -> Value {
        let fast = last(&entry(&input))["selection"]["fastScore"].as_i64().unwrap();
        if above {
            input["alpha"] = json!(fast + 250);
            input["beta"] = json!(fast + 251);
        } else {
            input["alpha"] = json!(fast - 251);
            input["beta"] = json!(fast - 250);
        }
        input
    }

    #[test]
    fn sparse_final_selection_has_no_fast_score_and_preserves_zero_identity_reuse() {
        let output = entry(&request("7k/8/8/8/8/8/8/K7 w - - 0 1", "a1b1"));
        assert_eq!(output["results"].as_array().unwrap().len(), 2);
        assert_eq!(last(&output)["selection"], json!({"initialKind":"full","fastScore":null,"refreshed":false}));
        assert_eq!(last(&output)["kind"], "full");
        assert_eq!(last(&output)["pawnEntryReused"], true);
        assert_eq!(last(&output)["inherited"]["evaluationAge"], 1);
        assert_eq!(last(&output)["retained"]["evaluationAge"], 0);
        assert_eq!(last(&output)["relationQueries"], 0);
        assert!(output["results"][0]["inherited"].is_null());
        assert!(output["results"][0].get("selection").is_none());
    }

    #[test]
    fn quiet_final_move_uses_strict_fast_endpoints_and_actual_refresh_details() {
        let input = request(START, "e2e4");
        let refreshed = entry(&input);
        assert_eq!(last(&refreshed)["selection"]["initialKind"], "fast");
        assert_eq!(last(&refreshed)["selection"]["refreshed"], true);
        assert_eq!(last(&refreshed)["kind"], "full");
        assert_eq!(last(&refreshed)["retained"]["evaluationAge"], 0);
        for above in [true, false] {
            let endpoint = outside_fast_window(input.clone(), above);
            let output = entry(&endpoint);
            let final_result = last(&output);
            assert_eq!(final_result["selection"]["refreshed"], false);
            assert_eq!(final_result["kind"], "fast");
            assert_eq!(final_result["score"], final_result["selection"]["fastScore"]);
            assert_eq!(final_result["retained"], final_result["inherited"]);
            assert_eq!(final_result["retained"]["evaluationAge"], 1);
            assert_eq!(final_result["relationQueries"], 0);
            assert!(final_result["pawnEntryReused"].is_null());
        }
        assert_eq!(entry(&input), refreshed);
    }

    #[test]
    fn capture_exception_uses_parent_victim_and_excludes_empty_ep_destination() {
        let ep = request("4k2r/8/8/3pP3/8/8/8/R3K2R w KQk d6 0 1", "e5d6");
        let ordinary = request("4k2r/8/3p4/4P3/8/8/8/R3K2R w KQk - 0 1", "e5d6");
        let ep_output = entry(&outside_fast_window(ep, true));
        let ordinary_output = entry(&outside_fast_window(ordinary, true));
        assert_eq!(last(&ep_output)["selection"]["refreshed"], false);
        assert_eq!(last(&ep_output)["kind"], "fast");
        assert_eq!(last(&ep_output)["state"]["halfmoveClock"], 0);
        assert_eq!(last(&ordinary_output)["selection"]["refreshed"], true);
        assert_eq!(last(&ordinary_output)["kind"], "full");
        assert_eq!(last(&ordinary_output)["retained"]["evaluationAge"], 0);
    }

    #[test]
    fn promotion_refresh_keeps_fixed_root_context_and_requires_a_suffix() {
        let mut input = request("7r/P5k1/8/8/8/8/8/R3K2R w KQ - 0 1", "a7a8q");
        input["averageDepth"] = json!(7);
        input["cfd"] = json!(31);
        input["sop"] = json!(73);
        let output = entry(&outside_fast_window(input.clone(), true));
        assert_eq!(last(&output)["selection"]["initialKind"], "fast");
        assert_eq!(last(&output)["selection"]["refreshed"], true);
        assert_ne!(last(&output)["rootPhase"], last(&output)["currentPhase"]);
        assert_eq!(last(&output)["rootPhase"], output["results"][0]["rootPhase"]);
        assert_eq!(last(&output)["drawPreference"], output["results"][0]["drawPreference"]);
        assert_eq!(last(&output)["variationRange"], output["results"][0]["variationRange"]);
        input["move"] = json!("a7a8");
        assert!(Request::parse(&input).is_err());
    }

    #[test]
    fn null_fast_history_continues_through_reversible_and_age_wraparound() {
        let mut input = request(&START.replace(" 0 1", " 255 1"), "e7e5");
        input["history"] = json!(vec![json!({"move":null,"kind":"fast"});255]);
        let output = entry(&outside_fast_window(input, true));
        let results = output["results"].as_array().unwrap();
        assert_eq!(results.len(), 257);
        assert_eq!(results[255]["retained"]["evaluationAge"], 255);
        assert_eq!(results[255]["state"]["halfmoveClock"], 254);
        assert_eq!(last(&output)["inherited"]["evaluationAge"], 0);
        assert_eq!(last(&output)["retained"]["evaluationAge"], 0);
        assert_eq!(last(&output)["state"]["halfmoveClock"], 0);
        assert_eq!(last(&output)["kind"], "fast");
        assert_eq!(results[1]["state"]["pieceOrder"], results[0]["state"]["pieceOrder"]);
        assert_eq!(results[1]["state"]["identity"], results[0]["state"]["identity"]);
        assert_eq!(results[1]["retained"]["positionalSubtotal"], results[0]["retained"]["positionalSubtotal"]);
    }

    #[test]
    fn disposition_adds_no_work_or_state_and_reports_tactical_or_unclipped_stand_pat() {
        let input = request(START, "e2e4");
        let expected = entry(&input);
        let mut output = dispatch("evaluation.quiescenceDisposition", &input).unwrap();
        let disposition = output["results"].as_array_mut().unwrap().last_mut().unwrap()
            .as_object_mut().unwrap().remove("disposition").unwrap();
        assert_eq!(disposition, json!({"action":"tactical","reason":null,"score":null}));
        assert_eq!(output, expected);
        let input = outside_fast_window(input, false);
        let output = dispatch("evaluation.quiescenceDisposition", &input).unwrap();
        assert_eq!(last(&output)["disposition"]["reason"], "stand-pat");
        assert_eq!(last(&output)["disposition"]["score"], last(&output)["score"]);
        assert!(last(&output)["disposition"]["score"].as_i64().unwrap() > input["beta"].as_i64().unwrap());
        assert_eq!(last(&output)["relationQueries"], 0);
    }

    #[test]
    fn exact_fields_and_ignored_king_percentages_validate_before_selection() {
        let input = request(START, "e2e4");
        for field in ["pawnOrder", "kind", "rootSide", "rootPhase", "retained", "steps", "identity"] {
            let mut bad = input.clone(); bad[field] = Value::Null;
            assert!(Request::parse(&bad).is_err());
        }
        let mut bad = input.clone(); bad["percentages"]["opponent"]["king"] = json!(1001);
        assert!(Request::parse(&bad).is_err());
        bad["percentages"]["opponent"]["king"] = json!(1000);
        assert!(Request::parse(&bad).is_ok());
        let mut bad = input.clone(); bad["history"] = json!([
            {"move":null,"kind":"fast"},{"move":null,"kind":"fast","pawnOrder":{}}]);
        assert!(Request::parse(&bad).is_err());
        let mut bad = input.clone(); bad["history"] = json!([{"move":null,"kind":"unknown"}]);
        assert!(Request::parse(&bad).is_err());
        let mut bad = input.clone(); bad["alpha"] = json!(0); bad["beta"] = json!(0);
        assert!(Request::parse(&bad).is_err());
        let mut bad = input.clone(); bad["alpha"] = json!(-10001);
        assert!(Request::parse(&bad).is_err());
        let mut bad = input.clone(); bad["beta"] = json!(1.5);
        assert!(Request::parse(&bad).is_err());
        let mut bad = input.clone(); bad["move"] = Value::Null;
        assert!(Request::parse(&bad).is_err());
        let mut bad = input; bad["history"] = json!(vec![json!({"move":null,"kind":"fast"});256]);
        assert!(Request::parse(&bad).is_err());
    }

    #[test]
    fn checked_history_evaluation_is_allowed_before_a_noncheck_final_position() {
        let mut input = request("7k/8/8/8/8/8/8/KR6 w - - 0 1", "h8h7");
        input["history"] = json!([{"move":"b1b8","kind":"fast"}]);
        let output = entry(&input);
        assert_eq!(output["results"][1]["inCheck"], true);
        assert_eq!(output["results"][1]["kind"], "fast");
        assert_eq!(output["results"][1]["relationQueries"], 0);
        assert_eq!(output["results"][1]["retained"]["evaluationAge"], 1);
        assert_eq!(last(&output)["inCheck"], false);
        assert_eq!(last(&output)["kind"], "full");
        assert_eq!(last(&output)["inherited"]["evaluationAge"], 2);
        assert_eq!(last(&output)["retained"]["evaluationAge"], 0);
    }

    #[test]
    fn final_check_null_check_and_illegal_coordinate_moves_are_rejected() {
        assert!(Request::parse(&request("7k/8/8/8/8/8/8/KR6 w - - 0 1", "b1h1")).is_err());
        for fen in ["7k/8/8/8/8/8/r7/K7 w - - 0 1", "7k/8/8/8/8/8/8/K6R w - - 0 1"] {
            let mut input = request(fen, "a1b1");
            input["history"] = json!([{"move":null,"kind":"full"}]);
            assert!(Request::parse(&input).is_err());
        }
        for spelling in ["e2e5", "e2e4q", "E2e4", "0000"] {
            assert!(Request::parse(&request(START, spelling)).is_err());
        }
    }

    #[test]
    fn setup_normalizes_rights_and_ep_without_resetting_the_reversible_counter() {
        let output = entry(&request("7k/8/8/8/8/8/8/K7 w KQkq e6 255 1", "a1b1"));
        assert_eq!(output["results"][0]["state"]["castling"], "-");
        assert_eq!(output["results"][0]["state"]["enPassant"], "-");
        assert_eq!(output["results"][0]["state"]["halfmoveClock"], 255);
        assert_eq!(last(&output)["state"]["halfmoveClock"], 0);
        assert_eq!(last(&output)["inherited"]["evaluationAge"], 1);
    }
}
