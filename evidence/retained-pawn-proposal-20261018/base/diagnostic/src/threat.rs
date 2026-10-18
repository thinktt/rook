//! Cold material-threat schemas and native fast-cutoff producer/consumer composition.
use super::{array, boolean, color, integer, moves, object, positions, Result};
use rook2::{
    evaluation::RootContext, influence::Influence, ordinary_policy, position::Position,
    quiescence_policy, types::PieceKind,
};
use serde_json::{json, Value};
use std::collections::HashSet;

struct ThreatContext {
    position: Position,
    root: RootContext,
    progress: i32,
    repetitions: usize,
}

impl ThreatContext {
    fn parse(input: &Value) -> Result<Self> {
        object(
            input,
            &[
                "placement",
                "side",
                "values",
                "squareAdjustments",
                "passedPawnBalance",
                "repetitions",
            ],
        )?;
        // Component placements admit adjacent/attacked kings and synthetic
        // boards. The shared placement schema enforces all count/rank bounds.
        let mut position = positions::placement(&input["placement"], true)?;
        position.side = color(&input["side"])?;
        let mut root = RootContext::neutral(&position);
        object(&input["values"], &moves::COLORS)?;
        for (side, name) in moves::COLORS.iter().enumerate() {
            let values = &input["values"][*name];
            object(values, &moves::PIECES[..5])?;
            for (kind, name) in moves::PIECES[..5].iter().enumerate() {
                root.values[side][kind] = integer(&values[*name], 0, 10000)?;
            }
        }
        // Values are already color-oriented; no rank reflection or side swap.
        root.squares = [[[0; 64]; 5]; 2];
        let mut seen = HashSet::new();
        for entry in array(&input["squareAdjustments"], 0, 768)? {
            object(entry, &["side", "piece", "square", "value"])?;
            let side = color(&entry["side"])?;
            let kind = moves::piece(&entry["piece"])?;
            if kind == PieceKind::King {
                return Err("king has no supplied square adjustment".into());
            }
            let square = positions::square(&entry["square"])?;
            let value = integer(&entry["value"], -128, 127)?;
            if !seen.insert((side.index(), kind.index(), square.0)) {
                return Err("duplicate square-adjustment key".into());
            }
            if !(-10000..=10000).contains(&(root.values[side.index()][kind.index()] + value)) {
                return Err("material plus square adjustment outside component domain".into());
            }
            root.squares[side.index()][kind.index()][square.0 as usize] = value as i16;
        }
        Ok(Self {
            position,
            root,
            progress: integer(&input["passedPawnBalance"], -10000, 10000)?,
            repetitions: integer(&input["repetitions"], 1, 16)? as usize,
        })
    }

    fn observe(&self, influence: &Influence) -> ordinary_policy::Threat {
        ordinary_policy::material_threat(&self.position, &self.root, influence, self.progress)
    }
}

fn material_threat(input: &Value) -> Result<Value> {
    let context = ThreatContext::parse(input)?;
    let influence = Influence::build(&context.position);
    let mut threat = 0;
    let mut charges = 0u64;
    // Reusing the unchanged map does not waive any observation's relation work.
    for _ in 0..context.repetitions {
        let observed = context.observe(&influence);
        threat = observed.value;
        charges += observed.queries;
    }
    Ok(json!({"threat":threat,"chargedRelationQueries":charges}))
}

