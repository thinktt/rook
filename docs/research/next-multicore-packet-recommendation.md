# Next packet: test FULL ownership placement before speculative inventory

2026-10-24. Bounded source/evidence recommendation, **no new implementation or
native execution**. Preserve the [positive own-PGO option](multicore-production-assessment.md)
and both negative queue checkpoints unchanged.

**Recommend one narrow reversed-FULL ownership discriminator if another experiment
is selected.** It offers certain actual FULL demand and a plausible latency/locality
improvement without speculative search or more workers. It exposes no additional
arithmetic parallelism and has no demonstrated gain yet. Same-node inventory is a
credible reserve, but current evidence does not price its eligible overlap.

## Same-node inventory: pure producer, uncertain useful window

`ordinary.rs::visit_ordinary_impl` hands Q off first, charges/polls, handles draws,
probes TT, then can fast-cut off before FULL. Its real legal inventory is generated
**after** FULL evaluation-bound cutoffs and a possible shallow/threat or recursive
null trial. Native `movegen::generate_legal` reads the exact Position and produces
an ordered inventory without learning, TT or evaluator mutation. That producer can
run independently; move priority/sort, generated-count charge, mate/IIO probes,
extensions and candidate consumption must stay at their original owner boundaries.

The useful speculative window would publish after early/TT admission, preferably
after the fast gate, before `ensure_influence_for_search` and FULL. Publishing after
bounds/null survival has much more certain demand, but little remaining evaluation
to overlap. Early FULL-bound and shallow/null cutoffs discard earlier generation.
A real null recursion can change authoritative state while the parent inventory
remains pure, but it cannot silently acquire the same occupied helper. A one-helper
variant must explicitly reserve it for the parent and run nested FULL inline, or
finish/discard/join before recursion; the latter prices its wait at the early path.
It must also choose an alternative to the existing FULL helper, not assume both
packets execute simultaneously on one worker.

Q is a different producer/domain (`quiescence.rs::visit_q_impl`): checked Q skips
evaluation, and `replies_available` reuses a previously complete inventory, so
neither provides this overlap. Nonchecked Q evaluates/refreshes first and may return
before `tactical::generate_for_search`, which produces a **tactical inventory**,
not the ordinary full legal list. Do not substitute one kind or sum all generation
cost as available overlap. Terminal-ply/early-draw paths also offer none. Supplied
maps, coherent-geometry permission, native inventory order and admitted Position
domain must remain exact; moved generation cannot broaden malformed/king-victim
execution ahead of its original admission.

No existing native measurement separates eligible ordinary inventory cost,
pre-demand FULL time, discarded inventories or nested helper conflicts. The old
whole-request functional comparison does not localize those components; historical
simulated instruction shares are not a native overlap budget. The failed child
queue's13–21% useful-task rate is evidence against assuming demand, not a measured
rate for this distinct same-node policy. This alternative therefore needs an
admitted-demand/cost discriminator before a broad speculative queue.

## Reversed FULL: exclusive ordered cache, not copying or fresh rebuilding

`Evaluator::fast_impl` only reads Node retained terms and finishes locally; it never
selects PawnCache. Normal FULL selects that private cache, while FRESH bypasses it
without replacing retained entries. Give one helper exclusive ownership of
`select → pawn_terms → structure_weighted/progress`; return weighted structure,
progress, pawn relation count and reuse flag. Keep Activity→Shelter, remaining
components, tempo, retained writes, finishing and **one combined R publication**
on the coordinator. This preserves the actual FULL ordering; no FAST roundtrip.

Packets need the exact supplied Influence and Position, current material, phase,
and already root-side-bound structure/progress coefficients, plus FRESH mode.
Identity hits intentionally retain old descriptors, including collisions; current
board consumers filter them. Recomputing fresh or copying an8KiB cache per FULL is
not equivalent ownership. `begin_search` needs an acknowledged ordered cache
clear before root FULL under new weights. Continued sequences retain cache state;
parking must not reset it. Mode2→1 must transfer the actual cache back once, and
1→2 must transfer the current cache rather than quietly restart it. Completed
cache mutations survive parking even if a result is discarded. Standalone/FRESH
observations and supplied contrary maps retain their existing semantics.

## Why exchanging sides might help

Let A=Activity–Shelter, B=pawn branch, C=other coordinator work, P=coordinator packet
preparation/publication, L=worker pickup/cache-transfer latency, J=join/finish.
A simplified current critical path is `P + max(B+C, L+A) + J`; reversal is
`P + max(A+C, L+B) + J`. **P stays serial in both.** Moving the heavier chain local
can hide remote latency behind it; equal total arithmetic does not imply equal
critical path. Conversely B cache misses, C placement, changed return payload and
cache locality can erase the advantage. Neither L nor P is proven constant across
placements or CPUs; this is a mechanism model, not a timing prediction.

The old standalone probe measured A direct350.98ns, A remote509.85ns, FULL
serial597.75ns and current overlap503.51ns. That makes an A-heavy remote critical
path plausible, but it used pre-shared inputs, a fixed neutral context and a
synthetic cache stream. Do not subtract those rows to claim measured B or L, or
predict production seconds. The completed production survey establishes current
net6.29% elapsed gain and1.873x CPU, not a chain decomposition. Its seven losses
include a substantial profile43 search, so a startup-only explanation is unsupported.

## Smallest useful selected-next discriminator

If authorized, implement **one same-image alternative FULL placement**, reusing the
parked lifecycle and inline control, with no new queue policy/worker/profile sweep.
First check detailed components, retained/R values, exact cache hit/collision/FRESH
state, ordered reset, mode transfer and supplied-map authority. Then one small
matched original35/08/04 comparison of inline/current split/reversal must include
fresh packet publication, actual cache chronology, startup/idle/joined shutdown,
whole CPU and serial cost. A generic mechanism trial can precede another own-PGO
campaign; comparing a new generic reversal only against the preserved PGO artifact
would confound the result. Preserve the positive artifact throughout.

No prototype, instrumentation, build, timing or additional policy was executed in
this source study. Reversal remains a hypothesis until that integrated discriminator;
its ownership work is justified by the clearer demand and critical-path question,
not an assumed larger pool of independent work.
