# Fresh pawn batch 2 — cold implementation proposal, 2026-10-18

From: imp2 native child fresh_pawn_transport. To: parent imp2. Requested runtime: Sol 6.1 High / Normal; speed control and speed readback unavailable. No Herdr access used.

## Delivery and validation status

Isolated source: `/tmp/imp2-fresh-pawn-20261018-native-child`. Source was copied from `/tmp/imp2-eval-observers-20261018`, excluding every `target`, `evidence`, `.git`, and `__pycache__` directory. A pre-edit cold snapshot is in `base/`; its full file hashes are `base-source-sha256.json`. No live root source, live diagnostic source, other proposal, optional route, or retained pawn lifecycle was modified.

Only read/inventory/write helpers were executed. No builds, tests, rustc, engines, profilers or formatter ran. Source validation, all seven added unit tests, and complete released-fixture comparisons remain for the parent. The proposal does not claim a conformance pass.

Apply `fresh-pawn.patch` from the chosen integration tree root, or use its three file changes when merging with another main.rs expansion. Patch SHA256: `8ea4acb4b417eac79791a6722db75b8f94c42efcb41047925638dca3980eced8`. It is based on the exact baseline hashes below. `proposal-source-sha256.json` inventories all isolated source files.

## Native ownership and schema decisions

- `evaluation.pawnStructure`: fresh native `pawn_structure::fresh`, diagnostic signed doubled weights. No structural penalty or relation lookup is added.
- `evaluation.pawnStructureScore`: the same fresh structure, then native `pawn_terms::structure_terms`; emitted `relationQueries` is exclusively its native selected work.
- `evaluation.pawnPiece`: native fresh descriptors and `pawn_terms::raw_piece_terms`; no phase gating or phase scaling, and no structural relation work. This preserves the raw operation even below the ordinary phase gate.
- `evaluation.pawnPressure`: new narrow `pawn_terms::{PawnPressure,pressure_observed}` exposes the existing private `advance_pressure`, `occupied_pressure` and `rook_line` producers. No formula or table was cloned into diagnostic code; ordinary producers and selection remain untouched.

All exact fields and nested doubled-weight maps are parsed eagerly across all queries before influence/classification/relation work. The existing bounded component placement parser admits artificial boards including attacked/adjacent kings, while requiring one king per color, at most eight nonterminal pawns, fifteen non-kings and the released type limits. Pressure square validation requires a present pawn; color comes from the board. Query count remains 1..4096 and repetitions are evaluated independently.

Native descriptors retain semantic chronology; only a copied descriptor vector is sorted by file then ascending rank for the output boundary. Candidate output uses that same canonical copy. Native structure and piece relation work retains the native white/black, descriptor/piece order. The four specified schemas admit no root/current phase, side, identity, or pawnOrder override, so these are rejected as extra fields. Phase/context independence is preserved by invoking the raw owner for pawnPiece. No broader route or semantic admission was introduced.

## Exact released fixture selection

Select all cases, unmodified, in each of these eight files under `/home/legolas/king-spec/conformance/fixtures/`. `selection.json` contains every zero-based case index, released case ID, operation, query/expected-result count and exact fixture SHA256. Counts describe planned inputs only.

| Fixture | Cases | Queries/results |
| --- | ---: | ---: |
| `pawn-structure-v1.json` | 60 | 4362 |
| `pawn-structure-boundaries-v1.json` | 3 | 36 |
| `pawn-pressure-v1.json` | 68 | 5049 |
| `pawn-pressure-boundaries-v1.json` | 3 | 36 |
| `pawn-structure-score-v1.json` | 74 | 1617 |
| `pawn-structure-score-boundaries-v1.json` | 1 | 2 |
| `pawn-piece-v1.json` | 29 | 982 |
| `pawn-piece-boundaries-v1.json` | 1 | 12 |

Total: **4 routes / 239 cases / 12,096 queries/results**. By operation: pawnStructure 63 cases / 4,398 queries; pawnPressure 71 / 5,085; pawnStructureScore 75 / 1,619; pawnPiece 30 / 994. Relative to the parent-provided 64-route / 3,470-case isolated plan, this proposal alone yields a planned 68 routes / 3,709 selected cases. Do not add earlier selection gaps or score-context work twice when merging sibling proposals.

## Changed source hashes

| Relative path | Baseline SHA256 | Proposed SHA256 |
| --- | --- | --- |
| `diagnostic/src/main.rs` | `c7d9cb3fa625eb73390e4f819e1a37e89b661a8b65d2be07730a5201c302190f` | `806a2cfa48372aad0250dca2518259800c9dc608c66ca569b3058ed5fbcdb530` |
| `diagnostic/src/pawn_fresh.rs` | `None` | `4355774d9f8b5b71e91591c98906f9de730b15f81b14a9a4f7682253167aff3d` |
| `src/pawn_terms.rs` | `41f5b0c8b5e5923dab8a69c4aa7c9dea80d7401225ed4f82f5e0f6701bf71305` | `a2081196fb0bfdbd1ac7830d2f668009b267e77d3e56b92c249af709cd99fff3` |

## Focused unexecuted tests and remaining work

Seven diagnostic unit-test sources cover canonical output versus native chronology; negative doubled-weight floor and duplicate fresh observations; repeated exposed-level relation work and blocked-backward zero work; raw piece output below the ordinary phase gate and explicit zero output; independently observed rookLine despite class precedence and board-derived color; eager nested/later-query validation and request bounds; and broad artificial placement admission with material/pawn-square rejection. Existing native pressure, structure and raw-piece tests were left intact.

No unresolved contract ambiguity was found within these four interfaces. Remaining issues are verification: compile the proposal, execute focused tests, compare all output fields for all 239 cases (including the 12,096 nested results), and perform the normal baseline regression checks after integration. The broad inherited production/lifecycle/qualification obligations in the review remain outside this bounded batch.
