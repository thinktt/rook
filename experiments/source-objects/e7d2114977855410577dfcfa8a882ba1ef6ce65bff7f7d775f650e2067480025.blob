//! Fresh joined ingress is executed by the actual persistent Session owner.
use super::{array, integer, object, positions, text, unsigned32, Result};
use rook2::{
    movegen::{self, MoveList},
    output::Event,
    parameters::{Parameters, NAMES},
    position::Position,
    quiescence::Limits,
    session::{self, Action, Session},
    timed::Point,
    timing::Adaptive,
};
use serde_json::{json, Map, Value};

const DELIVERY: [&str; 27] = [
    "avd", "cfd", "md", "myb", "mycc", "myks", "mymob", "myp", "mypp",
    "mypw", "myq", "myr", "myn", "opb", "opcc", "opks", "opmob", "opn",
    "opp", "oppp", "oppw", "opq", "opr", "rnd", "sel", "sop", "tts",
];
const SAFE: u64 = 9_007_199_254_740_991;

struct Request {
    fen: Option<String>,
    moves: Vec<String>,
    supplied: Parameters,
    effective: Parameters,
    randomness_override: Option<i32>,
    group: String,
    remaining: i32,
    seconds: u32,
    iterations: u8,
    units: u64,
    bytes: usize,
}

fn parameters(value: &Value) -> Result<Parameters> {
    object(value, &NAMES)?;
    let mut values = [0; 30];
    for (index, name) in NAMES.iter().enumerate() {
        let (minimum, maximum) = match *name {
            "ana" | "myk" | "opk" => (0, 0),
            "avd" => (-100, 100),
            "cfd" => (-10000, 10000),
            "sop" | "rnd" => (0, 100),
            "sel" => (0, 64),
            "md" => (1, 99),
            "tts" => (4194304, 75497472),
            _ => (0, 1000),
        };
        values[index] = integer(&value[*name], minimum, maximum)?;
        if *name == "tts" && ![4194304, 16777216, 67108864, 75497472].contains(&values[index]) {
            return Err("joined tts must be one of the four admitted capacities".into());
        }
    }
    Ok(Parameters { values })
}

fn coordinate(value: &Value) -> Result<String> {
    let spelling = text(value)?;
    let b = spelling.as_bytes();
    if !matches!(b.len(), 4 | 5)
        || !matches!(b[0], b'a'..=b'h') || !matches!(b[1], b'1'..=b'8')
        || !matches!(b[2], b'a'..=b'h') || !matches!(b[3], b'1'..=b'8')
        || (b.len() == 5 && !matches!(b[4], b'n' | b'b' | b'r' | b'q'))
    {
        return Err("expected lowercase coordinate move with optional promotion suffix".into());
    }
    Ok(spelling.to_owned())
}

impl Request {
    fn parse(input: &Value) -> Result<Self> {
        let mut keys = vec!["setup", "personalityParameters", "clock", "systemSeconds"];
        if input.get("randomnessOverride").is_some() { keys.push("randomnessOverride"); }
        if input.get("diagnosticCapacity").is_some() { keys.push("diagnosticCapacity"); }
        object(input, &keys)?;
        let setup = &input["setup"];
        let fen = match text(&setup["kind"])? {
            "standard-history" => {
                object(setup, &["kind", "moves"])?;
                None
            }
            "setboard-history" => {
                object(setup, &["kind", "fen", "moves"])?;
                let fen = text(&setup["fen"])?;
                if fen.split_ascii_whitespace().count() != 6 {
                    return Err("joined setboard requires six-field FEN".into());
                }
                Some(fen.to_owned())
            }
            _ => return Err("unknown joined setup kind".into()),
        };
        let moves = array(&setup["moves"], 0, 799)?.iter()
            .map(coordinate).collect::<Result<Vec<_>>>()?;
        let supplied = parameters(&input["personalityParameters"])?;
        let randomness_override = input.get("randomnessOverride")
            .map(|v| integer(v, 0, 100)).transpose()?;
        let mut effective = supplied.clone();
        if let Some(value) = randomness_override { effective.values[24] = value; }
        let clock = &input["clock"];
        object(clock, &["policyId", "group"])?;
        if text(&clock["policyId"])? != "joined-diagnostic-group-clocks-v1" {
            return Err("unsupported joined clock policy".into());
        }
        let group = text(&clock["group"])?;
        let remaining = match group {
            "Easy" => 6637, "Hard" => 9483, "GM" => 18100,
            _ => return Err("unknown joined clock group".into()),
        };
        let seconds = unsigned32(&input["systemSeconds"])?;
        let (iterations, units, bytes) = if let Some(capacity) = input.get("diagnosticCapacity") {
            object(capacity, &["maximumEnteredIterations", "maximumChargedSearchUnits", "maximumResultBytes"])?;
            (integer(&capacity["maximumEnteredIterations"], 1, 9)? as u8,
             integer(&capacity["maximumChargedSearchUnits"], 1, 524288)? as u64,
             integer(&capacity["maximumResultBytes"], 1, 16777216)? as usize)
        } else { (3, 8192, 16777216) };
        Ok(Self { fen, moves, supplied, effective, randomness_override,
            group: group.to_owned(), remaining, seconds, iterations, units, bytes })
    }

