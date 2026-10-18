# External diagnostic adapter

This separate Rust crate implements the required JSON transport incrementally,
calling the native `rook2` library for all specified calculations. It does not
read fixture files, recognize case IDs or contain expected answers. JSON
parsing/serialization uses pinned
[serde_json](https://docs.rs/serde_json/1.0.154/serde_json/); this dependency is
outside the ordinary engine crate and is not linked into `rook2`.

The current79 operations cover time schedule/allowance, parameters and output
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
fresh/retained pawn structure/candidates and fresh phase/subtotals.
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
The current4521-case external result comprises73 complete released fixture
files with no partial selection or duplicate cases. All86 adapter unit tests
pass after135 native tests. Frozen canonical adapter SHA256 is
`a9f6e9f666d476b2a7ef7dcdb33a7acec5b9178d9f43c0f556079853bf7c75b5`.
See `evidence/diagnostic-production-observers-20261018/`; both the25-file frontend
and43-file native closure are stable and independently reconciled. Native
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
still needs38 operations/3152 cases and wider production/gameplay qualification.
