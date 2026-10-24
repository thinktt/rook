//! Ordinary same-node inventory experiment: owned Position -> native MoveList.
//!
//! One slot and the existing parked atomic/Mutex/Condvar protocol, copied rather
//! than tuned. The coordinator owns all search counters and ordering. A ticket
//! makes one opportunistic READY decision at original demand; a miss stays a
//! miss and the coordinator generates inline before draining this unused work.

use crate::movegen::{self, MoveList};
use crate::position::Position;
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

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub(crate) struct Stats {
    pub eligible: u64,
    pub launches: u64,
    pub completed: u64,
    pub consumed: u64,
    pub discarded: u64,
    pub ready_consumed: u64,
    pub local_consumed: u64,
    pub ready_miss: u64,
    pub null_settles: u64,
    pub null_ready: u64,
    pub null_waited: u64,
    pub busy: u64,
    pub domain_skips: u64,
}

impl Stats {
    pub(crate) fn json(self) -> String {
        format!(concat!(
            "{{\"eligible\":{},\"launches\":{},\"completed\":{},\"consumed\":{},",
            "\"discarded\":{},\"ready_consumed\":{},\"local_consumed\":{},\"ready_miss\":{},",
            "\"null_settles\":{},\"null_ready\":{},\"null_waited\":{},\"busy\":{},\"domain_skips\":{}}}"
        ), self.eligible, self.launches, self.completed, self.consumed,
            self.discarded, self.ready_consumed, self.local_consumed, self.ready_miss,
            self.null_settles, self.null_ready, self.null_waited, self.busy, self.domain_skips)
    }
}

pub(crate) enum FallbackKind { Domain, Busy }

#[derive(Clone, Copy, PartialEq, Eq)]
struct Key { token: u64, epoch: u64, position: Position }

struct Slots {
    packet: Option<Key>,
    active: Option<Key>,
    output: MoveList,
    next_token: u64,
    epoch: u64,
    stats: Stats,
    failure: Option<String>,
}

impl Default for Slots {
    fn default() -> Self {
        Self { packet: None, active: None, output: MoveList::new(), next_token: 1,
            epoch: 0, stats: Stats::default(), failure: None }
    }
}

#[derive(Default)]
struct Control { scopes: usize, parking: bool }

struct Shared {
    state: AtomicU8,
    stop: AtomicBool,
    active_scopes: AtomicUsize,
    control: Mutex<Control>,
    wake: Condvar,
    slots: Mutex<Slots>,
    #[cfg(test)]
    hold_generation: AtomicBool,
    #[cfg(test)]
    fail_next: AtomicBool,
}

pub(crate) struct InventoryScope { shared: Arc<Shared>, armed: bool }

impl InventoryScope {
    pub(crate) fn finish(mut self) -> Result<(), String> {
        self.armed = false;
        release_scope(&self.shared)
    }
}

impl Drop for InventoryScope {
    fn drop(&mut self) {
        if self.armed {
            if let Err(error) = release_scope(&self.shared) {
                eprintln!("inventory worker scope close failed: {error}");
            }
        }
    }
}

enum TicketState { Pending, Local(Box<MoveList>), Finished }

/// No Search borrow and no inline MoveList. The null boundary alone allocates
/// an owned box so the parent's completed list survives recursive slot reuse.
pub(crate) struct Ticket {
    shared: Arc<Shared>,
    key: Key,
    state: TicketState,
    missed: bool,
}

