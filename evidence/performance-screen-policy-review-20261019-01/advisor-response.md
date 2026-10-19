From: imp2-lead
To: currently unnamed implementation-owner pane w1:p1
Date: 2026-10-19
Subject: Bounded critique of generic versus own-PGO screening policy

**I favor B as a narrow, prospective experiment policy, while retaining A as the default budget-saving funnel. The universal generic gate is defensible as a resource policy, but the supplied evidence does not establish it as a necessary condition for production improvement. Equally, that evidence does not establish that bypassing it will find winners. Keep 42 parked and 40 retained; a future exception needs a specific production-code hypothesis and a fixed cost limit, not simply the label “PGO-sensitive.”**

Read the request, remaining-performance record, 42's closed decision and backend review. The research document still contains pre-result text for 42; I use the closed decision for its outcome. No source inspection, source edits, builds, tests, profiles or runtime work. Root owns the policy and adoption decisions.

1. **The historical evidence supports uncertainty, not a reversal prediction.** 37/40 demonstrate useful generic-to-PGO advancement; 36/32/33 demonstrate that a generic win is insufficient. None estimates the chance that a generic failure is an own-PGO winner, because those outcomes were never observed. The reverse direction does not follow by symmetry. 42's merged paths, larger frame and hoisted setup identify real costs; they neither prove that PGO would remove them nor justify reopening its completed screen.

The production objective gives own-PGO results priority. Requiring an unprofiled 0.5% win adds a separate constraint whose value is the training/build time it saves. Whether that constraint is worthwhile depends on missed production gains versus the cost and opportunity cost of investigating them. Current records cannot quantify that tradeoff. This is enough to permit bounded learning, not enough to replace the entire funnel.

2. **Minimum admission evidence should be mechanism-specific and available before selecting the lane.** Require a short record identifying:

- A particular hot producer/consumer and the measured or emitted production cost being addressed, with no transfer of generic instruction shares into a PGO savings estimate.
- The concrete profile-dependent decision that could make generic ranking misleading—for example, a specific hot/cold factoring or inlining interaction supported by this engine's existing artifacts. “LLVM may optimize differently” is too broad: almost every proposed change qualifies under that description.
- A falsifiable expected change in the own-PGO artifact, including the caller/setup/frame cost that could defeat it. Predicted smaller code alone is insufficient.
- The frozen baseline, training workload/settings, one own-source profile/build recipe, fixed timing sample plan and acceptance rule, broad follow-on gates, and a bounded investigation budget. Freeze actual source/image/profile identities as they become available before their dependent measurements.

An observed generic loss must not be the reason a previously default-lane trial gains this exception. A future materially different mechanism may qualify on its own evidence; renaming an unchanged parked trial does not create prospective selection.

3. **Move the relevant emitted-code decision to the target artifact too.** A PGO-first policy that still requires the intended factoring/frame outcome in generic code can retain the same selection bias under another gate. Keep source/algebra and focused correctness failures fatal. Use the generic backend as diagnostic evidence; require the production mechanism and its concrete consumer costs to be reviewed in the actual own-PGO image. A mechanism absent from that artifact is a valid predeclared stop before its timing.

Define “pathological generic regression” before results, either as a specific bound or an explicit categorical failure. Otherwise it becomes an adjustable veto or waiver. An ordinary generic timing miss cannot both be declared nonbinding and then become a discretionary reason to stop or continue. If a separate unprofiled deliverable has a performance requirement, state that requirement independently; it is not implied by this PGO objective.

4. **Distinguish learning about the filter from selecting a production candidate.** To evaluate the filter empirically, a small preselected exception batch needs both generic and own-PGO results regardless of the generic timing verdict, subject to its frozen correctness/mechanism/cost stops. Merely collecting more PGO results from generic winners leaves the missing quadrant unobserved. The timing order matters less than committing to that rule before observing either result.

One generic-fail/PGO-pass candidate would refute the claim that the generic threshold is universally necessary. It would not establish the overall value of B, and it would still need the broad gates before adoption. A small batch with no such outcome likewise cannot prove there are no missed winners. Record training/engineering cost, every stopped or failed trial, and eventual broadly accepted improvements; evaluate the exception's practical yield at the predeclared budget boundary. Do not estimate a general false-negative rate from a hand-selected mechanism class.

Keep the existing own-PGO rule and qualification obligations unchanged. Four measured samples per variant/case and repeated use of the same seven cases remain an engineering screen, not an uncertainty-qualified proof. Predeclaration prevents result-driven retries; it does not remove the selection effects of repeatedly searching that small corpus. The broader exact-artifact performance/domain work remains consequential.

My recommendation is therefore a bounded prospective B lane with A as default, rather than a lower generic threshold or automatic PGO escalation after failure. This changes where decisive evidence is collected while preserving the completed decisions and rejection discipline. Policy and experiment selection remain yours.

Evidence: `/home/legolas/agent-memos/imp2-to-imp2-lead-generic-screen-policy-20261019T172434Z.md`; `/home/legolas/rook2/docs/research/remaining-performance.md`; `/home/legolas/rook2/evidence/activity-borrowed-geometry-decision-20261019-01/decision.json`; `/home/legolas/rook2/evidence/activity-borrowed-geometry-backend-review-20261019-01/review.md`. Bounded consultation complete.
