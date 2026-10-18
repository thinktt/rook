# Fresh pawn phase/subtotal proposal — 2026-10-18

Prepared by `/root/score_context_transport` for `/root`. Requested Sol6.1 High / Normal; runtime speed controls/readback unavailable. All shell work used affinity `0-5,8-13`. No Herdr, Imp1/Rook source, subagents, builds, tests, rustc, engines or profilers used. Counts below are source/fixture inventory, not passes.

## Ownership and exact artifacts

Predecessor: `/tmp/imp2-eval-pawn-context-20261018`, parent-reported passing 71 routes / 4177 cases / 70 diagnostic unit tests. New unique proposal: `/tmp/imp2-fresh-pawn-subtotals-proposal-20261018-wmbve21y`. Writes were confined to that new isolated copy and this evidence directory. The completed score-context proposal and live root source remain unchanged. The copy excludes targets/evidence.

Only four diagnostic files differ: `main.rs` adds the six dispatch routes; `pawn_progress.rs` exposes its unchanged supplied-candidate parser to sibling frontend modules; `scores.rs` exposes its unchanged eleven percentage field names; new `pawn_subtotals.rs` contains transport and seven unrun focused tests. **There are no native changes**, including no changes to native pawn_structure.rs or pawn_progress.rs. No merge conflict with the retained sibling's native helper proposal is expected. Parent owns integration/review and execution.

`proposal.patch` is the exact unified patch against the named predecessor. `source-hashes.json` records before/after hashes for all changed files and the complete proposed Rust-source manifest. `plan.json` extends the exact predecessor fixture selection with four complete released fixture files, recording hashes, case IDs and per-operation case/query counts. `spec-hashes.json` identifies the released contracts read.

## Native-backed composition and admission

Both phase routes compute fresh native structure with doubled weights 1024 and call `pawn_terms::compute_with_phase`. One accepts an independent supplied phase; the other derives phase from the placement. The native producer owns the >16 piece-work gate, per-color rounding and selected structural/piece R charge. No phase formula is copied.

The supplied subtotal route preserves independent structural/piece/candidate scores and ending inputs, even when they cannot derive from placement or phase. Candidate subtotal preserves its supplied candidate subsets, including empty lists and present pawns that fresh classification would not select. Its ordered lists reach native `candidates` and `ending`. Both routes use native `fallback`, `structure_weighted`, and `weighted`, preserving separate signed rounding and actual-count fallback. Their relation charge remains zero; no fresh structure calculation replaces controlled terms.

Fresh subtotal validates complete semantic pawn orders, then passes them to native `fresh_with_order`. It calls `compute_with_phase` and the production `pawn_progress::selected` composition; therefore selection order, equal-path terminal retention, fallback, material clamp and intermediate weighting remain native. Candidate arrays serialize descriptor chronology without sorting. Only the native phase/term producer supplies R. Each query owns fresh descriptors and influence; no cache or identity-based admission is used. Empty/zero-identity and full-identity collision placements remain independent fresh observations.

Context subtotal validates both bounded placements, independent root/current sides, every percentage including ignored king/mobility/safety fields, depth, and complete current pawn order. Native `RootContext::new` binds root phase, root counts/side and material percentages; `material` evaluates current counts. Native `coefficient` binds pawn/central effective weights to root ownership. Current `Position::phase` weights fresh pawn and central terms. Produced coefficients through 10240 are passed directly to native composition instead of being rejected by the distinct 10000 supplied-weight domain. `positional_terms::central` shares actual current influence and adds no R. No complete evaluator or retained lifecycle is constructed.

Every input object uses exact fields and existing bounded validators. All queries are parsed before influence production or selected work, so ignored dependencies and later malformed queries are not suppressed by an earlier semantic gate. No legal history between placements is required. No numerical scoring formula is cloned into transport.

## Inventory and focused source tests

New mandatory operations: pawnPhase 34, positionPawnPhase 31, pawnSubtotal 16, candidatePawnSubtotal 34, freshPawnSubtotal 66, contextPawnSubtotal 13 = **6 routes / 194 cases**. Whole selection becomes **77 routes / 4371 cases**. Seven diagnostic tests added as source give **77 source-declared diagnostic tests**; none were executed.

Tests isolate supplied versus derived phase and R gating, signed half rounding and preserved controlled terms, empty supplied candidate subsets with actual-count fallback, order-sensitive terminal/fallback behavior, root-side coefficients versus current-side/phase including 10240 production, strict ignored-field/order validation, and independent zero/colliding identities. Full released-fixture comparison remains the parent's decisive check; these focused tests do not substitute for it.

## Remaining review and risks

Parent should format/review the new module, run the seven new unit tests with the full diagnostic suite, compare all 194 new fixture cases separately from predecessor rechecks, and merge the three small visibility/routing edits with any sibling frontend changes. The source has not been compiled, so type/format integration remains unverified. No native code or hot evaluation behavior changed, but ordinary project integration checks still apply. Retained cache lifetime, search-pawn sequences, complete Full/fast evaluation, and production/gameplay/performance qualification are outside this bounded batch. No optional operations were implemented.
