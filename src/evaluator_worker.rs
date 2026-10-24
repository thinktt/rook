//! Narrow research-only Activity -> Shelter worker for confirmed FULL calls.
//!
//! Packet and result slots are reusable owned storage, never borrowed from a
//! caller's stack. Successful dispatch/complete allocate no memory or threads.
//! The worker spins only inside an owned active search/call scope. Outside those
//! scopes it acknowledges empty transport slots and sleeps on a condition.

use crate::activity::{self, Activity};
use crate::influence::Influence;
use crate::position::Position;
use crate::shelter::{self, Shelter};
use std::hint::spin_loop;
use std::sync::atomic::{AtomicBool, AtomicU8, AtomicUsize, Ordering};
use std::sync::{Arc, Condvar, Mutex, MutexGuard};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

const STARTING: u8 = 0;
const IDLE: u8 = 1;
const REQUESTED: u8 = 2;
const COMPLETE: u8 = 3;
const FAILED: u8 = 4;
const STOPPED: u8 = 5;
const PARKED: u8 = 6;
const WORKER_CPU: usize = 6;
const WAIT_LIMIT: Duration = Duration::from_secs(10);
const DEADLINE_POLL_SPINS: usize = 4096;

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
}

struct Shared {
    state: AtomicU8,
    stop: AtomicBool,
    active_scopes: AtomicUsize,
    control: Mutex<Control>,
    wake: Condvar,
    slots: Mutex<Slots>,
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
                eprintln!("research evaluator worker scope close failed: {error}");
            }
        }
    }
}

pub(crate) struct ActivityShelterWorker {
    shared: Arc<Shared>,
    thread: Option<JoinHandle<()>>,
}

impl ActivityShelterWorker {
    pub(crate) fn start() -> Result<Self, String> {
        Self::start_with(run)
    }

    fn start_with(entry: fn(&Shared) -> Result<(), String>) -> Result<Self, String> {
        let shared = Arc::new(Shared {
            state: AtomicU8::new(STARTING),
            stop: AtomicBool::new(false),
            active_scopes: AtomicUsize::new(0),
            control: Mutex::new(Control::default()),
            wake: Condvar::new(),
            slots: Mutex::new(Slots::default()),
        });
        let worker_shared = Arc::clone(&shared);
        let thread = thread::Builder::new()
            .name("rook2-eval-research".into())
            .spawn(move || {
                let result = std::panic::catch_unwind(|| entry(&worker_shared));
                let failure = match result {
                    Ok(Ok(())) => {
                        worker_shared.state.store(STOPPED, Ordering::Release);
                        worker_shared.wake.notify_all();
                        return;
                    }
                    Ok(Err(error)) => error,
                    Err(_) => "Activity/Shelter worker panicked".into(),
                };
                // Recover a poisoned slot only to report terminal failure. There
                // is no job recovery or fallback to a different computation.
                let mut control = control_lock(&worker_shared);
                worker_shared
                    .slots
                    .lock()
                    .unwrap_or_else(|e| e.into_inner())
                    .failure = Some(failure);
                worker_shared.state.store(FAILED, Ordering::Release);
                control.parking = false;
                worker_shared.wake.notify_all();
            })
            .map_err(|error| format!("cannot start Activity/Shelter worker: {error}"))?;
        let mut worker = Self {
            shared,
            thread: Some(thread),
        };
        let state = wait_while(
            STARTING,
            || worker.shared.state.load(Ordering::Acquire),
            "startup",
        );
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
        let deadline = Instant::now() + WAIT_LIMIT;
        while control.parking && !terminal(&self.shared) {
            control = wait_control(&self.shared, control, deadline, "prior parking");
        }
        if terminal(&self.shared) {
            return Err(self.failure());
        }
        let first = control.scopes == 0;
        control.scopes = control.scopes.checked_add(1).expect("worker active scope count exhausted");
        self.shared.active_scopes.store(control.scopes, Ordering::Release);
        let scope = ActiveScope { shared: Arc::clone(&self.shared), armed: true };
        if first {
            // A prior closing guard may still be an acknowledgment waiter on
            // this condition. Wake all so activation cannot wake only it.
            self.shared.wake.notify_all();
        }
        drop(control);
        if first {
            let state = wait_while(
                PARKED, || self.shared.state.load(Ordering::Acquire), "activation",
            );
            if state != IDLE {
                return Err(self.failure());
            }
        }
        Ok(scope)
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
        let state = wait_while(
            REQUESTED,
            || self.shared.state.load(Ordering::Acquire),
            "completion",
        );
        if state != COMPLETE {
            return Err(self.failure());
        }
        let output = self
            .shared
            .slots
            .lock()
            .map_err(|_| "worker slot poisoned")?
            .output
            .take()
            .ok_or("worker completed without an output")?;
        self.shared.state.store(IDLE, Ordering::Release);
        Ok(output)
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
        let Some(handle) = self.thread.as_ref() else {
            return Ok(());
        };
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
        wait_while(false, || handle.is_finished(), "shutdown");
        let handle = self.thread.take().unwrap();
        if handle.join().is_err() {
            return Err("Activity/Shelter worker exited with an uncaught panic".into());
        }
        {
            let mut slots = self.shared.slots.lock().unwrap_or_else(|error| error.into_inner());
            slots.packet = None;
            slots.output = None;
        }
        if self.shared.state.load(Ordering::Acquire) == FAILED {
            return Err(self.failure());
        }
        Ok(())
    }
}

