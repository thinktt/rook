//! Bounded pure child preparation; search and all semantic charges stay on the
//! coordinator. One scope publishes at most six owned jobs, with no refill.

use crate::evaluator_worker::{self, ActivityShelter};
use crate::influence::Influence;
use crate::position::Position;
use std::sync::{Arc, Condvar, Mutex, MutexGuard};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

pub(crate) const CAPACITY: usize = 6;
const WORKER_CPUS: [usize; 3] = [6, 4, 2];
const WORKER_STACK_BYTES: usize = 256 * 1024;
const WAIT_LIMIT: Duration = Duration::from_secs(10);

/// Producer precondition: a canonical legal ordinary child from the guarded
/// search domain. Material and weights are the current root-bound values, not
/// defaults or weights rebound to the child's moving side.
#[derive(Clone, Copy)]
pub(crate) struct Job {
    pub position: Position,
    pub material: i32,
    pub mobility_weights: [i32; 2],
    pub shelter_weights: [i32; 2],
    pub coherent: bool,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub(crate) struct Stats {
    pub scopes_started: u64,
    pub scopes_blocked: u64,
    pub published: u64,
    pub started: u64,
    /// Includes kernels finishing after their scope was cancelled.
    pub completed: u64,
    pub map_demands: u64,
    pub chain_demands: u64,
    pub map_uses: u64,
    pub chain_uses: u64,
    pub unique_map_used: u64,
    pub unique_chain_used: u64,
    pub unique_any_used: u64,
    /// Exact child found, but its output was not ready at this demand.
    pub not_ready: u64,
    /// Ready child found, but authoritative map/material/weights differed.
    pub mismatched: u64,
    /// Started jobs closed without consuming either output.
    pub discarded: u64,
    /// Started jobs closed without consuming their Activity/Shelter output.
    pub chain_discarded: u64,
    /// Published jobs cancelled before a worker started them.
    pub cancelled: u64,
    pub stale_completed: u64,
    pub worker_failures: u64,
    pub max_queue: usize,
}

impl Stats {
    pub(crate) fn json(self) -> String {
        format!(
            concat!(
                "{{\"scopes_started\":{},\"scopes_blocked\":{},\"published\":{},",
                "\"started\":{},\"completed\":{},\"map_demands\":{},\"chain_demands\":{},",
                "\"map_uses\":{},\"chain_uses\":{},\"unique_map_used\":{},",
                "\"unique_chain_used\":{},\"unique_any_used\":{},\"not_ready\":{},",
                "\"mismatched\":{},\"discarded\":{},\"chain_discarded\":{},",
                "\"cancelled\":{},\"stale_completed\":{},\"worker_failures\":{},\"max_queue\":{}}}"
            ),
            self.scopes_started, self.scopes_blocked, self.published,
            self.started, self.completed, self.map_demands, self.chain_demands,
            self.map_uses, self.chain_uses, self.unique_map_used,
            self.unique_chain_used, self.unique_any_used, self.not_ready,
            self.mismatched, self.discarded, self.chain_discarded,
            self.cancelled, self.stale_completed, self.worker_failures, self.max_queue,
        )
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Phase { Pending, Running, Ready }

struct Slot {
    token: u64,
    job: Job,
    phase: Phase,
    cancelled: bool,
    map: Option<Influence>,
    chain: Option<ActivityShelter>,
    map_used: bool,
    chain_used: bool,
}

struct State {
    slots: [Option<Slot>; CAPACITY],
    active: Option<u64>,
    next_token: u64,
    ready_workers: usize,
    stopping: bool,
    failure: Option<String>,
    stats: Stats,
}

impl State {
    fn new() -> Self {
        Self {
            slots: std::array::from_fn(|_| None), active: None, next_token: 1,
            ready_workers: 0, stopping: false, failure: None, stats: Stats::default(),
        }
    }
}

struct Shared { state: Mutex<State>, wake: Condvar }

impl Shared {
    fn new() -> Self {
        Self { state: Mutex::new(State::new()), wake: Condvar::new() }
    }

    fn lock(&self) -> MutexGuard<'_, State> {
        self.state.lock().unwrap_or_else(|error| error.into_inner())
    }
}

/// Holds no evaluator/search borrow. Early return, stop propagation and unwind
/// all cancel exactly this token; dropping an old guard cannot cancel a new one.
pub(crate) struct ScopeGuard { shared: Arc<Shared>, token: u64 }

impl ScopeGuard {
    pub(crate) fn token(&self) -> u64 { self.token }
}

impl Drop for ScopeGuard {
    fn drop(&mut self) {
        cancel(&mut self.shared.lock(), self.token);
        self.shared.wake.notify_all();
    }
}

pub(crate) struct ChildPreparation {
    shared: Arc<Shared>,
    threads: Vec<JoinHandle<()>>,
}

impl ChildPreparation {
    /// The caller reserves the coordinator separately. Budgets two and four
    /// use one and three helpers respectively; there is no nested FULL worker.
    pub(crate) fn start(workers: usize) -> Result<Self, String> {
        if !matches!(workers, 1 | 3) {
            return Err("child preparation needs one or three helpers".into());
        }
        let mut pool = Self { shared: Arc::new(Shared::new()), threads: Vec::with_capacity(workers) };
        for &cpu in &WORKER_CPUS[..workers] {
            let shared = Arc::clone(&pool.shared);
            let thread = thread::Builder::new()
                .name(format!("rook2-child-prep-{cpu}"))
                .stack_size(WORKER_STACK_BYTES)
                .spawn(move || {
                    let result = std::panic::catch_unwind(|| run(&shared, cpu));
                    let failure = match result {
                        Ok(Ok(())) => return,
                        Ok(Err(error)) => error,
                        Err(_) => "child preparation worker panicked".into(),
                    };
                    let mut state = shared.lock();
                    state.stats.worker_failures += 1;
                    state.failure.get_or_insert(failure);
                    state.stopping = true;
                    if let Some(token) = state.active { cancel(&mut state, token); }
                    drop(state);
                    shared.wake.notify_all();
                })
                .map_err(|error| format!("cannot start child preparation worker: {error}"))?;
            pool.threads.push(thread);
        }
        let deadline = Instant::now() + WAIT_LIMIT;
        let mut state = pool.shared.lock();
        while state.ready_workers < workers && state.failure.is_none() {
            let remaining = deadline.saturating_duration_since(Instant::now());
            if remaining.is_zero() { break; }
            state = pool.shared.wake.wait_timeout(state, remaining)
                .unwrap_or_else(|error| error.into_inner()).0;
        }
        let failure = state.failure.clone().or_else(|| {
            (state.ready_workers != workers).then(|| "child preparation startup timed out".into())
        });
        drop(state);
        if let Some(error) = failure {
            let _ = pool.shutdown();
            Err(error)
        } else {
            Ok(pool)
        }
    }

