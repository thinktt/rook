//! External fixture consumer. This file is never linked into an engine binary.
#![allow(dead_code)]
use std::{collections::BTreeMap, ops::Index};
use rook2::{endgame as eg, evaluator::{Components,Evaluator,Node,Parameters}, influence::Influence,
    movegen::in_check,pawn_progress as pp,pawn_structure,pawn_terms,positional_terms as pt,
    position::{Phase,Position},types::{Color,Square}};

#[derive(Debug)]
enum J {Null,Bool(bool),N(i64),S(String),A(Vec<J>),O(BTreeMap<String,J>)}
impl J {
    fn a(&self)->&[J] {if let Self::A(v)=self {v}else{panic!("not array: {self:?}")}}
    fn s(&self)->&str {if let Self::S(v)=self {v}else{panic!("not string: {self:?}")}}
    fn n(&self)->i32 {if let Self::N(v)=self {(*v).try_into().unwrap()}else{panic!("not integer: {self:?}")}}
    fn u(&self)->u32 {if let Self::N(v)=self {(*v).try_into().unwrap()}else{panic!("not uint: {self:?}")}}
    fn b(&self)->bool {if let Self::Bool(v)=self {*v}else{panic!("not bool: {self:?}")}}
    fn get(&self,k:&str)->Option<&J> {if let Self::O(v)=self {v.get(k)}else{None}}
    fn null(&self)->bool {matches!(self,Self::Null)}
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
            _=>{let start=self.i;if self.s[self.i]==b'-'{self.i+=1;}while self.i<self.s.len()&&self.s[self.i].is_ascii_digit(){self.i+=1;}
                J::N(std::str::from_utf8(&self.s[start..self.i]).unwrap().parse().unwrap())}
        }
    }
}
fn color(v:&J)->Color {match v.s(){"white"=>Color::White,"black"=>Color::Black,_=>panic!("color")}}
fn sq(v:&J)->Square {Square::parse(v.s()).unwrap()}
fn squares(v:&J)->Vec<Square>{v.a().iter().map(sq).collect()}
fn phase(v:&J)->Phase{Phase{opening:v["opening"].u() as u16,middlegame:v["middlegame"].u() as u16,endgame:v["endgame"].u() as u16}}
fn p(placement:&str,side:Color)->Position{Position::from_fen(&format!("{placement} {} - - 0 1",if side==Color::White{"w"}else{"b"})).unwrap()}
fn position(q:&J)->Position{p(q["placement"].s(),q.get("sideToMove").or(q.get("side")).map(color).unwrap_or(Color::White))}
fn bounded(q:&J)->eg::Bounded{eg::Bounded{score:q["score"].n(),lower:q["lowerBound"].n(),upper:q["upperBound"].n()}}
fn check_bounds(v:eg::Bounded,e:&J){assert_eq!((v.score,v.lower,v.upper),(e["score"].n(),e["lowerBound"].n(),e["upperBound"].n()));}
fn paths(v:&J)->pp::Paths{pp::Paths{score:0,minimum:v["minimumPath"].n(),best:v["bestPath"].n(),terminal:if v["bestTerminal"].null(){None}else{Some(sq(&v["bestTerminal"]))}}}
fn check_paths(v:pp::Paths,e:&J){assert_eq!((v.score,v.minimum,v.best,v.terminal),(e["score"].n(),e["minimumPath"].n(),e["bestPath"].n(),if e["bestTerminal"].null(){None}else{Some(sq(&e["bestTerminal"]))}));}
fn profile(v:&J)->u8{["weak","queen","rook","minor","pawn"].iter().zip([1,2,4,16,64]).map(|(k,w)|v[k].u()*w).sum::<u32>() as u8}
fn counts(v:&J)->[u8;6]{[v["pawn"].u() as u8,v["knight"].u() as u8,v["bishop"].u() as u8,v["rook"].u() as u8,v["queen"].u() as u8,1]}

