# Permission-sensitive native search bounds

Source proof, 2026-10-20; retained62 engine source. No engine change, build,
execution or new timing accompanies this analysis. The existing production
placement, fixed-root/cache-origin, evaluator arithmetic and score-capacity
premises apply. Arbitrary public `Store`, supplied retained state and mutated
library objects are outside this prepared native-search theorem.

## Result

For a normally completed native ordinary or Q call at ply `1 <= p <= 63`, with
incoming endpoints `L,U` and result `s`, let `C(p)=10000-p`. Then:

- `s < U` implies `s >= -C(p)`;
- `s > L` implies `s <= C(p)`.

Every valid native TT record simultaneously satisfies:

- UPPER permission implies normalized score `n >= -10000`;
- LOWER permission implies normalized score `n <= 10000`.

Exact records satisfy both. Neither implication constrains the opposite
direction of a one-sided record. This is not an unconditional raw-score bound
or a proof that every mate-band value denotes a genuine mate. No strict-window
premise is needed, including for equal or inverted incoming endpoints. The
earlier unconditional10063 capacity theorem remains useful and is not replaced.

In particular, a first-two-root TT query cannot export the positive
LOWER-permitted normalized score>=10002 identified in the preceding
[caller analysis](uncertified-hint-completion.md). The remaining unrestricted
ply2 lower-window premise closes. At **every native first-half ordinary
completion**, an inherited, unreplaced hint is excluded from normal learning.
The second-half hint/admission question remains open.

## Numerical ingredients

