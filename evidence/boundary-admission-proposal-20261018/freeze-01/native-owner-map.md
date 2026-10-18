# Native owner map and production scope

| Observation / decision | Owner |
|---|---|
| Historical count, equality, reversible tail, null handling | unchanged SearchHistory::{new,push,mark_root,repetition_count,short_reversal}, Boundary; cold adapter only reconstructs supplied context. |
| Repetition draw then next-ply clearing then guarded reversal | score_context_transport's exact shared-native-seams-v2.patch, ordinary_policy::early_draw(history,explicit_ply,checked,analysis,upper,learning). Original ordinary p and Q entry.ply remain the scalar sources. No charge moves. |
| Full-to-Q gate | extracted original ordinary policy depth<=0 || ply==63 || ply>=maximum_depth to quiescence_handoff. Ordinary adopts helper before charge. Diagnostic converts absolute target to remaining depth only. |
| Checked/no-legal-reply score | extracted original ply-10000 to mate_score. Ordinary and Q adopt helper at their existing terminal return expressions, with their unchecked alternatives unchanged. |
| Mate-leaf decisions | new bounded ordinary_policy::mate_leaf native component, explicitly SEARCH-MATE-LEAF rather than full mate engine. Calls shared early_draw upper0, then final-ply/noncheck guard, then static FnOnce legal-count dependency and native mate_score. |
| Check and full legal reply count | unchanged movegen::in_check and generate_legal/MoveList. Position route computes auxiliary inventory even when native leaf skips its count dependency; supplied route increments replyQueries only inside its FnOnce closure. |
| Fresh position and exact raw flags | existing Position::from_fen via neutral-flags positions::sequence_position + bounded_material; existing cold flags parser to native rights/EP. No copied placement or legal-generation algorithm. |

Only src/ordinary_policy.rs, ordinary.rs and quiescence.rs change natively. No source layout, hot fields, SearchHistory state layout, default observer API, node-charge locations, evaluation, Q final-ply evaluation or recursive ordinary mate probe changes. Released ordinary-iterations.md explicitly uses SEARCH-QUIESCENCE-TREE for the ordinary checking probe; no missing full-mate production feature is inferred. Shared EvaluationBounds is a prerequisite owned by the other child and is carried exactly, not independently reimplemented. Native-dependent.patch excludes that already-shared prerequisite.

Shared prerequisite is frozen patch55851159a84b0b2ef861be84f49b12bc03a477056550d64718b4c5fa74528abe. Parent centrally composes it once. This proposal's own native delta applies after that prerequisite, alongside a separate cold adapter patch. Full proposal.patch is supplied against exact88 for independent review. These source changes need native build/test and ordinary codegen review after parent scheduling; there is no CPU-neutrality claim.
