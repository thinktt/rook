//! Lexical owner tests; these run with the test profile's unwinding panic policy.
use super::*;
use crate::{engine::Search,history::SearchHistory,quiescence::{Limits,Stopped},ordinary,timed};
const START:&str="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
fn parked<const D:bool>(e:&Evaluator<D>){assert!(e.full_worker.as_ref().unwrap().is_parked());}

#[test]
fn full_scope_parks_after_completion_error_and_test_unwind() {
    let p=Position::from_fen(START).unwrap();
    let mut s=Search::<true>::new(&p);s.config.tts_bytes=65536;
    s.evaluator.set_threads(2).unwrap();parked(&s.evaluator);
    for fen in [START,"6k1/5pp1/6p1/3P4/8/2N5/5P2/6K1 w - - 0 40",START] {
        let p=Position::from_fen(fen).unwrap();let mut h=SearchHistory::new(&p);
        s.run_iterations(p,&mut h,2,Limits::default()).unwrap();parked(&s.evaluator);
        assert!(matches!(s.run_iterations(p,&mut h,3,Limits{nodes:Some(0)}),Err(ordinary::Error::Stopped(Stopped::NodeLimit(0)))));parked(&s.evaluator);
    }
    let mut h=SearchHistory::new(&p);
    let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        s.run_seeded_iterations(p,&mut h,1,Limits::default(),0,0, |_|panic!("test callback unwind"))
    }));assert!(result.is_err());parked(&s.evaluator);
    let mut h=SearchHistory::new(&p);
    s.run_iterations(p,&mut h,1,Limits::default()).unwrap();parked(&s.evaluator);
    let control=timed::Controls{average_cs:1000,maximum_cs:10000,origin:0,seed:0,randomness:0,maximum_entered_iterations:1};
    assert!(matches!(s.run_work_timed(p,&mut h,control,Limits::default()),Err(ordinary::Error::IterationCapacity)));parked(&s.evaluator);
    let mut node=Node::root(p,&s.evaluator.root);
    s.evaluator.full(&mut node,&Influence::build(&p),false);parked(&s.evaluator);
}

#[test]
fn full_scope_parks_after_live_finish_abort_and_host_error() {
    use crate::host::{Host,Command,Control};
    struct Events {command:Option<Command>,fail:bool}
    impl Host for Events {
        fn command(&mut self)->std::io::Result<Option<Command>> {
            if self.fail {Err(std::io::Error::other("host control failure"))} else {Ok(self.command.take())}
        }
    }
    for (command,fail) in [(Some(Command::Finish),false),(Some(Command::Abort),false),(None,true)] {
        let p=Position::from_fen(START).unwrap();let mut s=Search::<true>::new(&p);
        s.config.tts_bytes=65536;s.evaluator.set_threads(2).unwrap();
        let (mut s,_)=s.map_host(Events{command,fail});
        s.control=Some(Control{clock:crate::clock::GameClock::default(),post:false,force:false,
            pondering:false,published:false,fine_work:false,game_ply:0,initial_side:p.side,clock_color:p.side});
        let c=timed::Controls{average_cs:1000,maximum_cs:10000,origin:0,seed:0,randomness:0,maximum_entered_iterations:8};
        let mut h=SearchHistory::new(&p);
        let result=s.run_work_timed(p,&mut h,c,Limits{nodes:Some(10000)});
        if fail {assert!(matches!(result,Err(ordinary::Error::Stopped(Stopped::HostIo(_)))));}
        else {assert_eq!(result.unwrap().stop.reason,if command==Some(Command::Abort){"abort"}else{"host"});}
        parked(&s.evaluator);
    }
}

#[test]
fn first_iteration_and_public_quiescence_boundaries_park_on_normal_and_stopped_returns() {
    use crate::quiescence::{Entry, Observer, Work};
    struct Quiet;
    impl Observer for Quiet {
        const ENABLED: bool = false;
        type Parent = ();
        type Frame = ();
        fn parent(_: &Retained) {}
        fn enter(&mut self, _: &Position, _: Entry, _: Option<Move>, _: (),
            _: Retained, _: bool, _: Work) {}
        fn stage(&mut self, _: EvaluationStage) {}
        fn ordered(&mut self) {}
        fn leave(&mut self, _: (), _: Retained, _: i32, _: &[Move], _: Work) {}
    }
    let p=Position::from_fen(START).unwrap();
    let mut s=Search::<true>::new(&p);
    s.set_threads(2).unwrap();
    let mut h=SearchHistory::new(&p);
    assert!(crate::first_iteration::run(&mut s,p,&mut h,Limits{nodes:Some(0)}).is_err());
    parked(&s.evaluator);
    let actual=crate::first_iteration::run(&mut s,p,&mut h,Limits::default()).unwrap();
    parked(&s.evaluator);
    let mut serial=Search::<true>::new(&p);
    let expected=crate::first_iteration::run(&mut serial,p,&mut h,Limits::default()).unwrap();
    assert_eq!((actual.score,actual.pv,actual.work,actual.stats,actual.evaluations),
        (expected.score,expected.pv,expected.work,expected.stats,expected.evaluations));
    let root=s.prepare_root(p);
    parked(&s.evaluator);
    let mut moves=crate::movegen::MoveList::new();
    crate::movegen::generate_legal(&p,&mut moves);
    let movement=moves.as_slice()[0];
    let entry=Entry{ply:1,target:1,iteration_depth:1,lower:-10000,upper:10000,
        analysis:0,capture_exception:crate::quiescence_policy::capture_exception(&p,&movement)};
    for observed in [false,true] {
        let mut node=root.child(&s.evaluator.root,movement);
        let mut history=SearchHistory::new(&p);
        history.push(&node.position,Some(movement));
        let limit=Limits{nodes:Some(0)};
        let stopped=if observed {
            s.search_subtree_observed(&mut node,&mut history,entry,limit,&root.retained,&mut Quiet)
        } else {s.search_subtree(&mut node,&mut history,entry,limit)};
        assert!(matches!(stopped,Err(Stopped::NodeLimit(0))));
        assert_eq!(history.search_ply(),1);
        parked(&s.evaluator);
        let complete=if observed {
            s.search_subtree_observed(&mut node,&mut history,entry,Limits::default(),&root.retained,&mut Quiet)
        } else {s.search_subtree(&mut node,&mut history,entry,Limits::default())};
        assert!(complete.is_ok());
        assert_eq!(history.search_ply(),1);
        parked(&s.evaluator);
    }
}
