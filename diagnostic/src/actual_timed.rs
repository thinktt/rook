//! Cold, distinct admitted transports over actual native timed/session owners.
use super::{boolean, integer, moves, object, text, unsigned32, Result};
use rook2::{engine::Search, history::SearchHistory, movegen::{self, MoveList},
    output::{self, Event, Post}, parameters::{self, Parameters, NAMES},
    position::Position, quiescence::{Limits, Work}, session::{self, Action, Session},
    timed::{self, Controls, Point}, types::Move};
use serde_json::{json, Value};
use std::time::{SystemTime, UNIX_EPOCH};

// Exact released ordinary neutral vector, in native NAMES order. Request
// controls only: not startup defaults or a fixture-derived search answer.
const NEUTRAL: [i32;30] = [100,100,100,100,100,100,100,100,100,100,0,0,
    100,100,100,100,100,100,100,100,100,100,0,100,0,14,0,99,0,67108864];
const SAFE: u64 = 9_007_199_254_740_991;
fn profile(md: i32, rnd: i32) -> Parameters {
    let mut values=NEUTRAL; values[27]=md; values[24]=rnd; Parameters{values}
}
fn check_parameters(value: &Value, expected: &Parameters) -> Result<()> {
    object(value,&NAMES)?;
    let mut values=[0;30];
    for (index,name) in NAMES.iter().enumerate() {
        values[index]=integer(&value[*name],i32::MIN,i32::MAX)?;
    }
    if values!=expected.values { return Err("personality must equal the complete admitted neutral vector".into()); }
    Ok(())
}
struct Seeded { seed:u32 }
impl Seeded {
    fn parse(input:&Value) -> Result<Self> {
        object(input,&["fen","moves","personalityParameters","seed","allowance","controls"])?;
        if text(&input["fen"])?!=session::START { return Err("seeded timed search requires exact standard FEN".into()); }
        if !input["moves"].as_array().ok_or("expected move history array")?.is_empty() {
            return Err("seeded timed search requires empty history".into());
        }
        check_parameters(&input["personalityParameters"],&profile(20,50))?;
        let seed=unsigned32(&input["seed"])?;
        object(&input["allowance"],&["averageCs","maximumCs"])?;
        integer(&input["allowance"]["averageCs"],1,1)?;
        integer(&input["allowance"]["maximumCs"],1,1)?;
        let c=&input["controls"];
        object(c,&["completion","learnedState","pondering","seedSource","workClock","workOrigin"])?;
        for (key,expected) in [("completion","work-clock"),("learnedState","fresh-ordinary-search"),
            ("seedSource","explicit"),("workClock","kingwcr-reset-safe"),("workOrigin","after-root-preparation")] {
            if text(&c[key])?!=expected { return Err(format!("unsupported seeded timed {key}")); }
        }
        if boolean(&c["pondering"])? { return Err("pondering is outside seeded timed admission".into()); }
        Ok(Self{seed})
    }
    fn observe(self) -> Result<Value> {
        let root=Position::from_fen(session::START)?;
        let mut history=SearchHistory::new(&root);
        let mut search=Search::<true>::new(&root);
        profile(20,50).bind(&mut search).map_err(|e|format!("parameter binding: {e:?}"))?;
        let outcome=search.run_work_timed(root,&mut history,Controls{average_cs:1,maximum_cs:1,
            origin:0,seed:self.seed,randomness:50,maximum_entered_iterations:6},Limits{nodes:Some(8192)})
            .map_err(|e|format!("seeded timed search did not reach its admitted stop: {e:?}"))?;
        if history.search_ply()!=0 { return Err("native timed history did not unwind".into()); }
        validate_seeded(&outcome)?;
        if outcome.seed!=self.seed { return Err("native timed seed changed".into()); }
        let events=output::completed_events(root,&outcome,search.evaluator.draw_preference,
            search.config.selectivity,true).map_err(|e|format!("native output: {e:?}"))?;
        let iterations=outcome.iterations.iter().map(|i|json!({"depth":i.depth,"complete":i.complete,
            "steps":i.steps.iter().map(|s|json!({"move":moves::descriptor(s.movement),
                "window":{"lower":s.window[0],"upper":s.window[1]},"adjustment":s.adjustment,
                "score":s.score,"bestScore":s.best,"secondScore":s.second,
                "childPrincipalVariation":variation(&s.child_pv),"principalVariation":variation(&s.pv),
                "work":work(s.work)})).collect::<Vec<_>>()})).collect::<Vec<_>>();
        let checks=outcome.checks.iter().map(|c|json!({"point":point(c.point),"depth":c.depth,
            "rootIndex":c.root_index,"work":work(c.work),"elapsedCs":c.elapsed_cs,
            "limitSeconds":c.limit_seconds,"stop":c.stop})).collect::<Vec<_>>();
        let pending=outcome.stop.pending.map(|p|json!({"move":moves::descriptor(p.movement),
            "window":{"lower":p.window[0],"upper":p.window[1]},"adjustment":p.adjustment}));
        let captured=outcome.result.as_ref().ok_or("seeded timed search has no actual capture")?;
        Ok(json!({"seed":outcome.seed,"initialCandidates":variation(&outcome.initial_candidates),
            "iterations":iterations,"timeChecks":checks,
            "stop":{"point":point(outcome.stop.point),"depth":outcome.stop.depth,
                "rootIndex":outcome.stop.root_index,"work":work(outcome.stop.work),
                "elapsedCs":outcome.stop.elapsed_cs,"pendingRoot":pending},
            "result":{"depth":captured.depth,"rootIndex":captured.root_index,"score":captured.score,
                "principalVariation":variation(&captured.pv),"searchId":captured.search_id,
                "elapsedCs":captured.elapsed_cs},"events":events.iter().map(event).collect::<Vec<_>>() }))
    }
}
fn point(p:Point) -> &'static str { match p { Point::Root=>"root",Point::Iteration=>"iteration",Point::Poll=>"poll" } }
fn variation(pv:&[Move]) -> Vec<Value> { pv.iter().copied().map(moves::descriptor).collect() }
fn work(w:Work) -> Value { json!({"chargedSearchUnits":w.charged_search_units,"chargedRelationQueries":w.charged_relation_queries}) }
fn post(p:&Post) -> Value { json!({"depthToken":p.fields.depth_token,"evaluation":p.fields.evaluation,
    "searchId":p.fields.search_id,"pv":p.pv,"engineCentiseconds":p.fields.centiseconds}) }
