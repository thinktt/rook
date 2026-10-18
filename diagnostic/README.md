# External diagnostic adapter

This separate Rust crate implements the required JSON transport incrementally,
calling the native `rook2` library for all specified calculations. It does not
read fixture files, recognize case IDs or contain expected answers. JSON
parsing/serialization uses pinned
[serde_json](https://docs.rs/serde_json/1.0.154/serde_json/); this dependency is
outside the ordinary engine crate and is not linked into `rook2`.

The current operations are `time.schedule`, `time.allowance`,
`session.parameters`, `search.selectiveDepth`, `output.searchScore` and
`output.personalitySearchScore`, plus `position.setup`,
`position.setupMoveSequence`, `position.moveSequence`, `position.identity` and
`evaluation.phase`. Other operations fail explicitly until
implemented. This is not complete mandatory diagnostic acceptance.

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
The current416-case external result comprises eight complete fixture files plus
25 unchanged selected cases from two partially supported files. See the retained
`evidence/diagnostic-positions-20261018-02/` receipt and its selection provenance.