    /// Publishes the first six eligible jobs into currently free slots. A
    /// cancelled running job retains its slot until it finishes, keeping the
    /// complete pool bounded to six outstanding jobs across scope changes.
    pub(crate) fn begin(&self, jobs: Vec<Job>) -> Option<ScopeGuard> {
        let mut state = self.shared.lock();
        if state.stopping || state.active.is_some() {
            state.stats.scopes_blocked += 1;
            return None;
        }
        let token = state.next_token;
        state.next_token = token.checked_add(1).expect("child preparation scope token exhausted");
        let mut jobs = jobs.into_iter().filter(|job| job.coherent).take(CAPACITY);
        let mut published = 0;
        for slot in &mut state.slots {
            if slot.is_some() { continue; }
            let Some(job) = jobs.next() else { break; };
            *slot = Some(Slot {
                token, job, phase: Phase::Pending, cancelled: false,
                map: None, chain: None, map_used: false, chain_used: false,
            });
            published += 1;
        }
        if published == 0 { return None; }
        state.active = Some(token);
        state.stats.scopes_started += 1;
        state.stats.published += published;
        let queued = state.slots.iter().flatten().filter(|slot| slot.phase == Phase::Pending).count();
        state.stats.max_queue = state.stats.max_queue.max(queued);
        drop(state);
        self.shared.wake.notify_all();
        Some(ScopeGuard { shared: Arc::clone(&self.shared), token })
    }

    pub(crate) fn active_token(&self) -> Option<u64> { self.shared.lock().active }

