//! Activity -> Shelter worker for confirmed FULL calls.
//!
//! Packet and result slots are reusable owned storage, never borrowed from a
//! caller's stack. Successful dispatch/complete allocate no memory or threads.
//! The worker spins only inside an owned active search/call scope. Outside those
//! scopes it acknowledges empty transport slots and sleeps on a condition.
//! Scheduling delays never cause an engine wall-time abort. Affinity is inherited
//! from the creator; controlled benchmark placement belongs to its supervisor.

use crate::activity::{self, Activity};
use crate::influence::Influence;
use crate::position::Position;
use crate::shelter::{self, Shelter};
use std::hint::spin_loop;
use std::sync::atomic::{AtomicBool, AtomicU8, AtomicUsize, Ordering};
use std::sync::{Arc, Condvar, Mutex, MutexGuard};
use std::thread::{self, JoinHandle};

const STARTING: u8 = 0;
const IDLE: u8 = 1;
const REQUESTED: u8 = 2;
const COMPLETE: u8 = 3;
const FAILED: u8 = 4;
const STOPPED: u8 = 5;
const PARKED: u8 = 6;
const COMPLETION_SPINS: usize = 4096;

#[derive(Clone, Copy)]
pub(crate) struct ActivityShelter {
    pub activity: Activity,
    pub shelter: Shelter,
}

/// One shared numerical chain for both budgets; all prescribed rounding and
/// relation charging remains inside the existing component kernels.
#[inline]
pub(crate) fn compute(
    position: &Position,
    influence: &Influence,
    material: i32,
    mobility_weights: [i32; 2],
    shelter_weights: [i32; 2],
) -> ActivityShelter {
    let activity = activity::compute(position, influence, material, mobility_weights);
    let shelter = shelter::compute(
        position,
        influence,
        activity.pressure,
        material,
        shelter_weights,
    );
    ActivityShelter { activity, shelter }
}

struct Packet {
    position: Position,
    influence: Influence,
    material: i32,
    mobility_weights: [i32; 2],
    shelter_weights: [i32; 2],
}

#[derive(Default)]
struct Slots {
    packet: Option<Packet>,
    output: Option<ActivityShelter>,
    failure: Option<String>,
    completion_waiting: bool,
}

struct Shared {
    state: AtomicU8,
    stop: AtomicBool,
    active_scopes: AtomicUsize,
    control: Mutex<Control>,
    wake: Condvar,
    slots: Mutex<Slots>,
    completed: Condvar,
    #[cfg(test)]
    test_gate: Mutex<TestGate>,
    #[cfg(test)]
    test_wake: Condvar,
}

#[cfg(test)]
#[derive(Default)]
struct TestGate {
    blocked: bool,
    entered: bool,
    fail: bool,
}

#[derive(Default)]
struct Control {
    scopes: usize,
    parking: bool,
}

/// No evaluator or Search borrow survives activation. The final guard waits
/// for the helper to discard any abandoned packet/output and acknowledge sleep.
pub(crate) struct ActiveScope {
    shared: Arc<Shared>,
    armed: bool,
}

impl ActiveScope {
    pub(crate) fn finish(mut self) -> Result<(), String> {
        self.armed = false;
        release_scope(&self.shared)
    }
}

impl Drop for ActiveScope {
    fn drop(&mut self) {
        if self.armed {
            if let Err(error) = release_scope(&self.shared) {
                if thread::panicking() {
                    eprintln!("evaluator worker scope close failed during unwind: {error}");
                } else {
                    panic!("evaluator worker scope close failed: {error}");
                }
            }
        }
    }
}

pub(crate) struct ActivityShelterWorker {
    shared: Arc<Shared>,
    thread: Option<JoinHandle<()>>,
    close_error_reported: bool,
}

impl ActivityShelterWorker {
    pub(crate) fn start() -> Result<Self, String> {
        Self::start_with(run_active)
    }

