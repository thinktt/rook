//! Reversed FULL placement: one helper exclusively owns the ordered pawn cache.
//!
//! The transport and parked lifecycle copy the existing Activity/Shelter worker
//! protocol unchanged. This bounded ownership experiment does not select a new
//! transport. Keeping these two implementations aligned is explicit prototype
//! debt. Only cold install/reset/snapshot/transfer commands are added here.

use crate::influence::Influence;
use crate::pawn_branch::{self, PawnBranchResult};
use crate::pawn_structure::PawnCacheCore;
use crate::position::{Phase, Position};
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

struct FullPacket {
    position: Position,
    influence: Influence,
    phase: Phase,
    material: i32,
    structure_weights: [i32; 2],
    progress_weights: [i32; 2],
    fresh: bool,
}

enum Command {
    Full(FullPacket),
    Install,
    Reset,
    #[cfg(test)]
    Snapshot,
}

#[derive(Default)]
struct Slots {
    packet: Option<Command>,
    output: Option<PawnBranchResult>,
    // Cold cache moves and test snapshots use separate storage. Full result
    // transport must not take/copy an enum containing an eight-KiB variant.
    transfer: Option<PawnCacheCore>,
    failure: Option<String>,
}

#[derive(Default)]
struct Control { scopes: usize, parking: bool }

struct Shared {
    state: AtomicU8,
    stop: AtomicBool,
    active_scopes: AtomicUsize,
    has_core: AtomicBool,
    control: Mutex<Control>,
    wake: Condvar,
    slots: Mutex<Slots>,
    #[cfg(test)]
    fail_after_selection: AtomicBool,
}

pub(crate) struct PawnActiveScope { shared: Arc<Shared>, armed: bool }

impl PawnActiveScope {
    pub(crate) fn finish(mut self) -> Result<(), String> {
        self.armed = false;
        release_scope(&self.shared)
    }
}

impl Drop for PawnActiveScope {
    fn drop(&mut self) {
        if self.armed {
            if let Err(error) = release_scope(&self.shared) {
                eprintln!("research pawn worker scope close failed: {error}");
            }
        }
    }
}

/// Recovery always carries the actual cache. A worker error must never turn
/// an ownership transfer into an Err that drops those authoritative entries.
pub(crate) struct PawnWorkerRecovery {
    pub core: PawnCacheCore,
    pub failure: Option<String>,
}

pub(crate) struct PawnWorker { shared: Arc<Shared>, thread: Option<JoinHandle<()>> }

impl PawnWorker {
    /// Starts empty and parked. The caller still owns its actual cache if
    /// spawning, affinity setup or the startup handshake fails normally.
    pub(crate) fn start() -> Result<Self, String> { Self::start_with(true) }

