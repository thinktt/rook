# Rook2

An independent Rust implementation of the KingRE ordinary-play specification,
designed around efficient integrated search and eventual exact behavioral and
performance qualification.

The governing mission is [imp-perf-mission.md](../imp-perf-mission.md).
The released behavioral and performance contracts are in
[king-spec](../king-spec/README.md), currently v2.5.0.

This repository contains an integrated development engine: compact position
state, legal generation, composed retained evaluation and recursive ordinary/
tactical search, a work-timed root controller and persistent ordinary session.
The `rook2` executable serves the live King XBoard byte stream, including
search-time controls/status, natural seed acquisition, gate seed commands and
fine-work posts. A separate [diagnostic adapter](diagnostic/README.md) implements
44 mandatory operations with1968 external cases so far. Complete diagnostics, full gameplay and
performance qualification remain outstanding. Current generation reuse and
compiler-PGO experiments retain exact builds, strict replay results and balanced
whole-native CPU pilots; see [STATUS.md](STATUS.md) for their distinct scopes.

Placement now includes exact attack planes owned by Position160/Node176,
retaining copied-child state and independent retained evaluation. The measured
storage/kernel decision and its validation boundaries are recorded in
[decision0004](docs/decisions/0004-persistent-attack-planes.md).

Build the ordinary executable with retained settings and identity:

```sh
python3 tools/build.py --output evidence/fresh-ordinary-build --bin rook2
```

Run the emitted binary directly for the ordinary silent-startup profile.
`--diagnostic-seed-command` enables the opt-in persistent `king_seed` command
and consumed-seed stderr observations. `--work-clock=kingwcr` selects the default
work clock explicitly; `--work-clock-post=work` enables fine-work posts. The
ordinary binary has no diagnostic JSON mode or host wall-clock mode.

Build the development executable with retained settings and identity:

```sh
python3 tools/build.py --output evidence/fresh-build --bin rook2-dev
```

Run `rook2-dev inspect`, `perft --depth 4`, or `search --depth 4` from the emitted
binary path. Its JSON output identifies the search omissions and development
scope. It is a native development seam, not the XBoard or DIAG-TRANSPORT interface.

`rook2-dev quiescence --moves 'e2e4 d7d5' --root-move e4d5` exercises the newer
retained evaluator and tactical recursion. `--diagnostics off` selects its
specialization without development counters while preserving charged work. Each repeat starts
a fresh search lifetime; output excludes the preparatory root from subtree
counters. A node-budget stop is an error. The older
[frozen baseline](evidence/quiescence-v1/README.md) identifies its partial
evaluation scope; it is not a timing denominator for the current evaluator.

`rook2-dev first-iteration` visits the complete natural root list once, using
the specified second-ranked-score window and shared pawn-cache lifetime across
actual tactical children. Its diagnostic steps expose the returned windows,
ranking and PV. This mode stops at that first pass.

`rook2-dev ordinary --depth 4 --max-nodes 1000000` runs the newer iterative
ordinary/tactical pipeline with remembered results, learned ordering, pruning,
extensions and internal ordering passes. Its default TT budget is64 MiB;
`--tts-bytes` supports explicit development collision experiments. Timing and
public personality/protocol omissions are reported in every result. Selected
complete fixed-iteration observations match the released expectations; see
[native evaluation/root checks](evidence/evaluation-check-20261017-roots/README.md)
and the [current CPU baseline](evidence/neutral-evaluation-v2/README.md).

`rook2-dev work-timed --seed 0 --max-nodes 8192` runs neutral work-timed search
with explicit seed, randomness 50 and 1cs average/maximum allowances. The native
controller applies seeded root windows, adaptive checks, 4096-work polls,
interruption and retained captures. `--average-cs`, `--maximum-cs`,
`--randomness` and `--iteration-cap` expose development controls. Public seed
acquisition, host commands, persistent sessions and post/PV rendering remain
separate. See [native timing evidence](evidence/timing-check-20261017-frozen/README.md)
and the [timed CPU baseline](evidence/work-timed-v1/README.md).

Native [session/output checks](evidence/session-output-check-20261017-frozen/README.md)
cover persistent work-clock/seed lifetime, complete semantic post trails and
the inherited-settings three-search sequence. These run the actual session
model; they do not establish live protocol timing or command polling.

See [STATUS.md](STATUS.md) for the current milestones and
[AGENTS.md](AGENTS.md) for contribution and clean-room boundaries.
