# Frozen ordinary wire integration

The generic x86-64, thin-LTO, non-PGO `rook2` executable has SHA256
`da82041f29091ed8db54f2cd2ffd0c338da5ae5216cae3caea6130974573e648`.
The local immutable copy is `rook2-exact` (not committed).
[Build receipt](receipt.json), raw build logs and
[archive receipt](archive-receipt.json) bind the compiler/settings and 54
pre-build source/tool files. `verified-source-before.tar.gz` was checked
byte-for-byte against the original receipt hashes. The archive is retained;
the uncompressed working copy stays local.

This integrates static host callbacks at actual capture and 4096-unit polls,
live status/current paths, graceful finish/abort, active time synchronization,
post toggles, cold Linux nonblocking records, ordinary replies, natural seed
acquisition, opt-in diagnostic seed commands and fine-work publication.
The engine owns one process/thread. No fixture lookup or expected-answer data
is linked into the ordinary executable.

Validation on this frozen source/artifact:

- 128 native tests (126 library, two development CLI), retained in
  `native-tests.stdout` / `native-tests.stderr`.
- [201 native timing/session cases](../live-host-check-20261018-frozen/receipt.json)
  and [1,352 evaluator/root cases](../evaluation-check-20261018-live-regression/receipt.json),
  both using the release-optimization test harness with panic unwinding.
  These are native projections, not strict diagnostic transport checks.
- [Ordinary wire collection](../live-wire-check-20261018-frozen/receipt.json):
  all 54 profiling replay cases / 624 posts; six literal work-post controls;
  seed spelling/malformed-assignment and three-search persistence controls;
  four continuous switching segments / eight searches in one process;
  ten additional literal record/reply/fatal controls.
- [Eight literal-wire interruption fixtures](../live-interruption-wire-20261018-frozen/receipt.json),
  retaining 24 searches, complete stdin/stdout/stderr and clean outcomes.

Production retains panic abort. Full diagnostic conformance, independent full
games, the complete gameplay gate and performance qualification remain open.
The mission in `/home/legolas/imp-perf-mission.md` continues to govern them.

The earlier first artifact
`893448ddee8730364d239a1d2b8288acbe12cb94249733bbf1e3d52f8711a873`
has its own source archive and 54-case evidence. It is a different binary:
the CPU pilot below belongs to that first artifact, not this frozen hash.
