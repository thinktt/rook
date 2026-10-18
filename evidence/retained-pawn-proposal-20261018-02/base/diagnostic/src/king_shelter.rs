//! Cold raw shelter observations; every formula remains in the native owner.
use super::{array, integer, moves, object, positions, Result};
use rook2::{influence::Influence, shelter, types::Color};
use serde_json::{json, Value};

fn pair(input: &Value) -> Result<[i32; 2]> {
    object(input, &moves::COLORS)?;
    Ok([
        integer(&input["white"], 0, 4096)?,
        integer(&input["black"], 0, 4096)?,
    ])
}

pub(super) fn run(input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let mut results = Vec::new();
    for query in array(&input["queries"], 1, 4096)? {
        object(
            query,
            &["placement", "activityPressure", "weights", "materialScore"],
        )?;
        let position = positions::placement(&query["placement"], true)?;
        let pressure = pair(&query["activityPressure"])?;
        let weights = pair(&query["weights"])?;
        let material = integer(&query["materialScore"], -100000, 100000)?;
        let influence = Influence::build(&position);
        let result = shelter::compute(&position, &influence, pressure, material, weights);
        let side = |color: Color| {
            // Raw observations must survive even when their phase or effective
            // weight is zero. No shelter formula is duplicated in transport.
            let parts = shelter::components(&position, &influence, color);
            json!({"ring":parts.ring,"files":parts.files,"screen":parts.screen,
                "shelter":parts.shelter,"term":result.terms[color.index()]})
        };
        results.push(json!({"phase":positions::phase_value(position.phase()),
            "white":side(Color::White),"black":side(Color::Black),"weighted":result.weighted}));
    }
    Ok(json!({"results":results}))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn shelter_keeps_raw_terms_at_closed_phase_and_weight_gates_and_query_order() {
        let query = json!({"placement":"k7/8/8/8/8/8/5PPP/6K1",
            "activityPressure":{"white":0,"black":4096},
            "weights":{"white":0,"black":0},"materialScore":100000});
        let out = run(&json!({"queries":[query.clone(),query.clone()]})).unwrap();
        assert_eq!(out["results"][0], out["results"][1]);
        assert_eq!(
            out["results"][0]["phase"],
            json!({"opening":0,"middlegame":0,"endgame":256})
        );
        assert_eq!(out["results"][0]["white"]["shelter"], 25);
        assert_eq!(out["results"][0]["white"]["term"], 0);
        assert_eq!(out["results"][0]["black"]["term"], -1024);
        assert_eq!(out["results"][0]["weighted"], 0);
        let mut bad = query.clone();
        bad["phase"] = json!(0);
        assert!(run(&json!({"queries":[bad]})).is_err());
        for field in ["activityPressure", "weights"] {
            let mut bad = query.clone();
            bad[field]["black"] = json!(4097);
            assert!(run(&json!({"queries":[bad]})).is_err());
        }
        assert!(run(&json!({"queries":[]})).is_err());
    }
}
