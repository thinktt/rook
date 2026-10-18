# Remaining performance investigations

Date: 2026-10-18. Statuses below distinguish adopted experiments from hypotheses; none promises
a qualified speedup. Current canonical915f83e4 full local54 PGO CPU costs total
88.486549s versus the published63.431779s sum(raw uncalibrated ratio1.394988).
The earlier3660 collection totaled97.685122s. Calibration/profile differences
remain unresolved. The current profile-01 simulated total is13.607B Ir;
activity and influence are prominent after legality reuse and compiler PGO.
Function attribution changed through inlining, so source-line evidence matters.

1. **Shared immutable evaluation geometry.** An isolated prototype moves the
   existing legal-attack tables into a crate-private shared module, and consumes
   valid target sequences in influence rays/leapers and activity destinations.
   It preserves traversal along each ray, pawn forward extras, transparency,
   category wrapping and relation charges.10,000 broad constructed placements
   match our prior coordinate loops for complete influence bytes, all activity
   fields and relation counts. Native tests and all54 replays pass. A fixed
   six-case generic/non-PGO CPU pilot gives ratio0.977538, supporting adoption
   under decision0003; a separately trained production PGO six-case pilot also improves by3.19% (ratio0.968078). Position/Node
   layout, copied-child ownership and mutable search state remain unchanged.

2. **Repeated full evaluation: measured and rejected as next cache target.**
   A diagnostic-only D=true ordinary derivative matches all54 replays and counts
   18,569 age0 entries out of37,094,821 full evaluations (0.050058%, including
   first-root calls). Evidence is under `evidence/evaluation-opportunity-20261018/`.
   That is too small an opportunity for the proposed same-produced-node cache.
   No cache was implemented. The broader theoretical validity constraints below
   remain relevant to any different future cache proposal. Root initialization is an exception; prove the scope
   before interpreting it. The existing evaluator shares influence within one
   invocation but local derived state does not survive every scout/full or IIO
   revisit of the same produced node. A pure-component cache could reuse activity,
   shelter or other placement/root-owned terms only with exact lifetime and
   board/root/side validity. Pawn-cache accesses/replacements/collisions must
   still occur, and every consuming semantic R charge must remain exact. Caching
   a complete final score solely by fingerprint is invalid. A persistent-cache
   ownership decision would merit bounded architectural critique after evidence.

3. **Formula-derived relation lookup.** Four tested-piece tiers over two
   normalized8-bit profiles form a262144-byte direct table. A smaller isolated
   prototype instead maps each profile to its capped-multiplicity/least-tier
   pair:16 states, a256-byte map and1024-byte outcome table. It retains the
   common opponent-zero shortcut and adjusted subtraction on the original byte.
   The generator uses the general formula, never fixture answers. Source/archive
   preparation is complete under `evidence/relation-states-preparation-20261018/`;
   a fresh isolated preparation now uses the integrated attack-plane source
   under `evidence/relation-states-bitplanes-preparation-20261018/`. Compilation,
   the existing exhaustive digit-model oracle, all54 replays and a matched
   generic CPU pilot proceed as a separate bounded experiment. It has no
   measured benefit yet; two dependent class loads can offset lower footprint.

4. **Placement bitplanes/other representations.** The independently developed
   four-u64 Piece-tag representation has now passed a matched storage comparison
   and is adopted under decision0004. The mailbox and chronology retain their
   other consumers. Item7 records the measured scope and limits; other layouts
   remain alternatives requiring their own complete maintenance/copy/query cost.

The reported-only full12 collection on1dc996b2 now reconciles48 lifetimes/
2528 searches, summing941.928787s in game CPU medians (raw uncalibrated
ratio1.462116). Its helper-affinity limitation remains disclosed. Final qualified
54/12 costs, newer-artifact focused gameplay, remaining mandatory diagnostics
and production review remain requirements alongside optimization.

