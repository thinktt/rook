# Call-local geometry permission: minimal runtime-flag boundary

**Feasible with one private Search bool and no new recursion const or Node/Position fields.** It requires explicit public-ingress invalidation and two preparation distinctions; an existing root guard does not automatically seal later externally supplied Nodes. No implementation is selected. The updated Influence-only option is materially smaller than routing activity geometry: full/fast/activity need not change at all.

## Lifetime and reset inventory

| Owner/current anchors | Minimal edit or obligation |
|---|---|
| engine.rs34–70 | Initialize a private Search geometry flag false. Keep mutation/read access within source-audited crate-private helpers if cross-module impl access requires it. No public setter. |
| engine.rs76–113 map_host | Explicitly initialize the mapped Search flag false, rather than carrying permission across this public ownership transfer. Current Session calls it only outside active recursion. |
| timed.rs468–516 | Both existing ALLOW_IIO policies share the same runtime flag. The existing entry wrapper clears on entry; after unchanged input/history/table checks, bind exactly `position.validate().is_ok()` before initial root full. After the inner worker returns Ok/Err, clear the flag and retain the existing timing=None cleanup/order. |
| ordinary.rs520–559 | Both fixed/seeded root APIs use one outer cleanup wrapper around the current worker. Clear before entry assertions (including seeded randomness assertion544); bind after existing depth/history/table checks and before root full; clear after every Result. Do not add a geometry const to recursive ordinary/Q types. |
| quiescence.rs133–154 | Public prepare_root clears first. Existing pub(crate) prepare_root_with_influence is already the preserving internal root body; timed/fixed workers call it after binding. Its two production root callers and direct test callers must remain source-audited; it is not a public certificate for a returned Node. |
| quiescence.rs188–194 | Public begin_sequence clears the flag. Extract its current timing/stats/PV/limits reset into one crate-private preserving body, called instead by timed533/fixed567. Preserve every original reset and root-work exclusion. |
| quiescence.rs159–183,196–207 | Public search_subtree begins via public reset; continue_subtree independently clears at its first statement, before assertions. Observed subtree clears before its assertions, not merely at its later begin_sequence call. A caller must not inherit permission by skipping begin_sequence. |
| first_iteration.rs44–76 | The standalone first-iteration owner uses public prepare_root/begin_sequence/continue_subtree and therefore remains false. It is safe but outside this minimal guarded native timed/fixed scope; enabling it would require a separately audited owned-root route, not deleting public invalidation. |

Normal/Err cleanup is straightforward because the timed worker already returns through one outer wrapper; the fixed worker needs the analogous wrapper so its internal `?` cannot bypass reset. A panic bypasses statements after an inner call. Without an unwind guard, do not claim the flag is false after catch_unwind: **every later evaluating public ingress must clear/rebind**, and direct public Evaluator methods must bypass it. An optional safe root-only Drop guard can borrow the whole Search and invoke the worker through that borrow, clearing on unwind; a guard borrowing only the bool while also borrowing all Search mutably conflicts, and a raw-pointer Drop guard is unnecessary. That extra root wrapper has an unmeasured frame/code cost; no panic-handling or timing semantics should be rewritten merely for this flag.

Read-only work()/config/parameter access does not evaluate a Node and need not clear. Public Node constructors contain no flag. Public Evaluator begin_search cannot clear an owning Search, but it cannot grant geometry permission either. After public evaluator mutation, any later Search evaluation still crosses a clearing/binding entry. Safe Host/raw-score/trace callbacks have no mutable active Position/Search alias; the closed prior review's child/null/IIO/scout/retry/restore induction still applies. No permission is derived from H::ACTIVE, DIAGNOSTICS, a legal-looking move or a previously prepared Node.

## Reduced Influence-only routing after parent's scope update

Add one crate-private ensure-influence route with a passed runtime bool, sharing the existing None/provision/stat owner (evaluator.rs296–307). Public ensure_influence hardwires false. On **Some**, retain the exact supplied map and perform no replacement/rebuild regardless of permission. On **None**, true may select the future coherent-plane producer; false retains current Influence::build. Increment influence_builds exactly once under the current DIAGNOSTICS gate. Influence construction itself adds no semanticR. The bool must not select cached answers, normalize profiles or affect downstream numerical ownership.

Complete actual production construction edges are:

- Root: quiescence.rs148, before the initial full. Public prepare_root clears first; native timed/fixed preparation preserves the newly bound flag.
- Ordinary:782 fast-cutoff support and795 normal full share one local None scratch. Read the flag into a scalar local before mutably borrowing evaluator; retain existing demand timing and shared scratch.
- Q support: quiescence.rs356, inside the existing lazy destination-support closure; do not move construction before that closure is actually invoked.
- Q selection: quiescence.rs266 calls a crate-private default select route passing the bool. Add it only as a runtime argument to the existing shared select_noncheck_impl policy. Its sparse627 and refresh650 ensure sites use the private builder route; no arithmetic/choice/order clone.

Public select_noncheck/detailed/stages wrappers pass false, including prefilled custom Some scratch. Public observed-subtree ingress clears, so its current O::ENABLED stage selector remains false; there is no current true observed chain requiring a new private observer API. Keep that reachability statement explicit if a future caller changes it.

For this Influence-only option, root/ordinary full calls and every selector full/fast call can remain the **existing public numerical wrappers**: they consume the constructed map and run unchanged scalar activity. No geometry bool is needed in full_impl, no new default full monomorph is needed by the design, and public full/fresh/observed behavior stays independent of the Search flag. Fast has no map producer to route. The policy bool is read only when a private ensure/selection route demands it. Future compiler effects still need actual inspection; this is not ABI/erasure neutrality.

If activity geometry is later selected instead, additional private full and default-selector-to-full routing would be necessary at evaluator.rs373 and sparse634/refresh656. Keep public wrappers literal false and share the numerical body; avoid a new observer closure type solely for the private default route. That larger option is **not required by the pending Influence-only producer**, and is not selected here.

## Counterexamples and remaining obligations

1. True timed call → public prepare_root(other Position) → mutate returned Node → continue_subtree: both public boundaries clear, so unrelated/stale planes never inherit certification.
2. True worker stops/returns error or is caught unwinding → direct public Evaluator full/select with custom Node/map: hard false; next root entry clears then independently validates. Invalid seeded arguments must not leave a previous flag untouched before assertion.
3. Public begin_sequence called during a new external subtree must clear, but calling it from native timed/fixed setup would accidentally disable the initial permission. The shared preserving reset body resolves precisely this conflict.
4. A malformed or stale root takes false without a new rejection/canonicalization. Existing validate safely checks bounded canonical lists/mailbox before board-derived kind/hash reads; a mere four-plane equality test without tag validation is insufficient.
5. Native ownership certifies geometry only. Chronological sources, current phase/rook king row, supplied map bytes, live PawnCache, retained effects, R and finish remain original owners. A new slider/SIMD Influence producer still needs independent full128-byte wrapping/transparency/pawn-extra proof; the flag does not prove that kernel.

Flag storage may consume padding or grow Search/root layout; that is unknown. Root validation is real setup, and runtime flag loads/branches, constructor choice, selector argument traffic and any new call outlining are real costs. No eager per-node validation or Influence/category persistent state belongs in this boundary. No source, execution or performance decision follows from this memo.

Only this new evidence directory was written. All source/text/hash helpers use0-5,8-13 and HOME TMPDIR. No engine, compiler, test, binutils, profiler, Git, archive, Herdr or advisor action occurred. Final receipt records actual closure.
