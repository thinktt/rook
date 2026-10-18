//! Cold exact boundary/mate schemas; query producers remain native owners.
use super::{admission, array, boolean, integer, moves, object, positions, text, Result};
use rook2::{history::SearchHistory, ordinary_policy::{self as policy, Learning}, movegen::{self, MoveList}, position::Position, types::Move};
use serde_json::{json, Value};
use std::collections::BTreeMap;

struct Context {
    ply: usize,
    pre_root: usize,
    checked: bool,
    analysis: i32,
    prior: Vec<Position>,
    current: Position,
    current_move: Option<Move>,
    earlier_move: Option<Move>,
    learning: Learning,
}

impl Context {
    // Caller validates the exact operation object before shared field parsing.
    fn parse(input: &Value) -> Result<Self> {
        let ply = integer(&input["searchPly"], 1, 63)? as usize;
        let pre_root = integer(&input["preRootLength"], 0, 512)? as usize;
        let halfmove = integer(&input["halfmoveClock"], 0, 255)? as u8;
        let checked = boolean(&input["inCheck"])?;
        let analysis = integer(&input["analysis"], i32::MIN, i32::MAX)?;
        let current_move = moves::movement(&input["currentMove"])?;
        let earlier_move = moves::movement(&input["earlierMove"])?;
        let learning = admission::parse_killers(&input["killers"], 64)?;
        let mut labels = BTreeMap::new();
        let prior = array(&input["prior"], pre_root + ply, pre_root + ply)?.iter()
            .map(|state| admission::opaque_position(state, &mut labels)).collect::<Result<Vec<_>>>()?;
        let mut current = admission::opaque_position(&input["current"], &mut labels)?;
        current.halfmove = halfmove;
        Ok(Self { ply, pre_root, checked, analysis, prior, current, current_move, earlier_move, learning })
    }

    fn history(&self) -> SearchHistory {
        let mut history = SearchHistory::new(&self.prior[0]);
        let earlier_index = (self.ply >= 3).then(|| self.pre_root + self.ply - 2);
        for (index, position) in self.prior.iter().enumerate().skip(1) {
            let arrival = if Some(index) == earlier_index { self.earlier_move } else { None };
            history.push(position, arrival);
            if index == self.pre_root { history.mark_root(); }
        }
        history.push(&self.current, self.current_move);
        debug_assert_eq!((history.search_ply(), history.pre_root_len()), (self.ply, self.pre_root));
        history
    }
}

#[derive(Clone, Copy)]
enum Mode { Full, Quiescence, MateInterior }
impl Mode {
    fn name(self) -> &'static str {
        match self { Self::Full => "full", Self::Quiescence => "quiescence", Self::MateInterior => "mateInterior" }
    }
    fn parse(value: &Value) -> Result<Self> {
        match text(value)? {
            "full" => Ok(Self::Full), "quiescence" => Ok(Self::Quiescence),
            "mateInterior" => Ok(Self::MateInterior), _ => Err("invalid draw-boundary mode".into()),
        }
    }
}

struct Draw {
    context: Context,
    mode: Mode,
    target: i32,
    maximum: usize,
    upper: i32,
}
impl Draw {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["mode", "searchPly", "targetPly", "maximumDepth", "upperBound", "preRootLength", "halfmoveClock", "inCheck", "analysis", "prior", "current", "currentMove", "earlierMove", "killers"])?;
        let mode = Mode::parse(&input["mode"])?;
        let target = integer(&input["targetPly"], 0, 64)?;
        let maximum = integer(&input["maximumDepth"], 0, 99)? as usize;
        let upper = integer(&input["upperBound"], -10000, 10000)?;
        let context = Context::parse(input)?;
        if matches!(mode, Mode::MateInterior) && (context.ply == 63 || target <= context.ply as i32) {
            return Err("mateInterior must precede its target and final active ply".into());
        }
        Ok(Self { context, mode, target, maximum, upper })
    }

    fn observe(mut self) -> Value {
        let history = self.context.history();
        let count = history.repetition_count(self.context.checked);
        let cycle = history.short_reversal();
        let effective = if matches!(self.mode, Mode::Full)
            && policy::quiescence_handoff(self.target - self.context.ply as i32, self.context.ply, self.maximum)
            { Mode::Quiescence } else { self.mode };
        let draw = policy::early_draw(&history, self.context.ply, self.context.checked,
            self.context.analysis, self.upper, &mut self.context.learning);
        json!({"repetitionCount":count,"isCycle":cycle,"outcome":if draw {"draw"} else {"continue"},
            "continuationMode":if draw {Value::Null} else {json!(effective.name())},
            "chargedSearchUnits":1,"killers":admission::killers_output(&self.context.learning,64)})
    }
}

