# Retained pawn proposal 02 — lazy miss-only construction

From: native child fresh_pawn_transport. To: parent imp2.

This is a cold performance/chronology correction to proposal 01, not a specification-defect claim. The completed proposal 01 source and evidence remain unchanged. A read-only hash comparison confirms every proposal 01 source file still matches its recorded full-tree manifest.

New source: `/tmp/imp2-retained-pawn-20261018-native-child-02`. New evidence: `/home/legolas/rook2/evidence/retained-pawn-proposal-20261018-02/`. The new source was cloned from proposal 01 with target/evidence/.git/__pycache__ excluded. Only `src/pawn_structure.rs` differs from proposal 01.

Production `PawnCache::select` now calls a private generic `select_with_builder` with `|| fresh(position, influence, [1024; 2])`. Thus native `fresh` acquires the two production pawn-list slices inside the miss-only builder. `select_with_order` passes a separate `|| fresh_with_order(...)` builder. The private generic helper owns the single shared group probe, full-identity reuse, fresh build, and store rule. It invokes the `FnOnce` builder only after the hit return. Dispatch is static and adds no allocation or trait object. The supplied-order adapter still validates every order eagerly, including orders ignored on cache hits.

The accepted `current_candidates` extraction and all diagnostic schemas/routes are unchanged. There are no additional routes. Selection remains two routes / 150 new cases / 6,956 ordered results, with nine existing unexecuted diagnostic tests. One new unexecuted native test checks that zero identity, identity hits, other-group activity and clear preserve builder suppression, while same-group identity replacement invokes the builder. No pawn_terms edit or fresh-pawn native conflict is introduced.

Apply either `retained-pawn-02.patch` to the original 64-route baseline, or `correction-from-01.patch` to an integration tree that already has proposal 01. These are alternatives, not cumulative patches. The full replacement patch includes the unchanged diagnostic and current-candidate work from proposal 01.

- Full replacement patch SHA256: `7076b08b7aeaec42bfbbb0c3440d11e68da49cf6525e402550af9ef7b8ec8b7d`.
- Minimal correction patch SHA256: `6945ad82d115f101de0b0cc2ab3e9af7933faa3c0008f1643e0463ce13a64f77`.
- Prior pawn_structure.rs SHA256: `aafca21bf16be362f66218d0789aabcfa0533765128dcac1be68d3af535326f4`.
- Corrected pawn_structure.rs SHA256: `fe43e640f56c7134f076d59e8177c4e60fbce3a79373b1aa015389ac912b2bf2`.

`base-source-sha256.json` and `base/` identify the original 64-route source. `prior-proposal-source-sha256.json` identifies proposal 01. `proposal-source-sha256.json` identifies the new full source tree; `changed-source-sha256.json` records complete baseline-to-02 changes. `selection.json` preserves exact fixture/case/step mapping and points its twelve-case retained-structure subset at this new evidence directory, so it is self-contained. `correction-receipt.json` records the immutability comparison and patch identities.

No build, test, rustc, engine, profiler or formatter was executed. Only affinity-pinned cold file operations ran. Parent compilation, the new native laziness test, existing focused tests and full fixture/regression comparisons remain pending. No runtime performance claim is made.
