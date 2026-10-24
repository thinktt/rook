# Serial branch-transaction feasibility pilot

This feature-gated research driver simulates an ordered optimistic queue. It
preserves the inline Activity–Shelter baseline and default production behavior.
It does not run branch workers or establish a multicore speedup.

Fixed selection: profiling workloads35,08,04 in that order; queue depths2 then4;
maximum depth8; at most8 restricted-tail candidates; at most16384 retained events
per task. Reach Restricted policy naturally, execute child0 serially, then enqueue
native projected tail attempts. No artificial work threshold or policy override.
Original histories/personality parameters are retained, with explicit rnd=0.
NoHost, timing absent, unlimited logical nodes and fixed completion exclude live
poll commands, time/node interruption, partial stops and nonzero randomness.
Environment/config/root parameters/table geometry are immutable within each run;
the entry check is not a general task certificate.

Every semantic acceptance is audited against independent canonical execution.
A disagreement or broken rollback witness fails the process and halts collection.
Focused controls exercise nontrivial native search, irrelevant TT/pawn-miss
changes with fresh-canonical state preservation, and late rejection after staged
writes. The late read is an appended native probe, not a claimed naturally reached
branch dependency. Full-order validation reruns native sorting. Commit uses staged
native replay, never speculative final shared-state bytes.

Build with `cargo build --offline --release --features branch-transactions
--bin rook2-branch-tx --target-dir /external/path`. Run `collect.py --binary
/external/path/release/rook2-branch-tx --output /new/raw/directory` from housekeeping
CPUs0–5,8–13. Native processes are pinned to14. Each is capped at180s, total900s;
any timeout, nonzero exit or unsound acceptance stops the remaining schedule.
Raw evidence/build products are outside Git at
`/home/legolas/rook2-experiments/branch-transactions-20261024-01/`.

Queue snapshots retain complete speculative states for audit; this prototype copy
cost is explicit. Event enum padding, event construction and per-insertion clocks
are observer/representation costs rather than fundamental lower bounds.
Incomplete certificates (log overflow) retain their executed work. Independent
oracle execution/comparison/witness copies are audit costs; rejected oracle native
execution also supplies fallback and must not be counted twice. Head acceptance
(distance0) is separate from work prepared ahead of an earlier branch.
