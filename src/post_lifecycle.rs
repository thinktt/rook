//! Owned qualifying captures and publication/finish policy, independent of chess.
use crate::output::{captured_fields, Fields};
use std::convert::Infallible;

/// Retains the supplied owned payload; Clone follows P's own ownership contract.
/// Production captures and controlled label vectors own their complete PV buffers.
pub struct CaptureSlot<P> {
    latest: Option<P>,
    eligible: Vec<P>,
}
impl<P> CaptureSlot<P> {
    pub fn new() -> Self { Self { latest: None, eligible: Vec::new() } }
    pub fn latest(&self) -> Option<&P> { self.latest.as_ref() }
    pub fn eligible(&self) -> &[P] { &self.eligible }
    pub fn into_parts(self) -> (Option<P>, Vec<P>) { (self.latest, self.eligible) }
}
impl<P: Clone> CaptureSlot<P> {
    /// History records eligibility before a fallible live publication. A failure
    /// leaves the previous retained result intact and must propagate, not finish.
    /// No clock read or payload-empty/depth-monotonicity inference occurs here.
    pub fn capture<E>(
        &mut self, depth: u8, payload: P,
        publish: impl FnOnce(&P) -> Result<(), E>,
    ) -> Result<(), E> {
        if depth >= 3 {
            self.eligible.push(payload.clone());
            publish(&payload)?;
        }
        self.latest = Some(payload);
        Ok(())
    }
}

pub enum FinalReport<'a, P> {
    Suppressed,
    Retained(&'a P),
    Fallback,
}
/// Successful-finish report choice only. Abort, move selection, fallback
/// rendering and actual live publication success remain with their native owners.
pub fn final_report<P>(
    enabled: bool, already_published: bool, latest: Option<&P>,
) -> FinalReport<'_, P> {
    if !enabled || already_published { FinalReport::Suppressed }
    else if let Some(latest) = latest { FinalReport::Retained(latest) }
    else { FinalReport::Fallback }
}

