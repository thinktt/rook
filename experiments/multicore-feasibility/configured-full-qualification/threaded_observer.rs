//! Standalone test against the frozen source's existing normal library rlib.
//! No production source/default override; exercise enabled Q observation in1/2.
use rook2::engine::Search;
use rook2::evaluator::{EvalStats, EvaluationStage, Node, Retained};
use rook2::history::SearchHistory;
use rook2::movegen::{generate_legal, MoveList};
use rook2::position::Position;
use rook2::quiescence::{Entry, Limits, Observer, Stats, Stopped, Work};
use rook2::types::Move;

#[derive(Debug, PartialEq, Eq)]
enum Event {
    Enter(usize, Position, (usize,i32,i32,i32,i32,i32,bool), Option<Move>, Retained, Retained, bool, Work),
    Stage(EvaluationStage),
    Ordered,
    Leave(usize, Retained, i32, Vec<Move>, Work),
}

#[derive(Default, Debug, PartialEq, Eq)]
struct Trace {
    next: usize,
    events: Vec<Event>,
    stack: Vec<(usize,Retained)>,
}

impl Observer for Trace {
    const ENABLED: bool = true;
    type Parent = Retained;
    type Frame = usize;
    fn parent(retained: &Retained) -> Retained { *retained }
    fn enter(&mut self, position: &Position, entry: Entry, movement: Option<Move>,
        parent: Retained, arrival: Retained, checked: bool, work: Work) -> usize {
        if let Some((_,current))=self.stack.last() { assert_eq!(*current,parent); }
        assert_eq!(arrival.positional,parent.positional);
        assert_eq!(arrival.pawn_progress,parent.pawn_progress);
        assert_eq!(arrival.age,parent.age.wrapping_add(1));
        let id=self.next;self.next+=1;
        self.events.push(Event::Enter(id,*position,(entry.ply,entry.target,
            entry.iteration_depth,entry.lower,entry.upper,entry.analysis,entry.capture_exception),
            movement,parent,arrival,checked,work));
        self.stack.push((id,arrival));id
    }
    fn stage(&mut self, stage: EvaluationStage) {
        let current=&mut self.stack.last_mut().unwrap().1;
        assert_eq!(*current,stage.before);
        *current=stage.after;
        self.events.push(Event::Stage(stage));
    }
    fn ordered(&mut self) { self.events.push(Event::Ordered); }
    fn leave(&mut self, id: usize, retained: Retained, score: i32, pv: &[Move], work: Work) {
        assert_eq!(self.stack.pop(),Some((id,retained)));
        self.events.push(Event::Leave(id,retained,score,pv.to_vec(),work));
    }
}

#[derive(Debug, PartialEq, Eq)]
struct Observed {
    returned: Result<(i32,Vec<Move>,Work,Stats,EvalStats),Stopped>,
    trace: Trace,
    node: Node,
    work: Work,
    evaluations: EvalStats,
}

fn run(budget: usize, fen: &str, token: &str, limits: Limits) -> Observed {
    let position=Position::from_fen(fen).unwrap();
    let mut search=Search::<true>::new(&position);
    search.set_threads(budget).unwrap();
    assert_eq!((search.requested_threads(),search.configured_threads()),(budget,budget));
    let root=search.prepare_root(position);
    let mut legal=MoveList::new();generate_legal(&position,&mut legal);
    let movement=*legal.as_slice().iter().find(|m|m.to_string()==token).unwrap();
    let mut node=root.child(&search.evaluator.root,movement);
    let mut history=SearchHistory::new(&position);history.push(&node.position,Some(movement));
    let entry=Entry{ply:1,target:1,iteration_depth:1,lower:-10000,upper:10000,
        analysis:0,capture_exception:rook2::quiescence_policy::capture_exception(&position,&movement)};
    let mut trace=Trace::default();
    let returned=search.search_subtree_observed(&mut node,&mut history,entry,limits,
        &root.retained,&mut trace).map(|o|(o.score,o.pv,o.work,o.stats,o.evaluations));
    assert_eq!(history.search_ply(),1);
    if returned.is_ok() { assert!(trace.stack.is_empty()); }
    Observed{returned,trace,node,work:search.work(),evaluations:search.evaluator.stats}
}

#[test]
fn enabled_quiescence_observer_is_identical_with_one_or_two_configured_threads() {
    let mut stages=0;
    for (fen,token) in [
        ("r3k3/1Pr5/8/8/8/8/8/4K3 b - - 0 1","c7c8"),
        ("1N2k3/4r3/8/8/8/8/8/K3R3 w - - 0 1","b8d7"),
        ("1r5k/7p/6Q1/8/8/3B4/8/K7 b - - 0 1","b8b6"),
        ("1r5k/6pp/6Q1/8/8/3B4/8/K7 b - - 0 1","b8b7"),
        ("4k3/8/8/8/3p4/8/4P3/4K3 w - - 0 1","e2e4"),
        ("7k/8/5KQ1/8/8/8/8/8 w - - 0 1","g6g7"),
    ] {
        for limits in [Limits::default(),Limits{nodes:Some(2)}] {
            let one=run(1,fen,token,limits);
            let two=run(2,fen,token,limits);
            stages+=two.trace.events.iter().filter(|e|matches!(e,Event::Stage(_))).count();
            assert_eq!(one,two,"{fen} {token} {limits:?}");
        }
    }
    assert!(stages>0,"the enabled-observer producer must actually be exercised");
}
