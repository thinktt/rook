//! Cold fixed-completion transports over the native root controllers.
use super::{array, boolean, integer, moves, object, positions, text, unsigned32, Result};
use rook2::{engine::Search, first_iteration::{self, Step}, history::SearchHistory,
    movegen, timed, parameters::{Parameters, NAMES}, position::{Position, NO_SQUARE},
    quiescence::{Limits, Stats, Work}, types::{Color, Move, Piece, PieceKind}};
use serde_json::{json, Value};

// Exact released admission vectors, in native parameters::NAMES order.
// These are request controls, never fixture answers.
const PROFILES: [[i32; 30]; 4] = [
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0, 0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0, 100, 0, 14, 0, 99, 0, 67108864],
    [68, 103, 71, 100, 71, 100, 68, 103, 66, 95, 0, 0, 0, 0, 208, 208, 35, 35, 208, 208, 208, 208, -75, 30, 0, 6, -500, 99, 0, 16777216],
    [88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 0, 0, 115, 115, 107, 107, 105, 105, 122, 122, 115, 115, -10, 39, 0, 6, 500, 99, 0, 16777216],
    [136, 136, 158, 158, 113, 113, 136, 136, 143, 143, 0, 0, 0, 0, 7, 7, 78, 78, 78, 78, 94, 94, -10, 24, 0, 6, 0, 99, 0, 16777216],
];

// The default family differs from ordinaryIterations' neutral vector in md/tts.
// Selected seeded vectors have the same fixed coefficients but these exact rnd.
fn seeded_profile(values: [i32;30], completed: u8) -> bool {
    let mut default = Parameters::default().values;
    default[24] = values[24]; default[27] = values[27];
    if (2..=4).contains(&values[27]) && (0..=1000).contains(&values[24])
        && i32::from(completed) <= values[27] && values == default { return true; }
    completed == 2 && [75,10,20].into_iter().enumerate().any(|(i,rnd)| {
        let mut selected = PROFILES[i+1]; selected[24] = rnd; values == selected
    })
}
struct Request { root: Position, history: SearchHistory, parameters: Parameters,
    completed: Option<u8>, seed: Option<u32> }
