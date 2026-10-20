//! Exact controlled schemas and label projection over the shared native owner.
use super::{array,integer,object,text,Result};
use rook2::root_schedule::{self as native,Policy,Row,SuppliedCandidate,SuppliedReply};
use serde_json::{json,Value};
use std::collections::HashSet;
const SAFE:u64=9_007_199_254_740_991;
fn count(value:&Value,min:u64,max:u64)->Result<u64> {
    let number=value.as_f64().ok_or("expected exact nonnegative integer count")?;
    if !number.is_finite()||number.fract()!=0.0||number<min as f64||number>max as f64 {
        return Err("count outside exact-interchange integer domain".into());
    }
    Ok(number as u64)
}
fn sum(a:u64,b:u64)->Result<u64> {
    a.checked_add(b).filter(|&n|n<=SAFE).ok_or_else(||"conservative work sum exceeds exact interchange".into())
}
fn label(value:&Value,seen:&mut HashSet<String>)->Result<String> {
    let s=text(value)?;let bytes=s.as_bytes();
    if !(1..=32).contains(&bytes.len())||!bytes[0].is_ascii_alphabetic()
        ||!bytes[1..].iter().all(|b|b.is_ascii_alphanumeric()||matches!(*b,b'_'|b'-'))
        ||!seen.insert(s.to_owned()) {
        return Err("invalid or duplicate root label".into());
    }
    Ok(s.to_owned())
}
struct Schedule {
    search:u64,
    labels:Vec<String>,
    rows:Vec<Row>,
}
impl Schedule {
    fn parse(value:&Value)->Result<Self> {
        object(value,&["searchId","candidates"])?;
        let search=count(&value["searchId"],0,SAFE)?;
        let mut labels=Vec::new();let mut rows=Vec::new();let mut seen=HashSet::new();
        for (id,candidate) in array(&value["candidates"],1,64)?.iter().enumerate() {
            object(candidate,&["label","work"])?;
            labels.push(label(&candidate["label"],&mut seen)?);
            rows.push(Row{id:id as u16,score:0,work:count(&candidate["work"],0,SAFE)?});
        }
        Ok(Self{search,labels,rows})
    }
    fn observe(self)->Value { schedule(self.search,self.rows,&self.labels) }
}
fn schedule(search:u64,mut rows:Vec<Row>,labels:&[String])->Value {
    let policy=native::policy(search);native::order_tail(&mut rows,policy);
    json!({"restricted":policy==Policy::Restricted,"candidates":rows.iter().map(|r|
        json!({"label":labels[usize::from(r.id)],"work":r.work})).collect::<Vec<_>>()})
}
struct Sequence {
    search:u64,
    previous:i32,
    restricted:bool,
    labels:Vec<String>,
    supplied:Vec<SuppliedCandidate>,
}
impl Sequence {
    fn parse(value:&Value,restricted:bool)->Result<Self> {
        if restricted { object(value,&["initialSearchId","previousBest","candidates"])?; }
        else { object(value,&["initialSearchId","candidates"])?; }
        let search=count(&value["initialSearchId"],if restricted{25000}else{0},if restricted{SAFE}else{24999})?;
        let previous=if restricted{integer(&value["previousBest"],-10000,10000)?}else{0};
        let mut conservative_total=search;
        let mut labels=Vec::new();let mut supplied=Vec::new();let mut seen=HashSet::new();
        for c in array(&value["candidates"],1,32)? {
            if restricted { object(c,&["label","firstScore","retryScore","priorWork","firstWork","retryWork"])?; }
            else { object(c,&["label","score","priorWork","searchWork"])?; }
            labels.push(label(&c["label"],&mut seen)?);
            let prior_work=count(&c["priorWork"],0,SAFE)?;
            let first=SuppliedReply{score:integer(&c[if restricted{"firstScore"}else{"score"}],-10000,10000)?,
                work:count(&c[if restricted{"firstWork"}else{"searchWork"}],0,SAFE)?};
            // Parse every unused reply and conservative sum before any driver call.
            let retry=if restricted{Some(SuppliedReply{score:integer(&c["retryScore"],-10000,10000)?,
                work:count(&c["retryWork"],0,SAFE)?})}else{None};
            let possible_work=sum(first.work,retry.map_or(0,|r|r.work))?;
            sum(prior_work,possible_work)?;
            conservative_total=sum(conservative_total,possible_work)?;
            supplied.push(SuppliedCandidate{prior_work,first,retry});
        }
        Ok(Self{search,previous,restricted,labels,supplied})
    }
    fn observe(self)->Value {
        let out=native::supplied_iteration(self.search,self.previous,&self.supplied);
        let steps=out.steps.iter().map(|s|{
            let c=s.completed;
            let ranked=s.ranked.iter().map(|r|json!({"label":self.labels[usize::from(r.id)],
                "score":r.score,"work":r.work})).collect::<Vec<_>>();
            if self.restricted {
                json!({"label":self.labels[usize::from(c.id)],"passes":s.passes.iter().map(|p|
                    json!({"lowerBound":p.attempt.window[0],"upperBound":p.attempt.window[1],
                        "score":p.returned_score,"searchId":p.search_count})).collect::<Vec<_>>(),
                    "returnedScore":c.returned_score,"rankingScore":c.score,"insertionRank":s.insertion_rank(),
                    "rankedCandidates":ranked})
            } else {
                let pass=&s.passes[0];
                json!({"label":self.labels[usize::from(c.id)],"lowerBound":c.window[0],"upperBound":c.window[1],
                    "returnedScore":c.returned_score,"insertionRank":s.insertion_rank(),
                    "searchId":pass.search_count,"rankedCandidates":ranked})
            }
        }).collect::<Vec<_>>();
        json!({"steps":steps,"nextIteration":schedule(out.search_count,out.ranked,&self.labels)})
    }
}
pub(super) fn dispatch(operation:&str,input:&Value)->Result<Value> {
    object(input,&["queries"])?;
    match operation {
        "search.rootWorkSchedule"=>{
            let queries=array(&input["queries"],1,128)?.iter().map(Schedule::parse).collect::<Result<Vec<_>>>()?;
            Ok(json!({"results":queries.into_iter().map(Schedule::observe).collect::<Vec<_>>()}))
        },
        "search.unrestrictedRootSequence"|"search.restrictedRootSequence"=>{
            let restricted=operation=="search.restrictedRootSequence";
            let queries=array(&input["queries"],1,if restricted{8}else{16})?.iter()
                .map(|q|Sequence::parse(q,restricted)).collect::<Result<Vec<_>>>()?;
            Ok(json!({"results":queries.into_iter().map(Sequence::observe).collect::<Vec<_>>()}))
        },
        _=>Err("unknown controlled root operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn work_query()->Value { json!({"searchId":25000,"candidates":[
        {"label":"A","work":0},{"label":"B","work":3},
        {"label":"C","work":9},{"label":"D","work":9}]}) }
    fn unrestricted()->Value { json!({"initialSearchId":24999,"candidates":[
        {"label":"A","score":10,"priorWork":1,"searchWork":2},
        {"label":"B","score":10,"priorWork":7,"searchWork":0},
        {"label":"C","score":5,"priorWork":50,"searchWork":0}]}) }
    fn restricted()->Value { json!({"initialSearchId":25000,"previousBest":10,"candidates":[
        {"label":"A","firstScore":10,"retryScore":10000,"priorWork":100,"firstWork":3,"retryWork":99},
        {"label":"B","firstScore":-5,"retryScore":10000,"priorWork":200,"firstWork":4,"retryWork":88},
        {"label":"C","firstScore":13,"retryScore":12,"priorWork":300,"firstWork":5,"retryWork":7}]}) }
    #[test]
    fn exact_label_domains_and_candidate_limits_are_route_specific() {
        for invalid in ["","1A","_A","é","A.","abcdefghijklmnopqrstuvwxyzABCDEFG"] {
            let mut q=work_query();q["candidates"][0]["label"]=json!(invalid);
            assert!(Schedule::parse(&q).is_err());
        }
        let mut q=work_query();q["candidates"][1]["label"]=json!("A");assert!(Schedule::parse(&q).is_err());
        for label in ["A","z_9-","abcdefghijklmnopqrstuvwxyzABCDEF"] {
            let mut q=work_query();q["candidates"][0]["label"]=json!(label);assert!(Schedule::parse(&q).is_ok());
        }
        let rows=(0..64).map(|id|json!({"label":format!("C{id}"),"work":0})).collect::<Vec<_>>();
        assert!(Schedule::parse(&json!({"searchId":0,"candidates":rows})).is_ok());
        let rows=(0..33).map(|id|json!({"label":format!("C{id}"),"score":0,"priorWork":0,"searchWork":0})).collect::<Vec<_>>();
        assert!(Sequence::parse(&json!({"initialSearchId":0,"candidates":rows}),false).is_err());
    }
    #[test]
    fn exact_counts_and_conservative_unused_retry_sums_reject_before_execution() {
        for n in [0,2147483648,SAFE] { assert_eq!(count(&json!(n),0,SAFE).unwrap(),n); }
        for v in [json!(-1),json!(SAFE+1),json!(0.5),json!(false),json!("1")] {
            assert!(count(&v,0,SAFE).is_err());
        }
        let mut q=restricted();q["candidates"][0]["firstScore"]=json!(10000);
        q["candidates"][0]["retryScore"]=json!("unused but invalid");
        assert!(Sequence::parse(&q,true).is_err());
        q=restricted();q["candidates"][0]["priorWork"]=json!(SAFE);
        q["candidates"][0]["firstWork"]=json!(0);q["candidates"][0]["retryWork"]=json!(1);
        assert!(Sequence::parse(&q,true).is_err());
        q=json!({"initialSearchId":25000,"previousBest":0,"candidates":[
            {"label":"A","firstScore":10000,"retryScore":0,"priorWork":0,"firstWork":0,"retryWork":SAFE}]});
        assert!(Sequence::parse(&q,true).is_err());
        q=unrestricted();q["candidates"][0]["priorWork"]=json!(SAFE);assert!(Sequence::parse(&q,false).is_err());
    }
    #[test]
    fn actual_work_schedule_is_stable_idempotent_and_keeps_first_pinned() {
        let input=json!({"queries":[work_query()]});
        let out=dispatch("search.rootWorkSchedule",&input).unwrap();
        let result=&out["results"][0];
        assert_eq!(result["candidates"].as_array().unwrap().iter().map(|r|r["label"].as_str().unwrap()).collect::<Vec<_>>(),["A","C","D","B"]);
        let again=json!({"queries":[{"searchId":25000,"candidates":result["candidates"]}]});
        assert_eq!(dispatch("search.rootWorkSchedule",&again).unwrap(),out);
        let mut changed=work_query();changed["candidates"][0]["work"]=json!(SAFE);
        let changed=dispatch("search.rootWorkSchedule",&json!({"queries":[changed]})).unwrap();
        assert_eq!(changed["results"][0]["candidates"][0]["label"],json!("A"));
        assert_eq!(&changed["results"][0]["candidates"].as_array().unwrap()[1..],
            &result["candidates"].as_array().unwrap()[1..]);
    }
    #[test]
    fn unrestricted_crossing_preserves_prefixes_and_admits_equal_sentinel_windows() {
        let out=dispatch("search.unrestrictedRootSequence",&json!({"queries":[unrestricted()]})).unwrap();
        let r=&out["results"][0];let steps=r["steps"].as_array().unwrap();
        assert_eq!(steps.iter().map(|s|s["label"].as_str().unwrap()).collect::<Vec<_>>(),["A","B","C"]);
        assert_eq!(steps[2]["lowerBound"],json!(10));assert_eq!(steps[2]["searchId"],json!(25001));
        assert_eq!(steps[1]["insertionRank"],json!(1));
        assert_eq!(r["nextIteration"]["candidates"].as_array().unwrap().iter().map(|s|s["label"].as_str().unwrap()).collect::<Vec<_>>(),["A","C","B"]);
        let mut q=unrestricted();q["candidates"][0]["score"]=json!(10000);q["candidates"][1]["score"]=json!(10000);
        let out=dispatch("search.unrestrictedRootSequence",&json!({"queries":[q]})).unwrap();
        assert_eq!(out["results"][0]["steps"][2]["lowerBound"],json!(10000));
        assert_eq!(out["results"][0]["steps"][2]["upperBound"],json!(10000));
    }
    #[test]
    fn restricted_reply_slots_and_unused_data_are_independent_of_exploration_order() {
        let q=restricted();let expected=dispatch("search.restrictedRootSequence",&json!({"queries":[q.clone()]})).unwrap();
        let steps=expected["results"][0]["steps"].as_array().unwrap();
        assert_eq!(steps.iter().map(|s|s["label"].as_str().unwrap()).collect::<Vec<_>>(),["A","C","B"]);
        assert_eq!(steps[1]["passes"].as_array().unwrap().len(),2);
        assert_eq!(steps[1]["passes"][0]["score"],json!(13));
        assert_eq!(steps[1]["passes"][1]["lowerBound"],json!(12));
        assert_eq!(steps[1]["returnedScore"],json!(12));assert_eq!(steps[1]["rankingScore"],json!(10));
        assert_eq!(steps[1]["insertionRank"],json!(1));
        let mut changed=q;for index in [0,1] {
            changed["candidates"][index]["retryScore"]=json!(-10000);
            changed["candidates"][index]["retryWork"]=json!(0);
        }
        assert_eq!(dispatch("search.restrictedRootSequence",&json!({"queries":[changed]})).unwrap(),expected);
    }
    #[test]
    fn full_queries_are_validated_eagerly_and_batch_limits_do_not_leak_between_routes() {
        for (op,max,q) in [("search.rootWorkSchedule",128,work_query()),
            ("search.unrestrictedRootSequence",16,unrestricted()),("search.restrictedRootSequence",8,restricted())] {
            assert!(dispatch(op,&json!({"queries":vec![q.clone();max]})).is_ok());
            assert!(dispatch(op,&json!({"queries":vec![q.clone();max+1]})).is_err());
            let mut malformed=q.clone();malformed["extra"]=Value::Null;
            assert!(dispatch(op,&json!({"queries":[q,malformed]})).is_err());
        }
        let a=work_query();let mut b=a.clone();b["searchId"]=json!(24999);
        let out=dispatch("search.rootWorkSchedule",&json!({"queries":[a.clone(),b.clone(),a]})).unwrap();
        let reversed=dispatch("search.rootWorkSchedule",&json!({"queries":[b,work_query()]})).unwrap();
        assert_eq!(out["results"][0],out["results"][2]);
        assert_eq!(out["results"][1],reversed["results"][0]);assert_eq!(out["results"][0],reversed["results"][1]);
    }
}
