//! Fixed serial census of actual ordinary pre-inventory opportunities.
//!
//! This module owns no Search state. Sampling records real producers; discarded
//! candidates may run one late, domain-guarded shadow generator. No result is
//! installed and no logical search/relation charge is added.
use std::cell::RefCell;
use std::fmt::Write;
use std::time::Instant;

use crate::movegen::{self, MoveList};
use crate::position::Position;
use crate::types::PieceKind;

pub const STRIDE: u64 = 512;
pub const SAMPLE_CAP: usize = 16_384;
pub const TIMER_PROBES: usize = 1024;

thread_local! {
    static CENSUS: RefCell<Option<State>> = const { RefCell::new(None) };
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Counts {
    pub eligible: u64,
    pub full_bound: u64,
    pub cheap_threat_return: u64,
    pub recursive_null_cutoff: u64,
    pub original_inventory: u64,
    pub stopped_unfinished: u64,
    pub null_entered: u64,
    pub null_cutoff: u64,
    pub null_continued: u64,
    pub null_stopped: u64,
    pub null_unfinished: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Exit { FullBound, CheapThreatReturn, RecursiveNullCutoff, OriginalInventory, StoppedUnfinished }
impl Exit {
    fn name(self) -> &'static str {
        match self {
            Self::FullBound => "full_bound", Self::CheapThreatReturn => "cheap_threat_return",
            Self::RecursiveNullCutoff => "recursive_null_cutoff", Self::OriginalInventory => "original_inventory",
            Self::StoppedUnfinished => "stopped_unfinished",
        }
    }
    fn discarded(self) -> bool {
        matches!(self, Self::FullBound|Self::CheapThreatReturn|Self::RecursiveNullCutoff)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NullOutcome { NotEntered, Running, Cutoff, Continued, Stopped, Unfinished }
impl NullOutcome {
    fn name(self) -> &'static str {
        match self {
            Self::NotEntered => "not_entered", Self::Running => "running", Self::Cutoff => "cutoff",
            Self::Continued => "continued", Self::Stopped => "stopped", Self::Unfinished => "unfinished",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ShadowExclusion { Incoherent, KingPopulation, InvalidPosition, OpponentKingChecked }
impl ShadowExclusion {
    fn name(self) -> &'static str {
        match self {
            Self::Incoherent => "coherent_permission_absent", Self::KingPopulation => "king_population",
            Self::InvalidPosition => "invalid_position", Self::OpponentKingChecked => "opponent_king_checked",
        }
    }
}

#[derive(Clone, Debug)]
pub struct Sample {
    pub ordinal: u64,
    pub ply: usize,
    pub depth: i32,
    pub checked: bool,
    pub scratch_some: bool,
    pub coherent: bool,
    pub exit: Exit,
    pub full_interval_ns: Option<u128>,
    pub generation_kind: &'static str,
    pub generation_ns: Option<u128>,
    pub generation_count: Option<usize>,
    pub shadow_exclusion: Option<ShadowExclusion>,
    pub shadow_admission_ns: u128,
    pub null_outcome: NullOutcome,
    pub null_interval_ns: Option<u128>,
    pub setup_span_ns: u128,
    pub finish_span_ns: u128,
}

#[derive(Debug)]
pub struct TimerProbe {
    pub raw_ns: Vec<u128>,
    pub min_ns: u128,
    pub median_ns: u128,
    pub p95_ns: u128,
    pub max_ns: u128,
    pub total_ns: u128,
}

#[derive(Debug)]
pub struct Report {
    pub process_id: u32,
    pub counts: Counts,
    pub sample_requests: u64,
    pub cap_skipped: u64,
    pub samples: Vec<Sample>,
    pub timer_probe: TimerProbe,
    pub enable_span_ns: u128,
    pub reserved_sample_bytes: usize,
}

struct State {
    counts: Counts,
    sample_requests: u64,
    cap_skipped: u64,
    active: usize,
    samples: Vec<Option<Sample>>,
    timer_probe: TimerProbe,
    enable_span_ns: u128,
}

/// Enable once for this calling thread/lifetime. The CLI admits inline mode
/// before calling this function; worker threads never share this state.
pub fn enable() -> Result<(), String> {
    if CENSUS.with(|slot| slot.borrow().is_some()) { return Err("inventory census already enabled".into()); }
    let began = Instant::now();
    let mut raw_ns = Vec::with_capacity(TIMER_PROBES);
    for _ in 0..TIMER_PROBES {
        let first = Instant::now();
        let second = Instant::now();
        raw_ns.push(second.duration_since(first).as_nanos());
    }
    let mut sorted = raw_ns.clone(); sorted.sort_unstable();
    let timer_probe = TimerProbe { min_ns: sorted[0], median_ns: sorted[TIMER_PROBES/2],
        p95_ns: sorted[(TIMER_PROBES-1)*95/100], max_ns: sorted[TIMER_PROBES-1],
        total_ns: raw_ns.iter().sum(), raw_ns };
    let mut state = State { counts: Counts::default(), sample_requests:0, cap_skipped:0,
        active:0, samples:Vec::with_capacity(SAMPLE_CAP), timer_probe, enable_span_ns:0 };
    state.enable_span_ns = began.elapsed().as_nanos();
    CENSUS.with(|slot| *slot.borrow_mut() = Some(state));
    Ok(())
}

pub fn finish() -> Result<Report, String> {
    CENSUS.with(|slot| {
        let mut slot = slot.borrow_mut();
        let Some(state) = slot.as_ref() else { return Err("inventory census is not enabled".into()); };
        if state.active != 0 { return Err("inventory census has active ordinary frames".into()); }
        let state = slot.take().unwrap();
        assert_eq!(state.counts.eligible, state.counts.full_bound+state.counts.cheap_threat_return
            +state.counts.recursive_null_cutoff+state.counts.original_inventory+state.counts.stopped_unfinished);
        assert_eq!(state.counts.null_entered, state.counts.null_cutoff+state.counts.null_continued
            +state.counts.null_stopped+state.counts.null_unfinished);
        let reserved_sample_bytes = state.samples.capacity()*std::mem::size_of::<Option<Sample>>();
        let samples = state.samples.into_iter().map(|sample| sample.expect("unsettled census sample")).collect();
        Ok(Report { process_id:std::process::id(), counts:state.counts, sample_requests:state.sample_requests, cap_skipped:state.cap_skipped,
            samples, timer_probe:state.timer_probe, enable_span_ns:state.enable_span_ns, reserved_sample_bytes })
    })
}

pub fn finish_json() -> Result<String, String> { finish().map(|report|report.json()) }

struct Sampling {
    slot: usize,
    position: Position,
    row: Sample,
    full_start: Option<Instant>,
    null_start: Option<Instant>,
}

/// A frame is classified at its first original inventory generation, or at a
/// preceding return. Later mate/IIO/main-child stops already consumed inventory.
pub(crate) struct Frame {
    active: bool,
    null_outcome: NullOutcome,
    sampling: Option<Sampling>,
}

impl Frame {
    pub(crate) fn launch(position: &Position, coherent: bool, checked: bool, ply: usize,
        depth: i32, scratch_some: bool) -> Self {
        let decision = CENSUS.with(|slot| {
            let mut slot = slot.borrow_mut();
            let state = slot.as_mut()?;
            state.counts.eligible += 1; state.active += 1;
            let ordinal = state.counts.eligible;
            let sample = if ordinal%STRIDE == 0 {
                state.sample_requests += 1;
                if state.samples.len() == SAMPLE_CAP { state.cap_skipped += 1; None }
                else { let index = state.samples.len(); state.samples.push(None); Some(index) }
            } else {None};
            Some((ordinal, sample))
        });
        let Some((ordinal, reserved)) = decision else {
            return Self { active:false, null_outcome:NullOutcome::NotEntered, sampling:None };
        };
        let sampling = reserved.map(|slot| {
            let setup_start = Instant::now();
            let mut sampling = Sampling { slot, position:*position, full_start:None, null_start:None,
                row:Sample { ordinal, ply, depth, checked, scratch_some, coherent,
                    exit:Exit::StoppedUnfinished, full_interval_ns:None, generation_kind:"none",
                    generation_ns:None, generation_count:None, shadow_exclusion:None, shadow_admission_ns:0,
                    null_outcome:NullOutcome::NotEntered, null_interval_ns:None, setup_span_ns:0, finish_span_ns:0 } };
            let full_start = Instant::now();
            sampling.row.setup_span_ns = full_start.duration_since(setup_start).as_nanos();
            sampling.full_start = Some(full_start);
            sampling
        });
        Self { active:true, null_outcome:NullOutcome::NotEntered, sampling }
    }

    /// Immediately after the real FULL returns, before any bounds/null work.
    pub(crate) fn full_done(&mut self) {
        if let Some(sample) = &mut self.sampling {
            if let Some(start) = sample.full_start.take() {
                sample.row.full_interval_ns = Some(start.elapsed().as_nanos());
            }
        }
    }

    pub(crate) fn null_entered(&mut self) {
        if !self.active { return; }
        self.null_outcome = NullOutcome::Running;
        if let Some(sample) = &mut self.sampling { sample.null_start = Some(Instant::now()); }
    }

    pub(crate) fn null_returned(&mut self, cutoff: bool) {
        if !self.active { return; }
        self.null_outcome = if cutoff {NullOutcome::Cutoff} else {NullOutcome::Continued};
        self.finish_null_timer();
    }

    pub(crate) fn null_stopped(&mut self) {
        if !self.active { return; }
        self.null_outcome = NullOutcome::Stopped;
        self.finish_null_timer();
    }

    fn finish_null_timer(&mut self) {
        if let Some(sample) = &mut self.sampling {
            if let Some(start) = sample.null_start.take() {
                sample.row.null_interval_ns = Some(start.elapsed().as_nanos());
            }
        }
    }

    pub(crate) fn inventory_start(&self) -> Option<Instant> {
        self.sampling.as_ref().map(|_|Instant::now())
    }

    pub(crate) fn native_inventory(&mut self, start: Option<Instant>, inventory: &MoveList) {
        if let Some(sample) = &mut self.sampling {
            std::hint::black_box(inventory.as_slice());
            sample.row.generation_kind = "native";
            sample.row.generation_ns = start.map(|start|start.elapsed().as_nanos());
            sample.row.generation_count = Some(inventory.len);
        }
        self.settle(Exit::OriginalInventory);
    }

    pub(crate) fn full_bound(&mut self) { self.settle(Exit::FullBound); }
    pub(crate) fn cheap_threat_return(&mut self) { self.settle(Exit::CheapThreatReturn); }
    pub(crate) fn recursive_null_cutoff(&mut self) { self.settle(Exit::RecursiveNullCutoff); }

    fn settle(&mut self, exit: Exit) {
        if !self.active { return; }
        self.active = false;
        if self.null_outcome == NullOutcome::Running { self.null_outcome = NullOutcome::Unfinished; }
        let finish_started = self.sampling.as_ref().map(|_|Instant::now());
        let mut sampling = self.sampling.take();
        if let Some(sample) = &mut sampling {
            sample.row.exit = exit; sample.row.null_outcome = self.null_outcome;
            if exit.discarded() && sample.row.full_interval_ns.is_some() {
                // Neither validation nor the shadow producer ran ahead of FULL.
                let admission_start = Instant::now();
                let admitted = shadow_domain(&sample.position, sample.row.coherent);
                sample.row.shadow_admission_ns = admission_start.elapsed().as_nanos();
                match admitted {
                    Ok(()) => {
                        let mut local = MoveList::new();
                        let start = Instant::now();
                        movegen::generate_legal(&sample.position, &mut local);
                        std::hint::black_box(local.as_slice());
                        sample.row.generation_ns = Some(start.elapsed().as_nanos());
                        sample.row.generation_count = Some(local.len);
                        sample.row.generation_kind = "discard_shadow";
                    }
                    Err(reason) => {
                        sample.row.generation_kind = "excluded";
                        sample.row.shadow_exclusion = Some(reason);
                    }
                }
            }
        }
        let sampled_slot = sampling.as_ref().map(|sample|sample.slot);
        CENSUS.with(|slot| {
            let mut slot = slot.borrow_mut();
            let state = slot.as_mut().expect("census disabled before frame settled");
            state.active -= 1;
            match exit {
                Exit::FullBound => state.counts.full_bound += 1,
                Exit::CheapThreatReturn => state.counts.cheap_threat_return += 1,
                Exit::RecursiveNullCutoff => state.counts.recursive_null_cutoff += 1,
                Exit::OriginalInventory => state.counts.original_inventory += 1,
                Exit::StoppedUnfinished => state.counts.stopped_unfinished += 1,
            }
            match self.null_outcome {
                NullOutcome::NotEntered => (),
                NullOutcome::Cutoff => {state.counts.null_entered += 1; state.counts.null_cutoff += 1;},
                NullOutcome::Continued => {state.counts.null_entered += 1; state.counts.null_continued += 1;},
                NullOutcome::Stopped => {state.counts.null_entered += 1; state.counts.null_stopped += 1;},
                NullOutcome::Unfinished => {state.counts.null_entered += 1; state.counts.null_unfinished += 1;},
                NullOutcome::Running => unreachable!(),
            }
            if let Some(sample) = sampling { state.samples[sample.slot] = Some(sample.row); }
        });
        if let (Some(index),Some(start)) = (sampled_slot,finish_started) {
            let elapsed = start.elapsed().as_nanos();
            // This second short update is outside the span estimate, as are
            // per-entry TLS counters and full_done/null timer bookkeeping.
            CENSUS.with(|slot| slot.borrow_mut().as_mut().unwrap().samples[index]
                .as_mut().unwrap().finish_span_ns = elapsed);
        }
    }
}

impl Drop for Frame {
    fn drop(&mut self) { self.settle(Exit::StoppedUnfinished); }
}

fn shadow_domain(position: &Position, coherent: bool) -> Result<(), ShadowExclusion> {
    if !coherent { return Err(ShadowExclusion::Incoherent); }
    if position.counts.iter().any(|counts|counts[PieceKind::King.index()] != 1) {
        return Err(ShadowExclusion::KingPopulation);
    }
    if position.validate().is_err() { return Err(ShadowExclusion::InvalidPosition); }
    if movegen::in_check(position,position.side.opponent()) { return Err(ShadowExclusion::OpponentKingChecked); }
    Ok(())
}

fn option_number<T: std::fmt::Display>(value: Option<T>) -> String {
    value.map_or_else(||"null".into(), |value|value.to_string())
}

impl Report {
    pub fn json(&self) -> String {
        let c = self.counts; let t = &self.timer_probe;
        let shadow_ns: u128 = self.samples.iter().filter(|sample|sample.generation_kind=="discard_shadow")
            .filter_map(|sample|sample.generation_ns).sum();
        let admission_ns: u128 = self.samples.iter().map(|sample|sample.shadow_admission_ns).sum();
        let span_ns: u128 = self.samples.iter().map(|sample|sample.setup_span_ns+sample.finish_span_ns).sum();
        let mut output = format!(concat!("{{\"schema\":\"rook2-inventory-census-v1\",\"processId\":{},\"stride\":{},\"sample_cap\":{},",
            "\"sample_requests\":{},\"cap_skipped\":{},\"samples_count\":{},\"enable_span_ns\":{},\"reserved_sample_bytes\":{},",
            "\"shadow_generation_ns\":{},\"shadow_admission_ns\":{},\"sampling_span_estimate_ns\":{},",
            "\"counts\":{{\"eligible\":{},\"full_bound\":{},\"cheap_threat_return\":{},\"recursive_null_cutoff\":{},",
            "\"original_inventory\":{},\"stopped_unfinished\":{},\"null_entered\":{},\"null_cutoff\":{},",
            "\"null_continued\":{},\"null_stopped\":{},\"null_unfinished\":{}}},",
            "\"timer_probe\":{{\"count\":{},\"min_ns\":{},\"median_ns\":{},\"p95_ns\":{},\"max_ns\":{},\"total_ns\":{},\"raw_ns\":["),
            self.process_id,STRIDE,SAMPLE_CAP,self.sample_requests,self.cap_skipped,self.samples.len(),self.enable_span_ns,
            self.reserved_sample_bytes,shadow_ns,admission_ns,span_ns.saturating_sub(shadow_ns+admission_ns),
            c.eligible,c.full_bound,c.cheap_threat_return,c.recursive_null_cutoff,c.original_inventory,
            c.stopped_unfinished,c.null_entered,c.null_cutoff,c.null_continued,c.null_stopped,c.null_unfinished,
            t.raw_ns.len(),t.min_ns,t.median_ns,t.p95_ns,t.max_ns,t.total_ns);
        for (index,ns) in t.raw_ns.iter().enumerate() { if index!=0 {output.push(',');} write!(output,"{ns}").unwrap(); }
        output.push_str("]},\"samples\":[");
        for (index,sample) in self.samples.iter().enumerate() {
            if index!=0 {output.push(',');}
            let exclusion = sample.shadow_exclusion.map_or_else(||"null".into(),|value|format!("\"{}\"",value.name()));
            write!(output,concat!("{{\"ordinal\":{},\"ply\":{},\"depth\":{},\"checked\":{},\"scratch_some\":{},\"coherent\":{},",
                "\"exit\":\"{}\",\"full_interval_ns\":{},\"generation_kind\":\"{}\",\"generation_ns\":{},\"generation_count\":{},",
                "\"shadow_exclusion\":{},\"shadow_admission_ns\":{},\"null_outcome\":\"{}\",\"null_interval_ns\":{},",
                "\"setup_span_ns\":{},\"finish_span_ns\":{}}}"),sample.ordinal,sample.ply,sample.depth,sample.checked,
                sample.scratch_some,sample.coherent,sample.exit.name(),option_number(sample.full_interval_ns),sample.generation_kind,
                option_number(sample.generation_ns),option_number(sample.generation_count),exclusion,sample.shadow_admission_ns,
                sample.null_outcome.name(),option_number(sample.null_interval_ns),sample.setup_span_ns,sample.finish_span_ns).unwrap();
        }
        output.push_str(concat!("],\"limitations\":\"Serial instrumented census, not engine performance or parallel speedup. ",
            "FULL interval starts after FAST and includes Influence only when scratch was None. Null intervals are separate. ",
            "Late discarded shadows can warm later work. Sampling span estimate prices setup/finish spans less measured shadow/domain spans; ",
            "per-entry counter/TLS cost and intermediate timing updates remain unisolated. No timer correction is applied.\"}"));
        output
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::engine::Search;
    use crate::history::SearchHistory;
    use crate::quiescence::{Limits, Stopped};
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn position() -> Position { Position::from_fen(START).unwrap() }

    fn unsampled_inventory(count: usize) {
        let position = position(); let inventory = MoveList::new();
        for _ in 0..count {
            let mut frame = Frame::launch(&position,true,false,1,2,false);
            frame.full_done();
            let start = frame.inventory_start();
            frame.native_inventory(start,&inventory);
        }
    }

    #[test]
    fn fixed_stride_nested_frames_exit_partition_and_null_overlay() {
        enable().unwrap(); unsampled_inventory(511);
        let position = position();
        let mut sampled = Frame::launch(&position,true,false,3,4,true);
        assert!(sampled.sampling.is_some()); sampled.full_done(); sampled.null_entered();
        let mut child = Frame::launch(&position,true,true,4,1,false);
        child.full_done(); child.cheap_threat_return();
        sampled.null_returned(false);
        let start = sampled.inventory_start(); let mut inventory = MoveList::new();
        movegen::generate_legal(&position,&mut inventory);
        sampled.native_inventory(start,&inventory);
        let mut full = Frame::launch(&position,true,false,2,1,false); full.full_done(); full.full_bound();
        let mut cheap = Frame::launch(&position,true,false,2,1,false); cheap.full_done(); cheap.cheap_threat_return();
        let mut cutoff = Frame::launch(&position,true,false,2,3,false);
        cutoff.full_done(); cutoff.null_entered(); cutoff.null_returned(true); cutoff.recursive_null_cutoff();
        let mut stopped = Frame::launch(&position,true,false,2,3,false);
        stopped.full_done(); stopped.null_entered(); stopped.null_stopped(); drop(stopped);
        let mut unfinished = Frame::launch(&position,true,false,2,3,false);
        unfinished.full_done(); unfinished.null_entered(); drop(unfinished);
        let report = finish().unwrap();
        assert_eq!(report.counts,Counts { eligible:518, original_inventory:512, full_bound:1,
            cheap_threat_return:2, recursive_null_cutoff:1, stopped_unfinished:2,
            null_entered:4, null_cutoff:1, null_continued:1, null_stopped:1, null_unfinished:1 });
        assert_eq!((report.sample_requests,report.cap_skipped,report.samples.len()),(1,0,1));
        let row = &report.samples[0];
        assert_eq!(row.ordinal,512); assert!(row.scratch_some);
        assert_eq!(row.generation_kind,"native"); assert_eq!(row.generation_count,Some(20));
        assert!(row.full_interval_ns.is_some() && row.generation_ns.is_some() && row.null_interval_ns.is_some());
        assert_eq!(row.null_outcome,NullOutcome::Continued);
        assert_eq!(report.timer_probe.raw_ns.len(),1024);
        assert_eq!(report.timer_probe.total_ns,report.timer_probe.raw_ns.iter().sum());
    }

    #[test]
    fn late_shadow_is_separate_and_stopped_sample_never_generates() {
        enable().unwrap(); unsampled_inventory(511);
        let position = position();
        let mut frame = Frame::launch(&position,true,false,1,2,false);
        assert!(frame.sampling.as_ref().unwrap().row.generation_ns.is_none());
        frame.full_done(); frame.full_bound();
        unsampled_inventory(511);
        let mut stopped = Frame::launch(&position,true,false,1,2,false);
        stopped.full_done(); stopped.null_entered(); stopped.null_stopped(); drop(stopped);
        let report = finish().unwrap();
        assert_eq!(report.samples.len(),2);
        assert_eq!(report.samples[0].generation_kind,"discard_shadow");
        assert_eq!(report.samples[0].generation_count,Some(20));
        assert_eq!(report.samples[0].exit,Exit::FullBound);
        assert_eq!(report.samples[1].generation_kind,"none");
        assert!(report.samples[1].generation_ns.is_none());
        assert_eq!(report.samples[1].shadow_admission_ns,0);
        assert_eq!(report.samples[1].exit,Exit::StoppedUnfinished);
    }

    #[test]
    fn sample_cap_reservation_and_active_finish_are_bounded() {
        enable().unwrap();
        // Cold capacity fixture: do not execute millions of ordinary calls to
        // exercise one Vec-length boundary. No synthetic data is reported.
        CENSUS.with(|slot| {
            let mut slot=slot.borrow_mut(); let state=slot.as_mut().unwrap();
            state.samples.resize_with(SAMPLE_CAP,||None);
            state.counts.eligible=STRIDE-1;
        });
        let position=position(); let inventory=MoveList::new();
        let mut frame=Frame::launch(&position,true,false,1,2,false);
        assert!(frame.sampling.is_none()); assert!(finish().is_err());
        frame.full_done(); frame.native_inventory(None,&inventory);
        CENSUS.with(|slot| {
            let mut slot=slot.borrow_mut(); let state=slot.take().unwrap();
            assert_eq!(state.samples.len(),SAMPLE_CAP);
            assert_eq!(state.cap_skipped,1); assert_eq!(state.sample_requests,1); assert_eq!(state.active,0);
        });
    }

    #[test]
    fn shadow_domain_rejects_exceptional_inputs_before_generation() {
        let position=position(); assert_eq!(shadow_domain(&position,true),Ok(()));
        assert_eq!(shadow_domain(&position,false),Err(ShadowExclusion::Incoherent));
        let mut no_king=position; no_king.counts[0][PieceKind::King.index()]=0;
        assert_eq!(shadow_domain(&no_king,true),Err(ShadowExclusion::KingPopulation));
        let mut invalid=position; invalid.primary^=1;
        assert_eq!(shadow_domain(&invalid,true),Err(ShadowExclusion::InvalidPosition));
        let checked_enemy=Position::from_fen("4k3/8/8/8/8/8/4R3/4K3 w - - 0 1").unwrap();
        assert_eq!(shadow_domain(&checked_enemy,true),Err(ShadowExclusion::OpponentKingChecked));
        let checked_current=Position::from_fen("4k3/8/8/8/8/8/4r3/4K3 w - - 0 1").unwrap();
        assert_eq!(shadow_domain(&checked_current,true),Ok(()));
    }

    #[test]
    fn native_search_census_preserves_scores_pv_stats_and_semantic_work() {
        fn verify<const D:bool>(depth:u8) {
            let position=position();
            let mut baseline=Search::<D>::new(&position); baseline.config.tts_bytes=65536;
            let mut observed=Search::<D>::new(&position); observed.config.tts_bytes=65536;
            let (mut ah,mut bh)=(SearchHistory::new(&position),SearchHistory::new(&position));
            let expected=baseline.run_iterations(position,&mut ah,depth,Limits{nodes:Some(100000)}).unwrap();
            enable().unwrap();
            let actual=observed.run_iterations(position,&mut bh,depth,Limits{nodes:Some(100000)}).unwrap();
            let report=finish().unwrap();
            assert_eq!((actual.score,actual.pv,actual.work,actual.stats,actual.evaluations),
                (expected.score,expected.pv,expected.work,expected.stats,expected.evaluations));
            assert_eq!(actual.iterations.len(),expected.iterations.len());
            for (a,b) in actual.iterations.iter().zip(&expected.iterations) {
                assert_eq!((&a.candidates,&a.steps,a.score,&a.pv,a.work),(&b.candidates,&b.steps,b.score,&b.pv,b.work));
            }
            assert!(report.counts.eligible>0);
            if D {assert!(report.counts.eligible<=observed.stats.ordinary_nodes);}
            assert_eq!((ah.search_ply(),bh.search_ply()),(0,0));
            #[cfg(feature="branch-transactions")]
            assert!(observed.research_eq(&baseline));
        }
        verify::<true>(4); verify::<false>(2);
    }

    #[test]
    fn quiescence_and_prelaunch_node_stop_do_not_enter_denominator() {
        let position=position(); let mut search=Search::<true>::new(&position);
        search.config.tts_bytes=65536; let mut history=SearchHistory::new(&position);
        enable().unwrap(); search.run_iterations(position,&mut history,1,Limits::default()).unwrap();
        assert_eq!(finish().unwrap().counts.eligible,0);
        enable().unwrap();
        assert!(matches!(search.run_iterations(position,&mut history,2,Limits{nodes:Some(0)}),
            Err(crate::ordinary::Error::Stopped(Stopped::NodeLimit(0)))));
        assert_eq!(finish().unwrap().counts.eligible,0);
    }
}
