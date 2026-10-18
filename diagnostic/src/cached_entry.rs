//! Cold composition of native admission, result-table and supplied-score owners.
//! Parse complete requests before any semantic gate or mutable table operation.
use super::{admission, array, boolean, integer, learned::{self, Labels, TableEvent},
    moves, object, supplied::{self, FastCutoff, FastCutoffResult}, text, Result};
use rook2::{history::SearchHistory, ordinary_policy::{self, EvaluationBoundReturn, Learning},
    position::Position, remembered::{Query, RememberedTable, Store}, types::{Move, MoveKind}};
use serde_json::{json, Value};
use std::collections::BTreeMap;

struct CachedEntry {
    history:SearchHistory, learning:Learning, checked:bool, analysis:i32, ply:usize,
    query:Query, setup:Vec<TableEvent>, followup:Vec<Query>,
}
impl CachedEntry {
    fn parse(input:&Value) -> Result<Self> {
        object(input,&["context","setup","group","identity","followup"])?;
        let context=&input["context"];
        object(context,&["mode","searchPly","targetPly","maximumDepth","upperBound","lowerBound",
            "preRootLength","halfmoveClock","inCheck","analysis","prior","current",
            "currentMove","earlierMove","killers"])?;
        let ply=integer(&context["searchPly"],1,62)? as usize;
        let target=integer(&context["targetPly"],ply as i32+1,64)?;
        let maximum=integer(&context["maximumDepth"],0,99)?;
        match text(&context["mode"])? {
            "full" if (ply as i32)<maximum => {},
            "mateInterior" => {},
            _ => return Err("requires non-frontier full or interior mate context".into()),
        }
        let pre_root=integer(&context["preRootLength"],0,512)? as usize;
        let halfmove=integer(&context["halfmoveClock"],0,255)? as u8;
        let checked=boolean(&context["inCheck"])?;
        let analysis=integer(&context["analysis"],i32::MIN,i32::MAX)?;
        let current_move=moves::movement(&context["currentMove"])?;
        let earlier_move=moves::movement(&context["earlierMove"])?;
        let learning=admission::parse_killers(&context["killers"],64)?;
        // Repetition equality is independent from all result-table labels.
        let mut identities=BTreeMap::new();
        let prior=array(&context["prior"],pre_root+ply,pre_root+ply)?;
        let mut history=SearchHistory::new(&admission::opaque_position(&prior[0],&mut identities)?);
        for (index,state) in prior.iter().enumerate().skip(1) {
            let arrival=if ply>=3 && index==pre_root+ply-2 { earlier_move } else { None };
            history.push(&admission::opaque_position(state,&mut identities)?,arrival);
            if index==pre_root { history.mark_root(); }
        }
        let mut current=admission::opaque_position(&context["current"],&mut identities)?;
        current.halfmove=halfmove;history.push(&current,current_move);
        let mut labels=Labels::default();
        let setup=array(&input["setup"],0,128)?.iter()
            .map(|event|TableEvent::parse(event,&mut labels)).collect::<Result<Vec<_>>>()?;
        let query=labels.query(&json!({"group":input["group"],"identity":input["identity"],
            "searchPly":ply,"targetPly":target,"lowerBound":context["lowerBound"],
            "upperBound":context["upperBound"]}))?;
        let followup=array(&input["followup"],1,16)?.iter().map(|event| {
            match TableEvent::parse(event,&mut labels)? {
                TableEvent::Probe(query)=>Ok(query),
                _=>Err("followup requires probe events".into()),
            }
        }).collect::<Result<Vec<_>>>()?;
        Ok(Self { history,learning,checked,analysis,ply,query,setup,followup })
    }
    fn observe(mut self) -> Value {
        let mut table=RememberedTable::with_groups(16);
        for event in self.setup { event.apply(&mut table); }
        // These immutable auxiliary observations do not imply real-search
        // execution after a preceding return. The mutable query below does.
        let repetition=self.history.repetition_count(self.checked);
        let cycle=self.history.short_reversal();
        let draw=ordinary_policy::early_draw(&self.history,self.ply,self.checked,self.analysis,
            self.query.upper,&mut self.learning);
        let cache=if draw { None } else { Some(table.probe(self.query)) };
        let score=if draw { Some(0) } else { cache.as_ref().and_then(|hit|hit.score) };
        let outcome=if draw { "draw" } else if score.is_some() { "cached" } else { "continue" };
        let followup:Vec<_>=self.followup.into_iter().map(|query|learned::observation(table.probe(query))).collect();
        let killers:Vec<_>=(1..=64).filter_map(|ply| {
            let pair=self.learning.killers[ply];
            (pair!=[Move::NONE;2]).then(||json!({"ply":ply,
                "moves":[moves::descriptor(pair[0]),moves::descriptor(pair[1])]}))
        }).collect();
        json!({"repetitionCount":repetition,"isCycle":cycle,"outcome":outcome,"score":score,
            "cache":cache.map(learned::observation),"followup":followup,
            "chargedSearchUnits":1,"chargedRelationQueries":0,"killers":killers})
    }
}

