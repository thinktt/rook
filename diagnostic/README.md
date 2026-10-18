# External diagnostic adapter

This separate Rust crate implements the required JSON transport incrementally,
calling the native `rook2` library for all specified calculations. It does not
read fixture files, recognize case IDs or contain expected answers. JSON
parsing/serialization uses pinned
[serde_json](https://docs.rs/serde_json/1.0.154/serde_json/); this dependency is
outside the ordinary engine crate and is not linked into `rook2`.

The current53 operations cover time schedule/allowance, parameters and output
scores; position setup/history/identity and phase; influence and relations;
activity, board patterns, central balances and pawn progress/endings; work
ledger sequences; selective depth, cutoff memory, retained results and supplied
candidate ordering, priority-sequence permutation and capture preference;
root randomization/aspiration, quiescence capture policy and PV line length;
material balance, capture exception/defense/allowance, frontier estimate,
king pressure and guarded fast cutoff; opaque/produced-history admission and
local move extensions; pawn spread, pawnless potential, minor mating geometry,
composed endgame material and pawn-race classification; fresh personality
coefficient conversion/central balance and ordinary/final score finishing.
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
The current2496-case external result comprises44 complete fixture files plus
25 unchanged selected cases from two partially supported files. All39 adapter
unit tests pass. Frozen adapter SHA256 is
`9c8780c92888d676a2be24b4759f3dea827facefcc4b0af49971a318a4e793f8`.
See `evidence/diagnostic-scores-20261018/`; linked native source and all
declared dependencies remain unchanged. The original25-case selection provenance
remains in `diagnostic-positions-20261018-02/`.

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
