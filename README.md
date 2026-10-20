# Rook2

An independent Rust implementation of the released KingRE ordinary-play
specification. The guiding [mission](../imp-perf-mission.md) and released
[KingRE v2.5.0 contracts](../king-spec/README.md) govern behavior and qualification.

**Retained build: candidate62.** Its native engine and diagnostic source are
unchanged from candidate57;62 adds explicit profile-covered ExtTSP compiler
layout using the existing own57 PGO profile. Position owns coherent attack
planes; search keeps copied-child state, retained evaluation and ordinary/
tactical recursion. The current architecture and its scoped review are indexed
in [STATUS](STATUS.md) and the [production map](docs/production-map.md).

The exact retained ordinary image completed the full54-case collection at
**67.640360 whole-native CPU seconds** and regular12-game collection at
**675.156653 seconds** on Vic. These are local engineering measurements;
**final behavioral and performance qualification remains open**. Finite checks
do not prove every admitted production input, and the full3288-game gate belongs
off Vic. See [remaining obligations](docs/qualification-gaps.md).

Start with [retained artifacts, profile and build recipe](docs/production-build.md).
It identifies the tested binaries and their relocated paths. **Default builds do
not reproduce candidate62 automatically**:62 requires both the matching profile/
training provenance and `--ext-tsp-profiled`. A fresh rebuild is a new artifact,
not an automatic replacement for the tested image.

The ordinary `rook2` executable serves the live King XBoard byte stream. Its
optional `--diagnostic-seed-command` enables the persistent `king_seed` command;
`--work-clock=kingwcr` selects the default work clock explicitly, and
`--work-clock-post=work` enables fine-work posts. The ordinary binary has no
JSON diagnostic mode. The separate [diagnostic adapter](diagnostic/README.md)
serves the mandatory diagnostic operations; `rook2-dev` exposes development
interfaces described in [tools](tools/README.md).

For a fresh **generic development build**, with no PGO or62 layout selection:

```sh
python3 tools/build.py --bin rook2 --output /home/legolas/rook2-experiments/fresh-generic-build
```

The output directory must be absent. Substitute `--bin rook2-dev` for development
commands such as `inspect`, `perft` or `search`; this is not the ordinary protocol
or diagnostic adapter. Consult the retained-build recipe before timing a rebuild.

Navigation:

- [Current status](STATUS.md): retained state, latest closed work and open obligations.
- [Performance ideas/results](docs/performance-experiments.md): brief trials and untried proposals.
- [Production build](docs/production-build.md): exact artifact and profile identities.
- [Evidence layout](docs/evidence-layout.md): retained summaries versus relocated raw records.
- [Historical status snapshot](STATUS-history-20261020.md): preceding checkpoints, not current guidance.
- [Contribution and clean-room rules](AGENTS.md).
