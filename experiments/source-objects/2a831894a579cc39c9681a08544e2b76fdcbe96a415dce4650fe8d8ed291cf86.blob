//! Cold generation compositions; native owners produce and order every move.
use super::{admission, array, candidate_order, integer, moves, object, positions,
    quiescence_evaluation, text, Result};
use rook2::{movegen::{self, CheckClassification, MoveList}, position::Position,
    tactical, types::Move};
use serde_json::{json, Value};

const PRODUCED: &[&str] = &["fen", "moves", "ply", "values", "squareAdjustments",
    "history", "hashMove", "killers"];
const QUIESCENCE: &[&str] = &["fen", "percentages", "averageDepth", "cfd", "sop",
    "history", "move", "alpha", "beta", "orderingHistory"];

struct Produced {
    position: Position,
    context: candidate_order::Context,
    quiescence: bool,
}
impl Produced {
    fn parse(input: &Value) -> Result<Self> {
        let supplied = input.as_object().ok_or("expected object")?;
        let quiescence = if supplied.contains_key("orderingMode") {
            let mut keys=PRODUCED.to_vec();keys.push("orderingMode");object(input,&keys)?;
            if text(&input["orderingMode"])? != "quiescence" {
                return Err("only explicit quiescence ordering mode is admitted".into());
            }
            true
        } else { object(input,PRODUCED)?;false };
        let ply=integer(&input["ply"],1,62)? as usize;
        let mut position=admission::consumer_position(text(&input["fen"])?)?;
        let spellings=array(&input["moves"],0,256)?.iter().map(|value| {
            let spelling=text(value)?;positions::coordinate(spelling)?;Ok(spelling)
        }).collect::<Result<Vec<_>>>()?;
        // Cold legality replay completes before ranking or any output mutation;
        // native transitions preserve piece chronology instead of rebuilding it.
        for spelling in &spellings {
            position=positions::advance_with_move(&position,spelling)?.0;
        }
        let context=candidate_order::Context::parse(input,&position,ply)?;
        if quiescence && (!spellings.is_empty() || !movegen::in_check(&position,position.side)
            || context.hint.is_some() || context.learning.killers[ply] != [Move::NONE;2]
            || (ply>=3 && context.learning.killers[ply-2] != [Move::NONE;2])) {
            return Err("quiescence ordering needs setup-only check and no hash/killer preferences".into());
        }
        Ok(Self { position,context,quiescence })
    }

    fn observe(self) -> Result<Value> {
        let checked=movegen::check_classification(&self.position);
        let mut list=MoveList::new();movegen::generate_legal(&self.position,&mut list);
        if list.len>230 {return Err("complete legal candidate inventory exceeds diagnostic230 limit".into());}
        let generated=descriptors(&list);
        let terminal=if list.len!=0 {"none"} else if checked==CheckClassification::None {"stalemate"} else {"checkmate"};
        if self.quiescence {
            tactical::order(&self.position,&self.context.root,&self.context.learning.history,&mut list);
        } else {self.context.order(&self.position,&mut list);}
        Ok(json!({"position":{"placement":self.position.placement(),
            "sideToMove":if self.position.side==rook2::types::Color::White {"white"} else {"black"},
            "castling":positions::rights(&self.position),"enPassant":positions::ep(&self.position),
            "halfmoveClock":self.position.halfmove},
            "check":match checked {CheckClassification::None=>"none",CheckClassification::Single=>"single",CheckClassification::Double=>"double"},
            "terminal":terminal,"generatedCandidates":generated,"orderedCandidates":descriptors(&list),
            "chargedRelationQueries":0}))
    }
}

fn descriptors(list: &MoveList) -> Value {
    json!(list.as_slice().iter().map(|&movement|moves::descriptor(movement)).collect::<Vec<_>>())
}

