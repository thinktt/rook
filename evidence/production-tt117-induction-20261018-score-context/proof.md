# Production117 TT score-capacity induction

Bounded source/algebra continuation by score_context_transport, 2026-10-18. Exact source `/home/legolas/rook2-work/imp2-complete117-proposal-20261018-07et7r_s`, existing frozen graph `4310f9ab7a321a8cc40308a92afe78c287450a7a46fa4bffea303c05c86f5422`. No source edit, engine/build/test/codegen/timing/profile/hash/archive/Git, Rust parsing, Imp1 or Herdr. Helpers only0-5,8-13. This is a new proof memo; earlier reviews remain unchanged.

## Result

There is a closed conservative induction for **native normalized TT score capacity**, without assuming that every returned score is within +/-10000 or that every mate-band value is a genuine mate:

Set **B=10063**. At every successful actual ordinary return at ply p, **|v|<=B-p**. Every live search-origin TT record has normalized magnitude<=B. Every actual ordinary request satisfies the auxiliary **beta>=p-B**. Quiescence independently returns **|v|<=10000** at p<=63, which implies the same return envelope. Thus every ordinary score normalization is within[-10063,10063], safely inside i16. Root adjusted/ranked values have magnitude<=B-1=10062. Different-ply reuse and identity collisions preserve this enclosure.

This discharges the previously open **i16 score representation** and the corresponding bounded root/window scalar capacity for the mapped production callers. It does not prove the stronger canonical returned-score bound +/-10000, semantic mate provenance, every TT depth/identity/lifecycle rule, raw u64 work capacity, or full conformance. No production-reachable counterexample was found or is needed for this representation result.

## Preconditions already discharged by the adjacent audit

`production-retained117-numerical-crosswalk-20261018-score-context/review.md` maps current board/list/king, effective coefficients, fixed root, cache origins and P/G induction. Its current produced score bound is7900. Its tighter selected-FULL race bound is7477; queen/bishop/lack-wood rules and current full/fast consumer separation keep **consumed evaluation endpoints inside[-10000,10000]**. Pawn-only FAST at Qply63 discards endpoints. These facts, not the standalone final-score diagnostic's supplied-A cap, are used here.

Actual ordinary nodes enter at ply1 and hand off to Q at ply63 or earlier (`ordinary_policy.rs32-34`; `ordinary.rs695-723`). Q exits before generating descendants at63 (`quiescence.rs243-253`). All nested children have q=p+1<=63, regardless of IIO depth/extension chronology. A new actual root clears remembered entries (`quiescence.rs141-145`); only actual `store_ordinary` writes search-origin records. Supplied standalone remembered-results records and controlled timed reply providers are outside this production induction.

## Simultaneous invariant and table decoding

For each actual ordinary frame at p maintain:

- Entry **beta>=p-B**. No premise that alpha/beta lie in +/-10000 is required for the capacity proof.
- Every completed ordinary child at q=p+1 returns in[-(B-q),B-q].
- Once FULL bounds permit exploration, the mutable main `best` and `lower`, and each IIO pass's local `best`, are at most **U=B-q**. Since q<=63, U>=10000.
- Every previously stored live TT normalized score n satisfies |n|<=B.

`remembered.rs72-88` stores n=v+p for v>=9000, n=v-p for v<=-9000, otherwise n=v. `consider~119-123` decodes the matching signed band by subtracting/adding the new ply; a nonmate record remains below9000. Therefore an existing bounded record returns |v|<=B-p (B-p>=10000 covers nonmate records too). Identity/hash collisions choose an already bounded record and cannot enlarge its scalar envelope. Changing depth or move metadata does not change n. Generation clearing admits no arbitrary score origin; initially unused zero records cannot create an unbounded value (`remembered.rs172-179,192-242`).

This is induction over actual ordered execution/store events and nested calls, not reasoning that a checked conversion happened to succeed: each store's prospective n is bounded *before* `i16::try_from`.

## Q has a window-independent +/-10000 return enclosure

