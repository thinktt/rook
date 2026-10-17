# Native clock, timing and recursive search checks

All 70 cases pass on the frozen work-timed source:

- 16 work-ledger event sequences, including observed/unobserved resets,
  integer rounding, saturation and signed/wrapped observations.
- 12 adaptive-time cases containing 173 sequences, comparing exact binary64
  limits, retained best-change counts, stop decisions and consumed reads.
- Three terminal-stop cases containing 19 complete scalar producer/consumer
  queries, including phase-derived mate margins and signed clock differences.
- 16 root-randomization cases containing 11,480 queries, plus 17 aspiration
  cases containing 11,050 queries. These call the same native math as search.
- Two seeded and four generic actual timed-search requests. Every legal root
  descriptor, completed step/window/random adjustment/ranking/PV/work, clock
  check, stop boundary, pending root and retained capture matches. This includes
  a maximum poll at 4096 and another at 8192, plus completed-root time stops.

The six recursive cases contain no actual IIO phase, as required by their
diagnostic admission. They do not qualify larger restricted-policy searches
or IIO interruption. Their literal public `events` are intentionally not
compared: post/notation/ingress/session integration is still pending.

The work-clock snapshot unit check additionally verifies that fine-post data
belongs to the latest observation, is cleared on reset, excludes the carried
origin and does not combine fractional segments. This is a native primitive,
not yet the production post formatter.

The receipt binds released fixture, engine, checker, runner and generated
source/data hashes. All source/data and engine manifest/lock identities are
checked before/after. The compressed verified archive preserves every generated
file. Test data and valid-data JSON reading live in an external crate, never
the engine. There is no fixture-identifier or expected-answer dispatch in
engine code. The separate evaluator regression rechecked 1,352 cases on exactly
the same source. The native suite has 115 library and two CLI tests passing.

This is finite native semantic evidence. DIAG validation/transport, public
commands/events, complete gameplay and performance qualification remain open.