fn fast_threat(input: &Value) -> Result<Value> {
    object(
        input,
        &[
            "previousPlacement",
            "threatContext",
            "searchPly",
            "targetPly",
            "staticScore",
            "upperBound",
            "currentCheck",
            "previousCheck",
            "previousMove",
        ],
    )?;
    // Validate every supplied field before any lazy work gate, including unused
    // value entries and independent board/check/move facts. Do not replay moves
    // or apply the normal caller's narrower fast-entry eligibility conditions.
    let previous = positions::placement(&input["previousPlacement"], true)?;
    let context = ThreatContext::parse(&input["threatContext"])?;
    let ply = integer(&input["searchPly"], 1, 62)?;
    let target = integer(&input["targetPly"], ply + 1, 64)?;
    let score = integer(&input["staticScore"], -10000, 10000)?;
    let upper = integer(&input["upperBound"], -9999, 10000)?;
    let checked = boolean(&input["currentCheck"])?;
    let previous_checked = boolean(&input["previousCheck"])?;
    let movement = moves::movement(&input["previousMove"])?.ok_or("previousMove cannot be null")?;
    // The prior destination and counts come from the previous board; the
    // descriptor supplies promotion status without a source/legality check.
    let exception = quiescence_policy::capture_exception(&previous, &movement);
    let mut observations = Vec::with_capacity(context.repetitions);
    let mut maps = None;
    for _ in 0..context.repetitions {
        let admitted = ordinary_policy::fast_cutoff_gate(
            score,
            target - ply,
            upper,
            checked,
            previous_checked,
            exception,
        );
        let mut cutoff = None;
        let mut threat = None;
        let mut charges = 0;
        if let Some(adjusted) = admitted {
            // Influence construction is uncharged and maps can be reused.
            // Pressure is requested only after the initial gates. The native
            // helper selects CURRENT king neighbors and evaluation influence.
            let (before, current) = maps.get_or_insert_with(|| {
                (
                    Influence::build(&previous),
                    Influence::build(&context.position),
                )
            });
            if !ordinary_policy::king_pressure(&context.position, before, current) {
                let observed = context.observe(current);
                charges = observed.queries;
                threat = Some(observed.value);
                // Consumer composition matches search.fastCutoff: the native
                // estimator runs before the final signed score comparison.
                let result = adjusted - observed.value;
                if result >= upper {
                    cutoff = Some(result);
                }
            }
        }
        observations.push(json!({
            "cutoffScore":cutoff,
            "pressureChecked":admitted.is_some(),
            "materialThreatQueried":threat.is_some(),
            "materialThreat":threat,
            "chargedRelationQueries":charges,
        }));
    }
    Ok(json!({"observations":observations}))
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "evaluation.materialThreat" => material_threat(input),
        "search.fastThreat" => fast_threat(input),
        _ => Err(format!("unsupported threat operation: {operation}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn context(placement: &str) -> Value {
        let values = json!({"pawn":100,"knight":300,"bishop":310,"rook":500,"queen":900});
        json!({"placement":placement,"side":"white","values":{"white":values,"black":values},
            "squareAdjustments":[],"passedPawnBalance":0,"repetitions":3})
    }

    fn attempt(context: Value) -> Value {
        json!({"previousPlacement":context["placement"],"threatContext":context,
            "searchPly":1,"targetPly":2,"staticScore":10000,"upperBound":0,
            "currentCheck":false,"previousCheck":false,
            "previousMove":{"move":"h3f5","kind":"ordinary"}})
    }

    #[test]
    fn unused_fields_are_validated_even_when_cutoff_is_depth_rejected() {
        let mut query = attempt(context("7k/8/8/8/8/8/8/K7"));
        query["targetPly"] = json!(64);
        assert!(fast_threat(&query).is_ok());
        for entry in [
            json!({"side":"black","piece":"queen","square":"a3","value":128}),
            json!({"side":"black","piece":"king","square":"a3","value":0}),
            json!({"side":"black","piece":"queen","square":"a9","value":0}),
            json!({"side":"black","piece":"queen","square":"a3","value":0,"extra":0}),
        ] {
            let mut bad = query.clone();
            bad["threatContext"]["squareAdjustments"] = json!([entry]);
            assert!(fast_threat(&bad).is_err());
        }
        let entry = json!({"side":"black","piece":"queen","square":"a3","value":1});
        let mut bad = query.clone();
        bad["threatContext"]["squareAdjustments"] = json!([entry.clone(), entry.clone()]);
        assert!(fast_threat(&bad).is_err());
        bad["threatContext"]["squareAdjustments"] = json!([entry]);
        bad["threatContext"]["values"]["black"]["queen"] = json!(10000);
        assert!(fast_threat(&bad).is_err());
        for (field, value) in [
            ("repetitions", json!(0)),
            ("repetitions", json!(17)),
            ("passedPawnBalance", json!(10001)),
            ("side", json!("White")),
        ] {
            let mut bad = query.clone();
            bad["threatContext"][field] = value;
            assert!(fast_threat(&bad).is_err());
        }
        for placement in [
            "7k/8/8/8/8/NNNNNNNN/NNN5/K7", // More than ten knights.
            "7k/8/8/8/8/8/8/K6P",          // Pawn on rank one.
            "8/8/8/8/8/8/8/K7",            // Missing king.
        ] {
            let mut bad = query.clone();
            bad["previousPlacement"] = json!(placement);
            assert!(fast_threat(&bad).is_err());
        }
        query["previousMove"] = Value::Null;
        assert!(fast_threat(&query).is_err());
    }

    #[test]
    fn black_value_and_square_ownership_are_preserved_across_repetitions() {
        let mut query = context("7k/8/8/3p4/2P5/8/8/K7");
        query["side"] = json!("black");
        query["repetitions"] = json!(16);
        query["values"]["white"]["pawn"] = json!(123);
        query["values"]["black"]["pawn"] = json!(901);
        query["squareAdjustments"] = json!([
            {"side":"black","piece":"pawn","square":"d5","value":-11},
            {"side":"white","piece":"pawn","square":"d5","value":127}
        ]);
        assert_eq!(
            material_threat(&query).unwrap(),
            json!({"threat":1490,"chargedRelationQueries":16})
        );
    }

    #[test]
    fn favorable_relations_keep_charges_and_queried_zero_is_distinct_from_absence() {
        // Own pawn c3 supports d4; the opposing rook is too valuable to make
        // that protected pawn a threat, but its relation is still queried.
        let query = context("3r3k/8/8/8/3P4/2P5/8/K7");
        assert_eq!(
            material_threat(&query).unwrap(),
            json!({"threat":0,"chargedRelationQueries":3})
        );
        let mut query = attempt(query);
        query["staticScore"] = json!(100);
        let out = fast_threat(&query).unwrap();
        for observation in out["observations"].as_array().unwrap() {
            assert_eq!(
                *observation,
                json!({"cutoffScore":0,"pressureChecked":true,
                "materialThreatQueried":true,"materialThreat":0,"chargedRelationQueries":1})
            );
        }
        query["staticScore"] = json!(99);
        for observation in fast_threat(&query).unwrap()["observations"]
            .as_array()
            .unwrap()
        {
            assert_eq!(
                *observation,
                json!({"cutoffScore":null,"pressureChecked":false,
                "materialThreatQueried":false,"materialThreat":null,"chargedRelationQueries":0})
            );
        }
    }

    #[test]
    fn promotion_threat_can_be_positive_without_relation_queries() {
        let mut query = context("7K/8/8/8/8/8/p7/7k");
        query["passedPawnBalance"] = json!(10000);
        assert_eq!(
            material_threat(&query).unwrap(),
            json!({"threat":10750,"chargedRelationQueries":0})
        );
        for observation in fast_threat(&attempt(query)).unwrap()["observations"]
            .as_array()
            .unwrap()
        {
            assert_eq!(
                *observation,
                json!({"cutoffScore":null,"pressureChecked":true,
                "materialThreatQueried":true,"materialThreat":10750,"chargedRelationQueries":0})
            );
        }
    }

    #[test]
    fn final_score_failure_keeps_per_call_work_and_special_kinds_add_no_entry_guard() {
        let mut query = attempt(context("7k/8/8/2p5/3P4/8/8/K7"));
        query["staticScore"] = json!(799); // 799 - 100 - 700 = -1, below bound zero.
        for kind in ["ordinary", "castle", "enPassant"] {
            query["previousMove"]["kind"] = json!(kind);
            let out = fast_threat(&query).unwrap();
            assert_eq!(out["observations"].as_array().unwrap().len(), 3);
            for observation in out["observations"].as_array().unwrap() {
                assert_eq!(
                    *observation,
                    json!({"cutoffScore":null,"pressureChecked":true,
                    "materialThreatQueried":true,"materialThreat":700,"chargedRelationQueries":1})
                );
            }
        }
        for (field, value) in [
            ("targetPly", json!(4)),
            ("staticScore", json!(99)),
            ("currentCheck", json!(true)),
            ("previousCheck", json!(true)),
            ("previousMove", json!({"move":"h3f5q","kind":"ordinary"})),
        ] {
            let mut guarded = query.clone();
            guarded[field] = value;
            for observation in fast_threat(&guarded).unwrap()["observations"]
                .as_array()
                .unwrap()
            {
                assert_eq!(observation["pressureChecked"], false);
                assert_eq!(observation["materialThreat"], Value::Null);
                assert_eq!(observation["chargedRelationQueries"], 0);
            }
        }
    }

    #[test]
    fn pressure_uses_current_king_and_evaluation_transparency_on_empty_neighbors() {
        // The current king d4 is transparent to evaluation influence: both d5
        // and d3 receive the rook's contribution. A geometric attack map stops
        // at d4. Two increases to one trigger aggregate pressure; one does not.
        // The previous king a1 must not select this helper's neighborhood.
        let mut query = attempt(context("3r3k/8/8/8/3K4/8/8/8"));
        query["previousPlacement"] = json!("7k/8/8/8/8/8/8/K7");
        for observation in fast_threat(&query).unwrap()["observations"]
            .as_array()
            .unwrap()
        {
            assert_eq!(
                *observation,
                json!({"cutoffScore":null,"pressureChecked":true,
                "materialThreatQueried":false,"materialThreat":null,"chargedRelationQueries":0})
            );
        }
    }

    #[test]
    fn capture_exception_uses_previous_destination_and_previous_counts() {
        let mut query = attempt(context("7k/8/8/8/8/8/8/K7"));
        query["previousPlacement"] = json!("7k/8/8/8/5p2/8/8/K7");
        query["previousMove"] = json!({"move":"h3f4","kind":"ordinary"});
        for observation in fast_threat(&query).unwrap()["observations"]
            .as_array()
            .unwrap()
        {
            assert_eq!(observation["pressureChecked"], false);
            assert_eq!(observation["materialThreat"], Value::Null);
            assert_eq!(observation["chargedRelationQueries"], 0);
        }
        // Placements and move descriptors need not describe a legal transition.
        query["previousPlacement"] = query["threatContext"]["placement"].clone();
        assert_eq!(
            fast_threat(&query).unwrap()["observations"][0]["materialThreat"],
            0
        );
    }
}