impl Ticket {
    pub(crate) fn consume_into(&mut self, out: &mut MoveList) -> Result<bool, String> {
        if matches!(self.state, TicketState::Finished) { return Ok(false); }
        let mut slots = slots_lock(&self.shared);
        if self.shared.stop.load(Ordering::Acquire)
            || self.shared.active_scopes.load(Ordering::Acquire) == 0 || slots.epoch != self.key.epoch
        {
            if matches!(self.state, TicketState::Local(_)) { slots.stats.discarded += 1; }
            self.state = TicketState::Finished;
            return Err("inventory ticket outlived its worker activation".into());
        }
        match &self.state {
            TicketState::Local(list) => {
                copy_inventory(list, out);
                slots.stats.consumed += 1;
                slots.stats.local_consumed += 1;
                self.state = TicketState::Finished;
                Ok(true)
            }
            TicketState::Pending => {
                if slots.active != Some(self.key) {
                    self.state = TicketState::Finished;
                    return Err("inventory ticket no longer owns its slot".into());
                }
                if self.missed { return Ok(false); }
                match self.shared.state.load(Ordering::Acquire) {
                    COMPLETE => {
                        copy_inventory(&slots.output, out);
                        slots.stats.consumed += 1;
                        slots.stats.ready_consumed += 1;
                        clear_slot(&mut slots);
                        self.shared.state.store(IDLE, Ordering::Release);
                        self.state = TicketState::Finished;
                        Ok(true)
                    }
                    REQUESTED => {
                        slots.stats.ready_miss += 1;
                        self.missed = true;
                        Ok(false)
                    }
                    _ => Err(failure(&slots)),
                }
            }
            TicketState::Finished => Ok(false),
        }
    }

    /// Always settles before recursive null work, even when already READY.
    /// The one box allocation is counted by null_settles; no further launch or
    /// consumption allocation occurs. Nested null work may now use the slot.
    pub(crate) fn settle_for_null(&mut self) -> Result<(), String> {
        if !matches!(self.state, TicketState::Pending) { return Ok(()); }
        if self.missed { return Err("null settlement follows an original-demand readiness miss".into()); }
        let ready = {
            let slots = slots_lock(&self.shared);
            if slots.active != Some(self.key) { return Err("null ticket no longer owns its slot".into()); }
            self.shared.state.load(Ordering::Acquire) == COMPLETE
        };
        let state = wait_while(REQUESTED, || self.shared.state.load(Ordering::Acquire), "null settlement");
        let mut slots = slots_lock(&self.shared);
        if state != COMPLETE || slots.active != Some(self.key) { return Err(failure(&slots)); }
        let mut list = Box::new(MoveList::new());
        copy_inventory(&slots.output, &mut list);
        slots.stats.null_settles += 1;
        slots.stats.null_ready += u64::from(ready);
        slots.stats.null_waited += u64::from(!ready);
        clear_slot(&mut slots);
        self.shared.state.store(IDLE, Ordering::Release);
        self.state = TicketState::Local(list);
        Ok(())
    }

    pub(crate) fn discard(&mut self) -> Result<(), String> {
        match self.state {
            TicketState::Finished => return Ok(()),
            TicketState::Local(_) => {
                slots_lock(&self.shared).stats.discarded += 1;
                self.state = TicketState::Finished;
                return Ok(());
            }
            TicketState::Pending => {}
        }
        // An old ticket must neither wait for nor clear a newer activation.
        if slots_lock(&self.shared).active != Some(self.key) {
            self.state = TicketState::Finished;
            return Ok(());
        }
        let state = wait_while(REQUESTED, || self.shared.state.load(Ordering::Acquire), "discard drain");
        let mut slots = slots_lock(&self.shared);
        if slots.active != Some(self.key) {
            self.state = TicketState::Finished;
            return Ok(());
        }
        slots.stats.discarded += 1;
        clear_slot(&mut slots);
        self.state = TicketState::Finished;
        if state == COMPLETE {
            self.shared.state.store(IDLE, Ordering::Release);
            Ok(())
        } else { Err(failure(&slots)) }
    }
}

impl Drop for Ticket {
    fn drop(&mut self) {
        if let Err(error) = self.discard() { eprintln!("inventory ticket close failed: {error}"); }
    }
}

pub(crate) struct InventoryWorker { shared: Arc<Shared>, thread: Option<JoinHandle<()>> }

impl InventoryWorker {
    pub(crate) fn start() -> Result<Self, String> { Self::start_with(true) }