    /// Called only at the original scratch-is-None map-production boundary.
    /// It never credits an influence build; that remains the caller's action.
    pub(crate) fn take_map(&self, position: &Position) -> Option<Influence> {
        let mut state = self.shared.lock();
        let index = matching(&state, position)?;
        state.stats.map_demands += 1;
        let slot = state.slots[index].as_ref().unwrap();
        if slot.phase != Phase::Ready {
            state.stats.not_ready += 1;
            return None;
        }
        let map = slot.map?;
        let first_map = !slot.map_used;
        let first_any = !slot.map_used && !slot.chain_used;
        state.slots[index].as_mut().unwrap().map_used = true;
        state.stats.map_uses += 1;
        state.stats.unique_map_used += u64::from(first_map);
        state.stats.unique_any_used += u64::from(first_any);
        Some(map)
    }

    /// A supplied Influence is authoritative. Mismatched ready results are
    /// retained for another exact demand, but never replace supplied inputs.
    pub(crate) fn take_chain(
        &self, position: &Position, influence: &Influence, material: i32,
        mobility_weights: [i32; 2], shelter_weights: [i32; 2],
    ) -> Option<ActivityShelter> {
        let mut state = self.shared.lock();
        let index = matching(&state, position)?;
        state.stats.chain_demands += 1;
        let slot = state.slots[index].as_ref().unwrap();
        if slot.phase != Phase::Ready {
            state.stats.not_ready += 1;
            return None;
        }
        if slot.map.as_ref() != Some(influence) || slot.job.material != material
            || slot.job.mobility_weights != mobility_weights || slot.job.shelter_weights != shelter_weights
        {
            state.stats.mismatched += 1;
            return None;
        }
        let chain = slot.chain?;
        let first_chain = !slot.chain_used;
        let first_any = !slot.map_used && !slot.chain_used;
        state.slots[index].as_mut().unwrap().chain_used = true;
        state.stats.chain_uses += 1;
        state.stats.unique_chain_used += u64::from(first_chain);
        state.stats.unique_any_used += u64::from(first_any);
        Some(chain)
    }

    pub(crate) fn reset(&self) {
        let mut state = self.shared.lock();
        if let Some(token) = state.active { cancel(&mut state, token); }
        drop(state);
        self.shared.wake.notify_all();
    }

    pub(crate) fn stats(&self) -> Stats { self.shared.lock().stats }

    pub(crate) fn failure(&self) -> Option<String> { self.shared.lock().failure.clone() }

    /// Includes fixed owned slots and requested helper stack reservations;
    /// excludes allocator/thread/OS bookkeeping and the coordinator's stack.
    pub(crate) fn estimated_bytes(&self) -> usize {
        std::mem::size_of::<Self>() + std::mem::size_of::<Shared>()
            + 2 * std::mem::size_of::<usize>()
            + self.threads.capacity() * std::mem::size_of::<JoinHandle<()>>()
            + self.threads.len() * WORKER_STACK_BYTES
    }