fn event(e:&Event) -> Value { match e {
    Event::Post(p)=>{ let mut value=post(p);value["type"]=json!("post");value },
    Event::Move(m)=>json!({"type":"move","move":m.to_string()}),
} }
fn bounded_score(s:i32)->bool { (-10000..=10000).contains(&s) }
fn bounded_work(w:Work,max:u64)->bool { w.charged_search_units<=max && w.charged_relation_queries<=SAFE }
fn bounded_pv(pv:&[Move])->bool { pv.len()<=63 }
fn validate_records(out:&timed::Outcome,max:u64)->Result<()> {
    if out.initial_candidates.is_empty() || !bounded_work(out.stop.work,max) {
        return Err("timed result exceeds admitted root/work boundary".into());
    }
    let total=out.stop.work;
    let within=|w:Work|bounded_work(w,max)&&w.charged_search_units<=total.charged_search_units
        &&w.charged_relation_queries<=total.charged_relation_queries;
    for i in &out.iterations {
        for s in &i.steps {
            if !s.window.into_iter().all(bounded_score) || ![s.score,s.best,s.second].into_iter().all(bounded_score)
                || !bounded_pv(&s.child_pv) || !bounded_pv(&s.pv) || !within(s.work) {
                return Err("timed step exceeds admitted score/PV/work boundary".into());
            }
            for pass in &s.passes {
                if !pass.window.into_iter().all(bounded_score)||!bounded_score(pass.returned_score)||!within(pass.work) {
                    return Err("timed pass exceeds admitted boundary".into());
                }
            }
        }
    }
    for c in &out.checks {
        if !within(c.work)||!c.limit_seconds.is_finite()||c.limit_seconds<0.0 {
            return Err("timed check exceeds admitted boundary".into());
        }
    }
    for c in out.result.iter().chain(&out.publications) {
        if !bounded_score(c.score)||!bounded_pv(&c.pv)||c.search_id>total.charged_search_units
            ||c.depth<1||usize::from(c.depth)>out.iterations.len()
            ||c.root_index>=out.initial_candidates.len() {
            return Err("timed capture exceeds admitted boundary".into());
        }
    }
    Ok(())
}
fn validate_seeded(out:&timed::Outcome)->Result<()> {
    validate_records(out,8192)?;
    if out.stats.iio_initial_phases!=0 || out.stats.iio_tail_phases!=0 {
        return Err("seeded timed search entered unsupported internal iterative ordering".into());
    }
    if !matches!((out.stop.point,out.stop.reason),(Point::Root,"root")|(Point::Poll,"maximum"))
        || out.stop.root_index.is_none() || out.stop.depth<1 || out.stop.depth>6
        || out.iterations.is_empty() || out.iterations.len()>6 || out.result.is_none()
        || (out.stop.point==Point::Poll)!=out.stop.pending.is_some() {
        return Err("seeded timed result is outside natural root/poll completion".into());
    }
    for (index,i) in out.iterations.iter().enumerate() {
        let last=index+1==out.iterations.len();
        if usize::from(i.depth)!=index+1 || i.complete==last
            || i.steps.len()>out.initial_candidates.len()
            || (!last && i.steps.len()!=out.initial_candidates.len()) {
            return Err("seeded timed iteration is incomplete or outside its depth boundary".into());
        }
    }
    if out.iterations.last().unwrap().depth!=out.stop.depth {
        return Err("stop depth disagrees with actual iteration".into());
    }
    for c in &out.checks {
        if c.depth<1||c.depth>6 || (c.depth==1&&c.point!=Point::Poll)
            || (c.point==Point::Iteration)!=c.root_index.is_none()
            || c.root_index.is_some_and(|index|index>=out.initial_candidates.len()) {
            return Err("invalid native check chronology/domain".into());
        }
    }
    let check=out.checks.last().ok_or("natural stop has no actual clock check")?;
    if !check.stop||check.point!=out.stop.point||check.depth!=out.stop.depth
        ||check.root_index!=out.stop.root_index||check.work!=out.stop.work
        ||check.elapsed_cs!=out.stop.elapsed_cs {
        return Err("natural stop does not close from its actual clock check".into());
    }
    Ok(())
}

