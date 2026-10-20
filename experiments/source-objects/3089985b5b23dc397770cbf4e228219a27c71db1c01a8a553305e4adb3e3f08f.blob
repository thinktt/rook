//! One synchronous sequence owner for actual and controlled timed searches.
use crate::quiescence::Work;
use crate::root_schedule::{Attempt,Completed,Iteration,Policy,Returned,Row};
use crate::timing::Stage;

pub(crate) enum AttemptResult<I> { Returned(i32), Interrupted(I) }

/// Effects expose native owners through scoped static loans. The driver alone
/// admits and orders completion events; a Child remains alive through retries.
pub(crate) trait Effects {
    type Child;
    type Stop;
    type Interruption;
    type Error;
    fn work(&self)->Work;
    fn set_depth(&mut self,depth:u8);
    fn begin_iteration_records(&mut self,depth:u8);
    fn begin_candidate(&mut self,depth:u8,attempt:Attempt)->Self::Child;
    fn execute(&mut self,depth:u8,attempt:Attempt,child:&mut Self::Child)
        ->Result<AttemptResult<Self::Interruption>,Self::Error>;
    fn record_pass(&mut self,depth:u8,attempt:Attempt,value:i32,work:Work,child:&mut Self::Child);
    fn adjustment(&mut self,depth:u8,stage:Stage,previous:i32,best:i32,second:i32,work:Work);
    fn install_best(&mut self,child:&Self::Child,completed:Completed);
    fn capture(&mut self,depth:u8,completed:Completed,work:Work)->Result<(),Self::Error>;
    fn completed_step(&mut self,child:Self::Child,completed:Completed,work:Work);
    fn root_check(&mut self,depth:u8,completed:Completed,work:Work)->Option<Self::Stop>;
    fn finish_interrupted(&mut self,depth:u8,attempt:Attempt,child:&Self::Child,
        reason:Self::Interruption,work:Work)->Self::Stop;
    fn complete_iteration(&mut self,depth:u8,stage:Stage,previous:i32,best:i32,second:i32,
        work:Work)->Option<Self::Stop>;
}

/// None means only that the supplied resource/list is exhausted: actual search
/// turns it into IterationCapacity; controlled supplied runners report no stop.
pub(crate) fn drive<E:Effects>(mut rows:Vec<Row>,maximum_depth:u8,effects:&mut E)
    ->Result<Option<E::Stop>,E::Error> {
    let mut previous=0;
    for depth in 1..=maximum_depth {
        effects.set_depth(depth);
        let mut schedule=Iteration::new(rows,effects.work().charged_search_units,previous);
        let restricted=schedule.policy()==Policy::Restricted;
        effects.begin_iteration_records(depth);
        while let Some(initial)=schedule.next(effects.work().charged_search_units) {
            let mut child=effects.begin_candidate(depth,initial);
            let mut attempt=initial;
            let completed=loop {
                let value=match effects.execute(depth,attempt,&mut child)? {
                    AttemptResult::Returned(value)=>value,
                    AttemptResult::Interrupted(reason)=> {
                        let work=effects.work();
                        return Ok(Some(effects.finish_interrupted(depth,attempt,&child,reason,work)));
                    },
                };
                let work=effects.work();
                effects.record_pass(depth,attempt,value,work,&mut child);
                match schedule.returned(value,work.charged_search_units) {
                    Returned::Retry(next)=>attempt=next,
                    Returned::Completed(completed)=>break completed,
                }
            };
            let work=effects.work();
            if restricted&&completed.index==0 {
                effects.adjustment(depth,Stage::ScoreDrop,previous,completed.returned_score,
                    completed.second,work);
            }
            if completed.best_changed {
                effects.install_best(&child,completed);
                effects.adjustment(depth,Stage::BestChange,previous,completed.best,completed.second,work);
                effects.capture(depth,completed,work)?;
            }
            effects.completed_step(child,completed,work);
            if let Some(stop)=effects.root_check(depth,completed,work) { return Ok(Some(stop)); }
        }
        let (best,second,work)=(schedule.best(),schedule.second(),effects.work());
        let stage=if !restricted&&work.charged_search_units>=25000 {
            Stage::EasyIteration
        } else {Stage::Iteration};
        if let Some(stop)=effects.complete_iteration(depth,stage,previous,best,second,work) {
            return Ok(Some(stop));
        }
        previous=best;
        rows=schedule.into_ranked();
    }
    Ok(None)
}