    fn start_with(pin: bool) -> Result<Self, String> {
        let shared = Arc::new(Shared {
            state: AtomicU8::new(STARTING), stop: AtomicBool::new(false),
            active_scopes: AtomicUsize::new(0), has_core: AtomicBool::new(false),
            control: Mutex::new(Control::default()), wake: Condvar::new(),
            slots: Mutex::new(Slots::default()),
            #[cfg(test)]
            fail_after_selection: AtomicBool::new(false),
        });
        let worker_shared = Arc::clone(&shared);
        let thread = thread::Builder::new().name("rook2-pawn-research".into()).spawn(move || {
            // Cache storage lives outside catch_unwind. A numerical panic after
            // selection preserves its mutations and exports them for recovery.
            let mut core = None;
            let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                if pin { pin_worker()?; }
                run_active(&worker_shared, &mut core)
            }));
            let failure = match result {
                Ok(Ok(())) => None,
                Ok(Err(error)) => Some(error),
                Err(_) => Some("pawn worker panicked".into()),
            };
            let mut control = control_lock(&worker_shared);
            let mut slots = worker_shared.slots.lock().unwrap_or_else(|error| error.into_inner());
            if let Some(core) = core.take() {
                // A possible snapshot is disposable; the actual owned core wins.
                slots.transfer = Some(core);
            }
            if let Some(error) = failure {
                slots.failure = Some(error);
                worker_shared.state.store(FAILED, Ordering::Release);
            } else {
                worker_shared.state.store(STOPPED, Ordering::Release);
            }
            control.parking = false;
            worker_shared.wake.notify_all();
        }).map_err(|error| format!("cannot start pawn worker: {error}"))?;
        let mut worker = Self { shared, thread: Some(thread) };
        let state = wait_while(STARTING, || worker.shared.state.load(Ordering::Acquire), "startup");
        if state == PARKED {
            Ok(worker)
        } else {
            let failure = worker.failure();
            let _ = worker.shutdown();
            Err(failure)
        }
    }

    pub(crate) fn start_active_scope(&self) -> Result<PawnActiveScope, String> {
        let mut control = control_lock(&self.shared);
        let deadline = Instant::now() + WAIT_LIMIT;
        while control.parking && !terminal(&self.shared) {
            control = wait_control(&self.shared, control, deadline, "prior parking");
        }
        if terminal(&self.shared) { return Err(self.failure()); }
        let first = control.scopes == 0;
        control.scopes = control.scopes.checked_add(1).expect("pawn worker active scope count exhausted");
        self.shared.active_scopes.store(control.scopes, Ordering::Release);
        let scope = PawnActiveScope { shared: Arc::clone(&self.shared), armed: true };
        if first { self.shared.wake.notify_all(); }
        drop(control);
        if first {
            let state = wait_while(PARKED, || self.shared.state.load(Ordering::Acquire), "activation");
            if state != IDLE { return Err(self.failure()); }
        }
        Ok(scope)
    }

    pub(crate) fn start_call_scope(&self) -> Result<Option<PawnActiveScope>, String> {
        if self.shared.active_scopes.load(Ordering::Acquire) != 0 { Ok(None) }
        else { self.start_active_scope().map(Some) }
    }

    /// Once accepted by this method, core is always recoverable through
    /// shutdown_take, even if activation/install reports an ordinary failure.
    /// Installation is a one-time ownership transition, before any FULL.
    pub(crate) fn install(&mut self, core: PawnCacheCore) -> Result<(), String> {
        assert!(!self.shared.has_core.load(Ordering::Acquire), "pawn cache already installed");
        {
            let mut slots = self.shared.slots.lock().unwrap_or_else(|error| error.into_inner());
            assert!(slots.transfer.is_none(), "pawn cache transfer already pending");
            slots.transfer = Some(core);
        }
        let _scope = self.start_call_scope()?;
        self.publish(Command::Install)?;
        self.complete_control()
    }

    pub(crate) fn dispatch<const FRESH: bool>(
        &mut self, position: &Position, influence: &Influence, phase: Phase, material: i32,
        structure_weights: [i32; 2], progress_weights: [i32; 2],
    ) -> Result<(), String> {
        if !self.shared.has_core.load(Ordering::Acquire) { return Err("pawn worker has no cache".into()); }
        self.publish(Command::Full(FullPacket {
            position: *position, influence: *influence, phase, material,
            structure_weights, progress_weights, fresh: FRESH,
        }))
    }

    fn publish(&mut self, packet: Command) -> Result<(), String> {
        if self.shared.active_scopes.load(Ordering::Acquire) == 0
            || self.shared.state.load(Ordering::Acquire) != IDLE { return Err(self.failure()); }
        {
            let mut slots = self.shared.slots.lock().map_err(|_| "pawn worker slot poisoned")?;
            debug_assert!(slots.packet.is_none() && slots.output.is_none());
            slots.packet = Some(packet);
        }
        self.shared.state.store(REQUESTED, Ordering::Release);
        Ok(())
    }

    pub(crate) fn complete(&mut self) -> Result<PawnBranchResult, String> {
        self.await_complete()?;
        let output = self.shared.slots.lock().map_err(|_| "pawn worker slot poisoned")?
            .output.take().ok_or("pawn worker completed without a FULL output")?;
        self.shared.state.store(IDLE, Ordering::Release);
        Ok(output)
    }

    fn await_complete(&self) -> Result<(), String> {
        let state = wait_while(REQUESTED, || self.shared.state.load(Ordering::Acquire), "completion");
        if state == COMPLETE { Ok(()) } else { Err(self.failure()) }
    }

    fn complete_control(&mut self) -> Result<(), String> {
        self.await_complete()?;
        self.shared.state.store(IDLE, Ordering::Release);
        Ok(())
    }

    pub(crate) fn reset(&mut self) -> Result<(), String> {
        let _scope = self.start_call_scope()?;
        self.publish(Command::Reset)?;
        self.complete_control()
    }

    #[cfg(test)]
    pub(crate) fn snapshot_core(&mut self) -> Result<PawnCacheCore, String> {
        let _scope = self.start_call_scope()?;
        self.publish(Command::Snapshot)?;
        self.await_complete()?;
        let core = self.shared.slots.lock().map_err(|_| "pawn snapshot slot poisoned")?
            .transfer.take().ok_or("pawn snapshot missing")?;
        self.shared.state.store(IDLE, Ordering::Release);
        Ok(core)
    }

    #[cfg(test)]
    pub(crate) fn fail_after_selection_next(&self) {
        self.shared.fail_after_selection.store(true, Ordering::Release);
    }

    #[cfg(test)]
    pub(crate) fn is_parked(&self) -> bool {
        self.shared.state.load(Ordering::Acquire) == PARKED
            && self.shared.active_scopes.load(Ordering::Acquire) == 0
    }

    fn failure(&self) -> String {
        self.shared.slots.lock().unwrap_or_else(|error| error.into_inner()).failure.clone()
            .unwrap_or_else(|| "pawn worker entered an invalid state".into())
    }

    /// Every submitted operation must settle before stopping. In particular an
    /// abandoned FULL still owns its native cache selection/replacement effects.
    pub(crate) fn shutdown(&mut self) -> Result<(), String> {
        let Some(handle) = self.thread.as_ref() else { return Ok(()); };
        wait_while(REQUESTED, || self.shared.state.load(Ordering::Acquire), "shutdown drain");
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
        if handle.join().is_err() { return Err("pawn worker exited with an uncaught panic".into()); }
        {
            let mut slots = self.shared.slots.lock().unwrap_or_else(|error| error.into_inner());
            slots.packet = None;
            slots.output = None;
        }
        if self.shared.state.load(Ordering::Acquire) == FAILED { Err(self.failure()) } else { Ok(()) }
    }

    pub(crate) fn shutdown_take(&mut self) -> PawnWorkerRecovery {
        let failure = self.shutdown().err();
        let mut slots = self.shared.slots.lock().unwrap_or_else(|error| error.into_inner());
        let core = slots.transfer.take().expect("pawn worker lost its installed cache during recovery");
        PawnWorkerRecovery { core, failure: failure.or_else(|| slots.failure.clone()) }
    }
}

