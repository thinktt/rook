//! External valid-data checker; never linked into the engine.
#![allow(dead_code)]
use std::{collections::BTreeMap,ops::Index};
use rook2::{timing::{Adaptive,Stage,Terminal},work_clock::Ledger,quiescence::Work,position::Position};
#[derive(Debug)]
enum J {Null,Bool(bool),N(String),S(String),A(Vec<J>),O(BTreeMap<String,J>)}
impl J {
    fn a(&self)->&[J] {if let Self::A(v)=self {v}else{panic!("not array: {self:?}")}}
    fn s(&self)->&str {if let Self::S(v)=self {v}else{panic!("not string: {self:?}")}}
    fn n(&self)->i32 {if let Self::N(v)=self {v.parse().unwrap()}else{panic!("not integer: {self:?}")}}
    fn u(&self)->u32 {if let Self::N(v)=self {v.parse().unwrap()}else{panic!("not uint: {self:?}")}}
    fn f(&self)->f64 {if let Self::N(v)=self {v.parse().unwrap()}else{panic!("not number")}}
    fn b(&self)->bool {if let Self::Bool(v)=self {*v}else{panic!("not bool: {self:?}")}}
    fn get(&self,k:&str)->Option<&J> {if let Self::O(v)=self {v.get(k)}else{None}}
    fn null(&self)->bool {matches!(self,Self::Null)}
}
fn state(a:&Adaptive,e:&J,stop:bool){
    assert_eq!(a.limits,e["limits"].a().iter().map(J::f).collect::<Vec<_>>().as_slice());
    assert_eq!(a.changes,e["changes"].a().iter().map(J::u).collect::<Vec<_>>().as_slice());
    assert_eq!(a.clock_reads,e["clockReads"].u() as u64);assert_eq!(stop,e["stop"].b());
}