fn quiescence(input: &Value) -> Result<Value> {
    object(input,QUIESCENCE)?;
    // Supplied ordering keys validate before path replay, evaluator or cache
    // creation, including requests whose eventual disposition returns early.
    let history=candidate_order::ordering_history(&input["orderingHistory"])?;
    let request=quiescence_evaluation::Request::parse_candidates(input)?;
    request.observe_with(true,|evaluator,node,returned| {
        if returned.is_some() {return Ok(Some(json!({"reached":false})));}
        let mut list=MoveList::new();tactical::generate(&node.position,&mut list);
        if list.len>230 {return Err("complete tactical candidate inventory exceeds diagnostic230 limit".into());}
        let generated=descriptors(&list);
        tactical::order(&node.position,&evaluator.root,&history,&mut list);
        Ok(Some(json!({"reached":true,"generatedCandidates":generated,
            "orderedCandidates":descriptors(&list),"additionalChargedRelationQueries":0,
            "additionalChargedSearchUnits":0})))
    })
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "search.produceAndOrderCandidates"=>Produced::parse(input)?.observe(),
        "search.quiescenceCandidates"=>quiescence(input),
        _=>Err("unknown generation operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::scores;

    const START: &str="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    fn produced(fen:&str)->Value {
        let values=json!({"pawn":100,"knight":300,"bishop":300,"rook":500,"queen":890});
        json!({"fen":fen,"moves":[],"ply":3,"values":{"white":values.clone(),"black":values},
            "squareAdjustments":[],"history":[],"hashMove":null,
            "killers":{"current":[null,null],"twoPliesEarlier":[null,null]}})
    }
    fn qrequest(fen:&str,movement:&str)->Value {
        let percentages:serde_json::Map<String,Value>=scores::NAMES.iter()
            .map(|name|(name.to_string(),json!(100))).collect();
        json!({"fen":fen,"history":[],"move":movement,"alpha":-10000,"beta":10000,
            "percentages":{"own":percentages.clone(),"opponent":percentages},
            "averageDepth":0,"cfd":0,"sop":100,"orderingHistory":[]})
    }
    fn names(values:&Value)->Vec<String> {
        values.as_array().unwrap().iter().map(|value|value["move"].as_str().unwrap().to_owned()).collect()
    }
    fn history(piece:&str,square:&str,value:u32)->Value {
        json!({"side":"white","piece":piece,"square":square,"value":value})
    }

    #[test]
    fn produced_schema_and_local_domain_guards_are_exact() {
        let mut input=produced(START);input["orderingMode"]=json!("ordinary");
        assert!(Produced::parse(&input).is_err());
        input["orderingMode"]=json!("quiescence");assert!(Produced::parse(&input).is_err());
        let checked="K6r/p1P5/1p6/8/3k4/8/8/8 w - - 1 1";
        let mut input=produced(checked);input["orderingMode"]=json!("quiescence");
        input["hashMove"]=json!({"move":"a1b1","kind":"ordinary"});assert!(Produced::parse(&input).is_err());
        input["hashMove"]=Value::Null;input["history"]=json!([history("king","b7",2),history("king","b7",3)]);
        assert!(Produced::parse(&input).is_err());
        input["history"]=json!([]);input["killers"]["twoPliesEarlier"][1]=json!({"move":"a1b1","kind":"ordinary"});
        assert!(Produced::parse(&input).is_err());input["ply"]=json!(2);assert!(Produced::parse(&input).is_err());
        for fen in ["7k/8/8/8/8/8/8/K6R w - - 0 1", "7k/8/8/3nP3/8/8/8/K7 w - d6 0 1"] {
            assert!(positions::sequence_position(fen,true).is_ok());
            assert!(Produced::parse(&produced(fen)).is_err());
        }
        let mut input=produced(START);input["extra"]=json!(false);assert!(Produced::parse(&input).is_err());
    }

    #[test]
    fn complete_production_retains_checked_observable_order_and_terminal_labels() {
        // Capped king-first witnesses for this position differ from its full
        // inventory. This transport must retain the complete knight-first list.
        let output=Produced::parse(&produced("5n1k/8/8/5b2/8/8/8/K6R b - - 0 1")).unwrap().observe().unwrap();
        assert_eq!(output["check"],"single");assert_eq!(output["terminal"],"none");
        assert_eq!(output["generatedCandidates"].as_array().unwrap().len(),5);
        assert_eq!(output["generatedCandidates"][0]["move"],"f8h7");
        for (fen,check,terminal) in [
            ("7k/6Q1/5K2/8/8/8/8/8 b - - 0 1","single","checkmate"),
            ("8/8/8/8/8/2k5/2q5/K7 w - - 0 1","none","stalemate"),
        ] {
            let output=Produced::parse(&produced(fen)).unwrap().observe().unwrap();
            assert_eq!(output["check"],check);assert_eq!(output["terminal"],terminal);
            assert_eq!(output["generatedCandidates"],json!([]));assert_eq!(output["orderedCandidates"],json!([]));
        }
    }

    #[test]
    fn explicit_q_evasions_keep_quiet_promotions_and_original_source_history_keys() {
        let mut input=produced("K6r/p1P5/1p6/8/3k4/8/8/8 w - - 1 1");
        input["orderingMode"]=json!("quiescence");
        input["squareAdjustments"]=json!([{"side":"black","piece":"pawn","square":"a7","value":-2}]);
        let expected=["c7c8q","c7c8r","c7c8b","c7c8n","a8a7","a8b7"];
        for supplied in [json!([]),json!([history("pawn","c8",2)])] {
            input["history"]=supplied;
            let output=Produced::parse(&input).unwrap().observe().unwrap();
            assert_eq!(names(&output["orderedCandidates"]),expected);
            assert_eq!(names(&output["generatedCandidates"]),["c7c8q","c7c8r","c7c8b","c7c8n","a8b7","a8a7"]);
            assert_eq!(output["chargedRelationQueries"],0);
        }
        input["history"]=json!([history("king","b7",u32::MAX)]);
        let output=Produced::parse(&input).unwrap().observe().unwrap();
        assert_eq!(output["orderedCandidates"][0]["move"],"a8b7");
    }

    #[test]
    fn deferred_zero_one_keep_generated_order_then_native_preferred_prefix_is_added() {
        let mut input=produced("7k/8/8/8/8/8/PPP5/K7 w - - 0 1");
        input["history"]=json!([history("pawn","a3",1),history("pawn","c4",0)]);
        let low=Produced::parse(&input).unwrap().observe().unwrap();
        assert_eq!(low["orderedCandidates"],low["generatedCandidates"]);
        input["history"]=json!([history("pawn","a3",1),history("pawn","c4",2)]);
        let preferred=Produced::parse(&input).unwrap().observe().unwrap();
        let mut expected=names(&preferred["generatedCandidates"]);
        let index=expected.iter().position(|name|name=="c2c4").unwrap();let movement=expected.remove(index);
        expected.insert(0,movement);
        assert_eq!(names(&preferred["orderedCandidates"]),expected);
        assert_eq!(preferred["generatedCandidates"],low["generatedCandidates"]);
    }

    #[test]
    fn q_ordering_history_is_eager_and_static_returns_have_only_reached_false() {
        let mut input=qrequest("7k/8/8/8/8/8/8/K7 w - - 0 1","a1b1");
        input["alpha"]=json!(-10000);input["beta"]=json!(-9999);
        let output=quiescence(&input).unwrap();assert_eq!(output["tacticalGeneration"],json!({"reached":false}));
        for entries in [json!([history("pawn","a3",1),history("pawn","a3",2)]),
            json!([{"side":"white","piece":"king","square":"a1","value":4294967296u64}]),
            json!([{"side":"white","piece":"king","square":"a1","value":0,"extra":true}])] {
            input["orderingHistory"]=entries;assert!(quiescence(&input).is_err());
        }
    }

    #[test]
    fn q_keeps_exact_evaluation_results_and_pseudo_legal_king_exposing_candidates() {
        let mut input=qrequest(START,"g1f3");
        input["history"]=json!([{"move":"e2e4","kind":"full"},{"move":"e7e5","kind":"fast"}]);
        let mut evaluation=input.clone();evaluation.as_object_mut().unwrap().remove("orderingHistory");
        let expected=quiescence_evaluation::dispatch("evaluation.quiescenceDisposition",&evaluation).unwrap();
        let output=quiescence(&input).unwrap();assert_eq!(output["results"],expected["results"]);
        let input=qrequest("k3r3/8/8/8/8/8/4R2p/4K3 b - - 0 1","a8b8");
        let output=quiescence(&input).unwrap();assert_eq!(output["tacticalGeneration"]["reached"],true);
        let generated=&output["tacticalGeneration"]["generatedCandidates"];
        let capture=generated.as_array().unwrap().iter().find(|value|value["move"]=="e2h2").unwrap();
        let position=positions::sequence_position(input["fen"].as_str().unwrap(),true).unwrap();
        let current=positions::advance_with_move(&position,"a8b8").unwrap().0;
        let child=current.played_unchecked(moves::movement(capture).unwrap().unwrap());
        assert!(movegen::in_check(&child,current.side));
        assert_eq!(output["tacticalGeneration"]["additionalChargedRelationQueries"],0);
        assert_eq!(output["tacticalGeneration"]["additionalChargedSearchUnits"],0);
    }
}