    pub(crate) fn shutdown(&mut self) -> Result<(), String> {
        {
            let mut state = self.shared.lock();
            state.stopping = true;
            if let Some(token) = state.active { cancel(&mut state, token); }
        }
        self.shared.wake.notify_all();
        let deadline = Instant::now() + WAIT_LIMIT;
        while self.threads.iter().any(|thread| !thread.is_finished()) {
            if Instant::now() >= deadline {
                eprintln!("child preparation shutdown exceeded {WAIT_LIMIT:?}; aborting");
                std::process::abort();
            }
            thread::sleep(Duration::from_millis(1));
        }
        for thread in self.threads.drain(..) {
            if thread.join().is_err() {
                return Err("child preparation worker exited with an uncaught panic".into());
            }
        }
        match self.failure() { Some(error) => Err(error), None => Ok(()) }
    }
}

impl Drop for ChildPreparation {
    fn drop(&mut self) {
        if let Err(error) = self.shutdown() {
            eprintln!("child preparation shutdown failed: {error}");
        }
    }
}

fn matching(state: &State, position: &Position) -> Option<usize> {
    if state.stopping { return None; }
    let token = state.active?;
    state.slots.iter().position(|slot| slot.as_ref().is_some_and(|slot| {
        slot.token == token && !slot.cancelled && slot.job.position == *position
    }))
}

fn cancel(state: &mut State, token: u64) {
    if state.active != Some(token) { return; }
    state.active = None;
    for slot in &mut state.slots {
        let Some(job) = slot.as_mut().filter(|slot| slot.token == token) else { continue; };
        if job.phase == Phase::Pending {
            state.stats.cancelled += 1;
        } else {
            state.stats.discarded += u64::from(!job.map_used && !job.chain_used);
            state.stats.chain_discarded += u64::from(!job.chain_used);
        }
        if job.phase == Phase::Running {
            job.cancelled = true;
        } else {
            *slot = None;
        }
    }
}

fn claim(state: &mut State) -> Option<(usize, u64, Job)> {
    let token = state.active?;
    let index = state.slots.iter().position(|slot| slot.as_ref().is_some_and(|slot| {
        slot.token == token && slot.phase == Phase::Pending && !slot.cancelled
    }))?;
    let slot = state.slots[index].as_mut().unwrap();
    slot.phase = Phase::Running;
    state.stats.started += 1;
    Some((index, token, slot.job))
}

fn complete(state: &mut State, index: usize, token: u64, map: Influence, chain: ActivityShelter) {
    state.stats.completed += 1;
    let live = state.active == Some(token) && !state.stopping;
    if let Some(slot) = state.slots[index].as_mut().filter(|slot| slot.token == token) {
        if live && !slot.cancelled {
            slot.map = Some(map);
            slot.chain = Some(chain);
            slot.phase = Phase::Ready;
            return;
        }
        state.slots[index] = None;
    }
    state.stats.stale_completed += 1;
}

fn run(shared: &Shared, cpu: usize) -> Result<(), String> {
    pin_worker(cpu)?;
    let mut state = shared.lock();
    state.ready_workers += 1;
    shared.wake.notify_all();
    loop {
        if state.stopping { return Ok(()); }
        let Some((index, token, job)) = claim(&mut state) else {
            state = shared.wake.wait(state).unwrap_or_else(|error| error.into_inner());
            continue;
        };
        drop(state);
        let map = Influence::build_coherent(&job.position);
        let chain = evaluator_worker::compute(
            &job.position, &map, job.material, job.mobility_weights, job.shelter_weights,
        );
        state = shared.lock();
        complete(&mut state, index, token, map, chain);
    }
}

#[cfg(target_os = "linux")]
fn pin_worker(cpu: usize) -> Result<(), String> {
    extern "C" {
        fn sched_setaffinity(pid: i32, bytes: usize, mask: *const u64) -> i32;
        fn sched_getaffinity(pid: i32, bytes: usize, mask: *mut u64) -> i32;
    }
    let mut mask = [0u64; 16];
    mask[cpu / 64] = 1 << (cpu % 64);
    // Linux pid zero selects this helper. Both masks cover exactly 128 bytes.
    if unsafe { sched_setaffinity(0, std::mem::size_of_val(&mask), mask.as_ptr()) } != 0 {
        return Err(format!("cannot pin child preparation helper to CPU{cpu}: {}", std::io::Error::last_os_error()));
    }
    let mut actual = [0u64; 16];
    if unsafe { sched_getaffinity(0, std::mem::size_of_val(&actual), actual.as_mut_ptr()) } != 0 {
        return Err(format!("cannot verify child preparation helper affinity: {}", std::io::Error::last_os_error()));
    }
    if actual != mask {
        return Err(format!("child preparation helper affinity differs from CPU{cpu}"));
    }
    Ok(())
}

#[cfg(not(target_os = "linux"))]
fn pin_worker(_cpu: usize) -> Result<(), String> {
    Err("child preparation requires Linux helper affinity".into())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::activity::Activity;
    use crate::shelter::Shelter;

    fn pool() -> ChildPreparation {
        ChildPreparation { shared: Arc::new(Shared::new()), threads: Vec::new() }
    }

    fn job() -> Job {
        Job {
            position: Position::from_fen("7k/8/8/8/8/8/P7/K7 w - - 0 1").unwrap(),
            material: 73, mobility_weights: [1024, 777], shelter_weights: [900, 1234], coherent: true,
        }
    }

    fn ready(pool: &ChildPreparation) -> (Influence, ActivityShelter) {
        let map = Influence { profiles: [[0; 64]; 2] };
        let chain = ActivityShelter { activity: Activity::default(), shelter: Shelter::default() };
        let mut state = pool.shared.lock();
        let (index, token, _) = claim(&mut state).unwrap();
        complete(&mut state, index, token, map, chain);
        (map, chain)
    }

    #[test]
    fn capped_scope_guard_cancels_and_old_guard_cannot_cancel_new_scope() {
        let pool = pool();
        let old = pool.begin(vec![job(); CAPACITY + 2]).unwrap();
        assert_eq!(pool.stats().published, CAPACITY as u64);
        assert_eq!(pool.stats().max_queue, CAPACITY);
        assert!(pool.begin(vec![job()]).is_none());
        pool.reset();
        assert_eq!(pool.stats().cancelled, CAPACITY as u64);
        let current = pool.begin(vec![job()]).unwrap();
        assert_ne!(old.token(), current.token());
        drop(old);
        assert_eq!(pool.active_token(), Some(current.token()));
        drop(current);
        assert_eq!(pool.active_token(), None);
    }

    #[test]
    fn outputs_are_reusable_and_require_exact_authoritative_inputs() {
        let pool = pool();
        let job = job();
        let scope = pool.begin(vec![job]).unwrap();
        assert!(pool.take_map(&job.position).is_none());
        let (map, chain) = ready(&pool);
        assert_eq!(pool.take_map(&job.position), Some(map));
        assert_eq!(pool.take_map(&job.position), Some(map));
        let contrary = Influence { profiles: [[1; 64]; 2] };
        assert!(pool.take_chain(&job.position, &contrary, job.material,
            job.mobility_weights, job.shelter_weights).is_none());
        assert!(pool.take_chain(&job.position, &map, job.material + 1,
            job.mobility_weights, job.shelter_weights).is_none());
        assert!(pool.take_chain(&job.position, &map, job.material,
            [1, 2], job.shelter_weights).is_none());
        assert!(pool.take_chain(&job.position, &map, job.material,
            job.mobility_weights, [1, 2]).is_none());
        for _ in 0..2 {
            let actual = pool.take_chain(&job.position, &map, job.material,
                job.mobility_weights, job.shelter_weights).unwrap();
            assert_eq!(actual.activity, chain.activity);
            assert_eq!(actual.shelter, chain.shelter);
        }
        let mut different_position = job.position;
        different_position.halfmove += 1;
        assert!(pool.take_map(&different_position).is_none());
        let stats = pool.stats();
        assert_eq!((stats.map_uses, stats.chain_uses), (2, 2));
        assert_eq!((stats.unique_map_used, stats.unique_chain_used, stats.unique_any_used), (1, 1, 1));
        assert_eq!((stats.map_demands, stats.chain_demands, stats.not_ready, stats.mismatched), (3, 6, 1, 4));
        drop(scope);
        assert_eq!((pool.stats().discarded, pool.stats().chain_discarded), (0, 0));
    }

    #[test]
    fn cancelled_running_slots_remain_bounded_and_discard_late_output() {
        let pool = pool();
        let old = pool.begin(vec![job(); CAPACITY]).unwrap();
        let (index, token, _) = claim(&mut pool.shared.lock()).unwrap();
        drop(old);
        assert_eq!((pool.stats().cancelled, pool.stats().discarded), (5, 1));
        let current = pool.begin(vec![job(); CAPACITY]).unwrap();
        assert_eq!(pool.stats().published, 11);
        let map = Influence { profiles: [[0; 64]; 2] };
        let chain = ActivityShelter { activity: Activity::default(), shelter: Shelter::default() };
        complete(&mut pool.shared.lock(), index, token, map, chain);
        assert_eq!(pool.stats().stale_completed, 1);
        assert_eq!(pool.active_token(), Some(current.token()));
        assert!(pool.take_map(&job().position).is_none());
    }

    #[test]
    fn reset_invalidates_ready_outputs_and_unwind_drops_scope() {
        let pool = pool();
        let old = pool.begin(vec![job()]).unwrap();
        ready(&pool);
        pool.reset();
        assert!(pool.take_map(&job().position).is_none());
        assert_eq!((pool.stats().discarded, pool.stats().chain_discarded), (1, 1));
        let current = pool.begin(vec![job()]).unwrap();
        drop(old);
        assert_eq!(pool.active_token(), Some(current.token()));
        drop(current);
        let unwound = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _scope = pool.begin(vec![job()]).unwrap();
            panic!("intentional scope unwind");
        }));
        assert!(unwound.is_err());
        assert_eq!(pool.active_token(), None);
        assert!(pool.begin(vec![job()]).is_some());
    }
}