impl Drop for PawnWorker {
    fn drop(&mut self) {
        if let Err(error) = self.shutdown() { eprintln!("research pawn worker shutdown failed: {error}"); }
    }
}

fn run_active(shared: &Shared, core: &mut Option<PawnCacheCore>) -> Result<(), String> {
    park(shared)?;
    while !shared.stop.load(Ordering::Acquire) {
        if shared.state.load(Ordering::Acquire) != REQUESTED {
            if shared.active_scopes.load(Ordering::Acquire) == 0 { park(shared)?; continue; }
            spin_loop();
            continue;
        }
        let packet = shared.slots.lock().map_err(|_| "pawn worker slot poisoned")?
            .packet.take().ok_or("pawn worker request has no packet")?;
        let output = match packet {
            Command::Install => {
                if core.is_some() { return Err("pawn cache installed twice".into()); }
                *core = Some(shared.slots.lock().map_err(|_| "pawn install slot poisoned")?
                    .transfer.take().ok_or("pawn install has no cache")?);
                shared.has_core.store(true, Ordering::Release);
                None
            }
            Command::Reset => {
                core.as_mut().ok_or("pawn reset has no cache")?.clear();
                None
            }
            #[cfg(test)]
            Command::Snapshot => {
                shared.slots.lock().map_err(|_| "pawn snapshot slot poisoned")?.transfer =
                    Some(core.as_ref().ok_or("pawn snapshot has no cache")?.clone());
                None
            }
            Command::Full(packet) => {
                let cache = core.as_mut().ok_or("pawn FULL has no cache")?;
                #[cfg(test)]
                if shared.fail_after_selection.swap(false, Ordering::AcqRel) {
                    if !packet.fresh { cache.select(&packet.position, &packet.influence); }
                    panic!("intentional pawn failure after cache selection");
                }
                Some(if packet.fresh {
                    pawn_branch::compute_core::<true>(cache, &packet.position, &packet.influence,
                        packet.phase, packet.material, packet.structure_weights, packet.progress_weights)
                } else {
                    pawn_branch::compute_core::<false>(cache, &packet.position, &packet.influence,
                        packet.phase, packet.material, packet.structure_weights, packet.progress_weights)
                })
            }
        };
        shared.slots.lock().map_err(|_| "pawn result slot poisoned")?.output = output;
        shared.state.store(COMPLETE, Ordering::Release);
    }
    Ok(())
}