The Q algorithm (`quiescence.rs220-477`) has no TT score source. Draw returns0; ply63 returns only the clipped FAST score; admitted evaluator-bound returns are in[-10000,10000]. A checked no-reply return is p-10000 and the checking mate threshold p-9998 is also inside this interval. Otherwise checked best starts-10000, nonchecked best starts its clipped standing score, child negations are in[-10000,10000] by induction, and updates use maxima. Optimistic capture estimates may be larger, but the final result is `best.min(evaluation_upper)`, whose upper lies in[-10000,10000] (literal10000 for checked nodes). This preserves the lower bound too: both best and evaluation_upper are>=-10000. Q recursion advances ply and terminates at63, so the induction has a direct base case.

The capture callback may update best before later legality rejection; that does not defeat this scalar proof. `capture_policy` accepts an estimate only when estimate<=max(best,alpha), and Q still applies its final evaluation upper. No unbounded synthetic value bypasses that final return cap.

## All ordinary return/store sites

References below are current `src/ordinary.rs` unless qualified.

1. **Handoff / draw / table / endpoint / no-reply / mate-threshold:** handoff695-722 returns bounded Q. Draw returns0. Existing table749-756 returns the decoder enclosure above. Bound cutoff803-806 returns an endpoint within10000. No replies and the mate threshold850-858 return bounded literal/mate values. All obey |v|<=B-p; no new TT score is stored at these exits.

2. **Pre-FULL fast cutoff771-790:** fast.score is in[-7900,7900]. `fast_cutoff_gate` subtracts100 or150, so adjusted<=7800. Threat is nonnegative; a returned/stored trial s therefore satisfies **s<=7800**. The actual store guard requires **s>=beta**, and entry gives beta>=p-B. Hence s is in[p-B,7800], so |s|<=B-p. If negative mate-band, `-s+p<=B`; if ordinary-band, |n|<=8999. This is the only local threat-based store that needs the entry beta invariant before FULL's endpoint guard. Large negative loose trial bounds from the preceding audit cannot pass this guard outside the envelope.

3. **FULL guard strengthens control before descendants796-810:** `evaluation_bounds` either supplies current bounded endpoints or literal[-10000,10000]. `cutoff` tests lower>=beta then upper<=alpha (`ordinary_policy.rs62-80`). If neither returns, **beta>effective_lower>=-10000** and **alpha<effective_upper<=10000**. This conclusion does not depend on assuming a strict input window. Main/IIO child production occurs only after this guard.

4. **Static shallow cutoff810-842:** its trial is clipped evaluation minus nonnegative threat minus25/40, so s<=7875. It stores only if s>=beta. The strengthened beta>-10000 gives |s|<=10000, hence |n|<=10062 at p<=62. Threat's loose36750 maximum no longer threatens i16 after the actual guard.

5. **Null trial821-842:** eligible only when evaluation.score>=beta, hence beta<=7900, in addition to beta>-10000. Its child q gets beta_child=1-beta>=-7899>=q-B; the induction is callable. Negating the child's returned score gives |s|<=B-q=B-p-1. If re-stored in a mate band, normalized magnitude is<=B-1; ordinary-band values are smaller. This covers a returned TT score, an actual mate, or any other child origin without assuming semantic mate provenance.

6. **Checking Q probe886-924:** child upper=-8999 is admitted, Q return magnitude<=10000. Any proved score stored by the parent has |s|<=10000 and normalized magnitude<=10062. Its result cannot introduce a larger normalization origin.

7. **Final main store1075-1080:** best initializes to effective_lower>=-10000; every update is max-like; final `best.min(effective_upper)` yields a result in[-10000,10000]. Thus its normalization is<=10062. This remains true with a synthetic frontier score or a child TT result above10000 before that cap.

Every successful ordinary return is one of these sites. Errors/interruption yield no fabricated return; earlier valid stores remain within the invariant. The D-only counters and true/false IIO capability do not add another score return/store owner.

## All recursive request windows preserve beta

After the FULL guard, initial main best<=10000 and initial lower=alpha<10000. Both are<=U=B-q. For each main move (`ordinary.rs940-1072`):