Finished native evaluation scores lie in[-7900,7900]. Consumed endpoints have
the stronger directional enclosure
`-10000 <= effectiveLower <= 7477` and
`-7477 <= effectiveUpper <= 10000`.
The existing [race producer proof](../../evidence/current62-race-producer-correlation-review-20261020-01/review.md)
bounds the updated winning-race endpoint, not both endpoints' magnitudes.
Other bound writers preserve these directional inequalities: insufficient
material writes0; losing races write small signed bounds; White bishop/queen
fortresses lower upper to a nonnegative value, and Black fortresses raise lower
to a nonpositive value. Queen selection uses the sign of the same score supplied
to its fortress formula. Final Black orientation exchanges and negates the
endpoints. First-half ordinary and checked Q use[-10000,10000]. Sparse native
selection forces FULL before race endpoints are consumed; terminal FAST uses
score only. See [endgame owners](../../src/endgame.rs#L280),
[finishing](../../src/endgame.rs#L529) and the earlier consumer crosswalk.

Every ordinary frontier estimate is at least-8400. Quiet ordinary estimates
are finished score+30 plus a nonnegative correction; checking/special estimates
are10000. For captures, do not assume material is monotone. Removing one enemy
piece changes capturing-side raw balance by its nonnegative fixed value plus
an average-depth adjustment in[-50,50]. Each material imbalance correction is
in[-250,250]: losing-heavy factor<=150, winning-pawn factor<=100 and multiplier
<=1. Thus the complete pre-clipping gain is>=-550. The symmetric clamp to7000
is monotone and1-Lipschitz, preserving that lower difference bound. Capture
allowance adds50 and nonnegative terms, hence is>=-500; finished score>=-7900
gives the claimed-8400. These facts use current coherent counts, fixed values
and average depth in[-100,100], including a counts-only hypothetical removal.
See [material](../../src/evaluation.rs#L120),
[allowance](../../src/quiescence_policy.rs#L89) and
[frontier estimates](../../src/ordinary_policy.rs#L236).

## Induction and table ownership

Induct over the finite executed call/return/store sequence, with recursive
results established before their caller consumes them and existing records
established before lookup. Root preparation makes earlier generations invalid;
allocation starts invalid and generation wrap physically clears. Replacement
and displacement copy complete records. Probe can raise depth but cannot
change a record's score or permissions. Numeric identity collisions therefore
preserve the theorem without any board-equality premise.

For a [TT return](../../src/remembered.rs#L118), `s<U` rules out a lower cutoff,
so the returning record must have UPPER permission. If its normalized value is
negative mate-band, decoding adds p and the record invariant gives
`s>=-10000+p`; other bands already satisfy that bound. Symmetrically, `s>L`
rules out an upper cutoff and requires LOWER permission, giving `s<=10000-p`.
The score belongs to the actual returning record, regardless of metadata
accumulated from an earlier record. Mate/depth admission does not weaken either
implication.

[Store permissions](../../src/remembered.rs#L72) are exactly `s>L` for LOWER
and `s<U` for UPPER, using the original query. Thus a stored value satisfying
the two return implications preserves the record theorem: normalization adds
p to a positive mate-band value and subtracts p from a negative one. Other
bands cannot violate the corresponding one-sided bound. The checking-mate
store before main completion is addressed separately below. No other native
store site is omitted; the earlier direct stores in ordinary.rs are test-only.

## Q returns

At ply63, Q returns a finished FAST score within7900. Draw returns0. A checked
no-reply result is exactly `p-10000`; a noncheck empty tactical list returns its
initial standing score. The checked mate-distance shortcut returns `p-9998`
only when that value is>=U, so its negative-side implication is vacuous.

In noncheck static returns, a lower endpoint returns only at>=U, and an upper
endpoint returns only at<=L; the opposite implications follow from the7477
directional bounds. Stand-pat cutoffs are bounded by7900. For noncheck continued
search, best starts at the finished score and never decreases. The final upper
clip cannot lower it below-7900, which proves the negative-side implication.

For checked continued Q, best starts at-10000 and at least one legal reply is
searched. Its first child's lower is `-U`. If final result were below both U
and `-C(p)`, that first child's negated result would also be below U. The child
result would exceed its own lower, and induction would instead give the parent
candidate at least `-C(p+1) > -C(p)`, a contradiction. Checked Q has no candidate
skips before that first child and its final upper is10000.

For the positive-side implication in either Q branch, consider the first best
increase above `max(L,C(p))`. Initial best is below that threshold. At every
iteration, running lower is at most `max(L,best)`. An optimistic capture update
is admitted only at estimate<=`max(best,runningLower)`, so cannot produce the
first such increase. An actual child producing it has result strictly below
its upper `-runningLower`. The child's negative-side bound gives a parent score
at most `C(p+1) < C(p)`, again a contradiction. Final clipping cannot raise best.
See the [complete Q body](../../src/quiescence.rs#L233); this argument needs no
lower bound on optimistic Q estimates.

## Ordinary returns and all four store sites

Delegation to Q uses the established Q result. Draw and no-legal-move returns
are bounded as above. Effective-bound returns obey the same directional
argument as Q. The mate-distance shortcut is again>=U by its gate.

FAST and local shallow stores return only at trial>=U, so have no UPPER
permission and no negative-side obligation. Their trials are respectively
<=7800 and<=7875, since material threat is nonnegative. A successful null
trial is `s=-v>=U`, where the child's window is `[-U,1-U]`. Consequently
`v<=-U<1-U`; the child's negative-side implication gives
`s<=C(p+1)<C(p)`. Null descendants' intervening stores are already covered by
the induction.

The quiet checking-mate probe calls Q with upper=-8999. A selected score>=9000
means its child result<=-9000, strictly below that upper. Its score is therefore
<=C(p+1). Storage additionally requires score>=U, so no UPPER permission is
created. The store occurs before continued search; it does not rely on the
later ordinary return or roll back on a later stop.

Main search starts best at effectiveLower<=7477. As in Q, running lower remains
at most `max(L,best)`. A guarded frontier estimate cannot be the first best
increase above `max(L,C(p))`. An actual improving child returns below its upper:
full uses `-max(best,L)`, scout and retry use `-best`. The child's negative-side
implication excludes such an increase. This proves the positive-side bound
before the final upper clip.

For the negative side, at least one main move is processed. If the first is
skipped by its frontier estimate, its score>=-8400 already raises best above
`-C(p)`. Otherwise the first main child always uses the full window with
lower=-U. A hypothetical final result below both U and `-C(p)` cannot be caused
by the effective-upper clip, which is>=-7477. The first child's parent score
would therefore be below U; its child result exceeds its lower, yielding
parent score>=`-C(p+1)>-C(p)`. This contradicts the proposed final result.
No scout/retry premise is needed for this negative-side argument.

Thus the final clipped score satisfies both implications before normal storage.
Initial/tail IIO add ordinary descendant calls and reorder candidates; they do
not create a separate parent return or remove the first main move. Stops return
no score and perform no later completion store; earlier valid records remain.
See [ordinary entry and stores](../../src/ordinary.rs#L719),
[main children](../../src/ordinary.rs#L1013) and
[IIO](../../src/ordinary.rs#L1100).

## Root consequence and limits

Fixed/seeded and unrestricted timed iterations give their first two completed
root candidates the full child window[-10000,10000]; random subtraction leaves
its sentinel endpoints unchanged. The theorem gives those ply1 results<=9999
(values<=L trivially meet that ceiling). Negation and root score addition keep
their ranking scores>=-10000. Stable descending insertion then keeps the second
score>=-10000 for the rest of the iteration, whatever later returns do. When
there are fewer than two candidates, the default second remains-10000.

This supplies the last premise of the earlier caller proof: every native
ordinary entry has lower>=-10000. First-half effective lower=-10000 then forces
any normal completion learning above incoming lower to have replaced the
inherited hint with a generated candidate. Quiet-mate replacements are generated
as well. Restricted timed scheduling was already covered independently.

This closes only that inherited, unreplaced first-half completion route.
Second-half effectiveLower can exceed incoming L, so its conditional sparse
zero-score example remains relevant. The result supplies neither a public
violating prefix nor new behavioral authority for empty-source hints; it does
not complete general TT/IIO/stop/hint qualification or the external game gate.

## Independent challenge

The single Astra reviewer separately derived the two numerical lemmas and
[challenged the induction](/home/legolas/agent-memos/rook2-inward-endpoints-frontier-to-lead-20261020.md).
The review accepts the Q optimistic-update argument, first main child argument,
precompletion quiet-mate store and exact root consequence under the stated
native ownership/arithmetic premises. It does not re-audit those imported
premises. The lead checked the complete memo against the actual source and
retained the second-half and general qualification limits above.

## Reviewed source identity

Source hashes read at repository HEAD5b625c5a, before this documentation-only
change; all ten independently match the frozen retained62 promotion map bound
in the [local handoff](../../experiments/retained62-game-handoff/README.md).
The retained62 artifact and native source are unchanged.

| Source | SHA256 |
| --- | --- |
| ordinary.rs | e5dae89f6bcc6651ac4e8aeb943b3f559b882232f2cf571c79fd0f3d463ecbfb |
| ordinary_policy.rs | 5a796d4f7b11c1818a7dbdfe34080d9502d7c517217b521315534a318e9301a6 |
| quiescence.rs | 9ff56aefef807d7df53f446abef404dba90150572116c0cae09057556bb39e6a |
| quiescence_policy.rs | baeb3f40c47f119481f0040b1c9bb15f9af25ee39376cf0c01d1a06091011468 |
| remembered.rs | af2eb6046fd7e58b1a35e7ed3051936559b7f739224ed698b54c49317faec293 |
| evaluation.rs | 767b1ef83fea5d30d1b5a6edaa259fa718c666cfdb568fb9ad7b2aca2e9f33f7 |
| endgame.rs | 4f382e7b5359f1956a0e155328aad08f35dab74252ee0794d61dafcd1cd2214a |
| evaluator.rs | 0ea2af3606dfb20409b8c15d46a0c745bf3204c22bccee6e00d3493615a55c61 |
| root_schedule.rs | 550146f895ef9a43b8ecdc6fce5e26fb973602e6f5d5b17add1a4920768a72d8 |
| timed.rs | f62d6ea5591fc23515da241ee3dfefd30d500c79e0349068ca595076f8044d2e |
