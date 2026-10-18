# External diagnostic adapter

This separate Rust crate implements the required JSON transport incrementally,
calling the native `rook2` library for all specified calculations. It does not
read fixture files, recognize case IDs or contain expected answers. JSON
parsing/serialization uses pinned
[serde_json](https://docs.rs/serde_json/1.0.154/serde_json/); this dependency is
outside the ordinary engine crate and is not linked into `rook2`.

The current27 operations cover time schedule/allowance, parameters and output
scores; position setup/history/identity and phase; influence and relations;
activity, board patterns, central balances and pawn progress/endings; work
ledger sequences; selective depth, cutoff memory, retained results and supplied
candidate ordering. Other operations fail explicitly until implemented. This
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
The current1130-case external result comprises22 complete fixture files plus
25 unchanged selected cases from two partially supported files. All23 adapter
unit tests pass. Frozen adapter SHA256 is
`c4cd856638cbaa8ed4ef1408ab1478f02ab58fa60fc79e920292a2e73cfe1924`.
See `evidence/diagnostic-placement-20261018-02/`; linked native source and all
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