fn control_lock(shared: &Shared) -> MutexGuard<'_, Control> {
    shared.control.lock().unwrap_or_else(|error| error.into_inner())
}

fn terminal(shared: &Shared) -> bool {
    shared.stop.load(Ordering::Acquire) || matches!(shared.state.load(Ordering::Acquire), FAILED | STOPPED)
}

fn release_scope(shared: &Shared) -> Result<(), String> {
    let mut control = control_lock(shared);
    if shared.stop.load(Ordering::Acquire) { return Ok(()); }
    assert!(control.scopes != 0, "pawn scope released twice");
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
            .failure.clone().unwrap_or_else(|| "pawn worker stopped while parking".into()));
    }
    Ok(())
}

fn park(shared: &Shared) -> Result<(), String> {
    let mut control = control_lock(shared);
    if control.scopes != 0 { return Ok(()); }
    {
        let mut slots = shared.slots.lock().map_err(|_| "pawn slot poisoned while parking")?;
        slots.packet = None;
        slots.output = None;
        // The actual cache lives on the helper, not in either output slot.
        // Only a cold snapshot can remain here after an installed operation.
        if shared.has_core.load(Ordering::Acquire) { slots.transfer = None; }
    }
    shared.state.store(PARKED, Ordering::Release);
    control.parking = false;
    shared.wake.notify_all();
    while control.scopes == 0 && !shared.stop.load(Ordering::Acquire) {
        control = shared.wake.wait(control).unwrap_or_else(|error| error.into_inner());
    }
    if !shared.stop.load(Ordering::Acquire) { shared.state.store(IDLE, Ordering::Release); }
    Ok(())
}

fn wait_control<'a>(
    shared: &'a Shared, control: MutexGuard<'a, Control>, deadline: Instant, phase: &str,
) -> MutexGuard<'a, Control> {
    let remaining = deadline.saturating_duration_since(Instant::now());
    if remaining.is_zero() {
        eprintln!("research pawn worker {phase} exceeded {WAIT_LIMIT:?}; aborting");
        std::process::abort();
    }
    shared.wake.wait_timeout(control, remaining).unwrap_or_else(|error| error.into_inner()).0
}

