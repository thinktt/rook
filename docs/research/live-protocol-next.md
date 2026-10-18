# Live ordinary interface: integration checkpoint

The ordinary binary now connects the native persistent session to literal
stdin/stdout. A generic host receives actual root-capture and charged-work poll
events. The zero-sized NoHost specialization preserves native development
search; the ordinary binary disables development counters/root traces. Moving
the existing search storage and active clock into the live specialization
avoids aliasing game state during recursion, reallocating the search buffers
or adding a reader thread. Linux nonblocking input consumes at most one
complete available line at each 4096-unit poll; idle input waits with poll(2).

The implemented boundary follows `interrupted-sessions.md`, `post-lifecycle.md`,
`ordinary-xboard-wire.md`, `gate-seed-command.md` and `work-clock-profiling.md`:

- Consume at most one complete available input line per eligible poll. Preserve
  graceful finish, abort and maximum-time interruption as distinct outcomes.
  An interrupted child never manufactures a return or capture.
- Emit eligible deep captures immediately; deferred finish publication depends
  on actual prior publication, including post/nopost changes during search.
- Status uses the active recursive path, including null moves, rather than
  the saved best PV. Root indices/counts belong to actual exploration order.
- Fine-work posts use the ledger snapshot current at publication, including
  deferred shallow output. `go_live` publishes through the host; its returned
  event vector is empty. Native `go` retains the separate completed-events
  projection used by native seam checks.
- Natural POSIX seconds are acquired at the actual seed boundary after root
  preparation. Gate mode overrides and observes that acquisition. Work-clock
  origin and the explicit override persist through game resets.
- The byte input boundary enforces total record length including LF/CRLF,
  ASCII/NUL/embedded-CR rules and token bounds before passing idle payloads to
  the native session. Every completed output record is flushed.

The first frozen executable passes the six released literal work-post controls,
seed spelling/persistence controls, all 54 fresh-process profiling replays
(624 posts), and eight literal-wire interruption fixtures (24 ordered searches).
These observations are scoped evidence, not complete ordinary or gameplay
qualification. Native checks independently cover session clocks, root state,
interruption restoration and status/null paths.

Adjudication now uses the existing bounded legal-reply producer instead of
generating a full inventory solely to test emptiness. Terminal precedence and
the exceptional king-victim continuation are retained.

Next work includes strict DIAG validation/full ingress schemas, complete
persistent game replays and continuity, further ordinary wire coverage and
whole-lifetime measurement. Permanent layout/restoration selection,
calibration/PMU capabilities and whole-engine performance gates retain the full
mission scope in `/home/legolas/imp-perf-mission.md`. The first CPU14 pilot uses
the released sampled selected-move/checkpoint endpoint, not the primary
whole-lifetime acceptance boundary.