5. **Pure inputs within one evaluation invocation.** An isolated prototype at
   `/tmp/imp2-evaluation-inputs-20261018` reuses current phase and root-valued
   material between fast evaluation and its full refresh, and passes the same
   phase into king-square balance/finishing. Position and root context are
   unchanged throughout that call; PawnCache activity and R charges remain live.
   No persistent cache or mutable key is added. All130 native tests pass; the
   frozen generic build/check is under `evidence/evaluation-inputs-*20261018/`.
   All54 strict replays pass. A six-case/60-lifetime generic pilot gives
   sum-of-medians ratio0.992505 (0.74948% lower), with overlapping samples in
   several cases. It remains isolated: no production adoption or inferred PGO
   benefit. See `evidence/evaluation-inputs-cpu-pilot-20261018/`.


6. **King-coordinate metadata within existing padding.** An isolated prototype
   consumes two previously unused bytes of the128-byte Position for direct king
   access. Node remains144 bytes. Constructors/recompute, ordinary/castling king
   transitions, null copies and exceptional terminal king removal maintain this
   placement-derived metadata; chronological lists remain independent.130
   library tests plus two development-CLI tests and all54 strict replays pass.
   New mailbox-oracle legal histories and exceptional-child checks validate the
   invariant. A fixed six-case/60-lifetime generic CPU pilot is essentially flat:
   sum-of-medians ratio0.998770 (0.12298% lower), with overlapping ranges and
   two increased case medians. Production adoption is rejected. The unchanged
   representation remains; avoiding prefix sums alone did not select this
   change. See `evidence/king-square-cache-cpu-pilot-20261018/`.


7. **Matched derived-bitplane storage experiment: generic trial complete.**
   An identical Boolean kernel was tested with persistent Position160/Node176
   versus local Position128/Node144 supply. The initial consumer scope leaves
   ordered checker identities and quiescence mailbox reuse intact. Constructors,
   reflection/recompute and all copied placements are part of the invariant/cost
   audit. A bounded architectural critique prompted a matched local comparison
   before choosing storage; ownership and final decisions remain Imp2's.
   Both pass133 native tests and all54 strict replays. The independent90-lifetime
   six-case generic pilot sums16.7270585s baseline,16.3704720s persistent and
   16.8066150s local: persistent/base0.978682, local/base1.004756. All six persistent
   medians are lower, with substantial overlap in profile04. Its own PGO trial
   then passes54 replays/eight interruption fixtures and60 CPU lifetimes:
   trial14.805304s versus baseline1dc996b2 sum15.296771s, ratio0.967871193.
   Persistent source is integrated after133 native tests and25 adapter units/
   1214 cases; this explicit local strategy is parked. Canonical repository
   PGO915f83e4 has its own54-case profile and passes54 replays/eight interruption
   fixtures. Its own60-lifetime pilot sums14.907624s versus15.388885s baseline,
   ratio0.968726714(3.127329% lower), with profile04 ranges overlapping. A complete
   canonical54 CPU collection now independently reconciles216 lifetimes,
   summing88.486549s. No final54/12 qualification follows yet.
   See `evidence/bitplanes-20261018/` and its exact preparation/source archives.

8. **Counts-guided mailbox Boolean attacks: alternative kernel hypothesis.**
   The old Boolean query always walks potential pawn/knight/king/slider routes;
   the bitplane kernel can stop when a slider class is absent. A separate
   layout-preserving control could supply the existing opponent counts to a
   Boolean mailbox query, check king neighbors directly, and skip absent knight,
   diagonal or orthogonal classes. Original counts remain a conservative
   absence guide after an own-move safety projection: ordinary moves, promotions,
   castling and joined EP cannot create an opposing piece. Removing any actual
   victim only makes a nonzero count overestimate possible presence. All actual
   geometric matches would still read the projected board, including a removed
   king victim; no enemy-king coordinate or legal-ancestry shortcut is implied.
   Ordered capped checker identities and quiescence's existing mailbox reuse
   would retain their current owners. This differs from the common bitplane
   query kernel and cannot isolate storage cost. It is unimplemented/unmeasured;
   investigate only after the matched bitplane results, with broad independent
   Boolean/projection comparisons and whole-native timing before adoption.