pub struct ControlledCapture<P> {
    pub depth: u8,
    pub remainder: i32,
    pub ranking_score: i32,
    pub search_id: u64,
    pub payload: P,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ControlledReport<P> {
    pub fields: Fields,
    pub payload: P,
}
pub struct ControlledOutcome<P> {
    pub after_each: Vec<Vec<ControlledReport<P>>>,
    pub on_finish: Vec<ControlledReport<P>>,
    pub clock_reads: u64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NoCapture;

/// Supplied qualifying events use the same slot and finish policy as production.
/// Each event calls the explicit capture-clock source once. Start is supplied;
/// new/retention/finish make no observations. JSON/labels and finishClock are absent.
pub fn controlled<P: Clone>(
    start: u32, draw: i32,
    events: impl IntoIterator<Item = ControlledCapture<P>>,
    mut observe_capture: impl FnMut() -> u32,
) -> Result<ControlledOutcome<P>, NoCapture> {
    let mut slot = CaptureSlot::new();
    let mut after_each = Vec::new();
    let mut clock_reads = 0;
    for event in events {
        let clock = observe_capture();
        clock_reads += 1;
        let report = ControlledReport {
            fields: captured_fields(event.depth, event.remainder, event.ranking_score,
                draw, event.search_id, clock.wrapping_sub(start)),
            payload: event.payload,
        };
        let mut emitted = Vec::new();
        let result: Result<(), Infallible> = slot.capture(event.depth, report, |captured| {
            emitted.push(captured.clone()); Ok(())
        });
        match result { Ok(()) => {}, Err(impossible) => match impossible {} }
        after_each.push(emitted);
    }
    let on_finish = match final_report(true, !slot.eligible().is_empty(), slot.latest()) {
        FinalReport::Suppressed => Vec::new(),
        FinalReport::Retained(report) => vec![report.clone()],
        FinalReport::Fallback => return Err(NoCapture),
    };
    Ok(ControlledOutcome { after_each, on_finish, clock_reads })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::{Cell, RefCell};
    use std::rc::Rc;

    #[test]
    fn owned_snapshots_keep_shorter_empty_and_repeated_payloads() {
        let mut input = vec!["first".to_owned(), "second".to_owned()];
        let mut slot = CaptureSlot::new();
        slot.capture(3, input.clone(), |_| Ok::<(), ()>(())).unwrap();
        input[0].clear();
        assert_eq!(slot.eligible()[0], ["first", "second"]);
        slot.capture(3, vec!["first".to_owned(), "second".to_owned()],
            |_| Ok::<(), ()>(())).unwrap();
        assert_eq!(slot.eligible().len(), 2);
        slot.capture(2, vec!["short".to_owned()], |_| -> Result<(), ()> {
            panic!("shallow capture must not publish")
        }).unwrap();
        assert_eq!(slot.latest().unwrap(), &["short"]);
        slot.capture(1, Vec::new(), |_| -> Result<(), ()> {
            panic!("empty shallow capture must not publish")
        }).unwrap();
        assert!(matches!(final_report(true, false, slot.latest()),
            FinalReport::Retained(pv) if pv.is_empty()));
        let (latest, eligible) = slot.into_parts();
        assert!(latest.unwrap().is_empty());
        assert_eq!(eligible, vec![vec!["first", "second"], vec!["first", "second"]]);
    }

    #[test]
    fn publication_observes_clone_before_replacement_and_failure_retains_old_latest() {
        struct Tracked { name: &'static str, log: Rc<RefCell<Vec<String>>> }
        impl Clone for Tracked {
            fn clone(&self) -> Self {
                self.log.borrow_mut().push(format!("clone:{}", self.name));
                Self { name: self.name, log: self.log.clone() }
            }
        }
        impl Drop for Tracked {
            fn drop(&mut self) { self.log.borrow_mut().push(format!("drop:{}", self.name)); }
        }
        let log = Rc::new(RefCell::new(Vec::new()));
        let mut slot = CaptureSlot::new();
        slot.capture(1, Tracked { name: "old", log: log.clone() },
            |_| Ok::<(), ()>(())).unwrap();
        slot.capture(3, Tracked { name: "new", log: log.clone() }, |payload| {
            assert_eq!(payload.name, "new");
            log.borrow_mut().push("publish:new".to_owned());
            Ok::<(), ()>(())
        }).unwrap();
        assert_eq!(*log.borrow(), ["clone:new", "publish:new", "drop:old"]);
        log.borrow_mut().clear();
        assert_eq!(slot.capture(3, Tracked { name: "failed", log: log.clone() }, |_| {
            log.borrow_mut().push("publish:failed".to_owned()); Err("host")
        }), Err("host"));
        assert_eq!(*log.borrow(), ["clone:failed", "publish:failed", "drop:failed"]);
        assert_eq!(slot.latest().unwrap().name, "new");
        assert_eq!(slot.eligible().iter().map(|p| p.name).collect::<Vec<_>>(),
            ["new", "failed"]);
        // A failed caller propagates its error; it must not request a final report.
    }

    fn event(depth: u8, score: i32, payload: &[&str]) -> ControlledCapture<Vec<String>> {
        ControlledCapture { depth, remainder: -1, ranking_score: score, search_id: 17,
            payload: payload.iter().map(|s| (*s).to_owned()).collect() }
    }

    #[test]
    fn controlled_repeats_publish_independently_and_shallow_tail_does_not_finish_again() {
        let reads = Cell::new(0);
        let mut clocks = [1, 1, 4].into_iter();
        let outcome = controlled(u32::MAX - 2, 25,
            [event(3, 100, &["0-O", "next"]), event(3, 100, &["0-O", "next"]),
             event(1, -100, &[])], || {
                reads.set(reads.get() + 1); clocks.next().unwrap()
            }).unwrap();
        assert_eq!(reads.get(), 3);
        assert_eq!(outcome.clock_reads, 3);
        assert_eq!(outcome.after_each.iter().map(Vec::len).collect::<Vec<_>>(), [1, 1, 0]);
        assert_eq!(outcome.after_each[0], outcome.after_each[1]);
        assert_eq!(outcome.after_each[0][0].fields,
            Fields { depth_token: 2999, evaluation: 75, centiseconds: 4, search_id: 17 });
        assert!(outcome.on_finish.is_empty());
        assert_eq!(clocks.next(), None);
    }

    #[test]
    fn controlled_empty_and_shallow_finish_observe_no_start_or_finish_clock() {
        let reads = Cell::new(0);
        assert!(matches!(controlled::<Vec<String>>(0, 0, [], || {
            reads.set(reads.get() + 1); 0
        }), Err(NoCapture)));
        assert_eq!(reads.get(), 0);
        let outcome = controlled(0, -10000, [event(2, 8999, &[])], || {
            reads.set(reads.get() + 1); 0x8000_0001
        }).unwrap();
        assert_eq!(reads.get(), 1);
        assert_eq!(outcome.clock_reads, 1);
        assert!(outcome.after_each[0].is_empty());
        assert_eq!(outcome.on_finish.len(), 1);
        assert!(outcome.on_finish[0].payload.is_empty());
        assert_eq!(outcome.on_finish[0].fields,
            Fields { depth_token: 1999, evaluation: 7900,
                centiseconds: i32::MIN + 1, search_id: 17 });
        let mate = controlled(0, 10000, [event(1, 9000, &["mate"])], || 0).unwrap();
        assert_eq!(mate.on_finish[0].fields.evaluation, 9000);
    }
}