    fn start_with(entry: fn(&Shared) -> Result<(), String>) -> Result<Self, String> {
        let shared = Arc::new(Shared {
            state: AtomicU8::new(STARTING),
            stop: AtomicBool::new(false),
            active_scopes: AtomicUsize::new(0),
            control: Mutex::new(Control::default()),
            wake: Condvar::new(),
            slots: Mutex::new(Slots::default()),
            completed: Condvar::new(),
            #[cfg(test)]
            test_gate: Mutex::new(TestGate::default()),
            #[cfg(test)]
            test_wake: Condvar::new(),
        });
        let worker_shared = Arc::clone(&shared);
        let thread = thread::Builder::new()
            .name("rook2-eval-research".into())
            .spawn(move || {
                let result = std::panic::catch_unwind(|| entry(&worker_shared));
                let failure = match result {
                    Ok(Ok(())) => None,
                    Ok(Err(error)) => Some(error),
                    Err(_) => Some("Activity/Shelter worker panicked".into()),
                };
                publish_terminal(&worker_shared, failure);
            })
            .map_err(|error| format!("cannot start Activity/Shelter worker: {error}"))?;
        let mut worker = Self {
            shared,
            thread: Some(thread),
            close_error_reported: false,
        };
        let mut control = control_lock(&worker.shared);
        while worker.shared.state.load(Ordering::Acquire) == STARTING {
            control = wait_control(&worker.shared, control);
        }
        let state = worker.shared.state.load(Ordering::Acquire);
        drop(control);
        if state == PARKED {
            Ok(worker)
        } else {
            let failure = worker.failure();
            let _ = worker.shutdown();
            Err(failure)
        }
    }

    pub(crate) fn start_active_scope(&self) -> Result<ActiveScope, String> {
        let mut control = control_lock(&self.shared);
        while control.parking && !terminal(&self.shared) {
            control = wait_control(&self.shared, control);
        }
        if terminal(&self.shared) {
            return Err(self.failure());
        }
        let first = control.scopes == 0;
        control.scopes = control.scopes.checked_add(1).expect("worker active scope count exhausted");
        self.shared.active_scopes.store(control.scopes, Ordering::Release);
        if first {
            // A prior closing guard may still be an acknowledgment waiter on
            // this condition. Wake all so activation cannot wake only it.
            self.shared.wake.notify_all();
            while self.shared.state.load(Ordering::Acquire) == PARKED && !terminal(&self.shared) {
                control = wait_control(&self.shared, control);
            }
            if self.shared.state.load(Ordering::Acquire) != IDLE {
                control.scopes -= 1;
                self.shared.active_scopes.store(control.scopes, Ordering::Release);
                drop(control);
                return Err(self.failure());
            }
        }
        drop(control);
        Ok(ActiveScope { shared: Arc::clone(&self.shared), armed: true })
    }

    /// Evaluator FULL calls have one owning coordinator. An existing outer
    /// scope encloses this whole call, so its fast path needs no lifecycle lock
    /// or Arc clone. A standalone call gets an owned wake/park guard instead.
    pub(crate) fn start_call_scope(&self) -> Result<Option<ActiveScope>, String> {
        if self.shared.active_scopes.load(Ordering::Acquire) != 0 {
            Ok(None)
        } else {
            self.start_active_scope().map(Some)
        }
    }

    #[cfg(test)]
    pub(crate) fn is_parked(&self) -> bool {
        self.shared.state.load(Ordering::Acquire) == PARKED
            && self.shared.active_scopes.load(Ordering::Acquire) == 0
    }

    pub(crate) fn dispatch(
        &mut self,
        position: &Position,
        influence: &Influence,
        material: i32,
        mobility_weights: [i32; 2],
        shelter_weights: [i32; 2],
    ) -> Result<(), String> {
        if self.shared.active_scopes.load(Ordering::Acquire) == 0
            || self.shared.state.load(Ordering::Acquire) != IDLE {
            return Err(self.failure());
        }
        {
            let mut slots = self
                .shared
                .slots
                .lock()
                .map_err(|_| "worker slot poisoned")?;
            debug_assert!(slots.packet.is_none() && slots.output.is_none());
            slots.packet = Some(Packet {
                position: *position,
                influence: *influence,
                material,
                mobility_weights,
                shelter_weights,
            });
        }
        self.shared.state.store(REQUESTED, Ordering::Release);
        Ok(())
    }

    pub(crate) fn complete(&mut self) -> Result<ActivityShelter, String> {
        let mut slots = completion_slots(&self.shared)?;
        let output = slots.output.take().ok_or("worker completed without an output")?;
        self.shared.state.store(IDLE, Ordering::Release);
        Ok(output)
    }

    pub(crate) fn check_running(&self) -> Result<(), String> {
        if terminal(&self.shared) { Err(self.failure()) } else { Ok(()) }
    }

    fn failure(&self) -> String {
        self.shared
            .slots
            .lock()
            .unwrap_or_else(|e| e.into_inner())
            .failure
            .clone()
            .unwrap_or_else(|| "Activity/Shelter worker entered an invalid state".into())
    }

