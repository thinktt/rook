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
   under decision0003; production PGO impact remains to be measured. Position/Node
   layout, copied-child ownership and mutable search state remain unchanged.

2. **Measure repeated full evaluation before adding a cache.** Consider a
   diagnostics-only count of full evaluations entering with retained age0 as an
   opportunity estimate. Root initialization is an exception; prove the scope
   before interpreting it. The existing evaluator shares influence within one
   invocation but local derived state does not survive every scout/full or IIO
   revisit of the same produced node. A pure-component cache could reuse activity,
   shelter or other placement/root-owned terms only with exact lifetime and
   board/root/side validity. Pawn-cache accesses/replacements/collisions must
   still occur, and every consuming semantic R charge must remain exact. Caching
   a complete final score solely by fingerprint is invalid. A persistent-cache
   ownership decision would merit bounded architectural critique after evidence.

3. **Formula-derived relation lookup.** Four tested-piece tiers over two
   normalized8-bit profiles form a262144-byte pure table. A prototype could
   retain the common opponent-zero shortcut and compare cache/load costs against
   the current branchy classifier. Generate from the general formula, never
   fixture answers; exhaust all256x256 combinations per tier against the old
   formula, preserve adjusted saturation and all semantic query charges. This
   idea has no measured benefit yet and may lose through cache pressure.

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