pub fn run(path:&str){
    let bytes=std::fs::read(path).unwrap();let mut parser=Parser{s:&bytes,i:0};let case=parser.value();parser.ws();assert_eq!(parser.i,bytes.len());
    let input=&case["input"];let expected=&case["expected"];
    match case["operation"].s(){
        "clock.workSequence"=>{
            let mut ledger=Ledger::default();let mut work=Work::default();let mut observed=Vec::new();
            for event in input["events"].a(){
                if let Some(v)=event.get("work"){work=Work{charged_search_units:v["searchUnits"].s().parse().unwrap(),charged_relation_queries:v["relationQueries"].s().parse().unwrap()};}
                if event.get("observe").is_some_and(J::b){observed.push(ledger.observe(work) as i32);}
                if event.get("reset").is_some_and(J::b){ledger.reset();work=Work::default();assert_eq!(ledger.fine_post(),0);}
            }
            assert_eq!(observed,expected["observations"].a().iter().map(J::n).collect::<Vec<_>>());
        },
        "time.adaptiveSequence"=>{
            for(q,e)in input["queries"].a().iter().zip(expected["sequences"].a()){
                let mut a=Adaptive::new(q["average"].u(),q["maximum"].u(),q["inCheck"].b(),q["start"].u());state(&a,&e["initial"],false);
                let mut count=0;for event in q["events"].a(){
                    let stage=match event["stage"].s(){"best-change"=>Stage::BestChange,"score-drop"=>Stage::ScoreDrop,"root-check"=>Stage::Root,"iteration-check"=>Stage::Iteration,"easy-iteration-check"=>Stage::EasyIteration,"poll-check"=>Stage::Poll,_=>panic!("stage")};
                    let reads=a.clock_reads;let mut called=0;
                    let stop=a.apply(stage,event["depth"].n(),event["previousScore"].n(),event["bestScore"].n(),event["secondScore"].n(),||{called+=1;event["clock"].u()});
                    assert_eq!(a.clock_reads-reads,called);state(&a,&e["afterEach"].a()[count],stop);count+=1;if stop{break;}
                }
                assert_eq!(count,e["afterEach"].a().len());
            }
        },
        "search.iterationTerminalStop"=>{
            for(q,e)in input["queries"].a().iter().zip(expected["results"].a()){
                let root=Position::from_fen(&format!("{} w - - 0 1",q["rootPlacement"].s())).unwrap();
                let t=Terminal{depth:q["iterationDepth"].n(),selectivity:q["selectivity"].n(),root_endgame:root.phase().endgame,maximum_depth:q["maximumDepth"].u() as usize,analysis:q["analysisMode"].n(),average_cs:q["averageCentiseconds"].u(),best:q["bestScore"].n(),second:q["secondBestScore"].n(),previous:q["previousBestScore"].n(),start:q["startClock"].u(),clock:q["currentClock"].u(),iteration_limit:q["iterationLimitSeconds"].f()};
                assert_eq!(t.reason(),if e["reason"].null(){None}else{Some(e["reason"].s())});assert_eq!(t.reason().is_some(),e["stop"].b());assert_eq!((t.elapsed_cs(),t.mate_margin(),t.root_endgame),(e["elapsedCentiseconds"].n(),e["mateMargin"].n(),e["rootEndgameWeight"].u() as u16));
            }
        },
        _=>panic!("operation"),
    }
}
impl Index<&str> for J {type Output=J;fn index(&self,k:&str)->&J {self.get(k).unwrap_or_else(||panic!("missing {k}"))}}
struct Parser<'a>{s:&'a[u8],i:usize}
impl Parser<'_> {
    fn ws(&mut self){while self.i<self.s.len()&&self.s[self.i].is_ascii_whitespace(){self.i+=1;}}
    fn token(&mut self,c:u8){self.ws();assert_eq!(self.s[self.i],c);self.i+=1;}
    fn string(&mut self)->String {
        self.token(b'"');let mut out=Vec::new();loop {
            let b=self.s[self.i];self.i+=1;
            if b==b'"'{return String::from_utf8(out).unwrap();}
            if b!=b'\\'{out.push(b);continue;}
            let escaped=self.s[self.i];self.i+=1;
            if escaped==b'u'{
                let mut code=u32::from_str_radix(std::str::from_utf8(&self.s[self.i..self.i+4]).unwrap(),16).unwrap();self.i+=4;
                if (0xd800..=0xdbff).contains(&code){
                    assert_eq!(&self.s[self.i..self.i+2],b"\\u");self.i+=2;
                    let low=u32::from_str_radix(std::str::from_utf8(&self.s[self.i..self.i+4]).unwrap(),16).unwrap();self.i+=4;
                    assert!((0xdc00..=0xdfff).contains(&low));code=0x10000+((code-0xd800)<<10)+(low-0xdc00);
                }
                let mut bytes=[0;4];out.extend_from_slice(char::from_u32(code).unwrap().encode_utf8(&mut bytes).as_bytes());
            }else{out.push(match escaped {b'"'=>b'"',b'\\'=>b'\\',b'/'=>b'/',b'n'=>b'\n',b'r'=>b'\r',b't'=>b'\t',b'b'=>8,b'f'=>12,_=>panic!("escape")});}
        }
    }
    fn value(&mut self)->J {
        self.ws();match self.s[self.i] {
            b'"'=>J::S(self.string()),
            b'['=>{self.i+=1;self.ws();let mut v=Vec::new();if self.s[self.i]!=b']'{loop {v.push(self.value());self.ws();if self.s[self.i]==b']'{break;}self.token(b',');}}self.i+=1;J::A(v)},
            b'{'=>{self.i+=1;self.ws();let mut v=BTreeMap::new();if self.s[self.i]!=b'}'{loop{let k=self.string();self.token(b':');assert!(v.insert(k,self.value()).is_none());self.ws();if self.s[self.i]==b'}'{break;}self.token(b',');}}self.i+=1;J::O(v)},
            b't'=>{assert_eq!(&self.s[self.i..self.i+4],b"true");self.i+=4;J::Bool(true)},
            b'f'=>{assert_eq!(&self.s[self.i..self.i+5],b"false");self.i+=5;J::Bool(false)},
            b'n'=>{assert_eq!(&self.s[self.i..self.i+4],b"null");self.i+=4;J::Null},
            _=>{let start=self.i;if self.s[self.i]==b'-'{self.i+=1;}while self.i<self.s.len()&&matches!(self.s[self.i], b'0'..=b'9'|b'.'|b'e'|b'E'|b'+'|b'-'){self.i+=1;}
                J::N(std::str::from_utf8(&self.s[start..self.i]).unwrap().to_owned())}
        }
    }
}