pub fn run(path:&str){
    let bytes=std::fs::read(path).unwrap();let mut parser=Parser{s:&bytes,i:0};let case=parser.value();parser.ws();assert_eq!(parser.i,bytes.len());
    let op=case["operation"].s();let input=&case["input"];let expected=&case["expected"];
    if op.starts_with("search."){search(op,input,expected);return;}
    let answers=expected.get("results").or(expected.get("scores")).or(expected.get("classifications")).unwrap().a();
    let queries=input["queries"].a();assert_eq!(queries.len(),answers.len());
    for(index,(q,e))in queries.iter().zip(answers).enumerate(){check(op,q,e,index);}
}

fn descriptor(m:rook2::types::Move,e:&J){
    use rook2::types::MoveKind;
    assert_eq!(m.to_string(),e["move"].s());
    assert_eq!(match m.kind(){MoveKind::Castle=>"castle",MoveKind::EnPassant=>"enPassant",_=>"ordinary"},e["kind"].s());
}
fn moves(actual:&[rook2::types::Move],expected:&J){assert_eq!(actual.len(),expected.a().len());for(&m,e)in actual.iter().zip(expected.a()){descriptor(m,e);}}
fn work(actual:rook2::quiescence::Work,expected:&J){assert_eq!((actual.charged_search_units,actual.charged_relation_queries),(expected["chargedSearchUnits"].u() as u64,expected["chargedRelationQueries"].u() as u64));assert_eq!(actual.charged_search_units,expected["searchCounterDelta"].u() as u64);}
fn steps(actual:&[rook2::first_iteration::Step],expected:&J){
    assert_eq!(actual.len(),expected.a().len());
    for(a,e)in actual.iter().zip(expected.a()){
        descriptor(a.movement,&e["move"]);assert_eq!((a.lower,10000),(e["window"]["lower"].n(),e["window"]["upper"].n()));
        assert_eq!((a.score,a.best,a.second),(e["score"].n(),e["bestScore"].n(),e["secondScore"].n()));
        moves(&a.child_pv,&e["childPrincipalVariation"]);moves(&a.root_pv,&e["principalVariation"]);work(a.work,&e["work"]);
    }
}
fn search(op:&str,q:&J,e:&J){
    use rook2::{engine::Search,history::SearchHistory,movegen::{MoveList,generate_legal},quiescence::Limits};
    let mut position=Position::from_fen(q["fen"].s()).unwrap();let mut history=SearchHistory::new(&position);
    for token in q["moves"].a(){let mut legal=MoveList::new();generate_legal(&position,&mut legal);let movement=*legal.as_slice().iter().find(|m|m.to_string()==token.s()).unwrap();position=position.played_unchecked(movement);history.push(&position,Some(movement));}
    history.mark_root();let mut engine=Search::<true>::new(&position);let v=&q["personalityParameters"];
    let suffixes=["p","n","b","r","q","k","cc","mob","ks","pp","pw"];
    engine.evaluator.parameters=Parameters{own:std::array::from_fn(|i|v[format!("my{}",suffixes[i]).as_str()].n()),opponent:std::array::from_fn(|i|v[format!("op{}",suffixes[i]).as_str()].n()),average_depth:v["avd"].n(),draw:v["cfd"].n(),opponent_selectivity:v["sop"].n()};
    engine.config.selectivity=v["sel"].n();engine.config.maximum_depth=v["md"].u() as usize;engine.config.analysis=v["ana"].n();engine.config.tts_bytes=v["tts"].u() as usize;assert_eq!(v["rnd"].n(),0);
    let limits=Limits{nodes:Some(4095)};
    if op=="search.firstIteration"{
        let out=rook2::first_iteration::run(&mut engine,position,&mut history,limits).unwrap();moves(&out.candidates,&e["candidates"]);steps(&out.steps,&e["steps"]);assert_eq!(out.score,e["score"].n());moves(&out.pv,&e["principalVariation"]);work(out.work,&e["work"]);
    }else if op=="search.ordinaryIterations"{
        let out=engine.run_iterations(position,&mut history,q["completedIterations"].u() as u8,limits).unwrap();moves(&out.initial_candidates,&e["initialCandidates"]);assert_eq!(out.iterations.len(),e["iterations"].a().len());
        for(a,e)in out.iterations.iter().zip(e["iterations"].a()){assert_eq!(a.depth as u32,e["depth"].u());moves(&a.candidates,&e["candidates"]);steps(&a.steps,&e["steps"]);assert_eq!(a.score,e["score"].n());moves(&a.pv,&e["principalVariation"]);work(a.work,&e["work"]);}
        let result=&e["result"];assert_eq!(out.score,result["score"].n());moves(&out.pv,&result["principalVariation"]);work(out.work,&result["work"]);
    }else{panic!("unknown search operation {op}");}
    assert_eq!(history.search_ply(),0);
}

