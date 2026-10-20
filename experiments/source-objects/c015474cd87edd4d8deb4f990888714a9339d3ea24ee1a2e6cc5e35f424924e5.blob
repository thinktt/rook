//! Supplied candidate ordering transport; native policy owns priorities/order.
use super::{array, color, integer, moves, object, positions, unsigned32, Result};
use rook2::{
    evaluation::RootContext,
    influence::Influence,
    movegen::MoveList,
    ordinary_policy::{self, Learning},
    tactical::{self, OrderingScratch},
    types::{Move, PieceKind},
};
use serde_json::{json, Value};
use std::collections::HashSet;

fn pair(value: &Value) -> Result<[Move; 2]> {
    let values = array(value, 2, 2)?;
    Ok([
        moves::movement(&values[0])?.unwrap_or(Move::NONE),
        moves::movement(&values[1])?.unwrap_or(Move::NONE),
    ])
}

/// Shared cold supplied context. Each caller validates its exact operation keys.
pub(super) struct Context {
    pub(super) root: RootContext,
    pub(super) learning: Learning,
    pub(super) hint: Option<Move>,
    ply: usize,
}
impl Context {
    pub(super) fn parse(input: &Value, position: &rook2::position::Position, ply: usize) -> Result<Self> {
        let mut root = RootContext::neutral(position);
        object(&input["values"], &moves::COLORS)?;
        for (side, name) in moves::COLORS.iter().enumerate() {
            let values = &input["values"][*name];
            object(values, &moves::PIECES[..5])?;
            for (kind, name) in moves::PIECES[..5].iter().enumerate() {
                root.values[side][kind] = integer(&values[*name], 0, 10000)?;
            }
        }
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
        let mut learning = Learning::default();
        learning.history = ordering_history(&input["history"])?;
        // Ordering consumes supplied synthetic entries without learning or summing
        // them; unlike cutoffMemory, there is no10000 total restriction here.
        let killers = &input["killers"];
        object(killers, &["current", "twoPliesEarlier"])?;
        learning.killers[ply] = pair(&killers["current"])?;
        let earlier = pair(&killers["twoPliesEarlier"])?;
        if ply <= 2 {
            if earlier != [Move::NONE; 2] {
                return Err("two-plies-earlier killers require ply at least3".into());
            }
        } else {
            learning.killers[ply - 2] = earlier;
        }
        let hint = moves::movement(&input["hashMove"])?;
        Ok(Self { root,learning,hint,ply })
    }

    pub(super) fn order(&self, position: &rook2::position::Position, list: &mut MoveList) {
        let map = Influence::build(position);
        tactical::order_by(list, &mut OrderingScratch::new(), |movement| {
            ordinary_policy::priority(position, &self.root, &map, &self.learning,
                self.ply, self.hint, movement)
        });
    }
}

pub(super) fn ordering_history(value: &Value) -> Result<[[[u32;64];6];2]> {
    let mut history = [[[0;64];6];2];
    let mut seen = HashSet::new();
    for entry in array(value, 0, 768)? {
        object(entry, &["side", "piece", "square", "value"])?;
        let side = color(&entry["side"])?;
        let kind = moves::piece(&entry["piece"])?;
        let square = positions::square(&entry["square"])?;
        if !seen.insert((side.index(), kind.index(), square.0)) {
            return Err("duplicate history key".into());
        }
        history[side.index()][kind.index()][square.0 as usize] =
            unsigned32(&entry["value"])?;
    }
    Ok(history)
}

pub(super) fn dispatch(input: &Value) -> Result<Value> {
    object(
        input,
        &[
            "placement",
            "side",
            "ply",
            "values",
            "squareAdjustments",
            "history",
            "hashMove",
            "killers",
            "candidates",
        ],
    )?;
    let mut position = positions::placement(&input["placement"], true)?;
    position.side = color(&input["side"])?;
    let ply = integer(&input["ply"], 1, 62)? as usize;
    let context = Context::parse(input, &position, ply)?;
    let mut list = MoveList::new();
    let mut descriptors = HashSet::new();
    for value in array(&input["candidates"], 0, 230)? {
        let movement = moves::movement(value)?.ok_or("candidate cannot be null")?;
        moves::candidate(&position, position.side, movement)?;
        if !descriptors.insert(movement.0) {
            return Err("duplicate candidate descriptor".into());
        }
        list.push(movement);
    }
    let original = list.as_slice().to_vec();
    context.order(&position, &mut list);
    let indices: Vec<_> = list
        .as_slice()
        .iter()
        .map(|movement| {
            original
                .iter()
                .position(|m| m == movement)
                .expect("native ordering preserved candidates")
        })
        .collect();
    Ok(json!({"orderedIndices":indices,"chargedRelationQueries":0}))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn query() -> Value {
        let values = json!({"pawn":100,"knight":300,"bishop":300,"rook":500,"queen":900});
        json!({"placement":"7k/8/8/8/8/8/PP6/K7","side":"white","ply":1,
            "values":{"white":values,"black":values},"squareAdjustments":[],
            "history":[{"side":"white","piece":"pawn","square":"b3","value":4294967295u32}],
            "hashMove":{"move":"a2a3","kind":"ordinary"},"killers":{"current":[null,null],"twoPliesEarlier":[null,null]},
            "candidates":[{"move":"a2a3","kind":"ordinary"},{"move":"b2b3","kind":"ordinary"}]})
    }

    #[test]
    fn full_unsigned_history_can_outrank_a_hash_category_without_becoming_signed() {
        assert_eq!(
            dispatch(&query()).unwrap(),
            json!({"orderedIndices":[1,0],"chargedRelationQueries":0})
        );
    }

    #[test]
    fn component_domain_rejects_duplicate_keys_descriptors_and_early_killers() {
        let mut value = query();
        let duplicate = value["history"][0].clone();
        value["history"].as_array_mut().unwrap().push(duplicate);
        assert!(dispatch(&value).is_err());
        let mut value = query();
        value["candidates"][1] = value["candidates"][0].clone();
        assert!(dispatch(&value).is_err());
        let mut value = query();
        value["killers"]["twoPliesEarlier"][0] = json!({"move":"h3f5","kind":"castle"});
        assert!(dispatch(&value).is_err());
        value["ply"] = json!(3);
        assert!(dispatch(&value).is_ok());
    }
}