    fn start_with(pin: bool) -> Result<Self, String> {
        let shared = Arc::new(Shared {
            state: AtomicU8::new(STARTING), stop: AtomicBool::new(false),
            active_scopes: AtomicUsize::new(0), control: Mutex::new(Control::default()),
            wake: Condvar::new(), slots: Mutex::new(Slots::default()),
            #[cfg(test)]
            hold_generation: AtomicBool::new(false),
            #[cfg(test)]
            fail_next: AtomicBool::new(false),
        });
        let worker_shared = Arc::clone(&shared);
        let thread = thread::Builder::new().name("rook2-inventory-research".into()).spawn(move || {
            let result = std::panic::catch_unwind(|| {
                if pin { pin_worker()?; }
                run_active(&worker_shared)
            });
            let failure = match result {
                Ok(Ok(())) => {
                    worker_shared.state.store(STOPPED, Ordering::Release);
                    worker_shared.wake.notify_all();
                    return;
                }
                Ok(Err(error)) => error,
                Err(_) => "inventory worker panicked".into(),
            };
            let mut control = control_lock(&worker_shared);
            slots_lock(&worker_shared).failure = Some(failure);
            worker_shared.state.store(FAILED, Ordering::Release);
            control.parking = false;
            worker_shared.wake.notify_all();
        }).map_err(|error| format!("cannot start inventory worker: {error}"))?;
        let mut worker = Self { shared, thread: Some(thread) };
        let state = wait_while(STARTING, || worker.shared.state.load(Ordering::Acquire), "startup");
        if state == PARKED { Ok(worker) }
        else {
            let error = failure(&slots_lock(&worker.shared));
            let _ = worker.shutdown();
            Err(error)
        }
    }

    pub(crate) fn start_active_scope(&self) -> Result<InventoryScope, String> {
        let mut control = control_lock(&self.shared);
        let deadline = Instant::now() + WAIT_LIMIT;
        while control.parking && !terminal(&self.shared) {
            control = wait_control(&self.shared, control, deadline, "prior parking");
        }
        if terminal(&self.shared) { return Err(failure(&slots_lock(&self.shared))); }
        let first = control.scopes == 0;
        if first {
            let mut slots = slots_lock(&self.shared);
            slots.epoch = slots.epoch.checked_add(1).expect("inventory activation epoch exhausted");
        }
        control.scopes = control.scopes.checked_add(1).expect("inventory scope count exhausted");
        self.shared.active_scopes.store(control.scopes, Ordering::Release);
        let scope = InventoryScope { shared: Arc::clone(&self.shared), armed: true };
        if first { self.shared.wake.notify_all(); }
        drop(control);
        if first {
            let state = wait_while(PARKED, || self.shared.state.load(Ordering::Acquire), "activation");
            if state != IDLE { return Err(failure(&slots_lock(&self.shared))); }
        }
        Ok(scope)
    }

    pub(crate) fn start_call_scope(&self) -> Result<Option<InventoryScope>, String> {
        if self.shared.active_scopes.load(Ordering::Acquire) != 0 { Ok(None) }
        else { self.start_active_scope().map(Some) }
    }

    /// Caller supplies the admitted coherent ordinary search domain. This
    /// method counts admission and publishes copies, never generates inline.
    pub(crate) fn launch(&self, position: &Position) -> Result<Option<Ticket>, String> {
        if self.shared.active_scopes.load(Ordering::Acquire) == 0 {
            return Err("inventory launch has no active scope".into());
        }
        let mut slots = slots_lock(&self.shared);
        slots.stats.eligible += 1;
        let state = self.shared.state.load(Ordering::Acquire);
        if matches!(state, FAILED | STOPPED) { return Err(failure(&slots)); }
        if slots.active.is_some() || state != IDLE {
            slots.stats.busy += 1;
            return Ok(None);
        }
        let token = slots.next_token;
        slots.next_token = token.checked_add(1).expect("inventory ticket token exhausted");
        let key = Key { token, epoch: slots.epoch, position: *position };
        slots.packet = Some(key);
        slots.active = Some(key);
        slots.stats.launches += 1;
        self.shared.state.store(REQUESTED, Ordering::Release);
        Ok(Some(Ticket { shared: Arc::clone(&self.shared), key, state: TicketState::Pending, missed: false }))
    }

    pub(crate) fn record_fallback(&self, kind: FallbackKind) {
        let mut slots = slots_lock(&self.shared);
        slots.stats.eligible += 1;
        match kind {
            FallbackKind::Domain => slots.stats.domain_skips += 1,
            FallbackKind::Busy => slots.stats.busy += 1,
        }
    }

    pub(crate) fn note_domain_skip(&self) { self.record_fallback(FallbackKind::Domain); }

    pub(crate) fn stats(&self) -> Stats { slots_lock(&self.shared).stats }

