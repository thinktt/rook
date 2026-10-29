# Rook2

**This worktree is the deterministic multicore research branch.** The latest
[isolated three-thread candidate](experiments/multicore-feasibility/single-owner-own-pgo/report.md)
completed the descriptive 54-case survey in58.692s, versus58.935s for the prior
three-thread candidate and69.641s for accepted serial:0.41% and15.72% lower,
respectively. It uses2.526x serial CPU; its one-thread mode was1.29% slower than
serial in the same window. The coordinator prepares ordinary and eligible
unchecked-Q move lists while its two evaluation helpers are busy. Owner-local
flight state removes normal dispatch/completion lock arbitration under a restricted
activation API; cold lifecycle and actual reader retirement remain synchronized.
All270 comparison replays passed, with39/54 cases faster than the prior candidate
and54/54 faster than serial. The exact candidate is c242f0e4/profile1a81bdac;
the previous a4ec image and all predecessors remain preserved.
These are single observations, not confidence intervals. Broader exact-image
behavioral qualification and adoption remain open.

The three-thread source/image are retained with that experiment; canonical branch
source still preserves the [two-thread checkpoint](docs/research/deterministic-multicore-outcome.md)
and its selected local behavioral evidence. Accepted serial release bytes below
are unchanged. Historical KingWCR timings are not a matched comparison.

Research continues under the [multicore mission](docs/deterministic-multicore-mission.md).
On 2026-10-26 the owner restored an open architectural agenda: seek useful scaling
across increasing thread counts, with branch queues as one hypothesis rather than
the primary approach. The two-thread outcome is a preserved checkpoint, not closure
of the investigation. See [current research status](STATUS.md).

An independent Rust implementation of the released KingRE ordinary-play specification. The [mission](../imp-perf-mission.md) and [KingRE v2.5.0 contracts](../king-spec/README.md) guide behavior and qualification.

**Current local candidate: the first-main corrected build.** The tested first-main cutoff correction and test additions are adopted with the existing exact own-PGO ordinary image `5cf01208…` and separate diagnostic `68a1c304…`. Retained62 remains the initial comparison control. Position owns coherent attack planes; search retains copied-child state, retained evaluation and ordinary/tactical recursion. No additional architectural optimization is selected.

The paired full54 comparison recorded **68.569086 whole-native CPU s corrected** and **68.446861 s retained62**, summed per-case medians: descriptive **+0.178569%**. The corrected image also passes all mandatory checks and one fresh behavioral12/632 plus continuity, seed and interruption lane. That game pass supplies no full12 timing result. The later audited external packet reports the original main image passed the 3,288-game recorded-oracle comparison within its stated limits. Final specification-owner and performance qualification remain separate; see the release manifest for artifact-specific evidence.

For the reproducible four-binary builder and tag-triggered release process, start with [release tooling](release/README.md) and its [qualification manifest](release/qualification.json). No binaries are stored in Git.

For engine history, start with the [local adoption/handoff](experiments/first-main-cutoff-adoption/README.md), [current status](STATUS.md) and [exact artifacts and build recipe](docs/production-build.md). The tested images/profile remain outside Git. Generic development builds do not select the tested own-PGO/ExtTSP artifact automatically. The release builder reproduces the qualified hashes and rejects mismatches against the committed manifest.

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
