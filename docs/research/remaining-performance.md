# Remaining performance investigations

Date: 2026-10-18. Statuses below distinguish adopted experiments from hypotheses; none promises
a qualified speedup. Full local54 PGO CPU costs total97.685122s versus the published
63.431779s sum (raw uncalibrated ratio1.5400). Calibration/profile differences
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
   compilation, the existing exhaustive digit-model oracle, all54 replays and
   a matched generic CPU pilot wait for the live game collection. It has no
   measured benefit yet; two dependent class loads can offset lower footprint.

4. **Placement bitplanes/other representations.** A private four-u64 bit-sliced
   piece/color encoding could support occupancy and attack masks with32B extra
   Position payload, rather than twelve full piece bitboards. This is an
   independently considered alternative, not an adopted representation. All
   maintenance, projected legality, copy/restoration and other-consumer costs
   need whole-pipeline measurement. Current evidence does not select it over
   the mailbox or justify its larger state. First determine the remaining true
   attack opportunity after inlining and local summaries.

The full12 game-unit cost collection, newer-artifact focused gameplay, mandatory
external diagnostics and production review remain live requirements alongside
optimization. None of these hypotheses changes KingRE behavior or the mission.

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


7. **Matched derived-bitplane storage experiment: prepared, unexecuted.**
   An identical Boolean kernel is prepared with persistent Position160/Node176
   versus local Position128/Node144 supply. The initial consumer scope leaves
   ordered checker identities and quiescence mailbox reuse intact. Constructors,
   reflection/recompute and all copied placements are part of the invariant/cost
   audit. A bounded architectural critique prompted a matched local comparison
   before choosing storage; ownership and final decisions remain Imp2's.
   Source/archive and planned checks are in
   `evidence/bitplane-preparation-20261018/`. No compile, correctness, timing or
   adoption claim follows from this preparation. The live full12 CPU collection
   must finish before native tests/builds or another engine measurement starts.
