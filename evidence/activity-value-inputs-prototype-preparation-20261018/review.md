# Stateless activity destination value inputs: source prototype

Prepared source only; nothing compiled, parsed as Rust, formatted, tested or run. This is a candidate for parent review, not adoption or a performance claim. Only this new evidence directory is owned/changed.

## Exact basis and files

`base-src/activity.rs` is copied from `evidence/complete117-pgo-use-build-20261018/source-before/src/activity.rs`, the archived69-source basis of exact own-PGO image `6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50`. The canonical receipt already binds that source file as `07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38`. Actual byte comparison97a3db exited0. These are existing receipt identities plus a fresh file comparison; no new full-source/hash/archive verification is claimed.

`proposed-src/activity.rs`, `proposal.patch`, `inverse.patch` and the literal `prepare_source.py` make the one-file change reviewable. `scope-proof.json` records unchanged source sections and the7→8 activity test declaration delta. No original source, tools, fixture or oracle is edited.

## Change and algebraic equivalence

One immutable private static contains256 u8 values: two colors × ordinary/rook-seventh variants ×64 physical squares. Its const constructor uses only the existing DESTINATION_VALUE and ROOK_SEVENTH constants. It never runs during search and creates no runtime fill, cache, validity bit, counter, allocation or mutable state.

For color c and physical square q, define r=q/8 for White and r=7−q/8 for Black, f=q%8. Ordinary view[c][q] is exactly DESTINATION_VALUE[r][f]. Rook view[c][q] substitutes ROOK_SEVENTH[f] exactly when r=6 and otherwise equals ordinary. Current Color encoding is White0/Black1 (`source-before/src/types.rs:8–14`); the coherent activity destination domain is q<64. Existing debug bounds and Square(target&63) remain unchanged.

`compute` binds the color's two views once, then retains the existing four const-kind accumulations in the same order. Within each actual piece iteration, `piece_destination_values<KIND>` selects ordinary for every nonrook. A rook reads the same opposing king and uses the identical original condition `relativeRank==7 || (relativeRank==6 && file>=6)` to select its view once. The inner knight/ray loops replace only destination-value coordinate selection with values[target]. This moves destination-value variant selection out of the target loop while retaining per-piece rook admission (the original opposing-king admission was already outside its target loop). There is no new semantic query and no change to movement traversal or charge chronology.

Mobility categories/total/queries retain i64/i64/u64. Value elements remain u8, cast to i64 at the same multiplication. Category, destination value, and vertical multiplier are multiplied/accumulated in the same order. The direct/additional switch, transparency, mark writes, rook vertical multiplier and all R increments are unchanged. Piece scoring, low-mobility logic, source profile sums, pressure and final weighting are byte-identical. LOW_MOBILITY orientation is deliberately outside this first narrow trial; no pressure/category transformation is bundled.

The per-piece selector removes unused opposing-king/rank calculation from nonrook slider source code. It does not remove a charged relation query or change any evaluator/state result. Eligibility for a rook is still established only when visiting an actual rook, so an empty rook list creates no extra opposing-king lookup.

## Source tests and independent evidence

All seven original activity test bodies are byte-identical. Their private destinations wrapper only supplies the newly required value view to the same const-kind producer. The new single test checks every physical square in both views/colors through the inverse relative-coordinate mapping, then checks actual synthetic positions at the opposing-king file boundary f7/g7 and rank neighbors h8/h6 for both colors. It also checks that knight/bishop/queen select ordinary values despite rook-eligible king positions. These are general coordinate/admission witnesses, not public fixture answers. All tests remain unrun.

The separate full coordinate activity/influence oracle is not edited, taught the new table or replaced with the constructor. Its existing independence must be retained in future validation. This local transformation test cannot substitute for that complete-output/marks/R comparison or search regressions.

## Reason for experiment and remaining gates

Current fixed35/08 evidence is documented in `current117-evaluation-profile-review-20261018-score-context/review.md`. In35, exclusive displayed activity-owner rows account for11,324,462,593 simulated Ir (23.2314%); identified activity destination lines223–307 account for2,102,824,850, and shared relative_rank137 for592,226,863. The latter are source subsets, not additional owner cost or a removable-instruction forecast. Relative_rank remains needed for rook eligibility, piece scoring and exemption. The existing pressure_value/profile_sum/width trials are distinct and remain parked.

Private helpers now carry a static view reference. Public Activity, Node, Search, Position and evaluator interfaces do not change, but source signatures do not prove zero emitted argument/frame cost: inlining, spills, bounds checks and call factoring can change. The new static has a256-byte source payload; emitted rodata growth/constant folding is unmeasured. A later backend review must compare exact default activity/full/ordinary/Q scope, actual argument/call/frame lowering and surviving coordinate work. Compiler hoisting may already perform part of this transformation. Functional native/oracle/strict54/eight-wire gates and a matched CPU pilot remain separate parent-authorized steps. No gain, unchanged emitted layout, or neutrality claim is made.

## Actual preparation closure

Text derivation5758a1 exit0; patch/declaration display4050ae exit0; exact base comparison97a3db exit0; scope/inverse proofce65f5 exit0. A bounded source-path searchb59905 returned2 because an old guessed evaluation-geometry evidence path was absent; the existing activity-specialization record was successfully read, and no compiler/engine failure occurred. Every helper ran on0–5,8–13 and returned an actual terminal. Zero owned jobs remain. No Rust parser/formatter/build/test/engine/profiler/Git/hash/archive command was launched.