struct MateLeaf {
    context: Context,
    replies: usize,
}
impl MateLeaf {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["searchPly", "targetPly", "preRootLength", "halfmoveClock", "inCheck", "analysis", "prior", "current", "currentMove", "earlierMove", "killers", "legalReplyCount"])?;
        let target = integer(&input["targetPly"], 0, 64)?;
        let replies = integer(&input["legalReplyCount"], 0, 230)? as usize;
        let context = Context::parse(input)?;
        if context.ply < 63 && (context.ply as i32) < target {
            return Err("mateLeaf entry must reach its target or final active ply".into());
        }
        Ok(Self { context, replies })
    }

    fn observe(mut self) -> Value {
        let history = self.context.history();
        let count = history.repetition_count(self.context.checked);
        let cycle = history.short_reversal();
        let mut queries = 0;
        let replies = self.replies;
        let score = policy::mate_leaf(&history, self.context.ply, self.context.checked,
            self.context.analysis, &mut self.context.learning, || { queries += 1; replies });
        json!({"repetitionCount":count,"isCycle":cycle,"score":score,"replyQueries":queries,
            "chargedSearchUnits":1,"killers":admission::killers_output(&self.context.learning,64)})
    }
}

fn flag_position(value: &Value) -> Result<Position> {
    object(value, &["side", "castling", "enPassant"])?;
    let mut full = value.clone();
    full["identity"] = json!("flags");
    admission::opaque_position(&full, &mut BTreeMap::new())
}

struct Reversal {
    ply: usize,
    current: Position,
    baseline: Position,
    current_move: Option<Move>,
    earlier_move: Option<Move>,
}
impl Reversal {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["searchPly", "halfmoveClock", "currentMove", "earlierMove", "current", "baseline"])?;
        let ply = integer(&input["searchPly"], 0, 63)? as usize;
        let halfmove = integer(&input["halfmoveClock"], 0, 255)? as u8;
        let current_move = moves::movement(&input["currentMove"])?;
        let earlier_move = moves::movement(&input["earlierMove"])?;
        let mut current = flag_position(&input["current"])?;
        let baseline = flag_position(&input["baseline"])?;
        current.halfmove = halfmove;
        Ok(Self { ply, current, baseline, current_move, earlier_move })
    }

    fn observe(self) -> Value {
        let initial = if self.ply == 0 { &self.current } else { &self.baseline };
        let mut history = SearchHistory::new(initial);
        for ply in 1..=self.ply {
            let (position, arrival) = if ply == self.ply { (&self.current, self.current_move) }
                else if self.ply >= 3 && ply == self.ply - 2 { (&self.baseline, self.earlier_move) }
                else { (&self.baseline, None) };
            history.push(position, arrival);
        }
        json!({"isCycle":history.short_reversal(),"chargedSearchUnits":0})
    }
}