impl Request {
    fn parse(input: &Value, ordinary: bool) -> Result<Self> {
        Self::parse_mode(input, ordinary, false)
    }
    fn parse_seeded(input: &Value) -> Result<Self> { Self::parse_mode(input, true, true) }
    fn parse_mode(input: &Value, ordinary: bool, seeded: bool) -> Result<Self> {
        if seeded {
            object(input, &["fen", "moves", "personalityParameters", "completedIterations", "seed", "controls"])?;
        } else if ordinary {
            object(input, &["fen", "moves", "personalityParameters", "completedIterations", "controls"])?;
        } else { object(input, &["fen", "moves", "personalityParameters", "controls"])?; }
        let fen = text(&input["fen"])?;
        object(&input["personalityParameters"], &NAMES)?;
        let mut values = [0; 30];
        for (index, name) in NAMES.iter().enumerate() {
            values[index] = integer(&input["personalityParameters"][*name], i32::MIN, i32::MAX)?;
        }
        let completed = if ordinary {
            let depth = integer(&input["completedIterations"], 2, if seeded { 4 } else { 6 })? as u8;
            Some(depth)
        } else { None };
        let seed = if seeded { Some(unsigned32(&input["seed"])?) } else { None };
        let controls = &input["controls"];
        let controls_supported;
        if ordinary {
            if seeded {
                object(controls, &["completion", "learnedState", "pondering", "workOrigin", "seedSource"])?;
                if text(&controls["seedSource"])? != "explicit" {
                    return Err("seed source must be explicit".into());
                }
            } else { object(controls, &["completion", "learnedState", "pondering", "workOrigin"])?; }
            let completion = text(&controls["completion"])?;
            let origin = text(&controls["workOrigin"])?;
            controls_supported = completion == "fixed-iterations" && origin == "after-root-preparation";
        } else {
            object(controls, &["iterationDepth", "rootPass", "learnedState", "pondering"])?;
            integer(&controls["iterationDepth"], 1, 1)?;
            controls_supported = text(&controls["rootPass"])? == "first-unrestricted";
        }
        // Complete syntax validation precedes setup, legal replay or search.
        let learned = text(&controls["learnedState"])?;
        let pondering = boolean(&controls["pondering"])?;
        let supplied = array(&input["moves"], 0, 255)?.iter().map(|value| {
            let spelling = text(value)?; positions::coordinate(spelling)?; Ok(spelling)
        }).collect::<Result<Vec<_>>>()?;
        if seeded {
            if !seeded_profile(values, completed.unwrap()) {
                return Err("personality/depth outside complete seeded vectors".into());
            }
        } else {
            let profile = PROFILES.iter().position(|profile| *profile == values)
                .ok_or("personality must equal a complete released vector")?;
            if !ordinary && profile != 0 { return Err("first iteration requires neutral vector".into()); }
            if profile != 0 && completed != Some(2) { return Err("selected vectors require exactly two iterations".into()); }
        }
        if !controls_supported || learned != "fresh-ordinary-search" || pondering {
            return Err("unsupported fixed-completion controls".into());
        }
        // Same POSITION-SETUP width and normalized EP admission as Q-tree;
        // bounded moveSequence material caps and selected-child gates do not apply.
        let mut root = Position::from_fen(fen)?;
        if movegen::in_check(&root, root.side.opponent()) {
            return Err("initial nonmoving king is in check".into());
        }
        if root.ep != NO_SQUARE {
            let rank = if root.side == Color::White { 5 } else { 2 };
            if root.ep / 8 != rank { return Err("retained EP has wrong rank".into()); }
            let victim = if root.side == Color::White { root.ep - 8 } else { root.ep + 8 };
            if root.board[victim as usize]
                != Piece::new(root.side.opponent(), PieceKind::Pawn) {
                return Err("retained EP requires ordinary rank and opposing pawn victim".into());
            }
        }
        let mut history = SearchHistory::new(&root);
        for spelling in supplied {
            let movement = positions::legal_move(&root, spelling)?;
            root = root.played_unchecked(movement);
            history.push(&root, Some(movement));
        }
        history.mark_root();
        Ok(Self { root, history, parameters: Parameters { values }, completed, seed })
    }

    fn observe(mut self) -> Result<Value> {
        let mut search = Search::<true>::new(&self.root);
        self.parameters.bind(&mut search).map_err(|error| format!("parameter binding: {error:?}"))?;
        let limits = Limits { nodes: Some(4095) };
        if let Some(completed) = self.completed {
            let mut raw_scores = Vec::new();
            let result = if let Some(seed) = self.seed {
                search.run_seeded_iterations(self.root, &mut self.history, completed, limits,
                    seed, self.parameters.values[24] as u32, |raw| raw_scores.push(raw))
            } else { search.run_iterations(self.root, &mut self.history, completed, limits) };
            let outcome = result.map_err(|error| format!("fixed iterations did not complete: {error:?}"))?;
            qualified_ordinary(&outcome.stats)?;
            let mut raw_scores = raw_scores.into_iter();
            let iterations = outcome.iterations.iter().map(|iteration| {
                validate_result(iteration.score, &iteration.pv, iteration.work, &iteration.steps)?;
                let mut records = steps(&iteration.steps);
                if let Some(seed) = self.seed {
                    for (step, record) in iteration.steps.iter().zip(&mut records) {
                        let raw = raw_scores.next().ok_or("missing raw root observation")?;
                        let adjustment = timed::random_adjustment(seed, self.parameters.values[24] as u32, step.movement);
                        record["randomization"] = json!({"adjustment":adjustment,
                            "childWindow":{"lower":timed::score_add(step.lower,-adjustment),
                                "upper":timed::score_add(10000,-adjustment)},"rawScore":raw});
                    }
                }
                Ok(json!({"depth":iteration.depth,"candidates":variation(&iteration.candidates),
                    "steps":records,"score":iteration.score,
                    "principalVariation":variation(&iteration.pv),"work":work(iteration.work)}))
            }).collect::<Result<Vec<_>>>()?;
            if raw_scores.next().is_some() { return Err("extra raw root observation".into()); }
            let mut output = json!({"initialCandidates":variation(&outcome.initial_candidates),"iterations":iterations,
                "result":{"score":outcome.score,"principalVariation":variation(&outcome.pv),"work":work(outcome.work)}});
            if let Some(seed) = self.seed { output["seed"] = json!(seed); }
            Ok(output)
        } else {
            let outcome = first_iteration::run(&mut search, self.root, &mut self.history, limits)
                .map_err(|error| format!("first iteration did not complete: {error:?}"))?;
            validate_result(outcome.score, &outcome.pv, outcome.work, &outcome.steps)?;
            Ok(json!({"candidates":variation(&outcome.candidates),"steps":steps(&outcome.steps),
                "score":outcome.score,"principalVariation":variation(&outcome.pv),"work":work(outcome.work)}))
        }
    }
}