    pub(crate) fn shutdown(&mut self) -> Result<(), String> {
        if self.thread.is_none() {
            if self.shared.state.load(Ordering::Acquire) == FAILED {
                self.close_error_reported = true;
                return Err(self.failure());
            }
            return Ok(());
        }
        // This also covers unwinding after dispatch: finish or discard the
        // pending owned packet, then terminate before its storage is released.
        {
            let mut control = control_lock(&self.shared);
            self.shared.stop.store(true, Ordering::Release);
            self.shared.active_scopes.store(0, Ordering::Release);
            control.scopes = 0;
            control.parking = false;
            self.shared.wake.notify_all();
        }
        let handle = self.thread.take().unwrap();
        // No worker/control/slot lock may remain held across this join. The
        // external owner may impose a deadline; the engine does not infer a
        // terminal error merely from how long the helper was unscheduled.
        if handle.join().is_err() {
            publish_terminal(&self.shared, Some("Activity/Shelter worker exited with an uncaught panic".into()));
            self.close_error_reported = true;
            return Err("Activity/Shelter worker exited with an uncaught panic".into());
        }
        {
            let mut slots = self.shared.slots.lock().unwrap_or_else(|error| error.into_inner());
            slots.packet = None;
            slots.output = None;
        }
        if self.shared.state.load(Ordering::Acquire) == FAILED {
            self.close_error_reported = true;
            return Err(self.failure());
        }
        Ok(())
    }
}

impl Drop for ActivityShelterWorker {
    fn drop(&mut self) {
        // shutdown keeps terminal failure sticky, including after join. An
        // explicitly returned close Err discharges duplicate destructor reports.
        let reported = self.close_error_reported;
        if let Err(error) = self.shutdown() {
            if reported { return; }
            if thread::panicking() {
                eprintln!("evaluator worker shutdown failed during unwind: {error}");
            } else {
                panic!("evaluator worker shutdown failed: {error}");
            }
        }
    }
}

fn run_active(shared: &Shared) -> Result<(), String> {
    park(shared)?;
    while !shared.stop.load(Ordering::Acquire) {
        if shared.state.load(Ordering::Acquire) != REQUESTED {
            if shared.active_scopes.load(Ordering::Acquire) == 0 {
                park(shared)?;
                continue;
            }
            spin_loop();
            continue;
        }
        let packet = shared
            .slots
            .lock()
            .map_err(|_| "worker slot poisoned")?
            .packet
            .take()
            .ok_or("worker request has no packet")?;
        #[cfg(test)]
        test_gate(shared)?;
        let output = compute(
            &packet.position,
            &packet.influence,
            packet.material,
            packet.mobility_weights,
            packet.shelter_weights,
        );
        let notify = {
            let mut slots = shared.slots.lock().map_err(|_| "worker slot poisoned")?;
            slots.output = Some(output);
            shared.state.store(COMPLETE, Ordering::Release);
            slots.completion_waiting
        };
        // Registering a blocked waiter and publishing its predicate use Slots.
        // The usual spin completion adds no condition notification call.
        if notify { shared.completed.notify_all(); }
    }
    Ok(())
}

fn control_lock(shared: &Shared) -> MutexGuard<'_, Control> {
    shared.control.lock().unwrap_or_else(|error| error.into_inner())
}

/// Slots guards completion predicates. Nothing holding this guard may acquire
/// Control: terminal/lifecycle code consistently locks Control before Slots.
fn completion_slots(shared: &Shared) -> Result<MutexGuard<'_, Slots>, String> {
    for _ in 0..COMPLETION_SPINS {
        if shared.state.load(Ordering::Acquire) != REQUESTED { break; }
        spin_loop();
    }
    let mut slots = shared.slots.lock().map_err(|_| "worker slot poisoned")?;
    while shared.state.load(Ordering::Acquire) == REQUESTED {
        slots.completion_waiting = true;
        slots = shared.completed.wait(slots).map_err(|_| "worker slot poisoned")?;
    }
    slots.completion_waiting = false;
    if shared.state.load(Ordering::Acquire) != COMPLETE {
        return Err(slots.failure.clone().unwrap_or_else(|| "Activity/Shelter worker entered an invalid state".into()));
    }
    Ok(slots)
}

