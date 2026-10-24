//! Work-timed native ordinary search. Public ingress, commands and rendering are separate.
use crate::engine::Search;
use crate::evaluator::{EvalStats, Node};
use crate::influence::Influence;
use crate::history::SearchHistory;
use crate::movegen::{self, MoveList};
use crate::ordinary::{Error, Predecessor, Request};
use crate::position::Position;
use crate::post_lifecycle::CaptureSlot;
use crate::quiescence::{Limits, Stats, Stopped, Work};
use crate::root_schedule::{Attempt as RootAttempt, Completed as RootCompleted, Row as RootRow};
use crate::timed_sequence::{self, AttemptResult, Effects};
use crate::timing::{Adaptive, Stage, Terminal};
use crate::types::{Move, MoveKind, PieceKind};
use crate::work_clock::Ledger;

#[derive(Clone, Copy, Debug)]
pub struct Controls {
    pub average_cs: u32,
    pub maximum_cs: u32,
    pub origin: u32,
    pub seed: u32,
    pub randomness: u32,
    /// Resource admission only; exhausting it returns an error, never a partial result.
    pub maximum_entered_iterations: u8,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Point {
    Root,
    Iteration,
    Poll,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Check {
    pub point: Point,
    pub depth: u8,
    pub root_index: Option<usize>,
    pub work: Work,
    pub elapsed_cs: u32,
    pub limit_seconds: f64,
    pub stop: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Pending {
    pub movement: Move,
    pub window: [i32; 2],
    pub adjustment: i32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Capture {
    pub depth: u8,
    pub root_index: usize,
    pub score: i32,
    pub pv: Vec<Move>,
    pub search_id: u64,
    pub elapsed_cs: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Pass {
    pub window: [i32; 2],
    pub returned_score: i32,
    pub work: Work,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Step {
    pub movement: Move,
    pub window: [i32; 2],
    pub adjustment: i32,
    pub score: i32,
    pub best: i32,
    pub second: i32,
    pub child_pv: Vec<Move>,
    pub pv: Vec<Move>,
    pub work: Work,
    pub passes: Vec<Pass>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Iteration {
    pub depth: u8,
    pub complete: bool,
    pub steps: Vec<Step>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Stop {
    pub point: Point,
    pub depth: u8,
    pub root_index: Option<usize>,
    pub work: Work,
    pub elapsed_cs: u32,
    pub pending: Option<Pending>,
    pub reason: &'static str,
}

pub struct Outcome {
    pub seed: u32,
    pub initial_candidates: Vec<Move>,
    pub iterations: Vec<Iteration>,
    pub checks: Vec<Check>,
    pub stop: Stop,
    /// None means no root completed; the caller owns the first-root fallback arm.
    pub result: Option<Capture>,
    /// Best captures eligible for immediate publication (depth >=3).
    pub publications: Vec<Capture>,
    pub ledger: Ledger,
    pub stats: Stats,
    pub evaluations: EvalStats,
}

pub(crate) struct Clock {
    pub adaptive: Adaptive,
    pub ledger: Ledger,
    pub depth: u8,
    pub root_index: usize,
    pub checks: Vec<Check>,
    pub last_check: Option<Check>,
    pub root: Position,
    pub root_total: usize,
}

impl Clock {
    fn new(controls: Controls, checked: bool, root: Position, root_total: usize) -> Self {
        let mut ledger = Ledger::with_origin(controls.origin);
        let start = ledger.observe(Work::default());
        Self {
            adaptive: Adaptive::new(controls.average_cs, controls.maximum_cs, checked, start),
            ledger,
            depth: 1,
            root_index: 0,
            checks: Vec::new(),
            last_check: None,
            root,
            root_total,
        }
    }

    fn adjustment(&mut self, stage: Stage, previous: i32, best: i32, second: i32, work: Work) {
        self.adaptive
            .apply(stage, self.depth as i32, previous, best, second, || {
                self.ledger.observe(work)
            });
    }

    pub(crate) fn check<const D: bool>(
        &mut self,
        stage: Stage,
        best: i32,
        second: i32,
        work: Work,
    ) -> bool {
        let stop = self
            .adaptive
            .apply(stage, self.depth as i32, 0, best, second, || {
                self.ledger.observe(work)
            });
        if self.depth > 1 || stage == Stage::Poll {
            let (point, index) = match stage {
                Stage::Root => (Point::Root, 1),
                Stage::Poll => (Point::Poll, 2),
                Stage::Iteration | Stage::EasyIteration => (Point::Iteration, 0),
                _ => unreachable!(),
            };
            let check = Check {
                point,
                depth: self.depth,
                root_index: if point == Point::Iteration {
                    None
                } else {
                    Some(self.root_index)
                },
                work,
                elapsed_cs: self.adaptive.elapsed_cs(self.ledger.last()),
                limit_seconds: self.adaptive.limits[index],
                stop,
            };
            if D {
                self.checks.push(check.clone());
            }
            self.last_check = Some(check);
        }
        stop
    }
}

/// Ordinary-score addition leaves mate/sentinel bands untouched.
pub fn score_add(score: i32, delta: i32) -> i32 {
    if !(-8999..=8999).contains(&score) {
        score
    } else {
        (score as i64 + delta as i64).clamp(-8999, 8999) as i32
    }
}

pub fn aspiration(best: i32, previous: i32) -> [i32; 2] {
    [
        score_add(best, 2),
        score_add(10000.min(best.max(previous) + 1), 2),
    ]
}

pub fn ranking_score(returned: i32, window: [i32; 2], restricted: bool) -> i32 {
    if restricted && returned <= window[0] {
        score_add(returned, -2)
    } else {
        returned
    }
}

pub fn random_adjustment(seed: u32, randomness: u32, movement: Move) -> i32 {
    assert!(randomness <= i32::MAX as u32);
    if randomness == 0 {
        return 0;
    }
    let weight = |s: crate::types::Square| s.file() as u32 + 1 + 10 * s.rank() as u32;
    let (kind, promotion) = match movement.kind() {
        MoveKind::Ordinary => (0, 0),
        MoveKind::EnPassant => (16779280, 0),
        MoveKind::Castle => (33558560, 0),
        MoveKind::Promotion(k) => (
            0,
            match k {
                PieceKind::Knight => 1,
                PieceKind::Bishop => 2,
                PieceKind::Rook => 3,
                PieceKind::Queen => 4,
                _ => unreachable!(),
            },
        ),
    };
    let mixed = seed
        ^ seed.wrapping_shl(13)
        ^ (seed / 128)
        ^ (16908288 * weight(movement.from()))
        ^ (8193 * weight(movement.to()))
        ^ (2097410 * promotion)
        ^ kind;
    (mixed % (randomness + 1)) as i32 - (randomness / 2) as i32
}

#[cfg(test)]
mod tests {
    use super::*;
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    fn controls() -> Controls {
        Controls {
            average_cs: 0,
            maximum_cs: 1,
            origin: 0xfffffff0,
            seed: 0,
            randomness: 50,
            maximum_entered_iterations: 6,
        }
    }

    #[test]
    fn natural_poll_unwinds_and_preserves_completed_capture_across_diagnostic_modes() {
        let p = Position::from_fen(START).unwrap();
        let mut a = Search::<true>::new(&p);
        let mut b = Search::<false>::new(&p);
        a.config.tts_bytes = 65536;
        b.config.tts_bytes = 65536;
        let mut history = SearchHistory::new(&p);
        let x = a
            .run_work_timed(p, &mut history, controls(), Limits::default())
            .unwrap();
        assert_eq!(history.search_ply(), 0);
        let y = b
            .run_work_timed(p, &mut history, controls(), Limits::default())
            .unwrap();
        assert_eq!(history.search_ply(), 0);
        assert_eq!(x.stop.point, Point::Poll);
        assert_eq!(x.stop.work.charged_search_units % 4096, 0);
        assert!(x.stop.pending.is_some());
        assert!(x.result.as_ref().unwrap().search_id < x.stop.work.charged_search_units);
        assert!(!x.iterations.last().unwrap().complete);
        assert_eq!(
            (&x.result, &x.stop, &x.publications, x.ledger),
            (&y.result, &y.stop, &y.publications, y.ledger)
        );
        assert!(y.checks.is_empty() && y.iterations.iter().all(|i| i.steps.is_empty()));
        assert!(a.timing.is_none() && b.timing.is_none());
        let mut replay = p;
        for &m in &x.result.unwrap().pv {
            let mut legal = MoveList::new();
            movegen::generate_legal(&replay, &mut legal);
            assert!(legal.as_slice().contains(&m));
            replay = replay.played_unchecked(m);
        }
    }

    #[test]
    fn resource_exhaustion_returns_no_timed_result_and_clears_the_poll_controller() {
        let p = Position::from_fen(START).unwrap();
        let mut search = Search::<true>::new(&p);
        search.config.tts_bytes = 65536;
        let mut history = SearchHistory::new(&p);
        let mut c = controls();
        c.maximum_entered_iterations = 1;
        assert!(matches!(
            search.run_work_timed(p, &mut history, c, Limits::default()),
            Err(Error::IterationCapacity)
        ));
        assert!(search.timing.is_none());
        assert_eq!(history.search_ply(), 0);
        let out = search
            .run_iterations(p, &mut history, 1, Limits::default())
            .unwrap();
        assert_eq!(out.iterations.len(), 1);
        assert!(search.timing.is_none());
    }
    #[test]
    fn default_explicit_true_and_guarded_zero_entry_timed_runs_keep_identical_records() {
        let position=Position::from_fen(START).unwrap();
        let mut results=Vec::new();
        for mode in 0..3 {
            let mut search=Search::<true>::new(&position);
            search.config.tts_bytes=65536;
            let mut history=SearchHistory::new(&position);
            let mut control=controls();control.average_cs=1;control.origin=0;
            let result=match mode {
                0=>search.run_work_timed(position,&mut history,control,Limits{nodes:Some(8192)}),
                1=>search.run_work_timed_entry::<true>(position,&mut history,control,Limits{nodes:Some(8192)}),
                _=>search.run_work_timed_without_iio(position,&mut history,control,Limits{nodes:Some(8192)}),
            }.unwrap();
            assert!(search.timing.is_none());assert_eq!(history.search_ply(),0);
            assert_eq!((result.stats.iio_initial_phases,result.stats.iio_tail_phases),(0,0));
            results.push(result);
        }
        let expected=&results[0];
        for actual in &results[1..] {
            assert_eq!((&actual.initial_candidates,&actual.result,&actual.publications,
                &actual.stop,&actual.checks,actual.ledger,actual.stats,actual.evaluations),
                (&expected.initial_candidates,&expected.result,&expected.publications,
                &expected.stop,&expected.checks,expected.ledger,expected.stats,expected.evaluations));
            assert_eq!(actual.iterations.len(),expected.iterations.len());
            for (a,b) in actual.iterations.iter().zip(&expected.iterations) {
                assert_eq!((a.depth,a.complete,&a.steps),(b.depth,b.complete,&b.steps));
            }
        }
    }

    #[test]
    fn guarded_timed_iio_error_unwinds_active_history_and_always_clears_timing() {
        let position=Position::from_fen("6k1/8/8/8/8/8/P7/K6R w - - 0 1").unwrap();
        let mut search=Search::<true>::new(&position);search.config.tts_bytes=96;
        let mut history=SearchHistory::new(&position);
        let control=Controls{average_cs:0,maximum_cs:0,origin:u32::MAX-2,
            seed:0,randomness:0,maximum_entered_iterations:6};
        assert!(matches!(search.run_work_timed_without_iio(position,&mut history,control,
            Limits{nodes:Some(100000)}),Err(Error::Stopped(Stopped::InternalIterativeOrdering))));
        assert_eq!(history.search_ply(),0);assert!(search.timing.is_none());
        assert_eq!(search.stats.iio_initial_phases+search.stats.iio_tail_phases,1);
        assert_eq!((search.stats.iio_passes,search.stats.iio_children),(0,0));
        let retry=search.run_iterations(position,&mut history,1,Limits::default()).unwrap();
        let mut fresh=Search::<true>::new(&position);fresh.config.tts_bytes=96;
        let expected=fresh.run_iterations(position,&mut history,1,Limits::default()).unwrap();
        assert_eq!((retry.score,retry.pv,retry.work),(expected.score,expected.pv,expected.work));
        assert_eq!(history.search_ply(),0);assert!(search.timing.is_none());
    }

}

impl<const D: bool, H: crate::host::Host> Search<D, H> {
    pub(crate) fn publish_capture(&mut self, capture: &Capture) -> std::io::Result<()> {
        use crate::{host::Record, output};
        let Some(control) = self.control.as_mut() else {
            return Ok(());
        };
        if !control.post {
            return Ok(());
        }
        let clock = self.timing.as_ref().unwrap();
        let mut fields = output::capture_fields(
            &clock.root,
            capture,
            self.evaluator.draw_preference,
            self.config.selectivity,
        );
        if control.fine_work {
            fields.centiseconds = clock.ledger.fine_post();
        }
        let post = output::render(clock.root, &capture.pv, fields).map_err(|e| {
            std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                format!("invalid captured PV: {e:?}"),
            )
        })?;
        self.host.publish(Record::Post(post))?;
        control.published = true;
        Ok(())
    }

    pub(crate) fn work_poll(&mut self, history: &SearchHistory, work: Work) -> Result<(), Stopped> {
        use crate::host::{Command, Record};
        let Some(clock) = self.timing.as_mut() else {
            return Ok(());
        };
        let maximum = clock.check::<D>(Stage::Poll, 0, 0, work);
        if H::ACTIVE {
            let command = self.host.command().map_err(|e| Stopped::HostIo(e.kind()))?;
            if let Some(command) = command {
                let control = self
                    .control
                    .as_mut()
                    .expect("active host requires session controls");
                match command {
                    Command::Finish => return Err(Stopped::HostStop),
                    Command::Abort => {
                        control.force = true;
                        self.host
                            .publish(Record::Aborting)
                            .map_err(|e| Stopped::HostIo(e.kind()))?;
                        return Err(Stopped::HostAbort);
                    }
                    Command::Post(enabled) => control.post = enabled,
                    Command::Easy => control.pondering = false,
                    Command::Ignore => {}
                    Command::Time(remaining) => control
                        .clock
                        .synchronize(
                            remaining,
                            control.game_ply,
                            control.initial_side,
                            control.clock_color,
                            clock.ledger.last(),
                        )
                        .map_err(|_| Stopped::HostIo(std::io::ErrorKind::InvalidInput))?,
                    Command::Status => {
                        let depth = clock.depth as i32;
                        let margin = crate::ordinary_policy::selective_depth(
                            depth,
                            self.config.selectivity,
                            clock.root.phase().endgame,
                            depth,
                        )
                        .margin;
                        let status = crate::output::status(
                            clock.root,
                            history.search_path(),
                            clock.adaptive.elapsed_cs(clock.ledger.last()) as i32,
                            work.charged_search_units,
                            1000 * depth + margin,
                            clock.root_total - clock.root_index - 1,
                            clock.root_total,
                        )
                        .map_err(|_| Stopped::HostIo(std::io::ErrorKind::InvalidData))?;
                        self.host
                            .publish(Record::Status(status))
                            .map_err(|e| Stopped::HostIo(e.kind()))?;
                    }
                }
            }
        }
        if maximum {
            Err(Stopped::WorkPoll)
        } else {
            Ok(())
        }
    }

    pub fn run_work_timed(
        &mut self,
        position: Position,
        history: &mut SearchHistory,
        controls: Controls,
        limits: Limits,
    ) -> Result<Outcome, Error> {
        self.run_work_timed_entry::<true>(position, history, controls, limits)
    }

    /// Bounded diagnostic capability: fail at the first actual IIO entry.
    /// Default timed/ordinary production continues to allow the complete rule.
    pub fn run_work_timed_without_iio(
        &mut self,
        position: Position,
        history: &mut SearchHistory,
        controls: Controls,
        limits: Limits,
    ) -> Result<Outcome, Error> {
        self.run_work_timed_entry::<false>(position, history, controls, limits)
    }

    fn run_work_timed_entry<const ALLOW_IIO: bool>(
        &mut self,
        position: Position,
        history: &mut SearchHistory,
        controls: Controls,
        limits: Limits,
    ) -> Result<Outcome, Error> {
        let _worker_scope = self.evaluator.full_worker_scope();
        self.clear_geometry_permission();
        let result = self.run_work_timed_inner::<ALLOW_IIO>(position, history, controls, limits);
        self.clear_geometry_permission();
        self.timing = None;
        result
    }

    fn run_work_timed_inner<const ALLOW_IIO: bool>(
        &mut self,
        position: Position,
        history: &mut SearchHistory,
        mut controls: Controls,
        limits: Limits,
    ) -> Result<Outcome, Error> {
        if !(1..=62).contains(&controls.maximum_entered_iterations)
            || controls.randomness > i32::MAX as u32
        {
            return Err(Error::InvalidDepth);
        }
        assert_eq!(history.search_ply(), 0);
        self.ensure_table().map_err(Error::Table)?;
        self.bind_geometry_permission(&position);
        let (root, influence) = self.prepare_root_with_influence(position);
        let checked = movegen::in_check(&position, position.side);
        let mut legal = MoveList::new();
        movegen::generate_legal(&position, &mut legal);
        if legal.len == 0 {
            return Err(Error::NoLegalRoots);
        }
        let initial_candidates = legal.as_slice().to_vec();
        let roots: Vec<RootRow> = initial_candidates
            .iter()
            .enumerate()
            .map(|(id, _)| RootRow {
                id: id as u16,
                score: 0,
                work: 0,
            })
            .collect();
        self.begin_owned_sequence(limits);
        if H::ACTIVE {
            controls.seed = self
                .host
                .acquire_seed(controls.seed, controls.origin)
                .map_err(Error::Host)?;
        }
        self.timing = Some(Clock::new(controls, checked, position, roots.len()));
        if H::ACTIVE {
            self.host.started(controls.seed).map_err(Error::Host)?;
        }
        let mut effects=ActualEffects::<D,H,ALLOW_IIO> {
            search:self,history,root:&root,position:&position,influence:&influence,
            initial_candidates:&initial_candidates,controls,checked,
            iterations:Vec::new(),iteration:None,pv:Vec::new(),captures:CaptureSlot::new(),
        };
        let stop=timed_sequence::drive(roots,controls.maximum_entered_iterations,&mut effects)?
            .ok_or(Error::IterationCapacity)?;
        let ActualEffects{search,iterations,captures,..}=effects;
        let clock=search.timing.take().unwrap();
        let (captured,publications)=captures.into_parts();
        let stats=search.stats;
        let evaluations=search.evaluator.stats;
        Ok(Outcome {
            seed: controls.seed,
            initial_candidates,
            iterations,
            checks: clock.checks,
            stop,
            result: captured,
            publications,
            ledger: clock.ledger,
            stats,
            evaluations,
        })
    }
}


/// These are the former root-local variables, never new Search/Node fields.
struct ActualEffects<'a,const D:bool,H:crate::host::Host,const ALLOW_IIO:bool> {
    search:&'a mut Search<D,H>,
    history:&'a mut SearchHistory,
    root:&'a Node,
    position:&'a Position,
    influence:&'a Influence,
    initial_candidates:&'a [Move],
    controls:Controls,
    checked:bool,
    iterations:Vec<Iteration>,
    iteration:Option<Iteration>,
    pv:Vec<Move>,
    captures:CaptureSlot<Capture>,
}
struct ActualChild {
    node:Node,
    movement:Move,
    window:[i32;2],
    adjustment:i32,
    passes:Vec<Pass>,
}
impl<const D:bool,H:crate::host::Host,const ALLOW_IIO:bool> Effects
    for ActualEffects<'_,D,H,ALLOW_IIO> {
    type Child=ActualChild;
    type Stop=Stop;
    type Interruption=Stopped;
    type Error=Error;
    fn work(&self)->Work {self.search.work()}
    fn set_depth(&mut self,depth:u8) {self.search.timing.as_mut().unwrap().depth=depth;}
    fn begin_iteration_records(&mut self,depth:u8) {
        self.pv=Vec::new();
        self.iteration=Some(Iteration{depth,complete:false,steps:Vec::new()});
    }
    fn begin_candidate(&mut self,_depth:u8,attempt:RootAttempt)->ActualChild {
        self.search.timing.as_mut().unwrap().root_index=attempt.index;
        let movement=self.initial_candidates[usize::from(attempt.id)];
        let adjustment=random_adjustment(self.controls.seed,self.controls.randomness,movement);
        ActualChild{node:self.root.child(&self.search.evaluator.root,movement),movement,
            window:attempt.window,adjustment,passes:Vec::new()}
    }
    fn execute(&mut self,depth:u8,attempt:RootAttempt,child:&mut ActualChild)
        ->Result<AttemptResult<Stopped>,Error> {
        self.history.push(&child.node.position,Some(child.movement));
        let result=self.search.visit_ordinary_impl::<ALLOW_IIO>(
            &mut child.node,self.history,Request{ply:1,depth:depth as i32-1,
                lower:-score_add(attempt.window[1],-child.adjustment),
                upper:-score_add(attempt.window[0],-child.adjustment),previous_extension:0,
                iteration:depth as i32,checked:None},
            Predecessor{position:self.position,influence:self.influence,
                checked:self.checked,movement:Some(child.movement)});
        self.history.pop();
        match result {
            Ok(value)=>Ok(AttemptResult::Returned(score_add(-value,child.adjustment))),
            Err(stop @ (Stopped::WorkPoll|Stopped::HostStop|Stopped::HostAbort))=>
                Ok(AttemptResult::Interrupted(stop)),
            Err(error)=>Err(Error::Stopped(error)),
        }
    }
    fn record_pass(&mut self,_depth:u8,attempt:RootAttempt,value:i32,work:Work,child:&mut ActualChild) {
        if D {child.passes.push(Pass{window:attempt.window,returned_score:value,work});}
    }
    fn adjustment(&mut self,_depth:u8,stage:Stage,previous:i32,best:i32,second:i32,work:Work) {
        self.search.timing.as_mut().unwrap().adjustment(stage,previous,best,second,work);
    }
    fn install_best(&mut self,child:&ActualChild,_completed:RootCompleted) {
        self.pv.clear();self.pv.push(child.movement);
        self.pv.extend_from_slice(&self.search.pv[1][..self.search.pv_len[1]]);
    }
    fn capture(&mut self,depth:u8,completed:RootCompleted,work:Work)->Result<(),Error> {
        let clock=self.search.timing.as_mut().unwrap();
        let word=clock.ledger.observe(work);
        let capture=Capture{depth,root_index:completed.index,score:completed.score,pv:self.pv.clone(),
            search_id:work.charged_search_units,elapsed_cs:clock.adaptive.elapsed_cs(word)};
        let search=&mut *self.search;
        self.captures.capture(depth,capture,|capture| {
            if H::ACTIVE {search.publish_capture(capture).map_err(Error::Host)?;}
            Ok::<(),Error>(())
        })
    }
    fn completed_step(&mut self,child:ActualChild,completed:RootCompleted,work:Work) {
        if D {self.iteration.as_mut().unwrap().steps.push(Step{movement:child.movement,
            window:child.window,adjustment:child.adjustment,score:completed.score,
            best:completed.best,second:completed.second,
            child_pv:self.search.pv[1][..self.search.pv_len[1]].to_vec(),
            pv:self.pv.clone(),work,passes:child.passes});}
    }
    fn root_check(&mut self,depth:u8,completed:RootCompleted,work:Work)->Option<Stop> {
        if !self.search.timing.as_mut().unwrap().check::<D>(Stage::Root,completed.best,completed.second,work) {
            return None;
        }
        self.iterations.push(self.iteration.take().unwrap());
        let clock=self.search.timing.as_ref().unwrap();
        Some(Stop{point:Point::Root,depth,root_index:Some(completed.index),work,
            elapsed_cs:clock.adaptive.elapsed_cs(clock.ledger.last()),pending:None,reason:"root"})
    }
    fn finish_interrupted(&mut self,depth:u8,attempt:RootAttempt,child:&ActualChild,
        reason:Stopped,work:Work)->Stop {
        self.iterations.push(self.iteration.take().unwrap());
        let clock=self.search.timing.as_ref().unwrap();
        Stop{point:Point::Poll,depth,root_index:Some(attempt.index),work,
            elapsed_cs:clock.adaptive.elapsed_cs(clock.ledger.last()),
            pending:Some(Pending{movement:child.movement,window:attempt.window,adjustment:child.adjustment}),
            reason:match reason {Stopped::HostStop=>"host",Stopped::HostAbort=>"abort",_=>"maximum"}}
    }
    fn complete_iteration(&mut self,depth:u8,stage:Stage,previous:i32,best:i32,second:i32,
        work:Work)->Option<Stop> {
        let clock=self.search.timing.as_mut().unwrap();
        clock.check::<D>(stage,best,second,work);
        let terminal=Terminal{depth:depth as i32,selectivity:self.search.config.selectivity,
            root_endgame:self.search.evaluator.root.phase.endgame,
            maximum_depth:self.search.config.maximum_depth,analysis:self.search.config.analysis,
            average_cs:self.controls.average_cs,best,second,previous,start:clock.adaptive.start,
            clock:clock.ledger.last(),iteration_limit:clock.adaptive.limits[0]};
        let mut iteration=self.iteration.take().unwrap();iteration.complete=true;
        self.iterations.push(iteration);
        terminal.reason().map(|reason|Stop{point:Point::Iteration,depth,root_index:None,work,
            elapsed_cs:clock.adaptive.elapsed_cs(clock.ledger.last()),pending:None,reason})
    }
}
