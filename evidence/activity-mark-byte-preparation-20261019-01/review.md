# Experiment31 source preparation: arithmetic pressure-mark byte

Only the private `activity::mark` byte expression changes, from exact current production25 source69 graphd4bb0f94. Trial: `/home/legolas/rook2-work/imp2-activity-mark-byte-20261019-01`, graph31340f6b34e78ed71c74631a7af9be5ac7fdca16e1cea22e6e12005b76998d95,46native+23tools. Root source69 was compared to the accepted25 manifest before copying and again afterward; all69 match. All68 other files and the entire activity test module are unchanged. No26–30 composition, table, guard, runtime mode or second variant is present.

The old byte is `1 << (2*(kind.index()-1) + usize::from(category>=2))`; the new byte is `(1u8 + ((category as u8)>>1)) << (2*(kind.index()-1))`. The final indexed OR stays in the same place, using the same color/target and category input. This is a private admitted-domain equivalence, not equality on arbitrary i64 values.

## Every producer and the finite-domain proof

- `compute` activity.rs104–143 invokes only `accumulate_kind::<1..4>`. Its KIND is taken from `PieceKind::ALL`: Knight1,Bishop2,Rook3,Queen4. `destinations_kind`271–327 is the only production mark caller. Its knight call291 and non-additional slider call325 use that same supported kind. The cfg(test) `destinations` adapter matches only those four kinds; its unsupported-kind arm is unreachable. All direct existing test `mark` calls use Knight or Rook and categories0,2,3.
- Both production calls pass the result of `direct_category`217–236. That owner yields shortcut2 or `adjusted_relation(...) as i64`, then `capture_priority`. `Relation` is repr(u8) with Unfavorable0,Contested1,Favorable2; `adjusted_relation` calls the unchanged typed `relation` owner and full-byte typed table, including opponent0→Favorable. Thus the base is0..2 even for arbitrary valid supplied profile bytes. `capture_priority`201–214 returns the category unchanged or literal2/3 for its specified mover/victim pairs. Every final mark category is therefore0..3. Some kind/category combinations need not be naturally reachable; the proof covers the safe superset.
- Additional slider destinations at311–321 take their distinct relation/query/score path and **never call mark**. They cannot introduce another mark-category producer. Pawn and King are never activity mark kinds. Victim tags, including King, only select the existing capture-priority constants; they do not widen the category domain.

|category|old low two-bit byte|new `1+(u8(category)>>1)`|
|---:|---:|---:|
|0|1|1|
|1|1|1|
|2|2|2|
|3|2|2|

For the four kinds the common shift is0,2,4,6. Hence weak/strong bytes are Knight1/2,Bishop4/8,Rook16/32,Queen64/128. The cast is exact on0..3; addition is1 or2; maximum shifted value is128 and no bit is lost. The new byte is exactly the old byte, so OR preserves every possible existing mark byte. Category0 still inserts the weak presence bit; repeated marks remain presence, not counts. No new negative/large-category admission is introduced.

Raw mobility categories and totals stay i64 and retain their original category before/after the marker call. Direct slider/knight score multipliers, material weighting, signed rounding, capture shortcut/priority, relation calls and semantic R increments are byte-for-byte unchanged. Additional-ray R/work, pressure masks, occupancy stopping, king admission and `pressure_value` software counts also stay unchanged. This does not include experiment27's pressure digit-sum change.

## Existing checks and the next gate

No new test was added, per parent refinement: a16-case test mirroring the old expression would add little beyond the written finite-domain proof. All178 existing declarations remain176library+2development. Existing `pressure_marks_are_presence_bits_and_own_blockers_are_included` explicitly covers weak/strong OR presence and masked own-blocker pressure; `direct_capture_categories_and_queen_exception_use_final_category` covers capture override/final categories. `bishop_additional_rays_charge_without_direct_categories_or_marks`, the other transparent-ray witnesses, signed weighting tests and destination-coordinate/gate tests are unchanged. No historical oracle execution is claimed for this new source.

Parent first compiles the exact generic trial and inspects actual production lowering. If the change is unchanged/absent in the backend, park before tests/timing. If supported, parent chooses focused native checks and the existing fixed seven-case70 schedule (14excluded warmups/56measured), with unchanged aggregate≤0.995 AND at least5/7lower AND worst≤1.02. No branchful/LUT/tuned alternative or broad qualification is prepared. Own-PGO/full117/further gates require a clear win and separate parent selection. Source spelling alone predicts neither code erasure nor CPU gain; casts/shifts/register transport could lower the same or worse.

Source-only preparation: no Rust parser/formatter/compiler, native test/engine, binutils, profiling, Git or archive ran. One bounded source search referenced a nonexistent old README and returned075f35/2; it changed nothing. Subsequent proof uses actual current source and existing25 manifest. Actualsource preparation e6ec29/0; all helpers0-5,8-13/HOME TMPDIR; all owned jobs closed. Frozen source/patch/manifests are ready for parent admission.