use crate::post_lifecycle::CaptureSlot;
use crate::timing::{Adaptive,TerminalPrefix};
use crate::timed::Point;
use crate::work_clock::{charge_search_unit,Ledger};
use std::convert::Infallible;

#[derive(Clone,Copy,Debug)]
pub struct ElapsedReply {pub score:i32,pub work:u64,pub elapsed:u32}
#[derive(Clone,Copy,Debug)]
pub struct WorkReply {pub score:i32,pub work:u64,pub relations:u64}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum ControlledStage {Initialization,Adjustment,RootCompletion,IterationCompletion,Poll}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct ControlledCheck {
    pub stage:ControlledStage,pub depth:u8,pub index:usize,pub elapsed:u32,pub work:Work,
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct ControlledCapture {
    pub depth:u8,pub id:u16,pub score:i32,pub search_id:u64,pub elapsed:u32,
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct ControlledPass {
    pub depth:u8,pub attempt:Attempt,pub score:Option<i32>,pub completed:bool,
    pub work:Work,pub elapsed:u32,
}
pub struct SuppliedOutcome {
    pub limits:[f64;3],pub changes:[u32;3],pub depth:u8,pub stopped:bool,
    pub selected:Option<ControlledCapture>,pub work:Work,pub last_elapsed:u32,
    pub passes:Vec<ControlledPass>,pub posts:Vec<ControlledCapture>,pub clock_checks:Vec<ControlledCheck>,
}

trait Source:Sized {
    type Reply:Copy;
    fn work(&self)->Work;
    fn observe(&mut self)->u32;
    fn last(&self)->u32;
    fn score(reply:Self::Reply)->i32;
    fn perform<F:FnMut(&mut Self)->bool>(&mut self,reply:Self::Reply,poll:F)->bool;
}
struct ElapsedSource {work:Work,start:u32,elapsed:u32,last:u32}
impl Source for ElapsedSource {
    type Reply=ElapsedReply;
    fn work(&self)->Work {self.work}
    fn observe(&mut self)->u32 {self.last=self.start.wrapping_add(self.elapsed);self.last}
    fn last(&self)->u32 {self.last}
    fn score(reply:ElapsedReply)->i32 {reply.score}
    fn perform<F:FnMut(&mut Self)->bool>(&mut self,reply:ElapsedReply,_poll:F)->bool {
        self.work.charged_search_units=self.work.charged_search_units.checked_add(reply.work)
            .expect("supplied N exceeds native arithmetic domain");
        self.elapsed=self.elapsed.checked_add(reply.elapsed).expect("supplied elapsed exceeds u32");
        false
    }
}
struct WorkSource {work:Work,ledger:Ledger}
impl Source for WorkSource {
    type Reply=WorkReply;
    fn work(&self)->Work {self.work}
    fn observe(&mut self)->u32 {self.ledger.observe(self.work)}
    fn last(&self)->u32 {self.ledger.last()}
    fn score(reply:WorkReply)->i32 {reply.score}
    fn perform<F:FnMut(&mut Self)->bool>(&mut self,reply:WorkReply,mut poll:F)->bool {
        self.work.charged_relation_queries=self.work.charged_relation_queries.checked_add(reply.relations)
            .expect("supplied R exceeds native arithmetic domain");
        for _ in 0..reply.work {
            let due=charge_search_unit(&mut self.work.charged_search_units,None)
                .expect("absent supplied resource limit cannot fail");
            if due&&poll(self) {return true;}
        }
        false
    }
}

fn apply_control<S:Source>(adaptive:&mut Adaptive,source:&mut S,trace:&mut Vec<ControlledCheck>,
    stage:Stage,depth:u8,index:usize,previous:i32,best:i32,second:i32)->bool {
    let start=adaptive.start;
    adaptive.apply(stage,i32::from(depth),previous,best,second,|| {
        let clock=source.observe();
        let tag=match stage {
            Stage::BestChange|Stage::ScoreDrop=>ControlledStage::Adjustment,
            Stage::Root=>ControlledStage::RootCompletion,
            Stage::Iteration|Stage::EasyIteration=>ControlledStage::IterationCompletion,
            Stage::Poll=>ControlledStage::Poll,
        };
        trace.push(ControlledCheck{stage:tag,depth,index,elapsed:clock.wrapping_sub(start),work:source.work()});
        clock
    })
}

struct ControlledEffects<'a,S:Source> {
    replies:&'a [Vec<[S::Reply;2]>],source:S,adaptive:Adaptive,average:u32,
    index:usize,last_depth:u8,captures:CaptureSlot<ControlledCapture>,
    passes:Vec<ControlledPass>,trace:Vec<ControlledCheck>,
}
impl<S:Source> Effects for ControlledEffects<'_,S> {
    type Child=u16;
    type Stop=Point;
    type Interruption=();
    type Error=Infallible;
    fn work(&self)->Work {self.source.work()}
    fn set_depth(&mut self,depth:u8) {self.last_depth=depth;}
    fn begin_iteration_records(&mut self,_depth:u8) {}
    fn begin_candidate(&mut self,_depth:u8,attempt:Attempt)->u16 {self.index=attempt.index;attempt.id}
    fn execute(&mut self,depth:u8,attempt:Attempt,child:&mut u16)
        ->Result<AttemptResult<()>,Infallible> {
        let reply=self.replies[usize::from(depth)-1][usize::from(*child)][usize::from(attempt.retry)];
        let adaptive=&mut self.adaptive;let trace=&mut self.trace;
        let interrupted=self.source.perform(reply,|source| {
            apply_control(adaptive,source,trace,Stage::Poll,depth,attempt.index,0,0,0)
        });
        if interrupted {
            // The stopping poll already observed the credited final prefix.
            self.passes.push(ControlledPass{depth,attempt,score:None,completed:false,
                work:self.source.work(),elapsed:self.adaptive.elapsed_cs(self.source.last())});
            Ok(AttemptResult::Interrupted(()))
        } else {Ok(AttemptResult::Returned(S::score(reply)))}
    }
    fn record_pass(&mut self,depth:u8,attempt:Attempt,value:i32,work:Work,_child:&mut u16) {
        // Diagnostic reporting is an actual owned observation, excluded from the
        // adaptive trace. Actual production's Pass effect does not read a clock.
        let clock=self.source.observe();
        self.passes.push(ControlledPass{depth,attempt,score:Some(value),completed:true,work,
            elapsed:self.adaptive.elapsed_cs(clock)});
    }
    fn adjustment(&mut self,depth:u8,stage:Stage,previous:i32,best:i32,second:i32,_work:Work) {
        apply_control(&mut self.adaptive,&mut self.source,&mut self.trace,stage,depth,self.index,
            previous,best,second);
    }
    fn install_best(&mut self,_child:&u16,_completed:Completed) {}
    fn capture(&mut self,depth:u8,completed:Completed,work:Work)->Result<(),Infallible> {
        let clock=self.source.observe();
        let capture=ControlledCapture{depth,id:completed.id,score:completed.score,
            search_id:work.charged_search_units,elapsed:self.adaptive.elapsed_cs(clock)};
        self.captures.capture(depth,capture,|_|Ok::<(),Infallible>(()))
    }
    fn completed_step(&mut self,_child:u16,_completed:Completed,_work:Work) {}
    fn root_check(&mut self,depth:u8,completed:Completed,_work:Work)->Option<Point> {
        apply_control(&mut self.adaptive,&mut self.source,&mut self.trace,Stage::Root,depth,
            completed.index,0,completed.best,completed.second).then_some(Point::Root)
    }
    fn finish_interrupted(&mut self,_depth:u8,_attempt:Attempt,_child:&u16,_reason:(),_work:Work)->Point {
        Point::Poll
    }
    fn complete_iteration(&mut self,depth:u8,stage:Stage,previous:i32,best:i32,second:i32,
        _work:Work)->Option<Point> {
        let count=self.replies[usize::from(depth)-1].len();
        apply_control(&mut self.adaptive,&mut self.source,&mut self.trace,stage,depth,count,
            0,best,second);
        TerminalPrefix{depth:i32::from(depth),average_cs:self.average,analysis:0,best,second,previous,
            start:self.adaptive.start,clock:self.source.last(),iteration_limit:self.adaptive.limits[0]}
            .reason().map(|_|Point::Iteration)
    }
}