    fn prepare(&self) -> Result<Session<true>> {
        let mut live = Session::<true>::default();
        idle(&mut live, "xboard")?;
        idle(&mut live, "post")?;
        if let Some(fen) = &self.fen {
            // Native setboard owns FEN syntax, normalization and counter reset.
            // No standalone candidate-domain gate is inserted here.
            live.setboard(fen).map_err(|e| format!("joined setboard: {e:?}"))?;
        }
        idle(&mut live, &format!("time {}", self.remaining))?;
        idle(&mut live, &format!("otim {}", self.remaining))?;
        idle(&mut live, "cm_parm default")?;
        let mut command = String::from("cm_parm");
        for name in DELIVERY {
            let index = NAMES.iter().position(|n| *n == name).unwrap();
            command.push_str(&format!(" {name}={}", self.effective.values[index]));
        }
        idle(&mut live, &command)?;
        if live.parameters != self.effective {
            return Err("actual parameter commands did not establish the joined vector".into());
        }
        idle(&mut live, "easy")?;
        for spelling in &self.moves {
            if live.result.is_some() {
                return Err("joined history has a protocol-terminal prefix before another move".into());
            }
            let before = live.moves.len();
            idle(&mut live, spelling)?;
            if live.moves.len() != before + 1 || live.moves.last().unwrap().to_string() != *spelling {
                return Err("joined retained coordinate move was not accepted".into());
            }
            if live.position().counts.iter().any(|counts| counts[5] != 1) {
                return Err("the exceptional king-victim command continuation has no joined JSON outcome".into());
            }
        }
        Ok(live)
    }