fn publish_terminal(shared: &Shared, failure: Option<String>) {
    let mut control = control_lock(shared);
    let mut slots = shared.slots.lock().unwrap_or_else(|error| error.into_inner());
    let state = if let Some(error) = failure {
        slots.failure = Some(error);
        FAILED
    } else { STOPPED };
    shared.state.store(state, Ordering::Release);
    control.parking = false;
    // Both predicate families include terminal state, and that transition is
    // published with both associated mutexes held. Neither wake can be lost.
    shared.completed.notify_all();
    shared.wake.notify_all();
}

fn terminal(shared: &Shared) -> bool {
    shared.stop.load(Ordering::Acquire)
        || matches!(shared.state.load(Ordering::Acquire), FAILED | STOPPED)
}

fn release_scope(shared: &Shared) -> Result<(), String> {
    let mut control = control_lock(shared);
    // Shutdown owns and drains the transport. A guard outliving the worker's
    // owner has no remaining lifecycle action and must not underflow its count.
    if shared.stop.load(Ordering::Acquire) { return Ok(()); }
    assert!(control.scopes != 0, "worker scope released twice");
    control.scopes -= 1;
    shared.active_scopes.store(control.scopes, Ordering::Release);
    if control.scopes != 0 { return Ok(()); }
    control.parking = true;
    while control.parking && !terminal(shared) {
        control = wait_control(shared, control);
    }
    if matches!(shared.state.load(Ordering::Acquire), FAILED | STOPPED) {
        return Err(shared.slots.lock().unwrap_or_else(|error| error.into_inner())
            .failure.clone().unwrap_or_else(|| "worker stopped while parking".into()));
    }
    Ok(())
}

/// Called after any outstanding native computation. Clearing transport slots
/// precedes the PARKED release and parking acknowledgment under the same lock
/// used by activation, avoiding a lost wake or a stale next-lifetime output.
fn park(shared: &Shared) -> Result<(), String> {
    let mut control = control_lock(shared);
    if control.scopes != 0 { return Ok(()); }
    {
        let mut slots = shared.slots.lock().map_err(|_| "worker slot poisoned while parking")?;
        slots.packet = None;
        slots.output = None;
    }
    shared.state.store(PARKED, Ordering::Release);
    control.parking = false;
    shared.wake.notify_all();
    while control.scopes == 0 && !shared.stop.load(Ordering::Acquire) {
        control = shared.wake.wait(control).unwrap_or_else(|error| error.into_inner());
    }
    if !shared.stop.load(Ordering::Acquire) {
        shared.state.store(IDLE, Ordering::Release);
        shared.wake.notify_all();
    }
    Ok(())
}

fn wait_control<'a>(
    shared: &'a Shared, control: MutexGuard<'a, Control>,
) -> MutexGuard<'a, Control> {
    shared.wake.wait(control).unwrap_or_else(|error| error.into_inner())
}

#[cfg(test)]
fn test_gate(shared: &Shared) -> Result<(), String> {
    let mut gate = shared.test_gate.lock().unwrap();
    gate.entered = true;
    shared.test_wake.notify_all();
    while gate.blocked {
        gate = shared.test_wake.wait(gate).unwrap();
    }
    if gate.fail { Err("controlled Activity/Shelter worker failure".into()) } else { Ok(()) }
}

#[cfg(test)]
mod lifecycle_tests {
    use super::*;
    use std::time::{Duration, Instant};

    // Every worker, including test workers, inherits its creator's allowed CPU
    // set. Controlled placement belongs to the external test supervisor.
    fn worker() -> ActivityShelterWorker {
        ActivityShelterWorker::start_with(run_active).unwrap()
    }

    fn packet() -> Packet {
        let position = Position::from_fen(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        ).unwrap();
        Packet {
            position,
            influence: Influence::build(&position),
            material: 193,
            mobility_weights: [2017, 633],
            shelter_weights: [997, 3101],
        }
    }

    fn dispatch(worker: &mut ActivityShelterWorker, packet: &Packet) {
        worker.dispatch(
            &packet.position, &packet.influence, packet.material,
            packet.mobility_weights, packet.shelter_weights,
        ).unwrap();
    }

    fn block_job(shared: &Shared) {
        let mut gate = shared.test_gate.lock().unwrap();
        gate.blocked = true;
        gate.entered = false;
        gate.fail = false;
    }

    fn wait_job_entered(shared: &Shared) {
        let mut gate = shared.test_gate.lock().unwrap();
        while !gate.entered { gate = shared.test_wake.wait(gate).unwrap(); }
    }

