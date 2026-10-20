# One-sided relation compression: distinct bounded opportunity, no variant selected

**GO for parent consideration of a distinct source/compiler question.** Exact one-sided compression is possible, and the inspected history does not show it already timed. This is not a prototype, candidate selection, pipeline authorization, CPU forecast or justification to rerun parked38. No runtime tables or native source were written.

## Exact row counts and reconstruction

A standalone pure-data analysis reads the current generated typed table, not fixtures, parses exactly262144 U/C/F entries, and independently derives every result using radix division plus the Boolean relation characterization. It does not import or execute the maintenance generator. The generator's own general formula and the released definition are pinned as the numerical authority (scripts/generate_relation_table.py:features/relation; evaluation-relations.md:15–41). Both one-sided16-class and exact row-dictionary reconstructions were exhaustively checked at all4×256×256 typed tuples; all match current source. Actual final algebra terminal **f0789f/0**. `data-proof.json` retains row populations and row digests; initial feature-only proof is preserved separately.

| Tested tier | Distinct own→all256opponent rows | Typed outcome bytes |
|---|---:|---:|
| Pawn1 | 12 | 3072 |
| Minor3 (N/B shared) | 9 | 2304 |
| Rook5 | 6 | 1536 |
| Queen9 | 3 | 768 |

There are16 capped-multiplicity/least-tier own feature classes and12 distinct four-tier row signatures across all own bytes. Counts are from the full u8 domain, not observed native frequencies. These alternative shapes are data facts, **not chosen implementations**:

* Shared256B own CLASS plus four16×256 typed Relation banks:16384B outcomes, **16640B total**.
* Per-type exact row IDs (4×256B) plus30 distinct per-type rows:7680B outcomes, **8704B total**.
* Deduplicate rows across tested types too:27 global rows =6912B outcomes plus1024B typed own-row IDs, **7936B total**.

The last totals are logical payload sizes, excluding alignment/object/linker choices. No row ID is a Relation discriminant. All row IDs fit u8; table entries remain typed U/C/F (repr(u8), influence.rs:25–31). All dictionary rows return F at opponent0. Row0/Relation0 are real values, not empty sentinels; no sentinel is required. A future safe array access must establish the generated row-ID bound, or incur a bounds check; this review does not assume LLVM derives bounds from immutable table contents.

## Dependency tradeoff and full domain

Current relation dispatches kind first, rejects King, returns F for opponent0, then loads a single typed entry at `(own<<8)|opponent` (influence.rs:225–237). Its data bank is262144B. The old1280B compact scheme reads CLASS for both own and opponent, then loads the compact typed result. Those two CLASS reads can be independent of each other, but the outcome address depends on both. One-sided compression would read one own class/row ID, then a typed result using the **raw opponent byte**. It removes the opponent classification read and corresponding address contribution compared with the old compact route, while introducing an extra lookup dependency compared with current direct indexing. Neither historical timing nor smaller data prices that dependency on current62. Source profile-byte loads and surrounding queries are still required.

There is no bit-field extraction or safe numeric-enum decoder as in38. Read-only typed static outcomes preserve the enum directly; metadata ID lookup is not enum reconstruction. The footprint/latency tradeoff, address arithmetic, kind specialization, bounds/panic branches, register/spill/stack effects and actual emitted immutable storage remain unpriced. Static storage must not become repeated local table copies. No hardware cache geometry/residency/miss-rate claim follows from these sizes.

All256 own and opponent bytes remain meaningful, including wrapping-normalized crowded profiles. Knight and Bishop share the minor tier exactly. King must still panic **before** the opponent-zero shortcut, including `(King,opponent0)`. Adjusted queries must first perform original own-byte `saturating_sub(1/2/4/16/64)`, then classify that resulting byte (influence.rs:239–243; spec:117–145). Classifying before subtraction is invalid because normalization borrows across digits. Opponent and base map remain untouched. Exhaustive ordinary-byte reconstruction covers each possible saturated result; this analysis is not a new native exclusion test. Logical R, captures/shortcuts and all consumers stay at their original owners; no lifetime, mutable cache, permission or supplied-map restriction is introduced.

## Historical distinctness and decision limit

Decision0005 implemented two-sided16-state CLASS compression; its source at both create_variant.py:82–83 explicitly classifies both bytes. Decision0013 then selected the current full-byte typed table after its own generic/PGO comparisons, eliminating both classification reads. Candidate25 changed projected Boolean check generation and retained that table; it was not asymmetric relation compression. Decision0029/experiment38 packed all four typed outcomes for each raw byte pair into one64KiB byte and decoded the requested2-bit field. It parked after generic timing, with actual numeric consumers adding branches/conditional moves. One-sided row selection is therefore a different dependency/representation mechanism, not another decoder or a resized packed38.

The finite history search covers41 named relation/candidate25 proposal and review files, the prior current57 tier-packing review, decisions0005/0013/0029 and remaining-performance. No one-sided/asymmetric/row-dedup prior trial was found; that is a bounded search result, not a universal absence claim. Old global placement caches24/33 and the declined same-node Activity census solve different ownership questions and provide no benefit estimate here.

A later parent choice would need exact source/admission review and an actual current-target compiler discriminator: one intended metadata read followed by one typed outcome read, correct zero/King/exclusion order, all constant/variable-tier consumer costs, bounds, frames/calls and payload placement. Existing independent digit/exclusion native controls are relevant if execution is later authorized. This memo selects neither16-class nor dictionary layout and authorizes no source/generator/build/benchmark/PGO change. Current62 remains unchanged.