fn supplied<S:Source>(average:u32,maximum:u32,checked:bool,mut source:S,
    replies:&[Vec<[S::Reply;2]>])->SuppliedOutcome {
    assert!(!replies.is_empty()&&replies.len()<=usize::from(u8::MAX));
    let count=replies[0].len();
    assert!(count>0&&count<=usize::from(u16::MAX)+1);
    assert!(replies.iter().all(|row|row.len()==count));
    let start=source.observe();
    let trace=vec![ControlledCheck{stage:ControlledStage::Initialization,depth:0,index:0,
        elapsed:0,work:source.work()}];
    let mut effects=ControlledEffects{replies,source,adaptive:Adaptive::new(average,maximum,checked,start),
        average,index:0,last_depth:0,captures:CaptureSlot::new(),passes:Vec::new(),trace};
    let rows=(0..count).map(|id|Row{id:id as u16,score:0,work:0}).collect();
    let stop=match drive(rows,replies.len() as u8,&mut effects) {Ok(stop)=>stop,Err(never)=>match never {}};
    let ControlledEffects{source,adaptive,last_depth,captures,passes,trace,..}=effects;
    let (selected,posts)=captures.into_parts();
    SuppliedOutcome{limits:adaptive.limits,changes:adaptive.changes,depth:last_depth,stopped:stop.is_some(),
        selected,work:source.work(),last_elapsed:adaptive.elapsed_cs(source.last()),passes,posts,clock_checks:trace}
}

