# Current implementation status

**Retained candidate62; optimization goal paused.** Updated2026-10-20.
Candidate numbers identify artifacts/ideas, not a count of completed trials.

Candidate62 keeps candidate57's native engine and diagnostic source. Its only
promotion delta was `tools/build.py`: explicit profile-covered ExtTSP placement
using the immutable own57 profile. It was adopted from the tested isolated-path
artifact; no canonical-path rebuild or fresh training is claimed. The
[build guide](docs/production-build.md) gives exact image/profile/source identities,
relocated binary paths and the explicit recipe. A default build does not select62.

| Recorded workload on Vic | Whole-native CPU seconds |
|---|---:|
| Complete54-case suite | **67.640360** |
| Regular12-game collection | **675.156653** |

New62 ordinary-image checks cover the paired fixed70 screen, full54 collection
(216 fresh lifetimes,432 offline checks,2496 posts), wire8/24 and regular12
(48 fresh lifetimes,2528 searches,23204 posts). Existing195 native tests,
209 diagnostic tests,7673 mandatory cases/117 operations/115 whole fixture files,
and57 continuity/seed/persistence controls are **reused unchanged-source and
exact-companion evidence**, not new62 executions. See the frozen
[source promotion](/home/legolas/rook2-experiments/original-worktree/evidence/exttsp-profiled-integration-20261020-01/source-promotion.json),
[whole54](evidence/exttsp-profiled-standard54-results-20261020-01/README.md) and
[whole12](evidence/exttsp-profiled-games12-results-20261020-01/README.md) reports.

Finite checks are not final qualification. Separate-window and cross-hardware
comparisons remain descriptive; no universal Vic-to-Bee conversion is established.
CPU15 observations and unavailable per-search values retain the reports' limits.

Latest closed work:

- Experiments63–67 are parked; none replaced62. See the
  [brief catalog](docs/performance-experiments.md) for ideas and results.
- Whole-Activity repeats were too low to select caching. The generation-safety
  census completed195 native tests and two exact live/offline observations;
  checked off-mask rejections already avoid projection. It selected no new
  optimization or speed estimate. See the
  [census](evidence/current62-generation-safety-census-results-20261020-01/README.md).
- Current62's modeled branch/cache study retains a strict failure: header summary
  exceeds SELF/footer/log totals by2 simulated instructions. Its partial findings
  do not establish hardware costs or a qualified profile.

Remaining obligations:

- Complete the production-domain review, including global TT/window/score/IIO/
  stop joins, uncertified-hint admission, remaining caller/arithmetic premises,
  command/framing/poll/publication behavior and admitted diagnostic combinations.
  Local source lemmas remain conditional. No admitted empty-source hint witness
  or general fallback rule is established.
- Qualify whole54 and whole12 performance with compatible comparisons,
  repeatability/uncertainty and resource/private-memory/no-swap scope. Historical
  Rust-PGO totals are63.431779s/644.222971s; raw ratios alone are not acceptance.
  PMU remains unavailable on Vic.
- Prepare the exact artifact/evidence handoff for the external3288-game gate.
  Regular12 success does not pass it. No new external run, export or gate launch
  is authorized by these notes.

The authoritative detailed scopes remain in the
[production map](docs/production-map.md), [qualification gaps](docs/qualification-gaps.md)
and [Vic gate scope](docs/qualification-scope.md). The implementation goal remains
paused; this update performs no engine work or new measurements.

Historical checkpoints and raw records:

The complete preceding STATUS is preserved byte-for-byte in
[STATUS-history-20261020.md](STATUS-history-20261020.md). Its “current” headings
refer to their original checkpoints; they do not supersede this page. Historical
qualification/map snapshots remain indexed by the detailed documents.
Small reports/setups remain in `evidence/`; binaries, profiles and raw streams are
under `/home/legolas/rook2-experiments/original-worktree/evidence/`. Frozen reports
keep their original paths and commit IDs. Use the [relocation guide](docs/evidence-layout.md)
and history maps rather than editing frozen provenance to make paths look current.
