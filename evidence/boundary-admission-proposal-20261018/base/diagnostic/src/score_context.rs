//! Cold score-context transport; native owners produce every numerical value.
use super::{array, boolean, color, integer, object, phase, positions, unsigned32, Result};
use rook2::{
    endgame, evaluation,
    position::{Phase, Position},
    types::Color,
};
use serde_json::{json, Value};

struct Context {
    root_phase: Phase,
    root_side: Color,
    cfd: i32,
    sop: i32,
}

impl Context {
    fn parse(query: &Value, root_phase: Phase) -> Result<Self> {
        Ok(Self {
            root_phase,
            root_side: color(&query["rootSide"])?,
            cfd: integer(&query["cfd"], -10_000, 10_000)?,
            sop: integer(&query["sop"], 0, 100)?,
        })
    }

    fn values(&self) -> (i32, u32) {
        (
            evaluation::draw_preference(self.root_phase, self.cfd),
            evaluation::variation_range(self.sop),
        )
    }
}

struct Score {
    context: Context,
    position: Position,
    current_phase: Option<Phase>,
    base: i32,
    identity: u32,
    endgame: u16,
    checked: bool,
    progress: i32,
}

impl Score {
    fn parse(query: &Value, derived: bool) -> Result<Self> {
        let mut fields = vec![
            "placement",
            "rootSide",
            "side",
            "cfd",
            "sop",
            "baseScore",
            "variationIdentity",
            "reversiblePlies",
            "inCheck",
            "passedPawnBalance",
        ];
        if derived {
            fields.push("rootPlacement");
        } else {
            fields.extend(["rootPhase", "endgameWeight"]);
        }
        object(query, &fields)?;
        let mut position = positions::placement(&query["placement"], true)?;
        let (root_phase, current_phase, endgame) = if derived {
            let root = positions::placement(&query["rootPlacement"], true)?;
            let current = position.phase();
            (root.phase(), Some(current), current.endgame)
        } else {
            (
                phase(&query["rootPhase"])?,
                None,
                integer(&query["endgameWeight"], 0, 256)? as u16,
            )
        };
        let context = Context::parse(query, root_phase)?;
        position.side = color(&query["side"])?;
        position.halfmove = integer(&query["reversiblePlies"], 0, 255)? as u8;
        // Parse all supplied dependencies even if ordinary phase or zero range
        // makes a later numerical producer ignore them.
        Ok(Self {
            context,
            position,
            current_phase,
            base: integer(&query["baseScore"], -1_000_000, 1_000_000)?,
            identity: unsigned32(&query["variationIdentity"])?,
            endgame,
            checked: boolean(&query["inCheck"])?,
            progress: integer(&query["passedPawnBalance"], -10_000, 10_000)?,
        })
    }