    fn release_job(shared: &Shared, fail: bool) {
        let mut gate = shared.test_gate.lock().unwrap();
        gate.blocked = false;
        gate.fail = fail;
        shared.test_wake.notify_all();
    }

    fn assert_numerical_output(actual: ActivityShelter, packet: &Packet) {
        let expected = compute(&packet.position, &packet.influence, packet.material,
            packet.mobility_weights, packet.shelter_weights);
        assert_eq!(actual.activity, expected.activity);
        assert_eq!(actual.shelter, expected.shelter);
    }

    #[test]
    fn startup_and_standalone_scopes_park_with_empty_slots() {
        let mut worker = worker();
        assert!(worker.is_parked());
        let packet = packet();
        assert!(worker.dispatch(
            &packet.position, &packet.influence, packet.material,
            packet.mobility_weights, packet.shelter_weights,
        ).is_err(), "unscoped dispatch must fail");
        for _ in 0..3 {
            let scope = worker.start_call_scope().unwrap().unwrap();
            dispatch(&mut worker, &packet);
            let actual = worker.complete().unwrap();
            let expected = compute(
                &packet.position, &packet.influence, packet.material,
                packet.mobility_weights, packet.shelter_weights,
            );
            assert_eq!(actual.activity, expected.activity);
            assert_eq!(actual.shelter, expected.shelter);
            scope.finish().unwrap();
            assert!(worker.is_parked());
            let slots = worker.shared.slots.lock().unwrap();
            assert!(slots.packet.is_none() && slots.output.is_none());
        }
        worker.shutdown().unwrap();
    }

    #[test]
    fn nested_scopes_and_full_call_fast_path_keep_outer_active() {
        let mut worker = worker();
        let outer = worker.start_active_scope().unwrap();
        assert!(!worker.is_parked());
        let inner = worker.start_active_scope().unwrap();
        assert!(worker.start_call_scope().unwrap().is_none());
        inner.finish().unwrap();
        assert_eq!(worker.shared.active_scopes.load(Ordering::Acquire), 1);
        let packet = packet();
        dispatch(&mut worker, &packet);
        worker.complete().unwrap();
        assert!(!worker.is_parked());
        outer.finish().unwrap();
        assert!(worker.is_parked());
    }