- A real child score s=-v_child is<=U by the child's return invariant.
- A frontier estimate used instead of recursion must satisfy **estimate<=max(best,lower)** before it is accepted (`ordinary.rs984-989`), so it too is<=U. Its uncapped arithmetic may exceed10000; it cannot enlarge the maintained upper enclosure when used.
- Updating best/lower by such scores preserves their U enclosure. The full-window child upper is `-max(best,request.lower)`, scout upper is `-best`, and retry upper is also `-best` (`1001-1046`). All are>=-U=q-B. A reused child with refreshed P/G does not change this scalar reasoning.
- Child lower may be a negated parent beta or `-(best+1).min(parent beta)`; these do not create a new stored-score source. All their scalar magnitudes are bounded by B+1, well inside i32.

Each IIO pass (`1083-1182`) starts local best=-10000. Every update is -v from a child at the *same q*, hence <=U. Its request upper is `-max(local_best,request.lower)`, therefore>=q-B. Initial/tail phases, multiple shallow passes and accumulated extension flags do not alter q or the window formula. Even when IIO uses a large TT-derived best, the next sibling is anchored to precisely that same child-ply envelope; adding the parent's ply again would be the erroneous widening argument. A false capability returns an error before its children and has no score/store origin.

The remaining recursive path is the null child already covered above. Quiet-mate probes are Q and bounded independently. This enumerates actual recursive sources, rather than assuming all requests remain in +/-10000.

## Root, randomization, aspiration and retry

An actual completed child at p=1 returns |v|<=B-1. Root negation therefore produces raw score in[-10062,10062]. `timed.rs193-199::score_add` preserves any value outside[-8999,8999] *unchanged* and performs ordinary-band addition in i64 followed by clamp to8999. Consequently the root random adjustment cannot enlarge the mate-band envelope or promote a bounded ordinary score beyond8999. Root ranking's optional-2 uses this same helper, so row scores remain bounded. This is a normalization-band argument, not a claim all such values denote actual mate.

`root_schedule.rs123-140` unrestricted lower is the second ranked row (or-10000); restricted lower is `score_add(best,2)`. Both are<=B-1: adding2 is identity in the large band, while ordinary addition clamps8999. In `ActualEffects` (`timed.rs610-630`) child beta is **-score_add(root_lower,-adjustment)**, so beta>=-(B-1)=1-B. Retry152-157 changes the root upper to10000 and retains this lower/child, preserving the same beta premise. Root previous/best/second all retain their row bound; aspiration's `max(best,previous)+1`, cap10000 and subsequent score_add (`timed.rs202-207`) are safe i32 arithmetic. Root upper affects child alpha, not the pre-FULL fast store's lower enclosure.

Natural fixed ordinary iterations (`ordinary.rs574-609`) use the same root-child beta from second-ranked return, with the same optional seeded score_add. First iteration's Q-only children (`first_iteration.rs51-87`) return within10000 and provide no larger TT origin. The actual timed driver invokes the mapped recursive owner; controlled supplied reply runners and arbitrary remembered-results component stores are not production substitutions.

Thus the first root request establishes beta, each recursive request preserves it, every prospective store preserves |n|<=B, and every successful return preserves |v|<=B-p. The induction starts from the cleared table and bounded root FULL preparation and is closed across arbitrary finite iterations, retries, IIO true paths and hash collisions. It does not require a finite fixture enumeration, a true-mate-only band premise, or an imposed production search budget.

## Limits and disposition

This is sufficient for i16 **score** normalization capacity and for the named root/window +/-1/negation/addition intermediates. Existing current P/G/threat/frontier arithmetic enclosures supply the computations before guards; random root score_add uses i64, and random-adjustment's signed delta is within i32 for admitted rnd. It does not independently qualify remaining-depth i16 conversion, every extension/priority/time expression, host/error semantics, raw u64 counters, or complete protocol/search fidelity. In particular the stronger semantic claim “no actual returned score exceeds10000” has not been proved here and must not be inferred from this deliberately wider closed envelope.

The general supplied example store10000@ply62 -> decode10061@ply1 lies *inside* this theorem; it refutes the naive10000 decoder bound without refuting production score capacity. No reachable i16 overflow, source repair, production cap, wider record or backend change follows. Functional117 and codegen remain separate live validation obligations owned by the parent/validation child.