    fn observe(self) -> Result<Value> {
        let mut live = self.prepare()?;
        let root = live.position();
        let mut legal = MoveList::new();
        movegen::generate_legal(&root, &mut legal);
        let checked = movegen::in_check(&root, root.side);
        let allowance = live.allowance().map_err(|e| format!("joined allocation: {e:?}"))?;
        let adaptive = Adaptive::new(allowance.average_cs, allowance.maximum_cs, checked, live.ledger.last());
        let initial_fen = if self.fen.is_some() { normalized_fen(&live.states[0]) }
            else { session::START.to_owned() };
        let mut ingress = json!({
            "position": {"initialFen": initial_fen, "moves": self.moves,
                "root": {"placement": root.placement(), "sideToMove": side(root.side),
                    "castling": positions::rights(&root), "enPassant": positions::ep(&root),
                    "halfmoveClock": root.halfmove, "inCheck": checked}},
            "personality": {"suppliedParameters": vector(&self.supplied),
                "parameters": vector(&live.parameters), "effectiveRnd": live.parameters.values[24],
                "randomnessOverride": {"supplied": self.randomness_override.is_some(), "value": self.randomness_override},
                "parameterDelivery": {"explicitCommandFields": DELIVERY, "defaultedFields": ["ana", "myk", "opk"]}},
            "clock": {"policyId": "joined-diagnostic-group-clocks-v1", "group": self.group,
                "remainingTimeCs": self.remaining,
                "schedule": live.clock.schedule.stages.iter().map(|s| json!({"moves":s.moves,
                    "baseSeconds":s.base_seconds,"incrementSeconds":s.increment_seconds})).collect::<Vec<_>>(),
                "gamePly":live.game_ply(), "initialSide":side(live.states[0].side),
                "selectedClock":side(live.clock_color), "adjustmentCs":live.clock.adjustment_cs,
                "allowance":{"moveIndex":allowance.move_index,"averageCs":allowance.average_cs,"maximumCs":allowance.maximum_cs},
                "adaptiveInitial":{"iterationSeconds":adaptive.limits[0],"rootSeconds":adaptive.limits[1],"maximumSeconds":adaptive.limits[2]}},
            "controls":{"session":"fresh","mode":"ordinary","pondering":false,"analysis":false,
                "searchState":"fresh-ordinary-search","learnedState":"empty","pawnState":"empty",
                "transpositionState":"new-from-personality-tts"}
        });
        if !matches!(live.idle("go").map_err(|e| format!("joined go command: {e:?}"))?, Action::Search) {
            return Err("native joined go did not request search".into());
        }
        let result = live.go(self.seconds, Limits { nodes: Some(self.units) }, self.iterations);
        let output = match result {
            Err(session::Error::FatalEmptyRoot) if legal.len == 0 => {
                json!({"derivedIngress":ingress,"fatal":{"exit":{"code":1,"signal":null},"events":[]}})
            }
            Err(error) => return Err(format!("joined search failed without a portable outcome: {error:?}")),
            Ok(result) => {
                if legal.len == 0 || result.entry_clock != 0 || result.seed != self.seconds
                    || result.allowance != allowance || result.outcome.stop.work.charged_search_units > self.units
                    || result.outcome.stop.work.charged_relation_queries > SAFE
                    || result.outcome.initial_candidates.as_slice() != legal.as_slice()
                {
                    return Err("joined native result exceeds its bound or contradicts fresh ingress".into());
                }
                if result.outcome.result.is_none() {
                    let out = &result.outcome;
                    if out.stop.point != Point::Poll || out.stop.root_index != Some(0)
                        || out.stop.reason != "maximum" || out.stop.depth != 1
                        || out.stop.work.charged_search_units == 0
                        || out.stop.work.charged_search_units % 4096 != 0
                        || !out.publications.is_empty()
                        || out.iterations.iter().any(|i| i.complete || !i.steps.is_empty())
                        || out.stop.pending.is_none_or(|p| p.movement != out.initial_candidates[0])
                    {
                        return Err("joined uncaptured result is outside first-root poll fallback".into());
                    }
                    if !matches!(result.events.as_slice(), [Event::Post(post), Event::Move(movement)]
                        if post.fields == rook2::output::Fields::default() && *movement == legal.moves[0])
                    {
                        return Err("native first-root fallback must retain its zero report and initial move".into());
                    }
                }
                let posts = result.events.iter().filter(|event| matches!(event, Event::Post(_))).count();
                if posts == 0 || !matches!(result.events.last(), Some(Event::Move(_)))
                    || result.events[..result.events.len()-1].iter().any(|e| !matches!(e, Event::Post(_)))
                {
                    return Err("joined native completion lacks its ordered posts and sole final move".into());
                }
                ingress["seed"] = json!({"systemSeconds":self.seconds,
                    "entryWorkClockCentiseconds":result.entry_clock,"acceptedSeed":result.seed,
                    "dependency":"first search in a fresh KingWCR session; setup commands do not charge the work clock"});
                json!({"ingress":ingress,"terminalWork":{"searchWork":result.outcome.stop.work.charged_search_units,
                    "relationWork":result.outcome.stop.work.charged_relation_queries},
                    "events":result.events.iter().map(event).collect::<Vec<_>>()})
            }
        };
        fit_envelope(output, self.bytes)
    }
}

