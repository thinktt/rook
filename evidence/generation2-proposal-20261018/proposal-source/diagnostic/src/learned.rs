//! Supplied learning/table sequences call native policy with opaque input labels.
use super::{array, boolean, color, integer, moves, object, positions, text, Result};
use rook2::{
    ordinary_policy::Learning,
    remembered::{Bound, ProbeResult, Query, RememberedTable, Store},
    types::{Color, Move, PieceKind, Square},
};
use serde_json::{json, Value};
use std::collections::BTreeMap;

fn learning_snapshot(learning: &Learning) -> Value {
    let mut history = Vec::new();
    for side in [Color::White, Color::Black] {
        for kind in PieceKind::ALL {
            for square in 0..64 {
                let value = learning.history[side.index()][kind.index()][square];
                if value != 0 {
                    history.push(json!({"side":moves::COLORS[side.index()],"piece":moves::PIECES[kind.index()],
                        "square":Square(square as u8).to_string(),"value":value}));
                }
            }
        }
    }
    let mut killers = Vec::new();
    for ply in 1..=62 {
        let pair = learning.killers[ply];
        if pair != [Move::NONE; 2] {
            killers.push(
                json!({"ply":ply,"moves":[moves::descriptor(pair[0]),moves::descriptor(pair[1])]}),
            );
        }
    }
    json!({"history":history,"killers":killers,"total":learning.total})
}

fn cutoff_memory(input: &Value) -> Result<Value> {
    object(input, &["history", "killers", "events"])?;
    let mut learning = Learning::default();
    let mut seen = [[[false; 64]; 6]; 2];
    for entry in array(&input["history"], 0, 768)? {
        object(entry, &["side", "piece", "square", "value"])?;
        let side = color(&entry["side"])?;
        let kind = moves::piece(&entry["piece"])?;
        let square = positions::square(&entry["square"])?;
        let value = integer(&entry["value"], 0, 10000)? as u32;
        if seen[side.index()][kind.index()][square.0 as usize] {
            return Err("duplicate history key".into());
        }
        seen[side.index()][kind.index()][square.0 as usize] = true;
        learning.history[side.index()][kind.index()][square.0 as usize] = value;
        learning.total += value;
        if learning.total > 10000 {
            return Err("initial history total exceeds 10000".into());
        }
    }
    let mut plies = [false; 65];
    for entry in array(&input["killers"], 0, 62)? {
        object(entry, &["ply", "moves"])?;
        let ply = integer(&entry["ply"], 1, 62)? as usize;
        if plies[ply] {
            return Err("duplicate killer ply".into());
        }
        plies[ply] = true;
        let pair = array(&entry["moves"], 2, 2)?;
        learning.killers[ply] = [
            moves::movement(&pair[0])?.unwrap_or(Move::NONE),
            moves::movement(&pair[1])?.unwrap_or(Move::NONE),
        ];
    }
    let mut snapshots = vec![learning_snapshot(&learning)];
    for event in array(&input["events"], 1, 8)? {
        if event.get("reset").is_some() {
            object(event, &["reset"])?;
            if !boolean(&event["reset"])? {
                return Err("reset requires true".into());
            }
            learning.clear();
        } else {
            object(
                event,
                &["placement", "side", "ply", "depth", "move", "times"],
            )?;
            let mut position = positions::placement(&event["placement"], true)?;
            position.side = color(&event["side"])?;
            let ply = integer(&event["ply"], 1, 62)? as usize;
            let depth = integer(&event["depth"], 0, 62)?;
            let times = integer(&event["times"], 1, 4096)?;
            let movement = moves::movement(&event["move"])?;
            if let Some(movement) = movement {
                moves::candidate(&position, position.side, movement)?;
            }
            for _ in 0..times {
                learning.record(&position, ply, depth, movement);
            }
        }
        snapshots.push(learning_snapshot(&learning));
    }
    Ok(json!({"snapshots":snapshots}))
}

#[derive(Default)]
pub(super) struct Labels {
    groups: BTreeMap<String, usize>,
    identities: BTreeMap<String, u32>,
}

fn label(value: &Value) -> Result<&str> {
    let label = text(value)?;
    if !(1..=32).contains(&label.len())
        || !label
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
    {
        return Err("invalid opaque group/identity label".into());
    }
    Ok(label)
}

impl Labels {
    pub(super) fn query(&mut self, event: &Value) -> Result<Query> {
        let group = label(&event["group"])?;
        let group = match self.groups.get(group) {
            Some(&index) => index,
            None => {
                if self.groups.len() == 16 {
                    return Err("too many conflict groups".into());
                }
                let index = self.groups.len();
                self.groups.insert(group.into(), index);
                index
            }
        };
        let identity = label(&event["identity"])?;
        let next = self.identities.len() as u32 + 1;
        let identity = *self.identities.entry(identity.into()).or_insert(next);
        let lower = integer(&event["lowerBound"], -10000, 10000)?;
        let upper = integer(&event["upperBound"], -10000, 10000)?;
        if lower >= upper {
            return Err("window must have lower strictly below upper".into());
        }
        Ok(Query {
            group,
            identity,
            ply: integer(&event["searchPly"], 0, 63)?,
            target: integer(&event["targetPly"], 0, 64)?,
            lower,
            upper,
        })
    }
}