fn qualified_ordinary(stats: &Stats) -> Result<()> {
    // Every completed initial phase has D>=4 and therefore offset2 is eligible.
    // With no tail, aggregate equality proves exactly one pass per entered phase.
    if stats.iio_tail_phases != 0 || stats.iio_passes != stats.iio_initial_phases
        || stats.iio_nonzero_fresh_extensions != 0 || stats.accumulated_extension_uses != 0 {
        return Err("ordinary search exceeds qualified IIO boundary".into());
    }
    Ok(())
}
fn validate_result(score: i32, pv: &[Move], sample: Work, steps: &[Step]) -> Result<()> {
    let bounded = |score: i32| (-10000..=10000).contains(&score);
    if !bounded(score) || pv.len() > 63 || sample.charged_search_units >= 4096
        || steps.is_empty() { return Err("result exceeds fixed-search boundary".into()); }
    for step in steps {
        if ![step.lower, step.score, step.best, step.second].into_iter().all(bounded)
            || step.child_pv.len() > 63 || step.root_pv.len() > 63
            || step.work.charged_search_units >= 4096 {
            return Err("step exceeds fixed-search boundary".into());
        }
    }
    Ok(())
}
fn variation(pv: &[Move]) -> Vec<Value> { pv.iter().copied().map(moves::descriptor).collect() }
fn work(sample: Work) -> Value {
    json!({"searchCounterDelta":sample.effective_search_count(),
        "chargedSearchUnits":sample.charged_search_units,"chargedRelationQueries":sample.charged_relation_queries})
}
fn steps(records: &[Step]) -> Vec<Value> {
    records.iter().map(|step| json!({"move":moves::descriptor(step.movement),
        "window":{"lower":step.lower,"upper":10000},"score":step.score,
        "bestScore":step.best,"secondScore":step.second,
        "childPrincipalVariation":variation(&step.child_pv),
        "principalVariation":variation(&step.root_pv),"work":work(step.work)})).collect()
}
pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "search.firstIteration" => Request::parse(input, false)?.observe(),
        "search.ordinaryIterations" => Request::parse(input, true)?.observe(),
        "search.seededOrdinaryIterations" => Request::parse_seeded(input)?.observe(),
        _ => Err("unknown fixed-iteration operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    fn request(fen: &str, profile: usize, completed: Option<u8>) -> Value {
        let parameters: serde_json::Map<String, Value> = NAMES.iter().zip(PROFILES[profile])
            .map(|(name,value)| (name.to_string(),json!(value))).collect();
        let mut input = json!({"fen":fen,"moves":[],"personalityParameters":parameters});
        if let Some(depth) = completed {
            input["completedIterations"] = json!(depth);
            input["controls"] = json!({"completion":"fixed-iterations","learnedState":"fresh-ordinary-search",
                "pondering":false,"workOrigin":"after-root-preparation"});
        } else {
            input["controls"] = json!({"iterationDepth":1,"rootPass":"first-unrestricted",
                "learnedState":"fresh-ordinary-search","pondering":false});
        }
        input
    }

    fn seeded_request(fen: &str, md: u8, completed: u8, rnd: u32, seed: u32) -> Value {
        let mut input = request(fen,0,Some(completed));
        let mut parameters = Parameters::default();
        parameters.values[27] = i32::from(md); parameters.values[24] = rnd as i32;
        input["personalityParameters"] = Value::Object(NAMES.iter().zip(parameters.values)
            .map(|(name,value)| (name.to_string(),json!(value))).collect());
        input["seed"] = json!(seed); input["controls"]["seedSource"] = json!("explicit"); input
    }

    #[test]
    fn seeded_profiles_keep_exact_default_family_and_selected_vectors() {
        for md in 2..=4 { for completed in 2..=4 { for rnd in [0,1,1000] {
            let input = seeded_request(START,md,completed,rnd,0);
            assert_eq!(Request::parse_seeded(&input).is_ok(),completed<=md);
        } } }
        for (profile,rnd) in [(1,75),(2,10),(3,20)] {
            let mut input = request(START,profile,Some(2));
            input["personalityParameters"]["rnd"] = json!(rnd);
            input["seed"] = json!(u32::MAX); input["controls"]["seedSource"] = json!("explicit");
            assert!(Request::parse_seeded(&input).is_ok());
            for (name,value) in [("rnd",rnd+1),("md",3),("tts",75497472)] {
                let mut changed=input.clone(); changed["personalityParameters"][name]=json!(value);
                assert!(Request::parse_seeded(&changed).is_err());
            }
            input["completedIterations"]=json!(3); assert!(Request::parse_seeded(&input).is_err());
        }
        for (name,value) in [("md",1),("md",5),("rnd",-1),("rnd",1001),("tts",67108864)] {
            let mut input=seeded_request(START,3,2,50,0); input["personalityParameters"][name]=json!(value);
            assert!(Request::parse_seeded(&input).is_err());
        }
        for name in NAMES {
            let mut input=seeded_request(START,3,2,50,0);
            input["personalityParameters"].as_object_mut().unwrap().remove(name);
            assert!(Request::parse_seeded(&input).is_err());
        }
    }

    #[test]
    fn seeded_schema_validates_explicit_zero_and_all_controls_before_replay() {
        let valid=seeded_request(START,3,2,50,0);
        assert_eq!(Request::parse_seeded(&valid).unwrap().seed,Some(0));
        for seed in [json!(-1),json!(4294967296u64),json!(0.5),json!(false),json!("0")] {
            let mut input=valid.clone(); input["seed"]=seed; assert!(Request::parse_seeded(&input).is_err());
        }
        let mut input=valid.clone(); input["controls"]["seedSource"]=json!("clock");
        assert!(Request::parse_seeded(&input).is_err());
        input=valid.clone(); input["controls"]["extra"]=Value::Null;
        assert!(Request::parse_seeded(&input).is_err());
        input=valid; input["moves"]=json!(["a1a8"]); input["seed"]=json!(false);
        match Request::parse_seeded(&input) {
            Err(error)=>assert_eq!(error,"expected unsigned integer"),
            Ok(_)=>panic!("malformed seed must precede illegal replay"),
        }
    }

    #[test]
    fn seeded_reached_black_root_keeps_history_and_parameter_ownership() {
        let mut input=seeded_request(START,3,2,51,2147483648);
        input["moves"]=json!(["e2e4"]);
        let parsed=Request::parse_seeded(&input).unwrap();
        assert_eq!(parsed.root.side,Color::Black);
        assert_eq!(parsed.history.pre_root_len(),1);
        assert_eq!(parsed.history.search_ply(),0);
        assert_eq!(parsed.seed,Some(2147483648));
        assert_eq!(parsed.parameters.values[24],51);
        assert_eq!(parsed.parameters.values[29],75497472);
    }

    #[test]
    fn seeded_zero_randomness_projects_actual_completed_scores_without_extra_fields() {
        let input=seeded_request(START,2,2,0,0);
        let output=dispatch("search.seededOrdinaryIterations",&input).unwrap();
        assert_eq!(output["seed"],json!(0));
        assert_eq!(output.as_object().unwrap().len(),4);
        for iteration in output["iterations"].as_array().unwrap() {
            for step in iteration["steps"].as_array().unwrap() {
                assert_eq!(step.as_object().unwrap().len(),9);
                let random=&step["randomization"];
                assert_eq!(random["adjustment"],json!(0));
                assert_eq!(random["rawScore"],step["score"]);
                assert_eq!(random["childWindow"],step["window"]);
            }
        }
        assert_eq!(dispatch("search.seededOrdinaryIterations",&input).unwrap(),output);
        let last=output["iterations"].as_array().unwrap().last().unwrap();
        for name in ["score","principalVariation","work"] { assert_eq!(output["result"][name],last[name]); }
    }

    #[test]
    fn complete_profiles_and_fixed_completion_are_exact_before_search() {
        for depth in 2..=6 { assert!(Request::parse(&request(START,0,Some(depth)),true).is_ok()); }
        for profile in 1..=3 {
            assert!(Request::parse(&request(START,profile,Some(2)),true).is_ok());
            assert!(Request::parse(&request(START,profile,Some(3)),true).is_err());
            assert!(Request::parse(&request(START,profile,None),false).is_err());
        }
        for name in NAMES {
            let mut input = request(START,0,None);
            input["personalityParameters"].as_object_mut().unwrap().remove(name);
            assert!(Request::parse(&input,false).is_err());
        }
        let mut input = request(START,0,Some(2));
        input["personalityParameters"]["opk"] = json!(1);
        assert!(Request::parse(&input,true).is_err());
        input = request(START,0,None); input["rootMove"] = Value::Null;
        assert!(Request::parse(&input,false).is_err());
        input = request(START,0,Some(2)); input["controls"]["workOrigin"] = json!("before-root-preparation");
        assert!(Request::parse(&input,true).is_err());
    }

    #[test]
    fn all_schema_and_coordinate_shapes_precede_sequential_legality() {
        let mut input = request(START,0,None);
        input["moves"] = json!(["a1a8"]); // syntax-valid but illegal
        input["controls"]["pondering"] = json!(0);
        match Request::parse(&input,false) {
            Err(error) => assert_eq!(error,"expected boolean"),
            Ok(_) => panic!("malformed control must precede replay"),
        }
        input["controls"]["pondering"] = json!(false);
        input["moves"] = json!(["a1a8","é2e4"]);
        assert!(Request::parse(&input,false).is_err());
        input["moves"] = json!(vec!["a1b1";256]);
        assert!(Request::parse(&input,false).is_err());
    }

    #[test]
    fn setup_keeps_broad_piece_population_and_normalized_ep_domain() {
        let broad = Request::parse(&request("7k/6pp/8/8/8/QQQQQQQQ/QQ6/K7 w - - 0 1",0,None),false).unwrap();
        assert_eq!(broad.root.counts[0][PieceKind::Queen.index()],10);
        let normalized = Request::parse(&request("7k/8/8/8/8/8/8/K7 w KQ e6 255 1",0,None),false).unwrap();
        assert_eq!((normalized.root.rights,normalized.root.ep),(0,NO_SQUARE));
        assert!(Request::parse(&request("7k/8/8/3pP3/8/8/8/K7 w - d6 0 1",0,None),false).is_ok());
        for fen in ["7k/8/8/3nP3/8/8/8/K7 w - d6 0 1",
            "7k/8/8/8/8/8/7R/7K w - - 0 1"] {
            assert!(Request::parse(&request(fen,0,None),false).is_err());
        }
    }

    #[test]
    fn history_is_carried_to_the_reached_root_without_rebuilding_chronology() {
        let mut input = request(START,0,None);
        input["moves"] = json!(["g1f3","g8f6","f3g1","f6g8"]);
        let parsed = Request::parse(&input,false).unwrap();
        assert_eq!(parsed.history.pre_root_len(),4);
        assert_eq!(parsed.history.search_ply(),0);
        assert_eq!(parsed.root.placement(),Position::from_fen(START).unwrap().placement());
        assert_eq!(parsed.root.halfmove,4);
    }

    #[test]
    fn complete_first_roots_admit_checking_and_early_return_children_but_no_terminal_root() {
        for fen in ["7k/8/8/8/8/8/8/K7 w - - 0 1",
            "7k/6pp/6Q1/8/8/3B4/8/K7 w - - 0 1"] {
            let input = request(fen,0,None);
            let parsed = Request::parse(&input,false).unwrap();
            let mut legal = movegen::MoveList::new(); movegen::generate_legal(&parsed.root,&mut legal);
            let output = dispatch("search.firstIteration",&input).unwrap();
            assert_eq!(output["candidates"],json!(variation(legal.as_slice())));
            assert_eq!(output["steps"].as_array().unwrap().len(),legal.len);
            assert_eq!(output["work"],output["steps"].as_array().unwrap().last().unwrap()["work"]);
            assert_eq!(dispatch("search.firstIteration",&input).unwrap(),output);
        }
        let input=request("7k/6Q1/5K2/8/8/8/8/8 b - - 0 1",0,None);
        assert!(Request::parse(&input,false).is_ok());
        assert!(dispatch("search.firstIteration",&input).is_err());
    }

    #[test]
    fn ordinary_first_records_match_first_controller_and_final_work_remains_cumulative() {
        let first=dispatch("search.firstIteration",&request(START,0,None)).unwrap();
        let output=dispatch("search.ordinaryIterations",&request(START,0,Some(2))).unwrap();
        let iteration=&output["iterations"][0];
        for name in ["candidates","steps","score","principalVariation","work"] {
            assert_eq!(first[name],iteration[name]);
        }
        let final_iteration=&output["iterations"][1];
        for name in ["score","principalVariation","work"] { assert_eq!(output["result"][name],final_iteration[name]); }
        assert!(final_iteration["work"]["chargedSearchUnits"].as_u64().unwrap()
            > first["work"]["chargedSearchUnits"].as_u64().unwrap());
    }

    #[test]
    fn allowed_initial_single_pass_ordering_is_exposed_without_suppressing_native_work() {
        for fen in ["1r5k/7p/6Q1/8/8/3B4/8/K7 b - - 0 1",
            "1r5k/6pp/6Q1/8/8/3B4/8/K7 b - - 0 1"] {
            let input=request(fen,0,Some(5));
            let mut parsed=Request::parse(&input,true).unwrap();
            let mut native=Search::<true>::new(&parsed.root); parsed.parameters.bind(&mut native).unwrap();
            let actual=native.run_iterations(parsed.root,&mut parsed.history,5,Limits{nodes:Some(4095)}).unwrap();
            assert!(actual.stats.iio_initial_phases>0); qualified_ordinary(&actual.stats).unwrap();
            let output=dispatch("search.ordinaryIterations",&input).unwrap();
            assert_eq!(output["result"]["work"],work(actual.work));
            assert_eq!(output["result"]["principalVariation"],json!(variation(&actual.pv)));
            assert_eq!(output["iterations"].as_array().unwrap().len(),5);
        }
    }
}
