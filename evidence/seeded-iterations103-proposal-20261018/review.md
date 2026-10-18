# Seeded completed-iteration source proposal

Frozen source: `/home/legolas/rook2-work/imp2-seeded-iterations103-proposal-20261018-nhkezghb`. Exact parent: `/home/legolas/rook2-work/imp2-iterations-clock102-proposal-20261018-kkhjipnc`. This is SOURCE-ONLY and UNRUN: no compiler, test, engine, codegen, profiler, PGO or timing execution. The source-only Python helpers use housekeeping0-5,8-13. Root, frozen parent and earlier evidence are unchanged.

## Native ownership

Only `src/ordinary.rs`, `diagnostic/src/root_iterations.rs`, `diagnostic/src/main.rs` changed. `run_iterations` (ordinary.rs419) delegates to one private `run_iterations_inner<const SEEDED: bool,F>` (448), with explicit false mode. That false branch retains the old requested-child `-10000/-lower` window and raw returned score, and has no raw observation callback. The new `run_seeded_iterations` (433) selects true mode, immutable seed/rnd arguments and a statically dispatched raw-return callback. Both entries use the same actual root-generation, child creation, history push/pop, recursive visit, stable root ranking and iteration loop. No second root algorithm lives in the adapter.

Seeded adjustment (476) calls actual `timed::random_adjustment`. The requested child window (487) subtracts that adjustment using actual `timed::score_add`, then negates and exchanges bounds for `visit_ordinary`. Actual child return is negated at501; the raw observer runs once on that normal root result at502, before native score_add. It does not run for a stopped root. Adjusted score immediately controls ranking/following windows/PV in the existing loop. Seed does not advance, and zero is not a clock-seed sentinel. No time/host/PRNG substitute is involved. Existing fixed-completion depth/budget and root preparation/work-reset behavior remain shared.

The raw-score callback is necessary: clamping prevents recovering rawScore by subtracting adjustment from the final score. Parent accepted this narrow API and explicit false specialization before freeze. The adapter stores a flat raw-return sidecar outside Search, consumes it in ordered Step traversal and rejects missing/extra observations. It reuses the same pure native helper to project adjustment and root-oriented transformed `childWindow` metadata. All outputs are built after successful full completion and existing qualification; an error returns no partial successful output.

`first_iteration::Step`, ordinary Iteration/Outcome, Node, Retained, Evaluation, Position, Search, Config and recursive ordinary function bodies are unchanged. Source checks bind full unmodified modules and compare `store_ordinary` onward byte-for-byte. There are no new fields, dynamic dispatch/vtables, maintained seed state or recursive observation mode. Default entry is source-specialized, not reliant solely on propagation of zero constants.

## Admission and retained context

root_iterations.rs19 accepts either exact released default coefficients with md2..4, rnd0..1000 and completed2..4<=md, or one exact selected vector (rnd75/10/20, md99, completed2). Default tts75497472 is distinct from old ordinary neutral tts67108864; that distinction is preserved. Selected vectors reuse exact old selected coefficients with their exact seeded randomness restored; a source-only comparison independently reconstructed all30 fields against the released vector JSON in NAMES order.

All six input fields and five control fields are exact. Seed is explicitly unsigned32, including0 and high-bit values. Missing/extra fields, malformed controls and all move coordinate shapes are rejected before root setup/legal history replay. No fallback defaults, profile names or omitted controls. Initial validity/EP checks, legal move history replay, chronology, mark_root and root-side parameter binding use the existing parser/Parameters::bind. Reached root phase, my/op color ownership, draw preference and variation range remain in their existing actual native owner through all descendants. The seeded path does not convert final FEN into history or rebind coefficients per current side.

Existing `qualified_ordinary` is unchanged: reject IIO tails, pass/initial-phase mismatch, nonzero fresh extension and accumulated extension. Existing PV<=63, result/Step bounds, fresh ordinary state and node budget4095 are unchanged. The4096th unit remains an error, not a partial result. No relaxing of selected/default admission or IIO qualification.

## Declared test sources, not executed evidence

Two native declarations were added:

- Zero-randomness seeded vs old fixed wrapper across White start, sparse rook/knight and Black reached-position roots: compare full Step/candidate/PV/work records and all raw-score order; history unwinds.
- Explicit seed0/rnd50 first raw score/PV/work compared to a direct actual recursive child call; check complete ordered raw/adjusted returns over two iterations, real legal PVs and immutable per-move adjustment. A node-limit0 stopped root observes no raw score and restores history.

Four cold declarations were added: exact default/selected vectors and md/completed/rnd bounds; malformed seed/control domains before illegal replay; retained Black move history and seed high bit; zero-randomness full response schema/raw/adjusted/window equality and fresh repeated results. Existing tests were not weakened.

Actual source counts: native153 library+2dev=155 declarations, DIAG175 declarations. These are NOT executed pass counts. Expected union:103operations/7514cases/100whole fixture files. The five new cases come from both complete released seeded files (2default+3selected). Source closure remains102 files =43native+23tools+36DIAG; operation103 is not a source-file count. Inventory includes all98 inherited whole files unchanged, all unique IDs and operation counts, plus both new files. Expected outputs are never copied into native/adapter runtime code.

## Review limits and downstream gates

This proposal has not been Rust-parsed, compiled or executed. Source/Python metadata checks establish closure/vector/count/unchanged-owner evidence, not Rust typing or behavioral success. Native generics and cold raw sidecar iteration need compilation. Root-only const/closure specialization may instantiate extra root bodies; default and seeded wrappers' calls, frame, total text and stripping of false helper/callback branches need scoped emitted-code review later. No default code-size or CPU improvement is assumed. Cold sidecar allocates only for the new seeded diagnostic, outside the hot recursive state; the old cold ordinary path creates an empty Vec and never pushes it.

Parent review/explicit execution clearance precede native155 and DIAG175 tests, generic image freeze, strict54/eightwire24, full103/7514/100 raw/expected/exit reconciliation, and default codegen checks. The original five seeded cases must compare every ordered root transformation, score, child/root PV and work checkpoint. The old102 fixture union must also pass unchanged. The root5 controller remains deferred and is not part of this patch. No source improvement or timed/PGO experiment was bundled.