    /// Fixed shared data only. Helper-stack/OS storage and the null-settlement
    /// boxes held by live tickets are excluded; null_settles counts allocations.
    pub(crate) fn estimated_bytes(&self) -> usize {
        std::mem::size_of::<Self>() + std::mem::size_of::<Shared>() + 2 * std::mem::size_of::<usize>()
    }

    #[cfg(test)]
    pub(crate) fn is_parked(&self) -> bool {
        self.shared.state.load(Ordering::Acquire) == PARKED
            && self.shared.active_scopes.load(Ordering::Acquire) == 0
    }

    #[cfg(test)]
    pub(crate) fn fail_next(&self) { self.shared.fail_next.store(true, Ordering::Release); }

    pub(crate) fn shutdown(&mut self) -> Result<(), String> {
        let Some(handle) = self.thread.as_ref() else { return Ok(()); };
        wait_while(REQUESTED, || self.shared.state.load(Ordering::Acquire), "shutdown drain");
        {
            let mut control = control_lock(&self.shared);
            let mut slots = slots_lock(&self.shared);
            discard_slot(&mut slots);
            self.shared.stop.store(true, Ordering::Release);
            self.shared.active_scopes.store(0, Ordering::Release);
            control.scopes = 0;
            control.parking = false;
            self.shared.wake.notify_all();
        }
        wait_while(false, || handle.is_finished(), "shutdown");
        let handle = self.thread.take().unwrap();
        if handle.join().is_err() { return Err("inventory worker exited with an uncaught panic".into()); }
        if self.shared.state.load(Ordering::Acquire) == FAILED {
            Err(failure(&slots_lock(&self.shared)))
        } else { Ok(()) }
    }
}

impl Drop for InventoryWorker {
    fn drop(&mut self) {
        if let Err(error) = self.shutdown() { eprintln!("inventory worker shutdown failed: {error}"); }
    }
}

fn copy_inventory(input: &MoveList, output: &mut MoveList) {
    output.moves[..input.len].copy_from_slice(input.as_slice());
    output.len = input.len;
}

fn clear_slot(slots: &mut Slots) {
    slots.active = None;
    slots.packet = None;
    slots.output.clear();
}

fn discard_slot(slots: &mut Slots) {
    if slots.active.is_some() { slots.stats.discarded += 1; }
    clear_slot(slots);
}

fn run_active(shared: &Shared) -> Result<(), String> {
    let mut output = MoveList::new();
    park(shared)?;
    while !shared.stop.load(Ordering::Acquire) {
        if shared.state.load(Ordering::Acquire) != REQUESTED {
            if shared.active_scopes.load(Ordering::Acquire) == 0 { park(shared)?; continue; }
            spin_loop();
            continue;
        }
        let packet = slots_lock(shared).packet.take().ok_or("inventory request has no packet")?;
        #[cfg(test)]
        if shared.fail_next.swap(false, Ordering::AcqRel) { panic!("intentional inventory worker failure"); }
        #[cfg(test)]
        while shared.hold_generation.load(Ordering::Acquire) { spin_loop(); }
        movegen::generate_legal(&packet.position, &mut output);
        {
            let mut slots = slots_lock(shared);
            if slots.active != Some(packet) { return Err("inventory activation changed during generation".into()); }
            copy_inventory(&output, &mut slots.output);
            slots.stats.completed += 1;
        }
        shared.state.store(COMPLETE, Ordering::Release);
    }
    Ok(())
}

fn slots_lock(shared: &Shared) -> MutexGuard<'_, Slots> {
    shared.slots.lock().unwrap_or_else(|error| error.into_inner())
}

fn control_lock(shared: &Shared) -> MutexGuard<'_, Control> {
    shared.control.lock().unwrap_or_else(|error| error.into_inner())
}

fn failure(slots: &Slots) -> String {
    slots.failure.clone().unwrap_or_else(|| "inventory worker entered an invalid state".into())
}

fn terminal(shared: &Shared) -> bool {
    shared.stop.load(Ordering::Acquire) || matches!(shared.state.load(Ordering::Acquire), FAILED | STOPPED)
}

