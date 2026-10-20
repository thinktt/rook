# Three-unit functional cost study

This isolated diagnostic compares four routes for three released semantic units:
opening evaluation through scalar and production-coherent influence producers,
opening position history, and light-start ordinary search. It preserves retained62
and makes no production promotion or qualification claim. See `report.md` for the
closed outcome and `collector.md` / `FUNCTIONAL-COST-SOURCE.md` for exact scopes.

## Reproduction

`derivative-source.json` pins the retained62 baseline and all changed bytes.
`study.patch` contains the complete derivative. Reconstruct into an absent external
directory with `prepare_source.py --baseline /path/to/retained62 --destination
/external/absent-directory`. The 76 resulting native/tool files must match
`functional-source-manifest.json`; the original numerical/search routines stay
unchanged. The patch adds a cold module/bin and locked serde_json dependency.

The executed instance uses these fixed roots:

- W: `/home/legolas/rook2-work/imp2-functional-cost-20261020-01` (external symlink target).
- B: `/home/legolas/rook2-experiments/functional-cost-three-unit-20261020-01`.
- Helpers: CPUs `0-5,8-13`; native training and collection: CPU14, no owned work on15.

Before a new independent instance, select fresh roots in the setup; never reuse
the closed instance or replace its samples. Extract only each public unit's
`workload.request.input` into B/inputs/ROW.json, and its `expectedProjection` into
the separate B/expected/ROW.json. Evaluation rows share the same public unit.
Keep expected data on the checker side. Bind the frozen manifest and public
inputs before building.

Run `build_study.py STAGE --source-manifest W/functional-source-manifest.json
--execute` sequentially for `build-instrumented-wire`,
`build-instrumented-functional`, `train`, `build-use`, under housekeeping affinity,
`PATH=/usr/bin:/bin`, `TMPDIR=/home/legolas/rook2-build-tmp`, and
`PYTHONDONTWRITEBYTECODE=1`. The training stage runs the original public54 replay
checker and four explicitly separate functional coverage lifetimes; its own
profile is independently remerged before use. The two narrowly adapted build
helpers remain external; canonical tools stay unchanged. Captured stage-pipe caps
do not cover canonical Cargo log files, which are separately retained and sized.

The actual use artifact is B/build-use/rook2-functional-cost-exact, mode0555.
Complete projection checks, source/reset/consumer review and native-job closure
must precede collection. Create `execution-clearance.json` from the inert template
with actual ELF, source, profile/provenance and runtime bindings. This is an
execution binding, not a request for an additional approval chain.

Run `collect.py --engine ELF --output FRESH_EXTERNAL --stage calibrate`, record
its observed outer tool completion in that directory's tool-terminal.json, then
`collect.py --engine SAME_ELF --output ANOTHER_FRESH_EXTERNAL --stage collect
--calibration CALIBRATION_DIR/calibration.json`. Counts freeze from one short
probe per row; no retiming or sample replacement. One excluded warmup and three
measured batches per row have separate exact projection checks before and after.

All native processes use the unchanged owned-accounting wrapper. A failed
postexec placement observation, output/projection mismatch, unresolved clock or
timeout stops the stream with its failure preserved. Do not hide that failure by
retrying. Raw requests, outputs, CPU/wall samples, profiles, binaries and build
products belong in B, outside Git. Keep only setup and concise reports here.
