# Root-context transport proposal — COLD, unexecuted

Sender: Imp2 child `/root/root_context_transport`
Recipient: parent `/root`
Prepared: 2026-10-18
Directory: `/tmp/imp2-root-context-transport-20261018`

This is an isolated proposal for the four mandatory routes. It is not integrated,
compiled, tested, benchmarked, or qualified. Parent supplied canonical native43
identity `canonical8d9dddc5 /12c2`; this child has not independently verified that
aggregate identity. Parent's latest message says exact-8d Callgrind profile 99164
is active. Keep all live native files frozen until parent ends that measurement.

## Exact native changes

Only copied `src/evaluation.rs` changes:

1. `pub fn material_values(phase: Phase, percentages: [[u16; 5]; 2]) -> [[i32; 5]; 2]`
   extracts the existing base blend, percentage weight rounding, and final value
   rounding without changing arithmetic. Percentages are already color-bound.
   The existing 0..1000 percentage assertion moves with this kernel.
2. `pub fn square_adjustment(phase: Phase, color: Color, kind: PieceKind,
   square: Square) -> i32` extracts the existing orientation and `blend` call,
   extending the callable piece domain to king (basis already contains it).
   This permits absent pieces and pawn promotion-rank square queries.
3. `RootContext::new` calls those two helpers for the same values and same
   `[[[i16; 64]; 5]; 2]` non-king table. RootContext fields, storage sizes, caches,
   search interfaces and JSON-free native boundary remain unchanged. Constructor
   sequencing now calculates phase/material values before asserting averageDepth;
   all admitted inputs retain the same arithmetic and output.
4. `pub fn square_balance_from_phase(&self, position: &Position,
   nonking_sum: i32, phase: Phase) -> i32` takes the former method's body and
   substitutes the supplied phase only at the final king-difference blend.
   Existing `square_balance_from` remains the production wrapper and passes
   `position.phase()`. It still uses the root-valued non-king sum and current
   piece-count doubling gate. Kings' basis differences are blended/rounded once;
   individually rounded king square adjustments are never summed here.

The phase-domain preconditions are documented on the native helpers, consistent
with native `Phase` having public fields. The adapter validates all triples using
its existing strict `phase` helper. No wider rewrite or phase-cache proposal.

## Adapter wiring

Only copied diagnostic files change:

- `main.rs`: register `mod root_context`, dispatch exactly the four routes.
- `supplied.rs`: expose existing `counts` parser as `pub(super)`; no new parser.
- New `root_context.rs`: use existing `object`, `array`, `integer`, `color`,
  `phase`, `moves::piece`, `positions::square`, `positions::placement` and
  `positions::phase_value` schema helpers. Only ownership binding and named
  output-object assembly are new adapter logic, with no interpolation formulas.

`evaluation.materialValues` binds own/opponent percentages to rootSide then calls
native material_values. `evaluation.rootMaterial` parses the root placement,
sets rootSide, constructs RootContext natively, substitutes independent current
counts into a cold count-only hypothetical and calls native material. It never
rebuilds the root values from descendant counts.

`evaluation.squareValues` calls native square_adjustment per supplied query in
order, including duplicates, empty arrays, and absent/promotion-rank queries.
`evaluation.squareBalance` retains existing representation: build a cold neutral
RootContext, refill only its non-king table through native square_adjustment at
supplied rootPhase, then call native nonking_square_balance and explicit-phase
square_balance_from_phase. This avoids adding a second constructor solely for
transport. Its unused material values are irrelevant to this route.

Both placement routes use `positions::placement(..., false)` because their
released domain permits 15 non-king pieces/color regardless of per-type promotion
counts, king adjacency, checks or reachability. Native placement admission still
requires one king/color, <=8 pawns/color, no pawns on terminal ranks, <=16 total
pieces/color. Supplied current material counts retain their separate domain:
0..15/type, <=30 counted pieces across colors, no consistency with placement.
Square routes report exactly zero chargedRelationQueries.

## Prepared verification

Eight new diagnostic tests, all **unexecuted**:

1. Asymmetric black-root ownership plus the released mixed-phase material
   rounding vector (`root-material-values-3-black`).
2. Starting-root values survive independent pawn-only descendant counts,
   both root colors, and negative odd averageDepth rounding.
3. Ordered duplicate/mirrored knight queries, absent promotion-rank pawn query,
   and empty squareValues batch.
4. Independent root/current supplied phases using two released square-balance
   vectors, deliberately inconsistent with placement-derived phase.
5. Once-rounded king differences, signed half rounding under reflection,
   king-only and actual pawn-ending doubling, knight presence disabling doubling.
6. Two negative-half non-king contributions round individually before summing
   (-20 rather than -21).
7. Strict nested schemas, malformed phase, percentage/depth bounds, independent
   current-count domain and 768-query boundary with integer-valued JSON number.
8. Adjacent kings and 15 queens/color admitted; terminal-rank pawn rejected.

Existing native evaluation tests are preserved unchanged. Source-only rustfmt
succeeded for the changed native module/new adapter module/main wiring; the
shared supplied module was restored to its original formatting with only its
visibility edit. This is not Rust type checking or an executable passing claim.

Read authority: released root-material-context.md, positional-values.md,
material-balance.md, diagnostic-interface.md, the two corresponding fixture
files, native evaluation/position/types/basis, and existing diagnostic schemas.
No separate schema files were found in the released tree; field/domain contracts
were taken from those released documents and shared adapter validators.

No build, rustc, tests, native engine, profile or simulation ran. All shell/file
helpers used affinity `0-5,8-13`; no CPU14/15 work, Herdr, other subagents or
forbidden `/home/legolas/rook` source. Requested Normal speed is not runtime
verifiable with the available controls.

## Handoff and remaining scope

`native.patch` and `diagnostic.patch` are separate unified patches against the
unchanged live files; the entire copied src/Cargo/diagnostic source is available
for parent inspection. No target or evidence directory was copied or created.
`baseline-hashes.json` records the three original edited files. A final static
comparison confirmed exactly four changed/new copied source files and unchanged
live hashes for all three original files.

Parent owns integration, reconciliation with any concurrent changes after the
profile, builds/type checking, native regression tests, the eight new diagnostic
tests and both released fixture suites. Any native extraction must receive a
new artifact identity and suitable semantic/performance requalification. This
component proposal does not address phase caching, make/undo/reset lifecycle,
full evaluation/search parity or the remaining mandatory diagnostic families.