fn release_scope(shared: &Shared) -> Result<(), String> {
    let mut control = control_lock(shared);
    if shared.stop.load(Ordering::Acquire) { return Ok(()); }
    assert!(control.scopes != 0, "inventory scope released twice");
    control.scopes -= 1;
    shared.active_scopes.store(control.scopes, Ordering::Release);
    if control.scopes != 0 { return Ok(()); }
    control.parking = true;
    let deadline = Instant::now() + WAIT_LIMIT;
    while control.parking && !terminal(shared) {
        control = wait_control(shared, control, deadline, "parking");
    }
    if matches!(shared.state.load(Ordering::Acquire), FAILED | STOPPED) {
        return Err(failure(&slots_lock(shared)));
    }
    Ok(())
}

fn park(shared: &Shared) -> Result<(), String> {
    let mut control = control_lock(shared);
    if control.scopes != 0 { return Ok(()); }
    discard_slot(&mut slots_lock(shared));
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
        eprintln!("inventory worker {phase} exceeded {WAIT_LIMIT:?}; aborting");
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
                eprintln!("inventory worker {phase} exceeded {WAIT_LIMIT:?}; aborting");
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
        return Err(format!("cannot pin inventory worker to CPU{WORKER_CPU}: {}", std::io::Error::last_os_error()));
    }
    let mut actual = [0u64; 16];
    if unsafe { sched_getaffinity(0, std::mem::size_of_val(&actual), actual.as_mut_ptr()) } != 0 {
        return Err(format!("cannot verify inventory worker affinity: {}", std::io::Error::last_os_error()));
    }
    if actual != mask { return Err(format!("inventory worker affinity differs from CPU{WORKER_CPU}")); }
    Ok(())
}

#[cfg(not(target_os = "linux"))]
fn pin_worker() -> Result<(), String> { Err("inventory worker requires Linux CPU6 affinity".into()) }

#[cfg(test)]
mod tests {
    use super::*;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn position() -> Position { Position::from_fen(START).unwrap() }

    fn worker() -> InventoryWorker {
        let worker = InventoryWorker::start_with(false).unwrap();
        assert!(worker.is_parked());
        worker
    }

    fn await_ready(worker: &InventoryWorker) {
        assert_eq!(wait_while(REQUESTED, || worker.shared.state.load(Ordering::Acquire), "test ready"), COMPLETE);
    }

    fn accounting(worker: &InventoryWorker) {
        let stats = worker.stats();
        assert_eq!(stats.launches, stats.completed);
        assert_eq!(stats.launches, stats.consumed + stats.discarded);
        assert_eq!(stats.consumed, stats.ready_consumed + stats.local_consumed);
        assert_eq!(stats.null_settles, stats.null_ready + stats.null_waited);
        assert_eq!(stats.eligible, stats.launches + stats.domain_skips + stats.busy);
    }

    #[test]
    fn exact_native_inventory_order_across_ordinary_special_and_checked_positions() {
        let worker = worker();
        let scope = worker.start_active_scope().unwrap();
        let mut out = MoveList::new();
        for fen in [START,
            "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
            "7k/8/8/3pP3/8/8/8/K7 w - d6 0 1",
            "7k/P7/8/8/8/8/7p/K7 w - - 0 1",
            "7k/8/8/8/8/8/4r3/4K3 w - - 0 1",
        ] {
            let position = Position::from_fen(fen).unwrap();
            let mut expected = MoveList::new();
            movegen::generate_legal(&position, &mut expected);
            let mut ticket = worker.launch(&position).unwrap().unwrap();
            await_ready(&worker);
            assert!(ticket.consume_into(&mut out).unwrap());
            assert_eq!(out.as_slice(), expected.as_slice());
            assert!(!ticket.consume_into(&mut out).unwrap());
        }
        scope.finish().unwrap();
        assert!(worker.is_parked());
        accounting(&worker);
    }