struct MatePosition { position: Position, ply: usize }
impl MatePosition {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["fen", "searchPly"])?;
        let ply = integer(&input["searchPly"], 1, 63)? as usize;
        let fen = text(&input["fen"])?;
        let fields: Vec<_> = fen.split_whitespace().collect();
        if fields.len() != 4 { return Err("mateLeafPosition needs exactly four FEN fields".into()); }
        let side = match fields[1] { "w" => "white", "b" => "black", _ => return Err("invalid FEN side".into()) };
        // This component permits raw flags, including an occupied EP target.
        // Parse them exactly, produce placement with native neutral setup, and
        // restore the supplied native flags without importing setup's narrower
        // empty-target domain or its normalization of unsupported requests.
        let flags = flag_position(&json!({"side":side,"castling":if fields[2]=="-" {""} else {fields[2]},
            "enPassant":if fields[3]=="-" {Value::Null} else {json!(fields[3])}}))?;
        let mut position = positions::sequence_position(&format!("{} {} - - 0 1", fields[0], fields[1]), true)?;
        position.rights = flags.rights;
        position.ep = flags.ep;
        // No legal-history/nonmoving-king/EP-pawn-victim admission is imported.
        // Actual legal replies are not capped at the supplied-count230 domain.
        Ok(Self { position, ply })
    }
}

