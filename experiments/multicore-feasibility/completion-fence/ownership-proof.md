# Two-fence completion notification

This changes notification only in exact Q source68. The independent challenge is
preserved as `independent-challenge.md`; its publisher-only version is UNSOUND
and is not implemented. Source-level SC RMW registration is not a substitute for
the explicit waiter fence before non-SC predicate reads.

For an attempted cold sleep, R is `waiting.swap(true, SeqCst)`, Fw the immediately
following SC fence, Q an Acquire predicate read missing a done/stop publication D,
Fp the unconditional publisher SC fence after D, and L its SC waiting load.
Publication remains monotone during the wait: the single coordinator cannot
advance a request while waiting for that epoch; stop never resets. Q is therefore
coherence-before D. C++20 SC-fence ordering requires R <S Fw <S Fp <S L. Only the
waiter writes waiting after initialization; every repeated registration is true.
L must see true, or a later exit-clear that means this wait has resolved. A false
load before registration cannot accompany a missed publication after the fenced
recheck. Short-circuit both_done chooses the first missing reader and does not
weaken the argument.

A publisher that observes true ALWAYS locks Sleep and notifies, with no recheck.
The waiter holds Sleep over registration/fence/recheck, then atomically releases
and blocks. Notification cannot disappear in the check/wait gap. If it precedes
a later registration, Sleep release/acquire carries publication into that check.
Spurious wakes repeat registration AND fence before predicate reads. Delayed old
or duplicate notifications may wake an unrelated epoch; they neither publish
results nor acknowledge readers. Progress still requires runnable publishers and
mutex acquisition; this is not a scheduling-delay bound.

Concrete publication map in `src/colors_worker.rs`:

- `run_active`: output writes and reader.done Release precede signal_completion;
  no Control or Sleep guard is held. All lexical input borrows already ended.
- `publish_terminal`: stopped/failed reader state and stop Release occur under
  Control; that lexical guard ends before signal_completion. Reader exit, not
  terminal observation by the coordinator, retires that reader's accesses.
- `shutdown`: stop Release occurs in its Control block; signal follows that block,
  and actual joins still retire both started threads before flight retirement.
- `dispatch` exhaustion: stop Release and closing metadata precede explicit
  drop(control), then signal_completion and unchanged terminal drain.

These are every production signal site. `wait_completion` remains the only cold
waiter, called by the exclusive coordinator; tests run raw waiters consecutively,
never concurrently. Its sole registration loop fences on every iteration. Its
exit-clear still occurs under Sleep. Atomic initialization is the only other
writer; publishers merely fence/load, then conditionally acquire Sleep/notify.
No code nests Control with Sleep. The spin4096, sample512 and all other atomic
orderings are unchanged.

Request/done epochs, concrete input/output storage, Flight transitions, output
reverse edges, close/discard ownership, lexical scopes and numerical kernels are
byte-identical. Matching BOTH actual done Acquires still publish outputs and
retire input readers; notifications confer neither right. Only the sole waiter
clears waiting. Delayed notifier lifetime remains covered by Arc ownership and
real shutdown joins. There is no extra production flag, timeout or fallback.

Focused controls retain all24 worker tests and add one test-only pause after true
publisher load/before Sleep. Both publishers owe notifications; a spurious wake
lets the first waiter exit, then a new epoch registers while both old obligations
are paused. Releasing them only wakes/rechecks the new pending epoch; its actual
done publications still decide completion. Existing registration/spurious,
terminal, prior-epoch delay, close/drain, startup and exhaustion controls remain;
post-registration observation is AFTER the new fence. Barriers supplement this
proof but cannot reject the abstract one-fence counterexample. Test-only fields
are absent from the measured production layout.

Production declaration equality and compiled size/alignment/lowering are checked
from the one generic image, with unknown DWARF fields stated explicitly. Removing
publisher RMW may reduce latch ownership traffic; that is a hypothesis, not a
cache-miss attribution. Fences, remaining sharing and duplicate cold locks can
erase any benefit. No padding, weakening, retune or numerical change is selected.