fn idle(live: &mut Session<true>, command: &str) -> Result<()> {
    match live.idle(command).map_err(|e| format!("joined command: {e:?}"))? {
        Action::Reply(_) => Ok(()),
        _ => Err("unexpected search/quit while preparing joined ingress".into()),
    }
}
fn side(color: rook2::types::Color) -> &'static str {
    match color { rook2::types::Color::White => "white", rook2::types::Color::Black => "black" }
}
fn normalized_fen(p: &Position) -> String {
    format!("{} {} {} {} 0 1", p.placement(), if p.side == rook2::types::Color::White { "w" } else { "b" },
        positions::rights(p), positions::ep(p))
}
fn vector(p: &Parameters) -> Value {
    let values: Map<String, Value> = NAMES.iter().zip(p.values).map(|(name, value)|
        ((*name).to_owned(), json!(value))).collect();
    Value::Object(values)
}
fn event(event: &Event) -> Value {
    match event {
        Event::Post(post) => json!({"type":"post","depthToken":post.fields.depth_token,
            "evaluation":post.fields.evaluation,"searchId":post.fields.search_id,
            "pv":post.pv,"engineCentiseconds":post.fields.centiseconds}),
        Event::Move(movement) => json!({"type":"move","move":movement.to_string()}),
    }
}
fn fit_envelope(output: Value, maximum: usize) -> Result<Value> {
    let complete = json!({"version":1,"output":output});
    if serde_json::to_vec(&complete).map_err(|e| format!("joined serialization: {e}"))?.len() > maximum {
        return Err("complete joined JSON response exceeds maximumResultBytes".into());
    }
    Ok(complete["output"].clone())
}
pub(super) fn dispatch(input: &Value) -> Result<Value> { Request::parse(input)?.observe() }

#[cfg(test)]
mod tests {
    use super::*;
    fn request() -> Value {
        let mut p = Parameters::default();p.values[27] = 1;p.values[29] = 67108864;
        json!({"setup":{"kind":"standard-history","moves":[]},
            "personalityParameters":vector(&p),"clock":{"policyId":"joined-diagnostic-group-clocks-v1","group":"GM"},
            "systemSeconds":0})
    }
    #[test]
    fn omitted_override_is_distinct_from_explicit_zero_and_only_rnd_changes() {
        let mut input = request();input["personalityParameters"]["rnd"] = json!(100);
        let absent = Request::parse(&input).unwrap();assert_eq!(absent.randomness_override,None);
        assert_eq!(absent.effective.values[24],100);
        input["randomnessOverride"] = json!(0);
        let zero = Request::parse(&input).unwrap();assert_eq!(zero.randomness_override,Some(0));
        let mut expected = zero.supplied.clone();expected.values[24] = 0;
        assert_eq!(zero.effective,expected);
        input["randomnessOverride"] = Value::Null;assert!(Request::parse(&input).is_err());
    }
    #[test]
    fn setup_uses_native_counter_normalization_and_accepts_broad_nonpawn_ep() {
        let mut input = request();
        input["setup"] = json!({"kind":"setboard-history", "fen":"7k/8/8/8/8/8/3rP3/K7 w - d3 2147483647 2147483647", "moves":["e2d3"]});
        let parsed = Request::parse(&input).unwrap();let live = parsed.prepare().unwrap();
        assert_eq!(live.states[0].halfmove,0);assert_eq!(live.moves.len(),1);
        assert_eq!(live.position().placement(),"7k/8/8/8/8/3P4/8/K7");
        assert_eq!(live.ledger.last(),0);
        input["setup"] = json!({"kind":"setboard-history", "fen":"4k3/4R3/8/8/8/8/8/K7 w - - 0 1", "moves":[]});
        assert!(Request::parse(&input).unwrap().prepare().is_ok());
    }
    #[test]
    fn history_rejects_terminal_prefix_and_admission_keeps_independent_capacity() {
        let mut input = request();
        input["setup"] = json!({"kind":"setboard-history", "fen":"7k/8/8/8/8/8/8/K7 w - - 0 1", "moves":["a1b1"]});
        assert!(Request::parse(&input).unwrap().prepare().is_err());
        input["diagnosticCapacity"] = json!({"maximumEnteredIterations":9,"maximumChargedSearchUnits":524288,"maximumResultBytes":16777216});
        let parsed = Request::parse(&input).unwrap();assert_eq!((parsed.iterations,parsed.units,parsed.bytes),(9,524288,16777216));
        input["diagnosticCapacity"]["maximumResultBytes"] = json!(16777217);
        assert!(Request::parse(&input).is_err());
        input["diagnosticCapacity"]["maximumResultBytes"] = json!(1);
        input["personalityParameters"]["tts"] = json!(5000000);
        assert!(Request::parse(&input).is_err());
    }
}