struct Go { commands:Vec<String> }
impl Go {
    fn parse(input:&Value)->Result<Self> {
        object(input,&["commands","remainingTimeCs"])?;
        integer(&input["remainingTimeCs"],60000,60000)?;
        // No invented per-request command-count bound. The native ordinary
        // per-record byte/token limits still apply to every setup command.
        let supplied=input["commands"].as_array().ok_or("expected setup command array")?;
        let mut commands=Vec::new();let mut setboards=0;let mut post=false;let mut easy=false;
        for value in supplied {
            let line=text(value)?;
            if line.len()>1022||!line.is_ascii()||line.bytes().any(|b|b==0||b==b'\r'||b==b'\n'
                ||(b.is_ascii_whitespace()&&b!=b' '&&b!=b'\t')) {
                return Err("setup record is outside native ordinary syntax".into());
            }
            let words=line.split_ascii_whitespace().collect::<Vec<_>>();
            if words.len()>40 { return Err("too many ordinary setup tokens".into()); }
            match words.as_slice() {
                ["post"]=>post=true,
                ["easy"]=>easy=true,
                ["setboard",rest @ ..] if rest.len()==6=>{
                    // Actual Session::setboard owns semantic normalization;
                    // full FEN counters must not be narrowed to Position's u8.
                    for (field,min) in [(rest[4],0),(rest[5],1)] {
                        if !field.bytes().all(|b|b.is_ascii_digit())
                            ||parameters::integer(field).map_err(|e|format!("FEN counter: {e:?}"))?<min {
                            return Err("invalid public setboard counter".into());
                        }
                    }
                    setboards+=1;
                },
                ["cm_parm",args @ ..] if !args.is_empty()=>{
                    for arg in args {
                        if *arg=="default" { continue; }
                        let (name,value)=arg.split_once('=').ok_or("setup parameters require assignments or default")?;
                        if !NAMES.contains(&name)&&!["cc","mob","ks","pp","pw"].contains(&name) {
                            return Err("unknown setup parameter".into());
                        }
                        parameters::integer(value).map_err(|e|format!("setup integer: {e:?}"))?;
                    }
                },
                _=>return Err("command is outside fresh goOutcome setup".into()),
            }
            commands.push(line.to_owned());
        }
        if setboards!=1||!post||!easy { return Err("goOutcome requires one setboard, post and easy".into()); }
        Ok(Self{commands})
    }
    fn setup(&self)->Result<Session<true>> {
        let mut state=Session::<true>::default();
        idle(&mut state,"xboard")?;
        for command in &self.commands { idle(&mut state,command)?; }
        if state.parameters!=profile(1,0)||!state.post||state.pondering||!state.force||!state.moves.is_empty() {
            return Err("goOutcome requires the complete neutral md1/rnd0 empty-history state".into());
        }
        idle(&mut state,"time 60000")?;idle(&mut state,"otim 60000")?;
        Ok(state)
    }
    fn observe(self)->Result<Value> {
        let mut state=self.setup()?;
        let root=state.position();
        let mut legal=MoveList::new();movegen::generate_legal(&root,&mut legal);
        if legal.len!=0&&!movegen::in_check(&root,root.side) {
            return Err("nonempty goOutcome root must actually be checked".into());
        }
        let seconds=SystemTime::now().duration_since(UNIX_EPOCH)
            .map_err(|_|"ordinary system clock precedes POSIX epoch")?.as_secs() as u32;
        let result=state.go(seconds,Limits{nodes:Some(4095)},1);
        match result {
            Err(session::Error::FatalEmptyRoot) if legal.len==0=>
                Ok(json!({"kind":"fatalExit","exit":{"code":1,"signal":Value::Null},"posts":[],"move":Value::Null})),
            Err(error)=>Err(format!("goOutcome did not produce its admitted native outcome: {error:?}")),
            Ok(result)=>{
                if legal.len==0 { return Err("native result disagrees with empty generated roots".into()); }
                let out=&result.outcome;validate_records(out,4095)?;
                if out.stop.point!=Point::Iteration||out.stop.depth!=1||out.iterations.len()!=1
                    ||!out.iterations[0].complete||out.iterations[0].steps.len()!=legal.len
                    ||out.initial_candidates.as_slice()!=legal.as_slice()||out.result.is_none() {
                    return Err("goOutcome did not complete its actual first root iteration".into());
                }
                let mut posts=Vec::new();let mut selected=None;
                for e in &result.events { match e {
                    Event::Post(p) if selected.is_none()=>posts.push(post(p)),
                    Event::Move(m) if selected.is_none()=>selected=Some(*m),
                    _=>return Err("invalid native goOutcome event order".into()),
                } }
                let selected=selected.ok_or("native goOutcome has no selected move")?;
                if out.result.as_ref().and_then(|c|c.pv.first()).copied()!=Some(selected) {
                    return Err("native selected move disagrees with retained capture".into());
                }
                Ok(json!({"kind":"move","posts":posts,"move":selected.to_string()}))
            },
        }
    }
}
fn idle(state:&mut Session<true>,line:&str)->Result<()> {
    match state.idle(line).map_err(|e|format!("native setup: {e:?}"))? {
        Action::Reply(_)=>Ok(()),_=>Err("fresh setup must remain idle".into()),
    }
}
pub(super) fn dispatch(operation:&str,input:&Value)->Result<Value> {
    match operation {
        "search.seededTimedSearch"=>Seeded::parse(input)?.observe(),
        "session.goOutcome"=>Go::parse(input)?.observe(),
        _=>Err("unknown actual timed operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const CHECKED:&str="4k3/8/8/8/1b6/P7/2P4P/4K3 w - - 0 1";
    fn vector(p:Parameters)->Value {
        Value::Object(NAMES.iter().zip(p.values).map(|(n,v)|(n.to_string(),json!(v))).collect())
    }
    fn seeded(seed:u32)->Value { json!({"fen":session::START,"moves":[],
        "personalityParameters":vector(profile(20,50)),"seed":seed,
        "allowance":{"averageCs":1,"maximumCs":1},
        "controls":{"completion":"work-clock","learnedState":"fresh-ordinary-search",
            "pondering":false,"seedSource":"explicit","workClock":"kingwcr-reset-safe",
            "workOrigin":"after-root-preparation"}}) }
    fn go(fen:&str)->Value {
        let delivered=NAMES.iter().zip(profile(1,0).values).map(|(n,v)|format!("{n}={v}"))
            .collect::<Vec<_>>().join(" ");
        json!({"commands":["post",format!("cm_parm {delivered}"),"easy",format!("setboard {fen}")],
            "remainingTimeCs":60000})
    }
    #[test]
    fn seeded_exact_profile_does_not_alias_startup_or_generic_admission() {
        let valid=seeded(0);assert!(Seeded::parse(&valid).is_ok());
        for (name,value) in [("md",6),("rnd",0),("tts",75497472),("opk",1)] {
            let mut input=valid.clone();input["personalityParameters"][name]=json!(value);
            assert!(Seeded::parse(&input).is_err());
        }
        for name in NAMES {
            let mut input=valid.clone();input["personalityParameters"].as_object_mut().unwrap().remove(name);
            assert!(Seeded::parse(&input).is_err());
        }
        let mut input=valid;input["personalityParameters"]["extra"]=json!(0);
        assert!(Seeded::parse(&input).is_err());
    }
    #[test]
    fn seeded_controls_validate_zero_unsigned_seeds_and_fixed_history() {
        for seed in [0,2147483648,u32::MAX] { assert_eq!(Seeded::parse(&seeded(seed)).unwrap().seed,seed); }
        for bad in [json!(-1),json!(4294967296u64),json!(false),json!(0.5),json!("0")] {
            let mut input=seeded(0);input["seed"]=bad;assert!(Seeded::parse(&input).is_err());
        }
        for (key,value) in [("completion",json!("natural-work-clock")),("seedSource",json!("clock")),
            ("pondering",json!(0)),("workOrigin",json!("before-root-preparation"))] {
            let mut input=seeded(0);input["controls"][key]=value;assert!(Seeded::parse(&input).is_err());
        }
        let mut input=seeded(0);input["moves"]=json!(["e2e4"]);assert!(Seeded::parse(&input).is_err());
        input=seeded(0);input["allowance"]["maximumCs"]=json!(2);assert!(Seeded::parse(&input).is_err());
        input=seeded(0);input["controls"]["analysis"]=json!(false);assert!(Seeded::parse(&input).is_err());
    }
    #[test]
    fn actual_seeded_stops_keep_pending_attempt_separate_from_retained_capture() {
        let out=dispatch("search.seededTimedSearch",&seeded(0)).unwrap();
        assert_eq!(out["seed"],json!(0));assert_eq!(out.as_object().unwrap().len(),7);
        assert_eq!(out["stop"]["point"],json!("poll"));
        let stopped=out["stop"]["work"]["chargedSearchUnits"].as_u64().unwrap();
        assert!(stopped>0&&stopped%4096==0);
        assert!(out["result"]["searchId"].as_u64().unwrap()<stopped);
        let pending=out["stop"]["pendingRoot"].as_object().unwrap();
        assert_eq!(pending.len(),3);assert!(!pending.contains_key("score"));
        let final_iteration=out["iterations"].as_array().unwrap().last().unwrap();
        assert_eq!(final_iteration["complete"],json!(false));
        let events=out["events"].as_array().unwrap();
        assert_eq!(events.last().unwrap()["type"],json!("move"));
        assert!(events[..events.len()-1].iter().all(|e|e["type"]==json!("post")));
        let high=dispatch("search.seededTimedSearch",&seeded(2147483648)).unwrap();
        assert_eq!(high["stop"]["point"],json!("root"));assert!(high["stop"]["pendingRoot"].is_null());
    }
    #[test]
    fn go_schema_has_no_fixture_count_limit_and_rejects_nonsetup_records() {
        let valid=go(CHECKED);assert!(Go::parse(&valid).is_ok());
        let mut many=valid.clone();
        many["commands"].as_array_mut().unwrap().extend((0..300).map(|_|json!("post")));
        assert!(Go::parse(&many).is_ok());
        for line in ["go","quit","sd 1","a2a4","nopost","hard","cm_parm bad=1","cm_parm rnd",
            "post\ngo","cm_parm rnd=0.5","setboard 8/8/8/8/8/8/8/8 w - -"] {
            let mut input=valid.clone();input["commands"].as_array_mut().unwrap().push(json!(line));
            assert!(Go::parse(&input).is_err());
        }
        let mut input=valid.clone();input["remainingTimeCs"]=json!(59999);assert!(Go::parse(&input).is_err());
        input=valid;input["expected"]=json!("move");assert!(Go::parse(&input).is_err());
    }
    #[test]
    fn public_setboard_normalization_preserves_wide_text_counters_without_history() {
        let input=go("4k3/8/8/8/1b6/P7/2P4P/4K3 w - - 2147483647 2147483647");
        let state=Go::parse(&input).unwrap().setup().unwrap();
        assert_eq!(state.position().halfmove,0);assert!(state.moves.is_empty());
        assert_eq!(state.states.len(),1);assert_eq!(state.parameters,profile(1,0));
        assert!(state.post&&!state.pondering&&state.force);
    }
    #[test]
    fn actual_go_distinguishes_completed_checked_root_and_generated_empty_union() {
        let normal=dispatch("session.goOutcome",&go(CHECKED)).unwrap();
        assert_eq!(normal["kind"],json!("move"));assert_eq!(normal.as_object().unwrap().len(),3);
        assert!(!normal["posts"].as_array().unwrap().is_empty());
        assert_eq!(normal["move"].as_str().unwrap().len(),4);
        for fen in ["7k/6Q1/6K1/8/8/8/8/8 b - - 0 1","7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"] {
            let state=Go::parse(&go(fen)).unwrap().setup().unwrap();
            let mut roots=MoveList::new();movegen::generate_legal(&state.position(),&mut roots);
            assert_eq!(roots.len,0);
            let fatal=dispatch("session.goOutcome",&go(fen)).unwrap();
            assert_eq!(fatal,json!({"kind":"fatalExit","exit":{"code":1,"signal":Value::Null},"posts":[],"move":Value::Null}));
        }
    }
    #[test]
    fn go_produced_domain_rejects_unchecked_nonempty_and_late_profile_reset() {
        assert!(dispatch("session.goOutcome",&go(session::START)).is_err());
        let mut input=go(CHECKED);input["commands"].as_array_mut().unwrap().push(json!("cm_parm default"));
        assert!(Go::parse(&input).unwrap().setup().is_err());
        input=go(CHECKED);input["commands"].as_array_mut().unwrap().push(json!("cm_parm md=2"));
        assert!(Go::parse(&input).unwrap().setup().is_err());
    }
}
