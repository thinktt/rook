# Cold clock boundary proposal — source only

This isolated home-backed source forks frozen generation2 exactly, adding only
diagnostic/src/clock_boundaries.rs and its main.rs module/dispatch. All43 native
and23 tool files remain byte-identical. Root, generation2 and the separate
first/ordinary proposal remain untouched. No build, test, engine, codegen,
profile or timing has run. The plan inventories100 operations/7490 unique cases/
95 whole released files, adding43 cases across three files. Expected native152
and adapter164 units are declarations, all unrun for this source.

Adaptive sequences parse every sequence/event, including stopped suffixes,
before constructing any native Adaptive state. Exact schemas, sequence1..256,
events1..64, request-total4096, allowance order/ranges, unsigned clocks,
nondecreasing modular elapsed0..i32::MAX and depth1..30, and all score fields
are checked. One native Adaptive::new owns initialization/initial clock read;
apply receives a lazy closure for each supplied observation and owns all
arithmetic, retained changes, read counts and stop decisions. The cold loop
serializes native state and ends at its first stop. No formula or adjustment
state machine is copied into the adapter.

Terminal queries parse exact supplied fields and finite nonnegative binary64
allowance. Existing positions::placement(false) preserves the EVAL-PHASE
placement domain, including promotion-heavy types without imposing another
component's limits or nonmoving-king safety. Root endgame comes from actual
Position::phase. Native Terminal::{reason,elapsed_cs,mate_margin} owns every
ordered stop, signed clock-word interpretation and selective-depth computation.
No undocumented query count ceiling or nonempty restriction is added. Its
signed elapsed domain remains distinct from Adaptive's nonnegative interval.

Idle setup uses one actual Session<true> through all commands and calls its
idle method and final allowance. The cold request parses all strings/record
syntax first; all level triples, including ignored suffix stages, must have
valid integer syntax. It does not restrict the ordinary ten-stage grammar to
the fixtures' two stages. Native Session owns level normalization/replacement,
setup/counters, moves/rewind, selected clock color, retained parameters,
pondering and adjustment. Replies are ignored only after rejecting native
illegal/unknown-command replies. Search/Quit actions fail instead of executing
or fabricating a setup observation. Ordinary harmless idle commands remain
available rather than inventing a fixture-shaped whitelist.

Time synchronization has a cold admission-only check that scheduled credit
and the mathematical credit-minus-remaining fit the bounded signed32 setup
profile. The actual adjustment still comes only from Session::idle; no value
from the admission calculation replaces it. Final consumed sop must be0..100;
unrelated stored personality fields are not bound as a search. Native allowance
checks the resulting arithmetic domain. No initial/current side substitution,
counter-from-FEN substitution, automatic force, or reset between commands is
introduced. Wrapped-overflow/active-search behavior remains outside this
bounded component and is not changed in ordinary production.

Eight unrun test sources target eager stopped suffix/batch validation, skipped
clock observations, depth-jump history and modular shift invariance, signed
terminal wrap/priority/no invented batch cap, broad phase domain/late-invalid
fields, adjustment command order/reset/rewind, initial-side clock selection,
ten-stage/ignored-stage syntax and actual search/unknown/illegal rejection.
They do not replace official43-case or full-suite execution.

`source-manifest.json`, source-101.tar.gz, proposal.patch, test inventory and
the complete whole-file case inventory bind the reviewed source. Initial
preparation used the wrong structured-manifest level and failed before any
copy/mutation; preparation-reader-failure.json records the actual exit. All
helpers use housekeeping0-5,8-13. Freeze performs source/text archival only;
parent will obtain an independent review before composition or execution.
