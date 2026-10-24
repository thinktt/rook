# Multicore production survey: lead assessment

2026-10-24. Research assessment, not adoption or qualification.

The Activity–Shelter FULL split is now a demonstrated production-build option.
The completed own-PGO survey used the accepted serial artifact and one candidate
binary in inline/worker modes. Search elapsed totals across original54 were:

| Configuration | Search elapsed | Whole-process CPU |
| --- | ---: | ---: |
| Accepted serial | 68.237305 s | 68.307437 s |
| Candidate, one thread | 69.171315 s | 69.241398 s |
| Candidate, two threads | 63.946851 s | 127.931937 s |

Two threads lowered elapsed time 6.29% relative to accepted serial, with 1.873
times its CPU. Candidate one-thread elapsed was 1.37% higher. The worker was
faster on 47/54 cases; the worst observed ratio versus control was 1.05811 on
profile22. These are single observations per case/configuration, not estimates
with per-case uncertainty. The earlier three-case repeated comparison supports
the existence of a gain, but does not establish significance for every full54 row.
No current KingWCR comparison follows from similar historical absolute totals.

The seven observed regressions total0.240366 seconds. They are not exclusively
short searches: profile43 rises from2.886502 to3.005729 seconds, the largest
absolute loss. Conversely, the largest individual saving is0.351812 seconds on
profile35. A startup-only explanation or a short-search threshold is therefore
not established. These observations may guide a later mechanism investigation;
they do not justify a workload-ID selector or tuning to individual cases.

The independent recorded/raw audit reports all162 survey lifetimes and1872 posts
passing. Training used original54 once in each mode and one merged profile;
training108 and small-study36 replay lives also passed their audits. This is
focused behavioral evidence, not full adoption qualification. Source checkpoint
5612b55f and the experiment's exact artifact/profile records identify the variant.
Raw evidence is under
`/home/legolas/rook2-experiments/full-split-production-20261024-01/`.

Between-search parking resolves the observed continuous idle spin: the short
250ms probe registered0 ticks for the new worker versus0.25 CPU seconds for the
old one. Resolution is10ms; zero ticks does not mean literally zero cost. Active
search still spins, including during blocking host callbacks. Fixed CPU6 and a
10-second wall-time failure abort remain research constraints. Test unwind
cleanup does not imply recovery in production panic-abort builds.

## What this changes

Preserve this variant as the positive research baseline. It provides real
acceleration without changing search order or delegating authoritative state.
It does not yet realize scalable use of arbitrary thread counts: there is only
one independent helper chain, and its CPU cost is substantial. The one-thread
cost must remain visible rather than comparing parallel mode only against a
slower refactored inline mode.

The branch-transaction pilot and pure-child queue are separate negative results.
The former found no ahead-of-head whole-branch reuse in its sample; the latter
found genuine pure reuse but substantially worse elapsed costs at both tested
worker counts. Neither justifies a general impossibility claim about branch
parallelism. Neither justifies another queue-size sweep without a different
useful-work or ownership argument.

The next source investigation compares larger same-node overlap with reversing
FULL chain ownership. Available overlap, cutoff waste, recursion ownership and
transport must be priced together. In ordinary search, delaying inventory work
until after evaluation/null cutoffs reduces waste but also removes much of the
overlap. Checked Q skips evaluation, and reused reply lists are not new work.
Moving the pawn branch requires exclusive ordered cache ownership, not copied
cache state or fresh recomputation. No new implementation is selected by this
assessment; the existing positive result is retained while that recommendation
is developed.