    fn observe(self) -> Result<Value> {
        let (preference, range) = self.context.values();
        if self.endgame >= 192 {
            let adjusted = endgame::adjusted_subtotal(
                self.base,
                preference,
                self.context.root_side,
                range,
                self.identity,
            );
            if !(-10_000..=10_000).contains(&adjusted) {
                return Err("late-phase adjusted subtotal outside diagnostic domain".into());
            }
        }
        let result = endgame::finish(
            &self.position,
            self.base,
            preference,
            self.context.root_side,
            range,
            self.identity,
            self.endgame,
            self.checked,
            self.progress,
        );
        let mut output = json!({
            "drawPreference":preference,"variationRange":range,
            "score":result.score,"lowerBound":result.lower,"upperBound":result.upper,
        });
        if let Some(current) = self.current_phase {
            output["rootPhase"] = positions::phase_value(self.context.root_phase);
            output["currentPhase"] = positions::phase_value(current);
        }
        Ok(output)
    }
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let queries = array(&input["queries"], 1, 4096)?;
    match operation {
        "evaluation.scoreContext" => {
            let contexts = queries
                .iter()
                .map(|query| {
                    object(query, &["rootPhase", "rootSide", "cfd", "sop"])?;
                    Context::parse(query, phase(&query["rootPhase"])?)
                })
                .collect::<Result<Vec<_>>>()?;
            let contexts: Vec<_> = contexts
                .iter()
                .map(|context| {
                    let (preference, range) = context.values();
                    json!({"drawPreference":preference,"variationRange":range})
                })
                .collect();
            Ok(json!({"contexts":contexts}))
        }
        "evaluation.personalityScore" | "evaluation.positionScore" => {
            // Validate the entire request before any late-phase admission gate.
            let scores = queries
                .iter()
                .map(|query| Score::parse(query, operation == "evaluation.positionScore"))
                .collect::<Result<Vec<_>>>()?;
            let results = scores
                .into_iter()
                .map(Score::observe)
                .collect::<Result<Vec<_>>>()?;
            Ok(json!({"results":results}))
        }
        _ => Err(format!("unsupported score-context operation: {operation}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    const BARE: &str = "8/8/8/8/8/8/k7/K7";

    fn query() -> Value {
        json!({"placement":BARE,"rootPhase":{"opening":256,"middlegame":0,"endgame":0},
            "rootSide":"white","side":"white","cfd":0,"sop":100,"baseScore":-16,
            "variationIdentity":4294967295u32,"reversiblePlies":36,"endgameWeight":191,
            "inCheck":false,"passedPawnBalance":0})
    }

    fn observe(query: Value) -> Value {
        dispatch("evaluation.personalityScore", &json!({"queries":[query]})).unwrap()["results"][0]
            .clone()
    }

    fn position_query() -> Value {
        let mut query = query();
        query.as_object_mut().unwrap().remove("rootPhase");
        query.as_object_mut().unwrap().remove("endgameWeight");
        query["rootPlacement"] = json!(START);
        query
    }

    #[test]
    fn root_color_does_not_change_negative_context_rounding_or_variation() {
        let q = json!({"rootPhase":{"opening":0,"middlegame":256,"endgame":0},
            "rootSide":"white","cfd":-3,"sop":99});
        let mut black = q.clone();
        black["rootSide"] = json!("black");
        let output = dispatch("evaluation.scoreContext", &json!({"queries":[q,black]})).unwrap();
        assert_eq!(
            output,
            json!({"contexts":[
            {"drawPreference":-1,"variationRange":3},
            {"drawPreference":-1,"variationRange":3}]})
        );
        let edges = json!({"queries":[
            {"rootPhase":{"opening":256,"middlegame":0,"endgame":0},"rootSide":"black","cfd":-10000,"sop":0},
            {"rootPhase":{"opening":0,"middlegame":0,"endgame":256},"rootSide":"white","cfd":10000,"sop":100}]});
        assert_eq!(
            dispatch("evaluation.scoreContext", &edges).unwrap(),
            json!({"contexts":[
            {"drawPreference":-10000,"variationRange":5300},
            {"drawPreference":2500,"variationRange":0}]})
        );
    }

    #[test]
    fn supplied_identity_and_phase_are_independent_of_the_placement() {
        let mut q = query();
        q["reversiblePlies"] = json!(0);
        q["sop"] = json!(99);
        q["variationIdentity"] = json!(0);
        assert_eq!(observe(q.clone())["score"], -17);
        q["variationIdentity"] = json!(3);
        assert_eq!(observe(q.clone())["score"], -14);
        q["variationIdentity"] = json!(7);
        assert_eq!(observe(q.clone())["score"], -14);
        // The broad placement domain admits adjacent kings. Its derived late
        // phase must not replace the supplied ordinary phase.
        q["sop"] = json!(100);
        q["baseScore"] = json!(1_000_000);
        assert_eq!(observe(q)["score"], 7900);
    }

    #[test]
    fn late_admission_uses_produced_context_and_root_ownership() {
        let mut q = query();
        q["baseScore"] = json!(10001);
        q["cfd"] = json!(1);
        q["endgameWeight"] = json!(192);
        q["rootSide"] = json!("black");
        assert!(dispatch(
            "evaluation.personalityScore",
            &json!({"queries":[q.clone()]})
        )
        .is_ok());
        q["rootSide"] = json!("white");
        assert!(dispatch(
            "evaluation.personalityScore",
            &json!({"queries":[q.clone()]})
        )
        .is_err());
        q["cfd"] = json!(0);
        q["sop"] = json!(99);
        q["variationIdentity"] = json!(0); // Range 3 produces -1, admitting 10000.
        assert!(dispatch(
            "evaluation.personalityScore",
            &json!({"queries":[q.clone()]})
        )
        .is_ok());
        q["variationIdentity"] = json!(3);
        assert!(dispatch("evaluation.personalityScore", &json!({"queries":[q]})).is_err());
    }

    #[test]
    fn root_and_current_phase_are_derived_separately_without_query_carry() {
        let mut q = position_query();
        q["cfd"] = json!(-3);
        let mut opening = q.clone();
        opening["placement"] = json!(START);
        let mut ending_root = opening.clone();
        ending_root["rootPlacement"] = json!(BARE);
        let out = dispatch(
            "evaluation.positionScore",
            &json!({"queries":[q.clone(),opening,ending_root,q]}),
        )
        .unwrap();
        let r = &out["results"];
        assert_eq!(
            r[0]["rootPhase"],
            json!({"opening":256,"middlegame":0,"endgame":0})
        );
        assert_eq!(
            r[0]["currentPhase"],
            json!({"opening":0,"middlegame":0,"endgame":256})
        );
        assert_eq!(r[0]["drawPreference"], -3);
        assert_eq!(r[1]["currentPhase"], r[0]["rootPhase"]);
        assert_eq!(r[2]["drawPreference"], -1);
        assert_eq!(r[0], r[3]);
        let mut promoted = position_query();
        promoted["rootPlacement"] = json!("4k3/ppppppp1/nnnnnnnn/8/8/NNNNNNNN/PPPPPPP1/4K3");
        let out = dispatch("evaluation.positionScore", &json!({"queries":[promoted]})).unwrap();
        assert_eq!(
            out["results"][0]["rootPhase"],
            json!({"opening":0,"middlegame":8,"endgame":248})
        );
        let mut invalid = position_query();
        invalid["baseScore"] = json!(10001);
        assert!(dispatch(
            "evaluation.positionScore",
            &json!({"queries":[invalid.clone()]})
        )
        .is_err());
        invalid["placement"] = json!(START);
        assert!(dispatch("evaluation.positionScore", &json!({"queries":[invalid]})).is_ok());
    }

    #[test]
    fn all_schemas_are_validated_before_semantic_gates_and_ignored_inputs() {
        let mut late_invalid = query();
        late_invalid["baseScore"] = json!(10001);
        late_invalid["endgameWeight"] = json!(256);
        let mut malformed = query();
        malformed["inCheck"] = json!(0);
        let error = dispatch(
            "evaluation.personalityScore",
            &json!({"queries":[late_invalid,malformed]}),
        )
        .unwrap_err();
        assert_eq!(error, "expected boolean");
        for (field, value) in [
            ("variationIdentity", json!(4294967296u64)),
            ("passedPawnBalance", json!(10001)),
            ("sop", json!(101)),
            ("endgameWeight", json!(257)),
            (
                "rootPhase",
                json!({"opening":0,"middlegame":0,"endgame":255}),
            ),
            ("rootSide", json!("red")),
            ("extra", json!(0)),
        ] {
            let mut q = query();
            q[field] = value;
            assert!(dispatch("evaluation.personalityScore", &json!({"queries":[q]})).is_err());
        }
        let mut q = position_query();
        q["rootPlacement"] = json!("8/8/8/8/8/8/8/K7");
        assert!(dispatch("evaluation.positionScore", &json!({"queries":[q]})).is_err());
    }
}
