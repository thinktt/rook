//! Pure supplied priority/capture descriptions call the native ordering policy.
use super::{array, color, integer, moves, object, relations, text, unsigned32, Result};
use rook2::{
    ordinary_policy, tactical,
    types::{Move, PieceKind},
};
use serde_json::{json, Value};
use std::collections::BTreeMap;

fn ordered_indices(priorities: &[u32]) -> Vec<usize> {
    // Native priority_sequence only permutes opaque payloads. Every index is
    // at most229, so the existing u16 payload can carry it without interpreting
    // it as a playable descriptor or applying any move sentinel rule.
    let mut indices: Vec<_> = (0..priorities.len())
        .map(|index| Move(index as u16))
        .collect();
    let mut priorities = priorities.to_vec();
    tactical::priority_sequence(&mut indices, &mut priorities);
    indices.into_iter().map(|index| index.0 as usize).collect()
}

fn priority_sequence(input: &Value) -> Result<Value> {
    object(input, &["priorities"])?;
    let priorities = array(&input["priorities"], 0, 230)?
        .iter()
        .map(unsigned32)
        .collect::<Result<Vec<_>>>()?;
    Ok(json!({"orderedIndices":ordered_indices(&priorities),"chargedRelationQueries":0}))
}

fn capture_preferences(input: &Value) -> Result<Value> {
    object(input, &["candidates"])?;
    let mut priorities = Vec::new();
    for candidate in array(&input["candidates"], 0, 230)? {
        object(
            candidate,
            &[
                "attacker",
                "side",
                "attackerValue",
                "victimEffectiveValue",
                "own",
                "opponent",
                "promotion",
            ],
        )?;
        let kind = moves::piece(&candidate["attacker"])?;
        color(&candidate["side"])?;
        let promotion = match text(&candidate["promotion"])? {
            "none" => 0,
            "knight" => 256,
            "bishop" => 512,
            "rook" => 768,
            "queen" => 1024,
            _ => return Err("invalid promotion label".into()),
        };
        if promotion != 0 && kind != PieceKind::Pawn {
            return Err("only a pawn may promote".into());
        }
        let attacker = integer(&candidate["attackerValue"], 0, 10000)?;
        let victim = integer(&candidate["victimEffectiveValue"], -10000, 10000)?;
        let own = relations::profile(&candidate["own"])?;
        let opponent = relations::profile(&candidate["opponent"])?;
        priorities.push(ordinary_policy::capture_magnitude(
            kind, attacker, victim, own, opponent, promotion,
        ));
    }
    let mut groups = BTreeMap::<u32, Vec<usize>>::new();
    for (index, priority) in priorities.iter().enumerate() {
        groups.entry(*priority).or_default().push(index);
    }
    let groups: Vec<_> = groups
        .into_iter()
        .rev()
        .map(|(_, indices)| indices)
        .collect();
    let preferred: Vec<_> = priorities.iter().map(|priority| *priority != 0).collect();
    Ok(
        json!({"orderedIndices":ordered_indices(&priorities),"capturePreferred":preferred,
        "equalPreferenceGroups":groups,"chargedRelationQueries":0}),
    )
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "ordering.prioritySequence" => priority_sequence(input),
        "tactics.capturePreferenceOrder" => capture_preferences(input),
        _ => Err(format!("unsupported supplied-order operation: {operation}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn priority_transport_preserves_full_unsigned_values_and_six_class_ties() {
        assert_eq!(
            priority_sequence(&json!({"priorities":[1,1,1,1,1,1,2]})).unwrap()["orderedIndices"],
            json!([6, 1, 2, 3, 4, 5, 0])
        );
        assert_eq!(
            priority_sequence(&json!({"priorities":[0,4294967295u32]})).unwrap()["orderedIndices"],
            json!([1, 0])
        );
        assert!(priority_sequence(&json!({"priorities":[4294967296u64]})).is_err());
    }

    #[test]
    fn negative_capture_magnitudes_wrap_and_ignored_king_fields_still_validate() {
        let profile = json!({"weak":0,"queen":0,"rook":0,"minor":0,"pawn":0});
        let king = json!({"attacker":"king","side":"black","attackerValue":10000,"victimEffectiveValue":0,
            "own":profile,"opponent":profile,"promotion":"none"});
        let mut knight = king.clone();
        knight["attacker"] = json!("knight");
        knight["attackerValue"] = json!(0);
        let result = capture_preferences(&json!({"candidates":[king.clone(),knight]})).unwrap();
        assert_eq!(
            result,
            json!({"orderedIndices":[1,0],"capturePreferred":[true,true],"equalPreferenceGroups":[[1],[0]],"chargedRelationQueries":0})
        );
        let mut invalid = king.clone();
        invalid["own"]["weak"] = json!(32);
        assert!(capture_preferences(&json!({"candidates":[invalid]})).is_err());
        let mut invalid = king;
        invalid["promotion"] = json!("queen");
        assert!(capture_preferences(&json!({"candidates":[invalid]})).is_err());
    }
}