struct FastEntry {
    cutoff:FastCutoff, iteration:i32, selectivity:i32, endgame:u16,
    current:Position, movement:Move, lower:i32, followups:Vec<Query>,
}
impl FastEntry {
    fn parse(query:&Value) -> Result<Self> {
        object(query,&["cutoff","iterationDepth","selectivity","endgameWeight","moveKind",
            "currentMaterial","lowerBound","followups"])?;
        let cutoff=FastCutoff::parse(&query["cutoff"])?;
        let kind=match text(&query["moveKind"])? {
            "ordinary"=>cutoff.capture.movement.kind(),
            "enPassant"=>MoveKind::EnPassant,
            "castling"=>MoveKind::Castle,
            _=>return Err("invalid fast-entry move kind".into()),
        };
        if kind!=cutoff.capture.movement.kind() && cutoff.capture.movement.kind()!=MoveKind::Ordinary {
            return Err("nonordinary kind requires null promotion".into());
        }
        let movement=Move::new(cutoff.capture.movement.from(),cutoff.capture.movement.to(),kind);
        let mut current=Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 0 1")?;
        current.counts=supplied::counts(&query["currentMaterial"])?;
        let lower=integer(&query["lowerBound"],-10000,cutoff.upper-1)?;
        let followups=array(&query["followups"],1,4)?.iter().map(|followup| {
            object(followup,&["searchPly","targetPly","lowerBound","upperBound"])?;
            let lower=integer(&followup["lowerBound"],-10000,10000)?;
            let upper=integer(&followup["upperBound"],-10000,10000)?;
            if lower>=upper { return Err("window must have lower strictly below upper".into()); }
            Ok(Query { group:0,identity:1,ply:integer(&followup["searchPly"],0,63)?,
                target:integer(&followup["targetPly"],0,64)?,lower,upper })
        }).collect::<Result<Vec<_>>>()?;
        Ok(Self { cutoff,current,movement,lower,followups,
            iteration:integer(&query["iterationDepth"],0,64)?,
            selectivity:integer(&query["selectivity"],i32::MIN,i32::MAX)?,
            endgame:integer(&query["endgameWeight"],0,256)? as u16 })
    }
    fn observe(self) -> Value {
        let adjustment=ordinary_policy::selective_depth(self.iteration,self.selectivity,
            self.endgame,self.cutoff.target).adjustment;
        let admitted=ordinary_policy::fast_admitted(&self.current,&self.cutoff.capture.position,
            Some(self.movement),self.cutoff.target-self.cutoff.ply,adjustment);
        let result=if admitted { self.cutoff.observe() } else { FastCutoffResult::default() };
        let mut table=RememberedTable::with_groups(1);
        if let Some(score)=result.score {
            table.store(Store { query:Query { group:0,identity:1,ply:self.cutoff.ply,
                target:self.cutoff.target,lower:self.lower,upper:self.cutoff.upper },score,
                move_hint:None,quiet_mate_checked:false,mark_depth:false });
        }
        let remembered:Vec<_>=self.followups.into_iter().map(|query|learned::observation(table.probe(query))).collect();
        json!({"cutoffScore":result.score,"pressureChecked":result.pressure_checked,
            "materialThreatQueried":result.threat_queried,"fastEvaluationQueried":admitted,
            "resultStored":result.score.is_some(),"remembered":remembered})
    }
}