pub(super) fn observation(result: ProbeResult) -> Value {
    let bound = match result.bound {
        Bound::None => "none",
        Bound::Upper => "upper",
        Bound::Exact => "exact",
        Bound::Lower => "lower",
    };
    json!({"score":result.score,"bound":bound,"markedDepth":result.marked_depth,
        "move":result.move_hint.map(|movement| format!("{}{}",movement.from(),movement.to())),
        "quietMateChecked":result.quiet_mate_checked})
}

/// Parsed before any table mutation, so a suppressed stage still validates
/// all supplied fields and the global request's label/group domain.
pub(super) enum TableEvent { Clear, Store(Store), Probe(Query) }
impl TableEvent {
    pub(super) fn parse(event:&Value, labels:&mut Labels) -> Result<Self> {
        match text(&event["kind"])? {
            "clear" => { object(event,&["kind"])?; Ok(Self::Clear) }
            "store" => {
                object(event,&["kind","group","identity","searchPly","targetPly",
                    "lowerBound","upperBound","score","move","quietMateChecked","markDepth"])?;
                Ok(Self::Store(Store { query:labels.query(event)?,
                    score:integer(&event["score"],-10000,10000)?,
                    move_hint:moves::movement(&event["move"])?,
                    quiet_mate_checked:boolean(&event["quietMateChecked"])?,
                    mark_depth:boolean(&event["markDepth"])? }))
            }
            "probe" => {
                object(event,&["kind","group","identity","searchPly","targetPly","lowerBound","upperBound"])?;
                Ok(Self::Probe(labels.query(event)?))
            }
            _ => Err("unknown remembered-result event".into()),
        }
    }
    pub(super) fn apply(self, table:&mut RememberedTable) -> Option<ProbeResult> {
        match self {
            Self::Clear => { table.clear();None }
            Self::Store(store) => { table.store(store);None }
            Self::Probe(query) => Some(table.probe(query)),
        }
    }
}

fn remembered_results(input: &Value) -> Result<Value> {
    object(input, &["events"])?;
    let mut labels = Labels::default();
    let events = array(&input["events"],1,256)?.iter()
        .map(|event| TableEvent::parse(event,&mut labels)).collect::<Result<Vec<_>>>()?;
    if !events.iter().any(|event|matches!(event,TableEvent::Probe(_))) {
        return Err("remembered sequence requires a probe".into());
    }
    let mut table = RememberedTable::with_groups(16);
    let observations:Vec<_> = events.into_iter().filter_map(|event|event.apply(&mut table))
        .map(observation).collect();
    Ok(json!({"observations":observations,"chargedSearchUnits":0,"chargedRelationQueries":0}))
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "search.cutoffMemory" => cutoff_memory(input),
        "search.rememberedResults" => remembered_results(input),
        _ => Err(format!("unsupported learned-state operation: {operation}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn table_transport_distinguishes_missing_score_from_zero_and_discards_hint_kind() {
        let stored = json!({"kind":"store","group":"G","identity":"A","searchPly":0,"targetPly":2,
            "lowerBound":-1,"upperBound":1,"score":0,"move":{"move":"a2a3q","kind":"ordinary"},"quietMateChecked":false,"markDepth":true});
        let probe = json!({"kind":"probe","group":"G","identity":"A","searchPly":0,"targetPly":2,"lowerBound":-1,"upperBound":0});
        let mut miss = probe.clone();
        miss["identity"] = json!("a");
        let output = remembered_results(&json!({"events":[stored,probe,miss]})).unwrap();
        assert_eq!(output["observations"][0]["score"], 0);
        assert_eq!(output["observations"][0]["move"], "a2a3");
        assert!(output["observations"][1]["score"].is_null());
    }

    #[test]
    fn group_domain_remains_request_wide_across_clears() {
        let mut events = Vec::new();
        for index in 0..17 {
            events.push(json!({"kind":"probe","group":format!("G{index}"),"identity":"A","searchPly":0,"targetPly":0,"lowerBound":-1,"upperBound":1}));
            events.push(json!({"kind":"clear"}));
        }
        assert!(remembered_results(&json!({"events":events})).is_err());
    }

    #[test]
    fn initial_killers_may_not_fit_an_event_position_but_event_sources_must_fit() {
        let query = json!({"history":[],"killers":[{"ply":1,"moves":[{"move":"h3f5","kind":"castle"},null]}],
            "events":[{"placement":"7k/8/8/8/8/8/8/K7","side":"white","ply":1,"depth":0,
                "move":{"move":"a1a2","kind":"ordinary"},"times":1},{"reset":true}]});
        let result = cutoff_memory(&query).unwrap();
        assert_eq!(
            result["snapshots"][1]["killers"][0]["moves"][0]["move"],
            "h3f5"
        );
        assert_eq!(
            result["snapshots"][1]["killers"][0]["moves"][1]["move"],
            "a1a2"
        );
        assert_eq!(result["snapshots"][1]["history"][0]["piece"], "king");
        assert_eq!(result["snapshots"][2]["total"], 0);
        let mut invalid = query;
        invalid["events"][0]["move"]["move"] = json!("b1b2");
        assert!(cutoff_memory(&invalid).is_err());
    }
}