impl Drop for ActivityShelterWorker {
    fn drop(&mut self) {
        if let Err(error) = self.shutdown() {
            eprintln!("research evaluator worker shutdown failed: {error}");
        }
    }
}

fn run(shared: &Shared) -> Result<(), String> {
    pin_worker()?;
    run_active(shared)
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
        let output = compute(
            &packet.position,
            &packet.influence,
            packet.material,
            packet.mobility_weights,
            packet.shelter_weights,
        );
        shared
            .slots
            .lock()
            .map_err(|_| "worker slot poisoned")?
            .output = Some(output);
        shared.state.store(COMPLETE, Ordering::Release);
    }
    Ok(())
}

fn control_lock(shared: &Shared) -> MutexGuard<'_, Control> {
    shared.control.lock().unwrap_or_else(|error| error.into_inner())
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
    let deadline = Instant::now() + WAIT_LIMIT;
    while control.parking && !terminal(shared) {
        control = wait_control(shared, control, deadline, "parking");
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
    }
    Ok(())
}

fn wait_control<'a>(
    shared: &'a Shared, control: MutexGuard<'a, Control>, deadline: Instant, phase: &str,
) -> MutexGuard<'a, Control> {
    let remaining = deadline.saturating_duration_since(Instant::now());
    if remaining.is_zero() {
        eprintln!("research evaluator worker {phase} exceeded {WAIT_LIMIT:?}; aborting");
        std::process::abort();
    }
    shared.wake.wait_timeout(control, remaining).unwrap_or_else(|error| error.into_inner()).0
}

/// Ordinary jobs avoid clock reads. After a small fixed spin allowance, bound
/// every lifecycle wait by a wall-clock deadline. Rust has no timed thread join:
/// a stuck worker must terminate the process, rather than become an orphan.
fn wait_while<T: Copy + PartialEq>(expected: T, mut read: impl FnMut() -> T, phase: &str) -> T {
    let mut spins = 0;
    let mut started = None;
    loop {
        let state = read();
        if state != expected {
            return state;
        }
        spin_loop();
        spins += 1;
        if spins == DEADLINE_POLL_SPINS {
            spins = 0;
            let started = started.get_or_insert_with(Instant::now);
            if started.elapsed() >= WAIT_LIMIT {
                eprintln!("research evaluator worker {phase} exceeded {WAIT_LIMIT:?}; aborting");
                std::process::abort();
            }
        }
    }
}

#[cfg(target_os = "linux")]
fn pin_worker() -> Result<(), String> {
    extern "C" {
        fn sched_setaffinity(pid: i32, bytes: usize, mask: *const u64) -> i32;
        fn sched_getaffinity(pid: i32, bytes: usize, mask: *mut u64) -> i32;
    }
    let mut mask = [0u64; 16];
    mask[WORKER_CPU / 64] = 1 << (WORKER_CPU % 64);
    // Linux pid 0 selects the calling thread. Both pointers cover exactly the
    // supplied 128-byte cpu mask, and remain valid throughout each FFI call.
    if unsafe { sched_setaffinity(0, std::mem::size_of_val(&mask), mask.as_ptr()) } != 0 {
        return Err(format!(
            "cannot pin research evaluator worker to CPU{WORKER_CPU}: {}",
            std::io::Error::last_os_error()
        ));
    }
    let mut actual = [0u64; 16];
    if unsafe { sched_getaffinity(0, std::mem::size_of_val(&actual), actual.as_mut_ptr()) } != 0 {
        return Err(format!(
            "cannot verify research evaluator worker affinity: {}",
            std::io::Error::last_os_error()
        ));
    }
    if actual != mask {
        return Err(format!(
            "research evaluator worker affinity differs from CPU{WORKER_CPU}"
        ));
    }
    Ok(())
}

#[cfg(not(target_os = "linux"))]
fn pin_worker() -> Result<(), String> {
    Err("the research evaluator worker requires Linux CPU6 affinity".into())
}

#[cfg(test)]
mod lifecycle_tests {
    use super::*;

    // Exercise the production park/transport loop without changing the test
    // process's permitted CPU set. Integrated evaluator tests retain real pinning.
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
}