struct EvaluationBounds { ply:i32,target:i32,lower:i32,upper:i32,evaluation_lower:i32,evaluation_upper:i32 }
impl EvaluationBounds {
    fn parse(query:&Value) -> Result<Self> {
        object(query,&["searchPly","targetPly","lowerBound","upperBound","staticScore","evaluationLower","evaluationUpper"])?;
        let ply=integer(&query["searchPly"],1,62)?;
        let target=integer(&query["targetPly"],ply+1,64)?;
        let lower=integer(&query["lowerBound"],-10000,10000)?;
        let upper=integer(&query["upperBound"],-10000,10000)?;
        if lower>=upper { return Err("window must have lower strictly below upper".into()); }
        integer(&query["staticScore"],-10000,10000)?;
        Ok(Self { ply,target,lower,upper,evaluation_lower:integer(&query["evaluationLower"],-10000,10000)?,
            evaluation_upper:integer(&query["evaluationUpper"],-10000,10000)? })
    }
    fn observe(self) -> Value {
        match ordinary_policy::evaluation_bounds(self.ply,self.target,self.evaluation_lower,self.evaluation_upper)
            .cutoff(self.lower,self.upper) {
            Some(EvaluationBoundReturn::Lower(score))=>json!({"outcome":"lower","score":score}),
            Some(EvaluationBoundReturn::Upper(score))=>json!({"outcome":"upper","score":score}),
            None=>json!({"outcome":"continue","score":null}),
        }
    }
}

