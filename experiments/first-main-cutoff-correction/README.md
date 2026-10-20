# First-main-only cutoff correction: isolated correctness discriminator

**Pass, not promoted.** Retained62 canonical source, binaries and receipts remain
unchanged. The isolated candidate adds only the released first-main upper cutoff
after existing updates and before index advancement/tail dispatch. The seven-line
[production patch](production.patch) adds `index == 0 && score >= request.upper`,
one development cutoff count, and `break`. Existing strict cutoffs leave earlier;
no Q/IIO-pass, widening, preferred/PV, learning or stop rule is rewritten.

| Discriminator | Actual outcome |
|---|---|
| Old production logic with identical new tests | Equality fails specifically with `Err(InternalIterativeOrdering)` instead of `Ok(0)`; both comparison cases pass. Cargo/test exit101 is expected and retained. |
| Corrected actual-owner conditional cases | All3 pass: equality stops before tail; first score below an equal window still enters eligible tail; strict upper hit preserves old cutoff. |
| Complete corrected native library suite |196 pass,0 failed,0 ignored, including existing IIO/extension, interruption/history and retry controls. |
| Generic diagnostic + released focused checker | All1,008 cases /22 complete preselected mandatory files /20 operations pass, including the existing successful-mate continuation fixture. |
| Independent closure | Raw requests/responses, fixture projections, native exec/argv/PID/wait/affinity, binaries, source maps and canonical preservation pass. |

The conditional tests use actual generated child states and `visit_ordinary_impl`,
with supplied parent/child TT records and the existing disabled-IIO tail sentinel.
They inspect actual stored parent records through a `cfg(test)` accessor and
verify original preference/PV, parent learning, main/tail search counts, history
restoration and post-FULL parent retained state. The equality completion store
has neither score permission; the strict control retains normal preference,
learning and Lower storage. These are controlled internal contexts, **not an
admitted public fixture or native equality witness**. No expected answer enters
the engine or native supervisor. [conditional-tests.patch](conditional-tests.patch)
is identical for control and candidate.

The accepted strict-recursion theorem applies to an **actual ordinary/Q entry**
with L<U under its stated premises. A strict requested root window can collapse
before that entry. Whole-search preservation needs coupled prior state and no new
equality edge in preceding execution; this experiment claims no strict-ordinary
to equal-descendant reachability or unconditional whole-search equivalence.

## Exact setup, evidence and boundaries

[plan.json](plan.json) freezes source/tool/runtime hashes, generic x86-64 compiler
flags, commands, per-stage limits and the single900-second monotonic clock.
[retained-base-map.json](retained-base-map.json) binds all117 retained files;
[control-source-map.json](control-source-map.json) and
[candidate-source-map.json](candidate-source-map.json) bind the isolated copies.
The only release behavior delta is the production patch. Apply the conditional
patch to the validated base for control, then the production patch for candidate;
retain separate Cargo target directories. No ordinary executable was built.
The new diagnostic is generic non-PGO O3/thinLTO/one codegen unit/debuginfo1;
actual flags and Cargo artifact profiles are retained in the plan/results.
Native library tests use the normal debug/overflow-checking test profile.

[selected-fixtures.json](selected-fixtures.json) predates execution and names all
files/operations/counts/hashes. The unchanged released `conformance/run.mjs` checks
every case in those files. `capture.mjs` records its original spawnSync exchanges;
`native_launch.py` supervises each CPU14 child with inherited protocol pipes.
These capture/supervisor bytes are reused unchanged from the exact62 closure.
Builds, native library tests and helpers use H=`0–5,8–13`; no owned15.

`run_lane.py` starts the clock immediately before the control Cargo stage and
stops at an unexpected outcome. `reconcile.mjs` independently consumes every
captured request/response and receipt, using the frozen fixtures offline. There
were no routine repairs, repeated case runs or unplanned native stages. The lane
including independent closure finished within900seconds (126.005seconds resource
accounting, not a benchmark). Actual terminal `78cb6d/0`, session32560; every owned
group and all1,008 diagnostic children/1,008 supervisors are terminal.

Raw builds, isolated trees and all20,516,503 raw protocol bytes remain outside Git:

`/home/legolas/rook2-experiments/first-main-cutoff-correction-20261020-01/`

The generic diagnostic SHA256 is
`68a1c304f76435e4c100086d1a303b8dc94d8b5ecd63d26be834e3737bca2dda`
(14,038,952bytes). [result.json](result.json) binds its exact path, both test
executables, original logs/terminals, source maps and independent reconciliation.
Post-exec `/proc` observations exist for1,007/1,008 children; one completed before
that point observation. Its successful audited exec, pre-exec affinity, complete
streams and native wait/exit0 are retained; its unavailable observation remains
explicit, with no retry or substituted value.

This is the selected finite correctness result. No timing, PGO, full54/full12,
ordinary image, source promotion, artifact-wide qualification or external action
was performed. Further implementation/artifact decisions remain with the lead.
