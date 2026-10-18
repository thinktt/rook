# External diagnostic adapter

This separate Rust crate implements the required JSON transport incrementally,
calling the native `rook2` library for all specified calculations. It does not
read fixture files, recognize case IDs or contain expected answers. JSON
parsing/serialization uses pinned
[serde_json](https://docs.rs/serde_json/1.0.154/serde_json/); this dependency is
outside the ordinary engine crate and is not linked into `rook2`.

The current88 operations cover time schedule/allowance, parameters and output
scores; position setup/history/identity and phase; influence and relations;
activity, board patterns, central balances and pawn progress/endings; work
ledger sequences; selective depth, cutoff memory, retained results and supplied
candidate ordering, priority-sequence permutation and capture preference;
root randomization/aspiration, quiescence capture policy and PV line length;
material balance, capture exception/defense/allowance, frontier estimate,
king pressure and guarded fast cutoff; opaque/produced-history admission and
local move extensions; pawn spread, pawnless potential, minor mating geometry,
composed endgame material and pawn-race classification; fresh personality
coefficient conversion/central balance and ordinary/final score finishing;
selected pawn-race/fortress bounds, rook reductions and full endgame adjustment;
material-threat production and board-derived pressure/threat/cutoff composition;
root material/square and raw shelter observations; score-context production;
fresh/retained pawn structure/candidates and fresh phase/subtotals; complete
forced-fresh subtotal/score, controlled retained full/fast sequences, actual
move/null evaluation sequences, admitted Q entry/disposition, retained pawn
subtotals, fixed-root search pawn sequences and actual recursive quiescence trees.
Other operations fail explicitly until implemented. This
is not complete mandatory diagnostic acceptance.

```sh
cargo build --offline --locked --release --manifest-path diagnostic/Cargo.toml
```

The default output is `diagnostic/target/release/rook2-diag`. For a recorded
generic build, `tools/build.py --crate /absolute/path/rook2/diagnostic --bin
rook2-diag --output evidence/fresh-diag-build` also works. Its source closure
does not automatically cover the path-dependent engine: retain before/after
engine-source identities and archive that linked source separately.

One invocation reads one UTF-8 JSON request terminated by newline, supports
JSON whitespace/multiline layout, emits exactly one JSON response plus LF,
and exits. Input schemas validate named fields, array lengths and numeric
domains specified by each implemented contract. Parameter command lists have
no extra diagnostic count limit. Invalid schemas and unsupported operations
exit nonzero with diagnostic stderr and no substitute result.

The position adapter preserves established raw flags for lower moveSequence and
normalizes requested flags for setup history. Setup/history admission domains
remain distinct, and per-type diagnostic limits do not narrow ordinary ingress.
The current6161-case external result comprises83 complete released fixture
files with no partial selection or duplicate cases. All133 adapter unit tests
pass after147 native tests. Frozen adapter SHA256 is
`e70e9cadfdea544c95c9f0575cf08471fa67c8cda42135b9b5eb0a763abebdd2`.
See `evidence/king-first88-diagnostic-20261018/`; both the31-file frontend
and43-file native closure are stable and independently reconciled. Integration
independently matches both source closures to the exact tested proposal in
`evidence/king-first88-integration-20261018/`. This is source promotion
with named frozen artifacts, without a canonical-path rebuild claim. Native
observation helpers share production arithmetic and retain state/layout/charge
ownership. This does not transfer timing or gameplay from prior8d artifacts.
Earlier selected-case provenance remains retained with its original attempts.

The retained first expanded attempt passed1010of1022 cases and failed12
unsupported candidate-order requests bundled with cutoff learning. Adding the
native-backed candidate-order transport and its complete108-case fixture file
produced the passing fresh attempt. Original source preparations, failed build,
all reports and the corrected source archive remain. Ordering accepts full
unsigned32 synthetic history without applying cutoff learning's total limit.
All priorities and their final permutation call native policy. Relation encoding,
charge counts and retained-state changes likewise retain their native owners;
neither fixtures nor expected answers are read at runtime.

`ordering.prioritySequence` and `tactics.capturePreferenceOrder` first passed
with the previous native layout in frozen4d07ce08. The same unchanged frontend
then passed25 units/1214 cases against the integrated persistent-bitplane native
source in frozenfab90bb7. Both attempts and source archives remain. This is
component transport acceptance, without whole-production or complete mandatory
qualification.

The five endgame routes first passed against the previous native source in
137a71e9. The identical16-file frontend then passed36 units/2215 cases after
compact relation/typed-list influence integration in ab8b7c3c. Both source
closures, builds and reports remain retained. No trial timing transfers through
this component regression.

The four score/weight routes add281 cases and three admission-focused units
against unchanged canonical native source. Final scoring consumes supplied
phase, current side, check context and identity; it does not substitute their
placement-derived production. The late-phase adjusted-subtotal restriction is
validated before native evaluation. Fresh coefficients accept full signed32
percentages while the composed central route validates the narrower domain,
including ignored king fields. The first offline reconciler had an incorrect
case-count literal; its source/failure are preserved, and corrected
`reconcile-02.py` independently verifies all original2496 results without
rerunning any engine.

The four selected/full endgame-bound routes add372 cases and three units.
They preserve independent White-relative endpoints, including contradictory
intervals, and validate strict selected material before calling native geometry.
They do not infer legal ancestry, score favor, check state or phase from the
supplied placement. Full stage clipping remains lower-then-upper; selected
consumers preserve their distinct score/bound outputs. Frozenf8e0b7b0 passes
all2868 cases/42 units against unchanged canonical native source.

The identical57-operation frontend has now been relinked after static-kind
activity integration. Frozene31263ac again passes42 units and2868 unique
external cases; every original exit/report/source dependency is independently
reconciled. The priorf8e0b7b0 observation stays attached to its older native
source. No missing operation or production qualification claim is closed by
this relink.

Two threat routes now add368 cases and seven admission/composition units. They
validate all supplied values/adjustments before lazy gates, preserve Black/White
ownership, distinguish queried zero from absence, retain estimator charges
after failed final cutoff and repeat per-call work exactly. Pressure uses current
king neighbors and evaluation influence, including transparency. Native owners
perform every formula; current production43 source is unchanged. Frozenef406db7
passes3236 unique cases/49 units across59 operations. At that59-operation checkpoint, shelter raw observation
transport was deferred and no native visibility change or Cargo feature was
introduced. The later79-operation integration below now exposes shared native
observation seams without a feature switch.

Twenty added routes now cover material/square/root contexts, raw shelter,
produced score contexts and fresh/retained pawn observations/subtotals. They
preserve supplied versus derived phase/counts, actual color ownership, zero and
full-identity collisions, retained pawn chronology, raw ending before fallback,
ignored-field validation and per-call native relation work. The three old
identity cases are now included once in the whole identity-retention fixture.
Existing-route selection closure adds29 previously omitted cases. The first
64-route preparation omitted a version header and failed before external
execution; its fresh corrected attempt and all earlier artifacts remain.
Production cache selection shares a static miss-only builder, so a cache hit
does not acquire pawn lists or construct descriptors. RootContext/Position/Node
layout and ordinary ownership remain unchanged. Complete mandatory acceptance
at that79-operation checkpoint still needed38 operations/3152 cases.

The next three routes add200 cases through actual native full/fast observations.
Forced-fresh paths bypass cache matches; retained sequences use actual nonfresh
selection and report its reuse flag. Fast preserves the produced pair/age and
does not query influence or pawns. Current squares are rebuilt under the fixed
root for artificial placements. Produced finishing values come from one native
call and do not acquire the standalone supplied-input score restriction. The
frozen ordinary c6839096 passes54 strict replays/eight interruption fixtures;
focused static comparison finds unchanged ordinary full/fast code at its main
callers. No CPU result follows. At that82-operation checkpoint, mandatory
acceptance still needed35 operations/2952 cases.

The next move sequence and two Q-entry/disposition routes add568 cases. Actual
child/null inheritance and selected fast/full stages retain native ownership.
The private const-default selector keeps ordinary full/fast wrappers while
sharing all sparse/refresh conditions with the observer. Q disposition shares
the native ordered return policy. The corrected ordinary d38ff037 passes142
native tests,54 strict replays/eight interruption fixtures; combined adapter
7dd00a43 passes5289 cases/117 units. Its bounded default codegen review restores
the prior evaluation call scope and stack size, without a CPU-neutrality claim.
The original metadata-stability failure and clean replay retry are preserved.
At that85-operation checkpoint, mandatory acceptance still needed32
operations/2384 cases.

Two subsequent cold pawn routes add862 cases and25992 result records. They
share native retained selection, current membership/phase/piece terms, ending
fallback and fixed-root context production; all schemas validate before state
creation. Native43 is unchanged, so accepted142/strict54/eight-wire evidence is
reused. All126 adapter units and6151 original/raw/exit comparisons pass across
87 mandatory operations/82 whole files. At that checkpoint mandatory acceptance needed
30 operations/1522 cases, followed by wider production/gameplay/performance
qualification.

The recursive Q route adds ten cases and seven adapter units. One shared native
recursion records actual entries, retained evaluation stages, returns and PVs
through a static observer whose sink remains outside Search. Ordinary NoTrace
keeps the original full/fast call scope and55-call recursive ABI; reviewed local
stack grows32 bytes. Frozenfed8a40a passes145 native tests and54/eight-wire,
while adapter75097e2a passes133 units/6161 cases across88 operations/83 whole
files. The original terminal-stage test incorrectly encountered a repetition
draw; its failure and the minimal corrected test remain preserved. Remaining
mandatory inventory is29 operations/1512 cases. No timing result follows from
the source/codegen/behavior observations.

The same88-route frontend now passes133 units and all6161 cases after the
checked bounded king-first source composition. Fresh native731aa0aa passes147
tests,54 strict replays/eight-wire; adaptere70e9cad is relinked and independently
reconciled. This exact source promotion does not transfer the frozen85 PGO pilot
or claim a canonical-path rebuild. No diagnostic inventory changes here.
