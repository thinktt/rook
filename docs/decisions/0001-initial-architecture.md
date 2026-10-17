# Initial architecture decision

Date: 2026-10-17. Owner: imp2. Status: implement provisional baseline.

The independent critique from `imp2-lead` is retained at
`/home/legolas/agent-memos/imp2-lead-to-imp2-initial-architecture-20261017T172011Z.md`.
It found the proposed baseline credible and no contradiction in the ownership
model, while challenging the experiment boundaries. It is advisory, not an
approval or qualification receipt. No Imp1 source or architecture was consulted.

Imp2's decisions:

1. Implement the compact mailbox/type chronology, copy-child baseline. Keep it
   provisional until a representative full/fast/pawn-retention/TT mix exists.
2. Separate candidate geometry examination from full semantic child production
   immediately. A 64-byte mailbox projection suffices for initial legality;
   hashing, chronology and phase work occur only when producing actual children.
   Check the geometric projection against that full transition's placement.
3. Keep `NodeState` (produced position/evaluation) separate from fresh invocation
   controls. Parent entry-TT observations survive child writes. Scout retry
   preserves its child evaluation but recomputes invocation decisions.
4. Preserve simultaneous predecessor/current access in any later delta route;
   include prior material, occupancy and pressure observations in its cost.
5. Treat the first integrated partial evaluator as a smoke/cost baseline only.
   Add actual tactical/full-fast selection, pawn reuse/replacement and remembered
   results before choosing a preferred production representation. Use quiet,
   tactical/check-heavy and sparse cases, then exact composed search anchors.
6. Revisit representation/restoration interactions. A small2x2 experiment may be
   necessary if one-factor results are close or change with fidelity. No need
   to maintain four production kernels indefinitely.
7. Count full/fast evaluations, influence builds, candidate examinations versus
   produced children, pawn reuse/replacement and TT queries in a separate
   diagnostic artifact. Semantic N/R alone cannot explain those costs.

Before broad search expansion, check scout/retry/sibling ownership, ordering
child shared effects followed by a fresh main child, and interrupted ordering
work retaining a prior completed-root capture. These become meaningful tests
when their real state owners exist, rather than mocked copies of implementation.
