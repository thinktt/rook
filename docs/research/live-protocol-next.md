# Live ordinary interface: next integration boundary

The native session model now joins idle commands, chronological state/rewind,
game adjudication, parameter binding, allocation, seed/work-clock lifetime,
actual timed search and semantic post/move output. The frozen session/output
check has 193 passing cases, including 42 searches across eight clock-seeded
sequences and the complete three-search ordinary trace. The same source passes
124 native tests and 1,352 evaluator/root release cases. This is a checkpoint,
not completed transport, gameplay or performance qualification.

The next implementation should connect a live host at actual capture and
4096-work boundaries. Read `interrupted-sessions.md`, `post-lifecycle.md`,
`ordinary-xboard-wire.md`, `gate-seed-command.md` and `work-clock-profiling.md`
before fixing callback order and output ownership. In particular:

- Consume at most one complete available input line per eligible poll. Preserve
  graceful finish, abort and maximum-time interruption as distinct outcomes.
  An interrupted child never manufactures a return or capture.
- Emit eligible deep captures immediately; deferred finish publication depends
  on actual prior publication, including post/nopost changes during search.
- Status uses the active recursive path, including null moves, rather than
  the saved best PV. Root indices/counts belong to actual exploration order.
- Fine-work posts use the ledger snapshot current at publication. Do not attach
  that snapshot to the captured score/SearchID as though it were immutable.
  Native `completed_events` currently reconstructs ordinary semantic events
  after search; it is not a live publisher or the fine-work implementation.
- Add the natural POSIX seconds source and explicit opt-in gate seed controls
  without changing normal startup or resetting the work epoch on game reset.
- Enforce byte-record limits/ASCII/LF behavior at the transport boundary;
  current `Session::idle` consumes already separated payloads.

A concrete generic host with a zero-sized no-op specialization is a candidate
for retaining native costs while adding live events. Session/search ownership
must permit mutable clock/post controls without unsafe aliasing or per-node
allocation. The existing `Session` keeps reusable search storage separately
from persistent game state. Decide the transfer/borrowing boundary explicitly
and verify the no-host semantic baseline and actual host behavior independently.
This is an implementation direction to evaluate, not a committed public API.

Before whole-production measurements, make adjudication request only bounded
legal-reply availability instead of generating the complete root inventory
solely to test emptiness. The existing bounded reply producer already serves
quiescence. Preserve terminal precedence and exceptional king-victim handling.

Use the existing frozen raw/source evidence as the baseline. Literal process
I/O, strict DIAG validation and full ingress schemas still need checks beyond
the native projections. Permanent layout/restoration selection, gameplay,
calibration/PMU capabilities and whole-engine performance gates retain the full
mission scope in `/home/legolas/imp-perf-mission.md`.
