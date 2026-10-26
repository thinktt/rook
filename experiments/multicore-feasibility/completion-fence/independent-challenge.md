# Completion fence challenge — 2026-10-26

Sender: `/root/completion_fence_challenge`
Recipient: imp2-lead

Source/memory-model review only: unselected research, no implementation, builds, tests, engine runs, native measurements, or Git mutations. Authority: [retained positive64 source](/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01/src/colors_worker.rs:650), especially publication at 567/704 and waiting at 660–688.

**Verdict: the publisher-only fence variant admits a lost wake. The permitted additional cold-side SC fence makes this alternative sound under the stated invariants. Include that fence in any future discriminator.** This conclusion is an ordering argument, not a runtime result or implementation approval.

[Rust specifies C++20 atomic rules](https://doc.rust-lang.org/std/sync/atomic/index.html#memory-model-for-atomic-accesses). The relevant distinction is that an SC RMW is not an SC fence for ordering a later non-SC predicate read against another thread's publication. [C++20 atomics.order ¶3–5](https://timsong-cpp.github.io/cppwp/n4861/atomics.order#4) supplies the coherence/SC-fence constraints used below.

Initially `W=false`, `done_i=0`, target `g=1`. Here is a permitted abstract execution **without** the cold fence; arrows denote each thread's program order:

```text
Publisher i: D_i = done_i.store(1, Release)
             -> F_i = fence(SeqCst)
             -> L_i = W.load(SeqCst) reads initial false; skips Sleep
Waiter:      lock Sleep -> R = W.swap(true, SeqCst)
             -> stop.load(Acquire) reads false
             -> Q = done_0.load(Acquire) reads initial 0
             -> Condvar.wait(Sleep)
SC order:    F_0 < L_0 < F_1 < L_1 < R
```

Both publishers skip notification. `Q` is coherence-ordered before `D_0`, but no SC fence precedes `Q`, so that relationship imposes no opposite SC-order constraint. No publisher-to-waiter synchronization carries either done store. This satisfies atomic coherence and SC ordering; it is not a claim about a sequential interleaving on x86. The waiter may sleep indefinitely without a spurious wake. Conditional Sleep locking cannot rescue a path that never acquires Sleep.

Smallest sound change within the requested envelope, retaining the existing spin phase, Acquire predicates, SC registration/clear, and poison recovery:

```text
signal_completion():                 // after EVERY done/terminal publication
    fence(SeqCst)                    // unconditional, after dropping Control
    if waiting.load(SeqCst):
        lock Sleep
        completed.notify_all()
        unlock Sleep

cold_wait(g):
    lock Sleep
    loop:
        waiting.swap(true, SeqCst)    // R
        fence(SeqCst)                // F_w, on EVERY iteration
        stopped = stop.load(Acquire)
        done = both_done(g)          // existing Acquire loads
        if stopped or done:
            waiting.swap(false, SeqCst)
            unlock Sleep
            return existing result
        Condvar.wait(Sleep)          // atomically unlock/block, then reacquire
```

Proof for one attempted sleep: choose a publication `D` missed by that iteration's predicate read `Q`. For done, choose the first missing reader; short-circuiting `both_done` is harmless. No later epoch can overwrite its done while this coordinator is waiting. For terminal, false precedes every true store; stop never resets. Thus `Q` is coherence-ordered before `D`. Since `F_w` precedes `Q` and `D` precedes its publisher fence `F_p`, the SC-fence rule requires:

```text
R <S F_w <S F_p <S L
```

After initialization, only the waiter modifies W, using SC operations. Therefore `L` cannot read a false value preceding `R`. Until the waiter exits, every subsequent registration writes true. Consequently this publisher reads true and owes a notification, or reads a later exit-clear, in which case that wait has already resolved. Equivalently, a publisher that checked false before registration cannot have its publication missed by the fenced recheck.

After a true load, **always acquire Sleep and notify**. The waiter holds Sleep throughout registration/recheck; the publisher cannot notify in the check-to-wait gap. If notification precedes a later registration, the publisher's Sleep unlock and waiter's subsequent lock/reacquisition carry the publication to that recheck. [Condvar::wait atomically releases and blocks and allows spurious wakes](https://doc.rust-lang.org/std/sync/struct.Condvar.html#method.wait); repeated fenced rechecks handle those wakes. SC order alone is not a publication happens-before edge.

The same argument applies independently to both helpers and every terminal publisher. They may both observe true and both lock/notify; duplicate notifications are harmless. No publisher clears W or consumes another publisher's wake obligation. Delayed prior-epoch fence/load work can only skip an unnecessary notification or issue an extra one. A delayed true-load notification may follow exit or wake a later epoch; its unconditional Sleep acquisition remains safe, and that later epoch retains its own publication handshake.

Concurrent final close still claims Discarding under Control and waits for real quiescence. No Control/Sleep nesting is introduced. Waiter exit clears W before releasing Sleep; outstanding notifiers remain protected by existing Shared lifetimes and joined shutdown. A terminal wake does not retire either reader or authorize output access. Matching done Acquire loads, existing Control checks, and the next request Release/Acquire retain the ownership proof unchanged. Progress still requires publishers to finish signaling and threads to acquire mutexes/run; atomics provide no scheduling-delay bound.

One future bounded comparison is architecturally warranted: retained RMW protocol versus this protocol **with both fences**, with arithmetic/ownership, owner work, layout, placement, spin4096/sample512 and existing observation policy fixed. Removing publisher writes to W might reduce ownership traffic; fence cost, stop sharing/polling, and duplicate cold notifications may erase any benefit. No codegen or performance conclusion follows here.

Adapt only the existing registration/spurious-wake, terminal, and prior-epoch-delay controls: update their RMW-chain assumptions; place the post-registration gate after the new fence; add a narrow pause after a true publisher load and before Sleep acquisition to cover dual notifiers and delayed notification across exit/re-registration. Retain close/drain and numerical controls. These controls supplement the proof; synchronization in test gates cannot demonstrate exclusion of the abstract counterexample above. No sweep or new framework is warranted.
