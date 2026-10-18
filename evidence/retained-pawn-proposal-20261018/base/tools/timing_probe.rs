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
    if matches!(case["operation"].s(),"search.seededTimedSearch"|"search.genericTimedSearch"){
        real_search(input,expected);return;
    }
    match case["operation"].s(){
        "session.interruptedSearches"=>{
            let mut s=rook2::session::Session::<true>::default();
            assert_eq!(input["searches"].a().len(),expected["results"].a().len());
            for(q,e)in input["searches"].a().iter().zip(expected["results"].a()){
                for c in q["commands"].a(){s.idle(c.s()).unwrap();}
                s.idle(&format!("time {}",q["allowanceCs"].n())).unwrap();
                let host=QueueHost{commands:q["queued"].a().iter().map(|v|match v.s(){"?"=>rook2::host::Command::Finish,"force"=>rook2::host::Command::Abort,"."=>rook2::host::Command::Status,"post"=>rook2::host::Command::Post(true),"nopost"=>rook2::host::Command::Post(false),_=>panic!("queue")}).collect(),records:Vec::new()};
                let (result,host)=s.go_live(host,0,rook2::quiescence::Limits{nodes:Some(524288)},21,false);let _result=result.unwrap();assert!(host.commands.is_empty());
                let actual=host.records.iter().filter(|v|!matches!(v,rook2::host::Record::Aborting)).collect::<Vec<_>>();
                assert_eq!(actual.len(),e["events"].a().len());
                for(record,e)in actual.into_iter().zip(e["events"].a()){
                    match record{
                        rook2::host::Record::Post(p)=>{assert_eq!(e["type"].s(),"post");post(p,e);},
                        rook2::host::Record::Status(s)=>{assert_eq!(e["type"].s(),"status");assert_eq!((s.centiseconds,s.search_id,s.depth_token,s.remaining,s.total,s.pv.as_str()),(e["engineCentiseconds"].n(),e["searchId"].u() as u64,e["depthToken"].n(),e["remaining"].u() as usize,e["total"].u() as usize,e["pv"].s()));},
                        rook2::host::Record::Move(m)=>{assert_eq!(e["type"].s(),"move");assert_eq!(m.to_string(),e["move"].s());},
                        _=>panic!("unexpected record"),
                    }
                }
            }
        },
        "session.ordinaryIterations"=>persistent(input,expected),
        "session.clockSeededSearches"|"session.searches"=>{
            let mut s=rook2::session::Session::<true>::default();
            assert_eq!(input["searches"].a().len(),expected["results"].a().len());
            for(q,e)in input["searches"].a().iter().zip(expected["results"].a()){
                for command in q["commands"].a(){assert!(matches!(s.idle(command.s()).unwrap(),rook2::session::Action::Reply(_)));}
                s.idle(&format!("time {}",q["allowanceCs"].n())).unwrap();s.idle(&format!("otim {}",q["allowanceCs"].n())).unwrap();
                let r=s.go(input.get("systemSeconds").map_or(0,J::u),rook2::quiescence::Limits{nodes:Some(524288)},9).unwrap();
                if let Some(seed)=e.get("seed"){assert_eq!(r.seed,seed.u());}
                let posts=r.events.iter().filter_map(|v|if let rook2::output::Event::Post(p)=v{Some(p)}else{None}).collect::<Vec<_>>();
                assert_eq!(posts.len(),e["posts"].a().len());for(p,e)in posts.iter().zip(e["posts"].a()){post(p,e);}
                let selected=match r.events.last().unwrap(){rook2::output::Event::Move(m)=>m.to_string(),_=>panic!("move")};assert_eq!(selected,e["move"].s());
            }
        },
        "session.timeSetup"=>{
            let mut session=rook2::session::Session::<true>::default();
            for command in input["commands"].a(){assert!(matches!(session.idle(command.s()).unwrap(),rook2::session::Action::Reply(_)));}
            let a=session.allowance().unwrap();assert_eq!((session.game_ply(),session.clock.adjustment_cs,a.average_cs,a.maximum_cs),(expected["gamePly"].u(),expected["adjustmentCs"].n(),expected["averageCs"].u(),expected["maximumCs"].u()));
            assert_eq!(session.clock.schedule.stages.len(),expected["stages"].a().len());
            for(s,e)in session.clock.schedule.stages.iter().zip(expected["stages"].a()){assert_eq!((s.moves,s.base_seconds,s.increment_seconds),(e["moves"].u(),e["baseSeconds"].u(),e["incrementSeconds"].u()));}
        },
        "session.goOutcome"=>{
            let mut session=rook2::session::Session::<true>::default();
            for command in input["commands"].a(){session.idle(command.s()).unwrap();}
            session.idle(&format!("time {}",input["remainingTimeCs"].n())).unwrap();
            let result=session.go(0,rook2::quiescence::Limits{nodes:Some(4095)},1);
            if expected["kind"].s()=="fatalExit"{assert!(matches!(result,Err(rook2::session::Error::FatalEmptyRoot)));}
            else {let result=result.unwrap();let posts=result.events.iter().filter_map(|v|if let rook2::output::Event::Post(p)=v{Some(p)}else{None}).collect::<Vec<_>>();assert_eq!(posts.len(),expected["posts"].a().len());for(p,e)in posts.iter().zip(expected["posts"].a()){post(p,e);}let selected=match result.events.last().unwrap(){rook2::output::Event::Move(m)=>m.to_string(),_=>panic!("move")};assert_eq!(selected,expected["move"].s());}
        },
        "search.ordinaryJoinedSearch"=>joined(input,expected),
        "time.schedule"=>{
            let s=schedule(input);assert_eq!(s.seconds(input["moveIndex"].u() as u64).unwrap(),expected["seconds"].u() as u64);
        },
        "time.allowance"=>{
            let s=schedule(input);let a=s.allowance(input["gamePly"].u(),input["adjustmentCs"].n(),input["searchOptimism"].n(),input["pondering"].b()).unwrap();
            assert_eq!((a.average_cs,a.maximum_cs),(expected["averageCs"].u(),expected["maximumCs"].u()));
        },
        "session.parameters"=>{
            let mut params=rook2::parameters::Parameters::default();let mut replies=Vec::new();
            for cmd in input["commands"].a(){let mut tokens=cmd.s().split_ascii_whitespace();assert_eq!(tokens.next(),Some("cm_parm"));replies.push(params.command(&tokens.collect::<Vec<_>>()).unwrap());}
            assert_eq!(replies,expected["replies"].a().iter().map(|v|v.s().to_owned()).collect::<Vec<_>>());
        },
        "output.searchScore"|"output.personalitySearchScore"=>{
            for(q,e)in input["queries"].a().iter().zip(expected["results"].a()){
                let draw=if let Some(d)=q.get("drawPreference"){d.n()}else{let p=&q["rootPhase"];rook2::evaluation::draw_preference(rook2::position::Phase{opening:p["opening"].u() as u16,middlegame:p["middlegame"].u() as u16,endgame:p["endgame"].u() as u16},q["cfd"].n())};
                assert_eq!((draw,rook2::output::reported_score(q["rankingScore"].n(),draw)),(e["drawPreference"].n(),e["reportedScore"].n()));
            }
        },
        "output.pvLine"=>{
            for(q,e)in input["queries"].a().iter().zip(expected["lines"].a()){
                let tokens=q["tokens"].a().iter().map(|v|v.s().to_owned()).collect::<Vec<_>>();
                let (included,bytes)=rook2::output::displayed_tokens(q["prefixLength"].u() as usize,&tokens);
                assert_eq!(included,e["tokens"].a().iter().map(|v|v.s().to_owned()).collect::<Vec<_>>());assert_eq!(bytes,e["byteLength"].u() as usize);
            }
        },
        "search.rootAspiration"=>{
            use rook2::timed::{aspiration,ranking_score};
            for(q,e)in input["queries"].a().iter().zip(expected["results"].a()){
                let window=aspiration(q["currentBest"].n(),q["previousBest"].n());
                let first=q["firstScore"].n();let retry=first>=window[1];
                let returned=if retry{q["retryScore"].n()}else{first};
                let passes=e["passes"].a();assert_eq!(passes.len(),if retry{2}else{1});
                for(i,p)in passes.iter().enumerate(){assert_eq!((p["lowerBound"].n(),p["upperBound"].n(),p["score"].n()),(window[0],if i==0{window[1]}else{10000},if i==0{first}else{returned}));}
                assert_eq!((returned,ranking_score(returned,window,true)),(e["returnedScore"].n(),e["rankingScore"].n()));
            }
        },
        "search.rootRandomization"=>{
            use rook2::{timed::{random_adjustment,score_add},types::{Move,MoveKind,PieceKind,Square}};
            for(q,e)in input["queries"].a().iter().zip(expected["results"].a()){
                let m=&q["move"];let kind=if !m["promotion"].null(){MoveKind::Promotion(match m["promotion"].s(){"knight"=>PieceKind::Knight,"bishop"=>PieceKind::Bishop,"rook"=>PieceKind::Rook,"queen"=>PieceKind::Queen,_=>panic!("piece")})}else{match m["kind"].s(){"ordinary"=>MoveKind::Ordinary,"castle"=>MoveKind::Castle,"enPassant"=>MoveKind::EnPassant,_=>panic!("kind")}};
                let m=Move::new(Square::parse(m["from"].s()).unwrap(),Square::parse(m["to"].s()).unwrap(),kind);
                let adjustment=random_adjustment(q["seed"].u(),q["randomness"].u(),m);
                assert_eq!((adjustment,score_add(q["lowerBound"].n(),-adjustment),score_add(q["upperBound"].n(),-adjustment),score_add(q["rawScore"].n(),adjustment)),(e["adjustment"].n(),e["searchLowerBound"].n(),e["searchUpperBound"].n(),e["rankingScore"].n()));
            }
        },
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

fn descriptor(m:rook2::types::Move,e:&J){
    use rook2::types::MoveKind;
    assert_eq!(m.to_string(),e["move"].s());
    assert_eq!(match m.kind(){MoveKind::Castle=>"castle",MoveKind::EnPassant=>"enPassant",_=>"ordinary"},e["kind"].s());
}
struct QueueHost{commands:std::collections::VecDeque<rook2::host::Command>,records:Vec<rook2::host::Record>}
impl rook2::host::Host for QueueHost{
    fn command(&mut self)->std::io::Result<Option<rook2::host::Command>>{Ok(self.commands.pop_front())}
    fn publish(&mut self,record:rook2::host::Record)->std::io::Result<()>{self.records.push(record);Ok(())}
}
fn schedule(q:&J)->rook2::clock::Schedule{
    rook2::clock::Schedule{stages:q["stages"].a().iter().map(|s|rook2::clock::Stage{moves:s["moves"].u(),base_seconds:s["baseSeconds"].u(),increment_seconds:s["incrementSeconds"].u()}).collect()}
}
fn post(p:&rook2::output::Post,e:&J){assert_eq!((p.fields.depth_token,p.fields.evaluation,p.fields.search_id,p.fields.centiseconds,p.pv.as_str()),(e["depthToken"].n(),e["evaluation"].n(),e["searchId"].u() as u64,e["engineCentiseconds"].n(),e["pv"].s()));}
fn events(actual:&[rook2::output::Event],expected:&J){
    assert_eq!(actual.len(),expected.a().len());
    for(event,e)in actual.iter().zip(expected.a()){
        match event{
            rook2::output::Event::Move(m)=>{assert_eq!(e["type"].s(),"move");assert_eq!(m.to_string(),e["move"].s());},
            rook2::output::Event::Post(p)=>{assert_eq!(e["type"].s(),"post");post(p,e);assert!(event.wire().ends_with('\n'));}
        }
    }
}
fn joined(q:&J,e:&J){
    let mut s=rook2::session::Session::<true>::default();s.idle("xboard").unwrap();s.idle("post").unwrap();
    let setup=&q["setup"];if setup["kind"].s()=="setboard-history"{s.idle(&format!("setboard {}",setup["fen"].s())).unwrap();}
    let remaining=match q["clock"]["group"].s(){"Easy"=>6637,"Hard"=>9483,"GM"=>18100,_=>panic!("group")};
    s.idle(&format!("time {remaining}")).unwrap();s.idle(&format!("otim {remaining}")).unwrap();s.idle("cm_parm default").unwrap();
    for name in rook2::parameters::NAMES{if !matches!(name,"ana"|"myk"|"opk"){s.idle(&format!("cm_parm {name}={}",q["personalityParameters"][name].n())).unwrap();}}
    if let Some(rnd)=q.get("randomnessOverride"){s.idle(&format!("cm_parm rnd={}",rnd.n())).unwrap();}
    s.idle("easy").unwrap();for m in setup["moves"].a(){assert_eq!(s.idle(m.s()).unwrap(),rook2::session::Action::Reply(Vec::new()));}
    let cap=q.get("diagnosticCapacity");let iterations=cap.map_or(3,|c|c["maximumEnteredIterations"].u()) as u8;let nodes=cap.map_or(8192,|c|c["maximumChargedSearchUnits"].u()) as u64;
    let expected_ingress=e.get("ingress").or(e.get("derivedIngress")).unwrap();let c=&expected_ingress["clock"];
    let a=s.allowance().unwrap();assert_eq!((s.game_ply(),s.clock.adjustment_cs,a.move_index,a.average_cs,a.maximum_cs),(c["gamePly"].u(),c["adjustmentCs"].n(),c["allowance"]["moveIndex"].u(),c["allowance"]["averageCs"].u(),c["allowance"]["maximumCs"].u()));
    let result=s.go(q["systemSeconds"].u(),rook2::quiescence::Limits{nodes:Some(nodes)},iterations);
    if e.get("fatal").is_some(){assert!(matches!(result,Err(rook2::session::Error::FatalEmptyRoot)));return;}
    let r=result.unwrap();assert_eq!(r.seed,expected_ingress["seed"]["acceptedSeed"].u());
    assert_eq!((r.outcome.stop.work.charged_search_units,r.outcome.stop.work.charged_relation_queries),(e["terminalWork"]["searchWork"].u() as u64,e["terminalWork"]["relationWork"].u() as u64));events(&r.events,&e["events"]);
}
fn fen(p:Position,fullmove:usize)->String{
    let mut rights=String::new();for(bit,c)in [(2,'K'),(1,'Q'),(8,'k'),(4,'q')]{if p.rights&bit!=0{rights.push(c);}}if rights.is_empty(){rights.push('-');}
    format!("{} {} {} {} {} {}",p.placement(),if p.side==rook2::types::Color::White{"w"}else{"b"},rights,if p.ep==64{"-".to_owned()}else{rook2::types::Square(p.ep).to_string()},p.halfmove,fullmove)
}
fn snapshot(s:&rook2::session::Session<true>,e:&J){
    let initial=s.states[0];let black=usize::from(initial.side==rook2::types::Color::Black);
    assert_eq!(fen(initial,1),e["initialFen"].s());assert_eq!(fen(s.position(),1+(s.moves.len()+black)/2),e["currentFen"].s());
    assert_eq!(s.moves.iter().map(ToString::to_string).collect::<Vec<_>>(),e["moves"].a().iter().map(|m|m.s().to_owned()).collect::<Vec<_>>());
    assert_eq!(if s.position().side==rook2::types::Color::White{"white"}else{"black"},e["sideToMove"].s());
    assert_eq!(if s.force{"force"}else if s.engine_color==rook2::types::Color::White{"play-white"}else{"play-black"},e["mode"].s());
}
fn persistent(q:&J,e:&J){
    let mut s=rook2::session::Session::<true>::default();s.setboard(q["initial"]["fen"].s()).unwrap();
    for name in rook2::parameters::NAMES{s.idle(&format!("cm_parm {name}={}",q["personalityParameters"][name].n())).unwrap();}
    s.idle(q["schedule"]["levelCommand"].s()).unwrap();s.idle(&format!("time {}",q["schedule"]["remainingTimeCs"].n())).unwrap();snapshot(&s,&e["initial"]);
    let mut searches=0;
    for(action,ae)in q["actions"].a().iter().zip(e["actions"].a()){
        snapshot(&s,&ae["before"]);
        match action["kind"].s(){
            "search"=>{
                let se=&e["searches"].a()[searches];snapshot(&s,&se["root"]);
                let out=s.go(0,rook2::quiescence::Limits{nodes:Some(4095)},3).unwrap();let ordinary=&se["ordinary"];
                moves(&out.outcome.initial_candidates,&ordinary["initialCandidates"]);assert_eq!(out.outcome.iterations.len(),ordinary["iterations"].a().len());
                for(i,ie)in out.outcome.iterations.iter().zip(ordinary["iterations"].a()){
                    assert!(i.complete);assert_eq!(i.depth as u32,ie["depth"].u());moves(&i.steps.iter().map(|s|s.movement).collect::<Vec<_>>(),&ie["candidates"]);assert_eq!(i.steps.len(),ie["steps"].a().len());
                    for(step,e)in i.steps.iter().zip(ie["steps"].a()){
                        descriptor(step.movement,&e["move"]);assert_eq!(step.window,[e["window"]["lower"].n(),e["window"]["upper"].n()]);
                        assert_eq!((step.score,step.best,step.second),(e["score"].n(),e["bestScore"].n(),e["secondScore"].n()));
                        moves(&step.child_pv,&e["childPrincipalVariation"]);moves(&step.pv,&e["principalVariation"]);work(step.work,&e["work"]);assert_eq!(step.work.charged_search_units,e["work"]["searchCounterDelta"].u() as u64);
                    }
                    let last=i.steps.last().unwrap();assert_eq!(last.best,ie["score"].n());moves(&last.pv,&ie["principalVariation"]);work(last.work,&ie["work"]);
                }
                let r=out.outcome.result.as_ref().unwrap();let er=&ordinary["result"];assert_eq!(r.score,er["score"].n());moves(&r.pv,&er["principalVariation"]);work(out.outcome.stop.work,&er["work"]);
                assert_eq!(r.pv[0].to_string(),se["selectedMove"].s());snapshot(&s,&se["after"]);searches+=1;
            },
            "force"|"undo"=>{s.idle(action["kind"].s()).unwrap();},
            "move"=>{s.idle(action["move"].s()).unwrap();},
            _=>panic!("action"),
        }
        snapshot(&s,&ae["after"]);
    }
    assert_eq!(searches,e["searches"].a().len());snapshot(&s,&e["final"]);
}
fn moves(a:&[rook2::types::Move],e:&J){assert_eq!(a.len(),e.a().len());for(&m,e)in a.iter().zip(e.a()){descriptor(m,e);}}
fn work(a:Work,e:&J){assert_eq!((a.charged_search_units,a.charged_relation_queries),(e["chargedSearchUnits"].u() as u64,e["chargedRelationQueries"].u() as u64));}
fn point(p:rook2::timed::Point)->&'static str{match p{rook2::timed::Point::Root=>"root",rook2::timed::Point::Iteration=>"iteration",rook2::timed::Point::Poll=>"poll"}}
fn index(a:Option<usize>,e:&J){assert_eq!(a,if e.null(){None}else{Some(e.u() as usize)});}

fn real_search(q:&J,e:&J){
    use rook2::{engine::Search,evaluator::Parameters,history::SearchHistory,movegen::{generate_legal,MoveList},timed::Controls};
    let mut position=Position::from_fen(q["fen"].s()).unwrap();let mut history=SearchHistory::new(&position);
    for token in q["moves"].a(){let mut legal=MoveList::new();generate_legal(&position,&mut legal);let m=*legal.as_slice().iter().find(|m|m.to_string()==token.s()).unwrap();position=position.played_unchecked(m);history.push(&position,Some(m));}history.mark_root();
    let p=&q["personalityParameters"];let mut search=Search::<true>::new(&position);
    let own=["myp","myn","myb","myr","myq","myk","mycc","mymob","myks","mypp","mypw"].map(|k|p[k].n());
    let opponent=["opp","opn","opb","opr","opq","opk","opcc","opmob","opks","oppp","oppw"].map(|k|p[k].n());
    search.evaluator.parameters=Parameters{own,opponent,average_depth:p["avd"].n(),draw:p["cfd"].n(),opponent_selectivity:p["sop"].n()};
    search.config=rook2::engine::Config{selectivity:p["sel"].n(),maximum_depth:p["md"].u() as usize,analysis:p["ana"].n(),tts_bytes:p["tts"].u() as usize};
    let out=search.run_work_timed(position,&mut history,Controls{average_cs:q["allowance"]["averageCs"].u(),maximum_cs:q["allowance"]["maximumCs"].u(),origin:0,seed:q["seed"].u(),randomness:p["rnd"].u(),maximum_entered_iterations:6},rook2::quiescence::Limits{nodes:Some(8192)}).unwrap();
    assert_eq!(history.search_ply(),0);assert_eq!(out.stats.iio_initial_phases+out.stats.iio_tail_phases,0);
    moves(&out.initial_candidates,&e["initialCandidates"]);assert_eq!(out.iterations.len(),e["iterations"].a().len());
    for(i,e)in out.iterations.iter().zip(e["iterations"].a()){
        assert_eq!((i.depth as u32,i.complete),(e["depth"].u(),e["complete"].b()));assert_eq!(i.steps.len(),e["steps"].a().len());
        for(s,e)in i.steps.iter().zip(e["steps"].a()){
            descriptor(s.movement,&e["move"]);assert_eq!(s.window,[e["window"]["lower"].n(),e["window"]["upper"].n()]);
            assert_eq!((s.adjustment,s.score,s.best,s.second),(e["adjustment"].n(),e["score"].n(),e["bestScore"].n(),e["secondScore"].n()));
            moves(&s.child_pv,&e["childPrincipalVariation"]);moves(&s.pv,&e["principalVariation"]);work(s.work,&e["work"]);
        }
    }
    assert_eq!(out.checks.len(),e["timeChecks"].a().len());
    for(c,e)in out.checks.iter().zip(e["timeChecks"].a()){
        assert_eq!(point(c.point),e["point"].s());assert_eq!((c.depth as u32,c.elapsed_cs,c.limit_seconds,c.stop),(e["depth"].u(),e["elapsedCs"].u(),e["limitSeconds"].f(),e["stop"].b()));index(c.root_index,&e["rootIndex"]);work(c.work,&e["work"]);
    }
    let s=&out.stop;let stop=&e["stop"];assert_eq!(point(s.point),stop["point"].s());assert_eq!((s.depth as u32,s.elapsed_cs),(stop["depth"].u(),stop["elapsedCs"].u()));index(s.root_index,&stop["rootIndex"]);work(s.work,&stop["work"]);
    if let Some(p)=s.pending{let e=&stop["pendingRoot"];descriptor(p.movement,&e["move"]);assert_eq!((p.window,p.adjustment),([e["window"]["lower"].n(),e["window"]["upper"].n()],e["adjustment"].n()));}else{assert!(stop["pendingRoot"].null());}
    let r=out.result.as_ref().unwrap();let er=&e["result"];assert_eq!((r.depth as u32,r.root_index as u32,r.score,r.search_id,r.elapsed_cs),(er["depth"].u(),er["rootIndex"].u(),er["score"].n(),er["searchId"].u() as u64,er["elapsedCs"].u()));moves(&r.pv,&er["principalVariation"]);
    let output=rook2::output::completed_events(position,&out,search.evaluator.draw_preference,search.config.selectivity,true).unwrap();events(&output,&e["events"]);
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
