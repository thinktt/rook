# Retained pawn batch 3 — cold implementation proposal, 2026-10-18

From: imp2 native child fresh_pawn_transport. To: parent imp2. Requested runtime Sol 6.1 High / Normal; speed controls/readback unavailable. No Herdr access used.

## Scope and evidence status

Isolated source: `/tmp/imp2-retained-pawn-20261018-native-child`. This is a new copy of `/tmp/imp2-eval-observers-20261018` (the parent 64-operation prototype), excluding every target/evidence/.git/__pycache__ directory. It does not incorporate the separate completed fresh-pawn proposal. No live root, other proposal, or completed fresh-pawn artifact was modified.

Cold work only: file reads, source edits, and inventory/patch/hash generation. No builds, tests, rustc, engines, profilers or formatting runs were executed. Nine focused test sources are provided and remain unexecuted. No conformance pass is claimed.

Full patch: `retained-pawn.patch`, SHA256 `2eb2a16afbf37e4b370952625ed8d928b86bc55ba4880ed8e6ce16623a8b4989`. Optional split patches are `native.patch` (`34bb7bd15bdb5ad37e56aa501e4bc570c56d2f61adf995ddeae0e08d0cdb9e90`) and `diagnostic.patch` (`8e0824aaf4aeb2a2424292b7f8248a6911ce3041f9bac82224e80cd802801d61`); apply either the full patch or both split patches, not both alternatives. Pre-edit source snapshot is `base/`. Whole-tree identities are `base-source-sha256.json` and `proposal-source-sha256.json`; exact changed-source identities follow below.

## Native ownership and transport

1. `PawnCache::select_with_order` is a narrow new entry point. Existing `select` delegates with Position pawn chronology. Both use the same 128-group full-pawn-identity probe and early reuse rule; only a miss calls `fresh_with_order`, with fixed doubled coefficients 1024. No full-pawn-set comparison, supplied identity, valid flag or forced rebuild was introduced. This preserves zero-identity empty reuse, equal-full-identity collisions, replacement within a group, other-group isolation and explicit all-group clears.
2. `pawn_progress::current_candidates` extracts the current-square/color membership filter from native `selected`; production selected now calls the same helper. It writes surviving candidate squares in retained order to the existing eight-element buffer. Diagnostic code uses the shared filter, native `candidates`, and native `ending`. The last call is the existing raw selected-ending seam, with nonempty guard. Diagnostic code never calls `fallback`, `weighted` or the aggregate `selected` result whose ending already includes fallback.
3. `positions::identity` becomes `pub(super)` so the new transport reuses the existing complete identity projection without duplicating it. Identity remains derived from actual placement; side-to-move and supplied pawnOrder do not alter the fingerprints.

`pawn_retained.rs` parses and validates the entire request into typed steps before constructing the request-local PawnCache or producing influence. Every step checks exact keys, complete distinct same-color current-pawn order (including ignored order on a hit), bounded placement, Boolean clear, and side where applicable. A cache is created once per request, clear executes immediately before its step, and the result vector follows step order. Structure output preserves retained semantic order directly; it deliberately does not reuse fresh canonical serialization. Candidate output adds no newly present pawn absent from retained descriptors. Empty selected pairs return both progress scores and raw ending zero.

No code in `pawn_terms.rs` changed, so there is no native overlap with the fresh-pawn pressure wrapper. The shared integration touchpoint with that proposal is only main.rs module/routing insertion. Neither optional route nor retained subtotal/search/session lifecycle scope was admitted. Existing native production select/selected semantics are preserved by delegation/extraction; the parent must still execute native regression checks after merging.

## Exact released selections

`selection.json` gives every source fixture hash, zero-based case index, case ID, operation, steps and expected-result count. It also supplies a driver-friendly `fixtures` map. All 150 new cases are unmodified released requests/expected payloads.

| Fixture | Selected/source cases | Steps/results |
| --- | ---: | ---: |
| `identity-retention-v1.json` | 12/15 | 1048 |
| `pawn-full-collision-v1.json` | 32/32 | 256 |
| `pawn-retained-consumer-v1.json` | 106/106 | 5652 |

Total: **2 new operations / 150 cases / 6,956 ordered step results**. retainedPawnStructure contributes 44 cases / 1,304 steps; retainedPawnCandidates contributes 106 cases / 5,652 steps. The isolated base would become a planned 66 operations / 3,620 selected cases after execution succeeds; this is not a verified count.

The mixed identity-retention file contains three already-selected `position.identity` cases plus twelve new retained-structure cases. `selected-retained-structure-cases.json` selects only those twelve new cases for independent batch validation. For the integrated plan, either retain the baseline three-case selection and add this twelve-case subset, or replace the baseline subset with the whole released identity-retention fixture. Do not count its three identity cases twice. The collision and consumer fixtures are wholly selected.

## Changed source hashes

| Relative path | Baseline SHA256 | Proposed SHA256 |
| --- | --- | --- |
| `diagnostic/src/main.rs` | `c7d9cb3fa625eb73390e4f819e1a37e89b661a8b65d2be07730a5201c302190f` | `e031128ae6d4e3fb4b41afbfd258d390a13e6f662b3b3255d9a7ddad536f90de` |
| `diagnostic/src/pawn_retained.rs` | `None` | `376194968d3d957429681abc0be9a079a5ad028461ae678a4186b3dee3312b5c` |
| `diagnostic/src/positions.rs` | `910ca839a73ecede9fd34583d87aa746d66a292e86cf89087600bc5bc1d8d15b` | `a3769d0728ba81d9423344e37ccec524a6aac1307ac2cd0b4af4185bbaafb52a` |
| `src/pawn_progress.rs` | `efb62166204229ad18c319eca2c6dc2bf0aad60bff8e57c2eff3d580b3b64934` | `0bca6bb9678657b2efadc023c07d1ffcc9ff91c1c97553b84e2131c6ce30d9dc` |
| `src/pawn_structure.rs` | `64473dc7b7d3d235b86caec1e8755d7edb0deae895de26b7129a65b1202bf04c` | `aafca21bf16be362f66218d0789aabcfa0533765128dcac1be68d3af535326f4` |

## Unexecuted focused coverage and remaining verification

Nine test sources cover request-local cache reset and order retention, zero identity reuse and replacement, group isolation and clear-all behavior, genuine full-identity collisions with all candidates absent, partial collision membership without appending current-only pawns, retained-order tie endings through clear/reuse, raw ending versus material fallback and queen turn offsets, eager invalid later-step/order rejection, and broad component placement admission with exact material bounds. The collision/ending examples come from the released contracts/fixtures.

No unresolved specification ambiguity was found in these two routes. Remaining work is execution: compile, run the nine added tests and relevant native tests, compare complete output of all 150 cases including all 6,956 results, and perform integrated baseline regressions. Full evaluation/subtotals, search-start clearing, cross-search/session lifetime, production review, gameplay and performance qualification remain outside this bounded batch.