fn check(op:&str,q:&J,e:&J,index:usize){
    match op {
        "evaluation.centralInfluenceBalance"|"evaluation.positionCentralBalance"=>{
            let mut map=if q.get("placement").is_some(){Influence::build(&position(q))}else{Influence{profiles:[[0;64];2]}};
            if let Some(samples)=q.get("samples"){for sample in samples.a(){for(c,name)in ["white","black"].iter().enumerate(){map.profiles[c][sq(&sample["square"]).0 as usize]=profile(&sample[name]);}}}
            let v=pt::central(&map,phase(&q["phase"]),[q["weights"]["white"].n(),q["weights"]["black"].n()]);
            assert_eq!((v.colors[0],v.colors[1],v.weighted),(e["white"].n(),e["black"].n(),e["weighted"].n()),"query {index}");
        },
        "evaluation.boardPatterns"=>{let position=position(q);let v=pt::patterns(&position);assert_eq!(position.phase(),phase(&e["phase"]));
            assert_eq!((v.bishop_coordination,v.raw,v.opening),(e["bishopCoordination"].n(),e["rawPatterns"].n(),e["openingPatterns"].n()),"query {index}");},
        "evaluation.pawnProgress"=>{let position=position(q);assert_eq!(pp::raw(&position,&Influence::build(&position),sq(&q["pawnSquare"])),e["score"].n(),"query {index}");},
        "evaluation.pawnCandidates"|"evaluation.pawnCandidateEnding"=>{
            let position=position(q);let map=Influence::build(&position);let white=squares(&q["candidates"]["white"]);let black=squares(&q["candidates"]["black"]);
            let paths=[pp::candidates(&position,&map,Color::White,&white),pp::candidates(&position,&map,Color::Black,&black)];
            if op=="evaluation.pawnCandidates"{check_paths(paths[0],&e["white"]);check_paths(paths[1],&e["black"]);}
            else{let ending=pp::ending(&position,&map,paths,!white.is_empty()||!black.is_empty());assert_eq!((paths[0].score,paths[1].score,ending),(e["whiteScore"].n(),e["blackScore"].n(),e["endingScore"].n()),"query {index}");}
        },
        "evaluation.pawnEnding"=>{let position=position(q);let paths=[paths(&q["paths"]["white"]),paths(&q["paths"]["black"])];
            let ending=if q["kind"].s()=="pawnOnly"{pp::pawn_ending(&position,&Influence::build(&position),paths)}else{pp::queen_ending(&position,paths)};
            assert_eq!(ending,e["endingScore"].n(),"query {index}");},
        "evaluation.freshPawnSubtotal"=>{
            let position=position(q);let map=Influence::build(&position);let white=squares(&q["pawnOrder"]["white"]);let black=squares(&q["pawnOrder"]["black"]);
            let structure=pawn_structure::fresh_with_order(&position,&map,[&white,&black],[1024;2]);let phase=phase(&q["phase"]);
            let terms=pawn_terms::compute_with_phase(&position,&map,&structure,phase);
            let progress=pp::selected(&position,&map,&structure,phase,q["materialScore"].n(),[q["weights"]["white"]["progress"].n(),q["weights"]["black"]["progress"].n()]);
            let weighted=pp::structure_weighted(phase,terms.structure,terms.piece,[q["weights"]["white"]["structure"].n(),q["weights"]["black"]["structure"].n()]);
            assert_eq!((progress.ending,progress.weighted,weighted,terms.relation_queries),(e["endingScore"].n(),e["weightedProgress"].n(),e["weightedStructure"].n(),e["relationQueries"].u() as u64),"query {index}");
            for(c,name)in ["white","black"].iter().enumerate(){assert_eq!((terms.structure[c],terms.piece[c],progress.paths[c].score),(e["terms"][name]["structureScore"].n(),e["terms"][name]["pieceTerm"].n(),e["candidateScores"][name].n()),"query {index}");
                let side=if c==0{Color::White}else{Color::Black};let actual:Vec<_>=structure.pawn_slice(side).iter().filter(|d|d.candidate).map(|d|d.square).collect();assert_eq!(actual,squares(&e["candidates"][name]));}
        },
        "evaluation.pawnRace"=>assert_eq!(eg::pawn_race(color(&q["pawnSide"]),sq(&q["pawnKing"]),sq(&q["pawn"]),sq(&q["otherKing"]),color(&q["sideToMove"])),e.n(),"query {index}"),
        "evaluation.endgamePawnSpread"=>{let files=|key|q[key].a().iter().map(|v|v.s().as_bytes()[0]-b'a').collect::<Vec<_>>();assert_eq!(eg::pawn_spread_files(q["score"].n(),q["endgameWeight"].u() as u16,&files("whitePawnFiles"),&files("blackPawnFiles")),e.n(),"query {index}");},
        "evaluation.pawnlessPotential"=>assert_eq!(eg::pawnless_potential(q["score"].n(),&counts(&q["favoredMaterial"]),&counts(&q["otherMaterial"])),e.n(),"query {index}"),
        "evaluation.minorMateGeometry"=>assert_eq!(eg::minor_mate(sq(&q["strongerKing"]),sq(&q["weakerKing"]),sq(&q["bishop"])),e.n(),"query {index}"),
        "evaluation.endgameMaterialBlend"=>assert_eq!(eg::material_blend(&position(q),q["score"].n(),q["endgameWeight"].u() as u16,q["passedPawnBalance"].n()),e.n(),"query {index}"),
        "evaluation.fortressBounds"=>{let position=position(q);let side=color(&q["affectedSide"]);let value=if q["mode"].s()=="bishopPawns"{eg::bishop_pawns(&position,side,bounded(q))}else{eg::queen_pawn(&position,side,bounded(q))};assert_eq!((value.lower,value.upper),(e["lowerBound"].n(),e["upperBound"].n()),"query {index}");},
        "evaluation.rookFortress"=>{let position=position(q);let side=color(&q["affectedSide"]);let score=if q["mode"].s()=="rookPawn"{eg::rook_pawn(&position,side,q["score"].n())}else{eg::rook_against_pawns(&position,side,q["score"].n(),q["inCheck"].b())};assert_eq!(score,e.n(),"query {index}");},
        "evaluation.pawnRaceBounds"=>check_bounds(eg::race_bounds(&position(q),color(&q["pawnSide"]),bounded(q)),e),
        "evaluation.endgameAdjust"=>check_bounds(eg::adjust(&position(q),q["score"].n(),q["endgameWeight"].u() as u16,q["passedPawnBalance"].n(),q["inCheck"].b(),q["lowerBound"].n(),q["upperBound"].n()),e),
        "evaluation.finalScore"=>{let mut position=position(q);position.halfmove=q["reversiblePlies"].u() as u8;let v=eg::finish(&position,q["baseScore"].n(),q["drawPreference"].n(),color(&q["rootSide"]),q["variationRange"].u(),q["variationIdentity"].u(),q["endgameWeight"].u() as u16,q["inCheck"].b(),q["passedPawnBalance"].n());assert_eq!((v.score,v.lower,v.upper),(e["score"].n(),e["lowerBound"].n(),e["upperBound"].n()),"query {index}");},
        "evaluation.freshSubtotal"|"evaluation.freshScore"=>fresh(q,e,op=="evaluation.freshScore",index),
        _=>panic!("unsupported operation {op}"),
    }
}