impl MatePosition {
    fn observe(self) -> Value {
        let checked = movegen::in_check(&self.position, self.position.side);
        let mut replies = MoveList::new();
        movegen::generate_legal(&self.position, &mut replies);
        // The full legal count is auxiliary, including when the leaf skips its
        // dependency. No extra search entry is charged for this observation.
        let mut history = SearchHistory::new(&self.position);
        for _ in 0..self.ply { history.push(&self.position, None); }
        let score = policy::mate_leaf(&history, self.ply, checked, 0,
            &mut Learning::default(), || replies.len);
        json!({"inCheck":checked,"legalReplies":replies.len,"score":score,"chargedSearchUnits":1})
    }
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    // Every operation parses the whole request before any query or mutation.
    match operation {
        "search.drawBoundary" => Ok(Draw::parse(input)?.observe()),
        "search.moveReversal" => Ok(Reversal::parse(input)?.observe()),
        "search.mateLeaf" => Ok(MateLeaf::parse(input)?.observe()),
        "search.mateLeafPosition" => Ok(MatePosition::parse(input)?.observe()),
        _ => Err("unknown boundary-admission operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn state(identity: &str) -> Value {
        json!({"identity":identity,"side":"white","castling":"","enPassant":null})
    }
    fn remembered(coordinates: &str) -> Value { json!({"move":coordinates,"kind":"ordinary"}) }
    fn leaf(ply: usize, pre: usize) -> Value {
        let prior: Vec<_> = (0..pre+ply).map(|index| state(&format!("p{index}"))).collect();
        json!({"searchPly":ply,"targetPly":ply,"preRootLength":pre,"halfmoveClock":0,
            "inCheck":true,"analysis":0,"prior":prior,"current":state("current"),
            "currentMove":null,"earlierMove":null,"killers":[],"legalReplyCount":0})
    }
    fn draw(ply: usize, pre: usize) -> Value {
        let mut value = leaf(ply,pre);
        value.as_object_mut().unwrap().remove("legalReplyCount");
        value["mode"]=json!("full");value["maximumDepth"]=json!(99);value["upperBound"]=json!(1);
        value
    }
    fn preferences(ply: usize) -> Value {
        json!([{"ply":ply,"moves":[remembered("a1b1"),null]}])
    }

    #[test]
    fn exact_schemas_validate_ignored_fields_and_boundary_capacities_before_work() {
        let mut value=draw(1,0);value["mode"]=json!("quiescence");
        value["maximumDepth"]=json!(100);assert!(Draw::parse(&value).is_err());
        value["maximumDepth"]=json!(0);value["earlierMove"]=json!({"move":"a1a1","kind":"ordinary"});
        assert!(Draw::parse(&value).is_err());
        value["earlierMove"]=Value::Null;value["extra"]=json!(0);assert!(Draw::parse(&value).is_err());
        let mut value=leaf(63,0);value["legalReplyCount"]=json!(231);
        assert!(MateLeaf::parse(&value).is_err()); // validated even though ceiling skips it
        value["legalReplyCount"]=json!(230);value["killers"]=preferences(64);
        assert!(MateLeaf::parse(&value).is_ok());
        let duplicate=value["killers"][0].clone();value["killers"].as_array_mut().unwrap().push(duplicate);
        assert!(MateLeaf::parse(&value).is_err());
        let mut value=draw(3,0);value["mode"]=json!("mateInterior");
        assert!(Draw::parse(&value).is_err());value["targetPly"]=json!(4);
        value["maximumDepth"]=json!(0);assert!(Draw::parse(&value).is_ok());
        let mut value=leaf(1,0);value["targetPly"]=json!(2);assert!(MateLeaf::parse(&value).is_err());
    }

    #[test]
    fn root_offset_places_reversal_arrivals_and_baseline_at_native_indices() {
        for pre in [0,5,512] {
            let mut value=leaf(3,pre);value["halfmoveClock"]=json!(3);
            value["currentMove"]=remembered("b1a1");value["earlierMove"]=remembered("a1b1");
            let context=Context::parse(&value).unwrap();let history=context.history();
            assert_eq!((history.search_ply(),history.pre_root_len()),(3,pre));
            assert!(history.short_reversal());
            // Baseline is root (not the preceding pre-root boundary or ply1).
            value["prior"][pre]["castling"]=json!("K");
            assert!(!Context::parse(&value).unwrap().history().short_reversal());
        }
        for ply in [1,2] {
            let context=Context::parse(&leaf(ply,0)).unwrap();
            assert_eq!(context.history().search_ply(),ply);
        }
    }

    #[test]
    fn admission_preserves_repetition_preferences_but_clears_on_guarded_reversal_and_handoff() {
        let mut value=draw(1,3);value["current"]=state("p0");value["halfmoveClock"]=json!(4);
        value["killers"]=preferences(2);
        let observed=Draw::parse(&value).unwrap().observe();
        assert_eq!(observed["repetitionCount"],2);assert_eq!(observed["outcome"],"draw");
        assert_eq!(observed["killers"],value["killers"]);
        value["analysis"]=json!(1);
        let observed=Draw::parse(&value).unwrap().observe();
        assert_eq!(observed["outcome"],"continue");assert_eq!(observed["continuationMode"],"quiescence");
        assert_eq!(observed["killers"],json!([]));
        let mut value=draw(3,0);value["targetPly"]=json!(4);value["halfmoveClock"]=json!(3);
        value["currentMove"]=remembered("b1a1");value["earlierMove"]=remembered("a1b1");
        value["killers"]=preferences(4);
        for (upper,outcome) in [(1,"continue"),(0,"draw"),(-1,"draw")] {
            value["upperBound"]=json!(upper);
            let observed=Draw::parse(&value).unwrap().observe();
            assert_eq!(observed["isCycle"],true);assert_eq!(observed["outcome"],outcome);
            assert_eq!(observed["killers"],json!([]));assert_eq!(observed["chargedSearchUnits"],1);
        }
        value["upperBound"]=json!(-1);value["currentMove"]=Value::Null;value["earlierMove"]=Value::Null;
        value["targetPly"]=json!(3);
        let observed=Draw::parse(&value).unwrap().observe();
        assert_eq!(observed["isCycle"],false);assert_eq!(observed["outcome"],"continue");
        assert_eq!(observed["continuationMode"],"quiescence");
    }

    #[test]
    fn supplied_mate_count_is_lazy_and_final_ply_clears_pair64() {
        for (ply,checked,replies,score,queries) in [(62,true,0,-9938,1),(62,true,1,0,1),
            (62,false,0,0,0),(63,true,0,0,0)] {
            let mut value=leaf(ply,0);value["inCheck"]=json!(checked);value["legalReplyCount"]=json!(replies);
            value["killers"]=preferences(ply+1);
            let observed=MateLeaf::parse(&value).unwrap().observe();
            assert_eq!(observed["score"],score);assert_eq!(observed["replyQueries"],queries);
            assert_eq!(observed["killers"],json!([]));assert_eq!(observed["chargedSearchUnits"],1);
        }
        let mut value=leaf(3,0);value["halfmoveClock"]=json!(3);
        value["currentMove"]=remembered("b1a1");value["earlierMove"]=remembered("a1b1");
        let observed=MateLeaf::parse(&value).unwrap().observe();
        assert_eq!(observed["score"],0);assert_eq!(observed["replyQueries"],0);
        value["currentMove"]=Value::Null;value["earlierMove"]=Value::Null;
        let observed=MateLeaf::parse(&value).unwrap().observe();
        assert_eq!(observed["isCycle"],false);assert_eq!(observed["score"],-9997);
        assert_eq!(observed["replyQueries"],1);
    }

    #[test]
    fn standalone_reversal_validates_even_below_guard_and_ignores_side_kind_promotion() {
        let mut value=json!({"searchPly":3,"halfmoveClock":3,
            "currentMove":{"move":"a1b1q","kind":"ordinary"},
            "earlierMove":{"move":"b1a1","kind":"castle"},
            "current":{"side":"white","castling":"Kq","enPassant":"d6"},
            "baseline":{"side":"black","castling":"Kq","enPassant":"d6"}});
        assert_eq!(Reversal::parse(&value).unwrap().observe()["isCycle"],true);
        value["searchPly"]=json!(0);value["baseline"]["castling"]=json!("qK");
        assert!(Reversal::parse(&value).is_err());
        value["baseline"]["castling"]=json!("Kq");value["currentMove"]=Value::Null;
        value["earlierMove"]=Value::Null;value["searchPly"]=json!(3);
        assert_eq!(Reversal::parse(&value).unwrap().observe()["isCycle"],false);
    }

    #[test]
    fn mate_position_uses_actual_replies_broad_setup_and_ceiling_before_checkmate() {
        let fen="7k/6Q1/5K2/8/8/8/8/8 b - -";
        for (ply,score) in [(62,-9938),(63,0)] {
            let observed=MatePosition::parse(&json!({"fen":fen,"searchPly":ply})).unwrap().observe();
            assert_eq!(observed["inCheck"],true);assert_eq!(observed["legalReplies"],0);
            assert_eq!(observed["score"],score);assert_eq!(observed["chargedSearchUnits"],1);
        }
        for fen in ["7k/8/8/8/8/8/8/K6R w - -", "7k/8/8/3nP3/8/8/8/K7 w - d6"] {
            assert!(MatePosition::parse(&json!({"fen":fen,"searchPly":1})).is_ok());
        }
        // Occupied EP and unsupported raw rights are permitted by this
        // contract; they must reach native generation instead of setup reject.
        let raw=MatePosition::parse(&json!({"fen":"7k/8/3N4/4P3/8/8/8/K7 w KQkq d6","searchPly":1})).unwrap();
        assert_eq!(raw.position.rights,15);
        assert_eq!(raw.position.ep,rook2::types::Square::parse("d6").unwrap().0);
        assert!(raw.position.validate().is_ok());
        let mut actual=MoveList::new();movegen::generate_legal(&raw.position,&mut actual);
        assert!(actual.as_slice().iter().all(|m| m.kind()!=rook2::types::MoveKind::EnPassant));
        assert_eq!(raw.observe()["score"],0);
        for fen in ["7k/8/8/8/8/8/8/K7 w qK -", "7k/8/8/8/8/8/8/K7 w - d4",
            "7k/8/8/8/8/8/8/K7 w - - 0 1", "7k/8/8/8/8/8/8/K6P w - -"] {
            assert!(MatePosition::parse(&json!({"fen":fen,"searchPly":1})).is_err());
        }
    }
}
