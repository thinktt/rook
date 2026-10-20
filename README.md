# Rook2

An independent Rust implementation of the released KingRE ordinary-play specification. The [mission](../imp-perf-mission.md) and [KingRE v2.5.0 contracts](../king-spec/README.md) guide behavior and qualification.

**Current local candidate: the first-main corrected build.** The tested first-main cutoff correction and test additions are adopted with the existing exact own-PGO ordinary image `5cf01208…` and separate diagnostic `68a1c304…`. Retained62 remains the initial comparison control. Position owns coherent attack planes; search retains copied-child state, retained evaluation and ordinary/tactical recursion. No additional architectural optimization is selected.

The paired full54 comparison recorded **68.569086 whole-native CPU s corrected** and **68.446861 s retained62**, summed per-case medians: descriptive **+0.178569%**. The corrected image also passes all mandatory checks and one fresh behavioral12/632 plus continuity, seed and interruption lane. That game pass supplies no full12 timing result. Final specification-owner, external3,288-game and performance qualification remain open.

Start with the [local adoption/handoff](experiments/first-main-cutoff-adoption/README.md), [current status](STATUS.md) and [exact artifacts and build recipe](docs/production-build.md). The tested images/profile remain outside Git. Default builds do not select the tested own-PGO/ExtTSP artifact automatically; a rebuild is a new artifact requiring validation.

The ordinary `rook2` executable serves the live King XBoard byte stream. Optional `--diagnostic-seed-command` enables persistent `king_seed` overrides; `--work-clock=kingwcr` explicitly selects the default work clock, and `--work-clock-post=work` enables fine-work posts. The separate [diagnostic adapter](diagnostic/README.md) serves mandatory JSON operations; `rook2-dev` provides the [development interfaces](tools/README.md).

A fresh generic development build, with a new output directory:

```sh
python3 tools/build.py --mode generic --bin rook2 \
  --output /home/legolas/rook2-experiments/fresh-generic-build
```

Use `--bin rook2-dev` for development commands such as `inspect`, `perft` or `search`. Consult the production recipe before measuring a rebuilt artifact.

- [Current status](STATUS.md): current candidate, closed trials and remaining obligations.
- [Production build](docs/production-build.md): distinct ordinary/diagnostic/profile identities.
- [Local handoff manifest](experiments/first-main-cutoff-adoption/manifest.json): exact artifact/evidence bindings and unresolved external fields.
- [Performance ideas/results](docs/performance-experiments.md): brief historical trials and untried proposals.
- [Evidence layout](docs/evidence-layout.md) and [historical status](STATUS-history-20261020.md): preserved checkpoints and relocated raw records.
- [Contribution and clean-room rules](AGENTS.md).