    #[test]
    fn abandoned_request_is_drained_before_next_scope_and_unwind_parks() {
        let mut worker = worker();
        let packet = packet();
        let scope = worker.start_active_scope().unwrap();
        dispatch(&mut worker, &packet);
        // Intentionally omit complete: closing the scope waits for the native
        // computation, discards its output and acknowledges empty parked slots.
        drop(scope);
        assert!(worker.is_parked());
        let next = worker.start_active_scope().unwrap();
        assert!(worker.complete().is_err(), "old output must not cross a scope");
        dispatch(&mut worker, &packet);
        worker.complete().unwrap();
        drop(next);
        let unwound = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _scope = worker.start_active_scope().unwrap();
            dispatch(&mut worker, &packet);
            panic!("intentional worker scope unwind");
        }));
        assert!(unwound.is_err());
        assert!(worker.is_parked());
        let slots = worker.shared.slots.lock().unwrap();
        assert!(slots.packet.is_none() && slots.output.is_none());
    }

    #[test]
    fn parked_shutdown_and_guard_outliving_owner_leave_no_live_worker() {
        let mut worker = worker();
        let scope = worker.start_active_scope().unwrap();
        let packet = packet();
        dispatch(&mut worker, &packet);
        worker.shutdown().unwrap();
        assert!(worker.thread.is_none());
        assert_eq!(worker.shared.state.load(Ordering::Acquire), STOPPED);
        scope.finish().unwrap();
        let mut parked = self::worker();
        assert!(parked.is_parked());
        parked.shutdown().unwrap();
        assert!(parked.thread.is_none());
    }

    #[test]
    fn completion_before_wait_retains_exact_output_without_a_future_notification() {
        let mut worker = worker();
        let scope = worker.start_active_scope().unwrap();
        let packet = packet();
        dispatch(&mut worker, &packet);
        // Observe publication first, without consuming it. The public complete
        // call must use the predicate, rather than wait for another notification.
        drop(completion_slots(&worker.shared).unwrap());
        assert_eq!(worker.shared.state.load(Ordering::Acquire), COMPLETE);
        assert_numerical_output(worker.complete().unwrap(), &packet);
        scope.finish().unwrap();
        worker.shutdown().unwrap();
    }

    #[test]
    fn startup_failure_and_early_normal_stop_notify_lifecycle_waiters() {
        fn fail(_shared: &Shared) -> Result<(), String> { Err("controlled startup failure".into()) }
        fn stop(_shared: &Shared) -> Result<(), String> { Ok(()) }
        let failed = ActivityShelterWorker::start_with(fail);
        assert!(failed.is_err());
        assert_eq!(failed.err().unwrap(), "controlled startup failure");
        assert!(ActivityShelterWorker::start_with(stop).is_err());
    }

    #[test]
    fn terminal_failure_wakes_completion_and_last_scope_waiters() {
        let mut worker = worker();
        let scope = worker.start_active_scope().unwrap();
        block_job(&worker.shared);
        dispatch(&mut worker, &packet());
        wait_job_entered(&worker.shared);
        let shared = Arc::clone(&worker.shared);
        let completion = thread::spawn(move || {
            let result = completion_slots(&shared);
            let failed = result.is_err();
            drop(result);
            failed
        });
        let parking = thread::spawn(move || scope.finish().is_err());
        // These are fixed test barriers, not a wall-time engine policy. The
        // external test supervisor bounds a regression that loses either wake.
        loop {
            let waiting = worker.shared.slots.lock().unwrap().completion_waiting;
            let parking = worker.shared.control.lock().unwrap().parking;
            if waiting && parking { break; }
            thread::yield_now();
        }
        release_job(&worker.shared, true);
        assert!(completion.join().unwrap());
        assert!(parking.join().unwrap());
        let failure = worker.shutdown().unwrap_err(); // Explicitly discharge failed owner.
        assert_eq!(worker.shutdown().unwrap_err(), failure, "a retry must retain terminal failure");
        assert!(worker.thread.is_none());
        assert!(worker.check_running().is_err());
    }

    #[test]
    fn normal_terminal_stop_wakes_a_blocked_completion_waiter_and_joins() {
        fn stop_after_request(shared: &Shared) -> Result<(), String> {
            park(shared)?;
            while shared.state.load(Ordering::Acquire) != REQUESTED {
                if shared.stop.load(Ordering::Acquire) { return Ok(()); }
                spin_loop();
            }
            // This controlled entry exits a stopped, abandoned request without
            // publishing COMPLETE. Only the terminal notification can wake it.
            test_gate(shared)
        }
        let mut worker = ActivityShelterWorker::start_with(stop_after_request).unwrap();
        let scope = worker.start_active_scope().unwrap();
        block_job(&worker.shared);
        dispatch(&mut worker, &packet());
        wait_job_entered(&worker.shared);
        let shared = Arc::clone(&worker.shared);
        let completion = thread::spawn(move || {
            let result = completion_slots(&shared);
            let failed = result.is_err();
            drop(result);
            failed
        });
        while !worker.shared.slots.lock().unwrap().completion_waiting { thread::yield_now(); }
        // Model a terminal owner stop while a slow helper is in its owned
        // computation. No host polling or alternate numerical path is inserted.
        {
            let mut control = control_lock(&worker.shared);
            worker.shared.stop.store(true, Ordering::Release);
            worker.shared.active_scopes.store(0, Ordering::Release);
            control.scopes = 0;
            control.parking = false;
            worker.shared.wake.notify_all();
        }
        release_job(&worker.shared, false);
        assert!(completion.join().unwrap());
        worker.shutdown().unwrap();
        scope.finish().unwrap();
        assert!(worker.thread.is_none());
        assert_eq!(worker.shared.state.load(Ordering::Acquire), STOPPED);
    }

    #[test]
    #[ignore = "11-second controlled helper barrier; run explicitly under an external supervisor"]
    fn helper_delay_beyond_ten_seconds_preserves_result_and_lifecycle() {
        let mut worker = worker();
        let scope = worker.start_active_scope().unwrap();
        let packet = packet();
        block_job(&worker.shared);
        dispatch(&mut worker, &packet);
        wait_job_entered(&worker.shared);
        let shared = Arc::clone(&worker.shared);
        let started = Instant::now();
        let release = thread::spawn(move || {
            thread::sleep(Duration::from_secs(11));
            release_job(&shared, false);
        });
        let actual = worker.complete().unwrap();
        assert!(started.elapsed() >= Duration::from_secs(10));
        release.join().unwrap();
        assert_numerical_output(actual, &packet);
        scope.finish().unwrap();
        assert!(worker.is_parked());
        worker.shutdown().unwrap();
        assert!(worker.thread.is_none());
    }
}