fn wait_while<T: Copy + PartialEq>(expected: T, mut read: impl FnMut() -> T, phase: &str) -> T {
    let mut spins = 0;
    let mut started = None;
    loop {
        let state = read();
        if state != expected { return state; }
        spin_loop();
        spins += 1;
        if spins == DEADLINE_POLL_SPINS {
            spins = 0;
            let started = started.get_or_insert_with(Instant::now);
            if started.elapsed() >= WAIT_LIMIT {
                eprintln!("research pawn worker {phase} exceeded {WAIT_LIMIT:?}; aborting");
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
    if unsafe { sched_setaffinity(0, std::mem::size_of_val(&mask), mask.as_ptr()) } != 0 {
        return Err(format!("cannot pin pawn worker to CPU{WORKER_CPU}: {}", std::io::Error::last_os_error()));
    }
    let mut actual = [0u64; 16];
    if unsafe { sched_getaffinity(0, std::mem::size_of_val(&actual), actual.as_mut_ptr()) } != 0 {
        return Err(format!("cannot verify pawn worker affinity: {}", std::io::Error::last_os_error()));
    }
    if actual != mask { return Err(format!("pawn worker affinity differs from CPU{WORKER_CPU}")); }
    Ok(())
}

#[cfg(not(target_os = "linux"))]
fn pin_worker() -> Result<(), String> { Err("the pawn worker requires Linux CPU6 affinity".into()) }

#[cfg(test)]
mod tests {
    use super::*;
    use crate::pawn_structure::PawnCache;

    fn position() -> Position {
        Position::from_fen("7k/8/8/5p2/8/3PP3/8/K7 w - - 0 1").unwrap()
    }

    fn worker() -> PawnWorker {
        let mut worker = PawnWorker::start_with(false).unwrap();
        assert!(worker.is_parked());
        worker.install(PawnCacheCore::new()).unwrap();
        assert!(worker.is_parked());
        worker
    }

    fn dispatch<const FRESH: bool>(worker: &mut PawnWorker, position: &Position, map: &Influence) {
        worker.dispatch::<FRESH>(position, map, position.phase(), 83, [1301, 697], [2017, 313]).unwrap();
    }

    #[test]
    fn transferable_core_keeps_layout_and_needs_no_unsafe_send() {
        fn assert_send<T: Send>() {}
        assert_send::<PawnCacheCore>();
        assert_eq!(std::mem::size_of::<PawnCacheCore>(), 8192);
        let position = position();
        let map = Influence::build(&position);
        let mut cache = PawnCache::new();
        let selection = cache.select(&position, &map);
        let mut core = cache.take_core();
        assert_eq!(core.select(&position, &map).structure, selection.structure);
        assert!(core.select(&position, &map).reused);
        cache.install_core(core);
        assert!(cache.select(&position, &map).reused);
    }

    #[test]
    fn abandoned_full_preserves_cache_and_fresh_bypasses_mutation() {
        let mut worker = worker();
        let position = position();
        let map = Influence::build(&position);
        let scope = worker.start_active_scope().unwrap();
        let nested = worker.start_active_scope().unwrap();
        assert!(worker.start_call_scope().unwrap().is_none());
        drop(nested);
        dispatch::<false>(&mut worker, &position, &map);
        // Abandon the output; the park acknowledgment must retain selection.
        scope.finish().unwrap();
        assert!(worker.is_parked());
        let before = worker.snapshot_core().unwrap();
        let scope = worker.start_active_scope().unwrap();
        let contrary = Influence { profiles: [[255; 64], [0; 64]] };
        dispatch::<true>(&mut worker, &position, &contrary);
        let fresh = worker.complete().unwrap();
        assert!(!fresh.reused);
        drop(scope);
        assert_eq!(worker.snapshot_core().unwrap(), before);
        let scope = worker.start_active_scope().unwrap();
        dispatch::<false>(&mut worker, &position, &map);
        assert!(worker.complete().unwrap().reused);
        drop(scope);
        let recovery = worker.shutdown_take();
        assert!(recovery.failure.is_none());
        assert_eq!(recovery.core, before);
    }

    #[test]
    fn reset_is_ordered_and_shutdown_drains_pending_selection() {
        let mut worker = worker();
        let position = position();
        let map = Influence::build(&position);
        let scope = worker.start_active_scope().unwrap();
        dispatch::<false>(&mut worker, &position, &map);
        assert!(!worker.complete().unwrap().reused);
        worker.reset().unwrap();
        assert_eq!(worker.snapshot_core().unwrap(), PawnCacheCore::new());
        dispatch::<false>(&mut worker, &position, &map);
        // No complete or scope close before shutdown: submitted FULL still has
        // to perform its selection before the actual cache is handed back.
        let mut recovery = worker.shutdown_take();
        assert!(recovery.failure.is_none());
        assert!(recovery.core.select(&position, &map).reused);
        scope.finish().unwrap();
    }

    #[test]
    fn post_selection_failure_recovers_actual_mutated_cache() {
        let mut worker = worker();
        let position = position();
        let map = Influence::build(&position);
        let scope = worker.start_active_scope().unwrap();
        worker.fail_after_selection_next();
        dispatch::<false>(&mut worker, &position, &map);
        assert!(worker.complete().is_err());
        let mut expected = PawnCacheCore::new();
        expected.select(&position, &map);
        assert_ne!(expected, PawnCacheCore::new(), "failure fixture must mutate authoritative entries");
        let recovery = worker.shutdown_take();
        assert!(recovery.failure.is_some());
        assert_eq!(recovery.core, expected);
        scope.finish().unwrap();
    }

    #[test]
    fn install_failure_still_returns_supplied_core_and_unwind_keeps_mutations() {
        let mut worker = worker();
        let position = position();
        let map = Influence::build(&position);
        let unwound = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _scope = worker.start_active_scope().unwrap();
            dispatch::<false>(&mut worker, &position, &map);
            panic!("intentional abandoned pawn output");
        }));
        assert!(unwound.is_err());
        assert!(worker.is_parked());
        let original = worker.shutdown_take().core;

        let mut empty = PawnWorker::start_with(false).unwrap();
        empty.shutdown().unwrap();
        let expected = original.clone();
        assert!(empty.install(original).is_err());
        let recovery = empty.shutdown_take();
        assert_eq!(recovery.core, expected);
    }
}
