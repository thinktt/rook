# Rook2

An independent Rust implementation of the KingRE ordinary-play specification,
designed around efficient integrated search and eventual exact behavioral and
performance qualification.

The governing mission is [imp-perf-mission.md](../imp-perf-mission.md).
The released behavioral and performance contracts are in
[king-spec](../king-spec/README.md), currently v2.5.0.

This repository contains an integrated development engine: compact position
state, legal generation, partial evaluation and explicitly partial recursive
search. It does not yet implement the complete ordinary KingRE engine or claim
conformance or performance qualification.

Build the development executable with retained settings and identity:

```sh
python3 tools/build.py --output evidence/fresh-build --bin rook2-dev
```

Run `rook2-dev inspect`, `perft --depth 4`, or `search --depth 4` from the emitted
binary path. Its JSON output identifies the search omissions and development
scope. It is a native development seam, not the XBoard or DIAG-TRANSPORT interface.

See [STATUS.md](STATUS.md) for the current milestones and
[AGENTS.md](AGENTS.md) for contribution and clean-room boundaries.
