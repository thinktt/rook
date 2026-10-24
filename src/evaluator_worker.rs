//! Narrow research-only Activity -> Shelter worker for confirmed FULL calls.
//!
//! Packet and result slots are reusable owned storage, never borrowed from a
//! caller's stack. Successful dispatch/complete allocate no memory or threads.
//! The worker busy-spins for its entire lifetime, including idle search periods.

use crate::activity::{self, Activity};
use crate::influence::Influence;
use crate::position::Position;
use crate::shelter::{self, Shelter};
use std::hint::spin_loop;
use std::sync::atomic::{AtomicBool, AtomicU8, Ordering};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

const STARTING: u8 = 0;
const IDLE: u8 = 1;
const REQUESTED: u8 = 2;
const COMPLETE: u8 = 3;
const FAILED: u8 = 4;
const STOPPED: u8 = 5;
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
    slots: Mutex<Slots>,
}

pub(crate) struct ActivityShelterWorker {
    shared: Arc<Shared>,
    thread: Option<JoinHandle<()>>,
}

impl ActivityShelterWorker {
    pub(crate) fn start() -> Result<Self, String> {
        let shared = Arc::new(Shared {
            state: AtomicU8::new(STARTING),
            stop: AtomicBool::new(false),
            slots: Mutex::new(Slots::default()),
        });
        let worker_shared = Arc::clone(&shared);
        let thread = thread::Builder::new()
            .name("rook2-eval-research".into())
            .spawn(move || {
                let result = std::panic::catch_unwind(|| run(&worker_shared));
                let failure = match result {
                    Ok(Ok(())) => {
                        worker_shared.state.store(STOPPED, Ordering::Release);
                        return;
                    }
                    Ok(Err(error)) => error,
                    Err(_) => "Activity/Shelter worker panicked".into(),
                };
                // Recover a poisoned slot only to report terminal failure. There
                // is no job recovery or fallback to a different computation.
                worker_shared
                    .slots
                    .lock()
                    .unwrap_or_else(|e| e.into_inner())
                    .failure = Some(failure);
                worker_shared.state.store(FAILED, Ordering::Release);
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
        if state == IDLE {
            Ok(worker)
        } else {
            let failure = worker.failure();
            let _ = worker.shutdown();
            Err(failure)
        }
    }

    pub(crate) fn dispatch(
        &mut self,
        position: &Position,
        influence: &Influence,
        material: i32,
        mobility_weights: [i32; 2],
        shelter_weights: [i32; 2],
    ) -> Result<(), String> {
        if self.shared.state.load(Ordering::Acquire) != IDLE {
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
        self.shared.stop.store(true, Ordering::Release);
        wait_while(false, || handle.is_finished(), "shutdown");
        let handle = self.thread.take().unwrap();
        if handle.join().is_err() {
            return Err("Activity/Shelter worker exited with an uncaught panic".into());
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
    shared.state.store(IDLE, Ordering::Release);
    while !shared.stop.load(Ordering::Acquire) {
        if shared.state.load(Ordering::Acquire) != REQUESTED {
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