fn fresh(q:&J,e:&J,final_score:bool,index:usize){
    const NAMES:[&str;11]=["pawn","knight","bishop","rook","queen","king","centralInfluence","mobility","kingSafety","pawnProgress","pawnStructure"];
    let own=std::array::from_fn(|i|q["percentages"]["own"][NAMES[i]].n());let opponent=std::array::from_fn(|i|q["percentages"]["opponent"][NAMES[i]].n());
    let parameters=Parameters{own,opponent,average_depth:q["averageDepth"].n(),draw:q.get("cfd").map_or(0,J::n),opponent_selectivity:q.get("sop").map_or(100,J::n)};
    let mut position=position(q);position.halfmove=q.get("reversiblePlies").map_or(0,J::u) as u8;
    for(c,name)in ["white","black"].iter().enumerate(){let order=squares(&q["pawnOrder"][name]);position.squares[c][..order.len()].copy_from_slice(&order);}
    let root=p(q["rootPlacement"].s(),color(&q["rootSide"]));let mut evaluator=Evaluator::<true>::new(&root);evaluator.parameters=parameters;evaluator.begin_search(&root);
    let checked=in_check(&position,position.side);let map=Influence::build(&position);let mut node=Node::root(position,&evaluator.root);let mut c=Components::default();
    let v=evaluator.fresh_observed(&mut node,&map,checked,|components|c=components);let subtotal=if final_score{&e["subtotal"]}else{e};
    assert_eq!(root.phase(),phase(&subtotal["rootPhase"]));assert_eq!(position.phase(),phase(&subtotal["currentPhase"]));assert_eq!(checked,subtotal["inCheck"].b());
    for(value,name)in [(c.material,"material"),(c.squares,"squareBalance"),(c.pawn_structure,"pawnStructure"),(c.pawn_progress,"pawnProgress"),(c.activity,"activity"),(c.central,"centralInfluence"),(c.shelter,"kingShelter"),(c.bishops,"bishopCoordination"),(c.patterns,"openingPatterns"),(c.tempo,"tempo")]{assert_eq!(value,subtotal["components"][name].n(),"query {index} component {name}");}
    assert_eq!((c.positional(),c.base(),v.relation_queries),(subtotal["positionalSubtotal"].n(),subtotal["baseScore"].n(),subtotal["relationQueries"].u() as u64),"query {index}");
    assert_eq!((node.retained.positional,node.retained.pawn_progress,node.retained.age),(subtotal["retained"]["positionalSubtotal"].n(),subtotal["retained"]["pawnProgress"].n(),0));
    if final_score{
        let id=&e["identity"];assert_eq!((position.primary,position.secondary,position.pawn,position.pawn%128),(id["primary"].u(),id["secondary"].u(),id["pawn"].u(),id["pawnGroup"].u()));
        assert_eq!(position.primary^position.secondary,e["variationIdentity"].u());assert_eq!((evaluator.draw_preference,evaluator.variation_range),(e["drawPreference"].n(),e["variationRange"].u()));
        let stages=eg::finish(&position,c.base(),evaluator.draw_preference,root.side,evaluator.variation_range,position.primary^position.secondary,position.phase().endgame,checked,c.pawn_progress);
        assert_eq!((stages.adjusted_base,stages.late_score,stages.scaled_score),(e["adjustedBase"].n(),e["lateEndgame"].n(),e["scaledScore"].n()),"query {index}");
        assert_eq!((v.score,v.lower,v.upper),(e["score"].n(),e["lowerBound"].n(),e["upperBound"].n()),"query {index}");
    }
}