/// Typed supplied ordinary scores/work/elapsed; callers admit all rows before
/// entry and keep sums in the native arithmetic domain. Labels never enter here.
pub fn run_supplied_elapsed(average:u32,maximum:u32,start:u32,checked:bool,
    replies:&[Vec<[ElapsedReply;2]>])->SuppliedOutcome {
    supplied(average,maximum,checked,ElapsedSource{work:Work::default(),start,elapsed:0,last:start},replies)
}
/// Supplied relation-first/unit-by-unit activity, sharing actual credit/poll
/// admission and Ledger/Adaptive owners. No observation is added at finalization.
pub fn run_supplied_work(average:u32,maximum:u32,start:u32,checked:bool,
    replies:&[Vec<[WorkReply;2]>])->SuppliedOutcome {
    supplied(average,maximum,checked,WorkSource{work:Work::default(),ledger:Ledger::with_origin(start)},replies)
}


#[cfg(test)]
mod tests {
    use super::*;
    struct OrderedEffects {work:Work,events:Vec<&'static str>,stages:Vec<Stage>,depth:u8}
    impl Effects for OrderedEffects {
        type Child=u16;type Stop=();type Interruption=();type Error=Infallible;
        fn work(&self)->Work {self.work}
        fn set_depth(&mut self,depth:u8) {self.depth=depth;}
        fn begin_iteration_records(&mut self,_depth:u8) {}
        fn begin_candidate(&mut self,_depth:u8,attempt:Attempt)->u16 {attempt.id}
        fn execute(&mut self,_depth:u8,_attempt:Attempt,_child:&mut u16)
            ->Result<AttemptResult<()>,Infallible> {
            self.work.charged_search_units+=if self.work.charged_search_units==0 {25000} else {1};
            Ok(AttemptResult::Returned(100))
        }
        fn record_pass(&mut self,_depth:u8,_attempt:Attempt,_value:i32,_work:Work,_child:&mut u16) {}
        fn adjustment(&mut self,_depth:u8,stage:Stage,_previous:i32,_best:i32,_second:i32,_work:Work) {
            self.events.push(if stage==Stage::ScoreDrop {"drop"} else {"best"});
        }
        fn install_best(&mut self,_child:&u16,_completed:Completed) {self.events.push("install");}
        fn capture(&mut self,_depth:u8,_completed:Completed,_work:Work)->Result<(),Infallible> {
            self.events.push("capture");Ok(())
        }
        fn completed_step(&mut self,_child:u16,_completed:Completed,_work:Work) {self.events.push("step");}
        fn root_check(&mut self,depth:u8,completed:Completed,_work:Work)->Option<()> {
            self.events.push("root");(depth==2&&completed.index==0).then_some(())
        }
        fn finish_interrupted(&mut self,_depth:u8,_attempt:Attempt,_child:&u16,_reason:(),_work:Work) {}
        fn complete_iteration(&mut self,_depth:u8,stage:Stage,_previous:i32,_best:i32,_second:i32,
            _work:Work)->Option<()> {self.stages.push(stage);None}
    }
    #[test]
    fn coupled_driver_orders_restricted_first_transaction_and_stops_before_iteration_effects() {
        let rows=vec![Row{id:0,score:0,work:0},Row{id:1,score:0,work:0}];
        let mut effects=OrderedEffects{work:Work::default(),events:Vec::new(),stages:Vec::new(),depth:0};
        assert!(drive(rows,3,&mut effects).unwrap().is_some());
        assert_eq!(effects.depth,2);
        assert_eq!(effects.stages,[Stage::EasyIteration]);
        assert_eq!(&effects.events[effects.events.len()-6..],
            ["drop","install","best","capture","step","root"]);
        assert_eq!(effects.events.iter().filter(|&&e|e=="capture").count(),2);
        let r=|score,work|ElapsedReply{score,work,elapsed:0};
        let retried=run_supplied_elapsed(0,0,0,false,&[
            vec![[r(10,12500),r(0,0)],[r(0,12500),r(0,0)]],
            vec![[r(10,1),r(0,0)],[r(13,2),r(5,3)]]]);
        assert!(!retried.stopped);assert_eq!(retried.work.charged_search_units,25006);
        assert_eq!(retried.passes.len(),5);
        assert_eq!((retried.passes[3].attempt.window,retried.passes[3].score),([12,13],Some(13)));
        assert_eq!((retried.passes[4].attempt.window,retried.passes[4].score),([12,10000],Some(5)));
        assert!(retried.passes[4].attempt.retry);
        assert_eq!(retried.changes,[1,1,0]);
        let captured=retried.selected.unwrap();
        assert_eq!((captured.depth,captured.id,captured.score,captured.search_id),(2,0,10,25001));
    }
    fn reply(score:i32,work:u64,relations:u64)->WorkReply {WorkReply{score,work,relations}}
    #[test]
    fn final_unit_poll_withholds_score_and_preserves_only_previously_completed_capture() {
        let empty=run_supplied_work(0,1,0,false,&[vec![[reply(999,4096,50000),reply(0,1,0)]]]);
        assert!(empty.stopped);assert!(empty.selected.is_none());assert!(empty.posts.is_empty());
        assert_eq!(empty.work,Work{charged_search_units:4096,charged_relation_queries:50000});
        assert_eq!((empty.passes.len(),empty.passes[0].completed,empty.passes[0].score),(1,false,None));
        assert_eq!(empty.clock_checks.iter().map(|c|c.stage).collect::<Vec<_>>(),
            [ControlledStage::Initialization,ControlledStage::Poll]);
        let saved=run_supplied_work(0,1,u32::MAX,false,&[vec![
            [reply(100,4096,0),reply(0,50000,50000)],
            [reply(2000,4096,0),reply(0,50000,50000)]]]);
        assert!(saved.stopped);assert_eq!(saved.work.charged_search_units,8192);
        assert_eq!(saved.work.charged_relation_queries,0);
        assert_eq!(saved.passes.len(),2);assert!(!saved.passes[1].completed);
        let capture=saved.selected.unwrap();
        assert_eq!((capture.id,capture.score,capture.search_id,capture.elapsed),(0,100,4096,0));
        assert_eq!(saved.last_elapsed,1);assert!(saved.posts.is_empty());
    }
    #[test]
    fn relations_do_not_poll_and_reporting_reads_retain_fractional_carry_without_restamping_capture() {
        let only=run_supplied_work(0,1,19,false,&[vec![[reply(100,0,50000),reply(0,0,0)]]]);
        assert!(!only.stopped);assert_eq!(only.work.charged_search_units,0);
        assert_eq!(only.last_elapsed,1);assert_eq!(only.clock_checks.len(),1);
        assert_eq!(only.selected.as_ref().unwrap().elapsed,1);
        let carried=run_supplied_work(0,1,u32::MAX-2,false,&[vec![
            [reply(100,7882,0),reply(0,0,0)],[reply(0,0,2),reply(0,0,0)]]]);
        assert!(!carried.stopped);
        assert_eq!(carried.work,Work{charged_search_units:7882,charged_relation_queries:2});
        assert_eq!((carried.passes[0].elapsed,carried.passes[1].elapsed,carried.last_elapsed),(0,1,1));
        assert_eq!(carried.selected.as_ref().unwrap().elapsed,0);
        assert_eq!(carried.clock_checks.len(),2);
        assert_eq!(carried.clock_checks[1].work.charged_search_units,4096);
        assert!(carried.clock_checks.iter().all(|c|c.depth<=1));
    }
}