pub(super) fn dispatch(operation:&str,input:&Value) -> Result<Value> {
    if operation=="search.cachedAdmission" { return Ok(CachedEntry::parse(input)?.observe()); }
    object(input,&["queries"])?;
    let queries=array(&input["queries"],1,4096)?;
    match operation {
        "search.fastEntry"=> {
            let parsed=queries.iter().map(FastEntry::parse).collect::<Result<Vec<_>>>()?;
            Ok(json!({"results":parsed.into_iter().map(FastEntry::observe).collect::<Vec<_>>()}))
        }
        "search.evaluationBounds"=> {
            let parsed=queries.iter().map(EvaluationBounds::parse).collect::<Result<Vec<_>>>()?;
            Ok(json!({"results":parsed.into_iter().map(EvaluationBounds::observe).collect::<Vec<_>>()}))
        }
        _=>Err("unsupported cached-entry operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn state(id:&str) -> Value {
        json!({"identity":id,"side":"white","castling":"KQ","enPassant":null})
    }
    fn probe(target:i32) -> Value {
        json!({"kind":"probe","group":"G","identity":"A","searchPly":1,
            "targetPly":target,"lowerBound":-1,"upperBound":1})
    }
    fn cached() -> Value {
        let movement=json!({"move":"a2a3q","kind":"ordinary"});
        json!({"context":{"mode":"full","searchPly":1,"targetPly":6,"maximumDepth":99,
            "lowerBound":-1,"upperBound":1,"preRootLength":3,"halfmoveClock":4,
            "inCheck":false,"analysis":0,"prior":[state("repeat"),state("x"),state("y"),state("z")],
            "current":state("repeat"),"currentMove":null,"earlierMove":null,
            "killers":[{"ply":2,"moves":[movement,null]},{"ply":64,"moves":[movement,null]}]},
            "setup":[{"kind":"store","group":"G","identity":"A","searchPly":1,"targetPly":2,
                "lowerBound":-1,"upperBound":1,"score":9000,"move":movement,
                "quietMateChecked":true,"markDepth":true}],
            "group":"G","identity":"A","followup":[probe(6),probe(6)]})
    }
    fn empty_material() -> Value {
        let side=json!({"pawn":0,"knight":0,"bishop":0,"rook":0,"queen":0});
        json!({"white":side,"black":side})
    }
    fn fast() -> Value {
        let profile=json!({"weak":0,"queen":0,"rook":0,"minor":0,"pawn":0});
        let neighbor=json!({"included":true,"previous":profile,"current":profile});
        let mut material=empty_material();material["black"]["knight"]=json!(2);
        json!({"cutoff":{"searchPly":1,"targetPly":2,"staticScore":100,"upperBound":0,
                "currentCheck":false,"previousCheck":false,
                "capture":{"promotion":null,"destination":null,"material":empty_material()},
                "pressure":{"side":"white","neighbors":vec![neighbor;8]},"materialThreat":0},
            "iterationDepth":10,"selectivity":14,"endgameWeight":0,"moveKind":"ordinary",
            "currentMaterial":material,"lowerBound":-1,
            "followups":[{"searchPly":1,"targetPly":2,"lowerBound":-1,"upperBound":0},
                {"searchPly":1,"targetPly":64,"lowerBound":-1,"upperBound":0}]})
    }
    fn fast_result(query:Value) -> Value { FastEntry::parse(&query).unwrap().observe() }

    #[test]
    fn draw_skips_mutable_mate_probe_and_preserves_preferences_before_analysis_exception() {
        let mut query=cached();let draw=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(draw["outcome"],"draw");assert_eq!(draw["cache"],Value::Null);
        assert_eq!(draw["score"],0);assert_eq!(draw["killers"].as_array().unwrap().len(),2);
        // First follow-up sees old depth; only that actual query raises it.
        assert_eq!(draw["followup"][0]["markedDepth"],1);
        assert_eq!(draw["followup"][1]["markedDepth"],5);
        query["context"]["analysis"]=json!(1);
        let hit=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(hit["outcome"],"cached");assert_eq!(hit["score"],9000);
        assert_eq!(hit["cache"]["markedDepth"],1);
        assert_eq!(hit["followup"][0]["markedDepth"],5);
        assert_eq!(hit["killers"].as_array().unwrap().len(),1);
        assert_eq!(hit["killers"][0]["ply"],64);
        assert_eq!(hit["killers"][0]["moves"][0]["move"],"a2a3q");
        assert_eq!(hit["cache"]["move"],"a2a3");
    }
    #[test]
    fn cache_zero_is_a_return_but_exact_interior_retains_metadata_on_continuation() {
        let mut query=cached();query["context"]["halfmoveClock"]=json!(0);
        query["setup"][0]["targetPly"]=json!(6);query["setup"][0]["score"]=json!(0);
        let inside=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(inside["outcome"],"continue");assert_eq!(inside["score"],Value::Null);
        assert_eq!(inside["cache"]["bound"],"exact");assert_eq!(inside["cache"]["quietMateChecked"],true);
        query["context"]["upperBound"]=json!(0);
        let zero=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(zero["outcome"],"cached");assert_eq!(zero["score"],0);
    }
    #[test]
    fn setup_probe_mutations_precede_draw_and_result_contexts_do_not_alias_repetition_labels() {
        let mut query=cached();let setup_probe=probe(8);
        query["setup"].as_array_mut().unwrap().push(setup_probe);
        // Setup is executed even though this stage itself returns an early draw.
        let out=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(out["outcome"],"draw");assert_eq!(out["followup"][0]["markedDepth"],7);
        // Cache A was stored despite the repetition history using another label.
        query["context"]["analysis"]=json!(1);
        let out=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(out["outcome"],"cached");assert_eq!(out["cache"]["markedDepth"],7);
    }
    #[test]
    fn short_reversal_uses_supplied_arrival_and_rights_before_table_lookup() {
        let mut query=cached();query["context"]["searchPly"]=json!(3);
        query["context"]["preRootLength"]=json!(0);
        query["context"]["prior"]=json!([state("root"),state("one"),state("two")]);
        query["context"]["halfmoveClock"]=json!(3);query["context"]["upperBound"]=json!(0);
        query["context"]["earlierMove"]=json!({"move":"g1f3","kind":"castle"});
        query["context"]["currentMove"]=json!({"move":"f3g1q","kind":"ordinary"});
        let cycle=CachedEntry::parse(&query).unwrap().observe();
        assert_eq!(cycle["isCycle"],true);assert_eq!(cycle["cache"],Value::Null);
        query["context"]["current"]["castling"]=json!("K");
        assert_eq!(CachedEntry::parse(&query).unwrap().observe()["isCycle"],false);
        query["context"]["current"]["castling"]=json!("KQ");
        query["context"]["earlierMove"]=Value::Null;
        assert_eq!(CachedEntry::parse(&query).unwrap().observe()["isCycle"],false);
    }
    #[test]
    fn draw_still_validates_late_table_groups_descriptors_and_frontier_domain() {
        let mut query=cached();query["followup"][1]["targetPly"]=json!(65);
        assert!(CachedEntry::parse(&query).is_err());
        let mut query=cached();let events:Vec<_>=(0..16).map(|index| {
            let mut event=probe(0);event["group"]=json!(format!("group{index}"));event
        }).collect();query["setup"]=json!(events);
        assert!(CachedEntry::parse(&query).is_err()); // G is distinct group17, even on draw.
        query["group"]=json!("group0");query["followup"][0]["group"]=json!("group0");
        query["followup"][1]["group"]=json!("group0");assert!(CachedEntry::parse(&query).is_ok());
        query["context"]["maximumDepth"]=json!(1);assert!(CachedEntry::parse(&query).is_err());
        query["context"]["mode"]=json!("mateInterior");assert!(CachedEntry::parse(&query).is_ok());
        query["context"]["killers"][1]["moves"][1]=json!({"move":"a1a1","kind":"ordinary"});
        assert!(CachedEntry::parse(&query).is_err());
    }
    #[test]
    fn fast_request_precedes_depth_and_check_rejection_and_uses_current_material() {
        let query=fast();let out=fast_result(query.clone());
        assert_eq!(out["fastEvaluationQueried"],true);assert_eq!(out["cutoffScore"],0);
        assert_eq!(out["resultStored"],true);assert_eq!(out["remembered"][0]["score"],0);
        assert_eq!(out["remembered"][0]["bound"],"lower");assert_eq!(out["remembered"][1]["score"],Value::Null);
        let mut depth=query.clone();depth["cutoff"]["targetPly"]=json!(4);
        let out=fast_result(depth);assert_eq!(out["fastEvaluationQueried"],true);
        assert_eq!(out["pressureChecked"],false);assert_eq!(out["materialThreatQueried"],false);
        let mut check=query.clone();check["cutoff"]["currentCheck"]=json!(true);
        assert_eq!(fast_result(check)["fastEvaluationQueried"],true);
        let mut previous_only=query.clone();previous_only["cutoff"]["capture"]["material"]=query["currentMaterial"].clone();
        previous_only["currentMaterial"]=empty_material();
        assert_eq!(fast_result(previous_only)["fastEvaluationQueried"],false);
        for kind in ["enPassant","castling"] { let mut special=query.clone();special["moveKind"]=json!(kind);
            assert_eq!(fast_result(special)["fastEvaluationQueried"],false); }
        let mut occupied=query.clone();occupied["cutoff"]["capture"]["destination"]=json!({"side":"black","piece":"king"});
        assert_eq!(fast_result(occupied)["fastEvaluationQueried"],false);
        let mut promotion=query.clone();promotion["cutoff"]["capture"]["promotion"]=json!("queen");
        assert_eq!(fast_result(promotion.clone())["fastEvaluationQueried"],false);
        promotion["moveKind"]=json!("castling");assert!(FastEntry::parse(&promotion).is_err());
    }
    #[test]
    fn fast_material_normalization_negative_storage_and_pressure_request_order_remain_native() {
        let mut query=fast();query["currentMaterial"]=empty_material();
        query["currentMaterial"]["white"]["knight"]=json!(15);
        query["currentMaterial"]["white"]["rook"]=json!(1); // H17 mod16 =1.
        assert_eq!(fast_result(query.clone())["fastEvaluationQueried"],false);
        query["currentMaterial"]["black"]["bishop"]=json!(2);
        assert_eq!(fast_result(query)["fastEvaluationQueried"],true);
        let mut negative=fast();negative["cutoff"]["upperBound"]=json!(-2);
        negative["cutoff"]["staticScore"]=json!(99);negative["lowerBound"]=json!(-3);
        negative["followups"][0]["lowerBound"]=json!(-3);negative["followups"][0]["upperBound"]=json!(-2);
        let out=fast_result(negative);assert_eq!(out["cutoffScore"],-1);
        assert_eq!(out["resultStored"],true);assert_eq!(out["remembered"][0]["score"],-1);
        let mut pressure=fast();pressure["cutoff"]["pressure"]["neighbors"][0]["current"]["minor"]=json!(2);
        let out=fast_result(pressure);assert_eq!(out["pressureChecked"],true);
        assert_eq!(out["materialThreatQueried"],false);assert_eq!(out["resultStored"],false);
    }
    #[test]
    fn unused_fast_profiles_and_late_batch_queries_are_eagerly_validated() {
        let mut invalid=fast();invalid["moveKind"]=json!("enPassant");
        invalid["cutoff"]["pressure"]["neighbors"][7]["included"]=json!(false);
        invalid["cutoff"]["pressure"]["neighbors"][7]["current"]["queen"]=json!(99);
        assert!(dispatch("search.fastEntry",&json!({"queries":[fast(),invalid]})).is_err());
    }
    #[test]
    fn evaluation_bounds_keep_absolute_threshold_crossed_priority_and_static_independence() {
        let mut query=json!({"searchPly":4,"targetPly":9,"lowerBound":-1,"upperBound":0,
            "staticScore":-10000,"evaluationLower":0,"evaluationUpper":-1});
        assert_eq!(EvaluationBounds::parse(&query).unwrap().observe()["outcome"],"continue");
        query["searchPly"]=json!(5);
        for score in [-10000,0,10000] { query["staticScore"]=json!(score);
            assert_eq!(EvaluationBounds::parse(&query).unwrap().observe(),json!({"outcome":"lower","score":0})); }
        query["staticScore"]=json!(10001);
        assert!(dispatch("search.evaluationBounds",&json!({"queries":[{
            "searchPly":1,"targetPly":2,"lowerBound":-1,"upperBound":1,
            "staticScore":0,"evaluationLower":0,"evaluationUpper":0},query]})).is_err());
    }
}