    #[test]
    fn readiness_miss_stays_miss_then_inline_result_survives_discard() {
        let worker = worker();
        let scope = worker.start_active_scope().unwrap();
        worker.shared.hold_generation.store(true, Ordering::Release);
        let position = position();
        let mut ticket = worker.launch(&position).unwrap().unwrap();
        let mut out = MoveList::new();
        assert!(!ticket.consume_into(&mut out).unwrap());
        movegen::generate_legal(&position, &mut out);
        let expected = out.as_slice().to_vec();
        worker.shared.hold_generation.store(false, Ordering::Release);
        await_ready(&worker);
        assert!(!ticket.consume_into(&mut out).unwrap());
        ticket.discard().unwrap();
        assert_eq!(out.as_slice(), expected.as_slice());
        assert_eq!(worker.stats().ready_miss, 1);
        assert_eq!(worker.stats().discarded, 1);
        drop(scope);
        accounting(&worker);
    }

    #[test]
    fn null_settlement_releases_slot_for_nested_work_and_keeps_parent_owned() {
        let worker = worker();
        let scope = worker.start_active_scope().unwrap();
        let position = position();
        let mut parent = worker.launch(&position).unwrap().unwrap();
        assert!(worker.launch(&position).unwrap().is_none());
        parent.settle_for_null().unwrap();
        let nested = worker.start_active_scope().unwrap();
        let child_position = position.null_child();
        let mut child = worker.launch(&child_position).unwrap().unwrap();
        await_ready(&worker);
        let mut out = MoveList::new();
        assert!(child.consume_into(&mut out).unwrap());
        let mut expected = MoveList::new();
        movegen::generate_legal(&child_position, &mut expected);
        assert_eq!(out.as_slice(), expected.as_slice());
        drop(nested);
        assert!(parent.consume_into(&mut out).unwrap());
        movegen::generate_legal(&position, &mut expected);
        assert_eq!(out.as_slice(), expected.as_slice());
        let stats = worker.stats();
        assert_eq!((stats.null_settles, stats.local_consumed, stats.ready_consumed), (1, 1, 1));
        worker.note_domain_skip();
        drop(scope);
        accounting(&worker);
    }

    #[test]
    fn old_ticket_drop_cannot_clear_new_job_and_local_output_cannot_cross_root() {
        let worker = worker();
        let position = position();
        let old_scope = worker.start_active_scope().unwrap();
        let old = worker.launch(&position).unwrap().unwrap();
        drop(old_scope); // Parks, drains, and accounts the still-live ticket.
        assert!(worker.is_parked());
        let current_scope = worker.start_active_scope().unwrap();
        worker.shared.hold_generation.store(true, Ordering::Release);
        let mut current = worker.launch(&position).unwrap().unwrap();
        let current_key = current.key;
        drop(old);
        assert!(slots_lock(&worker.shared).active == Some(current_key));
        worker.shared.hold_generation.store(false, Ordering::Release);
        await_ready(&worker);
        assert!(current.consume_into(&mut MoveList::new()).unwrap());
        let mut local = worker.launch(&position).unwrap().unwrap();
        local.settle_for_null().unwrap();
        drop(current_scope);
        let next_scope = worker.start_active_scope().unwrap();
        assert!(local.consume_into(&mut MoveList::new()).is_err());
        drop(local);
        drop(next_scope);
        accounting(&worker);
    }

    #[test]
    fn early_drop_unwind_and_shutdown_drain_without_double_accounting() {
        let mut worker = worker();
        let scope = worker.start_active_scope().unwrap();
        let position = position();
        drop(worker.launch(&position).unwrap().unwrap());
        let unwound = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _ticket = worker.launch(&position).unwrap().unwrap();
            panic!("intentional inventory early exit");
        }));
        assert!(unwound.is_err());
        let ticket = worker.launch(&position).unwrap().unwrap();
        worker.shutdown().unwrap();
        drop(ticket);
        scope.finish().unwrap();
        assert!(worker.thread.is_none());
        accounting(&worker);
    }

    #[test]
    fn worker_failure_never_supplies_partial_inventory() {
        let mut worker = worker();
        let scope = worker.start_active_scope().unwrap();
        worker.fail_next();
        let mut ticket = worker.launch(&position()).unwrap().unwrap();
        let state = wait_while(REQUESTED, || worker.shared.state.load(Ordering::Acquire), "test failure");
        assert_eq!(state, FAILED);
        let mut out = MoveList::new();
        assert!(ticket.consume_into(&mut out).is_err());
        assert!(out.as_slice().is_empty());
        assert!(ticket.discard().is_err());
        assert!(worker.shutdown().is_err());
        scope.finish().unwrap();
    }
}
